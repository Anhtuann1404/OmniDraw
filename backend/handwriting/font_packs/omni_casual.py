import numpy as np

from .geometry import bz
from .legacy import (
    GLYPHS,
    GLYPH_WIDTHS,
    GLYPH_CENTERS,
)

# Omni Casual v1: biến thể nét đơn tối ưu cho robot, lấy cảm hứng từ chữ viết
# tay đời thường. Các ký tự chưa được vẽ riêng tiếp tục dùng hình học legacy để
# bảo đảm đầy đủ nội dung; metadata của font pack công khai rõ phạm vi này.
OMNI_CASUAL_V1_PUNCTUATION = (
    ".", ",", "!", "?", ":", ";",
    "-", "–", "—",
    "'", '"',
    "‘", "’", "“", "”",
    "(", ")", "/", "…",
)
OMNI_CASUAL_CUSTOM_CHARS = (
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
    "M", "N", "O", "P", "Q", "R",
    "S", "T", "U", "V", "W", "X", "Y", "Z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
) + OMNI_CASUAL_V1_PUNCTUATION
OMNI_CASUAL_GLYPHS = dict(GLYPHS)
OMNI_CASUAL_GLYPHS.update({
    "a": [np.vstack([
        bz(np.array([6.4, 8.4]), np.array([4.5, 6.6]), np.array([2.0, 7.6]), np.array([2.1, 11.0]), n=8),
        bz(np.array([2.1, 11.0]), np.array([2.2, 14.0]), np.array([5.2, 14.7]), np.array([6.3, 11.8]), n=8)[1:],
        bz(np.array([6.3, 11.8]), np.array([6.8, 10.2]), np.array([6.5, 9.0]), np.array([6.4, 8.4]), n=6)[1:],
        bz(np.array([6.4, 8.4]), np.array([6.2, 10.7]), np.array([6.2, 13.6]), np.array([8.1, 12.7]), n=7)[1:],
    ])],
    "b": [
        bz(np.array([2.2, 2.2]), np.array([2.1, 6.0]), np.array([2.1, 10.5]), np.array([2.2, 14.0]), n=10),
        np.vstack([
            bz(np.array([2.2, 7.8]), np.array([4.2, 6.9]), np.array([6.8, 7.6]), np.array([6.9, 10.5]), n=8),
            bz(np.array([6.9, 10.5]), np.array([7.0, 13.4]), np.array([4.5, 14.2]), np.array([2.2, 14.0]), n=8)[1:],
        ]),
    ],
    "c": [np.vstack([
        bz(np.array([6.2, 8.4]), np.array([5.5, 6.8]), np.array([2.4, 7.2]), np.array([2.0, 10.6]), n=8),
        bz(np.array([2.0, 10.6]), np.array([1.8, 13.4]), np.array([4.6, 14.3]), np.array([6.4, 12.8]), n=8)[1:],
    ])],
    "d": [
        np.vstack([
            bz(np.array([6.9, 2.2]), np.array([6.9, 6.0]), np.array([6.8, 10.5]), np.array([6.8, 13.8]), n=9),
            bz(np.array([6.8, 13.8]), np.array([6.8, 14.2]), np.array([7.3, 14.1]), np.array([7.8, 13.0]), n=5)[1:],
        ]),
        np.vstack([
            bz(np.array([6.8, 7.8]), np.array([4.5, 6.9]), np.array([2.2, 7.8]), np.array([2.0, 10.6]), n=8),
            bz(np.array([2.0, 10.6]), np.array([2.0, 13.4]), np.array([4.5, 14.2]), np.array([6.8, 13.8]), n=8)[1:],
        ]),
    ],
    "e": [np.vstack([
        bz(np.array([1.4, 11.0]), np.array([3.0, 10.8]), np.array([5.4, 10.4]), np.array([6.5, 9.2]), n=7),
        bz(np.array([6.5, 9.2]), np.array([6.0, 6.8]), np.array([2.2, 7.0]), np.array([2.0, 10.8]), n=8)[1:],
        bz(np.array([2.0, 10.8]), np.array([1.8, 14.0]), np.array([5.7, 15.0]), np.array([7.4, 12.5]), n=8)[1:],
    ])],
    "f": [
        np.vstack([
            bz(np.array([4.8, 2.6]), np.array([4.2, 2.0]), np.array([3.1, 2.0]), np.array([3.0, 3.8]), n=6),
            bz(np.array([3.0, 3.8]), np.array([2.9, 7.0]), np.array([3.0, 11.0]), np.array([3.0, 14.2]), n=9)[1:],
        ]),
        np.array([[1.5, 7.2], [4.5, 7.2]]),
    ],
    "g": [np.vstack([
        bz(np.array([6.3, 8.4]), np.array([4.6, 6.7]), np.array([2.0, 7.4]), np.array([2.1, 10.8]), n=8),
        bz(np.array([2.1, 10.8]), np.array([2.2, 14.0]), np.array([5.1, 14.6]), np.array([6.3, 11.7]), n=8)[1:],
        bz(np.array([6.3, 11.7]), np.array([6.8, 10.0]), np.array([6.5, 8.9]), np.array([6.3, 8.4]), n=6)[1:],
        bz(np.array([6.3, 8.4]), np.array([6.6, 12.0]), np.array([7.0, 17.8]), np.array([4.8, 18.7]), n=9)[1:],
        bz(np.array([4.8, 18.7]), np.array([3.2, 19.0]), np.array([2.2, 17.6]), np.array([3.1, 16.3]), n=7)[1:],
    ])],
    "h": [
        bz(np.array([2.3, 2.2]), np.array([2.0, 6.0]), np.array([2.1, 10.8]), np.array([2.2, 14.0]), n=11),
        np.vstack([
            bz(np.array([2.2, 10.5]), np.array([3.7, 7.2]), np.array([6.7, 7.0]), np.array([6.7, 10.4]), n=9),
            bz(np.array([6.7, 10.4]), np.array([6.7, 12.8]), np.array([6.8, 14.1]), np.array([8.2, 12.8]), n=7)[1:],
        ]),
    ],
    "i": [
        np.vstack([
            bz(np.array([3.0, 7.4]), np.array([2.9, 9.5]), np.array([3.0, 11.5]), np.array([3.0, 13.0]), n=7),
            bz(np.array([3.0, 13.0]), np.array([3.1, 14.1]), np.array([4.0, 14.1]), np.array([4.5, 13.0]), n=6)[1:],
        ]),
        np.array([[3.0, 4.3], [3.2, 4.3]]),
    ],
    "j": [
        np.vstack([
            bz(np.array([3.2, 7.4]), np.array([3.2, 11.0]), np.array([3.2, 14.5]), np.array([3.2, 17.0]), n=9),
            bz(np.array([3.2, 17.0]), np.array([3.2, 18.8]), np.array([2.2, 19.0]), np.array([1.4, 17.6]), n=7)[1:],
        ]),
        np.array([[3.2, 4.3], [3.4, 4.3]]),
    ],
    "k": [
        bz(np.array([2.4, 2.2]), np.array([2.3, 6.0]), np.array([2.3, 10.5]), np.array([2.4, 14.0]), n=10),
        np.vstack([
            bz(np.array([6.8, 7.4]), np.array([5.5, 7.8]), np.array([3.8, 9.4]), np.array([2.4, 10.5]), n=7),
            bz(np.array([2.4, 10.5]), np.array([3.8, 11.2]), np.array([5.8, 12.8]), np.array([7.2, 14.0]), n=7)[1:],
        ]),
    ],
    "l": [np.vstack([
        bz(np.array([2.4, 2.2]), np.array([2.3, 5.8]), np.array([2.3, 9.8]), np.array([2.4, 12.8]), n=10),
        bz(np.array([2.4, 12.8]), np.array([2.5, 14.1]), np.array([4.0, 14.2]), np.array([4.8, 12.8]), n=7)[1:],
    ])],
    "m": [
        bz(np.array([2.0, 7.3]), np.array([2.0, 9.5]), np.array([2.1, 12.2]), np.array([2.2, 13.8]), n=8),
        bz(np.array([2.2, 10.2]), np.array([3.4, 6.8]), np.array([6.2, 6.8]), np.array([6.2, 13.8]), n=10),
        bz(np.array([6.2, 10.3]), np.array([7.5, 6.8]), np.array([10.1, 6.9]), np.array([11.5, 12.8]), n=10),
    ],
    "n": [
        bz(np.array([2.0, 7.3]), np.array([2.0, 9.6]), np.array([2.1, 12.3]), np.array([2.2, 13.8]), n=8),
        np.vstack([
            bz(np.array([2.2, 10.2]), np.array([3.5, 6.8]), np.array([6.5, 6.8]), np.array([6.5, 10.4]), n=8),
            bz(np.array([6.5, 10.4]), np.array([6.5, 12.9]), np.array([6.6, 14.2]), np.array([8.0, 12.8]), n=7)[1:],
        ]),
    ],
    "o": [np.vstack([
        bz(np.array([4.5, 7.1]), np.array([3.0, 7.1]), np.array([2.0, 8.8]), np.array([2.0, 10.6]), n=7),
        bz(np.array([2.0, 10.6]), np.array([2.0, 13.2]), np.array([3.6, 14.2]), np.array([5.2, 14.1]), n=7)[1:],
        bz(np.array([5.2, 14.1]), np.array([6.4, 13.9]), np.array([6.9, 12.2]), np.array([6.8, 10.4]), n=7)[1:],
        bz(np.array([6.8, 10.4]), np.array([6.7, 8.2]), np.array([5.8, 7.1]), np.array([4.5, 7.1]), n=7)[1:],
    ])],
    "p": [
        bz(np.array([2.2, 7.2]), np.array([2.1, 11.0]), np.array([2.2, 15.0]), np.array([2.3, 19.0]), n=11),
        np.vstack([
            bz(np.array([2.2, 7.6]), np.array([4.2, 6.9]), np.array([6.8, 7.6]), np.array([6.9, 10.5]), n=8),
            bz(np.array([6.9, 10.5]), np.array([7.0, 13.4]), np.array([4.5, 14.2]), np.array([2.2, 14.0]), n=8)[1:],
        ]),
    ],
    "q": [
        np.vstack([
            bz(np.array([6.8, 7.2]), np.array([6.8, 11.0]), np.array([6.8, 15.0]), np.array([6.8, 18.8]), n=10),
            bz(np.array([6.8, 18.8]), np.array([7.0, 19.1]), np.array([7.6, 18.6]), np.array([8.0, 17.5]), n=5)[1:],
        ]),
        np.vstack([
            bz(np.array([6.8, 7.6]), np.array([4.5, 6.9]), np.array([2.2, 7.8]), np.array([2.0, 10.6]), n=8),
            bz(np.array([2.0, 10.6]), np.array([2.0, 13.4]), np.array([4.5, 14.2]), np.array([6.8, 14.0]), n=8)[1:],
        ]),
    ],
    "r": [
        bz(np.array([2.0, 7.3]), np.array([2.0, 9.6]), np.array([2.1, 12.3]), np.array([2.2, 13.8]), n=8),
        bz(np.array([2.2, 10.0]), np.array([3.2, 7.0]), np.array([5.2, 6.8]), np.array([6.4, 8.3]), n=8),
    ],
    "s": [np.vstack([
        bz(np.array([6.7, 8.2]), np.array([5.3, 6.5]), np.array([2.2, 7.2]), np.array([2.2, 9.5]), n=8),
        bz(np.array([2.2, 9.5]), np.array([2.4, 11.0]), np.array([6.5, 10.5]), np.array([6.6, 12.3]), n=8)[1:],
        bz(np.array([6.6, 12.3]), np.array([6.5, 14.5]), np.array([3.0, 14.8]), np.array([1.8, 13.2]), n=8)[1:],
    ])],
    "t": [
        np.vstack([
            bz(np.array([3.0, 3.8]), np.array([2.9, 7.0]), np.array([3.0, 10.5]), np.array([3.0, 12.8]), n=8),
            bz(np.array([3.0, 12.8]), np.array([3.1, 14.1]), np.array([4.2, 14.1]), np.array([5.0, 13.0]), n=6)[1:],
        ]),
        np.array([[1.5, 6.8], [4.5, 6.8]]),
    ],
    "u": [np.vstack([
        bz(np.array([2.2, 7.4]), np.array([2.2, 9.6]), np.array([2.3, 11.6]), np.array([2.6, 13.0]), n=7),
        bz(np.array([2.6, 13.0]), np.array([3.0, 14.3]), np.array([5.4, 14.3]), np.array([5.8, 13.0]), n=7)[1:],
        bz(np.array([5.8, 13.0]), np.array([6.1, 11.6]), np.array([6.2, 9.6]), np.array([6.2, 7.5]), n=7)[1:],
        bz(np.array([6.2, 7.5]), np.array([6.4, 8.8]), np.array([6.6, 12.0]), np.array([7.6, 12.6]), n=6)[1:],
    ])],
    "v": [np.vstack([
        bz(np.array([2.0, 7.4]), np.array([2.6, 10.0]), np.array([3.4, 12.8]), np.array([4.1, 14.0]), n=8),
        bz(np.array([4.1, 14.0]), np.array([4.8, 13.9]), np.array([5.7, 10.2]), np.array([6.3, 7.5]), n=8)[1:],
        bz(np.array([6.3, 7.5]), np.array([6.7, 7.2]), np.array([7.2, 7.3]), np.array([7.5, 7.8]), n=5)[1:],
    ])],
    "w": [np.vstack([
        bz(np.array([1.8, 7.4]), np.array([2.2, 10.4]), np.array([2.8, 13.8]), np.array([3.8, 14.0]), n=7),
        bz(np.array([3.8, 14.0]), np.array([4.5, 13.9]), np.array([5.2, 10.2]), np.array([5.8, 8.4]), n=7)[1:],
        bz(np.array([5.8, 8.4]), np.array([6.4, 10.2]), np.array([7.0, 13.9]), np.array([8.0, 14.0]), n=7)[1:],
        bz(np.array([8.0, 14.0]), np.array([8.8, 13.9]), np.array([9.4, 9.8]), np.array([9.8, 7.4]), n=7)[1:],
        bz(np.array([9.8, 7.4]), np.array([10.1, 7.2]), np.array([10.4, 7.4]), np.array([10.6, 7.8]), n=5)[1:],
    ])],
    "x": [
        bz(np.array([2.2, 7.4]), np.array([3.2, 9.4]), np.array([5.4, 12.0]), np.array([6.4, 14.0]), n=8),
        bz(np.array([6.4, 7.4]), np.array([5.4, 9.4]), np.array([3.2, 12.0]), np.array([2.2, 14.0]), n=8),
    ],
    "y": [np.vstack([
        bz(np.array([1.4, 7.6]), np.array([1.7, 10.8]), np.array([2.2, 14.0]), np.array([4.3, 14.0]), n=8),
        bz(np.array([4.3, 14.0]), np.array([6.2, 14.0]), np.array([6.8, 10.4]), np.array([6.9, 7.4]), n=8)[1:],
        bz(np.array([6.9, 7.4]), np.array([6.9, 12.5]), np.array([7.1, 18.0]), np.array([4.7, 18.8]), n=9)[1:],
        bz(np.array([4.7, 18.8]), np.array([3.1, 19.0]), np.array([2.1, 17.5]), np.array([3.0, 16.2]), n=7)[1:],
    ])],
    "z": [np.vstack([
        bz(np.array([2.2, 7.6]), np.array([3.5, 7.3]), np.array([5.0, 7.5]), np.array([6.2, 7.4]), n=6),
        bz(np.array([6.2, 7.4]), np.array([5.0, 9.8]), np.array([3.4, 11.8]), np.array([2.4, 14.0]), n=8)[1:],
        bz(np.array([2.4, 14.0]), np.array([3.8, 14.1]), np.array([5.5, 14.0]), np.array([6.8, 13.8]), n=7)[1:],
    ])],
    "A": [
        np.vstack([
            bz(np.array([1.8, 14.0]), np.array([2.8, 8.5]), np.array([4.4, 3.2]), np.array([5.3, 2.0]), n=8),
            bz(np.array([5.3, 2.0]), np.array([5.6, 2.0]), np.array([6.2, 3.2]), np.array([6.8, 4.8]), n=5)[1:],
            bz(np.array([6.8, 4.8]), np.array([7.6, 7.8]), np.array([8.4, 11.2]), np.array([9.0, 14.0]), n=7)[1:],
        ]),
        bz(np.array([3.2, 9.2]), np.array([4.6, 8.9]), np.array([6.0, 8.9]), np.array([7.4, 9.1]), n=6),
    ],
    "B": [
        bz(np.array([2.4, 2.2]), np.array([2.3, 6.0]), np.array([2.3, 10.5]), np.array([2.4, 14.0]), n=9),
        np.vstack([
            bz(np.array([2.4, 2.2]), np.array([5.2, 1.8]), np.array([7.8, 2.6]), np.array([7.8, 5.0]), n=7),
            bz(np.array([7.8, 5.0]), np.array([7.8, 7.2]), np.array([5.6, 7.8]), np.array([2.5, 7.8]), n=7)[1:],
            bz(np.array([2.5, 7.8]), np.array([5.8, 7.8]), np.array([8.5, 8.4]), np.array([8.5, 11.0]), n=7)[1:],
            bz(np.array([8.5, 11.0]), np.array([8.5, 13.6]), np.array([5.8, 14.2]), np.array([2.4, 14.0]), n=7)[1:],
        ]),
    ],
    "C": [
        np.vstack([
            bz(np.array([8.4, 4.6]), np.array([8.0, 2.6]), np.array([6.6, 2.1]), np.array([5.4, 2.1]), n=7),
            bz(np.array([5.4, 2.1]), np.array([3.4, 2.1]), np.array([2.0, 5.0]), np.array([2.0, 8.0]), n=7)[1:],
            bz(np.array([2.0, 8.0]), np.array([2.0, 11.0]), np.array([3.4, 14.0]), np.array([5.4, 14.0]), n=7)[1:],
            bz(np.array([5.4, 14.0]), np.array([6.6, 14.0]), np.array([8.0, 13.4]), np.array([8.5, 11.6]), n=7)[1:],
        ]),
    ],
    "D": [
        bz(np.array([2.2, 2.2]), np.array([2.1, 6.0]), np.array([2.1, 10.5]), np.array([2.2, 14.0]), n=9),
        np.vstack([
            bz(np.array([2.2, 2.2]), np.array([5.4, 1.9]), np.array([8.8, 3.2]), np.array([8.8, 8.0]), n=8),
            bz(np.array([8.8, 8.0]), np.array([8.8, 12.6]), np.array([5.4, 14.1]), np.array([2.2, 14.0]), n=8)[1:],
        ]),
    ],
    "E": [
        np.vstack([
            bz(np.array([8.2, 2.2]), np.array([5.5, 2.1]), np.array([3.2, 2.1]), np.array([2.4, 2.4]), n=6),
            bz(np.array([2.4, 2.4]), np.array([2.1, 3.2]), np.array([2.1, 6.0]), np.array([2.1, 10.5]), n=8)[1:],
            bz(np.array([2.1, 10.5]), np.array([2.1, 13.4]), np.array([2.4, 14.0]), np.array([3.5, 14.0]), n=6)[1:],
            bz(np.array([3.5, 14.0]), np.array([5.2, 14.0]), np.array([7.0, 14.0]), np.array([8.2, 14.0]), n=6)[1:],
        ]),
        bz(np.array([2.1, 8.0]), np.array([3.8, 7.9]), np.array([5.4, 7.9]), np.array([7.0, 8.0]), n=6),
    ],
    "F": [
        np.vstack([
            bz(np.array([8.2, 2.2]), np.array([5.5, 2.1]), np.array([3.2, 2.1]), np.array([2.4, 2.4]), n=6),
            bz(np.array([2.4, 2.4]), np.array([2.1, 3.2]), np.array([2.1, 6.0]), np.array([2.2, 10.5]), n=8)[1:],
            bz(np.array([2.2, 10.5]), np.array([2.2, 12.5]), np.array([2.2, 13.5]), np.array([2.2, 14.0]), n=5)[1:],
        ]),
        bz(np.array([2.1, 8.0]), np.array([3.6, 7.9]), np.array([5.0, 7.9]), np.array([6.6, 8.0]), n=6),
    ],
    "G": [
        np.vstack([
            bz(np.array([8.4, 4.6]), np.array([8.0, 2.6]), np.array([6.6, 2.1]), np.array([5.4, 2.1]), n=7),
            bz(np.array([5.4, 2.1]), np.array([3.4, 2.1]), np.array([2.0, 5.0]), np.array([2.0, 8.0]), n=7)[1:],
            bz(np.array([2.0, 8.0]), np.array([2.0, 11.0]), np.array([3.4, 14.0]), np.array([5.4, 14.0]), n=7)[1:],
            bz(np.array([5.4, 14.0]), np.array([7.2, 14.0]), np.array([8.6, 12.6]), np.array([8.6, 8.2]), n=8)[1:],
            bz(np.array([8.6, 8.2]), np.array([8.6, 8.0]), np.array([7.5, 8.0]), np.array([5.6, 8.0]), n=6)[1:],
        ]),
    ],
    "H": [
        bz(np.array([2.3, 2.2]), np.array([2.2, 6.0]), np.array([2.2, 10.5]), np.array([2.3, 14.0]), n=9),
        bz(np.array([8.1, 2.2]), np.array([8.0, 6.0]), np.array([8.0, 10.5]), np.array([8.1, 14.0]), n=9),
        bz(np.array([2.3, 8.1]), np.array([4.2, 8.0]), np.array([6.2, 8.0]), np.array([8.1, 8.1]), n=6),
    ],
    "I": [
        bz(np.array([2.2, 2.2]), np.array([3.4, 2.1]), np.array([4.8, 2.1]), np.array([6.0, 2.2]), n=6),
        bz(np.array([4.1, 2.2]), np.array([4.0, 6.0]), np.array([4.0, 10.5]), np.array([4.1, 14.0]), n=9),
        bz(np.array([2.2, 14.0]), np.array([3.4, 14.1]), np.array([4.8, 14.1]), np.array([6.0, 14.0]), n=6),
    ],
    "J": [
        bz(np.array([3.0, 2.2]), np.array([4.8, 2.1]), np.array([6.6, 2.1]), np.array([8.0, 2.2]), n=6),
        np.vstack([
            bz(np.array([6.2, 2.2]), np.array([6.1, 6.0]), np.array([6.1, 10.0]), np.array([6.1, 11.6]), n=8),
            bz(np.array([6.1, 11.6]), np.array([6.1, 13.8]), np.array([4.6, 14.1]), np.array([3.2, 14.0]), n=7)[1:],
            bz(np.array([3.2, 14.0]), np.array([2.0, 13.8]), np.array([1.6, 12.4]), np.array([2.0, 11.0]), n=6)[1:],
        ]),
    ],
    "K": [
        bz(np.array([2.4, 2.2]), np.array([2.3, 6.0]), np.array([2.3, 10.5]), np.array([2.4, 14.0]), n=9),
        np.vstack([
            bz(np.array([8.2, 2.2]), np.array([6.4, 4.2]), np.array([4.6, 6.8]), np.array([2.9, 8.2]), n=7),
            bz(np.array([2.9, 8.2]), np.array([4.4, 9.8]), np.array([6.4, 12.2]), np.array([8.4, 14.0]), n=7)[1:],
        ]),
    ],
    "L": [
        np.vstack([
            bz(np.array([2.4, 2.2]), np.array([2.3, 5.8]), np.array([2.3, 9.8]), np.array([2.3, 11.8]), n=8),
            bz(np.array([2.3, 11.8]), np.array([2.3, 13.8]), np.array([3.4, 14.0]), np.array([5.0, 14.0]), n=7)[1:],
            bz(np.array([5.0, 14.0]), np.array([6.2, 14.0]), np.array([7.4, 14.0]), np.array([8.2, 13.9]), n=6)[1:],
        ]),
    ],
    "M": [
        np.vstack([
            bz(np.array([2.2, 14.0]), np.array([2.2, 10.0]), np.array([2.3, 5.5]), np.array([2.4, 2.5]), n=6),
            bz(np.array([2.4, 2.5]), np.array([2.6, 2.1]), np.array([3.3, 2.1]), np.array([3.6, 2.8]), n=5)[1:],
            bz(np.array([3.6, 2.8]), np.array([4.4, 5.2]), np.array([5.2, 7.8]), np.array([5.7, 9.6]), n=6)[1:],
            bz(np.array([5.7, 9.6]), np.array([5.9, 10.1]), np.array([6.1, 10.1]), np.array([6.3, 9.6]), n=4)[1:],
            bz(np.array([6.3, 9.6]), np.array([6.8, 7.8]), np.array([7.6, 5.2]), np.array([8.4, 2.8]), n=6)[1:],
            bz(np.array([8.4, 2.8]), np.array([8.7, 2.1]), np.array([9.4, 2.1]), np.array([9.6, 2.5]), n=5)[1:],
            bz(np.array([9.6, 2.5]), np.array([9.7, 5.5]), np.array([9.8, 10.0]), np.array([9.8, 14.0]), n=6)[1:],
        ]),
    ],
    "N": [
        bz(np.array([2.3, 2.2]), np.array([2.2, 6.0]), np.array([2.2, 10.5]), np.array([2.3, 14.0]), n=8),
        np.vstack([
            bz(np.array([2.3, 2.2]), np.array([4.3, 6.1]), np.array([6.2, 10.1]), np.array([8.1, 14.0]), n=8),
            bz(np.array([8.1, 14.0]), np.array([8.1, 10.0]), np.array([8.1, 5.5]), np.array([8.2, 2.2]), n=7)[1:],
        ]),
    ],
    "O": [
        np.vstack([
            bz(np.array([5.4, 2.1]), np.array([3.4, 2.1]), np.array([2.0, 5.0]), np.array([2.0, 8.0]), n=7),
            bz(np.array([2.0, 8.0]), np.array([2.0, 11.0]), np.array([3.4, 14.0]), np.array([5.4, 14.0]), n=7)[1:],
            bz(np.array([5.4, 14.0]), np.array([7.4, 14.0]), np.array([8.7, 11.0]), np.array([8.7, 8.0]), n=7)[1:],
            bz(np.array([8.7, 8.0]), np.array([8.7, 5.0]), np.array([7.4, 2.1]), np.array([5.4, 2.1]), n=7)[1:],
        ]),
    ],
    "P": [
        bz(np.array([2.4, 2.2]), np.array([2.3, 6.0]), np.array([2.3, 10.5]), np.array([2.4, 14.0]), n=9),
        np.vstack([
            bz(np.array([2.4, 2.2]), np.array([5.4, 1.9]), np.array([8.2, 2.8]), np.array([8.2, 5.2]), n=7),
            bz(np.array([8.2, 5.2]), np.array([8.2, 7.4]), np.array([5.5, 8.0]), np.array([2.4, 8.0]), n=7)[1:],
        ]),
    ],
    "Q": [
        np.vstack([
            bz(np.array([5.4, 2.1]), np.array([3.4, 2.1]), np.array([2.0, 5.0]), np.array([2.0, 8.0]), n=7),
            bz(np.array([2.0, 8.0]), np.array([2.0, 11.0]), np.array([3.4, 14.0]), np.array([5.4, 14.0]), n=7)[1:],
            bz(np.array([5.4, 14.0]), np.array([7.4, 14.0]), np.array([8.7, 11.0]), np.array([8.7, 8.0]), n=7)[1:],
            bz(np.array([8.7, 8.0]), np.array([8.7, 5.0]), np.array([7.4, 2.1]), np.array([5.4, 2.1]), n=7)[1:],
        ]),
        bz(np.array([5.8, 11.6]), np.array([6.8, 12.3]), np.array([8.0, 13.5]), np.array([9.2, 14.0]), n=5),
    ],
    "R": [
        bz(np.array([2.4, 2.2]), np.array([2.3, 6.0]), np.array([2.3, 10.5]), np.array([2.4, 14.0]), n=9),
        np.vstack([
            bz(np.array([2.4, 2.2]), np.array([5.4, 1.9]), np.array([8.2, 2.8]), np.array([8.2, 5.2]), n=7),
            bz(np.array([8.2, 5.2]), np.array([8.2, 7.2]), np.array([5.8, 7.8]), np.array([3.4, 7.8]), n=7)[1:],
            bz(np.array([3.4, 7.8]), np.array([4.8, 9.5]), np.array([6.6, 12.0]), np.array([8.5, 14.0]), n=7)[1:],
        ]),
    ],
    "S": [
        np.vstack([
            bz(np.array([7.6, 4.2]), np.array([7.2, 2.6]), np.array([5.8, 2.1]), np.array([4.8, 2.1]), n=7),
            bz(np.array([4.8, 2.1]), np.array([3.2, 2.1]), np.array([2.3, 3.6]), np.array([2.6, 5.5]), n=7)[1:],
            bz(np.array([2.6, 5.5]), np.array([3.0, 7.4]), np.array([6.8, 7.6]), np.array([7.8, 9.6]), n=8)[1:],
            bz(np.array([7.8, 9.6]), np.array([8.4, 11.0]), np.array([7.6, 14.0]), np.array([5.0, 14.0]), n=7)[1:],
            bz(np.array([5.0, 14.0]), np.array([3.4, 14.0]), np.array([2.0, 13.6]), np.array([1.8, 12.2]), n=6)[1:],
        ]),
    ],
    "T": [
        bz(np.array([1.6, 2.4]), np.array([3.6, 2.1]), np.array([6.6, 2.1]), np.array([8.6, 2.4]), n=7),
        bz(np.array([5.1, 2.2]), np.array([5.0, 6.0]), np.array([5.0, 10.5]), np.array([5.1, 14.0]), n=9),
    ],
    "U": [
        np.vstack([
            bz(np.array([2.4, 2.2]), np.array([2.3, 6.0]), np.array([2.3, 10.5]), np.array([2.4, 12.0]), n=7),
            bz(np.array([2.4, 12.0]), np.array([2.5, 14.0]), np.array([4.2, 14.1]), np.array([5.4, 14.0]), n=7)[1:],
            bz(np.array([5.4, 14.0]), np.array([6.6, 14.1]), np.array([8.3, 14.0]), np.array([8.4, 12.0]), n=7)[1:],
            bz(np.array([8.4, 12.0]), np.array([8.5, 10.5]), np.array([8.5, 6.0]), np.array([8.4, 2.2]), n=7)[1:],
        ]),
    ],
    "V": [
        np.vstack([
            bz(np.array([2.0, 2.2]), np.array([2.8, 5.8]), np.array([4.2, 10.5]), np.array([5.2, 14.0]), n=8),
            bz(np.array([5.2, 14.0]), np.array([6.2, 10.5]), np.array([7.6, 5.8]), np.array([8.4, 2.2]), n=8)[1:],
        ]),
    ],
    "W": [
        np.vstack([
            bz(np.array([1.6, 2.2]), np.array([2.3, 6.0]), np.array([3.4, 10.5]), np.array([4.2, 14.0]), n=7),
            bz(np.array([4.2, 14.0]), np.array([5.0, 10.5]), np.array([5.8, 7.0]), np.array([6.6, 4.0]), n=6)[1:],
            bz(np.array([6.6, 4.0]), np.array([7.4, 7.0]), np.array([8.2, 10.5]), np.array([9.0, 14.0]), n=6)[1:],
            bz(np.array([9.0, 14.0]), np.array([9.8, 10.5]), np.array([10.9, 6.0]), np.array([11.6, 2.2]), n=7)[1:],
        ]),
    ],
    "X": [
        bz(np.array([2.2, 2.2]), np.array([4.2, 6.1]), np.array([6.2, 10.1]), np.array([8.2, 14.0]), n=8),
        bz(np.array([8.2, 2.2]), np.array([6.2, 6.1]), np.array([4.2, 10.1]), np.array([2.2, 14.0]), n=8),
    ],
    "Y": [
        bz(np.array([2.0, 2.2]), np.array([3.0, 4.8]), np.array([4.2, 6.8]), np.array([5.2, 8.0]), n=6),
        np.vstack([
            bz(np.array([8.4, 2.2]), np.array([7.4, 4.8]), np.array([6.2, 6.8]), np.array([5.2, 8.0]), n=6),
            bz(np.array([5.2, 8.0]), np.array([5.2, 10.0]), np.array([5.2, 12.0]), np.array([5.2, 14.0]), n=6)[1:],
        ]),
    ],
    "Z": [
        np.vstack([
            bz(np.array([2.2, 2.2]), np.array([4.2, 2.1]), np.array([6.2, 2.1]), np.array([8.0, 2.2]), n=6),
            bz(np.array([8.0, 2.2]), np.array([6.1, 6.1]), np.array([4.1, 10.1]), np.array([2.2, 14.0]), n=8)[1:],
            bz(np.array([2.2, 14.0]), np.array([4.2, 14.0]), np.array([6.2, 14.0]), np.array([8.2, 14.0]), n=6)[1:],
        ]),
    ],
    "0": [
        np.vstack([
            bz(np.array([4.9, 2.1]), np.array([3.4, 2.1]), np.array([2.4, 4.8]), np.array([2.4, 8.0]), n=7),
            bz(np.array([2.4, 8.0]), np.array([2.4, 11.2]), np.array([3.4, 14.0]), np.array([4.9, 14.0]), n=7)[1:],
            bz(np.array([4.9, 14.0]), np.array([6.4, 14.0]), np.array([7.4, 11.2]), np.array([7.4, 8.0]), n=7)[1:],
            bz(np.array([7.4, 8.0]), np.array([7.4, 4.8]), np.array([6.4, 2.1]), np.array([4.9, 2.1]), n=7)[1:],
        ]),
    ],
    "1": [
        np.vstack([
            bz(np.array([2.4, 5.2]), np.array([3.2, 3.4]), np.array([4.0, 2.3]), np.array([4.6, 2.2]), n=6),
            bz(np.array([4.6, 2.2]), np.array([4.6, 6.0]), np.array([4.6, 10.5]), np.array([4.6, 14.0]), n=8)[1:],
        ]),
        bz(np.array([2.6, 14.0]), np.array([3.6, 14.0]), np.array([5.6, 14.0]), np.array([6.6, 14.0]), n=5),
    ],
    "2": [
        np.vstack([
            bz(np.array([2.4, 5.0]), np.array([2.4, 2.8]), np.array([4.4, 2.1]), np.array([5.6, 2.1]), n=7),
            bz(np.array([5.6, 2.1]), np.array([7.2, 2.1]), np.array([7.6, 3.8]), np.array([7.4, 5.5]), n=6)[1:],
            bz(np.array([7.4, 5.5]), np.array([7.2, 7.5]), np.array([4.6, 10.8]), np.array([2.4, 14.0]), n=8)[1:],
            bz(np.array([2.4, 14.0]), np.array([4.0, 14.0]), np.array([6.2, 14.0]), np.array([7.8, 14.0]), n=6)[1:],
        ]),
    ],
    "3": [
        np.vstack([
            bz(np.array([2.5, 4.5]), np.array([2.6, 2.6]), np.array([4.4, 2.1]), np.array([5.4, 2.1]), n=6),
            bz(np.array([5.4, 2.1]), np.array([6.8, 2.1]), np.array([7.4, 3.2]), np.array([7.4, 4.8]), n=6)[1:],
            bz(np.array([7.4, 4.8]), np.array([7.4, 6.2]), np.array([6.0, 7.4]), np.array([4.8, 7.5]), n=6)[1:],
            bz(np.array([4.8, 7.5]), np.array([6.4, 7.6]), np.array([7.8, 9.0]), np.array([7.8, 10.8]), n=7)[1:],
            bz(np.array([7.8, 10.8]), np.array([7.8, 12.8]), np.array([6.6, 14.0]), np.array([5.0, 14.0]), n=7)[1:],
            bz(np.array([5.0, 14.0]), np.array([3.6, 14.0]), np.array([2.4, 13.5]), np.array([2.2, 12.2]), n=6)[1:],
        ]),
    ],
    "4": [
        np.vstack([
            bz(np.array([5.4, 2.2]), np.array([4.2, 4.8]), np.array([2.8, 7.4]), np.array([1.6, 9.8]), n=7),
            bz(np.array([1.6, 9.8]), np.array([3.6, 9.8]), np.array([5.8, 9.8]), np.array([7.8, 9.8]), n=6)[1:],
        ]),
        bz(np.array([5.8, 2.2]), np.array([5.8, 6.0]), np.array([5.8, 10.5]), np.array([5.8, 14.0]), n=8),
    ],
    "5": [
        np.vstack([
            bz(np.array([3.0, 2.2]), np.array([3.0, 4.0]), np.array([3.0, 5.5]), np.array([3.0, 7.0]), n=5),
            bz(np.array([3.0, 7.0]), np.array([5.2, 6.6]), np.array([7.8, 7.8]), np.array([7.8, 10.4]), n=7)[1:],
            bz(np.array([7.8, 10.4]), np.array([7.8, 12.8]), np.array([6.4, 14.0]), np.array([4.8, 14.0]), n=7)[1:],
            bz(np.array([4.8, 14.0]), np.array([3.4, 14.0]), np.array([2.2, 13.5]), np.array([2.0, 12.2]), n=6)[1:],
        ]),
        bz(np.array([2.8, 2.2]), np.array([4.4, 2.2]), np.array([6.0, 2.2]), np.array([7.4, 2.2]), n=6),
    ],
    "6": [
        np.vstack([
            bz(np.array([6.8, 2.2]), np.array([5.2, 2.2]), np.array([3.2, 4.2]), np.array([2.4, 8.0]), n=7),
            bz(np.array([2.4, 8.0]), np.array([2.0, 11.2]), np.array([3.2, 14.0]), np.array([5.0, 14.0]), n=7)[1:],
            bz(np.array([5.0, 14.0]), np.array([6.6, 14.0]), np.array([7.6, 12.4]), np.array([7.6, 10.2]), n=6)[1:],
            bz(np.array([7.6, 10.2]), np.array([7.6, 8.2]), np.array([5.8, 7.2]), np.array([3.6, 8.0]), n=7)[1:],
        ]),
    ],
    "7": [
        np.vstack([
            bz(np.array([2.0, 2.2]), np.array([4.0, 2.1]), np.array([6.0, 2.1]), np.array([7.6, 2.2]), n=6),
            bz(np.array([7.6, 2.2]), np.array([6.4, 6.0]), np.array([5.0, 10.0]), np.array([3.6, 14.0]), n=8)[1:],
        ]),
    ],
    "8": [
        np.vstack([
            bz(np.array([4.9, 2.1]), np.array([3.4, 2.1]), np.array([2.4, 3.4]), np.array([2.4, 5.0]), n=6),
            bz(np.array([2.4, 5.0]), np.array([2.4, 6.8]), np.array([3.6, 7.8]), np.array([4.9, 8.0]), n=6)[1:],
            bz(np.array([4.9, 8.0]), np.array([6.4, 8.2]), np.array([7.8, 9.6]), np.array([7.8, 11.4]), n=7)[1:],
            bz(np.array([7.8, 11.4]), np.array([7.8, 13.2]), np.array([6.6, 14.0]), np.array([4.9, 14.0]), n=7)[1:],
            bz(np.array([4.9, 14.0]), np.array([3.2, 14.0]), np.array([2.0, 13.2]), np.array([2.0, 11.4]), n=7)[1:],
            bz(np.array([2.0, 11.4]), np.array([2.0, 9.6]), np.array([3.4, 8.2]), np.array([4.9, 8.0]), n=7)[1:],
            bz(np.array([4.9, 8.0]), np.array([6.2, 7.8]), np.array([7.4, 6.8]), np.array([7.4, 5.0]), n=6)[1:],
            bz(np.array([7.4, 5.0]), np.array([7.4, 3.4]), np.array([6.4, 2.1]), np.array([4.9, 2.1]), n=6)[1:],
        ]),
    ],
    "9": [
        np.vstack([
            bz(np.array([7.4, 8.0]), np.array([7.4, 4.8]), np.array([6.4, 2.1]), np.array([4.9, 2.1]), n=7),
            bz(np.array([4.9, 2.1]), np.array([3.4, 2.1]), np.array([2.4, 4.8]), np.array([2.4, 7.5]), n=7)[1:],
            bz(np.array([2.4, 7.5]), np.array([2.4, 8.8]), np.array([4.0, 9.0]), np.array([5.8, 8.8]), n=6)[1:],
            bz(np.array([5.8, 8.8]), np.array([6.8, 8.5]), np.array([7.2, 8.2]), np.array([7.4, 8.0]), n=5)[1:],
            bz(np.array([7.4, 8.0]), np.array([7.4, 10.5]), np.array([6.8, 13.8]), np.array([4.2, 14.0]), n=8)[1:],
            bz(np.array([4.2, 14.0]), np.array([3.4, 14.0]), np.array([2.6, 13.6]), np.array([2.4, 12.6]), n=5)[1:],
        ]),
    ],
    ".": [np.array([[2.2, 13.3], [2.6, 13.7]])],
    ",": [bz(np.array([2.6, 13.0]), np.array([2.8, 13.8]), np.array([2.4, 15.2]), np.array([1.6, 15.8]), n=5)],
    "…": [
        np.array([[2.0, 13.3], [2.4, 13.7]]),
        np.array([[4.4, 13.3], [4.8, 13.7]]),
        np.array([[6.8, 13.3], [7.2, 13.7]]),
    ],
    "!": [
        bz(np.array([2.5, 2.2]), np.array([2.5, 5.0]), np.array([2.5, 8.0]), np.array([2.5, 10.2]), n=5),
        np.array([[2.3, 13.3], [2.7, 13.7]]),
    ],
    "?": [
        np.vstack([
            bz(np.array([2.0, 4.4]), np.array([2.0, 2.6]), np.array([4.2, 2.1]), np.array([5.5, 2.1]), n=6),
            bz(np.array([5.5, 2.1]), np.array([7.2, 2.1]), np.array([7.6, 3.8]), np.array([7.2, 5.5]), n=6)[1:],
            bz(np.array([7.2, 5.5]), np.array([6.8, 7.2]), np.array([4.8, 8.0]), np.array([4.6, 10.2]), n=7)[1:],
        ]),
        np.array([[4.4, 13.3], [4.8, 13.7]]),
    ],
    ":": [
        np.array([[2.3, 7.3], [2.7, 7.7]]),
        np.array([[2.3, 13.3], [2.7, 13.7]]),
    ],
    ";": [
        np.array([[2.3, 7.3], [2.7, 7.7]]),
        bz(np.array([2.6, 13.0]), np.array([2.8, 13.8]), np.array([2.4, 15.2]), np.array([1.6, 15.8]), n=5),
    ],
    "-": [np.linspace([1.8, 8.2], [5.8, 8.2], 4)],
    "–": [np.linspace([1.5, 8.2], [7.5, 8.2], 5)],
    "—": [np.linspace([1.2, 8.2], [10.2, 8.2], 7)],
    "/": [np.linspace([1.6, 14.2], [6.8, 2.0], 7)],
    "'": [np.array([[2.5, 2.2], [2.3, 5.0]])],
    '"': [
        np.array([[2.2, 2.2], [2.0, 5.0]]),
        np.array([[4.6, 2.2], [4.4, 5.0]]),
    ],
    "‘": [bz(np.array([1.8, 4.8]), np.array([2.4, 4.2]), np.array([2.5, 3.2]), np.array([2.4, 2.2]), n=5)],
    "’": [
        bz(
            np.array([2.0, 2.2]),
            np.array([1.9, 3.2]),
            np.array([2.0, 4.2]),
            np.array([2.6, 4.8]),
            n=5,
        )
    ],
    "“": [
        bz(np.array([1.8, 4.8]), np.array([2.4, 4.2]), np.array([2.5, 3.2]), np.array([2.4, 2.2]), n=5),
        bz(np.array([3.8, 4.8]), np.array([4.4, 4.2]), np.array([4.5, 3.2]), np.array([4.4, 2.2]), n=5),
    ],
    "”": [
        bz(np.array([2.0, 2.2]), np.array([1.9, 3.2]), np.array([2.0, 4.2]), np.array([2.6, 4.8]), n=5),
        bz(np.array([4.0, 2.2]), np.array([3.9, 3.2]), np.array([4.0, 4.2]), np.array([4.6, 4.8]), n=5),
    ],
    "(": [bz(np.array([4.8, 1.4]), np.array([2.2, 5.2]), np.array([2.2, 10.8]), np.array([4.8, 14.6]), n=8)],
    ")": [bz(np.array([2.2, 1.4]), np.array([4.8, 5.2]), np.array([4.8, 10.8]), np.array([2.2, 14.6]), n=8)],
})
OMNI_CASUAL_WIDTHS = dict(GLYPH_WIDTHS)
OMNI_CASUAL_WIDTHS.update({
    "a": 8.1, "b": 8.2, "c": 7.2, "d": 8.2, "e": 7.6, "f": 5.8, "g": 8.2, "h": 8.4,
    "i": 5.2, "j": 5.5, "k": 8.0, "l": 5.5, "m": 11.8, "n": 8.2, "o": 7.8, "p": 8.2,
    "q": 8.2, "r": 7.0, "s": 7.4, "t": 6.0, "u": 8.0, "v": 7.8, "w": 10.8, "x": 7.8,
    "y": 8.2, "z": 7.4,
    "A": 10.4, "B": 9.6, "C": 9.6, "D": 10.0, "E": 9.4, "F": 9.2,
    "G": 9.8, "H": 9.8, "I": 7.6, "J": 8.8, "K": 9.6, "L": 9.2,
    "M": 11.8, "N": 9.8, "O": 10.0, "P": 9.6, "Q": 10.4, "R": 9.8,
    "S": 9.6, "T": 9.6, "U": 9.8, "V": 9.6, "W": 12.6, "X": 9.6, "Y": 9.6, "Z": 9.6,
    "0": 8.6, "1": 7.2, "2": 8.8, "3": 8.8, "4": 9.0,
    "5": 8.8, "6": 8.8, "7": 8.8, "8": 8.8, "9": 8.8,
    ".": 4.6, ",": 4.6, "…": 9.2, "!": 5.0, "?": 8.2, ":": 5.0, ";": 5.0,
    "-": 7.0, "–": 8.8, "—": 11.4, "/": 8.4,
    "'": 4.6, '"': 6.6, "‘": 4.6, "’": 4.6, "“": 6.6, "”": 6.6,
    "(": 6.2, ")": 6.2,
})
OMNI_CASUAL_CENTERS = dict(GLYPH_CENTERS)
OMNI_CASUAL_CENTERS.update({
    "a": 4.3, "e": 4.3, "g": 4.3, "i": 3.1, "o": 4.4, "u": 4.4, "y": 4.3,
    "A": 5.4, "B": 5.0, "C": 5.2, "D": 5.2, "E": 5.0, "F": 4.8,
    "G": 5.2, "H": 5.1, "I": 4.1, "J": 5.0, "K": 5.2, "L": 5.0,
    "M": 6.0, "N": 5.2, "O": 5.4, "P": 5.0, "Q": 5.4, "R": 5.2,
    "S": 5.0, "T": 5.1, "U": 5.4, "V": 5.2, "W": 6.6, "X": 5.2, "Y": 5.2, "Z": 5.2,
    "0": 4.9, "1": 4.6, "2": 5.0, "3": 5.0, "4": 5.0,
    "5": 4.9, "6": 4.8, "7": 5.0, "8": 4.9, "9": 4.9,
    ".": 2.4, ",": 2.4, "…": 4.6, "!": 2.5, "?": 4.6, ":": 2.5, ";": 2.4,
    "-": 3.8, "–": 4.5, "—": 5.7, "/": 4.2,
    "'": 2.4, '"': 3.3, "‘": 2.4, "’": 2.4, "“": 3.3, "”": 3.3,
    "(": 3.5, ")": 3.5,
})
