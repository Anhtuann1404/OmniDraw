"""Opt-in PR3 renderer uses selected state and transition geometry once."""

from collections import Counter
import numpy as np

from backend.handwriting import engine
from backend.handwriting import composition
from backend.handwriting.metrics_evaluator import compute_stroke_fingerprint
from backend.handwriting.metrics_evaluator import total_travel_distance
from backend.handwriting.benchmark_fixtures import PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS
from backend.handwriting.baselines import B1_STATIC, B2_GREEDY
from backend.handwriting.experiment_runner import build_benchmark_rows
from backend.handwriting.composition import PROPOSED_METHOD_TAG


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


def test_pr3_secondary_route_keeps_geometry_and_within_glyph_order():
    base = [np.array([[0., 0.], [0., 0.]])]
    secondary = [
        np.array([[10., 0.], [11., 0.]]),
        np.array([[12., 0.], [13., 0.]]),
        np.array([[1., 0.], [2., 0.]]),
    ]
    meta = [{"meta": {"char_idx": i}} for i in (0, 0, 1)]
    ordered, ordered_meta = engine._order_pr3_secondary_strokes(base, secondary, meta)
    assert [next(i for i, original in enumerate(secondary) if stroke is original)
            for stroke in ordered] == [2, 0, 1]
    assert [item["meta"]["char_idx"] for item in ordered_meta] == [1, 0, 0]
    assert total_travel_distance(base + ordered) < total_travel_distance(base + secondary)


def test_pr3_e1_dev_acceptance_penup_beats_b1_and_b2():
    words = PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS
    proposed = build_benchmark_rows(words, "dev", fonts=["cursive"], seeds=[42],
                                    method_tag=PROPOSED_METHOD_TAG)
    proposed_distance = sum(row["pen_lift_distance_mm"] for row in proposed)
    for method in (B1_STATIC, B2_GREEDY):
        baseline = build_benchmark_rows(words, "dev", fonts=["cursive"], seeds=[42],
                                        method_tag=method)
        assert proposed_distance < sum(row["pen_lift_distance_mm"] for row in baseline)
    assert all(row["collision_count"] == 0 for row in proposed)


def test_pr3_reordered_secondary_trace_matches_rendered_strokes():
    result = engine.text_to_strokes_structured(
        "trường", font="cursive", seed=42, _algorithm_mode="pr3_composition")
    secondary = [item for item in result.trace if item.stroke_type in
                 ("secondary_stroke", "diacritic_stroke")]
    assert secondary
    for item in secondary:
        stroke_index = item.meta["continuous_stroke_id"]
        np.testing.assert_array_equal(item.points, result.strokes[stroke_index])


def test_pr3_supported_styles_evaluate_the_exact_rendered_marks(monkeypatch):
    original_solve = composition.optimize_composition_dag
    fingerprints = set()
    for style in engine.STYLE_CONFIGS:
        captured = {"marks": []}

        def capture(layers, *args, **kwargs):
            solution = original_solve(layers, *args, **kwargs)
            captured["marks"].extend(
                stroke for layer, chosen in zip(layers, solution["states"])
                for state, world in layer if state is chosen
                for stroke in world.diacritic_strokes)
            return solution

        monkeypatch.setattr(composition, "optimize_composition_dag", capture)
        result = engine.text_to_strokes_structured(
            "tiếng nước", font="cursive", style=style, seed=42,
            _algorithm_mode="pr3_composition")
        rendered_marks = [item.points for item in result.trace
                          if item.stroke_type == "diacritic_stroke"]
        assert Counter(stroke.tobytes() for stroke in captured["marks"]) == Counter(
            stroke.tobytes() for stroke in rendered_marks)
        assert all(np.isfinite(stroke).all() for stroke in result.strokes)
        fingerprints.add(compute_stroke_fingerprint(result.strokes))
    assert len(fingerprints) == len(engine.STYLE_CONFIGS)
