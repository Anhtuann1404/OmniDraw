"""DEV fixed-plan regret arithmetic; not certificate acceptance."""

from pathlib import Path
import pytest

from backend.research.joint_dp import solve_joint
from backend.research.schedule_checker import check_schedule_cost
from backend.research.schemas import Budget, Domain, ResearchCase, Theta, canonical_hash
from backend.research.service import load_manifest
from backend.research.vertex_analysis import analyze_fixed_schedule

FIXTURE = Path(__file__).parent / "fixtures" / "solver_dev_cases.json"
BUDGET = Budget(wall_time_ms=10000, max_states=100000, max_configurations=1, memory_limit_mb=64)
DOMAIN = Domain(rho_min=.2, rho_max=1, lambda_min_mm=0, lambda_max_mm=4)


def test_plan_fixed_while_all_vertex_competitors_can_change_geometry():
    case = load_manifest(FIXTURE)[0]
    pi = solve_joint(case, Theta(rho=.5, lambda_mm=2), BUDGET).schedule
    # A feasible alternative geometry is deliberately fixed for all four vertices.
    pi.candidate_ids[0] = "a-dev-alt"
    for action in pi.actions:
        if action.stroke.owner_index == 0:
            action.stroke.candidate_id = "a-dev-alt"
    before = canonical_hash(pi.model_dump(mode="json"))
    report = analyze_fixed_schedule(case, pi, DOMAIN, BUDGET)
    assert report["schedule_sha256"] == before == canonical_hash(pi.model_dump(mode="json"))
    assert report["certificate_status"] == "NOT_CERTIFIED"
    assert report["independent_validation"] == "NOT_RUN"
    assert len(report["vertices"]) == 4
    for vertex in report["vertices"]:
        theta = Theta.model_validate(vertex["theta"])
        assert vertex["J_pi_mm"] == check_schedule_cost(case, pi, theta).J_mm
        assert vertex["dev_regret_mm"] >= 0
    assert report["modeled_vertex_max_regret_mm"] > 0


def test_incomplete_vertex_cannot_produce_maximum_claim():
    case = load_manifest(FIXTURE)[0]
    pi = solve_joint(case, Theta(rho=.5, lambda_mm=2), BUDGET).schedule
    report = analyze_fixed_schedule(case, pi, DOMAIN, BUDGET.model_copy(update={"max_states": 1}))
    assert report["modeled_vertex_max_regret_mm"] is None
    assert report["certificate_status"] == "NOT_CERTIFIED"
    assert any(v["outcome"] == "RESOURCE_LIMIT" for v in report["vertices"])


def test_vertex_analysis_rejects_holdout():
    case = load_manifest(FIXTURE)[0]
    pi = solve_joint(case, Theta(rho=.5, lambda_mm=2), BUDGET).schedule
    data = case.model_dump(mode="json")
    data["split"] = "holdout"
    with pytest.raises(ValueError, match="dev/synthetic"):
        analyze_fixed_schedule(ResearchCase.prepare(data), pi, DOMAIN, BUDGET)
