import asyncio
import csv
import math
import os
import re
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

# ==========================================
# 1. KHỞI TẠO ỨNG DỤNG & CẤU HÌNH
# ==========================================
app = FastAPI(title="OmniDraw API Gateway (Integrated)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình giả lập phần cứng
ASSUMED_PEN_SPEED_MM_PER_SEC = 40.0
SVG_OUTPUT_DIR = os.environ.get("OMNIDRAW_SVG_DIR", "./svg_output")
DEVICE_CONNECTED = True
jobs: dict[str, dict] = {}
VALID_HARDWARE_ERRORS = {
    "HARDWARE_NOT_CONNECTED": "Máy không kết nối được",
    "HARDWARE_PAPER_JAM": "Phát hiện kẹt giấy",
    "HARDWARE_OUT_OF_INK": "Hết mực/bút không xuống mực",
}

# ==========================================
# 2. ĐỊNH NGHĨA DỮ LIỆU (PYDANTIC MODELS)
# ==========================================
class SvgMetrics(BaseModel):
    total_path_length_mm: Optional[float] = None
    pen_lift_distance_mm: Optional[float] = None
    pen_lift_count: Optional[int] = None
    optimize_time_ms: Optional[float] = None

class LogPayload(BaseModel):
    request_id: str
    timestamp: str
    dataset_item_id: Optional[str] = None
    method_tag: Optional[str] = None
    input_type: Optional[str] = None
    style: Optional[str] = None
    model_used: Optional[str] = None
    ai_processing_time_ms: Optional[float] = None
    svg_metrics: Optional[SvgMetrics] = None
    actual_draw_time_sec: float = 0.0
    final_status: str
    error_code: Optional[str] = None

class GenerateRequest(BaseModel):
    request_id: str
    input_type: str
    image_base64: Optional[str] = None
    prompt: Optional[str] = None
    style: str
    options: Optional[Dict[str, Any]] = None
    experiment: Optional[Dict[str, Any]] = None

class StartRequest(BaseModel):
    request_id: str
    paper_size: str = "a4"

class PauseCancelRequest(BaseModel):
    request_id: str

# ==========================================
# 3. HÀM HỖ TRỢ (HELPERS)
# ==========================================
def _log(request_id: str, message: str):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"[{request_id}] [hardware] [{ts}] {message}")

def error_response(code: str, message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"request_id": None, "status": "error", "error": {"code": code, "message": message}},
    )

def _parse_path_length_mm(d_attr: str) -> float:
    # Thuật toán đơn giản để phân tách và tính khoảng cách các điểm toạ độ SVG
    tokens = re.findall(r"[MLmlZz]|-?\d*\.?\d+", d_attr)
    total = cur_x = cur_y = start_x = start_y = 0.0
    i = 0
    cmd = None
    while i < len(tokens):
        tok = tokens[i]
        if tok in ("M", "m", "L", "l"):
            cmd = tok
            i += 1
            continue
        if tok in ("Z", "z"):
            total += math.hypot(start_x - cur_x, start_y - cur_y)
            cur_x, cur_y = start_x, start_y
            i += 1
            continue
        try:
            x, y = float(tok), float(tokens[i + 1])
        except (ValueError, IndexError):
            break
        i += 2

        nx, ny = (x, y) if cmd in ("M", "L") else (cur_x + x, cur_y + y)
        if cmd in ("M", "m") and cur_x == 0 and cur_y == 0 and total == 0:
            start_x, start_y = nx, ny
        else:
            total += math.hypot(nx - cur_x, ny - cur_y)
        cur_x, cur_y = nx, ny
        if cmd in ("M", "m"):
            start_x, start_y = nx, ny
            cmd = "L" if cmd == "M" else "l"
    return total

def svg_estimate_draw_time(request_id: str) -> int:
    svg_path = os.path.join(SVG_OUTPUT_DIR, f"output_{request_id}.svg")
    if os.path.isfile(svg_path):
        try:
            with open(svg_path, "r", encoding="utf-8") as f:
                paths = re.findall(r'<path[^>]*\bd="([^"]+)"', f.read())
                length_mm = sum(_parse_path_length_mm(d) for d in paths)
            if length_mm > 0:
                return max(2, int(round(length_mm / ASSUMED_PEN_SPEED_MM_PER_SEC)))
        except Exception as exc:
            print(f"[warn] khong doc duoc {svg_path}: {exc}")
    
    seed = sum(ord(c) for c in request_id) % 20
    return 15 + seed 

async def _run_job(request_id: str):
    job = jobs[request_id]
    job["status"] = "printing"
    job["started_at"] = time.monotonic()
    total = job["total_draw_time_sec"]

    while True:
        await asyncio.sleep(0.5)
        job_now = jobs.get(request_id)
        if job_now is None or job_now["status"] in ("paused", "cancelled", "error"):
            return
        
        elapsed = job_now["elapsed_before_pause"] + (time.monotonic() - job_now["started_at"])
        job_now["progress_percent"] = min(99, int((elapsed / total) * 100))
        job_now["estimated_time_remaining_sec"] = max(0, int(total - elapsed))

        if elapsed >= total:
            job_now.update({"status": "done", "progress_percent": 100, "estimated_time_remaining_sec": 0, "actual_draw_time_sec": int(elapsed)})
            _log(request_id, f"ve xong, actual_draw_time_sec={int(elapsed)}")
            return

# ==========================================
# 4. API PHẦN MỀM & LOGGING
# ==========================================
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Trạm trung chuyển OmniDraw đã sẵn sàng!"}

CSV_COLUMNS = [
    "request_id", "timestamp", "dataset_item_id", "method_tag", "input_type", 
    "style", "model_used", "ai_processing_time_ms", "svg_metrics.total_path_length_mm", 
    "svg_metrics.pen_lift_distance_mm", "svg_metrics.pen_lift_count", 
    "svg_metrics.optimize_time_ms", "actual_draw_time_sec", "final_status", "error_code"
]

@app.post("/api/log/experiment")
def log_experiment(payload: LogPayload):
    os.makedirs("logs", exist_ok=True)
    file_path = "logs/experiment_log.csv"
    file_exists = os.path.isfile(file_path)
    metrics = payload.svg_metrics or SvgMetrics()

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(CSV_COLUMNS)
        writer.writerow([
            payload.request_id, payload.timestamp, payload.dataset_item_id, payload.method_tag, 
            payload.input_type, payload.style, payload.model_used, payload.ai_processing_time_ms,
            metrics.total_path_length_mm, metrics.pen_lift_distance_mm, metrics.pen_lift_count, 
            metrics.optimize_time_ms, payload.actual_draw_time_sec, payload.final_status, payload.error_code
        ])
    return {"success": True, "message": "Đã lưu log thành công."}

@app.post("/api/ai/generate")
async def generate_ai_image(request: GenerateRequest):
    await asyncio.sleep(3)
    return {
        "request_id": request.request_id,
        "result_image_base64": "https://images.unsplash.com/photo-1547826039-bfc35e0f1ea8?auto=format&fit=crop&w=800&q=80",
        "meta": {"model_used": "ai-core-v1-python", "processing_time_ms": 3000},
    }

@app.get("/api/history")
async def get_history():
    return {"items": [{"id": "1", "title": "Mèo ngủ", "style": "sketch", "time_ago": "2 ngày trước", "minutes": 12, "thumbnail_url": None}]}

# ==========================================
# 5. API ĐIỀU KHIỂN PHẦN CỨNG (AXIDRAW)
# ==========================================
@app.post("/api/print/start")
async def start_print(body: StartRequest):
    if not DEVICE_CONNECTED:
        return error_response("HARDWARE_NOT_CONNECTED", "Máy không kết nối được", 503)
    
    total = svg_estimate_draw_time(body.request_id)
    jobs[body.request_id] = {
        "status": "queued", "progress_percent": 0, "estimated_time_remaining_sec": total,
        "actual_draw_time_sec": None, "error": None, "total_draw_time_sec": total,
        "started_at": None, "elapsed_before_pause": 0.0, "task": None,
    }
    jobs[body.request_id]["task"] = asyncio.create_task(_run_job(body.request_id))
    return {"request_id": body.request_id, "status": "printing"}

@app.post("/api/print/pause")
async def pause_print(body: PauseCancelRequest):
    job = jobs.get(body.request_id)
    if not job or job["status"] != "printing":
        raise HTTPException(status_code=409, detail="Không thể pause lúc này")
    
    job["elapsed_before_pause"] += (time.monotonic() - job["started_at"])
    job["status"] = "paused"
    return {"request_id": body.request_id, "status": "paused"}

@app.post("/api/print/resume")
async def resume_print(body: PauseCancelRequest):
    job = jobs.get(body.request_id)
    if not job or job["status"] != "paused":
        raise HTTPException(status_code=409, detail="Chưa pause nên không thể resume")
    
    job.update({"started_at": time.monotonic(), "status": "printing", "task": asyncio.create_task(_run_job(body.request_id))})
    return {"request_id": body.request_id, "status": "printing"}

@app.post("/api/print/cancel")
async def cancel_print(body: PauseCancelRequest):
    job = jobs.get(body.request_id)
    if not job: raise HTTPException(status_code=404, detail="ID không tồn tại")
    
    if job.get("task") and not job["task"].done(): job["task"].cancel()
    job["status"] = "cancelled"
    return {"request_id": body.request_id, "status": "cancelled"}

@app.get("/api/print/status/{request_id}")
async def get_status(request_id: str, simulate_error: Optional[str] = None):
    job = jobs.get(request_id)
    if not job: raise HTTPException(status_code=404, detail="ID không tồn tại")

    if simulate_error in VALID_HARDWARE_ERRORS:
        job.update({"status": "error", "error": {"code": simulate_error, "message": VALID_HARDWARE_ERRORS[simulate_error]}})

    response = {k: v for k, v in job.items() if k in ["status", "progress_percent", "estimated_time_remaining_sec", "error"]}
    response["request_id"] = request_id
    if job["status"] == "done": response["actual_draw_time_sec"] = job["actual_draw_time_sec"]
    return response

# ==========================================
# 6. GIAO DIỆN TEST HTML
# ==========================================
@app.get("/tester", response_class=HTMLResponse)
async def html_tester():
    # Trang giao diện HTML tĩnh nằm gọn trong 1 chuỗi để test 
    return """
    <!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><title>OmniDraw Mock Printer</title>
    <style>body{font-family:sans-serif;max-width:600px;margin:40px auto;}</style></head>
    <body><h2>🖨️ OmniDraw Mock Tester</h2>
    <p>Truy cập <a href="/docs">/docs</a> để dùng Swagger UI đầy đủ.</p>
    </body></html>
    """