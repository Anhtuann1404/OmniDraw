"""TV4 inner-solver consistency checks; these do not replace TV3's oracle."""

from itertools import product
from pathlib import Path

import pytest

from backend.research.dev_solve import result_packet
from backend.research.geometry import check_selected_geometry
from backend.research.joint_dp import solve_fixed_configuration, solve_joint
from backend.research.schemas import Budget, ResearchCase, Theta
from backend.research.service import load_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "solver_dev_cases.json"
BUDGET = Budget(wall_time_ms=10000, max_states=100000, max_configurations=1, memory_limit_mb=64)
THETA = Theta(rho=.5, lambda_mm=2)


def ids(case):
    return [row.variants[0].candidate_id for row in case.candidates]


@pytest.mark.parametrize("forget", [False, True])
def test_fixed_minimum_matches_joint_and_preserves_original_case(forget):
    case = load_manifest(FIXTURE)[0]
    original = case.model_dump(mode="json")
    configurations = product(*(tuple(v.candidate_id for v in row.variants) for row in case.candidates))
    runs = [solve_fixed_configuration(case, config, THETA, BUDGET, safe_forget=forget)
            for config in configurations]
    assert all(run.search_complete for run in runs)
    for run in runs:
        assert run.scope == "fixed_configuration"
        assert run.candidate_set_sha256 == case.candidate_set_sha256
        assert run.independent_validation == "NOT_RUN"
        assert not run.diagnostics["enumeration_complete"]
        assert not run.diagnostics["ranking_complete"]
        if run.schedule:
            assert tuple(run.schedule.candidate_ids) == run.configuration_candidate_ids
            assert check_selected_geometry(case, run.schedule)["status"] == "PASS"
    joint = solve_joint(case, THETA, BUDGET, safe_forget=forget)
    assert min(run.replay.J_mm for run in runs if run.replay) == pytest.approx(joint.replay.J_mm)
    assert joint.scope == "full_candidate_set" and joint.configuration_candidate_ids is None
    assert joint.candidate_set_sha256 == case.candidate_set_sha256
    assert case.model_dump(mode="json") == original


@pytest.mark.parametrize("forget", [False, True])
def test_fixed_solver_cannot_switch_to_cheaper_candidate(forget):
    data = load_manifest(FIXTURE)[0].model_dump(mode="json")
    for stroke in data["candidates"][0]["variants"][0]["strokes"]:
        stroke["polyline_mm"] = [[x, y + 50] for x, y in stroke["polyline_mm"]]
    case = ResearchCase.prepare(data)
    chosen = ids(case)
    fixed = solve_fixed_configuration(case, chosen, THETA, BUDGET, safe_forget=forget)
    joint = solve_joint(case, THETA, BUDGET, safe_forget=forget)
    assert fixed.outcome == joint.outcome == "OPTIMAL"
    assert fixed.schedule.candidate_ids == chosen
    assert fixed.replay.J_mm > joint.replay.J_mm
    chosen.clear()
    assert fixed.configuration_candidate_ids == tuple(ids(case))


@pytest.mark.parametrize("forget", [False, True])
def test_fixed_infeasible_is_not_global_infeasible(forget):
    data = load_manifest(FIXTURE)[0].model_dump(mode="json")
    for stroke in data["candidates"][0]["variants"][0]["strokes"]:
        stroke["polyline_mm"] = [[0, 0], [1, 0]]
    case = ResearchCase.prepare(data)
    fixed = solve_fixed_configuration(case, ids(case), THETA, BUDGET, safe_forget=forget)
    assert fixed.outcome == "INFEASIBLE" and fixed.search_complete
    assert fixed.schedule is fixed.replay is None
    assert fixed.scope == "fixed_configuration"
    assert solve_joint(case, THETA, BUDGET, safe_forget=forget).outcome == "OPTIMAL"


@pytest.mark.parametrize("selection", [None, "a-dev", {"a-dev"}, [True, "b-dev", "c-dev"],
                                       [1, "b-dev", "c-dev"], [], ["missing", "b-dev", "c-dev"],
                                       ["b-dev", "a-dev", "c-dev"],
                                       ["a-dev", "b-dev", "c-dev", "extra"]])
def test_invalid_selection_rejected(selection):
    with pytest.raises(ValueError, match="candidate|owner"):
        solve_fixed_configuration(load_manifest(FIXTURE)[0], selection, THETA, BUDGET)


@pytest.mark.parametrize("forget", [False, True])
def test_empty_fixed_configuration_and_budget_incumbent(forget):
    case = load_manifest(FIXTURE)[1]
    run = solve_fixed_configuration(case, [], THETA, BUDGET, safe_forget=forget)
    assert run.outcome == "OPTIMAL" and run.replay.J_mm == 2.5
    assert run.configuration_candidate_ids == ()
    data = case.model_dump(mode="json")
    data.update(normalized_text="a", original_text="a", candidates=[{
        "owner_index": 0, "grapheme": "a", "variants": [{"candidate_id": "v0", "source_hash": "b" * 64,
        "body_order": ["b"], "strokes": [{"stroke_id": "b", "role": "body", "owner_index": 0,
        "reversible": True, "polyline_mm": [[0, 0], [1, 0]]}]}]}])
    case = ResearchCase.prepare(data)
    limited = solve_fixed_configuration(case, ["v0"], THETA,
                                        BUDGET.model_copy(update={"max_states": 2}), safe_forget=forget)
    assert limited.outcome == "RESOURCE_LIMIT" and not limited.search_complete
    assert limited.schedule.candidate_ids == ["v0"]
    assert limited.scope == "fixed_configuration"


def test_timeout_remains_incomplete_with_fixed_identity(monkeypatch):
    import backend.research.joint_dp as dp
    ticks = iter([0])
    monkeypatch.setattr(dp, "monotonic", lambda: next(ticks, 2))
    case = load_manifest(FIXTURE)[0]
    run = solve_fixed_configuration(case, ids(case), THETA, BUDGET.model_copy(update={"wall_time_ms": 1}))
    assert run.outcome == "TIMEOUT" and not run.search_complete
    assert run.schedule is None and run.scope == "fixed_configuration"
    assert run.candidate_set_sha256 == case.candidate_set_sha256
    assert run.configuration_candidate_ids == tuple(ids(case))


def test_holdout_and_transport_scope_guard():
    case = load_manifest(FIXTURE)[0]
    run = solve_fixed_configuration(case, ids(case), THETA, BUDGET)
    with pytest.raises(ValueError, match="full-candidate-set"):
        result_packet(case, THETA, BUDGET, run, None, 0)
    data = case.model_dump(mode="json")
    data["split"] = "holdout"
    with pytest.raises(ValueError, match="HOLDOUT"):
        solve_fixed_configuration(ResearchCase.prepare(data), ids(case), THETA, BUDGET)
