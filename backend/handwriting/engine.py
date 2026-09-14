"""
OmniDraw - Module Viết Thư Tay Tự Động (Bio-Inspired Vietnamese Handwriting Engine)
==================================================================================
Tạo nét bút đơn (Single-Stroke Vector Centerline) cho chữ viết tay Tiếng Việt:
- Giải quyết bài toán Outline Font: không bị viền đôi như font TTF thông thường.
- Hỗ trợ toàn bộ ký tự Tiếng Việt có dấu nhờ tách âm vị NFD (Modular Accent Compositing).
- Thuật toán biến thiên sinh học (Bio-mimetic Variation):
  + Baseline drift: lượn sóng tự nhiên trục Y.
  + Slant variation: độ ngả nghiêng tự nhiên của nét chữ.
  + Micro-jitter: độ run vi mô của tay người.
- 4 phong cách: Học sinh, Thảo nghiêng, Thư pháp, Ký tên nhanh.
"""

import math
import random
import sys
import unicodedata
import numpy as np

if __package__:
    from .font_packs import FONT_PACKS, LETTER_VARIANT_SETS
    from .font_packs.geometry import (
        bz,
        make_oval,
        make_hook_stem,
        make_ascender_loop,
        make_descender_loop,
        make_arch,
    )
    from .font_packs.legacy import (
        GLYPHS,
        GLYPH_WIDTHS,
        GLYPH_CENTERS,
        DEFAULT_WIDTH,
        DEFAULT_CENTER,
    )
    from .font_packs.omni_casual import (
        OMNI_CASUAL_V1_PUNCTUATION,
        OMNI_CASUAL_CUSTOM_CHARS,
        OMNI_CASUAL_GLYPHS,
        OMNI_CASUAL_WIDTHS,
        OMNI_CASUAL_CENTERS,
    )
else:
    import os
    _cur_dir = os.path.dirname(os.path.abspath(__file__))
    _parent_dir = os.path.dirname(_cur_dir)
    if _parent_dir not in sys.path:
        sys.path.insert(0, _parent_dir)
    try:
        from handwriting.font_packs import FONT_PACKS, LETTER_VARIANT_SETS
        from handwriting.font_packs.geometry import (
            bz,
            make_oval,
            make_hook_stem,
            make_ascender_loop,
            make_descender_loop,
            make_arch,
        )
        from handwriting.font_packs.legacy import (
            GLYPHS,
            GLYPH_WIDTHS,
            GLYPH_CENTERS,
            DEFAULT_WIDTH,
            DEFAULT_CENTER,
        )
        from handwriting.font_packs.omni_casual import (
            OMNI_CASUAL_V1_PUNCTUATION,
            OMNI_CASUAL_CUSTOM_CHARS,
            OMNI_CASUAL_GLYPHS,
            OMNI_CASUAL_WIDTHS,
            OMNI_CASUAL_CENTERS,
        )
    except ImportError:
        from backend.handwriting.font_packs import FONT_PACKS, LETTER_VARIANT_SETS
        from backend.handwriting.font_packs.geometry import (
            bz,
            make_oval,
            make_hook_stem,
            make_ascender_loop,
            make_descender_loop,
            make_arch,
        )
        from backend.handwriting.font_packs.legacy import (
            GLYPHS,
            GLYPH_WIDTHS,
            GLYPH_CENTERS,
            DEFAULT_WIDTH,
            DEFAULT_CENTER,
        )
        from backend.handwriting.font_packs.omni_casual import (
            OMNI_CASUAL_V1_PUNCTUATION,
            OMNI_CASUAL_CUSTOM_CHARS,
            OMNI_CASUAL_GLYPHS,
            OMNI_CASUAL_WIDTHS,
            OMNI_CASUAL_CENTERS,
        )

class TextOverflowError(ValueError):
    """Nội dung thư tay không thể đặt trọn vẹn trong một trang."""


class UnsupportedCharacterError(ValueError):
    """Nội dung chứa ký tự chưa có glyph trong Font Pack đang chọn."""

    def __init__(self, characters):
        self.characters = tuple(characters)
        labels = ", ".join(
            f"{char!r} (U+{ord(char):04X})"
            for char in self.characters
        )
        super().__init__(f"Các ký tự chưa được font hỗ trợ: {labels}.")


class UnsupportedLetterTypeError(ValueError):
    """Loại văn bản / thư (letter_type) không được hỗ trợ hoặc không tương thích font pack."""
    pass


SUPPORTED_COMBINING_MARKS = frozenset({
    "\u0302",  # mũ
    "\u0306",  # trăng
    "\u031b",  # móc
    "\u0301",  # sắc
    "\u0300",  # huyền
    "\u0309",  # hỏi
    "\u0303",  # ngã
    "\u0323",  # nặng
})


def find_unsupported_characters(text, glyphs):
    """
    Kiểm tra nội dung văn bản sau chuẩn hóa NFD và trả về danh sách các ký tự
    chưa có glyph hoặc combining mark không được hỗ trợ.
    Giữ thứ tự xuất hiện đầu tiên và không lặp lại.
    """
    unsupported = []
    seen = set()

    def record(ch):
        if ch not in seen:
            seen.add(ch)
            unsupported.append(ch)

    decomposed = unicodedata.normalize("NFD", text)
    has_base = False

    for ch in decomposed:
        if ch in (" ", "\n"):
            has_base = False
            continue

        if unicodedata.combining(ch):
            if ch not in SUPPORTED_COMBINING_MARKS or not has_base:
                record(ch)
        else:
            b_char = "d" if ch == "đ" else ("D" if ch == "Đ" else ch)
            if b_char in glyphs:
                has_base = True
            else:
                has_base = False
                record(ch)

    return unsupported


# Dấu gạch ngang đ / Đ chuẩn vị trí cắt qua giữa thân sổ
STROKE_D_BAR = np.array([[5.2, 4.2], [8.8, 4.2]])
STROKE_CAP_D_BAR = np.array([[0.2, 7.5], [4.2, 7.5]])


# ----------------------------- Bộ Sinh Dấu Theo Quy Tắc Hình Học -----------------------------

def generate_accents(base_char, accents, cx, dot_below_x_offset=None):
    """
    Sinh các nét dấu Tiếng Việt (Single-stroke Accents) căn chỉnh tự động:
    - Bố trí dấu thanh và dấu định dạng theo quy tắc tách tầng để giảm nguy cơ va chạm.
      Độ an toàn hình học được hậu kiểm bằng audit_vietnamese_lowercase_accents(); đây không phải bảo đảm tuyệt đối cho mọi đầu vào.
    - Căn giữa chính xác theo trọng tâm nguyên âm cx.
    - Hỗ trợ cả chữ hoa (tự nâng chiều cao) và chữ thường.
    - Kích thước nhỏ gọn, thanh thoát, vừa vặn tự nhiên với chữ (fit với chữ).
    """
    strokes = []
    is_upper = base_char.isupper()
    # Nâng độ cao dấu nếu là chữ hoa (cap-height = 2 so với x-height = 7)
    y_shift = -5.0 if is_upper else 0.0

    has_non = '\u0302' in accents    # nón â, ê, ô
    has_trang = '\u0306' in accents  # trăng ă
    has_moc = '\u031b' in accents    # móc ơ, ư
    has_stacked_base = has_non or has_trang

    # 1. Dấu định dạng nguyên âm (nón, trăng, móc)
    if has_non:
        # Nón thanh thoát nhỏ gọn (rộng 3.2, cao 2.1), cách đỉnh chữ 2.4 đơn vị
        non_stroke = np.array([[cx - 1.6, 4.6 + y_shift], [cx, 2.5 + y_shift], [cx + 1.6, 4.6 + y_shift]])
        strokes.append(non_stroke)

    if has_trang:
        # Trăng uốn cong tròn lòng máng mềm mại (rộng 3.2, cao 1.3)
        trang_stroke = bz(np.array([cx - 1.6, 2.8 + y_shift]), np.array([cx - 0.9, 4.6 + y_shift]),
                          np.array([cx + 0.9, 4.6 + y_shift]), np.array([cx + 1.6, 2.8 + y_shift]), n=6)
        strokes.append(trang_stroke)

    if has_moc:
        # Móc cong tròn mềm mại chuẩn tiểu học gắn góc trên bên phải của o hoặc u
        m1 = bz(np.array([cx + 1.8, 7.0 + y_shift]), np.array([cx + 2.7, 6.4 + y_shift]),
                np.array([cx + 3.1, 5.2 + y_shift]), np.array([cx + 2.8, 4.5 + y_shift]), n=6)
        m2 = bz(np.array([cx + 2.8, 4.5 + y_shift]), np.array([cx + 2.6, 4.0 + y_shift]),
                np.array([cx + 2.0, 4.1 + y_shift]), np.array([cx + 1.9, 4.7 + y_shift]), n=6)
        strokes.append(np.vstack([m1, m2[1:]]))

    # 2. Dấu thanh điệu (sắc, huyền, hỏi, ngã, nặng)
    for acc in accents:
        if acc == '\u0323':
            # Dấu nặng: chấm tròn rõ ràng dưới baseline (y=14)
            default_dot_offset = 2.2 if base_char in ("y", "Y") else 0.0
            effective_dot_offset = (
                default_dot_offset
                if dot_below_x_offset is None
                else float(dot_below_x_offset)
            )
            cx_dot = cx + effective_dot_offset
            strokes.append(make_oval(cx=cx_dot, top_y=15.2, bot_y=16.3, rx=0.55, n=6))

        elif acc == '\u0301':
            # Dấu sắc: nét xiên sắc nét, rõ ràng
            if has_stacked_base:
                # Nằm chếch trên sườn phải của mũ nón/trăng
                s = np.array([[cx + 0.7, 2.4 + y_shift], [cx + 2.2, 0.2 + y_shift]])
            elif has_moc:
                s = np.array([[cx - 1.8, 4.8 + y_shift], [cx + 0.8, 2.0 + y_shift]])
            else:
                s = np.array([[cx - 1.2, 4.8 + y_shift], [cx + 1.4, 2.0 + y_shift]])
            strokes.append(s)

        elif acc == '\u0300':
            # Dấu huyền: nét xiên lượn nhẹ tự nhiên, rõ ràng
            if has_stacked_base:
                # Nằm chếch trên sườn trái của mũ nón/trăng
                s = np.array([[cx - 0.7, 2.4 + y_shift], [cx - 2.2, 0.2 + y_shift]])
            elif has_moc:
                s = bz(np.array([cx - 2.0, 2.0 + y_shift]), np.array([cx - 0.9, 3.2 + y_shift]),
                       np.array([cx - 0.1, 4.1 + y_shift]), np.array([cx + 0.6, 4.8 + y_shift]), n=6)
            else:
                s = bz(np.array([cx - 1.4, 2.0 + y_shift]), np.array([cx - 0.3, 3.2 + y_shift]),
                       np.array([cx + 0.5, 4.1 + y_shift]), np.array([cx + 1.2, 4.8 + y_shift]), n=6)
            strokes.append(s)

        elif acc == '\u0309':
            # Dấu hỏi: uốn móc cong mềm mại, to rõ ràng từ trên xuống dưới
            if has_stacked_base:
                # Trên mũ nón/trăng: đặt trên đỉnh mũ
                h1 = bz(np.array([cx - 0.6, 0.8 + y_shift]),
                        np.array([cx - 0.6, 0.0 + y_shift]),
                        np.array([cx + 0.1, -0.2 + y_shift]),
                        np.array([cx + 0.6, 0.5 + y_shift]), n=6)
                h2 = bz(np.array([cx + 0.6, 0.5 + y_shift]),
                        np.array([cx + 0.7, 1.2 + y_shift]),
                        np.array([cx + 0.1, 1.7 + y_shift]),
                        np.array([cx - 0.3, 2.2 + y_shift]), n=6)
                s = np.vstack([h1, h2[1:]])
            elif has_moc:
                # Trên ơ, ư: chếch sang bên trái tâm để nhường chỗ cho móc sườn phải
                cx_h = cx - 0.9
                h1 = bz(np.array([cx_h - 0.7, 2.8 + y_shift]),
                        np.array([cx_h - 0.7, 1.7 + y_shift]),
                        np.array([cx_h + 0.1, 1.6 + y_shift]),
                        np.array([cx_h + 0.7, 2.5 + y_shift]), n=6)
                h2 = bz(np.array([cx_h + 0.7, 2.5 + y_shift]),
                        np.array([cx_h + 0.8, 3.4 + y_shift]),
                        np.array([cx_h + 0.1, 4.0 + y_shift]),
                        np.array([cx_h - 0.4, 4.8 + y_shift]), n=6)
                s = np.vstack([h1, h2[1:]])
            else:
                # Đứng một mình trên nguyên âm (ả, ẻ, ỉ, ỏ, ủ, ỷ)
                h1 = bz(np.array([cx - 0.8, 2.8 + y_shift]),
                        np.array([cx - 0.8, 1.6 + y_shift]),
                        np.array([cx + 0.1, 1.5 + y_shift]),
                        np.array([cx + 0.8, 2.4 + y_shift]), n=6)
                h2 = bz(np.array([cx + 0.8, 2.4 + y_shift]),
                        np.array([cx + 0.9, 3.3 + y_shift]),
                        np.array([cx + 0.2, 4.0 + y_shift]),
                        np.array([cx - 0.4, 4.8 + y_shift]), n=6)
                s = np.vstack([h1, h2[1:]])
            strokes.append(s)

        elif acc == '\u0303':
            # Dấu ngã: lượn sóng rõ ràng, to vừa vặn
            if has_stacked_base:
                s = bz(np.array([cx - 1.5, 1.4 + y_shift]), np.array([cx - 0.6, 0.1 + y_shift]),
                       np.array([cx + 0.6, 2.0 + y_shift]), np.array([cx + 1.5, 0.8 + y_shift]), n=8)
            elif has_moc:
                s = bz(np.array([cx - 2.4, 4.0 + y_shift]), np.array([cx - 1.4, 2.4 + y_shift]),
                       np.array([cx - 0.1, 4.6 + y_shift]), np.array([cx + 0.8, 3.0 + y_shift]), n=8)
            else:
                s = bz(np.array([cx - 1.7, 4.0 + y_shift]), np.array([cx - 0.7, 2.4 + y_shift]),
                       np.array([cx + 0.7, 4.6 + y_shift]), np.array([cx + 1.7, 3.0 + y_shift]), n=8)
            strokes.append(s)

    return strokes


# ----------------------------- Bộ Tối Ưu Quỹ Đạo Nét Chữ Bằng Quy Hoạch Động (DAG DP Engine) -----------------------------

# Phân loại điểm đón nét (Entry) và thoát nét (Exit) theo giải phẫu học chữ viết tay người
ENTRY_TYPES = {
    'i': 'mid', 'u': 'mid', 'm': 'mid', 'n': 'mid', 't': 'mid',
    'p': 'mid', 'r': 'baseline', 's': 'baseline', 'v': 'mid', 'w': 'mid', 'y': 'mid',
    'e': 'mid',
    'a': 'oval', 'd': 'oval', 'g': 'oval', 'o': 'oval', 'q': 'oval', 'c': 'oval',
    'b': 'ascender', 'h': 'ascender', 'k': 'ascender', 'l': 'ascender',
    'x': 'none', 'z': 'none', 'f': 'none'
}

EXIT_TYPES = {
    'a': 'baseline_hook', 'c': 'baseline_hook', 'd': 'baseline_hook',
    'e': 'baseline_hook', 'h': 'baseline_hook', 'i': 'baseline_hook',
    'k': 'baseline_hook', 'l': 'baseline_hook', 'm': 'baseline_hook',
    'n': 'baseline_hook', 't': 'baseline_hook', 'u': 'baseline_hook',
    'p': 'baseline_hook', 'r': 'baseline_hook', 's': 'baseline_hook',
    'b': 'top_flick', 'o': 'top_flick', 'v': 'top_flick', 'w': 'top_flick',
    'g': 'descender_loop', 'y': 'descender_loop',
    'q': 'none', 'x': 'baseline_hook', 'z': 'none', 'f': 'none'
}


class GlyphVariant:
    """Biến thể hình học (Alloglyph Node) trong đồ thị DAG."""
    __slots__ = ('strokes', 'entry_pt', 'exit_pt', 'v_entry', 'v_exit', 'can_in', 'can_out', 'cost_legibility', 'tag')

    def __init__(self, strokes, entry_pt, exit_pt, v_entry, v_exit, can_in, can_out, cost_legibility=0.0, tag="std"):
        self.strokes = strokes
        self.entry_pt = np.asarray(entry_pt, dtype=float)
        self.exit_pt = np.asarray(exit_pt, dtype=float)
        self.v_entry = np.asarray(v_entry, dtype=float)
        self.v_exit = np.asarray(v_exit, dtype=float)
        self.can_in = can_in
        self.can_out = can_out
        self.cost_legibility = cost_legibility
        self.tag = tag


def split_glyph_strokes(base_char, strokes):
    """
    Tách nét chính (primary_strokes) và nét phụ (secondary_strokes) của glyph:
    - i, j: nét đầu là thân chữ (primary); nét sau là dấu chấm (secondary).
    - t, f: nét đầu là thân chữ (primary); nét sau là gạch ngang (secondary).
    - Các glyph còn lại: giữ nguyên toàn bộ stroke theo thứ tự hiện tại (primary).
    """
    if not strokes:
        return [], []
    if base_char in ('i', 'j', 't', 'f') and len(strokes) > 1:
        return [strokes[0]], list(strokes[1:])
    return list(strokes), []


def get_glyph_variants(base_char, raw_strokes):
    """
    Sinh 1-3 biến thể hình học cho ký tự trên đồ thị DAG:
    - std: Nét chuẩn canonical
    - mid_in / high_out: Nét đón/thoát ở midline y=7.0 để nối mượt
    - isolated: Nét ngắt độc lập, chủ động nhấc bút
    """
    prim_strokes, sec_strokes = split_glyph_strokes(base_char, raw_strokes)

    if not (base_char.isalpha() and base_char.islower()) or not prim_strokes or len(prim_strokes[0]) < 2:
        s_first = prim_strokes[0] if prim_strokes else (raw_strokes[0] if raw_strokes else np.array([[0.0, 0.0], [1.0, 0.0]]))
        s_last = prim_strokes[-1] if prim_strokes else s_first
        v_in = s_first[1] - s_first[0] if len(s_first) >= 2 else np.array([1.0, 0.0])
        v_out = s_last[-1] - s_last[-2] if len(s_last) >= 2 else np.array([1.0, 0.0])
        return [GlyphVariant(list(raw_strokes), s_first[0], s_last[-1], v_in, v_out, False, False, 0.0, "std")]

    prim_first = prim_strokes[0]
    prim_last = prim_strokes[-1]
    p_in = prim_first[0]
    p_out = prim_last[-1]

    v_in = prim_first[1] - prim_first[0]
    v_in = v_in / (np.linalg.norm(v_in) + 1e-6)

    v_out = prim_last[-1] - prim_last[-2] if len(prim_last) >= 2 else np.array([1.0, 0.0])
    v_out = v_out / (np.linalg.norm(v_out) + 1e-6)

    en_type = ENTRY_TYPES.get(base_char, 'none')
    ex_type = EXIT_TYPES.get(base_char, 'none')

    can_in = en_type in ('mid', 'baseline')
    can_out = ex_type != 'none'

    v0 = GlyphVariant(list(raw_strokes), p_in, p_out, v_in, v_out, can_in, can_out, 0.0, "std")
    variants = [v0]

    # Biến thể 1: Đón hoặc thoát ở midline
    if en_type == 'mid':
        lead_in = bz(np.array([p_in[0] - 1.2, 7.0]), np.array([p_in[0] - 0.4, 7.0]),
                     np.array([p_in[0], p_in[1] - 0.5]), p_in, n=5)
        new_prim_first = np.vstack([lead_in[:-1], prim_first])
        new_prim_strokes = [new_prim_first] + list(prim_strokes[1:])
        v1_strokes = new_prim_strokes + list(sec_strokes)
        v_in_mid = lead_in[1] - lead_in[0]
        v_in_mid = v_in_mid / (np.linalg.norm(v_in_mid) + 1e-6)
        v1 = GlyphVariant(v1_strokes, lead_in[0], p_out, v_in_mid, v_out, True, can_out, 0.05, "mid_in")
        variants.append(v1)
    elif ex_type == 'baseline_hook':
        lead_out = bz(p_out, p_out + np.array([0.5, -1.0]),
                      p_out + np.array([1.0, -2.5]), p_out + np.array([1.2, -3.2]), n=5)
        new_prim_last = np.vstack([prim_last, lead_out[1:]])
        new_prim_strokes = list(prim_strokes[:-1]) + [new_prim_last]
        v1_strokes = new_prim_strokes + list(sec_strokes)
        v_out_high = lead_out[-1] - lead_out[-2]
        v_out_high = v_out_high / (np.linalg.norm(v_out_high) + 1e-6)
        v1 = GlyphVariant(v1_strokes, p_in, lead_out[-1], v_in, v_out_high, can_in, True, 0.05, "high_out")
        variants.append(v1)
    elif base_char in ('o', 'b', 'v', 'w'):
        v1 = GlyphVariant(list(raw_strokes), p_in, p_out, v_in, v_out, can_in, False, 0.02, "closed")
        variants.append(v1)

    # Biến thể 2: Biến thể cô lập nhấc bút
    v2 = GlyphVariant(list(raw_strokes), p_in, p_out, v_in, v_out, False, False, 0.02, "isolated")
    variants.append(v2)
    return variants


def build_ligature_bridge(p_exit, v_exit, p_entry, v_entry, scale_hint=1.0, n=6):
    """
    Sinh các điểm nội suy đường cong Bézier bậc 3 cho cầu nối (ligature bridge) giữa 2 ký tự:
    - Nhận tọa độ và tangent trong world coordinates.
    - Chuẩn hóa tangent an toàn (tránh chia cho 0 hoặc NaN).
    - Tạo hai control point c1, c2 theo cùng công thức hình học chuẩn.
    - Trả về mảng (n, 2) các điểm Bézier từ p_exit đến p_entry.
    """
    p_ex = np.asarray(p_exit, dtype=float)
    p_en = np.asarray(p_entry, dtype=float)
    v_ex = np.asarray(v_exit, dtype=float)
    v_en = np.asarray(v_entry, dtype=float)

    norm_ex = float(np.linalg.norm(v_ex))
    if norm_ex < 1e-6 or np.isnan(norm_ex):
        v_ex_norm = np.array([1.0, 0.0])
    else:
        v_ex_norm = v_ex / norm_ex

    norm_en = float(np.linalg.norm(v_en))
    if norm_en < 1e-6 or np.isnan(norm_en):
        v_en_norm = np.array([1.0, 0.0])
    else:
        v_en_norm = v_en / norm_en

    dist = float(np.linalg.norm(p_en - p_ex))
    s_hint = float(scale_hint) if scale_hint is not None and scale_hint > 0 else 1.0
    factor = min(0.6 * s_hint, dist * 0.35)

    c1 = p_ex + v_ex_norm * factor
    c2 = p_en - v_en_norm * factor
    return bz(p_ex, c1, c2, p_en, n=n)


def point_to_segment_distance(p, a, b):
    """
    Tính khoảng cách Euclide ngắn nhất từ điểm p đến đoạn thẳng nối từ a đến b.
    """
    p = np.asarray(p, dtype=float)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    ab = b - a
    l2 = float(np.dot(ab, ab))
    if l2 < 1e-12:
        return float(np.linalg.norm(p - a))
    t = max(0.0, min(1.0, float(np.dot(p - a, ab)) / l2))
    proj = a + t * ab
    return float(np.linalg.norm(p - proj))


def point_on_segment(p, a, b, eps=1e-6):
    """Kiểm tra điểm p có nằm trên đoạn thẳng [a, b] trong hệ tọa độ 2D (khi p, a, b cùng phương)."""
    return (
        min(a[0], b[0]) - eps <= p[0] <= max(a[0], b[0]) + eps and
        min(a[1], b[1]) - eps <= p[1] <= max(a[1], b[1]) + eps
    )


def segments_intersect(p1, p2, q1, q2, eps=1e-6):
    """
    Kiểm tra giao nhau giữa 2 đoạn thẳng [p1, p2] và [q1, q2] bền vững:
    - Sử dụng tích có hướng 2D (orientation/cross product) với dung sai epsilon.
    - Kiểm tra point_on_segment cho các trường hợp mút và cùng phương.
    - Xử lý đúng general intersection, collinear overlapping, và tiếp xúc đầu mút.
    - Xử lý an toàn các đoạn suy biến (degenerate segments).
    """
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    q1 = np.asarray(q1, dtype=float)
    q2 = np.asarray(q2, dtype=float)

    len_p = float(np.linalg.norm(p2 - p1))
    len_q = float(np.linalg.norm(q2 - q1))

    # Xử lý đoạn suy biến (chiều dài gần 0)
    if len_p <= eps and len_q <= eps:
        return float(np.linalg.norm(p1 - q1)) <= eps
    if len_p <= eps:
        cross_q = (q2[0] - q1[0]) * (p1[1] - q1[1]) - (q2[1] - q1[1]) * (p1[0] - q1[0])
        return abs(cross_q) <= eps * max(1.0, len_q) and point_on_segment(p1, q1, q2, eps)
    if len_q <= eps:
        cross_p = (p2[0] - p1[0]) * (q1[1] - p1[1]) - (p2[1] - p1[1]) * (q1[0] - p1[0])
        return abs(cross_p) <= eps * max(1.0, len_p) and point_on_segment(q1, p1, p2, eps)

    def _cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    cp1 = _cross(p1, p2, q1)
    cp2 = _cross(p1, p2, q2)
    cq1 = _cross(q1, q2, p1)
    cq2 = _cross(q1, q2, p2)

    tol_p = eps * max(1.0, len_p)
    tol_q = eps * max(1.0, len_q)

    o1 = 0 if abs(cp1) <= tol_p else (1 if cp1 > 0 else -1)
    o2 = 0 if abs(cp2) <= tol_p else (1 if cp2 > 0 else -1)
    o3 = 0 if abs(cq1) <= tol_q else (1 if cq1 > 0 else -1)
    o4 = 0 if abs(cq2) <= tol_q else (1 if cq2 > 0 else -1)

    # Cắt nhau thông thường (straddle hai phía)
    if o1 != o2 and o3 != o4 and o1 != 0 and o2 != 0 and o3 != 0 and o4 != 0:
        return True

    # Trường hợp mút nằm trên đoạn hoặc collinear chồng lấn
    if o1 == 0 and point_on_segment(q1, p1, p2, eps):
        return True
    if o2 == 0 and point_on_segment(q2, p1, p2, eps):
        return True
    if o3 == 0 and point_on_segment(p1, q1, q2, eps):
        return True
    if o4 == 0 and point_on_segment(p2, q1, q2, eps):
        return True

    return False


_segments_cross = segments_intersect


def bridge_collision_cost(bridge, prev_strokes=None, curr_strokes=None, scale_hint=1.0):
    """
    Sampled-polyline / segment-distance heuristic:
    Tính chi phí va chạm hình học giữa candidate bridge và các nét chính (primary strokes) lân cận.
    Lưu ý: Đây là heuristic hình học dựa trên mẫu đoạn thẳng thực tế, không phải bộ kiểm tra va chạm tuyệt đối 100% (CAD ray-casting).
    """
    if bridge is None or len(bridge) < 2:
        return 0.0
    p_exit = bridge[0]
    p_entry = bridge[-1]
    s_hint = float(scale_hint) if scale_hint is not None and scale_hint > 0 else 1.0
    clearance = 0.2 * s_hint
    anchor_zone = 0.35 * s_hint

    # Lấy mẫu các điểm phân bố đều trên thân cầu nối (loại trừ mút p_exit và p_entry)
    sample_pts = []
    for k in range(len(bridge) - 1):
        mid = 0.5 * (bridge[k] + bridge[k + 1])
        sample_pts.append(mid)
        if k < len(bridge) - 2:
            sample_pts.append(bridge[k + 1])

    all_segments = []
    if prev_strokes:
        for s in prev_strokes:
            s_arr = np.asarray(s, dtype=float)
            if len(s_arr) >= 2:
                for k in range(len(s_arr) - 1):
                    all_segments.append((s_arr[k], s_arr[k + 1]))
    if curr_strokes:
        for s in curr_strokes:
            s_arr = np.asarray(s, dtype=float)
            if len(s_arr) >= 2:
                for k in range(len(s_arr) - 1):
                    all_segments.append((s_arr[k], s_arr[k + 1]))

    if not all_segments:
        return 0.0

    max_penetration = 0.0

    # 1. Kiểm tra cắt trực tiếp qua các đoạn của bridge bằng segments_intersect
    for k in range(len(bridge) - 1):
        br_seg_a = bridge[k]
        br_seg_b = bridge[k + 1]
        for seg_a, seg_b in all_segments:
            # Kiểm tra tiếp xúc hợp lệ tại mút nối p_exit hoặc p_entry
            shares_exit = (np.allclose(br_seg_a, p_exit, atol=1e-4) or np.allclose(br_seg_b, p_exit, atol=1e-4)) and \
                          (np.allclose(seg_a, p_exit, atol=1e-4) or np.allclose(seg_b, p_exit, atol=1e-4))
            shares_entry = (np.allclose(br_seg_a, p_entry, atol=1e-4) or np.allclose(br_seg_b, p_entry, atol=1e-4)) and \
                           (np.allclose(seg_a, p_entry, atol=1e-4) or np.allclose(seg_b, p_entry, atol=1e-4))

            if shares_exit:
                # Điểm chung là p_exit. Chỉ phạt nếu 2 đoạn cùng hướng vẽ đè lên nhau (collinear overlap)
                P = br_seg_b if np.allclose(br_seg_a, p_exit, atol=1e-4) else br_seg_a
                Q = seg_b if np.allclose(seg_a, p_exit, atol=1e-4) else seg_a
                u = P - p_exit
                v = Q - p_exit
                norm_u = float(np.linalg.norm(u))
                norm_v = float(np.linalg.norm(v))
                if norm_u > 1e-6 and norm_v > 1e-6:
                    cos_val = float(np.dot(u, v)) / (norm_u * norm_v)
                    if cos_val > 0.999:
                        max_penetration = 1.0
                        break
                continue

            if shares_entry:
                # Điểm chung là p_entry. Chỉ phạt nếu 2 đoạn cùng hướng vẽ đè lên nhau
                P = br_seg_a if np.allclose(br_seg_b, p_entry, atol=1e-4) else br_seg_b
                Q = seg_a if np.allclose(seg_b, p_entry, atol=1e-4) else seg_b
                u = P - p_entry
                v = Q - p_entry
                norm_u = float(np.linalg.norm(u))
                norm_v = float(np.linalg.norm(v))
                if norm_u > 1e-6 and norm_v > 1e-6:
                    cos_val = float(np.dot(u, v)) / (norm_u * norm_v)
                    if cos_val > 0.999:
                        max_penetration = 1.0
                        break
                continue

            if segments_intersect(br_seg_a, br_seg_b, seg_a, seg_b):
                max_penetration = 1.0
                break
        if max_penetration >= 1.0:
            break

    # 2. Kiểm tra khoảng cách tối thiểu (clearance) từ các điểm mẫu
    if max_penetration < 1.0:
        for pt in sample_pts:
            d_to_exit = float(np.linalg.norm(pt - p_exit))
            d_to_entry = float(np.linalg.norm(pt - p_entry))
            for seg_a, seg_b in all_segments:
                is_exit_seg = np.allclose(seg_b, p_exit, atol=1e-4) or np.allclose(seg_a, p_exit, atol=1e-4)
                is_entry_seg = np.allclose(seg_a, p_entry, atol=1e-4) or np.allclose(seg_b, p_entry, atol=1e-4)
                if is_exit_seg and d_to_exit < anchor_zone:
                    continue
                if is_entry_seg and d_to_entry < anchor_zone:
                    continue
                dist = point_to_segment_distance(pt, seg_a, seg_b)
                if dist < clearance:
                    pen = (clearance - dist) / clearance
                    if pen > max_penetration:
                        max_penetration = pen

    if max_penetration > 0.0:
        return 2.0 + 4.0 * max_penetration
    return 0.0


def eval_transition(u, w, p_exit, p_entry, weights=(0.5, 4.0, 2.0, 15.0, 1.0),
                    v_exit_world=None, v_entry_world=None,
                    prev_strokes_world=None, curr_strokes_world=None,
                    scale_hint=1.0):
    """
    Tính chi phí chuyển trạng thái giữa 2 node theo hàm mục tiêu:
    J = w1*D_penup + w2*N_lift + w3*C_curvature + w4*C_collision + w5*C_legibility
    """
    w1, w2, w3, w4, w5 = weights
    dist = float(np.linalg.norm(p_entry - p_exit))
    dx = p_entry[0] - p_exit[0]

    cost_lift = w1 * dist + w2 * 1.0 + w5 * w.cost_legibility

    if not (u.can_out and w.can_in and dx > -0.2 and dist < 12.0):
        return cost_lift, False

    # Tangent trong hệ tọa độ thực (World coordinates) đã được scale và normalize
    v_ex = v_exit_world if v_exit_world is not None else u.v_exit
    v_en = v_entry_world if v_entry_world is not None else w.v_entry

    d_vec = p_entry - p_exit
    d_norm = float(np.linalg.norm(d_vec))
    if d_norm > 1e-4:
        u_d = d_vec / d_norm
        cos1 = float(np.clip(np.dot(v_ex, u_d), -1.0, 1.0))
        cos2 = float(np.clip(np.dot(u_d, v_en), -1.0, 1.0))
        c_curvature = (1.0 - cos1) + (1.0 - cos2)
    else:
        c_curvature = 0.0

    # Dựng candidate bridge để kiểm tra hình học nhất quán với renderer
    candidate_br = build_ligature_bridge(p_exit, v_ex, p_entry, v_en, scale_hint=scale_hint, n=6)

    # Heuristic kiểm tra va chạm hình học (sampled-polyline / segment-distance)
    c_collision = 0.0
    if dx <= 0.0:
        c_collision += 2.0
    if dist > 8.0:
        c_collision += (dist - 8.0) * 0.4
    c_collision += bridge_collision_cost(
        candidate_br, prev_strokes_world, curr_strokes_world, scale_hint=scale_hint
    )

    cost_conn = w1 * 0.0 + w2 * 0.0 + w3 * c_curvature + w4 * c_collision + w5 * w.cost_legibility
    if cost_conn < cost_lift:
        return cost_conn, True
    return cost_lift, False


def optimize_word_dag(char_info_list, weights=(0.5, 4.0, 2.0, 15.0, 1.0), force_lift=False):
    """
    Quy hoạch động Viterbi DP trên đồ thị có hướng (DAG), độ phức tạp O(n * k^2).
    Tìm đường đi có chi phí J nhỏ nhất qua các biến thể ký tự.
    """
    n = len(char_info_list)
    if n == 0:
        return {"variants": [], "conns": []}

    variants_per_char = [get_glyph_variants(item["char"], item["raw_s"]) for item in char_info_list]

    if force_lift or n == 1:
        return {
            "variants": [vars_i[0] for vars_i in variants_per_char],
            "conns": [False] * (n - 1)
        }

    # Tiền xử lý nét chính (primary strokes) trong hệ tọa độ thực (World space) cho từng biến thể
    world_prim_per_char = []
    for item, vars_i in zip(char_info_list, variants_per_char):
        char_prim_vars = []
        for var in vars_i:
            prim, _ = split_glyph_strokes(item["char"], var.strokes)
            scaled_prim = [s.astype(float) * item["scale_vec"] + item["offset"] for s in prim]
            char_prim_vars.append(scaled_prim)
        world_prim_per_char.append(char_prim_vars)

    dp = [{} for _ in range(n)]
    bp = [{} for _ in range(n)]
    conn = [{} for _ in range(n)]

    for j, v in enumerate(variants_per_char[0]):
        dp[0][j] = weights[4] * v.cost_legibility

    for i in range(1, n):
        prev_item = char_info_list[i - 1]
        prev_vars = variants_per_char[i - 1]
        curr_item = char_info_list[i]
        curr_vars = variants_per_char[i]
        scale_hint = float(np.mean(prev_item["scale_vec"]))

        for j, curr_v in enumerate(curr_vars):
            p_entry = curr_v.entry_pt * curr_item["scale_vec"] + curr_item["offset"]
            v_en_world = curr_v.v_entry * curr_item["scale_vec"]
            v_en_world = v_en_world / (np.linalg.norm(v_en_world) + 1e-6)
            curr_prim_w = world_prim_per_char[i][j]
            best_cost = float('inf')
            best_p = 0
            best_is_conn = False

            for p, prev_v in enumerate(prev_vars):
                p_exit = prev_v.exit_pt * prev_item["scale_vec"] + prev_item["offset"]
                v_ex_world = prev_v.v_exit * prev_item["scale_vec"]
                v_ex_world = v_ex_world / (np.linalg.norm(v_ex_world) + 1e-6)
                prev_prim_w = world_prim_per_char[i - 1][p]
                cost_trans, is_conn = eval_transition(
                    prev_v, curr_v, p_exit, p_entry, weights,
                    v_exit_world=v_ex_world, v_entry_world=v_en_world,
                    prev_strokes_world=prev_prim_w, curr_strokes_world=curr_prim_w,
                    scale_hint=scale_hint
                )
                total = dp[i - 1][p] + cost_trans
                if total < best_cost:
                    best_cost = total
                    best_p = p
                    best_is_conn = is_conn

            dp[i][j] = best_cost
            bp[i][j] = best_p
            conn[i][j] = best_is_conn

    best_j = min(dp[n - 1].keys(), key=lambda j: dp[n - 1][j])
    chosen_var_indices = [best_j]
    chosen_conns = []
    curr_j = best_j
    for i in range(n - 1, 0, -1):
        chosen_conns.append(conn[i][curr_j])
        curr_j = bp[i][curr_j]
        chosen_var_indices.append(curr_j)

    chosen_var_indices.reverse()
    chosen_conns.reverse()

    chosen_vars = [variants_per_char[i][chosen_var_indices[i]] for i in range(n)]
    return {"variants": chosen_vars, "conns": chosen_conns}


def can_ligature(prev_char, curr_char):
    """Fallback tương thích ngược."""
    ex = EXIT_TYPES.get(prev_char, 'none')
    en = ENTRY_TYPES.get(curr_char, 'none')
    return ex != 'none' and en in ('mid', 'baseline')


# ----------------------------- Cấu Hình Phong Cách & Font -----------------------------

STYLE_CONFIGS = {
    "hand_hocsinh": {
        "name": "Chữ Học Sinh",
        "slant": 0.0,          # nét đứng nắn nót
        "jitter_amp": 0.015,    # rung tay sinh học rất mịn, nét tròn trịa
        "drift_amp": 0.12,      # lượn dòng rất ít
        "char_spacing": 1.0,
    },
    "hand_nguoilon": {
        "name": "Chữ Thảo Nghiêng",
        "slant": 0.20,         # nghiêng ~11 độ tự nhiên
        "jitter_amp": 0.035,    # rung tay vừa phải, mượt mà
        "drift_amp": 0.25,      # dòng lượn sóng nhẹ
        "char_spacing": 1.0,
    },
    "hand_thuphap": {
        "name": "Chữ Thư Pháp",
        "slant": 0.15,
        "jitter_amp": 0.045,    # nét phóng khoáng
        "drift_amp": 0.35,      # lượn sóng bổng trầm
        "char_spacing": 1.1,
    },
    "hand_chukinhanh": {
        "name": "Chữ Ký Tên",
        "slant": 0.32,         # nghiêng mạnh ~18 độ
        "jitter_amp": 0.060,
        "drift_amp": 0.20,
        "char_spacing": 0.95,
    },
}

RENDER_PROFILES = {
    "oly": {
        "font_pack": "omnidraw_legacy",
        "aspect_y": 1.0,
        "slant_add": 0.0,
        "thanhdam": False,
        "ligature": False,
        "flourish": False,
    },
    "thanhdam": {
        "font_pack": "omnidraw_legacy",
        "aspect_y": 1.04,
        "slant_add": 0.08,
        "thanhdam": True,      # Nhân đôi nét sổ mô phỏng ngòi bút mài lá tre
        "ligature": False,
        "flourish": False,
    },
    "thuphap": {
        "font_pack": "omnidraw_legacy",
        "aspect_y": 1.25,      # Kéo dài trục Y thanh thoát
        "slant_add": 0.05,
        "thanhdam": True,
        "flourish": True,      # Móc vát đuôi thư pháp
        "ligature": False,
    },
    "cursive": {
        "font_pack": "omnidraw_legacy",
        "aspect_y": 0.96,
        "slant_add": 0.15,     # Nghiêng thêm kiểu chữ thảo
        "thanhdam": False,
        "ligature": True,      # Nối nét liền mạch 0 pen lift trong từ
        "flourish": False,
    },
    "omni_casual": {
        "font_pack": "omni_casual",
        "aspect_y": 0.98,
        "slant_add": 0.03,
        "thanhdam": False,
        "ligature": False,
        "flourish": False,
    },
}

# Compatibility alias for earlier versions
FONT_CONFIGS = RENDER_PROFILES


def resolve_font(font_id):
    """
    Phân giải font_id thành (font_pack, render_profile).
    Không fallback ngầm cho font không tồn tại hoặc 'custom'.
    """
    if not isinstance(font_id, str):
        raise ValueError(f"Font ID không hợp lệ: {font_id}")
    if font_id not in RENDER_PROFILES:
        raise ValueError(f"Font '{font_id}' không được hỗ trợ. Các font khả dụng: {list(RENDER_PROFILES.keys())}")
    profile = RENDER_PROFILES[font_id]
    pack_id = profile.get("font_pack")
    if pack_id not in FONT_PACKS:
        raise ValueError(f"Font pack '{pack_id}' cho font '{font_id}' không tồn tại trong FONT_PACKS")
    pack = FONT_PACKS[pack_id]
    return pack, profile


LETTER_TYPES = {"general", "formal"}


def resolve_letter_type(letter_type, font_pack_id):
    """
    Xác thực letter_type và kiểm tra tính tương thích với font_pack_id.
    - 'general': luôn hợp lệ với mọi font pack.
    - 'formal': chỉ hợp lệ với font pack 'omnidraw_legacy'.
    Không fallback ngầm cho letter_type không hợp lệ.
    """
    if not isinstance(letter_type, str) or letter_type not in LETTER_TYPES:
        raise UnsupportedLetterTypeError(
            f"Loại thư '{letter_type}' không được hỗ trợ. Các loại thư hợp lệ: {sorted(LETTER_TYPES)}."
        )
    if letter_type == "formal":
        target_pack = LETTER_VARIANT_SETS["formal"].get("font_pack", "omnidraw_legacy")
        if font_pack_id != target_pack:
            raise UnsupportedLetterTypeError(
                f"Loại thư 'formal' chỉ hỗ trợ với Font Pack '{target_pack}', không hỗ trợ Font Pack '{font_pack_id}'."
            )
        return LETTER_VARIANT_SETS["formal"]
    return None


def select_contextual_glyph(
    base_char,
    font_pack,
    font_pack_id,
    letter_type,
    is_document_initial,
):
    """
    Chọn nét hình học, độ rộng và tâm của glyph theo ngữ cảnh tài liệu và loại thư.
    Trả về: (strokes, width, center, variant_tag)
    """
    glyphs = font_pack["glyphs"]
    widths = font_pack["widths"]
    centers = font_pack["centers"]
    default_width = font_pack.get("default_width", DEFAULT_WIDTH)
    default_center = font_pack.get("default_center", DEFAULT_CENTER)

    if (
        letter_type == "formal"
        and font_pack_id == "omnidraw_legacy"
        and is_document_initial
        and base_char in ("K", "T", "C")
    ):
        v_info = LETTER_VARIANT_SETS["formal"]["initial_glyphs"][base_char]
        return (
            [s.copy() for s in v_info["strokes"]],
            v_info["width"],
            v_info["center"],
            "formal_initial",
        )

    return (
        glyphs[base_char],
        widths.get(base_char, default_width),
        centers.get(base_char, default_center),
        "base",
    )


def apply_bio_variation(
    stroke,
    slant=0.0,
    jitter_amp=0.0,
    drift_y=0.0,
    rng=None,
):
    """
    Áp dụng các lớp biến dạng sinh học (Bio-mimetic Variation):
    1. Slant affine shear: x' = x + (baseline - y) * slant
    2. Baseline drift: y' = y + drift_y
    3. Micro-jitter: Nhiễu rung cơ học tự nhiên lọc thông thấp (ARMA), loại bỏ hoàn toàn răng cưa/gãy nét
    """
    out = stroke.copy().astype(float)
    if slant != 0.0:
        # Nghiêng về phía trước quanh trục baseline (y=14)
        out[:, 0] += (14.0 - out[:, 1]) * slant
    out[:, 1] += drift_y
    if jitter_amp > 0 and len(out) > 1:
        random_source = rng if rng is not None else np.random
        raw_noise = random_source.normal(0, jitter_amp, out.shape)
        # Bộ lọc làm mịn chuyển động bàn tay (Autoregressive low-pass filter)
        smooth_noise = np.zeros_like(raw_noise)
        smooth_noise[0] = raw_noise[0]
        alpha = 0.35
        for i in range(1, len(out)):
            smooth_noise[i] = smooth_noise[i - 1] * (1.0 - alpha) + raw_noise[i] * alpha
        out += smooth_noise
    return out


def text_to_strokes(text, font="oly", style="hand_hocsinh", font_size_mm=7.0, line_spacing_mm=13.0,
                    paper_size_mm=(210.0, 297.0), margin_mm=20.0, seed=None, letter_type="general"):
    """
    Biến đổi văn bản tiếng Việt thành mảng các nét vẽ mm (List of ndarray (N, 2)).
    Hỗ trợ xuống dòng tự động, căn lề, proportional kerning, nối nét cursive và chống dính dấu.
    """
    cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS["hand_hocsinh"])
    font_pack, f_cfg = resolve_font(font)
    font_pack_id = f_cfg.get("font_pack", "omnidraw_legacy")
    resolve_letter_type(letter_type, font_pack_id)

    glyphs = font_pack["glyphs"]
    widths = font_pack["widths"]
    centers = font_pack["centers"]
    default_width = font_pack.get("default_width", DEFAULT_WIDTH)
    default_center = font_pack.get("default_center", DEFAULT_CENTER)
    dot_below_x_offsets = font_pack.get("dot_below_x_offsets", {})

    unsupported_chars = find_unsupported_characters(text, glyphs)
    if unsupported_chars:
        raise UnsupportedCharacterError(unsupported_chars)

    if seed is not None:
        if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
            raise ValueError("Seed phải là số nguyên trong khoảng 0..4294967295.")
        if not 0 <= int(seed) <= 0xFFFFFFFF:
            raise ValueError("Seed phải là số nguyên trong khoảng 0..4294967295.")
        rng = np.random.default_rng(int(seed))
    else:
        rng = np.random

    slant = cfg["slant"] + f_cfg["slant_add"]
    jitter = cfg["jitter_amp"] * (font_size_mm / 7.0)
    drift_max = cfg["drift_amp"] * (font_size_mm / 7.0)

    paper_w, paper_h = paper_size_mm
    scale = font_size_mm / 14.0
    scale_y = scale * f_cfg["aspect_y"]
    space_w = 4.8 * scale * cfg["char_spacing"]

    strokes = []
    curr_x = margin_mm
    curr_y = margin_mm + font_size_mm
    rendered_char_count = 0

    words = text.split(" ")
    word_idx = 0

    for word in words:
        if word == "":
            curr_x += space_w
            continue

        # Xử lý ký tự xuống dòng thủ công \n trong từ
        sub_words = word.split("\n")
        for sub_i, sub_w in enumerate(sub_words):
            if sub_i > 0:
                curr_x = margin_mm
                curr_y += line_spacing_mm
                if curr_y > paper_h - margin_mm:
                    raise TextOverflowError(
                        "Nội dung thư quá dài để đặt trong một trang với cỡ chữ và giãn dòng hiện tại."
                    )

            # Chuẩn hóa NFD để bóc tách dấu thanh tiếng Việt
            decomposed = unicodedata.normalize('NFD', sub_w)
            char_queue = []
            current_group = []
            for ch in decomposed:
                if unicodedata.combining(ch):
                    current_group.append(ch)
                else:
                    if current_group:
                        char_queue.append(current_group)
                    current_group = [ch]
            if current_group:
                char_queue.append(current_group)

            # Kiểm tra tràn dòng (Word wrap) theo kích thước proportional
            est_w = sum(widths.get(g[0], default_width) for g in char_queue) * scale * cfg["char_spacing"]
            if curr_x + est_w > paper_w - margin_mm and curr_x > margin_mm:
                curr_x = margin_mm
                curr_y += line_spacing_mm
                if curr_y > paper_h - margin_mm:
                    raise TextOverflowError(
                        "Nội dung thư quá dài để đặt trong một trang với cỡ chữ và giãn dòng hiện tại."
                    )

            # Lượn sóng dòng kẻ (Baseline drift)
            drift_y = math.sin(curr_x * 0.05 + word_idx * 0.4) * drift_max

            # Chuẩn bị danh sách ký tự trong từ để tối ưu hóa đồ thị DAG
            char_info_list = []
            tmp_x = curr_x
            for char_idx, group in enumerate(char_queue):
                b_char = group[0]
                is_d = False
                if b_char == 'đ':
                    b_char = 'd'
                    is_d = True
                elif b_char == 'Đ':
                    b_char = 'D'
                    is_d = True

                char_rhythm = 1.0 + 0.02 * math.sin(word_idx * 1.7 + char_idx * 2.3)
                c_scale_x = scale * char_rhythm * cfg["char_spacing"]

                is_document_initial = (rendered_char_count == 0)
                raw_s, glyph_w, cx, _variant_tag = select_contextual_glyph(
                    b_char,
                    font_pack,
                    font_pack_id,
                    letter_type,
                    is_document_initial,
                )
                w_char = glyph_w * c_scale_x
                rendered_char_count += 1

                char_info_list.append({
                    "char": b_char,
                    "accents": group[1:],
                    "is_d_stroke": is_d,
                    "raw_s": raw_s,
                    "scale_vec": np.array([c_scale_x, scale_y]),
                    "offset": np.array([tmp_x, curr_y - 14.0 * scale]),
                    "w_char": w_char,
                    "cx": cx,
                })
                tmp_x += w_char

            # Quy hoạch động Viterbi DP trên DAG tìm chuỗi biến thể và nét nối tối ưu
            enable_lig = f_cfg.get("ligature", False)
            # ponytail: w2=0 when font disables ligature to force pen-lift without changing DP structure
            weights = (0.5, 4.0 if enable_lig else 0.0, 2.0, 15.0, 1.0)
            dp_sol = optimize_word_dag(char_info_list, weights=weights, force_lift=(not enable_lig))

            word_base_strokes = []
            word_secondary_strokes = []

            for char_idx, info in enumerate(char_info_list):
                var = dp_sol["variants"][char_idx]
                scaled_s = [s.astype(float) * info["scale_vec"] + info["offset"] for s in var.strokes]
                b_char = info["char"]

                # Tách nét chính và nét phụ dùng helper split_glyph_strokes
                prim_strokes, sec_strokes = split_glyph_strokes(b_char, scaled_s)
                if b_char in ('i', 'j'):
                    if len(info["accents"]) == 0:
                        word_secondary_strokes.extend(sec_strokes)
                else:
                    word_secondary_strokes.extend(sec_strokes)

                # Ghép nét nối liên tục (Ligature) theo quyết định tối ưu của DP
                if char_idx > 0 and dp_sol["conns"][char_idx - 1] and len(word_base_strokes) > 0:
                    p_exit = word_base_strokes[-1][-1]
                    p_entry = prim_strokes[0][0]
                    prev_info = char_info_list[char_idx - 1]
                    prev_var = dp_sol["variants"][char_idx - 1]
                    scale_hint = float(np.mean(prev_info["scale_vec"]))
                    v_ex_world = prev_var.v_exit * prev_info["scale_vec"]
                    v_ex_world = v_ex_world / (np.linalg.norm(v_ex_world) + 1e-6)
                    v_en_world = var.v_entry * info["scale_vec"]
                    v_en_world = v_en_world / (np.linalg.norm(v_en_world) + 1e-6)

                    bridge = build_ligature_bridge(
                        p_exit, v_ex_world, p_entry, v_en_world, scale_hint=scale_hint, n=6
                    )
                    merged = np.vstack([word_base_strokes[-1], bridge[1:-1], prim_strokes[0]])
                    word_base_strokes[-1] = merged
                    if len(prim_strokes) > 1:
                        word_base_strokes.extend(prim_strokes[1:])
                else:
                    word_base_strokes.extend(prim_strokes)

                # Nét thanh đậm (thanhdam)
                if f_cfg["thanhdam"]:
                    p_first = prim_strokes[0]
                    if len(p_first) >= 2 and (p_first[-1, 1] - p_first[0, 1] > 1.2 * scale):
                        offset_s = p_first.copy().astype(float)
                        offset_s[:, 0] += 0.22
                        word_secondary_strokes.append(offset_s)

                # Nét thư pháp móc đuôi chữ cuối từ
                if f_cfg["flourish"] and char_idx == len(char_info_list) - 1:
                    last_pt = prim_strokes[-1][-1]
                    hook = np.array([last_pt, last_pt + np.array([0.7 * scale, -1.4 * scale])])
                    word_secondary_strokes.append(hook)

                # Gạch ngang đ/Đ
                if info["is_d_stroke"]:
                    d_bar = STROKE_D_BAR if b_char == 'd' else STROKE_CAP_D_BAR
                    bar_scaled = d_bar.astype(float) * info["scale_vec"]
                    word_secondary_strokes.append(bar_scaled + info["offset"])

                # Sinh và đặt dấu theo quy tắc hình học
                if info["accents"]:
                    acc_list = generate_accents(
                        b_char,
                        info["accents"],
                        info["cx"],
                        dot_below_x_offset=dot_below_x_offsets.get(b_char),
                    )
                    for acc_s in acc_list:
                        acc_scaled = acc_s.astype(float) * info["scale_vec"]
                        acc_placed = acc_scaled + info["offset"]
                        word_secondary_strokes.append(acc_placed)

            curr_x = tmp_x

            # Gom nét từ và áp dụng biến thiên sinh học (Bio-mimetic Variation)
            rendered_word_strokes = []
            for s in word_base_strokes:
                rendered_word_strokes.append(apply_bio_variation(s, slant=slant, jitter_amp=jitter, drift_y=drift_y, rng=rng))
            for s in word_secondary_strokes:
                rendered_word_strokes.append(apply_bio_variation(s, slant=slant, jitter_amp=jitter, drift_y=drift_y, rng=rng))

            if rendered_word_strokes:
                word_points = np.concatenate(rendered_word_strokes, axis=0)
                if not np.isfinite(word_points).all():
                    raise ValueError("Tọa độ nét vẽ chứa giá trị không hữu hạn (NaN hoặc Inf).")
                if (
                    word_points[:, 0].min() < 0.0
                    or word_points[:, 0].max() > paper_w
                    or word_points[:, 1].min() < 0.0
                    or word_points[:, 1].max() > paper_h
                ):
                    raise TextOverflowError(
                        "Nội dung thư quá dài để đặt trong một trang với cỡ chữ và giãn dòng hiện tại."
                    )
                strokes.extend(rendered_word_strokes)

            # Khoảng cách giữa các từ
            curr_x += space_w * rng.uniform(0.95, 1.05)
            word_idx += 1

    return strokes


def generate_handwriting_svg(text, font="oly", style="hand_hocsinh", target_paper_size_mm=(210.0, 297.0),
                             font_size_mm=7.0, line_spacing_mm=13.0, skew_angle_deg=0.0, seed=None,
                             letter_type="general"):
    """
    Sinh file SVG chữ viết tay hoàn chỉnh, chạy qua bộ tối ưu hóa path_optimizer
    (Catmull-Rom Bézier smoothing, Auto-deskew).
    Giữ thứ tự viết tự nhiên từ trái sang phải, từ trên xuống dưới.
    """
    try:
        from path_optimizer import build_svg, compute_svg_metrics
    except ImportError:
        from backend.path_optimizer import build_svg, compute_svg_metrics

    strokes = text_to_strokes(
        text, font=font, style=style, font_size_mm=font_size_mm,
        line_spacing_mm=line_spacing_mm, paper_size_mm=target_paper_size_mm,
        seed=seed, letter_type=letter_type,
    )

    if not strokes:
        strokes = [np.array([[20.0, 20.0], [21.0, 20.0]])]

    # Giữ nguyên thứ tự viết tự nhiên (Natural Reading Order) theo từng từ
    # Tránh 2-Opt TSP đảo chiều nét bút hoặc nhảy lộn xộn giữa các từ
    order = list(range(len(strokes)))
    rev = [False] * len(strokes)

    # Xuất SVG với Catmull-Rom to Cubic Bézier smoothing mượt mà
    scale = 1.0
    offset = (0.0, 0.0)
    svg_content, is_within_bounds = build_svg(
        strokes, order, rev, scale, offset, target_paper_size_mm,
        stroke_width_mm=0.35, smooth=True, skew_angle_deg=skew_angle_deg
    )

    metrics = compute_svg_metrics(strokes, order, rev, scale=1.0, optimize_time_ms=1.0, skew_angle_deg=skew_angle_deg)
    return svg_content, metrics, is_within_bounds


# ----------------------------- Glyph Geometry Auditor -----------------------------

def audit_font_pack_geometry(
    font_pack,
    chars,
    overlap_tolerance=0.12,
    min_overlap_length=0.35,
    max_segment_length=4.0,
):
    """
    Kiểm tra hình học glyph dành cho máy vẽ plotter (Geometry Auditor):
    Phát hiện sớm đoạn suy biến, bước nhảy bất thường, nét tô chồng và glyph vượt khung.
    Chỉ kiểm tra và báo lỗi; tuyệt đối không tự động sửa hình học glyph.
    """
    findings = []
    sin_3deg = np.sin(np.radians(3.0))

    glyphs = font_pack.get("glyphs", {}) if isinstance(font_pack, dict) else {}
    widths = font_pack.get("widths", {}) if isinstance(font_pack, dict) else {}
    default_width = font_pack.get("default_width", DEFAULT_WIDTH) if isinstance(font_pack, dict) else DEFAULT_WIDTH

    for ch in chars:
        if ch not in glyphs:
            continue
        strokes = glyphs[ch]
        gw = widths.get(ch, default_width)

        # A & B. Thu thập và kiểm tra từng segment
        glyph_segments = []
        all_pts = []

        for s_idx, stroke in enumerate(strokes):
            s_arr = np.asarray(stroke, dtype=float)
            if len(s_arr) > 0:
                all_pts.append(s_arr)

            for k in range(len(s_arr) - 1):
                p1 = s_arr[k]
                p2 = s_arr[k + 1]
                seg_len = float(np.linalg.norm(p2 - p1))

                # Kiểm tra A: Đoạn suy biến (ZERO_LENGTH_SEGMENT)
                if seg_len <= 1e-6:
                    findings.append({
                        "char": ch,
                        "code": "ZERO_LENGTH_SEGMENT",
                        "message": f"Ký tự '{ch}' nét {s_idx} đoạn {k} có chiều dài suy biến ({seg_len:.2e} <= 1e-6)",
                        "stroke_a": s_idx,
                        "segment_a": k,
                    })

                # Kiểm tra B: Bước nhảy bất thường (SUSPICIOUS_JUMP)
                if seg_len > max_segment_length:
                    findings.append({
                        "char": ch,
                        "code": "SUSPICIOUS_JUMP",
                        "message": f"Ký tự '{ch}' nét {s_idx} đoạn {k} có bước nhảy bất thường ({seg_len:.2f} > {max_segment_length:.2f})",
                        "stroke_a": s_idx,
                        "segment_a": k,
                    })

                glyph_segments.append((s_idx, k, p1, p2, seg_len))

        # Kiểm tra D: Vượt khung glyph (OUT_OF_BOUNDS)
        if all_pts:
            pts_concat = np.concatenate(all_pts, axis=0)
            min_x, min_y = np.min(pts_concat, axis=0)
            max_x, max_y = np.max(pts_concat, axis=0)
            if min_x < -1.0 or max_x > gw + 2.0 or min_y < -1.0 or max_y > 20.5:
                findings.append({
                    "char": ch,
                    "code": "OUT_OF_BOUNDS",
                    "message": (
                        f"Ký tự '{ch}' vượt khung glyph: "
                        f"x=[{min_x:.2f}, {max_x:.2f}] (cho phép [-1.0, {gw + 2.0:.2f}]), "
                        f"y=[{min_y:.2f}, {max_y:.2f}] (cho phép [-1.0, 20.5])"
                    ),
                })

        # Kiểm tra C: Nét chồng lên nhau (OVERLAPPING_SEGMENTS)
        num_segs = len(glyph_segments)
        for i in range(num_segs):
            s_a, k_a, p1, p2, l1 = glyph_segments[i]
            if l1 <= 1e-6:
                continue
            u1 = (p2 - p1) / l1

            for j in range(i + 1, num_segs):
                s_b, k_b, q1, q2, l2 = glyph_segments[j]
                if l2 <= 1e-6:
                    continue

                # Bỏ qua hai segment kề nhau trong cùng một stroke
                if s_a == s_b and abs(k_a - k_b) <= 1:
                    continue

                u2 = (q2 - q1) / l2

                # 1. Normalized cross product kiểm tra góc gần song song / ngược hướng (~3 độ)
                cross_val = abs(float(u1[0] * u2[1] - u1[1] * u2[0]))
                if cross_val > sin_3deg:
                    continue

                # 2 & 3. Chiếu 1D lên trục đoạn thẳng thứ nhất để tính chiều dài chồng lấn
                t_q1 = float(np.dot(q1 - p1, u1))
                t_q2 = float(np.dot(q2 - p1, u1))

                t_q_min = min(t_q1, t_q2)
                t_q_max = max(t_q1, t_q2)

                overlap_start = max(0.0, t_q_min)
                overlap_end = min(l1, t_q_max)
                overlap_len = overlap_end - overlap_start

                if overlap_len < min_overlap_length:
                    continue

                # Đo khoảng cách giữa 2 đoạn trong vùng chiếu chồng lấn
                m_start = p1 + overlap_start * u1
                m_end = p1 + overlap_end * u1
                m_mid = p1 + 0.5 * (overlap_start + overlap_end) * u1

                d_start = point_to_segment_distance(m_start, q1, q2)
                d_end = point_to_segment_distance(m_end, q1, q2)
                d_mid = point_to_segment_distance(m_mid, q1, q2)

                max_dist = max(d_start, d_end, d_mid)
                if max_dist <= overlap_tolerance:
                    findings.append({
                        "char": ch,
                        "code": "OVERLAPPING_SEGMENTS",
                        "message": (
                            f"Ký tự '{ch}' nét {s_a} đoạn {k_a} và nét {s_b} đoạn {k_b} "
                            f"chồng lấn {overlap_len:.2f} (>= {min_overlap_length:.2f}) "
                            f"với khoảng cách {max_dist:.3f} (<= {overlap_tolerance:.3f})"
                        ),
                        "stroke_a": s_a,
                        "segment_a": k_a,
                        "stroke_b": s_b,
                        "segment_b": k_b,
                    })

    return findings


# ----------------------------- Vietnamese Accent Auditor -----------------------------

def _stroke_min_distance(stroke_a, stroke_b):
    """
    Tính khoảng cách tối thiểu giữa hai stroke (polyline) trong cùng hệ tọa độ glyph.
    Tái sử dụng segments_intersect() và point_to_segment_distance().
    Trả về 0.0 nếu hai nét cắt nhau, ngược lại trả về khoảng cách Euclide nhỏ nhất.
    """
    arr_a = np.asarray(stroke_a, dtype=float)
    arr_b = np.asarray(stroke_b, dtype=float)
    if len(arr_a) == 0 or len(arr_b) == 0:
        return float("inf")

    # 1. Kiểm tra cắt nhau trực tiếp giữa các đoạn của hai nét
    for i in range(len(arr_a) - 1):
        p1, p2 = arr_a[i], arr_a[i + 1]
        for j in range(len(arr_b) - 1):
            q1, q2 = arr_b[j], arr_b[j + 1]
            if segments_intersect(p1, p2, q1, q2):
                return 0.0

    # 2. Duyệt segment của stroke A và các điểm của stroke B
    min_dist = float("inf")
    for i in range(len(arr_a) - 1):
        p1, p2 = arr_a[i], arr_a[i + 1]
        for p in arr_b:
            d = point_to_segment_distance(p, p1, p2)
            if d < min_dist:
                min_dist = d

    # 3. Duyệt segment của stroke B và các điểm của stroke A
    for j in range(len(arr_b) - 1):
        q1, q2 = arr_b[j], arr_b[j + 1]
        for p in arr_a:
            d = point_to_segment_distance(p, q1, q2)
            if d < min_dist:
                min_dist = d

    if len(arr_a) == 1 and len(arr_b) == 1:
        min_dist = float(np.linalg.norm(arr_a[0] - arr_b[0]))

    return min_dist


def audit_vietnamese_lowercase_accents(
    font_pack,
    matrix,
    min_clearance=0.12,
    max_segment_length=4.0,
):
    """
    Kiểm định bộ dấu tiếng Việt viết thường cho một Font Pack.
    Kiểm tra 12 họ nguyên âm x 6 biến thể thanh điệu = 72 ký tự.
    Phát hiện phân rã NFD sai, thiếu/thừa nét dấu, shape không hợp lệ, tọa độ không finite,
    đoạn suy biến, đoạn nhảy dài bất thường, vượt bounding box,
    va chạm giữa các dấu (accent-accent) và va chạm giữa dấu với thân chữ (accent-base).
    """
    findings = []
    format_marks = {"\u0302", "\u0306", "\u031b"}
    tone_marks = {"\u0301", "\u0300", "\u0309", "\u0303", "\u0323"}
    valid_bases = {"a", "e", "i", "o", "u", "y"}

    glyphs = font_pack.get("glyphs", {}) if isinstance(font_pack, dict) else {}
    widths = font_pack.get("widths", {}) if isinstance(font_pack, dict) else {}
    centers = font_pack.get("centers", {}) if isinstance(font_pack, dict) else {}
    default_width = font_pack.get("default_width", DEFAULT_WIDTH) if isinstance(font_pack, dict) else DEFAULT_WIDTH
    default_center = font_pack.get("default_center", DEFAULT_CENTER) if isinstance(font_pack, dict) else DEFAULT_CENTER
    dot_below_x_offsets = font_pack.get("dot_below_x_offsets", {}) if isinstance(font_pack, dict) else {}

    for row in matrix:
        for ch in row:
            nfd = unicodedata.normalize("NFD", ch)
            base_char = nfd[0]
            accents = list(nfd[1:])

            # 3. Kiểm tra Unicode NFD
            if base_char not in valid_bases or any(m not in format_marks and m not in tone_marks for m in accents):
                findings.append({
                    "char": ch,
                    "base_char": base_char,
                    "code": "INVALID_DECOMPOSITION",
                    "message": f"Ký tự '{ch}' có phân rã NFD không hợp lệ: base='{base_char}', accents={accents}",
                })
                continue

            num_fmt = sum(m in format_marks for m in accents)
            num_tone = sum(m in tone_marks for m in accents)
            if num_fmt > 1 or num_tone > 1:
                findings.append({
                    "char": ch,
                    "base_char": base_char,
                    "code": "INVALID_DECOMPOSITION",
                    "message": f"Ký tự '{ch}' có nhiều hơn 1 format mark hoặc nhiều hơn 1 tone mark: {accents}",
                })
                continue

            # 4. Kiểm tra số stroke dấu
            cx = centers.get(base_char, default_center)
            accent_strokes = generate_accents(
                base_char,
                accents,
                cx,
                dot_below_x_offset=dot_below_x_offsets.get(base_char),
            )
            expected_accent_count = num_fmt + num_tone

            if len(accent_strokes) != expected_accent_count:
                findings.append({
                    "char": ch,
                    "base_char": base_char,
                    "code": "ACCENT_COUNT_MISMATCH",
                    "message": f"Ký tự '{ch}' sinh {len(accent_strokes)} accent strokes, mong đợi {expected_accent_count}",
                })

            gw = widths.get(base_char, default_width)

            # 5. Lọc và xác thực từng accent stroke (không crash khi shape sai hoặc chứa NaN/Inf)
            valid_accent_strokes = []
            for acc_idx, stroke in enumerate(accent_strokes):
                try:
                    arr = np.asarray(stroke, dtype=float)
                except (TypeError, ValueError) as exc:
                    findings.append({
                        "char": ch,
                        "base_char": base_char,
                        "code": "INVALID_ACCENT_SHAPE",
                        "message": (
                            f"Ký tự '{ch}' nét dấu {acc_idx} không thể chuyển thành "
                            f"mảng tọa độ hợp lệ: {exc}"
                        ),
                    })
                    continue

                if arr.ndim != 2 or arr.shape[1] != 2 or len(arr) < 2:
                    findings.append({
                        "char": ch,
                        "base_char": base_char,
                        "code": "INVALID_ACCENT_SHAPE",
                        "message": f"Ký tự '{ch}' nét dấu {acc_idx} shape không hợp lệ: {arr.shape}",
                    })
                    continue

                if np.any(np.isnan(arr)) or np.any(np.isinf(arr)):
                    findings.append({
                        "char": ch,
                        "base_char": base_char,
                        "code": "NON_FINITE_ACCENT",
                        "message": f"Ký tự '{ch}' nét dấu {acc_idx} chứa NaN hoặc Inf",
                    })
                    continue

                valid_accent_strokes.append((acc_idx, arr))

            # 6. Kiểm tra các stroke hợp lệ: segment length & bounds
            for orig_idx, arr in valid_accent_strokes:
                has_zero_len = False
                has_long_seg = False
                max_seg_found = 0.0
                for k in range(len(arr) - 1):
                    seg_len = float(np.linalg.norm(arr[k + 1] - arr[k]))
                    if seg_len <= 1e-6:
                        has_zero_len = True
                    if seg_len > max_segment_length:
                        has_long_seg = True
                        if seg_len > max_seg_found:
                            max_seg_found = seg_len

                if has_zero_len:
                    findings.append({
                        "char": ch,
                        "base_char": base_char,
                        "code": "ZERO_LENGTH_ACCENT",
                        "message": f"Ký tự '{ch}' nét dấu {orig_idx} có đoạn suy biến chiều dài <= 1e-6",
                    })

                if has_long_seg:
                    findings.append({
                        "char": ch,
                        "base_char": base_char,
                        "code": "SUSPICIOUS_ACCENT_JUMP",
                        "message": (
                            f"Ký tự '{ch}' nét dấu {orig_idx} có đoạn nhảy dài bất thường: "
                            f"{max_seg_found:.2f} > {max_segment_length:.2f}"
                        ),
                    })

                min_x, min_y = np.min(arr, axis=0)
                max_x, max_y = np.max(arr, axis=0)
                if min_x < -1.0 or max_x > gw + 2.0 or min_y < -1.0 or max_y > 20.5:
                    findings.append({
                        "char": ch,
                        "base_char": base_char,
                        "code": "ACCENT_OUT_OF_BOUNDS",
                        "message": (
                            f"Ký tự '{ch}' nét dấu {orig_idx} vượt khung: "
                            f"x=[{min_x:.2f}, {max_x:.2f}] (cho phép [-1.0, {gw + 2.0:.2f}]), "
                            f"y=[{min_y:.2f}, {max_y:.2f}] (cho phép [-1.0, 20.5])"
                        ),
                    })

            # 7. Kiểm tra va chạm giữa các dấu (accent-accent collision)
            if len(valid_accent_strokes) >= 2:
                for i in range(len(valid_accent_strokes)):
                    orig_i, arr_i = valid_accent_strokes[i]
                    for j in range(i + 1, len(valid_accent_strokes)):
                        orig_j, arr_j = valid_accent_strokes[j]
                        d_aa = _stroke_min_distance(arr_i, arr_j)
                        if d_aa < min_clearance:
                            findings.append({
                                "char": ch,
                                "base_char": base_char,
                                "code": "ACCENT_ACCENT_COLLISION",
                                "message": (
                                    f"Ký tự '{ch}' va chạm giữa các nét dấu ({orig_i} và {orig_j}): "
                                    f"khoảng cách {d_aa:.4f} < {min_clearance:.4f}"
                                ),
                            })

            # 8. Kiểm tra va chạm giữa dấu với thân chữ (accent-base collision)
            if base_char in glyphs:
                base_strokes = glyphs[base_char]
                primary_strokes, _ = split_glyph_strokes(base_char, base_strokes)

                for orig_idx, acc_s in valid_accent_strokes:
                    # Ngoại lệ: Với ơ, ư, format mark \u031b là dấu móc được phép gắn vào thân chữ
                    if base_char in ("o", "u") and "\u031b" in accents and orig_idx == 0:
                        continue

                    min_base_dist = float("inf")
                    collided_base_idx = -1
                    for b_idx, b_s in enumerate(primary_strokes):
                        d_ab = _stroke_min_distance(acc_s, b_s)
                        if d_ab < min_base_dist:
                            min_base_dist = d_ab
                            collided_base_idx = b_idx
                    if min_base_dist < min_clearance:
                        findings.append({
                            "char": ch,
                            "base_char": base_char,
                            "code": "ACCENT_BASE_COLLISION",
                            "message": (
                                f"Ký tự '{ch}' nét dấu {orig_idx} va chạm thân chữ nét {collided_base_idx}: "
                                f"khoảng cách {min_base_dist:.4f} < {min_clearance:.4f}"
                            ),
                        })

    return findings


# ----------------------------- Runnable Self-Check -----------------------------

def _run_self_check():
    """Kiểm tra tự động module viết thư tay với các kiểu nét đã đăng ký."""
    text_sample = "Kính gửi thầy cô kính yêu! Nhân ngày 20/11."

    # Kiểm tra mọi render profile đang cung cấp cho người dùng
    font_results = {}
    for font_id in ["oly", "thanhdam", "thuphap", "cursive", "omni_casual"]:
        s = text_to_strokes(text_sample, font=font_id, style="hand_hocsinh")
        font_results[font_id] = len(s)
        assert len(s) > 15, f"Font {font_id}: Số lượng nét phải > 15, nhận {len(s)}"

    # Thanhdam phải có nhiều nét hơn oly do nét sổ kép
    assert font_results["thanhdam"] > font_results["oly"], "Thanhdam phai nhan doi net so"

    # Cursive phải gom nét liền mạch (số lần nhấc bút ít hơn hẳn oly)
    assert font_results["cursive"] < font_results["oly"], f"Cursive phai gop net lien mach: {font_results['cursive']} < {font_results['oly']}"

    # Kiểm tra thuật toán quy hoạch động Viterbi DP trên DAG
    test_chars = []
    for idx, c in enumerate("viet"):
        test_chars.append({
            "char": c,
            "raw_s": GLYPHS[c],
            "scale_vec": np.array([0.5, 0.5]),
            "offset": np.array([10.0 + idx * 3.0, 20.0])
        })
    dp_test = optimize_word_dag(test_chars, weights=(0.5, 4.0, 2.0, 15.0, 1.0))
    assert len(dp_test["variants"]) == 4, "DP phải chọn đúng 4 biến thể cho từ 4 ký tự"
    assert len(dp_test["conns"]) == 3, "DP phải có đúng 3 quyết định chuyển tiếp"
    assert any(dp_test["conns"]), "DP cho từ 'viet' phải tìm ra ít nhất 1 nét nối liên tục"

    # 5. Kiểm tra invariant: entry_pt == đầu nét chính đầu tiên, exit_pt == cuối nét chính cuối cùng cho toàn bộ a-z và mọi variant
    import string
    for ch in string.ascii_lowercase:
        if ch in GLYPHS:
            variants = get_glyph_variants(ch, GLYPHS[ch])
            for var in variants:
                prim, _ = split_glyph_strokes(ch, var.strokes)
                assert len(prim) > 0, f"Glyph '{ch}' variant '{var.tag}' không có primary stroke nào"
                assert np.allclose(var.entry_pt, prim[0][0]), (
                    f"Invariant vi phạm: '{ch}' variant '{var.tag}': "
                    f"entry_pt {var.entry_pt} != primary_first[0] {prim[0][0]}"
                )
                assert np.allclose(var.exit_pt, prim[-1][-1]), (
                    f"Invariant vi phạm: '{ch}' variant '{var.tag}': "
                    f"exit_pt {var.exit_pt} != primary_last[-1] {prim[-1][-1]}"
                )

    # 6. Kiểm tra tích hợp cho từ có glyph nhiều nét ('minh', 'nguyen'):
    # Đảm bảo mỗi cầu nối bắt đầu tại đúng exit_pt và kết thúc tại đúng entry_pt mà DP đã dùng để tính transition.
    checked_multistroke_bridges = 0
    for test_word in ["minh", "nguyen"]:
        scale_test = 0.5
        char_info_test = []
        curr_x_test = 20.0
        curr_y_test = 30.0
        for ch in test_word:
            raw_s = GLYPHS[ch]
            w_ch = GLYPH_WIDTHS.get(ch, DEFAULT_WIDTH) * scale_test
            char_info_test.append({
                "char": ch,
                "raw_s": raw_s,
                "offset": np.array([curr_x_test, curr_y_test - 14.0 * scale_test]),
                "scale_vec": np.array([scale_test, scale_test])
            })
            curr_x_test += w_ch

        dp_word_sol = optimize_word_dag(char_info_test, weights=(0.5, 4.0, 2.0, 15.0, 1.0), force_lift=False)
        base_strokes_check = []
        for c_idx, c_info in enumerate(char_info_test):
            c_var = dp_word_sol["variants"][c_idx]
            c_scaled = [s.astype(float) * c_info["scale_vec"] + c_info["offset"] for s in c_var.strokes]
            c_prim, _ = split_glyph_strokes(c_info["char"], c_scaled)

            if c_idx > 0 and dp_word_sol["conns"][c_idx - 1] and len(base_strokes_check) > 0:
                p_exit_check = base_strokes_check[-1][-1]
                p_entry_check = c_prim[0][0]

                prev_c_info = char_info_test[c_idx - 1]
                prev_c_var = dp_word_sol["variants"][c_idx - 1]
                dp_expected_exit = prev_c_var.exit_pt * prev_c_info["scale_vec"] + prev_c_info["offset"]
                dp_expected_entry = c_var.entry_pt * c_info["scale_vec"] + c_info["offset"]

                assert np.allclose(p_exit_check, dp_expected_exit), (
                    f"Bridge exit mismatch in word '{test_word}' at char {c_idx} ('{c_info['char']}'): "
                    f"p_exit={p_exit_check} != dp_expected_exit={dp_expected_exit}"
                )
                assert np.allclose(p_entry_check, dp_expected_entry), (
                    f"Bridge entry mismatch in word '{test_word}' at char {c_idx} ('{c_info['char']}'): "
                    f"p_entry={p_entry_check} != dp_expected_entry={dp_expected_entry}"
                )

                # Đếm số bridge thực sự kết nối từ glyph đứng trước có nhiều hơn một primary stroke
                prev_prim, _ = split_glyph_strokes(prev_c_info["char"], prev_c_var.strokes)
                if len(prev_prim) > 1:
                    checked_multistroke_bridges += 1

                prev_c_v = prev_c_var
                v_ex_w_chk = prev_c_v.v_exit * prev_c_info["scale_vec"]
                v_en_w_chk = c_var.v_entry * c_info["scale_vec"]
                br = build_ligature_bridge(
                    p_exit_check, v_ex_w_chk, p_entry_check, v_en_w_chk, scale_hint=scale_test, n=6
                )
                base_strokes_check[-1] = np.vstack([base_strokes_check[-1], br[1:-1], c_prim[0]])
                if len(c_prim) > 1:
                    base_strokes_check.extend(c_prim[1:])
            else:
                base_strokes_check.extend(c_prim)

    assert checked_multistroke_bridges > 0, (
        f"Không có bridge nào từ glyph nhiều nét được kiểm tra (checked_multistroke_bridges={checked_multistroke_bridges})"
    )

    # 7. Kiểm tra tangent anisotropic (scale_x != scale_y)
    aniso_scale = np.array([0.45, 0.7])
    aniso_chars = [
        {"char": "m", "raw_s": GLYPHS["m"], "offset": np.array([10.0, 20.0]), "scale_vec": aniso_scale},
        {"char": "i", "raw_s": GLYPHS["i"], "offset": np.array([16.0, 20.0]), "scale_vec": aniso_scale},
    ]
    captured_transitions = []
    _mod = sys.modules[__name__]
    _orig_eval = _mod.eval_transition

    def _spy_eval(u, w, p_exit, p_entry, *args, **kwargs):
        v_exit_w = kwargs.get("v_exit_world", None)
        v_entry_w = kwargs.get("v_entry_world", None)
        captured_transitions.append((u, w, v_exit_w, v_entry_w))
        return _orig_eval(u, w, p_exit, p_entry, *args, **kwargs)

    _mod.eval_transition = _spy_eval
    try:
        _mod.optimize_word_dag(aniso_chars, weights=(0.5, 4.0, 2.0, 15.0, 1.0))
    finally:
        _mod.eval_transition = _orig_eval

    assert len(captured_transitions) > 0, "optimize_word_dag không gọi eval_transition"
    for u, w, v_ex_w, v_en_w in captured_transitions:
        assert v_ex_w is not None and v_en_w is not None, "Tangent world phải được truyền vào eval_transition"
        # Xác nhận norm xấp xỉ 1.0
        assert np.isclose(np.linalg.norm(v_ex_w), 1.0), f"Norm của v_exit_world={np.linalg.norm(v_ex_w)} != 1.0"
        assert np.isclose(np.linalg.norm(v_en_w), 1.0), f"Norm của v_entry_world={np.linalg.norm(v_en_w)} != 1.0"

        # Xác nhận tangent đã được scale và normalize đúng theo công thức
        expected_ex = u.v_exit * aniso_scale
        expected_ex /= np.linalg.norm(expected_ex) + 1e-6
        expected_en = w.v_entry * aniso_scale
        expected_en /= np.linalg.norm(expected_en) + 1e-6

        assert np.allclose(v_ex_w, expected_ex), "v_exit_world không khớp với vector sau khi scale và normalize"
        assert np.allclose(v_en_w, expected_en), "v_entry_world không khớp với vector sau khi scale và normalize"

        # Xác nhận test phải thất bại nếu quay lại dùng tangent canonical chưa scale
        if abs(u.v_exit[0]) > 0.05 and abs(u.v_exit[1]) > 0.05:
            assert not np.allclose(v_ex_w, u.v_exit), (
                f"Lỗi: v_exit_world {v_ex_w} trùng với tangent canonical chưa scale {u.v_exit}!"
            )
        if abs(w.v_entry[0]) > 0.05 and abs(w.v_entry[1]) > 0.05:
            assert not np.allclose(v_en_w, w.v_entry), (
                f"Lỗi: v_entry_world {v_en_w} trùng với tangent canonical chưa scale {w.v_entry}!"
            )

    # 8. Kiểm tra tính toàn vẹn của build_ligature_bridge()
    p_ex_t = np.array([10.0, 20.0])
    v_ex_t = np.array([1.0, 0.2])
    p_en_t = np.array([15.0, 21.0])
    v_en_t = np.array([1.0, -0.1])
    br_t = build_ligature_bridge(p_ex_t, v_ex_t, p_en_t, v_en_t, scale_hint=0.5, n=6)
    assert len(br_t) == 6, "Bridge phải có đúng n=6 điểm"
    assert np.allclose(br_t[0], p_ex_t), "Bridge phải bắt đầu đúng tại p_exit"
    assert np.allclose(br_t[-1], p_en_t), "Bridge phải kết thúc đúng tại p_entry"
    assert not np.any(np.isnan(br_t)), "Bridge không được chứa NaN"
    assert not np.any(np.isinf(br_t)), "Bridge không được chứa Inf"

    # Fallback an toàn khi tangent có norm gần 0
    br_zero = build_ligature_bridge(p_ex_t, [0.0, 0.0], p_en_t, [0.0, 0.0], scale_hint=0.5, n=6)
    assert not np.any(np.isnan(br_zero)) and not np.any(np.isinf(br_zero)), "Tangent 0 không được sinh NaN/Inf"
    assert np.allclose(br_zero[0], p_ex_t) and np.allclose(br_zero[-1], p_en_t)

    # 9. Kiểm tra va chạm hình học (segments_intersect và bridge_collision_cost)
    # Unit checks cho segments_intersect
    assert segments_intersect((0, 0), (2, 2), (0, 2), (2, 0)) == True, "Đoạn cắt nhau thông thường phải trả về True"
    assert segments_intersect((0, 0), (5, 0), (1.538, 0), (1.578, 0)) == True, "Đoạn collinear chồng nhau phải trả về True"
    assert segments_intersect((0, 0), (2, 0), (2, 0), (4, 0)) == True, "Đoạn chạm đúng đầu mút phải trả về True"
    assert segments_intersect((0, 0), (2, 0), (3, 0), (5, 0)) == False, "Hai đoạn tách biệt phải trả về False"
    assert segments_intersect((0, 0), (2, 0), (0, 1), (2, 1)) == False, "Hai đoạn song song tách biệt phải trả về False"

    # Regression check Bugbot: bridge (0, 0) -> (5, 0), obstacle (1.538, 0) -> (1.578, 0)
    br_bugbot = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [4.0, 0.0], [5.0, 0.0]])
    obs_bugbot = [np.array([[1.538, 0.0], [1.578, 0.0]])]
    cost_bugbot = bridge_collision_cost(br_bugbot, obs_bugbot, [], scale_hint=1.0)
    cost_nobugbot = bridge_collision_cost(br_bugbot, [], [], scale_hint=1.0)
    assert cost_bugbot > cost_nobugbot, f"Collision cost vật cản ngắn phải > không có vật cản ({cost_bugbot} vs {cost_nobugbot})"
    assert cost_bugbot >= 2.0, f"Collision cost phát hiện được phải >= 2.0, nhận được {cost_bugbot}"

    # Tiếp xúc hợp lệ tại mút nối p_exit / p_entry không bị phạt va chạm giả
    prev_s_clean = [np.array([[8.0, 20.0], [10.0, 20.0]])]
    curr_s_clean = [np.array([[15.0, 21.0], [17.0, 21.0]])]
    cost_clean = bridge_collision_cost(br_t, prev_s_clean, curr_s_clean, scale_hint=0.5)
    assert cost_clean == 0.0, f"Tiếp xúc hợp lệ tại mút nối p_exit/p_entry bị tính thành collision giả: {cost_clean}"

    obstacle_stroke = np.array([[12.5, 18.0], [12.5, 23.0]])
    cost_blocked = bridge_collision_cost(br_t, prev_s_clean + [obstacle_stroke], curr_s_clean, scale_hint=0.5)
    assert cost_blocked > cost_clean, (
        f"Vật cản chắn ngang bridge phải có collision cost > không vật cản ({cost_blocked} vs {cost_clean})"
    )
    assert cost_blocked >= 2.0, f"Collision cost khi có vật cản phải đủ lớn, nhận được {cost_blocked}"

    # 10. Kiểm tra tích hợp so sánh trực tiếp actual call của DP và actual call của Renderer
    _orig_bridge = _mod.build_ligature_bridge
    _orig_opt = _mod.optimize_word_dag

    recorded_bridge_calls = []
    current_phase = ["init"]
    dp_tracking = []

    def _spy_bridge_tracked(p_exit, v_exit, p_entry, v_entry, scale_hint=1.0, n=6):
        res = _orig_bridge(p_exit, v_exit, p_entry, v_entry, scale_hint=scale_hint, n=n)
        recorded_bridge_calls.append({
            "phase": current_phase[0],
            "p_exit": np.asarray(p_exit, dtype=float).copy(),
            "v_exit": np.asarray(v_exit, dtype=float).copy(),
            "p_entry": np.asarray(p_entry, dtype=float).copy(),
            "v_entry": np.asarray(v_entry, dtype=float).copy(),
            "scale_hint": float(scale_hint),
            "n": int(n),
            "bridge": np.asarray(res, dtype=float).copy(),
        })
        return res

    def _spy_opt_tracked(*args, **kwargs):
        current_phase[0] = "dp"
        start_idx = len(recorded_bridge_calls)
        try:
            sol = _orig_opt(*args, **kwargs)
            end_idx = len(recorded_bridge_calls)
            dp_tracking.append({
                "char_info_list": [dict(c) for c in args[0]] if args else [],
                "start_idx": start_idx,
                "end_idx": end_idx,
                "sol": sol,
            })
            return sol
        finally:
            current_phase[0] = "renderer"

    try:
        _mod.build_ligature_bridge = _spy_bridge_tracked
        _mod.optimize_word_dag = _spy_opt_tracked

        # Gọi đường thực tế text_to_strokes với từ có bridge liên tục ("minh")
        test_word = "minh"
        text_to_strokes(test_word, font="cursive", style="hand_nguoilon")

        assert len(dp_tracking) > 0, "text_to_strokes phải thực sự gọi optimize_word_dag"
        dp_sol = dp_tracking[0]["sol"]
        conns = dp_sol["conns"]
        assert any(conns), f"Từ '{test_word}' phải có ít nhất một connection được DP lựa chọn"

        start_idx = dp_tracking[0]["start_idx"]
        end_idx = dp_tracking[0]["end_idx"]
        dp_calls = recorded_bridge_calls[start_idx:end_idx]
        renderer_calls = recorded_bridge_calls[end_idx:]

        assert len(dp_calls) > 0, "DP (eval_transition) phải thực sự gọi build_ligature_bridge"
        assert len(renderer_calls) > 0, "Renderer phải thực sự gọi build_ligature_bridge"

        # So sánh actual call với actual call cho từng transition được DP chọn kết nối
        matched_transitions = 0
        ren_call_idx = 0

        for char_i, is_conn in enumerate(conns):
            if is_conn:
                assert ren_call_idx < len(renderer_calls), "Thiếu lời gọi renderer tương ứng với connection"
                r_call = renderer_calls[ren_call_idx]
                ren_call_idx += 1

                # Tìm lời gọi DP thực sự phát sinh tương ứng với transition này
                matching_dp = None
                for d_call in dp_calls:
                    if np.allclose(d_call["p_exit"], r_call["p_exit"]) and np.allclose(d_call["p_entry"], r_call["p_entry"]):
                        matching_dp = d_call
                        break

                assert matching_dp is not None, (
                    f"Không tìm thấy actual DP call tương ứng cho connection tại char_idx={char_i} ({test_word[char_i]}->{test_word[char_i+1]})"
                )

                # So sánh chính xác các trường giữa actual DP call và actual Renderer call
                assert np.allclose(matching_dp["p_exit"], r_call["p_exit"]), (
                    f"p_exit không khớp: DP={matching_dp['p_exit']} vs Renderer={r_call['p_exit']}"
                )
                assert np.allclose(matching_dp["v_exit"], r_call["v_exit"]), (
                    f"v_exit không khớp: DP={matching_dp['v_exit']} vs Renderer={r_call['v_exit']}"
                )
                assert np.allclose(matching_dp["p_entry"], r_call["p_entry"]), (
                    f"p_entry không khớp: DP={matching_dp['p_entry']} vs Renderer={r_call['p_entry']}"
                )
                assert np.allclose(matching_dp["v_entry"], r_call["v_entry"]), (
                    f"v_entry không khớp: DP={matching_dp['v_entry']} vs Renderer={r_call['v_entry']}"
                )
                assert np.isclose(matching_dp["scale_hint"], r_call["scale_hint"]), (
                    f"scale_hint không khớp: DP={matching_dp['scale_hint']} vs Renderer={r_call['scale_hint']}"
                )
                assert np.allclose(matching_dp["bridge"], r_call["bridge"]), (
                    "Toàn bộ điểm bridge giữa actual DP call và actual Renderer call không khớp nhau"
                )

                matched_transitions += 1

        assert matched_transitions > 0, "Phải xác nhận được ít nhất một transition thực tế giữa DP và Renderer"

    finally:
        _mod.build_ligature_bridge = _orig_bridge
        _mod.optimize_word_dag = _orig_opt

    # 11. Kiểm tra kiến trúc Font Pack & Render Profile
    # 11.1 resolve_font("oly") trả đúng pack omnidraw_legacy và render profile oly
    pack_oly, prof_oly = resolve_font("oly")
    assert prof_oly["font_pack"] == "omnidraw_legacy", "Profile 'oly' phải trỏ về pack 'omnidraw_legacy'"
    assert pack_oly["name"] == "OmniDraw Legacy Stroke", "Tên pack không khớp"

    # 11.2 Bốn ID cũ đều resolve thành công
    for fid in ["oly", "thanhdam", "thuphap", "cursive"]:
        p_chk, pr_chk = resolve_font(fid)
        assert p_chk is not None and pr_chk is not None, f"Không resolve được font '{fid}'"
        assert pr_chk["font_pack"] == "omnidraw_legacy"

    # 11.2b Omni Casual là pack riêng, có đủ coverage và glyphs custom thật sự khác legacy
    pack_casual, prof_casual = resolve_font("omni_casual")
    assert prof_casual["font_pack"] == "omni_casual"
    assert pack_casual is FONT_PACKS["omni_casual"] and pack_casual is not pack_oly
    assert pack_casual["custom_glyphs"] == OMNI_CASUAL_CUSTOM_CHARS
    expected_v1_chars = set(
        string.ascii_letters
        + string.digits
        + "".join(OMNI_CASUAL_V1_PUNCTUATION)
    )
    assert len(OMNI_CASUAL_CUSTOM_CHARS) == 81
    assert len(set(OMNI_CASUAL_CUSTOM_CHARS)) == 81
    assert set(OMNI_CASUAL_CUSTOM_CHARS) == expected_v1_chars
    for ch in ("b", "d", "f", "i", "j", "k", "p", "q", "t", "A", "B", "D", "E", "F", "J", "K", "N", "P", "Q", "R", "T", "X", "Y", "1", "4", "5", "!", "?", ":", ";", '"', "“", "”"):
        assert len(pack_casual["glyphs"][ch]) == 2, f"Omni Casual '{ch}' phải có đúng 2 strokes"
    for ch in ("c", "l", "o", "u", "v", "w", "z", "C", "G", "L", "M", "O", "S", "U", "V", "W", "Z", "0", "2", "3", "6", "7", "8", "9", ".", ",", "-", "–", "—", "/", "'", "‘", "’", "(", ")"):
        assert len(pack_casual["glyphs"][ch]) == 1, f"Omni Casual '{ch}' phải có đúng 1 stroke"
    for ch in ("m", "H", "I", "…"):
        assert len(pack_casual["glyphs"][ch]) == 3, f"Omni Casual '{ch}' phải có đúng 3 strokes"
    assert len(pack_casual["glyphs"]["x"]) == 2, "Omni Casual 'x' phải có đúng 2 strokes"
    assert len(pack_casual["glyphs"]["h"]) == 2, "Omni Casual 'h' phải gồm thân và vòm tách biệt, không chồng nét"
    assert len(pack_casual["glyphs"]["m"]) == 3, "Omni Casual 'm' phải tách thân và hai vòm để tránh tô chồng"
    for ch in ("n", "r"):
        assert len(pack_casual["glyphs"][ch]) == 2, f"Omni Casual '{ch}' phải tách thân và vòm để tránh tô chồng"

    for ch in ("i", "j"):
        primary, secondary = split_glyph_strokes(
            ch,
            pack_casual["glyphs"][ch],
        )
        assert len(primary) == 1, f"Primary cho '{ch}' phải có đúng 1 stroke"
        assert len(secondary) == 1, f"Secondary cho '{ch}' phải có đúng 1 stroke"
        assert secondary[0] is pack_casual["glyphs"][ch][1]

    for ch in ("f", "t"):
        primary, secondary = split_glyph_strokes(
            ch,
            pack_casual["glyphs"][ch],
        )
        assert len(primary) == 1, f"Primary cho '{ch}' phải có đúng 1 stroke"
        assert len(secondary) == 1, f"Secondary cho '{ch}' phải có đúng 1 stroke"

    primary_k, secondary_k = split_glyph_strokes(
        "k",
        pack_casual["glyphs"]["k"],
    )
    assert len(primary_k) == 2, "Primary cho 'k' phải có đúng 2 strokes"
    assert secondary_k == [], "Secondary cho 'k' phải rỗng"
    for ch in string.ascii_letters + string.digits:
        assert ch in pack_casual["glyphs"], f"Omni Casual thiếu ký tự '{ch}'"
    for ch in OMNI_CASUAL_CUSTOM_CHARS:
        if ch in pack_oly["glyphs"]:
            old_pts = np.concatenate(pack_oly["glyphs"][ch], axis=0)
            new_pts = np.concatenate(pack_casual["glyphs"][ch], axis=0)
            assert old_pts.shape != new_pts.shape or not np.allclose(old_pts, new_pts), f"Glyph '{ch}' chưa được vẽ lại"
        else:
            assert ch in pack_casual["glyphs"], f"Glyph custom '{ch}' thiếu trong pack_casual"

    np.random.seed(42)
    casual_vi = text_to_strokes("Kính gửi mẹ yêu", font="omni_casual", style="hand_hocsinh")
    np.random.seed(42)
    legacy_vi = text_to_strokes("Kính gửi mẹ yêu", font="oly", style="hand_hocsinh")
    assert casual_vi, "Omni Casual phải render được câu tiếng Việt"
    casual_fingerprint = np.concatenate(casual_vi, axis=0)
    legacy_fingerprint = np.concatenate(legacy_vi, axis=0)
    assert casual_fingerprint.shape != legacy_fingerprint.shape or not np.allclose(casual_fingerprint, legacy_fingerprint), (
        "Output Omni Casual phải khác geometry legacy với cùng seed"
    )

    # 11.2c Kiểm tra hình học glyph (audit_font_pack_geometry): 8 synthetic checks trên fixture cục bộ
    # 1. Hai segment trùng nhau cùng hướng -> có OVERLAPPING_SEGMENTS
    synth_1 = {
        "glyphs": {"t1": [np.array([[0.0, 0.0], [2.0, 0.0]]), np.array([[0.0, 0.0], [2.0, 0.0]])]},
        "widths": {"t1": 8.0},
        "default_width": 8.0,
    }
    f1 = audit_font_pack_geometry(synth_1, ["t1"])
    assert any(f["code"] == "OVERLAPPING_SEGMENTS" for f in f1), "Synthetic check 1 thất bại: không phát hiện nét trùng nhau cùng hướng"

    # 2. Hai segment trùng nhau ngược hướng -> có OVERLAPPING_SEGMENTS
    synth_2 = {
        "glyphs": {"t2": [np.array([[0.0, 0.0], [2.0, 0.0]]), np.array([[2.0, 0.0], [0.0, 0.0]])]},
        "widths": {"t2": 8.0},
        "default_width": 8.0,
    }
    f2 = audit_font_pack_geometry(synth_2, ["t2"])
    assert any(f["code"] == "OVERLAPPING_SEGMENTS" for f in f2), "Synthetic check 2 thất bại: không phát hiện nét trùng nhau ngược hướng"

    # 3. Hai segment gần song song và chồng đủ dài -> có OVERLAPPING_SEGMENTS
    ang_3 = np.radians(1.5)
    seg_3 = np.array([[0.5, 0.05], [0.5 + np.cos(ang_3), 0.05 + np.sin(ang_3)]])
    synth_3 = {
        "glyphs": {"t3": [np.array([[0.0, 0.0], [2.0, 0.0]]), seg_3]},
        "widths": {"t3": 8.0},
        "default_width": 8.0,
    }
    f3 = audit_font_pack_geometry(synth_3, ["t3"])
    assert any(f["code"] == "OVERLAPPING_SEGMENTS" for f in f3), "Synthetic check 3 thất bại: không phát hiện nét gần song song chồng đủ dài"

    # 4. Hai segment chỉ chạm đầu mút -> không có OVERLAPPING_SEGMENTS
    synth_4 = {
        "glyphs": {"t4": [np.array([[0.0, 0.0], [2.0, 0.0]]), np.array([[2.0, 0.0], [4.0, 0.0]])]},
        "widths": {"t4": 8.0},
        "default_width": 8.0,
    }
    f4 = audit_font_pack_geometry(synth_4, ["t4"])
    assert not any(f["code"] == "OVERLAPPING_SEGMENTS" for f in f4), "Synthetic check 4 thất bại: báo nhầm khi chỉ chạm đầu mút"

    # 5. Hai segment giao nhau hình chữ X -> không có OVERLAPPING_SEGMENTS
    synth_5 = {
        "glyphs": {"t5": [np.array([[0.0, 0.0], [2.0, 2.0]]), np.array([[0.0, 2.0], [2.0, 0.0]])]},
        "widths": {"t5": 8.0},
        "default_width": 8.0,
    }
    f5 = audit_font_pack_geometry(synth_5, ["t5"])
    assert not any(f["code"] == "OVERLAPPING_SEGMENTS" for f in f5), "Synthetic check 5 thất bại: báo nhầm khi giao nhau hình chữ X"

    # 6. Hai điểm liên tiếp giống nhau -> có ZERO_LENGTH_SEGMENT
    synth_6 = {
        "glyphs": {"t6": [np.array([[1.0, 1.0], [1.0, 1.0], [2.0, 2.0]])]},
        "widths": {"t6": 8.0},
        "default_width": 8.0,
    }
    f6 = audit_font_pack_geometry(synth_6, ["t6"])
    assert any(f["code"] == "ZERO_LENGTH_SEGMENT" for f in f6), "Synthetic check 6 thất bại: không phát hiện ZERO_LENGTH_SEGMENT"

    # 7. Một bước nhảy lớn hơn ngưỡng -> có SUSPICIOUS_JUMP
    synth_7 = {
        "glyphs": {"t7": [np.array([[0.0, 0.0], [5.0, 0.0]])]},
        "widths": {"t7": 8.0},
        "default_width": 8.0,
    }
    f7 = audit_font_pack_geometry(synth_7, ["t7"], max_segment_length=4.0)
    assert any(f["code"] == "SUSPICIOUS_JUMP" for f in f7), "Synthetic check 7 thất bại: không phát hiện SUSPICIOUS_JUMP"

    # 8. Một điểm vượt khung -> có OUT_OF_BOUNDS
    synth_8 = {
        "glyphs": {"t8": [np.array([[0.0, 0.0], [12.0, 5.0]])]},
        "widths": {"t8": 8.0},
        "default_width": 8.0,
    }
    f8 = audit_font_pack_geometry(synth_8, ["t8"])
    assert any(f["code"] == "OUT_OF_BOUNDS" for f in f8), "Synthetic check 8 thất bại: không phát hiện OUT_OF_BOUNDS"

    # 9. Regression check: Stroke khép kín có retrace -> có OVERLAPPING_SEGMENTS
    synth_retrace = {
        "glyphs": {
            "t_retrace": [np.array([
                [0.0, 0.0],
                [2.0, 0.0],
                [3.0, 1.0],
                [1.0, 0.0],
                [0.0, 0.0],
            ])]
        },
        "widths": {"t_retrace": 8.0},
        "default_width": 8.0,
    }
    f_retrace = audit_font_pack_geometry(synth_retrace, ["t_retrace"])
    assert any(f["code"] == "OVERLAPPING_SEGMENTS" for f in f_retrace), (
        "Regression check 9 thất bại: không phát hiện retrace giữa segment cuối và segment đầu trong stroke khép kín"
    )

    # 10. Regression check: Stroke khép kín sạch (tam giác) -> không có OVERLAPPING_SEGMENTS
    synth_clean_tri = {
        "glyphs": {
            "t_clean": [np.array([
                [0.0, 0.0],
                [2.0, 0.0],
                [1.0, 1.5],
                [0.0, 0.0],
            ])]
        },
        "widths": {"t_clean": 8.0},
        "default_width": 8.0,
    }
    f_clean = audit_font_pack_geometry(synth_clean_tri, ["t_clean"])
    assert not any(f["code"] == "OVERLAPPING_SEGMENTS" for f in f_clean), (
        "Regression check 10 thất bại: báo nhầm OVERLAPPING_SEGMENTS cho tam giác khép kín sạch"
    )

    # 11.2d Audit hình học thực tế cho Omni Casual font pack
    casual_findings = audit_font_pack_geometry(
        FONT_PACKS["omni_casual"],
        OMNI_CASUAL_CUSTOM_CHARS,
    )
    assert casual_findings == [], f"Phát hiện lỗi hình học trong Omni Casual font pack: {casual_findings}"

    # 11.2e Kiểm tra render câu tiếng Việt chứa đầy đủ các ký tự mới của batch 2
    sample_text_new = "Cô vui vì cuộc sống có vô số xúc cảm; wow zoo."
    for ch in ("c", "o", "u", "v", "w", "x", "z"):
        assert ch in sample_text_new.lower(), f"Câu render test thiếu glyph batch 2: '{ch}'"
    strokes_new = text_to_strokes(sample_text_new, font="omni_casual", style="hand_hocsinh")
    assert strokes_new, "text_to_strokes font omni_casual không trả về nét vẽ"
    for s in strokes_new:
        assert not np.any(np.isnan(s)), "Nét vẽ chứa giá trị NaN"
        assert not np.any(np.isinf(s)), "Nét vẽ chứa giá trị Inf"
    svg_new, metrics_new, in_bounds_new = generate_handwriting_svg(
        sample_text_new, font="omni_casual", style="hand_hocsinh"
    )
    assert svg_new and "<svg" in svg_new, "SVG tạo ra không hợp lệ"
    assert in_bounds_new, "Tọa độ SVG của omni_casual vượt ngoài khổ giấy"

    # 11.2f Kiểm tra tích hợp chữ đ (base glyph 'd' + STROKE_D_BAR)
    np.random.seed(42)
    strokes_d = text_to_strokes("d", font="omni_casual", style="hand_hocsinh")
    np.random.seed(42)
    strokes_d_bar = text_to_strokes("đ", font="omni_casual", style="hand_hocsinh")
    assert len(strokes_d_bar) == len(strokes_d) + 1, (
        f"Chữ đ phải thêm đúng 1 stroke gạch ngang ({len(strokes_d_bar)} vs {len(strokes_d)} + 1)"
    )
    added_d_stroke = strokes_d_bar[-1]
    assert len(added_d_stroke) >= 2, "Stroke gạch ngang chữ đ phải có ít nhất 2 điểm"
    assert not np.any(np.isnan(added_d_stroke)), "Stroke gạch ngang chữ đ chứa NaN"
    assert not np.any(np.isinf(added_d_stroke)), "Stroke gạch ngang chữ đ chứa Inf"
    d_stroke_len = float(np.sum(np.linalg.norm(np.diff(added_d_stroke, axis=0), axis=1)))
    assert d_stroke_len > 0, "Chiều dài gạch ngang chữ đ phải lớn hơn 0"
    dy_bar = abs(float(added_d_stroke[-1][1] - added_d_stroke[0][1]))
    dx_bar = abs(float(added_d_stroke[-1][0] - added_d_stroke[0][0]))
    assert dx_bar > 0 and dy_bar / dx_bar < 0.2, (
        f"Gạch ngang chữ đ phải gần nằm ngang (dx={dx_bar:.2f}, dy={dy_bar:.2f})"
    )

    # 11.2g Kiểm tra render câu tiếng Việt batch 3A chứa đầy đủ b, d, l, p, q, đ
    sample_batch_3a = "Em bé đi dạo, mang quà qua lớp rồi ghé phố."
    for ch in ("b", "d", "l", "p", "q", "đ"):
        assert ch in sample_batch_3a, f"Câu render test batch 3A thiếu ký tự thường '{ch}'"
    strokes_3a = text_to_strokes(sample_batch_3a, font="omni_casual", style="hand_hocsinh")
    assert strokes_3a, "text_to_strokes font omni_casual batch 3A không trả về nét vẽ"
    for s in strokes_3a:
        assert not np.any(np.isnan(s)), "Nét vẽ batch 3A chứa giá trị NaN"
        assert not np.any(np.isinf(s)), "Nét vẽ batch 3A chứa giá trị Inf"
    svg_3a, metrics_3a, in_bounds_3a = generate_handwriting_svg(
        sample_batch_3a, font="omni_casual", style="hand_hocsinh"
    )
    assert svg_3a and "<svg" in svg_3a, "SVG batch 3A tạo ra không hợp lệ"
    assert in_bounds_3a, "Tọa độ SVG batch 3A của omni_casual vượt ngoài khổ giấy"

    # 11.2h Kiểm tra dấu chấm và dấu thanh của 'i'
    np.random.seed(42)
    plain_i = text_to_strokes(
        "i",
        font="omni_casual",
        style="hand_hocsinh",
    )
    np.random.seed(42)
    accented_i = text_to_strokes(
        "í ì ỉ ĩ ị",
        font="omni_casual",
        style="hand_hocsinh",
    )
    assert plain_i, "plain_i không trả về nét vẽ"
    assert accented_i, "accented_i không trả về nét vẽ"
    for s in plain_i + accented_i:
        assert not np.any(np.isnan(s)), "Nét vẽ i chứa NaN"
        assert not np.any(np.isinf(s)), "Nét vẽ i chứa Inf"
    assert len(plain_i) == 2, f"plain_i phải có đúng 2 strokes, nhận {len(plain_i)}"
    assert len(accented_i) == 10, f"accented_i phải có đúng 10 strokes (thân + dấu thanh, không có dấu chấm thừa), nhận {len(accented_i)}"

    # 11.2i Kiểm tra render câu batch 3B và toàn bộ alphabet
    sample_batch_3b = "fit kịp giờ, jazz thật vui."
    for ch in ("f", "i", "j", "k", "t"):
        assert ch in sample_batch_3b, f"Câu batch 3B thiếu glyph thường '{ch}'"
    strokes_3b = text_to_strokes(sample_batch_3b, font="omni_casual", style="hand_hocsinh")
    assert strokes_3b, "text_to_strokes font omni_casual batch 3B không trả về nét vẽ"
    for s in strokes_3b:
        assert not np.any(np.isnan(s)), "Nét vẽ batch 3B chứa NaN"
        assert not np.any(np.isinf(s)), "Nét vẽ batch 3B chứa Inf"
    svg_3b, metrics_3b, in_bounds_3b = generate_handwriting_svg(
        sample_batch_3b, font="omni_casual", style="hand_hocsinh"
    )
    assert svg_3b and "<svg" in svg_3b, "SVG batch 3B tạo ra không hợp lệ"
    assert in_bounds_3b, "Tọa độ SVG batch 3B của omni_casual vượt ngoài khổ giấy"

    alphabet_sample = string.ascii_lowercase
    strokes_alpha = text_to_strokes(alphabet_sample, font="omni_casual", style="hand_hocsinh")
    assert strokes_alpha, "Render alphabet không trả về nét vẽ"
    for s in strokes_alpha:
        assert not np.any(np.isnan(s)), "Nét vẽ alphabet chứa NaN"
        assert not np.any(np.isinf(s)), "Nét vẽ alphabet chứa Inf"

    # 11.2j Kiểm tra render chữ hoa batch 1 (A-F, Đ và nguyên âm có dấu)
    sample_upper_batch_1 = (
        "ABCDEF\n"
        "An Bình Cảm Động Êm\n"
        "Á À Ả Ã Ạ\n"
        "Ă Ắ Ằ Ẳ Ẵ Ặ\n"
        "Â Ấ Ầ Ẩ Ẫ Ậ\n"
        "É È Ẻ Ẽ Ẹ\n"
        "Ê Ế Ề Ể Ễ Ệ\n"
        "Đ"
    )
    strokes_upper_1 = text_to_strokes(sample_upper_batch_1, font="omni_casual", style="hand_hocsinh")
    assert strokes_upper_1, "Render uppercase batch 1 không trả về nét vẽ"
    for s in strokes_upper_1:
        assert not np.any(np.isnan(s)), "Nét vẽ uppercase batch 1 chứa NaN"
        assert not np.any(np.isinf(s)), "Nét vẽ uppercase batch 1 chứa Inf"

    svg_upper_1, metrics_upper_1, in_bounds_upper_1 = generate_handwriting_svg(
        sample_upper_batch_1, font="omni_casual", style="hand_hocsinh"
    )
    assert svg_upper_1 and "<svg" in svg_upper_1, "SVG uppercase batch 1 không hợp lệ"
    assert in_bounds_upper_1, "SVG uppercase batch 1 vượt ngoài khổ giấy"
    assert metrics_upper_1["total_path_length_mm"] > 0, "SVG uppercase batch 1 có length <= 0"

    # Xác nhận Đ sử dụng geometry của D custom cộng thêm nét ngang STROKE_CAP_D_BAR
    np.random.seed(42)
    s_d = text_to_strokes("D", font="omni_casual", style="hand_hocsinh")
    np.random.seed(42)
    s_d_bar = text_to_strokes("Đ", font="omni_casual", style="hand_hocsinh")
    assert len(s_d_bar) == len(s_d) + 1, "Ký tự 'Đ' phải gồm toàn bộ nét của 'D' cộng thêm đúng 1 nét ngang"
    for i_st in range(len(s_d)):
        assert np.allclose(s_d[i_st], s_d_bar[i_st]), f"Nét {i_st} của 'Đ' không khớp với nét của 'D'"

    # 11.2k Kiểm tra kích thước và metrics của glyph C (đỉnh y=2.1, đáy y=14.0, width 6.4-6.7, advance 9.5-9.6, center 5.2)
    pts_c = np.concatenate(pack_casual["glyphs"]["C"], axis=0)
    c_min_x, c_min_y = np.min(pts_c, axis=0)
    c_max_x, c_max_y = np.max(pts_c, axis=0)
    c_width = c_max_x - c_min_x
    assert np.isclose(c_min_y, 2.1, atol=0.05), f"Đỉnh thật của C phải gần 2.1, nhận {c_min_y:.3f}"
    assert np.isclose(c_max_y, 14.0, atol=0.05), f"Đáy thật của C phải gần 14.0, nhận {c_max_y:.3f}"
    assert 6.4 <= c_width <= 6.7, f"Độ rộng nét của C phải trong khoảng [6.4, 6.7], nhận {c_width:.3f}"
    assert pack_casual["widths"]["C"] in (9.5, 9.6), f"Advance width của C phải là 9.5 hoặc 9.6, nhận {pack_casual['widths']['C']}"
    assert np.isclose(pack_casual["centers"]["C"], 5.2, atol=0.05), f"Center của C phải gần 5.2, nhận {pack_casual['centers']['C']}"

    # 11.2l Kiểm tra chữ hoa batch 2 (G-L, I có dấu, specimen render)
    for ch in ("G", "H", "I", "J", "K", "L"):
        pts = np.concatenate(pack_casual["glyphs"][ch], axis=0)
        assert not np.any(np.isnan(pts)), f"Glyph '{ch}' chứa NaN"
        assert not np.any(np.isinf(pts)), f"Glyph '{ch}' chứa Inf"
        min_x, min_y = np.min(pts, axis=0)
        max_x, max_y = np.max(pts, axis=0)
        ink_h = max_y - min_y
        ink_w = max_x - min_x
        adv_w = pack_casual["widths"][ch]
        assert 2.0 <= min_y <= 2.3, f"Glyph '{ch}' cap height ngoài khoảng [2.0, 2.3]: {min_y:.3f}"
        assert 13.8 <= max_y <= 14.2, f"Glyph '{ch}' baseline ngoài khoảng [13.8, 14.2]: {max_y:.3f}"
        assert ink_h >= 11.5, f"Glyph '{ch}' ink height thấp hơn 11.5: {ink_h:.3f}"
        assert min_x >= 0.0, f"Glyph '{ch}' min_x < 0: {min_x:.3f}"
        assert max_x <= adv_w + 0.05, f"Glyph '{ch}' vượt width khai báo: {max_x:.3f} > {adv_w}"
        ratio = adv_w / ink_w
        assert 1.2 <= ratio <= 2.5, f"Glyph '{ch}' tỷ lệ advance/ink bất thường: {ratio:.2f}"

    # Kiểm tra render riêng chữ I và 5 biến thể có dấu (I Í Ì Ỉ Ĩ Ị)
    np.random.seed(42)
    st_i = text_to_strokes("I", font="omni_casual", style="hand_hocsinh")
    assert len(st_i) == 3, f"Chữ hoa 'I' phải có đúng 3 nét (không có dấu chấm mặc định), nhận {len(st_i)}"
    for s in st_i:
        assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), "Nét 'I' chứa NaN hoặc Inf"

    for ch in ("Í", "Ì", "Ỉ", "Ĩ"):
        np.random.seed(42)
        st = text_to_strokes(ch, font="omni_casual", style="hand_hocsinh")
        assert len(st) == 4, f"'{ch}' phải có đúng 4 nét (3 thân + 1 dấu thanh), nhận {len(st)}"
        for s in st:
            assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), f"Nét '{ch}' chứa NaN hoặc Inf"
        base_pts = np.concatenate(st[:3], axis=0)
        acc_pts = st[3]
        assert np.max(acc_pts[:, 1]) < np.min(base_pts[:, 1]), f"Dấu thanh của '{ch}' phải nằm trên thân chữ"
        dists = np.linalg.norm(base_pts[:, None, :] - acc_pts[None, :, :], axis=-1)
        min_d = np.min(dists)
        assert min_d > 0.12, f"Va chạm dấu thanh và thân chữ '{ch}': khoảng cách {min_d:.3f} <= 0.12"

    np.random.seed(42)
    st_i_dot = text_to_strokes("Ị", font="omni_casual", style="hand_hocsinh")
    assert len(st_i_dot) == 4, f"'Ị' phải có đúng 4 nét (3 thân + 1 dấu nặng), nhận {len(st_i_dot)}"
    for s in st_i_dot:
        assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), "Nét 'Ị' chứa NaN hoặc Inf"
    base_pts = np.concatenate(st_i_dot[:3], axis=0)
    dot_pts = st_i_dot[3]
    assert np.min(dot_pts[:, 1]) > np.max(base_pts[:, 1]), "Dấu nặng của 'Ị' phải nằm dưới thân chữ"
    dists = np.linalg.norm(base_pts[:, None, :] - dot_pts[None, :, :], axis=-1)
    min_d = np.min(dists)
    assert min_d > 0.12, f"Va chạm dấu nặng và thân chữ 'Ị': khoảng cách {min_d:.3f} <= 0.12"

    # SVG specimen batch 2 chữ hoa
    specimen_upper_2 = (
        "G H I J K L\n"
        "Gửi Hương\n"
        "I Í Ì Ỉ Ĩ Ị\n"
        "Kính Lan\n"
        "ABCDEFGHIJKL"
    )
    st_spec_2 = text_to_strokes(specimen_upper_2, font="omni_casual", style="hand_hocsinh")
    assert st_spec_2, "Specimen batch 2 không trả về nét vẽ"
    for s in st_spec_2:
        assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), "Nét specimen batch 2 chứa NaN hoặc Inf"

    svg_spec_2, metrics_spec_2, in_bounds_spec_2 = generate_handwriting_svg(
        specimen_upper_2, font="omni_casual", style="hand_hocsinh"
    )
    assert svg_spec_2 and "<svg" in svg_spec_2, "SVG specimen batch 2 không hợp lệ"
    assert in_bounds_spec_2, "SVG specimen batch 2 vượt ngoài khổ giấy"
    assert metrics_spec_2["total_path_length_mm"] > 0, "SVG specimen batch 2 có total_path_length_mm <= 0"

    # 11.2m Kiểm tra chữ hoa batch 3 (M-R, 18 biến thể O/Ô/Ơ, specimen render)
    for ch in ("M", "N", "O", "P", "Q", "R"):
        pts = np.concatenate(pack_casual["glyphs"][ch], axis=0)
        assert not np.any(np.isnan(pts)), f"Glyph '{ch}' chứa NaN"
        assert not np.any(np.isinf(pts)), f"Glyph '{ch}' chứa Inf"
        min_x, min_y = np.min(pts, axis=0)
        max_x, max_y = np.max(pts, axis=0)
        ink_h = max_y - min_y
        ink_w = max_x - min_x
        adv_w = pack_casual["widths"][ch]
        assert 2.0 <= min_y <= 2.3, f"Glyph '{ch}' cap height ngoài khoảng [2.0, 2.3]: {min_y:.3f}"
        assert 13.8 <= max_y <= 14.2, f"Glyph '{ch}' baseline ngoài khoảng [13.8, 14.2]: {max_y:.3f}"
        assert ink_h >= 11.5, f"Glyph '{ch}' ink height thấp hơn 11.5: {ink_h:.3f}"
        assert min_x >= 0.0, f"Glyph '{ch}' min_x < 0: {min_x:.3f}"
        assert max_x <= adv_w + 0.05, f"Glyph '{ch}' vượt width khai báo: {max_x:.3f} > {adv_w}"
        ratio = adv_w / ink_w
        assert 1.2 <= ratio <= 2.5, f"Glyph '{ch}' tỷ lệ advance/ink bất thường: {ratio:.2f}"

    # Vòng lặp của Q phải có cùng hình dáng và kích thước với O
    assert np.allclose(pack_casual["glyphs"]["Q"][0], pack_casual["glyphs"]["O"][0]), (
        "Thân vòng của Q phải tương thích và đồng nhất hình học với O"
    )

    # Regression test: helper _stroke_min_distance bắt được hai segment cắt nhau giữa các vertex
    crossing_a = np.array([
        [0.0, 0.0],
        [2.0, 2.0],
    ])
    crossing_b = np.array([
        [0.0, 2.0],
        [2.0, 0.0],
    ])
    assert _stroke_min_distance(crossing_a, crossing_b) == 0.0, (
        "Helper _stroke_min_distance phải phát hiện 2 segment cắt nhau ở giữa và trả về khoảng cách 0.0"
    )

    # Kiểm tra 18 biến thể chữ hoa ba họ O/Ô/Ơ
    uppercase_o_matrix = (
        ("O", "Ó", "Ò", "Ỏ", "Õ", "Ọ"),
        ("Ô", "Ố", "Ồ", "Ổ", "Ỗ", "Ộ"),
        ("Ơ", "Ớ", "Ờ", "Ở", "Ỡ", "Ợ"),
    )
    for row in uppercase_o_matrix:
        for ch in row:
            np.random.seed(42)
            st = text_to_strokes(ch, font="omni_casual", style="hand_hocsinh")
            assert st, f"text_to_strokes('{ch}') trả về rỗng"
            nfd = unicodedata.normalize("NFD", ch)
            marks = [c for c in nfd if unicodedata.combining(c)]
            expected_strokes = 1 + len(marks)
            assert len(st) == expected_strokes, (
                f"Ký tự '{ch}' phải có đúng {expected_strokes} strokes (1 base O + {len(marks)} dấu), nhận {len(st)}"
            )
            for s in st:
                assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), f"Ký tự '{ch}' chứa NaN/Inf"
            base_pts = st[0]
            has_dot_below = "\u0323" in marks
            if has_dot_below:
                dot_strokes = [s for s in st[1:] if np.min(s[:, 1]) > np.max(base_pts[:, 1])]
                assert len(dot_strokes) == 1, f"Dấu nặng của '{ch}' phải nằm dưới baseline"
                dot_min_distance = _stroke_min_distance(
                    base_pts,
                    dot_strokes[0],
                )
                assert dot_min_distance > 0.12, (
                    f"Dấu nặng của '{ch}' va chạm với base glyph: "
                    f"{dot_min_distance:.3f}"
                )
            for acc_s in st[1:]:
                if np.min(acc_s[:, 1]) > np.max(base_pts[:, 1]):
                    continue
                min_d = _stroke_min_distance(base_pts, acc_s)
                assert min_d > 0.12, (
                    f"Dấu phía trên/móc của '{ch}' va chạm với base glyph: "
                    f"{min_d:.3f} <= 0.12"
                )

    # SVG specimen batch 3 chữ hoa
    specimen_upper_3 = (
        "M N O P Q R\n"
        "Mẹ Nói\n"
        "O Ó Ò Ỏ Õ Ọ\n"
        "Ô Ố Ồ Ổ Ỗ Ộ\n"
        "Ơ Ớ Ờ Ở Ỡ Ợ\n"
        "Phương Quý\n"
        "ABCDEFGHIJKLMNOPQR"
    )
    st_spec_3 = text_to_strokes(specimen_upper_3, font="omni_casual", style="hand_hocsinh")
    assert st_spec_3, "Specimen batch 3 không trả về nét vẽ"
    for s in st_spec_3:
        assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), "Nét specimen batch 3 chứa NaN hoặc Inf"

    svg_spec_3, metrics_spec_3, in_bounds_spec_3 = generate_handwriting_svg(
        specimen_upper_3, font="omni_casual", style="hand_hocsinh"
    )
    assert svg_spec_3 and "<svg" in svg_spec_3, "SVG specimen batch 3 không hợp lệ"
    assert in_bounds_spec_3, "SVG specimen batch 3 vượt ngoài khổ giấy"
    assert metrics_spec_3["total_path_length_mm"] > 0, "SVG specimen batch 3 có total_path_length_mm <= 0"

    # 11.2n Kiểm tra chữ hoa batch 4 (S-Z, 18 biến thể U/Ư/Y, specimen render toàn bộ bảng chữ cái)
    for ch in ("S", "T", "U", "V", "W", "X", "Y", "Z"):
        pts = np.concatenate(pack_casual["glyphs"][ch], axis=0)
        assert not np.any(np.isnan(pts)), f"Glyph '{ch}' chứa NaN"
        assert not np.any(np.isinf(pts)), f"Glyph '{ch}' chứa Inf"
        min_x, min_y = np.min(pts, axis=0)
        max_x, max_y = np.max(pts, axis=0)
        ink_h = max_y - min_y
        ink_w = max_x - min_x
        adv_w = pack_casual["widths"][ch]
        assert 2.0 <= min_y <= 2.3, f"Glyph '{ch}' cap height ngoài khoảng [2.0, 2.3]: {min_y:.3f}"
        assert 13.8 <= max_y <= 14.2, f"Glyph '{ch}' baseline ngoài khoảng [13.8, 14.2]: {max_y:.3f}"
        assert ink_h >= 11.5, f"Glyph '{ch}' ink height thấp hơn 11.5: {ink_h:.3f}"
        assert min_x >= 0.0, f"Glyph '{ch}' min_x < 0: {min_x:.3f}"
        assert max_x <= adv_w + 0.05, f"Glyph '{ch}' vượt width khai báo: {max_x:.3f} > {adv_w}"
        ratio = adv_w / ink_w
        assert 1.2 <= ratio <= 2.5, f"Glyph '{ch}' tỷ lệ advance/ink bất thường: {ratio:.2f}"

    # Quan hệ độ rộng: W rộng hơn V; I là glyph hẹp nhất trong bảng chữ hoa
    assert pack_casual["widths"]["W"] > pack_casual["widths"]["V"], "W phải rộng hơn V"
    assert all(
        pack_casual["widths"]["I"] <= pack_casual["widths"][c]
        for c in string.ascii_uppercase
    ), "I phải là glyph hẹp nhất bảng chữ hoa"

    # Kiểm tra 18 biến thể chữ hoa ba họ U/Ư/Y
    uppercase_u_y_matrix = (
        ("U", "Ú", "Ù", "Ủ", "Ũ", "Ụ"),
        ("Ư", "Ứ", "Ừ", "Ử", "Ữ", "Ự"),
        ("Y", "Ý", "Ỳ", "Ỷ", "Ỹ", "Ỵ"),
    )
    for row in uppercase_u_y_matrix:
        for ch in row:
            np.random.seed(42)
            st = text_to_strokes(ch, font="omni_casual", style="hand_hocsinh")
            assert st, f"text_to_strokes('{ch}') trả về rỗng"
            nfd = unicodedata.normalize("NFD", ch)
            marks = [c for c in nfd if unicodedata.combining(c)]
            base_char = nfd[0]
            base_strokes_count = len(pack_casual["glyphs"][base_char])
            expected_strokes = base_strokes_count + len(marks)
            assert len(st) == expected_strokes, (
                f"Ký tự '{ch}' phải có đúng {expected_strokes} strokes ({base_strokes_count} base + {len(marks)} dấu), nhận {len(st)}"
            )
            for s in st:
                assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), f"Ký tự '{ch}' chứa NaN/Inf"
            base_pts = np.concatenate(st[:base_strokes_count], axis=0)
            accent_strokes = st[base_strokes_count:]
            has_dot_below = "\u0323" in marks
            if has_dot_below:
                dot_strokes = [s for s in accent_strokes if np.min(s[:, 1]) > np.max(base_pts[:, 1])]
                assert len(dot_strokes) == 1, f"Dấu nặng của '{ch}' phải nằm dưới baseline"
                dot_min_distance = _stroke_min_distance(
                    base_pts,
                    dot_strokes[0],
                )
                assert dot_min_distance > 0.12, (
                    f"Dấu nặng của '{ch}' va chạm với base glyph: "
                    f"{dot_min_distance:.3f}"
                )
            for acc_s in accent_strokes:
                if np.min(acc_s[:, 1]) > np.max(base_pts[:, 1]):
                    continue
                min_d = _stroke_min_distance(base_pts, acc_s)
                assert min_d > 0.12, (
                    f"Dấu phía trên/móc của '{ch}' va chạm với base glyph: "
                    f"{min_d:.3f} <= 0.12"
                )

    # Kiểm tra căn tâm dấu nặng của Ỵ trong Omni Casual và regression font legacy
    casual_dot_offsets = pack_casual["dot_below_x_offsets"]
    assert casual_dot_offsets["y"] == 0.0
    assert casual_dot_offsets["Y"] == 0.0

    raw_y_upper_dot = generate_accents(
        "Y",
        ["\u0323"],
        pack_casual["centers"]["Y"],
        dot_below_x_offset=casual_dot_offsets["Y"],
    )[0]
    raw_y_upper_dot_center = (
        float(np.min(raw_y_upper_dot[:, 0]))
        + float(np.max(raw_y_upper_dot[:, 0]))
    ) / 2.0
    assert abs(
        raw_y_upper_dot_center - pack_casual["centers"]["Y"]
    ) <= 0.05, (
        f"Dấu nặng của 'Ỵ' lệch tâm: dot={raw_y_upper_dot_center:.3f}, "
        f"center={pack_casual['centers']['Y']:.3f}"
    )
    raw_y_base_pts = np.concatenate(pack_casual["glyphs"]["Y"], axis=0)
    raw_y_dot_distance = _stroke_min_distance(raw_y_base_pts, raw_y_upper_dot)
    assert raw_y_dot_distance > 0.12, (
        f"Dấu nặng của 'Ỵ' va chạm với base glyph: {raw_y_dot_distance:.3f}"
    )

    legacy_y_upper_dot = generate_accents(
        "Y",
        ["\u0323"],
        pack_oly["centers"]["Y"],
        dot_below_x_offset=None,
    )[0]
    legacy_y_upper_dot_center = (
        float(np.min(legacy_y_upper_dot[:, 0]))
        + float(np.max(legacy_y_upper_dot[:, 0]))
    ) / 2.0
    assert abs(
        legacy_y_upper_dot_center - (pack_oly["centers"]["Y"] + 2.2)
    ) <= 0.05, (
        f"Dấu nặng legacy của 'Y' lệch: dot={legacy_y_upper_dot_center:.3f}, "
        f"expected={pack_oly['centers']['Y'] + 2.2:.3f}"
    )

    # SVG specimen batch 4 chữ hoa và toàn bộ bảng chữ cái
    specimen_upper_4 = (
        "S T U V W X Y Z\n"
        "Sơn Tinh Thủy Tinh Vươn Xa\n"
        "U Ú Ù Ủ Ũ Ụ\n"
        "Ư Ứ Ừ Ử Ữ Ự\n"
        "Y Ý Ỳ Ỷ Ỹ Ỵ\n"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    st_spec_4 = text_to_strokes(specimen_upper_4, font="omni_casual", style="hand_hocsinh")
    assert st_spec_4, "Specimen batch 4 không trả về nét vẽ"
    for s in st_spec_4:
        assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), "Nét specimen batch 4 chứa NaN hoặc Inf"

    svg_spec_4, metrics_spec_4, in_bounds_spec_4 = generate_handwriting_svg(
        specimen_upper_4, font="omni_casual", style="hand_hocsinh"
    )
    assert svg_spec_4 and "<svg" in svg_spec_4, "SVG specimen batch 4 không hợp lệ"
    assert in_bounds_spec_4, "SVG specimen batch 4 vượt ngoài khổ giấy"
    assert metrics_spec_4["total_path_length_mm"] > 0, "SVG specimen batch 4 có total_path_length_mm <= 0"

    # 11.2o Kiểm tra bộ chữ số 0-9 Omni Casual (metrics, confusable pairs, specimen render)
    for ch in string.digits:
        old_pts = np.concatenate(pack_oly["glyphs"][ch], axis=0)
        new_pts = np.concatenate(pack_casual["glyphs"][ch], axis=0)
        assert (
            old_pts.shape != new_pts.shape
            or not np.allclose(old_pts, new_pts)
        ), f"Digit '{ch}' vẫn dùng geometry legacy"

        pts = np.concatenate(pack_casual["glyphs"][ch], axis=0)
        assert not np.any(np.isnan(pts)), f"Digit '{ch}' chứa NaN"
        assert not np.any(np.isinf(pts)), f"Digit '{ch}' chứa Inf"
        min_x, min_y = np.min(pts, axis=0)
        max_x, max_y = np.max(pts, axis=0)
        ink_h = max_y - min_y
        ink_w = max_x - min_x
        adv_w = pack_casual["widths"][ch]
        assert 2.0 <= min_y <= 2.3, f"Digit '{ch}' cap height ngoài khoảng [2.0, 2.3]: {min_y:.3f}"
        assert 13.8 <= max_y <= 14.2, f"Digit '{ch}' baseline ngoài khoảng [13.8, 14.2]: {max_y:.3f}"
        assert ink_h >= 11.5, f"Digit '{ch}' ink height thấp hơn 11.5: {ink_h:.3f}"
        assert min_x >= 0.0, f"Digit '{ch}' min_x < 0: {min_x:.3f}"
        assert max_x <= adv_w + 0.05, f"Digit '{ch}' vượt width khai báo: {max_x:.3f} > {adv_w}"
        ratio = adv_w / ink_w
        assert 1.2 <= ratio <= 2.5, f"Digit '{ch}' tỷ lệ advance/ink bất thường: {ratio:.2f}"

    # Chữ số 1 là số hẹp nhất
    assert all(
        pack_casual["widths"]["1"] < pack_casual["widths"][d]
        for d in "023456789"
    ), "Digit 1 phải là chữ số hẹp nhất"

    # Kiểm tra phân biệt các cặp dễ nhầm:
    # 0 vs O vs o
    pts_0 = np.concatenate(pack_casual["glyphs"]["0"], axis=0)
    pts_O = np.concatenate(pack_casual["glyphs"]["O"], axis=0)
    pts_o = np.concatenate(pack_casual["glyphs"]["o"], axis=0)
    w_0 = np.max(pts_0[:, 0]) - np.min(pts_0[:, 0])
    w_O = np.max(pts_O[:, 0]) - np.min(pts_O[:, 0])
    h_0 = np.max(pts_0[:, 1]) - np.min(pts_0[:, 1])
    h_o = np.max(pts_o[:, 1]) - np.min(pts_o[:, 1])
    assert w_0 < w_O, f"Digit 0 ({w_0:.2f}) phải hẹp hơn chữ O hoa ({w_O:.2f})"
    assert h_0 > h_o + 4.0, f"Digit 0 ({h_0:.2f}) phải cao hơn rõ rệt so với chữ o thường ({h_o:.2f})"

    # 1 vs I vs l
    assert len(pack_casual["glyphs"]["1"]) == 2, "Digit 1 có 2 strokes (thân+móc, chân ngang)"
    assert len(pack_casual["glyphs"]["I"]) == 3, "Chữ I hoa có 3 strokes"
    assert len(pack_casual["glyphs"]["l"]) == 1, "Chữ l thường có 1 stroke"

    # 5 vs S vs s
    assert len(pack_casual["glyphs"]["5"]) == 2, "Digit 5 có 2 strokes (thân vòng + nóc ngang)"
    assert len(pack_casual["glyphs"]["S"]) == 1, "Chữ S hoa có 1 stroke uốn liền"

    # 6 vs G
    pts_6 = np.concatenate(pack_casual["glyphs"]["6"], axis=0)
    pts_G = np.concatenate(pack_casual["glyphs"]["G"], axis=0)
    assert pts_6.shape != pts_G.shape or not np.allclose(pts_6, pts_G), "6 và G phải có hình học khác biệt"

    # 8 vs B
    assert len(pack_casual["glyphs"]["8"]) == 1, "Digit 8 có 1 stroke figure-8"
    assert len(pack_casual["glyphs"]["B"]) == 2, "Chữ B hoa có 2 strokes"

    # 9 vs g vs q
    pts_9 = np.concatenate(pack_casual["glyphs"]["9"], axis=0)
    pts_g = np.concatenate(pack_casual["glyphs"]["g"], axis=0)
    pts_q = np.concatenate(pack_casual["glyphs"]["q"], axis=0)
    max_y_9 = np.max(pts_9[:, 1])
    max_y_g = np.max(pts_g[:, 1])
    max_y_q = np.max(pts_q[:, 1])
    assert max_y_9 <= 14.2, f"Digit 9 phải nằm trên baseline (<= 14.2), nhận {max_y_9:.3f}"
    assert max_y_g > 16.0, f"Chữ g thường phải có nét descender xuống dưới, nhận {max_y_g:.3f}"
    assert max_y_q > 16.0, f"Chữ q thường phải có nét descender xuống dưới, nhận {max_y_q:.3f}"

    # Render mẫu văn bản chứa chữ số và các cặp đối chiếu
    specimen_digits = (
        "0123456789\n"
        "2026 2027\n"
        "0912345678\n"
        "0 O o\n"
        "1 I l\n"
        "5 S s\n"
        "6 G\n"
        "8 B\n"
        "9 g q\n"
        "OmniDraw 2026"
    )
    st_spec_dig = text_to_strokes(specimen_digits, font="omni_casual", style="hand_hocsinh")
    assert st_spec_dig, "Specimen chữ số không trả về nét vẽ"
    for s in st_spec_dig:
        assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), "Nét specimen chữ số chứa NaN/Inf"

    svg_spec_dig, metrics_spec_dig, in_bounds_spec_dig = generate_handwriting_svg(
        specimen_digits, font="omni_casual", style="hand_hocsinh"
    )
    assert svg_spec_dig and "<svg" in svg_spec_dig, "SVG specimen chữ số không hợp lệ"
    assert in_bounds_spec_dig, "SVG specimen chữ số vượt ngoài khổ giấy"
    assert metrics_spec_dig["total_path_length_mm"] > 0, "SVG specimen chữ số có total_path_length_mm <= 0"

    # 11.2p Kiểm tra bộ 19 dấu câu Omni Casual (charset, metrics, smart quotes, specimen render)
    assert len(OMNI_CASUAL_V1_PUNCTUATION) == 19
    assert len(set(OMNI_CASUAL_V1_PUNCTUATION)) == 19

    for ch in OMNI_CASUAL_V1_PUNCTUATION:
        assert ch in pack_casual["glyphs"], f"Thiếu glyph dấu câu '{ch}' trong pack_casual"
        assert ch in pack_casual["widths"], f"Thiếu width cho dấu câu '{ch}' trong pack_casual"
        assert ch in pack_casual["centers"], f"Thiếu center cho dấu câu '{ch}' trong pack_casual"

    # Xác nhận các dấu câu đã có trong legacy không dùng lại geometry legacy
    for ch in [".", ",", "!", "?", ":", ";", "-", "'", '"', "(", ")", "/"]:
        old_pts = np.concatenate(pack_oly["glyphs"][ch], axis=0)
        new_pts = np.concatenate(pack_casual["glyphs"][ch], axis=0)
        assert (
            old_pts.shape != new_pts.shape
            or not np.allclose(old_pts, new_pts)
        ), f"Punctuation '{ch}' vẫn dùng geometry legacy"

    # Quan hệ độ dài gạch: em dash > en dash > hyphen
    assert (
        pack_casual["widths"]["—"]
        > pack_casual["widths"]["–"]
        > pack_casual["widths"]["-"]
    ), "Độ rộng phải thỏa mãn: em dash (—) > en dash (–) > hyphen (-)"

    # Kiểm tra bounds và tọa độ finite cho từng dấu câu
    for ch in OMNI_CASUAL_V1_PUNCTUATION:
        pts = np.concatenate(pack_casual["glyphs"][ch], axis=0)
        assert not np.any(np.isnan(pts)), f"Punctuation '{ch}' chứa NaN"
        assert not np.any(np.isinf(pts)), f"Punctuation '{ch}' chứa Inf"
        min_x, min_y = np.min(pts, axis=0)
        max_x, max_y = np.max(pts, axis=0)
        adv_w = pack_casual["widths"][ch]
        assert min_x >= 0.0, f"Punctuation '{ch}' min_x < 0: {min_x:.3f}"
        assert max_x <= adv_w + 0.05, f"Punctuation '{ch}' vượt width: {max_x:.3f} > {adv_w}"

    # Kiểm tra hướng smart quotes: ‘ và ’ là mirror hình học thật sự, không phụ thuộc hướng đi bút
    pts_ls = np.concatenate(pack_casual["glyphs"]["‘"], axis=0)
    pts_rs = np.concatenate(pack_casual["glyphs"]["’"], axis=0)
    assert pts_ls.shape == pts_rs.shape, f"‘ và ’ không cùng shape: {pts_ls.shape} vs {pts_rs.shape}"

    mirrored_ls = pts_ls.copy()
    mirrored_ls[:, 0] = 2.0 * 2.2 - mirrored_ls[:, 0]
    mirror_delta = min(
        float(np.max(np.abs(mirrored_ls - pts_rs))),
        float(np.max(np.abs(mirrored_ls[::-1] - pts_rs))),
    )
    assert mirror_delta <= 0.05, (
        f"‘ và ’ không phải mirror hình học thực sự: delta={mirror_delta:.3f}"
    )

    reverse_only_delta = float(np.max(np.abs(pts_ls[::-1] - pts_rs)))
    assert reverse_only_delta > 0.3, (
        f"’ chỉ là ‘ đảo hướng đi bút, chưa mirror hình học: delta={reverse_only_delta:.3f}"
    )

    # Kiểm tra quote kép “ và ”
    assert len(pack_casual["glyphs"]["“"]) == 2, "“ phải có đúng 2 strokes"
    assert len(pack_casual["glyphs"]["”"]) == 2, "” phải có đúng 2 strokes"
    for s_idx, axis_x in enumerate([2.2, 4.2]):
        s_open = pack_casual["glyphs"]["“"][s_idx]
        s_close = pack_casual["glyphs"]["”"][s_idx]
        assert s_open.shape == s_close.shape, f"Stroke {s_idx} của “ và ” không cùng shape"

        mirrored_open = s_open.copy()
        mirrored_open[:, 0] = 2.0 * axis_x - mirrored_open[:, 0]
        m_delta = min(
            float(np.max(np.abs(mirrored_open - s_close))),
            float(np.max(np.abs(mirrored_open[::-1] - s_close))),
        )
        assert m_delta <= 0.05, (
            f"Stroke {s_idx} của “ và ” không phải mirror thực sự: delta={m_delta:.3f}"
        )

        rev_delta = float(np.max(np.abs(s_open[::-1] - s_close)))
        assert rev_delta > 0.3, (
            f"Stroke {s_idx} của ” chỉ là “ đảo hướng đi bút: delta={rev_delta:.3f}"
        )

    # Render specimen thư tay với đầy đủ 19 dấu câu
    punctuation_inventory_line = (
        ". , ! ? : ; - – — ' \" ‘ ’ “ ” ( ) / …"
    )
    specimen_punct = (
        f"{punctuation_inventory_line}\n"
        "“Chào bạn,”\n"
        "Mình viết thư này…\n"
        "Bạn khỏe không?\n"
        "Ngày 14/09/2026 – một ngày đẹp!\n"
        "Omni Casual — thân thiện, rõ ràng.\n"
        "‘Cảm ơn!’ (Hẹn gặp lại.)\n"
        "\"ASCII quotes\" - vẫn hoạt động."
    )
    for ch in OMNI_CASUAL_V1_PUNCTUATION:
        assert ch in specimen_punct, (
            f"Specimen punctuation thiếu ký tự {ch!r}"
        )
    st_spec_p = text_to_strokes(specimen_punct, font="omni_casual", style="hand_hocsinh")
    assert st_spec_p, "Specimen dấu câu không trả về nét vẽ"
    for s in st_spec_p:
        assert not np.any(np.isnan(s)) and not np.any(np.isinf(s)), "Nét specimen chứa NaN/Inf"

    svg_spec_p, metrics_spec_p, in_bounds_spec_p = generate_handwriting_svg(
        specimen_punct, font="omni_casual", style="hand_hocsinh"
    )
    assert svg_spec_p and "<svg" in svg_spec_p, "SVG specimen dấu câu không hợp lệ"
    assert in_bounds_spec_p, "SVG specimen dấu câu vượt ngoài khổ giấy"
    assert metrics_spec_p["total_path_length_mm"] > 0, "SVG specimen dấu câu có total_path_length_mm <= 0"

    # 11.3 Font không tồn tại và 'custom' đều raise ValueError
    for bad_font in ["custom", "non_existent_font", 123, None, "patrick_hand", "playpen_sans"]:
        try:
            resolve_font(bad_font)
            assert False, f"resolve_font('{bad_font}') phải raise ValueError"
        except ValueError:
            pass

    # 11.4 Font pack có đủ glyphs, widths, centers, default metrics và basic English glyphs
    assert "glyphs" in pack_oly and isinstance(pack_oly["glyphs"], dict)
    assert "widths" in pack_oly and isinstance(pack_oly["widths"], dict)
    assert "centers" in pack_oly and isinstance(pack_oly["centers"], dict)
    assert "default_width" in pack_oly and "default_center" in pack_oly
    for ch in string.ascii_lowercase:
        assert ch in pack_oly["glyphs"], f"Thiếu basic English lowercase '{ch}' trong font pack"
    for ch in string.ascii_uppercase:
        assert ch in pack_oly["glyphs"], f"Thiếu basic English uppercase '{ch}' trong font pack"
    for ch in string.digits:
        assert ch in pack_oly["glyphs"], f"Thiếu digit '{ch}' trong font pack"

    # 11.5 Regression test so khớp với deterministic fingerprint đã ghi nhận trước refactor
    import hashlib
    np.random.seed(42)
    s_reg = text_to_strokes(text_sample, font="oly", style="hand_hocsinh")
    assert len(s_reg) == 68, f"Số strokes không khớp baseline (mong đợi 68, nhận {len(s_reg)})"
    pts_reg = sum(len(st) for st in s_reg)
    assert pts_reg == 1007, f"Số điểm không khớp baseline (mong đợi 1007, nhận {pts_reg})"
    len_reg = sum(float(np.sum(np.linalg.norm(np.diff(st, axis=0), axis=1))) for st in s_reg)
    assert np.isclose(len_reg, 499.4142, atol=1e-3), f"Tổng chiều dài không khớp baseline: {len_reg:.4f} vs 499.4142"
    hash_reg = hashlib.sha256(np.round(np.concatenate(s_reg, axis=0), 4).tobytes()).hexdigest()
    assert hash_reg == "d2f86bda2d3eda28b2e1b99e2fdb17c36b93299a7c43eb616ac9b7b4742ea05d", (
        f"SHA-256 fingerprint không khớp baseline: {hash_reg}"
    )

    np.random.seed(42)
    s_cur_reg = text_to_strokes("minh nguyen", font="cursive", style="hand_nguoilon")
    assert len(s_cur_reg) == 13, f"Số strokes cursive không khớp baseline: {len(s_cur_reg)}"
    pts_cur_reg = sum(len(st) for st in s_cur_reg)
    assert pts_cur_reg == 372, f"Số điểm cursive không khớp baseline: {pts_cur_reg}"
    hash_cur_reg = hashlib.sha256(np.round(np.concatenate(s_cur_reg, axis=0), 4).tobytes()).hexdigest()
    assert hash_cur_reg == "16787dedda194060b4c5f72d57168cc2460d8e27330c5380b0404fd52b45eed8", (
        f"SHA-256 fingerprint cursive không khớp baseline: {hash_cur_reg}"
    )

    # 11.6 Mock Font Test: Xác nhận text_to_strokes() thực sự lấy geometry từ resolved font pack, không đọc ngầm GLYPHS toàn cục
    mock_pack_id = "test_mock_pack"
    mock_font_id = "test_mock_font"
    mock_glyph_a = [np.array([[0.0, 0.0], [99.0, 99.0]])]
    mock_pack = {
        "name": "Mock Test Pack",
        "glyphs": {'a': mock_glyph_a, '?': [np.array([[0.0, 0.0], [1.0, 1.0]])]},
        "widths": {'a': 77.7},
        "centers": {'a': 33.3},
        "default_width": 55.5,
        "default_center": 22.2,
        "supports_vietnamese_accents": False,
        "source_type": "mock",
    }
    mock_profile = {
        "font_pack": mock_pack_id,
        "aspect_y": 1.0,
        "slant_add": 0.0,
        "thanhdam": False,
        "ligature": False,
        "flourish": False,
    }

    try:
        FONT_PACKS[mock_pack_id] = mock_pack
        RENDER_PROFILES[mock_font_id] = mock_profile

        strokes_mock = text_to_strokes("a", font=mock_font_id, style="hand_hocsinh", font_size_mm=14.0)
        assert len(strokes_mock) > 0, "Mock font phải sinh ra nét vẽ"
        all_mock_pts = np.concatenate(strokes_mock, axis=0)
        has_mock_geom = np.any(np.isclose(all_mock_pts[:, 0] - 20.0, 99.0, atol=1.0))
        assert has_mock_geom, (
            "text_to_strokes không sử dụng geometry từ mock font pack được resolve (có thể đang đọc ngầm GLYPHS toàn cục)"
        )
    finally:
        FONT_PACKS.pop(mock_pack_id, None)
        RENDER_PROFILES.pop(mock_font_id, None)

    assert mock_pack_id not in FONT_PACKS, "mock_pack_id phải được dọn sạch khỏi FONT_PACKS"
    assert mock_font_id not in RENDER_PROFILES, "mock_font_id phải được dọn sạch khỏi RENDER_PROFILES"

    # 11.7 Kiểm định toàn bộ dấu tiếng Việt viết thường cho Font Pack Omni Casual
    # 11.7a Khai báo và xác thực ma trận tiếng Việt viết thường (12 họ x 6 thanh = 72 ký tự)
    vietnamese_lowercase_matrix = (
        ("a", "á", "à", "ả", "ã", "ạ"),
        ("ă", "ắ", "ằ", "ẳ", "ẵ", "ặ"),
        ("â", "ấ", "ầ", "ẩ", "ẫ", "ậ"),
        ("e", "é", "è", "ẻ", "ẽ", "ẹ"),
        ("ê", "ế", "ề", "ể", "ễ", "ệ"),
        ("i", "í", "ì", "ỉ", "ĩ", "ị"),
        ("o", "ó", "ò", "ỏ", "õ", "ọ"),
        ("ô", "ố", "ồ", "ổ", "ỗ", "ộ"),
        ("ơ", "ớ", "ờ", "ở", "ỡ", "ợ"),
        ("u", "ú", "ù", "ủ", "ũ", "ụ"),
        ("ư", "ứ", "ừ", "ử", "ữ", "ự"),
        ("y", "ý", "ỳ", "ỷ", "ỹ", "ỵ"),
    )

    assert len(vietnamese_lowercase_matrix) == 12
    assert all(len(row) == 6 for row in vietnamese_lowercase_matrix)

    all_vi_chars = [
        ch
        for row in vietnamese_lowercase_matrix
        for ch in row
    ]

    assert len(all_vi_chars) == 72
    assert len(set(all_vi_chars)) == 72

    # 11.7b Kiểm tra runtime đủ 72 ký tự và kiểm tra riêng hàng 'i'
    for ch in all_vi_chars:
        np.random.seed(42)
        strokes = text_to_strokes(
            ch,
            font="omni_casual",
            style="hand_hocsinh",
        )
        assert len(strokes) >= 1, f"text_to_strokes không trả về nét cho ký tự '{ch}'"
        for s in strokes:
            assert not np.any(np.isnan(s)), f"Nét vẽ ký tự '{ch}' chứa NaN"
            assert not np.any(np.isinf(s)), f"Nét vẽ ký tự '{ch}' chứa Inf"

    np.random.seed(42)
    plain_i_strokes = text_to_strokes("i", font="omni_casual", style="hand_hocsinh")
    assert len(plain_i_strokes) == 2, f"'i' thường phải có 2 nét (thân + chấm), nhận {len(plain_i_strokes)}"
    for ch_i in ("í", "ì", "ỉ", "ĩ", "ị"):
        np.random.seed(42)
        accented_i_strokes = text_to_strokes(ch_i, font="omni_casual", style="hand_hocsinh")
        assert len(accented_i_strokes) == 2, (
            f"'{ch_i}' phải có đúng 2 nét (thân + dấu thanh, không có dấu chấm thường), nhận {len(accented_i_strokes)}"
        )

    # 11.7c Tạo SVG specimen toàn ma trận 72 ký tự tiếng Việt viết thường
    matrix_text = "\n".join(
        " ".join(row)
        for row in vietnamese_lowercase_matrix
    )
    svg_vi, metrics_vi, in_bounds_vi = generate_handwriting_svg(
        matrix_text,
        font="omni_casual",
        style="hand_hocsinh",
        font_size_mm=7.0,
        line_spacing_mm=13.0,
    )
    assert svg_vi and "<svg" in svg_vi, "SVG specimen tiếng Việt không hợp lệ"
    assert in_bounds_vi, "SVG specimen tiếng Việt vượt ngoài khổ giấy"
    assert metrics_vi["total_path_length_mm"] > 0, "SVG specimen có total_path_length_mm <= 0"

    # 11.7d Audit chi tiết dấu tiếng Việt (NFD, số nét, bounds, khoảng cách)
    vi_accent_findings = audit_vietnamese_lowercase_accents(
        FONT_PACKS["omni_casual"],
        vietnamese_lowercase_matrix,
    )
    if vi_accent_findings:
        print(f"[ACCENT AUDIT FINDINGS] Phát hiện {len(vi_accent_findings)} vấn đề dấu tiếng Việt:")
        for finding in vi_accent_findings:
            print(f"  - [{finding['code']}] {finding['char']} (base: {finding['base_char']}): {finding['message']}")
    assert vi_accent_findings == [], (
        "Phát hiện lỗi dấu tiếng Việt Omni Casual: "
        f"{vi_accent_findings}"
    )

    # 11.7e Kiểm tra riêng ký tự 'ỵ' (không va chạm thân chữ, render hợp lệ)
    strokes_y_nang = text_to_strokes("ỵ", font="omni_casual", style="hand_hocsinh")
    assert len(strokes_y_nang) == 2, f"'ỵ' phải có 2 nét (thân + dấu nặng), nhận {len(strokes_y_nang)}"
    for s in strokes_y_nang:
        assert not np.any(np.isnan(s)), "Nét vẽ của 'ỵ' chứa NaN"
        assert not np.any(np.isinf(s)), "Nét vẽ của 'ỵ' chứa Inf"

    y_nang_specimen = "ỵ"
    assert "ỵ" in y_nang_specimen

    svg_y, metrics_y, in_bounds_y = generate_handwriting_svg(
        y_nang_specimen,
        font="omni_casual",
        style="hand_hocsinh",
    )
    assert svg_y and "<svg" in svg_y, "SVG chứa 'ỵ' không hợp lệ"
    assert in_bounds_y, "SVG chứa 'ỵ' vượt ngoài khổ giấy"
    assert metrics_y["total_path_length_mm"] > 0, "SVG chứa 'ỵ' có length <= 0"

    # 11.7f Regression tests: SUSPICIOUS_ACCENT_JUMP, INVALID_ACCENT_SHAPE, NON_FINITE_ACCENT
    orig_generate_accents = generate_accents
    try:
        # Test 1: Synthetic long segment -> SUSPICIOUS_ACCENT_JUMP
        globals()["generate_accents"] = lambda base_char, accents, cx, dot_below_x_offset=None: [
            np.array([[0.0, 0.0], [5.0, 0.0]])
        ]
        jump_findings = audit_vietnamese_lowercase_accents(
            FONT_PACKS["omni_casual"],
            (("á",),),
            max_segment_length=4.0,
        )
        assert any(f["code"] == "SUSPICIOUS_ACCENT_JUMP" for f in jump_findings), (
            f"Auditor phải trả về SUSPICIOUS_ACCENT_JUMP cho segment dài 5.0, nhận: {jump_findings}"
        )

        # Test 2: Invalid shape (1, 3) -> INVALID_ACCENT_SHAPE (không crash)
        globals()["generate_accents"] = lambda base_char, accents, cx, dot_below_x_offset=None: [
            np.array([[0.0, 1.0, 2.0]])
        ]
        shape_findings = audit_vietnamese_lowercase_accents(
            FONT_PACKS["omni_casual"],
            (("á",),),
        )
        assert any(f["code"] == "INVALID_ACCENT_SHAPE" for f in shape_findings), (
            f"Auditor phải trả về INVALID_ACCENT_SHAPE cho shape (1, 3), nhận: {shape_findings}"
        )

        # Test 3: Ragged stroke -> INVALID_ACCENT_SHAPE (không crash, không ném exception)
        globals()["generate_accents"] = lambda base_char, accents, cx, dot_below_x_offset=None: [
            [[0.0, 0.0], [1.0]]
        ]
        ragged_findings = audit_vietnamese_lowercase_accents(
            FONT_PACKS["omni_casual"],
            (("á",),),
        )
        assert any(f["code"] == "INVALID_ACCENT_SHAPE" for f in ragged_findings), (
            f"Auditor phải trả về INVALID_ACCENT_SHAPE cho ragged stroke, nhận: {ragged_findings}"
        )

        # Test 4: Non-numeric stroke -> INVALID_ACCENT_SHAPE (không crash, không ném exception)
        globals()["generate_accents"] = lambda base_char, accents, cx, dot_below_x_offset=None: [
            [["invalid", "data"], [1.0, 2.0]]
        ]
        non_num_findings = audit_vietnamese_lowercase_accents(
            FONT_PACKS["omni_casual"],
            (("á",),),
        )
        assert any(f["code"] == "INVALID_ACCENT_SHAPE" for f in non_num_findings), (
            f"Auditor phải trả về INVALID_ACCENT_SHAPE cho non-numeric stroke, nhận: {non_num_findings}"
        )

        # Test 5: Non-finite accent (NaN) -> NON_FINITE_ACCENT (không crash)
        globals()["generate_accents"] = lambda base_char, accents, cx, dot_below_x_offset=None: [
            np.array([[0.0, 0.0], [np.nan, 2.0]])
        ]
        nan_findings = audit_vietnamese_lowercase_accents(
            FONT_PACKS["omni_casual"],
            (("á",),),
        )
        assert any(f["code"] == "NON_FINITE_ACCENT" for f in nan_findings), (
            f"Auditor phải trả về NON_FINITE_ACCENT cho stroke chứa NaN, nhận: {nan_findings}"
        )
    finally:
        globals()["generate_accents"] = orig_generate_accents

    # 11.8 Kiểm tra cơ chế seed tái lập kết quả độc lập với global RNG
    seed_text = "Xin chào OmniDraw"

    np.random.seed(1)
    seeded_a = text_to_strokes(
        seed_text,
        font="omni_casual",
        style="hand_hocsinh",
        seed=2026,
    )

    np.random.seed(9999)
    seeded_b = text_to_strokes(
        seed_text,
        font="omni_casual",
        style="hand_hocsinh",
        seed=2026,
    )

    assert len(seeded_a) == len(seeded_b), f"Số strokes không bằng nhau: {len(seeded_a)} vs {len(seeded_b)}"
    for idx_s, (sa, sb) in enumerate(zip(seeded_a, seeded_b)):
        assert sa.shape == sb.shape, f"Stroke {idx_s} khác shape: {sa.shape} vs {sb.shape}"
        assert np.array_equal(sa, sb), f"Stroke {idx_s} khác tọa độ giữa 2 lần render cùng seed"

    seeded_c = text_to_strokes(
        seed_text,
        font="omni_casual",
        style="hand_hocsinh",
        seed=2027,
    )
    assert any(not np.array_equal(sa, sc) for sa, sc in zip(seeded_a, seeded_c)), (
        "Seed khác nhau (2026 vs 2027) phải tạo biến thiên tọa độ khác nhau"
    )

    # Seed không hợp lệ phải raise ValueError
    for invalid_seed in (True, False, -1, 4294967296, 1.5, "42"):
        try:
            text_to_strokes(seed_text, seed=invalid_seed)
            assert False, f"text_to_strokes phải raise ValueError cho invalid seed: {invalid_seed!r}"
        except ValueError:
            pass

    # Hai biên hợp lệ không raise
    for valid_edge in (0, 4294967295):
        edge_strokes = text_to_strokes(seed_text, seed=valid_edge)
        assert len(edge_strokes) > 0, f"text_to_strokes thất bại với biên seed={valid_edge}"

    # 11.9 Kiểm tra cơ chế chống tràn trang (Single-page Safe Overflow Validation)
    # a. Văn bản bình thường
    short_text = "OmniDraw kính chào quý khách."
    short_strokes = text_to_strokes(short_text, font="omni_casual", style="hand_hocsinh")
    assert len(short_strokes) > 0, "Văn bản ngắn phải có strokes"
    short_pts = np.concatenate(short_strokes, axis=0)
    assert np.isfinite(short_pts).all(), "Tọa độ văn bản ngắn phải finite"
    assert short_pts[:, 0].min() >= 0.0 and short_pts[:, 0].max() <= 210.0, "Tọa độ X vượt ngoài khổ A4"
    assert short_pts[:, 1].min() >= 0.0 and short_pts[:, 1].max() <= 297.0, "Tọa độ Y vượt ngoài khổ A4"
    _, _, short_in_bounds = generate_handwriting_svg(short_text, font="omni_casual", style="hand_hocsinh")
    assert short_in_bounds is True, "Văn bản ngắn phải có in_bounds=True"

    # b. Văn bản quá dài phải raise TextOverflowError
    long_text = " ".join(["Xin chào"] * 800)
    try:
        text_to_strokes(long_text, font="omni_casual", style="hand_hocsinh")
        assert False, "Văn bản 800 từ phải raise TextOverflowError"
    except TextOverflowError:
        pass

    # c. Từ đơn quá dài phải raise TextOverflowError
    long_word = "a" * 1000
    try:
        text_to_strokes(long_word, font="omni_casual", style="hand_hocsinh")
        assert False, "Từ đơn 1000 ký tự phải raise TextOverflowError"
    except TextOverflowError:
        pass

    # d. Validation trước clip trong build_svg
    try:
        from path_optimizer import build_svg
    except ImportError:
        from backend.path_optimizer import build_svg

    _, bad_bounds = build_svg(
        [np.array([[20.0, 20.0], [20.0, 400.0]])],
        [0],
        [False],
        1.0,
        (0.0, 0.0),
        (210.0, 297.0),
    )
    _, good_bounds = build_svg(
        [np.array([[20.0, 20.0], [30.0, 30.0]])],
        [0],
        [False],
        1.0,
        (0.0, 0.0),
        (210.0, 297.0),
    )
    assert bad_bounds is False, "Stroke vượt khổ giấy phải trả is_within_bounds=False"
    assert good_bounds is True, "Stroke hợp lệ phải trả is_within_bounds=True"

    # 11.10 Kiểm tra từ chối ký tự không được hỗ trợ (UnsupportedCharacterError)
    # A. Ký tự hợp lệ vẫn hoạt động
    valid_text_res = text_to_strokes(
        "Tiếng Việt: Đặng Thị Hồng?",
        font="omni_casual",
        seed=123,
    )
    assert len(valid_text_res) > 0, "Tiếng Việt hợp lệ phải sinh ra nét vẽ"

    # B. Unicode NFD hợp lệ
    nfd_res = text_to_strokes(
        "e\u0302\u0301",
        font="omni_casual",
        seed=123,
    )
    assert len(nfd_res) > 0, "Unicode NFD hợp lệ phải sinh ra nét vẽ"

    # C. Emoji bị từ chối
    try:
        text_to_strokes("Xin chào 😊", font="omni_casual")
        assert False, "Emoji phải bị từ chối"
    except UnsupportedCharacterError as exc:
        assert exc.characters == ("😊",), f"Mong đợi ('😊',), nhận {exc.characters}"

    # D. Ký tự CJK bị từ chối giữ đúng thứ tự
    try:
        text_to_strokes("你好", font="omni_casual")
        assert False, "Ký tự CJK phải bị từ chối"
    except UnsupportedCharacterError as exc:
        assert exc.characters == ("你", "好"), f"Mong đợi ('你', '好'), nhận {exc.characters}"

    # E. Không lặp ký tự lỗi
    try:
        text_to_strokes("😊你😊", font="omni_casual")
        assert False, "Ký tự lặp lỗi phải bị từ chối"
    except UnsupportedCharacterError as exc:
        assert exc.characters == ("😊", "你"), f"Mong đợi ('😊', '你'), nhận {exc.characters}"

    # F. Combining mark không hỗ trợ
    try:
        text_to_strokes("a\u0308", font="omni_casual")
        assert False, "Diaeresis combining mark phải bị từ chối"
    except UnsupportedCharacterError as exc:
        assert exc.characters == ("\u0308",), f"Mong đợi ('\\u0308',), nhận {exc.characters}"

    # G. Combining mark đứng riêng
    try:
        text_to_strokes("\u0301", font="omni_casual")
        assert False, "Combining mark đứng riêng phải bị từ chối"
    except UnsupportedCharacterError as exc:
        assert exc.characters == ("\u0301",), f"Mong đợi ('\\u0301',), nhận {exc.characters}"

    # H. Dấu hỏi thật vẫn hợp lệ
    q_strokes = text_to_strokes("?", font="omni_casual")
    assert len(q_strokes) > 0, "Dấu hỏi thật '?' phải render thành công"

    # 11.11 Kiểm tra loại thư (Letter Type) và biến thể chữ hoa mở đầu (formal initial glyphs)
    # A. General giữ nguyên
    gen_def = text_to_strokes("Kính gửi", font="oly", seed=123)
    gen_exp = text_to_strokes("Kính gửi", font="oly", seed=123, letter_type="general")
    assert len(gen_def) == len(gen_exp), "Số lượng nét general mặc định và tường minh phải bằng nhau"
    for s1, s2 in zip(gen_def, gen_exp):
        assert np.array_equal(s1, s2), "General mặc định phải giống hệt general tường minh từng byte"

    # B. Formal khác general
    formal_res = text_to_strokes("Kính gửi", font="oly", seed=123, letter_type="formal")
    assert not np.array_equal(gen_exp[0], formal_res[0]), "Chữ K đầu tiên của formal phải khác glyph nền của general"

    # C. Cả ba glyph hoạt động (K, T, C)
    for sample_txt in ["Kính gửi", "Thân gửi", "Cảm ơn"]:
        f_svg, f_met, f_in_bounds = generate_handwriting_svg(sample_txt, font="oly", letter_type="formal", seed=123)
        assert "<svg" in f_svg, f"SVG cho '{sample_txt}' formal phải hợp lệ"
        assert f_in_bounds, f"Nội dung '{sample_txt}' formal phải nằm trong bounds"

    # D. Chỉ áp dụng ở đầu tài liệu
    font_legacy_pack, _ = resolve_font("oly")
    for non_initial_txt, target_char in [("Anh Khoa", "K"), ("Anh Tuấn", "T"), ("Anh Cường", "C")]:
        _, _, _, v_tag = select_contextual_glyph(target_char, font_legacy_pack, "omnidraw_legacy", "formal", False)
        assert v_tag == "base", f"'{target_char}' không ở đầu văn bản phải dùng variant 'base'"

    # E. Bỏ qua khoảng trắng đầu
    space_formal = text_to_strokes("  \nKính gửi", font="oly", seed=123, letter_type="formal")
    assert len(space_formal) > 0, "Chuỗi có khoảng trắng đầu phải render thành công"

    # F. Font không tương thích (formal với omni_casual phải raise)
    try:
        text_to_strokes("Kính gửi", font="omni_casual", letter_type="formal")
        assert False, "formal với omni_casual phải raise UnsupportedLetterTypeError"
    except UnsupportedLetterTypeError:
        pass

    # G. Loại thư không tồn tại
    try:
        text_to_strokes("Kính gửi", font="oly", letter_type="romantic")
        assert False, "romantic phải raise UnsupportedLetterTypeError"
    except UnsupportedLetterTypeError:
        pass

    # H. Geometry thật sự khác legacy
    for char_key in ["K", "T", "C"]:
        legacy_s = GLYPHS[char_key]
        formal_s = LETTER_VARIANT_SETS["formal"]["initial_glyphs"][char_key]["strokes"]
        for s_f in formal_s:
            for s_l in legacy_s:
                assert s_f is not s_l, f"Formal glyph '{char_key}' không được dùng chung mutable array với legacy"
        legacy_pts = np.vstack(legacy_s)
        formal_pts = np.vstack(formal_s)
        assert len(formal_pts) != len(legacy_pts) or not np.allclose(formal_pts, legacy_pts), f"Formal glyph '{char_key}' phải có geometry riêng"

    svg, metrics, in_bounds = generate_handwriting_svg(text_sample, font="cursive", style="hand_nguoilon", skew_angle_deg=2.5)
    assert "<svg" in svg and "C" in svg, "SVG phải hợp lệ và chứa lệnh Bézier C"
    assert in_bounds, "Tọa độ phải nằm trong khổ giấy"
    print(f"[HANDWRITING SELF-CHECK PASS] Kiểm tra thành công {len(font_results)} kiểu nét: {font_results} | DAG DP OK | SVG Cursive: {metrics['total_path_length_mm']:.1f}mm | Deskew OK")


if __name__ == "__main__":
    _run_self_check()
