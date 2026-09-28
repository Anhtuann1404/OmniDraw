"""
Unit Tests for OmniDraw Dataset Schemas & Validators.

Đường chạy: TV1 — AI Data & Writer Profile Lead
Kiểm chuẩn toàn diện:
1. Tính toàn vẹn cấu trúc của cả 3 tệp JSON Schema trong dataset/schemas/:
   - writer_profile.schema.json (P2 Personalization)
   - collection_manifest.schema.json (Doc 21 Section 6.2)
   - ca_vhc_annotation.schema.json (Doc 08 Section 7.2)
2. Thẩm định quy tắc dữ liệu cho Collection Manifest Record.
3. Thẩm định quy tắc dữ liệu cho CA-VHC Annotation Record.
4. Cơ chế bẫy lỗi fail-closed khi thiếu trường, sai enum hoặc sai miền giá trị.
"""

import json
from pathlib import Path
import pytest

from backend.scan_validator.schema_validator import (
    load_schema,
    validate_manifest_record,
    validate_ca_vhc_annotation,
    VALID_PAGE_IDS,
    VALID_QC_STATUSES,
    VALID_ANOMALY_STATUSES,
)

_SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "dataset" / "schemas"


# =============================================================================
# 1. Kiểm thử Tính toàn vẹn của các file JSON Schema
# =============================================================================

@pytest.mark.parametrize("schema_file,expected_title", [
    ("writer_profile.schema.json", "OmniDraw_Writer_Profile_Schema"),
    ("collection_manifest.schema.json", "OmniDraw_Collection_Manifest_Schema"),
    ("ca_vhc_annotation.schema.json", "OmniDraw_CA_VHC_Annotation_Schema"),
])
def test_schema_file_integrity(schema_file, expected_title):
    path = _SCHEMAS_DIR / schema_file
    assert path.exists(), f"Không tìm thấy file schema: {path}"

    with open(path, "r", encoding="utf-8") as f:
        schema_data = json.load(f)

    assert schema_data.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
    assert schema_data.get("title") == expected_title
    assert schema_data.get("type") == "object"
    assert isinstance(schema_data.get("required"), list)
    assert len(schema_data["required"]) > 0
    assert isinstance(schema_data.get("properties"), dict)
    assert len(schema_data["properties"]) > 0


def test_load_schema_helper():
    manifest_schema = load_schema("collection_manifest.schema.json")
    assert manifest_schema["title"] == "OmniDraw_Collection_Manifest_Schema"

    with pytest.raises(FileNotFoundError):
        load_schema("non_existent_schema_file.json")


# =============================================================================
# 2. Kiểm thử Thẩm định Collection Manifest Record
# =============================================================================

def test_validate_manifest_record_valid():
    valid_record = {
        "scan_id": "W001_S01_P01",
        "writer_id": "W001",
        "session_id": "S01",
        "page_id": "P01",
        "is_spare": False,
        "scan_timestamp": "2026-09-25T10:00:00Z",
        "scanner_model": "Epson Perfection V39 II",
        "optical_dpi": 600,
        "calibration_metrics": {
            "ruler_length_mm": 50.04,
            "ruler_error_mm": 0.04,
            "square_aspect_ratio": 1.001,
            "deskew_angle_deg": -0.15,
        },
        "qc_status": "QC_VERIFIED_PASS",
        "qc_operator": "TV1",
        "cell_anomalies": [
            {
                "cell_id": "TONE_002",
                "status": "USER_MISWRITTEN",
                "note": "Viết nhầm dấu sắc thay vì huyền",
            }
        ],
    }

    is_valid, errors = validate_manifest_record(valid_record)
    assert is_valid is True, f"Bản ghi hợp lệ bị báo lỗi: {errors}"
    assert len(errors) == 0


def test_validate_manifest_record_missing_required():
    incomplete_record = {
        "scan_id": "W001_S01_P01",
        # Thiếu writer_id, page_id, qc_status, v.v.
    }
    is_valid, errors = validate_manifest_record(incomplete_record)
    assert is_valid is False
    assert any("writer_id" in err for err in errors)
    assert any("page_id" in err for err in errors)
    assert any("qc_status" in err for err in errors)


def test_validate_manifest_record_invalid_page_and_status():
    record = {
        "scan_id": "W001_S01_P01",
        "writer_id": "W001",
        "session_id": "S01",
        "page_id": "P05",  # Sai: chỉ chấp nhận P01..P04
        "is_spare": False,
        "scan_timestamp": "2026-09-25T10:00:00Z",
        "scanner_model": "Epson Perfection V39 II",
        "optical_dpi": 600,
        "calibration_metrics": {
            "ruler_length_mm": 50.0,
            "ruler_error_mm": 0.0,
            "square_aspect_ratio": 1.0,
            "deskew_angle_deg": 0.0,
        },
        "qc_status": "QC_UNKNOWN_STATUS",  # Sai enum
        "qc_operator": "TV1",
    }
    is_valid, errors = validate_manifest_record(record)
    assert is_valid is False
    assert any("page_id" in err for err in errors)
    assert any("qc_status" in err for err in errors)


def test_validate_manifest_record_calibration_bounds():
    record = {
        "scan_id": "W001_S01_P01",
        "writer_id": "W001",
        "session_id": "S01",
        "page_id": "P01",
        "is_spare": False,
        "scan_timestamp": "2026-09-25T10:00:00Z",
        "scanner_model": "Epson Perfection V39 II",
        "optical_dpi": 600,
        "calibration_metrics": {
            "ruler_length_mm": -5.0,  # Âm
            "ruler_error_mm": 0.0,
            "square_aspect_ratio": 2.5,  # Vượt quá [0.5, 1.5]
            "deskew_angle_deg": 0.0,
        },
        "qc_status": "QC_AUTO_PASS",
        "qc_operator": "TV1",
    }
    is_valid, errors = validate_manifest_record(record)
    assert is_valid is False
    assert any("ruler_length_mm" in err for err in errors)
    assert any("square_aspect_ratio" in err for err in errors)


def test_validate_manifest_record_anomalies():
    # Anomaly sai status
    record = {
        "scan_id": "W001_S01_P01",
        "writer_id": "W001",
        "session_id": "S01",
        "page_id": "P01",
        "is_spare": False,
        "scan_timestamp": "2026-09-25T10:00:00Z",
        "scanner_model": "Epson Perfection V39 II",
        "optical_dpi": 600,
        "calibration_metrics": {
            "ruler_length_mm": 50.0,
            "ruler_error_mm": 0.0,
            "square_aspect_ratio": 1.0,
            "deskew_angle_deg": 0.0,
        },
        "qc_status": "QC_AUTO_FLAGGED",
        "qc_operator": "TV1",
        "cell_anomalies": [
            {"cell_id": "BASE_001", "status": "INVALID_STATUS_TAG"}
        ],
    }
    is_valid, errors = validate_manifest_record(record)
    assert is_valid is False
    assert any("cell_anomalies[0].status" in err for err in errors)


# =============================================================================
# 3. Kiểm thử Thẩm định CA-VHC Annotation Record
# =============================================================================

def test_validate_ca_vhc_annotation_valid():
    valid_annotation = {
        "sample_id": "SMP_W001_00421",
        "writer_id": "W001",
        "source_image_id": "W001_S01_P01.png",
        "timestamp": "2026-09-25T10:15:30Z",
        "char_raw": "ế",
        "unicode_nfd": "e\u0302\u0301",
        "base_char": "e",
        "diacritics": [
            {
                "type": "circumflex",
                "unicode_codepoint": "U+0302",
                "bounding_box": [120.0, 45.0, 160.0, 75.0],
            },
            {
                "type": "acute",
                "unicode_codepoint": "U+0301",
                "bounding_box": [140.0, 20.0, 170.0, 45.0],
            }
        ],
        "tone_mark": "acute",
        "context_info": {
            "position": "word_medial",
            "prev_char": "u",
            "next_char": "n",
            "syllable_text": "nguyễn",
            "letter_type": "general",
        },
        "geometry": {
            "bounding_box": [100.0, 20.0, 180.0, 150.0],
            "baseline_y": 140.0,
            "base_anchor": [140.0, 50.0],
            "diacritic_anchor": [145.0, 35.0],
            "diacritic_offset": [0.35, -0.20],
            "clearance_box": [95.0, 15.0, 185.0, 155.0],
        },
        "quality_flags": {
            "legibility_score": 5,
            "is_degenerate": False,
            "is_ambiguous": False,
            "annotator_id": "TV1",
        },
    }

    is_valid, errors = validate_ca_vhc_annotation(valid_annotation)
    assert is_valid is True, f"Annotation hợp lệ bị báo lỗi: {errors}"
    assert len(errors) == 0


def test_validate_ca_vhc_annotation_missing_fields():
    incomplete = {
        "sample_id": "SMP_W001_00421",
        "writer_id": "W001",
    }
    is_valid, errors = validate_ca_vhc_annotation(incomplete)
    assert is_valid is False
    assert any("geometry" in err for err in errors)
    assert any("quality_flags" in err for err in errors)
    assert any("diacritics" in err for err in errors)


def test_validate_ca_vhc_annotation_invalid_enums():
    annotation = {
        "sample_id": "SMP_W001_00421",
        "writer_id": "W001",
        "source_image_id": "W001_S01_P01.png",
        "char_raw": "a",
        "unicode_nfd": "a",
        "base_char": "a",
        "diacritics": [
            {
                "type": "non_existent_mark_type",  # Sai enum
                "unicode_codepoint": "U+9999",
            }
        ],
        "tone_mark": "invalid_tone",  # Sai enum
        "context_info": {
            "position": "middle_of_word",  # Sai enum (phải là word_medial)
        },
        "geometry": {
            "bounding_box": [10.0, 20.0, 30.0],  # Thiếu 1 số (chỉ có 3)
            "baseline_y": 100.0,
            "base_anchor": [15.0, 25.0],
            "diacritic_offset": [0.0, 0.0],
        },
        "quality_flags": {
            "legibility_score": 7,  # Ngoài [1, 5]
            "is_degenerate": "not_a_bool",  # Sai kiểu
            "is_ambiguous": False,
        },
    }
    is_valid, errors = validate_ca_vhc_annotation(annotation)
    assert is_valid is False
    assert any("diacritics[0].type" in err for err in errors)
    assert any("tone_mark" in err for err in errors)
    assert any("context_info.position" in err for err in errors)
    assert any("bounding_box" in err for err in errors)
    assert any("legibility_score" in err for err in errors)
    assert any("is_degenerate" in err for err in errors)
