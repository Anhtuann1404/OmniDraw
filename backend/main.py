import asyncio
import math
import os
import re
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load biến môi trường từ file .env TRƯỚC KHI import các module khác
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel

from database import init_db, save_history_record, get_all_history

from logs.csv_logger import log_experiment_csv
from api_generator import (
    call_openai_image_api,
    APIResponse,
    PromptData,
    save_image_and_metadata,
    DATA_DIR,
    LOGS_DIR
)
from path_optimizer import process as svg_process

# ==============================================================================
# 2. Khởi tạo FastAPI App
# ==============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo DB SQLite khi app khởi động
    init_db()
    yield

app = FastAPI(
    title="OmniDraw API",
    description="API Gateway cho dự án vẽ tranh AI AxiDraw",
    version="1.3",
    lifespan=lifespan
)

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


# Cache svg_metrics phía server — TV2 ghi vào sau khi convert xong,
# endpoint /api/log/experiment tự lấy nếu frontend không gửi kèm.
_svg_metrics_cache: dict[str, dict] = {}


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
    # Nếu frontend không gửi svg_metrics → tự lấy từ cache server-side (TV2 đã ghi)
    metrics = payload.svg_metrics
    if metrics is None or (metrics.total_path_length_mm is None
                           and metrics.pen_lift_distance_mm is None):
        cached = _svg_metrics_cache.get(payload.request_id)
        if cached:
            metrics = SvgMetrics(
                total_path_length_mm=cached.get("total_path_length_mm"),
                pen_lift_distance_mm=cached.get("pen_lift_distance_mm"),
                pen_lift_count=cached.get("pen_lift_count"),
                optimize_time_ms=cached.get("optimize_time_ms"),
            )
            print(f"[log] Auto-filled svg_metrics from cache for {payload.request_id}")
    if metrics is None:
        metrics = SvgMetrics()

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
    
    # ── Lưu vào SQLite Database cho màn Thư viện ──
    if payload.final_status == "done":
        title = "Bức tranh OmniDraw" if not payload.dataset_item_id else payload.dataset_item_id
        stroke_count = (metrics.pen_lift_count + 1) if metrics.pen_lift_count is not None else 0
        thumbnail_url = f"http://localhost:8000/api/thumbnail/{payload.request_id}"
        save_history_record(
            request_id=payload.request_id,
            title=title,
            style=payload.style or "sketch",
            input_type=payload.input_type or "unknown",
            actual_draw_time_sec=payload.actual_draw_time_sec,
            stroke_count=stroke_count,
            thumbnail_url=thumbnail_url
        )
        
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

            # --- Pipeline: gọi TV2 chuyển ảnh → SVG ngay sau khi AI trả kết quả ---
            svg_metrics_data = None
            try:
                raw_b64 = resp.result_image_base64
                # Loại bỏ prefix data:image/...;base64, nếu có
                if raw_b64 and "," in raw_b64 and raw_b64.startswith("data:"):
                    raw_b64 = raw_b64.split(",", 1)[1]

                paper_w, paper_h = 210.0, 297.0
                if request.options and request.options.get("target_paper_size_mm"):
                    paper_w, paper_h = request.options["target_paper_size_mm"]

                svg_result = await asyncio.to_thread(
                    svg_process,
                    request_id=resp.request_id,
                    image_base64=raw_b64,
                    target_paper_size_mm=(paper_w, paper_h),
                    output_dir=SVG_OUTPUT_DIR,
                    style=request.style,  # TV4→TV2: truyền style để TV2 chọn thuật toán tương ứng
                )
                print(f"[pipeline] SVG conversion: {svg_result.get('status')} "
                      f"(metrics={svg_result.get('svg_metrics')})")

                if svg_result.get("status") == "success":
                    svg_metrics_data = svg_result.get("svg_metrics")
                    # Lưu vào cache server-side để /api/log/experiment có thể tự lấy
                    _svg_metrics_cache[resp.request_id] = svg_metrics_data
            except Exception as e:
                print(f"[warn] SVG conversion failed: {e}")

            return {
                "request_id": resp.request_id,
                "status": "success",
                "result_image_base64": img_data,
                "meta": {
                    "model_used": resp.model_used or "dall-e-3",
                    "processing_time_ms": resp.processing_time_ms
                },
                "svg_ready": svg_metrics_data is not None,
                "svg_metrics": svg_metrics_data,
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

    elif request.input_type == "image" and request.image_base64:
        # Nhận ảnh trực tiếp từ người dùng tải lên và chuyển sang SVG
        img_data = request.image_base64
        
        # Đảm bảo format đúng chuẩn base64 để render trên web
        if not img_data.startswith("data:") and not img_data.startswith("http"):
            img_data = f"data:image/png;base64,{img_data}"
            
        # Lấy base64 thuần để đưa vào OpenCV
        raw_b64 = request.image_base64
        if "base64," in raw_b64:
            raw_b64 = raw_b64.split("base64,")[1]
            
        # TV2: Chạy thuật toán tạo SVG 
        svg_metrics_data = None
        try:
            paper_w, paper_h = 210, 297  # Mặc định A4
            if request.options and "target_paper_size_mm" in request.options:
                paper_w, paper_h = request.options["target_paper_size_mm"]

            # Chạy hàm biến đổi ảnh thành nét vẽ SVG
            svg_result = await asyncio.to_thread(
                svg_process,
                request_id=request.request_id,
                image_base64=raw_b64,
                target_paper_size_mm=(paper_w, paper_h),
                output_dir=SVG_OUTPUT_DIR,
                style=request.style,  # TV4→TV2: truyền style để TV2 chọn thuật toán tương ứng
            )
            
            print(f"[pipeline] Image upload SVG conversion: {svg_result.get('status')} "
                  f"(metrics={svg_result.get('svg_metrics')})")

            if svg_result.get("status") == "success":
                svg_metrics_data = svg_result.get("svg_metrics")
                _svg_metrics_cache[request.request_id] = svg_metrics_data
        except Exception as e:
            print(f"[warn] SVG conversion failed for uploaded image: {e}")

        return {
            "request_id": request.request_id,
            "status": "success",
            "result_image_base64": img_data,
            "meta": {
                "model_used": "uploaded-image",
                "processing_time_ms": 0
            },
            "svg_ready": svg_metrics_data is not None,
            "svg_metrics": svg_metrics_data,
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


from fastapi.responses import FileResponse

@app.get("/api/thumbnail/{request_id}")
async def get_thumbnail(request_id: str):
    # Ưu tiên trả ảnh gốc PNG (nếu là ảnh AI sinh ra)
    png_path = os.path.join(DATA_DIR, "images", f"img_{request_id}.png")
    if os.path.exists(png_path):
        return FileResponse(png_path, media_type="image/png")
    
    # Nếu tải ảnh từ ngoài vào (không có PNG gốc ở backend), trả về bản nét vẽ SVG làm thumbnail
    svg_path = os.path.join(SVG_OUTPUT_DIR, f"output_{request_id}.svg")
    if os.path.exists(svg_path):
        return FileResponse(svg_path, media_type="image/svg+xml")
        
    return JSONResponse(status_code=404, content={"error": "Not found"})

@app.get("/api/history")
async def get_history():
    items = get_all_history()
    return {"items": items}

@app.delete("/api/history/{request_id}")
async def delete_history(request_id: str):
    from database import delete_history_item
    try:
        delete_history_item(request_id)
        return {"status": "success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ---------- Mục 5d API Spec: GET /api/print/svg/{request_id} ----------
@app.get("/api/print/svg/{request_id}")
async def get_svg_content(request_id: str):
    """Trả nội dung SVG thật để giao diện render hiệu ứng 'vẽ dần theo %'."""
    svg_path = os.path.join(SVG_OUTPUT_DIR, f"output_{request_id}.svg")
    if not os.path.isfile(svg_path):
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "error": {
                    "code": "SVG_NOT_FOUND",
                    "message": f"Chưa có file SVG cho request_id '{request_id}'. "
                               "Thuật toán chưa xử lý xong hoặc request_id không tồn tại."
                }
            }
        )
    try:
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        return {
            "request_id": request_id,
            "status": "success",
            "svg_content": svg_content,
            "error": None,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": {
                    "code": "SVG_READ_ERROR",
                    "message": f"Không thể đọc file SVG: {exc}"
                }
            }
        )


ASSUMED_PEN_SPEED_MM_PER_SEC = 40.0
SVG_OUTPUT_DIR = os.environ.get(
    "OMNIDRAW_SVG_DIR",
    os.path.join(os.path.dirname(__file__), "svg_output")
)
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