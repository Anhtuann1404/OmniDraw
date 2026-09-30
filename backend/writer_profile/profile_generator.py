"""
OmniDraw Writer Profile Generator — Pipeline Bridge (TV1 — AI Data Lead).

Kết nối kết quả đầu ra của Scan-Validation Pipeline (ảnh crop, bounding box, nhãn QC)
sang đối tượng hồ sơ phong cách cá nhân hóa WriterProfile theo chuẩn P2:
1. Chuyển đổi ảnh crop viết tay thành mảng nét polyline (mm).
2. Phân nhóm ký tự, từ và điểm tiếp xúc chân dòng (baseline).
3. Đóng gói đối tượng WriterProfile và kiểm định với JSON Schema.
4. Lưu trữ file JSON hồ sơ và cập nhật bảng tổng hợp writer_features_summary.jsonl.

Tuân thủ triết lý Ponytail: Tối giản, toán học hình thức, dùng OpenCV/NumPy có sẵn.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import cv2
import numpy as np

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.writer_profile.extractor import (
    WriterProfile,
    WriterProfileExtractor,
    validate_writer_profile,
)

MM_PER_INCH = 25.4


def px_to_mm(pixels: float, dpi: int = 600) -> float:
    """Chuyển đổi từ pixel sang milimet theo DPI định chuẩn."""
    return float(pixels) * MM_PER_INCH / float(dpi)


def mm_to_px(mm: float, dpi: int = 600) -> int:
    """Chuyển đổi từ milimet sang pixel theo DPI định chuẩn."""
    return int(round(float(mm) * float(dpi) / MM_PER_INCH))


def extract_strokes_from_image(
    crop_image: np.ndarray,
    dpi: int = 600,
    min_perimeter_px: float = 6.0,
    poly_approx_epsilon_mm: float = 0.15,
) -> List[np.ndarray]:
    """
    Trích xuất danh sách các nét viết (strokes) từ ảnh crop viết tay.

    Args:
        crop_image: Mảng numpy ảnh BGR hoặc Grayscale của ô viết tay.
        dpi: Độ phân giải quang học (mặc định 600 DPI).
        min_perimeter_px: Ngưỡng chu vi tối thiểu để lọc nhiễu hạt mực (pixel).
        poly_approx_epsilon_mm: Ngưỡng xấp xỉ đa tuyến (mm) để làm mịn nét.

    Returns:
        Danh sách mảng (N, 2) tọa độ nét viết tính theo milimet.
    """
    if crop_image is None or crop_image.size == 0:
        return []

    if len(crop_image.shape) == 3:
        gray = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = crop_image.copy()

    # Nhị phân hóa Otsu nghịch đảo (mực nét viết thành màu trắng 255, nền giấy là 0)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Lọc nhiễu nhẹ
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # Tìm đường bao nét với toàn bộ điểm biên để tránh mất góc
    contours, _ = cv2.findContours(cleaned, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    strokes: List[np.ndarray] = []
    scale = MM_PER_INCH / float(dpi)
    epsilon_px = max(1.0, poly_approx_epsilon_mm / scale)

    for cnt in contours:
        if cv2.arcLength(cnt, True) < min_perimeter_px:
            continue

        # Đơn giản hóa đường bao thành polyline
        approx = cv2.approxPolyDP(cnt, epsilon=epsilon_px, closed=False)
        pts = approx.reshape(-1, 2).astype(float)
        if len(pts) >= 2:
            # Chuyển đổi sang milimet
            pts_mm = pts * scale
            strokes.append(pts_mm)

    return strokes


def extract_char_boxes_from_image(
    crop_image: np.ndarray,
    dpi: int = 600,
    min_area_px: int = 25,
) -> List[Tuple[float, float, float, float]]:
    """
    Bóc tách danh sách bounding box (xmin, ymin, xmax, ymax) tính bằng mm của
    các ký tự / thành phần liên thông trong một ảnh từ viết tay.
    """
    if crop_image is None or crop_image.size == 0:
        return []

    if len(crop_image.shape) == 3:
        gray = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = crop_image.copy()

    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    boxes: List[Tuple[float, float, float, float]] = []

    scale = MM_PER_INCH / float(dpi)

    for i in range(1, num_labels):  # Bỏ qua label 0 là background
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_area_px:
            continue
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]

        x_min_mm = float(x) * scale
        y_min_mm = float(y) * scale
        x_max_mm = float(x + w) * scale
        y_max_mm = float(y + h) * scale

        boxes.append((x_min_mm, y_min_mm, x_max_mm, y_max_mm))

    # Sắp xếp các bounding box theo thứ tự từ trái sang phải
    boxes.sort(key=lambda b: b[0])
    return boxes


def generate_writer_profile_from_crops(
    writer_id: str,
    crops_data: List[Dict[str, Any]],
    dpi: int = 600,
    version: str = "1.0.0",
    default_stroke_width_mm: float = 0.5,
    used_indices: Optional[List[int]] = None,
) -> WriterProfile:
    """
    Tự động sinh hồ sơ phong cách WriterProfile từ danh sách dữ liệu ảnh crop.

    Args:
        writer_id: Mã định danh người viết (ví dụ: "W001").
        crops_data: Danh sách dict, mỗi phần tử chứa:
            - "crop_image": np.ndarray
            - "context_tag": str (tùy chọn, ví dụ: "isolated", "contextual_word", "sentence")
            - "is_valid": bool (tùy chọn, mặc định True)
        dpi: Độ phân giải ảnh crop (mặc định 600 DPI).
        version: Phiên bản thuật toán trích xuất (mặc định "1.0.0").
        default_stroke_width_mm: Bề rộng nét ngòi bút giả định (mm).
        used_indices: (Tùy chọn) Danh sách lưu chỉ mục các ô crop thực tế được trích xuất thành công.

    Returns:
        Đối tượng WriterProfile hợp lệ theo JSON Schema.
    """
    all_strokes: List[np.ndarray] = []
    char_stroke_groups: List[List[np.ndarray]] = []
    words_data: List[List[Tuple[float, float, float, float]]] = []
    baseline_points: List[Tuple[float, float]] = []

    valid_samples_count = 0

    for idx, item in enumerate(crops_data):
        if not item.get("is_valid", True):
            continue

        img = item.get("crop_image")
        if img is None or img.size == 0:
            continue

        strokes = extract_strokes_from_image(img, dpi=dpi)
        if not strokes:
            continue

        valid_samples_count += 1
        if used_indices is not None:
            used_indices.append(idx)
        all_strokes.extend(strokes)

        context = item.get("context_tag", "isolated")

        # 1. Nếu là ký tự rời (isolated), gom toàn bộ nét của ô này thành 1 ký tự
        if "isolated" in context or "char" in context:
            char_stroke_groups.append(strokes)
            # Điểm đáy của ký tự
            y_bottom = max(np.max(s[:, 1]) for s in strokes)
            x_center = float(np.mean([np.mean(s[:, 0]) for s in strokes]))
            baseline_points.append((x_center, y_bottom))

        # 2. Nếu là từ ngữ cảnh (contextual), trích xuất bounding box từng ký tự để đo khoảng cách
        elif "word" in context:
            boxes = extract_char_boxes_from_image(img, dpi=dpi)
            if boxes:
                words_data.append(boxes)
                for b in boxes:
                    baseline_points.append(((b[0] + b[2]) / 2.0, b[3]))

        # 3. Nếu là câu hoặc đoạn văn, trích xuất chuỗi ký tự theo dòng
        elif "sentence" in context or "paragraph" in context:
            boxes = extract_char_boxes_from_image(img, dpi=dpi)
            if boxes:
                words_data.append(boxes)
                for b in boxes:
                    baseline_points.append(((b[0] + b[2]) / 2.0, b[3]))

    # Sử dụng WriterProfileExtractor để tính toán các đặc trưng thống kê
    extractor = WriterProfileExtractor(
        version=version, default_stroke_width_mm=default_stroke_width_mm
    )

    profile = extractor.extract_from_samples(
        writer_id=writer_id,
        strokes=all_strokes,
        character_stroke_groups=char_stroke_groups if char_stroke_groups else None,
        words_data=words_data if words_data else None,
        baseline_points=baseline_points if baseline_points else None,
        num_samples_analyzed=max(1, valid_samples_count),
    )

    # Kiểm định tính hợp thức của profile theo schema
    is_valid, errors = validate_writer_profile(profile.to_dict())
    if not is_valid:
        raise ValueError(
            f"Sinh hồ sơ WriterProfile cho {writer_id} thất bại do vi phạm schema: {errors}"
        )

    return profile


def record_profile_crop_provenance(
    profile_id: str,
    writer_id: str,
    used_crops_metadata: List[Dict[str, Any]],
    ledger_path: Union[str, Path],
    scan_id: Optional[str] = None,
) -> Path:
    """
    Ghi nhật ký liên kết xuất xứ cấp ô cắt (crop-level provenance ledger) cho đợt pilot RQ4.

    Lưu trữ độc lập dạng JSON Lines (không làm biến dạng cấu trúc JSON của WriterProfile),
    ghi nhận bộ ba (profile_id, scan_id, cell_id/sample_id) của các ô cắt thực tế được
    sử dụng để tổng hợp đặc trưng phong cách, bảo toàn tính truy vết cho nghiên cứu.

    Args:
        profile_id: Mã định danh hồ sơ phong cách (ví dụ: 'profile_W001_v1').
        writer_id: Mã định danh người viết (ví dụ: 'W001').
        used_crops_metadata: Danh sách metadata của các ô cắt đã được nạp và phân tích.
        ledger_path: Đường dẫn tệp JSONL nhật ký xuất xứ.
        scan_id: Mã định danh phiên quét/trang nếu metadata ô chưa có.

    Returns:
        Đường dẫn tệp ledger vừa được ghi/cập nhật.

    Raises:
        ValueError: Nếu ô cắt thiếu scan_id hoặc cell_id/sample_id hợp lệ, hoặc tệp cũ bị lỗi JSON (fail-closed).
    """
    ledger_p = Path(ledger_path)
    ledger_p.parent.mkdir(parents=True, exist_ok=True)

    records: List[Dict[str, Any]] = []
    for item in used_crops_metadata:
        # Lọc nghiêm ngặt: chỉ ghi nhận ô thực sự hợp lệ cho dataset và không bị từ chối/rỗng
        if not item.get("is_valid_for_dataset", item.get("is_valid", True)):
            continue
        if item.get("qc_status") in ("QC_REJECTED", "QC_EMPTY"):
            continue

        c_scan_id = item.get("scan_id") or scan_id

        if not c_scan_id or not str(c_scan_id).strip():
            raise ValueError(
                f"Từ chối ghi nhận provenance cho profile '{profile_id}': crop thiếu 'scan_id' hợp lệ: {item}"
            )
        c_scan_id_str = str(c_scan_id).strip()
        # Fail-closed: scan_id phải là mã định danh chuẩn, không được chứa đường dẫn tệp hay đuôi file
        if any(sep in c_scan_id_str for sep in ("/", "\\")) or any(
            c_scan_id_str.lower().endswith(ext)
            for ext in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".json")
        ):
            raise ValueError(
                f"Từ chối ghi nhận provenance cho profile '{profile_id}': 'scan_id' mang định dạng đường dẫn tệp không hợp lệ: {c_scan_id_str!r}. "
                "Yêu cầu mã định danh chuẩn (ví dụ 'W001_S01_P01'), tuyệt đối không dùng đường dẫn tệp thay thế."
            )

        c_cell_id = item.get("cell_id") or item.get("sample_id")
        if not c_cell_id or not str(c_cell_id).strip():
            raise ValueError(
                f"Từ chối ghi nhận provenance cho profile '{profile_id}': crop thiếu 'cell_id' (hoặc 'sample_id') hợp lệ: {item}"
            )

        record = {
            "profile_id": profile_id,
            "writer_id": writer_id,
            "scan_id": c_scan_id_str,
            "cell_id": str(c_cell_id).strip(),
            "sample_id": item.get("sample_id"),
            "crop_file": item.get("crop_file"),
            "qc_status": item.get("qc_status", "QC_AUTO_PASS"),
            "context_tag": item.get("context_tag", "isolated"),
        }
        records.append(record)

    # Đọc ledger hiện tại để xử lý chạy lại một cách xác định (idempotent / deduplication)
    # Fail-closed: Nếu ledger cũ có dòng JSON hỏng, lập tức báo lỗi và giữ nguyên tệp cũ, không mất dữ liệu.
    existing_records: List[Dict[str, Any]] = []
    if ledger_p.exists():
        with open(ledger_p, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    row = json.loads(line_str)
                except json.JSONDecodeError as err:
                    raise ValueError(
                        f"Phát hiện dòng JSON bị lỗi cấu trúc tại dòng {line_no} trong tệp ledger '{ledger_p}': {line_str}. "
                        "Hủy bỏ thao tác ghi để bảo vệ toàn vẹn dữ liệu và giữ nguyên tệp cũ."
                    ) from err

                if not isinstance(row, dict):
                    raise ValueError(
                        f"Phát hiện dòng không phải JSON object tại dòng {line_no} trong tệp ledger '{ledger_p}': {line_str}. "
                        "Hủy bỏ thao tác ghi để bảo vệ toàn vẹn dữ liệu và giữ nguyên tệp cũ."
                    )

                # Giữ lại các bản ghi của các profile_id khác, ghi đè/thay thế bản ghi của profile_id này
                if row.get("profile_id") != profile_id:
                    existing_records.append(row)

    # Gộp danh sách bản ghi mới
    all_records = existing_records + records

    # Sắp xếp xác định (deterministic ordering) theo (profile_id, scan_id, cell_id)
    all_records.sort(
        key=lambda r: (
            str(r.get("profile_id", "")),
            str(r.get("scan_id", "")),
            str(r.get("cell_id", "")),
        )
    )

    with open(ledger_p, "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return ledger_p


def generate_writer_profile_from_report(
    report_dict: Dict[str, Any],
    writer_id: str,
    crops_base_dir: Optional[Union[str, Path]] = None,
    dpi: int = 600,
    provenance_ledger_path: Optional[Union[str, Path]] = None,
    require_provenance: bool = False,
) -> WriterProfile:
    """
    Sinh hồ sơ WriterProfile từ báo cáo quét ScanValidationReport (hoặc dict).

    Args:
        report_dict: Báo cáo quét hoặc từ điển kết quả scan validation.
        writer_id: Mã định danh người viết.
        crops_base_dir: Thư mục cơ sở chứa file ảnh crop.
        dpi: Độ phân giải quang học quét.
        provenance_ledger_path: Đường dẫn ghi nhật ký xuất xứ ô crop độc lập.
        require_provenance: Bắt buộc chỉ định provenance_ledger_path (mặc định False cho unit test cũ, True trong pilot).
    """
    # Trong đường chạy pilot hoặc khi bật cờ require_provenance, bắt buộc phải có ledger_path
    is_pilot = require_provenance or report_dict.get("is_pilot", False) or report_dict.get("pilot_run", False)
    if is_pilot and not provenance_ledger_path:
        raise ValueError(
            f"Trong đường chạy pilot RQ4 cho {writer_id}, bắt buộc phải chỉ định provenance_ledger_path "
            "để lưu vết xuất xứ ô cắt, không được để trống."
        )

    # Kiểm tra mã scan_id: Yêu cầu định danh chuẩn, không dùng đường dẫn input_file thay thế
    scan_id = report_dict.get("scan_id")
    if provenance_ledger_path is not None:
        if not scan_id:
            candidate_scan_ids = {str(m.get("scan_id")).strip() for m in report_dict.get("crops_metadata", []) if m.get("scan_id")}
            if len(candidate_scan_ids) == 1:
                scan_id = candidate_scan_ids.pop()

        if not scan_id or not str(scan_id).strip():
            raise ValueError(
                f"Thiếu mã 'scan_id' hợp lệ trong báo cáo quét để ghi nhận provenance cho người viết {writer_id}. "
                "Yêu cầu mã định danh chuẩn (ví dụ 'W001_S01_P01'), tuyệt đối không dùng đường dẫn tệp thay thế."
            )
        scan_id_str = str(scan_id).strip()
        if any(sep in scan_id_str for sep in ("/", "\\")) or any(
            scan_id_str.lower().endswith(ext)
            for ext in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".json")
        ):
            raise ValueError(
                f"Mã 'scan_id' trong báo cáo quét mang định dạng đường dẫn tệp không hợp lệ: {scan_id_str!r}. "
                "Yêu cầu mã định danh chuẩn (ví dụ 'W001_S01_P01'), không được dùng đường dẫn thay thế."
            )
    else:
        scan_id_str = str(scan_id).strip() if scan_id else None

    crops_meta = report_dict.get("crops_metadata", [])
    crops_data: List[Dict[str, Any]] = []
    candidate_crops_meta: List[Dict[str, Any]] = []

    base_p = Path(crops_base_dir) if crops_base_dir else None

    for m in crops_meta:
        # Bỏ qua các ô bị từ chối hoặc ô trống
        if m.get("qc_status") in ("QC_REJECTED", "QC_EMPTY"):
            continue

        # Bỏ qua các ô không hợp lệ cho dataset
        if not m.get("is_valid_for_dataset", True):
            continue

        crop_file_rel = m.get("crop_file")
        if not crop_file_rel or not base_p:
            continue

        crop_path = base_p / crop_file_rel
        if not crop_path.exists():
            continue

        img = cv2.imread(str(crop_path))
        if img is None:
            continue

        crops_data.append({
            "crop_image": img,
            "context_tag": m.get("context_tag", "isolated"),
            "is_valid": True,
        })
        candidate_crops_meta.append(m)

    # Trích xuất profile và lấy chính xác danh sách chỉ mục các ô thực sự được extractor sử dụng
    used_crops_indices: List[int] = []
    profile = generate_writer_profile_from_crops(
        writer_id=writer_id,
        crops_data=crops_data,
        dpi=dpi,
        used_indices=used_crops_indices,
    )

    actual_used_crops_meta = [candidate_crops_meta[i] for i in used_crops_indices]

    if provenance_ledger_path is not None:
        record_profile_crop_provenance(
            profile_id=profile.profile_id,
            writer_id=writer_id,
            used_crops_metadata=actual_used_crops_meta,
            ledger_path=provenance_ledger_path,
            scan_id=scan_id_str,
        )

    return profile


def save_writer_profile(
    profile: WriterProfile,
    output_profiles_dir: Union[str, Path],
    summary_jsonl_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Lưu hồ sơ người viết ra file JSON và ghi dòng tổng hợp vào writer_features_summary.jsonl.

    Args:
        profile: Đối tượng WriterProfile cần lưu.
        output_profiles_dir: Thư mục chứa các file JSON (ví dụ: dataset/processed/writer_profiles/profiles/).
        summary_jsonl_path: Đường dẫn file JSONL tổng hợp (tùy chọn).

    Returns:
        Đường dẫn file JSON profile vừa được ghi.
    """
    out_dir = Path(output_profiles_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile_dict = profile.to_dict()
    profile_filename = f"{profile.profile_id}.json"
    profile_path = out_dir / profile_filename

    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile_dict, f, indent=2, ensure_ascii=False)

    # Ghi hoặc cập nhật file summary.jsonl
    if summary_jsonl_path is not None:
        sum_p = Path(summary_jsonl_path)
        sum_p.parent.mkdir(parents=True, exist_ok=True)

        p_dict = profile.to_dict()
        summary_row = {
            "writer_id": p_dict["writer_id"],
            "profile_id": p_dict["profile_id"],
            "version": p_dict["version"],
            "created_at": p_dict["created_at"],
            "num_samples_analyzed": p_dict["num_samples_analyzed"],
            "mean_slant_deg": p_dict["global_style"]["mean_slant_deg"],
            "aspect_ratio_mean": p_dict["global_style"]["aspect_ratio_mean"],
            "stroke_width_mean_mm": p_dict["global_style"]["stroke_width_mean_mm"],
            "baseline_jitter_std": p_dict["global_style"]["baseline_jitter_std"],
            "char_spacing_mean_ratio": p_dict["spacing"]["char_spacing_mean_ratio"],
            "word_spacing_mean_ratio": p_dict["spacing"]["word_spacing_mean_ratio"],
            "line_spacing_mean_ratio": p_dict["spacing"]["line_spacing_mean_ratio"],
            "diacritic_offset_bias": p_dict["diacritic_tendencies"]["diacritic_offset_bias"],
            "diacritic_scale_ratio": p_dict["diacritic_tendencies"]["diacritic_scale_ratio"],
        }

        # Nếu file đã tồn tại, đọc các dòng cũ để tránh trùng lặp writer_id
        # Fail-closed: Báo lỗi nếu phát hiện dòng JSON bị hỏng, giữ nguyên file cũ
        existing_rows: List[Dict[str, Any]] = []
        if sum_p.exists():
            with open(sum_p, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line_str = line.strip()
                    if line_str:
                        try:
                            row = json.loads(line_str)
                            if row.get("writer_id") != profile.writer_id:
                                existing_rows.append(row)
                        except json.JSONDecodeError as err:
                            raise ValueError(
                                f"Phát hiện dòng JSON bị lỗi cấu trúc tại dòng {line_no} trong tệp summary '{sum_p}': {line_str}. "
                                "Hủy bỏ thao tác ghi để bảo vệ toàn vẹn dữ liệu."
                            ) from err

        existing_rows.append(summary_row)
        # Sắp xếp theo writer_id
        existing_rows.sort(key=lambda r: r.get("writer_id", ""))

        with open(sum_p, "w", encoding="utf-8") as f:
            for r in existing_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return profile_path


def main():
    parser = argparse.ArgumentParser(description="OmniDraw Writer Profile Generator CLI")
    parser.add_argument("--report", "-r", required=True, help="Path to ScanValidationReport JSON")
    parser.add_argument("--writer-id", "-w", required=True, help="Writer ID (e.g. W001)")
    parser.add_argument("--crops-dir", "-c", default=None, help="Base dir containing crop image files")
    parser.add_argument("--output-dir", "-o", default="dataset/processed/writer_profiles/profiles", help="Output directory for profile JSON")
    parser.add_argument("--summary", "-s", default="dataset/processed/writer_profiles/features/writer_features_summary.jsonl", help="Path to features summary JSONL")
    parser.add_argument("--provenance-ledger", "-l", required=True, help="Đường dẫn file JSONL nhật ký xuất xứ ô cắt (Bắt buộc trong pilot RQ4 để không mất provenance)")
    parser.add_argument("--dpi", type=int, default=600, help="Scan DPI")
    args = parser.parse_args()

    report_p = Path(args.report)
    if not report_p.exists():
        print(f"Error: Report file not found: {report_p}")
        sys.exit(1)

    with open(report_p, "r", encoding="utf-8") as f:
        report_dict = json.load(f)

    crops_dir = args.crops_dir or report_p.parent

    print(f"Generating Writer Profile for {args.writer_id} from {report_p}...")
    profile = generate_writer_profile_from_report(
        report_dict=report_dict,
        writer_id=args.writer_id,
        crops_base_dir=crops_dir,
        dpi=args.dpi,
        provenance_ledger_path=args.provenance_ledger,
        require_provenance=True,
    )

    out_file = save_writer_profile(
        profile=profile,
        output_profiles_dir=args.output_dir,
        summary_jsonl_path=args.summary,
    )

    print(f"Successfully generated and validated profile: {out_file}")
    print(f"Global Style: Slant={profile.global_style.mean_slant_deg:.2f} deg, AR={profile.global_style.aspect_ratio_mean:.3f}, Jitter={profile.global_style.baseline_jitter_std:.3f} mm")


if __name__ == "__main__":
    main()
