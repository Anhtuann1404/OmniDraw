"""
OmniDraw - Module Viết Thư Tay Tự Động (Bio-Inspired Vietnamese Handwriting Engine)
==================================================================================
Tạo nét bút đơn (Single-Stroke Vector Centerline) cho chữ viết tay Tiếng Việt:
- Giải quyết bài toán Outline Font: không bị viền đôi như font TTF thông thường.
- Hỗ trợ toàn bộ ký tự Tiếng Việt có dấu nhờ tách âm vị NFD (Modular Accent Compositing).
- Thuật toán biến thiên sinh học (Bio-mimetic Variation):
  + Baseline drift: lượn sóng tự nhiên trục Y.
  + Slant variation: độ ngả nghiêng tự nhiên của nét chữ.
  + Micro-jitter: độ run vi mô của tay người.
- 4 phong cách: Học sinh, Thảo nghiêng, Thư pháp, Ký tên nhanh.
"""

import math
import os
import random
import unicodedata
import numpy as np

# ----------------------------- Bộ Sinh Nét Cong Bézier Hữu Cơ Chuẩn Hình Học -----------------------------

def bz(p0, c1, c2, p3, n=8):
    """Tính các điểm nội suy đường cong Bézier bậc 3 mượt mà C2."""
    t = np.linspace(0.0, 1.0, n)[:, None]
    return (1.0 - t)**3 * p0 + 3.0 * (1.0 - t)**2 * t * c1 + 3.0 * (1.0 - t) * t**2 * c2 + t**3 * p3


def make_oval(cx=4.8, top_y=7.0, bot_y=14.0, rx=2.4, n=8):
    """
    Sinh hình tròn/elip khép kín hoàn hảo bằng 4 cung Bézier chuẩn hình học:
    Hệ số kappa = 4*(sqrt(2)-1)/3 = 0.55228475.
    Tiếp tuyến hoàn toàn nằm ngang ở đỉnh và đáy, thẳng đứng ở hai bên sườn.
    Triệt tiêu 100% hiện tượng góc nhọn, méo, thắt nút hay hình thoi.
    """
    k = 0.55228475
    cy = (top_y + bot_y) / 2.0
    ry = (bot_y - top_y) / 2.0
    kx = rx * k
    ky = ry * k

    # Ngược chiều kim đồng hồ từ đỉnh: đỉnh -> trái -> đáy -> phải -> đỉnh
    q1 = bz(np.array([cx, top_y]), np.array([cx - kx, top_y]), np.array([cx - rx, cy - ky]), np.array([cx - rx, cy]), n=n)
    q2 = bz(np.array([cx - rx, cy]), np.array([cx - rx, cy + ky]), np.array([cx - kx, bot_y]), np.array([cx, bot_y]), n=n)
    q3 = bz(np.array([cx, bot_y]), np.array([cx + kx, bot_y]), np.array([cx + rx, cy + ky]), np.array([cx + rx, cy]), n=n)
    q4 = bz(np.array([cx + rx, cy]), np.array([cx + rx, cy - ky]), np.array([cx + kx, top_y]), np.array([cx, top_y]), n=n)
    return np.vstack([q1, q2[1:], q3[1:], q4[1:]])


def make_hook_stem(x_stem=7.0, top_y=7.0, bot_y=14.0, hook_w=2.0, hook_h=2.8, n=6):
    """Sinh nét sổ thẳng tiếp xúc baseline và móc lên cong tròn C1-continuous."""
    turn_y = bot_y - hook_h * 0.8
    if top_y < turn_y:
        num_stem = max(3, int((turn_y - top_y) / 1.5))
        y_vals = np.linspace(top_y, turn_y, num_stem)
        stem = np.column_stack([np.full_like(y_vals, x_stem), y_vals])
    else:
        stem = np.array([[x_stem, top_y]])

    mid_x = x_stem + hook_w * 0.45
    p0 = np.array([x_stem, turn_y])
    c1 = np.array([x_stem, bot_y])
    c2 = np.array([x_stem + hook_w * 0.2, bot_y])
    p_bot = np.array([mid_x, bot_y])
    h1 = bz(p0, c1, c2, p_bot, n=n)

    c3 = np.array([x_stem + hook_w * 0.7, bot_y])
    c4 = np.array([x_stem + hook_w * 0.9, bot_y - hook_h * 0.6])
    p_end = np.array([x_stem + hook_w, bot_y - hook_h])
    h2 = bz(p_bot, c3, c4, p_end, n=n)

    return np.vstack([stem, h1[1:], h2[1:]])


def make_ascender_loop(x_stem=2.0, top_y=0.5, bot_y=11.5, loop_w=2.2, n=8):
    """
    Sinh nét khuyết trên chuẩn tiểu học Việt Nam:
    Bầu khuyết rộng mở tròn trịa, đỉnh uốn cong vòm mềm mại, thân sổ thẳng đứng.
    """
    p0 = np.array([x_stem - 0.7, 9.5])
    c1 = np.array([x_stem + 1.0, 6.0])
    c2 = np.array([x_stem + loop_w, 2.0])
    p_top = np.array([x_stem + 1.2, top_y])
    up = bz(p0, c1, c2, p_top, n=n)

    c3 = np.array([x_stem + 0.2, top_y])
    c4 = np.array([x_stem, top_y + 0.6])
    p_turn = np.array([x_stem, top_y + 1.8])
    turn = bz(p_top, c3, c4, p_turn, n=6)

    num_stem = max(3, int((bot_y - (top_y + 1.8)) / 1.5))
    y_vals = np.linspace(top_y + 1.8, bot_y, num_stem)
    stem = np.column_stack([np.full_like(y_vals, x_stem), y_vals])

    return np.vstack([up, turn[1:], stem[1:]])


def make_descender_loop(x_stem=7.0, top_y=7.0, bot_y=19.5, loop_w=2.4, exit_x=8.8, exit_y=11.5, n=8):
    """
    Sinh nét khuyết dưới chuẩn tiểu học Việt Nam:
    Bầu đuôi elip thon dài dạng oval (bot_y=19.5, ry=3.2, rx=1.2),
    đối xứng tròn trịa chuẩn hệ số kappa = 0.55228475.
    Tiếp tuyến nằm ngang tuyệt đối ở đáy, vươn chéo cắt baseline tại thân sổ.
    """
    k = 0.55228475
    rx = loop_w / 2.0
    ry = 3.2
    x_mid = x_stem - rx
    turn_y = bot_y - ry  # 16.3

    # 1. Thân sổ thẳng đứng từ top_y đến turn_y
    num_stem = max(3, int((turn_y - top_y) / 2.0))
    y_stem = np.linspace(top_y, turn_y, num_stem)
    stem = np.column_stack([np.full_like(y_stem, x_stem), y_stem])

    # 2. Bầu khuyết nửa phải: từ tiếp tuyến đứng x_stem đến tiếp tuyến ngang bot_y
    p0 = np.array([x_stem, turn_y])
    c1 = np.array([x_stem, turn_y + ry * k])
    c2 = np.array([x_mid + rx * k, bot_y])
    p_bot = np.array([x_mid, bot_y])
    cup_right = bz(p0, c1, c2, p_bot, n=n)

    # 3. Bầu khuyết nửa trái: từ tiếp tuyến ngang bot_y đến tiếp tuyến đứng x_stem - loop_w
    c3 = np.array([x_mid - rx * k, bot_y])
    c4 = np.array([x_stem - loop_w, turn_y + ry * k])
    p_left = np.array([x_stem - loop_w, turn_y])
    cup_left = bz(p_bot, c3, c4, p_left, n=n)

    # 4. Nét chéo lượn lên cắt đường kẻ đáy tại thân sổ (x_stem, 14.0)
    c5 = np.array([x_stem - loop_w, 15.0])
    c6 = np.array([x_stem - 0.7, 14.0])
    p_cross = np.array([x_stem, 14.0])
    cross = bz(p_left, c5, c6, p_cross, n=n)

    # 5. Móc thoát nét lượn cong mềm sang chữ tiếp theo
    c7 = np.array([x_stem + 0.6, 14.0])
    c8 = np.array([exit_x - 0.4, exit_y + 0.8])
    p_exit = np.array([exit_x, exit_y])
    exit_s = bz(p_cross, c7, c8, p_exit, n=6)

    return np.vstack([stem, cup_right[1:], cup_left[1:], cross[1:], exit_s[1:]])


def make_arch(x_left=2.2, x_right=6.8, top_y=7.0, bot_y=14.0, hook_w=2.0, n=6):
    """
    Sinh nét móc vòm cong tròn tự nhiên chuẩn hình học đối xứng:
    Hai cung Bézier bậc 3 ghép lại tiếp xúc đỉnh top_y nằm ngang hoàn hảo.
    """
    x_mid = (x_left + x_right) / 2.0
    w_half = (x_right - x_left) / 2.0
    k = 0.55228475
    h = 10.5 - top_y

    arch_left = bz(np.array([x_left, 10.5]),
                   np.array([x_left, top_y + h * 0.2]),
                   np.array([x_mid - w_half * k, top_y]),
                   np.array([x_mid, top_y]), n=n)

    arch_right = bz(np.array([x_mid, top_y]),
                    np.array([x_mid + w_half * k, top_y]),
                    np.array([x_right, top_y + h * 0.2]),
                    np.array([x_right, 10.5]), n=n)

    stem_hook = make_hook_stem(x_stem=x_right, top_y=10.5, bot_y=bot_y, hook_w=hook_w, hook_h=2.8, n=n)
    return np.vstack([arch_left, arch_right[1:], stem_hook[1:]])


# ----------------------------- Bộ Glyph Nét Đơn Hữu Cơ (Grid 12x18) -----------------------------
# Baseline = 14, Cap-height = 2, x-height = 7, Ascender = 0, Descender = 18

GLYPHS = {
    # Chữ in hoa với nét cong tròn Bézier
    'A': [np.array([[1.0, 14.0], [5.5, 2.0], [10.0, 14.0]]), np.array([[2.8, 9.5], [8.2, 9.5]])],
    'B': [
        np.array([[2.0, 2.0], [2.0, 14.0]]),
        bz(np.array([2.0, 2.0]), np.array([8.2, 1.8]), np.array([8.2, 8.0]), np.array([2.0, 8.0]), n=8),
        bz(np.array([2.0, 8.0]), np.array([9.2, 7.8]), np.array([9.2, 14.2]), np.array([2.0, 14.0]), n=8)
    ],
    'C': [
        bz(np.array([9.5, 4.5]), np.array([5.5, 1.8]), np.array([2.0, 4.5]), np.array([2.0, 11.5]), n=8),
        bz(np.array([2.0, 11.5]), np.array([2.0, 14.2]), np.array([6.5, 14.2]), np.array([9.5, 12.0]), n=8)
    ],
    'D': [
        np.array([[2.0, 2.0], [2.0, 14.0]]),
        bz(np.array([2.0, 2.0]), np.array([9.8, 1.8]), np.array([9.8, 14.2]), np.array([2.0, 14.0]), n=12)
    ],
    'E': [np.array([[9.0, 2.0], [2.0, 2.0], [2.0, 14.0], [9.0, 14.0]]), np.array([[2.0, 8.0], [7.5, 8.0]])],
    'F': [np.array([[9.0, 2.0], [2.0, 2.0], [2.0, 14.0]]), np.array([[2.0, 8.0], [7.0, 8.0]])],
    'G': [
        bz(np.array([9.5, 4.5]), np.array([5.5, 1.8]), np.array([2.0, 4.5]), np.array([2.0, 11.5]), n=8),
        bz(np.array([2.0, 11.5]), np.array([2.0, 14.2]), np.array([7.5, 14.2]), np.array([9.5, 14.0]), n=8),
        np.array([[9.5, 14.0], [9.5, 8.5], [6.0, 8.5]])
    ],
    'H': [np.array([[2.0, 2.0], [2.0, 14.0]]), np.array([[9.0, 2.0], [9.0, 14.0]]), np.array([[2.0, 8.0], [9.0, 8.0]])],
    'I': [np.array([[2.0, 2.0], [6.0, 2.0]]), np.array([[4.0, 2.0], [4.0, 14.0]]), np.array([[2.0, 14.0], [6.0, 14.0]])],
    'J': [
        bz(np.array([7.0, 2.0]), np.array([7.0, 11.0]), np.array([5.5, 14.2]), np.array([3.0, 14.2]), n=8),
        bz(np.array([3.0, 14.2]), np.array([1.5, 14.0]), np.array([1.2, 12.0]), np.array([1.5, 11.0]), n=6)
    ],
    'K': [np.array([[2.0, 2.0], [2.0, 14.0]]), np.array([[8.5, 2.0], [2.0, 8.5], [9.0, 14.0]])],
    'L': [np.array([[2.0, 2.0], [2.0, 14.0], [9.0, 14.0]])],
    'M': [np.array([[2.0, 14.0], [2.0, 2.0], [6.0, 9.5], [10.0, 2.0], [10.0, 14.0]])],
    'N': [np.array([[2.0, 14.0], [2.0, 2.0], [9.0, 14.0], [9.0, 2.0]])],
    'O': [make_oval(cx=5.5, top_y=2.0, bot_y=14.0, rx=3.5, n=12)],
    'P': [
        np.array([[2.0, 2.0], [2.0, 14.0]]),
        bz(np.array([2.0, 2.0]), np.array([8.2, 1.8]), np.array([8.2, 8.0]), np.array([2.0, 8.0]), n=8)
    ],
    'Q': [make_oval(cx=5.5, top_y=2.0, bot_y=14.0, rx=3.5, n=12), np.array([[6.5, 11.0], [10.5, 15.5]])],
    'R': [
        np.array([[2.0, 2.0], [2.0, 14.0]]),
        bz(np.array([2.0, 2.0]), np.array([8.2, 1.8]), np.array([8.2, 8.0]), np.array([2.0, 8.0]), n=8),
        np.array([[5.5, 8.0], [9.0, 14.0]])
    ],
    'S': [
        bz(np.array([9.0, 4.0]), np.array([6.5, 1.8]), np.array([2.5, 3.8]), np.array([3.5, 7.0]), n=8),
        bz(np.array([3.5, 7.0]), np.array([8.5, 8.5]), np.array([8.5, 13.5]), np.array([4.8, 14.2]), n=8),
        np.array([[4.8, 14.2], [2.0, 12.8]])
    ],
    'T': [np.array([[1.0, 2.0], [10.0, 2.0]]), np.array([[5.5, 2.0], [5.5, 14.0]])],
    'U': [
        bz(np.array([2.0, 2.0]), np.array([2.0, 11.0]), np.array([2.0, 14.2]), np.array([5.5, 14.2]), n=8),
        bz(np.array([5.5, 14.2]), np.array([9.0, 14.2]), np.array([9.0, 11.0]), np.array([9.0, 2.0]), n=8)
    ],
    'V': [np.array([[1.5, 2.0], [5.5, 14.0], [9.5, 2.0]])],
    'W': [np.array([[1.0, 2.0], [3.5, 14.0], [5.5, 6.5], [7.5, 14.0], [10.0, 2.0]])],
    'X': [np.array([[2.0, 2.0], [9.0, 14.0]]), np.array([[9.0, 2.0], [2.0, 14.0]])],
    'Y': [np.array([[1.5, 2.0], [5.5, 8.0], [9.5, 2.0]]), np.array([[5.5, 8.0], [5.5, 14.0]])],
    'Z': [np.array([[2.0, 2.0], [9.0, 2.0], [2.0, 14.0], [9.0, 14.0]])],

    # BẢNG CHỮ CÁI TIẾNG VIỆT CHUẨN MẪU TIỂU HỌC (Quyết định 31/2002/QĐ-BGDĐT)
    # a: Nét cong kín (oval) + nét móc ngược
    'a': [
        make_oval(cx=4.8, top_y=7.0, bot_y=14.0, rx=2.4),
        make_hook_stem(x_stem=7.0, top_y=7.0, bot_y=14.0, hook_w=2.0, hook_h=3.0)
    ],
    # b: Nét khuyết trên + nét móc đáy uốn lên x-height tạo vòng thắt sang phải
    'b': [np.vstack([
        make_ascender_loop(x_stem=2.0, top_y=0.5, bot_y=11.5, loop_w=2.2),
        bz(np.array([2.0, 11.5]), np.array([2.0, 14.0]), np.array([3.5, 14.0]), np.array([4.8, 14.0]), n=6)[1:],
        bz(np.array([4.8, 14.0]), np.array([6.5, 14.0]), np.array([6.5, 10.5]), np.array([6.2, 8.5]), n=6)[1:],
        bz(np.array([6.2, 8.5]), np.array([6.0, 7.2]), np.array([5.5, 7.0]), np.array([4.8, 7.0]), n=6)[1:],
        bz(np.array([4.8, 7.0]), np.array([4.2, 6.2]), np.array([5.8, 6.2]), np.array([7.2, 7.0]), n=6)[1:]
    ])],
    # c: Nét cong hở phải uốn tròn chuẩn hình học (3/4 vòng elip cân đối, móc nối mềm mại)
    'c': [np.vstack([
        bz(np.array([6.8, 8.5]), np.array([6.8, 7.2]), np.array([5.8, 7.0]), np.array([4.8, 7.0]), n=6),
        bz(np.array([4.8, 7.0]), np.array([3.48, 7.0]), np.array([2.4, 8.57]), np.array([2.4, 10.5]), n=8)[1:],
        bz(np.array([2.4, 10.5]), np.array([2.4, 12.43]), np.array([3.48, 14.0]), np.array([4.8, 14.0]), n=8)[1:],
        bz(np.array([4.8, 14.0]), np.array([5.8, 14.0]), np.array([6.8, 13.0]), np.array([7.4, 11.5]), n=6)[1:]
    ])],
    # d: Nét cong kín + nét móc ngược cao (từ cap-height y=1.2)
    'd': [
        make_oval(cx=4.8, top_y=7.0, bot_y=14.0, rx=2.4),
        make_hook_stem(x_stem=7.0, top_y=1.2, bot_y=14.0, hook_w=2.0, hook_h=3.0)
    ],
    # e: Nét cong bắt đầu từ giữa dòng lượn lên x-height tạo vòm tròn cân đối, lưng và móc nối tròn chuẩn như c
    'e': [np.vstack([
        bz(np.array([2.0, 11.0]), np.array([3.4, 10.2]), np.array([5.0, 9.0]), np.array([6.0, 7.8]), n=6),
        bz(np.array([6.0, 7.8]), np.array([6.2, 7.0]), np.array([5.6, 7.0]), np.array([4.8, 7.0]), n=6)[1:],
        bz(np.array([4.8, 7.0]), np.array([3.48, 7.0]), np.array([2.4, 8.57]), np.array([2.4, 10.5]), n=8)[1:],
        bz(np.array([2.4, 10.5]), np.array([2.4, 12.43]), np.array([3.48, 14.0]), np.array([4.8, 14.0]), n=8)[1:],
        bz(np.array([4.8, 14.0]), np.array([5.8, 14.0]), np.array([6.8, 13.0]), np.array([7.4, 11.5]), n=6)[1:]
    ])],
    # f: Chữ f phụ âm ngoại lai (nét khuyết trên + gạch ngang)
    'f': [
        bz(np.array([6.5, 2.5]), np.array([4.5, 0.8]), np.array([3.0, 2.0]), np.array([3.0, 14.0]), n=10),
        np.array([[1.5, 7.0], [6.0, 7.0]])
    ],
    # g: Nét cong kín + nét khuyết dưới dạng oval thon dài chuẩn tiểu học
    'g': [
        make_oval(cx=4.8, top_y=7.0, bot_y=14.0, rx=2.4),
        make_descender_loop(x_stem=7.2, top_y=7.0, bot_y=19.5, loop_w=2.4, exit_x=9.0, exit_y=11.5)
    ],
    # h: Nét khuyết trên + nét móc 2 đầu
    'h': [
        make_ascender_loop(x_stem=2.0, top_y=0.5, bot_y=14.0, loop_w=2.2),
        make_arch(x_left=2.0, x_right=6.8, top_y=7.0, bot_y=14.0, hook_w=2.0)
    ],
    # i: Nét hất + nét móc ngược + dấu chấm
    'i': [
        np.vstack([
            bz(np.array([1.2, 9.5]), np.array([2.0, 8.5]), np.array([2.8, 7.5]), np.array([3.2, 7.0]), n=6),
            make_hook_stem(x_stem=3.2, top_y=7.0, bot_y=14.0, hook_w=2.0, hook_h=3.0)[1:]
        ]),
        np.array([[3.2, 3.2], [3.4, 3.2]])
    ],
    # j: Nét hất + nét khuyết dưới + dấu chấm
    'j': [
        np.vstack([
            np.array([[1.2, 9.5], [3.2, 7.0], [3.2, 15.0]]),
            bz(np.array([3.2, 15.0]), np.array([3.2, 18.2]), np.array([1.8, 18.2]), np.array([1.0, 17.0]), n=8)[1:],
            bz(np.array([1.0, 17.0]), np.array([0.5, 16.0]), np.array([2.0, 14.5]), np.array([3.2, 14.0]), n=6)[1:]
        ]),
        np.array([[3.2, 3.2], [3.4, 3.2]])
    ],
    # k: Nét khuyết trên + Nét móc hai đầu có thắt ở giữa chuẩn tiểu học Việt Nam (bầu thon gọn)
    'k': [
        make_ascender_loop(x_stem=2.0, top_y=0.5, bot_y=14.0, loop_w=2.2),
        np.vstack([
            bz(np.array([2.0, 9.5]), np.array([2.1, 7.0]), np.array([2.8, 7.0]), np.array([3.4, 7.0]), n=6),
            bz(np.array([3.4, 7.0]), np.array([4.2, 7.0]), np.array([4.6, 8.0]), np.array([4.5, 9.0]), n=6)[1:],
            bz(np.array([4.5, 9.0]), np.array([4.2, 10.0]), np.array([3.2, 9.8]), np.array([2.6, 10.2]), n=6)[1:],
            bz(np.array([2.6, 10.2]), np.array([2.0, 10.5]), np.array([2.8, 11.0]), np.array([3.3, 10.8]), n=6)[1:],
            bz(np.array([3.3, 10.8]), np.array([4.0, 12.5]), np.array([4.5, 14.0]), np.array([5.4, 14.0]), n=6)[1:],
            bz(np.array([5.4, 14.0]), np.array([6.2, 14.0]), np.array([6.8, 12.8]), np.array([7.0, 11.5]), n=6)[1:]
        ])
    ],
    # l: Nét khuyết trên nối liền nét móc ngược chân rộng
    'l': [np.vstack([
        make_ascender_loop(x_stem=2.0, top_y=0.5, bot_y=11.5, loop_w=2.2),
        bz(np.array([2.0, 11.5]), np.array([2.0, 14.0]), np.array([2.8, 14.0]), np.array([3.8, 14.0]), n=6)[1:],
        bz(np.array([3.8, 14.0]), np.array([4.8, 14.0]), np.array([5.6, 12.5]), np.array([6.0, 11.2]), n=6)[1:]
    ])],
    # m: Nét móc xuôi 1 + nét móc xuôi 2 cong vòm tròn trịa + nét móc hai đầu có móc thoát nét
    'm': [
        np.vstack([
            np.array([[1.0, 9.5], [2.0, 7.0]]),
            np.array([[2.0, 7.0], [2.0, 14.0]])
        ]),
        make_arch(x_left=2.0, x_right=5.8, top_y=7.0, bot_y=14.0, hook_w=0.0),
        make_arch(x_left=5.8, x_right=9.6, top_y=7.0, bot_y=14.0, hook_w=2.0)
    ],
    # n: Nét móc xuôi + nét móc hai đầu
    'n': [
        np.vstack([
            np.array([[1.0, 9.5], [2.2, 7.0]]),
            np.array([[2.2, 7.0], [2.2, 14.0]])
        ]),
        make_arch(x_left=2.2, x_right=6.8, top_y=7.0, bot_y=14.0, hook_w=2.0)
    ],
    # o: Nét cong kín hình ô van đều chuẩn hình học
    'o': [make_oval(cx=4.8, top_y=7.0, bot_y=14.0, rx=2.4)],
    # p: Nét hất + nét sổ thẳng (xuống y=18) + nét móc hai đầu chuẩn tiểu học Việt Nam
    'p': [
        np.array([[1.2, 10.0], [2.8, 7.0]]),
        np.array([[2.8, 7.0], [2.8, 18.0]]),
        make_arch(x_left=2.8, x_right=6.8, top_y=7.0, bot_y=14.0, hook_w=2.0)
    ],
    # q: Nét cong kín + nét sổ thẳng xuống y=18
    'q': [
        make_oval(cx=4.8, top_y=7.0, bot_y=14.0, rx=2.4),
        np.array([[7.0, 7.0], [7.0, 18.0], [8.5, 16.5]])
    ],
    # r: CHUẨN TIỂU HỌC VIỆT NAM (Nét xiên lên đỉnh 1.25 đv, thắt tròn mắt nhỏ, vai cong võng mềm sang nét móc ngược)
    'r': [np.vstack([
        bz(np.array([1.2, 14.0]), np.array([2.0, 11.0]), np.array([2.8, 7.5]), np.array([3.4, 5.6]), n=8),
        bz(np.array([3.4, 5.6]), np.array([3.6, 5.0]), np.array([4.2, 5.0]), np.array([4.2, 5.5]), n=6)[1:],
        bz(np.array([4.2, 5.5]), np.array([4.2, 6.4]), np.array([3.0, 6.4]), np.array([3.2, 5.6]), n=6)[1:],
        bz(np.array([3.2, 5.6]), np.array([3.3, 5.2]), np.array([4.0, 6.2]), np.array([4.8, 6.4]), n=6)[1:],
        bz(np.array([4.8, 6.4]), np.array([5.5, 6.6]), np.array([6.2, 6.6]), np.array([6.6, 7.0]), n=6)[1:],
        bz(np.array([6.6, 7.0]), np.array([6.8, 7.3]), np.array([6.8, 8.0]), np.array([6.8, 9.5]), n=6)[1:],
        np.array([[6.8, 9.5], [6.8, 11.5]])[1:],
        bz(np.array([6.8, 11.5]), np.array([6.8, 14.0]), np.array([7.4, 14.0]), np.array([7.8, 14.0]), n=6)[1:],
        bz(np.array([7.8, 14.0]), np.array([8.4, 14.0]), np.array([8.8, 12.5]), np.array([8.8, 11.2]), n=6)[1:]
    ])],
    # s: CHUẨN TIỂU HỌC VIỆT NAM (Nét xiên lên đỉnh cao 1.25 đv, thắt nốt xoắn tròn rõ ràng, cong phồng lưng chữ s, cuộn đáy)
    's': [np.vstack([
        bz(np.array([1.2, 14.0]), np.array([2.0, 11.0]), np.array([3.0, 8.0]), np.array([3.6, 6.0]), n=8),
        bz(np.array([3.6, 6.0]), np.array([3.8, 4.6]), np.array([2.8, 4.4]), np.array([2.4, 5.2]), n=6)[1:],
        bz(np.array([2.4, 5.2]), np.array([2.0, 6.0]), np.array([3.0, 6.5]), np.array([3.8, 6.0]), n=6)[1:],
        bz(np.array([3.8, 6.0]), np.array([7.6, 8.0]), np.array([7.6, 12.5]), np.array([4.6, 14.0]), n=10)[1:],
        bz(np.array([4.6, 14.0]), np.array([2.6, 14.0]), np.array([2.2, 13.0]), np.array([3.2, 12.2]), n=6)[1:],
        bz(np.array([3.2, 12.2]), np.array([4.8, 14.0]), np.array([6.5, 14.0]), np.array([7.8, 11.5]), n=6)[1:]
    ])],
    # t: Nét hất lượn lên đỉnh 1.5 đv + nét sổ móc ngược + gạch ngang ngắn
    't': [
        np.vstack([
            bz(np.array([1.2, 9.5]), np.array([2.0, 7.5]), np.array([2.8, 4.5]), np.array([3.2, 3.5]), n=6),
            np.array([[3.2, 3.5], [3.2, 5.5], [3.2, 7.5], [3.2, 9.5], [3.2, 11.5]])[1:],
            bz(np.array([3.2, 11.5]), np.array([3.2, 14.0]), np.array([3.8, 14.0]), np.array([4.2, 14.0]), n=6)[1:],
            bz(np.array([4.2, 14.0]), np.array([4.8, 14.0]), np.array([5.2, 12.5]), np.array([5.2, 11.2]), n=6)[1:]
        ]),
        np.array([[2.0, 6.0], [4.4, 6.0]])
    ],
    # u: Nét hất + nét móc ngược 1 + nét móc ngược 2
    'u': [
        np.vstack([
            np.array([[1.2, 9.5], [2.8, 7.0]]),
            bz(np.array([2.8, 7.0]), np.array([2.8, 11.5]), np.array([3.4, 14.0]), np.array([4.8, 14.0]), n=6)[1:],
            bz(np.array([4.8, 14.0]), np.array([6.2, 14.0]), np.array([6.8, 11.5]), np.array([6.8, 7.0]), n=6)[1:]
        ]),
        make_hook_stem(x_stem=6.8, top_y=7.0, bot_y=14.0, hook_w=2.0, hook_h=3.0)
    ],
    # v: Nét móc 2 đầu + đáy uốn cong tròn + nét thắt nhỏ ở đỉnh sang phải
    'v': [np.vstack([
        bz(np.array([1.2, 9.5]), np.array([1.8, 7.2]), np.array([2.6, 7.0]), np.array([3.2, 7.5]), n=6),
        bz(np.array([3.2, 7.5]), np.array([3.8, 10.5]), np.array([4.2, 14.0]), np.array([5.2, 14.0]), n=8)[1:],
        bz(np.array([5.2, 14.0]), np.array([6.2, 14.0]), np.array([7.0, 9.5]), np.array([7.5, 7.0]), n=8)[1:],
        bz(np.array([7.5, 7.0]), np.array([7.2, 6.2]), np.array([8.2, 6.2]), np.array([8.8, 7.2]), n=6)[1:]
    ])],
    # w: Ngoại lai (hai nét u uốn cong tròn tiếp xúc baseline ngang)
    'w': [np.vstack([
        bz(np.array([1.2, 9.5]), np.array([1.8, 7.2]), np.array([2.2, 7.0]), np.array([2.6, 7.2]), n=5),
        bz(np.array([2.6, 7.2]), np.array([2.6, 11.5]), np.array([3.2, 14.0]), np.array([4.3, 14.0]), n=6)[1:],
        bz(np.array([4.3, 14.0]), np.array([5.4, 14.0]), np.array([6.0, 11.5]), np.array([6.0, 7.2]), n=6)[1:],
        bz(np.array([6.0, 7.2]), np.array([6.0, 11.5]), np.array([6.6, 14.0]), np.array([7.7, 14.0]), n=6)[1:],
        bz(np.array([7.7, 14.0]), np.array([8.8, 14.0]), np.array([9.4, 11.5]), np.array([9.4, 7.2]), n=6)[1:],
        bz(np.array([9.4, 7.2]), np.array([9.4, 6.4]), np.array([10.2, 6.4]), np.array([10.6, 7.2]), n=5)[1:]
    ])],
    # x: CHUẨN TIỂU HỌC VIỆT NAM (Hai nét cong chữ C ngược nhau chạm lưng ở giữa x=4.8, y=10.5)
    'x': [
        np.vstack([
            bz(np.array([2.4, 8.5]), np.array([2.4, 7.0]), np.array([3.4, 7.0]), np.array([4.0, 7.0]), n=6),
            bz(np.array([4.0, 7.0]), np.array([4.8, 7.0]), np.array([4.8, 8.8]), np.array([4.8, 10.5]), n=6)[1:],
            bz(np.array([4.8, 10.5]), np.array([4.8, 12.2]), np.array([4.8, 14.0]), np.array([4.0, 14.0]), n=6)[1:],
            bz(np.array([4.0, 14.0]), np.array([3.4, 14.0]), np.array([2.4, 14.0]), np.array([2.4, 12.5]), n=6)[1:]
        ]),
        np.vstack([
            bz(np.array([7.2, 8.5]), np.array([7.2, 7.0]), np.array([6.2, 7.0]), np.array([5.6, 7.0]), n=6),
            bz(np.array([5.6, 7.0]), np.array([4.8, 7.0]), np.array([4.8, 8.8]), np.array([4.8, 10.5]), n=6)[1:],
            bz(np.array([4.8, 10.5]), np.array([4.8, 12.2]), np.array([4.8, 14.0]), np.array([5.6, 14.0]), n=6)[1:],
            bz(np.array([5.6, 14.0]), np.array([6.4, 14.0]), np.array([7.4, 13.5]), np.array([7.4, 11.5]), n=6)[1:]
        ])
    ],
    # y: Nét hất + thân u tròn đáy + nét khuyết dưới dạng oval thon dài chuẩn tiểu học (nối liền mạch 1 nét)
    'y': [np.vstack([
        np.array([[1.2, 9.5], [2.8, 7.0]]),
        bz(np.array([2.8, 7.0]), np.array([2.8, 11.5]), np.array([3.4, 14.0]), np.array([4.8, 14.0]), n=6)[1:],
        bz(np.array([4.8, 14.0]), np.array([6.2, 14.0]), np.array([6.8, 11.5]), np.array([6.8, 7.0]), n=6)[1:],
        make_descender_loop(x_stem=6.8, top_y=7.0, bot_y=19.5, loop_w=2.4, exit_x=8.8, exit_y=11.5)[1:]
    ])],
    # z:
    'z': [np.array([[2.0, 7.0], [6.8, 7.0], [2.8, 14.0], [7.0, 14.0], [8.5, 11.0]])],

    # Chữ số nét uốn tự nhiên
    '0': [make_oval(cx=5.0, top_y=2.0, bot_y=14.0, rx=3.0, n=10)],
    '1': [np.array([[3.0, 5.0], [5.5, 2.0], [5.5, 14.0]]), np.array([[2.5, 14.0], [8.5, 14.0]])],
    '2': [
        bz(np.array([2.0, 5.0]), np.array([5.0, 1.8]), np.array([8.0, 3.8]), np.array([8.0, 7.0]), n=8),
        np.array([[8.0, 7.0], [2.0, 14.0], [8.5, 14.0]])
    ],
    '3': [
        bz(np.array([2.0, 3.0]), np.array([7.5, 2.0]), np.array([7.5, 7.5]), np.array([4.5, 8.0]), n=8),
        bz(np.array([4.5, 8.0]), np.array([8.2, 8.5]), np.array([8.2, 14.2]), np.array([2.0, 13.0]), n=8)
    ],
    '4': [np.array([[6.5, 14.0], [6.5, 2.0], [1.5, 10.0], [9.0, 10.0]])],
    '5': [
        np.array([[7.5, 2.0], [2.5, 2.0], [2.5, 7.0]]),
        bz(np.array([2.5, 7.0]), np.array([8.0, 7.0]), np.array([8.0, 14.2]), np.array([2.0, 13.0]), n=10)
    ],
    '6': [
        bz(np.array([6.5, 3.0]), np.array([3.0, 6.0]), np.array([2.0, 10.0]), np.array([4.5, 14.0]), n=8),
        make_oval(cx=4.8, top_y=8.0, bot_y=14.0, rx=2.6, n=8)
    ],
    '7': [np.array([[1.5, 2.0], [8.5, 2.0], [4.0, 14.0]]), np.array([[2.8, 8.0], [6.5, 8.0]])],
    '8': [
        make_oval(cx=5.0, top_y=2.0, bot_y=8.0, rx=2.5, n=8),
        make_oval(cx=5.0, top_y=8.0, bot_y=14.0, rx=2.8, n=8)
    ],
    '9': [
        make_oval(cx=5.0, top_y=2.0, bot_y=8.5, rx=2.6, n=8),
        bz(np.array([7.5, 6.0]), np.array([7.5, 11.0]), np.array([5.5, 14.2]), np.array([2.5, 13.0]), n=8)
    ],

    # Ký tự dấu câu
    '.': [np.array([[2.5, 13.5], [2.8, 13.5]])],
    ',': [np.array([[2.8, 13.5], [1.8, 16.0]])],
    '!': [np.array([[2.8, 2.0], [2.8, 10.0]]), np.array([[2.8, 13.5], [3.0, 13.5]])],
    '?': [
        bz(np.array([2.0, 4.0]), np.array([4.5, 1.8]), np.array([7.0, 3.8]), np.array([5.5, 7.5]), n=8),
        np.array([[5.5, 7.5], [3.8, 9.0], [3.8, 11.0]]),
        np.array([[3.8, 13.5], [4.0, 13.5]])
    ],
    ':': [np.array([[2.8, 6.5], [3.0, 6.5]]), np.array([[2.8, 13.5], [3.0, 13.5]])],
    ';': [np.array([[2.8, 6.5], [3.0, 6.5]]), np.array([[2.8, 13.5], [1.8, 15.5]])],
    '-': [np.array([[1.5, 9.5], [6.0, 9.5]])],
    '_': [np.array([[0.0, 15.5], [8.5, 15.5]])],
    '/': [np.array([[1.0, 15.0], [8.0, 2.0]])],
    '(': [bz(np.array([5.5, 1.0]), np.array([2.2, 6.0]), np.array([2.2, 11.0]), np.array([5.5, 16.0]), n=8)],
    ')': [bz(np.array([2.5, 1.0]), np.array([5.8, 6.0]), np.array([5.8, 11.0]), np.array([2.5, 16.0]), n=8)],
    '"': [np.array([[2.0, 2.0], [2.0, 5.0]]), np.array([[4.5, 2.0], [4.5, 5.0]])],
    "'": [np.array([[2.5, 2.0], [2.0, 5.0]])],
    '+': [np.array([[2.0, 9.0], [8.0, 9.0]]), np.array([[5.0, 6.0], [5.0, 12.0]])],
    '=': [np.array([[2.0, 7.0], [8.0, 7.0]]), np.array([[2.0, 11.0], [8.0, 11.0]])],
}

# ----------------------------- Kích thước & Trọng tâm Proportional -----------------------------
# Triệt tiêu cảm giác rời rạc như máy gõ typewriter
GLYPH_WIDTHS = {
    'i': 5.5, 'l': 6.8, 'j': 5.5, 't': 6.0, 'f': 5.8, 'r': 8.2, 's': 7.8,
    'c': 7.4, 'e': 7.6, 'o': 7.5, 'a': 7.8, 'd': 8.4, 'g': 8.8, 'q': 7.8,
    'u': 7.8, 'v': 8.0, 'n': 7.8, 'h': 7.8, 'k': 8.2, 'p': 8.0, 'b': 7.8,
    'x': 8.0, 'y': 8.8, 'z': 7.5, 'w': 11.2, 'm': 11.5,
    'I': 5.5, 'J': 7.0, 'L': 7.5, 'T': 8.5, 'F': 8.0, 'E': 8.2, 'M': 11.5, 'W': 11.5,
    '.': 3.5, ',': 3.5, '!': 3.5, ':': 3.5, ';': 3.5, "'": 3.0, '"': 5.0,
    '-': 5.5, '?': 6.5, '(': 5.5, ')': 5.5, ' ': 4.5,
}
DEFAULT_WIDTH = 8.5

# Trọng tâm trục X để căn chỉnh dấu chuẩn xác trên từng nguyên âm
GLYPH_CENTERS = {
    'a': 4.8, 'c': 4.8, 'e': 4.8, 'i': 3.2, 'o': 4.8, 'u': 4.8, 'y': 4.8,
    'A': 5.5, 'E': 5.5, 'I': 4.0, 'O': 5.5, 'U': 5.5, 'Y': 5.5,
}
DEFAULT_CENTER = 4.8

# Dấu gạch ngang đ / Đ chuẩn vị trí cắt qua giữa thân sổ
STROKE_D_BAR = np.array([[5.2, 4.2], [8.8, 4.2]])
STROKE_CAP_D_BAR = np.array([[0.2, 7.5], [4.2, 7.5]])


# ----------------------------- Thuật Toán Sinh Dấu Chống Dính (Anti-collision) -----------------------------

def generate_accents(base_char, accents, cx):
    """
    Sinh các nét dấu Tiếng Việt (Single-stroke Accents) căn chỉnh tự động:
    - Tránh va chạm 100% giữa dấu thanh và mũ nón/trăng/móc (Anti-collision).
    - Căn giữa chính xác theo trọng tâm nguyên âm cx.
    - Hỗ trợ cả chữ hoa (tự nâng chiều cao) và chữ thường.
    - Kích thước nhỏ gọn, thanh thoát, vừa vặn tự nhiên với chữ (fit với chữ).
    """
    strokes = []
    is_upper = base_char.isupper()
    # Nâng độ cao dấu nếu là chữ hoa (cap-height = 2 so với x-height = 7)
    y_shift = -5.0 if is_upper else 0.0

    has_non = '\u0302' in accents    # nón â, ê, ô
    has_trang = '\u0306' in accents  # trăng ă
    has_moc = '\u031b' in accents    # móc ơ, ư
    has_stacked_base = has_non or has_trang

    # 1. Dấu định dạng nguyên âm (nón, trăng, móc)
    if has_non:
        # Nón thanh thoát nhỏ gọn (rộng 3.2, cao 2.1), cách đỉnh chữ 2.4 đơn vị
        non_stroke = np.array([[cx - 1.6, 4.6 + y_shift], [cx, 2.5 + y_shift], [cx + 1.6, 4.6 + y_shift]])
        strokes.append(non_stroke)

    if has_trang:
        # Trăng uốn cong tròn lòng máng mềm mại (rộng 3.2, cao 1.3)
        trang_stroke = bz(np.array([cx - 1.6, 2.8 + y_shift]), np.array([cx - 0.9, 4.6 + y_shift]),
                          np.array([cx + 0.9, 4.6 + y_shift]), np.array([cx + 1.6, 2.8 + y_shift]), n=6)
        strokes.append(trang_stroke)

    if has_moc:
        # Móc cong tròn mềm mại chuẩn tiểu học gắn góc trên bên phải của o hoặc u
        m1 = bz(np.array([cx + 1.8, 7.0 + y_shift]), np.array([cx + 2.7, 6.4 + y_shift]),
                np.array([cx + 3.1, 5.2 + y_shift]), np.array([cx + 2.8, 4.5 + y_shift]), n=6)
        m2 = bz(np.array([cx + 2.8, 4.5 + y_shift]), np.array([cx + 2.6, 4.0 + y_shift]),
                np.array([cx + 2.0, 4.1 + y_shift]), np.array([cx + 1.9, 4.7 + y_shift]), n=6)
        strokes.append(np.vstack([m1, m2[1:]]))

    # 2. Dấu thanh điệu (sắc, huyền, hỏi, ngã, nặng)
    for acc in accents:
        if acc == '\u0323':
            # Dấu nặng: chấm tròn nhỏ dưới baseline (y=14)
            if base_char in ('y', 'Y'):
                strokes.append(np.array([[cx + 2.0, 15.6], [cx + 2.3, 15.6]]))
            else:
                strokes.append(np.array([[cx - 0.2, 15.6], [cx + 0.3, 15.6]]))

        elif acc == '\u0301':
            # Dấu sắc
            if has_stacked_base:
                # Nằm chếch trên sườn phải của mũ nón/trăng, nhỏ gọn
                s = np.array([[cx + 0.8, 2.2 + y_shift], [cx + 2.0, 0.4 + y_shift]])
            elif has_moc:
                # Nằm chếch trái tâm một chút để nhường chỗ cho móc bên phải
                s = np.array([[cx - 1.4, 4.6 + y_shift], [cx + 0.6, 2.4 + y_shift]])
            else:
                s = np.array([[cx - 0.9, 4.6 + y_shift], [cx + 1.1, 2.4 + y_shift]])
            strokes.append(s)

        elif acc == '\u0300':
            # Dấu huyền
            if has_stacked_base:
                # Nằm chếch trên sườn trái của mũ nón/trăng, nhỏ gọn
                s = np.array([[cx - 0.8, 2.2 + y_shift], [cx - 2.0, 0.4 + y_shift]])
            elif has_moc:
                s = np.array([[cx + 0.4, 4.6 + y_shift], [cx - 1.6, 2.4 + y_shift]])
            else:
                s = np.array([[cx + 0.9, 4.6 + y_shift], [cx - 1.1, 2.4 + y_shift]])
            strokes.append(s)

        elif acc == '\u0309':
            # Dấu hỏi: uốn móc cong nhỏ gọn
            if has_stacked_base:
                s = np.array([[cx - 0.3, 1.2 + y_shift], [cx - 0.7, 0.2 + y_shift],
                              [cx + 0.5, -0.2 + y_shift], [cx + 0.7, 0.6 + y_shift], [cx, 1.0 + y_shift]])
            elif has_moc:
                s = np.array([[cx - 1.0, 4.6 + y_shift], [cx - 1.5, 3.0 + y_shift],
                              [cx + 0.2, 2.5 + y_shift], [cx + 0.3, 3.4 + y_shift], [cx - 0.5, 4.1 + y_shift]])
            else:
                s = np.array([[cx - 0.4, 4.6 + y_shift], [cx - 0.9, 3.0 + y_shift],
                              [cx + 0.7, 2.5 + y_shift], [cx + 0.8, 3.4 + y_shift], [cx, 4.1 + y_shift]])
            strokes.append(s)

        elif acc == '\u0303':
            # Dấu ngã: lượn sóng nhỏ gọn
            if has_stacked_base:
                s = bz(np.array([cx - 1.2, 1.4 + y_shift]), np.array([cx - 0.4, 0.4 + y_shift]),
                       np.array([cx + 0.4, 1.8 + y_shift]), np.array([cx + 1.2, 0.9 + y_shift]), n=6)
            elif has_moc:
                s = bz(np.array([cx - 2.0, 3.8 + y_shift]), np.array([cx - 1.2, 2.8 + y_shift]),
                       np.array([cx - 0.2, 4.2 + y_shift]), np.array([cx + 0.6, 3.2 + y_shift]), n=6)
            else:
                s = bz(np.array([cx - 1.3, 3.8 + y_shift]), np.array([cx - 0.5, 2.7 + y_shift]),
                       np.array([cx + 0.5, 4.3 + y_shift]), np.array([cx + 1.3, 3.2 + y_shift]), n=6)
            strokes.append(s)

    return strokes


# ----------------------------- Bộ Phân Loại & Nối Nét Chọn Lọc (Selective Ligature Engine) -----------------------------

# Phân loại điểm đón nét (Entry) và thoát nét (Exit) theo giải phẫu học chữ viết tay người
ENTRY_TYPES = {
    'i': 'mid', 'u': 'mid', 'm': 'mid', 'n': 'mid', 't': 'mid',
    'p': 'mid', 'r': 'baseline', 's': 'baseline', 'v': 'mid', 'w': 'mid', 'y': 'mid',
    'e': 'mid',
    'a': 'oval', 'd': 'oval', 'g': 'oval', 'o': 'oval', 'q': 'oval', 'c': 'oval',
    'b': 'ascender', 'h': 'ascender', 'k': 'ascender', 'l': 'ascender',
    'x': 'none', 'z': 'none', 'f': 'none'
}

EXIT_TYPES = {
    'a': 'baseline_hook', 'c': 'baseline_hook', 'd': 'baseline_hook',
    'e': 'baseline_hook', 'h': 'baseline_hook', 'i': 'baseline_hook',
    'k': 'baseline_hook', 'l': 'baseline_hook', 'm': 'baseline_hook',
    'n': 'baseline_hook', 't': 'baseline_hook', 'u': 'baseline_hook',
    'p': 'baseline_hook', 'r': 'baseline_hook', 's': 'baseline_hook',
    'b': 'top_flick', 'o': 'top_flick', 'v': 'top_flick', 'w': 'top_flick',
    'g': 'descender_loop', 'y': 'descender_loop',
    'q': 'none', 'x': 'baseline_hook', 'z': 'none', 'f': 'none'
}


def can_ligature(prev_char, curr_char):
    """
    Quy tắc sinh học mô phỏng bàn tay người viết chữ Tiếng Việt:
    - Chỉ nối nét khi tự nhiên, thuận chiều di chuyển của cổ tay (vd: t-i, i-e, e-n, a-y, t-r, s-e...).
    - Chủ động NHẤC BÚT (Pen Lift) khi chuẩn bị viết chữ tròn oval (a, d, g, o, q, c) hoặc nét khuyết trên (b, h, k, l)
      hoặc sau ký tự không có móc thoát thuận lợi (x, z, q) -> TRIỆT TIÊU 100% HIỆN TƯỢNG 'DƯ NÉT MỰC'.
    """
    if not (prev_char.isalpha() and prev_char.islower() and curr_char.isalpha() and curr_char.islower()):
        return False

    ex = EXIT_TYPES.get(prev_char, 'none')
    en = ENTRY_TYPES.get(curr_char, 'none')

    # 1. Nếu chữ sau là chữ tròn (oval) -> Nhấc bút bắt đầu từ góc 2 giờ, tránh nét gạch chéo bụng chữ
    if en == 'oval':
        return False

    # 2. Nếu chữ sau là nét khuyết trên (ascender) -> Nhấc bút để đặt bút từ đỉnh kéo xuống
    if en == 'ascender':
        return False

    # 3. Nếu chữ trước không có móc thoát thuận lợi (none) -> Nhấc bút
    if ex == 'none':
        return False

    # 4. Thoát móc chân (baseline_hook) nối sang đón nét thân giữa (mid) hoặc nét đón chân (baseline: r, s)
    if ex == 'baseline_hook' and en in ('mid', 'baseline'):
        return True

    # 5. Thoát móc trên (top_flick) nối sang đón nét thân giữa (mid) hoặc e
    if ex == 'top_flick' and en in ('mid', 'e'):
        return True

    # 6. Thoát móc khuyết dưới (descender_loop: g, y) lượn lên nối tiếp nét đón thân (mid, e)
    if ex == 'descender_loop' and en in ('mid', 'e'):
        return True

    return False


# ----------------------------- Cấu Hình Phong Cách & Font -----------------------------

STYLE_CONFIGS = {
    "hand_hocsinh": {
        "name": "Chữ Học Sinh",
        "slant": 0.0,          # nét đứng nắn nót
        "jitter_amp": 0.015,    # rung tay sinh học rất mịn, nét tròn trịa
        "drift_amp": 0.12,      # lượn dòng rất ít
        "char_spacing": 1.0,
    },
    "hand_nguoilon": {
        "name": "Chữ Thảo Nghiêng",
        "slant": 0.20,         # nghiêng ~11 độ tự nhiên
        "jitter_amp": 0.035,    # rung tay vừa phải, mượt mà
        "drift_amp": 0.25,      # dòng lượn sóng nhẹ
        "char_spacing": 1.0,
    },
    "hand_thuphap": {
        "name": "Chữ Thư Pháp",
        "slant": 0.15,
        "jitter_amp": 0.045,    # nét phóng khoáng
        "drift_amp": 0.35,      # lượn sóng bổng trầm
        "char_spacing": 1.1,
    },
    "hand_chukinhanh": {
        "name": "Chữ Ký Tên",
        "slant": 0.32,         # nghiêng mạnh ~18 độ
        "jitter_amp": 0.060,
        "drift_amp": 0.20,
        "char_spacing": 0.95,
    },
}

FONT_CONFIGS = {
    "oly": {
        "aspect_y": 1.0,
        "slant_add": 0.0,
        "thanhdam": False,
        "ligature": False,
        "flourish": False,
    },
    "thanhdam": {
        "aspect_y": 1.04,
        "slant_add": 0.08,
        "thanhdam": True,      # Nhân đôi nét sổ mô phỏng ngòi bút mài lá tre
        "ligature": False,
        "flourish": False,
    },
    "thuphap": {
        "aspect_y": 1.25,      # Kéo dài trục Y thanh thoát
        "slant_add": 0.05,
        "thanhdam": True,
        "flourish": True,      # Móc vát đuôi thư pháp
        "ligature": False,
    },
    "cursive": {
        "aspect_y": 0.96,
        "slant_add": 0.15,     # Nghiêng thêm kiểu chữ thảo
        "thanhdam": False,
        "ligature": True,      # Nối nét liền mạch 0 pen lift trong từ
        "flourish": False,
    },
    "custom": {
        "aspect_y": 1.0,
        "slant_add": 0.0,
        "thanhdam": False,
        "ligature": False,
        "flourish": False,
    },
}


def apply_bio_variation(stroke, slant=0.0, jitter_amp=0.0, drift_y=0.0):
    """
    Áp dụng các lớp biến dạng sinh học (Bio-mimetic Variation):
    1. Slant affine shear: x' = x + (baseline - y) * slant
    2. Baseline drift: y' = y + drift_y
    3. Micro-jitter: Nhiễu rung cơ học tự nhiên lọc thông thấp (ARMA), loại bỏ hoàn toàn răng cưa/gãy nét
    """
    out = stroke.copy().astype(float)
    if slant != 0.0:
        # Nghiêng về phía trước quanh trục baseline (y=14)
        out[:, 0] += (14.0 - out[:, 1]) * slant
    out[:, 1] += drift_y
    if jitter_amp > 0 and len(out) > 1:
        raw_noise = np.random.normal(0, jitter_amp, out.shape)
        # Bộ lọc làm mịn chuyển động bàn tay (Autoregressive low-pass filter)
        smooth_noise = np.zeros_like(raw_noise)
        smooth_noise[0] = raw_noise[0]
        alpha = 0.35
        for i in range(1, len(out)):
            smooth_noise[i] = smooth_noise[i - 1] * (1.0 - alpha) + raw_noise[i] * alpha
        out += smooth_noise
    return out


def text_to_strokes(text, font="oly", style="hand_hocsinh", font_size_mm=7.0, line_spacing_mm=13.0,
                    paper_size_mm=(210.0, 297.0), margin_mm=20.0):
    """
    Biến đổi văn bản tiếng Việt thành mảng các nét vẽ mm (List of ndarray (N, 2)).
    Hỗ trợ xuống dòng tự động, căn lề, proportional kerning, nối nét cursive và chống dính dấu.
    """
    cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS["hand_hocsinh"])
    f_cfg = FONT_CONFIGS.get(font, FONT_CONFIGS["oly"])

    slant = cfg["slant"] + f_cfg["slant_add"]
    jitter = cfg["jitter_amp"] * (font_size_mm / 7.0)
    drift_max = cfg["drift_amp"] * (font_size_mm / 7.0)

    paper_w, paper_h = paper_size_mm
    scale = font_size_mm / 14.0
    scale_y = scale * f_cfg["aspect_y"]
    space_w = 4.8 * scale * cfg["char_spacing"]

    strokes = []
    curr_x = margin_mm
    curr_y = margin_mm + font_size_mm

    words = text.split(" ")
    word_idx = 0

    for word in words:
        if word == "":
            curr_x += space_w
            continue

        # Xử lý ký tự xuống dòng thủ công \n trong từ
        sub_words = word.split("\n")
        for sub_i, sub_w in enumerate(sub_words):
            if sub_i > 0:
                curr_x = margin_mm
                curr_y += line_spacing_mm
                if curr_y > paper_h - margin_mm:
                    break

            # Chuẩn hóa NFD để bóc tách dấu thanh tiếng Việt
            decomposed = unicodedata.normalize('NFD', sub_w)
            char_queue = []
            current_group = []
            for ch in decomposed:
                if unicodedata.combining(ch):
                    current_group.append(ch)
                else:
                    if current_group:
                        char_queue.append(current_group)
                    current_group = [ch]
            if current_group:
                char_queue.append(current_group)

            # Kiểm tra tràn dòng (Word wrap) theo kích thước proportional
            est_w = sum(GLYPH_WIDTHS.get(g[0], DEFAULT_WIDTH) for g in char_queue) * scale * cfg["char_spacing"]
            if curr_x + est_w > paper_w - margin_mm and curr_x > margin_mm:
                curr_x = margin_mm
                curr_y += line_spacing_mm
                if curr_y > paper_h - margin_mm:
                    break

            # Lượn sóng dòng kẻ (Baseline drift)
            drift_y = math.sin(curr_x * 0.05 + word_idx * 0.4) * drift_max

            word_base_strokes = []
            word_secondary_strokes = []
            last_char = None

            for char_idx, group in enumerate(char_queue):
                base_char = group[0]
                accents = group[1:]

                # Xử lý chữ đ/Đ
                is_d_stroke = False
                if base_char == 'đ':
                    base_char = 'd'
                    is_d_stroke = True
                elif base_char == 'Đ':
                    base_char = 'D'
                    is_d_stroke = True

                char_rhythm = 1.0 + 0.02 * math.sin(word_idx * 1.7 + char_idx * 2.3)
                char_scale_x = scale * char_rhythm * cfg["char_spacing"]
                w_char = GLYPH_WIDTHS.get(base_char, DEFAULT_WIDTH) * char_scale_x
                cx = GLYPH_CENTERS.get(base_char, DEFAULT_CENTER)

                raw_s = GLYPHS.get(base_char, GLYPHS.get('?'))
                # Tọa độ thực tế mm của từng nét trong glyph
                scaled_s = [s.astype(float) * np.array([char_scale_x, scale_y]) + np.array([curr_x, curr_y - 14.0 * scale]) for s in raw_s]

                # Tách nét chính và nét phụ (dấu chấm i, j; gạch ngang t, f)
                if base_char in ('i', 'j'):
                    prim_strokes = [scaled_s[0]]
                    if len(accents) == 0:
                        word_secondary_strokes.append(scaled_s[1])
                elif base_char in ('t', 'f'):
                    prim_strokes = [scaled_s[0]]
                    word_secondary_strokes.append(scaled_s[1])
                else:
                    prim_strokes = scaled_s

                # Xử lý nối nét chọn lọc mô phỏng tay người (Selective Ligature)
                if f_cfg["ligature"] and last_char is not None and len(word_base_strokes) > 0 and can_ligature(last_char, base_char):
                    p_exit = word_base_strokes[-1][-1]
                    p_entry = prim_strokes[0][0]
                    # Cầu nối Bézier uốn mềm giữa điểm thoát nét trước và điểm đón nét sau theo hướng tiếp tuyến tự nhiên
                    last_stroke = word_base_strokes[-1]
                    next_stroke = prim_strokes[0]
                    v_exit = (last_stroke[-1] - last_stroke[-2]) if len(last_stroke) >= 2 else np.array([0.5 * scale, 0.0])
                    v_entry = (next_stroke[1] - next_stroke[0]) if len(next_stroke) >= 2 else np.array([0.5 * scale, 0.0])

                    dist = float(np.linalg.norm(p_entry - p_exit))
                    factor = min(0.6 * scale, dist * 0.35)
                    c1 = p_exit + v_exit * (factor / (float(np.linalg.norm(v_exit)) + 1e-6))
                    c2 = p_entry - v_entry * (factor / (float(np.linalg.norm(v_entry)) + 1e-6))
                    bridge = bz(p_exit, c1, c2, p_entry, n=6)
                    merged = np.vstack([word_base_strokes[-1], bridge[1:-1], prim_strokes[0]])
                    word_base_strokes[-1] = merged
                    if len(prim_strokes) > 1:
                        word_base_strokes.extend(prim_strokes[1:])
                else:
                    word_base_strokes.extend(prim_strokes)

                # Nét thanh đậm (thanhdam)
                if f_cfg["thanhdam"]:
                    p_first = prim_strokes[0]
                    if len(p_first) >= 2 and (p_first[-1, 1] - p_first[0, 1] > 1.2 * scale):
                        offset_s = p_first.copy().astype(float)
                        offset_s[:, 0] += 0.22
                        word_secondary_strokes.append(offset_s)

                # Nét thư pháp móc đuôi chữ cuối từ
                if f_cfg["flourish"] and char_idx == len(char_queue) - 1:
                    last_pt = prim_strokes[-1][-1]
                    hook = np.array([last_pt, last_pt + np.array([0.7 * scale, -1.4 * scale])])
                    word_secondary_strokes.append(hook)

                # Gạch ngang đ/Đ
                if is_d_stroke:
                    d_bar = STROKE_D_BAR if base_char == 'd' else STROKE_CAP_D_BAR
                    bar_scaled = d_bar.astype(float) * np.array([char_scale_x, scale_y])
                    word_secondary_strokes.append(bar_scaled + np.array([curr_x, curr_y - 14.0 * scale]))

                # Dấu thanh chống va chạm
                if accents:
                    acc_list = generate_accents(base_char, accents, cx)
                    for acc_s in acc_list:
                        acc_scaled = acc_s.astype(float) * np.array([char_scale_x, scale_y])
                        acc_placed = acc_scaled + np.array([curr_x, curr_y - 14.0 * scale])
                        word_secondary_strokes.append(acc_placed)

                last_char = base_char if (base_char.isalpha() and base_char.islower()) else None
                curr_x += w_char

            # Gom nét từ và áp dụng biến thiên sinh học (Bio-mimetic Variation)
            for s in word_base_strokes:
                strokes.append(apply_bio_variation(s, slant=slant, jitter_amp=jitter, drift_y=drift_y))
            for s in word_secondary_strokes:
                strokes.append(apply_bio_variation(s, slant=slant, jitter_amp=jitter, drift_y=drift_y))

            # Khoảng cách giữa các từ
            curr_x += space_w * np.random.uniform(0.95, 1.05)
            word_idx += 1

    return strokes


def generate_handwriting_svg(text, font="oly", style="hand_hocsinh", target_paper_size_mm=(210.0, 297.0),
                             font_size_mm=7.0, line_spacing_mm=13.0, skew_angle_deg=0.0):
    """
    Sinh file SVG chữ viết tay hoàn chỉnh, chạy qua bộ tối ưu hóa path_optimizer
    (Catmull-Rom Bézier smoothing, Auto-deskew).
    Giữ thứ tự viết tự nhiên từ trái sang phải, từ trên xuống dưới.
    """
    try:
        from path_optimizer import build_svg, compute_svg_metrics
    except ImportError:
        from backend.path_optimizer import build_svg, compute_svg_metrics

    strokes = text_to_strokes(
        text, font=font, style=style, font_size_mm=font_size_mm,
        line_spacing_mm=line_spacing_mm, paper_size_mm=target_paper_size_mm
    )

    if not strokes:
        strokes = [np.array([[20.0, 20.0], [21.0, 20.0]])]

    # Giữ nguyên thứ tự viết tự nhiên (Natural Reading Order) theo từng từ
    # Tránh 2-Opt TSP đảo chiều nét bút hoặc nhảy lộn xộn giữa các từ
    order = list(range(len(strokes)))
    rev = [False] * len(strokes)

    # Xuất SVG với Catmull-Rom to Cubic Bézier smoothing mượt mà
    scale = 1.0
    offset = (0.0, 0.0)
    svg_content, is_within_bounds = build_svg(
        strokes, order, rev, scale, offset, target_paper_size_mm,
        stroke_width_mm=0.35, smooth=True, skew_angle_deg=skew_angle_deg
    )

    metrics = compute_svg_metrics(strokes, order, rev, scale=1.0, optimize_time_ms=1.0, skew_angle_deg=skew_angle_deg)
    return svg_content, metrics, is_within_bounds


# ----------------------------- Runnable Self-Check -----------------------------

def _run_self_check():
    """Kiểm tra tự động module viết thư tay với đầy đủ 4 font."""
    text_sample = "Kính gửi thầy cô kính yêu! Nhân ngày 20/11."

    # Kiểm tra 4 font
    font_results = {}
    for font_id in ["oly", "thanhdam", "thuphap", "cursive"]:
        s = text_to_strokes(text_sample, font=font_id, style="hand_hocsinh")
        font_results[font_id] = len(s)
        assert len(s) > 15, f"Font {font_id}: Số lượng nét phải > 15, nhận {len(s)}"

    # Thanhdam phải có nhiều nét hơn oly do nét sổ kép
    assert font_results["thanhdam"] > font_results["oly"], "Thanhdam phai nhan doi net so"

    # Cursive phải gom nét liền mạch (số lần nhấc bút ít hơn hẳn oly)
    assert font_results["cursive"] < font_results["oly"], f"Cursive phai gop net lien mach: {font_results['cursive']} < {font_results['oly']}"

    # Kiểm tra tiếng Việt có dấu
    for char in ['ế', 'ậ', 'đ', 'ờ', 'ũ']:
        s = text_to_strokes(char)
        assert len(s) >= 2, f"Ký tự {char} phải có ít nhất 2 nét (gốc + dấu)"

    svg, metrics, in_bounds = generate_handwriting_svg(text_sample, font="cursive", style="hand_nguoilon", skew_angle_deg=2.5)
    assert "<svg" in svg and "C" in svg, "SVG phải hợp lệ và chứa lệnh Bézier C"
    assert in_bounds, "Tọa độ phải nằm trong khổ giấy"
    print(f"[HANDWRITING SELF-CHECK PASS] Kiểm tra thành công 4 fonts: {font_results} | SVG Cursive: {metrics['total_path_length_mm']:.1f}mm | Deskew OK")


if __name__ == "__main__":
    _run_self_check()

