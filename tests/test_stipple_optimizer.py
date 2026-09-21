import os
import sys
import cv2
import numpy as np
import pytest

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from path_optimizer import (
    extract_strokes_stipple,
    extract_strokes,
    extract_strokes_line_art,
    extract_strokes_hatching,
    nearest_neighbor_order,
    two_opt_improve,
    or_opt_improve,
    compute_pixel_to_mm_transform,
    get_render_bounds_px,
    build_svg,
    process,
)


def _create_synthetic_portrait(h=800, w=600):
    """Fixture anh chan dung tong hop (BGR 3 channels) dung de do luong tieu chuan."""
    img = np.ones((h, w), dtype=np.uint8) * 240
    cv2.ellipse(img, (300, 320), (160, 210), 0, 0, 360, 180, -1)
    cv2.ellipse(img, (300, 230), (180, 150), 0, 0, 360, 40, -1)
    for cx, cy in [(180, 280), (420, 280), (160, 360), (440, 360)]:
        cv2.circle(img, (cx, cy), 50, 35, -1)
    cv2.ellipse(img, (235, 290), (30, 15), 0, 0, 360, 30, -1)
    cv2.ellipse(img, (365, 290), (30, 15), 0, 0, 360, 30, -1)
    cv2.rectangle(img, (185, 265), (285, 315), 10, 4)
    cv2.rectangle(img, (315, 265), (415, 315), 10, 4)
    cv2.line(img, (285, 290), (315, 290), 10, 4)
    cv2.line(img, (300, 300), (300, 355), 70, 3)
    cv2.ellipse(img, (300, 400), (45, 18), 0, 0, 360, 70, -1)
    cv2.rectangle(img, (50, 520), (550, 800), 25, -1)
    cv2.line(img, (50, 520), (240, 600), 200, 3)
    cv2.line(img, (550, 520), (360, 600), 200, 3)
    blurred = cv2.GaussianBlur(img, (5, 5), 1.0)
    return cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)


def test_stipple_determinism():
    """1. Cung anh va seed phai cho cung ket qua dong nhat."""
    img = _create_synthetic_portrait(200, 150)
    s1, size1 = extract_strokes_stipple(img, target_grid_dim=50, seed=42)
    s2, size2 = extract_strokes_stipple(img, target_grid_dim=50, seed=42)
    assert size1 == size2
    assert len(s1) == len(s2), "Determinism failed on stroke count"
    for p1, p2 in zip(s1, s2):
        assert np.array_equal(p1, p2), "Coordinates differed with same seed"


def test_stipple_edge_dots_not_culled():
    """2. Edge dots khong bi loai boi tone sampling."""
    img_split = np.ones((80, 80, 3), dtype=np.uint8) * 255
    img_split[:, :40] = 30 # vung toi tao ranh gioi Canny tai x=40
    strokes, (w, h) = extract_strokes_stipple(img_split, target_grid_dim=40, seed=42)
    # Ranh gioi x=40 phai chua day du cac cham bien net
    boundary_dots = [s for s in strokes if abs(s[0, 0] - 40.0) < 4.0]
    assert len(boundary_dots) >= 10, f"Canny edge dots must not be culled, got {len(boundary_dots)}"


def test_stipple_geometry_at_least_6_segments():
    """3. Kiem tra hinh hoc: cham khep kin (n_seg >= 6) va contour lien tuc (len >= 2)."""
    img = _create_synthetic_portrait(200, 150)
    strokes, _ = extract_strokes_stipple(img, target_grid_dim=50, seed=42)
    assert len(strokes) > 0, "Stipple phai tao duoc strokes tren anh chan dung"

    dots = [s for s in strokes if len(s) >= 7 and np.allclose(s[0], s[-1])]
    contours = [s for s in strokes if not (len(s) >= 7 and np.allclose(s[0], s[-1]))]

    assert len(dots) > 0, "Phai tao duoc cac hat cham sac do (dots)"
    for s in dots:
        assert len(s) >= 7, f"Moi cham phai co it nhat 7 diem (6 segments), nhan {len(s)}"
        assert np.allclose(s[0], s[-1]), "Cham phai la polygon khep kin tai diem dau"

    for s in contours:
        assert len(s) >= 2, f"Contour phai co it nhat 2 diem, nhan {len(s)}"


def test_stipple_radius_bounds():
    """4. Ban kinh cua cac hat cham nam trong dai thich ung cho phep."""
    img = _create_synthetic_portrait(200, 150)
    grid_dim = 50
    strokes, (w, h) = extract_strokes_stipple(img, target_grid_dim=grid_dim, seed=42)
    cell_size = min(w, h) / float(grid_dim)

    dots = [s for s in strokes if len(s) >= 7 and np.allclose(s[0], s[-1])]
    assert len(dots) > 0, "Phai co cac hat cham de kiem tra ban kinh"

    for s in dots:
        center = np.mean(s[:-1], axis=0)
        r = float(np.linalg.norm(s[0] - center))
        factor = r / cell_size
        assert 0.18 <= factor <= 0.45, f"Radius factor {factor:.3f} out of allowable range"


def test_stipple_white_image_no_anomalous_dots():
    """5. Anh trang khong tao so cham bat thuong."""
    white_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    strokes, _ = extract_strokes_stipple(white_img, target_grid_dim=50)
    assert len(strokes) == 0, f"White image should produce 0 dots, got {len(strokes)}"


def test_stipple_black_image_in_bounds():
    """6. Anh den khong gay loi hoac vuot bounds."""
    black_img = np.zeros((80, 80, 3), dtype=np.uint8)
    strokes, img_size_px = extract_strokes_stipple(black_img, target_grid_dim=40, seed=42)
    assert len(strokes) > 0, "Black image should generate dots"
    paper_size_mm = (210.0, 297.0)
    render_bounds = get_render_bounds_px(strokes, img_size_px, smooth=False)
    scale, offset = compute_pixel_to_mm_transform(img_size_px, paper_size_mm, render_bounds_px=render_bounds)
    order, rev = nearest_neighbor_order(strokes)
    _, in_bounds = build_svg(strokes, order, rev, scale, offset, paper_size_mm, smooth=False)
    assert in_bounds is True, "Black image SVG exceeded paper bounds"


def test_stipple_svg_valid_contract():
    """7. SVG hop le va moi toa do nam trong giay."""
    img = _create_synthetic_portrait(200, 150)
    strokes, img_size_px = extract_strokes_stipple(img, target_grid_dim=40, seed=42)
    paper_size_mm = (210.0, 297.0)
    render_bounds = get_render_bounds_px(strokes, img_size_px, smooth=False)
    scale, offset = compute_pixel_to_mm_transform(img_size_px, paper_size_mm, render_bounds_px=render_bounds)
    order, rev = nearest_neighbor_order(strokes)
    svg_str, in_bounds = build_svg(strokes, order, rev, scale, offset, paper_size_mm, smooth=False)

    assert in_bounds is True, "SVG was reported out of paper bounds"
    assert "<svg" in svg_str and "</svg>" in svg_str
    assert 'fill="none"' in svg_str
    assert 'stroke="black"' in svg_str


def test_other_styles_untouched():
    """8. Cac style khac (sketch, line_art, hatching) khong doi."""
    test_img = np.zeros((60, 60, 3), dtype=np.uint8)
    test_img[10:50, 10:50] = 200

    s_sketch, _ = extract_strokes(test_img)
    assert isinstance(s_sketch, list)

    s_line, _ = extract_strokes_line_art(test_img)
    assert isinstance(s_line, list)

    s_hatch, _ = extract_strokes_hatching(test_img)
    assert isinstance(s_hatch, list)
