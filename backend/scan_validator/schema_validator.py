"""
OmniDraw Dataset Schema Validator (TV1 — AI Data & Writer Profile Lead).

Triển khai các bộ thẩm định quy tắc (rule-based validators) thuần túy theo chuẩn:
1. dataset/schemas/collection_manifest.schema.json (Doc 21 Section 6.2)
2. dataset/schemas/ca_vhc_annotation.schema.json (Doc 08 Section 7.2)

Tuân thủ nghiêm ngặt nguyên tắc Ponytail & Kỷ luật Fail-Closed:
- Hoàn toàn độc lập, không thêm phụ thuộc ngoài (không cần jsonschema library).
- Kiểm tra chặt chẽ kiểu dữ liệu, chặn triệt để TypeError khi input sai kiểu (ví dụ page_id là list).
- Kiểm tra tính hợp lệ của date-time ISO 8601 bằng cả regex và parser datetime.
- Chặn boolean ở các trường số (Python coi bool là subclass của int).
- Chặn số thực không hợp lệ (NaN, +Inf, -Inf).
- Báo cáo lỗi tường minh, phục vụ trực tiếp cho Scan Validation Pipeline và Data Governance.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Thư mục gốc chứa schemas
_SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "dataset" / "schemas"

# Regex cho RFC 3339 / ISO 8601 date-time bắt buộc có múi giờ (Z hoặc offset +/-HH:MM) theo JSON Schema format: date-time
_ISO8601_REGEX = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$",
    re.IGNORECASE,
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


def _safe_repr(val: Any, max_len: int = 60) -> str:
    """Biểu diễn an toàn giá trị để đưa vào thông báo lỗi, tránh crash vì độ dài hoặc kiểu."""
    try:
        s = repr(val)
        if len(s) > max_len:
            return s[:max_len] + "... (truncated)"
        return s
    except Exception:
        return f"<{type(val).__name__}>"


def _is_valid_int(val: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool:
    """Kiểm tra số nguyên hợp lệ, loại trừ bool, NaN, Inf hoặc kiểu không phải int (tuân thủ 100% JSON Schema)."""
    if type(val) is bool or not isinstance(val, int):
        return False
    try:
        if min_val is not None and val < min_val:
            return False
        if max_val is not None and val > max_val:
            return False
    except (OverflowError, ValueError):
        return False
    return True


def _is_valid_float(val: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """Kiểm tra số thực/nguyên hợp lệ, loại trừ bool, NaN, Inf, và xử lý an toàn OverflowError."""
    if type(val) is bool or not isinstance(val, (int, float)):
        return False
    try:
        f_val = float(val)
        if math.isnan(f_val) or math.isinf(f_val):
            return False
    except (OverflowError, ValueError):
        return False

    try:
        if min_val is not None and val < min_val:
            return False
        if max_val is not None and val > max_val:
            return False
    except (OverflowError, ValueError):
        return False
    return True


def _is_valid_iso8601(val: Any) -> bool:
    """
    Kiểm tra chuỗi ISO 8601 / RFC 3339 date-time hợp lệ.
    Tuân thủ format: date-time của JSON Schema: bắt buộc phải có múi giờ (Z hoặc offset +/-HH:MM).
    """
    if not isinstance(val, str) or not val.strip():
        return False
    if not _ISO8601_REGEX.match(val):
        return False
    try:
        clean_ts = val[:-1] + "+00:00" if val.endswith(("Z", "z")) else val
        dt = datetime.fromisoformat(clean_ts)
        return dt.tzinfo is not None
    except (ValueError, TypeError, OverflowError):
        return False


# =============================================================================
# 1. Thẩm định Bản ghi Collection Manifest (Doc 21 Section 6.2)
# =============================================================================

def validate_manifest_record(record: Any) -> Tuple[bool, List[str]]:
    """
    Thẩm định tính hợp lệ của một bản ghi nhật ký thu thập (collection manifest record).
    Khớp 100% với dataset/schemas/collection_manifest.schema.json.
    Trả về (False, errors) khi input sai kiểu, không bao giờ ném TypeError.
    """
    errors: List[str] = []

    if not isinstance(record, dict):
        return False, [f"Bản ghi manifest phải là dictionary (object), nhận: {type(record).__name__}"]

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
    for str_f in ["scan_id", "writer_id", "session_id", "scanner_model", "qc_operator"]:
        val = record.get(str_f)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"Trường '{str_f}' phải là chuỗi không rỗng")

    page_id = record.get("page_id")
    if not isinstance(page_id, str) or page_id not in VALID_PAGE_IDS:
        errors.append(f"Trường 'page_id' phải là chuỗi thuộc {sorted(VALID_PAGE_IDS)}, nhận: {_safe_repr(page_id)}")

    is_spare = record.get("is_spare")
    if type(is_spare) is not bool:
        errors.append(f"Trường 'is_spare' phải là boolean (True/False), nhận: {_safe_repr(is_spare)}")

    scan_ts = record.get("scan_timestamp")
    if not _is_valid_iso8601(scan_ts):
        errors.append(f"Trường 'scan_timestamp' phải là định dạng date-time ISO 8601 hợp lệ, nhận: {_safe_repr(scan_ts)}")

    dpi = record.get("optical_dpi")
    if not _is_valid_int(dpi, min_val=150):
        errors.append(f"Trường 'optical_dpi' phải là số nguyên >= 150 (không nhận boolean/NaN/Inf), nhận: {_safe_repr(dpi)}")

    # 2. Calibration metrics
    calib = record.get("calibration_metrics")
    if not isinstance(calib, dict):
        errors.append(f"Trường 'calibration_metrics' phải là một object (dict), nhận: {_safe_repr(calib)}")
    else:
        calib_req = ["ruler_length_mm", "ruler_error_mm", "square_aspect_ratio", "deskew_angle_deg"]
        for cf in calib_req:
            if cf not in calib:
                errors.append(f"Thiếu trường 'calibration_metrics.{cf}'")

        if "ruler_length_mm" in calib:
            val = calib["ruler_length_mm"]
            if not _is_valid_float(val, min_val=0.0):
                errors.append(f"'calibration_metrics.ruler_length_mm' phải là số thực hữu hạn >= 0.0, nhận: {_safe_repr(val)}")

        if "ruler_error_mm" in calib:
            val = calib["ruler_error_mm"]
            if not _is_valid_float(val):
                errors.append(f"'calibration_metrics.ruler_error_mm' phải là số thực hữu hạn, nhận: {_safe_repr(val)}")

        if "square_aspect_ratio" in calib:
            val = calib["square_aspect_ratio"]
            if not _is_valid_float(val, min_val=0.5, max_val=1.5):
                errors.append(f"'calibration_metrics.square_aspect_ratio' phải là số thực hữu hạn thuộc [0.5, 1.5], nhận: {_safe_repr(val)}")

        if "deskew_angle_deg" in calib:
            val = calib["deskew_angle_deg"]
            if not _is_valid_float(val):
                errors.append(f"'calibration_metrics.deskew_angle_deg' phải là số thực hữu hạn, nhận: {_safe_repr(val)}")

    # 3. QC status & operator
    qc_status = record.get("qc_status")
    if not isinstance(qc_status, str) or qc_status not in VALID_QC_STATUSES:
        errors.append(f"Trường 'qc_status' phải là chuỗi thuộc {sorted(VALID_QC_STATUSES)}, nhận: {_safe_repr(qc_status)}")

    # 4. Cell anomalies (tùy chọn)
    if "cell_anomalies" in record:
        anomalies = record["cell_anomalies"]
        if not isinstance(anomalies, list):
            errors.append(f"Trường 'cell_anomalies' phải là mảng danh sách (list), nhận: {_safe_repr(anomalies)}")
        else:
            for i, a in enumerate(anomalies):
                if not isinstance(a, dict):
                    errors.append(f"'cell_anomalies[{i}]' phải là object (dict), nhận: {_safe_repr(a)}")
                    continue
                cell_id = a.get("cell_id")
                if not isinstance(cell_id, str) or not cell_id.strip():
                    errors.append(f"'cell_anomalies[{i}].cell_id' phải là chuỗi không rỗng")
                st = a.get("status")
                if not isinstance(st, str) or st not in VALID_ANOMALY_STATUSES:
                    errors.append(f"'cell_anomalies[{i}].status' phải là chuỗi thuộc {sorted(VALID_ANOMALY_STATUSES)}, nhận: {_safe_repr(st)}")
                if "note" in a and not isinstance(a["note"], str):
                    errors.append(f"'cell_anomalies[{i}].note' phải là chuỗi nếu có")

    return len(errors) == 0, errors


# =============================================================================
# 2. Thẩm định Bản ghi CA-VHC Annotation (Doc 08 Section 7.2)
# =============================================================================

def validate_ca_vhc_annotation(annotation: Any) -> Tuple[bool, List[str]]:
    """
    Thẩm định tính hợp lệ của bản ghi gán nhãn ký tự và mỏ neo dấu CA-VHC.
    Khớp 100% với dataset/schemas/ca_vhc_annotation.schema.json.
    Trả về (False, errors) khi input sai kiểu, không bao giờ ném TypeError.
    """
    errors: List[str] = []

    if not isinstance(annotation, dict):
        return False, [f"Bản ghi annotation phải là dictionary (object), nhận: {type(annotation).__name__}"]

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
        val = annotation.get(str_f)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"Trường '{str_f}' phải là chuỗi không rỗng")

    if "timestamp" in annotation:
        ts = annotation["timestamp"]
        if not _is_valid_iso8601(ts):
            errors.append(f"Trường 'timestamp' phải là định dạng date-time ISO 8601 hợp lệ, nhận: {_safe_repr(ts)}")

    # 2. Diacritics array
    diacs = annotation.get("diacritics")
    if not isinstance(diacs, list):
        errors.append(f"Trường 'diacritics' phải là danh sách mảng (list), nhận: {_safe_repr(diacs)}")
    else:
        for i, d in enumerate(diacs):
            if not isinstance(d, dict):
                errors.append(f"'diacritics[{i}]' phải là object (dict), nhận: {_safe_repr(d)}")
                continue
            dtype = d.get("type")
            if not isinstance(dtype, str) or dtype not in VALID_DIACRITIC_TYPES:
                errors.append(f"'diacritics[{i}].type' phải là chuỗi thuộc {sorted(VALID_DIACRITIC_TYPES)}, nhận: {_safe_repr(dtype)}")
            cp = d.get("unicode_codepoint")
            if not isinstance(cp, str) or not cp.strip():
                errors.append(f"'diacritics[{i}].unicode_codepoint' phải là chuỗi mã code không rỗng")
            if "bounding_box" in d:
                bbox = d["bounding_box"]
                if not isinstance(bbox, (list, tuple)) or len(bbox) != 4 or not all(_is_valid_float(x) for x in bbox):
                    errors.append(f"'diacritics[{i}].bounding_box' phải là mảng 4 số thực hữu hạn [xmin, ymin, xmax, ymax]")

    # 3. Tone mark
    if "tone_mark" in annotation:
        tm = annotation["tone_mark"]
        if not isinstance(tm, str) or tm not in VALID_TONE_MARKS:
            errors.append(f"Trường 'tone_mark' phải là chuỗi thuộc {sorted(VALID_TONE_MARKS)}, nhận: {_safe_repr(tm)}")

    # 4. Context info
    ctx = annotation.get("context_info")
    if not isinstance(ctx, dict):
        errors.append(f"Trường 'context_info' phải là object (dict), nhận: {_safe_repr(ctx)}")
    else:
        pos = ctx.get("position")
        if not isinstance(pos, str) or pos not in VALID_POSITIONS:
            errors.append(f"'context_info.position' phải là chuỗi thuộc {sorted(VALID_POSITIONS)}, nhận: {_safe_repr(pos)}")
        if "prev_char" in ctx and ctx["prev_char"] is not None and not isinstance(ctx["prev_char"], str):
            errors.append("'context_info.prev_char' phải là chuỗi hoặc null")
        if "next_char" in ctx and ctx["next_char"] is not None and not isinstance(ctx["next_char"], str):
            errors.append("'context_info.next_char' phải là chuỗi hoặc null")
        if "syllable_text" in ctx and ctx["syllable_text"] is not None and not isinstance(ctx["syllable_text"], str):
            errors.append("'context_info.syllable_text' phải là chuỗi hoặc null")
        if "letter_type" in ctx and not isinstance(ctx["letter_type"], str):
            errors.append("'context_info.letter_type' phải là chuỗi")

    # 5. Geometry
    geom = annotation.get("geometry")
    if not isinstance(geom, dict):
        errors.append(f"Trường 'geometry' phải là object (dict), nhận: {_safe_repr(geom)}")
    else:
        geom_req = ["bounding_box", "baseline_y", "base_anchor", "diacritic_offset"]
        for gf in geom_req:
            if gf not in geom:
                errors.append(f"Thiếu trường 'geometry.{gf}'")

        if "bounding_box" in geom:
            bbox = geom["bounding_box"]
            if not isinstance(bbox, (list, tuple)) or len(bbox) != 4 or not all(_is_valid_float(x) for x in bbox):
                errors.append("'geometry.bounding_box' phải là mảng 4 số thực hữu hạn [xmin, ymin, xmax, ymax]")

        if "baseline_y" in geom and not _is_valid_float(geom["baseline_y"]):
            errors.append("'geometry.baseline_y' phải là số thực hữu hạn (pixel)")

        if "base_anchor" in geom:
            ba = geom["base_anchor"]
            if not isinstance(ba, (list, tuple)) or len(ba) != 2 or not all(_is_valid_float(x) for x in ba):
                errors.append("'geometry.base_anchor' phải là mảng 2 số thực hữu hạn [x, y] (mm)")

        if "diacritic_anchor" in geom:
            da = geom["diacritic_anchor"]
            if not isinstance(da, (list, tuple)) or len(da) != 2 or not all(_is_valid_float(x) for x in da):
                errors.append("'geometry.diacritic_anchor' phải là mảng 2 số thực hữu hạn [x, y] (mm)")

        if "diacritic_offset" in geom:
            do = geom["diacritic_offset"]
            if not isinstance(do, (list, tuple)) or len(do) != 2 or not all(_is_valid_float(x) for x in do):
                errors.append("'geometry.diacritic_offset' phải là mảng 2 số thực hữu hạn [dx, dy] (mm)")

        if "clearance_box" in geom:
            cb = geom["clearance_box"]
            if not isinstance(cb, (list, tuple)) or len(cb) != 4 or not all(_is_valid_float(x) for x in cb):
                errors.append("'geometry.clearance_box' phải là mảng 4 số thực hữu hạn [xmin, ymin, xmax, ymax]")

    # 6. Quality flags
    qf = annotation.get("quality_flags")
    if not isinstance(qf, dict):
        errors.append(f"Trường 'quality_flags' phải là object (dict), nhận: {_safe_repr(qf)}")
    else:
        for qff in ["legibility_score", "is_degenerate", "is_ambiguous"]:
            if qff not in qf:
                errors.append(f"Thiếu trường 'quality_flags.{qff}'")

        if "legibility_score" in qf:
            ls = qf["legibility_score"]
            if not _is_valid_int(ls, min_val=1, max_val=5):
                errors.append(f"'quality_flags.legibility_score' phải là số nguyên thuộc [1, 5] (không nhận boolean/NaN/Inf), nhận: {_safe_repr(ls)}")

        if "is_degenerate" in qf and type(qf["is_degenerate"]) is not bool:
            errors.append(f"'quality_flags.is_degenerate' phải là boolean (True/False), nhận: {_safe_repr(qf['is_degenerate'])}")

        if "is_ambiguous" in qf and type(qf["is_ambiguous"]) is not bool:
            errors.append(f"'quality_flags.is_ambiguous' phải là boolean (True/False), nhận: {_safe_repr(qf['is_ambiguous'])}")

        if "annotator_id" in qf and (not isinstance(qf["annotator_id"], str) or not qf["annotator_id"].strip()):
            errors.append("'quality_flags.annotator_id' phải là chuỗi không rỗng nếu có")

    return len(errors) == 0, errors
