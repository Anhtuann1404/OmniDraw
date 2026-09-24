"""
Tests cho Module CA-VHC CompositionState và DiacriticCandidate (PR3 Slice 1)
=============================================================================
Kiểm thử 10 ca kiểm thử theo đặc tả Docs 07 (Mục 14.1) và Docs 17 (Mục 6):
1. test_composition_state_without_accent
2. test_acute_accent_candidate_generation
3. test_circumflex_acute_geometry_clearance
4. test_circumflex_acute_internal_collision_cost
5. test_horn_tone_candidate_generation
6. test_dot_below_candidate_generation
7. test_internal_diacritic_base_collision
8. test_candidate_pruning_never_revives_hard_invalid
9. test_composition_state_is_immutable
10. test_transform_state_to_world_uses_single_frame_contract
"""

from dataclasses import FrozenInstanceError
import math
import numpy as np
import pytest

from backend.handwriting.composition import (
    DiacriticConfig,
    DiacriticCandidate,
    CompositionState,
    TransitionWeights,
    TransitionCostBreakdown,
    TransitionResult,
    GlyphWorldGeometry,
    NoValidCompositionState,
    compute_bounds_local,
    compute_clearance_zone_local,
    compute_internal_clearance_mm,
    compute_internal_collision_cost,
    compute_state_cost,
    generate_diacritic_candidates,
    build_composition_states,
    transform_state_to_world,
    build_glyph_world_geometry,
)
from backend.handwriting.engine import (
    GLYPHS,
    GLYPH_CENTERS,
    _stroke_min_distance,
)


# =============================================================================
# 1. test_composition_state_without_accent
# =============================================================================

def test_composition_state_without_accent():
    """
    Kiểm tra ký tự không dấu (Latinh thường):
    - Sinh đúng K_base trạng thái (K_base <= 3).
    - Mọi trạng thái đều có diacritic_candidate is None.
    - C_internal_collision = 0.0, C_placement = 0.0, legibility_cost = bv.cost_legibility.
    - C_state(s) = legibility_cost.
    """
    config = DiacriticConfig()
    for char in ("a", "m", "h", "o"):
        char_info = {
            "char": char,
            "raw_s": GLYPHS[char],
            "accents": (),
            "cx": GLYPH_CENTERS.get(char, 5.0),
        }
        states = build_composition_states(char_info, config=config)

        assert 1 <= len(states) <= 3, f"Số states của '{char}' phải <= 3, nhận {len(states)}"
        for s in states:
            assert s.diacritic_candidate is None, "Ký tự không dấu phải có diacritic_candidate is None"
            assert s.base_char == char
            assert s.accents == ()
            assert s.internal_collision_cost == 0.0, "C_internal_collision của ký tự không dấu phải bằng 0.0"
            assert s.legibility_cost == s.base_variant.cost_legibility
            assert s.state_tag == s.base_variant.tag
            assert compute_state_cost(s, config) == pytest.approx(s.base_variant.cost_legibility)


# =============================================================================
# 2. test_acute_accent_candidate_generation
# =============================================================================

def test_acute_accent_candidate_generation():
    """
    Kiểm tra nguyên âm mang dấu thanh đơn (á, é, ó):
    - Sinh đầy đủ 3 ứng viên: 'canonical', 'safe_left', 'safe_right'.
    - Độ lệch dx đọc từ config: 0.0, -0.45, +0.45.
    - Placement penalty: canonical = 0.0, safe_left = 0.45, safe_right = 0.45.
    - strokes_local của safe_left lệch trái, safe_right lệch phải so với canonical.
    """
    config = DiacriticConfig()
    for char in ("a", "e", "o"):
        candidates = generate_diacritic_candidates(
            base_char=char,
            accents=("\u0301",),  # Dấu sắc
            config=config,
        )

        assert len(candidates) == 3, f"Phải sinh đúng 3 ứng viên cho '{char}' mang dấu sắc"
        tags = [c.placement_tag for c in candidates]
        assert set(tags) == {"canonical", "safe_left", "safe_right"}

        c_canon = next(c for c in candidates if c.placement_tag == "canonical")
        c_left = next(c for c in candidates if c.placement_tag == "safe_left")
        c_right = next(c for c in candidates if c.placement_tag == "safe_right")

        # Kiểm tra dx
        assert c_canon.dx == 0.0
        assert c_left.dx == pytest.approx(-0.45)
        assert c_right.dx == pytest.approx(0.45)

        # Kiểm tra placement_penalty
        assert c_canon.placement_penalty == pytest.approx(0.0)
        assert c_left.placement_penalty == pytest.approx(0.45)
        assert c_right.placement_penalty == pytest.approx(0.45)

        # Kiểm tra tọa độ hình học thực tế của strokes_local
        # safe_left phải có X nhỏ hơn canonical, safe_right phải có X lớn hơn canonical
        canon_x_mean = np.mean([np.mean(s[:, 0]) for s in c_canon.strokes_local])
        left_x_mean = np.mean([np.mean(s[:, 0]) for s in c_left.strokes_local])
        right_x_mean = np.mean([np.mean(s[:, 0]) for s in c_right.strokes_local])

        assert left_x_mean < canon_x_mean, "safe_left phải lệch sang trái so với canonical"
        assert right_x_mean > canon_x_mean, "safe_right phải lệch sang phải so với canonical"
        assert (canon_x_mean - left_x_mean) == pytest.approx(0.45)
        assert (right_x_mean - canon_x_mean) == pytest.approx(0.45)


# =============================================================================
# 3. test_circumflex_acute_geometry_clearance
# =============================================================================

def test_circumflex_acute_geometry_clearance():
    """
    Kiểm tra hình học nguyên âm đôi phức hợp (ế, ố) theo Geometry Metric:
    - Sinh cấu trúc 2 tầng (mũ + sắc) chính xác (2 strokes trong diacritic).
    - Khoảng cách an toàn min_clearance_mm >= clearance_threshold_mm (0.20 mm).
    - Độ sâu xuyên thấu penetration <= tolerance_mm (0.05 mm) -> không giao cắt.
    """
    config = DiacriticConfig()
    for char in ("e", "o"):
        candidates = generate_diacritic_candidates(
            base_char=char,
            accents=("\u0302", "\u0301"),  # mũ + sắc
            config=config,
        )

        for dc in candidates:
            assert len(dc.strokes_local) == 2, f"'{char}' với mũ+sắc phải có đúng 2 nét dấu"
            non_stroke, sac_stroke = dc.strokes_local[0], dc.strokes_local[1]

            # Tính khoảng cách hình học thực tế giữa 2 nét
            d = _stroke_min_distance(non_stroke, sac_stroke)
            assert d >= config.clearance_threshold_mm, (
                f"Candidate {dc.placement_tag} của '{char}': khoảng cách giữa mũ và sắc "
                f"là {d:.4f} mm, phải >= {config.clearance_threshold_mm} mm"
            )


# =============================================================================
# 4. test_circumflex_acute_internal_collision_cost
# =============================================================================

def test_circumflex_acute_internal_collision_cost():
    """
    Kiểm tra chi phí phạt va chạm nội tại vô hướng C_internal_collision của mũ + sắc:
    - Chi phí phạt không âm: 0.0 <= C_internal_collision <= max_internal_collision_cost (0.50).
    - Toàn bộ candidates hợp lệ không bị cắt tỉa oan uổng.
    """
    config = DiacriticConfig()
    for char in ("e", "o"):
        char_info = {
            "char": char,
            "raw_s": GLYPHS[char],
            "accents": ("\u0302", "\u0301"),
            "cx": GLYPH_CENTERS.get(char, 5.0),
        }
        states = build_composition_states(char_info, config=config)

        assert len(states) >= 3, f"Phải giữ lại ít nhất 3 CompositionState hợp lệ cho '{char}' có mũ+sắc"
        for s in states:
            assert 0.0 <= s.internal_collision_cost <= config.max_internal_collision_cost, (
                f"State {s.state_tag} có C_internal_collision = {s.internal_collision_cost:.4f}, "
                f"vượt ngưỡng cho phép {config.max_internal_collision_cost}"
            )


# =============================================================================
# 5. test_horn_tone_candidate_generation
# =============================================================================

def test_horn_tone_candidate_generation():
    """
    Kiểm tra nguyên âm có móc (ở, ứ):
    - Đặt dấu thanh lệch chuẩn bên cạnh dấu móc theo thẩm mỹ chữ Việt.
    - Móc gắn góc trên bên phải, dấu hỏi/sắc nằm né sang bên trái của móc.
    - Khoảng cách giữa móc và dấu thanh >= clearance_threshold_mm (0.20 mm).
    - Nét móc chạm thân chữ o/u không bị tính nhầm là va chạm nội tại.
    """
    config = DiacriticConfig()
    # 'ở': 'o' + horn ('\u031b') + hook above ('\u0309')
    candidates_o = generate_diacritic_candidates(
        base_char="o",
        accents=("\u031b", "\u0309"),
        config=config,
    )
    assert len(candidates_o) == 3
    c_canon = next(c for c in candidates_o if c.placement_tag == "canonical")
    assert len(c_canon.strokes_local) == 2

    horn_stroke, hook_stroke = c_canon.strokes_local[0], c_canon.strokes_local[1]

    # Móc ở bên phải: min(X_horn) > min(X_hook)
    assert np.min(horn_stroke[:, 0]) > np.min(hook_stroke[:, 0])
    # Khoảng cách an toàn giữa móc và hỏi
    d = _stroke_min_distance(horn_stroke, hook_stroke)
    assert d >= config.clearance_threshold_mm

    # Kiểm tra không bị tính va chạm nội tại với thân chữ o
    cost_o = compute_internal_collision_cost(
        base_strokes_local=GLYPHS["o"],
        diacritic_strokes_local=c_canon.strokes_local,
        base_char="o",
        accents=("\u031b", "\u0309"),
    )
    assert cost_o <= config.max_internal_collision_cost


# =============================================================================
# 6. test_dot_below_candidate_generation
# =============================================================================

def test_dot_below_candidate_generation():
    """
    Kiểm tra dấu nặng (ạ, ệ, ọ, y):
    - Chỉ sinh 1 ứng viên canonical duy nhất nằm dưới baseline (dx = 0, dy = 0).
    - Tuyệt đối không sinh safe_left / safe_right cho dấu nặng đơn thuần.
    - Điểm Y của nét chấm nằm dưới baseline (> 14.0 mm).
    """
    config = DiacriticConfig()
    for char in ("a", "e", "o", "y"):
        dot_offset = 2.2 if char == "y" else 0.0
        char_info = {
            "char": char,
            "raw_s": GLYPHS[char],
            "accents": ("\u0323",),
            "cx": GLYPH_CENTERS.get(char, 5.0),
            "dot_below_x_offset": dot_offset,
        }
        candidates = generate_diacritic_candidates(
            base_char=char,
            accents=("\u0323",),
            char_info=char_info,
            config=config,
        )

        assert len(candidates) == 1, f"Dấu nặng cho '{char}' chỉ được có đúng 1 candidate canonical"
        c = candidates[0]
        assert c.placement_tag == "canonical"
        assert c.dx == 0.0
        assert c.dy == 0.0
        assert c.placement_penalty == 0.0

        # Nét chấm nằm dưới baseline (y > 14.0)
        dot_stroke = c.strokes_local[0]
        assert np.min(dot_stroke[:, 1]) > 14.0, f"Dấu nặng của '{char}' phải nằm dưới baseline y=14.0"


# =============================================================================
# 7. test_internal_diacritic_base_collision
# =============================================================================

def test_internal_diacritic_base_collision():
    """
    Giả lập dấu bị đặt đè lên đỉnh thân chữ:
    - Phát hiện vi phạm khoảng cách hở (min_dist <= tolerance_mm) và tính chi phí phạt nội tại C_internal_collision = 1.0 > max_cost.
    - Kiểm tra vùng đệm (tolerance < min_dist < clearance): phạt mềm (0 < cost <= 0.40).
    """
    config = DiacriticConfig()
    base_stroke = GLYPHS["e"][0]

    # 1. Nét dấu giả lập giao cắt trực tiếp qua thân chữ 'e'
    colliding_diacritic = [np.array([[1.0, 9.0], [7.0, 9.0]])]
    cost_hard = compute_internal_collision_cost(
        base_strokes_local=[base_stroke],
        diacritic_strokes_local=colliding_diacritic,
        tolerance_mm=config.internal_collision_tolerance_mm,
        clearance_threshold_mm=config.clearance_threshold_mm,
        max_internal_collision_cost=config.max_internal_collision_cost,
    )
    assert cost_hard == 1.0, "Giao cắt trực tiếp phải nhận cost va chạm cứng = 1.0"
    assert cost_hard > config.max_internal_collision_cost

    # 2. Nét dấu đặt cách thân chữ 0.10 mm (nằm giữa tolerance 0.05 và clearance 0.20)
    # y đỉnh của 'e' là 7.0, đặt ở y = 7.0 - 0.10 = 6.90
    soft_diacritic = [np.array([[4.0, 6.90], [6.0, 6.90]])]
    cost_soft = compute_internal_collision_cost(
        base_strokes_local=[base_stroke],
        diacritic_strokes_local=soft_diacritic,
        tolerance_mm=config.internal_collision_tolerance_mm,
        clearance_threshold_mm=config.clearance_threshold_mm,
        max_internal_collision_cost=config.max_internal_collision_cost,
    )
    assert 0.0 < cost_soft <= 0.40, f"Vùng đệm phải nhận phạt mềm, nhận {cost_soft}"
    assert cost_soft <= config.max_internal_collision_cost


# =============================================================================
# 8. test_candidate_pruning_never_revives_hard_invalid
# =============================================================================

def test_candidate_pruning_never_revives_hard_invalid():
    """
    Kiểm tra cơ chế cắt tỉa cứng khi candidate vi phạm hard constraints:
    - Dấu chứa NaN / Inf / rỗng bị loại bỏ hoàn toàn.
    - Dấu vượt trần dòng chữ (line_top_bound_local) bị loại bỏ.
    - Khi toàn bộ candidates bị loại: ném ngoại lệ NoValidCompositionState,
      TUYỆT ĐỐI KHÔNG hồi sinh canonical candidate bằng fallback.
    """
    config = DiacriticConfig()

    # Ca 1: Toàn bộ dấu vượt trần dòng chữ (line_top_bound = -100.0)
    info_out_of_bounds = {
        "char": "e",
        "raw_s": GLYPHS["e"],
        "accents": ("\u0302", "\u0301"),
        "cx": GLYPH_CENTERS["e"],
        "line_top_bound_local": -100.0,
    }
    with pytest.raises(NoValidCompositionState) as exc_info:
        build_composition_states(info_out_of_bounds, config=config)
    assert "Toàn bộ ứng viên đã bị loại bỏ" in str(exc_info.value)

    # Ca 2: Kiểm tra cắt tỉa va chạm nội tại cứng
    # Dùng custom config với max_internal_collision_cost cực thấp hoặc tolerance cực lớn
    info_collide = {
        "char": "e",
        "raw_s": GLYPHS["e"],
        "accents": ("\u0302", "\u0301"),
        "cx": GLYPH_CENTERS["e"],
    }
    # Đặt clearance_threshold_mm = 10.0 và tolerance = 5.0 để mọi candidate đều bị coi là va chạm cứng
    strict_config = DiacriticConfig(
        internal_collision_tolerance_mm=5.0,
        max_internal_collision_cost=0.50,
    )
    with pytest.raises(NoValidCompositionState):
        build_composition_states(info_collide, config=strict_config)


# =============================================================================
# 9. test_composition_state_is_immutable
# =============================================================================

def test_composition_state_is_immutable():
    """
    Kiểm tra tính bất biến (frozen=True) của các dataclass PR3:
    - CompositionState
    - DiacriticCandidate
    - DiacriticConfig
    - TransitionWeights
    - TransitionCostBreakdown
    - TransitionResult
    - GlyphWorldGeometry
    Mọi nỗ lực gán lại trường thuộc tính đều phải ném FrozenInstanceError.
    """
    config = DiacriticConfig()
    char_info = {
        "char": "e",
        "raw_s": GLYPHS["e"],
        "accents": ("\u0301",),
        "cx": GLYPH_CENTERS["e"],
    }
    states = build_composition_states(char_info, config=config)
    state = states[0]
    candidate = state.diacritic_candidate

    # 1. CompositionState bất biến
    with pytest.raises((FrozenInstanceError, AttributeError)):
        state.internal_collision_cost = 0.99  # type: ignore

    with pytest.raises((FrozenInstanceError, AttributeError)):
        state.base_char = "x"  # type: ignore

    # 2. DiacriticCandidate bất biến
    assert candidate is not None
    with pytest.raises((FrozenInstanceError, AttributeError)):
        candidate.dx = 1.0  # type: ignore

    with pytest.raises((FrozenInstanceError, AttributeError)):
        candidate.placement_tag = "other"  # type: ignore

    # 3. DiacriticConfig bất biến
    with pytest.raises((FrozenInstanceError, AttributeError)):
        config.clearance_threshold_mm = 0.99  # type: ignore

    # 4. Transition types bất biến
    weights = TransitionWeights()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        weights.w_penup = 99.0  # type: ignore

    breakdown = TransitionCostBreakdown(1.0, 1, 0.5, 0.0, 1.5)
    with pytest.raises((FrozenInstanceError, AttributeError)):
        breakdown.total_cost = 0.0  # type: ignore

    res = TransitionResult(True, "CONNECT", 1.5, breakdown)
    with pytest.raises((FrozenInstanceError, AttributeError)):
        res.decision = "LIFT"  # type: ignore

    gw = GlyphWorldGeometry(
        p_entry=np.array([0.0, 0.0]),
        p_exit=np.array([1.0, 1.0]),
        v_entry=np.array([1.0, 0.0]),
        v_exit=np.array([1.0, 0.0]),
        base_strokes=(),
    )
    with pytest.raises((FrozenInstanceError, AttributeError)):
        gw.base_strokes = (np.array([[0, 0]]),)  # type: ignore


# =============================================================================
# 10. test_transform_state_to_world_uses_single_frame_contract
# =============================================================================

def test_transform_state_to_world_uses_single_frame_contract():
    """
    Kiểm tra hợp đồng biến đổi tọa độ thế giới (Single Frame Contract) theo Docs 18 (Q4/Q7):
    - Biến đổi thân chữ: p_w = p_l * scale_vec + offset.
    - Biến đổi tiếp tuyến: t_w = normalize(t_l * scale_vec).
    - Biến đổi nét dấu: p_w = (p_l_canon * scale_vec) + offset + [dx_mm, dy_mm].
    - Thử nghiệm trên phép co giãn không đều (anisotropic scaling) và offset tùy ý.
    """
    config = DiacriticConfig()
    char_info = {
        "char": "e",
        "raw_s": GLYPHS["e"],
        "accents": ("\u0302", "\u0301"),
        "cx": GLYPH_CENTERS["e"],
    }
    states = build_composition_states(char_info, config=config)
    s_safe_right = next(s for s in states if s.state_tag == "std_safe_right")

    scale_vec = np.array([0.45, 0.70])
    offset = np.array([12.5, 30.0])

    # 1. Kiểm tra transform_state_to_world
    w_base, w_diac = transform_state_to_world(
        s_safe_right,
        scale_vec=scale_vec,
        offset=offset,
    )

    # Thân chữ: p_w = p_l * scale_vec + offset
    expected_base = s_safe_right.base_variant.strokes[0] * scale_vec + offset
    assert np.allclose(w_base[0], expected_base), "Biến đổi thân chữ không khớp công thức affine"

    # Dấu: p_w = (p_canon * scale_vec) + offset + [dx, dy]
    dc = s_safe_right.diacritic_candidate
    assert dc is not None
    shift_vec = np.array([dc.dx, dc.dy])
    expected_diac_0 = dc.canonical_strokes_local[0] * scale_vec + offset + shift_vec
    assert np.allclose(w_diac[0], expected_diac_0), "Biến đổi dấu không khớp công thức world shift Q7"

    # 2. Kiểm tra build_glyph_world_geometry và chuẩn hóa tiếp tuyến
    gw = build_glyph_world_geometry(s_safe_right, scale_vec=scale_vec, offset=offset)

    # Điểm vào/ra
    expected_p_en = s_safe_right.base_variant.entry_pt * scale_vec + offset
    expected_p_ex = s_safe_right.base_variant.exit_pt * scale_vec + offset
    assert np.allclose(gw.p_entry, expected_p_en)
    assert np.allclose(gw.p_exit, expected_p_ex)

    # Tiếp tuyến phải được chuẩn hóa (norm == 1.0)
    assert np.isclose(np.linalg.norm(gw.v_entry), 1.0)
    assert np.isclose(np.linalg.norm(gw.v_exit), 1.0)

    # Hướng tiếp tuyến world phải cùng phương với (t_l * scale_vec)
    expected_v_en = (s_safe_right.base_variant.v_entry * scale_vec) / np.linalg.norm(
        s_safe_right.base_variant.v_entry * scale_vec
    )
    expected_v_ex = (s_safe_right.base_variant.v_exit * scale_vec) / np.linalg.norm(
        s_safe_right.base_variant.v_exit * scale_vec
    )
    assert np.allclose(gw.v_entry, expected_v_en)
    assert np.allclose(gw.v_exit, expected_v_ex)
