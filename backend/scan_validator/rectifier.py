"""
OmniDraw Scan-Validation Pipeline — Perspective & Affine Rectifier.

Warps the raw scanned image into a canonical metric coordinate frame (A4 at 600 DPI)
using homography derived from the 4 detected fiducial markers.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import cv2
import numpy as np

from backend.scan_validator.specs import (
    A4_WIDTH_MM,
    A4_HEIGHT_MM,
    FIDUCIAL_THEORETICAL_CENTERS_MM,
    mm_to_px,
    DEFAULT_DPI,
)


@dataclass
class RectificationResult:
    is_success: bool
    rectified_image: Optional[np.ndarray]
    transform_matrix: Optional[np.ndarray]
    target_width_px: int
    target_height_px: int
    target_dpi: int
    error_message: Optional[str] = None


def rectify_scan(
    image: np.ndarray,
    fiducial_centers: Dict[str, Tuple[float, float]],
    target_dpi: int = DEFAULT_DPI,
) -> RectificationResult:
    """
    Nắn chỉnh phối cảnh (Perspective Warp) ảnh quét đưa về canvas chuẩn A4.

    Args:
        image: Ảnh quét gốc (BGR hoặc Grayscale).
        fiducial_centers: Tọa độ 4 tâm mốc ("top_left", "top_right", "bottom_left", "bottom_right").
        target_dpi: Độ phân giải canvas chuẩn đầu ra (mặc định 600 DPI).

    Returns:
        RectificationResult chứa ảnh đã nắn thẳng và ma trận biến đổi.
    """
    if image is None or image.size == 0:
        return RectificationResult(
            is_success=False,
            rectified_image=None,
            transform_matrix=None,
            target_width_px=0,
            target_height_px=0,
            target_dpi=target_dpi,
            error_message="Cannot rectify empty image.",
        )

    required_keys = ["top_left", "top_right", "bottom_right", "bottom_left"]
    for k in required_keys:
        if k not in fiducial_centers:
            return RectificationResult(
                is_success=False,
                rectified_image=None,
                transform_matrix=None,
                target_width_px=0,
                target_height_px=0,
                target_dpi=target_dpi,
                error_message=f"Missing fiducial coordinate: '{k}'.",
            )

    # Tọa độ nguồn (Source Points từ ảnh quét)
    src_pts = np.array([
        fiducial_centers["top_left"],
        fiducial_centers["top_right"],
        fiducial_centers["bottom_right"],
        fiducial_centers["bottom_left"],
    ], dtype=np.float32)

    # Tọa độ đích lý thuyết (Destination Points trên canvas chuẩn)
    dst_tl = (
        mm_to_px(FIDUCIAL_THEORETICAL_CENTERS_MM["top_left"][0], target_dpi),
        mm_to_px(FIDUCIAL_THEORETICAL_CENTERS_MM["top_left"][1], target_dpi),
    )
    dst_tr = (
        mm_to_px(FIDUCIAL_THEORETICAL_CENTERS_MM["top_right"][0], target_dpi),
        mm_to_px(FIDUCIAL_THEORETICAL_CENTERS_MM["top_right"][1], target_dpi),
    )
    dst_br = (
        mm_to_px(FIDUCIAL_THEORETICAL_CENTERS_MM["bottom_right"][0], target_dpi),
        mm_to_px(FIDUCIAL_THEORETICAL_CENTERS_MM["bottom_right"][1], target_dpi),
    )
    dst_bl = (
        mm_to_px(FIDUCIAL_THEORETICAL_CENTERS_MM["bottom_left"][0], target_dpi),
        mm_to_px(FIDUCIAL_THEORETICAL_CENTERS_MM["bottom_left"][1], target_dpi),
    )

    dst_pts = np.array([dst_tl, dst_tr, dst_br, dst_bl], dtype=np.float32)

    # Tính ma trận Homography phối cảnh
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # Kích thước canvas A4 chuẩn
    target_w = mm_to_px(A4_WIDTH_MM, target_dpi)
    target_h = mm_to_px(A4_HEIGHT_MM, target_dpi)

    border_val = (255, 255, 255) if len(image.shape) == 3 else 255

    rectified = cv2.warpPerspective(
        image,
        M,
        (target_w, target_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_val,
    )

    return RectificationResult(
        is_success=True,
        rectified_image=rectified,
        transform_matrix=M,
        target_width_px=target_w,
        target_height_px=target_h,
        target_dpi=target_dpi,
        error_message=None,
    )
