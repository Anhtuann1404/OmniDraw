
import asyncio
import csv
import math
import os
=======
import sys
import os

# Tự động nhận diện và chuyển sang môi trường ảo backend/venv nếu đang chạy bằng Python ngoài
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

_venv_python = os.path.join(_backend_dir, "venv", "bin", "python")
_in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
if not _in_venv and os.path.isfile(_venv_python) and sys.executable != _venv_python:
    print(f"[OmniDraw] 🔄 Đang tự động chuyển sang môi trường ảo: {_venv_python}")
    os.execv(_venv_python, [_venv_python] + sys.argv)

import asyncio
import math

import re
import time
from typing import Any, Dict, Optional, Tuple

# Load biến môi trường từ file .env (hỗ trợ cả python-dotenv lẫn đọc thủ công dự phòng)
def _load_env():
    env_paths = [
        os.path.join(_backend_dir, ".env"),
        os.path.join(_backend_dir, "..", ".env"),
    ]
    loaded = False
    try:
        from dotenv import load_dotenv
        for p in env_paths:
            if os.path.isfile(p):
                load_dotenv(p, encoding="utf-8")
                loaded = True
                break
    except ImportError:
        pass

    # Dự phòng nếu chưa cài thư viện python-dotenv: tự đọc file .env thủ công
    if not loaded:
        for p in env_paths:
            if os.path.isfile(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
                    loaded = True
                    break
                except Exception as e:
                    print(f"[warn] Không thể đọc {p}: {e}")

_load_env()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

from pydantic import BaseModel

# ==========================================
# 1. KHỞI TẠO ỨNG DỤNG & CẤU HÌNH
# ==========================================
app = FastAPI(title="OmniDraw API Gateway (Integrated)")
=======
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
from path_optimizer import process as svg_process, VALID_STYLES as ART_MODE_STYLES

if __package__:
    from .handwriting import (
        generate_handwriting_svg,
        resolve_font,
        resolve_letter_type,
        STYLE_CONFIGS,
        RENDER_PROFILES,
        LETTER_TYPES,
        TextOverflowError,
        UnsupportedCharacterError,
        UnsupportedLetterTypeError,
    )
else:
    from handwriting import (
        generate_handwriting_svg,
        resolve_font,
        resolve_letter_type,
        STYLE_CONFIGS,
        RENDER_PROFILES,
        LETTER_TYPES,
        TextOverflowError,
        UnsupportedCharacterError,
        UnsupportedLetterTypeError,
    )

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


class DoubleSlashMiddleware:
    """Tự động chuẩn hóa các URL bị thừa dấu gạch chéo (ví dụ: //api/history -> /api/history)"""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if "//" in path:
                scope["path"] = re.sub(r"/+", "/", path)
        await self.app(scope, receive, send)


app.add_middleware(DoubleSlashMiddleware)


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


SVG_OUTPUT_DIR = os.environ.get(
    "OMNIDRAW_SVG_DIR",
    os.path.join(os.path.dirname(__file__), "svg_output")
)

# Cache svg_metrics phía server — TV2 ghi vào sau khi convert xong,
# endpoint /api/log/experiment tự lấy nếu frontend không gửi kèm.
_svg_metrics_cache: dict[str, dict] = {}


def _clear_cached_svg_for_request(request_id: str):
    """Xóa file SVG và cache metrics của một request_id nếu bị retry hoặc gặp lỗi."""
    if not request_id or not isinstance(request_id, str):
        return
    _svg_metrics_cache.pop(request_id, None)
    try:
        base_dir = os.path.abspath(SVG_OUTPUT_DIR)
        target_file = os.path.abspath(os.path.join(base_dir, f"output_{request_id}.svg"))
        if (
            os.path.commonpath([base_dir, target_file]) == base_dir
            and os.path.dirname(target_file) == base_dir
            and target_file != base_dir
            and os.path.isfile(target_file)
        ):
            os.remove(target_file)
    except Exception as e:
        print(f"[warn] Failed to clear SVG for request_id '{request_id}': {e}")



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
        est_min = None
        if metrics.total_path_length_mm is not None:
            est_sec = (metrics.total_path_length_mm + (metrics.pen_lift_distance_mm or 0)) / 40.0
            est_min = max(1, math.ceil(est_sec / 60.0))

        save_history_record(
            request_id=payload.request_id,
            title=title,
            style=payload.style or "sketch",
            input_type=payload.input_type or "unknown",
            actual_draw_time_sec=payload.actual_draw_time_sec,
            stroke_count=stroke_count,
            thumbnail_url=thumbnail_url,
            paper_size="a4",
            model_used=payload.model_used,
            estimated_minutes=est_min,
            total_path_length_mm=metrics.total_path_length_mm,
            pen_lift_distance_mm=metrics.pen_lift_distance_mm
        )
        
    return {"success": True}



class GenerateRequest(BaseModel):
    request_id: str
    input_type: Optional[Any] = None
    image_base64: Optional[str] = None
    prompt: Optional[str] = None
    style: Optional[Any] = None
    options: Optional[Dict[str, Any]] = None
    experiment: Optional[Dict[str, Any]] = None

class StartRequest(BaseModel):
    request_id: str
    paper_size: str = "a4"


class PauseCancelRequest(BaseModel):
    request_id: str

def resolve_art_style(style: Any) -> Tuple[Optional[str], Optional[dict]]:
    """
    Resolve and validate style for Art Mode (input_type in {'text', 'image'}).
    Contract:
      - omitted / None: default to 'sketch'
      - valid: 'sketch', 'line_art', 'stipple', 'hatching'
      - empty string, invalid datatype, or non-enum string: reject with INPUT_INVALID_FORMAT
    """
    if style is None:
        return "sketch", None
    if not isinstance(style, str):
        return None, {
            "code": "INPUT_INVALID_FORMAT",
            "message": f"Phong cách Art Mode '{style}' không hợp lệ (sai kiểu dữ liệu). Các phong cách khả dụng: {sorted(ART_MODE_STYLES)}."
        }
    if style not in ART_MODE_STYLES:
        return None, {
            "code": "INPUT_INVALID_FORMAT",
            "message": f"Phong cách Art Mode '{style}' không hợp lệ. Các phong cách khả dụng: {sorted(ART_MODE_STYLES)}."
        }
    return style, None


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

def validate_target_paper_size(options: Optional[Dict[str, Any]]) -> Tuple[Tuple[float, float], Optional[dict]]:
    """
    Validates target_paper_size_mm in options.
    Contract:
      - omitted: default A4 [210.0, 297.0]
      - explicit null, wrong length, not numbers, bool, <= 0, NaN, Inf: reject with INPUT_INVALID_FORMAT
    """
    paper_w, paper_h = 210.0, 297.0
    if not options or "target_paper_size_mm" not in options:
        return (paper_w, paper_h), None
    paper_size = options["target_paper_size_mm"]
    if (
        not isinstance(paper_size, (list, tuple))
        or len(paper_size) != 2
        or isinstance(paper_size[0], bool)
        or isinstance(paper_size[1], bool)
        or not isinstance(paper_size[0], (int, float))
        or not isinstance(paper_size[1], (int, float))
        or not math.isfinite(paper_size[0])
        or not math.isfinite(paper_size[1])
        or paper_size[0] <= 0
        or paper_size[1] <= 0
    ):
        return (paper_w, paper_h), {
            "code": "INPUT_INVALID_FORMAT",
            "message": "target_paper_size_mm phải là danh sách [width, height] gồm 2 số dương (mm).",
        }
    return (float(paper_size[0]), float(paper_size[1])), None


def validate_skew_angle(options: Optional[Dict[str, Any]]) -> Tuple[float, Optional[dict]]:
    """
    Validates skew_angle_deg in options.
    """
    skew_angle = 0.0
    if not options:
        return skew_angle, None
    if "skew_angle_deg" in options and options["skew_angle_deg"] is not None:
        try:
            val = float(options["skew_angle_deg"])
            if not math.isfinite(val):
                raise ValueError()
            skew_angle = val
        except (ValueError, TypeError):
            return 0.0, {
                "code": "INPUT_INVALID_FORMAT",
                "message": "skew_angle_deg phải là số thực hữu hạn.",
            }
    elif options.get("auto_deskew"):
        from camera_inspector import inspect_paper
        cam_res = inspect_paper()
        skew_angle = float(cam_res.get("skew_angle_deg", 0.0))
    return skew_angle, None


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

    # 1. Kiểm tra input_type hợp lệ
    if request.input_type not in ("handwriting", "letter", "text", "image"):
        return {
            "request_id": request.request_id,
            "status": "error",
            "result_image_base64": None,
            "error": {
                "code": "INPUT_INVALID_FORMAT",
                "message": f"input_type '{request.input_type}' không hợp lệ. Các loại hỗ trợ: 'handwriting', 'text', 'image'."
            }
        }

    # 2. Phân nhánh Viết Thư Tay (Single-Stroke Bio-Mimetic Handwriting)
    if request.input_type in ("handwriting", "letter"):
        t_start = time.perf_counter()
        text_content = request.prompt or ""

        # Nếu tải lên file văn bản (.docx hoặc .txt) dưới dạng base64
        if request.image_base64:
            raw_data = request.image_base64
            if "," in raw_data:
                raw_data = raw_data.split(",", 1)[1]
            try:
                import io, base64
                decoded_bytes = base64.b64decode(raw_data)
                try:
                    import docx
                    doc = docx.Document(io.BytesIO(decoded_bytes))
                    extracted = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                    if extracted.strip():
                        text_content = extracted
                except Exception:
                    text_content = decoded_bytes.decode("utf-8", errors="ignore")
            except Exception as e:
                print(f"[warn] Lỗi giải mã file văn bản: {e}")

        if not text_content.strip():
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": {"code": "EMPTY_TEXT", "message": "Nội dung thư tay không được để trống."}
            }

        if not isinstance(request.style, str) or request.style not in STYLE_CONFIGS:
            msg = (
                f"Phong cách chữ '{request.style}' không hợp lệ (trường 'style' là bắt buộc đối với chế độ viết thư tay). "
                f"Các phong cách khả dụng: {sorted(STYLE_CONFIGS.keys())}."
            )
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": {
                    "code": "INPUT_INVALID_FORMAT",
                    "message": msg,
                }
            }
        effective_style = request.style

        # Validation target_paper_size_mm
        (paper_w, paper_h), paper_err = validate_target_paper_size(request.options)
        if paper_err:
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": paper_err,
            }

        skew_angle, skew_err = validate_skew_angle(request.options)
        if skew_err:
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": skew_err,
            }

        font_param = "oly"
        if request.options and "font" in request.options:
            font_param = request.options["font"]
            if not isinstance(font_param, str) or font_param not in RENDER_PROFILES:
                return {
                    "request_id": request.request_id,
                    "status": "error",
                    "result_image_base64": None,
                    "error": {
                        "code": "UNSUPPORTED_FONT",
                        "message": f"Font '{font_param}' chưa được hỗ trợ. Các font khả dụng: {sorted(RENDER_PROFILES.keys())}."
                    }
                }

        seed_param = request.options.get("seed") if request.options else None
        if seed_param is not None:
            if isinstance(seed_param, bool) or not isinstance(seed_param, int) or not (0 <= seed_param <= 0xFFFFFFFF):
                return {
                    "request_id": request.request_id,
                    "status": "error",
                    "result_image_base64": None,
                    "error": {
                        "code": "INVALID_SEED",
                        "message": "Seed phải là số nguyên trong khoảng 0..4294967295."
                    }
                }

        letter_type_param = "general"
        if request.options and "letter_type" in request.options:
            letter_type_param = request.options["letter_type"]
            if not isinstance(letter_type_param, str) or letter_type_param not in LETTER_TYPES:
                return {
                    "request_id": request.request_id,
                    "status": "error",
                    "result_image_base64": None,
                    "error": {
                        "code": "UNSUPPORTED_LETTER_TYPE",
                        "message": f"Loại thư '{letter_type_param}' không được hỗ trợ. Các loại thư hợp lệ: {sorted(LETTER_TYPES)}.",
                    }
                }

        font_pack_id = RENDER_PROFILES.get(font_param, {}).get("font_pack", "omnidraw_legacy")
        try:
            resolve_letter_type(letter_type_param, font_pack_id)
        except UnsupportedLetterTypeError as exc:
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": {
                    "code": "UNSUPPORTED_LETTER_TYPE",
                    "message": str(exc),
                }
            }

        # Toàn bộ validation thành công -> Dọn dẹp cache & file SVG cũ cho request_id này trước khi thực thi pipeline
        _clear_cached_svg_for_request(request.request_id)

        try:
            svg_content, metrics, in_bounds = generate_handwriting_svg(
                text=text_content,
                font=font_param,
                style=request.style,
                target_paper_size_mm=(paper_w, paper_h),
                skew_angle_deg=skew_angle,
                seed=seed_param,
                letter_type=letter_type_param,
            )
        except UnsupportedLetterTypeError as exc:
            _clear_cached_svg_for_request(request.request_id)
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": {
                    "code": "UNSUPPORTED_LETTER_TYPE",
                    "message": str(exc),
                },
            }
        except UnsupportedCharacterError as exc:
            _clear_cached_svg_for_request(request.request_id)
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": {
                    "code": "UNSUPPORTED_CHARACTER",
                    "message": str(exc),
                    "characters": list(exc.characters),
                },
            }
        except TextOverflowError as exc:
            _clear_cached_svg_for_request(request.request_id)
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": {
                    "code": "TEXT_OVERFLOW",
                    "message": str(exc),
                },
            }
        except ValueError as exc:
            _clear_cached_svg_for_request(request.request_id)
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": {
                    "code": "INPUT_INVALID_FORMAT",
                    "message": str(exc),
                },
            }

        if not in_bounds:
            _clear_cached_svg_for_request(request.request_id)
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": {
                    "code": "SVG_OUT_OF_BOUNDS",
                    "message": "Nét vẽ vượt ngoài khổ giấy sau khi kết xuất.",
                },
            }

        svg_filename = f"output_{request.request_id}.svg"
        svg_path = os.path.join(SVG_OUTPUT_DIR, svg_filename)
        os.makedirs(SVG_OUTPUT_DIR, exist_ok=True)
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        _svg_metrics_cache[request.request_id] = metrics
        processing_time_ms = max(0.0, (time.perf_counter() - t_start) * 1000.0)

        return {
            "request_id": request.request_id,
            "status": "success",
            "result_image_base64": None,
            "meta": {
                "model_used": f"Bio-mimetic ({font_param} / {request.style})",
                "processing_time_ms": processing_time_ms,
                "seed": seed_param,
                "letter_type": letter_type_param,
            },
            "svg_ready": True,
            "svg_metrics": metrics,
            "error": None
        }

    # 3. Phân nhánh Art Mode (Text-to-Drawing & Image-to-Drawing)
    elif request.input_type in ("text", "image"):
        # 1. Validation & resolve style cho Art Mode
        effective_style, style_err = resolve_art_style(request.style)
        if style_err:
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": style_err,
            }

        # 2. Validation target_paper_size_mm
        (paper_w, paper_h), paper_err = validate_target_paper_size(request.options)
        if paper_err:
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": paper_err,
            }

        # 3. Validation skew_angle
        skew_angle, skew_err = validate_skew_angle(request.options)
        if skew_err:
            return {
                "request_id": request.request_id,
                "status": "error",
                "result_image_base64": None,
                "error": skew_err,
            }

        # TV1: Xử lý Text-to-drawing qua OpenAI API
        if request.input_type == "text":
            if not request.prompt or not str(request.prompt).strip():
                return {
                    "request_id": request.request_id,
                    "status": "error",
                    "result_image_base64": None,
                    "error": {
                        "code": "INPUT_INVALID_FORMAT",
                        "message": "Prompt không được để trống khi input_type='text'."
                    }
                }

            # Validation thành công -> Dọn dẹp cache & SVG cũ cho request_id này trước khi gọi pipeline AI
            _clear_cached_svg_for_request(request.request_id)

            # Chạy đồng bộ trong thread pool để không block event loop của FastAPI
            resp: APIResponse = await asyncio.to_thread(
                call_openai_image_api,
                prompt=request.prompt,
                request_id=request.request_id,
                style=effective_style,
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
                        style=effective_style,
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

                    svg_result = await asyncio.to_thread(
                        svg_process,
                        request_id=resp.request_id,
                        image_base64=raw_b64,
                        target_paper_size_mm=(paper_w, paper_h),
                        output_dir=SVG_OUTPUT_DIR,
                        style=effective_style,
                        skew_angle_deg=skew_angle,
                    )
                    print(f"[pipeline] SVG conversion: {svg_result.get('status')} "
                          f"(metrics={svg_result.get('svg_metrics')})")

                    if svg_result.get("status") == "error":
                        _clear_cached_svg_for_request(resp.request_id)
                        _clear_cached_svg_for_request(request.request_id)
                        err = svg_result.get("error") or {}
                        return {
                            "request_id": resp.request_id,
                            "status": "error",
                            "result_image_base64": None,
                            "svg_ready": False,
                            "svg_metrics": None,
                            "error": {
                                "code": err.get("code", "VECTORIZE_FAILED"),
                                "message": err.get("message", "Chuyển đổi vector hoá SVG thất bại.")
                            }
                        }

                    svg_metrics_data = svg_result.get("svg_metrics")
                    # Lưu vào cache server-side để /api/log/experiment có thể tự lấy
                    _svg_metrics_cache[resp.request_id] = svg_metrics_data
                except Exception as e:
                    print(f"[warn] SVG conversion failed: {e}")
                    _clear_cached_svg_for_request(resp.request_id)
                    _clear_cached_svg_for_request(request.request_id)
                    return {
                        "request_id": resp.request_id,
                        "status": "error",
                        "result_image_base64": None,
                        "svg_ready": False,
                        "svg_metrics": None,
                        "error": {
                            "code": "VECTORIZE_FAILED",
                            "message": str(e)
                        }
                    }

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
                _clear_cached_svg_for_request(resp.request_id)
                _clear_cached_svg_for_request(request.request_id)
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
            if not request.image_base64 or not str(request.image_base64).strip():
                return {
                    "request_id": request.request_id,
                    "status": "error",
                    "result_image_base64": None,
                    "error": {
                        "code": "INPUT_INVALID_FORMAT",
                        "message": "image_base64 không được để trống khi input_type='image'."
                    }
                }

            # Validation thành công -> Dọn dẹp cache & SVG cũ cho request_id này trước khi gọi pipeline vector hóa
            _clear_cached_svg_for_request(request.request_id)

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
                # Chạy hàm biến đổi ảnh thành nét vẽ SVG
                svg_result = await asyncio.to_thread(
                    svg_process,
                    request_id=request.request_id,
                    image_base64=raw_b64,
                    target_paper_size_mm=(paper_w, paper_h),
                    output_dir=SVG_OUTPUT_DIR,
                    style=effective_style,
                    skew_angle_deg=skew_angle,
                )

                print(f"[pipeline] Image upload SVG conversion: {svg_result.get('status')} "
                      f"(metrics={svg_result.get('svg_metrics')})")

                if svg_result.get("status") == "error":
                    _clear_cached_svg_for_request(request.request_id)
                    err = svg_result.get("error") or {}
                    return {
                        "request_id": request.request_id,
                        "status": "error",
                        "result_image_base64": None,
                        "svg_ready": False,
                        "svg_metrics": None,
                        "error": {
                            "code": err.get("code", "VECTORIZE_FAILED"),
                            "message": err.get("message", "Chuyển đổi vector hoá SVG thất bại.")
                        }
                    }

                svg_metrics_data = svg_result.get("svg_metrics")
                _svg_metrics_cache[request.request_id] = svg_metrics_data
            except Exception as e:
                print(f"[warn] SVG conversion failed for uploaded image: {e}")
                _clear_cached_svg_for_request(request.request_id)
                return {
                    "request_id": request.request_id,
                    "status": "error",
                    "result_image_base64": None,
                    "svg_ready": False,
                    "svg_metrics": None,
                    "error": {
                        "code": "VECTORIZE_FAILED",
                        "message": str(e)
                    }
                }

            return {
                "request_id": request.request_id,
                "status": "success",
                "result_image_base64": img_data,
                "meta": {
                    "model_used": "uploaded-image",
                    "processing_time_ms": 0
                },
                "svg_ready": True,
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
    base_dir = os.path.abspath(SVG_OUTPUT_DIR)
    target_file = os.path.abspath(os.path.join(base_dir, f"output_{request_id}.svg"))
    if (
        os.path.commonpath([base_dir, target_file]) == base_dir
        and os.path.dirname(target_file) == base_dir
        and target_file != base_dir
        and os.path.isfile(target_file)
    ):
        return FileResponse(target_file, media_type="image/svg+xml")
        
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
        _clear_cached_svg_for_request(request_id)
        return {"status": "success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ---------- Mục 5d API Spec: GET /api/print/svg/{request_id} ----------
@app.get("/api/print/svg/{request_id}")
async def get_svg_content(request_id: str):
    """Trả nội dung SVG thật để giao diện render hiệu ứng 'vẽ dần theo %'."""
    base_dir = os.path.abspath(SVG_OUTPUT_DIR)
    target_file = os.path.abspath(os.path.join(base_dir, f"output_{request_id}.svg"))
    if not (
        os.path.commonpath([base_dir, target_file]) == base_dir
        and os.path.dirname(target_file) == base_dir
        and target_file != base_dir
        and os.path.isfile(target_file)
    ):
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
        with open(target_file, "r", encoding="utf-8") as f:
            svg_content = f.read()

        metrics = _svg_metrics_cache.get(request_id)
        if not metrics:
            from database import parse_svg_info
            metrics = parse_svg_info(target_file)
            if metrics:
                _svg_metrics_cache[request_id] = metrics

        return {
            "request_id": request_id,
            "status": "success",
            "svg_content": svg_content,
            "svg_metrics": metrics,
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

>>>>>>> develop

@app.post("/api/print/resume")
async def resume_print(body: PauseCancelRequest):
    job = jobs.get(body.request_id)

    if not job or job["status"] != "paused":
        raise HTTPException(status_code=409, detail="Chưa pause nên không thể resume")
    
    job.update({"started_at": time.monotonic(), "status": "printing", "task": asyncio.create_task(_run_job(body.request_id))})
    return {"request_id": body.request_id, "status": "printing"}

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

    if not job: raise HTTPException(status_code=404, detail="ID không tồn tại")
    

    if not job: return custom_error("JOB_NOT_FOUND", "Không tìm thấy ID", 404)


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


@app.get("/api/camera/inspect-paper")
async def api_inspect_paper(device: int = 0):
    """Kiem tra tinh trang giay va goc lech qua camera thi giac (Closed-Loop Vision)."""
    from camera_inspector import inspect_paper
    result = inspect_paper(camera_index=device)
    return result


@app.get("/")
async def root():
    return HTMLResponse("<h1>Trạm OmniDraw đang chạy ở cổng 8000!</h1>")


if __name__ == "__main__":
    try:
        import uvicorn
        print("\n🚀 [OmniDraw] Khởi động máy chủ Backend tại http://localhost:8000 ...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, app_dir=_backend_dir)
    except ImportError:
        print("\n❌ Lỗi: Chưa tìm thấy thư viện uvicorn. Hãy chạy trong môi trường ảo:")
        print(f"   source {os.path.join(_backend_dir, 'venv', 'bin', 'activate')}")
        print("   uvicorn main:app --reload --port 8000")
>>>>>>> develop
