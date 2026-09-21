"""
OmniDraw CA-VHC Metrics Evaluator & Structured Render Trace.

Provides:
- TraceStroke: structured stroke representation with type metadata
- Geometric metrics:
  - segments_intersect: line segment intersection including endpoint touch
  - count_bridge_diacritic_collisions: stroke-pair collision counter
  - compute_diacritic_clearance: minimum Euclidean clearance
  - compute_curvature_cost_from_vectors / compute_total_curvature_cost
  - compute_stroke_fingerprint
  - evaluate_ca_vhc_metrics
"""

from dataclasses import dataclass, field
import hashlib
import math
from typing import Any, Dict, List, Optional, Sequence
import numpy as np


VALID_STROKE_TYPES = {
    "base_stroke",
    "bridge_stroke",
    "secondary_stroke",
    "diacritic_stroke",
}


@dataclass
class TraceStroke:
    """
    Cấu trúc dữ liệu đại diện cho một nét vẽ kèm thông tin ngữ cảnh CA-VHC.
    Hỗ trợ truy xuất dạng object thuộc tính (.points, .stroke_type, .char, .word_idx, .meta)
    và dạng dictionary indexing (stroke["points"], stroke["stroke_type"], etc.).
    """
    points: np.ndarray
    stroke_type: str
    char: str
    word_idx: int
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.stroke_type not in VALID_STROKE_TYPES:
            raise ValueError(
                f"stroke_type '{self.stroke_type}' không hợp lệ. "
                f"Các loại hợp lệ: {sorted(VALID_STROKE_TYPES)}"
            )

    @property
    def stroke(self) -> np.ndarray:
        """Alias cho points để tương thích với các thuật toán vẽ/tối ưu."""
        return self.points

    def __getitem__(self, key: str) -> Any:
        if key in ("points", "stroke"):
            return self.points
        elif key == "stroke_type":
            return self.stroke_type
        elif key == "char":
            return self.char
        elif key == "word_idx":
            return self.word_idx
        elif key == "meta":
            return self.meta
        elif key in self.meta:
            return self.meta[key]
        raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in ("points", "stroke", "stroke_type", "char", "word_idx", "meta") or key in self.meta

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def to_dict(self) -> Dict[str, Any]:
        return {
            "points": self.points,
            "stroke_type": self.stroke_type,
            "char": self.char,
            "word_idx": self.word_idx,
            "meta": self.meta,
        }


def _extract_points(stroke_obj: Any) -> Optional[np.ndarray]:
    """Trích xuất mảng numpy (N, 2) an toàn từ TraceStroke, dict hoặc ndarray."""
    if stroke_obj is None:
        return None
    if isinstance(stroke_obj, TraceStroke):
        pts = stroke_obj.points
    elif isinstance(stroke_obj, dict):
        pts = stroke_obj.get("points", stroke_obj.get("stroke"))
    elif isinstance(stroke_obj, np.ndarray):
        pts = stroke_obj
    else:
        pts = getattr(stroke_obj, "points", getattr(stroke_obj, "stroke", None))

    if pts is None:
        return None
    pts = np.asarray(pts, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 2:
        return None
    return pts


# ----------------------------- Hình học đoạn thẳng & Va chạm -----------------------------

def point_to_segment_distance(p, a, b) -> float:
    """
    Tính khoảng cách Euclide ngắn nhất từ điểm p đến đoạn thẳng nối từ a đến b.
    Xử lý an toàn đoạn suy biến (a == b).
    """
    p = np.asarray(p, dtype=float)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    if not (np.isfinite(p).all() and np.isfinite(a).all() and np.isfinite(b).all()):
        return float('inf')

    ab = b - a
    norm_sq = float(np.dot(ab, ab))
    if norm_sq < 1e-12:
        return float(np.linalg.norm(p - a))

    t = float(np.dot(p - a, ab) / norm_sq)
    t = max(0.0, min(1.0, t))
    proj = a + t * ab
    return float(np.linalg.norm(p - proj))


def segments_intersect(p1, p2, q1, q2, eps: float = 1e-6) -> bool:
    """
    Kiểm tra va chạm giao cắt hình học giữa hai đoạn thẳng [p1, p2] và [q1, q2].

    Quy tắc nghiệp vụ CA-VHC (PR1):
    - Đối với bridge_stroke vs diacritic_stroke: mọi giao cắt hoặc chạm mút (endpoint touch)
      đều tính là va chạm (collision).
    - Không miễn endpoint contact giữa bridge và diacritic.
    - Xử lý an toàn đoạn suy biến, tọa độ NaN, Inf.
    """
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    q1 = np.asarray(q1, dtype=float)
    q2 = np.asarray(q2, dtype=float)

    if not (np.isfinite(p1).all() and np.isfinite(p2).all() and
            np.isfinite(q1).all() and np.isfinite(q2).all()):
        return False

    len_p = float(np.linalg.norm(p2 - p1))
    len_q = float(np.linalg.norm(q2 - q1))
    if len_p <= eps and len_q <= eps:
        return float(np.linalg.norm(p1 - q1)) <= eps
    if len_p <= eps:
        return point_to_segment_distance(p1, q1, q2) <= eps
    if len_q <= eps:
        return point_to_segment_distance(q1, p1, p2) <= eps

    # Tiếp xúc đầu mút: chạm bất kỳ mút nào đều là va chạm giữa bridge và diacritic
    if (np.linalg.norm(p1 - q1) <= eps or np.linalg.norm(p1 - q2) <= eps or
        np.linalg.norm(p2 - q1) <= eps or np.linalg.norm(p2 - q2) <= eps):
        return True

    def _cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    cp1 = _cross(p1, p2, q1)
    cp2 = _cross(p1, p2, q2)
    cq1 = _cross(q1, q2, p1)
    cq2 = _cross(q1, q2, p2)

    tol_p = eps * max(1.0, len_p)
    tol_q = eps * max(1.0, len_q)

    # Cắt nhau chéo (straddling check)
    if ((cp1 > tol_p and cp2 < -tol_p) or (cp1 < -tol_p and cp2 > tol_p)) and \
       ((cq1 > tol_q and cq2 < -tol_q) or (cq1 < -tol_q and cq2 > tol_q)):
        return True

    # Điểm nằm trên đoạn thẳng hoặc collinear
    def _on_segment(pt, a, b):
        ab = b - a
        ap = pt - a
        cross_val = ab[0] * ap[1] - ab[1] * ap[0]
        if abs(cross_val) > eps * max(1.0, float(np.linalg.norm(ab))):
            return False
        dot = float(np.dot(ap, ab))
        ab_sq = float(np.dot(ab, ab))
        return -eps <= dot <= ab_sq + eps

    if _on_segment(q1, p1, p2) or _on_segment(q2, p1, p2) or \
       _on_segment(p1, q1, q2) or _on_segment(p2, q1, q2):
        return True

    return False


# Giữ alias segments_intersect_strict để tương thích
segments_intersect_strict = segments_intersect


def segment_to_segment_distance(p1, p2, q1, q2, eps: float = 1e-6) -> float:
    """
    Tính khoảng cách Euclide ngắn nhất giữa hai đoạn thẳng [p1, p2] và [q1, q2].
    Nếu 2 đoạn giao nhau hoặc chạm mút: trả về 0.0.
    """
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    q1 = np.asarray(q1, dtype=float)
    q2 = np.asarray(q2, dtype=float)

    if not (np.isfinite(p1).all() and np.isfinite(p2).all() and
            np.isfinite(q1).all() and np.isfinite(q2).all()):
        return float('inf')

    # Nếu giao cắt thực tế hoặc chạm mút: khoảng cách hình học = 0.0
    if segments_intersect(p1, p2, q1, q2, eps=eps):
        return 0.0

    d1 = point_to_segment_distance(p1, q1, q2)
    d2 = point_to_segment_distance(p2, q1, q2)
    d3 = point_to_segment_distance(q1, p1, p2)
    d4 = point_to_segment_distance(q2, p1, p2)
    return float(min(d1, d2, d3, d4))


def count_bridge_diacritic_collisions(
    bridge_strokes: Sequence[Any],
    diacritic_strokes: Sequence[Any],
    eps: float = 1e-6,
) -> int:
    """
    Đếm số cặp (bridge_stroke, diacritic_stroke) có ít nhất một giao cắt hoặc chạm mút.
    Mỗi cặp stroke có va chạm chỉ tính 1 collision event, không đếm lặp theo số cặp segment.
    Xử lý an toàn với stroke rỗng, stroke 1 điểm hoặc dữ liệu NaN/Inf.
    """
    bridges = [_extract_points(s) for s in bridge_strokes]
    diacritics = [_extract_points(s) for s in diacritic_strokes]

    valid_bridges = [b for b in bridges if b is not None and len(b) >= 2 and np.isfinite(b).all()]
    valid_diacritics = [d for d in diacritics if d is not None and len(d) >= 2 and np.isfinite(d).all()]

    if not valid_bridges or not valid_diacritics:
        return 0

    collisions = 0
    for br in valid_bridges:
        for dia in valid_diacritics:
            pair_collides = False
            for i in range(len(br) - 1):
                bp1, bp2 = br[i], br[i + 1]
                for j in range(len(dia) - 1):
                    dp1, dp2 = dia[j], dia[j + 1]
                    if segments_intersect(bp1, bp2, dp1, dp2, eps=eps):
                        pair_collides = True
                        break
                if pair_collides:
                    break
            if pair_collides:
                collisions += 1

    return collisions


def compute_diacritic_clearance(
    bridge_strokes: Sequence[Any],
    diacritic_strokes: Sequence[Any],
    eps: float = 1e-6,
) -> float:
    """
    Tính khoảng cách Euclide ngắn nhất giữa bất kỳ đoạn thẳng nào của bridge_stroke
    và diacritic_stroke.
    Trả về float('inf') nếu không có bridge hoặc không có diacritic.
    """
    bridges = [_extract_points(s) for s in bridge_strokes]
    diacritics = [_extract_points(s) for s in diacritic_strokes]

    valid_bridges = [b for b in bridges if b is not None and len(b) >= 2 and np.isfinite(b).all()]
    valid_diacritics = [d for d in diacritics if d is not None and len(d) >= 2 and np.isfinite(d).all()]

    if not valid_bridges or not valid_diacritics:
        return float('inf')

    min_dist = float('inf')
    for br in valid_bridges:
        for i in range(len(br) - 1):
            bp1, bp2 = br[i], br[i + 1]
            for dia in valid_diacritics:
                for j in range(len(dia) - 1):
                    dp1, dp2 = dia[j], dia[j + 1]
                    d = segment_to_segment_distance(bp1, bp2, dp1, dp2, eps=eps)
                    if d < min_dist:
                        min_dist = d
                        if min_dist <= 0.0:
                            return 0.0
    return float(min_dist)


# ----------------------------- Chi phí độ cong tiếp tuyến (Curvature Cost) -----------------------------

def compute_turning_cost(theta_rad: float) -> float:
    """
    Tính chi phí bẻ một góc tiếp tuyến: 1.0 - cos(theta).
    - 0 deg -> 0.0
    - 90 deg -> 1.0
    - 180 deg -> 2.0
    """
    return float(1.0 - math.cos(theta_rad))


def compute_curvature_cost_from_vectors(v_exit, p_exit, p_entry, v_entry) -> float:
    """
    Tính chi phí góc bẻ tiếp tuyến cho một cầu nối theo đúng định nghĩa đặc tả:
    u_d = (P_entry - P_exit) / ||P_entry - P_exit||
    cos_theta1 = clip(V_exit . u_d, -1.0, 1.0)
    cos_theta2 = clip(u_d . V_entry, -1.0, 1.0)
    C_curvature = (1.0 - cos_theta1) + (1.0 - cos_theta2) in [0.0, 4.0]
    """
    p_ex = np.asarray(p_exit, dtype=float)
    p_en = np.asarray(p_entry, dtype=float)
    v_ex = np.asarray(v_exit, dtype=float)
    v_en = np.asarray(v_entry, dtype=float)

    if not (np.isfinite(p_ex).all() and np.isfinite(p_en).all() and
            np.isfinite(v_ex).all() and np.isfinite(v_en).all()):
        return 0.0

    d_vec = p_en - p_ex
    d_norm = float(np.linalg.norm(d_vec))
    if d_norm <= 1e-6:
        return 0.0

    norm_ex = float(np.linalg.norm(v_ex))
    norm_en = float(np.linalg.norm(v_en))
    if norm_ex <= 1e-6 or norm_en <= 1e-6:
        return 0.0

    u_d = d_vec / d_norm
    u_ex = v_ex / norm_ex
    u_en = v_en / norm_en

    cos1 = float(np.clip(np.dot(u_ex, u_d), -1.0, 1.0))
    cos2 = float(np.clip(np.dot(u_d, u_en), -1.0, 1.0))
    return float((1.0 - cos1) + (1.0 - cos2))


def compute_curvature_cost_from_stroke(stroke_points: Any) -> float:
    """
    Tính chi phí độ cong xấp xỉ từ các điểm polyline của một bridge stroke.
    """
    pts = _extract_points(stroke_points)
    if pts is None or len(pts) < 2 or not np.isfinite(pts).all():
        return 0.0

    p_start, p_end = pts[0], pts[-1]
    d_vec = p_end - p_start
    d_norm = float(np.linalg.norm(d_vec))
    if d_norm <= 1e-6:
        return 0.0
    u_d = d_vec / d_norm

    v1 = pts[1] - pts[0]
    v2 = pts[-1] - pts[-2]
    n1 = float(np.linalg.norm(v1))
    n2 = float(np.linalg.norm(v2))
    if n1 <= 1e-6 or n2 <= 1e-6:
        return 0.0

    cos1 = float(np.clip(np.dot(v1 / n1, u_d), -1.0, 1.0))
    cos2 = float(np.clip(np.dot(u_d, v2 / n2), -1.0, 1.0))
    return float((1.0 - cos1) + (1.0 - cos2))


def compute_total_curvature_cost(bridge_strokes_or_trace: Sequence[Any]) -> float:
    """
    Tổng chi phí độ cong của tất cả các cầu nối.
    Ưu tiên đọc meta['curvature_cost'] nếu có, hoặc tính trực tiếp từ tọa độ nét.
    """
    total = 0.0
    for item in bridge_strokes_or_trace:
        stroke_type = item.get("stroke_type") if hasattr(item, "get") else getattr(item, "stroke_type", None)
        if stroke_type in ("bridge_stroke", None):
            meta = item.get("meta", {}) if hasattr(item, "get") else getattr(item, "meta", {})
            if isinstance(meta, dict) and "curvature_cost" in meta:
                total += float(meta["curvature_cost"])
            else:
                pts = _extract_points(item)
                if pts is not None:
                    total += compute_curvature_cost_from_stroke(pts)
    return float(total)


# ----------------------------- Thống kê & Độ dài nét -----------------------------

def polyline_length(pts: np.ndarray) -> float:
    """Tính chiều dài polyline nét vẽ."""
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 2 or not np.isfinite(pts).all():
        return 0.0
    diffs = np.diff(pts, axis=0)
    return float(np.sum(np.sqrt(np.sum(diffs ** 2, axis=1))))


def total_travel_distance(strokes: List[np.ndarray]) -> float:
    """Tính tổng quãng đường di chuyển trên không (pen lift distance)."""
    total = 0.0
    prev_end = None
    for s in strokes:
        s = np.asarray(s, dtype=float)
        if len(s) == 0 or not np.isfinite(s).all():
            continue
        start_pt = s[0]
        end_pt = s[-1]
        if prev_end is not None:
            total += float(np.linalg.norm(start_pt - prev_end))
        prev_end = end_pt
    return float(total)


def compute_stroke_fingerprint(strokes: Sequence[np.ndarray]) -> str:
    """
    Tính SHA-256 fingerprint đồng nhất với kiểm thử hồi quy của OmniDraw engine.
    """
    digest = hashlib.sha256()
    digest.update(len(strokes).to_bytes(4, "little"))
    for stroke in strokes:
        arr = np.asarray(stroke, dtype="<f8")
        rounded = np.round(arr, 4).astype("<f8", copy=False)
        digest.update(np.asarray(arr.shape, dtype="<i8").tobytes())
        digest.update(rounded.tobytes())
    return digest.hexdigest()


# ----------------------------- Hàm Đánh Giá Toàn Diện CA-VHC -----------------------------

def evaluate_ca_vhc_metrics(
    trace: Any,
    optimize_time_ms: float = 0.0,
    strokes: Optional[List[np.ndarray]] = None,
) -> Dict[str, Any]:
    """
    Đánh giá bộ 7 chỉ số nghiên cứu CA-VHC chuẩn theo docs/05_ca_vhc_research_spec.md.

    Tham số:
    - trace: List[TraceStroke], hoặc kết quả StructuredRenderResult, hoặc dict-like strokes
    - optimize_time_ms: thời gian thực thi của optimize_word_dag đo qua time.perf_counter()
    - strokes: (tùy chọn) danh sách nét hoàn chỉnh đã ghép nối (cho đo lift/travel)

    Trả về:
    dict gồm 7 chỉ số tối thiểu + stroke_counts_by_type.
    """
    # Xử lý nếu trace là StructuredRenderResult
    if hasattr(trace, "trace") and hasattr(trace, "strokes"):
        if strokes is None:
            strokes = trace.strokes
        if optimize_time_ms == 0.0 and hasattr(trace, "optimize_time_ms"):
            optimize_time_ms = trace.optimize_time_ms
        trace_list = trace.trace
    else:
        trace_list = trace if isinstance(trace, (list, tuple)) else []

    # Phân loại nét trong trace
    counts_by_type = {
        "base_stroke": 0,
        "bridge_stroke": 0,
        "secondary_stroke": 0,
        "diacritic_stroke": 0,
    }
    bridge_strokes = []
    diacritic_strokes = []

    for item in trace_list:
        stype = item.get("stroke_type") if hasattr(item, "get") else getattr(item, "stroke_type", "base_stroke")
        if stype in counts_by_type:
            counts_by_type[stype] += 1
        pts = _extract_points(item)
        if pts is not None:
            if stype == "bridge_stroke":
                bridge_strokes.append(item)
            elif stype == "diacritic_stroke":
                diacritic_strokes.append(item)

    # Đo va chạm và khoảng cách cách ly giữa bridge và diacritic
    collision_cnt = count_bridge_diacritic_collisions(bridge_strokes, diacritic_strokes)
    clearance_mm = compute_diacritic_clearance(bridge_strokes, diacritic_strokes)

    # Đo chi phí độ cong tiếp tuyến
    curv_cost = compute_total_curvature_cost(bridge_strokes)

    # Đo đạc nét vẽ và nhấc bút
    if strokes is not None:
        valid_strokes = [s for s in strokes if s is not None and len(s) > 0 and np.isfinite(s).all()]
        total_path_len = sum(polyline_length(s) for s in valid_strokes)
        pen_lift_dist = total_travel_distance(valid_strokes)
        pen_lift_cnt = max(0, len(valid_strokes) - 1)
    else:
        # Nếu strokes không được truyền, kiểm tra xem trace có continuous_stroke_id không
        continuous_map: Dict[Any, List[np.ndarray]] = {}
        has_continuous_ids = False

        for idx, item in enumerate(trace_list):
            pts = _extract_points(item)
            if pts is None or len(pts) == 0 or not np.isfinite(pts).all():
                continue
            meta = item.get("meta", {}) if hasattr(item, "get") else getattr(item, "meta", {})
            c_id = meta.get("continuous_stroke_id") if isinstance(meta, dict) else None
            w_idx = item.get("word_idx") if hasattr(item, "get") else getattr(item, "word_idx", 0)
            if c_id is not None:
                has_continuous_ids = True
                key = (w_idx, c_id)
                continuous_map.setdefault(key, []).append(pts)
            else:
                continuous_map[idx] = [pts]

        if has_continuous_ids:
            reconstructed_strokes = []
            for key, piece_list in continuous_map.items():
                if len(piece_list) == 1:
                    reconstructed_strokes.append(piece_list[0])
                else:
                    reconstructed_strokes.append(np.vstack(piece_list))
            total_path_len = sum(polyline_length(s) for s in reconstructed_strokes)
            pen_lift_dist = total_travel_distance(reconstructed_strokes)
            pen_lift_cnt = max(0, len(reconstructed_strokes) - 1)
        else:
            raw_pts_list = [_extract_points(item) for item in trace_list]
            valid_pts = [p for p in raw_pts_list if p is not None and len(p) > 0 and np.isfinite(p).all()]
            total_path_len = sum(polyline_length(p) for p in valid_pts)
            pen_lift_dist = total_travel_distance(valid_pts)
            pen_lift_cnt = max(0, len(valid_pts) - 1)

    return {
        "total_path_length_mm": round(float(total_path_len), 3),
        "pen_lift_distance_mm": round(float(pen_lift_dist), 3),
        "pen_lift_count": int(pen_lift_cnt),
        "collision_count": int(collision_cnt),
        "minimum_diacritic_clearance_mm": round(float(clearance_mm), 3) if clearance_mm != float('inf') else float('inf'),
        "curvature_cost": round(float(curv_cost), 4),
        "optimize_time_ms": round(float(optimize_time_ms), 3),
        "stroke_counts_by_type": counts_by_type,
    }
