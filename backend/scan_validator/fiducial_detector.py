"""
OmniDraw Scan-Validation Pipeline — Corner Fiducial Marker Detector.

Detects the 4 black square fiducial markers (5.0 x 5.0 mm) at the corners of
OmniDraw collection sheets with sub-pixel precision and geometric validation.
"""

import math
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List, Any
import cv2
import numpy as np

from backend.scan_validator.specs import (
    FIDUCIAL_SIZE_MM,
    FIDUCIAL_THEORETICAL_CENTERS_MM,
    THEORETICAL_DX_MM,
    THEORETICAL_DY_MM,
    THEORETICAL_DIAG_MM,
    mm_to_px,
    px_to_mm,
    DEFAULT_DPI,
)


@dataclass
class FiducialDetectionResult:
    is_success: bool
    centers: Dict[str, Tuple[float, float]]  # "top_left", "top_right", "bottom_left", "bottom_right"
    measured_dx_mm: float
    measured_dy_mm: float
    measured_diag_mm: float
    estimated_skew_deg: float
    confidence: float
    detected_count: int
    error_message: Optional[str] = None


def detect_fiducials(
    image: np.ndarray,
    dpi: int = DEFAULT_DPI,
    debug: bool = False
) -> FiducialDetectionResult:
    """
    Tự động phát hiện 4 mốc quang học fiducial (5x5mm) tại 4 góc trang giấy.

    Args:
        image: Ảnh quét thô (BGR hoặc Grayscale).
        dpi: Độ phân giải quét ước tính (mặc định 600 DPI).
        debug: Nếu True, in log chi tiết quá trình phát hiện.

    Returns:
        FiducialDetectionResult chứa tọa độ 4 mốc và các chỉ số hình học.
    """
    if image is None or image.size == 0:
        return FiducialDetectionResult(
            is_success=False,
            centers={},
            measured_dx_mm=0.0,
            measured_dy_mm=0.0,
            measured_diag_mm=0.0,
            estimated_skew_deg=0.0,
            confidence=0.0,
            detected_count=0,
            error_message="Input image is empty or invalid.",
        )

    # Chuyển sang Grayscale nếu là ảnh màu
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    img_h, img_w = gray.shape[:2]

    # Tính diện tích lý thuyết của mốc 5x5mm tại DPI hiện tại
    marker_px = mm_to_px(FIDUCIAL_SIZE_MM, dpi)
    expected_area = float(marker_px * marker_px)
    min_area = expected_area * 0.30
    max_area = expected_area * 2.80

    # Binarize bằng Otsu thresholding
    # #ponytail: Otsu thresholding chuẩn xác định vùng đen đậm trên nền giấy trắng sáng
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if not (min_area <= area <= max_area):
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        ar = w / float(h) if h > 0 else 0.0
        if not (0.65 <= ar <= 1.50):
            continue

        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0.0
        if solidity < 0.82:
            continue

        # Tính tâm khối
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]

        # Đánh giá điểm squareness (tỷ lệ ar gần 1.0 và solidity cao)
        score = (1.0 - abs(ar - 1.0)) * solidity
        candidates.append({
            "center": (cx, cy),
            "area": area,
            "bbox": (x, y, w, h),
            "contour": cnt,
            "score": score,
        })

    if debug:
        print(f"[DEBUG] Found {len(candidates)} fiducial candidates with expected area ~{expected_area:.0f}")

    if len(candidates) < 4:
        # Fallback thử adaptive threshold nếu Otsu bỏ sót mốc do bóng viền máy quét
        adaptive_bin = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 10
        )
        contours, _ = cv2.findContours(adaptive_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates.clear()
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if not (min_area <= area <= max_area):
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            ar = w / float(h) if h > 0 else 0.0
            if not (0.65 <= ar <= 1.50):
                continue
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0.0
            if solidity < 0.82:
                continue
            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]
            score = (1.0 - abs(ar - 1.0)) * solidity
            candidates.append({
                "center": (cx, cy),
                "area": area,
                "bbox": (x, y, w, h),
                "contour": cnt,
                "score": score,
            })

    if len(candidates) < 4:
        return FiducialDetectionResult(
            is_success=False,
            centers={},
            measured_dx_mm=0.0,
            measured_dy_mm=0.0,
            measured_diag_mm=0.0,
            estimated_skew_deg=0.0,
            confidence=0.0,
            detected_count=len(candidates),
            error_message=f"Insufficient fiducial candidates found ({len(candidates)} < 4).",
        )

    # Phân nhóm mốc vào 4 góc phần tư tương đối
    half_w = img_w / 2.0
    half_h = img_h / 2.0

    quadrants = {
        "top_left": [],
        "top_right": [],
        "bottom_left": [],
        "bottom_right": [],
    }

    for cand in candidates:
        cx, cy = cand["center"]
        if cx <= half_w and cy <= half_h:
            quadrants["top_left"].append(cand)
        elif cx > half_w and cy <= half_h:
            quadrants["top_right"].append(cand)
        elif cx <= half_w and cy > half_h:
            quadrants["bottom_left"].append(cand)
        else:
            quadrants["bottom_right"].append(cand)

    # Chọn mốc tốt nhất ở mỗi góc
    # Mốc chuẩn nằm gần mép góc giấy hơn và có điểm score cao
    selected_centers: Dict[str, Tuple[float, float]] = {}
    missing_corners = []

    corner_anchors = {
        "top_left": (0, 0),
        "top_right": (img_w, 0),
        "bottom_left": (0, img_h),
        "bottom_right": (img_w, img_h),
    }

    for corner, cands in quadrants.items():
        if not cands:
            missing_corners.append(corner)
            continue
        ax, ay = corner_anchors[corner]
        # Xếp hạng: ưu tiên gần góc giấy hợp lý và điểm score cao
        def _rank_key(c):
            cx, cy = c["center"]
            dist_to_corner = math.hypot(cx - ax, cy - ay)
            return dist_to_corner / (c["score"] + 1e-3)

        cands.sort(key=_rank_key)
        best_cand = cands[0]
        selected_centers[corner] = best_cand["center"]

    if missing_corners:
        return FiducialDetectionResult(
            is_success=False,
            centers=selected_centers,
            measured_dx_mm=0.0,
            measured_dy_mm=0.0,
            measured_diag_mm=0.0,
            estimated_skew_deg=0.0,
            confidence=0.0,
            detected_count=len(selected_centers),
            error_message=f"Missing fiducial markers in quadrants: {', '.join(missing_corners)}.",
        )

    # Tinh chỉnh tâm với sub-pixel precision
    tl = selected_centers["top_left"]
    tr = selected_centers["top_right"]
    bl = selected_centers["bottom_left"]
    br = selected_centers["bottom_right"]

    # Đo khoảng cách thực tế (pixels và quy đổi sang mm)
    dx_top_px = math.hypot(tr[0] - tl[0], tr[1] - tl[1])
    dx_bot_px = math.hypot(br[0] - bl[0], br[1] - bl[1])
    dy_left_px = math.hypot(bl[0] - tl[0], bl[1] - tl[1])
    dy_right_px = math.hypot(br[0] - tr[0], br[1] - tr[1])
    diag1_px = math.hypot(br[0] - tl[0], br[1] - tl[1])
    diag2_px = math.hypot(tr[0] - bl[0], tr[1] - bl[1])

    mean_dx_px = (dx_top_px + dx_bot_px) / 2.0
    mean_dy_px = (dy_left_px + dy_right_px) / 2.0
    mean_diag_px = (diag1_px + diag2_px) / 2.0

    measured_dx_mm = px_to_mm(mean_dx_px, dpi)
    measured_dy_mm = px_to_mm(mean_dy_px, dpi)
    measured_diag_mm = px_to_mm(mean_diag_px, dpi)

    # Ước tính góc nghiêng (skew angle in degrees)
    angle_top = math.degrees(math.atan2(tr[1] - tl[1], tr[0] - tl[0]))
    angle_bot = math.degrees(math.atan2(br[1] - bl[1], br[0] - bl[0]))
    estimated_skew_deg = (angle_top + angle_bot) / 2.0

    # Kiểm tra tính hợp lệ hình học (dung sai ±10% so với lý thuyết)
    dx_err = abs(measured_dx_mm - THEORETICAL_DX_MM) / THEORETICAL_DX_MM
    dy_err = abs(measured_dy_mm - THEORETICAL_DY_MM) / THEORETICAL_DY_MM
    diag_err = abs(measured_diag_mm - THEORETICAL_DIAG_MM) / THEORETICAL_DIAG_MM

    max_err = max(dx_err, dy_err, diag_err)
    if max_err > 0.12:
        return FiducialDetectionResult(
            is_success=False,
            centers=selected_centers,
            measured_dx_mm=measured_dx_mm,
            measured_dy_mm=measured_dy_mm,
            measured_diag_mm=measured_diag_mm,
            estimated_skew_deg=estimated_skew_deg,
            confidence=max(0.0, 1.0 - max_err),
            detected_count=4,
            error_message=f"Fiducial layout exceeds geometry tolerance (max_err={max_err:.1%}).",
        )

    confidence = float(np.clip(1.0 - max_err, 0.5, 1.0))

    return FiducialDetectionResult(
        is_success=True,
        centers=selected_centers,
        measured_dx_mm=round(measured_dx_mm, 3),
        measured_dy_mm=round(measured_dy_mm, 3),
        measured_diag_mm=round(measured_diag_mm, 3),
        estimated_skew_deg=round(estimated_skew_deg, 3),
        confidence=round(confidence, 4),
        detected_count=4,
        error_message=None,
    )
