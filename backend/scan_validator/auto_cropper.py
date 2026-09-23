"""
OmniDraw Scan-Validation Pipeline — Deterministic Auto-Cropper.

Slices the rectified canvas into individual sample specimens based on
millimeter coordinate layouts defined in specs.py.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np

from backend.scan_validator.specs import (
    get_form_specs,
    CropItemSpec,
    mm_to_px,
    DEFAULT_DPI,
)
from backend.scan_validator.qc_evaluator import evaluate_crop_qc, CropQCResult


@dataclass
class ExtractedCrop:
    sample_id: str
    prompt: str
    context_tag: str
    bbox_mm: Tuple[float, float, float, float]
    writing_bbox_mm: Tuple[float, float, float, float]
    pixel_bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    crop_image: np.ndarray
    full_cell_image: Optional[np.ndarray]
    qc_result: CropQCResult
    metadata: Dict[str, Any]


def crop_sheet(
    rectified_image: np.ndarray,
    form_type: str = "P01",
    dpi: int = DEFAULT_DPI,
    extract_full_cell: bool = True,
) -> List[ExtractedCrop]:
    """
    Tự động cắt toàn bộ các ô / dòng mẫu viết tay trên canvas đã nắn thẳng.

    Args:
        rectified_image: Ảnh canvas A4 đã được nắn chỉnh phối cảnh.
        form_type: Tên biểu mẫu ("P01", "P02", "P03", "P04").
        dpi: Độ phân giải canvas (mặc định 600 DPI).
        extract_full_cell: Nếu True, trích xuất cả ô đầy đủ (chứa dải nhãn) làm tham chiếu.

    Returns:
        Danh sách ExtractedCrop chứa ảnh cắt và metadata kiểm định QC.
    """
    if rectified_image is None or rectified_image.size == 0:
        return []

    img_h, img_w = rectified_image.shape[:2]
    specs = get_form_specs(form_type)
    crops: List[ExtractedCrop] = []

    for item in specs:
        # 1. Tọa độ vùng viết tay (Writing Zone)
        wx, wy, ww, wh = item.writing_bbox_mm
        x1 = max(0, mm_to_px(wx, dpi))
        y1 = max(0, mm_to_px(wy, dpi))
        x2 = min(img_w, mm_to_px(wx + ww, dpi))
        y2 = min(img_h, mm_to_px(wy + wh, dpi))

        writing_crop = rectified_image[y1:y2, x1:x2].copy()

        # 2. Tọa độ ô bao quát (Full Cell Bounding Box) nếu cần
        full_cell_img = None
        if extract_full_cell:
            bx, by, bw, bh = item.bbox_mm
            cx1 = max(0, mm_to_px(bx, dpi))
            cy1 = max(0, mm_to_px(by, dpi))
            cx2 = min(img_w, mm_to_px(bx + bw, dpi))
            cy2 = min(img_h, mm_to_px(by + bh, dpi))
            full_cell_img = rectified_image[cy1:cy2, cx1:cx2].copy()

        # 3. Đánh giá chất lượng quang học QC
        qc_result = evaluate_crop_qc(writing_crop, dpi=dpi)

        crops.append(ExtractedCrop(
            sample_id=item.sample_id,
            prompt=item.prompt,
            context_tag=item.context_tag,
            bbox_mm=item.bbox_mm,
            writing_bbox_mm=item.writing_bbox_mm,
            pixel_bbox=(x1, y1, x2, y2),
            crop_image=writing_crop,
            full_cell_image=full_cell_img,
            qc_result=qc_result,
            metadata=item.metadata,
        ))

    return crops
