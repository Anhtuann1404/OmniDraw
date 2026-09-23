"""
OmniDraw Scan-Validation Pipeline — Calibration Scale & Distortion Checker.

Validates optical scanner scale and aspect ratio distortion on the rectified canvas:
1. 50.0 mm Precision Ruler (Pilot check: 50.0 ± 0.2 mm).
2. 20.0 x 20.0 mm Aspect Ratio Square (Pilot check: 1.000 ± 0.005).
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np

from backend.scan_validator.specs import (
    RULER_50MM_X1_MM,
    RULER_50MM_X2_MM,
    RULER_50MM_Y_MM,
    RULER_THEORETICAL_LENGTH_MM,
    RULER_TOLERANCE_MM,
    SQUARE_20MM_X_MM,
    SQUARE_20MM_Y_MM,
    SQUARE_20MM_SIZE_MM,
    SQUARE_ASPECT_RATIO_TARGET,
    SQUARE_ASPECT_RATIO_TOLERANCE,
    SQUARE_SIZE_TOLERANCE_MM,
    mm_to_px,
    px_to_mm,
    DEFAULT_DPI,
)


@dataclass
class CalibrationCheckResult:
    overall_pass: bool
    ruler_length_measured_mm: float
    ruler_error_mm: float
    ruler_pass: bool
    square_width_measured_mm: float
    square_height_measured_mm: float
    square_aspect_ratio: float
    square_aspect_ratio_error: float
    square_pass: bool
    details: Dict[str, Any]
    error_message: Optional[str] = None


def check_calibration(
    rectified_image: np.ndarray,
    dpi: int = DEFAULT_DPI,
    debug: bool = False
) -> CalibrationCheckResult:
    """
    Kiểm chứng độ chính xác tỷ lệ co giãn trục quang học và tỷ lệ khung hình.

    Args:
        rectified_image: Ảnh canvas A4 đã được nắn chỉnh phối cảnh chuẩn.
        dpi: Độ phân giải canvas (mặc định 600 DPI).
        debug: Nếu True, in log chi tiết.

    Returns:
        CalibrationCheckResult với kết quả kiểm định chi tiết.
    """
    if rectified_image is None or rectified_image.size == 0:
        return CalibrationCheckResult(
            overall_pass=False,
            ruler_length_measured_mm=0.0,
            ruler_error_mm=0.0,
            ruler_pass=False,
            square_width_measured_mm=0.0,
            square_height_measured_mm=0.0,
            square_aspect_ratio=0.0,
            square_aspect_ratio_error=0.0,
            square_pass=False,
            details={},
            error_message="Rectified image is empty.",
        )

    if len(rectified_image.shape) == 3:
        gray = cv2.cvtColor(rectified_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = rectified_image

    # ==========================================================================
    # 1. Kiểm tra Thước đo 50.0 mm
    # ==========================================================================
    # Vùng chứa thước đo: X in [20.0, 74.0] mm, Y in [266.0, 274.0] mm
    ruler_roi_x1 = mm_to_px(RULER_50MM_X1_MM - 2.0, dpi)
    ruler_roi_x2 = mm_to_px(RULER_50MM_X2_MM + 2.0, dpi)
    ruler_roi_y1 = mm_to_px(RULER_50MM_Y_MM - 4.0, dpi)
    ruler_roi_y2 = mm_to_px(RULER_50MM_Y_MM + 4.0, dpi)

    ruler_crop = gray[ruler_roi_y1:ruler_roi_y2, ruler_roi_x1:ruler_roi_x2]

    # Binarize vùng thước đo để tìm vạch bắt đầu (0mm) và kết thúc (50mm)
    _, ruler_bin = cv2.threshold(ruler_crop, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Chiếu dọc (vertical projection) để phát hiện vị trí các vạch chia
    vert_proj = np.sum(ruler_bin > 0, axis=0)

    # Tìm vị trí đỉnh của vạch 0mm (gần bên trái) và vạch 50mm (gần bên phải)
    # Vạch 0mm nằm gần x_offset = 2.0mm * dpi / 25.4
    expected_x0_roi = mm_to_px(2.0, dpi)
    expected_x50_roi = mm_to_px(52.0, dpi)
    search_win = mm_to_px(2.5, dpi)

    x0_win_start = max(0, expected_x0_roi - search_win)
    x0_win_end = min(len(vert_proj), expected_x0_roi + search_win)
    x50_win_start = max(0, expected_x50_roi - search_win)
    x50_win_end = min(len(vert_proj), expected_x50_roi + search_win)

    if x0_win_start >= x0_win_end or x50_win_start >= x50_win_end or len(vert_proj) == 0:
        measured_ruler_px = 0.0
        measured_ruler_mm = 0.0
        ruler_error_mm = RULER_THEORETICAL_LENGTH_MM
        ruler_pass = False
    else:
        x0_slice = vert_proj[x0_win_start:x0_win_end]
        x50_slice = vert_proj[x50_win_start:x50_win_end]
        min_tick_height_px = max(2, int(mm_to_px(0.2, dpi)))
        if np.max(x0_slice) < min_tick_height_px or np.max(x50_slice) < min_tick_height_px:
            measured_ruler_px = 0.0
            measured_ruler_mm = 0.0
            ruler_error_mm = RULER_THEORETICAL_LENGTH_MM
            ruler_pass = False
        else:
            x0_peak_idx = x0_win_start + int(np.argmax(x0_slice))
            x50_peak_idx = x50_win_start + int(np.argmax(x50_slice))
            measured_ruler_px = float(x50_peak_idx - x0_peak_idx)
            measured_ruler_mm = px_to_mm(measured_ruler_px, dpi)
            ruler_error_mm = abs(measured_ruler_mm - RULER_THEORETICAL_LENGTH_MM)
            ruler_pass = bool(ruler_error_mm <= RULER_TOLERANCE_MM)

    # ==========================================================================
    # 2. Kiểm tra Ô vuông 20.0 x 20.0 mm
    # ==========================================================================
    # Vùng chứa ô vuông: X in [123.0, 147.0] mm, Y in [255.5, 279.5] mm
    sq_roi_x1 = mm_to_px(SQUARE_20MM_X_MM - 2.0, dpi)
    sq_roi_x2 = mm_to_px(SQUARE_20MM_X_MM + SQUARE_20MM_SIZE_MM + 2.0, dpi)
    sq_roi_y1 = mm_to_px(SQUARE_20MM_Y_MM - 2.0, dpi)
    sq_roi_y2 = mm_to_px(SQUARE_20MM_Y_MM + SQUARE_20MM_SIZE_MM + 2.0, dpi)

    sq_crop = gray[sq_roi_y1:sq_roi_y2, sq_roi_x1:sq_roi_x2]
    _, sq_bin = cv2.threshold(sq_crop, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    sq_contours, _ = cv2.findContours(sq_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_cnt = None
    best_area = 0.0
    for cnt in sq_contours:
        area = cv2.contourArea(cnt)
        if area > best_area:
            best_area = area
            best_cnt = cnt

    if best_cnt is not None and best_area > 0:
        x, y, w, h = cv2.boundingRect(best_cnt)
        measured_sq_w_mm = px_to_mm(w, dpi)
        measured_sq_h_mm = px_to_mm(h, dpi)
        sq_aspect_ratio = float(w / h) if h > 0 else 0.0
        ar_error = abs(sq_aspect_ratio - SQUARE_ASPECT_RATIO_TARGET)
        w_error = abs(measured_sq_w_mm - SQUARE_20MM_SIZE_MM)
        h_error = abs(measured_sq_h_mm - SQUARE_20MM_SIZE_MM)
        square_pass = bool(
            ar_error <= SQUARE_ASPECT_RATIO_TOLERANCE
            and w_error <= SQUARE_SIZE_TOLERANCE_MM
            and h_error <= SQUARE_SIZE_TOLERANCE_MM
        )
    else:
        # Không tìm thấy ô vuông: Báo lỗi thất bại, tuyệt đối không gán giá trị lý thuyết!
        measured_sq_w_mm = 0.0
        measured_sq_h_mm = 0.0
        sq_aspect_ratio = 0.0
        ar_error = abs(0.0 - SQUARE_ASPECT_RATIO_TARGET)
        square_pass = False

    overall_pass = bool(ruler_pass and square_pass)

    details = {
        "ruler": {
            "target_mm": RULER_THEORETICAL_LENGTH_MM,
            "measured_mm": round(measured_ruler_mm, 3),
            "error_mm": round(ruler_error_mm, 3),
            "tolerance_mm": RULER_TOLERANCE_MM,
            "is_pass": ruler_pass,
        },
        "square": {
            "target_size_mm": SQUARE_20MM_SIZE_MM,
            "measured_w_mm": round(measured_sq_w_mm, 3),
            "measured_h_mm": round(measured_sq_h_mm, 3),
            "aspect_ratio": round(sq_aspect_ratio, 4),
            "ar_error": round(ar_error, 4),
            "ar_tolerance": SQUARE_ASPECT_RATIO_TOLERANCE,
            "is_pass": square_pass,
        },
    }

    return CalibrationCheckResult(
        overall_pass=overall_pass,
        ruler_length_measured_mm=round(measured_ruler_mm, 3),
        ruler_error_mm=round(ruler_error_mm, 3),
        ruler_pass=ruler_pass,
        square_width_measured_mm=round(measured_sq_w_mm, 3),
        square_height_measured_mm=round(measured_sq_h_mm, 3),
        square_aspect_ratio=round(sq_aspect_ratio, 4),
        square_aspect_ratio_error=round(ar_error, 4),
        square_pass=square_pass,
        details=details,
        error_message=None if overall_pass else "Calibration tolerances exceeded.",
    )
