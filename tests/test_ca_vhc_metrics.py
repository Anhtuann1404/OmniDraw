"""
Unit tests for PR1: CA-VHC Metrics, Structured Render Trace, and Benchmark Fixtures.

Covers:
1. Zero-collision scenario: safe text has collision_count == 0
2. Synthetic collision: bridge crossing diacritic mark detected accurately
3. Valid endpoint contact: endpoint touching is not counted as collision
4. Clearance calculation: known geometric distance between parallel segments
5. Curvature cost: turning cost formula verified for 0, 90, 180 degrees and vectors
6. Absolute backward compatibility: text_to_strokes bit-exact parity across 20 dev words x 2 fonts x 2 seeds
7. Stroke tagging coverage: base_stroke, bridge_stroke, secondary_stroke, diacritic_stroke present and tagged
8. Edge cases: empty text, 1-character text, combined accent text
9. Malformed input handling: strokes with NaN, Inf, and single-point strokes
10. Corpus disjointness: dev and holdout corpora have zero intersection and len == 20
"""

import math
import os
import sys
import numpy as np
import pytest

# Ensure backend and repo root are in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.abspath(os.path.join(_current_dir, ".."))
_backend_dir = os.path.join(_repo_root, "backend")
for p in (_backend_dir, _repo_root):
    if p not in sys.path:
        sys.path.insert(0, p)

from handwriting.benchmark_fixtures import (
    BENCHMARK_DEV_CORPUS_20,
    BENCHMARK_HOLDOUT_CORPUS_20,
    STANDARD_SEEDS,
    load_benchmark_fonts,
)
from handwriting.metrics_evaluator import (
    DIACRITIC_CLEARANCE_PROVISIONAL_TARGET_MM,
    DIACRITIC_CLEARANCE_TECHNICAL_MIN_MM,
    TraceStroke,
    VALID_STROKE_TYPES,
    segments_intersect,
    segments_intersect_strict,
    segment_to_segment_distance,
    count_bridge_diacritic_collisions,
    compute_diacritic_clearance,
    classify_diacritic_clearance_acceptance,
    compute_turning_cost,
    compute_curvature_cost_from_vectors,
    compute_curvature_cost_from_stroke,
    compute_total_curvature_cost,
    compute_stroke_fingerprint,
    evaluate_ca_vhc_metrics,
)
from handwriting.engine import (
    text_to_strokes,
    text_to_strokes_structured,
    generate_handwriting_svg,
    StructuredRenderResult,
)


@pytest.mark.parametrize(
    ("collision_count", "clearance_mm", "expected"),
    [
        (1, 1.00, "FAIL"),
        (0, 0.199, "FAIL"),
        (0, 0.20, "INCONCLUSIVE"),
        (0, 0.499, "INCONCLUSIVE"),
        (0, 0.50, "PASS_PROVISIONAL_TARGET"),
        (0, float("inf"), "NOT_APPLICABLE"),
    ],
)
def test_diacritic_clearance_acceptance_boundaries(
    collision_count, clearance_mm, expected
):
    """Lock the exact C2/C3 boundary semantics before PR3 implementation."""
    assert DIACRITIC_CLEARANCE_TECHNICAL_MIN_MM == 0.20
    assert DIACRITIC_CLEARANCE_PROVISIONAL_TARGET_MM == 0.50
    assert (
        classify_diacritic_clearance_acceptance(collision_count, clearance_mm)
        == expected
    )


@pytest.mark.parametrize(
    ("collision_count", "clearance_mm"),
    [
        (-1, 0.50),
        (True, 0.50),
        (0, -0.01),
        (0, float("nan")),
        (0, True),
        (0, "0.5"),
        (0, "not-a-number"),
    ],
)
def test_diacritic_clearance_acceptance_rejects_invalid_metrics(
    collision_count, clearance_mm
):
    """Invalid measurements must fail closed instead of receiving a pass verdict."""
    with pytest.raises(ValueError):
        classify_diacritic_clearance_acceptance(collision_count, clearance_mm)


@pytest.mark.parametrize(
    "threshold_kwargs",
    [
        {"technical_min_mm": True},
        {"technical_min_mm": "0.20"},
        {"provisional_target_mm": False},
        {"provisional_target_mm": "0.50"},
    ],
)
def test_diacritic_clearance_acceptance_rejects_non_numeric_threshold_types(
    threshold_kwargs,
):
    with pytest.raises(ValueError):
        classify_diacritic_clearance_acceptance(0, 0.50, **threshold_kwargs)


@pytest.mark.parametrize(
    ("raw_clearance_mm", "expected"),
    [
        (0.1996, "FAIL"),
        (0.4996, "INCONCLUSIVE"),
    ],
)
def test_evaluator_preserves_clearance_precision_before_classification(
    raw_clearance_mm, expected
):
    bridge = TraceStroke(
        points=np.array([[0.0, 0.0], [1.0, 0.0]]),
        stroke_type="bridge_stroke",
        char="a->b",
        word_idx=0,
    )
    diacritic = TraceStroke(
        points=np.array([[0.0, raw_clearance_mm], [1.0, raw_clearance_mm]]),
        stroke_type="diacritic_stroke",
        char="b",
        word_idx=0,
    )

    metrics = evaluate_ca_vhc_metrics([bridge, diacritic])
    measured = metrics["minimum_diacritic_clearance_mm"]

    assert measured == pytest.approx(raw_clearance_mm)
    assert classify_diacritic_clearance_acceptance(0, measured) == expected


# ==============================================================================
# 1. Zero-collision case
# ==============================================================================
def test_zero_collision_case():
    """Kịch bản không va chạm: chữ chuẩn không có cầu nối cắt qua dấu."""
    res = text_to_strokes_structured("tiếng", font="oly", seed=42)
    metrics = evaluate_ca_vhc_metrics(res)
    assert metrics["collision_count"] == 0
    # oly không bật ligatures nên bridge_stroke = 0 -> clearance = inf
    assert metrics["minimum_diacritic_clearance_mm"] == float("inf")

    # Với font cursive có cầu nối, các cầu nối thông thường không cắt qua dấu
    res_cur = text_to_strokes_structured("nguyễn", font="cursive", seed=42)
    metrics_cur = evaluate_ca_vhc_metrics(res_cur)
    assert metrics_cur["collision_count"] == 0
    assert metrics_cur["minimum_diacritic_clearance_mm"] > 0.0


# ==============================================================================
# 2. Synthetic collision scenario & stroke-pair counting
# ==============================================================================
def test_synthetic_collision_detection():
    """
    Kịch bản giả lập va chạm:
    - Đếm số cặp bridge–diacritic có ít nhất một giao cắt.
    - Một cặp stroke va chạm nhiều segment vẫn chỉ tính 1 collision event.
    - Hai bridge độc lập cùng va chạm 1 diacritic => tính 2 collision events.
    """
    # Bridge 1 nằm ngang từ (10, 10) qua (20, 10) đến (30, 10) (2 segments)
    bridge1_pts = np.array([[10.0, 10.0], [20.0, 10.0], [30.0, 10.0]])
    # Diacritic thẳng đứng cắt ngang qua bridge tại (20, 10): từ (20, 5) đến (20, 15)
    diacritic_pts = np.array([[20.0, 5.0], [20.0, 15.0]])

    trace = [
        TraceStroke(points=bridge1_pts, stroke_type="bridge_stroke", char="u->w", word_idx=0),
        TraceStroke(points=diacritic_pts, stroke_type="diacritic_stroke", char="w", word_idx=0),
    ]

    # Cặp bridge1 - diacritic có va chạm (dù chạm/cắt ở cả 2 segment liền kề tại vertex) -> tính đúng 1 collision event
    collisions = count_bridge_diacritic_collisions([bridge1_pts], [diacritic_pts])
    assert collisions == 1

    clearance = compute_diacritic_clearance([bridge1_pts], [diacritic_pts])
    assert clearance == 0.0

    metrics = evaluate_ca_vhc_metrics(trace)
    assert metrics["collision_count"] == 1
    assert metrics["minimum_diacritic_clearance_mm"] == 0.0

    # Nếu thêm Bridge 2 độc lập cũng cắt qua diacritic đó -> 2 collision events (2 cặp stroke va chạm)
    bridge2_pts = np.array([[15.0, 12.0], [25.0, 12.0]])
    collisions_2 = count_bridge_diacritic_collisions([bridge1_pts, bridge2_pts], [diacritic_pts])
    assert collisions_2 == 2


# ==============================================================================
# 3. Bridge-Diacritic Endpoint Touch vs Separated & Bridge-Base Valid Contact
# ==============================================================================
def test_bridge_diacritic_endpoint_touch_is_collision():
    """
    Kiểm thử semantics va chạm bridge–diacritic:
    a) bridge chạm endpoint của diacritic => collision (không miễn trừ endpoint contact).
    b) hai đoạn tách rời => không collision.
    """
    # Đoạn bridge P từ (0, 0) đến (2, 0)
    bridge_p = np.array([[0.0, 0.0], [2.0, 0.0]])

    # a) Đoạn diacritic Q chạm đúng đầu mút p2 tại (2, 0) và đi lên (2, 2)
    diacritic_touch = np.array([[2.0, 0.0], [2.0, 2.0]])
    assert segments_intersect(bridge_p[0], bridge_p[1], diacritic_touch[0], diacritic_touch[1])
    cnt_touch = count_bridge_diacritic_collisions([bridge_p], [diacritic_touch])
    assert cnt_touch == 1
    clr_touch = compute_diacritic_clearance([bridge_p], [diacritic_touch])
    assert clr_touch == 0.0

    # b) Hai đoạn tách rời hoàn toàn: bridge P [0, 0]->[2, 0] và diacritic [2.5, 1.0]->[2.5, 3.0]
    diacritic_separated = np.array([[2.5, 1.0], [2.5, 3.0]])
    assert not segments_intersect(bridge_p[0], bridge_p[1], diacritic_separated[0], diacritic_separated[1])
    cnt_sep = count_bridge_diacritic_collisions([bridge_p], [diacritic_separated])
    assert cnt_sep == 0
    clr_sep = compute_diacritic_clearance([bridge_p], [diacritic_separated])
    assert clr_sep > 0.0


# ==============================================================================
# 4. Clearance calculation with known geometry
# ==============================================================================
def test_clearance_calculation_known_distance():
    """Tính toán khoảng cách cách ly (clearance) chính xác với hình học đã biết."""
    # Hai đoạn thẳng song song cách nhau đúng 1.25 mm
    d_expected = 1.25
    s_bridge = np.array([[0.0, 0.0], [10.0, 0.0]])
    s_diacritic = np.array([[2.0, d_expected], [8.0, d_expected]])

    clearance = compute_diacritic_clearance([s_bridge], [s_diacritic])
    assert pytest.approx(clearance, rel=1e-5) == d_expected

    # Kiểm tra khoảng cách chéo: điểm đầu gần nhất
    s_diag_bridge = np.array([[0.0, 0.0], [3.0, 0.0]])
    s_diag_diacritic = np.array([[3.0, 4.0], [6.0, 4.0]])
    # Khoảng cách giữa (3, 0) và (3, 4) là đúng 4.0 mm
    assert pytest.approx(compute_diacritic_clearance([s_diag_bridge], [s_diag_diacritic]), rel=1e-5) == 4.0


# ==============================================================================
# 5. Curvature cost formula verification
# ==============================================================================
def test_curvature_cost_formula():
    """
    Curvature cost tính đúng theo công thức với các góc đã biết:
    - 0 độ -> cost 0
    - 90 độ -> cost 1
    - 180 độ -> cost 2
    """
    # 1. Kiểm tra đơn vị bẻ góc compute_turning_cost(theta)
    assert pytest.approx(compute_turning_cost(0.0), abs=1e-6) == 0.0
    assert pytest.approx(compute_turning_cost(math.pi / 2.0), abs=1e-6) == 1.0
    assert pytest.approx(compute_turning_cost(math.pi), abs=1e-6) == 2.0

    # 2. Kiểm tra từ vectors chuyển dịch
    # Trường hợp thẳng hàng trơn tru (0 độ cả exit và entry):
    p_exit = np.array([0.0, 0.0])
    p_entry = np.array([5.0, 0.0])  # u_d = (1, 0)
    v_exit_straight = np.array([1.0, 0.0])
    v_entry_straight = np.array([1.0, 0.0])
    c_straight = compute_curvature_cost_from_vectors(v_exit_straight, p_exit, p_entry, v_entry_straight)
    assert pytest.approx(c_straight, abs=1e-6) == 0.0

    # Trường hợp bẻ vuông góc 90 độ tại exit và thẳng hàng tại entry:
    v_exit_90 = np.array([0.0, 1.0])  # vuông góc với u_d
    c_90 = compute_curvature_cost_from_vectors(v_exit_90, p_exit, p_entry, v_entry_straight)
    assert pytest.approx(c_90, abs=1e-6) == 1.0

    # Trường hợp bẻ ngược 180 độ tại exit và entry:
    v_exit_180 = np.array([-1.0, 0.0])
    v_entry_180 = np.array([-1.0, 0.0])
    c_180 = compute_curvature_cost_from_vectors(v_exit_180, p_exit, p_entry, v_entry_180)
    assert pytest.approx(c_180, abs=1e-6) == 4.0  # 2 + 2 = 4


# ==============================================================================
# 6. Absolute backward compatibility (bit-exact reproducibility)
# ==============================================================================
def test_backward_compatibility_dev_corpus():
    """
    So sánh đầu ra của text_to_strokes() và text_to_strokes_structured().strokes
    trên 20 từ DEV corpus x 2 fonts x 2 seeds.
    Đảm bảo 100% số stroke, số point và SHA-256 fingerprint không đổi.
    """
    fonts = ["oly", "omni_casual"]
    seeds = [42, 2026]

    for word in BENCHMARK_DEV_CORPUS_20:
        for font in fonts:
            for seed in seeds:
                strokes_pub = text_to_strokes(word, font=font, seed=seed)
                res_struct = text_to_strokes_structured(word, font=font, seed=seed)

                # Số stroke phải tuyệt đối bằng nhau
                assert len(strokes_pub) == len(res_struct.strokes), (
                    f"Lệch số strokes tại word '{word}', font={font}, seed={seed}: "
                    f"{len(strokes_pub)} vs {len(res_struct.strokes)}"
                )

                # Tổng số point phải tuyệt đối bằng nhau
                pts_pub = sum(len(s) for s in strokes_pub)
                pts_struct = sum(len(s) for s in res_struct.strokes)
                assert pts_pub == pts_struct, (
                    f"Lệch tổng số điểm tại word '{word}', font={font}, seed={seed}"
                )

                # Fingerprint SHA-256 phải tuyệt đối bằng nhau
                fp_pub = compute_stroke_fingerprint(strokes_pub)
                fp_struct = compute_stroke_fingerprint(res_struct.strokes)
                assert fp_pub == fp_struct, (
                    f"Lệch SHA-256 fingerprint tại word '{word}', font={font}, seed={seed}"
                )

                # Kiểm tra từng mảng tọa độ
                for s1, s2 in zip(strokes_pub, res_struct.strokes):
                    np.testing.assert_array_equal(s1, s2)


# ==============================================================================
# 7. Stroke tagging coverage
# ==============================================================================
def test_stroke_tagging_coverage():
    """
    Kiểm tra trên tập từ mẫu tiếng Việt với font cursive,
    cả 4 loại nhãn nét (base_stroke, bridge_stroke, secondary_stroke, diacritic_stroke)
    đều xuất hiện và được gắn đúng metadata.
    """
    res = text_to_strokes_structured("tiếng Việt", font="cursive", seed=42)
    trace = res.trace

    types_found = {item.stroke_type for item in trace}
    assert types_found == VALID_STROKE_TYPES, (
        f"Không bao phủ đủ 4 loại nét: tìm thấy {types_found}, cần {VALID_STROKE_TYPES}"
    )

    # Kiểm tra nội dung metadata
    bridges = [item for item in trace if item.stroke_type == "bridge_stroke"]
    assert len(bridges) > 0
    for br in bridges:
        assert "->" in br.char
        assert "curvature_cost" in br.meta
        assert br.meta["curvature_cost"] >= 0.0

    diacritics = [item for item in trace if item.stroke_type == "diacritic_stroke"]
    assert len(diacritics) > 0
    for dia in diacritics:
        assert len(dia.points) >= 1
        assert "accents" in dia.meta


# ==============================================================================
# 8. Edge cases: empty, 1-character, accent-only text
# ==============================================================================
def test_edge_cases():
    """Xử lý an toàn các trường hợp biên: chuỗi rỗng, 1 ký tự, nhiều dấu liên tiếp."""
    # 1. Chuỗi rỗng
    res_empty = text_to_strokes_structured("", font="oly", seed=42)
    assert len(res_empty.strokes) == 0
    assert len(res_empty.trace) == 0
    metrics_empty = evaluate_ca_vhc_metrics(res_empty)
    assert metrics_empty["total_path_length_mm"] == 0.0
    assert metrics_empty["pen_lift_count"] == 0
    assert metrics_empty["collision_count"] == 0

    # 2. Một ký tự
    res_single = text_to_strokes_structured("a", font="oly", seed=42)
    assert len(res_single.strokes) >= 1
    assert len(res_single.trace) >= 1
    metrics_single = evaluate_ca_vhc_metrics(res_single)
    assert metrics_single["total_path_length_mm"] > 0.0
    assert metrics_single["collision_count"] == 0

    # 3. Ký tự tiếng Việt phức tạp chứa nhiều dấu
    res_acc = text_to_strokes_structured("nguyễn", font="oly", seed=42)
    types = {item.stroke_type for item in res_acc.trace}
    assert "diacritic_stroke" in types
    assert "base_stroke" in types


# ==============================================================================
# 9. Malformed input handling (NaN, Inf, 1-point)
# ==============================================================================
def test_malformed_input_handling():
    """Xử lý an toàn dữ liệu bất thường: stroke chứa NaN, Inf hoặc chỉ có 1 điểm."""
    # Stroke 1 điểm
    single_pt = np.array([[10.0, 10.0]])
    # Stroke chứa NaN
    nan_stroke = np.array([[0.0, 0.0], [np.nan, 5.0], [10.0, 10.0]])
    # Stroke chứa Inf
    inf_stroke = np.array([[0.0, 0.0], [np.inf, 5.0]])

    # Đo va chạm không được raise Exception
    cnt = count_bridge_diacritic_collisions([single_pt, nan_stroke], [inf_stroke, single_pt])
    assert cnt == 0

    # Đo clearance không được raise Exception
    clr = compute_diacritic_clearance([single_pt, nan_stroke], [inf_stroke])
    assert clr == float("inf")

    # Đánh giá toàn diện với trace chứa stroke bất thường
    malformed_trace = [
        TraceStroke(points=single_pt, stroke_type="bridge_stroke", char="x", word_idx=0),
        TraceStroke(points=nan_stroke, stroke_type="diacritic_stroke", char="y", word_idx=0),
    ]
    metrics = evaluate_ca_vhc_metrics(malformed_trace)
    assert metrics["collision_count"] == 0
    assert metrics["minimum_diacritic_clearance_mm"] == float("inf")


# ==============================================================================
# 10. Corpus disjointness check
# ==============================================================================
def test_corpus_disjointness_and_counts():
    """
    Kiểm tra tính rời nhau (disjoint) của BENCHMARK_DEV_CORPUS_20 và BENCHMARK_HOLDOUT_CORPUS_20:
    - Đúng 20 từ mỗi tập
    - Giao của 2 tập phải là tập rỗng tuyệt đối
    """
    assert len(BENCHMARK_DEV_CORPUS_20) == 20
    assert len(BENCHMARK_HOLDOUT_CORPUS_20) == 20

    dev_set = set(BENCHMARK_DEV_CORPUS_20)
    holdout_set = set(BENCHMARK_HOLDOUT_CORPUS_20)

    # Không có từ nào trùng nhau giữa 2 tập
    intersection = dev_set.intersection(holdout_set)
    assert len(intersection) == 0, f"Phát hiện từ trùng lặp giữa DEV và HOLDOUT corpus: {intersection}"

    # Kiểm tra standard seeds
    assert STANDARD_SEEDS == [42, 100, 2026, 999999]

    # Kiểm tra hàm load_benchmark_fonts trả về đúng cấu trúc {font_id: {"font_pack": ..., "render_profile": ...}}
    fonts = load_benchmark_fonts()
    assert "oly" in fonts
    assert "omni_casual" in fonts
    assert "font_pack" in fonts["oly"] and "render_profile" in fonts["oly"]
    assert "glyphs" in fonts["oly"]["font_pack"]
    assert "glyphs" in fonts["omni_casual"]["font_pack"]
    assert "aspect_y" in fonts["oly"]["render_profile"]


# ==============================================================================
# 11. TraceStroke and StructuredRenderResult API contract
# ==============================================================================
def test_trace_stroke_and_render_result_contract():
    """Kiểm tra hợp đồng dữ liệu của TraceStroke và StructuredRenderResult."""
    ts = TraceStroke(
        points=np.array([[1.0, 2.0], [3.0, 4.0]]),
        stroke_type="base_stroke",
        char="a",
        word_idx=0,
        meta={"key": "val"},
    )
    # Thuộc tính
    assert ts.stroke_type == "base_stroke"
    assert ts.char == "a"
    assert ts.word_idx == 0
    assert ts.meta["key"] == "val"
    np.testing.assert_array_equal(ts.points, ts.stroke)

    # Dictionary indexing
    assert ts["stroke_type"] == "base_stroke"
    assert ts["char"] == "a"
    assert ts["word_idx"] == 0
    assert ts["key"] == "val"
    assert "points" in ts
    assert ts.get("nonexistent", 99) == 99

    # StructuredRenderResult unpacking
    dummy_result = StructuredRenderResult(strokes=[ts.points], trace=[ts], optimize_time_ms=1.5)
    st, tr, opt_t = dummy_result
    assert len(st) == 1
    assert len(tr) == 1
    assert opt_t == 1.5


# ==============================================================================
# 12. generate_handwriting_svg preserves signature and returns real timing
# ==============================================================================
def test_generate_handwriting_svg_preserves_contract():
    """generate_handwriting_svg giữ nguyên chữ ký, kiểu trả về và trả timing thực."""
    svg_content, metrics, is_within_bounds = generate_handwriting_svg(
        "Kính gửi bạn.", font="oly", seed=42
    )
    assert isinstance(svg_content, str)
    assert svg_content.startswith("<svg") or "svg" in svg_content
    assert isinstance(metrics, dict)
    assert isinstance(is_within_bounds, (bool, np.bool_))

    # optimize_time_ms phải là số thực không âm (được đo thực tế qua perf_counter)
    assert "optimize_time_ms" in metrics
    assert metrics["optimize_time_ms"] >= 0.0
