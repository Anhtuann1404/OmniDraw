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


# =============================================================================
# 4. Kiểm thử Cơ chế Fail-Closed Chặt chẽ (Input Sai Kiểu, ISO 8601, NaN/Inf, Bool)
# =============================================================================

def test_validate_manifest_record_fail_closed_non_dict_and_unhashable_types():
    """Kiểm tra fail-closed khi input không phải dict hoặc chứa kiểu unhashable (list/dict) tại page_id/qc_status."""
    # 1. Non-dict input
    for bad_input in [None, "string", [1, 2, 3], 12345]:
        is_valid, errors = validate_manifest_record(bad_input)
        assert is_valid is False
        assert any("dictionary" in err for err in errors)

    # 2. page_id là list, dict, int (không được ném TypeError do kiểm tra set)
    base_record = {
        "scan_id": "W001_S01_P01",
        "writer_id": "W001",
        "session_id": "S01",
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
    }

    for bad_page_id in [["P01"], {"page": "P01"}, 101, None]:
        rec = dict(base_record)
        rec["page_id"] = bad_page_id
        is_valid, errors = validate_manifest_record(rec)
        assert is_valid is False
        assert any("page_id" in err for err in errors)

    # 3. qc_status là list, dict
    for bad_qc in [["QC_AUTO_PASS"], {"qc": "QC_RAW"}, 999]:
        rec = dict(base_record)
        rec["page_id"] = "P01"
        rec["qc_status"] = bad_qc
        is_valid, errors = validate_manifest_record(rec)
        assert is_valid is False
        assert any("qc_status" in err for err in errors)


def test_validate_manifest_record_fail_closed_iso8601():
    """Kiểm tra fail-closed cho ngày giờ ISO 8601 không hợp lệ hoặc sai định dạng."""
    base_record = {
        "scan_id": "W001_S01_P01",
        "writer_id": "W001",
        "session_id": "S01",
        "page_id": "P01",
        "is_spare": False,
        "scanner_model": "Epson Perfection V39 II",
        "optical_dpi": 600,
        "calibration_metrics": {
            "ruler_length_mm": 50.0,
            "ruler_error_mm": 0.0,
            "square_aspect_ratio": 1.0,
            "deskew_angle_deg": 0.0,
        },
        "qc_status": "QC_AUTO_PASS",
        "qc_operator": "TV1",
    }

    invalid_timestamps = [
        "not-a-timestamp",
        "2026-99-99T99:99:99Z",
        "2026-02-30T10:00:00Z",  # Ngày 30 tháng 2 không tồn tại
        "2026-13-01T10:00:00Z",  # Tháng 13 không tồn tại
        "2026-09-25T10:00:00",  # Thiếu timezone (offset hoặc Z) - vi phạm format: date-time
        "2026-09-25 10:00:00",  # Thiếu timezone
        "2026-09-25T10:00:00.123456",  # Thiếu timezone
        "2026-09-25T10:00:00+25:00",  # Múi giờ vượt quá giới hạn hợp lệ
        123456789,
        None,
        "",
    ]
    for bad_ts in invalid_timestamps:
        rec = dict(base_record)
        rec["scan_timestamp"] = bad_ts
        is_valid, errors = validate_manifest_record(rec)
        assert is_valid is False
        assert any("scan_timestamp" in err for err in errors)

    # Các chuỗi date-time có múi giờ hợp lệ phải PASS
    for valid_ts in [
        "2026-09-25T10:00:00Z",
        "2026-09-25T10:00:00z",
        "2026-09-25T10:00:00+07:00",
        "2026-09-25T10:00:00-05:00",
        "2026-09-25T10:00:00.123Z",
    ]:
        rec = dict(base_record)
        rec["scan_timestamp"] = valid_ts
        is_valid, errors = validate_manifest_record(rec)
        assert is_valid is True, f"Timestamp hợp lệ bị từ chối: {valid_ts}, lỗi: {errors}"


def test_validate_manifest_record_fail_closed_numbers_bool_nan_inf():
    """Kiểm tra loại trừ boolean, NaN, Inf tại các trường số của manifest."""
    base_record = {
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
        "qc_status": "QC_AUTO_PASS",
        "qc_operator": "TV1",
    }

    # 1. optical_dpi không nhận bool (True), float, NaN, Inf, và số nguyên cực lớn (Overflow)
    for bad_dpi in [True, False, float("nan"), float("inf"), -float("inf"), "600", 149, 10**1000]:
        rec = dict(base_record)
        rec["optical_dpi"] = bad_dpi
        is_valid, errors = validate_manifest_record(rec)
        assert is_valid is False
        assert any("optical_dpi" in err for err in errors)

    # 2. is_spare không nhận int (1/0) hay string
    for bad_spare in [1, 0, "true", None]:
        rec = dict(base_record)
        rec["is_spare"] = bad_spare
        is_valid, errors = validate_manifest_record(rec)
        assert is_valid is False
        assert any("is_spare" in err for err in errors)

    # 3. calibration_metrics chứa bool, NaN, Inf, OverflowError (10**1000)
    for field_name in ["ruler_length_mm", "ruler_error_mm", "square_aspect_ratio", "deskew_angle_deg"]:
        for bad_val in [True, False, float("nan"), float("inf"), -float("inf"), "0.0", 10**1000, -10**1000]:
            rec = dict(base_record)
            rec["calibration_metrics"] = dict(base_record["calibration_metrics"])
            rec["calibration_metrics"][field_name] = bad_val
            is_valid, errors = validate_manifest_record(rec)
            assert is_valid is False
            assert any(field_name in err for err in errors)

    # 4. calibration_metrics không phải dict
    for bad_calib in [None, [50.0, 0.0, 1.0, 0.0], "calibration_data"]:
        rec = dict(base_record)
        rec["calibration_metrics"] = bad_calib
        is_valid, errors = validate_manifest_record(rec)
        assert is_valid is False
        assert any("calibration_metrics" in err for err in errors)


def test_validate_manifest_record_cell_anomalies_fail_closed():
    """Kiểm tra fail-closed cho cell_anomalies với kiểu sai và unhashable status."""
    base_record = {
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
        "qc_status": "QC_AUTO_PASS",
        "qc_operator": "TV1",
    }

    # 1. cell_anomalies không phải list
    rec = dict(base_record)
    rec["cell_anomalies"] = "not_a_list"
    is_valid, errors = validate_manifest_record(rec)
    assert is_valid is False
    assert any("cell_anomalies" in err for err in errors)

    # 2. item không phải dict
    rec = dict(base_record)
    rec["cell_anomalies"] = [123, "not_dict"]
    is_valid, errors = validate_manifest_record(rec)
    assert is_valid is False
    assert any("cell_anomalies[0]" in err for err in errors)

    # 3. status là list (unhashable)
    rec = dict(base_record)
    rec["cell_anomalies"] = [{"cell_id": "TONE_01", "status": ["USER_MISWRITTEN"]}]
    is_valid, errors = validate_manifest_record(rec)
    assert is_valid is False
    assert any("cell_anomalies[0].status" in err for err in errors)


def test_validate_ca_vhc_annotation_fail_closed_comprehensive():
    """Kiểm tra fail-closed toàn diện cho CA-VHC annotation: non-dict, ISO 8601, NaN/Inf, boolean."""
    # 1. Non-dict input
    for bad_input in [None, "string", [1, 2, 3], 42]:
        is_valid, errors = validate_ca_vhc_annotation(bad_input)
        assert is_valid is False
        assert any("dictionary" in err for err in errors)

    base_annotation = {
        "sample_id": "SMP_W001_00421",
        "writer_id": "W001",
        "source_image_id": "W001_S01_P01.png",
        "char_raw": "ế",
        "unicode_nfd": "e\u0302\u0301",
        "base_char": "e",
        "diacritics": [
            {
                "type": "circumflex",
                "unicode_codepoint": "U+0302",
                "bounding_box": [120.0, 45.0, 160.0, 75.0],
            }
        ],
        "tone_mark": "acute",
        "context_info": {
            "position": "word_medial",
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
        },
    }

    # 2. timestamp ISO 8601 không hợp lệ (kể cả thiếu múi giờ theo format: date-time)
    for bad_ts in ["not_iso", "2026-02-30T10:00:00Z", "2026-09-25T10:00:00", 12345]:
        ann = dict(base_annotation)
        ann["timestamp"] = bad_ts
        is_valid, errors = validate_ca_vhc_annotation(ann)
        assert is_valid is False
        assert any("timestamp" in err for err in errors)

    # 3. diacritics[0].type là list (unhashable)
    ann = dict(base_annotation)
    ann["diacritics"] = [{"type": ["circumflex"], "unicode_codepoint": "U+0302"}]
    is_valid, errors = validate_ca_vhc_annotation(ann)
    assert is_valid is False
    assert any("diacritics[0].type" in err for err in errors)

    # 4. diacritics[0].bounding_box chứa bool, NaN, Inf, OverflowError (10**1000)
    for bad_coord in [True, float("nan"), float("inf"), 10**1000]:
        ann = dict(base_annotation)
        ann["diacritics"] = [
            {
                "type": "circumflex",
                "unicode_codepoint": "U+0302",
                "bounding_box": [120.0, bad_coord, 160.0, 75.0],
            }
        ]
        is_valid, errors = validate_ca_vhc_annotation(ann)
        assert is_valid is False
        assert any("bounding_box" in err for err in errors)

    # 5. geometry bounding_box chứa bool, NaN, Inf, OverflowError (10**1000)
    for bad_coord in [True, float("nan"), float("inf"), 10**1000]:
        ann = dict(base_annotation)
        ann["geometry"] = dict(base_annotation["geometry"])
        ann["geometry"]["bounding_box"] = [100.0, 20.0, bad_coord, 150.0]
        is_valid, errors = validate_ca_vhc_annotation(ann)
        assert is_valid is False
        assert any("bounding_box" in err for err in errors)

    # 6. geometry baseline_y, base_anchor, diacritic_offset chứa NaN/Inf/bool/Overflow
    for f_name, bad_val in [
        ("baseline_y", True),
        ("baseline_y", float("nan")),
        ("baseline_y", 10**1000),
        ("base_anchor", [True, 50.0]),
        ("base_anchor", [140.0, float("inf")]),
        ("base_anchor", [10**1000, 50.0]),
        ("diacritic_offset", [float("nan"), 0.0]),
        ("diacritic_offset", [10**1000, -0.20]),
        ("clearance_box", [95.0, 15.0, True, 155.0]),
        ("clearance_box", [95.0, 15.0, 10**1000, 155.0]),
    ]:
        ann = dict(base_annotation)
        ann["geometry"] = dict(base_annotation["geometry"])
        ann["geometry"][f_name] = bad_val
        is_valid, errors = validate_ca_vhc_annotation(ann)
        assert is_valid is False
        assert any(f_name in err for err in errors)

    # 7. quality_flags legibility_score là bool (True), NaN, float, Overflow (10**1000)
    for bad_score in [True, False, float("nan"), 3.5, 0, 6, 10**1000]:
        ann = dict(base_annotation)
        ann["quality_flags"] = dict(base_annotation["quality_flags"])
        ann["quality_flags"]["legibility_score"] = bad_score
        is_valid, errors = validate_ca_vhc_annotation(ann)
        assert is_valid is False
        assert any("legibility_score" in err for err in errors)

    # 8. quality_flags is_degenerate / is_ambiguous là int (1/0), str
    for flag_name in ["is_degenerate", "is_ambiguous"]:
        for bad_bool in [1, 0, "True", None]:
            ann = dict(base_annotation)
            ann["quality_flags"] = dict(base_annotation["quality_flags"])
            ann["quality_flags"][flag_name] = bad_bool
            is_valid, errors = validate_ca_vhc_annotation(ann)
            assert is_valid is False
            assert any(flag_name in err for err in errors)


def test_schema_validator_overflow_and_rfc3339_regression():
    """
    Regression test chuyên sâu theo review TV4:
    1. _is_valid_float(10**1000) và _is_valid_int(10**1000) trả về False thay vì ném OverflowError.
    2. _is_valid_iso8601() bắt buộc có múi giờ (Z hoặc offset +/-HH:MM), từ chối chuỗi thiếu múi giờ.
    3. Toàn bộ trường số của manifest và annotation trả về validation error thay vì crash validator.
    """
    from backend.scan_validator.schema_validator import (
        _is_valid_float,
        _is_valid_int,
        _is_valid_iso8601,
    )

    # 1. Trực tiếp kiểm thử các helper functions
    assert _is_valid_float(10**1000) is False
    assert _is_valid_float(-10**1000) is False
    assert _is_valid_int(10**1000) is False
    assert _is_valid_int(-10**1000) is False

    assert _is_valid_iso8601("2026-09-25T10:00:00") is False  # Thiếu timezone
    assert _is_valid_iso8601("2026-09-25 10:00:00") is False  # Thiếu timezone
    assert _is_valid_iso8601("2026-09-25T10:00:00Z") is True
    assert _is_valid_iso8601("2026-09-25T10:00:00+07:00") is True
    assert _is_valid_iso8601("2026-09-25T10:00:00-05:00") is True

    # 2. Manifest record với ruler_length_mm = 10**1000 không crash mà trả lỗi hợp lệ
    manifest_rec = {
        "scan_id": "W001_S01_P01",
        "writer_id": "W001",
        "session_id": "S01",
        "page_id": "P01",
        "is_spare": False,
        "scan_timestamp": "2026-09-25T10:00:00Z",
        "scanner_model": "Epson Perfection V39 II",
        "optical_dpi": 600,
        "calibration_metrics": {
            "ruler_length_mm": 10**1000,
            "ruler_error_mm": 0.0,
            "square_aspect_ratio": 1.0,
            "deskew_angle_deg": 0.0,
        },
        "qc_status": "QC_AUTO_PASS",
        "qc_operator": "TV1",
    }
    is_valid, errors = validate_manifest_record(manifest_rec)
    assert is_valid is False
    assert any("ruler_length_mm" in err for err in errors)

    # 3. Annotation với baseline_y = 10**1000 không crash mà trả lỗi hợp lệ
    annotation_rec = {
        "sample_id": "SMP_W001_00421",
        "writer_id": "W001",
        "source_image_id": "W001_S01_P01.png",
        "char_raw": "ế",
        "unicode_nfd": "e\u0302\u0301",
        "base_char": "e",
        "diacritics": [],
        "context_info": {"position": "isolated"},
        "geometry": {
            "bounding_box": [100.0, 20.0, 180.0, 150.0],
            "baseline_y": 10**1000,
            "base_anchor": [140.0, 50.0],
            "diacritic_offset": [0.0, 0.0],
        },
        "quality_flags": {
            "legibility_score": 5,
            "is_degenerate": False,
            "is_ambiguous": False,
        },
    }
    is_valid, errors = validate_ca_vhc_annotation(annotation_rec)
    assert is_valid is False
    assert any("baseline_y" in err for err in errors)
