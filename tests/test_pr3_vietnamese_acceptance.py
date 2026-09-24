"""
Tests Nghiệm Thu CA-VHC Tiếng Việt Cho PR3 (Slice 2-5)
======================================================
Kiểm thử tự động theo Hợp đồng Nghiệm thu Kỹ thuật Docs 09 và Docs 17 (Mục 6):
1. test_pr3_vietnamese_unicode_nfd_mark_preservation
2. test_pr3_vietnamese_zero_collision
3. test_pr3_vietnamese_clearance_threshold
4. test_viterbi_synthetic_trellis_optimality
5. test_pr3_trellis_dev_specimens_run_safely
6. test_pr3_state_layer_bound_is_at_most_nine
7. test_pr3_same_seed_is_deterministic
8. test_pr3_renderer_does_not_duplicate_diacritics
"""

import numpy as np
import pytest
import unicodedata

from backend.handwriting.benchmark_fixtures import (
    PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS,
    STANDARD_SEEDS,
    load_benchmark_fonts,
)
from backend.handwriting.composition import (
    DiacriticConfig,
    DiacriticCandidate,
    CompositionState,
    build_composition_states,
    build_glyph_world_geometry,
    evaluate_composition_transition,
    compute_bounds_local,
    compute_state_cost,
    optimize_word_composition_dag,
)
from backend.handwriting.engine import (
    GLYPHS,
    build_ligature_bridge,
    text_to_strokes,
    text_to_strokes_structured,
)
from backend.handwriting.metrics_evaluator import (
    evaluate_ca_vhc_metrics,
    classify_diacritic_clearance_acceptance,
    compute_stroke_fingerprint,
)


# =============================================================================
# 1. test_pr3_vietnamese_unicode_nfd_mark_preservation
# =============================================================================

def test_pr3_vietnamese_unicode_nfd_mark_preservation():
    """
    Kiểm tra bảo toàn bản sắc chữ viết Unicode NFD trên 10 tiêu bản DEV acceptance:
    - Số nét dấu (diacritic_stroke) trong trace của Proposed mode phải khớp chính xác
      với số nét dấu của B3 baseline.
    - Không làm mất dấu, không gán thiếu dấu.
    """
    for word in PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS:
        res_b3 = text_to_strokes_structured(
            word, font="oly", style="hand_hocsinh", seed=42, _algorithm_mode="b3_current_trellis"
        )
        res_prop = text_to_strokes_structured(
            word, font="oly", style="hand_hocsinh", seed=42, _algorithm_mode="proposed_ca_vhc"
        )

        diac_b3 = [t for t in res_b3.trace if t.stroke_type == "diacritic_stroke"]
        diac_prop = [t for t in res_prop.trace if t.stroke_type == "diacritic_stroke"]

        assert len(diac_prop) == len(diac_b3), (
            f"Từ '{word}': số nét dấu Proposed ({len(diac_prop)}) không khớp B3 ({len(diac_b3)})"
        )

        # Đếm số combining mark kỳ vọng từ NFD
        nfd_text = unicodedata.normalize("NFD", word)
        expected_marks_count = sum(1 for ch in nfd_text if unicodedata.combining(ch))
        assert len(diac_prop) >= expected_marks_count, (
            f"Từ '{word}': số nét dấu ({len(diac_prop)}) ít hơn số dấu NFD ({expected_marks_count})"
        )


# =============================================================================
# 2. test_pr3_vietnamese_zero_collision
# =============================================================================

def test_pr3_vietnamese_zero_collision():
    """
    Kiểm tra va chạm bridge–diacritic trên 10 tiêu bản DEV acceptance:
    - Thuật toán CA-VHC Proposed phải đạt collision_count == 0.
    """
    for word in PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS:
        res = text_to_strokes_structured(
            word, font="oly", style="hand_hocsinh", seed=42, _algorithm_mode="proposed_ca_vhc"
        )
        metrics = evaluate_ca_vhc_metrics(res)
        assert metrics["collision_count"] == 0, (
            f"Từ '{word}' xuất hiện {metrics['collision_count']} va chạm bridge–diacritic"
        )


# =============================================================================
# 3. test_pr3_vietnamese_clearance_threshold
# =============================================================================

def test_pr3_vietnamese_clearance_threshold():
    """
    Kiểm tra khoảng cách an toàn (clearance threshold) trên 10 tiêu bản DEV acceptance:
    - Phân loại nghiệm thu classify_diacritic_clearance_acceptance tuyệt đối không trả FAIL.
    """
    for word in PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS:
        res = text_to_strokes_structured(
            word, font="oly", style="hand_hocsinh", seed=42, _algorithm_mode="proposed_ca_vhc"
        )
        metrics = evaluate_ca_vhc_metrics(res)
        colls = metrics["collision_count"]
        clr = metrics["minimum_diacritic_clearance_mm"]
        verdict = classify_diacritic_clearance_acceptance(colls, clr)

        assert verdict != "FAIL", (
            f"Từ '{word}' nhận phán quyết FAIL với khoảng hở {clr:.4f} mm"
        )


# =============================================================================
# 4. test_viterbi_synthetic_trellis_optimality
# =============================================================================

def test_viterbi_synthetic_trellis_optimality():
    """
    Kiểm tra tính tối ưu toán học của Viterbi DP trên Trellis DAG tổng hợp:
    - Xây dựng 2 đường đi:
      + Đường đi A (Canonical): nét dấu bị cầu nối cắt ngang -> vi phạm hard collision -> ép nhấc bút (cost cao).
      + Đường đi B (Safe): nét dấu được dịch chuyển an toàn né cầu nối -> cho phép nối nét mượt mà (cost thấp).
    - Viterbi DP bắt buộc phải chọn Đường đi B (Safe).
    """
    # Ký tự 1: 'e' ở x=0.0
    se = build_composition_states({"char": "e", "raw_s": GLYPHS["e"], "accents": ()})[0]
    we = build_glyph_world_geometry(se, scale_vec=np.array([1.0, 1.0]), offset=np.array([0.0, 0.0]))

    # Ký tự 2: 'i' ở x=10.0
    si_raw = build_composition_states({"char": "i", "raw_s": GLYPHS["i"], "accents": ("\u0301",)})[0]
    wi_raw = build_glyph_world_geometry(si_raw, scale_vec=np.array([1.0, 1.0]), offset=np.array([10.0, 0.0]))

    # Tìm trung điểm quỹ đạo cầu nối giữa e và i
    br = build_ligature_bridge(we.p_exit, we.v_exit, wi_raw.p_entry, wi_raw.v_entry)
    mid_pt = br[len(br) // 2]

    # Đặt nét dấu canonical cắt ngang qua cầu nối (trong local frame của i)
    local_mid = mid_pt - np.array([10.0, 0.0])
    colliding_stroke = np.array([local_mid - np.array([0.0, 1.0]), local_mid + np.array([0.0, 1.0])])

    # Đặt nét dấu safe dời lên trên 10mm (xa khỏi cầu nối)
    safe_stroke = colliding_stroke - np.array([0.0, 10.0])

    cand_collide = DiacriticCandidate(
        marks=("\u0301",), placement_tag="canonical",
        strokes_local=(colliding_stroke,), anchor_x=5.0, anchor_y=0.0,
        dx=0.0, dy=0.0, bounds_local=compute_bounds_local((colliding_stroke,)),
        clearance_zone_local=(), placement_penalty=0.0, canonical_strokes_local=(colliding_stroke,)
    )
    cand_safe = DiacriticCandidate(
        marks=("\u0301",), placement_tag="safe_right",
        strokes_local=(safe_stroke,), anchor_x=5.0, anchor_y=0.0,
        dx=1.0, dy=0.0, bounds_local=compute_bounds_local((safe_stroke,)),
        clearance_zone_local=(), placement_penalty=0.1, canonical_strokes_local=(safe_stroke,)
    )

    s_collide = CompositionState(
        base_variant=si_raw.base_variant, diacritic_candidate=cand_collide,
        base_char="i", accents=("\u0301",), context={}, state_tag="std_canonical",
        internal_collision_cost=0.0, legibility_cost=0.0
    )
    s_safe = CompositionState(
        base_variant=si_raw.base_variant, diacritic_candidate=cand_safe,
        base_char="i", accents=("\u0301",), context={}, state_tag="std_safe_right",
        internal_collision_cost=0.0, legibility_cost=0.0
    )

    w_collide = build_glyph_world_geometry(s_collide, scale_vec=np.array([1.0, 1.0]), offset=np.array([10.0, 0.0]))
    w_safe = build_glyph_world_geometry(s_safe, scale_vec=np.array([1.0, 1.0]), offset=np.array([10.0, 0.0]))

    tr_c = evaluate_composition_transition(se, s_collide, we, w_collide)
    tr_s = evaluate_composition_transition(se, s_safe, we, w_safe)

    assert tr_c.decision == "LIFT", "Nét dấu va chạm với bridge bắt buộc phải ép nhấc bút (LIFT)"
    assert tr_s.decision == "CONNECT", "Nét dấu an toàn phải cho phép nối nét liền (CONNECT)"

    dp0 = compute_state_cost(se)
    cost_collide_path = dp0 + tr_c.total_cost + compute_state_cost(s_collide)
    cost_safe_path = dp0 + tr_s.total_cost + compute_state_cost(s_safe)

    assert cost_safe_path < cost_collide_path, (
        f"Chi phí đường an toàn ({cost_safe_path:.4f}) phải nhỏ hơn đường va chạm ({cost_collide_path:.4f})"
    )


# =============================================================================
# 5. test_pr3_trellis_dev_specimens_run_safely
# =============================================================================

def test_pr3_trellis_dev_specimens_run_safely():
    """
    Chạy an toàn 10 tiêu bản DEV acceptance trên cả 2 font và 4 standard seeds:
    - 0 lỗi crash.
    - Toàn bộ tọa độ nét đầu ra là số thực hữu hạn (np.isfinite).
    """
    for font_id in ("oly", "omni_casual"):
        for seed in STANDARD_SEEDS:
            for word in PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS:
                strokes = text_to_strokes(
                    word, font=font_id, style="hand_hocsinh", seed=seed, _algorithm_mode="proposed_ca_vhc"
                )
                assert len(strokes) > 0, f"'{word}' (font={font_id}, seed={seed}) trả về rỗng"
                for s in strokes:
                    assert np.isfinite(s).all(), f"Tọa độ nét chứa NaN/Inf trong '{word}'"


# =============================================================================
# 6. test_pr3_state_layer_bound_is_at_most_nine
# =============================================================================

def test_pr3_state_layer_bound_is_at_most_nine():
    """
    Kiểm tra chặn trên không gian trạng thái thô:
    - Với mọi ký tự trong 10 tiêu bản DEV acceptance:
      Số trạng thái tại mỗi layer phải thỏa mãn 1 <= K <= 9.
    """
    config = DiacriticConfig()
    fonts = load_benchmark_fonts()
    for word in PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS:
        # Tách từng cụm grapheme
        nfd_word = unicodedata.normalize("NFD", word)
        idx = 0
        while idx < len(nfd_word):
            b_char = nfd_word[idx]
            idx += 1
            acc_list = []
            while idx < len(nfd_word) and unicodedata.combining(nfd_word[idx]):
                acc_list.append(nfd_word[idx])
                idx += 1

            if b_char in GLYPHS:
                info = {
                    "char": b_char,
                    "raw_s": GLYPHS[b_char],
                    "accents": tuple(acc_list),
                    "cx": 5.0,
                }
                font_pack = fonts["oly"]["font_pack"] if isinstance(fonts["oly"], dict) else fonts["oly"][0]
                states = build_composition_states(info, font_pack=font_pack, config=config)
                assert 1 <= len(states) <= 9, (
                    f"Ký tự '{b_char}' mang dấu {acc_list} có {len(states)} states, vượt trần 9"
                )


# =============================================================================
# 7. test_pr3_same_seed_is_deterministic
# =============================================================================

def test_pr3_same_seed_is_deterministic():
    """
    Kiểm tra tính tất định tuyệt đối:
    - Cùng một từ, cùng một seed=42 chạy qua Proposed mode:
      Toàn bộ nét và fingerprint phải trùng khớp 100%.
    """
    for word in PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS:
        res1 = text_to_strokes_structured(
            word, font="oly", style="hand_hocsinh", seed=42, _algorithm_mode="proposed_ca_vhc"
        )
        res2 = text_to_strokes_structured(
            word, font="oly", style="hand_hocsinh", seed=42, _algorithm_mode="proposed_ca_vhc"
        )

        assert len(res1.strokes) == len(res2.strokes)
        assert len(res1.trace) == len(res2.trace)

        for s1, s2 in zip(res1.strokes, res2.strokes):
            assert np.allclose(s1, s2, atol=1e-6), f"Lệch tọa độ trong từ '{word}' giữa 2 lần chạy"

        fp1 = compute_stroke_fingerprint(res1.strokes)
        fp2 = compute_stroke_fingerprint(res2.strokes)
        assert fp1 == fp2, f"Lệch fingerprint trong từ '{word}' giữa 2 lần chạy"


# =============================================================================
# 8. test_pr3_renderer_does_not_duplicate_diacritics
# =============================================================================

def test_pr3_renderer_does_not_duplicate_diacritics():
    """
    Kiểm tra chống double-render:
    - Proposed mode lấy dấu trực tiếp từ CompositionState và chặn generate_accents() hậu DAG.
    - Đảm bảo số nét diacritic_stroke bằng chính xác số nét dấu dự kiến, không bị nhân đôi.
    """
    for word in PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS:
        res = text_to_strokes_structured(
            word, font="oly", style="hand_hocsinh", seed=42, _algorithm_mode="proposed_ca_vhc"
        )
        diac_strokes = [t for t in res.trace if t.stroke_type == "diacritic_stroke"]

        # So sánh với B3: số lượng nét dấu phải bằng nhau
        res_b3 = text_to_strokes_structured(
            word, font="oly", style="hand_hocsinh", seed=42, _algorithm_mode="b3_current_trellis"
        )
        diac_b3 = [t for t in res_b3.trace if t.stroke_type == "diacritic_stroke"]

        assert len(diac_strokes) == len(diac_b3), (
            f"Từ '{word}': số nét dấu ({len(diac_strokes)}) khác với B3 ({len(diac_b3)}), "
            "có thể bị double-render hoặc thiếu dấu!"
        )
