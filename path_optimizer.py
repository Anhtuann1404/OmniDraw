"""
OmniDraw - Pen-lift Path Optimization (v2 - cai thien hieu nang)
==================================================================
Muc tieu: Tu anh dau vao, trich cac net ve (stroke), roi sap xep lai
thu tu ve cac net de TOI THIEU HOA tong quang duong nhac but (pen-up
travel) giua cac net.

Pipeline:
  1. Anh -> grayscale -> Canny edge detection
  2. Tim contours (moi contour la 1 stroke, danh sach diem lien tuc)
  3. Loc bo stroke qua nho (noise)
  3b. [MOI] Noi chuoi (chain) cac stroke co diem dau/cuoi gan nhau
      thanh net dai hon -> giam so luong phan tu can toi uu, dac biet
      quan trong voi anh nhieu texture/chi tiet (VD: da ran, nan hoa...)
  4. Toi uu thu tu stroke:
     - [MOI] Nearest Neighbor dung KD-tree (scipy.spatial.cKDTree)
       thay vi so sanh tuyen tinh -> nhanh hon nhieu voi hang nghin stroke
     - [MOI] Cai tien theo danh sach hang xom khong gian (candidate list
       tu KD-tree) thay vi 2-opt duyet toan bo cap -> scale tot voi
       so luong stroke lon (hang nghin), khong bi cham nhu ban dau
  5. Xuat: anh minh hoa + so lieu quang duong truoc/sau toi uu + JSON

Chua ket noi voi OmniDraw_API_Spec.md / 01_tech-stack.md (chua co san).
Khi co 2 file nay, can chinh lai input/output format cho dung chuan
chung cua nhom (VD: dinh dang JSON tra ve, don vi toa do, ten field...).

Cach dung:
    python path_optimizer.py --image duong_dan_anh.jpg --output_dir out/
"""

import argparse
import json
import math
import os
import time

import cv2
import numpy as np
from scipy.spatial import cKDTree


# ----------------------------- Buoc 1-3: Trich stroke -----------------------------

def extract_strokes(image_path, canny_low=50, canny_high=150,
                     min_stroke_len=15, resize_max_dim=800):
    """
    Doc anh, trich duong net thanh danh sach cac stroke.
    Moi stroke la mot np.ndarray shape (N, 2) toa do (x, y) lien tuc.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Khong doc duoc anh: {image_path}")

    # Resize de xu ly nhanh hon voi anh lon, giu ti le
    h, w = img.shape[:2]
    scale = 1.0
    if max(h, w) > resize_max_dim:
        scale = resize_max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, canny_low, canny_high)

    # Lam day net mong 1 chut de contour lien tuc hon
    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    strokes = []
    for c in contours:
        pts = c.reshape(-1, 2).astype(np.float64)
        if len(pts) < 2:
            continue
        length = polyline_length(pts)
        if length < min_stroke_len:
            continue
        strokes.append(pts)

    return strokes, img, scale


def polyline_length(pts):
    if len(pts) < 2:
        return 0.0
    diffs = np.diff(pts, axis=0)
    return float(np.sum(np.sqrt(np.sum(diffs ** 2, axis=1))))


def chain_strokes(strokes, snap_dist=15.0, max_chain_iters=3):
    """
    [MOI] Noi cac stroke co diem dau/cuoi nam gan nhau (trong ban kinh
    snap_dist) thanh 1 net dai hon. Muc dich: voi anh nhieu texture
    (VD: da ran, nan hoa xe dap...), Canny + findContours thuong tra ve
    hang nghin doan rat ngan bi vun ra do nhieu - trong khi ve mat vat
    ly, nhieu doan trong so do lien tiep nhau va nen duoc coi la 1 net
    but lien tuc.

    Thuat toan: xay KD-tree tren tat ca diem dau + diem cuoi cua stroke,
    voi moi stroke chua duoc noi, tim stroke khac co diem dau/cuoi gan
    nhat (<= snap_dist) va noi lien 2 stroke do (uu tien noi endpoint
    voi startpoint gan nhat). Lap lai vai vong (max_chain_iters) de noi
    tiep cac chuoi da noi voi nhau nua neu con gan.
    """
    current = [np.asarray(s, dtype=np.float64) for s in strokes]

    for _ in range(max_chain_iters):
        n = len(current)
        if n < 2:
            break

        endpoints = np.array([s[0] for s in current] + [s[-1] for s in current])
        # endpoints[0:n] = diem dau cac stroke, endpoints[n:2n] = diem cuoi
        tree = cKDTree(endpoints)

        used = set()
        merged = []
        did_merge = False

        for i in range(n):
            if i in used:
                continue
            used.add(i)
            chain = current[i]

            # Thu noi tiep ve 2 dau cua chain voi cac stroke chua dung khac
            extended = True
            guard = 0
            while extended and guard < n:
                extended = False
                guard += 1
                chain_start = chain[0]
                chain_end = chain[-1]

                candidates = []
                # Tim ung vien gan diem cuoi chain (de noi tiep phia sau)
                for query_pt, mode in [(chain_end, "end"), (chain_start, "start")]:
                    dists, idxs = tree.query(query_pt, k=min(6, 2 * n))
                    dists = np.atleast_1d(dists)
                    idxs = np.atleast_1d(idxs)
                    for d, idx in zip(dists, idxs):
                        stroke_idx = idx % n
                        if stroke_idx == i or stroke_idx in used:
                            continue
                        if d <= snap_dist:
                            is_start_pt = idx < n  # True neu la diem dau cua stroke_idx
                            candidates.append((d, stroke_idx, mode, is_start_pt))

                if candidates:
                    candidates.sort(key=lambda c: c[0])
                    d, stroke_idx, mode, is_start_pt = candidates[0]
                    other = current[stroke_idx]
                    if not is_start_pt:
                        other = other[::-1]  # dao de diem noi la diem dau cua other

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


# ----------------------------- Buoc 4: Toi uu thu tu -----------------------------

def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def nearest_neighbor_order(strokes):
    """
    [CAI THIEN] Sap xep stroke ban dau bang Nearest Neighbor, dung
    KD-tree de tim stroke gan nhat trong O(log n) thay vi so sanh
    tuyen tinh O(n) tai moi buoc -> tong do phuc tap O(n log n) thay
    vi O(n^2), quan trong khi co hang nghin stroke.

    Van cho phep dao huong tung stroke de chon diem noi gan hon.
    """
    n = len(strokes)
    starts = np.array([s[0] for s in strokes])
    ends = np.array([s[-1] for s in strokes])
    # endpoints_all[0:n] = diem dau, endpoints_all[n:2n] = diem cuoi
    endpoints_all = np.vstack([starts, ends])

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
        # Xay lai KD-tree tren cac diem dau/cuoi cua stroke con lai
        # (chi lay stroke chua dung, ca 2 dau)
        valid_ids = np.nonzero(unused_mask)[0]
        candidate_pts = np.vstack([starts[valid_ids], ends[valid_ids]])
        tree = cKDTree(candidate_pts)

        k = min(4, len(candidate_pts))
        dists, idxs = tree.query(current_end, k=k)
        dists = np.atleast_1d(dists)
        idxs = np.atleast_1d(idxs)

        best_d = dists[0]
        best_pos = idxs[0]
        num_valid = len(valid_ids)
        best_stroke_id = valid_ids[best_pos % num_valid]
        best_reversed = best_pos >= num_valid  # True neu diem gan nhat la diem cuoi

        order.append(best_stroke_id)
        reversed_flags.append(bool(best_reversed))
        unused_mask[best_stroke_id] = False
        current_end = starts[best_stroke_id] if best_reversed else ends[best_stroke_id]
        remaining -= 1

    return order, reversed_flags


def total_travel_distance(strokes, order, reversed_flags):
    """Tinh tong quang duong nhac but (khong tinh quang duong ve net)."""
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
    """Chi phi (quang duong nhac but) giua vi tri p va p+1 trong order."""
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
    [MOI - thay cho 2-opt cu] Cai tien thu tu bang Or-opt (di chuyen 1
    stroke den vi tri khac trong danh sach) dua tren DANH SACH HANG XOM
    KHONG GIAN (candidate list tu KD-tree), thay vi xet TOAN BO cap vi
    tri nhu 2-opt truyen thong.

    Ly do can thiet: voi ảnh co hang nghin stroke (VD: texture da ran,
    nan hoa...), 2-opt duyet het cap O(n^2) khong the chay xong trong
    thoi gian hop ly. O day, moi stroke chi duoc xet chuyen den GAN cac
    stroke lang gieng GAN VE MAT KHONG GIAN (khong phai gan trong danh
    sach thu tu hien tai) - day chinh la nhung vi tri co kha nang cai
    thien duong di nhat. Chi phi danh gia moi buoc la O(1) (tinh cuc
    bo), nen tong do phuc tap ~O(n * k_neighbors * so_pass), scale tot
    voi n lon.
    """
    n = len(order)
    if n < 4:
        return order, reversed_flags

    order = order[:]
    reversed_flags = reversed_flags[:]

    starts = np.array([s[0] for s in strokes])
    ends = np.array([s[-1] for s in strokes])
    all_pts = np.vstack([starts, ends])
    tree = cKDTree(all_pts)  # co dinh theo khong gian, khong doi trong qua trinh toi uu

    start_time = time.time()
    total_moves_applied = 0

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

            # Lay k stroke gan nhat VE KHONG GIAN voi diem dau/cuoi cua stroke nay
            _, nn_idxs = tree.query(np.vstack([s_p, e_p]), k=min(k_neighbors, 2 * n))
            candidate_stroke_ids = set(int(i) % n for i in np.atleast_1d(nn_idxs).ravel())
            candidate_stroke_ids.discard(idx_p)

            best_delta = -1e-6
            best_q = None
            best_rev_p = reversed_flags[p]

            old_cost = _edge_cost(strokes, order, reversed_flags, p - 1) + \
                       _edge_cost(strokes, order, reversed_flags, p)

            # Chi phi sau khi bo stroke p ra (noi p-1 truc tiep voi p+1)
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
                # Thuc hien di chuyen: bo stroke khoi vi tri p, chen vao sau vi tri best_q
                moved_idx = order.pop(p)
                moved_rev = best_rev_p
                reversed_flags.pop(p)

                # Sau khi pop(p), moi vi tri > p bi dich xuong 1
                insert_at = (best_q + 1) if best_q < p else best_q
                order.insert(insert_at, moved_idx)
                reversed_flags.insert(insert_at, moved_rev)

                pos_map = {idx: pp for pp, idx in enumerate(order)}
                improved_this_pass = True
                total_moves_applied += 1

        if not improved_this_pass:
            break

    return order, reversed_flags


# ----------------------------- Buoc 5: Xuat ket qua -----------------------------

def visualize(img, strokes, order, reversed_flags, output_path):
    """Ve anh minh hoa: net ve lien tuc mau xanh, duong nhac but mau do net dut."""
    canvas = img.copy()
    prev_end = None
    for step, (idx, rev) in enumerate(zip(order, reversed_flags)):
        pts = strokes[idx]
        if rev:
            pts = pts[::-1]

        # Duong nhac but (pen-up) tu diem truoc den diem dau stroke nay
        if prev_end is not None:
            draw_dashed_line(canvas, tuple(prev_end.astype(int)),
                              tuple(pts[0].astype(int)), (0, 0, 255), 1)

        # Ve stroke (pen-down) mau xanh
        for k in range(len(pts) - 1):
            p1 = tuple(pts[k].astype(int))
            p2 = tuple(pts[k + 1].astype(int))
            cv2.line(canvas, p1, p2, (0, 200, 0), 2)

        prev_end = pts[-1]

    cv2.imwrite(output_path, canvas)


def draw_dashed_line(canvas, p1, p2, color, thickness, dash_len=6):
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    n_dashes = max(1, int(length // dash_len))
    for i in range(n_dashes):
        if i % 2 == 0:
            t0 = i / n_dashes
            t1 = min(1.0, (i + 1) / n_dashes)
            xa = int(x1 + (x2 - x1) * t0)
            ya = int(y1 + (y2 - y1) * t0)
            xb = int(x1 + (x2 - x1) * t1)
            yb = int(y1 + (y2 - y1) * t1)
            cv2.line(canvas, (xa, ya), (xb, yb), color, thickness)


def export_json(strokes, order, reversed_flags, scale, output_path):
    data = {
        "num_strokes": len(order),
        "image_scale_applied": scale,
        "stroke_order": []
    }
    for step, (idx, rev) in enumerate(zip(order, reversed_flags)):
        pts = strokes[idx]
        if rev:
            pts = pts[::-1]
        data["stroke_order"].append({
            "step": step,
            "original_index": int(idx),
            "reversed": bool(rev),
            "num_points": len(pts),
            "start": pts[0].tolist(),
            "end": pts[-1].tolist(),
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ----------------------------- Main -----------------------------

def run(image_path, output_dir, snap_dist=15.0):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    print(f"[1/5] Trich duong net tu: {image_path}")
    strokes, img, scale = extract_strokes(image_path)
    print(f"      -> Tim thay {len(strokes)} stroke tho (truoc khi noi chuoi)")

    if len(strokes) < 2:
        print("      Qua it stroke de toi uu thu tu, dung tai day.")
        return

    print(f"[2/5] Noi chuoi cac stroke gan nhau (snap_dist={snap_dist}px)...")
    t0 = time.time()
    strokes = chain_strokes(strokes, snap_dist=snap_dist)
    print(f"      -> Con lai {len(strokes)} stroke sau khi noi chuoi "
          f"({time.time() - t0:.2f}s)")

    print("[3/5] Sap xep ban dau (Nearest Neighbor + KD-tree)...")
    t0 = time.time()
    order, reversed_flags = nearest_neighbor_order(strokes)
    nn_cost = total_travel_distance(strokes, order, reversed_flags)
    print(f"      -> Tong quang duong nhac but (NN): {nn_cost:.1f} px "
          f"({time.time() - t0:.2f}s)")

    print("[4/5] Cai tien bang Or-opt (candidate list tu KD-tree)...")
    t0 = time.time()
    order, reversed_flags = or_opt_improve(strokes, order, reversed_flags)
    final_cost = total_travel_distance(strokes, order, reversed_flags)
    improvement = (nn_cost - final_cost) / nn_cost * 100 if nn_cost > 0 else 0
    print(f"      -> Tong quang duong nhac but (Or-opt): {final_cost:.1f} px "
          f"(giam {improvement:.1f}%, {time.time() - t0:.2f}s)")

    print("[5/5] Xuat ket qua...")
    img_out_path = os.path.join(output_dir, f"{base_name}_path.png")
    json_out_path = os.path.join(output_dir, f"{base_name}_path.json")
    visualize(img, strokes, order, reversed_flags, img_out_path)
    export_json(strokes, order, reversed_flags, scale, json_out_path)
    print(f"      -> Anh minh hoa: {img_out_path}")
    print(f"      -> Du lieu JSON: {json_out_path}")

    return {
        "num_strokes": len(strokes),
        "nn_cost": nn_cost,
        "final_cost": final_cost,
        "improvement_pct": improvement,
        "image_out": img_out_path,
        "json_out": json_out_path,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OmniDraw pen-lift path optimizer (MVP)")
    parser.add_argument("--image", required=True, help="Duong dan anh dau vao")
    parser.add_argument("--output_dir", default="output", help="Thu muc luu ket qua")
    args = parser.parse_args()

    run(args.image, args.output_dir)
