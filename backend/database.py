import sqlite3
import os
import datetime
import re
import math

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "omnidraw.db")
SVG_DIR = os.path.join(os.path.dirname(__file__), "svg_output")

def parse_svg_info(svg_path):
    """Tính toán nhanh số nét vẽ, chiều dài và thời gian ước tính từ file SVG nếu database chưa có."""
    if not os.path.exists(svg_path):
        return None
    try:
        with open(svg_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Xác định khổ giấy từ width / height
        w_match = re.search(r'width="([\d.]+)mm"', content)
        h_match = re.search(r'height="([\d.]+)mm"', content)
        paper_size = "a4"
        if w_match and h_match:
            w, h = float(w_match.group(1)), float(h_match.group(1))
            if abs(w - 297) < 5 and abs(h - 420) < 5:
                paper_size = "a3"
            elif abs(w - 148) < 5 and abs(h - 210) < 5:
                paper_size = "a5"
            else:
                paper_size = "a4"

        paths = re.findall(r'<path[^>]*d="([^"]+)"', content)
        stroke_count = len(paths)
        if stroke_count == 0:
            return None

        total_draw_mm = 0.0
        total_lift_mm = 0.0
        prev_end = None

        for d in paths:
            coords = re.findall(r'([ML])\s*([\d.-]+)\s*,\s*([\d.-]+)', d)
            if not coords:
                continue
            pts = [(float(c[1]), float(c[2])) for c in coords]
            if prev_end is not None:
                total_lift_mm += math.hypot(pts[0][0] - prev_end[0], pts[0][1] - prev_end[1])
            prev_end = pts[-1]
            for i in range(len(pts) - 1):
                total_draw_mm += math.hypot(pts[i+1][0] - pts[i][0], pts[i+1][1] - pts[i][1])

        # Tốc độ vẽ giả định 40mm/s
        est_sec = (total_draw_mm + total_lift_mm) / 40.0
        est_min = max(1, math.ceil(est_sec / 60.0))

        return {
            "stroke_count": stroke_count,
            "paper_size": paper_size,
            "total_path_length_mm": round(total_draw_mm, 2),
            "pen_lift_distance_mm": round(total_lift_mm, 2),
            "pen_lift_count": max(0, stroke_count - 1),
            "estimated_minutes": est_min,
        }
    except Exception as e:
        print(f"[warn] parse_svg_info error: {e}")
        return None

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tạo bảng lịch sử nếu chưa có
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            request_id TEXT PRIMARY KEY,
            title TEXT,
            style TEXT,
            input_type TEXT,
            created_at TIMESTAMP,
            actual_draw_time_sec INTEGER,
            stroke_count INTEGER,
            thumbnail_url TEXT,
            paper_size TEXT,
            model_used TEXT,
            estimated_minutes INTEGER,
            total_path_length_mm REAL,
            pen_lift_distance_mm REAL
        )
    ''')
    # Tự động bổ sung các cột mới nếu bảng cũ chưa có
    new_cols = [
        ("paper_size", "TEXT"),
        ("model_used", "TEXT"),
        ("estimated_minutes", "INTEGER"),
        ("total_path_length_mm", "REAL"),
        ("pen_lift_distance_mm", "REAL"),
    ]
    for col_name, col_type in new_cols:
        try:
            cursor.execute(f"ALTER TABLE history ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass  # Cột đã tồn tại
    conn.commit()
    conn.close()

def save_history_record(request_id, title, style, input_type, actual_draw_time_sec, stroke_count, thumbnail_url=None, paper_size="a4", model_used=None, estimated_minutes=None, total_path_length_mm=None, pen_lift_distance_mm=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    
    # Dùng INSERT OR REPLACE để tránh lỗi trùng lặp
    cursor.execute('''
        INSERT OR REPLACE INTO history 
        (request_id, title, style, input_type, created_at, actual_draw_time_sec, stroke_count, thumbnail_url, paper_size, model_used, estimated_minutes, total_path_length_mm, pen_lift_distance_mm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        request_id, title, style, input_type, now, actual_draw_time_sec, stroke_count, thumbnail_url, paper_size, model_used, estimated_minutes, total_path_length_mm, pen_lift_distance_mm
    ))
    conn.commit()
    conn.close()

def format_time_ago(iso_str):
    if not iso_str: return "Gần đây"
    try:
        dt = datetime.datetime.fromisoformat(iso_str)
        now = datetime.datetime.now()
        diff = now - dt
        if diff.total_seconds() < 60:
            return "Vừa xong"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() // 60)} phút trước"
        elif diff.total_seconds() < 86400:
            return f"{int(diff.total_seconds() // 3600)} giờ trước"
        else:
            return f"{int(diff.total_seconds() // 86400)} ngày trước"
    except:
        return "Gần đây"

def get_all_history():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT request_id, title, style, input_type, created_at, actual_draw_time_sec, stroke_count, thumbnail_url, paper_size, model_used, estimated_minutes, total_path_length_mm, pen_lift_distance_mm
        FROM history
        ORDER BY created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for r in rows:
        req_id = r[0]
        actual_draw_sec = r[5]
        stroke_cnt = r[6]
        paper_size = r[8] or "a4"
        model_used = r[9]
        est_minutes = r[10]
        total_len = r[11]
        lift_dist = r[12]

        # Nếu thiếu stroke_count hoặc estimated_minutes, tự động tính toán từ file SVG thực tế
        if not stroke_cnt or not est_minutes or not total_len:
            svg_file = os.path.join(SVG_DIR, f"output_{req_id}.svg")
            metrics = parse_svg_info(svg_file)
            if metrics:
                if not stroke_cnt:
                    stroke_cnt = metrics["stroke_count"]
                if not est_minutes:
                    est_minutes = metrics["estimated_minutes"]
                if not total_len:
                    total_len = metrics["total_path_length_mm"]
                if not lift_dist:
                    lift_dist = metrics["pen_lift_distance_mm"]
                if not r[8]:
                    paper_size = metrics["paper_size"]

        final_minutes = est_minutes if est_minutes else (max(1, round(actual_draw_sec / 60)) if actual_draw_sec else None)

        svg_metrics_obj = None
        if total_len is not None or stroke_cnt is not None:
            svg_metrics_obj = {
                "total_path_length_mm": total_len,
                "pen_lift_distance_mm": lift_dist or 0.0,
                "pen_lift_count": max(0, (stroke_cnt or 1) - 1),
            }

        items.append({
            "id": req_id,
            "title": r[1],
            "style": r[2],
            "input_type": r[3],
            "created_at": r[4],
            "actual_draw_time_sec": actual_draw_sec,
            "minutes": final_minutes,
            "estimated_minutes": est_minutes or final_minutes,
            "stroke_count": stroke_cnt,
            "paper_size": paper_size,
            "model_used": model_used,
            "svg_metrics": svg_metrics_obj,
            "thumbnail_url": r[7],
            "time_ago": format_time_ago(r[4])
        })
    return items

def delete_history_item(request_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE request_id = ?", (request_id,))
    conn.commit()
    conn.close()

