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
    record_profile_crop_provenance,
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


def test_record_profile_crop_provenance_ledger(tmp_path):
    ledger_file = tmp_path / "crop_provenance_ledger.jsonl"
    used_crops = [
        {
            "cell_id": "P01_C01",
            "sample_id": "SMP_W001_001",
            "crop_file": "crops/SMP_W001_001_crop.png",
            "qc_status": "QC_AUTO_PASS",
            "context_tag": "isolated",
        },
        {
            "cell_id": "P01_C02",
            "sample_id": "SMP_W001_002",
            "crop_file": "crops/SMP_W001_002_crop.png",
            "qc_status": "QC_AUTO_PASS",
            "context_tag": "isolated",
        }
    ]

    out_p = record_profile_crop_provenance(
        profile_id="profile_W001_v1",
        writer_id="W001",
        used_crops_metadata=used_crops,
        ledger_path=ledger_file,
        scan_id="W001_S01_P01",
    )

    assert out_p.exists()
    with open(out_p, "r", encoding="utf-8") as f:
        lines = [json.loads(line.strip()) for line in f if line.strip()]

    assert len(lines) == 2
    assert lines[0]["profile_id"] == "profile_W001_v1"
    assert lines[0]["writer_id"] == "W001"
    assert lines[0]["scan_id"] == "W001_S01_P01"
    assert lines[0]["cell_id"] == "P01_C01"
    assert lines[0]["qc_status"] == "QC_AUTO_PASS"

    assert lines[1]["cell_id"] == "P01_C02"


def test_generate_writer_profile_from_report_with_provenance_ledger(tmp_path):
    dpi = 600
    crops_dir = tmp_path / "crops"
    crops_dir.mkdir(parents=True)

    img = create_synthetic_char_crop(slant_deg=8.0)
    crop_filename = "SMP_W002_001_crop.png"
    cv2.imwrite(str(crops_dir / crop_filename), img)

    mock_report = {
        "is_success": True,
        "scan_id": "W002_S01_P01",
        "form_type": "P01",
        "input_file": "W002_S01_P01.png",
        "target_dpi": dpi,
        "overall_status": "SHEET_PASS",
        "crops_metadata": [
            {
                "cell_id": "P01_C01",
                "sample_id": "SMP_W002_001",
                "context_tag": "isolated",
                "crop_file": f"crops/{crop_filename}",
                "qc_status": "QC_AUTO_PASS",
                "is_valid_for_dataset": True,
            },
            {
                "cell_id": "P01_C02",
                "sample_id": "SMP_W002_002",
                "context_tag": "isolated",
                "crop_file": "crops/rejected.png",
                "qc_status": "QC_REJECTED",
                "is_valid_for_dataset": False,
            }
        ]
    }

    ledger_file = tmp_path / "provenance" / "crop_provenance_ledger.jsonl"

    profile = generate_writer_profile_from_report(
        report_dict=mock_report,
        writer_id="W002",
        crops_base_dir=tmp_path,
        dpi=dpi,
        provenance_ledger_path=ledger_file,
    )

    # 1. Profile hợp lệ 9 trường theo schema
    assert profile.writer_id == "W002"
    p_dict = profile.to_dict()
    is_valid, errors = validate_writer_profile(p_dict)
    assert is_valid, f"Profile không hợp lệ: {errors}"
    assert "provenance_manifest" not in p_dict

    # 2. Ledger ghi đúng ô hợp lệ, bỏ qua ô bị từ chối
    assert ledger_file.exists()
    with open(ledger_file, "r", encoding="utf-8") as f:
        ledger_lines = [json.loads(line.strip()) for line in f if line.strip()]

    assert len(ledger_lines) == 1
    assert ledger_lines[0]["scan_id"] == "W002_S01_P01"
    assert ledger_lines[0]["cell_id"] == "P01_C01"
    assert ledger_lines[0]["profile_id"] == profile.profile_id


def test_synthetic_features_fixture_integrity():
    fixture_path = _REPO_ROOT / "tests" / "fixtures" / "synthetic_writer_features_summary.jsonl"
    assert fixture_path.exists(), f"Không tìm thấy fixture: {fixture_path}"

    with open(fixture_path, "r", encoding="utf-8") as f:
        rows = [json.loads(line.strip()) for line in f if line.strip()]

    assert len(rows) == 3
    writer_ids = [r["writer_id"] for r in rows]
    assert writer_ids == ["W001", "W002", "W003"]
    for r in rows:
        assert "profile_id" in r
        assert "mean_slant_deg" in r
        assert "aspect_ratio_mean" in r
        assert "baseline_jitter_std" in r


def test_provenance_ledger_excludes_invalid_dataset_crops(tmp_path):
    """Kiểm thử bẫy lỗi 1: Các crop có is_valid_for_dataset=False tuyệt đối không được ghi vào ledger."""
    dpi = 600
    crops_dir = tmp_path / "crops"
    crops_dir.mkdir(parents=True)

    img = create_synthetic_char_crop(slant_deg=0.0)
    valid_crop_file = "SMP_W003_001_valid.png"
    invalid_crop_file = "SMP_W003_002_invalid.png"
    cv2.imwrite(str(crops_dir / valid_crop_file), img)
    cv2.imwrite(str(crops_dir / invalid_crop_file), img)

    mock_report = {
        "is_success": True,
        "scan_id": "W003_S01_P01",
        "form_type": "P01",
        "input_file": "W003_S01_P01.png",
        "target_dpi": dpi,
        "overall_status": "SHEET_PASS",
        "crops_metadata": [
            {
                "cell_id": "P01_C01",
                "sample_id": "SMP_W003_001",
                "context_tag": "isolated",
                "crop_file": f"crops/{valid_crop_file}",
                "qc_status": "QC_AUTO_PASS",
                "is_valid_for_dataset": True,
            },
            {
                "cell_id": "P01_C02",
                "sample_id": "SMP_W003_002",
                "context_tag": "isolated",
                "crop_file": f"crops/{invalid_crop_file}",
                "qc_status": "QC_AUTO_PASS",  # Dù QC_AUTO_PASS nhưng is_valid_for_dataset=False (bị loại)
                "is_valid_for_dataset": False,
            }
        ]
    }

    ledger_file = tmp_path / "provenance" / "crop_provenance_ledger.jsonl"

    profile = generate_writer_profile_from_report(
        report_dict=mock_report,
        writer_id="W003",
        crops_base_dir=tmp_path,
        dpi=dpi,
        provenance_ledger_path=ledger_file,
    )

    assert profile.num_samples_analyzed == 1
    assert ledger_file.exists()
    with open(ledger_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line.strip()) for line in f if line.strip()]

    # Chỉ ghi nhận đúng 1 ô hợp lệ thực sự tham gia tính toán
    assert len(lines) == 1
    assert lines[0]["cell_id"] == "P01_C01"
    assert lines[0]["sample_id"] == "SMP_W003_001"


def test_provenance_ledger_rejects_missing_traceability_ids(tmp_path):
    """Kiểm thử bẫy lỗi 2: Từ chối fail-closed khi thiếu scan_id hoặc cell_id, không ghi UNKNOWN_*."""
    ledger_file = tmp_path / "crop_provenance_ledger.jsonl"

    # Ca A: Thiếu scan_id
    crop_missing_scan = [{
        "cell_id": "P01_C01",
        "sample_id": "SMP_001",
        "crop_file": "crops/c1.png",
        "is_valid": True,
    }]
    with pytest.raises(ValueError, match="scan_id"):
        record_profile_crop_provenance(
            profile_id="profile_W001_v1",
            writer_id="W001",
            used_crops_metadata=crop_missing_scan,
            ledger_path=ledger_file,
            scan_id=None,
        )

    # Ca B: Thiếu cả cell_id và sample_id
    crop_missing_cell = [{
        "scan_id": "W001_S01_P01",
        "crop_file": "crops/c1.png",
        "is_valid": True,
    }]
    with pytest.raises(ValueError, match="cell_id"):
        record_profile_crop_provenance(
            profile_id="profile_W001_v1",
            writer_id="W001",
            used_crops_metadata=crop_missing_cell,
            ledger_path=ledger_file,
            scan_id="W001_S01_P01",
        )

    # Bảo đảm không tạo file hoặc không ghi rác UNKNOWN_*
    if ledger_file.exists():
        with open(ledger_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "UNKNOWN_SCAN" not in content
        assert "UNKNOWN_CELL" not in content


def test_provenance_ledger_deterministic_rerun_no_duplicates(tmp_path):
    """Kiểm thử bẫy lỗi 3: Chạy lại cùng một profile xử lý một cách xác định (idempotent, không tạo dòng trùng)."""
    ledger_file = tmp_path / "crop_provenance_ledger.jsonl"

    crops_w1 = [
        {"cell_id": "P01_C01", "sample_id": "SMP_W001_001", "scan_id": "W001_S01_P01"},
        {"cell_id": "P01_C02", "sample_id": "SMP_W001_002", "scan_id": "W001_S01_P01"},
    ]

    # Lần chạy 1 cho W001
    record_profile_crop_provenance("profile_W001_v1", "W001", crops_w1, ledger_file)
    with open(ledger_file, "r", encoding="utf-8") as f:
        lines_run1 = [line.strip() for line in f if line.strip()]
    assert len(lines_run1) == 2

    # Lần chạy 2 (chạy lại W001): Số dòng phải giữ nguyên là 2 (không bị nhân đôi lên 4)
    record_profile_crop_provenance("profile_W001_v1", "W001", crops_w1, ledger_file)
    with open(ledger_file, "r", encoding="utf-8") as f:
        lines_run2 = [line.strip() for line in f if line.strip()]
    assert len(lines_run2) == 2
    assert lines_run2 == lines_run1

    # Thêm W002
    crops_w2 = [
        {"cell_id": "P01_C01", "sample_id": "SMP_W002_001", "scan_id": "W002_S01_P01"},
    ]
    record_profile_crop_provenance("profile_W002_v1", "W002", crops_w2, ledger_file)
    with open(ledger_file, "r", encoding="utf-8") as f:
        lines_run3 = [json.loads(line.strip()) for line in f if line.strip()]
    assert len(lines_run3) == 3
    profiles_recorded = [r["profile_id"] for r in lines_run3]
    assert profiles_recorded == ["profile_W001_v1", "profile_W001_v1", "profile_W002_v1"]


def test_pilot_mode_requires_provenance_ledger(tmp_path):
    """Kiểm thử yêu cầu pilot: Bắt buộc chỉ định provenance ledger, không âm thầm bỏ qua."""
    mock_report = {
        "is_success": True,
        "is_pilot": True,
        "scan_id": "W001_S01_P01",
        "form_type": "P01",
        "crops_metadata": []
    }

    # Bị từ chối vì is_pilot=True nhưng không truyền provenance_ledger_path
    with pytest.raises(ValueError, match="chỉ định provenance_ledger_path"):
        generate_writer_profile_from_report(
            report_dict=mock_report,
            writer_id="W001",
            provenance_ledger_path=None,
        )

    # Khi require_provenance=True cũng phải từ chối
    with pytest.raises(ValueError, match="chỉ định provenance_ledger_path"):
        generate_writer_profile_from_report(
            report_dict={"is_success": True, "crops_metadata": []},
            writer_id="W001",
            provenance_ledger_path=None,
            require_provenance=True,
        )


def test_provenance_ledger_excludes_blank_or_no_stroke_crops(tmp_path):
    """Kiểm thử đối chiếu: Crop ảnh trắng/không trích xuất được nét bị loại khỏi ledger, khớp num_samples_analyzed."""
    dpi = 600
    crops_dir = tmp_path / "crops"
    crops_dir.mkdir(parents=True)

    # Crop 1: Có nét chữ hợp lệ
    img_valid = create_synthetic_char_crop(slant_deg=0.0)
    valid_crop_file = "SMP_W004_001_valid.png"
    cv2.imwrite(str(crops_dir / valid_crop_file), img_valid)

    # Crop 2: Ảnh trắng tinh (255) không có nét, dù metadata đánh dấu hợp lệ
    img_blank = np.full((120, 120), 255, dtype=np.uint8)
    blank_crop_file = "SMP_W004_002_blank.png"
    cv2.imwrite(str(crops_dir / blank_crop_file), img_blank)

    mock_report = {
        "is_success": True,
        "scan_id": "W004_S01_P01",
        "form_type": "P01",
        "input_file": "W004_S01_P01.png",
        "target_dpi": dpi,
        "overall_status": "SHEET_PASS",
        "crops_metadata": [
            {
                "cell_id": "P01_C01",
                "sample_id": "SMP_W004_001",
                "context_tag": "isolated",
                "crop_file": f"crops/{valid_crop_file}",
                "qc_status": "QC_AUTO_PASS",
                "is_valid_for_dataset": True,
            },
            {
                "cell_id": "P01_C02",
                "sample_id": "SMP_W004_002",
                "context_tag": "isolated",
                "crop_file": f"crops/{blank_crop_file}",
                "qc_status": "QC_AUTO_PASS",  # Đánh dấu PASS nhưng ảnh trắng không có nét
                "is_valid_for_dataset": True,
            }
        ]
    }

    ledger_file = tmp_path / "provenance" / "crop_provenance_ledger.jsonl"

    profile = generate_writer_profile_from_report(
        report_dict=mock_report,
        writer_id="W004",
        crops_base_dir=tmp_path,
        dpi=dpi,
        provenance_ledger_path=ledger_file,
    )

    # 1. Extractor chỉ tính ô có nét thực tế
    assert profile.num_samples_analyzed == 1

    # 2. Đọc ledger và đối chiếu hai bên
    assert ledger_file.exists()
    with open(ledger_file, "r", encoding="utf-8") as f:
        ledger_records = [json.loads(line.strip()) for line in f if line.strip()]

    # Số bản ghi trong ledger phải KHỚP TUYỆT ĐỐI với số mẫu extractor phân tích
    assert len(ledger_records) == profile.num_samples_analyzed == 1
    assert ledger_records[0]["cell_id"] == "P01_C01"
    assert ledger_records[0]["sample_id"] == "SMP_W004_001"
    # Ô ảnh trắng P01_C02 tuyệt đối không được xuất hiện
    assert all(r["cell_id"] != "P01_C02" for r in ledger_records)


def test_provenance_ledger_rejects_missing_or_path_scan_id(tmp_path):
    """Kiểm thử fail-closed: Từ chối thiếu scan_id hoặc dùng đường dẫn tệp/đuôi file thay thế."""
    dpi = 600
    crops_dir = tmp_path / "crops"
    crops_dir.mkdir(parents=True)
    img = create_synthetic_char_crop()
    cv2.imwrite(str(crops_dir / "crop1.png"), img)
    ledger_file = tmp_path / "ledger.jsonl"

    # Ca 1: Thiếu scan_id trong report, có input_file -> Cấm lấy input_file thay thế, phải raise ValueError
    report_missing_scan_id = {
        "is_success": True,
        "input_file": "scans/raw_page_01.png",
        "crops_metadata": [{
            "cell_id": "P01_C01",
            "sample_id": "SMP_001",
            "crop_file": "crops/crop1.png",
            "is_valid_for_dataset": True,
        }]
    }
    with pytest.raises(ValueError, match="scan_id"):
        generate_writer_profile_from_report(
            report_dict=report_missing_scan_id,
            writer_id="W001",
            crops_base_dir=tmp_path,
            dpi=dpi,
            provenance_ledger_path=ledger_file,
        )

    # Ca 2: scan_id mang đuôi file ảnh (.png) trong report -> Bị từ chối
    report_ext_scan_id = {
        "is_success": True,
        "scan_id": "W001_S01_P01.png",
        "crops_metadata": [{
            "cell_id": "P01_C01",
            "sample_id": "SMP_001",
            "crop_file": "crops/crop1.png",
            "is_valid_for_dataset": True,
        }]
    }
    with pytest.raises(ValueError, match="đường dẫn tệp không hợp lệ"):
        generate_writer_profile_from_report(
            report_dict=report_ext_scan_id,
            writer_id="W001",
            crops_base_dir=tmp_path,
            dpi=dpi,
            provenance_ledger_path=ledger_file,
        )

    # Ca 3: record_profile_crop_provenance trực tiếp với scan_id chứa đường dẫn thư mục
    with pytest.raises(ValueError, match="đường dẫn tệp không hợp lệ"):
        record_profile_crop_provenance(
            profile_id="profile_W001_v1",
            writer_id="W001",
            used_crops_metadata=[{
                "cell_id": "P01_C01",
                "sample_id": "SMP_001",
                "scan_id": "scans/W001_S01_P01",
                "is_valid_for_dataset": True,
            }],
            ledger_path=ledger_file,
        )


def test_provenance_ledger_preserves_corrupted_file_on_error(tmp_path):
    """Kiểm thử fail-closed & toàn vẹn dữ liệu: Khi ledger cũ có dòng JSON hỏng, báo lỗi và giữ nguyên 100% tệp cũ."""
    ledger_file = tmp_path / "corrupted_ledger.jsonl"

    # Tạo tệp ledger cũ chứa 1 dòng hợp lệ và 1 dòng JSON bị hỏng
    initial_content = (
        '{"profile_id": "profile_W001_v1", "writer_id": "W001", "scan_id": "W001_S01_P01", "cell_id": "P01_C01"}\n'
        '{"corrupted_json_line: INVALID_SYNTAX\n'
    )
    ledger_file.write_text(initial_content, encoding="utf-8")
    initial_bytes = ledger_file.read_bytes()

    crops_new = [
        {"cell_id": "P01_C02", "sample_id": "SMP_W002_002", "scan_id": "W002_S01_P01"},
    ]

    # Cố gắng ghi bản ghi mới vào ledger hỏng -> Phải lập tức ném ValueError
    with pytest.raises(ValueError, match="Phát hiện dòng JSON bị lỗi cấu trúc"):
        record_profile_crop_provenance(
            profile_id="profile_W002_v1",
            writer_id="W002",
            used_crops_metadata=crops_new,
            ledger_path=ledger_file,
        )

    # Kiểm tra chứng minh không mất dữ liệu: Nội dung tệp cũ phải giữ nguyên 100% từng byte
    assert ledger_file.exists()
    assert ledger_file.read_bytes() == initial_bytes
