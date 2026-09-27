"""PR3 Slice 1: candidate generation remains separate from the default solver."""

from dataclasses import FrozenInstanceError
from types import SimpleNamespace
import numpy as np
import pytest

from backend.handwriting.composition import (
    CompositionGeometryError, DiacriticConfig, GlyphWorldGeometry, NoValidCompositionState,
    build_composition_states, evaluate_composition_state,
    generate_diacritic_candidates, prune_composition_states, transform_state_to_world,
)
from backend.handwriting.engine import generate_accents, get_glyph_variants


def _variants(char="e"):
    return get_glyph_variants(char, [np.array([[0., 10.], [4., 7.]])])


def test_composition_state_without_accent():
    states = build_composition_states("e", (), _variants(), 2.0)
    assert len(states) == len(_variants())
    assert all(s.diacritic_candidate is None for s in states)


@pytest.mark.parametrize("marks", [("\u0301",), ("\u0302", "\u0301"),
                                    ("\u031b", "\u0309"), ("\u0323",)])
def test_candidate_generation_uses_existing_accent_geometry(marks):
    candidates = generate_diacritic_candidates("e", marks, 2.0)
    assert [c.placement_tag for c in candidates] == ["canonical", "safe_left", "safe_right"]
    canonical = generate_accents("e", marks, 2.0)
    assert len(candidates[0].strokes_local) == len(canonical)
    for actual, expected in zip(candidates[0].strokes_local, canonical):
        np.testing.assert_array_equal(actual, expected)
        assert not actual.flags.writeable
    assert candidates[0].dx == candidates[0].dy == candidates[0].placement_penalty == 0
    assert candidates[1].dx < 0 < candidates[2].dx


def test_composition_state_is_immutable_at_placement_boundary():
    config_offsets = {"canonical": 0., "safe_left": -0.45, "safe_right": 0.45}
    config = DiacriticConfig(dx_candidates_mm=config_offsets)
    config_offsets["safe_left"] = -9.
    assert config.dx_candidates_mm["safe_left"] == -0.45
    states = build_composition_states("e", ("\u0301",), _variants(), 2., config)
    assert len(states) <= 9
    with pytest.raises(FrozenInstanceError):
        states[0].state_tag = "changed"
    with pytest.raises(TypeError):
        states[0].context["changed"] = True
    with pytest.raises(ValueError):
        states[0].diacritic_candidate.strokes_local[0][0, 0] = 99


def test_candidate_pruning_never_revives_hard_invalid():
    config = DiacriticConfig(max_placement_shift_mm=0)
    assert [c.placement_tag for c in generate_diacritic_candidates("e", ("\u0301",), 2., config)] == ["canonical"]
    with pytest.raises(NoValidCompositionState):
        build_composition_states("e", ("\u034f",), _variants(), 2.)


def test_transform_state_to_world_uses_single_frame_contract():
    states = build_composition_states("e", ("\u0301",), _variants(), 2.)
    canonical, left = states[0], states[1]
    frame = (np.array([2., 3.]), np.array([10., 20.]))
    first = transform_state_to_world(canonical, *frame)
    shifted = transform_state_to_world(left, *frame)
    np.testing.assert_allclose(first.entry_pt, canonical.base_variant.entry_pt * frame[0] + frame[1])
    expected_tangent = canonical.base_variant.v_entry * frame[0]
    expected_tangent /= np.linalg.norm(expected_tangent)
    np.testing.assert_allclose(first.v_entry, expected_tangent)
    np.testing.assert_allclose(shifted.diacritic_strokes[0] - first.diacritic_strokes[0],
                               np.tile([left.diacritic_candidate.dx, 0.], (2, 1)))
    assert shifted.diacritic_bbox[0] == pytest.approx(first.diacritic_bbox[0] - 0.45)
    assert not shifted.diacritic_strokes[0].flags.writeable


def test_transform_rejects_invalid_geometry_and_frame():
    state = build_composition_states("e", (), _variants(), 2.)[0]
    with pytest.raises(CompositionGeometryError):
        transform_state_to_world(state, [0., 1.], [0., 0.])
    state.base_variant.v_entry[:] = 0.
    with pytest.raises(CompositionGeometryError):
        transform_state_to_world(state, [1., 1.], [0., 0.])


def test_state_cost_separates_mm_clearance_from_dimensionless_penalties():
    states = build_composition_states("e", ("\u0301",), _variants(), 2.)
    world = transform_state_to_world(states[0], [1., 1.], [0., 0.])
    cost = evaluate_composition_state(states[0], world)
    assert cost.minimum_internal_clearance_mm >= 0
    assert cost.c_internal_collision >= 0
    assert cost.total_cost == pytest.approx(
        cost.c_internal_collision + cost.c_legibility + cost.c_placement)
    assert evaluate_composition_state(states[1], transform_state_to_world(states[1], [1., 1.], [0., 0.])).c_placement > 0


def test_unaccented_state_has_no_internal_or_placement_cost():
    state = build_composition_states("e", (), _variants(), 2.)[0]
    world = transform_state_to_world(state, [1., 1.], [0., 0.])
    cost = evaluate_composition_state(state, world)
    assert cost.minimum_internal_clearance_mm == float("inf")
    assert cost.c_internal_collision == cost.c_placement == 0


def test_world_boundary_pruning_never_restores_canonical():
    states = build_composition_states("e", ("\u0301",), _variants(), 2.)
    world = transform_state_to_world(states[0], [1., 1.], [0., 0.])
    x0, y0, x1, y1 = world.diacritic_bbox
    with pytest.raises(NoValidCompositionState):
        prune_composition_states(states, [1., 1.], [0., 0.],
                                 page_bounds_mm=(x1 + 1., y0, x1 + 2., y1))


def test_internal_collision_cost_detects_crossing():
    world = GlyphWorldGeometry(
        (np.array([[0., 0.], [2., 2.]]),),
        (np.array([[0., 2.], [2., 0.]]),),
        np.array([0., 0.]), np.array([2., 2.]),
        np.array([1., 0.]), np.array([1., 0.]), (0., 0., 2., 2.),
    )
    state = SimpleNamespace(legibility_cost=0., diacritic_candidate=SimpleNamespace(placement_penalty=0.))
    cost = evaluate_composition_state(state, world)
    assert cost.minimum_internal_clearance_mm == 0
    assert cost.c_internal_collision == 1
    assert cost.total_cost == 1
