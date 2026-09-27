"""PR3 Slice 1: candidate generation remains separate from the default solver."""

from dataclasses import FrozenInstanceError
import numpy as np
import pytest

from backend.handwriting.composition import (
    DiacriticConfig, NoValidCompositionState, build_composition_states,
    generate_diacritic_candidates,
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
