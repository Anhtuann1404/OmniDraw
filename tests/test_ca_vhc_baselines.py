"""PR2 acceptance tests for the three independent CA-VHC baselines."""

from types import SimpleNamespace

import numpy as np

import pytest

from backend.handwriting.baselines import (
    B1_STATIC,
    B2_GREEDY,
    B3_CURRENT_TRELLIS,
    solve_baseline,
)
from backend.handwriting.engine import text_to_strokes_structured
from backend.handwriting.experiment_runner import build_benchmark_rows
from backend.handwriting.metrics_evaluator import compute_stroke_fingerprint


def test_runner_executes_and_labels_each_baseline():
    rows = [
        build_benchmark_rows(
            ["minh"], "dev", fonts=["cursive"], seeds=[42], method_tag=method
        )[0]
        for method in (B1_STATIC, B2_GREEDY, B3_CURRENT_TRELLIS)
    ]

    assert [row["method_tag"] for row in rows] == [
        B1_STATIC,
        B2_GREEDY,
        B3_CURRENT_TRELLIS,
    ]
    assert rows[0]["bridge_stroke_count"] == 0
    assert rows[1]["optimize_time_ms"] >= 0.0
    assert rows[2]["optimize_time_ms"] >= 0.0


def test_b1_always_lifts_and_uses_no_bridges():
    result = text_to_strokes_structured(
        "minimum", font="cursive", seed=42, _algorithm_mode=B1_STATIC
    )
    assert all(item.stroke_type != "bridge_stroke" for item in result.trace)


def test_b2_respects_force_lift_for_non_ligature_font():
    result = text_to_strokes_structured(
        "minimum", font="oly", seed=42, _algorithm_mode=B2_GREEDY
    )
    assert all(item.stroke_type != "bridge_stroke" for item in result.trace)


def test_b2_prefix_is_not_changed_by_a_later_character(monkeypatch):
    from backend.handwriting import baselines, engine

    def variant(label, legibility):
        return SimpleNamespace(
            label=label,
            cost_legibility=legibility,
            entry_pt=np.zeros(2),
            exit_pt=np.ones(2),
            v_entry=np.array([1.0, 0.0]),
            v_exit=np.array([1.0, 0.0]),
        )

    variants = [
        [variant("a0", 0.0), variant("a1", 1.0)],
        [variant("b0", 0.0), variant("b1", 1.0)],
        [variant("c0", 0.0), variant("c1", 1.0)],
        [variant("d0", 0.0), variant("d1", 1.0)],
    ]
    world = [[[np.zeros((2, 2))] for _ in pair] for pair in variants]
    monkeypatch.setattr(
        baselines,
        "_variants_and_world_strokes",
        lambda items: (variants[:len(items)], world[:len(items)]),
    )
    monkeypatch.setattr(
        engine,
        "eval_transition",
        lambda _u, w, *_args, **_kwargs: (w.cost_legibility, w.label.endswith("0")),
    )
    items = [
        {"scale_vec": np.ones(2), "offset": np.zeros(2)}
        for _ in variants
    ]

    prefix = baselines.greedy_contextual_baseline(items[:3], (0, 0, 0, 0, 1))
    extended = baselines.greedy_contextual_baseline(items, (0, 0, 0, 0, 1))

    assert [v.label for v in prefix["variants"]] == ["a0", "b0", "c0"]
    assert [v.label for v in extended["variants"][:3]] == ["a0", "b0", "c0"]
    assert extended["conns"][:2] == prefix["conns"]


def test_b3_remains_the_default_frozen_geometry():
    default = text_to_strokes_structured("OmniDraw", font="oly", seed=42)
    explicit = text_to_strokes_structured(
        "OmniDraw", font="oly", seed=42, _algorithm_mode=B3_CURRENT_TRELLIS
    )
    assert compute_stroke_fingerprint(default.strokes) == compute_stroke_fingerprint(
        explicit.strokes
    )


def test_unknown_baseline_is_rejected():
    with pytest.raises(ValueError, match="Unknown baseline method"):
        solve_baseline([], "unknown", (0.5, 4.0, 2.0, 15.0, 1.0))
