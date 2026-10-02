"""Hand-calculated DEV replay cases; not TV3 oracle or solver acceptance."""

from math import sqrt
from pathlib import Path

import pytest

from backend.research.schedule_checker import check_schedule_cost
from backend.research.schemas import ResearchCase, Schedule, Theta
from backend.research.service import load_manifest, ResearchService

FIXTURE = Path(__file__).parent / "fixtures" / "replay_dev_cases.json"
THETA = Theta(rho=0.5, lambda_mm=2.0)  # DEV arithmetic only; not theta0.


@pytest.fixture
def case():
    return load_manifest(FIXTURE)[0]


def action(owner, sid, transition="LIFT", orientation="forward", cid=None):
    return {"stroke": {"owner_index": owner, "candidate_id": cid or ("a-dev", "b-dev", "c-dev")[owner],
                       "stroke_id": sid}, "orientation": orientation, "transition": transition}


def schedule(case, actions=None, ids=None):
    return Schedule(candidate_ids=ids or ["a-dev", "b-dev", "c-dev"],
                    actions=actions if actions is not None else [
                        action(0, "b"), action(0, "shape"), action(0, "tone"),
                        action(1, "b1"), action(1, "b2", "CONNECT"), action(2, "b")],
                    boundary_convention_id=case.boundary.convention_id)


def reprepare(case, **updates):
    return ResearchCase.prepare(dict(case.model_dump(mode="json"), **updates))


def test_manifest_hand_calculation_and_no_acceptance_claim(case):
    result = check_schedule_cost(case, schedule(case), THETA)
    assert result.L_down_mm == 6
    assert result.L_up_mm == pytest.approx(3 + 4 * sqrt(2))
    assert result.N_cycle == 5
    assert result.J_mm == pytest.approx(17.5 + 2 * sqrt(2))
    assert sum(step.delta_J_mm for step in result.trace) == pytest.approx(result.J_mm)
    assert result.trace[-1].kind == "END"
    assert result.trace[-1].delta_cycles == 0
    assert result.trace[-1].endpoint_mm == case.boundary.p_end_mm
    assert result.geometric_validation == result.independent_validation == "NOT_RUN"
    assert result.trace[-1].assignments == ((0, "a-dev"), (1, "b-dev"), (2, "c-dev"))
    assert not any(ResearchService(load_manifest(FIXTURE)).capabilities()["methods"].values())


def test_lift_at_identical_endpoint_still_starts_cycle(case):
    base = schedule(case)
    connected = check_schedule_cost(case, base, THETA)
    base.actions[4].transition = "LIFT"
    lifted = check_schedule_cost(case, base, THETA)
    assert lifted.L_up_mm == connected.L_up_mm
    assert lifted.N_cycle == connected.N_cycle + 1
    assert lifted.J_mm == connected.J_mm + THETA.lambda_mm


def test_mark_can_interleave_multistroke_body_at_k1(case):
    actions = [action(0, "b"), action(1, "b1"), action(0, "shape"),
               action(0, "tone"), action(1, "b2"), action(2, "b")]
    result = check_schedule_cost(case, schedule(case, actions), THETA)
    assert (result.trace[1].i, result.trace[1].t) == (1, 1)
    assert (result.trace[2].i, result.trace[2].t) == (1, 1)
    assert len(result.trace[1].pending) == 2
    assert len(result.trace[2].pending) == 1


@pytest.mark.parametrize("k,qualified", [(0, False), (0, True), (1, False)])
def test_deadline_on_body_start_and_id_over_type(case, k, qualified):
    delay = {"dev-tone": 1 if qualified else k}
    if qualified:
        delay["0/a-dev/shape"] = k
    case = reprepare(case, delay_policy=delay)
    actions = [action(0, "b"), action(1, "b1"), action(1, "b2", "CONNECT"),
               action(2, "b"), action(0, "shape"), action(0, "tone")]
    with pytest.raises(ValueError, match="deadline"):
        check_schedule_cost(case, schedule(case, actions), THETA)


@pytest.mark.parametrize("k", [0, 1, 20])
def test_immediate_marks_allowed_for_every_delay(case, k):
    case = reprepare(case, delay_policy={"dev-tone": k})
    assert check_schedule_cost(case, schedule(case), THETA).N_cycle == 5


def test_deadline_beyond_word_still_allows_marks_before_end(case):
    case = reprepare(case, delay_policy={"dev-tone": 20})
    actions = [action(0, "b"), action(1, "b1"), action(1, "b2", "CONNECT"),
               action(2, "b"), action(0, "shape"), action(0, "tone")]
    result = check_schedule_cost(case, schedule(case, actions), THETA)
    assert len(result.trace[3].pending) == 2
    assert result.trace[-1].pending == ()


@pytest.mark.parametrize("order,message", [
    ([1, 0, 2, 3, 4, 5], "completed owner"),
    ([0, 2, 1, 3, 4, 5], "predecessor"),
    ([3, 0, 1, 2, 4, 5], "BODY"),
    ([0, 1, 2, 4, 3, 5], "BODY"),
    ([0, 1, 2, 3, 5, 4], "BODY"),
])
def test_temporal_violations(case, order, message):
    base = schedule(case)
    with pytest.raises(ValueError, match=message):
        check_schedule_cost(case, schedule(case, [base.actions[j] for j in order]), THETA)


def test_reverse_changes_endpoints_not_length(case):
    base = schedule(case)
    forward = check_schedule_cost(case, base, THETA)
    base.actions[-1].orientation = "reverse"
    reverse = check_schedule_cost(case, base, THETA)
    assert reverse.L_down_mm == forward.L_down_mm
    assert reverse.L_up_mm == forward.L_up_mm + 2
    assert reverse.trace[-2].endpoint_mm == (6, 0)


@pytest.mark.parametrize("mutation,message", [
    ("missing_contact", "explicit"), ("reverse", "endpoints"),
    ("location", "endpoints"),
    ("policy", "Unsupported"), ("case_policy", "Unsupported"),
])
def test_connect_is_whitelisted_and_exact_only(case, mutation, message):
    base = schedule(case)
    data = case.model_dump(mode="json")
    if mutation == "missing_contact":
        data["contacts"] = []
    elif mutation == "reverse":
        base.actions[4].orientation = "reverse"
    elif mutation == "location":
        data["contacts"][0]["location_mm"] = [4.001, 0]
    elif mutation == "policy":
        data["contacts"][0]["policy_id"] = "pending-policy"
    else:
        data["geometry_policy"]["contact_policy_id"] = "pending-policy"
    with pytest.raises(ValueError, match=message):
        check_schedule_cost(ResearchCase.prepare(data), base, THETA)


def test_mark_can_connect_with_explicit_contact(case):
    data = case.model_dump(mode="json")
    data["candidates"][0]["variants"][0]["strokes"][1]["polyline_mm"] = [[1, 0], [2, 0]]
    data["contacts"].append(dict(data["contacts"][0], first=action(0, "b")["stroke"],
                                 second=action(0, "shape")["stroke"], location_mm=[1, 0]))
    case = ResearchCase.prepare(data)
    base = schedule(case)
    base.actions[1].transition = "CONNECT"
    assert check_schedule_cost(case, base, THETA).N_cycle == 4


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "wrong_candidate", "boundary", "first_connect", "irreversible"])
def test_structural_checks_are_preserved(case, mutation):
    base = schedule(case)
    if mutation == "missing":
        base.actions.pop()
    elif mutation == "duplicate":
        base.actions.append(base.actions[0])
    elif mutation == "wrong_candidate":
        base.actions[0].stroke.candidate_id = "a-dev-alt"
    elif mutation == "boundary":
        base.boundary_convention_id = "unknown"
    elif mutation == "first_connect":
        base.actions[0].transition = "CONNECT"
    else:
        data = case.model_dump(mode="json")
        data["candidates"][2]["variants"][0]["strokes"][0]["reversible"] = False
        case = ResearchCase.prepare(data)
        base.actions[-1].orientation = "reverse"
    with pytest.raises(ValueError):
        check_schedule_cost(case, base, THETA)


def test_variant_choice_retained_without_mixing(case):
    base = schedule(case, ids=["a-dev-alt", "b-dev", "c-dev"])
    for a in base.actions[:3]:
        a.stroke.candidate_id = "a-dev-alt"
    result = check_schedule_cost(case, base, THETA)
    assert result.trace[-1].assignments[0] == (0, "a-dev-alt")
    assert result.L_down_mm == 6


def test_declared_zero_length_stroke_still_has_a_cycle(case):
    data = case.model_dump(mode="json")
    data["geometry_policy"]["allow_zero_length"] = True
    data["candidates"][2]["variants"][0]["strokes"][0]["polyline_mm"] = [[6, 0], [6, 0]]
    case = ResearchCase.prepare(data)
    result = check_schedule_cost(case, schedule(case), THETA)
    assert result.L_down_mm == 5
    assert result.N_cycle == 5


def test_replay_does_not_claim_clearance_for_overlapping_marks(case):
    data = case.model_dump(mode="json")
    variant = data["candidates"][0]["variants"][0]
    variant["strokes"][2]["polyline_mm"] = variant["strokes"][1]["polyline_mm"]
    case = ResearchCase.prepare(data)
    result = check_schedule_cost(case, schedule(case), THETA)
    assert result.geometric_validation == "NOT_RUN"
    assert result.independent_validation == "NOT_RUN"


@pytest.mark.parametrize("rho,lam", [(0.5, 0), (1, 2), (2, 7)])
def test_affine_cost_at_dev_parameters(case, rho, lam):
    result = check_schedule_cost(case, schedule(case), Theta(rho=rho, lambda_mm=lam))
    assert result.J_mm == pytest.approx(6 + rho * (3 + 4 * sqrt(2)) + lam * 5)


@pytest.mark.parametrize("coincident", [False, True])
def test_empty_case_has_only_up_travel_and_zero_cycles(coincident):
    case = load_manifest(FIXTURE)[1]
    if coincident:
        data = case.model_dump(mode="json")
        data["boundary"]["p_end_mm"] = [0, 0]
        case = ResearchCase.prepare(data)
    base = Schedule(candidate_ids=[], actions=[], boundary_convention_id=case.boundary.convention_id)
    result = check_schedule_cost(case, base, THETA)
    assert result.L_down_mm == result.N_cycle == 0
    assert result.L_up_mm == (0 if coincident else 5)
    assert result.J_mm == (0 if coincident else 2.5)
    assert len(result.trace) == 1


def test_revalidate_mutated_input_and_reject_float_overflow(case):
    case.candidate_set_sha256 = "f" * 64
    with pytest.raises(ValueError, match="hash mismatch"):
        check_schedule_cost(case, schedule(case), THETA)
    case = load_manifest(FIXTURE)[1]
    data = case.model_dump(mode="json")
    data["boundary"].update(p0_mm=[-1e308, 0], p_end_mm=[1e308, 0])
    case = ResearchCase.prepare(data)
    base = Schedule(candidate_ids=[], actions=[], boundary_convention_id=case.boundary.convention_id)
    with pytest.raises(ValueError, match="Non-finite"):
        check_schedule_cost(case, base, THETA)
