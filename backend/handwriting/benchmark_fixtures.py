"""
OmniDraw CA-VHC Benchmark Fixtures & Corpus Definitions.

Formal Version: CA-VHC-CORPUS-v1.0-FROZEN
Reviewed and Frozen by: TV1 (AI Data & Writer Profile Lead) - 23/09/2026
Report: docs/19_benchmark_corpus_freeze_report.md

Defined per docs/05_ca_vhc_research_spec.md & docs/19_benchmark_corpus_freeze_report.md:
- BENCHMARK_DEV_CORPUS_20: 20 development words
- BENCHMARK_HOLDOUT_CORPUS_20: 20 holdout words (strictly disjoint from dev)
- PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS: 10 DEV-only software acceptance words
- STANDARD_SEEDS: [42, 100, 2026, 999999]
- load_benchmark_fonts(): loads 'oly' (omnidraw_legacy) and 'omni_casual' font packs
"""

import json
from pathlib import Path
from typing import Dict, Any, List

CORPUS_VERSION: str = "CA-VHC-CORPUS-v1.0-FROZEN"
_CORPUS_JSON_PATH = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / "ca_vhc_corpus_v1_frozen.json"

BENCHMARK_DEV_CORPUS_20: List[str] = [
    "tiếng", "việt", "nguyễn", "nước", "đường",
    "khuấy", "thuở", "nghỉ", "hoặc", "chuẩn",
    "trường", "quyện", "nghĩ", "phượng", "kiều",
    "hướng", "mượt", "bước", "vẫy", "nhánh",
]

BENCHMARK_HOLDOUT_CORPUS_20: List[str] = [
    "nghiêng", "khoác", "truyền", "hoàng", "nguyệt",
    "thoáng", "quỳnh", "nhuộm", "duyệt", "khoảnh",
    "giường", "chuyện", "xoay", "bỗng", "quét",
    "khẽ", "nhặt", "nguồn", "sưởi", "vẹn",
]

# Deliberately selected from DEV only. Do not add holdout words here and do not
# freeze geometry fingerprints: PR3 is expected to change diacritic placement.
PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS: List[str] = [
    "tiếng",
    "nước",
    "đường",
    "khuấy",
    "thuở",
    "nghỉ",
    "trường",
    "phượng",
    "mượt",
    "vẫy",
]

STANDARD_SEEDS: List[int] = [42, 100, 2026, 999999]


def load_benchmark_fonts() -> Dict[str, Dict[str, Any]]:
    """
    Tải 2 font pack chuẩn dùng cho nghiên cứu CA-VHC: 'oly' và 'omni_casual'.
    Trả về dict: {font_id: {"font_pack": pack, "render_profile": profile}}
    """
    try:
        from handwriting.engine import resolve_font
    except ImportError:
        from backend.handwriting.engine import resolve_font

    fonts = {}
    for font_id in ("oly", "omni_casual"):
        pack, profile = resolve_font(font_id)
        fonts[font_id] = {
            "font_pack": pack,
            "render_profile": profile,
        }
    return fonts


def get_frozen_corpus_path() -> Path:
    """Trả về đường dẫn tuyệt đối đến file fixture JSON của corpus đóng băng."""
    return _CORPUS_JSON_PATH


def load_frozen_corpus_metadata() -> Dict[str, Any]:
    """
    Nạp dữ liệu chi tiết của bộ ngữ liệu đối chuẩn đóng băng CA-VHC-CORPUS-v1.0-FROZEN
    từ file fixture tests/fixtures/ca_vhc_corpus_v1_frozen.json.
    """
    if not _CORPUS_JSON_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file corpus frozen: {_CORPUS_JSON_PATH}")
    with open(_CORPUS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
