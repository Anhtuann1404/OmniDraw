"""Proposed PR3 runner is opt-in and DEV-only."""

import pytest

from backend.handwriting.composition import PROPOSED_METHOD_TAG
from backend.handwriting.experiment_runner import build_benchmark_rows, main


def test_pr3_proposed_row_uses_existing_schema():
    row = build_benchmark_rows(
        ["tiếng"], "dev", fonts=["cursive"], seeds=[42],
        method_tag=PROPOSED_METHOD_TAG)[0]
    assert row["method_tag"] == PROPOSED_METHOD_TAG
    assert row["corpus_split"] == "dev"
    assert row["collision_count"] == 0
    assert row["diacritic_stroke_count"] > 0


def test_pr3_proposed_blocks_holdout_at_api_and_cli(tmp_path):
    with pytest.raises(ValueError, match="DEV-only"):
        build_benchmark_rows(["tiếng"], "holdout", fonts=["oly"], seeds=[42],
                             method_tag=PROPOSED_METHOD_TAG)
    with pytest.raises(SystemExit) as error:
        main(["--method", PROPOSED_METHOD_TAG, "--corpus", "holdout",
              "--allow-holdout", "--output", str(tmp_path / "blocked.csv")])
    assert error.value.code == 2
    assert not (tmp_path / "blocked.csv").exists()
