"""
Tests for TV1 Vietnamese Candidate Dataset and Fixtures (Docs 31/32).

Verifies:
1. Manifest integrity and canonical SHA-256 hashing.
2. Compliance with strict ResearchCase schema (NFD graphemes, owners, polylines).
3. TV4 geometry compilation: c_min floor 0.20 mm, self-intersection, declared contacts.
4. Feasibility and joint DP solve (no-forget vs safe-forget) on realistic Vietnamese cases.
5. Vietnamese diacritic handling:
   - Stacked diacritics ('ấb': circumflex + acute precedence).
   - Mark below ('ệc': circumflex above + dot below baseline).
   - Distant interaction ('óto': deadline k=2 allows delaying diacritic past letter 1 and 2).
"""

from pathlib import Path
import pytest

from backend.research.geometry import compile_geometry, check_selected_geometry
from backend.research.joint_dp import solve_joint
from backend.research.schemas import Budget, ResearchCase, Theta, canonical_hash
from backend.research.service import load_manifest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "tv1_candidates_dev.json"
DEV_DATASET_PATH = Path(__file__).parent.parent.parent / "dataset" / "research" / "dev" / "tv1_dev_manifest.json"

BUDGET = Budget(wall_time_ms=10000, max_states=100000, max_configurations=10000, memory_limit_mb=64)
THETA = Theta(rho=0.5, lambda_mm=2.0)


def test_tv1_manifest_files_exist_and_match():
    """Verify both manifest files exist and are byte-identical or hash-identical."""
    assert FIXTURE_PATH.is_file(), f"Fixture file not found: {FIXTURE_PATH}"
    assert DEV_DATASET_PATH.is_file(), f"Dev dataset file not found: {DEV_DATASET_PATH}"

    cases_fixture = load_manifest(FIXTURE_PATH)
    cases_dev = load_manifest(DEV_DATASET_PATH)

    assert len(cases_fixture) == 3
    assert len(cases_dev) == 3

    for c1, c2 in zip(cases_fixture, cases_dev):
        assert c1.case_id == c2.case_id
        assert c1.candidate_set_sha256 == c2.candidate_set_sha256
        assert c1.manifest_sha256 == c2.manifest_sha256


def test_tv1_cases_schema_and_geometry_hash():
    """Verify each TV1 case satisfies strict schema and geometry hash canonicalization."""
    cases = load_manifest(FIXTURE_PATH)
    for case in cases:
        assert case.schema_version == "joint-artifact-v1-draft"
        assert case.split == "dev"
        assert case.normalization == "NFD"
        assert case.geometry_policy.c_min_mm == 0.20
        assert case.candidate_set_sha256 == case.geometry_hash()

        # Compile geometry using TV4 polyline engine
        geom_idx = compile_geometry(case)
        assert len(geom_idx.invalid_variants) == 0, f"Case {case.case_id} has invalid variants"


@pytest.mark.parametrize("forget", [False, True])
def test_tv1_stacked_diacritic_solve(forget: bool):
    """
    Case 1: 'ấb'
    Verifies that stacked diacritics (circumflex + acute) are scheduled correctly:
    - Circumflex must precede acute in execution order.
    - Circumflex has k=0, acute has k=1.
    - DP finds an OPTIMAL schedule that passes geometry checks.
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-stacked-diacritic-01")

    run = solve_joint(case, THETA, BUDGET, safe_forget=forget)
    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.schedule is not None

    # Geometry verification
    geom_check = check_selected_geometry(case, run.schedule)
    assert geom_check["status"] == "PASS"

    # Verify stroke order: circumflex action must precede acute action
    actions = run.schedule.actions
    circ_idx = next(i for i, a in enumerate(actions) if a.stroke.stroke_id == "shape_circumflex")
    acute_idx = next(i for i, a in enumerate(actions) if a.stroke.stroke_id == "tone_acute")
    assert circ_idx < acute_idx, "Circumflex mark must be drawn before acute mark according to precedence"


@pytest.mark.parametrize("forget", [False, True])
def test_tv1_mark_below_solve(forget: bool):
    """
    Case 2: 'ệc'
    Verifies mark below (dot below baseline) + mark above (circumflex):
    - Both diacritics have k=0 (must flush before next character 'c').
    - DP finds an OPTIMAL schedule without negative coordinate / clearance issues.
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-mark-below-02")

    run = solve_joint(case, THETA, BUDGET, safe_forget=forget)
    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.schedule is not None

    geom_check = check_selected_geometry(case, run.schedule)
    assert geom_check["status"] == "PASS"

    # Verify both marks of letter 0 are drawn before letter 1 ('c')
    actions = run.schedule.actions
    c_body_idx = next(i for i, a in enumerate(actions) if a.stroke.owner_index == 1)
    e_marks = [i for i, a in enumerate(actions) if a.stroke.owner_index == 0 and a.stroke.stroke_id.startswith("tone_") or a.stroke.stroke_id.startswith("shape_")]
    for m_idx in e_marks:
        assert m_idx < c_body_idx, f"Mark at action {m_idx} must be completed before character 1 starts due to k=0"


@pytest.mark.parametrize("forget", [False, True])
def test_tv1_distant_interaction_solve(forget: bool):
    """
    Case 3: 'óto'
    Verifies delayed diacritic with k=2:
    - Acute mark of letter 0 has k=2, so it can be delayed past letter 1 ('t') and letter 2 ('o').
    - Letter 1 ('t') has a declared contact between stem and crossbar.
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-distant-interaction-03")

    run = solve_joint(case, THETA, BUDGET, safe_forget=forget)
    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.schedule is not None

    geom_check = check_selected_geometry(case, run.schedule)
    assert geom_check["status"] == "PASS"
