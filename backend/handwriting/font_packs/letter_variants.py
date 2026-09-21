"""
OmniDraw - Letter Variant Sets
==============================
Định nghĩa các tập glyph biến thể theo ngữ cảnh và loại văn bản (Letter Types).
Không phải Font Pack hoàn chỉnh; hoạt động như một lớp override theo loại thư và vị trí.
"""

import numpy as np
from .geometry import bz

# -----------------------------------------------------------------------------
# Hình học nét đơn K / T / C phong cách Trang Trọng (Formal Initial Glyphs)
# -----------------------------------------------------------------------------

# K: Thân đứng với móc mở đầu thanh lịch; hai nhánh tiếp giáp thân rõ ràng, nhánh dưới vuốt nhẹ
_FORMAL_K_STEM = bz(np.array([1.4, 3.2]), np.array([2.0, 1.8]), np.array([2.8, 1.8]), np.array([2.8, 14.0]), n=12)
_FORMAL_K_ARM_UP = bz(np.array([9.2, 2.0]), np.array([7.0, 2.2]), np.array([4.5, 5.5]), np.array([2.8, 8.0]), n=10)
_FORMAL_K_ARM_DOWN = bz(np.array([3.2, 7.5]), np.array([5.2, 9.0]), np.array([7.5, 12.8]), np.array([9.6, 14.0]), n=10)
_FORMAL_K_STROKES = [_FORMAL_K_STEM, _FORMAL_K_ARM_UP, _FORMAL_K_ARM_DOWN]

# T: Nét ngang đầu uốn lượn flourish cân đối; thân chính trang trọng đứng thẳng, lượn nhẹ ở chân
_FORMAL_T_BAR = bz(np.array([1.5, 3.0]), np.array([2.2, 1.8]), np.array([8.2, 1.8]), np.array([9.5, 2.5]), n=12)
_FORMAL_T_STEM = bz(np.array([5.5, 2.0]), np.array([5.5, 9.0]), np.array([5.4, 12.8]), np.array([4.2, 14.0]), n=10)
_FORMAL_T_STROKES = [_FORMAL_T_BAR, _FORMAL_T_STEM]

# C: Cung mở mềm mại cân đối với K/T, có nét vào thanh thoát và nét thoát trang nhã
_FORMAL_C_1 = bz(np.array([8.6, 4.2]), np.array([7.5, 1.0]), np.array([3.5, 1.0]), np.array([1.8, 5.2]), n=10)
_FORMAL_C_2 = bz(np.array([1.8, 5.2]), np.array([1.2, 7.8]), np.array([1.2, 10.8]), np.array([2.5, 13.0]), n=10)
_FORMAL_C_3 = bz(np.array([2.5, 13.0]), np.array([4.0, 14.5]), np.array([7.5, 14.5]), np.array([8.8, 12.0]), n=10)
_FORMAL_C_STROKE = np.vstack([_FORMAL_C_1, _FORMAL_C_2[1:], _FORMAL_C_3[1:]])
_FORMAL_C_STROKES = [_FORMAL_C_STROKE]


LETTER_VARIANT_SETS = {
    "formal": {
        "name": "Trang trọng",
        "font_pack": "omnidraw_legacy",
        "initial_glyphs": {
            "K": {
                "strokes": _FORMAL_K_STROKES,
                "width": 10.0,
                "center": 5.5,
            },
            "T": {
                "strokes": _FORMAL_T_STROKES,
                "width": 9.8,
                "center": 5.5,
            },
            "C": {
                "strokes": _FORMAL_C_STROKES,
                "width": 9.2,
                "center": 5.0,
            },
        },
    },
}
