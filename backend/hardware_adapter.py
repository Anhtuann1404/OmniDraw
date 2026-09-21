"""
OmniDraw - Module Quản lý & Điều khiển Thiết bị Phần cứng (Hardware Abstraction Layer)
====================================================================================
Tác giả: TV3 (Hardware, Calibration & Physical Validation Lead)
Phiên bản: v1.4 (21/09/2026)
Mục tiêu:
  1. Chuẩn hóa interface chung giữa simulator (mô phỏng) và máy vẽ thật (AxiDraw).
  2. Xử lý an toàn các lệnh start, pause, resume, cancel theo API Spec v1.4.
  3. Phân định rạch ròi giữa thời gian mô phỏng (simulation), fake driver (CI test)
     và thời gian đo đạc thật (actual_draw_time_sec) trên máy vật lý:
     - Chế độ physical chỉ dùng driver thật; thiếu pyaxidraw thì báo lỗi không kết nối,
       tuyệt đối KHÔNG tự ý tráo đổi ngầm sang fake driver.
  4. Xác thực cú pháp XML/SVG nghiêm ngặt bằng xml.etree.ElementTree (chặn thẻ sai cú pháp).
  5. Tính toán chính xác độ dài đường dẫn SVG với đầy đủ phân cấp nhóm lồng nhau (<g transform="scale(...)">),
     Bézier (cubic/quadratic), Elliptic Arc (A/a), và quãng đường nhấc bút (pen-up) thực tế.
  6. Hiệu chuẩn: Quy đổi offset an toàn 5mm sang đơn vị viewBox tương ứng trước khi chèn vào SVG.
  7. Cung cấp CLI smoke test tự động: `python backend/hardware_adapter.py --smoke-test`.

Quy tắc phân định nguồn dữ liệu (NCKH Research Data Integrity):
  - is_simulated=True, actual_hardware_measured=False: Khi chạy trên Simulator hoặc Fake Driver.
  - is_simulated=False, actual_hardware_measured=True: DUY NHẤT khi chạy trên AxiDraw phần cứng thật.
  - source_tag: 'simulator' | 'axidraw_fake_driver' | 'axidraw_real'.
"""

from abc import ABC, abstractmethod
import argparse
import asyncio
import csv
import datetime
import math
import os
import re
import sys
import threading
import time
from typing import Dict, Any, Optional, List, Tuple
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# Hằng số mặc định
# ---------------------------------------------------------------------------
ASSUMED_PEN_SPEED_MM_PER_SEC: float = 40.0     # Art Mode mặc định (mm/s)
ASSUMED_PEN_UP_SPEED_MM_PER_SEC: float = 75.0    # Tốc độ nhấc bút rapid travel (mm/s)
ASSUMED_PEN_DOWN_DELAY_MS: float = 120.0         # Độ trễ hạ bút (ms)
ASSUMED_PEN_UP_DELAY_MS: float = 100.0           # Độ trễ nâng bút (ms)

# Mapping model AxiDraw sang mã số pyaxidraw
AXIDRAW_MODEL_CODES: Dict[str, int] = {
    "AxiDraw_V2": 1,
    "AxiDraw_V3": 1,
    "AxiDraw_V3_A3": 2,
    "AxiDraw_SE_A3": 2,
    "AxiDraw_V3_XLX": 3,
    "AxiDraw_MiniKit": 4,
    "AxiDraw_SE_A4": 5,
    "AxiDraw_V3_B6": 8,
}

# ---------------------------------------------------------------------------
# Mã lỗi chuẩn (theo API Spec v1.4)
# ---------------------------------------------------------------------------
VALID_HARDWARE_ERRORS: Dict[str, str] = {
    "HARDWARE_NOT_CONNECTED": "Mất kết nối máy vẽ",
    "HARDWARE_PAPER_JAM": "Phát hiện kẹt giấy tại bàn vẽ",
    "HARDWARE_OUT_OF_INK": "Hết mực hoặc ngòi không tiếp xúc giấy",
    "JOB_NOT_FOUND": "Không tìm thấy ID bản vẽ",
    "JOB_ALREADY_EXISTS": "Bản vẽ này đang chạy",
    "INVALID_STATE": "Trạng thái không hợp lệ cho thao tác",
    "NOT_SUPPORTED": "Thao tác không được thiết bị hỗ trợ",
    "SVG_READ_ERROR": "File SVG không tồn tại hoặc không đọc được",
    "SVG_INVALID": "Nội dung SVG không hợp lệ hoặc sai cú pháp XML",
    "PROFILE_LOAD_ERROR": "Không thể nạp hoặc validate calibration profile",
    "HARDWARE_ERROR": "Lỗi phần cứng chưa phân loại",
}

# ---------------------------------------------------------------------------
# Kiểm tra & Xác thực SVG bằng xml.etree.ElementTree
# ---------------------------------------------------------------------------

def validate_svg_content_or_path(svg_content_or_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Xác thực SVG đầu vào:
    - Nếu là file path (.svg hoặc có path separator): kiểm tra file tồn tại (SVG_READ_ERROR)
      và cú pháp XML hợp lệ (SVG_INVALID).
    - Nếu là inline string: kiểm tra tính hợp lệ của XML bằng xml.etree.ElementTree.
      Bất kỳ chuỗi nào sai XML (như <svg><path></svg> thiếu thẻ đóng) hoặc không phải SVG
      đều bị từ chối với SVG_INVALID.
    
    Returns:
        (is_valid, resolved_content_or_path, error_code)
    """
    if not svg_content_or_path or not str(svg_content_or_path).strip():
        return False, None, "SVG_READ_ERROR"

    raw = svg_content_or_path.strip()

    # Kiểm tra nếu là file
    if os.path.isfile(raw):
        try:
            with open(raw, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return False, None, "SVG_READ_ERROR"

        try:
            root = ET.fromstring(content)
            tag = root.tag.lower()
            if not tag.endswith("svg"):
                return False, None, "SVG_INVALID"
            return True, raw, None
        except ET.ParseError:
            return False, None, "SVG_INVALID"

    # Nhận diện đường dẫn file nhưng không tìm thấy file
    is_path_like = ("<svg" not in raw.lower()) and (raw.lower().endswith(".svg") or "/" in raw or "\\" in raw)
    if is_path_like:
        return False, None, "SVG_READ_ERROR"

    # Kiểm tra inline SVG string bằng XML parser
    try:
        root = ET.fromstring(raw)
        tag = root.tag.lower()
        if not tag.endswith("svg"):
            return False, None, "SVG_INVALID"
        return True, raw, None
    except ET.ParseError:
        return False, None, "SVG_INVALID"


# ---------------------------------------------------------------------------
# Calibration Profile (Validation & Built-in Parser)
# ---------------------------------------------------------------------------

def _default_profile() -> Dict[str, Any]:
    return {
        "version": "1.0",
        "device": {
            "model": "AxiDraw_V3",
            "port": None
        },
        "paper": {
            "size": "a4",
            "orientation": "landscape",
            "width_mm": 297.0,
            "height_mm": 210.0
        },
        "origin": {
            "x_mm": 5.0,
            "y_mm": 5.0,
            "note": "5mm safety margin từ mép giấy"
        },
        "motion": {
            "speed_pendown_mm_s": ASSUMED_PEN_SPEED_MM_PER_SEC,
            "speed_penup_mm_s": ASSUMED_PEN_UP_SPEED_MM_PER_SEC,
            "accel_pct": 75
        },
        "pen": {
            "pos_up_pct": 60,
            "pos_down_pct": 35,
            "delay_down_ms": ASSUMED_PEN_DOWN_DELAY_MS,
            "delay_up_ms": ASSUMED_PEN_UP_DELAY_MS
        }
    }


def validate_calibration_profile(profile: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(profile, dict):
        return False, "Profile phải là một dictionary"

    if "version" not in profile:
        return False, "Thiếu trường 'version'"

    device = profile.get("device", {})
    if not isinstance(device, dict):
        return False, "Trường 'device' phải là mapping"
    model = device.get("model", "AxiDraw_V3")
    if model not in AXIDRAW_MODEL_CODES and model not in ("AxiDraw_V2", "AxiDraw_V3", "AxiDraw_SE_A4"):
        return False, f"Model '{model}' không được hỗ trợ trong danh mục AxiDraw"

    paper = profile.get("paper", {})
    if not isinstance(paper, dict):
        return False, "Trường 'paper' phải là mapping"
    for field in ("width_mm", "height_mm"):
        val = paper.get(field)
        if val is None or not (isinstance(val, (int, float)) and val > 0):
            return False, f"Khổ giấy 'paper.{field}' phải là số dương"

    origin = profile.get("origin", {})
    if not isinstance(origin, dict):
        return False, "Trường 'origin' phải là mapping"
    for field in ("x_mm", "y_mm"):
        val = origin.get(field)
        if val is None or not (isinstance(val, (int, float)) and val >= 0):
            return False, f"Gốc tọa độ 'origin.{field}' phải là số >= 0"

    motion = profile.get("motion", {})
    if not isinstance(motion, dict):
        return False, "Trường 'motion' phải là mapping"
    for field in ("speed_pendown_mm_s", "speed_penup_mm_s", "accel_pct"):
        val = motion.get(field)
        if val is None or not (isinstance(val, (int, float)) and val > 0):
            return False, f"Tham số động học 'motion.{field}' phải là số dương"

    pen = profile.get("pen", {})
    if not isinstance(pen, dict):
        return False, "Trường 'pen' phải là mapping"
    for field in ("pos_up_pct", "pos_down_pct", "delay_down_ms", "delay_up_ms"):
        val = pen.get(field)
        if val is None or not (isinstance(val, (int, float)) and val >= 0):
            return False, f"Tham số nâng hạ bút 'pen.{field}' phải là số >= 0"

    return True, "Valid"


def _fallback_parse_yaml(text: str) -> Dict[str, Any]:
    res: Dict[str, Any] = {}
    current_section: Optional[str] = None
    for line in text.splitlines():
        line_clean = line.split("#")[0].rstrip()
        if not line_clean.strip():
            continue

        if not line_clean.startswith(" ") and ":" in line_clean:
            parts = line_clean.split(":", 1)
            k = parts[0].strip()
            v = parts[1].strip()
            if not v:
                current_section = k
                res[current_section] = {}
            else:
                current_section = None
                res[k] = _parse_yaml_scalar(v)
        elif line_clean.startswith("  ") and current_section and ":" in line_clean:
            parts = line_clean.strip().split(":", 1)
            sub_k = parts[0].strip()
            sub_v = parts[1].strip()
            res[current_section][sub_k] = _parse_yaml_scalar(sub_v)

    return res


def _parse_yaml_scalar(val: str) -> Any:
    val = val.strip()
    if val.startswith('"') and val.endswith('"') and len(val) >= 2:
        return val[1:-1]
    if val.startswith("'") and val.endswith("'") and len(val) >= 2:
        return val[1:-1]
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    if val.lower() in ("null", "none"):
        return None
    try:
        if "." in val:
            return float(val)
        return int(val)
    except ValueError:
        return val


def load_calibration_profile(profile_path: Optional[str] = None) -> Dict[str, Any]:
    if profile_path is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        profile_path = os.path.join(repo_root, "config", "calibration_profile.yaml")

    profile = _default_profile()
    if not os.path.isfile(profile_path):
        return profile

    try:
        loaded = None
        try:
            import yaml  # type: ignore
            with open(profile_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
        except ImportError:
            with open(profile_path, "r", encoding="utf-8") as f:
                loaded = _fallback_parse_yaml(f.read())

        if isinstance(loaded, dict):
            _deep_merge(profile, loaded)
            is_valid, msg = validate_calibration_profile(profile)
            if not is_valid:
                print(f"[TV3 WARNING] Calibration profile không hợp lệ ({msg}). Dùng mặc định.")
                return _default_profile()
    except Exception as exc:
        print(f"[TV3 WARNING] Lỗi khi nạp profile ({exc}). Dùng mặc định.")

    return profile


def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def extract_svg_viewbox_scale(svg_content: str) -> Tuple[float, float]:
    """
    Trích xuất tỉ lệ chuyển đổi (scale_x, scale_y) từ viewBox và width/height của thẻ <svg>.
    Đơn vị trả về: (mm_per_user_unit_x, mm_per_user_unit_y).
    """
    w_match = re.search(r'width=["\']([0-9.]+)(mm|px|cm|in|pt|pc|%)?["\']', svg_content)
    h_match = re.search(r'height=["\']([0-9.]+)(mm|px|cm|in|pt|pc|%)?["\']', svg_content)
    vb_match = re.search(r'viewBox=["\']([0-9.\s-]+)["\']', svg_content)

    if not (w_match and h_match and vb_match):
        return 1.0, 1.0

    w_val, w_unit = float(w_match.group(1)), (w_match.group(2) or "px")
    h_val, h_unit = float(h_match.group(1)), (h_match.group(2) or "px")

    _unit_to_mm = {"mm": 1.0, "cm": 10.0, "in": 25.4, "px": 25.4 / 96.0, "pt": 25.4 / 72.0, "pc": 25.4 / 6.0}
    w_mm = w_val * _unit_to_mm.get(w_unit, 1.0)
    h_mm = h_val * _unit_to_mm.get(h_unit, 1.0)

    parts = vb_match.group(1).split()
    if len(parts) < 4:
        return 1.0, 1.0

    vb_w = float(parts[2])
    vb_h = float(parts[3])
    if vb_w == 0.0 or vb_h == 0.0:
        return 1.0, 1.0

    return w_mm / vb_w, h_mm / vb_h


def apply_origin_offset_to_svg(svg_content: str, offset_x_mm: float = 5.0, offset_y_mm: float = 5.0) -> str:
    """
    Áp dụng offset tọa độ an toàn (mặc định 5mm, 5mm trên giấy) vào SVG.
    QUY ĐỔI CHÍNH XÁC THEO VIEWBOX:
    Offset 5mm được chuyển đổi sang số đơn vị user units trong viewBox tương ứng:
      dx_units = offset_x_mm / scale_x
      dy_units = offset_y_mm / scale_y
    """
    if offset_x_mm == 0.0 and offset_y_mm == 0.0:
        return svg_content

    scale_x, scale_y = extract_svg_viewbox_scale(svg_content)
    offset_x_units = offset_x_mm / max(1e-6, scale_x)
    offset_y_units = offset_y_mm / max(1e-6, scale_y)

    svg_tag_match = re.search(r"<svg\b[^>]*>", svg_content, re.IGNORECASE)
    close_tag_match = re.search(r"</svg>", svg_content, re.IGNORECASE)

    if not svg_tag_match or not close_tag_match:
        return svg_content

    svg_open_end = svg_tag_match.end()
    svg_close_start = close_tag_match.start()

    inner_content = svg_content[svg_open_end:svg_close_start]
    wrapped_inner = f'\n  <g id="calibration_origin_offset" transform="translate({offset_x_units:.4f}, {offset_y_units:.4f})">{inner_content}\n  </g>\n'

    return svg_content[:svg_open_end] + wrapped_inner + svg_content[svg_close_start:]


# ---------------------------------------------------------------------------
# Ghi nhận Metrics (CSV Logging)
# ---------------------------------------------------------------------------

def record_metric(job: Dict[str, Any]) -> None:
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    csv_path = os.path.join(log_dir, "hardware_metrics.csv")
    fieldnames = [
        "request_id",
        "timestamp",
        "actual_draw_time_sec",
        "estimated_draw_time_sec",
        "is_simulated",
        "hardware_status",
        "source_tag",
    ]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = {
        "request_id": job.get("request_id", ""),
        "timestamp": now,
        "actual_draw_time_sec": job.get("actual_draw_time_sec"),
        "estimated_draw_time_sec": job.get("total_draw_time_sec"),
        "is_simulated": job.get("is_simulated", True),
        "hardware_status": job.get("status", ""),
        "source_tag": job.get("source_tag", "simulator"),
    }
    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


# ---------------------------------------------------------------------------
# SVG Path Geometry Engine (Bézier, Arc A/a, Transform & Real Pen-up Tracking)
# ---------------------------------------------------------------------------

def _bezier_cubic_length(p0: Tuple[float, float], p1: Tuple[float, float],
                         p2: Tuple[float, float], p3: Tuple[float, float],
                         n_segments: int = 20) -> float:
    def bezier_point(t: float) -> Tuple[float, float]:
        u = 1.0 - t
        tt = t * t
        uu = u * u
        uui = uu * u
        tti = tt * t
        x = uui * p0[0] + 3.0 * uu * t * p1[0] + 3.0 * u * tt * p2[0] + tti * p3[0]
        y = uui * p0[1] + 3.0 * uu * t * p1[1] + 3.0 * u * tt * p2[1] + tti * p3[1]
        return x, y

    length = 0.0
    prev = p0
    for i in range(1, n_segments + 1):
        curr = bezier_point(i / n_segments)
        length += math.hypot(curr[0] - prev[0], curr[1] - prev[1])
        prev = curr
    return length


def _bezier_quadratic_length(p0: Tuple[float, float], p1: Tuple[float, float],
                             p2: Tuple[float, float], n_segments: int = 20) -> float:
    def bezier_q(t: float) -> Tuple[float, float]:
        u = 1.0 - t
        x = u * u * p0[0] + 2.0 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2.0 * u * t * p1[1] + t * t * p2[1]
        return x, y

    length = 0.0
    prev = p0
    for i in range(1, n_segments + 1):
        curr = bezier_q(i / n_segments)
        length += math.hypot(curr[0] - prev[0], curr[1] - prev[1])
        prev = curr
    return length


def _arc_svg_length(x0: float, y0: float, rx: float, ry: float,
                    phi_deg: float, large_arc: bool, sweep: bool,
                    x1: float, y1: float, n_segments: int = 20) -> float:
    if x0 == x1 and y0 == y1:
        return 0.0

    rx = abs(rx)
    ry = abs(ry)
    if rx == 0.0 or ry == 0.0:
        return math.hypot(x1 - x0, y1 - y0)

    phi = math.radians(phi_deg % 360.0)
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)

    dx = (x0 - x1) / 2.0
    dy = (y0 - y1) / 2.0
    x1_prime = cos_phi * dx + sin_phi * dy
    y1_prime = -sin_phi * dx + cos_phi * dy

    lambda_rad = (x1_prime * x1_prime) / (rx * rx) + (y1_prime * y1_prime) / (ry * ry)
    if lambda_rad > 1.0:
        sqrt_l = math.sqrt(lambda_rad)
        rx *= sqrt_l
        ry *= sqrt_l

    num = rx * rx * ry * ry - rx * rx * y1_prime * y1_prime - ry * ry * x1_prime * x1_prime
    den = rx * rx * y1_prime * y1_prime + ry * ry * x1_prime * x1_prime
    sign = -1.0 if large_arc == sweep else 1.0
    sq = max(0.0, num / max(1e-9, den))
    coef = sign * math.sqrt(sq)

    cx_prime = coef * ((rx * y1_prime) / ry)
    cy_prime = coef * (-(ry * x1_prime) / rx)

    cx = cos_phi * cx_prime - sin_phi * cy_prime + (x0 + x1) / 2.0
    cy = sin_phi * cx_prime + cos_phi * cy_prime + (y0 + y1) / 2.0

    def angle_between(u: Tuple[float, float], v: Tuple[float, float]) -> float:
        dot = u[0] * v[0] + u[1] * v[1]
        len_u = math.hypot(u[0], u[1])
        len_v = math.hypot(v[0], v[1])
        val = max(-1.0, min(1.0, dot / max(1e-9, (len_u * len_v))))
        ang = math.acos(val)
        if (u[0] * v[1] - u[1] * v[0]) < 0.0:
            ang = -ang
        return ang

    v_start = ((x1_prime - cx_prime) / rx, (y1_prime - cy_prime) / ry)
    theta1 = angle_between((1.0, 0.0), v_start)

    v_end = ((-x1_prime - cx_prime) / rx, (-y1_prime - cy_prime) / ry)
    delta_theta = angle_between(v_start, v_end)

    if not sweep and delta_theta > 0:
        delta_theta -= 2.0 * math.pi
    elif sweep and delta_theta < 0:
        delta_theta += 2.0 * math.pi

    length = 0.0
    prev_pt = (x0, y0)
    for i in range(1, n_segments + 1):
        ang = theta1 + delta_theta * (i / n_segments)
        ex = rx * math.cos(ang)
        ey = ry * math.sin(ang)
        curr_x = cos_phi * ex - sin_phi * ey + cx
        curr_y = sin_phi * ex + cos_phi * ey + cy
        length += math.hypot(curr_x - prev_pt[0], curr_y - prev_pt[1])
        prev_pt = (curr_x, curr_y)

    return length


def _tokenize_path(d: str) -> List[Any]:
    token_re = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])|(-?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)")
    tokens: List[Any] = []
    for m in token_re.finditer(d):
        cmd, num = m.group(1), m.group(2)
        if cmd:
            tokens.append(cmd)
        elif num:
            tokens.append(float(num))
    return tokens


def _consume_coords(tokens: List[Any], idx: int, n: int) -> Tuple[Tuple[float, ...], int]:
    vals = []
    for _ in range(n):
        if idx >= len(tokens) or isinstance(tokens[idx], str):
            raise ValueError("Thiếu toạ độ trong path")
        vals.append(float(tokens[idx]))
        idx += 1
    return tuple(vals), idx


def parse_svg_path_geometry(d_attr: str) -> Tuple[float, List[Tuple[Tuple[float, float], Tuple[float, float]]]]:
    if not d_attr or not d_attr.strip():
        return 0.0, []

    tokens = _tokenize_path(d_attr)
    total_len = 0.0
    cur_x = cur_y = 0.0
    start_x = start_y = 0.0
    last_ctrl_x = last_ctrl_y = None
    cmd = None
    idx = 0

    subpaths: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
    current_subpath_start: Optional[Tuple[float, float]] = None

    while idx < len(tokens):
        tok = tokens[idx]

        if isinstance(tok, str):
            cmd = tok
            idx += 1
            if cmd in ('Z', 'z'):
                if current_subpath_start is not None:
                    dist = math.hypot(start_x - cur_x, start_y - cur_y)
                    total_len += dist
                    cur_x, cur_y = start_x, start_y
                    subpaths.append((current_subpath_start, (cur_x, cur_y)))
                    current_subpath_start = None
                last_ctrl_x = last_ctrl_y = None
                cmd = None
            continue

        if cmd is None:
            idx += 1
            continue

        if cmd in ('M', 'm'):
            try:
                (x, y), idx = _consume_coords(tokens, idx, 2)
            except ValueError:
                break
            if current_subpath_start is not None:
                subpaths.append((current_subpath_start, (cur_x, cur_y)))
            if cmd == 'M':
                cur_x, cur_y = x, y
            else:
                cur_x += x
                cur_y += y
            start_x, start_y = cur_x, cur_y
            current_subpath_start = (start_x, start_y)
            last_ctrl_x = last_ctrl_y = None
            cmd = 'L' if cmd == 'M' else 'l'
            continue

        elif cmd in ('L', 'l'):
            try:
                (x, y), idx = _consume_coords(tokens, idx, 2)
            except ValueError:
                break
            nx = x if cmd == 'L' else cur_x + x
            ny = y if cmd == 'L' else cur_y + y
            total_len += math.hypot(nx - cur_x, ny - cur_y)
            cur_x, cur_y = nx, ny
            last_ctrl_x = last_ctrl_y = None

        elif cmd in ('H', 'h'):
            try:
                (x,), idx = _consume_coords(tokens, idx, 1)
            except ValueError:
                break
            nx = x if cmd == 'H' else cur_x + x
            total_len += abs(nx - cur_x)
            cur_x = nx
            last_ctrl_x = last_ctrl_y = None

        elif cmd in ('V', 'v'):
            try:
                (y,), idx = _consume_coords(tokens, idx, 1)
            except ValueError:
                break
            ny = y if cmd == 'V' else cur_y + y
            total_len += abs(ny - cur_y)
            cur_y = ny
            last_ctrl_x = last_ctrl_y = None

        elif cmd in ('C', 'c'):
            try:
                (x1, y1, x2, y2, x, y), idx = _consume_coords(tokens, idx, 6)
            except ValueError:
                break
            if cmd == 'c':
                x1 += cur_x
                y1 += cur_y
                x2 += cur_x
                y2 += cur_y
                x += cur_x
                y += cur_y
            total_len += _bezier_cubic_length((cur_x, cur_y), (x1, y1), (x2, y2), (x, y))
            last_ctrl_x, last_ctrl_y = x2, y2
            cur_x, cur_y = x, y

        elif cmd in ('S', 's'):
            try:
                (x2, y2, x, y), idx = _consume_coords(tokens, idx, 4)
            except ValueError:
                break
            if cmd == 's':
                x2 += cur_x
                y2 += cur_y
                x += cur_x
                y += cur_y
            if last_ctrl_x is not None:
                x1 = 2.0 * cur_x - last_ctrl_x
                y1 = 2.0 * cur_y - last_ctrl_y
            else:
                x1, y1 = cur_x, cur_y
            total_len += _bezier_cubic_length((cur_x, cur_y), (x1, y1), (x2, y2), (x, y))
            last_ctrl_x, last_ctrl_y = x2, y2
            cur_x, cur_y = x, y

        elif cmd in ('Q', 'q'):
            try:
                (x1, y1, x, y), idx = _consume_coords(tokens, idx, 4)
            except ValueError:
                break
            if cmd == 'q':
                x1 += cur_x
                y1 += cur_y
                x += cur_x
                y += cur_y
            total_len += _bezier_quadratic_length((cur_x, cur_y), (x1, y1), (x, y))
            last_ctrl_x, last_ctrl_y = x1, y1
            cur_x, cur_y = x, y

        elif cmd in ('T', 't'):
            try:
                (x, y), idx = _consume_coords(tokens, idx, 2)
            except ValueError:
                break
            if cmd == 't':
                x += cur_x
                y += cur_y
            if last_ctrl_x is not None:
                x1 = 2.0 * cur_x - last_ctrl_x
                y1 = 2.0 * cur_y - last_ctrl_y
            else:
                x1, y1 = cur_x, cur_y
            total_len += _bezier_quadratic_length((cur_x, cur_y), (x1, y1), (x, y))
            last_ctrl_x, last_ctrl_y = x1, y1
            cur_x, cur_y = x, y

        elif cmd in ('A', 'a'):
            try:
                (rx, ry, x_rot, l_arc, swp, x, y), idx = _consume_coords(tokens, idx, 7)
            except ValueError:
                break
            nx = x if cmd == 'A' else cur_x + x
            ny = y if cmd == 'A' else cur_y + y
            total_len += _arc_svg_length(cur_x, cur_y, rx, ry, x_rot, bool(l_arc), bool(swp), nx, ny)
            cur_x, cur_y = nx, ny
            last_ctrl_x = last_ctrl_y = None

        else:
            idx += 1

    if current_subpath_start is not None:
        subpaths.append((current_subpath_start, (cur_x, cur_y)))

    return total_len, subpaths


def parse_svg_path_length_mm(d_attr: str) -> float:
    length, _ = parse_svg_path_geometry(d_attr)
    return length


def _parse_transform_scale(transform_str: Optional[str]) -> Tuple[float, float]:
    """Trích xuất tỉ lệ phóng đại từ thuộc tính transform="scale(...) translate(...)"."""
    scale_x = scale_y = 1.0
    if not transform_str:
        return 1.0, 1.0

    scale_m = re.search(r"scale\(\s*(-?[0-9.]+)(?:[\s,]+(-?[0-9.]+))?\s*\)", transform_str)
    if scale_m:
        sx = float(scale_m.group(1))
        sy = float(scale_m.group(2)) if scale_m.group(2) else sx
        scale_x *= abs(sx)
        scale_y *= abs(sy)

    return scale_x, scale_y


def estimate_svg_draw_time(
    svg_content_or_path: str,
    speed_mm_per_sec: float = ASSUMED_PEN_SPEED_MM_PER_SEC,
    speed_penup_mm_per_sec: float = ASSUMED_PEN_UP_SPEED_MM_PER_SEC,
    pen_down_delay_ms: float = ASSUMED_PEN_DOWN_DELAY_MS,
    pen_up_delay_ms: float = ASSUMED_PEN_UP_DELAY_MS,
    request_id: Optional[str] = None,
) -> int:
    """
    Ước lượng thời gian thi công chuẩn xác (giây) cho bản vẽ SVG:
    Công thức: T = L_pendown / v_down + L_penup_real / v_up + N_lifts * (t_down + t_up)
    
    HỖ TRỢ PHÂN CẤP NHÓM LỒNG NHAU (Hierarchical DOM Traversal):
    Duyệt đệ quy qua các thẻ <g transform="scale(...)"> để tích lũy hệ số scale chính xác
    lên từng thẻ <path>. Giải quyết triệt để lỗi đường 10mm trong nhóm scale(2) bị tính thành 10s thay vì 20s.
    """
    content = ""
    if svg_content_or_path:
        if os.path.isfile(svg_content_or_path):
            try:
                with open(svg_content_or_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except OSError:
                return 15
        else:
            content = svg_content_or_path

    if not content.strip() or "<svg" not in content.lower():
        return 15

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return 15

    base_scale_x, base_scale_y = extract_svg_viewbox_scale(content)

    total_pendown_mm = 0.0
    all_subpaths: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []

    def traverse_node(node: ET.Element, parent_sx: float, parent_sy: float) -> None:
        nonlocal total_pendown_mm
        # Lấy transform của chính node hiện tại
        node_trans = node.attrib.get("transform")
        local_sx, local_sy = _parse_transform_scale(node_trans)
        curr_sx = parent_sx * local_sx
        curr_sy = parent_sy * local_sy

        tag_name = node.tag.split("}")[-1].lower() if "}" in node.tag else node.tag.lower()

        if tag_name == "path":
            d = node.attrib.get("d")
            if d:
                effective_scale = ((curr_sx * base_scale_x) + (curr_sy * base_scale_y)) / 2.0
                p_len, subps = parse_svg_path_geometry(d)
                total_pendown_mm += p_len * effective_scale

                for (s_pt, e_pt) in subps:
                    all_subpaths.append((
                        (s_pt[0] * base_scale_x * curr_sx, s_pt[1] * base_scale_y * curr_sy),
                        (e_pt[0] * base_scale_x * curr_sx, e_pt[1] * base_scale_y * curr_sy)
                    ))

        for child in node:
            traverse_node(child, curr_sx, curr_sy)

    traverse_node(root, 1.0, 1.0)

    if total_pendown_mm <= 0:
        return 15

    # Tính quãng đường nhấc bút (pen-up distance) thực tế
    real_penup_mm = 0.0
    current_pen_pos = (0.0, 0.0)
    n_lifts = len(all_subpaths)

    for (start_pt, end_pt) in all_subpaths:
        travel = math.hypot(start_pt[0] - current_pen_pos[0], start_pt[1] - current_pen_pos[1])
        real_penup_mm += travel
        current_pen_pos = end_pt

    real_penup_mm += math.hypot(0.0 - current_pen_pos[0], 0.0 - current_pen_pos[1])

    t_pendown = total_pendown_mm / max(0.1, speed_mm_per_sec)
    t_penup = real_penup_mm / max(0.1, speed_penup_mm_per_sec)
    t_delays = n_lifts * (pen_down_delay_ms + pen_up_delay_ms) / 1000.0

    total_sec = t_pendown + t_penup + t_delays
    return max(2, int(round(total_sec)))


# ---------------------------------------------------------------------------
# Interface trừu tượng
# ---------------------------------------------------------------------------

class HardwareAdapterInterface(ABC):

    @abstractmethod
    def connect(self, port: Optional[str] = None) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_simulation(self) -> bool:
        pass

    @abstractmethod
    def load_profile(self, profile_path: Optional[str] = None) -> None:
        pass

    @abstractmethod
    async def start_job(self, request_id: str, svg_content_or_path: str, paper_size: str = "a4") -> Dict[str, Any]:
        pass

    @abstractmethod
    async def pause_job(self, request_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def resume_job(self, request_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def cancel_job(self, request_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_status(self, request_id: str, simulate_error: Optional[str] = None) -> Dict[str, Any]:
        pass


# ---------------------------------------------------------------------------
# MockSimulatorAdapter
# ---------------------------------------------------------------------------

class MockSimulatorAdapter(HardwareAdapterInterface):

    def __init__(self, connected: bool = True, speed_factor: float = 1.0,
                 profile_path: Optional[str] = None):
        self._connected = connected
        self._speed_factor = max(0.1, speed_factor)
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self._profile: Dict[str, Any] = {}
        self.load_profile(profile_path)

    def load_profile(self, profile_path: Optional[str] = None) -> None:
        self._profile = load_calibration_profile(profile_path)

    def connect(self, port: Optional[str] = None) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False
        for rid, job in self.jobs.items():
            if job.get("status") in ("printing", "queued", "paused"):
                task = job.get("task")
                if task and not task.done():
                    task.cancel()
                job["task"] = None
                job["status"] = "error"
                job["error"] = {
                    "code": "HARDWARE_NOT_CONNECTED",
                    "message": VALID_HARDWARE_ERRORS["HARDWARE_NOT_CONNECTED"],
                }

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def is_simulation(self) -> bool:
        return True

    async def _simulate_task(self, request_id: str) -> None:
        job = self.jobs.get(request_id)
        if not job:
            return

        if not job.get("started_at"):
            job["started_at"] = time.monotonic()

        total = job["total_draw_time_sec"]

        try:
            while True:
                await asyncio.sleep(0.05)

                job_now = self.jobs.get(request_id)
                if not job_now:
                    return

                if job_now["status"] in ("paused", "cancelled", "error"):
                    return

                elapsed = (
                    job_now["elapsed_before_pause"]
                    + (time.monotonic() - job_now["started_at"]) * self._speed_factor
                )
                job_now["progress_percent"] = min(99, int((elapsed / max(1.0, total)) * 100))
                job_now["estimated_time_remaining_sec"] = max(0, int(total - elapsed))

                if elapsed >= total:
                    job_now.update({
                        "status": "done",
                        "progress_percent": 100,
                        "estimated_time_remaining_sec": 0,
                        "actual_draw_time_sec": round(elapsed, 2),
                        "is_simulated": True,
                        "actual_hardware_measured": False,
                        "task": None,
                    })
                    record_metric(job_now)
                    return

        except asyncio.CancelledError:
            job_now = self.jobs.get(request_id)
            if job_now and job_now.get("task") is not None:
                job_now["task"] = None
            raise

    async def start_job(self, request_id: str, svg_content_or_path: str,
                        paper_size: str = "a4") -> Dict[str, Any]:
        if not self._connected:
            return {
                "error": {
                    "code": "HARDWARE_NOT_CONNECTED",
                    "message": VALID_HARDWARE_ERRORS["HARDWARE_NOT_CONNECTED"],
                },
                "status_code": 503,
            }

        is_valid, resolved, err_code = validate_svg_content_or_path(svg_content_or_path)
        if not is_valid:
            return {
                "error": {
                    "code": err_code or "SVG_READ_ERROR",
                    "message": VALID_HARDWARE_ERRORS.get(err_code or "SVG_READ_ERROR"),
                },
                "status_code": 400,
            }

        existing = self.jobs.get(request_id)
        if existing and existing["status"] in ("printing", "paused", "queued"):
            return {
                "error": {
                    "code": "JOB_ALREADY_EXISTS",
                    "message": VALID_HARDWARE_ERRORS["JOB_ALREADY_EXISTS"],
                },
                "status_code": 409,
            }

        speed_pendown = self._profile.get("motion", {}).get("speed_pendown_mm_s", ASSUMED_PEN_SPEED_MM_PER_SEC)
        speed_penup = self._profile.get("motion", {}).get("speed_penup_mm_s", ASSUMED_PEN_UP_SPEED_MM_PER_SEC)
        delay_down = self._profile.get("pen", {}).get("delay_down_ms", ASSUMED_PEN_DOWN_DELAY_MS)
        delay_up = self._profile.get("pen", {}).get("delay_up_ms", ASSUMED_PEN_UP_DELAY_MS)

        total_time = estimate_svg_draw_time(
            resolved or svg_content_or_path,
            speed_mm_per_sec=speed_pendown,
            speed_penup_mm_per_sec=speed_penup,
            pen_down_delay_ms=delay_down,
            pen_up_delay_ms=delay_up,
            request_id=request_id,
        )

        self.jobs[request_id] = {
            "request_id": request_id,
            "status": "printing",
            "progress_percent": 0,
            "estimated_time_remaining_sec": total_time,
            "total_draw_time_sec": total_time,
            "actual_draw_time_sec": None,
            "error": None,
            "started_at": time.monotonic(),
            "elapsed_before_pause": 0.0,
            "paper_size": paper_size,
            "is_simulated": True,
            "actual_hardware_measured": False,
            "source_tag": "simulator",
            "task": None,
        }
        self.jobs[request_id]["task"] = asyncio.create_task(self._simulate_task(request_id))
        return {"request_id": request_id, "status": "printing"}

    async def pause_job(self, request_id: str) -> Dict[str, Any]:
        job = self.jobs.get(request_id)
        if not job:
            return {
                "error": {"code": "JOB_NOT_FOUND", "message": VALID_HARDWARE_ERRORS["JOB_NOT_FOUND"]},
                "status_code": 404,
            }
        if job["status"] not in ("printing", "queued"):
            return {
                "error": {"code": "INVALID_STATE", "message": "Chỉ có thể pause khi đang printing"},
                "status_code": 409,
            }

        if job.get("started_at"):
            job["elapsed_before_pause"] += (time.monotonic() - job["started_at"]) * self._speed_factor

        task = job.get("task")
        if task and not task.done():
            task.cancel()
            try:
                await asyncio.shield(asyncio.wait_for(asyncio.gather(task, return_exceptions=True), timeout=0.5))
            except Exception:
                pass
        job["task"] = None
        job["status"] = "paused"
        return {"request_id": request_id, "status": "paused"}

    async def resume_job(self, request_id: str) -> Dict[str, Any]:
        job = self.jobs.get(request_id)
        if not job:
            return {
                "error": {"code": "JOB_NOT_FOUND", "message": VALID_HARDWARE_ERRORS["JOB_NOT_FOUND"]},
                "status_code": 404,
            }
        if job["status"] != "paused":
            return {
                "error": {"code": "INVALID_STATE", "message": "Chỉ có thể resume khi đang paused"},
                "status_code": 409,
            }

        old_task = job.get("task")
        if old_task and not old_task.done():
            old_task.cancel()
            try:
                await asyncio.shield(asyncio.wait_for(asyncio.gather(old_task, return_exceptions=True), timeout=0.2))
            except Exception:
                pass

        job["started_at"] = time.monotonic()
        job["status"] = "printing"
        job["task"] = asyncio.create_task(self._simulate_task(request_id))
        return {"request_id": request_id, "status": "printing"}

    async def cancel_job(self, request_id: str) -> Dict[str, Any]:
        job = self.jobs.get(request_id)
        if not job:
            return {
                "error": {"code": "JOB_NOT_FOUND", "message": VALID_HARDWARE_ERRORS["JOB_NOT_FOUND"]},
                "status_code": 404,
            }
        if job["status"] in ("done", "cancelled"):
            return {
                "error": {
                    "code": "INVALID_STATE",
                    "message": f"Không thể cancel job đã ở trạng thái '{job['status']}'",
                },
                "status_code": 409,
            }

        task = job.get("task")
        if task and not task.done():
            task.cancel()
            try:
                await asyncio.shield(asyncio.wait_for(asyncio.gather(task, return_exceptions=True), timeout=0.5))
            except Exception:
                pass
        job["task"] = None
        job["status"] = "cancelled"
        record_metric(job)
        return {"request_id": request_id, "status": "cancelled"}

    def get_status(self, request_id: str, simulate_error: Optional[str] = None) -> Dict[str, Any]:
        job = self.jobs.get(request_id)
        if not job:
            return {
                "error": {"code": "JOB_NOT_FOUND", "message": VALID_HARDWARE_ERRORS["JOB_NOT_FOUND"]},
                "status_code": 404,
            }

        if simulate_error:
            msg = VALID_HARDWARE_ERRORS.get(simulate_error, f"Lỗi giả lập: {simulate_error}")
            job.update({"status": "error", "error": {"code": simulate_error, "message": msg}})

        res: Dict[str, Any] = {
            "request_id": request_id,
            "status": job["status"],
            "progress_percent": job["progress_percent"],
            "estimated_time_remaining_sec": job["estimated_time_remaining_sec"],
            "error": job["error"],
        }
        if job["status"] in ("done", "cancelled", "error"):
            res["actual_draw_time_sec"] = job.get("actual_draw_time_sec")
            res["is_simulated"] = job.get("is_simulated", True)
            res["actual_hardware_measured"] = False
            res["source_tag"] = "simulator"

        return res


# ---------------------------------------------------------------------------
# AxiDraw Fake Driver
# ---------------------------------------------------------------------------

class _FakeAxiDrawDriver:
    """Fake driver mô phỏng có khả năng dừng/ngắt cho CI/Unit test."""

    def __init__(self):
        self.options = type("opts", (), {
            "mode": "plot",
            "model": 1,
            "speed_pendown": 25,
            "speed_penup": 75,
            "accel": 75,
            "pen_pos_up": 60,
            "pen_pos_down": 35,
            "pen_delay_up": 100,
            "pen_delay_down": 120,
            "port": None,
            "auto_rotate": True,
        })()
        self._connected = False
        self._is_paused = False
        self._is_stopped = False
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._stop_event = threading.Event()
        self.total_plot_time = 0.2

    def interactive(self):
        pass

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self):
        self.stop()
        self._connected = False

    def plot_setup(self, svg_path: str) -> None:
        if not os.path.isfile(svg_path):
            raise FileNotFoundError(f"SVG not found: {svg_path}")
        self._is_stopped = False
        self._is_paused = False
        self._pause_event.set()
        self._stop_event.clear()

    def plot_run(self) -> None:
        steps = 10
        step_duration = self.total_plot_time / steps

        for _ in range(steps):
            if self._stop_event.is_set():
                break

            while not self._pause_event.is_set():
                if self._stop_event.is_set():
                    return
                time.sleep(0.01)

            time.sleep(step_duration)

    def pause(self):
        self._is_paused = True
        self._pause_event.clear()

    def resume(self):
        self._is_paused = False
        self._pause_event.set()

    def stop(self):
        self._is_stopped = True
        self._stop_event.set()
        self._pause_event.set()

    def penup(self):
        pass

    def pendown(self):
        pass

    @property
    def connected(self):
        return self._connected


# ---------------------------------------------------------------------------
# AxiDrawAdapter — Máy vẽ AxiDraw
# ---------------------------------------------------------------------------

class AxiDrawAdapter(HardwareAdapterInterface):
    """
    Adapter Máy vẽ AxiDraw:
    - Khi use_fake_driver=False: Bắt buộc dùng driver pyaxidraw thật. Nếu thiếu thư viện
      hoặc thiết bị không cắm, báo lỗi không kết nối; TUYỆT ĐỐI KHÔNG tự ý tráo sang fake driver.
    - Khi use_fake_driver=True: Dùng _FakeAxiDrawDriver (dành riêng cho CI).
    """

    def __init__(self, port: Optional[str] = None, use_fake_driver: bool = False,
                 profile_path: Optional[str] = None):
        self._port = port
        self._connected = False
        self._ad: Any = None
        self._use_fake_driver = use_fake_driver
        self._job_lock = threading.Lock()
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self._profile: Dict[str, Any] = {}
        self.load_profile(profile_path)
        self._init_driver()

    def load_profile(self, profile_path: Optional[str] = None) -> None:
        self._profile = load_calibration_profile(profile_path)

    def _init_driver(self) -> None:
        if self._use_fake_driver:
            self._ad = _FakeAxiDrawDriver()
            self._connected = False
            return

        # Khi yêu cầu máy thật (use_fake_driver=False):
        try:
            from pyaxidraw import axidraw  # type: ignore
            self._ad = axidraw.AxiDraw()
        except ImportError:
            # QUY TẮC RÕ RÀNG: Không có driver thật -> đặt None, không fallback ngầm!
            self._ad = None

        self._connected = False

    def _apply_profile_to_driver(self) -> None:
        if self._ad is None:
            return

        device = self._profile.get("device", {})
        paper = self._profile.get("paper", {})
        motion = self._profile.get("motion", {})
        pen = self._profile.get("pen", {})

        opts = self._ad.options
        try:
            model_name = device.get("model", "AxiDraw_V3")
            if hasattr(opts, "model"):
                opts.model = AXIDRAW_MODEL_CODES.get(model_name, 1)

            if hasattr(opts, "auto_rotate"):
                opts.auto_rotate = (paper.get("orientation", "landscape") == "landscape")

            opts.speed_pendown = int(motion.get("speed_pendown_mm_s", ASSUMED_PEN_SPEED_MM_PER_SEC))
            opts.speed_penup = int(motion.get("speed_penup_mm_s", ASSUMED_PEN_UP_SPEED_MM_PER_SEC))
            opts.accel = int(motion.get("accel_pct", 75))

            opts.pen_pos_up = int(pen.get("pos_up_pct", 60))
            opts.pen_pos_down = int(pen.get("pos_down_pct", 35))
            opts.pen_delay_up = int(pen.get("delay_up_ms", ASSUMED_PEN_UP_DELAY_MS))
            opts.pen_delay_down = int(pen.get("delay_down_ms", ASSUMED_PEN_DOWN_DELAY_MS))

            port = self._port or device.get("port")
            if port and hasattr(opts, "port"):
                opts.port = port
        except AttributeError:
            pass

    def connect(self, port: Optional[str] = None) -> bool:
        if port:
            self._port = port

        if self._ad is None:
            self._connected = False
            return False

        self._apply_profile_to_driver()

        try:
            if hasattr(self._ad, 'interactive'):
                self._ad.interactive()
            if hasattr(self._ad, 'connect'):
                res = self._ad.connect()
                self._connected = bool(res)
            else:
                self._connected = True
        except Exception as exc:
            print(f"[TV3 ERROR] Kết nối AxiDraw thất bại: {exc}")
            self._connected = False

        return self._connected

    def disconnect(self) -> None:
        for rid, job in self.jobs.items():
            if job.get("status") in ("printing", "paused"):
                job["_cancel_event"].set()
                job["_pause_event"].set()
                job["status"] = "error"
                job["error"] = {
                    "code": "HARDWARE_NOT_CONNECTED",
                    "message": VALID_HARDWARE_ERRORS["HARDWARE_NOT_CONNECTED"],
                }

        if self._ad:
            try:
                if hasattr(self._ad, 'stop'):
                    self._ad.stop()
                if hasattr(self._ad, 'options'):
                    self._ad.options.mode = "align"
                if hasattr(self._ad, 'plot_run'):
                    self._ad.plot_run()
                if hasattr(self._ad, 'disconnect'):
                    self._ad.disconnect()
            except Exception:
                pass

        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected and (self._ad is not None)

    @property
    def is_simulation(self) -> bool:
        return self._use_fake_driver

    def _get_source_tag(self) -> str:
        if self._use_fake_driver:
            return "axidraw_fake_driver"
        return "axidraw_real"

    def _is_real_physical_measurement(self) -> bool:
        return (not self._use_fake_driver) and self.is_connected

    async def start_job(self, request_id: str, svg_content_or_path: str,
                        paper_size: str = "a4") -> Dict[str, Any]:
        if not self.is_connected:
            err_msg = (
                "AxiDraw chưa được kết nối vật lý. Không tìm thấy thư viện pyaxidraw hoặc thiết bị phần cứng."
                if not self._use_fake_driver
                else "Fake driver chưa được kết nối. Gọi connect() trước."
            )
            return {
                "error": {
                    "code": "HARDWARE_NOT_CONNECTED",
                    "message": err_msg,
                },
                "status_code": 503,
            }

        is_valid, resolved, err_code = validate_svg_content_or_path(svg_content_or_path)
        if not is_valid:
            return {
                "error": {
                    "code": err_code or "SVG_READ_ERROR",
                    "message": VALID_HARDWARE_ERRORS.get(err_code or "SVG_READ_ERROR"),
                },
                "status_code": 400,
            }

        with self._job_lock:
            active = [rid for rid, j in self.jobs.items() if j.get("status") in ("printing", "paused")]
            if active:
                return {
                    "error": {
                        "code": "JOB_ALREADY_EXISTS",
                        "message": f"Máy đang thi công job '{active[0]}'. Không thể bắt đầu job mới.",
                    },
                    "status_code": 409,
                }

        raw_svg_content = ""
        if os.path.isfile(svg_content_or_path):
            with open(svg_content_or_path, "r", encoding="utf-8") as f:
                raw_svg_content = f.read()
        else:
            raw_svg_content = svg_content_or_path

        origin_x = float(self._profile.get("origin", {}).get("x_mm", 5.0))
        origin_y = float(self._profile.get("origin", {}).get("y_mm", 5.0))
        prepared_svg = apply_origin_offset_to_svg(raw_svg_content, origin_x, origin_y)

        tmp_dir = os.path.join(os.path.dirname(__file__), "tmp_print")
        os.makedirs(tmp_dir, exist_ok=True)
        final_svg_path = os.path.join(tmp_dir, f"{request_id}_prepared.svg")
        with open(final_svg_path, "w", encoding="utf-8") as f:
            f.write(prepared_svg)

        motion = self._profile.get("motion", {})
        pen = self._profile.get("pen", {})
        total_est = estimate_svg_draw_time(
            final_svg_path,
            speed_mm_per_sec=motion.get("speed_pendown_mm_s", ASSUMED_PEN_SPEED_MM_PER_SEC),
            speed_penup_mm_per_sec=motion.get("speed_penup_mm_s", ASSUMED_PEN_UP_SPEED_MM_PER_SEC),
            pen_down_delay_ms=pen.get("delay_down_ms", ASSUMED_PEN_DOWN_DELAY_MS),
            pen_up_delay_ms=pen.get("delay_up_ms", ASSUMED_PEN_UP_DELAY_MS),
            request_id=request_id,
        )

        is_real = self._is_real_physical_measurement()
        pause_evt = threading.Event()
        pause_evt.set()
        cancel_evt = threading.Event()

        self.jobs[request_id] = {
            "request_id": request_id,
            "status": "printing",
            "progress_percent": 0,
            "estimated_time_remaining_sec": total_est,
            "total_draw_time_sec": total_est,
            "actual_draw_time_sec": None,
            "error": None,
            "started_at": time.monotonic(),
            "svg_path": final_svg_path,
            "is_simulated": not is_real,
            "actual_hardware_measured": is_real,
            "source_tag": self._get_source_tag(),
            "_pause_event": pause_evt,
            "_cancel_event": cancel_evt,
        }

        adapter_ref = self

        def _plot_worker():
            job = adapter_ref.jobs.get(request_id)
            if not job:
                return

            try:
                adapter_ref._apply_profile_to_driver()
                adapter_ref._ad.plot_setup(final_svg_path)

                if job["_cancel_event"].is_set():
                    return

                t_start = time.monotonic()
                adapter_ref._ad.plot_run()

                while not job["_pause_event"].is_set():
                    if job["_cancel_event"].is_set():
                        return
                    time.sleep(0.05)

                if job["_cancel_event"].is_set() or job.get("status") in ("cancelled", "error", "paused"):
                    return

                elapsed = int(time.monotonic() - t_start)
                job.update({
                    "status": "done",
                    "progress_percent": 100,
                    "estimated_time_remaining_sec": 0,
                    "actual_draw_time_sec": elapsed,
                })
                record_metric(job)

            except Exception as exc:
                err_code = "HARDWARE_ERROR"
                err_msg = str(exc)
                if "not connected" in err_msg.lower() or "disconnect" in err_msg.lower():
                    err_code = "HARDWARE_NOT_CONNECTED"
                job.update({
                    "status": "error",
                    "error": {"code": err_code, "message": err_msg},
                })
                record_metric(job)

        thread = threading.Thread(target=_plot_worker, daemon=True)
        thread.start()
        return {"request_id": request_id, "status": "printing"}

    async def pause_job(self, request_id: str) -> Dict[str, Any]:
        job = self.jobs.get(request_id)
        if not job:
            return {
                "error": {"code": "JOB_NOT_FOUND", "message": VALID_HARDWARE_ERRORS["JOB_NOT_FOUND"]},
                "status_code": 404,
            }
        if job["status"] not in ("printing", "queued"):
            return {
                "error": {"code": "INVALID_STATE", "message": "Chỉ có thể pause khi đang printing"},
                "status_code": 409,
            }

        # Kiểm tra nếu driver thật KHÔNG hỗ trợ pause:
        if not self._use_fake_driver and not hasattr(self._ad, "pause"):
            return {
                "error": {
                    "code": "NOT_SUPPORTED",
                    "message": "AxiDraw phần cứng không hỗ trợ tạm dừng (pause) giữa chừng nét vẽ theo tài liệu pyaxidraw.",
                },
                "status_code": 400,
                "pause_supported": False,
                "status": job["status"],
            }

        job["status"] = "paused"
        job["_pause_event"].clear()

        if hasattr(self._ad, 'pause'):
            self._ad.pause()

        return {
            "request_id": request_id,
            "status": "paused",
            "pause_supported": True if self._use_fake_driver else False,
        }

    async def resume_job(self, request_id: str) -> Dict[str, Any]:
        job = self.jobs.get(request_id)
        if not job:
            return {
                "error": {"code": "JOB_NOT_FOUND", "message": VALID_HARDWARE_ERRORS["JOB_NOT_FOUND"]},
                "status_code": 404,
            }
        if job["status"] != "paused":
            return {
                "error": {"code": "INVALID_STATE", "message": "Chỉ có thể resume khi đang paused"},
                "status_code": 409,
            }

        job["status"] = "printing"
        job["_pause_event"].set()

        if hasattr(self._ad, 'resume'):
            self._ad.resume()

        return {
            "request_id": request_id,
            "status": "printing",
            "pause_supported": True if self._use_fake_driver else False,
        }

    async def cancel_job(self, request_id: str) -> Dict[str, Any]:
        job = self.jobs.get(request_id)
        if not job:
            return {
                "error": {"code": "JOB_NOT_FOUND", "message": VALID_HARDWARE_ERRORS["JOB_NOT_FOUND"]},
                "status_code": 404,
            }
        if job["status"] in ("done", "cancelled"):
            return {
                "error": {
                    "code": "INVALID_STATE",
                    "message": f"Không thể cancel job đã ở trạng thái '{job['status']}'",
                },
                "status_code": 409,
            }

        job["status"] = "cancelled"
        job["_cancel_event"].set()
        job["_pause_event"].set()

        # Ngắt driver thực sự
        if self._ad:
            if hasattr(self._ad, 'stop'):
                self._ad.stop()
            elif hasattr(self._ad, 'disconnect'):
                self._ad.disconnect()

        record_metric(job)
        return {"request_id": request_id, "status": "cancelled"}

    def get_status(self, request_id: str, simulate_error: Optional[str] = None) -> Dict[str, Any]:
        job = self.jobs.get(request_id)
        if not job:
            return {
                "error": {"code": "JOB_NOT_FOUND", "message": VALID_HARDWARE_ERRORS["JOB_NOT_FOUND"]},
                "status_code": 404,
            }

        if simulate_error:
            msg = VALID_HARDWARE_ERRORS.get(simulate_error, f"Lỗi giả lập: {simulate_error}")
            job.update({"status": "error", "error": {"code": simulate_error, "message": msg}})

        is_real = self._is_real_physical_measurement()
        res: Dict[str, Any] = {
            "request_id": request_id,
            "status": job["status"],
            "progress_percent": job.get("progress_percent", 0),
            "estimated_time_remaining_sec": job.get("estimated_time_remaining_sec", 0),
            "error": job.get("error"),
            "progress_is_estimated": True,
        }
        if job["status"] in ("done", "cancelled", "error"):
            res["actual_draw_time_sec"] = job.get("actual_draw_time_sec")
            res["is_simulated"] = not is_real
            res["actual_hardware_measured"] = is_real
            res["source_tag"] = self._get_source_tag()

        return res


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_global_hardware_adapter: Optional[HardwareAdapterInterface] = None


def get_hardware_adapter(mode: str = "auto", speed_factor: float = 1.0,
                         profile_path: Optional[str] = None) -> HardwareAdapterInterface:
    global _global_hardware_adapter
    if _global_hardware_adapter is not None:
        return _global_hardware_adapter

    if mode == "physical":
        adapter = AxiDrawAdapter(profile_path=profile_path, use_fake_driver=False)
    elif mode == "fake":
        adapter = AxiDrawAdapter(use_fake_driver=True, profile_path=profile_path)
    elif mode == "simulator":
        adapter = MockSimulatorAdapter(speed_factor=speed_factor, profile_path=profile_path)
    else:  # auto
        try:
            candidate = AxiDrawAdapter(profile_path=profile_path, use_fake_driver=False)
            if candidate.connect():
                adapter = candidate
            else:
                adapter = MockSimulatorAdapter(speed_factor=speed_factor, profile_path=profile_path)
        except Exception:
            adapter = MockSimulatorAdapter(speed_factor=speed_factor, profile_path=profile_path)

    _global_hardware_adapter = adapter
    return _global_hardware_adapter


def reset_hardware_adapter() -> None:
    global _global_hardware_adapter
    _global_hardware_adapter = None


# ---------------------------------------------------------------------------
# CLI Entry Point: Smoke Test cho TV3
# ---------------------------------------------------------------------------

async def _run_smoke_test(mode: str = "simulator", fixture_path: Optional[str] = None,
                          profile_path: Optional[str] = None) -> int:
    print("=" * 70)
    print(f"OmniDraw TV3 Hardware Smoke Test Runner — Mode: {mode.upper()}")
    print("=" * 70)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not fixture_path:
        fixture_path = os.path.join(repo_root, "tests", "fixtures", "smoke_test_specimen.svg")

    if not os.path.isfile(fixture_path):
        print(f"[FAIL] Không tìm thấy SVG fixture tại: {fixture_path}")
        return 1

    print(f"1. Nạp fixture: {fixture_path}")
    print(f"2. Nạp calibration profile từ: {profile_path or 'config/calibration_profile.yaml'}")

    adapter: HardwareAdapterInterface
    if mode == "physical":
        adapter = AxiDrawAdapter(profile_path=profile_path, use_fake_driver=False)
    elif mode == "fake":
        adapter = AxiDrawAdapter(profile_path=profile_path, use_fake_driver=True)
    else:
        adapter = MockSimulatorAdapter(connected=True, speed_factor=15.0, profile_path=profile_path)

    print(f"3. Thử kết nối adapter ({adapter.__class__.__name__})...")
    conn = adapter.connect()
    print(f"   Kết nối: {'THÀNH CÔNG' if conn else 'THẤT BẠI (Blocked by hardware)'}")
    if not conn and mode == "physical":
        print("[INFO] Không tìm thấy pyaxidraw hoặc thiết bị vật lý AxiDraw. Máy chưa sẵn sàng.")
        return 2

    req_id = f"smoke-{int(time.time())}"
    print(f"4. Bắt đầu tác vụ in với request_id='{req_id}'...")
    res = await adapter.start_job(req_id, fixture_path)
    if "error" in res:
        print(f"[FAIL] Khởi tạo job thất bại: {res['error']}")
        return 1
    print(f"   Trạng thái ban đầu: {res.get('status')}")

    print("5. Thử nghiệm tạm dừng (pause)...")
    p_res = await adapter.pause_job(req_id)
    print(f"   Trạng thái sau pause: {p_res.get('status')}")
    await asyncio.sleep(0.1)

    print("6. Thử nghiệm tiếp tục (resume)...")
    r_res = await adapter.resume_job(req_id)
    print(f"   Trạng thái sau resume: {r_res.get('status')}")

    print("7. Đợi tác vụ hoàn tất (polling status)...")
    for _ in range(100):
        await asyncio.sleep(0.1)
        st = adapter.get_status(req_id)
        if st["status"] == "done":
            print(f"[PASS] Bản vẽ hoàn tất thành công 100%!")
            print(f"   - actual_draw_time_sec: {st.get('actual_draw_time_sec')}s")
            print(f"   - is_simulated: {st.get('is_simulated')}")
            print(f"   - actual_hardware_measured: {st.get('actual_hardware_measured')}")
            print(f"   - source_tag: {st.get('source_tag', 'N/A')}")
            return 0
        elif st["status"] == "error":
            print(f"[FAIL] Tác vụ gặp lỗi: {st.get('error')}")
            return 1

    print("[TIMEOUT] Quá thời gian chờ hoàn thành smoke test.")
    return 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="OmniDraw TV3 Hardware CLI & Smoke Test")
    parser.add_argument("--smoke-test", action="store_true", help="Chạy quy trình smoke test tự động")
    parser.add_argument("--mode", choices=["simulator", "fake", "physical"], default="simulator",
                        help="Chế độ chạy adapter: simulator, fake, hoặc physical")
    parser.add_argument("--svg", type=str, default=None, help="Đường dẫn file SVG mẫu")
    parser.add_argument("--profile", type=str, default=None, help="Đường dẫn calibration_profile.yaml")
    args = parser.parse_args()

    if args.smoke_test:
        code = asyncio.run(_run_smoke_test(mode=args.mode, fixture_path=args.svg, profile_path=args.profile))
        sys.exit(code)
    else:
        parser.print_help()
