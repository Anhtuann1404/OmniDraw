import csv
import json
from pathlib import Path

import pytest

from backend.handwriting.benchmark_fixtures import (
    BENCHMARK_DEV_CORPUS_20,
    STANDARD_SEEDS,
)
from backend.handwriting.experiment_runner import (
    CA_VHC_CSV_COLUMNS,
    METHOD_TAG,
    build_benchmark_rows,
    main,
    write_benchmark_csv,
)
from backend.logs.csv_logger import log_experiment_csv


def test_runner_builds_reproducible_geometry_row():
    first = build_benchmark_rows(["tiếng"], "dev", fonts=["oly"], seeds=[42])[0]
    second = build_benchmark_rows(["tiếng"], "dev", fonts=["oly"], seeds=[42])[0]

    assert first["dataset_item_id"] == "dev_001"
    assert first["method_tag"] == METHOD_TAG
    assert first["stroke_fingerprint_sha256"] == second["stroke_fingerprint_sha256"]
    assert first["total_path_length_mm"] == second["total_path_length_mm"]
    assert first["pen_lift_distance_mm"] == second["pen_lift_distance_mm"]
    assert first["optimize_time_ms"] >= 0.0


def test_runner_writes_declared_csv_schema(tmp_path):
    output = tmp_path / "baseline.csv"
    rows = build_benchmark_rows(["việt"], "dev", fonts=["omni_casual"], seeds=[2026])

    assert write_benchmark_csv(rows, output) == 1
    with output.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        written = list(reader)

    assert reader.fieldnames == CA_VHC_CSV_COLUMNS
    assert written[0]["corpus_split"] == "dev"
    assert written[0]["font"] == "omni_casual"
    assert len(written[0]["stroke_fingerprint_sha256"]) == 64


def test_runner_refuses_accidental_overwrite(tmp_path):
    output = tmp_path / "baseline.csv"
    rows = build_benchmark_rows(["nước"], "dev", fonts=["oly"], seeds=[42])
    write_benchmark_csv(rows, output)

    with pytest.raises(FileExistsError):
        write_benchmark_csv(rows, output)


def test_csv_logger_refuses_mixed_schemas(tmp_path):
    output = tmp_path / "metrics.csv"
    log_experiment_csv({"a": 1}, str(output), columns=["a"])

    with pytest.raises(ValueError, match="CSV schema mismatch"):
        log_experiment_csv({"b": 2}, str(output), columns=["b"])


def test_csv_logger_handles_precreated_empty_file(tmp_path):
    output = tmp_path / "empty.csv"
    output.touch()
    log_experiment_csv({"a": 1}, str(output), columns=["a"])

    with output.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    assert reader.fieldnames == ["a"]
    assert rows == [{"a": "1"}]


def test_cli_requires_explicit_holdout_acknowledgement(tmp_path):
    output = tmp_path / "holdout.csv"

    with pytest.raises(SystemExit):
        main(["--corpus", "holdout", "--output", str(output)])
    assert not output.exists()


def test_pr1_dev_geometry_matches_frozen_baseline():
    fixture_path = Path(__file__).parent / "fixtures" / "ca_vhc_pr1_fingerprints.json"
    snapshot = json.loads(fixture_path.read_text(encoding="utf-8"))
    rows = build_benchmark_rows(
        BENCHMARK_DEV_CORPUS_20,
        "dev",
        seeds=STANDARD_SEEDS,
    )
    actual = [
        {
            "dataset_item_id": row["dataset_item_id"],
            "text": row["text"],
            "font": row["font"],
            "seed": row["seed"],
            "stroke_fingerprint_sha256": row["stroke_fingerprint_sha256"],
        }
        for row in rows
    ]

    assert snapshot["schema_version"] == 1
    assert snapshot["method_tag"] == METHOD_TAG
    assert snapshot["case_count"] == 160
    assert actual == snapshot["cases"]
