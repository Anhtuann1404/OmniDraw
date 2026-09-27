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
