"""
Tests for TV1 Vietnamese Candidate Dataset and Fixtures (Docs 31/32).

Verifies:
1. Manifest integrity and byte/schema equality between DEV and fixtures.
2. Strict ResearchCase schema: NFD grapheme normalization (with multi-codepoint decomposing characters),
   stroke geometry, and canonical hashing.
3. TV4 geometry compilation: c_min floor 0.20 mm, self-intersection, declared contacts.
4. Feasibility and joint DP solve (exact frontier vs safe-forget) on realistic Vietnamese cases:
   - Stacked diacritics ('ấb': circumflex + acute precedence).
   - Mark below ('ệc': circumflex above + dot below baseline).
   - Distant interaction ('óto': multi-character word with declared contact and delay k=2).
5. Isolated enforcement of Vietnamese linguistic constraints:
   - Body order enforcement ('t_stem' before 't_crossbar').
   - Mark precedence isolation (negative test: swapping mark order raises ValueError).
   - Delay k deadline enforcement (positive with k=2, negative with k=0).
   - Stroke reversibility enforcement (both negative for non-reversible and positive for reversible).
"""

from pathlib import Path
import unicodedata
import pytest

from backend.research.geometry import compile_geometry, check_selected_geometry
from backend.research.joint_dp import solve_joint
from backend.research.schemas import (
    Budget,
    ResearchCase,
    Schedule,
    ScheduleAction,
    StrokeRef,
    Theta,
    check_schedule_structure,
)
from backend.research.schedule_checker import check_schedule_cost
from backend.research.service import load_manifest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "tv1_candidates_dev.json"
DEV_DATASET_PATH = Path(__file__).parent.parent.parent / "dataset" / "research" / "dev" / "tv1_dev_manifest.json"

BUDGET = Budget(wall_time_ms=10000, max_states=100000, max_configurations=10000, memory_limit_mb=64)
THETA = Theta(rho=0.5, lambda_mm=2.0)


def test_tv1_manifest_files_exist_and_match():
    """Verify both manifest files exist, hashes match, and payloads are identical."""
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
        assert len(c1.manifest_sha256) == 64
        assert c1.model_dump(mode="json") == c2.model_dump(mode="json"), (
            f"Case {c1.case_id} payload mismatch between fixture and dev manifest"
        )


def test_tv1_cases_schema_and_geometry_hash():
    """Verify each TV1 case satisfies strict schema, NFD graphemes, and geometry hash canonicalization."""
    cases = load_manifest(FIXTURE_PATH)
    for case in cases:
        assert case.schema_version == "joint-artifact-v1-draft"
        assert case.split == "dev"
        assert case.normalization == "NFD"
        assert unicodedata.is_normalized("NFD", case.normalized_text)

        for char in case.candidates:
            assert unicodedata.is_normalized("NFD", char.grapheme), (
                f"Grapheme '{char.grapheme}' in case {case.case_id} is not NFD normalized"
            )
            for var in char.variants:
                for stroke in var.strokes:
                    assert len(stroke.polyline_mm) >= 2
                    assert len(stroke.polyline_mm[0]) == 2

        # Explicit verification that Vietnamese diacritic characters decompose into multi-codepoint NFD sequences
        c0 = case.candidates[0]
        if case.case_id == "tv1-dev-stacked-diacritic-01":
            assert c0.grapheme == unicodedata.normalize("NFD", "ấ")
            assert len(c0.grapheme) == 3, "NFD 'ấ' must consist of base 'a' + circumflex (U+0302) + acute (U+0301)"
        elif case.case_id == "tv1-dev-mark-below-02":
            assert c0.grapheme == unicodedata.normalize("NFD", "ệ")
            assert len(c0.grapheme) == 3, "NFD 'ệ' must consist of base 'e' + circumflex (U+0302) + dot below (U+0323)"
        elif case.case_id == "tv1-dev-distant-interaction-03":
            assert c0.grapheme == unicodedata.normalize("NFD", "ó")
            assert len(c0.grapheme) == 2, "NFD 'ó' must consist of base 'o' + acute (U+0301)"

        assert case.geometry_policy.c_min_mm == 0.20
        assert case.candidate_set_sha256 == case.geometry_hash()

        # Compile geometry using TV4 polyline engine
        geom_idx = compile_geometry(case)
        assert len(geom_idx.invalid_variants) == 0, f"Case {case.case_id} has invalid variants"


@pytest.mark.parametrize("safe_forget", [False, True])
def test_tv1_stacked_diacritic_solve(safe_forget: bool):
    """
    Case 1: 'ấb'
    Verifies stacked diacritics (circumflex + acute) on letter 'a':
    - Circumflex must precede acute in execution order.
    - DP solver finds an OPTIMAL schedule that passes geometry checks.
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-stacked-diacritic-01")

    run = solve_joint(case, THETA, BUDGET, safe_forget=safe_forget)
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


def test_tv1_mark_precedence_isolated_enforcement():
    """
    Verifies that mark precedence is strictly enforced by schedule checker independent of delay k.
    Constructs a schedule with acute before circumflex on 'ấb' and asserts ValueError is raised.
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-stacked-diacritic-01")

    # Run solver to get a valid schedule
    run = solve_joint(case, THETA, BUDGET, safe_forget=False)
    assert run.schedule is not None

    # Invert the order of circumflex and acute
    circ_idx = next(i for i, a in enumerate(run.schedule.actions) if a.stroke.stroke_id == "shape_circumflex")
    acute_idx = next(i for i, a in enumerate(run.schedule.actions) if a.stroke.stroke_id == "tone_acute")

    inverted_actions = list(run.schedule.actions)
    inverted_actions[circ_idx], inverted_actions[acute_idx] = inverted_actions[acute_idx], inverted_actions[circ_idx]

    invalid_schedule = Schedule(
        candidate_ids=run.schedule.candidate_ids,
        actions=inverted_actions,
        boundary_convention_id=run.schedule.boundary_convention_id,
    )

    with pytest.raises(ValueError, match="MARK predecessor has not been drawn"):
        check_schedule_cost(case, invalid_schedule, THETA)


@pytest.mark.parametrize("safe_forget", [False, True])
def test_tv1_mark_below_solve(safe_forget: bool):
    """
    Case 2: 'ệc'
    Verifies mark below (dot below baseline) + mark above (circumflex):
    - Both diacritics have k=0 (must flush before next character 'c').
    - DP finds an OPTIMAL schedule without negative coordinate / clearance issues.
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-mark-below-02")

    run = solve_joint(case, THETA, BUDGET, safe_forget=safe_forget)
    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.schedule is not None

    geom_check = check_selected_geometry(case, run.schedule)
    assert geom_check["status"] == "PASS"

    # Verify both marks of letter 0 are drawn before letter 1 ('c')
    actions = run.schedule.actions
    c_body_idx = next(i for i, a in enumerate(actions) if a.stroke.owner_index == 1)
    e_marks = [
        i for i, a in enumerate(actions)
        if a.stroke.owner_index == 0 and (
            a.stroke.stroke_id.startswith("tone_") or a.stroke.stroke_id.startswith("shape_")
        )
    ]
    assert len(e_marks) == 2, "Letter 0 must have exactly two marks (circumflex and dot below)"
    for m_idx in e_marks:
        assert m_idx < c_body_idx, f"Mark at action {m_idx} must be completed before character 1 starts due to k=0"


@pytest.mark.parametrize("safe_forget", [False, True])
def test_tv1_distant_interaction_solve(safe_forget: bool):
    """
    Case 3: 'óto'
    Verifies:
    1. Solving multi-character word with DP (exact frontier vs safe-forget).
    2. Body order: 't_stem' must precede 't_crossbar' in execution.
    3. Contact enforcement: declared contact between 't_stem' and 't_crossbar'.
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-distant-interaction-03")

    run = solve_joint(case, THETA, BUDGET, safe_forget=safe_forget)
    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.schedule is not None

    geom_check = check_selected_geometry(case, run.schedule)
    assert geom_check["status"] == "PASS"

    actions = run.schedule.actions
    t_stem_idx = next(i for i, a in enumerate(actions) if a.stroke.stroke_id == "t_stem")
    t_crossbar_idx = next(i for i, a in enumerate(actions) if a.stroke.stroke_id == "t_crossbar")

    # 1. Body order verification
    assert t_stem_idx < t_crossbar_idx, "t_stem must precede t_crossbar according to body_order"

    # 2. Contact verification
    assert len(case.contacts) == 1
    contact = case.contacts[0]
    assert list(contact.location_mm) == [3.0, 3.5]


def test_tv1_delay_k_deadline_enforcement():
    """
    Isolates and verifies the delay k deadline semantics (Docs 31 §2):
    - With k=2 on 'tv1-dev-distant-interaction-03', delaying acute mark of letter 0
      past letter 1 ('t_stem' and 't_crossbar') is fully VALID.
    - If k=0 is imposed on the acute mark, the exact same delayed schedule raises
      ValueError('Pending MARK deadline forbids starting this BODY').
    """
    cases = load_manifest(FIXTURE_PATH)
    case_k2 = next(c for c in cases if c.case_id == "tv1-dev-distant-interaction-03")

    # Construct an explicit schedule where letter 0's mark is delayed past letter 1:
    # 0: o_body (char 0)
    # 1: t_stem (char 1)
    # 2: t_crossbar (char 1)
    # 3: tone_acute (char 0, delayed!)
    # 4: o_body (char 2)
    delayed_actions = [
        ScheduleAction(stroke=StrokeRef(owner_index=0, candidate_id="o-std", stroke_id="o_body"),
                       orientation="forward", transition="LIFT"),
        ScheduleAction(stroke=StrokeRef(owner_index=1, candidate_id="t-std", stroke_id="t_stem"),
                       orientation="forward", transition="LIFT"),
        ScheduleAction(stroke=StrokeRef(owner_index=1, candidate_id="t-std", stroke_id="t_crossbar"),
                       orientation="forward", transition="LIFT"),
        ScheduleAction(stroke=StrokeRef(owner_index=0, candidate_id="o-std", stroke_id="tone_acute"),
                       orientation="forward", transition="LIFT"),
        ScheduleAction(stroke=StrokeRef(owner_index=2, candidate_id="o2-std", stroke_id="o_body"),
                       orientation="forward", transition="LIFT"),
    ]
    delayed_schedule = Schedule(
        candidate_ids=["o-std", "t-std", "o2-std"],
        actions=delayed_actions,
        boundary_convention_id=case_k2.boundary.convention_id,
    )

    # 1. Under k=2, this delayed schedule must PASS replay checker
    replay = check_schedule_cost(case_k2, delayed_schedule, THETA)
    assert replay.J_mm > 0.0

    # 2. Under k=0, starting character 1 ('t_stem') with pending mark on char 0 must FAIL
    k0_data = case_k2.model_dump(mode="json")
    assert "tv1-acute-distant" in k0_data["delay_policy"], "Key 'tv1-acute-distant' must exist in delay_policy"
    k0_data["delay_policy"]["tv1-acute-distant"] = 0
    # ResearchCase.prepare recalculates canonical geometry_hash
    k0_case = ResearchCase.prepare(k0_data)

    with pytest.raises(ValueError, match="Pending MARK deadline forbids starting this BODY"):
        check_schedule_cost(k0_case, delayed_schedule, THETA)


def test_tv1_stroke_reversibility_enforcement():
    """
    Verifies stroke reversibility contract:
    - Attempting to reverse a non-reversible stroke raises ValueError in check_schedule_structure.
    - Reversible strokes can be executed in reverse orientation without error.
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-stacked-diacritic-01")

    run = solve_joint(case, THETA, BUDGET, safe_forget=False)
    assert run.schedule is not None

    # Negative test: 'a_body' is non-reversible (reversible=False)
    a_body_idx = next(i for i, a in enumerate(run.schedule.actions) if a.stroke.stroke_id == "a_body")
    invalid_actions = list(run.schedule.actions)
    bad_action = ScheduleAction(
        stroke=invalid_actions[a_body_idx].stroke,
        orientation="reverse",  # illegal for a_body
        transition=invalid_actions[a_body_idx].transition,
    )
    invalid_actions[a_body_idx] = bad_action

    illegal_schedule = Schedule(
        candidate_ids=run.schedule.candidate_ids,
        actions=invalid_actions,
        boundary_convention_id=run.schedule.boundary_convention_id,
    )

    with pytest.raises(ValueError, match="Schedule reverses a non-reversible stroke"):
        check_schedule_structure(case, illegal_schedule)

    # Positive test: 'shape_circumflex' is reversible (reversible=True)
    circ_idx = next(i for i, a in enumerate(run.schedule.actions) if a.stroke.stroke_id == "shape_circumflex")
    valid_reversed_actions = list(run.schedule.actions)
    valid_reversed_actions[circ_idx] = ScheduleAction(
        stroke=valid_reversed_actions[circ_idx].stroke,
        orientation="reverse",  # legal for reversible stroke
        transition=valid_reversed_actions[circ_idx].transition,
    )
    valid_schedule = Schedule(
        candidate_ids=run.schedule.candidate_ids,
        actions=valid_reversed_actions,
        boundary_convention_id=run.schedule.boundary_convention_id,
    )
    # Must validate structure without error
    check_schedule_structure(case, valid_schedule)
