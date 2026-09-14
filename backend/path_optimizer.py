"""
OmniDraw - Module Thuat toan: Anh -> SVG toi uu duong ve
============================================================
Khop chuan giao tiep OmniDraw_API_Spec.md (v1.3) va 01_tech-stack.md.

[MOI] Ho tro 4 style theo enum o muc 1 API Spec:
    - sketch    : Canny co ban, giu net tu nhien (mac dinh, hanh vi cu)
    - line_art  : Canny nguong cao + loc net vun + lam tron duong net
                  (approxPolyDP) -> vien sac net, dut khoat
    - stipple   : chuyen vung toi thanh cac cham diem (vong tron nho),
                  mat do/kich thuoc cham ti le do toi cua vung
    - hatching  : danh bong vung toi bang duong gach cheo song song,
                  vung rat toi them lop gach cheo vuong goc (cross-hatch)

INPUT  (theo muc 3 API Spec - ket qua tu module AI):
    result_image_base64: string base64 (PNG), hoac image_path khi test local.
    request_id: string - PHAI giu xuyen suot de debug (muc 7).
    style: "sketch" | "line_art" | "stipple" | "hatching" (muc 1) - mac dinh "sketch".
    target_paper_size_mm: [width, height], mac dinh [210, 297] (A4) - tu
        options.target_paper_size_mm o muc 2.

OUTPUT (theo muc 4 API Spec):
    File SVG: output_{request_id}.svg
        - Don vi mm, khop target_paper_size_mm
        - Moi net ve = 1 <path> rieng (khong gop)
        - fill="none" bat buoc (ap dung cho ca stipple - cham duoc ve
          nhu duong vien vong tron nho, khong to dac, dung chuan may AxiDraw)
        - Chi dung <path>, <line>, <polyline>
    + svg_metrics (phuc vu log CSV khoa hoc - muc 6):
        - total_path_length_mm, pen_lift_distance_mm,
          pen_lift_count, optimize_time_ms

Ma loi dung theo bang chuan muc 8: VECTORIZE_FAILED, SVG_OUT_OF_BOUNDS.
Log theo format muc 7: [request_id] [ten module] [timestamp] message.

LUU Y (can nhom xac nhan lai):
    - API_Spec muc 4 chi mo ta "input/output" dang function, KHONG dinh nghia
      endpoint HTTP rieng cho module Thuat toan (khac voi muc 2,5,5b,5c,5d
      deu co ten endpoint ro rang). Ham process() duoi day duoc thiet ke nhu
      1 ham noi bo (hoac ham xu ly cho 1 endpoint noi bo, vd goi tu AI/backend
      pipeline sau khi co ket qua tu muc 3) - tra ve dict co status/svg_metrics
      de module ghi log (muc 6, do TV4 dam nhan) co the lay duoc so lieu.
      Neu nhom muon Thuat toan tu expose 1 REST endpoint rieng, can bo sung
      vao OmniDraw_API_Spec.md truoc, hien tai file nay chi la ham Python
      goi truc tiep hoac qua CLI (vd. tich hop noi bo trong backend/main).
    - Style khong hop le (khong nam trong 4 enum) se tu dong fallback ve
      "sketch" kem canh bao log, thay vi lam hong ca pipeline - can nhom
      xac nhan hanh vi nay co on khong hay muon tra loi VECTORIZE_FAILED.

Cach dung (CLI, test local voi file anh thay vi base64):
    python path_optimizer.py --image duong_dan_anh.jpg --request_id test123 \
        --style line_art --paper_width_mm 210 --paper_height_mm 297 --output_dir output/
"""

import argparse
import base64
import json
import math
import os
import time
from datetime import datetime, timezone

import cv2
import numpy as np
from scipy.spatial import cKDTree


MODULE_NAME = "ThuatToan"


def log_msg(request_id, message):
    """Log dung format chuan muc 7: [request_id] [ten module] [timestamp] message"""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{request_id}] [{MODULE_NAME}] [{ts}] {message}")


def make_error(code, message):
    """Cau truc loi chuan dung chung toan he thong (muc 3, 5, 8)."""
    return {"code": code, "message": message}


# ----------------------------- Doc anh dau vao -----------------------------

def decode_image(image_base64=None, image_path=None):
    """
    Doc anh tu base64 (dung khi tich hop thuc te - nhan result_image_base64
    tu module AI theo muc 3) hoac tu file path (dung khi test local qua CLI).
    """
    if image_base64 is not None:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        img_bytes = base64.b64decode(image_base64)
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    elif image_path is not None:
        img = cv2.imread(image_path)
    else:
        raise ValueError("Can cung cap image_base64 hoac image_path")

    if img is None:
        raise ValueError("Khong doc duoc anh (sai dinh dang hoac du lieu hong)")
    return img


# ----------------------------- Trich stroke tu anh -----------------------------

def extract_strokes(img, canny_low=30, canny_high=90, min_stroke_len=8,
                     resize_max_dim=1024):
    """
    [NANG CAP TOAN DIEN v2] Style sketch (Ky hoa chi danh bong):
    Tao cam giac chan thuc cua mot buc tranh ky hoa but chi:
    1. Net vien chi (Pencil Outlines): Trich xuat cac duong bao net ro (mat, mui, mieng, dang nguoi, toc).
    2. Net danh bong chi (Pencil Shading Strokes):
       - Vung bong toi (< 150): Danh cac net chi nghieng min (spacing=4.5px, goc 30 do)
         de tao mang bong do va chieu sau 3D.
       - Vung bong sau (< 85): Danh them lop net chi cheo nguoc lai (spacing=3.5px, goc -45 do)
         de nhan dam cac vung hoc mat, duoi cam, mai toc den.
    3. Vung sang duoc giu sach se, tao su tuong phan sang/toi cuc ky bat mat.
    """
    img, gray, (w, h) = _resize_and_gray(img, resize_max_dim)
    
    # 1. CLAHE tang cuong tuong phan cuc bo
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray)
    
    # 2. Net vien chi (Pencil Outlines)
    blurred = cv2.GaussianBlur(gray_eq, (3, 3), 0)
    edges = cv2.Canny(blurred, canny_low, canny_high)
    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    outline_strokes = []
    for c in contours:
        raw_pts = c.reshape(-1, 2).astype(np.float64)
        if len(raw_pts) < 2 or polyline_length(raw_pts) < min_stroke_len:
            continue
        simplified = cv2.approxPolyDP(c, epsilon=0.6, closed=False)
        pts = simplified.reshape(-1, 2).astype(np.float64)
        if len(pts) >= 2:
            outline_strokes.append(pts)
            
    # 3. Net danh bong chi vung toi (Pencil Shading Strokes in Shadow Regions)
    diag = math.hypot(w, h)
    
    def scan_pencil_shading(angle_deg, spacing, max_thresh, min_len=4):
        rad = math.radians(angle_deg)
        dx, dy = math.cos(rad), math.sin(rad)
        perp_dx, perp_dy = -dy, dx
        n_lines = int(diag / spacing) * 2
        n_samples = max(2, int(diag / 2.0))
        
        strokes_res = []
        for i in range(-n_lines // 2, n_lines // 2):
            offset = i * spacing
            cx0 = w / 2 + perp_dx * offset - dx * diag
            cy0 = h / 2 + perp_dy * offset - dy * diag
            cx1 = w / 2 + perp_dx * offset + dx * diag
            cy1 = h / 2 + perp_dy * offset + dy * diag
            
            xs = np.linspace(cx0, cx1, n_samples)
            ys = np.linspace(cy0, cy1, n_samples)
            
            in_seg = False
            seg_start = None
            last_valid = None
            for x, y in zip(xs, ys):
                valid = (0.0 <= x <= (w - 1) and 0.0 <= y <= (h - 1))
                xi, yi = int(round(x)), int(round(y))
                is_shadow = (valid and 0 <= xi < w and 0 <= yi < h and gray[yi, xi] < max_thresh)
                
                if is_shadow:
                    if not in_seg:
                        in_seg = True
                        seg_start = (x, y)
                    last_valid = (x, y)
                elif in_seg:
                    in_seg = False
                    seg_end = last_valid
                    if seg_end is not None and math.hypot(seg_end[0] - seg_start[0], seg_end[1] - seg_start[1]) >= min_len:
                        strokes_res.append(np.array([seg_start, seg_end], dtype=np.float64))
                    seg_start = None
                    last_valid = None

            if in_seg and last_valid is not None and seg_start is not None:
                seg_end = last_valid
                if math.hypot(seg_end[0] - seg_start[0], seg_end[1] - seg_start[1]) >= min_len:
                    strokes_res.append(np.array([seg_start, seg_end], dtype=np.float64))
        return strokes_res

    # Lop danh bong 1: Net chi nghieng 30 do cho vung bong toi (< 150)
    shading_1 = scan_pencil_shading(30, spacing=4.5, max_thresh=150)
    # Lop danh bong 2: Net chi nghieng -45 do cho vung bong sau / dam (< 85)
    shading_2 = scan_pencil_shading(-45, spacing=3.5, max_thresh=85)
    
    all_strokes = outline_strokes + shading_1 + shading_2
    return all_strokes, (w, h)


def polyline_length(pts):
    if len(pts) < 2:
        return 0.0
    diffs = np.diff(pts, axis=0)
    return float(np.sum(np.sqrt(np.sum(diffs ** 2, axis=1))))


def _resize_and_gray(img, resize_max_dim=1024):
    """Ham dung chung: resize an toan + chuyen grayscale, tra ve (gray, (w,h))."""
    h, w = img.shape[:2]
    if max(h, w) > resize_max_dim:
        s = resize_max_dim / max(h, w)
        img = cv2.resize(img, (int(w * s), int(h * s)))
        h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img, gray, (w, h)


def extract_strokes_line_art(img, canny_low=40, canny_high=120,
                              min_stroke_len=12, resize_max_dim=1024,
                              simplify_epsilon=1.2):
    """
    [NANG CAP] Style line_art: 
    1. Dung Bilateral Filter thay vi Gaussian: Giup lam min be mat (xoa nhieu) 
       nhung VAN GIU LAI ranh gioi sac net.
    2. Dung CLAHE: Tang tuong phan cuc bo giup cac chi tiet mo (nep gap ao,
       mat, mui) noi bat len de thuat toan bat duoc.
    3. Ha nguong Canny (120 thay vi 220) & giam min_stroke_len (12 thay vi 25):
       Giu lai cac chi tiet nho (mat, mui, bieu cam) thay vi xoa sach, giup 
       tranh bi "bo trang" nhieu cho tren hinh.
    """
    img, _, (w, h) = _resize_and_gray(img, resize_max_dim)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Bilateral Filter: xoa nhieu/texture nhung khong lam mo vien net
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # 2. CLAHE: keo sang/toi cuc bo de giup bat cac duong net an
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    filtered = clahe.apply(filtered)

    # 3. Bat canh
    edges = cv2.Canny(filtered, canny_low, canny_high)

    # Chi dilate nhe de noi cac doan canh dut quang
    kernel_dilate = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel_dilate, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    strokes = []
    for c in contours:
        raw_pts = c.reshape(-1, 2).astype(np.float64)
        # Loc net vun bang do dai (nguong cao hon sketch) - day la buoc
        # thay the cho erode, an toan hon vi khong lam hong canh that
        if polyline_length(raw_pts) < min_stroke_len:
            continue
        # Lam tron/don gian hoa duong net -> net sac, dut khoat hon
        simplified = cv2.approxPolyDP(c, epsilon=simplify_epsilon, closed=False)
        pts = simplified.reshape(-1, 2).astype(np.float64)
        if len(pts) < 2:
            continue
        strokes.append(pts)

    return strokes, (w, h)


def extract_strokes_stipple(img, target_grid_dim=160, contrast_boost=1.7,
                             dot_radius=0.75, resize_max_dim=1024, seed=42):
    """
    [NANG CAP v3] Style stipple: CLAHE + Direct Edge Enhancement + Floyd-Steinberg Dithering.
    
    Cai tien vuot bac:
    - CLAHE (Adaptive Histogram): Tu dong lam bat do sau va chi tiet o ca vung toi lan vung sang.
    - target_grid_dim tang len 160 -> do phan giai cao gap 3 lan ban dau, chi tiet cuc ky ro net.
    - Canny Edge Detection truc tiep tren luoi grid: Bat 100% cac duong vien chinh (mat, mui,
      mieng, nep nhan, vien do vat) va dat cham chinh xac khong lech 1 pixel.
    - Khu nhieu jitter o vung vien net: Giup duong bao sac gon, dứt khoát.
    """
    _, gray, (w, h) = _resize_and_gray(img, resize_max_dim)
    
    # 1. CLAHE tang cuong tuong phan cuc bo giup lam ro mat, mui, chi tiet nho
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray_clahe = clahe.apply(gray)
    
    # 2. Tinh kich thuoc luoi tinh toan phu hop theo ty le anh
    if w >= h:
        grid_w = target_grid_dim
        grid_h = max(10, int(round(target_grid_dim * (h / float(w)))))
    else:
        grid_h = target_grid_dim
        grid_w = max(10, int(round(target_grid_dim * (w / float(h)))))

    # Resize anh xam ve kich thuoc grid
    small_gray = cv2.resize(gray_clahe, (grid_w, grid_h), interpolation=cv2.INTER_AREA).astype(np.float32)
    
    # 3. Tang cuong tuong phan va gamma
    small_gray = np.clip(128.0 + (small_gray - 128.0) * contrast_boost, 0.0, 255.0)
    small_gray = 255.0 * ((small_gray / 255.0) ** 1.35)
    
    # 4. Trich xuat vien net truc tiep tren grid de chac chan giu 100% duong net quan trong
    edges = cv2.Canny(cv2.GaussianBlur(small_gray.astype(np.uint8), (3, 3), 0), 30, 95)
    is_edge_pixel = (edges > 0)
    small_gray[is_edge_pixel] = np.minimum(small_gray[is_edge_pixel], 10.0)

    # 5. Floyd-Steinberg Error Diffusion Dithering
    dithered = small_gray.copy()
    dot_coords = []
    scale_x = w / float(grid_w)
    scale_y = h / float(grid_h)
    rng = np.random.default_rng(seed)

    for y in range(grid_h):
        for x in range(grid_w):
            old_val = dithered[y, x]
            new_val = 0.0 if old_val < 128.0 else 255.0
            dithered[y, x] = new_val
            err = old_val - new_val
            
            # Khuech tan sai so sang cac pixel lan can
            if x + 1 < grid_w:
                dithered[y, x + 1] += err * (7.0 / 16.0)
            if y + 1 < grid_h:
                if x - 1 >= 0:
                    dithered[y + 1, x - 1] += err * (3.0 / 16.0)
                dithered[y + 1, x] += err * (5.0 / 16.0)
                if x + 1 < grid_w:
                    dithered[y + 1, x + 1] += err * (1.0 / 16.0)
                    
            if new_val == 0.0:
                # Neu la diem vien net: khong them jitter de net thang tap, sac gon
                if is_edge_pixel[y, x]:
                    jitter_x, jitter_y = 0.0, 0.0
                else:
                    jitter_x = (rng.uniform(-0.15, 0.15)) * scale_x
                    jitter_y = (rng.uniform(-0.15, 0.15)) * scale_y
                    
                px = max(1.0, min(w - 1.0, (x + 0.5) * scale_x + jitter_x))
                py = max(1.0, min(h - 1.0, (y + 0.5) * scale_y + jitter_y))
                dot_coords.append((px, py))

    # 6. Chuyen toa do dot thanh cac stroke vong tron nho (fill='none')
    strokes = []
    n_seg = 6
    r = max(0.5, dot_radius * (scale_x / 8.0))
    for px, py in dot_coords:
        circle_pts = [
            [px + r * math.cos(2 * math.pi * k / n_seg),
             py + r * math.sin(2 * math.pi * k / n_seg)]
            for k in range(n_seg + 1)
        ]
        strokes.append(np.array(circle_pts, dtype=np.float64))

    return strokes, (w, h)


def extract_strokes_hatching(img, base_spacing=6, cross_spacing=4,
                              dark_threshold=140, very_dark_threshold=70,
                              light_spacing=12, light_threshold=235,
                              resize_max_dim=1024, min_segment_len=3):
    """
    [NANG CAP] Style hatching: quet cac duong thang song song theo 3 huong de
    tao khoi 3D tu vung sang den vung toi:
    - Vung sang (light_threshold=235): Gach thua (spacing=12), goc 15 do -> Giup
      giu lai chieu sau cho bau troi, may, mau da, tranh viec cac vung nay bi
      trang boc / bien mat hoan toan.
    - Vung toi (dark_threshold=140): Gach day hon (spacing=6), goc 45 do.
    - Vung rat toi (very_dark_threshold=70): Gach cheo vuong goc (spacing=4), goc 135 do.
    
    Dong thoi ap dung tang cuong vien net (Edge Enhancement) giong Stipple, de
    chac chan vien dam may, duong chan troi, nep ao luon duoc ve ro.
    """
    _, gray, (w, h) = _resize_and_gray(img, resize_max_dim)
    
    # Tang cuong vien net: giong phong cach khac go, giu lai duong bao cua may, nui
    edges = cv2.Canny(cv2.GaussianBlur(gray, (3, 3), 0), 40, 120)
    gray_enhanced = gray.copy().astype(np.float32)
    gray_enhanced[edges > 0] = np.minimum(gray_enhanced[edges > 0], 50.0) # Ep vien thanh vung toi
    gray = gray_enhanced.astype(np.uint8)

    strokes = []

    def scan_diagonal(angle_deg, spacing, threshold):
        rad = math.radians(angle_deg)
        dx, dy = math.cos(rad), math.sin(rad)
        diag = math.hypot(w, h)
        perp_dx, perp_dy = -dy, dx

        n_lines = int(diag / spacing) * 2
        n_samples = max(2, int(diag))

        for i in range(-n_lines // 2, n_lines // 2):
            offset = i * spacing
            cx0 = w / 2 + perp_dx * offset - dx * diag
            cy0 = h / 2 + perp_dy * offset - dy * diag
            cx1 = w / 2 + perp_dx * offset + dx * diag
            cy1 = h / 2 + perp_dy * offset + dy * diag

            xs = np.linspace(cx0, cx1, n_samples)
            ys = np.linspace(cy0, cy1, n_samples)

            in_seg = False
            seg_start = None
            last_valid = None
            for x, y in zip(xs, ys):
                valid = (0.0 <= x <= (w - 1) and 0.0 <= y <= (h - 1))
                xi, yi = int(round(x)), int(round(y))
                dark_enough = (valid and 0 <= xi < w and 0 <= yi < h and gray[yi, xi] < threshold)

                if dark_enough:
                    if not in_seg:
                        in_seg = True
                        seg_start = (x, y)
                    last_valid = (x, y)
                elif in_seg:
                    in_seg = False
                    seg_end = last_valid
                    if seg_end is not None and math.hypot(seg_end[0] - seg_start[0], seg_end[1] - seg_start[1]) >= min_segment_len:
                        strokes.append(np.array([seg_start, seg_end], dtype=np.float64))
                    seg_start = None
                    last_valid = None

            if in_seg and last_valid is not None and seg_start is not None:
                seg_end = last_valid
                if math.hypot(seg_end[0] - seg_start[0], seg_end[1] - seg_start[1]) >= min_segment_len:
                    strokes.append(np.array([seg_start, seg_end], dtype=np.float64))

    # 1. Lop gach thua cho VUNG SANG (Bau troi, may, nen da, tuong) - Goc 15 do
    scan_diagonal(15, light_spacing, light_threshold)
    
    # 2. Lop gach net vua cho VUNG TOI - Goc 45 do
    scan_diagonal(45, base_spacing, dark_threshold)
    
    # 3. Lop gach xiet chong len cho VUNG RAT TOI - Goc 135 do
    scan_diagonal(135, cross_spacing, very_dark_threshold)

    return strokes, (w, h)


def chain_strokes(strokes, snap_dist=15.0, max_chain_iters=3):
    """
    Noi cac stroke co diem dau/cuoi gan nhau (trong ban kinh snap_dist) thanh
    1 net dai hon. Giam manh so luong stroke voi anh nhieu texture/nhieu chi
    tiet (VD: nhom anh 021-030 trong bo du lieu chuan - da ran, nan hoa...),
    giup thuat toan toi uu thu tu chay nhanh va hieu qua hon.
    """
    current = [np.asarray(s, dtype=np.float64) for s in strokes]

    for _ in range(max_chain_iters):
        n = len(current)
        if n < 2:
            break

        endpoints = np.array([s[0] for s in current] + [s[-1] for s in current])
        tree = cKDTree(endpoints)

        used = set()
        merged = []
        did_merge = False

        for i in range(n):
            if i in used:
                continue
            used.add(i)
            chain = current[i]

            extended = True
            guard = 0
            while extended and guard < n:
                extended = False
                guard += 1
                chain_start = chain[0]
                chain_end = chain[-1]

                candidates = []
                for query_pt, mode in [(chain_end, "end"), (chain_start, "start")]:
                    dists, idxs = tree.query(query_pt, k=min(6, 2 * n))
                    dists = np.atleast_1d(dists)
                    idxs = np.atleast_1d(idxs)
                    for d, idx in zip(dists, idxs):
                        stroke_idx = idx % n
                        if stroke_idx == i or stroke_idx in used:
                            continue
                        if d <= snap_dist:
                            is_start_pt = idx < n
                            candidates.append((d, stroke_idx, mode, is_start_pt))

                if candidates:
                    candidates.sort(key=lambda c: c[0])
                    d, stroke_idx, mode, is_start_pt = candidates[0]
                    other = current[stroke_idx]
                    if not is_start_pt:
                        other = other[::-1]

                    if mode == "end":
                        chain = np.vstack([chain, other])
                    else:
                        chain = np.vstack([other[::-1], chain])

                    used.add(stroke_idx)
                    extended = True
                    did_merge = True

            merged.append(chain)

        current = merged
        if not did_merge:
            break

    return current


# ----------------------------- Toi uu thu tu ve -----------------------------

def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def kinematic_cost(p1, v1, p2, lambda_turn=1.5):
    """
    Chiêu 3: Khoang cach Euclid + phat goc quay quan tinh dong hoc: dist + lambda * (1 - cos(theta)).
    # ponytail: tinh truc tiep bang tich vo huong math.hypot, khong dung them lib ngoai.
    """
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    d = math.hypot(dx, dy)
    if d < 1e-6 or lambda_turn <= 0 or v1 is None:
        return d
    v_norm = math.hypot(v1[0], v1[1])
    if v_norm < 1e-6:
        return d
    cos_t = max(-1.0, min(1.0, (v1[0] * dx + v1[1] * dy) / (v_norm * d)))
    return d + lambda_turn * (1.0 - cos_t)


def nearest_neighbor_order(strokes, lambda_turn=1.5):
    """
    Sap xep ban dau bang Nearest Neighbor ket hop phat quan tinh dong hoc (Chiêu 1 & Chiêu 3).
    # ponytail: build cKDTree dung 1 lan tren 2N endpoints; loc top-32 theo kinematic_cost.
    """
    n = len(strokes)
    starts = np.array([s[0] for s in strokes])
    ends = np.array([s[-1] for s in strokes])
    all_pts = np.vstack([starts, ends])
    tree = cKDTree(all_pts)

    fwd_exit = np.array([s[-1] - s[-2] if len(s) >= 2 else [0.0, 0.0] for s in strokes])
    rev_exit = np.array([s[0] - s[1] if len(s) >= 2 else [0.0, 0.0] for s in strokes])

    unused_mask = np.ones(n, dtype=bool)
    order = [0]
    reversed_flags = [False]
    unused_mask[0] = False
    current_end = ends[0]
    current_exit = fwd_exit[0]

    k_query = min(32, 2 * n)
    for _ in range(n - 1):
        _, idxs = tree.query(current_end, k=k_query)
        idxs = np.atleast_1d(idxs)
        valid_cands = [i for i in idxs if unused_mask[i % n]]

        if valid_cands:
            if lambda_turn > 0:
                costs = [kinematic_cost(current_end, current_exit, all_pts[i], lambda_turn)
                         for i in valid_cands]
                best_idx = valid_cands[np.argmin(costs)]
            else:
                best_idx = valid_cands[0]
        else:
            # Fallback neu ca k hang xom deu da dung
            valid_ids = np.nonzero(unused_mask)[0]
            valid_pts_idx = np.concatenate([valid_ids, valid_ids + n])
            sub_dists = np.hypot(all_pts[valid_pts_idx, 0] - current_end[0],
                                 all_pts[valid_pts_idx, 1] - current_end[1])
            best_idx = valid_pts_idx[np.argmin(sub_dists)]

        stroke_id = best_idx % n
        is_rev = (best_idx >= n)
        order.append(stroke_id)
        reversed_flags.append(bool(is_rev))
        unused_mask[stroke_id] = False
        current_end = starts[stroke_id] if is_rev else ends[stroke_id]
        current_exit = rev_exit[stroke_id] if is_rev else fwd_exit[stroke_id]

    return order, reversed_flags


def two_opt_improve(strokes, order, reversed_flags, max_passes=3, time_budget_s=3.0):
    """
    2-Opt dao nguoc doan de go cac duong nhac but cat cheo nhau (crossing edges).
    # ponytail: cua so cuc bo 50 hang xom giu do phuc tap O(N) moi pass thay vi O(N^2).
    """
    n = len(order)
    if n < 4:
        return order, reversed_flags

    t_start = time.time()
    order = list(order)
    reversed_flags = list(reversed_flags)

    def get_pts(pos):
        idx, rev = order[pos], reversed_flags[pos]
        s, e = strokes[idx][0], strokes[idx][-1]
        return (e, s) if rev else (s, e)

    for _ in range(max_passes):
        improved = False
        for i in range(n - 2):
            if time.time() - t_start > time_budget_s:
                break
            _, end_i = get_pts(i)
            start_i1, _ = get_pts(i + 1)
            d_i = dist(end_i, start_i1)

            for j in range(i + 2, min(i + 50, n)):
                _, end_j = get_pts(j)
                start_j1 = get_pts(j + 1)[0] if j + 1 < n else None
                d_j = dist(end_j, start_j1) if start_j1 is not None else 0.0

                new_d_i = dist(end_i, end_j)
                new_d_j = dist(start_i1, start_j1) if start_j1 is not None else 0.0

                if (new_d_i + new_d_j) < (d_i + d_j) - 1e-4:
                    order[i + 1 : j + 1] = order[i + 1 : j + 1][::-1]
                    reversed_flags[i + 1 : j + 1] = [not r for r in reversed_flags[i + 1 : j + 1][::-1]]
                    improved = True
                    break
            if improved:
                break
        if not improved or (time.time() - t_start > time_budget_s):
            break

    return order, reversed_flags



def total_travel_distance(strokes, order, reversed_flags):
    """Tong quang duong nhac but (khong tinh quang duong ve net), don vi = don vi cua strokes dau vao."""
    total = 0.0
    prev_end = None
    for idx, rev in zip(order, reversed_flags):
        s, e = strokes[idx][0], strokes[idx][-1]
        start_pt = e if rev else s
        end_pt = s if rev else e
        if prev_end is not None:
            total += dist(prev_end, start_pt)
        prev_end = end_pt
    return total


def _edge_cost(strokes, order, reversed_flags, p):
    n = len(order)
    if p < 0 or p + 1 >= n:
        return 0.0
    idx1, rev1 = order[p], reversed_flags[p]
    idx2, rev2 = order[p + 1], reversed_flags[p + 1]
    end1 = strokes[idx1][0] if rev1 else strokes[idx1][-1]
    start2 = strokes[idx2][-1] if rev2 else strokes[idx2][0]
    return dist(end1, start2)


def or_opt_improve(strokes, order, reversed_flags, k_neighbors=6,
                    max_passes=10, time_budget_s=8.0):
    """
    Cai tien thu tu bang Or-opt dua tren danh sach hang xom KHONG GIAN (KD-tree),
    scale tot voi hang nghin stroke (thay cho 2-opt duyet toan bo cap - qua cham).
    """
    n = len(order)
    if n < 4:
        return order, reversed_flags

    order = order[:]
    reversed_flags = reversed_flags[:]

    starts = np.array([s[0] for s in strokes])
    ends = np.array([s[-1] for s in strokes])
    all_pts = np.vstack([starts, ends])
    tree = cKDTree(all_pts)

    start_time = time.time()

    for _pass in range(max_passes):
        if (time.time() - start_time) > time_budget_s:
            break

        pos_map = {idx: p for p, idx in enumerate(order)}
        improved_this_pass = False

        for p in range(n):
            if (time.time() - start_time) > time_budget_s:
                break

            idx_p = order[p]
            s_p, e_p = strokes[idx_p][0], strokes[idx_p][-1]

            _, nn_idxs = tree.query(np.vstack([s_p, e_p]), k=min(k_neighbors, 2 * n))
            candidate_stroke_ids = set(int(i) % n for i in np.atleast_1d(nn_idxs).ravel())
            candidate_stroke_ids.discard(idx_p)

            best_delta = -1e-6
            best_q = None
            best_rev_p = reversed_flags[p]

            old_cost = _edge_cost(strokes, order, reversed_flags, p - 1) + \
                       _edge_cost(strokes, order, reversed_flags, p)

            if p > 0 and p < n - 1:
                idx_prev, rev_prev = order[p - 1], reversed_flags[p - 1]
                idx_next, rev_next = order[p + 1], reversed_flags[p + 1]
                e_prev = strokes[idx_prev][0] if rev_prev else strokes[idx_prev][-1]
                s_next = strokes[idx_next][-1] if rev_next else strokes[idx_next][0]
                gap_cost = dist(e_prev, s_next)
            else:
                gap_cost = 0.0

            for cand_idx in candidate_stroke_ids:
                q = pos_map[cand_idx]
                if q == p or q == p - 1:
                    continue

                cost_q = _edge_cost(strokes, order, reversed_flags, q)

                idx_q, rev_q = order[q], reversed_flags[q]
                e_q = strokes[idx_q][0] if rev_q else strokes[idx_q][-1]
                if q + 1 < n:
                    idx_qn, rev_qn = order[q + 1], reversed_flags[q + 1]
                    s_qn = strokes[idx_qn][-1] if rev_qn else strokes[idx_qn][0]
                else:
                    s_qn = None

                for rev_try in (False, True):
                    start_p = e_p if rev_try else s_p
                    end_p = s_p if rev_try else e_p
                    insert_cost = dist(e_q, start_p)
                    if s_qn is not None:
                        insert_cost += dist(end_p, s_qn)

                    new_cost = gap_cost + insert_cost
                    old_total = old_cost + cost_q
                    delta = new_cost - old_total

                    if delta < best_delta:
                        best_delta = delta
                        best_q = q
                        best_rev_p = rev_try

            if best_q is not None:
                moved_idx = order.pop(p)
                moved_rev = best_rev_p
                reversed_flags.pop(p)

                insert_at = (best_q + 1) if best_q < p else best_q
                order.insert(insert_at, moved_idx)
                reversed_flags.insert(insert_at, moved_rev)

                pos_map = {idx: pp for pp, idx in enumerate(order)}
                improved_this_pass = True

        if not improved_this_pass:
            break

    return order, reversed_flags


# ----------------------------- Quy doi pixel -> mm + xuat SVG -----------------------------

def compute_pixel_to_mm_transform(img_size_px, paper_size_mm, margin_mm=0.0, render_bounds_px=None):
    """
    Tinh he so quy doi pixel -> mm theo kieu "contain" (giu ty le, can giua
    trong khung giay) - dam bao khong bao gio vuot khung giay (tranh loi
    SVG_OUT_OF_BOUNDS o muc 8). margin_mm dung cho auto-deskew tranh cham le.
    render_bounds_px: (min_x, min_y, max_x, max_y) de tinh theo geometry thuc te se render.
    """
    img_w_px, img_h_px = img_size_px
    paper_w_mm, paper_h_mm = paper_size_mm

    if render_bounds_px is not None:
        min_x, min_y, max_x, max_y = render_bounds_px
    else:
        min_x = 0.0
        min_y = 0.0
        max_x = float(img_w_px)
        max_y = float(img_h_px)

    bbox_w = max(1e-3, max_x - min_x)
    bbox_h = max(1e-3, max_y - min_y)

    eff_w = max(10.0, paper_w_mm - 2 * margin_mm)
    eff_h = max(10.0, paper_h_mm - 2 * margin_mm)

    scale = min(eff_w / bbox_w, eff_h / bbox_h)
    offset_x = (paper_w_mm - (min_x + max_x) * scale) / 2.0
    offset_y = (paper_h_mm - (min_y + max_y) * scale) / 2.0

    return scale, (offset_x, offset_y)


def px_to_mm(pts_px, scale, offset, paper_size_mm=None, clamp_eps=0.001):
    """
    Quy doi pixel -> mm. Neu co truyen paper_size_mm, CLAMP ket qua ve dung
    trong khung [0, w_mm] x [0, h_mm] - day la lop phong ve cuoi cung de dam
    bao khong bao gio xuat SVG vuot khung giay (loi SVG_OUT_OF_BOUNDS), du
    sai so lam tron/tinh toan o buoc truoc co the lech ra ngoai vai phan
    nghin mm (tung gap voi style hatching do sai so int(round()) khi kiem
    tra pixel hop le).
    """
    mm_pts = pts_px * scale + np.array(offset)
    if paper_size_mm is not None:
        w_mm, h_mm = paper_size_mm
        mm_pts[:, 0] = np.clip(mm_pts[:, 0], clamp_eps, w_mm - clamp_eps)
        mm_pts[:, 1] = np.clip(mm_pts[:, 1], clamp_eps, h_mm - clamp_eps)
    return mm_pts


def rotate_points_2d(pts, angle_deg, center, paper_size_mm=None, clamp_eps=0.001):
    """
    Xoay toa do 2D quanh tam 'center' mot goc angle_deg (do).
    Dung de tu dong bu goc lech giay (Auto-Deskew) do Camera phat hien.
    """
    if abs(angle_deg) < 1e-4 or len(pts) == 0:
        return pts
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    cx, cy = center
    rel = pts - np.array([cx, cy])
    rot_x = rel[:, 0] * cos_a - rel[:, 1] * sin_a + cx
    rot_y = rel[:, 0] * sin_a + rel[:, 1] * cos_a + cy
    rot_pts = np.column_stack([rot_x, rot_y])
    if paper_size_mm is not None:
        w_mm, h_mm = paper_size_mm
        rot_pts[:, 0] = np.clip(rot_pts[:, 0], clamp_eps, w_mm - clamp_eps)
        rot_pts[:, 1] = np.clip(rot_pts[:, 1], clamp_eps, h_mm - clamp_eps)
    return rot_pts


def validate_within_bounds(all_mm_points, paper_size_mm, tolerance=0.01):
    w_mm, h_mm = paper_size_mm
    if len(all_mm_points) == 0:
        return True
    xs = all_mm_points[:, 0]
    ys = all_mm_points[:, 1]
    return bool(xs.min() >= -tolerance and xs.max() <= w_mm + tolerance and
                ys.min() >= -tolerance and ys.max() <= h_mm + tolerance)


def _catmull_rom_cubic_segments(points):
    """
    Trả về các segment Cubic Bézier (p1, c1, c2, p2)
    dùng đúng công thức hiện tại của polyline_to_path_d().
    """
    points = np.asarray(points, dtype=float)
    segments = []

    for i in range(len(points) - 1):
        p0 = points[max(0, i - 1)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(len(points) - 1, i + 2)]

        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        segments.append((p1, c1, c2, p2))

    return segments


def get_render_bounds_px(strokes, img_size_px, smooth=False, skew_angle_deg=0.0):
    """
    Lay bounds thuc te se render theo pixel:
    - Bounds ban dau bao gom rectangle anh [0, img_w] x [0, img_h]
    - Voi smooth=False: dung cac anchor points
    - Voi smooth=True: dung anchor va control point tu _catmull_rom_cubic_segments()
    - Chi mo rong bounds khi geometry that vuot rectangle anh
    - Voi skew_angle_deg != 0: xoay 4 goc quanh tam rectangle de tinh bounding box sau xoay
    """
    img_w, img_h = img_size_px
    min_x = 0.0
    min_y = 0.0
    max_x = float(img_w)
    max_y = float(img_h)

    for pts in strokes:
        if len(pts) == 0:
            continue
        pts_arr = np.asarray(pts, dtype=np.float64)
        if smooth and len(pts_arr) >= 3:
            segments = _catmull_rom_cubic_segments(pts_arr)
            for p1, c1, c2, p2 in segments:
                min_x = min(min_x, p1[0], c1[0], c2[0], p2[0])
                max_x = max(max_x, p1[0], c1[0], c2[0], p2[0])
                min_y = min(min_y, p1[1], c1[1], c2[1], p2[1])
                max_y = max(max_y, p1[1], c1[1], c2[1], p2[1])
        else:
            min_x = min(min_x, float(np.min(pts_arr[:, 0])))
            max_x = max(max_x, float(np.max(pts_arr[:, 0])))
            min_y = min(min_y, float(np.min(pts_arr[:, 1])))
            max_y = max(max_y, float(np.max(pts_arr[:, 1])))

    # Neu geometry thuc su vuot ngoai anh, mo rong doi xung de khong lam dich tam bbox
    eps = 1e-3
    if min_x < 0.0 or max_x > float(img_w):
        min_x -= eps
        max_x += eps
    if min_y < 0.0 or max_y > float(img_h):
        min_y -= eps
        max_y += eps

    # Mo rong bounds theo skew_angle_deg truoc khi tinh scale/offset
    if abs(skew_angle_deg) > 1e-4:
        cx = (min_x + max_x) / 2.0
        cy = (min_y + max_y) / 2.0
        rad = math.radians(skew_angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        corners = [
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y),
        ]
        rot_xs = []
        rot_ys = []
        for x, y in corners:
            dx = x - cx
            dy = y - cy
            rx = cx + dx * cos_a - dy * sin_a
            ry = cy + dx * sin_a + dy * cos_a
            rot_xs.append(rx)
            rot_ys.append(ry)

        # Dung chinh bbox da xoay lam bounds cuoi, mo rong doi xung voi eps chong sai so so thuc
        min_x = min(rot_xs) - eps
        max_x = max(rot_xs) + eps
        min_y = min(rot_ys) - eps
        max_y = max(rot_ys) + eps

    return (min_x, min_y, max_x, max_y)


def polyline_to_path_d(mm_pts, smooth=True):
    """
    Chuyen doi danh sach toa do mm thanh SVG path data.
    Neu smooth=True va so diem >= 3: dung Catmull-Rom spline (tau=0.5) chuyen thanh Cubic Bézier ('C'),
    giup lam muot net ve tu nhien, triet tieu goc nhon rung co khi cua co cau but.
    Neu smooth=False hoac < 3 diem: giu nguyen tuyen tinh ('L').
    """
    n = len(mm_pts)
    if n == 0:
        return ""
    if not smooth or n < 3:
        parts = [f"M{mm_pts[0][0]:.3f},{mm_pts[0][1]:.3f}"]
        for x, y in mm_pts[1:]:
            parts.append(f"L{x:.3f},{y:.3f}")
        return " ".join(parts)

    parts = [f"M{mm_pts[0][0]:.3f},{mm_pts[0][1]:.3f}"]
    for p1, c1, c2, p2 in _catmull_rom_cubic_segments(mm_pts):
        parts.append(f"C{c1[0]:.3f},{c1[1]:.3f} {c2[0]:.3f},{c2[1]:.3f} {p2[0]:.3f},{p2[1]:.3f}")
    return " ".join(parts)


def build_svg(strokes, order, reversed_flags, scale, offset, paper_size_mm,
              stroke_width_mm=0.3, smooth=True, skew_angle_deg=0.0):
    """
    Xuat SVG dung chuan muc 4 API Spec:
    - xmlns, width/height dang "{w}mm"/"{h}mm", viewBox theo don vi mm
    - Moi net ve = 1 <path> rieng (khong gop)
    - fill="none" bat buoc
    - Chi dung <path> (khong <text>/<image>/<use>)
    - smooth: bat Catmull-Rom to Cubic Bézier smoothing cho cac style duong cong
    - skew_angle_deg: goc tu dong xoay bu nghieng giay (Auto-Deskew) tu camera
    """
    w_mm, h_mm = paper_size_mm
    center = (w_mm / 2.0, h_mm / 2.0)
    path_lines = []
    all_mm_points_for_validation = []

    for idx, rev in zip(order, reversed_flags):
        pts = strokes[idx]
        if rev:
            pts = pts[::-1]
        raw_mm_pts = px_to_mm(pts, scale, offset, paper_size_mm=None)
        if abs(skew_angle_deg) > 1e-4:
            raw_mm_pts = rotate_points_2d(raw_mm_pts, skew_angle_deg, center=center, paper_size_mm=None)

        raw_validation_points = raw_mm_pts

        if smooth and len(raw_mm_pts) >= 3:
            segments = _catmull_rom_cubic_segments(raw_mm_pts)
            if segments:
                raw_validation_points = np.vstack([
                    np.vstack((p1, c1, c2, p2))
                    for p1, c1, c2, p2 in segments
                ])

        all_mm_points_for_validation.append(raw_validation_points)

        mm_pts = raw_mm_pts

        d = polyline_to_path_d(mm_pts, smooth=smooth)
        path_lines.append(f'  <path d="{d}" stroke="black" fill="none" stroke-width="{stroke_width_mm}"/>')

    all_pts_concat = np.vstack(all_mm_points_for_validation) if all_mm_points_for_validation else np.empty((0, 2))
    is_within_bounds = validate_within_bounds(all_pts_concat, paper_size_mm, tolerance=0.0)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_mm}mm" height="{h_mm}mm" '
        f'viewBox="0 0 {w_mm} {h_mm}">\n' + "\n".join(path_lines) + "\n</svg>"
    )
    return svg, is_within_bounds


# ----------------------------- Tinh svg_metrics (muc 6) -----------------------------

def compute_svg_metrics(strokes, order, reversed_flags, scale, optimize_time_ms, skew_angle_deg=0.0):
    """
    Tinh cac chi so bat buoc cho log CSV khoa hoc (muc 6):
      - total_path_length_mm : tong chieu dai net ve (khong tinh nhac but)
      - pen_lift_distance_mm : tong quang duong nhac but
      - pen_lift_count       : so lan nhac but
      - optimize_time_ms     : thoi gian tinh toan toi uu thu tu net
      - skew_angle_deg       : goc lech giay duoc tu dong bu tru (auto-deskew)
    """
    total_draw_length_px = sum(polyline_length(strokes[idx]) for idx in order)
    travel_px = total_travel_distance(strokes, order, reversed_flags)

    return {
        "total_path_length_mm": round(total_draw_length_px * scale, 3),
        "pen_lift_distance_mm": round(travel_px * scale, 3),
        "pen_lift_count": max(0, len(order) - 1),
        "optimize_time_ms": round(optimize_time_ms, 1),
        "skew_angle_deg": round(float(skew_angle_deg), 2),
    }


# ----------------------------- Ham xu ly chinh -----------------------------

VALID_STYLES = {"sketch", "line_art", "stipple", "hatching"}


def process(request_id, image_base64=None, image_path=None,
            style="sketch",
            target_paper_size_mm=(210, 297), output_dir="output",
            snap_dist=15.0, skew_angle_deg=0.0):
    """
    Ham xu ly chinh cua module Thuat toan, khop input/output muc 1-3-4-6 cua
    API Spec. Ho tro 4 style: sketch | line_art | stipple | hatching.

    Tra ve dict:
        {
          "request_id": ...,
          "status": "success" | "error",
          "style": ...,
          "svg_path": "output/output_{request_id}.svg"  (neu success),
          "svg_metrics": {...}  (neu success),
          "error": {"code":..., "message":...}  (neu error, None neu success)
        }
    """
    os.makedirs(output_dir, exist_ok=True)
    log_msg(request_id, f"Bat dau xu ly anh -> SVG (style={style}, deskew={skew_angle_deg}deg)")

    def _cleanup_stale_svg():
        try:
            base_dir = os.path.abspath(output_dir)
            target_abs = os.path.abspath(os.path.join(base_dir, f"output_{request_id}.svg"))
            if (
                os.path.commonpath([base_dir, target_abs]) == base_dir
                and os.path.dirname(target_abs) == base_dir
                and target_abs != base_dir
                and os.path.isfile(target_abs)
            ):
                os.remove(target_abs)
        except Exception:
            pass

    # Xóa file SVG cũ của request_id này nếu đang retry
    _cleanup_stale_svg()

    if style not in VALID_STYLES:
        log_msg(request_id, f"CANH BAO: style '{style}' khong hop le "
                             f"(chi nhan {sorted(VALID_STYLES)}), fallback ve 'sketch'")
        style = "sketch"

    try:
        img = decode_image(image_base64=image_base64, image_path=image_path)
    except Exception as e:
        log_msg(request_id, f"Loi doc anh: {e}")
        _cleanup_stale_svg()
        return {
            "request_id": request_id, "status": "error", "style": style,
            "svg_path": None, "svg_metrics": None,
            "error": make_error("VECTORIZE_FAILED", f"Khong doc duoc anh dau vao: {e}")
        }

    # Phan nhanh trich stroke theo style.
    # line_art chi chua duong vien (contour) nen phu hop noi chuoi (chain_strokes).
    # sketch chua ca contour va cac doan shading roi rac, KHONG noi chuoi de tranh
    # dinh cac net danh bong vao contour gay vong lap va long gai khi lam muot.
    # stipple/hatching la tap cac cham/doan gach roi rac, KHONG noi chuoi.
    if style == "sketch":
        strokes, img_size_px = extract_strokes(img)
        # Sketch chua ca contour va shading strokes nen khong duoc chain chung
        do_chain = False
    elif style == "line_art":
        strokes, img_size_px = extract_strokes_line_art(img)
        do_chain = True
    elif style == "stipple":
        strokes, img_size_px = extract_strokes_stipple(img)
        do_chain = False
    else:  # "hatching"
        strokes, img_size_px = extract_strokes_hatching(img)
        do_chain = False

    log_msg(request_id, f"Trich duoc {len(strokes)} stroke tho (style={style})")

    if len(strokes) < 1:
        log_msg(request_id, "Khong trich duoc net nao tu anh")
        _cleanup_stale_svg()
        return {
            "request_id": request_id, "status": "error", "style": style,
            "svg_path": None, "svg_metrics": None,
            "error": make_error("VECTORIZE_FAILED", "Khong trich duoc duong net nao tu anh dau vao")
        }

    if do_chain:
        strokes = chain_strokes(strokes, snap_dist=snap_dist)
        log_msg(request_id, f"Con lai {len(strokes)} stroke sau khi noi chuoi")
    else:
        log_msg(request_id, "Bo qua buoc noi chuoi (khong phu hop voi style nay)")

    t0 = time.time()
    if len(strokes) >= 2:
        order, reversed_flags = nearest_neighbor_order(strokes)
        order, reversed_flags = two_opt_improve(strokes, order, reversed_flags)
        order, reversed_flags = or_opt_improve(strokes, order, reversed_flags)
    else:
        order, reversed_flags = [0], [False]
    optimize_time_ms = (time.time() - t0) * 1000
    log_msg(request_id, f"Toi uu thu tu xong trong {optimize_time_ms:.1f}ms")

    margin = 0.0
    smooth_curve = style in ("sketch", "line_art")
    render_bounds = get_render_bounds_px(
        strokes, img_size_px, smooth=smooth_curve, skew_angle_deg=skew_angle_deg
    )
    scale, offset = compute_pixel_to_mm_transform(
        img_size_px, target_paper_size_mm, margin_mm=margin, render_bounds_px=render_bounds
    )
    svg_content, is_within_bounds = build_svg(strokes, order, reversed_flags,
                                               scale, offset, target_paper_size_mm,
                                               smooth=smooth_curve,
                                               skew_angle_deg=skew_angle_deg)

    if not is_within_bounds:
        log_msg(request_id, "CANH BAO: toa do vuot khung giay sau khi quy doi")
        _cleanup_stale_svg()
        return {
            "request_id": request_id, "status": "error", "style": style,
            "svg_path": None, "svg_metrics": None,
            "error": make_error("SVG_OUT_OF_BOUNDS", "Toa do SVG vuot khung giay sau khi quy doi mm")
        }

    svg_filename = f"output_{request_id}.svg"
    svg_path = os.path.join(output_dir, svg_filename)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    log_msg(request_id, f"Da luu SVG: {svg_path}")

    metrics = compute_svg_metrics(strokes, order, reversed_flags, scale, optimize_time_ms, skew_angle_deg=skew_angle_deg)
    log_msg(request_id, f"svg_metrics: {metrics}")

    return {
        "request_id": request_id,
        "status": "success",
        "style": style,
        "svg_path": svg_path,
        "svg_metrics": metrics,
        "error": None,
    }


# ----------------------------- CLI (test local) -----------------------------

def _run_self_check():
    """Ponytail runnable check: assert NN + 2-Opt + Or-Opt reduces travel distance."""
    np.random.seed(42)
    mock_strokes = [np.array([[x, y], [x + np.random.uniform(-4, 4), y + np.random.uniform(-4, 4)]])
                    for x in np.linspace(0, 100, 20) for y in np.linspace(0, 100, 5)]
    d_raw = total_travel_distance(mock_strokes, list(range(len(mock_strokes))), [False] * len(mock_strokes))
    order, rev = nearest_neighbor_order(mock_strokes)
    d_nn = total_travel_distance(mock_strokes, order, rev)
    order_2opt, rev_2opt = two_opt_improve(mock_strokes, order, rev)
    d_2opt = total_travel_distance(mock_strokes, order_2opt, rev_2opt)
    order_or, rev_or = or_opt_improve(mock_strokes, order_2opt, rev_2opt)
    d_final = total_travel_distance(mock_strokes, order_or, rev_or)
    assert d_final <= d_2opt + 1e-6, f"Or-Opt khong duoc lam tang: {d_final} vs {d_2opt}"

    # Assertion Chiêu 3: Quan tinh dong hoc phat U-turn cao hon duong thang
    c_straight = kinematic_cost((0, 0), (1, 0), (10, 0), lambda_turn=2.0)
    c_uturn = kinematic_cost((0, 0), (1, 0), (-10, 0), lambda_turn=2.0)
    assert c_straight == 10.0, f"Thang phai la 10.0, nhan {c_straight}"
    assert c_uturn == 14.0, f"U-turn phai la 14.0, nhan {c_uturn}"

    # Assertion Chiêu 4: Bézier smoothing chuyen polyline thanh Cubic Bézier C
    test_poly = np.array([[0, 0], [10, 5], [20, 0], [30, 10]], dtype=float)
    d_smooth = polyline_to_path_d(test_poly, smooth=True)
    d_linear = polyline_to_path_d(test_poly, smooth=False)
    assert "C" in d_smooth and d_smooth.startswith("M0.000,0.000 C"), f"Smooth loi: {d_smooth}"
    assert "C" not in d_linear and "L" in d_linear, f"Linear loi: {d_linear}"

    # Assertion Auto-Deskew: Xoay toa do bu goc lech giay
    test_line = np.array([[5.0, 10.0], [15.0, 10.0]])
    rot_90 = rotate_points_2d(test_line, 90.0, center=(10.0, 10.0))
    assert np.allclose(rot_90, [[10.0, 5.0], [10.0, 15.0]]), "Xoay 90 do that bai"
    rot_0 = rotate_points_2d(test_line, 0.0, center=(10.0, 10.0))
    assert np.allclose(rot_0, test_line), "Xoay 0 do that bai"

    # Assertion Bézier Overshoot & Bounds Validation
    overshoot_stroke = np.array([
        [1.0, 0.1],
        [2.0, 0.1],
        [3.0, 0.1],
        [4.0, 10.0],
    ])
    svg_bad, bounds_bad = build_svg(
        [overshoot_stroke],
        [0],
        [False],
        1.0,
        (0.0, 0.0),
        (210.0, 297.0),
        smooth=True,
    )
    assert bounds_bad is False

    segments = _catmull_rom_cubic_segments(overshoot_stroke)
    controls = np.vstack([
        np.vstack((c1, c2))
        for _, c1, c2, _ in segments
    ])
    assert controls[:, 1].min() < 0.0

    _, bounds_linear = build_svg(
        [overshoot_stroke],
        [0],
        [False],
        1.0,
        (0.0, 0.0),
        (210.0, 297.0),
        smooth=False,
    )
    assert bounds_linear is True

    almost_outside_stroke = np.array([
        [10.0, 0.060],
        [20.0, 0.001],
        [30.0, 0.001],
        [40.0, 0.060],
    ], dtype=float)

    _, almost_outside_bounds = build_svg(
        [almost_outside_stroke],
        [0],
        [False],
        1.0,
        (0.0, 0.0),
        (210.0, 297.0),
        smooth=True,
    )

    assert almost_outside_bounds is False

    # Đường cong hợp lệ
    valid_stroke = np.array([
        [10.0, 10.0],
        [30.0, 50.0],
        [60.0, 20.0],
        [80.0, 70.0],
        [100.0, 40.0],
    ], dtype=float)
    _, valid_bounds = build_svg(
        [valid_stroke],
        [0],
        [False],
        1.0,
        (0.0, 0.0),
        (210.0, 297.0),
        smooth=True,
    )
    assert valid_bounds is True

    # Bảo toàn output so với baseline cũ (tính theo công thức gốc)
    orig_parts = [f"M{valid_stroke[0][0]:.3f},{valid_stroke[0][1]:.3f}"]
    n_pts = len(valid_stroke)
    for i in range(n_pts - 1):
        p0 = valid_stroke[max(0, i - 1)]
        p1 = valid_stroke[i]
        p2 = valid_stroke[i + 1]
        p3 = valid_stroke[min(n_pts - 1, i + 2)]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        orig_parts.append(f"C{c1[0]:.3f},{c1[1]:.3f} {c2[0]:.3f},{c2[1]:.3f} {p2[0]:.3f},{p2[1]:.3f}")
    expected_d = " ".join(orig_parts)
    actual_d = polyline_to_path_d(valid_stroke, smooth=True)
    assert actual_d == expected_d, "Output polyline_to_path_d không khớp baseline cũ byte-for-byte"

    # Regression test: Deskew trên ảnh dọc với stroke Catmull-Rom bất đối xứng vượt bounds ảnh
    v_img_size_px = (100, 320)
    specimen_pos40 = np.array([
        [45.181, 20.217],
        [96.053, 2.620],
        [32.548, 65.054]
    ])
    specimen_neg40 = np.array([
        [100.0 - 45.181, 20.217],
        [100.0 - 96.053, 2.620],
        [100.0 - 32.548, 65.054]
    ])

    # Xác nhận control point của spline thực sự vượt ra ngoài rectangle ảnh (y < 0)
    seg_pos = _catmull_rom_cubic_segments(specimen_pos40)
    pos_ctrl_min_y = min(min(c1[1], c2[1]) for _, c1, c2, _ in seg_pos)
    assert pos_ctrl_min_y < 0.0, f"Control point phải vượt ngoài rectangle ảnh, nhận {pos_ctrl_min_y}"

    paper_dim_mm = (210.0, 297.0)
    # Kiểm tra cả +40° và -40°: build_svg() phải trả is_within_bounds=True
    for test_name, test_stroke, test_skew in [
        ("+40 deg", specimen_pos40, 40.0),
        ("-40 deg", specimen_neg40, -40.0),
    ]:
        v_bounds = get_render_bounds_px([test_stroke], v_img_size_px, smooth=True, skew_angle_deg=test_skew)
        v_scale, v_offset = compute_pixel_to_mm_transform(v_img_size_px, paper_dim_mm, margin_mm=0.0, render_bounds_px=v_bounds)
        v_svg, v_in_bounds = build_svg([test_stroke], [0], [False], v_scale, v_offset, paper_dim_mm, smooth=True, skew_angle_deg=test_skew)
        assert v_in_bounds is True, f"Deskew {test_name} phải nằm trong bounds giấy"

    # Giữ lại và kiểm tra toàn diện các góc deskew hiện có: 0°, ±3.5°, ±5°, ±10°
    for angle in [0.0, 3.5, -3.5, 5.0, -5.0, 10.0, -10.0]:
        v_bounds = get_render_bounds_px([specimen_pos40], v_img_size_px, smooth=True, skew_angle_deg=angle)
        v_scale, v_offset = compute_pixel_to_mm_transform(v_img_size_px, paper_dim_mm, margin_mm=0.0, render_bounds_px=v_bounds)
        _, v_in_bounds = build_svg([specimen_pos40], [0], [False], v_scale, v_offset, paper_dim_mm, smooth=True, skew_angle_deg=angle)
        assert v_in_bounds is True, f"Deskew {angle}° phải nằm trong bounds giấy"

    reduction = ((d_raw - d_final) / d_raw) * 100
    print(f"[SELF-CHECK PASS] Raw: {d_raw:.1f} -> Optimized: {d_final:.1f} (Giam {reduction:.1f}%) | Kinematics OK | Bézier OK | Deskew OK")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OmniDraw - module Thuat toan (anh -> SVG toi uu duong ve)")
    parser.add_argument("--image", help="Duong dan anh dau vao (test local)")
    parser.add_argument("--request_id", default="test-local", help="request_id (mac dinh: test-local)")
    parser.add_argument("--style", default="sketch", choices=sorted(VALID_STYLES),
                         help="sketch | line_art | stipple | hatching")
    parser.add_argument("--paper_width_mm", type=float, default=210.0)
    parser.add_argument("--paper_height_mm", type=float, default=297.0)
    parser.add_argument("--output_dir", default="output")
    parser.add_argument("--self-check", action="store_true", help="Chay kiem tra tu dong thuat toan")
    args = parser.parse_args()

    if args.self_check:
        _run_self_check()
    elif args.image:
        result = process(
            request_id=args.request_id,
            image_path=args.image,
            style=args.style,
            target_paper_size_mm=(args.paper_width_mm, args.paper_height_mm),
            output_dir=args.output_dir,
        )
        print("\n--- Ket qua ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        parser.print_help()