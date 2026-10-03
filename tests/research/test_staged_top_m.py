"""TV2 DEV H_ref baseline checks; TV3 oracle and quality gate remain pending."""

from pathlib import Path

from backend.research.joint_dp import solve_joint
from backend.research.schemas import Budget, ResearchCase, Theta
from backend.research.service import load_manifest
from backend.research.staged_top_m import staged_top_m_h_ref

FIXTURE = Path(__file__).parent / "fixtures" / "method_gap_example.json"
THETA = Theta(rho=.5, lambda_mm=2)
BUDGET = Budget(wall_time_ms=10000, max_states=100000,
                max_configurations=100, memory_limit_mb=64)


def test_reference_ranking_and_nested_exact_prefix():
    case = load_manifest(FIXTURE)[0]
    first = staged_top_m_h_ref(case, THETA, THETA, 1, BUDGET)
    full = staged_top_m_h_ref(case, THETA, THETA, 2, BUDGET)
    joint = solve_joint(case, THETA, BUDGET, safe_forget=True)
    assert first.ranked_prefix == (("a-local", "b-fixed"),)
    assert full.ranked_prefix == (("a-local", "b-fixed"), ("a-delayed", "b-fixed"))
    assert all((run.enumeration_complete, run.ranking_complete, run.search_complete) ==
               (True, True, True) for run in (first, full))
    assert first.scope == full.scope == "declared_prefix"
    assert first.outcome == full.outcome == "OPTIMAL"
    assert first.best_inner.objective_exact > full.best_inner.objective_exact
    assert full.best_inner.objective_exact == joint.objective_exact
    assert first.candidate_set_sha256 == full.candidate_set_sha256 == case.candidate_set_sha256


def test_invalid_reference_is_ranked_last_not_removed():
    data = load_manifest(FIXTURE)[0].model_dump(mode="json")
    variant = data["candidates"][0]["variants"][0]
    variant["strokes"].extend([
        {"stroke_id": "a", "role": "mark", "owner_index": 0, "reversible": False,
         "polyline_mm": [[0, 2], [1, 2]], "mark_type": "synthetic-tone"},
        {"stroke_id": "z", "role": "mark", "owner_index": 0, "reversible": False,
         "polyline_mm": [[0, 3], [1, 3]], "mark_type": "synthetic-tone"},
    ])
    variant["mark_precedence"] = [["z", "a"]]
    case = ResearchCase.prepare(data)
    run = staged_top_m_h_ref(case, THETA, THETA, 2, BUDGET)
    assert run.invalid_reference_count == 1
    assert run.ranked_prefix[-1] == ("a-local", "b-fixed")
    assert run.enumeration_complete and run.ranking_complete and run.search_complete


def test_ranking_budget_keeps_explored_subset_incomplete():
    case = load_manifest(FIXTURE)[0]
    limited = BUDGET.model_copy(update={"max_configurations": 1})
    run = staged_top_m_h_ref(case, THETA, THETA, 1, limited)
    assert run.outcome == "RESOURCE_LIMIT" and run.scope == "explored_subset"
    assert not run.enumeration_complete and not run.ranking_complete and not run.search_complete
    assert run.best_inner is None and run.configurations_seen == 1


def test_empty_case_and_no_feasible_prefix():
    empty = load_manifest(Path(__file__).parent / "fixtures" / "solver_dev_cases.json")[1]
    run = staged_top_m_h_ref(empty, THETA, THETA, 1, BUDGET)
    assert run.outcome == "OPTIMAL" and run.ranked_prefix == ((),)
    assert run.best_inner.replay.N_cycle == 0
    data = load_manifest(FIXTURE)[0].model_dump(mode="json")
    for variant in data["candidates"][0]["variants"]:
        for stroke in variant["strokes"]:
            stroke["polyline_mm"] = [[0, 0], [1, 0]]
    impossible = ResearchCase.prepare(data)
    no_prefix = staged_top_m_h_ref(impossible, THETA, THETA, 1, BUDGET)
    assert no_prefix.outcome == "NO_FEASIBLE_IN_PREFIX"
    assert no_prefix.scope == "declared_prefix" and no_prefix.search_complete
    assert no_prefix.best_inner is None
