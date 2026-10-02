"""Regenerate PR3 E1 per-case DEV evidence without opening HOLDOUT."""

import csv
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.handwriting.baselines import B1_STATIC, B2_GREEDY
from backend.handwriting.benchmark_fixtures import (
    BENCHMARK_DEV_CORPUS_20, CORPUS_VERSION, STANDARD_SEEDS,
)
from backend.handwriting.composition import PROPOSED_METHOD_TAG
from backend.handwriting.experiment_runner import build_benchmark_rows


OUTPUT = ROOT / "docs" / "evidence" / "pr3_e1_dev_rows.csv"
METADATA = ROOT / "docs" / "evidence" / "pr3_e1_dev_metadata.json"
FONTS = ("oly", "omni_casual")
METHODS = (B1_STATIC, B2_GREEDY, PROPOSED_METHOD_TAG)
STYLE = "hand_hocsinh"
COLUMNS = (
    "dataset_item_id", "text", "method_tag", "font", "style", "seed",
    "pen_lift_distance_mm", "pen_lift_count", "collision_count",
    "stroke_fingerprint_sha256",
)


def main():
    rows = []
    for method in METHODS:
        rows.extend(build_benchmark_rows(
            BENCHMARK_DEV_CORPUS_20, "dev", fonts=FONTS,
            seeds=STANDARD_SEEDS, style=STYLE, method_tag=method))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows({column: row[column] for column in COLUMNS} for row in rows)

    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    corpus_sha = hashlib.sha256(json.dumps(
        BENCHMARK_DEV_CORPUS_20, ensure_ascii=False,
        separators=(",", ":")).encode("utf-8")).hexdigest()
    metadata = {
        "source_commit": commit,
        "corpus_version": CORPUS_VERSION,
        "corpus_sha256": corpus_sha,
        "corpus_split": "dev",
        "word_count": len(BENCHMARK_DEV_CORPUS_20),
        "fonts": FONTS,
        "seeds": STANDARD_SEEDS,
        "style": STYLE,
        "methods": METHODS,
        "rows_per_method": len(BENCHMARK_DEV_CORPUS_20) * len(FONTS) * len(STANDARD_SEEDS),
        "total_rows": len(rows),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "csv_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "command": "backend/venv/bin/python3 scripts/legacy/generate_pr3_e1_dev_evidence.py",
    }
    METADATA.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    totals = {method: round(sum(row["pen_lift_distance_mm"] for row in rows
                                if row["method_tag"] == method), 3) for method in METHODS}
    print(f"Wrote {len(rows)} DEV rows: {totals}")


if __name__ == "__main__":
    main()
