"""Technical Art Mode baseline comparison on identical extracted strokes.

This is a dry-run, not a formal research result or physical time measurement.
"""

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from path_optimizer import (  # noqa: E402
    chain_strokes,
    extract_strokes_line_art,
    nearest_neighbor_order,
    or_opt_improve,
    total_travel_distance,
    two_opt_improve,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = cv2.imread(str(args.image))
    if image is None:
        parser.error(f"Cannot read image: {args.image}")

    raw, _ = extract_strokes_line_art(image)
    strokes = chain_strokes(raw, snap_dist=15.0)
    if not strokes:
        parser.error("No strokes extracted")

    methods = {}
    for name in ("original", "greedy_euclidean", "current_pipeline"):
        started = perf_counter()
        if name == "original":
            order, reverse = list(range(len(strokes))), [False] * len(strokes)
        else:
            order, reverse = nearest_neighbor_order(
                strokes, lambda_turn=0.0 if name == "greedy_euclidean" else 1.5
            )
            if name == "current_pipeline":
                order, reverse = two_opt_improve(strokes, order, reverse)
                order, reverse = or_opt_improve(strokes, order, reverse)
        methods[name] = {
            "pen_lift_distance_px": round(float(total_travel_distance(strokes, order, reverse)), 3),
            "pen_lift_count": len(strokes) - 1,
            "order_time_ms_single_run": round((perf_counter() - started) * 1000, 3),
        }

    print(json.dumps({"image": str(args.image), "raw_strokes": len(raw),
                      "chained_strokes": len(strokes), "methods": methods}, indent=2))


if __name__ == "__main__":
    main()
