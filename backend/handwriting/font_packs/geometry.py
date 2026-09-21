import numpy as np

# ----------------------------- Bộ Sinh Nét Cong Bézier Hữu Cơ Chuẩn Hình Học -----------------------------

def bz(p0, c1, c2, p3, n=8):
    """Lấy mẫu n điểm trên một đoạn Cubic Bézier bậc ba.

    Hàm này không tự bảo đảm bậc liên tục giữa nhiều đoạn Bézier.
    """
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
