"""
Tests for TV1 Vietnamese Candidate Dataset and Fixtures (Docs 31/32).

Verifies TV4 Review Requirements (F1–F6):
1. Manifest integrity and byte/schema equality between DEV and fixtures across all 4 cases.
2. Strict ResearchCase schema: NFD grapheme normalization (multi-codepoint sequences),
   stroke validity, c_min floor 0.20 mm, and canonical geometry hashing.
3. Exact J replay values and feasibility on:
   - Case 1: Stacked diacritics ('ấb': circumflex + acute precedence).
   - Case 2: Mark below ('ệc': circumflex above + dot below baseline).
   - Case 3: Delayed mark multi-body ('óto': deadline k=2 allows delaying diacritic past 2 bodies).
   - Case 4: True distant interaction ('óto': incompatible variant pair between owner 0 and 2,
     non-empty future_neighbors edge {0: {2}, 2: {0}}, safe-forget frontier retention).
4. Isolated linguistic and solver constraints:
   - Mark precedence isolation (F3: negative swap test).
   - Delay k boundary isolation (F3: probe schedule distinguishing k=2 vs k=1 vs k=0).
   - True distant interaction and frontier pruning (F4: incompatible pair pruning, safe-forget vs no-forget agreement).
   - Contact whitelist vs CONNECT traversal (F5: positive CONNECT with zero-cycle/zero-up, negative whitelist and mismatch).
   - Stroke reversibility enforcement (positive and negative).
"""

from pathlib import Path
import unicodedata
import pytest

from backend.research.geometry import (
    FLATTEN_POLICY,
    NUMERIC_POLICY,
    SEPARATION_POLICY,
    compile_geometry,
    check_selected_geometry,
)
from backend.research.joint_dp import solve_joint
from backend.research.schemas import (
    Budget,
    Character,
    Contact,
    GeometryPolicy,
    ResearchCase,
    Schedule,
    ScheduleAction,
    Stroke,
    StrokeRef,
    Theta,
    Variant,
    canonical_hash,
    check_schedule_structure,
)
from backend.research.schedule_checker import EXACT_CONTACT_POLICY, check_schedule_cost
from backend.research.service import load_manifest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "tv1_candidates_dev.json"
DEV_DATASET_PATH = Path(__file__).parent.parent.parent / "dataset" / "research" / "dev" / "tv1_dev_manifest.json"

BUDGET = Budget(wall_time_ms=10000, max_states=100000, max_configurations=10000, memory_limit_mb=64)
THETA = Theta(rho=0.5, lambda_mm=2.0)


def test_tv1_manifest_files_exist_and_match():
    """Verify both manifest files exist, hashes match, and payloads are identical (F1/F2)."""
    assert FIXTURE_PATH.is_file(), f"Fixture file not found: {FIXTURE_PATH}"
    assert DEV_DATASET_PATH.is_file(), f"Dev dataset file not found: {DEV_DATASET_PATH}"

    cases_fixture = load_manifest(FIXTURE_PATH)
    cases_dev = load_manifest(DEV_DATASET_PATH)

    assert len(cases_fixture) == 4
    assert len(cases_dev) == 4

    for c1, c2 in zip(cases_fixture, cases_dev):
        assert c1.case_id == c2.case_id
        assert c1.candidate_set_sha256 == c2.candidate_set_sha256
        assert c1.manifest_sha256 == c2.manifest_sha256
        assert len(c1.manifest_sha256) == 64
        assert c1.model_dump(mode="json") == c2.model_dump(mode="json"), (
            f"Case {c1.case_id} payload mismatch between fixture and dev manifest"
        )


def test_tv1_cases_schema_and_geometry_hash():
    """Verify each TV1 case satisfies strict schema, NFD graphemes, and geometry hash canonicalization (F2)."""
    cases = load_manifest(FIXTURE_PATH)
    for case in cases:
        assert case.schema_version == "joint-artifact-v1-draft"
        assert case.split == "dev"
        assert case.normalization == "NFD"
        assert unicodedata.is_normalized("NFD", case.normalized_text)
        assert case.reference_geometry is None, "DEV synthetic cases must declare reference_geometry=None"

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
        elif case.case_id in {"tv1-dev-distant-interaction-03", "tv1-dev-distant-interaction-04"}:
            assert c0.grapheme == unicodedata.normalize("NFD", "ó")
            assert len(c0.grapheme) == 2, "NFD 'ó' must consist of base 'o' + acute (U+0301)"
        else:
            pytest.fail(f"Unexpected case_id in TV1 manifest: {case.case_id}")

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
    - Verifies exact replay cost J_mm matching TV4 evidence (F1).
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-stacked-diacritic-01")

    run = solve_joint(case, THETA, BUDGET, safe_forget=safe_forget)
    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.schedule is not None
    assert abs(run.replay.J_mm - 27.746604752708503) < 1e-6
    assert run.replay.N_cycle == 4

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

    run = solve_joint(case, THETA, BUDGET, safe_forget=False)
    assert run.schedule is not None

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
    - Verifies exact replay cost J_mm matching TV4 evidence (F1).
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-mark-below-02")

    run = solve_joint(case, THETA, BUDGET, safe_forget=safe_forget)
    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.schedule is not None
    assert abs(run.replay.J_mm - 26.658710256581244) < 1e-6
    assert run.replay.N_cycle == 4

    geom_check = check_selected_geometry(case, run.schedule)
    assert geom_check["status"] == "PASS"

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
def test_tv1_delayed_mark_solve(safe_forget: bool):
    """
    Case 3: 'óto' (Delayed Mark & Multi-Body Fixture)
    Verifies:
    1. Multi-character word with DP: exact replay cost J_mm matches TV4 evidence (F1).
    2. Body order: 't_stem' must precede 't_crossbar' in execution.
    3. Contact clearance whitelist: declared contact between 't_stem' and 't_crossbar' at [3.0, 3.5].
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-distant-interaction-03")

    run = solve_joint(case, THETA, BUDGET, safe_forget=safe_forget)
    assert run.outcome == "OPTIMAL"
    assert run.search_complete is True
    assert run.schedule is not None
    assert abs(run.replay.J_mm - 33.972504012143716) < 1e-6
    assert run.replay.N_cycle == 5

    geom_check = check_selected_geometry(case, run.schedule)
    assert geom_check["status"] == "PASS"

    actions = run.schedule.actions
    t_stem_idx = next(i for i, a in enumerate(actions) if a.stroke.stroke_id == "t_stem")
    t_crossbar_idx = next(i for i, a in enumerate(actions) if a.stroke.stroke_id == "t_crossbar")

    assert t_stem_idx < t_crossbar_idx, "t_stem must precede t_crossbar according to body_order"
    assert len(case.contacts) == 1
    contact = case.contacts[0]
    assert list(contact.location_mm) == [3.0, 3.5]


def test_tv1_delay_k_two_body_boundary():
    """
    Isolates and strictly verifies delay k boundary distinguishing k=2 from k=1 and k=0 (F3):
    - Construct probe schedule where letter 0's mark is drawn AFTER both letter 1 AND letter 2 bodies:
      body0 -> t_stem (1) -> t_crossbar (1) -> body2 (2) -> tone0 (0)
    - With k=2: Deadline is 0 + 2 + 1 = 3. Body 2 starts at i=2 < 3. Schedule must PASS!
    - With k=1: Deadline is 0 + 1 + 1 = 2. Body 2 starts at i=2 <= 2. Schedule must FAIL!
    - With k=0: Deadline is 0 + 0 + 1 = 1. Body 1 starts at i=1 <= 1. Schedule must FAIL!
    """
    cases = load_manifest(FIXTURE_PATH)
    case_k2 = next(c for c in cases if c.case_id == "tv1-dev-distant-interaction-03")

    probe_actions = [
        ScheduleAction(stroke=StrokeRef(owner_index=0, candidate_id="o-std", stroke_id="o_body"),
                       orientation="forward", transition="LIFT"),
        ScheduleAction(stroke=StrokeRef(owner_index=1, candidate_id="t-std", stroke_id="t_stem"),
                       orientation="forward", transition="LIFT"),
        ScheduleAction(stroke=StrokeRef(owner_index=1, candidate_id="t-std", stroke_id="t_crossbar"),
                       orientation="forward", transition="LIFT"),
        ScheduleAction(stroke=StrokeRef(owner_index=2, candidate_id="o2-std", stroke_id="o_body"),
                       orientation="forward", transition="LIFT"),
        ScheduleAction(stroke=StrokeRef(owner_index=0, candidate_id="o-std", stroke_id="tone_acute"),
                       orientation="forward", transition="LIFT"),
    ]
    delayed_schedule = Schedule(
        candidate_ids=["o-std", "t-std", "o2-std"],
        actions=probe_actions,
        boundary_convention_id=case_k2.boundary.convention_id,
    )

    # 1. k=2: PASS
    replay = check_schedule_cost(case_k2, delayed_schedule, THETA)
    assert replay.J_mm > 0.0

    # 2. k=1: FAIL (Pending MARK deadline forbids starting this BODY at character 2)
    k1_data = case_k2.model_dump(mode="json")
    assert "tv1-acute-distant" in k1_data["delay_policy"]
    k1_data["delay_policy"]["tv1-acute-distant"] = 1
    k1_case = ResearchCase.prepare(k1_data)
    with pytest.raises(ValueError, match="Pending MARK deadline forbids starting this BODY"):
        check_schedule_cost(k1_case, delayed_schedule, THETA)

    # 3. k=0: FAIL (Pending MARK deadline forbids starting this BODY at character 1)
    k0_data = case_k2.model_dump(mode="json")
    k0_data["delay_policy"]["tv1-acute-distant"] = 0
    k0_case = ResearchCase.prepare(k0_data)
    with pytest.raises(ValueError, match="Pending MARK deadline forbids starting this BODY"):
        check_schedule_cost(k0_case, delayed_schedule, THETA)


def test_tv1_distant_interaction_frontier_and_solve():
    """
    Case 4: 'óto' (True Distant Geometric Interaction - F4)
    Verifies:
    1. Interaction graph has non-empty distant edge:
       2 in future_neighbors[0] and 0 in future_neighbors[2].
    2. Incompatible candidate pair is detected: (0, 'o-swash') and (2, 'o2-flourish') < 0.20 mm.
    3. DP solver prunes incompatible pair, and both safe-forget and no-forget modes agree on
       the OPTIMAL schedule and value J_mm = 25.918342316257434.
    """
    cases = load_manifest(FIXTURE_PATH)
    case = next(c for c in cases if c.case_id == "tv1-dev-distant-interaction-04")

    # 1. Verify interaction graph and incompatible set
    geom_idx = compile_geometry(case)
    assert 2 in geom_idx.future_neighbors[0], "Owner 0 must have future neighbor 2 across intervening letter 1"
    assert 0 in geom_idx.future_neighbors[2], "Owner 2 must have neighbor 0"
    assert 1 not in geom_idx.future_neighbors[0], "Owner 1 should have no clearance conflict with owner 0"

    incompatible_pairs = geom_idx.incompatible
    assert frozenset({(0, "o-swash"), (2, "o2-flourish")}) in incompatible_pairs, (
        "Expected (0, 'o-swash') and (2, 'o2-flourish') to collide within c_min floor 0.20 mm"
    )

    # 2. Verify DP solve in both modes
    run_no = solve_joint(case, THETA, BUDGET, safe_forget=False)
    run_safe = solve_joint(case, THETA, BUDGET, safe_forget=True)

    assert run_no.outcome == "OPTIMAL"
    assert run_safe.outcome == "OPTIMAL"
    assert run_no.schedule.candidate_ids == ["o-compact", "t-std", "o2-compact"]
    assert run_safe.schedule.candidate_ids == ["o-compact", "t-std", "o2-compact"]
    assert abs(run_no.replay.J_mm - 25.918342316257434) < 1e-6
    assert abs(run_safe.replay.J_mm - 25.918342316257434) < 1e-6


def test_tv1_contact_and_connect_traversal():
    """
    Isolates and verifies declared contact whitelist vs CONNECT execution traversal (F5):
    - Traversal with matching endpoint executes CONNECT with delta_up_mm=0, delta_cycles=0.
    - Missing contact from whitelist raises ValueError('CONNECT requires an explicit stroke-pair contact').
    - Endpoint mismatch raises ValueError('CONNECT endpoints must equal the declared contact location').
    """
    geom_policy = GeometryPolicy(
        c_min_mm=0.20,
        flatten_policy_id=FLATTEN_POLICY,
        contact_policy_id=EXACT_CONTACT_POLICY,
        numeric_policy_id=NUMERIC_POLICY,
        separation_policy_id=SEPARATION_POLICY,
        allow_zero_length=False,
    )

    # Construct clean CONNECT test case: stem goes upwards to [3.0, 3.5], crossbar starts at [3.0, 3.5]
    stem_up = Stroke(stroke_id="stem", role="body", owner_index=0, reversible=False,
                     polyline_mm=[[3.0, 0.0], [3.0, 3.5]])
    bar = Stroke(stroke_id="bar", role="body", owner_index=0, reversible=False,
                 polyline_mm=[[3.0, 3.5], [3.8, 3.5]])

    contact = Contact(
        first=StrokeRef(owner_index=0, candidate_id="t-std", stroke_id="stem"),
        second=StrokeRef(owner_index=0, candidate_id="t-std", stroke_id="bar"),
        location_mm=[3.0, 3.5],
        radius_mm=0.25,
        policy_id=EXACT_CONTACT_POLICY,
    )

    char_t = Character(
        owner_index=0,
        grapheme=unicodedata.normalize("NFD", "t"),
        variants=[
            Variant(candidate_id="t-std", source_hash=canonical_hash("t-connect-fixture"),
                    strokes=[stem_up, bar], body_order=["stem", "bar"], mark_precedence=[]),
        ],
    )

    case_connect = ResearchCase.prepare({
        "schema_version": "joint-artifact-v1-draft",
        "case_id": "tv1-dev-connect-fixture",
        "dataset_version": "tv1-vietnamese-dev-v1",
        "manifest_sha256": "0" * 64,
        "split": "dev",
        "original_text": "t",
        "normalized_text": unicodedata.normalize("NFD", "t"),
        "normalization": "NFD",
        "candidates": [char_t.model_dump(mode="json")],
        "contacts": [contact.model_dump(mode="json")],
        "separation_pairs": [],
        "delay_policy": {},
        "geometry_policy": geom_policy.model_dump(mode="json"),
        "boundary": {"p0_mm": [-1.0, 0.0], "p_end_mm": [5.0, 0.0], "initial_pen": "UP", "final_pen": "UP",
                     "convention_id": "tv1-origin-margin-v1"},
        "reference_geometry": None,
    })

    # 1. Positive: valid CONNECT schedule
    actions_connect = [
        ScheduleAction(stroke=StrokeRef(owner_index=0, candidate_id="t-std", stroke_id="stem"),
                       orientation="forward", transition="LIFT"),
        ScheduleAction(stroke=StrokeRef(owner_index=0, candidate_id="t-std", stroke_id="bar"),
                       orientation="forward", transition="CONNECT"),
    ]
    sched_connect = Schedule(candidate_ids=["t-std"], actions=actions_connect,
                             boundary_convention_id="tv1-origin-margin-v1")
    replay = check_schedule_cost(case_connect, sched_connect, THETA)
    assert replay.N_cycle == 1, "CONNECT must avoid a pen-up cycle between touching strokes"
    # Action 1 (bar) must have zero up travel and zero cycles
    step_bar = replay.trace[1]
    assert step_bar.transition == "CONNECT"
    assert step_bar.delta_up_mm == 0.0
    assert step_bar.delta_cycles == 0

    # 2. Negative: missing contact from whitelist
    case_no_contact = ResearchCase.prepare({
        "schema_version": "joint-artifact-v1-draft",
        "case_id": "tv1-dev-connect-fixture-neg1",
        "dataset_version": "tv1-vietnamese-dev-v1",
        "manifest_sha256": "0" * 64,
        "split": "dev",
        "original_text": "t",
        "normalized_text": unicodedata.normalize("NFD", "t"),
        "normalization": "NFD",
        "candidates": [char_t.model_dump(mode="json")],
        "contacts": [],  # no contact declared
        "separation_pairs": [],
        "delay_policy": {},
        "geometry_policy": geom_policy.model_dump(mode="json"),
        "boundary": {"p0_mm": [-1.0, 0.0], "p_end_mm": [5.0, 0.0], "initial_pen": "UP", "final_pen": "UP",
                     "convention_id": "tv1-origin-margin-v1"},
        "reference_geometry": None,
    })
    with pytest.raises(ValueError, match="CONNECT requires an explicit stroke-pair contact"):
        check_schedule_cost(case_no_contact, sched_connect, THETA)

    # 3. Negative: endpoint mismatch (bar starts at [3.1, 3.5] instead of [3.0, 3.5])
    bar_mismatch = Stroke(stroke_id="bar", role="body", owner_index=0, reversible=False,
                          polyline_mm=[[3.1, 3.5], [3.8, 3.5]])
    char_t_mismatch = Character(
        owner_index=0,
        grapheme=unicodedata.normalize("NFD", "t"),
        variants=[
            Variant(candidate_id="t-std", source_hash=canonical_hash("t-connect-fixture-neg2"),
                    strokes=[stem_up, bar_mismatch], body_order=["stem", "bar"], mark_precedence=[]),
        ],
    )
    case_mismatch = ResearchCase.prepare({
        "schema_version": "joint-artifact-v1-draft",
        "case_id": "tv1-dev-connect-fixture-neg2",
        "dataset_version": "tv1-vietnamese-dev-v1",
        "manifest_sha256": "0" * 64,
        "split": "dev",
        "original_text": "t",
        "normalized_text": unicodedata.normalize("NFD", "t"),
        "normalization": "NFD",
        "candidates": [char_t_mismatch.model_dump(mode="json")],
        "contacts": [contact.model_dump(mode="json")],
        "separation_pairs": [],
        "delay_policy": {},
        "geometry_policy": geom_policy.model_dump(mode="json"),
        "boundary": {"p0_mm": [-1.0, 0.0], "p_end_mm": [5.0, 0.0], "initial_pen": "UP", "final_pen": "UP",
                     "convention_id": "tv1-origin-margin-v1"},
        "reference_geometry": None,
    })
    with pytest.raises(ValueError, match="CONNECT endpoints must equal the declared contact location"):
        check_schedule_cost(case_mismatch, sched_connect, THETA)


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
