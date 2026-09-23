"""
Unit and Integration Tests for OmniDraw Scan-Validation Pipeline.

Tests:
1. Specs & geometric conversions.
2. Synthetic sheet generation & corner fiducial detection.
3. Rotation & skew rectification stress test.
4. Scale calibration & aspect ratio checking.
5. Deterministic auto-cropping across all forms (P01..P04).
6. Quality control & boundary overflow detection.
7. Full pipeline integration with report serialization.
"""

import json
import math
from pathlib import Path
import sys
import cv2
import numpy as np
import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.scan_validator.specs import (
    A4_WIDTH_MM,
    A4_HEIGHT_MM,
    FIDUCIAL_SIZE_MM,
    FIDUCIAL_THEORETICAL_CENTERS_MM,
    THEORETICAL_DX_MM,
    THEORETICAL_DY_MM,
    THEORETICAL_DIAG_MM,
    RULER_50MM_X1_MM,
    RULER_50MM_X2_MM,
    RULER_50MM_Y_MM,
    SQUARE_20MM_X_MM,
    SQUARE_20MM_Y_MM,
    SQUARE_20MM_SIZE_MM,
    SQUARE_ASPECT_RATIO_TARGET,
    SQUARE_SIZE_TOLERANCE_MM,
    mm_to_px,
    px_to_mm,
    get_form_specs,
    DEFAULT_DPI,
)
from backend.scan_validator.fiducial_detector import detect_fiducials, FiducialDetectionResult
from backend.scan_validator.rectifier import rectify_scan, RectificationResult
from backend.scan_validator.calibration_checker import check_calibration, CalibrationCheckResult
from backend.scan_validator.qc_evaluator import evaluate_crop_qc, CropQCResult
from backend.scan_validator.auto_cropper import crop_sheet, ExtractedCrop
from backend.scan_validator.pipeline import ScanValidationPipeline, ScanValidationReport


def create_synthetic_sheet(
    dpi: int = 150,
    add_ruler: bool = True,
    add_square: bool = True,
    rotation_deg: float = 0.0,
    shift_x_px: int = 0,
    shift_y_px: int = 0,
) -> np.ndarray:
    """Tạo một canvas ảnh giả lập chuẩn A4 có đầy đủ 4 mốc fiducial và khối kiểm chuẩn."""
    w = mm_to_px(A4_WIDTH_MM, dpi)
    h = mm_to_px(A4_HEIGHT_MM, dpi)

    # Nền giấy trắng
    img = np.full((h, w, 3), 255, dtype=np.uint8)

    # Vẽ 4 mốc fiducial vuông đen 5x5mm tại các góc
    # TL: [12, 17] mm; TR: [193, 198] mm; BL: [12, 17] x [280, 285] mm; BR: [193, 198] x [280, 285] mm
    f_sz = mm_to_px(FIDUCIAL_SIZE_MM, dpi)

    tl_x1 = mm_to_px(12.0, dpi)
    tl_y1 = mm_to_px(12.0, dpi)
    cv2.rectangle(img, (tl_x1, tl_y1), (tl_x1 + f_sz, tl_y1 + f_sz), (0, 0, 0), -1)

    tr_x1 = mm_to_px(193.0, dpi)
    tr_y1 = mm_to_px(12.0, dpi)
    cv2.rectangle(img, (tr_x1, tr_y1), (tr_x1 + f_sz, tr_y1 + f_sz), (0, 0, 0), -1)

    bl_x1 = mm_to_px(12.0, dpi)
    bl_y1 = mm_to_px(280.0, dpi)
    cv2.rectangle(img, (bl_x1, bl_y1), (bl_x1 + f_sz, bl_y1 + f_sz), (0, 0, 0), -1)

    br_x1 = mm_to_px(193.0, dpi)
    br_y1 = mm_to_px(280.0, dpi)
    cv2.rectangle(img, (br_x1, br_y1), (br_x1 + f_sz, br_y1 + f_sz), (0, 0, 0), -1)

    # Vẽ thước đo 50mm tại Y=270.0mm (từ X=22.0 đến 72.0mm)
    if add_ruler:
        rx1 = mm_to_px(RULER_50MM_X1_MM, dpi)
        rx2 = mm_to_px(RULER_50MM_X2_MM, dpi)
        ry = mm_to_px(RULER_50MM_Y_MM, dpi)
        cv2.line(img, (rx1, ry), (rx2, ry), (0, 0, 0), max(1, mm_to_px(0.4, dpi)))
        # Vạch chia 0mm và 50mm
        tick_h = mm_to_px(4.0, dpi)
        cv2.line(img, (rx1, ry - tick_h // 2), (rx1, ry + tick_h // 2), (0, 0, 0), max(1, mm_to_px(0.4, dpi)))
        cv2.line(img, (rx2, ry - tick_h // 2), (rx2, ry + tick_h // 2), (0, 0, 0), max(1, mm_to_px(0.4, dpi)))

    # Vẽ ô vuông 20x20mm tại X=167.0, Y=257.5mm
    if add_square:
        sx1 = mm_to_px(SQUARE_20MM_X_MM, dpi)
        sy1 = mm_to_px(SQUARE_20MM_Y_MM, dpi)
        ssz = mm_to_px(SQUARE_20MM_SIZE_MM, dpi)
        cv2.rectangle(img, (sx1, sy1), (sx1 + ssz, sy1 + ssz), (0, 0, 0), max(1, mm_to_px(0.4, dpi)))

    # Nếu có xoay hoặc dịch chuyển giả lập
    if abs(rotation_deg) > 1e-3 or shift_x_px != 0 or shift_y_px != 0:
        center = (w / 2.0, h / 2.0)
        M = cv2.getRotationMatrix2D(center, rotation_deg, 1.0)
        M[0, 2] += shift_x_px
        M[1, 2] += shift_y_px
        img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

    return img


# ==============================================================================
# 1. Tests for Specs & Conversion
# ==============================================================================

def test_specs_and_conversion():
    """Kiểm tra tính nhất quán giữa các hàm quy đổi mm <-> px và danh mục form."""
    assert mm_to_px(25.4, dpi=600) == 600
    assert mm_to_px(25.4, dpi=300) == 300
    assert math.isclose(px_to_mm(600, dpi=600), 25.4, rel_tol=1e-5)

    # Kiểm tra số lượng mẫu từng form
    p01 = get_form_specs("P01")
    assert len(p01) == 24
    assert p01[0].sample_id == "BASE_001"
    assert p01[-1].sample_id == "REP_004"

    p02 = get_form_specs("P02")
    assert len(p02) == 16
    assert p02[0].sample_id == "CTX_INIT_001"

    p03 = get_form_specs("P03")
    assert len(p03) == 3
    assert p03[0].sample_id == "SENT_001"

    p04 = get_form_specs("P04")
    assert len(p04) == 1
    assert p04[0].sample_id == "PARA_001"

    # Kiểm tra tọa độ kiểm chuẩn ô vuông và ROI [123.0, 147.0] mm
    assert SQUARE_20MM_X_MM == 125.0
    assert SQUARE_20MM_Y_MM == 257.5
    assert (SQUARE_20MM_X_MM - 2.0) == 123.0
    assert (SQUARE_20MM_X_MM + SQUARE_20MM_SIZE_MM + 2.0) == 147.0

    with pytest.raises(ValueError):
        get_form_specs("INVALID_FORM")


# ==============================================================================
# 2. Tests for Fiducial Detection
# ==============================================================================

def test_fiducial_detection_ideal():
    """Kiểm tra phát hiện chính xác 4 mốc fiducial trên ảnh giả lập chuẩn."""
    dpi = 150
    img = create_synthetic_sheet(dpi=dpi)
    res = detect_fiducials(img, dpi=dpi)

    assert res.is_success is True
    assert res.detected_count == 4
    assert len(res.centers) == 4
    for key in ("top_left", "top_right", "bottom_left", "bottom_right"):
        assert key in res.centers

    # Sai số khoảng cách so với lý thuyết < 1.0 mm (ở dpi 150)
    assert abs(res.measured_dx_mm - THEORETICAL_DX_MM) < 1.0
    assert abs(res.measured_dy_mm - THEORETICAL_DY_MM) < 1.0
    assert abs(res.measured_diag_mm - THEORETICAL_DIAG_MM) < 1.5
    assert abs(res.estimated_skew_deg) < 0.2


def test_fiducial_detection_rotated():
    """Kiểm tra phát hiện mốc khi ảnh bị xoay nghiêng (+2.5 độ)."""
    dpi = 150
    rot = 2.5
    img = create_synthetic_sheet(dpi=dpi, rotation_deg=rot)
    res = detect_fiducials(img, dpi=dpi)

    assert res.is_success is True
    assert res.detected_count == 4
    # Góc ước tính phải gần bằng góc xoay thực
    # Chú ý: cv2 rotation matrix quay ngược chiều kim đồng hồ đối với góc dương
    assert abs(abs(res.estimated_skew_deg) - rot) < 0.5


def test_fiducial_detection_empty_fails():
    """Kiểm tra xử lý ảnh rỗng hoặc thiếu mốc trả về lỗi sạch."""
    res = detect_fiducials(None)
    assert res.is_success is False
    assert res.error_message is not None

    blank = np.full((500, 500), 255, dtype=np.uint8)
    res_blank = detect_fiducials(blank, dpi=150)
    assert res_blank.is_success is False


# ==============================================================================
# 3. Tests for Rectifier
# ==============================================================================

def test_rectifier_deskews_rotated_sheet():
    """Kiểm tra nắn thẳng ảnh xoay nghiêng về canvas chuẩn."""
    dpi = 150
    img = create_synthetic_sheet(dpi=dpi, rotation_deg=-2.0, shift_x_px=10, shift_y_px=-10)
    det = detect_fiducials(img, dpi=dpi)
    assert det.is_success is True

    rect = rectify_scan(img, det.centers, target_dpi=dpi)
    assert rect.is_success is True
    assert rect.rectified_image is not None
    assert rect.target_width_px == mm_to_px(A4_WIDTH_MM, dpi)
    assert rect.target_height_px == mm_to_px(A4_HEIGHT_MM, dpi)

    # Sau khi nắn thẳng, chạy lại detect_fiducials trên ảnh nắn phải có góc nghiêng ~ 0 độ
    det_after = detect_fiducials(rect.rectified_image, dpi=dpi)
    assert det_after.is_success is True
    assert abs(det_after.estimated_skew_deg) < 0.15


# ==============================================================================
# 4. Tests for Calibration Checker
# ==============================================================================

def test_calibration_checker_ideal():
    """Kiểm tra khối kiểm chuẩn trên ảnh chuẩn đạt PASS."""
    dpi = 150
    img = create_synthetic_sheet(dpi=dpi, add_ruler=True, add_square=True)
    calib = check_calibration(img, dpi=dpi)

    assert calib.ruler_pass is True
    assert calib.ruler_error_mm <= 0.20
    assert calib.square_pass is True
    assert calib.square_aspect_ratio_error <= 0.005
    assert calib.overall_pass is True


# ==============================================================================
# 5. Tests for Auto-Cropper
# ==============================================================================

def test_auto_cropper_extracts_all_cells():
    """Kiểm tra auto_cropper bóc tách đủ 24 ô mẫu cho P01."""
    dpi = 150
    img = create_synthetic_sheet(dpi=dpi)
    crops = crop_sheet(img, form_type="P01", dpi=dpi, extract_full_cell=True)

    assert len(crops) == 24
    assert crops[0].sample_id == "BASE_001"
    assert crops[0].crop_image.shape[0] > 0
    assert crops[0].crop_image.shape[1] > 0
    assert crops[0].full_cell_image is not None


# ==============================================================================
# 6. Tests for QC & Overflow Evaluation
# ==============================================================================

def test_qc_evaluator_clean_ink():
    """Kiểm tra ô có nét viết hợp lệ không tràn viền đạt QC_PASS."""
    h, w = 200, 300
    crop = np.full((h, w, 3), 255, dtype=np.uint8)
    # Vẽ nét viết ở giữa ô (cách xa biên)
    cv2.line(crop, (100, 100), (200, 100), (20, 20, 20), 4)

    res = evaluate_crop_qc(crop, dpi=150, border_margin_mm=1.0)
    assert res.has_ink is True
    assert res.overflow_detected is False
    assert res.qc_status == "QC_PASS"
    assert res.is_valid_for_dataset is True


def test_qc_evaluator_overflow_top():
    """Kiểm tra nét viết tràn qua đỉnh ô (chạm dải nhãn) bị gắn cờ cảnh báo/lỗi."""
    h, w = 200, 300
    crop = np.full((h, w, 3), 255, dtype=np.uint8)
    # Vẽ nét viết cắt qua mép trên
    cv2.line(crop, (150, 0), (150, 80), (10, 10, 10), 6)

    res = evaluate_crop_qc(crop, dpi=150, border_margin_mm=1.0)
    assert res.has_ink is True
    assert res.overflow_detected is True
    assert res.overflow_details["has_top_overflow"] is True
    assert res.qc_status in ("QC_FLAGGED", "QC_REJECTED")


def test_qc_evaluator_empty_cell():
    """Kiểm tra ô trắng không có nét viết trả về QC_EMPTY."""
    crop = np.full((200, 300, 3), 255, dtype=np.uint8)
    res = evaluate_crop_qc(crop, dpi=150)
    assert res.has_ink is False
    assert res.qc_status == "QC_EMPTY"
    assert res.is_valid_for_dataset is False


# ==============================================================================
# 7. End-to-End Pipeline Test
# ==============================================================================

def test_full_pipeline_run_and_persistence(tmp_path: Path):
    """Kiểm chứng toàn trình pipeline từ ảnh quét đến tạo thư mục và file JSON report."""
    dpi = 150
    img = create_synthetic_sheet(dpi=dpi, rotation_deg=1.0)
    img_path = tmp_path / "test_scan_p01.png"
    cv2.imwrite(str(img_path), img)

    out_dir = tmp_path / "output_processed"

    pipeline = ScanValidationPipeline(dpi=dpi)
    report = pipeline.process(
        image_input=img_path,
        form_type="P01",
        output_dir=out_dir,
        save_crops=True,
        save_rectified=True,
    )

    assert report.is_success is True
    assert report.form_type == "P01"
    assert report.summary["total_extracted_samples"] == 24
    assert report.fiducials["detected_count"] == 4

    # Kiểm tra các artifact được lưu đúng trên đĩa
    assert (out_dir / "rectified_canvas.png").exists()
    assert (out_dir / "validation_report.json").exists()
    assert (out_dir / "crops" / "BASE_001_crop.png").exists()
    assert (out_dir / "crops" / "BASE_001_full.png").exists()

    # Kiểm tra nội dung JSON report đọc lại được
    with open(out_dir / "validation_report.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["form_type"] == "P01"
    assert len(data["crops_metadata"]) == 24


# ==============================================================================
# 8. Hardening & Edge-Case Tests (from Code Review)
# ==============================================================================

def test_mm_to_px_rounding_precision_at_600dpi():
    """Kiểm tra hàm mm_to_px dùng round() chuẩn xác, không bị lỗi off-by-one."""
    # 1.0 mm tại 600 DPI = 600 / 25.4 = 23.622... px -> làm tròn thành 24 px
    assert mm_to_px(1.0, 600) == 24
    # 0.5 mm tại 600 DPI = 300 / 25.4 = 11.811... px -> làm tròn thành 12 px
    assert mm_to_px(0.5, 600) == 12
    # 25.4 mm (chính xác 1 inch) tại 600 DPI = 600 px
    assert mm_to_px(25.4, 600) == 600
    # Ngược lại px_to_mm(600, 600) == 25.4
    assert abs(px_to_mm(600, 600) - 25.4) < 1e-6


def test_calibration_checker_missing_square():
    """Kiểm tra khi ô vuông bị mất/mờ, checker phải FAIL và KHÔNG fallback pass ngầm."""
    dpi = 150
    # Tạo sheet chỉ có thước đo, KHÔNG có ô vuông
    img = create_synthetic_sheet(dpi=dpi, add_ruler=True, add_square=False)
    calib = check_calibration(img, dpi=dpi)

    assert calib.ruler_pass is True
    assert calib.square_pass is False
    assert calib.overall_pass is False
    assert calib.square_aspect_ratio_error == abs(0.0 - SQUARE_ASPECT_RATIO_TARGET)
    assert calib.details["square"]["ar_error"] == abs(0.0 - SQUARE_ASPECT_RATIO_TARGET)
    assert calib.error_message is not None


def test_calibration_checker_square_boundary_tolerance():
    """Kiểm tra dung sai kích thước ô vuông SQUARE_SIZE_TOLERANCE_MM (0.80 mm) tại các điểm biên."""
    dpi = 300  # Sử dụng 300 DPI để đạt độ mịn pixel cao (11.8 px/mm)
    # 1. Kích thước chuẩn 20.0 mm: PASS
    img_pass = create_synthetic_sheet(dpi=dpi, add_ruler=True, add_square=True)
    calib_pass = check_calibration(img_pass, dpi=dpi)
    assert calib_pass.square_pass is True

    # 2. Điểm biên nằm TRONG dung sai: ô vuông 20.5 mm (|20.5 - 20.0| = 0.50 mm <= 0.80 mm) -> PASS
    img_within = create_synthetic_sheet(dpi=dpi, add_ruler=True, add_square=False)
    sx1 = mm_to_px(SQUARE_20MM_X_MM, dpi)
    sy1 = mm_to_px(SQUARE_20MM_Y_MM, dpi)
    ssz_within = mm_to_px(20.5, dpi)
    cv2.rectangle(img_within, (sx1, sy1), (sx1 + ssz_within, sy1 + ssz_within), (0, 0, 0), 1)
    calib_within = check_calibration(img_within, dpi=dpi)
    assert calib_within.square_pass is True

    # 3. Điểm biên VƯỢT QUÁ dung sai: ô vuông 21.5 mm (|21.5 - 20.0| = 1.50 mm > 0.80 mm) -> FAIL
    img_fail = create_synthetic_sheet(dpi=dpi, add_ruler=True, add_square=False)
    ssz_large = mm_to_px(21.5, dpi)
    cv2.rectangle(img_fail, (sx1, sy1), (sx1 + ssz_large, sy1 + ssz_large), (0, 0, 0), 1)
    calib_fail = check_calibration(img_fail, dpi=dpi)
    assert calib_fail.square_pass is False
    assert calib_fail.overall_pass is False


def test_calibration_checker_missing_ruler():
    """Kiểm tra khi thước đo bị mất/trắng, checker phải FAIL và guard argmax an toàn."""
    dpi = 150
    # Tạo sheet chỉ có ô vuông, KHÔNG có thước đo
    img = create_synthetic_sheet(dpi=dpi, add_ruler=False, add_square=True)
    calib = check_calibration(img, dpi=dpi)

    assert calib.ruler_pass is False
    assert calib.overall_pass is False


def test_fiducial_detection_missing_one_marker():
    """Kiểm tra khi chỉ phát hiện 3 mốc (thiếu 1 mốc ở góc), hệ thống từ chối an toàn."""
    dpi = 150
    h, w = mm_to_px(A4_HEIGHT_MM, dpi), mm_to_px(A4_WIDTH_MM, dpi)
    img = np.full((h, w, 3), 255, dtype=np.uint8)
    f_sz = mm_to_px(FIDUCIAL_SIZE_MM, dpi)

    # Chỉ vẽ 3 mốc (TL, TR, BL), bỏ BR
    tl = mm_to_px(12.0, dpi)
    tr = mm_to_px(193.0, dpi)
    bl_y = mm_to_px(280.0, dpi)
    cv2.rectangle(img, (tl, tl), (tl + f_sz, tl + f_sz), (0, 0, 0), -1)
    cv2.rectangle(img, (tr, tl), (tr + f_sz, tl + f_sz), (0, 0, 0), -1)
    cv2.rectangle(img, (tl, bl_y), (tl + f_sz, bl_y + f_sz), (0, 0, 0), -1)

    result = detect_fiducials(img, dpi=dpi)
    assert result.is_success is False
    assert result.detected_count == 3
    assert result.error_message is not None


def test_auto_cropper_all_forms_and_counts():
    """Kiểm tra auto-cropper hỗ trợ đầy đủ cả 4 form P01, P02, P03, P04 với đúng số lượng ô."""
    dpi = 150
    img = create_synthetic_sheet(dpi=dpi)

    crops_p01 = crop_sheet(img, form_type="P01", dpi=dpi)
    crops_p02 = crop_sheet(img, form_type="P02", dpi=dpi)
    crops_p03 = crop_sheet(img, form_type="P03", dpi=dpi)
    crops_p04 = crop_sheet(img, form_type="P04", dpi=dpi)

    assert len(crops_p01) == 24
    assert len(crops_p02) == 16
    assert len(crops_p03) == 3
    assert len(crops_p04) == 1


def test_auto_cropper_out_of_bounds_handling():
    """Kiểm tra auto-cropper xử lý ảnh quá nhỏ mà không gây crash exception."""
    dpi = 150
    # Ảnh quá nhỏ (100x100 px), các ô của form nằm ngoài kích thước ảnh
    tiny_img = np.full((100, 100, 3), 255, dtype=np.uint8)
    crops = crop_sheet(tiny_img, form_type="P01", dpi=dpi, extract_full_cell=True)

    assert len(crops) == 24
    assert crops[0].qc_result.overflow_detected is True
    assert crops[0].qc_result.overflow_details["has_bounds_overflow"] is True
    for c in crops:
        assert c.qc_result.qc_status == "QC_REJECTED"
        assert c.qc_result.overflow_detected is True
        assert c.qc_result.overflow_details.get("has_bounds_overflow") is True
        assert c.qc_result.is_valid_for_dataset is False
        assert c.crop_image.shape == (0, 0, 3)
        assert c.full_cell_image is None


def test_auto_cropper_partial_overflow():
    """Kiểm tra auto-cropper phát hiện trường hợp ô viết bị cắt một phần ở biên ảnh (partial bounds overflow)."""
    dpi = 150
    # Kích thước A4 chuẩn tại 150 DPI là 1240 x 1754 px.
    # Cắt bớt chiều ngang còn 1000 px khiến các ô cột 4 của P01 bị cắt cụt một phần
    full_img = create_synthetic_sheet(dpi=dpi)
    partially_clipped_img = full_img[:, :1000].copy()

    crops = crop_sheet(partially_clipped_img, form_type="P01", dpi=dpi)
    assert len(crops) == 24

    clipped_crops = [c for c in crops if c.qc_result.overflow_details.get("is_partial_clip")]
    assert len(clipped_crops) > 0
    for c in clipped_crops:
        assert c.qc_result.overflow_detected is True
        assert c.qc_result.overflow_details["has_bounds_overflow"] is True
        assert c.qc_result.overflow_details["is_partial_clip"] is True
        assert c.qc_result.qc_status in ("QC_FLAGGED", "QC_REJECTED")


def test_auto_cropper_extract_full_cell_disabled():
    """Kiểm tra cờ extract_full_cell=False không trích xuất ảnh cell bao quát."""
    dpi = 150
    img = create_synthetic_sheet(dpi=dpi)
    crops = crop_sheet(img, form_type="P01", dpi=dpi, extract_full_cell=False)

    assert len(crops) == 24
    for c in crops:
        assert c.full_cell_image is None
        assert c.crop_image.shape[0] > 0 and c.crop_image.shape[1] > 0


def test_full_pipeline_p02_and_p04(tmp_path: Path):
    """Kiểm tra toàn trình pipeline với form P02 và P04."""
    dpi = 150
    img = create_synthetic_sheet(dpi=dpi)
    pipeline = ScanValidationPipeline(dpi=dpi)

    # Test P02
    report_p02 = pipeline.process(
        image_input=img,
        form_type="P02",
        output_dir=tmp_path / "out_p02",
        save_crops=True,
    )
    assert report_p02.is_success is True
    assert report_p02.form_type == "P02"
    assert report_p02.summary["total_extracted_samples"] == 16
    assert (tmp_path / "out_p02" / "validation_report.json").exists()

    # Test P04
    report_p04 = pipeline.process(
        image_input=img,
        form_type="P04",
        output_dir=tmp_path / "out_p04",
        save_crops=True,
    )
    assert report_p04.is_success is True
    assert report_p04.form_type == "P04"
    assert report_p04.summary["total_extracted_samples"] == 1
    assert (tmp_path / "out_p04" / "validation_report.json").exists()


