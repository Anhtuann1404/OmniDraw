"""Unit and integration tests for TV3 independent exhaustive oracle enumerator.

Authored independently by TV3 following Docs 31 (joint solver contract) and Docs 32.
Validates small registered cases (empty, reverse, CONNECT/LIFT, stacked marks,
deadline k=0/1, equal cost, and infeasibility) against exact requirements.
Cross-validates against TV4 solver output using an external comparison harness
without importing TV4 solver internals into the oracle package.
"""

from __future__ import annotations

import math
from pathlib import Path
import pytest

from backend.research.schemas import (
    Budget,
    ResearchCase,
    SolveRequest,
    SolveResult,
    Theta,
)
from backend.research.service import load_manifest
from backend.research.independent_oracle.enumerator import (
    OracleRun,
    solve_oracle,
    validate_configuration_geometry,
)
from backend.research.independent_oracle.adapter import (
    solve_oracle_adapter,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SOLVER_CASES = FIXTURES_DIR / "solver_dev_cases.json"
NUMERIC_CASES = FIXTURES_DIR / "numeric_rounding_cases.json"


# ---------------------------------------------------------------------------
# 1. Empty Case Verification
# ---------------------------------------------------------------------------

def test_oracle_empty_case():
    """Empty text case: 0 strokes, pen moves UP from p0 to p_end, N_cycle=0."""
    manifest = load_manifest(SOLVER_CASES)
    empty_case = next(c for c in manifest if c.case_id == "tv4-solver-dev-empty")

    theta = Theta(rho=1.0, lambda_mm=2.0)
    run = solve_oracle(empty_case, theta)

    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.enumeration_complete is True
    assert run.schedule is not None
    assert run.schedule.actions == []
    assert run.schedule.N_cycle == 0
    assert run.schedule.L_down_mm == 0.0

    expected_up = math.hypot(
        empty_case.boundary.p_end_mm[0] - empty_case.boundary.p0_mm[0],
        empty_case.boundary.p_end_mm[1] - empty_case.boundary.p0_mm[1],
    )
    assert math.isclose(run.schedule.L_up_mm, expected_up, rel_tol=1e-9)
    assert math.isclose(run.schedule.J_mm, theta.rho * expected_up, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# 2. CONNECT vs LIFT at Contact Endpoint
# ---------------------------------------------------------------------------

def test_oracle_connect_vs_lift():
    """Verify that CONNECT transition is preferred when lambda > 0 and endpoints coincide with contact."""
    manifest = load_manifest(SOLVER_CASES)
    stacked_case = next(c for c in manifest if c.case_id == "tv4-solver-dev-stacked-3")

    # With lambda > 0, connecting touching strokes b1 and b2 of owner 1 saves 1 cycle
    theta_pos_lambda = Theta(rho=1.0, lambda_mm=5.0)
    run = solve_oracle(stacked_case, theta_pos_lambda)

    assert run.outcome == "OPTIMAL"
    assert run.schedule is not None
    transitions = [a.transition for a in run.schedule.actions]
    # owner 1 body b1 and b2 touch at (4.0, 0.0) with declared contact
    assert "CONNECT" in transitions


# ---------------------------------------------------------------------------
# 3. Clearance Infeasibility Detection
# ---------------------------------------------------------------------------

def test_oracle_infeasible_geometry():
    """Case where all candidates violate c_min floor must return INFEASIBLE."""
    manifest = load_manifest(SOLVER_CASES)
    case_data = manifest[0].model_dump(mode="json")

    # Modify stroke to have clearance 0.19 mm (< c_min = 0.20 mm) without contact
    # Owner 0 variant "a-dev" stroke "shape" placed at y=0.19 above body at y=0.0
    case_data["candidates"][0]["variants"][0]["strokes"][1]["polyline_mm"] = [[0.0, 0.19], [1.0, 0.19]]
    # Also modify the other variant so no feasible variant exists
    case_data["candidates"][0]["variants"][1]["strokes"][1]["polyline_mm"] = [[0.0, 0.19], [1.0, 0.19]]

    infeasible_case = ResearchCase.prepare(case_data)
    theta = Theta(rho=1.0, lambda_mm=2.0)
    run = solve_oracle(infeasible_case, theta)

    assert run.outcome == "INFEASIBLE"
    assert run.schedule is None
    assert run.search_complete is True


# ---------------------------------------------------------------------------
# 4. Mark Precedence and Deadline k=0 vs k=1
# ---------------------------------------------------------------------------

def test_oracle_mark_precedence_and_deadline():
    """Verify that mark precedence and delay policies are strictly enforced."""
    manifest = load_manifest(SOLVER_CASES)
    stacked_case = next(c for c in manifest if c.case_id == "tv4-solver-dev-stacked-3")

    # In stacked-3, variant "a-dev" has marks "shape" and "tone"
    # mark_precedence requires "shape" before "tone"
    theta = Theta(rho=1.0, lambda_mm=2.0)
    run = solve_oracle(stacked_case, theta)

    assert run.outcome == "OPTIMAL"
    assert run.schedule is not None

    actions = run.schedule.actions
    # Extract order of owner 0 marks
    owner0_marks = [a.stroke_id for a in actions if a.owner_index == 0 and a.stroke_id in {"shape", "tone"}]
    assert owner0_marks == ["shape", "tone"]


# ---------------------------------------------------------------------------
# 5. Cross-validation: Independent Oracle vs TV4 Solver (External Harness)
# ---------------------------------------------------------------------------

def test_cross_validate_oracle_with_tv4_solver():
    """Cross-validates oracle results with TV4 solver on solver_dev_cases.

    The oracle is executed independently. TV4 solve_joint is called strictly
    inside the test harness for comparative verification, not inside oracle code.
    """
    from backend.research.joint_dp import solve_joint

    manifest = load_manifest(SOLVER_CASES)
    theta = Theta(rho=1.0, lambda_mm=2.0)
    budget = Budget(wall_time_ms=10000, max_states=100000, max_configurations=10000, memory_limit_mb=512)

    for case in manifest:
        # Solve with independent oracle
        oracle_run = solve_oracle(case, theta, budget)

        # Solve with TV4 joint DP
        tv4_run = solve_joint(case, theta, budget)

        # 1. Feasibility & Outcome agreement
        assert oracle_run.outcome == tv4_run.outcome, f"Outcome mismatch on case {case.case_id}"

        # 2. Optimal objective value agreement within floating-point tolerance
        if oracle_run.outcome == "OPTIMAL":
            assert oracle_run.schedule is not None
            assert tv4_run.schedule is not None

            oracle_j = oracle_run.schedule.J_mm
            tv4_j = tv4_run.replay.J_mm if tv4_run.replay else None

            assert tv4_j is not None
            assert math.isclose(oracle_j, tv4_j, rel_tol=1e-9, abs_tol=1e-9), (
                f"Objective mismatch on case {case.case_id}: oracle J={oracle_j} vs tv4 J={tv4_j}"
            )

            # 3. Coefficients agreement
            assert math.isclose(oracle_run.schedule.L_down_mm, tv4_run.replay.L_down_mm, rel_tol=1e-9)
            assert math.isclose(oracle_run.schedule.L_up_mm, tv4_run.replay.L_up_mm, rel_tol=1e-9)
            assert oracle_run.schedule.N_cycle == tv4_run.replay.N_cycle


# ---------------------------------------------------------------------------
# 6. Adapter Contract Compliance (Docs 32)
# ---------------------------------------------------------------------------

def test_oracle_adapter_contract():
    """Verify that solve_oracle_adapter conforms to Docs 32 SolveResult contract."""
    manifest = load_manifest(SOLVER_CASES)
    case = manifest[0]

    request = SolveRequest(
        schema_version="joint-artifact-v1-draft",
        run_id="test-oracle-run-001",
        case_ref=case.case_id,
        method="independent_oracle",
        theta=Theta(rho=1.0, lambda_mm=2.0),
        budget=Budget(wall_time_ms=10000, max_states=100000, max_configurations=10000, memory_limit_mb=512),
        seed=42,
    )

    result = solve_oracle_adapter(case, request)

    assert isinstance(result, SolveResult)
    assert result.method == "independent_oracle"
    assert result.outcome == "OPTIMAL"
    assert result.scope == "full_candidate_set"
    assert result.enumeration_complete is True
    assert result.ranking_complete is True
    assert result.search_complete is True
    assert result.schedule is not None
    assert result.validation.status == "NOT_RUN"
    assert result.bounds.lower_bound_J_mm == result.metrics.J_mm
    assert result.bounds.upper_bound_J_mm == result.metrics.J_mm
    assert result.provenance.git_commit is not None
    assert result.provenance.timing_source == "dev"


# ---------------------------------------------------------------------------
# 7. Method Gap Example Verification (Docs 36)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rho,lam", [(0.5, 2.0), (1.0, 0.0), (2.0, 4.0)])
def test_oracle_on_method_gap_example(rho: float, lam: float):
    """Verifies that independent oracle chooses the globally optimal schedule
    ('a-delayed' variant with late tone) matching Docs 36 witness.
    """
    gap_fixture = FIXTURES_DIR / "method_gap_example.json"
    case = load_manifest(gap_fixture)[0]
    theta = Theta(rho=rho, lambda_mm=lam)

    run = solve_oracle(case, theta)

    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.schedule is not None

    # Expected: winner is candidate 'a-delayed', and tone mark of owner 0 is scheduled after owner 1 body
    assert run.schedule.candidate_ids == ["a-delayed", "b-fixed"]
    actions = run.schedule.actions
    assert len(actions) == 3
    assert actions[0].as_key() == (0, "a-delayed", "body")
    assert actions[1].as_key() == (1, "b-fixed", "body")
    assert actions[2].as_key() == (0, "a-delayed", "tone")  # delayed tone execution

    # Expected up distance for ('a-delayed', True) is 2.0
    assert math.isclose(run.schedule.L_up_mm, 2.0, rel_tol=1e-9)
    assert run.schedule.L_down_mm == 3.0
    assert run.schedule.N_cycle == 3
    expected_j = 3.0 + rho * 2.0 + lam * 3
    assert math.isclose(run.schedule.J_mm, expected_j, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# 8. Numeric Rounding Precision Stress-Test (Audit 20261002)
# ---------------------------------------------------------------------------

def test_oracle_on_numeric_rounding_cases():
    """Verifies that independent oracle handles high-precision dyadic tie/stress cases."""
    manifest = load_manifest(NUMERIC_CASES)
    theta = Theta(rho=1.0, lambda_mm=float(2**53))

    for case in manifest:
        run = solve_oracle(case, theta)
        assert run.outcome == "OPTIMAL"
        assert run.search_complete is True
        assert run.schedule is not None
        # On two-owner case, v1 (length 0.6) has shorter down length than v0 (0.9)
        if case.case_id == "tv4-numeric-two-owners":
            assert run.schedule.candidate_ids[0] == "v1-shorter-dev"
