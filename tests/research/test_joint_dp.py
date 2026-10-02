"""DEV hand cases and no-forget/safe-forget equivalence, not TV3 oracle."""

import random
from pathlib import Path
import pytest

from backend.research.geometry import check_selected_geometry
from backend.research.joint_dp import solve_joint
from backend.research.schedule_checker import check_schedule_cost
from backend.research.schemas import Budget, ResearchCase, Theta
from backend.research.service import load_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "solver_dev_cases.json"
BUDGET = Budget(wall_time_ms=10000, max_states=100000, max_configurations=10000, memory_limit_mb=64)
THETA = Theta(rho=.5, lambda_mm=2)


def tiny_case(rows):
    data = load_manifest(FIXTURE)[1].model_dump(mode="json")
    data["case_id"] = "tv4-dev-hand-case"
    data["boundary"].update(p0_mm=[0, 0], p_end_mm=[3, 0])
    data["candidates"] = []
    for owner, alternatives in enumerate(rows):
        variants = []
        for j, points in enumerate(alternatives):
            variants.append({"candidate_id": f"v{j}", "source_hash": "b" * 64,
                             "body_order": ["b"], "strokes": [{"stroke_id": "b", "role": "body",
                             "owner_index": owner, "reversible": False, "polyline_mm": points}]})
        data["candidates"].append({"owner_index": owner, "grapheme": "a", "variants": variants})
    data["normalized_text"] = data["original_text"] = "a" * len(rows)
    return ResearchCase.prepare(data)


@pytest.mark.parametrize("forget", [False, True])
def test_hand_cost_and_empty_boundary(forget):
    case = tiny_case([[[[0, 0], [1, 0]]], [[[2, 0], [3, 0]]]])
    run = solve_joint(case, THETA, BUDGET, safe_forget=forget)
    assert run.outcome == "OPTIMAL" and run.search_complete
    assert run.replay.J_mm == 6.5  # down=2, up=1, cycles=2
    assert run.replay.N_cycle == 2
    assert run.diagnostics["peak_frontier"] >= 1
    assert run.independent_validation == "NOT_RUN"
    assert check_selected_geometry(case, run.schedule)["status"] == "PASS"
    empty = solve_joint(load_manifest(FIXTURE)[1], THETA, BUDGET, safe_forget=forget)
    assert empty.replay.J_mm == 2.5 and empty.replay.N_cycle == 0


def test_distant_interaction_must_keep_old_choice():
    case = tiny_case([[[[0, 0], [1, 0]], [[0, 1], [1, 1]]],
                      [[[3, 0], [4, 0]]], [[[0, 0], [1, 0]]]])
    results = [solve_joint(case, THETA, BUDGET, safe_forget=f) for f in (False, True)]
    for run in results:
        assert run.schedule.candidate_ids[0] == "v1"
        assert run.outcome == "OPTIMAL"
        check_selected_geometry(case, run.schedule)
    assert results[0].replay.J_mm == results[1].replay.J_mm


@pytest.mark.parametrize("forget", [False, True])
def test_infeasible_is_exhausted_search(forget):
    case = tiny_case([[[[0, 0], [1, 0]]], [[[0, .19], [1, .19]]]])
    run = solve_joint(case, THETA, BUDGET, safe_forget=forget)
    assert run.outcome == "INFEASIBLE" and run.search_complete
    assert run.schedule is run.replay is None


def test_resource_limit_preserves_completed_incumbent():
    case = tiny_case([[[[0, 0], [1, 0]], [[0, 1], [1, 1]]]])
    run = solve_joint(case, THETA, BUDGET.model_copy(update={"max_states": 2}))
    assert run.outcome == "RESOURCE_LIMIT" and not run.search_complete
    assert run.schedule is not None and run.replay.J_mm > 0
    check_selected_geometry(case, run.schedule)


def test_resource_limit_without_incumbent():
    run = solve_joint(load_manifest(FIXTURE)[0], THETA, BUDGET.model_copy(update={"max_states": 1}))
    assert run.outcome == "RESOURCE_LIMIT" and not run.search_complete
    assert run.schedule is run.replay is None


def test_timeout_is_not_optimal(monkeypatch):
    import backend.research.joint_dp as dp
    values = iter([0])
    monkeypatch.setattr(dp, "monotonic", lambda: next(values, 2))
    run = solve_joint(load_manifest(FIXTURE)[0], THETA, BUDGET.model_copy(update={"wall_time_ms": 1}))
    assert run.outcome == "TIMEOUT" and not run.search_complete


def test_memory_limit_during_preprocessing(monkeypatch):
    import backend.research.joint_dp as dp
    values = iter([(0, 0)])
    monkeypatch.setattr(dp.tracemalloc, "is_tracing", lambda: True)
    monkeypatch.setattr(dp.tracemalloc, "get_traced_memory", lambda: next(values, (2 * 1024 * 1024, 0)))
    run = solve_joint(load_manifest(FIXTURE)[0], THETA, BUDGET.model_copy(update={"memory_limit_mb": 1}))
    assert run.outcome == "RESOURCE_LIMIT" and not run.search_complete


def test_repeated_equal_cost_choices_have_stable_dev_tie():
    case = tiny_case([[[[0, 0], [1, 0]], [[0, 0], [1, 0]]]])
    runs = [solve_joint(case, THETA, BUDGET, safe_forget=f) for f in (False, True)]
    assert all(r.schedule.candidate_ids == ["v0"] for r in runs)
    assert runs[0].schedule == runs[1].schedule


def test_geometry_policy_and_holdout_are_not_silently_accepted():
    data = load_manifest(FIXTURE)[0].model_dump(mode="json")
    data["split"] = "holdout"
    with pytest.raises(ValueError, match="HOLDOUT"):
        solve_joint(ResearchCase.prepare(data), THETA, BUDGET)
    data["split"] = "dev"
    data["geometry_policy"]["numeric_policy_id"] = "PENDING"
    with pytest.raises(ValueError, match="Unsupported"):
        solve_joint(ResearchCase.prepare(data), THETA, BUDGET)


@pytest.mark.parametrize("seed", range(12))
def test_seeded_dev_no_forget_matches_safe_forget(seed):
    rng = random.Random(seed)
    data = load_manifest(FIXTURE)[0].model_dump(mode="json")
    data["delay_policy"] = {"dev-tone": rng.choice([0, 1, 2])}
    for v in data["candidates"][0]["variants"]:
        for s in v["strokes"]:
            if s["role"] == "mark":
                offset = rng.choice([0, .1, .3])
                s["polyline_mm"] = [[x, y + offset] for x, y in s["polyline_mm"]]
            s["reversible"] = rng.choice([True, False])
    case = ResearchCase.prepare(data)
    theta = Theta(rho=rng.choice([.3, .5, 1]), lambda_mm=rng.choice([0, 2, 4]))
    a, b = [solve_joint(case, theta, BUDGET, safe_forget=f) for f in (False, True)]
    assert a.search_complete and b.search_complete and a.outcome == b.outcome
    if a.replay:
        assert a.replay.J_mm == pytest.approx(b.replay.J_mm)
        for run in (a, b):
            assert check_schedule_cost(case, run.schedule, theta).J_mm == run.replay.J_mm
            check_selected_geometry(case, run.schedule)
    assert b.diagnostics["peak_states"] <= a.diagnostics["peak_states"]
