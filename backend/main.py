import asyncio
import csv
import os
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 1. Khởi tạo ứng dụng
app = FastAPI(title="OmniDraw API Gateway")

# 2. Cấu hình CORS (Cho phép React ở cổng 5173 gọi sang Python ở cổng 8000)
# SỬA: allow_origins=["*"] kết hợp allow_credentials=True là tổ hợp không hợp lệ
# theo chuẩn CORS — trình duyệt có thể từ chối request. Vì hiện tại frontend
# không dùng cookie/session (chỉ gửi JSON thuần), đổi allow_credentials=False
# và liệt kê rõ origin của Vite dev server thay vì "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Định nghĩa cấu trúc khung xương dữ liệu (Pydantic Models)
# Cấu trúc này phải khớp 100% với hàm log ở Frontend


class SvgMetrics(BaseModel):
    """Khớp svg_metrics.* ở mục 6 API Spec — để trống (None) khi module
    Thuật toán thật chưa xong, không bắt buộc điền ngay."""

    total_path_length_mm: Optional[float] = None
    pen_lift_distance_mm: Optional[float] = None
    pen_lift_count: Optional[int] = None
    optimize_time_ms: Optional[float] = None


class LogPayload(BaseModel):
    # SỬA: bổ sung đủ cột theo bảng ở mục 6 API Spec — bản cũ chỉ có 7/13 cột,
    # thiếu hẳn các chỉ số chính dùng cho RQ1/RQ2 (svg_metrics, ai_processing_time_ms)
    # và các trường gắn thí nghiệm (dataset_item_id, method_tag, input_type).
    # Tất cả các trường mới đều Optional để frontend hiện tại (chưa có module AI/thuật
    # toán thật) vẫn gọi được bình thường mà không cần sửa gì — điền dần khi có dữ liệu thật.
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


# 4. Các Endpoints (Đường ống)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Trạm trung chuyển OmniDraw đã sẵn sàng!"}


# Thứ tự cột CSV cố định — dùng chung cho cả header và mỗi dòng ghi,
# để không bao giờ bị lệch cột nếu sau này thêm field mới (thêm ở CSV_COLUMNS
# là đủ, không phải sửa 2 chỗ).
CSV_COLUMNS = [
    "request_id",
    "timestamp",
    "dataset_item_id",
    "method_tag",
    "input_type",
    "style",
    "model_used",
    "ai_processing_time_ms",
    "svg_metrics.total_path_length_mm",
    "svg_metrics.pen_lift_distance_mm",
    "svg_metrics.pen_lift_count",
    "svg_metrics.optimize_time_ms",
    "actual_draw_time_sec",
    "final_status",
    "error_code",
]


# Endpoint: Nhận và ghi log file CSV
@app.post("/api/log/experiment")
def log_experiment(payload: LogPayload):
    # Tạo thư mục 'logs' nếu chưa có
    os.makedirs("logs", exist_ok=True)
    file_path = "logs/experiment_log.csv"

    # Kiểm tra xem file đã tồn tại chưa để viết tiêu đề cột
    file_exists = os.path.isfile(file_path)

    metrics = payload.svg_metrics or SvgMetrics()

    # Mở file CSV và ghi thêm (append) vào dòng cuối cùng
    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Nếu file mới tinh, ghi hàng tiêu đề (Headers)
        if not file_exists:
            writer.writerow(CSV_COLUMNS)

        # Ghi dữ liệu thực tế từ React gửi lên — đúng thứ tự CSV_COLUMNS ở trên
        writer.writerow([
            payload.request_id,
            payload.timestamp,
            payload.dataset_item_id,
            payload.method_tag,
            payload.input_type,
            payload.style,
            payload.model_used,
            payload.ai_processing_time_ms,
            metrics.total_path_length_mm,
            metrics.pen_lift_distance_mm,
            metrics.pen_lift_count,
            metrics.optimize_time_ms,
            payload.actual_draw_time_sec,
            payload.final_status,
            payload.error_code,
        ])

    print(f"✅ Đã ghi log thành công vào CSV cho request: {payload.request_id}")
    return {"success": True, "message": "Đã lưu log thành công."}


@app.post("/api/ai/generate")
async def generate_ai_image(request: GenerateRequest):
    print(
        f"🎨 Nhận yêu cầu vẽ tranh ({request.request_id}) - "
        f"Kiểu: {request.input_type} - Phong cách: {request.style}"
    )

    # SỬA: time.sleep(3) là hàm chặn (blocking) — gọi trong hàm async sẽ đứng
    # luôn toàn bộ server suốt 3 giây đó, không request nào khác (kể cả health
    # check) xử lý được. Dùng asyncio.sleep để chỉ "nhường" thời gian này cho
    # các request khác, không chặn cả server. Quan trọng hơn khi sau này chạy
    # hàng loạt 30 ảnh + 15 prompt cho thí nghiệm khoa học.
    await asyncio.sleep(3)

    # Ảnh kết quả (sau này thay bằng ảnh do AI của bạn vẽ)
    # TODO: đây vẫn là ảnh mẫu gọi ra Internet thật (Unsplash) — mất mạng lúc
    # demo sẽ không hiện được ảnh. Thay bằng ảnh tĩnh local (vd: đặt 1 file
    # trong thư mục static/ và trả đường dẫn nội bộ) khi có thời gian.
    dummy_result_image = (
        "https://images.unsplash.com/photo-1547826039-bfc35e0f1ea8"
        "?auto=format&fit=crop&w=800&q=80"
    )

    print("✅ Đã xử lý xong ảnh AI!")

    # Trả về đúng cấu trúc mà hàm generateArt bên Frontend đang chờ
    return {
        "request_id": request.request_id,
        "result_image_base64": dummy_result_image,
        "meta": {"model_used": "ai-core-v1-python", "processing_time_ms": 3000},
    }


# --- CÁC CỔNG API ĐIỀU KHIỂN MÁY VẼ ---


class PrintRequest(BaseModel):
    request_id: str
    paper_size: Optional[str] = "a4"


class PrintAction(BaseModel):
    request_id: str


@app.post("/api/print/start")
async def start_print(request: PrintRequest):
    print(f"🚀 Bắt đầu ra lệnh cho máy vẽ... (ID: {request.request_id})")
    # TODO: Sau này gắn code kết nối với phần cứng máy vẽ thật vào đây
    return {"request_id": request.request_id, "status": "printing"}


@app.post("/api/print/pause")
async def pause_print(request: PrintAction):
    print(f"⏸️ Tạm dừng máy vẽ (ID: {request.request_id})")
    return {"request_id": request.request_id, "status": "paused"}


@app.post("/api/print/cancel")
async def cancel_print(request: PrintAction):
    print(f"🛑 Đã huỷ lệnh máy vẽ (ID: {request.request_id})")
    return {"request_id": request.request_id, "status": "cancelled"}


# Dùng một biến tạm để giả lập thời gian máy đang vẽ (thay thế cho thanh tiến trình Mock ở React)
mock_print_jobs: Dict[str, float] = {}


@app.get("/api/print/status/{request_id}")
async def get_print_status(request_id: str):
    # Nếu là lần đầu hỏi trạng thái, ghi nhận thời gian bắt đầu
    if request_id not in mock_print_jobs:
        mock_print_jobs[request_id] = time.time()

    elapsed = time.time() - mock_print_jobs[request_id]
    total_time = 15  # Giả lập máy cần 15 giây để vẽ xong

    # SỬA: bổ sung "request_id" vào response — mục 5 API Spec yêu cầu trường
    # này để frontend/log có thể đối chiếu, bản cũ thiếu (dù frontend hiện
    # chưa dùng đến nên chưa gây lỗi, nhưng lệch chuẩn thì nên sửa sớm).

    # Nếu đã qua 15 giây -> Báo xong!
    if elapsed >= total_time:
        return {
            "request_id": request_id,
            "status": "done",
            "progress_percent": 100,
            "estimated_time_remaining_sec": 0,
            "actual_draw_time_sec": total_time,
            "error": None,
        }

    # Nếu chưa xong -> Tính phần trăm tiến độ
    percent = int((elapsed / total_time) * 100)
    return {
        "request_id": request_id,
        "status": "printing",
        "progress_percent": percent,
        "estimated_time_remaining_sec": int(total_time - elapsed),
        "actual_draw_time_sec": None,
        "error": None,
    }


# --- LỊCH SỬ TRANH ĐÃ VẼ (mục 5c API Spec) ---
# MỚI: endpoint này chưa tồn tại ở bản cũ, khiến màn Thư viện bên frontend
# luôn nhận lỗi 404. Tạm trả dữ liệu mẫu cố định — thay bằng đọc từ
# database/log CSV thật khi nhóm chốt xong 3 câu hỏi còn mở ở mục 5c
# (nguồn "title", quan hệ với log CSV, định dạng "time_ago").


@app.get("/api/history")
async def get_history():
    items = [
        {
            "id": "1",
            "title": "Mèo ngủ",
            "style": "sketch",
            "time_ago": "2 ngày trước",
            "minutes": 12,
            "thumbnail_url": None,
        },
        {
            "id": "2",
            "title": "Phong cảnh núi",
            "style": "line_art",
            "time_ago": "5 ngày trước",
            "minutes": 10,
            "thumbnail_url": None,
        },
    ]
    return {"items": items}
