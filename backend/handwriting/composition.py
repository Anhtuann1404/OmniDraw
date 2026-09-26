"""
OmniDraw - Module Bố Trí Dấu và Không Gian Trạng Thái CA-VHC (PR3 Slice 1)
========================================================================
Hiện thực kiến trúc trạng thái kết hợp CompositionState và DiacriticCandidate
cho thuật toán CA-VHC Diacritic-Aware Trellis DAG:
- Bất biến dữ liệu (frozen dataclasses): CompositionState, DiacriticCandidate, DiacriticConfig.
- Độc lập hai hệ tọa độ: Cục bộ (glyph-local units) và Thực tế thế giới (world mm).
- Tách bạch chi phí trạng thái C_state và chi phí chuyển tiếp J_transition (Zero Double-Count).
- Cắt tỉa cứng (Hard-invalid pruning): loại bỏ vĩnh viễn các candidate va chạm vượt ngưỡng,
  không bao giờ hồi sinh bằng fallback.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import numpy as np

if __package__:
    from .engine import (
        GlyphVariant,
        get_glyph_variants,
        generate_accents,
        split_glyph_strokes,
        _stroke_min_distance,
        segments_intersect,
        point_to_segment_distance,
        build_ligature_bridge,
        bridge_collision_cost,
        GLYPH_CENTERS,
        GLYPHS,
    )
else:
    try:
        from handwriting.engine import (
            GlyphVariant,
            get_glyph_variants,
            generate_accents,
            split_glyph_strokes,
            _stroke_min_distance,
            segments_intersect,
            point_to_segment_distance,
            build_ligature_bridge,
            bridge_collision_cost,
            GLYPH_CENTERS,
            GLYPHS,
        )
    except ImportError:
        from backend.handwriting.engine import (
            GlyphVariant,
            get_glyph_variants,
            generate_accents,
            split_glyph_strokes,
            _stroke_min_distance,
            segments_intersect,
            point_to_segment_distance,
            build_ligature_bridge,
            bridge_collision_cost,
            GLYPH_CENTERS,
            GLYPHS,
        )


# =============================================================================
# 1. Cấu hình Tham số Duy nhất (Single Source of Truth)
# =============================================================================

@dataclass(frozen=True)
class DiacriticConfig:
    """
    Nguồn cấu hình duy nhất (Single Source of Truth) cho hệ thống dấu CA-VHC.
    Toàn bộ giải thuật sinh ứng viên và hàm tính chi phí đều đọc từ cấu trúc này.
    """
    # Ngưỡng dung sai va chạm hình học (Geometry Metric, đơn vị mm):
    # Nếu khoảng cách hở <= internal_collision_tolerance_mm thì coi như va chạm/xuyên thấu
    internal_collision_tolerance_mm: float = 0.05

    # Khoảng cách an toàn tối thiểu mong muốn giữa dấu và nét liền kề (Geometry Metric, đơn vị mm):
    clearance_threshold_mm: float = 0.20

    # Ngưỡng chi phí va chạm nội tại tối đa cho phép trước khi cắt tỉa ứng viên (Cost Metric, vô hướng):
    max_internal_collision_cost: float = 0.50

    # Danh sách độ dịch ngang cho các ứng viên P0 (mm)
    dx_candidates_mm: Dict[str, float] = field(default_factory=lambda: {
        "canonical": 0.0,
        "safe_left": -0.45,
        "safe_right": 0.45,
    })

    # Danh sách độ dịch dọc cho các ứng viên P0 (mm)
    dy_candidates_mm: Dict[str, float] = field(default_factory=lambda: {
        "canonical": 0.0,
    })

    # Độ lệch dịch chuyển tối đa cho phép để chuẩn hóa placement penalty (mm)
    max_placement_shift_mm: float = 1.0

    # Trọng số thành phần của State Cost C_state:
    w_internal_collision: float = 1.0  # w_4a
    w_legibility: float = 1.0          # w_5
    w_placement: float = 1.0           # w_6


# =============================================================================
# 2. Cấu trúc Dữ liệu Ứng viên Dấu và Trạng thái Ghép nối
# =============================================================================

@dataclass(frozen=True)
class DiacriticCandidate:
    """
    Biểu diễn một cấu hình ứng viên của dấu tiếng Việt cho ký tự cơ sở.
    Bất biến (immutable, frozen=True) để bảo đảm an toàn dữ liệu trong Viterbi DP.
    """
    marks: Tuple[str, ...]                          # Danh sách Unicode combining marks NFD
    placement_tag: str                              # 'canonical', 'safe_left', 'safe_right'
    strokes_local: Tuple[np.ndarray, ...]           # Polyline nét dấu ở TỌA ĐỘ CỤC BỘ (local glyph frame)
    anchor_x: float                                 # Tọa độ mỏ neo X cục bộ cơ sở (local glyph frame)
    anchor_y: float                                 # Tọa độ mỏ neo Y cục bộ cơ sở (local glyph frame)
    dx: float                                       # Khoảng dịch ngang (mm)
    dy: float                                       # Khoảng dịch dọc (mm)
    bounds_local: Tuple[float, float, float, float] # Hộp bao cục bộ AABB: (xmin, ymin, xmax, ymax)
    clearance_zone_local: Tuple[np.ndarray, ...]    # Vùng bao an toàn cục bộ (polygon envelope)
    placement_penalty: float                        # Chi phí phạt do lệch vị trí chuẩn tắc (>= 0.0)
    canonical_strokes_local: Tuple[np.ndarray, ...] = ()  # Tọa độ chuẩn tắc chưa dịch (cho world transform)


@dataclass(frozen=True)
class CompositionState:
    """
    Node logic chính thức của Trellis DAG tại vị trí ký tự i.
    Bất biến (frozen=True) để bảo đảm an toàn dữ liệu và tái lập thực nghiệm.
    """
    base_variant: GlyphVariant                        # Biến thể hình học thân chữ cái gốc
    diacritic_candidate: Optional[DiacriticCandidate] # Ứng viên cấu hình dấu (None nếu không dấu)
    base_char: str                                    # Ký tự gốc (VD: 'e', 'a', 'o', 'd')
    accents: Tuple[str, ...]                          # Bộ combining marks nguyên bản từ NFD
    context: Dict[str, Any]                           # Ngữ cảnh ký tự
    state_tag: str                                    # Nhãn kết hợp (VD: 'std_canonical', 'high_out_safe_left')
    internal_collision_cost: float                    # Chi phí tự va chạm nội tại C_internal_collision (>= 0.0)
    legibility_cost: float                            # Chi phí thẩm mỹ thân chữ kế thừa từ base_variant (>= 0.0)
    metadata: Dict[str, Any] = field(default_factory=dict) # Thông tin phục vụ debug, tracking


# =============================================================================
# 3. Hợp đồng Chuyển tiếp E4 (Shared Transition Contract)
# =============================================================================

@dataclass(frozen=True)
class TransitionWeights:
    """Trọng số động học cho hàm chi phí chuyển tiếp J_transition."""
    w_penup: float = 0.5              # w1: Quãng đường di chuyển không vẽ (mm)
    w_lift: float = 4.0               # w2: Chi phí phạt nhấc bút
    w_curvature: float = 2.0          # w3: Chi phí phạt đổi hướng tiếp tuyến
    w_bridge_collision: float = 15.0  # w4: Chi phí phạt va chạm bridge–diacritic / bridge–glyph


@dataclass(frozen=True)
class TransitionCostBreakdown:
    """Bóc tách chi tiết các thành phần chi phí chuyển tiếp."""
    d_penup_mm: float
    n_lift: int
    c_curvature: float
    c_bridge_collision: float
    total_cost: float


@dataclass(frozen=True)
class TransitionResult:
    """Kết quả đánh giá chuyển tiếp giữa 2 CompositionState."""
    is_valid: bool                                       # False nếu vi phạm hard constraint
    decision: str                                        # "CONNECT" | "LIFT" | "REJECT"
    total_cost: float                                    # min(J_conn, J_lift) hoặc +inf
    breakdown: TransitionCostBreakdown
    bridge_strokes: Optional[List[np.ndarray]] = None    # Polylines trong world frame (nếu CONNECT)


@dataclass(frozen=True)
class GlyphWorldGeometry:
    """Hình học của glyph và dấu trong hệ tọa độ world (mm)."""
    p_entry: np.ndarray
    p_exit: np.ndarray
    v_entry: np.ndarray
    v_exit: np.ndarray
    base_strokes: Tuple[np.ndarray, ...]
    diacritic_strokes: Tuple[np.ndarray, ...] = ()


class NoValidCompositionState(ValueError):
    """Ngoại lệ khi toàn bộ CompositionState bị cắt tỉa bởi hard invalid constraints."""
    pass


# =============================================================================
# 4. Tiện ích Tính toán Hình học và Va chạm Nội tại
# =============================================================================

def compute_bounds_local(strokes: Sequence[np.ndarray]) -> Tuple[float, float, float, float]:
    """Tính hộp bao AABB (xmin, ymin, xmax, ymax) từ tập nét trong hệ tọa độ cục bộ."""
    valid_strokes = [s for s in strokes if len(s) > 0]
    if not valid_strokes:
        return (0.0, 0.0, 0.0, 0.0)
    xmin = min(float(np.min(s[:, 0])) for s in valid_strokes)
    ymin = min(float(np.min(s[:, 1])) for s in valid_strokes)
    xmax = max(float(np.max(s[:, 0])) for s in valid_strokes)
    ymax = max(float(np.max(s[:, 1])) for s in valid_strokes)
    return (xmin, ymin, xmax, ymax)


def compute_clearance_zone_local(
    strokes: Sequence[np.ndarray],
    clearance_mm: float
) -> Tuple[np.ndarray, ...]:
    """Tạo vùng an toàn mở rộng (clearance envelope) bao quanh các nét dấu."""
    zones = []
    for s in strokes:
        if len(s) == 0:
            continue
        x0 = float(np.min(s[:, 0])) - clearance_mm
        y0 = float(np.min(s[:, 1])) - clearance_mm
        x1 = float(np.max(s[:, 0])) + clearance_mm
        y1 = float(np.max(s[:, 1])) + clearance_mm
        poly = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=float)
        zones.append(poly)
    return tuple(zones)


def compute_internal_clearance_mm(
    base_strokes_local: Sequence[np.ndarray],
    diacritic_strokes_local: Sequence[np.ndarray],
    scale_vec: Tuple[float, float] = (1.0, 1.0),
    base_char: str = "",
    accents: Sequence[str] = (),
) -> float:
    """
    Tính khoảng cách hở Euclide nhỏ nhất (min clearance mm) trong nội tại ký tự:
    - Giữa các nét dấu với nhau (accent–accent).
    - Giữa các nét dấu với nét thân chữ (accent–base), bỏ qua điểm gắn móc tự nhiên trên 'o'/'u'.
    - Tọa độ nét được chuyển đổi từ glyph-local sang world mm thông qua vector scale bất đẳng hướng scale_vec (sx, sy).
    """
    sx, sy = float(scale_vec[0]), float(scale_vec[1])
    s_vec = np.array([sx, sy], dtype=float)

    valid_diac = [np.asarray(s, dtype=float) * s_vec for s in diacritic_strokes_local if len(s) > 0]
    if not valid_diac:
        return float("inf")

    min_dist = float("inf")

    # 1. Khoảng cách giữa các nét dấu với nhau (accent–accent)
    if len(valid_diac) >= 2:
        for i in range(len(valid_diac)):
            for j in range(i + 1, len(valid_diac)):
                d = _stroke_min_distance(valid_diac[i], valid_diac[j])
                if d < min_dist:
                    min_dist = d

    # 2. Khoảng cách giữa nét dấu với nét thân chữ (accent–base)
    valid_base = [np.asarray(s, dtype=float) * s_vec for s in base_strokes_local if len(s) > 0]
    if valid_base:
        for idx, d_stroke in enumerate(valid_diac):
            # Móc của o/u được gắn liền góc trên bên phải của thân chữ theo thiết kế font
            if base_char in ("o", "u") and "\u031b" in accents and idx == 0:
                continue
            for b_stroke in valid_base:
                d = _stroke_min_distance(d_stroke, b_stroke)
                if d < min_dist:
                    min_dist = d

    return min_dist


def compute_internal_collision_cost(
    base_strokes_local: Sequence[np.ndarray],
    diacritic_strokes_local: Sequence[np.ndarray],
    scale_vec: Tuple[float, float] = (1.0, 1.0),
    tolerance_mm: float = 0.05,
    clearance_threshold_mm: float = 0.20,
    max_internal_collision_cost: float = 0.50,
    base_char: str = "",
    accents: Sequence[str] = (),
) -> float:
    """
    Tính chi phí va chạm nội tại vô hướng C_internal_collision in [0.0, 1.0]:
    - Nếu min_clearance <= tolerance_mm (giao cắt hoặc xâm lấn): cost = 1.0 (vượt trần 0.50 -> prune).
    - Nếu min_clearance >= clearance_threshold_mm: cost = 0.0.
    - Nếu tolerance_mm < min_clearance < clearance_threshold_mm:
      phạt mềm tuyến tính trong khoảng (0.0, 0.40] <= max_internal_collision_cost.
    """
    valid_diac = [s for s in diacritic_strokes_local if len(s) > 0]
    if not valid_diac:
        return 0.0

    min_dist = compute_internal_clearance_mm(
        base_strokes_local=base_strokes_local,
        diacritic_strokes_local=diacritic_strokes_local,
        scale_vec=scale_vec,
        base_char=base_char,
        accents=accents,
    )

    if math.isinf(min_dist):
        return 0.0

    # Va chạm cứng: khoảng cách nhỏ hơn hoặc bằng dung sai xuyên thấu
    if min_dist <= tolerance_mm:
        return 1.0

    # An toàn tuyệt đối: khoảng cách lớn hơn hoặc bằng ngưỡng an toàn
    if min_dist >= clearance_threshold_mm:
        return 0.0

    # Phạt mềm (soft penalty) khi nằm trong vùng đệm [tolerance_mm, clearance_threshold_mm]
    # Tối đa 0.40 để không vô tình kích hoạt hard invalid pruning (0.50)
    buffer_range = clearance_threshold_mm - tolerance_mm
    ratio = (clearance_threshold_mm - min_dist) / (buffer_range if buffer_range > 1e-9 else 1.0)
    return float(np.clip(0.40 * ratio, 0.0, 0.40))


def compute_state_cost(
    state: CompositionState,
    config: Optional[DiacriticConfig] = None
) -> float:
    """
    Tính chi phí nội tại C_state(s) theo công thức Docs 07 / Docs 18:
    C_state(s) = w_4a * C_internal_collision + w_5 * C_legibility + w_6 * C_placement
    """
    cfg = config if config is not None else DiacriticConfig()
    c_internal = state.internal_collision_cost
    c_legibility = state.legibility_cost
    c_placement = (
        state.diacritic_candidate.placement_penalty
        if state.diacritic_candidate is not None
        else 0.0
    )
    return (
        cfg.w_internal_collision * c_internal
        + cfg.w_legibility * c_legibility
        + cfg.w_placement * c_placement
    )


# =============================================================================
# 5. Sinh Ứng viên Dấu và Trạng thái Ghép nối
# =============================================================================

def generate_diacritic_candidates(
    base_char: str,
    accents: Sequence[str],
    char_info: Optional[Dict[str, Any]] = None,
    font_pack: Optional[Dict[str, Any]] = None,
    config: Optional[DiacriticConfig] = None,
) -> List[DiacriticCandidate]:
    """
    Sinh danh sách ứng viên bố trí dấu (DiacriticCandidate) cho một ký tự cơ sở.
    - Với dấu nặng đơn thuần ('\u0323'): sinh 1 ứng viên canonical duy nhất dưới baseline.
    - Với các dấu khác: sinh các ứng viên canonical, safe_left, safe_right theo config.
    """
    if not accents:
        return []

    cfg = config if config is not None else DiacriticConfig()
    info = char_info if char_info is not None else {}

    # 1. Xác định tọa độ trọng tâm cx và bù dấu nặng
    cx = info.get("cx")
    if cx is None and font_pack is not None and "centers" in font_pack:
        cx = font_pack["centers"].get(base_char, 5.0)
    if cx is None:
        cx = GLYPH_CENTERS.get(base_char, 5.0)

    dot_below_x_offset = info.get("dot_below_x_offset")

    # 2. Sinh nét canonical bằng hàm chuẩn tắc hiện hành
    canonical_list = generate_accents(
        base_char,
        list(accents),
        cx,
        dot_below_x_offset=dot_below_x_offset
    )
    if not canonical_list:
        return []

    canonical_strokes = tuple(np.asarray(s, dtype=float) for s in canonical_list)

    # 3. Xác định tập nhãn ứng viên
    # Nếu chỉ có dấu nặng '\u0323' dưới chân chữ: chỉ sinh canonical, không dịch trái/phải
    if tuple(accents) == ("\u0323",):
        candidate_tags = ["canonical"]
    else:
        candidate_tags = list(cfg.dx_candidates_mm.keys())

    scale_vec = info.get("scale_vec")
    scale_x = float(scale_vec[0]) if scale_vec is not None else 1.0

    candidates = []
    for tag in candidate_tags:
        dx_mm = float(cfg.dx_candidates_mm.get(tag, 0.0))
        dy_mm = float(cfg.dy_candidates_mm.get(tag, 0.0))

        # Áp dụng dịch chuyển vào tọa độ cục bộ
        # Độ dịch cục bộ dx_loc = dx_mm / scale_x để khi nhân scale_x ra đúng dx_mm trên giấy
        dx_loc = dx_mm / (scale_x if abs(scale_x) > 1e-6 else 1.0)
        dy_loc = dy_mm

        shifted_strokes = tuple(s + np.array([dx_loc, dy_loc]) for s in canonical_strokes)
        bounds_loc = compute_bounds_local(shifted_strokes)
        clearance_zones = compute_clearance_zone_local(shifted_strokes, cfg.clearance_threshold_mm)

        # Placement penalty: tỉ lệ khoảng dịch so với khoảng dịch tối đa cho phép
        shift_dist = math.sqrt(dx_mm ** 2 + dy_mm ** 2)
        penalty = shift_dist / (cfg.max_placement_shift_mm if cfg.max_placement_shift_mm > 0 else 1.0)

        candidates.append(DiacriticCandidate(
            marks=tuple(accents),
            placement_tag=tag,
            strokes_local=shifted_strokes,
            anchor_x=float(cx),
            anchor_y=0.0,
            dx=dx_mm,
            dy=dy_mm,
            bounds_local=bounds_loc,
            clearance_zone_local=clearance_zones,
            placement_penalty=float(penalty),
            canonical_strokes_local=canonical_strokes,
        ))

    return candidates


def build_composition_states(
    char_info: Dict[str, Any],
    font_pack: Optional[Dict[str, Any]] = None,
    config: Optional[DiacriticConfig] = None,
) -> List[CompositionState]:
    """
    Sinh tập ứng viên CompositionState cho một ký tự tại vị trí xác định.
    - Ký tự không dấu (ASCII): sinh K_base states, diacritic_candidate = None.
    - Ký tự có dấu: tổ hợp tích Descartes K_base x K_diacritic và cắt tỉa bất hợp lệ cứng.
    - Cắt tỉa cứng: NaN/Inf, rỗng, vượt biên dòng kẻ, hoặc C_internal_collision > max_cost.
    - Không có state nào hợp lệ -> ném ngoại lệ NoValidCompositionState.
    """
    cfg = config if config is not None else DiacriticConfig()
    base_char = char_info.get("base_char", char_info.get("char", ""))
    accents = tuple(char_info.get("accents", ()))
    context = char_info.get("context", {})

    raw_strokes = char_info.get("raw_s", char_info.get("raw_strokes", []))
    if not raw_strokes and base_char in GLYPHS:
        raw_strokes = GLYPHS[base_char]

    # 1. Lấy danh sách biến thể thân chữ cơ bản
    base_variants = get_glyph_variants(base_char, raw_strokes)

    # 2. Xử lý ký tự không dấu (ASCII / no-diacritic)
    if not accents:
        return [
            CompositionState(
                base_variant=bv,
                diacritic_candidate=None,
                base_char=base_char,
                accents=(),
                context=context,
                state_tag=bv.tag,
                internal_collision_cost=0.0,
                legibility_cost=bv.cost_legibility,
                metadata={"index": char_info.get("index", 0), "bv_tag": bv.tag}
            )
            for bv in base_variants
        ]

    # 3. Sinh danh sách ứng viên cấu hình dấu
    diacritic_candidates = generate_diacritic_candidates(
        base_char=base_char,
        accents=accents,
        char_info=char_info,
        font_pack=font_pack,
        config=cfg,
    )

    # 4. Tổ hợp tích Descartes và Cắt tỉa bất hợp lệ cứng (Hard Invalid Pruning)
    valid_states: List[CompositionState] = []
    line_top_bound = char_info.get("line_top_bound_local", float("inf"))
    line_bot_bound = char_info.get("line_bottom_bound_local", -float("inf"))

    scale_vec = tuple(char_info.get("scale_vec", (1.0, 1.0)))

    for bv in base_variants:
        for dc in diacritic_candidates:
            # Cắt tỉa cứng 0: Dữ liệu hình học rỗng hoặc chứa NaN/Inf
            if not dc.strokes_local or any(
                len(s) == 0 or np.isnan(s).any() or np.isinf(s).any()
                for s in dc.strokes_local
            ):
                continue

            # Cắt tỉa cứng 1: Va chạm nội tại vượt ngưỡng trần cứng
            internal_cost = compute_internal_collision_cost(
                base_strokes_local=bv.strokes,
                diacritic_strokes_local=dc.strokes_local,
                scale_vec=scale_vec,
                tolerance_mm=cfg.internal_collision_tolerance_mm,
                clearance_threshold_mm=cfg.clearance_threshold_mm,
                max_internal_collision_cost=cfg.max_internal_collision_cost,
                base_char=base_char,
                accents=accents,
            )
            if internal_cost > cfg.max_internal_collision_cost:
                continue

            # Cắt tỉa cứng 2: Dấu vượt trần hoặc đáy dòng chữ
            if dc.bounds_local[3] > line_top_bound or dc.bounds_local[1] < line_bot_bound:
                continue

            state_tag = f"{bv.tag}_{dc.placement_tag}"
            valid_states.append(CompositionState(
                base_variant=bv,
                diacritic_candidate=dc,
                base_char=base_char,
                accents=accents,
                context=context,
                state_tag=state_tag,
                internal_collision_cost=internal_cost,
                legibility_cost=bv.cost_legibility,
                metadata={
                    "index": char_info.get("index", 0),
                    "bv_tag": bv.tag,
                    "dc_tag": dc.placement_tag,
                }
            ))

    # 5. Xử lý kết quả: Tuyệt đối không hồi sinh candidate bị loại bởi hard constraints
    if valid_states:
        return valid_states

    raise NoValidCompositionState(
        f"Không tìm thấy CompositionState hợp lệ cho ký tự '{base_char}' với dấu {accents}. "
        "Toàn bộ ứng viên đã bị loại bỏ bởi Hard Invalid Constraints."
    )


# =============================================================================
# 6. Biến đổi Hình học Sang Tọa độ Thế giới (Local-to-World Transform Helper)
# =============================================================================

def transform_state_to_world(
    state: CompositionState,
    scale_vec: Any = (1.0, 1.0),
    offset: Any = (0.0, 0.0),
    word_origin_x: Optional[float] = None,
    baseline_y: Optional[float] = None,
    scale: Optional[float] = None,
) -> Tuple[Tuple[np.ndarray, ...], Tuple[np.ndarray, ...]]:
    """
    Chuyển đổi toàn bộ nét của CompositionState từ tọa độ cục bộ sang tọa độ trang giấy (World, mm).
    Tuân thủ hợp đồng đơn khung E4:
    - Base: p_w = p_l * scale_vec + offset
    - Diacritic: p_w = (p_l_canon * scale_vec) + offset + [dx_mm, dy_mm]
    Trả về: (world_base_strokes, world_diacritic_strokes)
    """
    # Hỗ trợ cú pháp tương thích Docs 07 (word_origin_x, baseline_y, scale)
    if word_origin_x is not None and baseline_y is not None:
        sc = 1.0 if scale is None else float(scale)
        s_vec = np.array([sc, sc], dtype=float)
        off = np.array([float(word_origin_x), float(baseline_y)], dtype=float)
    else:
        if isinstance(scale_vec, (int, float)):
            s_vec = np.array([float(scale_vec), float(scale_vec)], dtype=float)
        else:
            s_vec = np.asarray(scale_vec, dtype=float)
        off = np.asarray(offset, dtype=float)

    # 1. Biến đổi nét thân chữ
    world_base = tuple(
        s.astype(float) * s_vec + off
        for s in state.base_variant.strokes
    )

    # 2. Biến đổi nét dấu (nếu có)
    world_diacritic: Tuple[np.ndarray, ...] = ()
    if state.diacritic_candidate is not None:
        dc = state.diacritic_candidate
        shift_vec = np.array([dc.dx, dc.dy], dtype=float)
        if dc.canonical_strokes_local:
            world_diacritic = tuple(
                s.astype(float) * s_vec + off + shift_vec
                for s in dc.canonical_strokes_local
            )
        else:
            world_diacritic = tuple(
                s.astype(float) * s_vec + off
                for s in dc.strokes_local
            )

    return world_base, world_diacritic


def build_glyph_world_geometry(
    state: CompositionState,
    scale_vec: Any = (1.0, 1.0),
    offset: Any = (0.0, 0.0),
) -> GlyphWorldGeometry:
    """
    Dựng toàn bộ hình học của CompositionState trong hệ tọa độ thế giới (world mm),
    bao gồm điểm đón/thoát, tiếp tuyến chuẩn hóa và polylines.
    """
    if isinstance(scale_vec, (int, float)):
        s_vec = np.array([float(scale_vec), float(scale_vec)], dtype=float)
    else:
        s_vec = np.asarray(scale_vec, dtype=float)
    off = np.asarray(offset, dtype=float)

    bv = state.base_variant

    # Điểm vào/ra trong world frame
    p_en = bv.entry_pt.astype(float) * s_vec + off
    p_ex = bv.exit_pt.astype(float) * s_vec + off

    # Tiếp tuyến trong world frame chuẩn hóa
    v_en_scaled = bv.v_entry.astype(float) * s_vec
    norm_en = float(np.linalg.norm(v_en_scaled))
    v_en = v_en_scaled / (norm_en + 1e-6)

    v_ex_scaled = bv.v_exit.astype(float) * s_vec
    norm_ex = float(np.linalg.norm(v_ex_scaled))
    v_ex = v_ex_scaled / (norm_ex + 1e-6)

    w_base, w_diac = transform_state_to_world(state, scale_vec=s_vec, offset=off)

    return GlyphWorldGeometry(
        p_entry=p_en,
        p_exit=p_ex,
        v_entry=v_en,
        v_exit=v_ex,
        base_strokes=w_base,
        diacritic_strokes=w_diac,
    )


# =============================================================================
# 7. Đánh giá Chuyển tiếp Trạng thái (Hợp đồng E4: evaluate_composition_transition)
# =============================================================================

def evaluate_composition_transition(
    prev_state: CompositionState,
    curr_state: CompositionState,
    prev_world: GlyphWorldGeometry,
    curr_world: GlyphWorldGeometry,
    transition_weights: Optional[TransitionWeights] = None,
    diacritic_config: Optional[DiacriticConfig] = None,
    force_lift: bool = False,
    scale_hint: float = 1.0,
) -> TransitionResult:
    """
    Đánh giá chi phí chuyển tiếp J_transition(prev, curr) giữa hai node CompositionState theo Hợp đồng E4:
    - Nhánh LIFT: J_lift = w1 * D_penup + w2 * N_lift (N_lift = 1).
    - Nhánh CONNECT: J_conn = w3 * C_curvature + w4 * C_bridge_collision.
    - Cắt tỉa cứng (Hard reject): Gán J_conn = +inf nếu vi phạm hard clearance hoặc giao cắt dấu.
    - Kết quả: Chọn min(J_conn, J_lift); nếu cả hai không hợp lệ -> REJECT (+inf).
    - Không chứa cost_legibility (đã chuyển hoàn toàn sang C_state).
    """
    tw = transition_weights if transition_weights is not None else TransitionWeights()
    cfg = diacritic_config if diacritic_config is not None else DiacriticConfig()

    p_exit = prev_world.p_exit
    p_entry = curr_world.p_entry
    v_exit = prev_world.v_exit
    v_entry = curr_world.v_entry

    d_vec = p_entry - p_exit
    dist = float(np.linalg.norm(d_vec))
    dx = float(d_vec[0])

    # Nhánh LIFT: Quãng đường penup + chi phí phạt nhấc bút
    cost_lift = tw.w_penup * dist + tw.w_lift * 1.0

    if force_lift:
        return TransitionResult(
            is_valid=True,
            decision="LIFT",
            total_cost=float(cost_lift),
            breakdown=TransitionCostBreakdown(
                d_penup_mm=dist,
                n_lift=1,
                c_curvature=0.0,
                c_bridge_collision=0.0,
                total_cost=float(cost_lift),
            ),
            bridge_strokes=None,
        )

    # Kiểm tra điều kiện hình học cho phép nối nét
    u = prev_state.base_variant
    w = curr_state.base_variant
    can_connect = (u.can_out and w.can_in and dx > -0.2 and dist < 12.0)

    if not can_connect:
        return TransitionResult(
            is_valid=True,
            decision="LIFT",
            total_cost=float(cost_lift),
            breakdown=TransitionCostBreakdown(
                d_penup_mm=dist,
                n_lift=1,
                c_curvature=0.0,
                c_bridge_collision=0.0,
                total_cost=float(cost_lift),
            ),
            bridge_strokes=None,
        )

    # 1. Chi phí bẻ góc tiếp tuyến (Curvature Cost)
    if dist > 1e-4:
        u_d = d_vec / dist
        cos1 = float(np.clip(np.dot(v_exit, u_d), -1.0, 1.0))
        cos2 = float(np.clip(np.dot(u_d, v_entry), -1.0, 1.0))
        c_curvature = (1.0 - cos1) + (1.0 - cos2)
    else:
        c_curvature = 0.0

    # 2. Dựng candidate bridge trong world frame
    candidate_br = build_ligature_bridge(p_exit, v_exit, p_entry, v_entry, scale_hint=scale_hint, n=6)

    # 3. Kiểm tra va chạm Bridge với 4 tập nét ở world frame:
    # prev_base, prev_diacritic, curr_base, curr_diacritic (Docs 18 Section 2.2 line 99)
    all_diac_strokes = list(prev_world.diacritic_strokes) + list(curr_world.diacritic_strokes)
    c_diac_collision = 0.0
    diac_hard_collision = False

    for ds in all_diac_strokes:
        if len(ds) == 0:
            continue
        d = _stroke_min_distance(candidate_br, ds)
        # Va chạm cứng: cắt qua nét dấu hoặc khoảng hở <= tolerance
        if d <= cfg.internal_collision_tolerance_mm:
            diac_hard_collision = True
            break
        # Phạt mềm nếu lấn vào vùng an toàn clearance
        if d < cfg.clearance_threshold_mm:
            pen = (cfg.clearance_threshold_mm - d) / (cfg.clearance_threshold_mm if cfg.clearance_threshold_mm > 0 else 1.0)
            c_diac_collision += 4.0 * pen

    if diac_hard_collision:
        cost_conn = float("inf")
    else:
        # Kiểm tra va chạm với thân chữ (base strokes)
        c_base = bridge_collision_cost(
            candidate_br,
            prev_strokes=prev_world.base_strokes,
            curr_strokes=curr_world.base_strokes,
            scale_hint=scale_hint,
        )
        if c_base >= 6.0:  # Xuyên thấu thân chữ nghiêm trọng
            cost_conn = float("inf")
        else:
            c_collision = c_base + c_diac_collision
            if dx <= 0.0:
                c_collision += 2.0
            if dist > 8.0:
                c_collision += (dist - 8.0) * 0.4
            cost_conn = tw.w_curvature * c_curvature + tw.w_bridge_collision * c_collision

    # 4. Phán quyết nhánh tối ưu: min(J_conn, J_lift)
    if cost_conn < cost_lift and not math.isinf(cost_conn):
        return TransitionResult(
            is_valid=True,
            decision="CONNECT",
            total_cost=float(cost_conn),
            breakdown=TransitionCostBreakdown(
                d_penup_mm=0.0,
                n_lift=0,
                c_curvature=float(c_curvature),
                c_bridge_collision=float(c_collision),
                total_cost=float(cost_conn),
            ),
            bridge_strokes=[candidate_br],
        )
    else:
        return TransitionResult(
            is_valid=True,
            decision="LIFT",
            total_cost=float(cost_lift),
            breakdown=TransitionCostBreakdown(
                d_penup_mm=dist,
                n_lift=1,
                c_curvature=0.0,
                c_bridge_collision=0.0,
                total_cost=float(cost_lift),
            ),
            bridge_strokes=None,
        )


# =============================================================================
# 8. Thuật toán Quy hoạch Động Viterbi Diacritic-Aware Trellis DAG
# =============================================================================

def optimize_word_composition_dag(
    char_info_list: List[Dict[str, Any]],
    transition_weights: Optional[TransitionWeights] = None,
    diacritic_config: Optional[DiacriticConfig] = None,
    font_pack: Optional[Dict[str, Any]] = None,
    force_lift: bool = False,
    scale_hint: float = 1.0,
) -> Dict[str, Any]:
    """
    Quy hoạch động Viterbi DP trên Diacritic-Aware Trellis DAG:
    - Layer: CompositionState = (GlyphVariant, DiacriticCandidate)
    - Kích thước không gian trạng thái: K_raw <= 9 mỗi layer
    - Hàm mục tiêu Bellman: DP[i, j] = C_state(s[i, j]) + min_p (DP[i-1, p] + J_transition(prev, curr))
    - Fail-closed: Nếu không tìm thấy đường đi hợp lệ -> ném ngoại lệ NoValidCompositionState.
    """
    n = len(char_info_list)
    if n == 0:
        return {
            "states": [],
            "transitions": [],
            "conns": [],
            "bridge_strokes": [],
            "total_cost": 0.0,
        }

    tw = transition_weights if transition_weights is not None else TransitionWeights()
    cfg = diacritic_config if diacritic_config is not None else DiacriticConfig()

    # 1. Xây dựng tập CompositionState và GlyphWorldGeometry cho từng layer
    states_per_char: List[List[CompositionState]] = []
    world_per_char: List[List[GlyphWorldGeometry]] = []

    for item in char_info_list:
        states = build_composition_states(item, font_pack=font_pack, config=cfg)
        if not states:
            raise NoValidCompositionState(
                f"Ký tự '{item.get('char', '')}' không còn CompositionState nào hợp lệ."
            )
        scale_vec = item.get("scale_vec", np.array([1.0, 1.0]))
        offset = item.get("offset", np.array([0.0, 0.0]))
        geoms = [build_glyph_world_geometry(s, scale_vec=scale_vec, offset=offset) for s in states]
        states_per_char.append(states)
        world_per_char.append(geoms)

    # Trường hợp từ đơn 1 ký tự
    if n == 1:
        costs = [compute_state_cost(s, config=cfg) for s in states_per_char[0]]
        best_j = int(np.argmin(costs))
        return {
            "states": [states_per_char[0][best_j]],
            "transitions": [],
            "conns": [],
            "bridge_strokes": [],
            "total_cost": float(costs[best_j]),
        }

    # 2. Khởi tạo Base Case (Layer 0)
    dp: List[Dict[int, float]] = [{} for _ in range(n)]
    bp: List[Dict[int, int]] = [{} for _ in range(n)]
    tr_map: List[Dict[int, Optional[TransitionResult]]] = [{} for _ in range(n)]

    for j, s in enumerate(states_per_char[0]):
        dp[0][j] = compute_state_cost(s, config=cfg)
        bp[0][j] = -1
        tr_map[0][j] = None

    # 3. Bước truy hồi Viterbi (Inductive Step)
    for i in range(1, n):
        curr_states = states_per_char[i]
        curr_geoms = world_per_char[i]
        prev_states = states_per_char[i - 1]
        prev_geoms = world_per_char[i - 1]

        for j, (curr_s, curr_w) in enumerate(zip(curr_states, curr_geoms)):
            c_state = compute_state_cost(curr_s, config=cfg)
            best_cost = float("inf")
            best_p = -1
            best_tr: Optional[TransitionResult] = None

            for p, (prev_s, prev_w) in enumerate(zip(prev_states, prev_geoms)):
                prev_dp = dp[i - 1].get(p, float("inf"))
                if math.isinf(prev_dp):
                    continue

                tr = evaluate_composition_transition(
                    prev_state=prev_s,
                    curr_state=curr_s,
                    prev_world=prev_w,
                    curr_world=curr_w,
                    transition_weights=tw,
                    diacritic_config=cfg,
                    force_lift=force_lift,
                    scale_hint=scale_hint,
                )

                if not tr.is_valid or math.isinf(tr.total_cost):
                    continue

                total_c = prev_dp + tr.total_cost + c_state
                if total_c < best_cost:
                    best_cost = total_c
                    best_p = p
                    best_tr = tr

            dp[i][j] = best_cost
            bp[i][j] = best_p
            tr_map[i][j] = best_tr

    # 4. Kết thúc và Truy ngược đường đi (Termination & Backtracking)
    last_dp = dp[n - 1]
    valid_costs = [(c, j) for j, c in last_dp.items() if not math.isinf(c)]
    if not valid_costs:
        raise NoValidCompositionState(
            "Không tìm thấy đường đi hợp lệ qua toàn bộ từ trong Diacritic-Aware Trellis DAG. "
            "Toàn bộ transitions hoặc states đã bị loại bỏ bởi ràng buộc cứng (Fail-closed)."
        )

    best_total_cost, best_last_j = min(valid_costs)

    chosen_states: List[CompositionState] = [None] * n  # type: ignore
    chosen_transitions: List[TransitionResult] = [None] * (n - 1)  # type: ignore
    curr_j = best_last_j

    for i in range(n - 1, 0, -1):
        chosen_states[i] = states_per_char[i][curr_j]
        chosen_transitions[i - 1] = tr_map[i][curr_j]  # type: ignore
        curr_j = bp[i][curr_j]

    chosen_states[0] = states_per_char[0][curr_j]

    conns = [tr.decision == "CONNECT" for tr in chosen_transitions]
    bridge_strokes = [
        (tr.bridge_strokes[0] if (tr and tr.bridge_strokes) else None)
        for tr in chosen_transitions
    ]

    return {
        "states": chosen_states,
        "transitions": chosen_transitions,
        "conns": conns,
        "bridge_strokes": bridge_strokes,
        "total_cost": float(best_total_cost),
    }

