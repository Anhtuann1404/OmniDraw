"""
OmniDraw Scan-Validation Pipeline — Geometry & Form Specifications.

Specifies:
- Standard ISO A4 dimensions & DPI conversions.
- Canonical theoretical fiducial marker coordinates.
- Calibration block dimensions & pilot tolerances.
- Bounding box definitions for Collection Sheets P01, P02, P03, P04.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional


# ISO A4 dimensions in millimeters
A4_WIDTH_MM: float = 210.0
A4_HEIGHT_MM: float = 297.0

# Default digitization resolution
DEFAULT_DPI: int = 600
MM_PER_INCH: float = 25.4


def mm_to_px(mm: float, dpi: int = DEFAULT_DPI) -> int:
    """Chuyển đổi từ milimét sang pixels tại DPI chỉ định."""
    return int(round(mm * dpi / MM_PER_INCH))


def px_to_mm(px: float, dpi: int = DEFAULT_DPI) -> float:
    """Chuyển đổi từ pixels sang milimét tại DPI chỉ định."""
    return float(px * MM_PER_INCH / dpi)


# ==============================================================================
# 1. Mốc định vị quang học (Fiducial Markers)
# ==============================================================================
# 4 ô vuông đen đặc 5.0 x 5.0 mm tại 4 góc
FIDUCIAL_SIZE_MM: float = 5.0

# Tâm lý thuyết của 4 mốc (theo tài liệu P01..P04 notes)
# TL: (12.0 + 2.5, 12.0 + 2.5) = (14.50, 14.50)
# TR: (193.0 + 2.5, 12.0 + 2.5) = (195.50, 14.50)
# BL: (12.0 + 2.5, 280.0 + 2.5) = (14.50, 282.50)
# BR: (193.0 + 2.5, 280.0 + 2.5) = (195.50, 282.50)
FIDUCIAL_THEORETICAL_CENTERS_MM: Dict[str, Tuple[float, float]] = {
    "top_left": (14.50, 14.50),
    "top_right": (195.50, 14.50),
    "bottom_left": (14.50, 282.50),
    "bottom_right": (195.50, 282.50),
}

# Khoảng cách lý thuyết giữa các tâm mốc
THEORETICAL_DX_MM: float = 181.00
THEORETICAL_DY_MM: float = 268.00
THEORETICAL_DIAG_MM: float = 323.389857  # sqrt(181^2 + 268^2)


# ==============================================================================
# 2. Khối kiểm chuẩn đo lường (Calibration Area)
# ==============================================================================
# Vùng chứa thước đo và ô vuông: Y in [256.5, 278.5] mm
CALIBRATION_AREA_BBOX_MM: Tuple[float, float, float, float] = (13.0, 256.5, 184.0, 22.0)

# Thước đo 50.0 mm: từ X=22.0 đến X=72.0 mm tại Y=270.0 mm
RULER_50MM_X1_MM: float = 22.0
RULER_50MM_X2_MM: float = 72.0
RULER_50MM_Y_MM: float = 270.0
RULER_THEORETICAL_LENGTH_MM: float = 50.0
RULER_TOLERANCE_MM: float = 0.20  # Dung sai kiểm chuẩn: 50.0 ± 0.2 mm

# Ô vuông kiểm chuẩn 20.0 x 20.0 mm tại X=125.0, Y=257.5 mm
SQUARE_20MM_X_MM: float = 125.0
SQUARE_20MM_Y_MM: float = 257.5
SQUARE_20MM_SIZE_MM: float = 20.0
SQUARE_ASPECT_RATIO_TARGET: float = 1.000
SQUARE_ASPECT_RATIO_TOLERANCE: float = 0.005  # Dung sai tỷ lệ cạnh: 1.000 ± 0.005
SQUARE_SIZE_TOLERANCE_MM: float = 0.80        # Dung sai kích thước bao ngoài viền in (mm)


# ==============================================================================
# 3. Đặc tả Bounding Box cho từng Form (P01, P02, P03, P04)
# ==============================================================================

@dataclass
class CropItemSpec:
    sample_id: str
    prompt: str
    context_tag: str
    bbox_mm: Tuple[float, float, float, float]           # (x, y, w, h) bao quát toàn ô
    writing_bbox_mm: Tuple[float, float, float, float]   # (x, y, w, h) vùng viết tay thực tế
    metadata: Dict[str, Any] = field(default_factory=dict)


def get_p01_specs() -> List[CropItemSpec]:
    """
    Trả về danh sách 24 ô mẫu cho biểu mẫu P01 (Isolated Characters & Diacritics).
    4 cột x 6 hàng, col_w=43.5, row_h=31.0, col_gap=3.333, row_gap=3.0, start=(13.0, 53.5).
    """
    cells_data = [
        # Row 1
        {"id": "BASE_001", "target": "a", "tag": "BASE_CHARACTER"},
        {"id": "BASE_002", "target": "e", "tag": "BASE_CHARACTER"},
        {"id": "BASE_003", "target": "o", "tag": "BASE_CHARACTER"},
        {"id": "BASE_004", "target": "u", "tag": "BASE_CHARACTER"},
        # Row 2
        {"id": "STR_001",  "target": "ă", "tag": "STRUCTURAL_DIACRITIC"},
        {"id": "STR_002",  "target": "â", "tag": "STRUCTURAL_DIACRITIC"},
        {"id": "STR_003",  "target": "ê", "tag": "STRUCTURAL_DIACRITIC"},
        {"id": "STR_004",  "target": "ơ", "tag": "STRUCTURAL_DIACRITIC"},
        # Row 3
        {"id": "TONE_001", "target": "á", "tag": "TONE_DIACRITIC"},
        {"id": "TONE_002", "target": "à", "tag": "TONE_DIACRITIC"},
        {"id": "TONE_003", "target": "ả", "tag": "TONE_DIACRITIC"},
        {"id": "TONE_004", "target": "ạ", "tag": "TONE_DIACRITIC"},
        # Row 4
        {"id": "SEC_001",  "target": "đ", "tag": "SECONDARY_STROKE"},
        {"id": "STR_005",  "target": "ư", "tag": "STRUCTURAL_DIACRITIC"},
        {"id": "BASE_005", "target": "n", "tag": "BASE_CHARACTER"},
        {"id": "BASE_006", "target": "m", "tag": "BASE_CHARACTER"},
        # Row 5
        {"id": "CMP_001",  "target": "ắ", "tag": "COMPLEX_STACKED_DIACRITIC"},
        {"id": "CMP_002",  "target": "ấ", "tag": "COMPLEX_STACKED_DIACRITIC"},
        {"id": "CMP_003",  "target": "ố", "tag": "COMPLEX_STACKED_DIACRITIC"},
        {"id": "CMP_004",  "target": "ở", "tag": "COMPLEX_STACKED_DIACRITIC"},
        # Row 6
        {"id": "REP_001",  "target": "ế", "tag": "INTRA_WRITER_TRIAL_A"},
        {"id": "REP_002",  "target": "ế", "tag": "INTRA_WRITER_TRIAL_B"},
        {"id": "REP_003",  "target": "ử", "tag": "INTRA_WRITER_TRIAL_A"},
        {"id": "REP_004",  "target": "ử", "tag": "INTRA_WRITER_TRIAL_B"},
    ]

    col_w = 43.50
    col_gap = 3.333333
    row_h = 31.00
    row_gap = 3.00
    start_x = 13.00
    start_y = 53.50
    label_h = 6.50
    writing_h = row_h - label_h  # 24.50 mm

    specs = []
    for idx, c in enumerate(cells_data):
        row = idx // 4
        col = idx % 4
        cx = start_x + col * (col_w + col_gap)
        cy = start_y + row * (row_h + row_gap)
        bbox = (round(cx, 2), round(cy, 2), col_w, row_h)
        writing_bbox = (round(cx, 2), round(cy + label_h, 2), col_w, writing_h)
        specs.append(CropItemSpec(
            sample_id=c["id"],
            prompt=c["target"],
            context_tag=c["tag"],
            bbox_mm=bbox,
            writing_bbox_mm=writing_bbox,
            metadata={"row": row, "col": col}
        ))
    return specs


def get_p02_specs() -> List[CropItemSpec]:
    """
    Trả về danh sách 16 dòng mẫu cho biểu mẫu P02 (Context & Ligatures).
    Section A (4 dòng), Section B (6 dòng), Section C (6 dòng).
    """
    sections = [
        # Section A
        {"id": "CTX_INIT_001", "prompt": "Kính gửi", "tag": "WORD_INITIAL"},
        {"id": "CTX_INIT_002", "prompt": "Thân gửi", "tag": "WORD_INITIAL"},
        {"id": "CTX_INIT_003", "prompt": "Cảm ơn", "tag": "WORD_INITIAL"},
        {"id": "CTX_INIT_004", "prompt": "Chào mừng", "tag": "WORD_INITIAL"},
        # Section B
        {"id": "CTX_MED_001",   "prompt": "thuyền",  "tag": "WORD_MEDIAL_LIGATURE"},
        {"id": "CTX_MED_002",   "prompt": "nghiêng", "tag": "WORD_MEDIAL_LIGATURE"},
        {"id": "CTX_MED_003_A", "prompt": "trường",  "tag": "LIGATURE_TRIAL_A"},
        {"id": "CTX_MED_003_B", "prompt": "trường",  "tag": "LIGATURE_TRIAL_B"},
        {"id": "CTX_MED_004_A", "prompt": "nguyễn",  "tag": "LIGATURE_TRIAL_A"},
        {"id": "CTX_MED_004_B", "prompt": "nguyễn",  "tag": "LIGATURE_TRIAL_B"},
        # Section C
        {"id": "CTX_FINAL_001", "prompt": "bạn",  "tag": "WORD_FINAL"},
        {"id": "CTX_FINAL_002", "prompt": "nam",  "tag": "WORD_FINAL"},
        {"id": "CTX_FINAL_003", "prompt": "nhìn", "tag": "WORD_FINAL"},
        {"id": "CTX_FINAL_004", "prompt": "tình", "tag": "WORD_FINAL"},
        {"id": "CTX_FINAL_005", "prompt": "mộc",  "tag": "WORD_FINAL"},
        {"id": "CTX_FINAL_006", "prompt": "hoa",  "tag": "WORD_FINAL"},
    ]

    current_y = 46.0
    sec_header_h = 3.5
    gap_after_sec = 0.8
    row_w = 184.0
    row_h = 11.6
    label_h = 3.5
    writing_h = row_h - label_h
    row_gap = 0.5
    sec_gap = 1.8
    start_x = 13.0

    counts = [4, 6, 6]
    specs = []
    item_idx = 0
    for count in counts:
        current_y += sec_header_h + gap_after_sec
        for _ in range(count):
            item = sections[item_idx]
            bbox = (round(start_x, 2), round(current_y, 2), row_w, row_h)
            writing_bbox = (round(start_x, 2), round(current_y + label_h, 2), row_w, writing_h)
            specs.append(CropItemSpec(
                sample_id=item["id"],
                prompt=item["prompt"],
                context_tag=item["tag"],
                bbox_mm=bbox,
                writing_bbox_mm=writing_bbox,
            ))
            current_y += row_h + row_gap
            item_idx += 1
        current_y += sec_gap - row_gap
    return specs


def get_p03_specs() -> List[CropItemSpec]:
    """
    Trả về danh sách 3 khối câu cho biểu mẫu P03 (Sentence Flow & Pangrams).
    """
    sentences = [
        {"id": "SENT_001", "prompt": "Do bạch kim rất quý nên qua thời gian phong thổ vẫn giữ màu sáng rực rỡ."},
        {"id": "SENT_002", "prompt": "Cậu bé xinh đẹp này phóng vèo qua dãy phố cổ mù sương."},
        {"id": "SENT_003", "prompt": "Hoàng tử nhảy múa cùng các cô gái vùng biển xanh biếc."}
    ]
    current_y = 48.0
    block_w = 184.0
    block_h = 58.0
    prompt_h = 12.0
    writing_h = 46.0
    block_gap = 8.0
    start_x = 13.0

    specs = []
    for idx, s in enumerate(sentences):
        by = current_y + idx * (block_h + block_gap)
        bbox = (round(start_x, 2), round(by, 2), block_w, block_h)
        writing_bbox = (round(start_x, 2), round(by + prompt_h, 2), block_w, writing_h)
        specs.append(CropItemSpec(
            sample_id=s["id"],
            prompt=s["prompt"],
            context_tag="PANGRAM_SENTENCE",
            bbox_mm=bbox,
            writing_bbox_mm=writing_bbox,
        ))
    return specs


def get_p04_specs() -> List[CropItemSpec]:
    """
    Trả về đặc tả khối đoạn văn cho biểu mẫu P04 (Natural Paragraph).
    """
    prompt = "Mỗi dòng chữ nắn nót trên trang giấy trắng là nhịp cầu nối liền những tấm lòng thân thương, gửi gắm trọn vẹn niềm tin cùng bao ước vọng tốt đẹp nhất."
    block_x = 13.0
    block_y = 48.0
    block_w = 184.0
    prompt_h = 30.0
    wz_h = 150.0
    block_h = prompt_h + wz_h

    bbox = (block_x, block_y, block_w, block_h)
    writing_bbox = (block_x, block_y + prompt_h, block_w, wz_h)
    return [
        CropItemSpec(
            sample_id="PARA_001",
            prompt=prompt,
            context_tag="NATURAL_PARAGRAPH",
            bbox_mm=bbox,
            writing_bbox_mm=writing_bbox,
        )
    ]


def get_form_specs(form_type: str) -> List[CropItemSpec]:
    """Lấy danh mục CropItemSpec theo tên biểu mẫu P01, P02, P03, P04."""
    f = form_type.upper().strip()
    if f in ("P01", "P1"):
        return get_p01_specs()
    elif f in ("P02", "P2"):
        return get_p02_specs()
    elif f in ("P03", "P3"):
        return get_p03_specs()
    elif f in ("P04", "P4"):
        return get_p04_specs()
    raise ValueError(f"Unsupported collection sheet form: {form_type}. Choose from P01, P02, P03, P04.")
