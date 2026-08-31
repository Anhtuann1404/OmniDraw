import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "omnidraw.db")

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
            thumbnail_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_history_record(request_id, title, style, input_type, actual_draw_time_sec, stroke_count, thumbnail_url=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    
    # Dùng INSERT OR REPLACE để tránh lỗi trùng lặp (ví dụ log nhiều lần)
    cursor.execute('''
        INSERT OR REPLACE INTO history 
        (request_id, title, style, input_type, created_at, actual_draw_time_sec, stroke_count, thumbnail_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        request_id, title, style, input_type, now, actual_draw_time_sec, stroke_count, thumbnail_url
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT request_id, title, style, input_type, created_at, actual_draw_time_sec, stroke_count, thumbnail_url
        FROM history
        ORDER BY created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for r in rows:
        items.append({
            "id": r[0],
            "title": r[1],
            "style": r[2],
            "input_type": r[3],
            "created_at": r[4],
            "minutes": max(1, round((r[5] or 0) / 60)) if r[5] else None,
            "stroke_count": r[6],
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
