"""
OmniDraw - Mock Printer Server (Hardware module - TV3)
=======================================================
Giả lập máy vẽ AxiDraw khi chưa có máy thật, đúng chuẩn API Spec v1.2
(mục 4, 5, 5b, 8).

Cách chạy:
    pip install fastapi uvicorn
    uvicorn mock_printer:app --reload --port 8003

Sau đó mở trình duyệt: http://127.0.0.1:8003/docs
để test trực tiếp từng endpoint (Swagger UI tự sinh).

Khi có máy AxiDraw thật:
    - Chỉ cần thay nội dung 3 hàm _start_job / _pause_job / _cancel_job
      để gọi pyaxidraw thật, thay vì asyncio.sleep giả lập.
    - Toàn bộ phần định dạng JSON/route giữ nguyên, không đổi hợp đồng
      với Giao diện (TV4).
"""

import asyncio
import math
import os
import re
import time
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

# Tốc độ vẽ giả định của bút (mm/giây) khi bút đang chạm giấy — dùng để ước
# lượng thời gian vẽ từ độ dài đường thật, thay vì bịa số ngẫu nhiên.
# Con số 40mm/s là ước lượng hợp lý cho AxiDraw ở tốc độ vẽ mặc định
# (pen down speed ~25% max) — CẦN chỉnh lại khi có máy thật đo thực tế.
ASSUMED_PEN_SPEED_MM_PER_SEC = 40.0

# Thư mục chứa file SVG do module Thuật toán (TV2) xuất ra, đặt tên
# output_{request_id}.svg theo đúng quy ước mục 4 API Spec.
SVG_OUTPUT_DIR = os.environ.get("OMNIDRAW_SVG_DIR", "./svg_output")


# ---------------------------------------------------------------------------
# Trang tester HTML — bảng điều khiển trực quan cho người không quen gõ JSON
# tay trên Swagger. Chỉ phục vụ demo/test, không thuộc API Spec chính thức.
# ---------------------------------------------------------------------------

TESTER_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>OmniDraw Mock Printer — Bảng test</title>
<style>
  body { font-family: -apple-system, "Segoe UI", Arial, sans-serif; max-width: 720px;
         margin: 40px auto; padding: 0 20px; color: #1a1a1a; background: #fafafa; }
  h1 { font-size: 22px; }
  p.sub { color: #666; margin-top: -8px; }
  .card { background: #fff; border: 1px solid #e0e0e0; border-radius: 10px;
          padding: 20px; margin-bottom: 18px; }
  label { font-weight: 600; font-size: 14px; display: block; margin-bottom: 6px; }
  input[type=text] { width: 100%; padding: 9px 10px; font-size: 14px;
          border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
  .btn-row { display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; }
  button { padding: 9px 16px; font-size: 14px; border: none; border-radius: 6px;
           cursor: pointer; color: #fff; font-weight: 600; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-start   { background: #16a34a; }
  .btn-pause   { background: #ca8a04; }
  .btn-resume  { background: #2563eb; }
  .btn-cancel  { background: #dc2626; }
  .btn-refresh { background: #4b5563; }
  .status-box { margin-top: 16px; padding: 14px; border-radius: 8px; background: #f3f4f6;
                font-family: "Cascadia Code", Consolas, monospace; font-size: 13px;
                white-space: pre-wrap; }
  .bar-bg { width: 100%; height: 18px; background: #e5e7eb; border-radius: 9px;
            overflow: hidden; margin-top: 10px; }
  .bar-fill { height: 100%; background: #16a34a; width: 0%; transition: width 0.3s; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 12px;
           font-size: 12px; font-weight: 700; color: #fff; }
  .b-queued    { background: #9ca3af; }
  .b-printing  { background: #2563eb; }
  .b-paused    { background: #ca8a04; }
  .b-done      { background: #16a34a; }
  .b-error     { background: #dc2626; }
  .b-cancelled { background: #6b7280; }
  a.doclink { font-size: 13px; color: #2563eb; }
  .step { font-size: 13px; color: #444; margin: 4px 0 0 0; }
</style>
</head>
<body>
  <h1>🖨️ OmniDraw Mock Printer — Bảng test</h1>
  <p class="sub">Máy vẽ giả lập cho module Phần cứng (TV3). Bấm nút theo thứ tự để thử luồng vẽ.
    Xem chi tiết kỹ thuật từng API tại <a class="doclink" href="/docs">/docs</a>.</p>

  <div class="card">
    <label for="rid">1. request_id (tự đặt tên bất kỳ, ví dụ demo1)</label>
    <input type="text" id="rid" value="demo1">
    <p class="step">👉 Gõ 1 mã tuỳ ý, dùng lại đúng mã này cho mọi nút bên dưới.</p>

    <div class="btn-row">
      <button class="btn-start" onclick="callApi('start')">2. Bắt đầu vẽ</button>
      <button class="btn-pause" onclick="callApi('pause')">3. Tạm dừng</button>
      <button class="btn-resume" onclick="callApi('resume')">4. Tiếp tục</button>
      <button class="btn-cancel" onclick="callApi('cancel')">5. Huỷ vẽ</button>
      <button class="btn-refresh" onclick="refreshStatus()">🔄 Xem trạng thái</button>
    </div>

    <div class="bar-bg"><div class="bar-fill" id="bar"></div></div>
    <div id="badge"></div>
    <div class="status-box" id="statusBox">Chưa có dữ liệu — bấm "Bắt đầu vẽ" trước.</div>
  </div>

  <div class="card">
    <b>Mẹo đọc kết quả:</b>
    <ul style="font-size:13px; line-height:1.6;">
      <li><b>progress_percent</b> — % đã vẽ xong</li>
      <li><b>status</b> — queued / printing / paused / done / error / cancelled</li>
      <li>Sau khi "Tạm dừng", bấm "Xem trạng thái" — % phải <b>giữ nguyên</b>, không mất tiến độ</li>
      <li>Trang này tự làm mới trạng thái mỗi 1 giây khi đang "printing"</li>
    </ul>
  </div>

<script>
let pollTimer = null;

function badgeClass(status) {
  return {
    queued: "b-queued", printing: "b-printing", paused: "b-paused",
    done: "b-done", error: "b-error", cancelled: "b-cancelled"
  }[status] || "b-queued";
}

function render(data) {
  document.getElementById("statusBox").textContent = JSON.stringify(data, null, 2);
  const pct = data.progress_percent ?? 0;
  document.getElementById("bar").style.width = pct + "%";
  const status = data.status || "?";
  document.getElementById("badge").innerHTML =
    '<span class="badge ' + badgeClass(status) + '">' + status + '</span>';

  clearInterval(pollTimer);
  if (status === "printing") {
    pollTimer = setInterval(refreshStatus, 1000);
  }
}

async function callApi(action) {
  const rid = document.getElementById("rid").value.trim();
  if (!rid) { alert("Nhập request_id trước đã"); return; }

  const urlMap = {
    start: "/api/print/start",
    pause: "/api/print/pause",
    resume: "/api/print/resume",
    cancel: "/api/print/cancel",
  };
  const body = action === "start"
    ? { request_id: rid, paper_size: "a4" }
    : { request_id: rid };

  try {
    const res = await fetch(urlMap[action], {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) {
      document.getElementById("statusBox").textContent =
        "Lỗi (" + res.status + "):\\n" + JSON.stringify(data, null, 2);
      return;
    }
    await refreshStatus();
  } catch (e) {
    document.getElementById("statusBox").textContent = "Không gọi được server: " + e;
  }
}

async function refreshStatus() {
  const rid = document.getElementById("rid").value.trim();
  if (!rid) return;
  try {
    const res = await fetch("/api/print/status/" + encodeURIComponent(rid));
    const data = await res.json();
    if (!res.ok) {
      document.getElementById("statusBox").textContent =
        "Lỗi (" + res.status + "):\\n" + JSON.stringify(data, null, 2);
      clearInterval(pollTimer);
      return;
    }
    render(data);
  } catch (e) {
    document.getElementById("statusBox").textContent = "Không gọi được server: " + e;
  }
}
</script>
</body>
</html>
"""

app = FastAPI(title="OmniDraw Mock Printer (Hardware - TV3)")

# ---------------------------------------------------------------------------
# "Cơ sở dữ liệu" tạm trong bộ nhớ — lưu trạng thái từng request_id
# ---------------------------------------------------------------------------
# jobs[request_id] = {
#     "status": "queued" | "printing" | "paused" | "done" | "error" | "cancelled",
#     "progress_percent": int,
#     "estimated_time_remaining_sec": int,
#     "actual_draw_time_sec": Optional[int],
#     "error": Optional[dict],
#     "total_draw_time_sec": int,   # tổng thời gian giả lập vẽ xong 100%
#     "started_at": Optional[float],
#     "elapsed_before_pause": float,  # số giây đã vẽ trước khi bị pause (cộng dồn)
#     "task": Optional[asyncio.Task],
# }
jobs: dict[str, dict] = {}

# Mã lỗi hardware hợp lệ theo mục 8 của API Spec
VALID_HARDWARE_ERRORS = {
    "HARDWARE_NOT_CONNECTED": "Máy không kết nối được",
    "HARDWARE_PAPER_JAM": "Phát hiện kẹt giấy",
    "HARDWARE_OUT_OF_INK": "Hết mực/bút không xuống mực",
}

# Giả lập: máy có đang "kết nối" hay không (đổi biến này để test lỗi)
DEVICE_CONNECTED = True


def _log(request_id: str, message: str):
    """Log hoạt động theo đúng format mục 7: [request_id] [module] [timestamp] message"""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"[{request_id}] [hardware] [{ts}] {message}")


# ---------------------------------------------------------------------------
# Request/Response models (Pydantic) — khớp mục 5b của API Spec
# ---------------------------------------------------------------------------

class StartRequest(BaseModel):
    request_id: str
    paper_size: str = "a4"


class PauseCancelRequest(BaseModel):
    request_id: str


def error_response(code: str, message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={
            "request_id": None,
            "status": "error",
            "error": {"code": code, "message": message},
        },
    )


def _parse_path_length_mm(d_attr: str) -> float:
    """
    Tính gần đúng tổng độ dài của 1 path SVG (thuộc tính "d").
    CHỈ hỗ trợ lệnh M/m (move) và L/l (line) — đúng với quy tắc mục 4 API
    Spec (không dùng curve phức tạp, chỉ path/line/polyline đơn giản).
    Nếu path có lệnh khác (C, A, Q...), các đoạn đó bị bỏ qua trong ước
    lượng — đủ dùng cho mock, KHÔNG dùng số này để tính svg_metrics chính
    thức (đó là trách nhiệm của module Thuật toán - TV2, xem mục 6).
    """
    tokens = re.findall(r"[MLmlZz]|-?\d*\.?\d+", d_attr)
    total = 0.0
    cur_x = cur_y = start_x = start_y = 0.0
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
            x = float(tok)
            y = float(tokens[i + 1])
        except (ValueError, IndexError):
            break
        i += 2

        if cmd in ("M", "L"):
            nx, ny = x, y
        else:  # relative m/l
            nx, ny = cur_x + x, cur_y + y

        if cmd in ("M", "m") and cur_x == 0 and cur_y == 0 and total == 0:
            start_x, start_y = nx, ny
        else:
            total += math.hypot(nx - cur_x, ny - cur_y)

        cur_x, cur_y = nx, ny
        if cmd in ("M", "m"):
            start_x, start_y = nx, ny
            cmd = "L" if cmd == "M" else "l"  # sau move đầu, coi như line

    return total


def svg_total_path_length_mm(svg_text: str) -> float:
    """Cộng độ dài toàn bộ các <path d="..."> trong 1 file SVG (đơn vị mm,
    theo đúng quy ước viewBox=mm của mục 4 API Spec)."""
    paths = re.findall(r'<path[^>]*\bd="([^"]+)"', svg_text)
    return sum(_parse_path_length_mm(d) for d in paths)


def svg_estimate_draw_time(request_id: str) -> int:
    """
    Ước lượng thời gian vẽ (giây) cho 1 request_id.

    Ưu tiên đọc file SVG thật tại SVG_OUTPUT_DIR/output_{request_id}.svg
    (do TV2 - Thuật toán xuất ra theo mục 4) và tính theo tổng độ dài nét /
    tốc độ bút giả định.

    Nếu chưa có file thật (ví dụ đang test riêng module hardware, chưa nối
    với TV2), rơi về số giả ổn định theo request_id như cũ, để không bị vỡ
    luồng test hiện có.
    """
    svg_path = os.path.join(SVG_OUTPUT_DIR, f"output_{request_id}.svg")
    if os.path.isfile(svg_path):
        try:
            with open(svg_path, "r", encoding="utf-8") as f:
                svg_text = f.read()
            length_mm = svg_total_path_length_mm(svg_text)
            if length_mm > 0:
                seconds = length_mm / ASSUMED_PEN_SPEED_MM_PER_SEC
                return max(2, int(round(seconds)))
        except Exception as exc:  # không để lỗi đọc file làm crash cả request
            print(f"[warn] khong doc duoc {svg_path}: {exc}")

    # Fallback: chưa có file SVG thật -> số giả ổn định để vẫn test được
    seed = sum(ord(c) for c in request_id) % 20
    return 15 + seed  # 15-34 giây


# ---------------------------------------------------------------------------
# Vòng lặp giả lập tiến độ vẽ (chạy nền bằng asyncio.Task)
# ---------------------------------------------------------------------------

async def _run_job(request_id: str):
    job = jobs[request_id]
    job["status"] = "printing"
    job["started_at"] = time.monotonic()
    _log(request_id, "bat dau ve (mo phong)")

    total = job["total_draw_time_sec"]

    while True:
        await asyncio.sleep(0.5)

        job_now = jobs.get(request_id)
        if job_now is None:
            return  # job bị xoá

        if job_now["status"] in ("paused", "cancelled", "error"):
            # Vòng lặp tự dừng, chờ resume/cancel xử lý riêng
            return

        elapsed = job_now["elapsed_before_pause"] + (
            time.monotonic() - job_now["started_at"]
        )
        percent = min(99, int((elapsed / total) * 100))
        job_now["progress_percent"] = percent
        job_now["estimated_time_remaining_sec"] = max(0, int(total - elapsed))

        if elapsed >= total:
            job_now["status"] = "done"
            job_now["progress_percent"] = 100
            job_now["estimated_time_remaining_sec"] = 0
            job_now["actual_draw_time_sec"] = int(elapsed)
            _log(request_id, f"ve xong, actual_draw_time_sec={int(elapsed)}")
            return


# ---------------------------------------------------------------------------
# Mục 5b: POST /api/print/start
# ---------------------------------------------------------------------------

@app.post("/api/print/start")
async def start_print(body: StartRequest):
    request_id = body.request_id

    if not DEVICE_CONNECTED:
        _log(request_id, "loi: may khong ket noi")
        return error_response(
            "HARDWARE_NOT_CONNECTED",
            "Máy không kết nối được",
            status_code=503,
        )

    if request_id in jobs and jobs[request_id]["status"] in ("printing", "paused"):
        raise HTTPException(
            status_code=409, detail="request_id nay dang duoc ve, khong the start lai"
        )

    total = svg_estimate_draw_time(request_id)
    jobs[request_id] = {
        "status": "queued",
        "progress_percent": 0,
        "estimated_time_remaining_sec": total,
        "actual_draw_time_sec": None,
        "error": None,
        "total_draw_time_sec": total,
        "started_at": None,
        "elapsed_before_pause": 0.0,
        "task": None,
    }

    task = asyncio.create_task(_run_job(request_id))
    jobs[request_id]["task"] = task

    _log(request_id, f"nhan yeu cau ve, paper_size={body.paper_size}, uoc tinh {total}s")
    return {"request_id": request_id, "status": "printing"}


# ---------------------------------------------------------------------------
# Mục 5b: POST /api/print/pause
# ---------------------------------------------------------------------------

@app.post("/api/print/pause")
async def pause_print(body: PauseCancelRequest):
    request_id = body.request_id
    job = jobs.get(request_id)

    if job is None:
        raise HTTPException(status_code=404, detail="request_id khong ton tai")

    if job["status"] != "printing":
        raise HTTPException(
            status_code=409,
            detail=f"khong the pause khi status hien tai la '{job['status']}'",
        )

    # Cộng dồn thời gian đã vẽ trước khi dừng (giữ đúng vị trí, theo AxiDraw
    # hỗ trợ offset vị trí pause chính thức)
    elapsed_now = job["elapsed_before_pause"] + (time.monotonic() - job["started_at"])
    job["elapsed_before_pause"] = elapsed_now
    job["status"] = "paused"
    _log(request_id, f"tam dung, da ve {elapsed_now:.1f}s")

    return {"request_id": request_id, "status": "paused"}


@app.post("/api/print/resume")
async def resume_print(body: PauseCancelRequest):
    """Không có trong bảng route chính thức của mục 5b nhưng cần thiết để
    demo được luồng pause -> resume trong mock. Khi chốt với nhóm, có thể
    dùng lại chính /api/print/start để resume, hoặc bổ sung route này vào
    API Spec — cần TV4 xác nhận."""
    request_id = body.request_id
    job = jobs.get(request_id)

    if job is None:
        raise HTTPException(status_code=404, detail="request_id khong ton tai")
    if job["status"] != "paused":
        raise HTTPException(status_code=409, detail="job khong o trang thai paused")

    job["started_at"] = time.monotonic()
    job["status"] = "printing"
    task = asyncio.create_task(_run_job(request_id))
    job["task"] = task
    _log(request_id, "tiep tuc ve tu vi tri da dung")

    return {"request_id": request_id, "status": "printing"}


# ---------------------------------------------------------------------------
# Mục 5b: POST /api/print/cancel
# ---------------------------------------------------------------------------

@app.post("/api/print/cancel")
async def cancel_print(body: PauseCancelRequest):
    request_id = body.request_id
    job = jobs.get(request_id)

    if job is None:
        raise HTTPException(status_code=404, detail="request_id khong ton tai")

    if job["status"] not in ("queued", "printing", "paused"):
        raise HTTPException(
            status_code=409,
            detail=f"khong the cancel khi status hien tai la '{job['status']}'",
        )

    task: Optional[asyncio.Task] = job.get("task")
    if task and not task.done():
        task.cancel()

    job["status"] = "cancelled"
    _log(request_id, "huy ve theo yeu cau")

    return {"request_id": request_id, "status": "cancelled"}


# ---------------------------------------------------------------------------
# Mục 5: GET /api/print/status/{request_id}
# ---------------------------------------------------------------------------

@app.get("/api/print/status/{request_id}")
async def get_status(request_id: str, simulate_error: Optional[str] = None):
    """
    Query param `simulate_error` chỉ dùng để TEST, không có trong API Spec
    chính thức. Ví dụ:
        GET /api/print/status/abc123?simulate_error=HARDWARE_PAPER_JAM
    sẽ ép job này chuyển sang lỗi ngay lập tức, để TV4 test luồng xử lý lỗi
    mà không cần gây lỗi phần cứng thật.
    """
    job = jobs.get(request_id)
    if job is None:
        raise HTTPException(status_code=404, detail="request_id khong ton tai")

    if simulate_error:
        if simulate_error not in VALID_HARDWARE_ERRORS:
            raise HTTPException(
                status_code=400,
                detail=f"simulate_error phai la mot trong {list(VALID_HARDWARE_ERRORS)}",
            )
        job["status"] = "error"
        job["error"] = {
            "code": simulate_error,
            "message": VALID_HARDWARE_ERRORS[simulate_error],
        }
        _log(request_id, f"gia lap loi: {simulate_error}")

    response = {
        "request_id": request_id,
        "status": job["status"],
        "progress_percent": job["progress_percent"],
        "estimated_time_remaining_sec": job["estimated_time_remaining_sec"],
        "error": job["error"],
    }

    if job["status"] == "done":
        response["actual_draw_time_sec"] = job["actual_draw_time_sec"]

    return response


# ---------------------------------------------------------------------------
# Endpoint phụ trợ để test nhanh (không thuộc API Spec)
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def root():
    """Trang chủ: bảng điều khiển demo trực quan, bấm nút thay vì gõ JSON tay."""
    return TESTER_HTML


@app.get("/api/_debug/jobs")
async def debug_jobs():
    """Chỉ để bạn tự xem toàn bộ jobs đang có trong bộ nhớ khi test, không phải API chính thức."""
    return {
        rid: {k: v for k, v in job.items() if k != "task"}
        for rid, job in jobs.items()
    }