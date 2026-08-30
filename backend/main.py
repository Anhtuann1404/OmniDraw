import asyncio
import math
import os
import re
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

from logs.csv_logger import log_experiment_csv
from api_generator import (
    call_openai_image_api,
    APIResponse,
    PromptData,
    save_image_and_metadata,
    DATA_DIR,
    LOGS_DIR
)

app = FastAPI(title="OmniDraw API Gateway (Master Integrated)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_error(code: str, message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "error": {"code": code, "message": message}}
    )


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/auth/login")
async def login_admin(request: LoginRequest):
    if request.email == "admin@omnidraw.com" and request.password == "admin123":
        return {"token": "admin-token", "user": {"id": "1", "name": "Admin", "email": request.email}}
    return custom_error("AUTH_FAILED", "Sai thông tin.", 401)


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


@app.post("/api/log/experiment")
def log_experiment(payload: LogPayload):
    metrics = payload.svg_metrics or SvgMetrics()
    payload_dict = {
        "request_id": payload.request_id,
        "timestamp": payload.timestamp,
        "dataset_item_id": payload.dataset_item_id,
        "method_tag": payload.method_tag,
        "input_type": payload.input_type,
        "style": payload.style,
        "model_used": payload.model_used,
        "ai_processing_time_ms": payload.ai_processing_time_ms,
        "svg_metrics.total_path_length_mm": metrics.total_path_length_mm,
        "svg_metrics.pen_lift_distance_mm": metrics.pen_lift_distance_mm,
        "svg_metrics.pen_lift_count": metrics.pen_lift_count,
        "svg_metrics.optimize_time_ms": metrics.optimize_time_ms,
        "actual_draw_time_sec": payload.actual_draw_time_sec,
        "final_status": payload.final_status,
        "error_code": payload.error_code
    }
    log_file = os.path.join(os.path.dirname(__file__), "logs", "experiment_log.csv")
    log_experiment_csv(payload_dict, log_file)
    return {"success": True}


class GenerateRequest(BaseModel):
    request_id: str
    input_type: str
    image_base64: Optional[str] = None
    prompt: Optional[str] = None
    style: str
    options: Optional[Dict[str, Any]] = None
    experiment: Optional[Dict[str, Any]] = None


@app.post("/api/ai/generate")
async def generate_ai_image(request: GenerateRequest):
    # TV1: Xử lý Text-to-drawing qua OpenAI API
    if request.input_type == "text" and request.prompt:
        # Chạy đồng bộ trong thread pool để không block event loop của FastAPI
        resp: APIResponse = await asyncio.to_thread(
            call_openai_image_api,
            prompt=request.prompt,
            request_id=request.request_id,
            style=request.style,
        )

        if resp.status == "success" and resp.result_image_base64:
            img_data = resp.result_image_base64
            if not img_data.startswith("data:") and not img_data.startswith("http"):
                img_data = f"data:image/png;base64,{img_data}"

            # Lưu ảnh & metadata nếu cần ghi nhận
            try:
                dataset_item_id = (
                    request.experiment.get("dataset_item_id")
                    if request.experiment and request.experiment.get("dataset_item_id")
                    else "web_prompt"
                )
                p_data = PromptData(
                    dataset_item_id=dataset_item_id,
                    style=request.style,
                    prompt_text=request.prompt,
                    prompt_vi=request.prompt
                )
                save_image_and_metadata(resp, p_data)
            except Exception as e:
                print(f"[warn] Không thể lưu metadata: {e}")

            return {
                "request_id": resp.request_id,
                "status": "success",
                "result_image_base64": img_data,
                "meta": {
                    "model_used": resp.model_used or "dall-e-3",
                    "processing_time_ms": resp.processing_time_ms
                },
                "error": None
            }
        else:
            return {
                "request_id": resp.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": {
                    "code": resp.error_code or "AI_GENERATION_FAILED",
                    "message": resp.error_message or "Không thể sinh ảnh từ AI."
                }
            }

    elif request.input_type == "image":
        # Style transfer preview (chờ model style transfer từ TV1/TV2)
        img_data = request.image_base64 or "https://images.unsplash.com/photo-1547826039-bfc35e0f1ea8?auto=format&fit=crop&w=800&q=80"
        return {
            "request_id": request.request_id,
            "status": "success",
            "result_image_base64": img_data,
            "meta": {
                "model_used": "style-transfer-v1 (preview)",
                "processing_time_ms": 1500
            },
            "error": None
        }

    return {
        "request_id": request.request_id,
        "status": "error",
        "result_image_base64": None,
        "error": {
            "code": "INPUT_INVALID_FORMAT",
            "message": "input_type hoặc prompt không hợp lệ."
        }
    }


@app.get("/api/history")
async def get_history():
    return {"items": [{"id": "1", "title": "Mèo ngủ", "style": "sketch", "time_ago": "2 ngày trước", "minutes": 12,
                       "thumbnail_url": None}]}


ASSUMED_PEN_SPEED_MM_PER_SEC = 40.0
SVG_OUTPUT_DIR = os.environ.get("OMNIDRAW_SVG_DIR", "./svg_output")
jobs: dict[str, dict] = {}
DEVICE_CONNECTED = True
VALID_HARDWARE_ERRORS = {"HARDWARE_NOT_CONNECTED": "Lỗi kết nối", "HARDWARE_PAPER_JAM": "Kẹt giấy",
                         "HARDWARE_OUT_OF_INK": "Hết mực"}


class StartRequest(BaseModel):
    request_id: str
    paper_size: str = "a4"


class PauseCancelRequest(BaseModel):
    request_id: str




def _parse_path_length_mm(d_attr: str) -> float:
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
        if job_now is None or job_now["status"] in ("paused", "cancelled", "error"): return
        elapsed = job_now["elapsed_before_pause"] + (time.monotonic() - job_now["started_at"])
        job_now["progress_percent"] = min(99, int((elapsed / total) * 100))
        job_now["estimated_time_remaining_sec"] = max(0, int(total - elapsed))

        if elapsed >= total:
            job_now.update({"status": "done", "progress_percent": 100, "estimated_time_remaining_sec": 0,
                            "actual_draw_time_sec": int(elapsed)})
            return


@app.post("/api/print/start")
async def start_print(body: StartRequest):
    if not DEVICE_CONNECTED:
        return custom_error("HARDWARE_NOT_CONNECTED", "Mất kết nối máy vẽ", 503)
    if body.request_id in jobs and jobs[body.request_id]["status"] in ("printing", "paused"):
        return custom_error("JOB_ALREADY_EXISTS", "Bản vẽ này đang chạy", 409)

    total = svg_estimate_draw_time(body.request_id)
    jobs[body.request_id] = {"status": "queued", "progress_percent": 0, "estimated_time_remaining_sec": total,
                             "actual_draw_time_sec": None, "error": None, "total_draw_time_sec": total,
                             "started_at": None, "elapsed_before_pause": 0.0, "task": None}
    jobs[body.request_id]["task"] = asyncio.create_task(_run_job(body.request_id))
    return {"request_id": body.request_id, "status": "printing"}


@app.post("/api/print/pause")
async def pause_print(body: PauseCancelRequest):
    job = jobs.get(body.request_id)
    if not job: return custom_error("JOB_NOT_FOUND", "Không tìm thấy ID", 404)

    if job["status"] == "printing":
        job["elapsed_before_pause"] += (time.monotonic() - job["started_at"])
        job["status"] = "paused"
        return {"request_id": body.request_id, "status": "paused"}
    return custom_error("INVALID_STATE", "Chỉ có thể tạm dừng khi đang in", 409)


@app.post("/api/print/resume")
async def resume_print(body: PauseCancelRequest):
    job = jobs.get(body.request_id)
    if not job: return custom_error("JOB_NOT_FOUND", "Không tìm thấy ID", 404)

    if job["status"] == "paused":
        job["started_at"] = time.monotonic()
        job["status"] = "printing"
        job["task"] = asyncio.create_task(_run_job(body.request_id))
        return {"request_id": body.request_id, "status": "printing"}
    return custom_error("INVALID_STATE", "Chỉ có thể tiếp tục khi đang tạm dừng", 409)


@app.post("/api/print/cancel")
async def cancel_print(body: PauseCancelRequest):
    job = jobs.get(body.request_id)
    if not job: return custom_error("JOB_NOT_FOUND", "Không tìm thấy ID", 404)

    if job.get("task") and not job["task"].done(): job["task"].cancel()
    job["status"] = "cancelled"
    return {"request_id": body.request_id, "status": "cancelled"}


@app.get("/api/print/status/{request_id}")
async def get_status(request_id: str, simulate_error: Optional[str] = None):
    job = jobs.get(request_id)
    if not job: return custom_error("JOB_NOT_FOUND", "Không tìm thấy ID", 404)

    if simulate_error:
        job.update({"status": "error", "error": {"code": simulate_error,
                                                 "message": VALID_HARDWARE_ERRORS.get(simulate_error, "Lỗi giả lập")}})

    res = {"request_id": request_id, "status": job["status"], "progress_percent": job["progress_percent"],
           "estimated_time_remaining_sec": job["estimated_time_remaining_sec"], "error": job["error"]}
    if job["status"] == "done": res["actual_draw_time_sec"] = job["actual_draw_time_sec"]
    return res


@app.get("/")
async def root():
    return HTMLResponse("<h1>Trạm OmniDraw đang chạy ở cổng 8000!</h1>")