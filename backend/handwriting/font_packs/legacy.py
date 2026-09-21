import numpy as np

from .geometry import (
    bz,
    make_oval,
    make_hook_stem,
    make_ascender_loop,
    make_descender_loop,
    make_arch,
)

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
    # e: Nét cong bắt đầu từ giữa dòng lượn lên x-height tạo vòm tròn xoe hoàn hảo, lưng và móc nối tròn mượt
    'e': [np.vstack([
        bz(np.array([2.0, 11.0]), np.array([3.4, 10.6]), np.array([5.2, 10.0]), np.array([6.6, 8.8]), n=6),
        bz(np.array([6.6, 8.8]), np.array([6.8, 7.8]), np.array([5.82, 7.0]), np.array([4.6, 7.0]), n=7)[1:],
        bz(np.array([4.6, 7.0]), np.array([3.38, 7.0]), np.array([2.4, 8.57]), np.array([2.4, 10.5]), n=8)[1:],
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
    # h: Nét khuyết trên + nét móc 2 đầu thon gọn
    'h': [
        make_ascender_loop(x_stem=2.0, top_y=0.5, bot_y=14.0, loop_w=2.2),
        make_arch(x_left=2.0, x_right=5.8, top_y=7.0, bot_y=14.0, hook_w=2.0)
    ],
    # i: Nét sổ thẳng từ x-height xuống baseline có móc ngược + dấu chấm (bỏ nét móc hất đầu để nối liền mạch)
    'i': [
        make_hook_stem(x_stem=3.2, top_y=7.0, bot_y=14.0, hook_w=2.0, hook_h=2.8),
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
    # t: Nét sổ thẳng từ đỉnh 1.5 đv (y=3.5) xuống baseline có móc ngược + gạch ngang ngắn (bỏ nét móc hất đầu)
    't': [
        make_hook_stem(x_stem=3.2, top_y=3.5, bot_y=14.0, hook_w=2.0, hook_h=2.8),
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
