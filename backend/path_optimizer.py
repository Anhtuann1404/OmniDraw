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

def extract_strokes(img, canny_low=50, canny_high=150, min_stroke_len=15,
                     resize_max_dim=1024):
    """
    Trich duong net thanh danh sach stroke (pixel toa do), tra ve
    (strokes, kich_thuoc_anh_da_xu_ly (w,h)).

    Ghi chu: theo muc 1 API Spec, anh da duoc giao dien chuan hoa ve canh dai
    nhat = 1024px truoc khi vao pipeline - o day van giu 1 lop resize an toan
    (khong lam gi neu anh da dung chuan) de module nay khong phu thuoc tuyet
    doi vao viec module truoc co lam dung khong.
    """
    h, w = img.shape[:2]
    if max(h, w) > resize_max_dim:
        scale_resize = resize_max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale_resize), int(h * scale_resize)))
        h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, canny_low, canny_high)

    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    strokes = []
    for c in contours:
        pts = c.reshape(-1, 2).astype(np.float64)
        if len(pts) < 2:
            continue
        if polyline_length(pts) < min_stroke_len:
            continue
        strokes.append(pts)

    return strokes, (w, h)


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
            for x, y in zip(xs, ys):
                xi, yi = int(round(x)), int(round(y))
                valid = 0 <= xi < w and 0 <= yi < h
                dark_enough = valid and gray[yi, xi] < threshold

                if dark_enough and not in_seg:
                    in_seg = True
                    seg_start = (x, y)
                elif not dark_enough and in_seg:
                    in_seg = False
                    seg_end = (x, y)
                    if math.hypot(seg_end[0] - seg_start[0], seg_end[1] - seg_start[1]) >= min_segment_len:
                        strokes.append(np.array([seg_start, seg_end], dtype=np.float64))

            if in_seg:
                seg_end = (xs[-1], ys[-1])
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


def nearest_neighbor_order(strokes):
    """Sap xep ban dau bang Nearest Neighbor, dung KD-tree de scale tot voi hang nghin stroke."""
    n = len(strokes)
    starts = np.array([s[0] for s in strokes])
    ends = np.array([s[-1] for s in strokes])

    unused_mask = np.ones(n, dtype=bool)
    order = []
    reversed_flags = []

    current_idx = 0
    order.append(current_idx)
    reversed_flags.append(False)
    unused_mask[current_idx] = False
    current_end = ends[current_idx]

    remaining = n - 1
    while remaining > 0:
        valid_ids = np.nonzero(unused_mask)[0]
        candidate_pts = np.vstack([starts[valid_ids], ends[valid_ids]])
        tree = cKDTree(candidate_pts)

        k = min(4, len(candidate_pts))
        dists, idxs = tree.query(current_end, k=k)
        idxs = np.atleast_1d(idxs)

        best_pos = idxs[0]
        num_valid = len(valid_ids)
        best_stroke_id = valid_ids[best_pos % num_valid]
        best_reversed = best_pos >= num_valid

        order.append(best_stroke_id)
        reversed_flags.append(bool(best_reversed))
        unused_mask[best_stroke_id] = False
        current_end = starts[best_stroke_id] if best_reversed else ends[best_stroke_id]
        remaining -= 1

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

def compute_pixel_to_mm_transform(img_size_px, paper_size_mm):
    """
    Tinh he so quy doi pixel -> mm theo kieu "contain" (giu ty le, can giua
    trong khung giay) - dam bao khong bao gio vuot khung giay (tranh loi
    SVG_OUT_OF_BOUNDS o muc 8).
    """
    img_w_px, img_h_px = img_size_px
    paper_w_mm, paper_h_mm = paper_size_mm

    scale = min(paper_w_mm / img_w_px, paper_h_mm / img_h_px)
    offset_x = (paper_w_mm - img_w_px * scale) / 2.0
    offset_y = (paper_h_mm - img_h_px * scale) / 2.0

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


def validate_within_bounds(all_mm_points, paper_size_mm, tolerance=0.01):
    w_mm, h_mm = paper_size_mm
    if len(all_mm_points) == 0:
        return True
    xs = all_mm_points[:, 0]
    ys = all_mm_points[:, 1]
    return (xs.min() >= -tolerance and xs.max() <= w_mm + tolerance and
            ys.min() >= -tolerance and ys.max() <= h_mm + tolerance)


def polyline_to_path_d(mm_pts):
    parts = [f"M{mm_pts[0][0]:.3f},{mm_pts[0][1]:.3f}"]
    for x, y in mm_pts[1:]:
        parts.append(f"L{x:.3f},{y:.3f}")
    return " ".join(parts)


def build_svg(strokes, order, reversed_flags, scale, offset, paper_size_mm,
              stroke_width_mm=0.3):
    """
    Xuat SVG dung chuan muc 4 API Spec:
    - xmlns, width/height dang "{w}mm"/"{h}mm", viewBox theo don vi mm
    - Moi net ve = 1 <path> rieng (khong gop)
    - fill="none" bat buoc
    - Chi dung <path> (khong <text>/<image>/<use>)
    """
    w_mm, h_mm = paper_size_mm
    path_lines = []
    all_mm_points_for_validation = []

    for idx, rev in zip(order, reversed_flags):
        pts = strokes[idx]
        if rev:
            pts = pts[::-1]
        mm_pts = px_to_mm(pts, scale, offset, paper_size_mm=paper_size_mm)
        all_mm_points_for_validation.append(mm_pts)
        d = polyline_to_path_d(mm_pts)
        path_lines.append(f'  <path d="{d}" stroke="black" fill="none" stroke-width="{stroke_width_mm}"/>')

    all_pts_concat = np.vstack(all_mm_points_for_validation) if all_mm_points_for_validation else np.empty((0, 2))
    is_within_bounds = validate_within_bounds(all_pts_concat, paper_size_mm)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_mm}mm" height="{h_mm}mm" '
        f'viewBox="0 0 {w_mm} {h_mm}">\n' + "\n".join(path_lines) + "\n</svg>"
    )
    return svg, is_within_bounds


# ----------------------------- Tinh svg_metrics (muc 6) -----------------------------

def compute_svg_metrics(strokes, order, reversed_flags, scale, optimize_time_ms):
    """
    Tinh cac chi so bat buoc cho log CSV khoa hoc (muc 6):
      - total_path_length_mm : tong chieu dai net ve (khong tinh nhac but)
      - pen_lift_distance_mm : tong quang duong nhac but
      - pen_lift_count       : so lan nhac but
      - optimize_time_ms     : thoi gian tinh toan toi uu thu tu net
    """
    total_draw_length_px = sum(polyline_length(strokes[idx]) for idx in order)
    travel_px = total_travel_distance(strokes, order, reversed_flags)

    return {
        "total_path_length_mm": round(total_draw_length_px * scale, 3),
        "pen_lift_distance_mm": round(travel_px * scale, 3),
        "pen_lift_count": max(0, len(order) - 1),
        "optimize_time_ms": round(optimize_time_ms, 1),
    }


# ----------------------------- Ham xu ly chinh -----------------------------

VALID_STYLES = {"sketch", "line_art", "stipple", "hatching"}


def process(request_id, image_base64=None, image_path=None,
            style="sketch",
            target_paper_size_mm=(210, 297), output_dir="output",
            snap_dist=15.0):
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
    log_msg(request_id, f"Bat dau xu ly anh -> SVG (style={style})")

    if style not in VALID_STYLES:
        log_msg(request_id, f"CANH BAO: style '{style}' khong hop le "
                             f"(chi nhan {sorted(VALID_STYLES)}), fallback ve 'sketch'")
        style = "sketch"

    try:
        img = decode_image(image_base64=image_base64, image_path=image_path)
    except Exception as e:
        log_msg(request_id, f"Loi doc anh: {e}")
        return {
            "request_id": request_id, "status": "error", "style": style,
            "svg_path": None, "svg_metrics": None,
            "error": make_error("VECTORIZE_FAILED", f"Khong doc duoc anh dau vao: {e}")
        }

    # Phan nhanh trich stroke theo style. Sketch/line_art dua tren duong vien
    # (contour) nen phu hop noi chuoi (chain_strokes); stipple/hatching la tap
    # cac cham/doan gach roi rac theo thiet ke, KHONG noi chuoi (se pha vo
    # hieu ung cham/gach rieng biet).
    if style == "sketch":
        strokes, img_size_px = extract_strokes(img)
        do_chain = True
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
        order, reversed_flags = or_opt_improve(strokes, order, reversed_flags)
    else:
        order, reversed_flags = [0], [False]
    optimize_time_ms = (time.time() - t0) * 1000
    log_msg(request_id, f"Toi uu thu tu xong trong {optimize_time_ms:.1f}ms")

    scale, offset = compute_pixel_to_mm_transform(img_size_px, target_paper_size_mm)
    svg_content, is_within_bounds = build_svg(strokes, order, reversed_flags,
                                               scale, offset, target_paper_size_mm)

    if not is_within_bounds:
        log_msg(request_id, "CANH BAO: toa do vuot khung giay sau khi quy doi")
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

    metrics = compute_svg_metrics(strokes, order, reversed_flags, scale, optimize_time_ms)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OmniDraw - module Thuat toan (anh -> SVG toi uu duong ve)")
    parser.add_argument("--image", required=True, help="Duong dan anh dau vao (test local)")
    parser.add_argument("--request_id", default="test-local", help="request_id (mac dinh: test-local)")
    parser.add_argument("--style", default="sketch", choices=sorted(VALID_STYLES),
                         help="sketch | line_art | stipple | hatching")
    parser.add_argument("--paper_width_mm", type=float, default=210.0)
    parser.add_argument("--paper_height_mm", type=float, default=297.0)
    parser.add_argument("--output_dir", default="output")
    args = parser.parse_args()

    result = process(
        request_id=args.request_id,
        image_path=args.image,
        style=args.style,
        target_paper_size_mm=(args.paper_width_mm, args.paper_height_mm),
        output_dir=args.output_dir,
    )

    print("\n--- Ket qua ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))