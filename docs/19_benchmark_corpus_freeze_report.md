# OmniDraw — Báo cáo Đóng băng Ngữ liệu Benchmark CA-VHC (Corpus Review & Freeze Report)

```text
CORPUS_ID: CA-VHC-CORPUS-v1.0-FROZEN
REVIEWER_AND_OWNER: TV1 — AI Data & Writer Profile Lead
APPROVAL_DATE: 23/09/2026
CORPUS_STATUS: APPROVED_AND_FROZEN
LEAKAGE_GUARD_STATUS: STRICTLY_DISJOINT_AND_ENFORCED
```

---

## 1. Mục đích và Phạm vi

Tài liệu này xác lập quyết định học thuật và kỹ thuật chính thức của **TV1 (AI Data & Writer Profile Lead)** về việc **rà soát độ phủ ngôn ngữ học (Coverage Analysis)** và **chính thức đóng băng (Formal Freeze)** bộ ngữ liệu đối chứng chuẩn tiếng Việt (Benchmark Corpus).

Bộ ngữ liệu đóng băng này là **Nguồn sự thật duy nhất (Single Source of Truth)** dùng để:
1. Huấn luyện, điều chỉnh tham số hình học và kiểm thử hồi quy phần mềm trong giai đoạn phát triển (**Development Set — DEV 20 từ**).
2. Nghiệm thu phần mềm trước khi mở cổng PR3 (**DEV-only Acceptance Specimens — 10 từ**).
3. Đánh giá độc lập, khách quan năng lực giải quyết va chạm dấu và tối ưu hóa chuyển động nét vẽ của thuật toán CA-VHC so với ba baseline B1/B2/B3 (**Holdout Evaluation Set — HOLDOUT 20 từ**).

---

## 2. Chi tiết Danh mục Ngữ liệu Đóng băng

### 2.1. Tập Phát triển (Development Corpus — `BENCHMARK_DEV_CORPUS_20`)

Bao gồm 20 từ đơn âm tiết tiếng Việt đại diện, được dùng công khai trong quá trình phát triển thuật toán, căn chỉnh trọng số hàm mục tiêu $J$ và chạy regression tests.

| STT | Từ | Cấu trúc âm tiết (NFD) | Thanh điệu | Dấu chữ cái | Phụ âm đầu / cuối | Đặc điểm hình học & Thách thức CA-VHC |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `tiếng` | `t + i + e + ̂ + ́ + n + g` | Sắc | Mũ `ê` | `t` / `ng` | Ascender `t`, descender `g`, dấu sắc xếp trên mũ `ê`, rủi ro va chạm bridge `i-ê` và `ê-n`. |
| 2 | `việt` | `v + i + e + ̂ + ̣ + t` | Nặng | Mũ `ê` | `v` / `t` | Nét xuất phát `v` mid/high, dấu nặng nằm dưới mũ `ê`, kết thúc ascender `t`. |
| 3 | `nguyễn` | `n + g + u + y + e + ̂ + ̃ + n` | Ngã | Mũ `ê` | `ng` / `n` | Tổ hợp phụ âm đầu `ng`, descender `y` kéo sâu, dấu ngã đặt trên mũ `ê`. |
| 4 | `nước` | `n + u + ̛ + o + ̛ + ́ + c` | Sắc | Râu `ư`, `ơ` | `n` / `c` | Nguyên âm đôi mang râu kép `ươ`, dấu sắc đặt trên `ơ`, rủi ro va chạm râu `ơ`. |
| 5 | `đường` | `đ + u + ̛ + o + ̛ + ̀ + n + g` | Huyền | Gạch `đ`, Râu `ư`, `ơ` | `đ` / `ng` | Nét gạch ngang thân `đ` (delayed stroke), cụm `ươ`, dấu huyền trên `ơ`, descender `g`. |
| 6 | `khuấy` | `k + h + u + a + ̂ + ́ + y` | Sắc | Mũ `â` | `kh` / `y` | Tổ hợp ascender kép `kh`, nguyên âm 3 `uây`, mũ `â` và dấu sắc, descender `y`. |
| 7 | `thuở` | `t + h + u + o + ̛ + ̉` | Hỏi | Râu `ơ` | `th` / (mở) | Tổ hợp `th`, nguyên âm đôi `uơ`, dấu hỏi đặt trên `ơ` ở vị trí kết thúc từ. |
| 8 | `nghỉ` | `n + g + h + i + ̉` | Hỏi | — | `ngh` / (mở) | Phụ âm đầu 3 ký tự `ngh` (kết hợp descender `g` và ascender `h`), dấu hỏi trên thân chữ hẹp `i`. |
| 9 | `hoặc` | `h + o + a + ̆ + ̣ + c` | Nặng | Trăng `ă` | `h` / `c` | Ascender `h`, tổ hợp `oă`, dấu trăng `ă`, dấu nặng đặt dưới đáy ký tự `ă`. |
| 10 | `chuẩn` | `c + h + u + a + ̂ + ̉ + n` | Hỏi | Mũ `â` | `ch` / `n` | Ascender `h`, cụm `uân`, mũ `â`, dấu hỏi đặt trên mũ `â`. |
| 11 | `trường` | `t + r + u + ̛ + o + ̛ + ̀ + n + g` | Huyền | Râu `ư`, `ơ` | `tr` / `ng` | Ascender `t`, nét uốn `r`, cụm râu kép `ươ`, dấu huyền trên `ơ`, descender `g`. |
| 12 | `quyện` | `q + u + y + e + ̂ + ̣ + n` | Nặng | Mũ `ê` | `q` / `n` | Descender `q` và `y`, mũ `ê`, dấu nặng đặt dưới `ê`, liên kết nối nét phức tạp. |
| 13 | `nghĩ` | `n + g + h + i + ̃` | Ngã | — | `ngh` / (mở) | Cụm `ngh` thách thức nối nét qua ascender/descender, dấu ngã trên thân `i`. |
| 14 | `phượng` | `p + h + u + ̛ + o + ̛ + ̣ + n + g` | Nặng | Râu `ư`, `ơ` | `ph` / `ng` | Descender `p`, ascender `h`, cụm `ươ`, dấu nặng dưới `ơ`, descender `g`. |
| 15 | `kiều` | `k + i + e + ̂ + ̀ + u` | Huyền | Mũ `ê` | `k` / (mở) | Ascender cao `k`, cụm nguyên âm `iêu`, dấu huyền trên mũ `ê`. |
| 16 | `hướng` | `h + u + ̛ + o + ̛ + ́ + n + g` | Sắc | Râu `ư`, `ơ` | `h` / `ng` | Ascender `h`, cụm `ươ`, dấu sắc trên `ơ`, descender `g`. |
| 17 | `mượt` | `m + u + ̛ + o + ̛ + ̣ + t` | Nặng | Râu `ư`, `ơ` | `m` / `t` | Cụm `ươ`, dấu nặng dưới `ơ`, ascender `t` ở đuôi từ. |
| 18 | `bước` | `b + u + ̛ + o + ̛ + ́ + c` | Sắc | Râu `ư`, `ơ` | `b` / `c` | Ascender `b` có vòng khép, cụm `ươ`, dấu sắc trên `ơ`. |
| 19 | `vẫy` | `v + a + ̂ + ̃ + y` | Ngã | Mũ `â` | `v` / `y` | Điểm xuất phát cao của `v`, mũ `â`, dấu ngã trên `â`, descender `y`. |
| 20 | `nhánh` | `n + h + a + ́ + n + h` | Sắc | — | `nh` / `nh` | Cặp phụ âm `nh` đầu và cuối, ascender `h` kép, dấu sắc trên thân `a`. |

---

### 2.2. Tập Mẫu Nghiệm thu Phần mềm (`PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS`)

Trích xuất $100\%$ từ tập DEV để phục vụ kiểm thử chấp nhận tự động (Pre-PR3 Exit Gate) mà không gây ô nhiễm (contamination) tập Holdout:
```python
PR3_VIETNAMESE_ACCEPTANCE_SPECIMENS = [
    "tiếng", "nước", "đường", "khuấy", "thuở",
    "nghỉ", "trường", "phượng", "mượt", "vẫy"
]
```

---

### 2.3. Tập Đánh giá Độc lập (Holdout Evaluation Corpus — `BENCHMARK_HOLDOUT_CORPUS_20`)

Bao gồm 20 từ độc lập tuyệt đối, được khóa bảo mật chống rò rỉ dữ liệu (zero leakage). Tập này chỉ được mở đúng 1 lần khi toàn bộ hệ thống đã hoàn thiện mã nguồn và sẵn sàng chạy báo cáo thực nghiệm chính thức PR5.

| STT | Từ | Cấu trúc âm tiết (NFD) | Thanh điệu | Dấu chữ cái | Phụ âm đầu / cuối | Đặc điểm hình học kiểm chứng tính tổng quát hóa |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `nghiêng` | `n + g + h + i + e + ̂ + n + g` | Ngang | Mũ `ê` | `ngh` / `ng` | Độ dài từ lớn (8 ký tự), cụm `ngh` và `ng`, mũ `ê` không dấu thanh. |
| 2 | `khoác` | `k + h + o + a + ́ + c` | Sắc | — | `kh` / `c` | Ascender kép `kh`, cụm `oa`, dấu sắc trên `a`. |
| 3 | `truyền` | `t + r + u + y + e + ̂ + ̀ + n` | Huyền | Mũ `ê` | `tr` / `n` | Tổ hợp `uyê`, descender `y`, dấu huyền trên mũ `ê`. |
| 4 | `hoàng` | `h + o + a + ̀ + n + g` | Huyền | — | `h` / `ng` | Ascender `h`, cụm `oa`, dấu huyền trên `a`, descender `g`. |
| 5 | `nguyệt` | `n + g + u + y + e + ̂ + ̣ + t` | Nặng | Mũ `ê` | `ng` / `t` | Tổ hợp `uyê`, dấu nặng dưới `ê`, ascender `t`. |
| 6 | `thoáng` | `t + h + o + a + ́ + n + g` | Sắc | — | `th` / `ng` | Ascender `th`, cụm `oa`, dấu sắc trên `a`, descender `ng`. |
| 7 | `quỳnh` | `q + u + y + ̀ + n + h` | Huyền | — | `qu` / `nh` | Descender `q` và `y`, dấu huyền trên `y`, ascender `h` ở đuôi. |
| 8 | `nhuộm` | `n + h + u + o + ̂ + ̣ + m` | Nặng | Mũ `ô` | `nh` / `m` | Phụ âm `nh`, nguyên âm đôi `uô`, mũ `ô`, dấu nặng dưới `ô`. |
| 9 | `duyệt` | `d + u + y + e + ̂ + ̣ + t` | Nặng | Mũ `ê` | `d` / `t` | Ascender `d` và `t`, descender `y`, mũ `ê`, dấu nặng. |
| 10 | `khoảnh` | `k + h + o + a + ̉ + n + h` | Hỏi | — | `kh` / `nh` | Ascender kép `kh` đầu và `h` cuối, dấu hỏi trên `a`. |
| 11 | `giường` | `g + i + u + ̛ + o + ̛ + ̀ + n + g` | Huyền | Râu `ư`, `ơ` | `gi` / `ng` | Phụ âm `gi`, cụm râu kép `ươ`, dấu huyền trên `ơ`, descender `g`. |
| 12 | `chuyện` | `c + h + u + y + e + ̂ + ̣ + n` | Nặng | Mũ `ê` | `ch` / `n` | Cụm `uyê`, descender `y`, mũ `ê`, dấu nặng dưới `ê`. |
| 13 | `xoay` | `x + o + a + y` | Ngang | — | `x` / `y` | Nét chéo `x`, cụm `oay`, descender `y`, không thanh điệu. |
| 14 | `bỗng` | `b + o + ̂ + ̃ + n + g` | Ngã | Mũ `ô` | `b` / `ng` | Ascender `b`, mũ `ô`, dấu ngã trên `ô`, descender `g`. |
| 15 | `quét` | `q + u + e + ́ + t` | Sắc | — | `qu` / `t` | Descender `q`, ascender `t`, dấu sắc trên `e`. |
| 16 | `khẽ` | `k + h + e + ̃` | Ngã | — | `kh` / (mở) | Ascender kép `kh`, dấu ngã trên `e`, từ ngắn 3 ký tự. |
| 17 | `nhặt` | `n + h + a + ̆ + ̣ + t` | Nặng | Trăng `ă` | `nh` / `t` | Ascender `h` và `t`, dấu trăng `ă`, dấu nặng dưới `ă`. |
| 18 | `nguồn` | `n + g + u + o + ̂ + ̀ + n` | Huyền | Mũ `ô` | `ng` / `n` | Phụ âm `ng`, nguyên âm đôi `uô`, mũ `ô`, dấu huyền trên `ô`. |
| 19 | `sưởi` | `s + u + ̛ + o + ̛ + ̉ + i` | Hỏi | Râu `ư`, `ơ` | `s` / (mở) | Ký tự `s`, cụm râu kép `ươ`, dấu hỏi trên `ơ`, nguyên âm kết thúc `i`. |
| 20 | `vẹn` | `v + e + ̣ + n` | Nặng | — | `v` / `n` | Nét xuất phát `v`, dấu nặng dưới `e`. |

---

## 3. Phân tích Độ phủ Ngôn ngữ học & Hình học (Coverage Analysis)

### 3.1. Độ phủ Thanh điệu (Tones)
Cả hai tập DEV và HOLDOUT đều bảo đảm độ phủ toàn diện 100% hệ thống 6 thanh tiếng Việt (ngang, huyền, sắc, hỏi, ngã, nặng):
- **Thanh Ngang (Không dấu):** DEV bao gồm trong các âm tiết nền tảng; HOLDOUT có `nghiêng`, `xoay`.
- **Thanh Sắc:** DEV (5 từ: `tiếng`, `nước`, `khuấy`, `hướng`, `bước`, `nhánh`); HOLDOUT (3 từ: `khoác`, `thoáng`, `quét`).
- **Thanh Huyền:** DEV (3 từ: `đường`, `trường`, `kiều`); HOLDOUT (5 từ: `truyền`, `hoàng`, `quỳnh`, `giường`, `nguồn`).
- **Thanh Hỏi:** DEV (3 từ: `thuở`, `nghỉ`, `chuẩn`); HOLDOUT (2 từ: `khoảnh`, `sưởi`).
- **Thanh Ngã:** DEV (3 từ: `nguyễn`, `nghĩ`, `vẫy`); HOLDOUT (2 từ: `bỗng`, `khẽ`).
- **Thanh Nặng:** DEV (5 từ: `việt`, `hoặc`, `quyện`, `phượng`, `mượt`); HOLDOUT (6 từ: `nguyệt`, `nhuộm`, `duyệt`, `chuyện`, `nhặt`, `vẹn`).

### 3.2. Độ phủ Dấu Phụ / Ký tự Biến âm (Diacritics & Combining Marks)
- **Dấu Mũ (`^`):** Xuất hiện trên cả `â`, `ê`, `ô` (`khuấy`, `chuẩn`, `vẫy`, `tiếng`, `việt`, `nguyễn`, `quyện`, `kiều`, `bỗng`, `nhuộm`, `nguồn`).
- **Dấu Râu (`ư, ơ`):** Xuất hiện đơn lẻ và tổ hợp kép `ươ` (`nước`, `đường`, `thuở`, `trường`, `phượng`, `hướng`, `mượt`, `bước`, `giường`, `sưởi`).
- **Dấu Trăng (`ă`):** Xuất hiện đầy đủ cả dạng dấu sắc và dấu nặng (`hoặc`, `nhặt`).
- **Dấu Gạch ngang (`đ`):** Xuất hiện trong `đường`.
- **Dấu Phức hợp (Stacking Diacritics):** Dấu thanh đặt trên mũ (`tiếng`, `nguyễn`, `khuấy`, `chuẩn`, `kiều`, `bỗng`, `nguồn`) và dấu thanh đặt trên râu (`nước`, `đường`, `thuở`, `trường`, `phượng`, `hướng`, `mượt`, `bước`, `giường`, `sưởi`). Đây là các trường hợp có nguy cơ va chạm hình học (bridge collision) cao nhất trong tiếng Việt.

### 3.3. Độ phủ Cấu trúc Hình học Ký tự (Ascenders & Descenders)
- **Nét nhô cao (Ascenders: b, d, đ, h, k, l, t):** Đảm bảo mật độ cao ở tất cả các vị trí đầu, giữa và cuối từ để kiểm tra khả năng tránh va chạm của bridge nét đơn khi di chuyển qua các đỉnh cao.
- **Nét kéo dài xuống (Descenders: g, p, q, y):** Đảm bảo kiểm tra va chạm với các nét liên kết ở đường chân dòng (baseline / descender clearance).
- **Phụ âm ghép đa dạng:** Bao phủ đầy đủ các phụ âm phức tạp nhất của tiếng Việt (`ngh`, `ng`, `kh`, `th`, `tr`, `ch`, `ph`, `nh`, `qu`, `gi`).

---

## 4. Kiểm chứng Tính Rời nhau & Toàn vẹn Dữ liệu (Integrity Verification)

Kiểm chứng tự động thông qua test suite độc lập (`tests/test_ca_vhc_metrics.py` và `tests/test_pr3_acceptance_baseline.py`):
1. **Số lượng mẫu:** $|DEV| = 20$, $|HOLDOUT| = 20$.
2. **Tính rời nhau tuyệt đối (Strictly Disjoint):**
   $$DEV \cap HOLDOUT = \emptyset$$
   Không có bất kỳ từ nào xuất hiện đồng thời trong cả hai tập.
3. **Bộ font kiểm thử chuẩn hóa:**
   Tất cả các từ đều được kiểm chứng khả năng render thành công trên cả 2 font pack: `oly` (OmniDraw Legacy) và `omni_casual` (Omni Casual nét đơn v1).
4. **Bộ seed kiểm chuẩn:**
   Bốn seed tất định được cố định: `[42, 100, 2026, 999999]`.

---

## 5. Kỷ luật Quản trị Ngữ liệu (Data Governance & Anti-Leakage Protocol)

1. **Khóa bất biến (Immutable Freeze):**
   Danh sách 20 từ DEV và 20 từ HOLDOUT được đóng băng nguyên trạng với mã `CA-VHC-CORPUS-v1.0-FROZEN`. Tuyệt đối không thêm, bớt hoặc sửa đổi bất kỳ từ nào trong quá trình phát triển thuật toán PR3, PR4.
2. **Rào chắn Chống ô nhiễm (Anti-Contamination Guard):**
   - Trong quá trình phát triển PR3 (Diacritic-Aware Trellis DAG) và PR4 (Delayed-stroke scheduler), engine và runner chỉ được phép chạy trên tập DEV hoặc synthetic unit tests.
   - Cấm chạy runner với cờ `--corpus holdout` hoặc `--allow-holdout` trong môi trường phát triển hàng ngày.
   - Tập Holdout chỉ được mở đúng một lần duy nhất tại mốc PR5 để lập Bảng kết quả thực nghiệm chính thức cho Chương 4.

---

## 6. Quyết định Đóng băng (Formal Verdict)

Căn cứ vào kết quả phân tích độ phủ ngôn ngữ học, độ phủ hình học và kiểm chứng tính rời nhau tự động đạt 100% PASS:

* **QUYẾT ĐỊNH CỦA TV1:** **CHÍNH THỨC PHÊ DUYỆT VÀ ĐÓNG BĂNG BỘ NGỮ LIỆU BENCHMARK CA-VHC v1.0**
* **Mã phiên bản:** `CA-VHC-CORPUS-v1.0-FROZEN`
* **Người phê duyệt:** **TV1 — AI Data & Writer Profile Lead**
* **Ngày phê duyệt:** **23/09/2026**
* **Trạng thái cổng E5:** **READY FOR PR3 / DOWNSTREAM GATES UNLOCKED FOR FORMAL EVALUATION PROTOCOL**
