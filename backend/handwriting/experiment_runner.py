"""Internal CA-VHC baseline runner for PR1 research metrics."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

try:
    from backend.handwriting.benchmark_fixtures import (
        BENCHMARK_DEV_CORPUS_20,
        BENCHMARK_HOLDOUT_CORPUS_20,
        STANDARD_SEEDS,
    )
    from backend.handwriting.engine import text_to_strokes_structured
    from backend.handwriting.metrics_evaluator import (
        compute_stroke_fingerprint,
        evaluate_ca_vhc_metrics,
    )
    from backend.logs.csv_logger import log_experiment_csv
except ImportError:  # Direct execution from backend/.
    from handwriting.benchmark_fixtures import (
        BENCHMARK_DEV_CORPUS_20,
        BENCHMARK_HOLDOUT_CORPUS_20,
        STANDARD_SEEDS,
    )
    from handwriting.engine import text_to_strokes_structured
    from handwriting.metrics_evaluator import (
        compute_stroke_fingerprint,
        evaluate_ca_vhc_metrics,
    )
    from logs.csv_logger import log_experiment_csv


METHOD_TAG = "b3_current_trellis"
DEFAULT_FONTS = ("oly", "omni_casual")
CA_VHC_CSV_COLUMNS = [
    "dataset_item_id",
    "corpus_split",
    "text",
    "method_tag",
    "font",
    "style",
    "seed",
    "total_path_length_mm",
    "pen_lift_distance_mm",
    "pen_lift_count",
    "collision_count",
    "minimum_diacritic_clearance_mm",
    "curvature_cost",
    "optimize_time_ms",
    "base_stroke_count",
    "bridge_stroke_count",
    "secondary_stroke_count",
    "diacritic_stroke_count",
    "stroke_fingerprint_sha256",
]


def build_benchmark_rows(
    words: Iterable[str],
    corpus_split: str,
    fonts: Sequence[str] = DEFAULT_FONTS,
    seeds: Sequence[int] = STANDARD_SEEDS,
    style: str = "hand_hocsinh",
) -> list[dict]:
    """Render a deterministic matrix and return one flat metrics row per case."""
    rows = []
    for item_index, text in enumerate(words, start=1):
        for font in fonts:
            for seed in seeds:
                result = text_to_strokes_structured(
                    text,
                    font=font,
                    style=style,
                    seed=seed,
                )
                metrics = evaluate_ca_vhc_metrics(result)
                counts = metrics["stroke_counts_by_type"]
                rows.append({
                    "dataset_item_id": f"{corpus_split}_{item_index:03d}",
                    "corpus_split": corpus_split,
                    "text": text,
                    "method_tag": METHOD_TAG,
                    "font": font,
                    "style": style,
                    "seed": seed,
                    "total_path_length_mm": metrics["total_path_length_mm"],
                    "pen_lift_distance_mm": metrics["pen_lift_distance_mm"],
                    "pen_lift_count": metrics["pen_lift_count"],
                    "collision_count": metrics["collision_count"],
                    "minimum_diacritic_clearance_mm": (
                        round(metrics["minimum_diacritic_clearance_mm"], 3)
                        if metrics["minimum_diacritic_clearance_mm"] != float("inf")
                        else float("inf")
                    ),
                    "curvature_cost": metrics["curvature_cost"],
                    "optimize_time_ms": metrics["optimize_time_ms"],
                    "base_stroke_count": counts["base_stroke"],
                    "bridge_stroke_count": counts["bridge_stroke"],
                    "secondary_stroke_count": counts["secondary_stroke"],
                    "diacritic_stroke_count": counts["diacritic_stroke"],
                    "stroke_fingerprint_sha256": compute_stroke_fingerprint(result.strokes),
                })
    return rows


def write_benchmark_csv(rows: Iterable[dict], output_path: Path, overwrite: bool = False) -> int:
    """Write rows with the PR1 schema; refuse accidental duplicate/overwrite by default."""
    output_path = Path(output_path)
    if output_path.exists():
        if not overwrite:
            raise FileExistsError(f"Output already exists: {output_path}")
        output_path.unlink()

    count = 0
    for row in rows:
        log_experiment_csv(row, str(output_path), columns=CA_VHC_CSV_COLUMNS)
        count += 1
    return count


def _selected_corpora(selection: str):
    if selection == "dev":
        return [("dev", BENCHMARK_DEV_CORPUS_20)]
    if selection == "holdout":
        return [("holdout", BENCHMARK_HOLDOUT_CORPUS_20)]
    return [
        ("dev", BENCHMARK_DEV_CORPUS_20),
        ("holdout", BENCHMARK_HOLDOUT_CORPUS_20),
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the internal CA-VHC PR1 baseline matrix.")
    parser.add_argument("--corpus", choices=("dev", "holdout", "all"), default="dev")
    parser.add_argument("--fonts", nargs="+", default=list(DEFAULT_FONTS))
    parser.add_argument("--seeds", nargs="+", type=int, default=list(STANDARD_SEEDS))
    parser.add_argument("--style", default="hand_hocsinh")
    parser.add_argument(
        "--allow-holdout",
        action="store_true",
        help="Explicitly acknowledge holdout use; never enable this during tuning.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "logs" / "ca_vhc_pr1_baseline.csv",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    if args.corpus != "dev" and not args.allow_holdout:
        parser.error("holdout/all requires --allow-holdout to prevent accidental tuning leakage")

    rows = []
    for split, words in _selected_corpora(args.corpus):
        rows.extend(build_benchmark_rows(words, split, args.fonts, args.seeds, args.style))
    written = write_benchmark_csv(rows, args.output, overwrite=args.overwrite)
    print(f"Wrote {written} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
