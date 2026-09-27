"""Opt-in PR3 renderer uses selected state and transition geometry once."""

from collections import Counter
import numpy as np

from backend.handwriting import engine
from backend.handwriting.metrics_evaluator import compute_stroke_fingerprint


def test_pr3_diacritics_render_once_with_original_nfd_marks():
    result = engine.text_to_strokes_structured(
        "nguyễn", font="cursive", seed=42, _algorithm_mode="pr3_composition")
    marks = [item for item in result.trace if item.stroke_type == "diacritic_stroke"]
    assert len(marks) == 2  # tilde and circumflex for ễ
    assert all(np.isfinite(item.points).all() for item in marks)
    assert all(item.meta["accents"] for item in marks)


def test_pr3_renderer_reuses_transition_bridge(monkeypatch):
    # composition.py keeps its own evaluator reference. If the renderer calls
    # engine.build_ligature_bridge again, the test fails.
    monkeypatch.setattr(engine, "build_ligature_bridge",
                        lambda *_args, **_kwargs: (_ for _ in ()).throw(
                            AssertionError("renderer rebuilt evaluated bridge")))
    result = engine.text_to_strokes_structured(
        "nguyễn", font="cursive", seed=42, _algorithm_mode="pr3_composition")
    assert any(item.stroke_type == "bridge_stroke" for item in result.trace)


def test_pr3_opt_in_does_not_change_default_b3():
    before = engine.text_to_strokes_structured("OmniDraw", font="oly", seed=42)
    _ = engine.text_to_strokes_structured(
        "lụy thụy quỹ", font="oly", seed=42, _algorithm_mode="pr3_composition")
    after = engine.text_to_strokes_structured("OmniDraw", font="oly", seed=42)
    assert compute_stroke_fingerprint(before.strokes) == compute_stroke_fingerprint(after.strokes)
    assert Counter(item.stroke_type for item in before.trace) == Counter(
        item.stroke_type for item in after.trace)
