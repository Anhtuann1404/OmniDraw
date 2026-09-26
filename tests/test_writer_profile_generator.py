"""
Bộ Unit Test Kiểm chuẩn Module Writer Profile Generator (profile_generator.py).

Đường chạy: TV1 — AI Data & Writer Profile Lead
Phục vụ: Kết nối Scan-Validation Pipeline sang Hồ sơ Phong cách Người viết P2.
"""

import json
import os
import sys
from pathlib import Path
import cv2
import numpy as np
import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.writer_profile.profile_generator import (
    extract_strokes_from_image,
    extract_char_boxes_from_image,
    generate_writer_profile_from_crops,
    generate_writer_profile_from_report,
    save_writer_profile,
    px_to_mm,
    mm_to_px,
)
from backend.writer_profile.extractor import validate_writer_profile


def create_synthetic_char_crop(
    slant_deg: float = 0.0,
    width_px: int = 200,
    height_px: int = 200,
    stroke_thickness_px: int = 6,
) -> np.ndarray:
    """Tạo một ảnh crop nền trắng có 1 nét thẳng nghiêng giả lập chữ viết tay."""
    img = np.full((height_px, width_px, 3), 255, dtype=np.uint8)
    cx = width_px // 2
    y1, y2 = 40, height_px - 40
    h = y2 - y1

    dx = int(round(h * np.tan(np.radians(slant_deg))))
    pt1 = (cx - dx // 2, y1)
    pt2 = (cx + dx // 2, y2)

    cv2.line(img, pt1, pt2, (0, 0, 0), stroke_thickness_px)
    return img


def test_px_mm_conversions():
    dpi = 600
    # 25.4 mm = 600 px at 600 DPI
    px = mm_to_px(25.4, dpi)
    assert px == 600
    mm = px_to_mm(600, dpi)
    assert abs(mm - 25.4) < 1e-4


def test_extract_strokes_from_image():
    dpi = 600
    crop = create_synthetic_char_crop(slant_deg=0.0)
    strokes = extract_strokes_from_image(crop, dpi=dpi)

    assert len(strokes) > 0, "Phải trích xuất được ít nhất 1 nét"
    for s in strokes:
        assert isinstance(s, np.ndarray)
        assert s.ndim == 2
        assert s.shape[1] == 2
        # Tọa độ nét phải tính bằng mm (ảnh 200px tại 600DPI là ~8.46mm)
        assert np.all(s >= 0.0)
        assert np.all(s <= 10.0)


def test_extract_char_boxes_from_image():
    dpi = 600
    # Tạo ảnh có 2 khối đen tách biệt (đại diện 2 ký tự trong từ)
    img = np.full((150, 300, 3), 255, dtype=np.uint8)
    cv2.rectangle(img, (50, 40), (100, 110), (0, 0, 0), -1)   # char 1
    cv2.rectangle(img, (150, 40), (200, 110), (0, 0, 0), -1)  # char 2

    boxes = extract_char_boxes_from_image(img, dpi=dpi)
    assert len(boxes) == 2, f"Phải tìm thấy 2 khối ký tự, nhận: {len(boxes)}"
    # Đã được sắp xếp trái sang phải
    assert boxes[0][0] < boxes[1][0]
    # Chiều rộng mỗi khối ~ 50px = ~2.11 mm
    w1 = boxes[0][2] - boxes[0][0]
    assert abs(w1 - px_to_mm(50, dpi)) < 0.2


def test_generate_writer_profile_from_crops():
    dpi = 600
    # Chuẩn bị dữ liệu crop mẫu
    crop1 = create_synthetic_char_crop(slant_deg=10.0)
    crop2 = create_synthetic_char_crop(slant_deg=12.0)

    # Ảnh từ
    word_img = np.full((150, 300, 3), 255, dtype=np.uint8)
    cv2.rectangle(word_img, (50, 40), (100, 110), (0, 0, 0), -1)
    cv2.rectangle(word_img, (130, 40), (180, 110), (0, 0, 0), -1)

    crops_data = [
        {"crop_image": crop1, "context_tag": "isolated", "is_valid": True},
        {"crop_image": crop2, "context_tag": "isolated", "is_valid": True},
        {"crop_image": word_img, "context_tag": "contextual_word", "is_valid": True},
        {"crop_image": None, "context_tag": "isolated", "is_valid": False},  # Test bỏ qua invalid
    ]

    profile = generate_writer_profile_from_crops(
        writer_id="W001",
        crops_data=crops_data,
        dpi=dpi,
        version="1.0.0",
    )

    assert profile.writer_id == "W001"
    assert profile.profile_id == "profile_W001_v1"
    assert profile.num_samples_analyzed == 3

    # Kiểm tra tính hợp thức của profile theo schema
    p_dict = profile.to_dict()
    is_valid, errors = validate_writer_profile(p_dict)
    assert is_valid, f"Profile sinh ra không hợp lệ theo JSON Schema: {errors}"

    # Độ nghiêng phải nằm trong khoảng hợp lý quanh 10-12 độ
    slant = p_dict["global_style"]["mean_slant_deg"]
    assert -45.0 <= slant <= 45.0


def test_save_writer_profile_and_summary_jsonl(tmp_path):
    dpi = 600
    crop = create_synthetic_char_crop(slant_deg=15.0)
    crops_data = [{"crop_image": crop, "context_tag": "isolated", "is_valid": True}]

    # Sinh và lưu W001
    prof1 = generate_writer_profile_from_crops("W001", crops_data, dpi=dpi)
    profiles_dir = tmp_path / "profiles"
    summary_file = tmp_path / "features" / "writer_features_summary.jsonl"

    p1_path = save_writer_profile(prof1, profiles_dir, summary_file)
    assert p1_path.exists()
    assert p1_path.name == "profile_W001_v1.json"

    with open(p1_path, "r", encoding="utf-8") as f:
        loaded_p1 = json.load(f)
    assert loaded_p1["writer_id"] == "W001"

    # Kiểm tra summary JSONL
    assert summary_file.exists()
    with open(summary_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    assert len(lines) == 1
    row1 = json.loads(lines[0])
    assert row1["writer_id"] == "W001"
    assert "mean_slant_deg" in row1

    # Lưu tiếp W002
    prof2 = generate_writer_profile_from_crops("W002", crops_data, dpi=dpi)
    p2_path = save_writer_profile(prof2, profiles_dir, summary_file)
    assert p2_path.exists()

    with open(summary_file, "r", encoding="utf-8") as f:
        lines2 = [line.strip() for line in f if line.strip()]
    assert len(lines2) == 2
    row2 = json.loads(lines2[1])
    assert row2["writer_id"] == "W002"


def test_generate_writer_profile_from_report(tmp_path):
    dpi = 600
    # Chuẩn bị file crop thật trong tmp_path
    crops_dir = tmp_path / "crops"
    crops_dir.mkdir(parents=True)

    img = create_synthetic_char_crop(slant_deg=5.0)
    crop_filename = "SMP_W001_001_crop.png"
    cv2.imwrite(str(crops_dir / crop_filename), img)

    mock_report = {
        "is_success": True,
        "form_type": "P01",
        "input_file": "W001_S01_P01.png",
        "target_dpi": dpi,
        "overall_status": "SHEET_PASS",
        "crops_metadata": [
            {
                "sample_id": "SMP_W001_001",
                "context_tag": "isolated",
                "crop_file": f"crops/{crop_filename}",
                "qc_status": "QC_PASS",
                "is_valid_for_dataset": True,
            },
            {
                "sample_id": "SMP_W001_002",
                "context_tag": "isolated",
                "crop_file": "crops/non_existent.png",
                "qc_status": "QC_REJECTED",
                "is_valid_for_dataset": False,
            }
        ]
    }

    profile = generate_writer_profile_from_report(
        report_dict=mock_report,
        writer_id="W001",
        crops_base_dir=tmp_path,
        dpi=dpi,
    )

    assert profile.writer_id == "W001"
    assert profile.num_samples_analyzed == 1
    is_valid, errors = validate_writer_profile(profile.to_dict())
    assert is_valid, f"Profile từ scan report không hợp lệ: {errors}"
