"""PR3 software acceptance on the frozen DEV-only specimen subset."""

import math

import pytest

from backend.handwriting.benchmark_fixtures import (
    BENCHMARK_DEV_CORPUS_20, PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS,
)
from backend.handwriting.engine import (
    STYLE_CONFIGS, generate_accents, group_nfd_graphemes, text_to_strokes_structured,
)
from backend.handwriting.metrics_evaluator import evaluate_ca_vhc_metrics
from backend.handwriting.metrics_evaluator import compute_stroke_fingerprint


def test_pr3_acceptance_specimens_are_dev_only():
    assert len(PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS) == 10
    assert set(PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS) <= set(BENCHMARK_DEV_CORPUS_20)


@pytest.mark.parametrize("word", PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS)
@pytest.mark.parametrize("style", STYLE_CONFIGS)
def test_pr3_dev_specimen_nfd_geometry_and_clearance(word, style, monkeypatch):
    from backend.handwriting import composition

    original_solve = composition.optimize_composition_dag
    layer_sizes = []

    def checked_solve(layers, *args, **kwargs):
        layer_sizes.extend(len(layer) for layer in layers)
        return original_solve(layers, *args, **kwargs)

    monkeypatch.setattr(composition, "optimize_composition_dag", checked_solve)
    result = text_to_strokes_structured(
        word, font="cursive", style=style, seed=42,
        _algorithm_mode="pr3_composition")
    metrics = evaluate_ca_vhc_metrics(result)
    assert layer_sizes and max(layer_sizes) <= 9
    assert all(1 <= size <= 9 for size in layer_sizes)
    assert all(math.isfinite(value) for value in (
        metrics["pen_lift_distance_mm"], metrics["total_path_length_mm"],
        metrics["optimize_time_ms"],
    ))
    assert metrics["collision_count"] == 0
    assert metrics["minimum_diacritic_clearance_mm"] >= 0.20

    groups = group_nfd_graphemes(word)
    marks_by_index = {index: tuple(group[1:]) for index, group in enumerate(groups)
                      if group[1:]}
    rendered = [item for item in result.trace if item.stroke_type == "diacritic_stroke"]
    assert set(item.meta["char_idx"] for item in rendered) == set(marks_by_index)
    for index, marks in marks_by_index.items():
        actual = [item for item in rendered if item.meta["char_idx"] == index]
        base = groups[index][0]
        expected_count = len(generate_accents(base, marks, 0.))
        assert len(actual) == expected_count
        assert all(tuple(item.meta["accents"]) == marks for item in actual)


@pytest.mark.parametrize("style", STYLE_CONFIGS)
def test_pr3_same_seed_is_deterministic(style):
    fingerprints = [compute_stroke_fingerprint(text_to_strokes_structured(
        "tiếng", font="cursive", style=style, seed=42,
        _algorithm_mode="pr3_composition").strokes) for _ in range(5)]
    assert len(set(fingerprints)) == 1
