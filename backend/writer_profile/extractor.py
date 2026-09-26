"""
OmniDraw Writer Profile Feature Extractor (TV1 — AI Data & Writer Profile Lead).

Triển khai module trích xuất đặc trưng phong cách người viết phục vụ nghiên cứu cá nhân hóa P2:
1. Độ nghiêng nét chữ trung bình (mean_slant_deg)
2. Tỷ lệ kích thước chữ trung bình (aspect_ratio_mean)
3. Khoảng cách chữ và từ (char_spacing, word_spacing)
4. Độ dao động đường chân dòng (baseline_jitter_std)
5. Xu hướng dịch chuyển tâm dấu và tỷ lệ kích thước dấu (diacritic_tendencies)

Tuân thủ nghiêm ngặt:
- docs/08_handwriting_dataset_spec.md (Section 8)
- dataset/schemas/writer_profile.schema.json
- Ponytail Senior Dev Discipline: Tối giản, toán học hình thức, không thêm phụ thuộc ngoài.

Ranh giới kiến trúc & Nghiên cứu:
- Writer Profile P2 tiếp tục độc lập hoàn toàn với CA-VHC P0.
- Đây là prototype kiểm thử ngoại tuyến bằng synthetic fixtures (tests/fixtures/writer_profile_synthetic_samples.json),
  chưa được xác thực trên mẫu viết tay thật và chưa bật trong luồng render/API chính.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np


@dataclass
class GlobalStyleFeatures:
    """Các đặc trưng phong cách toàn cục của người viết."""
    mean_slant_deg: float
    aspect_ratio_mean: float
    stroke_width_mean_mm: float
    baseline_jitter_std: float


@dataclass
class SpacingFeatures:
    """Các đặc trưng phân bố khoảng cách chữ, từ và dòng."""
    char_spacing_mean_ratio: float
    word_spacing_mean_ratio: float
    line_spacing_mean_ratio: float


@dataclass
class DiacriticTendencyFeatures:
    """Các đặc trưng xu hướng đặt dấu tiếng Việt của người viết."""
    diacritic_offset_bias: List[float]  # [dx_bias_mm, dy_bias_mm]
    diacritic_scale_ratio: float


@dataclass
class WriterProfile:
    """
    Hồ sơ đặc trưng phong cách cá nhân hóa của một người viết cụ thể.
    Khớp 100% với JSON Schema: dataset/schemas/writer_profile.schema.json.
    """
    profile_id: str
    writer_id: str
    version: str
    created_at: str
    num_samples_analyzed: int
    global_style: GlobalStyleFeatures
    spacing: SpacingFeatures
    diacritic_tendencies: DiacriticTendencyFeatures
    allograph_tendencies: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi hồ sơ sang cấu trúc dict có thể serialize JSON."""
        return {
            "profile_id": self.profile_id,
            "writer_id": self.writer_id,
            "version": self.version,
            "created_at": self.created_at,
            "num_samples_analyzed": int(self.num_samples_analyzed),
            "global_style": {
                "mean_slant_deg": round(float(self.global_style.mean_slant_deg), 2),
                "aspect_ratio_mean": round(float(self.global_style.aspect_ratio_mean), 3),
                "stroke_width_mean_mm": round(float(self.global_style.stroke_width_mean_mm), 3),
                "baseline_jitter_std": round(float(self.global_style.baseline_jitter_std), 3),
            },
            "spacing": {
                "char_spacing_mean_ratio": round(float(self.spacing.char_spacing_mean_ratio), 3),
                "word_spacing_mean_ratio": round(float(self.spacing.word_spacing_mean_ratio), 3),
                "line_spacing_mean_ratio": round(float(self.spacing.line_spacing_mean_ratio), 3),
            },
            "diacritic_tendencies": {
                "diacritic_offset_bias": [
                    round(float(self.diacritic_tendencies.diacritic_offset_bias[0]), 3),
                    round(float(self.diacritic_tendencies.diacritic_offset_bias[1]), 3),
                ],
                "diacritic_scale_ratio": round(float(self.diacritic_tendencies.diacritic_scale_ratio), 3),
            },
            "allograph_tendencies": {
                k: round(float(v), 3) for k, v in self.allograph_tendencies.items()
            },
        }


# =============================================================================
# 1. Các giải thuật trích xuất đặc trưng hình học độc lập (Independent Feature Extractors)
# =============================================================================

def extract_mean_slant_deg(strokes: List[np.ndarray]) -> float:
    """
    Ước lượng góc nghiêng trung bình (mean_slant_deg) từ tập nét viết.
    
    Thuật toán:
    - Duyệt qua từng phân đoạn (segment) nối giữa 2 điểm liên tiếp (p_i, p_{i+1}).
    - Lọc các phân đoạn có xu hướng thẳng đứng chủ đạo: |dy| / L > sin(30°) = 0.5.
    - Chuẩn hóa hướng vector sao cho dy > 0 (hướng xuống).
    - Tính góc nghiêng: theta = arctan2(dx, dy) theo đơn vị độ.
      Góc dương (>0): nghiêng phải (forward slant / clockwise).
      Góc âm (<0): nghiêng trái (backward slant / counterclockwise).
    - Lấy trung bình có trọng số theo chiều dài phân đoạn.
    - Kẹp trong giới hạn [-45.0°, 45.0°].
    """
    if not strokes:
        return 0.0

    total_weight = 0.0
    weighted_angle_sum = 0.0

    for stroke in strokes:
        if len(stroke) < 2:
            continue
        arr = np.asarray(stroke, dtype=float)
        diffs = np.diff(arr, axis=0)  # (N-1, 2)
        lengths = np.hypot(diffs[:, 0], diffs[:, 1])

        valid_mask = lengths > 1e-4
        if not np.any(valid_mask):
            continue

        diffs = diffs[valid_mask]
        lengths = lengths[valid_mask]

        # Phân đoạn chủ đạo thẳng đứng: |dy| / L > 0.5
        vertical_ratio = np.abs(diffs[:, 1]) / lengths
        vert_mask = vertical_ratio > 0.5

        if not np.any(vert_mask):
            continue

        v_diffs = diffs[vert_mask]
        v_lengths = lengths[vert_mask]

        # Chuẩn hóa về chiều hướng xuống (dy > 0)
        sign = np.where(v_diffs[:, 1] < 0, -1.0, 1.0)[:, np.newaxis]
        norm_diffs = v_diffs * sign

        angles_rad = np.arctan2(norm_diffs[:, 0], norm_diffs[:, 1])
        angles_deg = np.degrees(angles_rad)

        weighted_angle_sum += float(np.sum(angles_deg * v_lengths))
        total_weight += float(np.sum(v_lengths))

    if total_weight < 1e-5:
        return 0.0

    mean_slant = weighted_angle_sum / total_weight
    return float(np.clip(mean_slant, -45.0, 45.0))


def extract_mean_aspect_ratio(
    character_stroke_groups: List[List[np.ndarray]],
    min_height_mm: float = 0.5
) -> float:
    """
    Tính tỷ lệ chiều rộng / chiều cao (aspect_ratio = W / H) trung bình của các ký tự.
    
    Mỗi phần tử trong character_stroke_groups là một danh sách nét của 1 ký tự.
    Nếu ký tự có H < min_height_mm, bỏ qua để tránh chia cho 0 hoặc dấu chấm nhỏ.
    """
    if not character_stroke_groups:
        return 1.0

    aspect_ratios: List[float] = []

    for strokes in character_stroke_groups:
        if not strokes:
            continue
        all_pts = [np.asarray(s, dtype=float) for s in strokes if len(s) > 0]
        if not all_pts:
            continue
        pts = np.vstack(all_pts)
        xmin, ymin = np.min(pts, axis=0)
        xmax, ymax = np.max(pts, axis=0)

        w = xmax - xmin
        h = ymax - ymin

        if h >= min_height_mm:
            ratio = w / h
            # Giới hạn hợp lý cho tỷ lệ khung chữ tiếng Việt [0.2, 3.0]
            aspect_ratios.append(float(np.clip(ratio, 0.2, 3.0)))

    if not aspect_ratios:
        return 1.0

    return float(np.mean(aspect_ratios))


def extract_spacing_ratios(
    words_data: List[List[Tuple[float, float, float, float]]],
    default_char_spacing: float = 0.25,
    default_word_spacing: float = 0.85,
    default_line_spacing: float = 1.5,
) -> Tuple[float, float, float]:
    """
    Tính các tỷ lệ khoảng cách:
    - char_spacing_mean_ratio: khoảng cách giữa 2 ký tự liên tiếp / chiều rộng ký tự
    - word_spacing_mean_ratio: khoảng cách giữa 2 từ liên tiếp / chiều rộng ký tự
    - line_spacing_mean_ratio: khoảng cách giữa các dòng / chiều cao ký tự

    Input:
    - words_data: Danh sách các từ, mỗi từ là danh sách các bounding boxes (xmin, ymin, xmax, ymax) của từng ký tự.
    """
    char_spacings: List[float] = []
    char_widths: List[float] = []
    word_spacings: List[float] = []

    prev_word_xmax: Optional[float] = None

    for char_boxes in words_data:
        if not char_boxes:
            continue

        # Đo khoảng cách giữa các từ liên tiếp
        word_xmin = min(b[0] for b in char_boxes)
        word_xmax = max(b[2] for b in char_boxes)

        if prev_word_xmax is not None and word_xmin > prev_word_xmax:
            word_spacings.append(word_xmin - prev_word_xmax)
        prev_word_xmax = word_xmax

        # Đo khoảng cách giữa các ký tự trong từ
        for i in range(len(char_boxes)):
            b_curr = char_boxes[i]
            w_curr = b_curr[2] - b_curr[0]
            if w_curr > 0.1:
                char_widths.append(w_curr)

            if i < len(char_boxes) - 1:
                b_next = char_boxes[i + 1]
                gap = b_next[0] - b_curr[2]
                if gap > -1.0:  # Cho phép hơi dính hoặc chạm nhẹ
                    char_spacings.append(max(0.0, gap))

    avg_char_w = float(np.mean(char_widths)) if char_widths else 3.0

    char_ratio = (
        float(np.mean(char_spacings)) / avg_char_w
        if (char_spacings and avg_char_w > 0.1)
        else default_char_spacing
    )
    word_ratio = (
        float(np.mean(word_spacings)) / avg_char_w
        if (word_spacings and avg_char_w > 0.1)
        else default_word_spacing
    )

    return (
        float(np.clip(char_ratio, 0.05, 1.5)),
        float(np.clip(word_ratio, 0.3, 3.5)),
        float(default_line_spacing),
    )


def extract_baseline_jitter_std(base_points: List[Tuple[float, float]]) -> float:
    """
    Đo độ lệch chuẩn dao động của chân chữ quanh đường chân dòng danh định (baseline).
    
    Input:
    - base_points: Danh sách các điểm tiếp xúc chân dòng (x_i, y_i) của các ký tự không có descender.
    
    Phương pháp:
    - Khớp đường hồi quy tuyến tính: y = a * x + b.
    - Tính sai số phần dư (residual): r_i = y_i - (a * x_i + b).
    - baseline_jitter_std = std(r_i, ddof=1) (đơn vị: mm).
    """
    if len(base_points) < 2:
        return 0.0

    pts = np.asarray(base_points, dtype=float)
    x = pts[:, 0]
    y = pts[:, 1]

    # Kiểm tra biến thiên trục X
    if np.max(x) - np.min(x) < 1e-4:
        return float(np.std(y, ddof=1))

    # Hồi quy tuyến tính bằng numpy polyfit bậc 1
    poly = np.polyfit(x, y, deg=1)
    y_fitted = np.polyval(poly, x)
    residuals = y - y_fitted

    jitter_std = float(np.std(residuals, ddof=1)) if len(residuals) > 1 else 0.0
    return max(0.0, jitter_std)


# =============================================================================
# 2. Lớp Trích xuất Tổng thể (WriterProfileExtractor)
# =============================================================================

class WriterProfileExtractor:
    """
    Bộ trích xuất và đóng gói hồ sơ phong cách người viết WriterProfile.
    """

    def __init__(self, version: str = "1.0.0", default_stroke_width_mm: float = 0.5):
        self.version = version
        self.default_stroke_width_mm = default_stroke_width_mm

    def extract_from_samples(
        self,
        writer_id: str,
        strokes: List[np.ndarray],
        character_stroke_groups: Optional[List[List[np.ndarray]]] = None,
        words_data: Optional[List[List[Tuple[float, float, float, float]]]] = None,
        baseline_points: Optional[List[Tuple[float, float]]] = None,
        diacritic_offset_bias: Optional[List[float]] = None,
        diacritic_scale_ratio: float = 1.0,
        allograph_tendencies: Optional[Dict[str, float]] = None,
        num_samples_analyzed: Optional[int] = None,
    ) -> WriterProfile:
        """
        Trích xuất toàn bộ vector đặc trưng và sinh đối tượng WriterProfile.
        """
        # 1. Độ nghiêng trung bình
        slant = extract_mean_slant_deg(strokes)

        # 2. Tỷ lệ khung chữ
        if character_stroke_groups:
            aspect = extract_mean_aspect_ratio(character_stroke_groups)
        else:
            # Fallback: coi mỗi nét là 1 ký tự nếu không gom nhóm
            aspect = extract_mean_aspect_ratio([[s] for s in strokes])

        # 3. Khoảng cách chữ, từ, dòng
        if words_data:
            c_ratio, w_ratio, l_ratio = extract_spacing_ratios(words_data)
        else:
            c_ratio, w_ratio, l_ratio = 0.25, 0.85, 1.5

        # 4. Độ dao động baseline
        if baseline_points:
            jitter = extract_baseline_jitter_std(baseline_points)
        else:
            # Ước lượng baseline từ điểm đáy các nét
            pts_bottom = [
                (float(np.mean(s[:, 0])), float(np.max(s[:, 1])))
                for s in strokes if len(s) > 0
            ]
            jitter = extract_baseline_jitter_std(pts_bottom)

        # 5. Xu hướng dấu
        bias = diacritic_offset_bias if diacritic_offset_bias is not None else [0.0, 0.0]

        # 6. Đóng gói đối tượng
        timestamp_str = datetime.now(timezone.utc).isoformat()
        samples_count = num_samples_analyzed if num_samples_analyzed is not None else max(1, len(strokes))

        profile = WriterProfile(
            profile_id=f"profile_{writer_id}_v1",
            writer_id=writer_id,
            version=self.version,
            created_at=timestamp_str,
            num_samples_analyzed=samples_count,
            global_style=GlobalStyleFeatures(
                mean_slant_deg=slant,
                aspect_ratio_mean=aspect,
                stroke_width_mean_mm=self.default_stroke_width_mm,
                baseline_jitter_std=jitter,
            ),
            spacing=SpacingFeatures(
                char_spacing_mean_ratio=c_ratio,
                word_spacing_mean_ratio=w_ratio,
                line_spacing_mean_ratio=l_ratio,
            ),
            diacritic_tendencies=DiacriticTendencyFeatures(
                diacritic_offset_bias=bias,
                diacritic_scale_ratio=float(diacritic_scale_ratio),
            ),
            allograph_tendencies=allograph_tendencies or {},
        )

        return profile


def extract_writer_profile(
    writer_id: str,
    strokes: List[np.ndarray],
    **kwargs: Any
) -> WriterProfile:
    """Hàm tiện ích trích xuất hồ sơ phong cách người viết chuẩn."""
    extractor = WriterProfileExtractor()
    return extractor.extract_from_samples(writer_id, strokes, **kwargs)


# =============================================================================
# 3. Kiểm định Hồ sơ theo Schema (Strict Rule-based Schema Validation)
# =============================================================================

def validate_writer_profile(profile_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Kiểm định đối tượng profile_dict theo quy chuẩn dataset/schemas/writer_profile.schema.json.
    Trả về: (is_valid: bool, errors: List[str]).
    """
    errors: List[str] = []

    required_top = [
        "profile_id", "writer_id", "version", "created_at",
        "num_samples_analyzed", "global_style", "spacing", "diacritic_tendencies"
    ]
    for field_name in required_top:
        if field_name not in profile_dict:
            errors.append(f"Thiếu trường bắt buộc cấp gốc: '{field_name}'")

    if errors:
        return False, errors

    # 1. Kiểm tra writer_id & profile_id
    if not isinstance(profile_dict["writer_id"], str) or not profile_dict["writer_id"]:
        errors.append("Trường 'writer_id' phải là chuỗi không rỗng")

    if not isinstance(profile_dict["num_samples_analyzed"], int) or profile_dict["num_samples_analyzed"] < 1:
        errors.append("Trường 'num_samples_analyzed' phải là số nguyên >= 1")

    # 2. Kiểm tra global_style
    gs = profile_dict.get("global_style", {})
    for f in ["mean_slant_deg", "aspect_ratio_mean", "stroke_width_mean_mm", "baseline_jitter_std"]:
        if f not in gs:
            errors.append(f"Thiếu trường 'global_style.{f}'")

    if "mean_slant_deg" in gs:
        val = gs["mean_slant_deg"]
        if not isinstance(val, (int, float)) or not (-45.0 <= val <= 45.0):
            errors.append(f"'global_style.mean_slant_deg' phải thuộc [-45.0, 45.0], nhận: {val}")

    if "aspect_ratio_mean" in gs:
        val = gs["aspect_ratio_mean"]
        if not isinstance(val, (int, float)) or not (0.2 <= val <= 3.0):
            errors.append(f"'global_style.aspect_ratio_mean' phải thuộc [0.2, 3.0], nhận: {val}")

    if "stroke_width_mean_mm" in gs:
        val = gs["stroke_width_mean_mm"]
        if not isinstance(val, (int, float)) or not (0.1 <= val <= 2.0):
            errors.append(f"'global_style.stroke_width_mean_mm' phải thuộc [0.1, 2.0], nhận: {val}")

    if "baseline_jitter_std" in gs:
        val = gs["baseline_jitter_std"]
        if not isinstance(val, (int, float)) or val < 0.0:
            errors.append(f"'global_style.baseline_jitter_std' phải >= 0.0, nhận: {val}")

    # 3. Kiểm tra spacing
    sp = profile_dict.get("spacing", {})
    for f in ["char_spacing_mean_ratio", "word_spacing_mean_ratio", "line_spacing_mean_ratio"]:
        if f not in sp:
            errors.append(f"Thiếu trường 'spacing.{f}'")
        elif not isinstance(sp[f], (int, float)):
            errors.append(f"'spacing.{f}' phải là số")

    # 4. Kiểm tra diacritic_tendencies
    dt = profile_dict.get("diacritic_tendencies", {})
    if "diacritic_offset_bias" not in dt:
        errors.append("Thiếu trường 'diacritic_tendencies.diacritic_offset_bias'")
    else:
        bias = dt["diacritic_offset_bias"]
        if not isinstance(bias, (list, tuple)) or len(bias) != 2:
            errors.append("'diacritic_tendencies.diacritic_offset_bias' phải là mảng 2 phần tử [dx, dy]")

    if "diacritic_scale_ratio" in dt:
        val = dt["diacritic_scale_ratio"]
        if not isinstance(val, (int, float)) or not (0.5 <= val <= 2.0):
            errors.append(f"'diacritic_tendencies.diacritic_scale_ratio' phải thuộc [0.5, 2.0], nhận: {val}")

    return len(errors) == 0, errors
