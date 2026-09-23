"""
OmniDraw Scan-Validation Pipeline — Quality Control & Boundary Overflow Evaluator.

Evaluates extracted writing specimens:
1. Ink stroke detection & presence check.
2. Background cleanliness and noise statistics.
3. Boundary overflow detection (ink crossing cell borders or label strips).
4. Assigns QC status: QC_PASS, QC_FLAGGED, QC_EMPTY, or QC_REJECTED.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import cv2
import numpy as np

from backend.scan_validator.specs import mm_to_px, DEFAULT_DPI


@dataclass
class CropQCResult:
    qc_status: str               # "QC_PASS", "QC_FLAGGED", "QC_EMPTY", "QC_REJECTED"
    has_ink: bool
    ink_ratio_percent: float
    background_mean: float
    background_std: float
    overflow_detected: bool
    overflow_details: Dict[str, Any]
    warnings: List[str]
    is_valid_for_dataset: bool


def evaluate_crop_qc(
    crop_image: np.ndarray,
    dpi: int = DEFAULT_DPI,
    border_margin_mm: float = 1.0,
    dark_threshold: int = 125,
) -> CropQCResult:
    """
    Đánh giá chất lượng quang học của một ô mẫu viết tay đã cắt.

    Args:
        crop_image: Ảnh ô viết tay (BGR hoặc Grayscale).
        dpi: Độ phân giải ảnh (mặc định 600 DPI).
        border_margin_mm: Bề dày vùng biên kiểm tra tràn nét (mặc định 1.0 mm).
        dark_threshold: Ngưỡng độ sáng coi là nét mực viết (mặc định < 125).

    Returns:
        CropQCResult chứa các chỉ số kiểm định và cờ QC.
    """
    if crop_image is None or crop_image.size == 0:
        return CropQCResult(
            qc_status="QC_REJECTED",
            has_ink=False,
            ink_ratio_percent=0.0,
            background_mean=0.0,
            background_std=0.0,
            overflow_detected=False,
            overflow_details={},
            warnings=["Crop image is empty."],
            is_valid_for_dataset=False,
        )

    if len(crop_image.shape) == 3:
        gray = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = crop_image

    h, w = gray.shape
    total_pixels = h * w
    warnings = []

    # 1. Phát hiện nét mực đen
    ink_mask = gray < dark_threshold
    ink_pixel_count = int(np.sum(ink_mask))
    ink_ratio = (ink_pixel_count / total_pixels) * 100.0

    # Phân tích nền giấy
    bg_pixels = gray[gray >= dark_threshold]
    if len(bg_pixels) > 0:
        bg_mean = float(np.mean(bg_pixels))
        bg_std = float(np.std(bg_pixels))
    else:
        bg_mean = 0.0
        bg_std = 0.0

    # 2. Kiểm tra ô trống (Writer bỏ qua không viết)
    # Nếu tỷ lệ nét mực < 0.04% (ít hơn vài chục pixel nhiễu)
    if ink_ratio < 0.04:
        return CropQCResult(
            qc_status="QC_EMPTY",
            has_ink=False,
            ink_ratio_percent=round(ink_ratio, 4),
            background_mean=round(bg_mean, 2),
            background_std=round(bg_std, 2),
            overflow_detected=False,
            overflow_details={"top": 0, "bottom": 0, "left": 0, "right": 0},
            warnings=["No handwriting detected in sample cell."],
            is_valid_for_dataset=False,
        )

    # 3. Kiểm tra tràn viền (Boundary Overflow Check)
    margin_px = max(1, mm_to_px(border_margin_mm, dpi))
    # Đảm bảo margin không vượt quá nửa kích thước ô
    margin_px = min(margin_px, h // 6, w // 6)

    # Đếm số pixel mực trong dải biên 4 cạnh
    top_band = ink_mask[0:margin_px, :]
    bot_band = ink_mask[h - margin_px:h, :]
    left_band = ink_mask[:, 0:margin_px]
    right_band = ink_mask[:, w - margin_px:w]

    overflow_top = int(np.sum(top_band))
    overflow_bot = int(np.sum(bot_band))
    overflow_left = int(np.sum(left_band))
    overflow_right = int(np.sum(right_band))

    # Ngưỡng pixel tràn coi là vi phạm (vượt quá nhiễu điểm nhỏ ngẫu nhiên)
    overflow_pixel_threshold = max(8, int(margin_px * 0.4))
    has_top_overflow = overflow_top > overflow_pixel_threshold
    has_bot_overflow = overflow_bot > overflow_pixel_threshold
    has_left_overflow = overflow_left > overflow_pixel_threshold
    has_right_overflow = overflow_right > overflow_pixel_threshold

    overflow_detected = has_top_overflow or has_bot_overflow or has_left_overflow or has_right_overflow

    overflow_details = {
        "top": overflow_top,
        "bottom": overflow_bot,
        "left": overflow_left,
        "right": overflow_right,
        "has_top_overflow": has_top_overflow,
        "has_bot_overflow": has_bot_overflow,
        "has_left_overflow": has_left_overflow,
        "has_right_overflow": has_right_overflow,
    }

    if has_top_overflow:
        warnings.append("Strokes overflow into upper label strip.")
    if has_bot_overflow:
        warnings.append("Strokes overflow across bottom boundary.")
    if has_left_overflow or has_right_overflow:
        warnings.append("Strokes overflow across lateral cell borders.")

    # 4. Kiểm tra độ sạch nền
    if bg_mean < 210.0:
        warnings.append("Background paper brightness is low (potential scanner shadow or dirty paper).")
    if bg_std > 30.0:
        warnings.append("Background paper noise variance is high.")

    # 5. Phán quyết trạng thái QC
    if overflow_detected:
        # Nếu chỉ chạm nhẹ 1 phía -> QC_FLAGGED (vẫn có thể kiểm tra thủ công)
        # Nếu tràn nhiều phía (>2 phía) -> QC_REJECTED
        num_sides = sum([has_top_overflow, has_bot_overflow, has_left_overflow, has_right_overflow])
        if num_sides >= 2:
            qc_status = "QC_REJECTED"
            is_valid = False
        else:
            qc_status = "QC_FLAGGED"
            is_valid = True  # Cho phép giữ lại kèm cờ cảnh báo
    elif bg_mean < 200.0:
        qc_status = "QC_FLAGGED"
        is_valid = True
    else:
        qc_status = "QC_PASS"
        is_valid = True

    return CropQCResult(
        qc_status=qc_status,
        has_ink=True,
        ink_ratio_percent=round(ink_ratio, 4),
        background_mean=round(bg_mean, 2),
        background_std=round(bg_std, 2),
        overflow_detected=overflow_detected,
        overflow_details=overflow_details,
        warnings=warnings,
        is_valid_for_dataset=is_valid,
    )
