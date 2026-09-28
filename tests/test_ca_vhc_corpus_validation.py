"""
Kiểm thử Tính Toàn vẹn và Kỷ luật Quản trị Ngữ liệu CA-VHC Corpus v1.0.

Corpus: CA-VHC-CORPUS-v1.0-FROZEN
Owner: TV1 (AI Data & Writer Profile Lead)
Report: docs/19_benchmark_corpus_freeze_report.md
Specification: docs/05_ca_vhc_research_spec.md & docs/08_handwriting_dataset_spec.md

Mục tiêu kiểm thử:
1. Xác thực file fixture JSON tests/fixtures/ca_vhc_corpus_v1_frozen.json.
2. Kiểm tra tính đồng nhất 100% (parity) giữa file JSON và constants trong benchmark_fixtures.py.
3. Rào chắn chống rò rỉ dữ liệu (Anti-Leakage Guard): DEV ∩ HOLDOUT = ∅.
4. Toàn vẹn chuẩn hóa Unicode (NFC / NFD).
5. Độ phủ ngôn ngữ học: 6 thanh điệu, dấu phụ biến âm (mũ, râu, trăng, gạch), stacking diacritics.
6. Độ phủ hình học: ascenders, descenders.
7. Tập nghiệm thu phần mềm (Acceptance Specimens): 10 từ DEV, 0 từ HOLDOUT.
"""

import json
import unicodedata
from pathlib import Path
import pytest

from backend.handwriting.benchmark_fixtures import (
    CORPUS_VERSION,
    BENCHMARK_DEV_CORPUS_20,
    BENCHMARK_HOLDOUT_CORPUS_20,
    PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS,
    STANDARD_SEEDS,
    get_frozen_corpus_path,
    load_frozen_corpus_metadata,
)

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "ca_vhc_corpus_v1_frozen.json"


# ==============================================================================
# 1. Kiểm thử File Fixture & Cấu trúc Dữ liệu
# ==============================================================================

def test_corpus_fixture_file_exists_and_loads():
    """Kiểm tra file fixture tồn tại và nạp cú pháp JSON hợp lệ."""
    assert FIXTURE_PATH.exists(), f"Không tìm thấy file fixture: {FIXTURE_PATH}"
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["corpus_id"] == CORPUS_VERSION
    assert data["version"] == "1.0"
    assert data["owner"] == "TV1 — AI Data & Writer Profile Lead"
    assert data["leakage_guard"]["status"] == "STRICTLY_DISJOINT_AND_ENFORCED"
    assert data["leakage_guard"]["disjoint_condition"] == "DEV ∩ HOLDOUT = ∅"
    assert data["leakage_guard"]["dev_count"] == 20
    assert data["leakage_guard"]["holdout_count"] == 20
    assert data["leakage_guard"]["intersection_count"] == 0


def test_helper_functions_and_error_handling(monkeypatch):
    """Kiểm tra các hàm trợ giúp get_frozen_corpus_path và load_frozen_corpus_metadata."""
    path = get_frozen_corpus_path()
    assert path == FIXTURE_PATH
    assert path.exists()

    data = load_frozen_corpus_metadata()
    assert isinstance(data, dict)
    assert data["corpus_id"] == CORPUS_VERSION

    # Kiểm tra ném ngoại lệ khi file không tồn tại
    from backend.handwriting import benchmark_fixtures
    fake_path = Path("fake_non_existent_corpus.json")
    monkeypatch.setattr(benchmark_fixtures, "_CORPUS_JSON_PATH", fake_path)
    with pytest.raises(FileNotFoundError):
        benchmark_fixtures.load_frozen_corpus_metadata()


# ==============================================================================
# 2. Kiểm thử Tính Đồng nhất (Parity) với Mã nguồn
# ==============================================================================

def test_corpus_python_constants_parity():
    """Xác thực tính đồng nhất 100% giữa file fixture JSON và constants python."""
    data = load_frozen_corpus_metadata()

    json_dev_words = [item["word"] for item in data["dev_corpus_20"]]
    json_holdout_words = [item["word"] for item in data["holdout_corpus_20"]]
    json_acceptance_words = data["acceptance_specimens_10"]
    json_seeds = data["standard_seeds"]

    assert json_dev_words == BENCHMARK_DEV_CORPUS_20, "Lệch danh sách DEV giữa JSON và Python constants"
    assert json_holdout_words == BENCHMARK_HOLDOUT_CORPUS_20, "Lệch danh sách HOLDOUT giữa JSON và Python constants"
    assert json_acceptance_words == PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS, "Lệch mẫu Acceptance giữa JSON và Python"
    assert json_seeds == STANDARD_SEEDS, "Lệch Standard Seeds giữa JSON và Python"


# ==============================================================================
# 3. Rào chắn Chống Rò rỉ Dữ liệu & Tính Rời nhau Tuyệt đối
# ==============================================================================

def test_strict_disjointness_anti_leakage_guard():
    """
    Rào chắn chống rò rỉ:
    - DEV ∩ HOLDOUT = ∅
    - Acceptance Specimens ⊆ DEV
    - Acceptance Specimens ∩ HOLDOUT = ∅
    """
    data = load_frozen_corpus_metadata()
    dev_set = set(item["word"] for item in data["dev_corpus_20"])
    holdout_set = set(item["word"] for item in data["holdout_corpus_20"])
    acceptance_set = set(data["acceptance_specimens_10"])

    assert len(dev_set) == 20, "Tập DEV phải có đúng 20 từ duy nhất"
    assert len(holdout_set) == 20, "Tập HOLDOUT phải có đúng 20 từ duy nhất"
    assert len(acceptance_set) == 10, "Tập Acceptance phải có đúng 10 từ duy nhất"

    intersection = dev_set.intersection(holdout_set)
    assert len(intersection) == 0, f"VI PHẠM RÀO CHẮN: Có từ rò rỉ giữa DEV và HOLDOUT: {intersection}"

    assert acceptance_set.issubset(dev_set), "Tập Acceptance phải là tập con 100% của DEV"
    assert len(acceptance_set.intersection(holdout_set)) == 0, "Acceptance specimens không được chạm vào HOLDOUT"


# ==============================================================================
# 4. Kiểm chuẩn Unicode & Không Ký tự Ẩn
# ==============================================================================

def test_unicode_normalization_integrity():
    """Kiểm tra chuẩn hóa Unicode NFC, NFD và không chứa ký tự điều khiển/khoảng trắng lạ."""
    data = load_frozen_corpus_metadata()
    all_words_data = data["dev_corpus_20"] + data["holdout_corpus_20"]

    for item in all_words_data:
        word = item["word"]
        # Không chứa khoảng trắng đầu/cuối hay ký tự điều khiển
        assert word == word.strip(), f"Từ có khoảng trắng: '{word}'"
        assert not any(unicodedata.category(c).startswith("C") for c in word), f"Từ có ký tự điều khiển: '{word}'"

        # Khớp chuẩn NFC và NFD
        expected_nfc = unicodedata.normalize("NFC", word)
        expected_nfd = unicodedata.normalize("NFD", word)
        assert item["unicode_nfc"] == expected_nfc
        assert item["unicode_nfd"] == expected_nfd


# ==============================================================================
# 5. Phân tích Độ phủ Ngôn ngữ học (Tones & Diacritics)
# ==============================================================================

def test_tone_distribution_coverage():
    """Kiểm tra độ phủ đầy đủ 6 thanh điệu tiếng Việt theo Doc 19 Mục 3.1."""
    data = load_frozen_corpus_metadata()

    # Tập DEV: 5 sắc, 3 huyền, 3 hỏi, 3 ngã, 5 nặng (tổng 20) + nhánh (sắc) -> 6 sắc
    dev_tones = [item["tone"] for item in data["dev_corpus_20"]]
    assert dev_tones.count("acute") == 6
    assert dev_tones.count("grave") == 3
    assert dev_tones.count("hook_above") == 3
    assert dev_tones.count("tilde") == 3
    assert dev_tones.count("dot_below") == 5

    # Tập HOLDOUT: 2 ngang (level), 3 sắc, 5 huyền, 2 hỏi, 2 ngã, 6 nặng (tổng 20)
    holdout_tones = [item["tone"] for item in data["holdout_corpus_20"]]
    assert holdout_tones.count("level") == 2
    assert holdout_tones.count("acute") == 3
    assert holdout_tones.count("grave") == 5
    assert holdout_tones.count("hook_above") == 2
    assert holdout_tones.count("tilde") == 2
    assert holdout_tones.count("dot_below") == 6

    # Cả hai tập đều có độ phủ thanh điệu phong phú
    assert set(dev_tones) == {"acute", "grave", "hook_above", "tilde", "dot_below"}
    assert set(holdout_tones) == {"level", "acute", "grave", "hook_above", "tilde", "dot_below"}


def test_diacritics_and_stacking_coverage():
    """Kiểm tra độ phủ dấu phụ (mũ, râu, trăng, gạch) và dấu xếp chồng (stacking)."""
    data = load_frozen_corpus_metadata()
    all_words = data["dev_corpus_20"] + data["holdout_corpus_20"]

    # Phải có dấu mũ (circumflex), râu (horn), trăng (breve), gạch (đ)
    all_vowel_diacritics = [d for item in all_words for d in item["vowel_diacritics"]]
    assert "circumflex" in all_vowel_diacritics
    assert "horn_u" in all_vowel_diacritics
    assert "horn_o" in all_vowel_diacritics
    assert "breve" in all_vowel_diacritics
    assert "stroke_d" in all_vowel_diacritics

    # Phải có trường hợp dấu xếp chồng (stacking diacritics: dấu thanh trên mũ/râu)
    dev_stacking = [item for item in data["dev_corpus_20"] if item["stacking_diacritics"]]
    holdout_stacking = [item for item in data["holdout_corpus_20"] if item["stacking_diacritics"]]
    assert len(dev_stacking) >= 10, "DEV phải có ít nhất 10 từ có dấu thanh xếp chồng"
    assert len(holdout_stacking) >= 5, "HOLDOUT phải có ít nhất 5 từ có dấu thanh xếp chồng"


# ==============================================================================
# 6. Phân tích Độ phủ Hình học (Ascenders & Descenders)
# ==============================================================================

def test_geometric_structural_coverage():
    """Kiểm tra độ phủ nét nhô cao (ascender) và nét kéo dài xuống (descender)."""
    data = load_frozen_corpus_metadata()

    dev_ascenders = [item for item in data["dev_corpus_20"] if item["has_ascender"]]
    dev_descenders = [item for item in data["dev_corpus_20"] if item["has_descender"]]
    assert len(dev_ascenders) >= 12, "DEV phải có tỷ lệ lớn từ chứa ascender"
    assert len(dev_descenders) >= 8, "DEV phải có đủ từ chứa descender"

    holdout_ascenders = [item for item in data["holdout_corpus_20"] if item["has_ascender"]]
    holdout_descenders = [item for item in data["holdout_corpus_20"] if item["has_descender"]]
    assert len(holdout_ascenders) >= 10
    assert len(holdout_descenders) >= 8
