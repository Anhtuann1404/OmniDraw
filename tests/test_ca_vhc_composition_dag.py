"""E4 transition and PR3 trellis tests; B3 remains on its existing path."""

import numpy as np
import pytest

from backend.handwriting import composition
from backend.handwriting.composition import (
    CONTRACT_VERSION, CompositionState, DiacriticConfig, GlyphWorldGeometry,
    NoValidPathError, TransitionEvaluationError, TransitionResult, TransitionWeights,
    evaluate_composition_transition, optimize_composition_dag, transform_state_to_world,
)
from backend.handwriting.engine import GlyphVariant


def _state(x, *, can_in=True, can_out=True, legibility=0.):
    stroke = np.array([[x, 0.], [x + 1., 0.]])
    base = GlyphVariant([stroke], stroke[0], stroke[-1], [1., 0.], [1., 0.],
                        can_in, can_out, legibility, f"at_{x}")
    state = CompositionState(base, None, "a", (), {}, base.tag, 0., legibility, {})
    return state, transform_state_to_world(state, [1., 1.], [0., 0.])


def _with_stroke(world, stroke, *, mark=False, prepend=False):
    return GlyphWorldGeometry(
        world.base_strokes if mark else ((stroke,) + world.base_strokes if prepend
                                         else world.base_strokes + (stroke,)),
        world.diacritic_strokes + (stroke,) if mark else world.diacritic_strokes,
        world.entry_pt, world.exit_pt, world.v_entry, world.v_exit,
        world.diacritic_bbox,
    )


def _transition(prev_world, curr_world, *, clearance=0.2, prev_x=0., curr_x=3.):
    prev, _ = _state(prev_x)
    curr, _ = _state(curr_x)
    return evaluate_composition_transition(
        prev, curr, prev_world, curr_world,
        TransitionWeights(w_penup=0., w_lift=100., w_curvature=0., w_bridge_collision=0.),
        DiacriticConfig(clearance_threshold_mm=clearance),
    )


def test_bridge_body_crossing_is_hard_invalid_even_with_zero_collision_weight():
    _, prev = _state(0.)
    _, curr = _state(3.)
    crossing = np.array([[2., -1.], [2., 1.]])
    assert _transition(_with_stroke(prev, crossing, prepend=True), curr).decision == "LIFT"
    assert _transition(prev, _with_stroke(curr, crossing)).decision == "LIFT"


def test_bridge_anchor_exemption_belongs_to_correct_glyph_only():
    _, prev = _state(0.)
    _, curr = _state(3.)
    assert _transition(prev, curr).decision == "CONNECT"
    wrong_exit = np.array([[1., 0.], [1., 1.]])
    wrong_entry = np.array([[3., 0.], [3., 1.]])
    assert _transition(prev, _with_stroke(curr, wrong_exit)).decision == "LIFT"
    assert _transition(_with_stroke(prev, wrong_entry, prepend=True), curr).decision == "LIFT"


def test_bridge_off_port_touch_and_exit_overlap_are_not_exempt():
    _, prev = _state(0.)
    _, curr = _state(3.)
    off_port_touch = np.array([[2., 0.], [2., 1.]])
    assert _transition(prev, _with_stroke(curr, off_port_touch)).decision == "LIFT"
    overlap_at_exit = GlyphWorldGeometry(
        (np.array([[1.5, 0.], [1., 0.]]),), prev.diacritic_strokes,
        prev.entry_pt, prev.exit_pt, prev.v_entry, prev.v_exit, prev.diacritic_bbox,
    )
    assert _transition(overlap_at_exit, curr).decision == "LIFT"


def test_near_port_overlap_at_large_coordinates_is_not_exempt():
    _, prev = _state(99.)
    _, curr = _state(102.)
    shifted_exit = GlyphWorldGeometry(
        (np.array([[99., 0.], [100.0005, 0.]]),), prev.diacritic_strokes,
        prev.entry_pt, prev.exit_pt, prev.v_entry, prev.v_exit, prev.diacritic_bbox,
    )
    assert _transition(shifted_exit, curr, prev_x=99., curr_x=102.).decision == "LIFT"


@pytest.mark.parametrize("mark", [
    np.array([[2., -1.], [2., 1.]]),
    np.array([[2., 0.], [2., 1.]]),
])
@pytest.mark.parametrize("owner", ["prev", "curr"])
def test_bridge_mark_cross_or_touch_is_hard_invalid_at_zero_clearance(mark, owner):
    _, prev = _state(0.)
    _, curr = _state(3.)
    if owner == "prev":
        prev = _with_stroke(prev, mark, mark=True)
    else:
        curr = _with_stroke(curr, mark, mark=True)
    assert _transition(prev, curr, clearance=0.).decision == "LIFT"


def test_transition_connect_has_finite_breakdown_and_immutable_bridge():
    prev, prev_world = _state(0.)
    curr, curr_world = _state(3.)
    result = evaluate_composition_transition(prev, curr, prev_world, curr_world,
                                             TransitionWeights(), DiacriticConfig())
    assert result.contract_version == CONTRACT_VERSION
    assert result.decision == "CONNECT" and result.is_valid
    assert result.breakdown.total_cost == result.total_cost
    assert result.breakdown.n_lift == 0
    with pytest.raises(ValueError):
        result.bridge_strokes[0][0, 0] = 42.


def test_transition_lift_does_not_count_legibility_again():
    prev, prev_world = _state(0., can_out=False)
    curr, curr_world = _state(3., legibility=50.)
    result = evaluate_composition_transition(prev, curr, prev_world, curr_world,
                                             TransitionWeights(), DiacriticConfig())
    assert result.decision == "LIFT" and result.bridge_strokes is None
    assert result.total_cost == pytest.approx(5.)
    assert result.breakdown.n_lift == 1


@pytest.mark.parametrize("can_out, expected_decision", [(True, "CONNECT"), (False, "LIFT")])
def test_nondefault_transition_weights_and_dag_count_each_state_once(can_out, expected_decision):
    prev, prev_world = _state(0., can_out=can_out, legibility=7.)
    curr, curr_world = _state(3., legibility=11.)
    weights = TransitionWeights(w_penup=3., w_lift=17., w_curvature=5., w_bridge_collision=2.)
    transition = evaluate_composition_transition(prev, curr, prev_world, curr_world,
                                                 weights, DiacriticConfig())
    assert transition.decision == expected_decision
    if can_out:
        expected = (weights.w_curvature * transition.breakdown.c_curvature +
                    weights.w_bridge_collision * transition.breakdown.c_bridge_collision)
    else:
        expected = weights.w_penup * 2. + weights.w_lift
    assert transition.total_cost == pytest.approx(expected)
    path = optimize_composition_dag((((prev, prev_world),), ((curr, curr_world),)),
                                    weights, DiacriticConfig())
    assert path["total_cost"] == pytest.approx(7. + 11. + expected)


def test_transition_reject_and_computational_error_are_distinct():
    prev, prev_world = _state(0.)
    curr, curr_world = _state(3.)
    crossing = GlyphWorldGeometry(curr_world.base_strokes,
                                  (np.array([[3., -1.], [3., 1.]]),),
                                  curr_world.entry_pt, curr_world.exit_pt,
                                  curr_world.v_entry, curr_world.v_exit, (3., -1., 3., 1.))
    # State/internal geometry hard rejection is separate from a numeric error.
    reject = evaluate_composition_transition(prev, curr, prev_world, crossing,
                                             TransitionWeights(), DiacriticConfig())
    assert reject.decision == "REJECT" and not reject.is_valid
    assert reject.total_cost == float("inf")
    assert reject.breakdown is None and reject.bridge_strokes is None and reject.reject_reason
    malformed = object.__new__(GlyphWorldGeometry)
    object.__setattr__(malformed, "entry_pt", np.array([np.nan, 0.]))
    for name in ("exit_pt", "v_entry", "v_exit"):
        object.__setattr__(malformed, name, getattr(curr_world, name))
    with pytest.raises(TransitionEvaluationError):
        evaluate_composition_transition(prev, curr, prev_world, malformed,
                                        TransitionWeights(), DiacriticConfig())


def test_viterbi_synthetic_trellis_optimality(monkeypatch):
    a, b = _state(0.), _state(0., legibility=1.)
    c, d = _state(2.), _state(2., legibility=1.)
    e = _state(4.)

    def known_cost(prev, curr, *_args):
        # The locally cheapest first node is a; globally b -> d -> e wins.
        matrix = {(id(a[0]), id(c[0])): 10., (id(a[0]), id(d[0])): 10.,
                  (id(b[0]), id(c[0])): 10., (id(b[0]), id(d[0])): 0.,
                  (id(c[0]), id(e[0])): 10., (id(d[0]), id(e[0])): 0.}
        cost = matrix[(id(prev), id(curr))]
        return TransitionResult(CONTRACT_VERSION, True, "LIFT", cost,
                                composition.TransitionCostBreakdown(0., 1, 0., 0., cost))

    monkeypatch.setattr(composition, "evaluate_composition_transition", known_cost)
    result = optimize_composition_dag(((a, b), (c, d), (e,)))
    assert result["states"] == (b[0], d[0], e[0])
    assert result["total_cost"] == pytest.approx(2.)
    assert len(result["transitions"]) == 2


def test_empty_layer_has_explicit_failure():
    with pytest.raises(NoValidPathError):
        optimize_composition_dag(((_state(0.),), ()))
