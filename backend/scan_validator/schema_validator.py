"""
OmniDraw Dataset Schema Validator (TV1 — AI Data & Writer Profile Lead).

Triển khai các bộ thẩm định quy tắc (rule-based validators) thuần túy theo chuẩn:
1. dataset/schemas/collection_manifest.schema.json (Doc 21 Section 6.2)
2. dataset/schemas/ca_vhc_annotation.schema.json (Doc 08 Section 7.2)

Tuân thủ nghiêm ngặt nguyên tắc Ponytail:
- Hoàn toàn độc lập, không thêm phụ thuộc ngoài (không cần jsonschema library).
- Validate chi tiết các trường bắt buộc, kiểu dữ liệu, miền giá trị và enum.
- Báo cáo lỗi tường minh, phục vụ trực tiếp cho Scan Validation Pipeline và Data Governance.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Thư mục gốc chứa schemas
_SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "dataset" / "schemas"

# Regex cơ bản cho ISO 8601 date-time
_ISO8601_REGEX = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$"
)

# Enums định chuẩn
VALID_PAGE_IDS = {"P01", "P02", "P03", "P04"}
VALID_QC_STATUSES = {
    "QC_RAW",
    "QC_AUTO_PASS",
    "QC_AUTO_FLAGGED",
    "QC_VERIFIED_PASS",
    "QC_REJECTED",
}
VALID_ANOMALY_STATUSES = {
    "USER_MISWRITTEN",
    "BOUNDARY_OVERFLOW",
    "INK_STAIN_SMUDGE",
    "CORRECTION_VIOLATION",
    "OTHER_ANOMALY",
}

VALID_DIACRITIC_TYPES = {
    "circumflex",
    "breve",
    "horn",
    "acute",
    "grave",
    "hook_above",
    "tilde",
    "dot_below",
}
VALID_TONE_MARKS = {"none", "acute", "grave", "hook_above", "tilde", "dot_below"}
VALID_POSITIONS = {"isolated", "word_initial", "word_medial", "word_final"}


def load_schema(schema_filename: str) -> Dict[str, Any]:
    """Tải nội dung định nghĩa JSON Schema từ dataset/schemas/."""
    schema_path = _SCHEMAS_DIR / schema_filename
    if not schema_path.exists():
        raise FileNotFoundError(f"Không tìm thấy schema: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 1. Thẩm định Bản ghi Collection Manifest (Doc 21 Section 6.2)
# =============================================================================

def validate_manifest_record(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Thẩm định tính hợp lệ của một bản ghi nhật ký thu thập (collection manifest record).
    Khớp 100% với dataset/schemas/collection_manifest.schema.json.
    """
    errors: List[str] = []

    required_fields = [
        "scan_id",
        "writer_id",
        "session_id",
        "page_id",
        "is_spare",
        "scan_timestamp",
        "scanner_model",
        "optical_dpi",
        "calibration_metrics",
        "qc_status",
        "qc_operator",
    ]
    for field in required_fields:
        if field not in record:
            errors.append(f"Thiếu trường bắt buộc cấp gốc: '{field}'")

    if errors:
        return False, errors

    # 1. Định danh & thông số cơ bản
    if not isinstance(record["scan_id"], str) or not record["scan_id"].strip():
        errors.append("Trường 'scan_id' phải là chuỗi không rỗng")

    if not isinstance(record["writer_id"], str) or not record["writer_id"].strip():
        errors.append("Trường 'writer_id' phải là chuỗi không rỗng")

    if not isinstance(record["session_id"], str) or not record["session_id"].strip():
        errors.append("Trường 'session_id' phải là chuỗi không rỗng")

    if record["page_id"] not in VALID_PAGE_IDS:
        errors.append(f"Trường 'page_id' phải thuộc {sorted(VALID_PAGE_IDS)}, nhận: {record['page_id']}")

    if not isinstance(record["is_spare"], bool):
        errors.append("Trường 'is_spare' phải là boolean (True/False)")

    if not isinstance(record["scan_timestamp"], str) or not _ISO8601_REGEX.match(record["scan_timestamp"]):
        errors.append(f"Trường 'scan_timestamp' phải là định dạng date-time ISO 8601, nhận: {record.get('scan_timestamp')}")

    if not isinstance(record["scanner_model"], str) or not record["scanner_model"].strip():
        errors.append("Trường 'scanner_model' phải là chuỗi không rỗng")

    if not isinstance(record["optical_dpi"], int) or record["optical_dpi"] < 150:
        errors.append(f"Trường 'optical_dpi' phải là số nguyên >= 150, nhận: {record['optical_dpi']}")

    # 2. Calibration metrics
    calib = record.get("calibration_metrics")
    if not isinstance(calib, dict):
        errors.append("Trường 'calibration_metrics' phải là một object")
    else:
        calib_req = ["ruler_length_mm", "ruler_error_mm", "square_aspect_ratio", "deskew_angle_deg"]
        for cf in calib_req:
            if cf not in calib:
                errors.append(f"Thiếu trường 'calibration_metrics.{cf}'")

        if "ruler_length_mm" in calib:
            val = calib["ruler_length_mm"]
            if not isinstance(val, (int, float)) or val < 0.0:
                errors.append(f"'calibration_metrics.ruler_length_mm' phải là số >= 0.0, nhận: {val}")

        if "ruler_error_mm" in calib:
            if not isinstance(calib["ruler_error_mm"], (int, float)):
                errors.append(f"'calibration_metrics.ruler_error_mm' phải là số, nhận: {calib['ruler_error_mm']}")

        if "square_aspect_ratio" in calib:
            val = calib["square_aspect_ratio"]
            if not isinstance(val, (int, float)) or not (0.5 <= val <= 1.5):
                errors.append(f"'calibration_metrics.square_aspect_ratio' phải thuộc [0.5, 1.5], nhận: {val}")

        if "deskew_angle_deg" in calib:
            if not isinstance(calib["deskew_angle_deg"], (int, float)):
                errors.append(f"'calibration_metrics.deskew_angle_deg' phải là số, nhận: {calib['deskew_angle_deg']}")

    # 3. QC status & operator
    if record["qc_status"] not in VALID_QC_STATUSES:
        errors.append(f"Trường 'qc_status' phải thuộc {sorted(VALID_QC_STATUSES)}, nhận: {record['qc_status']}")

    if not isinstance(record["qc_operator"], str) or not record["qc_operator"].strip():
        errors.append("Trường 'qc_operator' phải là chuỗi không rỗng")

    # 4. Cell anomalies (tùy chọn)
    if "cell_anomalies" in record:
        anomalies = record["cell_anomalies"]
        if not isinstance(anomalies, list):
            errors.append("Trường 'cell_anomalies' phải là mảng danh sách")
        else:
            for i, a in enumerate(anomalies):
                if not isinstance(a, dict):
                    errors.append(f"'cell_anomalies[{i}]' phải là object")
                    continue
                if "cell_id" not in a or not isinstance(a["cell_id"], str) or not a["cell_id"].strip():
                    errors.append(f"'cell_anomalies[{i}].cell_id' phải là chuỗi không rỗng")
                if "status" not in a or a["status"] not in VALID_ANOMALY_STATUSES:
                    errors.append(f"'cell_anomalies[{i}].status' phải thuộc {sorted(VALID_ANOMALY_STATUSES)}, nhận: {a.get('status')}")

    return len(errors) == 0, errors


# =============================================================================
# 2. Thẩm định Bản ghi CA-VHC Annotation (Doc 08 Section 7.2)
# =============================================================================

def validate_ca_vhc_annotation(annotation: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Thẩm định tính hợp lệ của bản ghi gán nhãn ký tự và mỏ neo dấu CA-VHC.
    Khớp 100% với dataset/schemas/ca_vhc_annotation.schema.json.
    """
    errors: List[str] = []

    required_fields = [
        "sample_id",
        "writer_id",
        "source_image_id",
        "char_raw",
        "unicode_nfd",
        "base_char",
        "diacritics",
        "context_info",
        "geometry",
        "quality_flags",
    ]
    for field in required_fields:
        if field not in annotation:
            errors.append(f"Thiếu trường bắt buộc cấp gốc: '{field}'")

    if errors:
        return False, errors

    # 1. Định danh & thông tin văn bản
    for str_f in ["sample_id", "writer_id", "source_image_id", "char_raw", "unicode_nfd", "base_char"]:
        if not isinstance(annotation[str_f], str) or not annotation[str_f].strip():
            errors.append(f"Trường '{str_f}' phải là chuỗi không rỗng")

    if "timestamp" in annotation:
        ts = annotation["timestamp"]
        if not isinstance(ts, str) or not _ISO8601_REGEX.match(ts):
            errors.append(f"Trường 'timestamp' phải là định dạng date-time ISO 8601, nhận: {ts}")

    # 2. Diacritics array
    if not isinstance(annotation["diacritics"], list):
        errors.append("Trường 'diacritics' phải là danh sách mảng")
    else:
        for i, d in enumerate(annotation["diacritics"]):
            if not isinstance(d, dict):
                errors.append(f"'diacritics[{i}]' phải là object")
                continue
            if "type" not in d or d["type"] not in VALID_DIACRITIC_TYPES:
                errors.append(f"'diacritics[{i}].type' phải thuộc {sorted(VALID_DIACRITIC_TYPES)}, nhận: {d.get('type')}")
            if "unicode_codepoint" not in d or not isinstance(d["unicode_codepoint"], str):
                errors.append(f"'diacritics[{i}].unicode_codepoint' phải là chuỗi mã code")
            if "bounding_box" in d:
                bbox = d["bounding_box"]
                if not isinstance(bbox, (list, tuple)) or len(bbox) != 4 or not all(isinstance(x, (int, float)) for x in bbox):
                    errors.append(f"'diacritics[{i}].bounding_box' phải là mảng 4 số [xmin, ymin, xmax, ymax]")

    # 3. Tone mark
    if "tone_mark" in annotation and annotation["tone_mark"] not in VALID_TONE_MARKS:
        errors.append(f"Trường 'tone_mark' phải thuộc {sorted(VALID_TONE_MARKS)}, nhận: {annotation['tone_mark']}")

    # 4. Context info
    ctx = annotation.get("context_info")
    if not isinstance(ctx, dict):
        errors.append("Trường 'context_info' phải là object")
    else:
        if "position" not in ctx or ctx["position"] not in VALID_POSITIONS:
            errors.append(f"'context_info.position' phải thuộc {sorted(VALID_POSITIONS)}, nhận: {ctx.get('position')}")

    # 5. Geometry
    geom = annotation.get("geometry")
    if not isinstance(geom, dict):
        errors.append("Trường 'geometry' phải là object")
    else:
        geom_req = ["bounding_box", "baseline_y", "base_anchor", "diacritic_offset"]
        for gf in geom_req:
            if gf not in geom:
                errors.append(f"Thiếu trường 'geometry.{gf}'")

        if "bounding_box" in geom:
            bbox = geom["bounding_box"]
            if not isinstance(bbox, (list, tuple)) or len(bbox) != 4 or not all(isinstance(x, (int, float)) for x in bbox):
                errors.append("'geometry.bounding_box' phải là mảng 4 số [xmin, ymin, xmax, ymax]")

        if "baseline_y" in geom and not isinstance(geom["baseline_y"], (int, float)):
            errors.append("'geometry.baseline_y' phải là số (pixel)")

        if "base_anchor" in geom:
            ba = geom["base_anchor"]
            if not isinstance(ba, (list, tuple)) or len(ba) != 2 or not all(isinstance(x, (int, float)) for x in ba):
                errors.append("'geometry.base_anchor' phải là mảng 2 số [x, y] (mm)")

        if "diacritic_offset" in geom:
            do = geom["diacritic_offset"]
            if not isinstance(do, (list, tuple)) or len(do) != 2 or not all(isinstance(x, (int, float)) for x in do):
                errors.append("'geometry.diacritic_offset' phải là mảng 2 số [dx, dy] (mm)")

        if "diacritic_anchor" in geom:
            da = geom["diacritic_anchor"]
            if not isinstance(da, (list, tuple)) or len(da) != 2 or not all(isinstance(x, (int, float)) for x in da):
                errors.append("'geometry.diacritic_anchor' phải là mảng 2 số [x, y] (mm)")

        if "clearance_box" in geom:
            cb = geom["clearance_box"]
            if not isinstance(cb, (list, tuple)) or len(cb) != 4 or not all(isinstance(x, (int, float)) for x in cb):
                errors.append("'geometry.clearance_box' phải là mảng 4 số [xmin, ymin, xmax, ymax]")

    # 6. Quality flags
    qf = annotation.get("quality_flags")
    if not isinstance(qf, dict):
        errors.append("Trường 'quality_flags' phải là object")
    else:
        for qff in ["legibility_score", "is_degenerate", "is_ambiguous"]:
            if qff not in qf:
                errors.append(f"Thiếu trường 'quality_flags.{qff}'")

        if "legibility_score" in qf:
            ls = qf["legibility_score"]
            if not isinstance(ls, int) or not (1 <= ls <= 5):
                errors.append(f"'quality_flags.legibility_score' phải là số nguyên thuộc [1, 5], nhận: {ls}")

        if "is_degenerate" in qf and not isinstance(qf["is_degenerate"], bool):
            errors.append("'quality_flags.is_degenerate' phải là boolean")

        if "is_ambiguous" in qf and not isinstance(qf["is_ambiguous"], bool):
            errors.append("'quality_flags.is_ambiguous' phải là boolean")

    return len(errors) == 0, errors
