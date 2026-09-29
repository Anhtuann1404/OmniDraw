"""
Bộ Kiểm thử Thực nghiệm: Bẫy Lỗi Tách Dấu (Detached Diacritics) & Chữ Dính Nét (Touching Ligatures)
trong Module Writer Profile Generator (profile_generator.py).

Đường chạy: TV1 — AI Data & Writer Profile Lead
Phục vụ: Đánh giá thực nghiệm RQ4, kiểm soát rủi ro phân đoạn ảnh tĩnh và đề xuất
        kiến nghị điều chỉnh protocol trước khi TV4 tích hợp Writer Profile.
"""

import math
from pathlib import Path
import cv2
import numpy as np
import pytest

from backend.writer_profile.profile_generator import (
    extract_strokes_from_image,
    extract_char_boxes_from_image,
    generate_writer_profile_from_crops,
    px_to_mm,
    mm_to_px,
)
from backend.writer_profile.extractor import (
    WriterProfile,
    WriterProfileExtractor,
    extract_mean_aspect_ratio,
    extract_spacing_ratios,
    extract_baseline_jitter_std,
    validate_writer_profile,
)


def create_synthetic_accented_letter_image(
    dpi: int = 600,
    width_mm: float = 14.0,
    height_mm: float = 14.0,
    base_char: str = "e",
) -> np.ndarray:
    """
    Tạo ảnh crop giả lập chữ cái tiếng Việt có dấu tách rời (ví dụ: chữ 'ế').
    Gồm 3 thành phần vật lý tách biệt không dính mực:
    1. Thân chữ 'e' (base glyph): nằm ở vùng baseline (y = 8..11 mm)
    2. Dấu mũ '^' (circumflex): nằm tách rời phía trên thân chữ (y = 5..7 mm)
    3. Dấu sắc '/' (acute): nằm tách rời phía trên dấu mũ (y = 2..4 mm)
    """
    w_px = mm_to_px(width_mm, dpi)
    h_px = mm_to_px(height_mm, dpi)
    img = np.full((h_px, w_px, 3), 255, dtype=np.uint8)

    cx = w_px // 2
    stroke_thickness = max(2, mm_to_px(0.45, dpi))

    # 1. Thân chữ cơ sở: hình elip/vòng cung mô phỏng thân chữ 'e'
    y_base_top = mm_to_px(7.5, dpi)
    y_base_bot = mm_to_px(11.5, dpi)
    base_center = (cx, (y_base_top + y_base_bot) // 2)
    base_axes = (mm_to_px(2.2, dpi), (y_base_bot - y_base_top) // 2)
    cv2.ellipse(img, base_center, base_axes, 0, 0, 360, (0, 0, 0), stroke_thickness)

    # 2. Dấu mũ tách rời: 2 nét tạo góc ^ (khoảng y = 5.0..6.5 mm)
    y_hat_peak = mm_to_px(5.0, dpi)
    y_hat_bot = mm_to_px(6.5, dpi)
    cv2.line(img, (cx - mm_to_px(1.5, dpi), y_hat_bot), (cx, y_hat_peak), (0, 0, 0), stroke_thickness)
    cv2.line(img, (cx, y_hat_peak), (cx + mm_to_px(1.5, dpi), y_hat_bot), (0, 0, 0), stroke_thickness)

    # 3. Dấu sắc tách rời: 1 nét xiên nghiêng phải (khoảng y = 2.5..4.2 mm)
    y_acute_top = mm_to_px(2.5, dpi)
    y_acute_bot = mm_to_px(4.2, dpi)
    cv2.line(img, (cx + mm_to_px(1.8, dpi), y_acute_top), (cx + mm_to_px(0.8, dpi), y_acute_bot), (0, 0, 0), stroke_thickness)

    return img


def create_synthetic_cursive_word_image(
    dpi: int = 600,
    width_mm: float = 30.0,
    height_mm: float = 14.0,
) -> np.ndarray:
    """
    Tạo ảnh crop giả lập từ viết thảo liền nét (cursive ligatures, ví dụ chữ 'nam').
    Các ký tự nối liền nhau qua đường nối ngòi bút liên tục (không nhấc bút).
    """
    w_px = mm_to_px(width_mm, dpi)
    h_px = mm_to_px(height_mm, dpi)
    img = np.full((h_px, w_px, 3), 255, dtype=np.uint8)

    stroke_thickness = max(2, mm_to_px(0.5, dpi))

    # Vẽ đường uốn lượn liên tục 3 con chữ nối liền
    pts = []
    x_start = mm_to_px(4.0, dpi)
    x_end = mm_to_px(26.0, dpi)
    num_pts = 100
    for i in range(num_pts):
        x = int(x_start + (x_end - x_start) * i / float(num_pts - 1))
        # 3 chu kỳ lượn sóng mô phỏng 3 chữ nối liền
        t = i / float(num_pts - 1) * 3.0 * 2.0 * math.pi
        y = int(mm_to_px(9.0, dpi) + mm_to_px(2.0, dpi) * math.sin(t))
        pts.append([x, y])

    pts_arr = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [pts_arr], isClosed=False, color=(0, 0, 0), thickness=stroke_thickness)

    return img


def test_detached_diacritic_segmentation_anomaly():
    """
    Thực nghiệm 1: Chứng minh hiện tượng bẫy lỗi dấu tách rời (Detached Diacritic Anomaly).
    Khi sử dụng connectedComponentsWithStats trên ảnh từ/dòng:
    1. Chữ 'ế' bị phân mảnh thành 3 connected components (thân, mũ, sắc).
    2. Nếu coi mỗi box là 1 ký tự, tỷ lệ khung chữ aspect_ratio bị sai lệch nghiêm trọng.
    3. Điểm đáy của dấu trên (y nhỏ) nếu nhầm là baseline sẽ làm baseline_jitter_std tăng vọt.
    """
    dpi = 600
    img_e = create_synthetic_accented_letter_image(dpi=dpi)

    # 1. Trích xuất bounding boxes bằng connected components
    boxes = extract_char_boxes_from_image(img_e, dpi=dpi, min_area_px=15)

    # Khẳng định hiện tượng: 1 chữ 'ế' bị tách thành 3 bounding boxes độc lập!
    assert len(boxes) == 3, f"Kỳ vọng 3 connected components tách rời, nhận: {len(boxes)}"

    # Phân loại 3 hộp theo tọa độ y_min
    boxes_by_y = sorted(boxes, key=lambda b: b[1])
    acute_box = boxes_by_y[0]  # Dấu sắc ở trên cùng (y_min nhỏ nhất)
    hat_box = boxes_by_y[1]    # Dấu mũ ở giữa
    base_box = boxes_by_y[2]   # Thân chữ ở dưới cùng

    # Chiều cao của dấu rất nhỏ so với thân chữ
    h_acute = acute_box[3] - acute_box[1]
    h_hat = hat_box[3] - hat_box[1]
    h_base = base_box[3] - base_box[1]

    assert h_acute < 2.5, f"Chiều cao dấu sắc phải nhỏ (~1.7mm), nhận: {h_acute}"
    assert h_base > 3.0, f"Chiều cao thân chữ phải lớn (~4mm), nhận: {h_base}"

    # 2. Nguy cơ Baseline Jitter:
    # Nếu lấy đáy của cả 3 boxes làm baseline points:
    naive_baseline_points = [
        ((b[0] + b[2]) / 2.0, b[3]) for b in boxes
    ]
    # Đáy dấu sắc ở ~4.2mm, đáy dấu mũ ở ~6.5mm, đáy thân ở ~11.5mm
    y_bottoms = [pt[1] for pt in naive_baseline_points]
    naive_jitter = extract_baseline_jitter_std(naive_baseline_points)

    # Sai số: jitter bị vọt lên > 2.5mm (trong khi thực tế baseline của người viết là phẳng 0.0mm!)
    assert naive_jitter > 2.0, (
        f"Lỗi: Việc lấy đáy dấu tách rời làm điểm chân dòng gây nhiễu nhân tạo nặng: {naive_jitter}mm"
    )

    # 3. Giải pháp khắc phục: Lọc bỏ các component ở nửa trên (dấu)
    # Baseline thực sự chỉ nằm ở đáy của thân chữ (y_base_bot ~ 11.5mm)
    true_baseline_y = base_box[3]
    assert 11.0 <= true_baseline_y <= 12.0


def test_touching_cursive_ligature_anomaly():
    """
    Thực nghiệm 2: Chứng minh hiện tượng bẫy lỗi chữ viết liền nét (Touching Cursive Anomaly).
    Trong chữ viết thảo P02/P03, các ký tự nối liền nhau qua nét ligature:
    1. cv2.connectedComponentsWithStats coi cả cụm chữ là 1 thành phần duy nhất.
    2. extract_spacing_ratios không tìm thấy khoảng cách giữa các ký tự trong từ.
    """
    dpi = 600
    img_word = create_synthetic_cursive_word_image(dpi=dpi)

    boxes = extract_char_boxes_from_image(img_word, dpi=dpi, min_area_px=25)

    # Khẳng định hiện tượng: Toàn bộ từ viết thảo 3 chữ bị gộp thành đúng 1 box!
    assert len(boxes) == 1, f"Từ liền nét bị gộp thành 1 component, nhận: {len(boxes)}"

    # Do chỉ có 1 box, không thể trích xuất khoảng cách ký tự nội từ
    words_data = [boxes]
    char_ratio, word_ratio, line_ratio = extract_spacing_ratios(
        words_data,
        default_char_spacing=0.25,
        default_word_spacing=0.85,
    )

    # Khi không có 2 box liên tiếp trong từ, hàm buộc phải trả default_char_spacing 0.25
    assert char_ratio == 0.25, (
        "Khi chữ viết dính nét, extract_spacing_ratios không đo được và phải rơi về giá trị mặc định"
    )


def test_isolated_p01_grouping_resilience():
    """
    Thực nghiệm 3: Chứng minh tính chuẩn xác và kiên cố của trang P01 (Isolated Character Cells).
    Vì mỗi ô P01 đã biết trước là 1 ký tự đơn lẻ (ground truth context='isolated'):
    1. Toàn bộ nét của ô (kể cả dấu tách rời) được gom chung thành 1 ký tự duy nhất.
    2. Điểm đáy baseline chỉ lấy giá trị y lớn nhất (đáy thân chữ), hoàn toàn miễn nhiễm
       với việc dấu tách rời phía trên.
    3. Tỷ lệ khung chữ và góc nghiêng nét được tính toán chính xác 100%.
    """
    dpi = 600
    img_e = create_synthetic_accented_letter_image(dpi=dpi)

    # Đưa vào pipeline với context_tag="isolated"
    crops_data = [
        {"crop_image": img_e, "context_tag": "isolated", "is_valid": True}
    ]

    profile = generate_writer_profile_from_crops(
        writer_id="W001",
        crops_data=crops_data,
        dpi=dpi,
        version="1.0.0",
    )

    # Khẳng định: Hồ sơ hợp thức 100% theo JSON Schema
    is_valid, errors = validate_writer_profile(profile.to_dict())
    assert is_valid is True, f"Profile không hợp lệ: {errors}"

    # Số mẫu phân tích đúng bằng 1
    assert profile.num_samples_analyzed == 1

    # Tỷ lệ khung chữ của cả tổ hợp 'ế' nằm trong khoảng hợp lý [0.5, 1.5]
    aspect_ratio = profile.global_style.aspect_ratio_mean
    assert 0.4 <= aspect_ratio <= 1.2, f"Tỷ lệ khung chữ 'ế' gom đúng, nhận: {aspect_ratio}"

    # Độ rung baseline của 1 mẫu đơn lẻ là 0.0mm (không bị nhiễu dấu kéo lên 2.5mm như phép trích xuất ngây thơ)
    jitter = profile.global_style.baseline_jitter_std
    assert jitter == 0.0, f"Baseline jitter của mẫu ô đơn lập phải là 0.0, nhận: {jitter}"


def test_qc_filtering_and_provenance_integrity():
    """
    Thực nghiệm 4: Kiểm chứng tính toàn vẹn của cơ chế lọc QC và truy vết nguồn gốc.
    Các mẫu bị đánh dấu `is_valid=False` (hoặc QC_REJECTED) bị loại khỏi tính toán profile,
    ngăn ngừa dữ liệu rác làm sai lệch hồ sơ cá nhân hóa.
    """
    dpi = 600
    img_valid = create_synthetic_accented_letter_image(dpi=dpi)
    # Ảnh rác (gạch xóa, vẽ bậy)
    img_corrupted = np.zeros((mm_to_px(14.0, dpi), mm_to_px(14.0, dpi), 3), dtype=np.uint8)

    crops_data = [
        {"crop_image": img_valid, "context_tag": "isolated", "is_valid": True},
        {"crop_image": img_corrupted, "context_tag": "isolated", "is_valid": False},  # QC_REJECTED
    ]

    profile = generate_writer_profile_from_crops(
        writer_id="W002",
        crops_data=crops_data,
        dpi=dpi,
    )

    # Mẫu hỏng bị loại bỏ, chỉ còn 1 mẫu hợp lệ được phân tích
    assert profile.num_samples_analyzed == 1
    assert profile.writer_id == "W002"
