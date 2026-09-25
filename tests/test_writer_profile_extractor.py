"""
Bộ Unit Test Kiểm chuẩn Module Trích xuất Đặc trưng Người viết (Writer Profile Extractor).

Đường chạy: TV1 — AI Data & Writer Profile Lead
Phục vụ: Nghiên cứu cá nhân hóa P2 (Non-binding offline research)
"""

import json
import os
import sys
from pathlib import Path
import math
import numpy as np
import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.writer_profile.extractor import (
    WriterProfile,
    WriterProfileExtractor,
    extract_mean_slant_deg,
    extract_mean_aspect_ratio,
    extract_spacing_ratios,
    extract_baseline_jitter_std,
    extract_writer_profile,
    validate_writer_profile,
)

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "writer_profile_synthetic_samples.json"
)


# =============================================================================
# 1. Kiểm thử ước lượng góc nghiêng (Slant Angle Estimation)
# =============================================================================

def test_extract_slant_accuracy():
    # 1. Nét thẳng đứng hoàn hảo (dx=0, dy=10)
    vert_strokes = [np.array([[10.0, 0.0], [10.0, 10.0]])]
    slant_0 = extract_mean_slant_deg(vert_strokes)
    assert abs(slant_0) < 1e-3, f"Nét thẳng đứng phải có slant ~0, nhận: {slant_0}"

    # 2. Nét nghiêng phải chuẩn 15.0 độ
    # dx = 10 * tan(15 deg) = 10 * 0.267949 = 2.6795
    dx_15 = 10.0 * math.tan(math.radians(15.0))
    slant_15_strokes = [np.array([[10.0, 0.0], [10.0 + dx_15, 10.0]])]
    slant_15 = extract_mean_slant_deg(slant_15_strokes)
    assert abs(slant_15 - 15.0) < 0.1, f"Nét nghiêng 15 độ phải đo ra ~15.0, nhận: {slant_15}"

    # 3. Nét nghiêng trái chuẩn -12.0 độ
    dx_minus_12 = 10.0 * math.tan(math.radians(-12.0))
    slant_m12_strokes = [np.array([[10.0, 0.0], [10.0 + dx_minus_12, 10.0]])]
    slant_m12 = extract_mean_slant_deg(slant_m12_strokes)
    assert abs(slant_m12 - (-12.0)) < 0.1, f"Nét nghiêng -12 độ phải đo ra ~ -12.0, nhận: {slant_m12}"

    # 4. Tập rỗng hoặc chỉ có nét ngang
    horiz_strokes = [np.array([[0.0, 10.0], [20.0, 10.0]])]
    slant_h = extract_mean_slant_deg(horiz_strokes)
    assert slant_h == 0.0, "Nét ngang thuần túy không chứa nét sổ dọc nên slant = 0.0"


# =============================================================================
# 2. Kiểm thử tỷ lệ khung chữ (Aspect Ratio Estimation)
# =============================================================================

def test_extract_aspect_ratio():
    # Ký tự 1: W = 8.0, H = 10.0 -> AR = 0.8
    char1 = [np.array([[10.0, 10.0], [18.0, 10.0], [18.0, 20.0], [10.0, 20.0]])]
    # Ký tự 2: W = 12.0, H = 10.0 -> AR = 1.2
    char2 = [np.array([[20.0, 10.0], [32.0, 10.0], [32.0, 20.0], [20.0, 20.0]])]

    mean_ar = extract_mean_aspect_ratio([char1, char2])
    assert abs(mean_ar - 1.0) < 1e-3, f"Aspect ratio trung bình của (0.8 + 1.2)/2 phải là 1.0, nhận: {mean_ar}"


# =============================================================================
# 3. Kiểm thử khoảng cách chữ và từ (Spacing Estimation)
# =============================================================================

def test_extract_spacing():
    # 2 từ trên cùng 1 dòng
    # Từ 1: 2 ký tự rộng 4.0, gap giữa 2 ký tự = 1.0
    # box: [xmin, ymin, xmax, ymax]
    word1 = [
        (10.0, 10.0, 14.0, 20.0),  # char 1
        (15.0, 10.0, 19.0, 20.0),  # char 2 (gap = 15 - 14 = 1.0)
    ]
    # Từ 2: gap từ = 23 - 19 = 4.0
    word2 = [
        (23.0, 10.0, 27.0, 20.0),  # char 3
        (28.0, 10.0, 32.0, 20.0),  # char 4 (gap = 28 - 27 = 1.0)
    ]

    c_ratio, w_ratio, l_ratio = extract_spacing_ratios([word1, word2])
    # char width = 4.0, char gap = 1.0 -> c_ratio = 1.0 / 4.0 = 0.25
    assert abs(c_ratio - 0.25) < 0.05, f"char_spacing_mean_ratio phải ~0.25, nhận: {c_ratio}"
    # word gap = 4.0 -> w_ratio = 4.0 / 4.0 = 1.0
    assert abs(w_ratio - 1.0) < 0.05, f"word_spacing_mean_ratio phải ~1.0, nhận: {w_ratio}"


# =============================================================================
# 4. Kiểm thử độ dao động baseline (Baseline Jitter Estimation)
# =============================================================================

def test_extract_baseline_jitter():
    # 1. Đường chân dòng phẳng nằm ngang y = 30.0 -> jitter = 0.0
    flat_pts = [(10.0, 30.0), (20.0, 30.0), (30.0, 30.0), (40.0, 30.0)]
    j_flat = extract_baseline_jitter_std(flat_pts)
    assert abs(j_flat) < 1e-4, f"Baseline phẳng phải có jitter ~0.0, nhận: {j_flat}"

    # 2. Đường chân dòng dốc nghiêng đều y = 0.5 * x + 10.0 -> jitter = 0.0 (không bị nhầm độ dốc với rung lắc)
    sloped_pts = [(10.0, 15.0), (20.0, 20.0), (30.0, 25.0), (40.0, 30.0)]
    j_sloped = extract_baseline_jitter_std(sloped_pts)
    assert abs(j_sloped) < 1e-4, f"Baseline dốc đều thẳng tắp phải có jitter ~0.0, nhận: {j_sloped}"

    # 3. Đường chân dòng zíc zắc dao động
    jittery_pts = [(10.0, 30.5), (20.0, 29.5), (30.0, 31.0), (40.0, 29.0)]
    j_noisy = extract_baseline_jitter_std(jittery_pts)
    assert j_noisy > 0.5, f"Baseline zíc zắc phải có jitter > 0.5 mm, nhận: {j_noisy}"


# =============================================================================
# 5. Kiểm thử đối tượng WriterProfile và Serialization
# =============================================================================

def test_writer_profile_object_and_dict():
    extractor = WriterProfileExtractor(version="1.0.0")
    dummy_strokes = [
        np.array([[10.0, 20.0], [12.0, 30.0]]),
        np.array([[15.0, 20.0], [17.0, 30.0]]),
    ]
    profile = extractor.extract_from_samples(
        writer_id="W001",
        strokes=dummy_strokes,
        diacritic_offset_bias=[0.1, -0.2],
        diacritic_scale_ratio=1.05,
        allograph_tendencies={"terminal_hook": 0.8},
        num_samples_analyzed=10,
    )

    p_dict = profile.to_dict()
    assert p_dict["profile_id"] == "profile_W001_v1"
    assert p_dict["writer_id"] == "W001"
    assert p_dict["version"] == "1.0.0"
    assert p_dict["num_samples_analyzed"] == 10
    assert "mean_slant_deg" in p_dict["global_style"]
    assert p_dict["diacritic_tendencies"]["diacritic_offset_bias"] == [0.1, -0.2]
    assert p_dict["allograph_tendencies"]["terminal_hook"] == 0.8


# =============================================================================
# 6. Kiểm thử Schema Validation
# =============================================================================

def test_writer_profile_validation():
    valid_dict = {
        "profile_id": "profile_W001_v1",
        "writer_id": "W001",
        "version": "1.0.0",
        "created_at": "2026-09-25T10:00:00Z",
        "num_samples_analyzed": 50,
        "global_style": {
            "mean_slant_deg": 12.5,
            "aspect_ratio_mean": 0.85,
            "stroke_width_mean_mm": 0.5,
            "baseline_jitter_std": 0.15,
        },
        "spacing": {
            "char_spacing_mean_ratio": 0.25,
            "word_spacing_mean_ratio": 0.85,
            "line_spacing_mean_ratio": 1.5,
        },
        "diacritic_tendencies": {
            "diacritic_offset_bias": [0.0, 0.1],
            "diacritic_scale_ratio": 1.0,
        },
        "allograph_tendencies": {},
    }

    is_valid, errors = validate_writer_profile(valid_dict)
    assert is_valid, f"Profile hợp lệ bị báo lỗi: {errors}"

    # Thử trường hợp vi phạm: mean_slant_deg vượt trần 45 độ
    invalid_dict = dict(valid_dict)
    invalid_dict["global_style"] = dict(valid_dict["global_style"])
    invalid_dict["global_style"]["mean_slant_deg"] = 65.0
    is_valid_inv, errors_inv = validate_writer_profile(invalid_dict)
    assert not is_valid_inv
    assert any("mean_slant_deg" in e for e in errors_inv)


# =============================================================================
# 7. Kiểm thử dữ liệu mẫu giả lập từ Fixture JSON
# =============================================================================

def test_synthetic_fixture_extraction():
    assert os.path.exists(FIXTURE_PATH), f"Không tìm thấy fixture {FIXTURE_PATH}"

    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    synthetic_writers = data["synthetic_writers"]

    # 1. W_VERTICAL
    w_vert = synthetic_writers["W_VERTICAL"]
    strokes_vert = [np.array(s, dtype=float) for s in w_vert["strokes"]]
    bp_vert = [tuple(p) for p in w_vert["baseline_points"]]
    char_groups_vert = [
        [np.array(s, dtype=float) for s in group]
        for group in w_vert["character_stroke_groups"]
    ]

    prof_vert = extract_writer_profile(
        writer_id=w_vert["writer_id"],
        strokes=strokes_vert,
        character_stroke_groups=char_groups_vert,
        baseline_points=bp_vert,
    )
    p_dict_vert = prof_vert.to_dict()
    is_valid, errs = validate_writer_profile(p_dict_vert)
    assert is_valid, f"Profile W_VERTICAL không hợp lệ: {errs}"

    slant_vert = p_dict_vert["global_style"]["mean_slant_deg"]
    assert w_vert["expected_slant_range"][0] <= slant_vert <= w_vert["expected_slant_range"][1]
    jitter_vert = p_dict_vert["global_style"]["baseline_jitter_std"]
    assert jitter_vert <= w_vert["expected_jitter_max"]

    # 2. W_SLANTED_15DEG
    w_slant = synthetic_writers["W_SLANTED_15DEG"]
    strokes_slant = [np.array(s, dtype=float) for s in w_slant["strokes"]]
    bp_slant = [tuple(p) for p in w_slant["baseline_points"]]
    char_groups_slant = [
        [np.array(s, dtype=float) for s in group]
        for group in w_slant["character_stroke_groups"]
    ]

    prof_slant = extract_writer_profile(
        writer_id=w_slant["writer_id"],
        strokes=strokes_slant,
        character_stroke_groups=char_groups_slant,
        baseline_points=bp_slant,
    )
    p_dict_slant = prof_slant.to_dict()
    is_valid_s, errs_s = validate_writer_profile(p_dict_slant)
    assert is_valid_s, f"Profile W_SLANTED_15DEG không hợp lệ: {errs_s}"

    slant_val = p_dict_slant["global_style"]["mean_slant_deg"]
    assert w_slant["expected_slant_range"][0] <= slant_val <= w_slant["expected_slant_range"][1]

    # 3. W_JITTERY_BASELINE
    w_jit = synthetic_writers["W_JITTERY_BASELINE"]
    strokes_jit = [np.array(s, dtype=float) for s in w_jit["strokes"]]
    bp_jit = [tuple(p) for p in w_jit["baseline_points"]]

    prof_jit = extract_writer_profile(
        writer_id=w_jit["writer_id"],
        strokes=strokes_jit,
        baseline_points=bp_jit,
    )
    p_dict_jit = prof_jit.to_dict()
    is_valid_j, errs_j = validate_writer_profile(p_dict_jit)
    assert is_valid_j, f"Profile W_JITTERY_BASELINE không hợp lệ: {errs_j}"

    jitter_val = p_dict_jit["global_style"]["baseline_jitter_std"]
    assert jitter_val >= w_jit["expected_jitter_min"]
