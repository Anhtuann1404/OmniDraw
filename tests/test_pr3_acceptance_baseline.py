"""Pre-PR3 acceptance baseline tests for ASCII behavior locking and DEV-only corpus scoping."""

import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from backend.handwriting.benchmark_fixtures import (
    BENCHMARK_DEV_CORPUS_20,
    STANDARD_SEEDS,
)
from backend.handwriting.engine import (
    generate_handwriting_svg,
    text_to_strokes_structured,
)
from backend.handwriting.experiment_runner import (
    METHOD_TAG,
    build_benchmark_rows,
)
from backend.handwriting.metrics_evaluator import compute_stroke_fingerprint

ASCII_WORDS = ["OmniDraw", "plotter", "vector", "minimum", "connection", "handwriting"]
ASCII_FONTS = ["oly", "omni_casual"]
ASCII_SEEDS = list(STANDARD_SEEDS)
ASCII_STYLE = "hand_hocsinh"

PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS = [
    "tiếng",
    "nước",
    "đường",
    "khuấy",
    "thuở",
    "nghỉ",
    "trường",
    "phượng",
    "mượt",
    "vẫy",
]

HEX_64_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _load_ascii_fixture() -> dict:
    fixture_path = (
        Path(__file__).parent / "fixtures" / "pr3_ascii_baseline_fingerprints.json"
    )
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def test_pr3_ascii_fixture_has_exact_declared_matrix():
    snapshot = _load_ascii_fixture()

    assert snapshot["schema_version"] == 1
    assert snapshot["method_tag"] == METHOD_TAG
    assert snapshot["case_count"] == 48

    cases = snapshot["cases"]
    assert len(cases) == 48

    allowed_case_keys = {
        "text",
        "font",
        "style",
        "seed",
        "stroke_fingerprint_sha256",
    }
    forbidden_substrings = ("time", "duration", "timestamp", "date", "system")

    keys = []
    for case in cases:
        assert set(case.keys()) == allowed_case_keys
        for k in case.keys():
            assert not any(sub in k.lower() for sub in forbidden_substrings)

        assert case["text"] in ASCII_WORDS
        assert case["font"] in ASCII_FONTS
        assert case["style"] == ASCII_STYLE
        assert case["seed"] in ASCII_SEEDS
        assert HEX_64_PATTERN.match(case["stroke_fingerprint_sha256"]) is not None

        keys.append((case["text"], case["font"], case["seed"]))

    assert len(set(keys)) == 48
    assert {c["text"] for c in cases} == set(ASCII_WORDS)
    assert {c["font"] for c in cases} == set(ASCII_FONTS)
    assert {c["seed"] for c in cases} == set(ASCII_SEEDS)


def test_pr3_ascii_baseline_fingerprints_match_current_engine():
    snapshot = _load_ascii_fixture()
    rows = build_benchmark_rows(
        ASCII_WORDS,
        "ascii_baseline",
        fonts=ASCII_FONTS,
        seeds=ASCII_SEEDS,
        style=ASCII_STYLE,
    )

    actual_cases = [
        {
            "text": row["text"],
            "font": row["font"],
            "style": row["style"],
            "seed": row["seed"],
            "stroke_fingerprint_sha256": row["stroke_fingerprint_sha256"],
        }
        for row in rows
    ]
    actual_cases.sort(key=lambda c: (c["text"], c["font"], c["seed"]))
    expected_cases = sorted(
        snapshot["cases"], key=lambda c: (c["text"], c["font"], c["seed"])
    )

    assert len(actual_cases) == 48
    assert actual_cases == expected_cases


def test_pr3_ascii_seed_determinism():
    for font in ASCII_FONTS:
        fingerprints = []
        for _ in range(5):
            result = text_to_strokes_structured(
                "OmniDraw",
                font=font,
                style=ASCII_STYLE,
                seed=42,
            )
            fp = compute_stroke_fingerprint(result.strokes)
            fingerprints.append(fp)

        assert len(fingerprints) == 5
        assert len(set(fingerprints)) == 1, (
            f"Non-deterministic fingerprint across runs for font={font}"
        )


def test_pr3_ascii_svg_and_bounds_valid():
    """Verify criteria A2: render all 48 ASCII matrix configurations and validate SVG contract."""
    for text in ASCII_WORDS:
        for font in ASCII_FONTS:
            for seed in ASCII_SEEDS:
                svg_content, metrics, is_within_bounds = generate_handwriting_svg(
                    text,
                    font=font,
                    style=ASCII_STYLE,
                    seed=seed,
                )
                assert is_within_bounds is True, (
                    f"Out of bounds for text={text}, font={font}, seed={seed}"
                )
                root = ET.fromstring(svg_content)
                assert root.tag.endswith("svg"), (
                    f"Root tag is not svg: {root.tag} for text={text}"
                )

                paths = [el for el in root.iter() if el.tag.endswith("path")]
                assert len(paths) >= 1, (
                    f"No path elements found in SVG for text={text}, font={font}, seed={seed}"
                )
                assert any(p.attrib.get("d", "").strip() for p in paths), (
                    f"No non-empty path d attribute found for text={text}, font={font}, seed={seed}"
                )

                for el in root.iter():
                    for attr_name, attr_val in el.attrib.items():
                        for token in attr_val.replace(",", " ").split():
                            t_clean = token.lstrip("MLCHVSQTAZmlchvsqtaz+-").rstrip("pxem%")
                            if t_clean:
                                assert t_clean.lower() not in ("nan", "inf", "infinity"), (
                                    f"Invalid coordinate '{token}' in attribute {attr_name}='{attr_val}'"
                                )


def test_pr3_ascii_batch_order_does_not_change_fingerprint():
    """Verify criteria D2: isolated vs batch runs with different orders yield identical fingerprints."""
    for font in ASCII_FONTS:
        # 1. Render isolated "OmniDraw"
        isolated_rows = build_benchmark_rows(
            ["OmniDraw"],
            "batch_order_test",
            fonts=[font],
            seeds=[42],
            style=ASCII_STYLE,
        )
        fp_isolated = isolated_rows[0]["stroke_fingerprint_sha256"]

        # 2. Render batch where another word precedes "OmniDraw"
        batch_prefix_rows = build_benchmark_rows(
            ["vector", "OmniDraw"],
            "batch_order_test",
            fonts=[font],
            seeds=[42],
            style=ASCII_STYLE,
        )
        fp_batch_prefix = next(
            r["stroke_fingerprint_sha256"]
            for r in batch_prefix_rows
            if r["text"] == "OmniDraw"
        )

        # 3. Render batch with reverse order
        batch_suffix_rows = build_benchmark_rows(
            ["OmniDraw", "vector"],
            "batch_order_test",
            fonts=[font],
            seeds=[42],
            style=ASCII_STYLE,
        )
        fp_batch_suffix = next(
            r["stroke_fingerprint_sha256"]
            for r in batch_suffix_rows
            if r["text"] == "OmniDraw"
        )

        # 4. Assert identical fingerprints across all 3 execution orders
        assert fp_isolated == fp_batch_prefix == fp_batch_suffix, (
            f"State leak detected for font={font}: isolated={fp_isolated}, "
            f"batch_prefix={fp_batch_prefix}, batch_suffix={fp_batch_suffix}"
        )


def test_pr3_acceptance_specimens_are_dev_only():
    """Verify criteria G1: acceptance specimens contain exactly 10 unique DEV words without touching Holdout."""
    assert len(PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS) == 10
    assert len(set(PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS)) == 10

    # Must be a strict subset of DEV corpus
    assert set(PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS).issubset(
        set(BENCHMARK_DEV_CORPUS_20)
    )
