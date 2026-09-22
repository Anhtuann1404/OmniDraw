# OmniDraw — Tiêu Chí Nghiệm Thu Trước PR3 (Pre-PR3 Acceptance Contract)
*(Hợp đồng Nghiệm thu Kỹ thuật cho CA-VHC Diacritic-Aware Trellis DAG)*

```text
═══════════════════════════════════════════════════════════════════════════════════════════
                           PR3 PRE-IMPLEMENTATION ACCEPTANCE CONTRACT
═══════════════════════════════════════════════════════════════════════════════════════════
• PR3 ACCEPTANCE CONTRACT:     DEFINED
• PR3 IMPLEMENTATION:         NOT STARTED
• PR3 ENTRY GATE:             WAITING FOR E4 (TV2+TV4 Shared Interface Agreement)
• FORMAL EXPERIMENT READINESS: NO (Acceptance suite uses DEV only; pending TV1 & TV3 gates)
═══════════════════════════════════════════════════════════════════════════════════════════
```

## Material Passport

- **Origin Skill:** `academic-research-suite / experiment-agent`
- **Origin Mode:** `plan`
- **Origin Date:** `2026-09-22`
- **Verification Status:** `VERIFIED` *(chỉ đối với logic nghiệm thu phần mềm; hiệu chuẩn vật lý vẫn pending)*
- **Version Label:** `pr3_acceptance_contract_v2`
- **Evidence Boundary:** Chỉ xác nhận quy tắc phân loại hình học và unit test phần mềm; không xác nhận độ an toàn cơ học hoặc chất lượng nét trên máy vẽ thật.

---

## 1. Giới thiệu & Mục tiêu (Purpose & Scope)

Tài liệu này xác lập **Hợp đồng Nghiệm thu Kỹ thuật (Acceptance Contract)** chính thức trước khi bắt đầu triển khai mã nguồn cho **PR3 — CA-VHC Diacritic-Aware Trellis** trong hệ thống OmniDraw.

### Mục tiêu cốt lõi:
1. **Xác định Cổng Đầu Vào (Entry Gate):** Các điều kiện tiên quyết bắt buộc phải thỏa mãn trước khi TV4 và TV2 được phép viết dòng code đầu tiên của PR3 vào `backend/handwriting/`.
2. **Khóa Hành vi Cơ sở ASCII / Không Dấu:** Bảo đảm việc bổ sung không gian trạng thái dấu không làm thay đổi hay suy giảm hình học, tính tất định và chất lượng nét vẽ của văn bản không dấu.
3. **Xác định Cổng Xuất Xưởng (Exit Gate):** Danh mục tiêu chí định lượng và chức năng cụ thể để PR3 được phép merge vào nhánh phát triển chính ở cấp phần mềm.
4. **Phân loại Trạng thái Kiểm chứng Rõ ràng:** Tách bạch 4 nhóm trạng thái kiểm tra nhằm ngăn chặn việc công bố sai lệch tiến độ hoặc nhầm lẫn giữa mô phỏng phần mềm và đo đạc vật lý.
5. **Kỷ luật Dữ liệu & Nghiên cứu:** Acceptance suite không lựa chọn, iterate, render hoặc ghi nhận bất kỳ case nào từ `BENCHMARK_HOLDOUT_CORPUS_20`. Tuyệt đối không tạo số liệu thực nghiệm giả hoặc ước lượng cảm tính.

---

## 2. Bốn Trạng Thái Kiểm Chứng (Four Verification States)

Mọi tiêu chí trong hợp đồng nghiệm thu đều được gán nhãn duy nhất thuộc 1 trong 4 trạng thái sau:

| Trạng thái | Ký hiệu | Định nghĩa & Ý nghĩa kỹ thuật |
| :--- | :--- | :--- |
| **Đã Vượt qua Hiện hành** | `PASS_CURRENT` | Tiêu chí đã có mã kiểm thử tự động trong repository và đạt kết quả kiểm tra thành công 100% trên nền mã nguồn hiện tại. |
| **Phụ thuộc PR2** | `PR2_DEPENDENT` | Tiêu chí yêu cầu phải có 3 adapter đối chứng B1, B2, B3 và giao diện chuyển tiếp từ TV2 mới có thể thực hiện kiểm chứng so sánh. |
| **Yêu cầu Mã nguồn PR3** | `PR3_REQUIRED` | Tiêu chí chỉ có thể kiểm chứng sau khi `CompositionState` và thuật toán Trellis DAG nhận biết dấu được hiện thực hóa trong PR3. |
| **Bị Chặn bởi Hiệu chuẩn** | `BLOCKED_CALIBRATION` | Tiêu chí yêu cầu phần cứng máy vẽ vật lý và quy trình hiệu chuẩn đo đạc thực tế của TV3; không thể nghiệm thu chỉ bằng phần mềm giả lập. |

---

## 3. Cổng Đầu Vào PR3 (PR3 Entry Gate Requirements)

Để được phép bắt đầu viết code cho PR3, toàn bộ các điều kiện tiên quyết sau đây phải được thỏa mãn và có bằng chứng xác nhận:

- [x] **E1 — PR1 Hoàn tất & Đóng gói:** Commit `daca566` đã tích hợp đầy đủ hạ tầng thực nghiệm PR1 (`backend/handwriting/experiment_runner.py`, `backend/logs/csv_logger.py`, schema CSV chuẩn 19 cột, kiểm định tính bất biến fixture 160 ca DEV). Toàn bộ automated tests trong hệ thống đạt PASS (`Full automated suite: 67 passed tại lần verification này`).
- [x] **E2 — Khóa Snapshot Hình học ASCII:** Đã sinh và khóa toàn bộ 48 ca kiểm thử hình học cho văn bản ASCII không dấu tại `tests/fixtures/pr3_ascii_baseline_fingerprints.json`, được bảo vệ bởi test tự động `tests/test_pr3_acceptance_baseline.py`.
- [x] **E3 — PR2 Baseline Adapters B1, B2, B3 (TV2 chủ trì) — PASS:** Đã đóng gói độc lập 3 adapter trong `backend/handwriting/baselines.py`, tích hợp runner qua `--method` và khóa bằng `tests/test_ca_vhc_baselines.py`:
  - B1: *Static Glyph Renderer* (dựng chữ tĩnh theo anchor rời).
  - B2: *Greedy Contextual Heuristic* (chọn biến thể tham lam cục bộ).
  - B3: *Current Trellis DAG* (bộ giải Viterbi hiện hành chưa xét ràng buộc dấu nâng cao).
- [ ] **E4 — Thống nhất Giao diện Chuyển tiếp (Shared Interface Agreement):** TV4 và TV2 ký duyệt chữ ký hàm chuyển tiếp `eval_transition(s_prev, s_next)`, cách trích xuất bounding box của dấu trong tọa độ thế giới (`world_bbox`), và hợp đồng tham số cấu hình tập trung `DiacriticConfig`.
- [x] **E5 — Kỷ luật Ngữ liệu (Corpus Integrity):** Acceptance suite không lựa chọn, iterate, render hoặc ghi nhận bất kỳ case nào từ `BENCHMARK_HOLDOUT_CORPUS_20`. Mười mẫu nghiệm thu tiếng Việt được lấy hoàn toàn từ `BENCHMARK_DEV_CORPUS_20`; 48 ca ASCII là technical regression fixture độc lập và không thuộc corpus tiếng Việt. Tuyệt đối không chạy `--corpus holdout`, `--corpus all`, hoặc `--allow-holdout`.

---

## 4. Bảng Tiêu Chí Nghiệm Thu PR3 Cấp Phần Mềm (PR3 Software Exit Gate Criteria)

Dưới đây là ma trận tiêu chí chi tiết để nghiệm thu và sáp nhập (merge) mã nguồn phần mềm PR3:

| ID | Nhóm | Nội dung Tiêu chí | Metric hoặc Bằng chứng | Ngưỡng Nghiệm thu | Trạng thái Hiện tại | Owner |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A1** | A. Bảo toàn ASCII | Bảo toàn 100% hình học nét vẽ cho văn bản ASCII / không dấu | So sánh SHA-256 fingerprint trên 48 ca ma trận ASCII | Khớp chính xác 48/48 ca (0 sai lệch) | `PASS_CURRENT` | TV4 |
| **A2** | A. Bảo toàn ASCII | Tính hợp lệ của cấu trúc SVG và bounding box khi render ASCII | Parse XML SVG qua `xml.etree.ElementTree`, kiểm tra root tag SVG, `is_within_bounds is True`, path `d` không rỗng, không chứa literal `nan`/`inf` trong dữ liệu tọa độ | Đạt chuẩn 48/48 ca ASCII (`test_pr3_ascii_svg_and_bounds_valid`) | `PASS_CURRENT` | TV4 |
| **A3** | A. Bảo toàn ASCII | Strict validation không bị thoái lui (regression) | `backend/test_handwriting_validation.py` | 34/34 tests PASS | `PASS_CURRENT` | TV4 |
| **B1** | B. Không gian Trạng thái | Cấu trúc `CompositionState` kết hợp đúng cặp `(GlyphVariant, DiacriticCandidate)` | Khởi tạo hợp lệ, immutability, world coordinate mapping | Không phát sinh lỗi runtime, schema hợp lệ | `PR3_REQUIRED` | TV4 |
| **B2** | B. Không gian Trạng thái | Khống chế số lượng ứng viên thô và cắt tỉa trạng thái bất hợp lệ | $K_{\text{raw}} \le 9$, loại bỏ ứng viên vi phạm hard-boundary | Số trạng thái hữu hiệu $K_{\text{valid}} \le 9$ tại mỗi bước Trellis | `PR3_REQUIRED` | TV4 |
| **B3** | B. Không gian Trạng thái | Chi phí trạng thái nội tại $C_{\text{state}}$ không tính lặp với chi phí chuyển tiếp | Kiểm thử cô lập hàm mục tiêu và phân tách chi phí | Không có thành phần $J_{\text{transition}}$ bên trong $C_{\text{state}}$ | `PR3_REQUIRED` | TV4 & TV2 |
| **C1** | C. Xử lý Dấu tiếng Việt | Bảo toàn base character và chuỗi combining marks sau Unicode NFD | Mỗi ký tự đầu vào phải ánh xạ đúng base character, đúng thứ tự combining marks và sinh nhóm dấu tương ứng, không mất dấu hoặc chuyển dấu sang ký tự khác (`unicodedata.normalize("NFD", text)`, so sánh base character, ordered combining marks, metadata diacritic stroke) | Đúng 100% cấu trúc NFD và nhóm nét dấu tương ứng trên 10 mẫu DEV nghiệm thu | `PR3_REQUIRED` | TV4 |
| **C2** | C. Xử lý Dấu tiếng Việt | Không có va chạm giữa nét nối (bridge) và dấu thanh/mũ | `collision_count` đo bằng `evaluate_ca_vhc_metrics` | `collision_count == 0` trên 10 mẫu DEV nghiệm thu | `PR3_REQUIRED` | TV4 |
| **C3** | C. Xử lý Dấu tiếng Việt | Khoảng cách an toàn ngòi bút đạt ngưỡng kỹ thuật tối thiểu | `minimum_diacritic_clearance_mm` | $d_{\min} \ge 0.20\,\text{mm}$ (với mọi ca có bridge & dấu) | `PR3_REQUIRED` | TV4 |
| **D1** | D. Tính Tất Định | Tính tất định tuyệt đối theo seed ngẫu nhiên | SHA-256 fingerprint qua 5 lần chạy liên tiếp cùng seed | Khớp 100% fingerprint giữa các lần chạy | `PASS_CURRENT` | TV4 |
| **D2** | D. Tính Tất Định | Không rò rỉ trạng thái nội bộ giữa batch và isolated run | So sánh SHA-256 fingerprint của `"OmniDraw"` giữa render độc lập và render batch (thứ tự xuôi/đảo) | Khớp chính xác fingerprint trên cả 3 trường hợp (`test_pr3_ascii_batch_order_does_not_change_fingerprint`) | `PASS_CURRENT` | TV4 |
| **E1** | E. Tối ưu Chuyển động | Giảm quãng đường nhấc bút ($D_{\text{penup}}$) so với baseline B1 và B2 | Tỷ lệ giảm quãng đường nhấc bút trên tập DEV | Đo đạc định lượng rõ ràng qua runner | `PASS_CURRENT` (PR2 adapters available) | TV2 |
| **E2** | E. Tối ưu Chuyển động | Tích hợp chi phí chuyển tiếp $J_{\text{transition}}$ vào Viterbi DP | Mọi transition cost phải hữu hạn và không âm; trên synthetic trellis nhỏ có nghiệm biết trước, Viterbi phải chọn đường đi có tổng $C_{\text{state}} + J_{\text{transition}}$ nhỏ nhất (PR2 cung cấp interface/components, PR3 tích hợp Trellis) | Viterbi chọn đường đi tối ưu chính xác | `PR3_REQUIRED` | TV2 & TV4 |
| **E3** | E. Tối ưu Chuyển động | Chạy Trellis DAG hoàn tất và an toàn cho toàn bộ tập mẫu nghiệm thu | PR3 chạy hoàn tất trên toàn bộ DEV acceptance specimens, không crash, không sinh giá trị metric NaN, và số `CompositionState` mỗi layer không vượt giới hạn thiết kế $K_{\text{valid}} \le 9$ | Hoàn tất 10/10 mẫu DEV, 0 crash, không NaN metric, $K_{\text{valid}} \le 9$ | `PR3_REQUIRED` | TV4 & TV2 |
| **G1** | G. Kỷ luật Ngữ liệu | Độc lập ngữ liệu: chỉ sử dụng DEV corpus cho nghiệm thu | Kiểm thử `test_pr3_acceptance_specimens_are_dev_only` | Toàn bộ 10 mẫu nghiệm thu $\in \text{DEV}$; không lựa chọn/chạy Holdout | `PASS_CURRENT` | TV4 & TV1 |

---

## 5. Các Cổng Kiểm Định Downstream (Downstream Formal-Experiment & Hardware Gates)

Các tiêu chí và cổng kiểm định dưới đây **KHÔNG chặn việc phát triển hoặc merge mã nguồn phần mềm PR3**, nhưng là điều kiện bắt buộc trước khi chạy thực nghiệm chính thức (PR5 Formal Benchmark) và công bố kết quả khoa học:

```text
═══════════════════════════════════════════════════════════════════════════════════════════
                      TRẠNG THÁI CÁC CỔNG KIỂM ĐỊNH DOWNSTREAM
═══════════════════════════════════════════════════════════════════════════════════════════
• TV1 FORMAL CORPUS FREEZE:            PENDING (Độc lập với PR2; không chặn PR3 software)
• TV3 PHYSICAL CLEARANCE CALIBRATION:  PENDING (Chờ phần cứng máy vẽ vật lý)
• PR5 FORMAL PERFORMANCE BENCHMARK:   PENDING (Triển khai sau khi PR2, PR3, PR4 hoàn tất)
• FORMAL EXPERIMENT READINESS:        NO (Tuyệt đối không chạy holdout trước khi đủ gates)
═══════════════════════════════════════════════════════════════════════════════════════════
```

### 5.1. Downstream PR5 Performance Gate
- **Phạm vi:** Benchmark hiệu năng tính toán chính thức thuộc về PR5.
- **Quy trình chuẩn:** 10 lượt warm-up, sau đó thực hiện $N_{\text{runs}} = 50$ lần lặp cho mỗi cấu hình trên 4 seeds chuẩn `[42, 100, 2026, 999999]`. Báo cáo đồng thời Median và p95 của `optimize_time_ms`.
- **Ngưỡng quy chuẩn (Canonical thresholds từ `docs/05_ca_vhc_research_spec.md`):**
  - **PASS:** $\text{Median} \le 5\,\text{ms}$ và $\text{p95} \le 10\,\text{ms}$.
  - **FAIL:** $\text{Median} > 15\,\text{ms}$ hoặc $\text{p95} > 30\,\text{ms}$.
  - **INCONCLUSIVE:** Mọi trường hợp còn lại ($5\,\text{ms} < \text{Median} \le 15\,\text{ms}$ hoặc $10\,\text{ms} < \text{p95} \le 30\,\text{ms}$).
- **Kỷ luật thực nghiệm:** Tuyệt đối không lấy tốc độ của một máy tính cá nhân đơn lẻ hay một lần đo trung bình đơn lẻ làm điều kiện merge code PR3. Không đặt median/p95 làm unit test. Không chạy formal benchmark trong giai đoạn pre-PR3.

### 5.2. Downstream Hardware Physical Validation Gates (TV3 Lead)
- **F1 — Kiểm chứng vật lý không va chạm / không lem mực:** Đo quang học bản vẽ thật quét ở 600 DPI hoặc sử dụng kính lúp đo lường cơ khí chuyên dụng; xác nhận không có hiện tượng dính nét giữa bridge và dấu khi thi công thực tế. Trạng thái: `BLOCKED_CALIBRATION`. Không chặn PR3 software merge.
- **F2 — Log đo đạc thời gian thi công thực tế:** Thu thập và phân tích trường `actual_draw_time_sec` từ firmware/phần cứng máy vẽ; phân biệt tuyệt đối với thời gian mô phỏng phần mềm. Trạng thái: `BLOCKED_CALIBRATION`. Không chặn PR3 software merge.
- **C4 — Ngưỡng an toàn mục tiêu nghiên cứu:** Xác nhận $d_{\min} \ge 0.50\,\text{mm}$ dựa trên độ nảy ngòi bút và sai số cơ học thực tế của máy vẽ. Trạng thái: `BLOCKED_CALIBRATION`. Không chặn PR3 software merge.

### 5.3. Downstream Corpus Governance Gate (TV1 Lead)
- **TV1 Formal Corpus Freeze:** TV1 rà soát độ phủ ngữ âm học / ngôn ngữ học của ngữ liệu và ký duyệt đóng băng (freeze) phiên bản chính thức của Development Corpus và Holdout Corpus.
- **Ranh giới:** Cổng này hoàn toàn độc lập với PR2, không chặn việc viết hoặc merge mã nguồn PR3, nhưng là điều kiện tiên quyết bắt buộc trước khi mở khóa chạy benchmark chính thức.

---

## 6. Quy Chuẩn Đánh Giá Ngưỡng Khoảng Cách An Toàn (Clearance Interpretation)

Khoảng cách an toàn giữa nét nối (bridge) và nét dấu (diacritic) được tính bằng hàm `minimum_diacritic_clearance_mm` trong `metrics_evaluator.py`. Kết luận kỹ thuật được phân tầng nghiêm ngặt như sau:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        QUY CHUẨN ĐÁNH GIÁ KHOẢNG CÁCH AN TOÀN                          │
├───────────────────────────────┬──────────────────────┬─────────────────────────────────┤
│ ĐIỀU KIỆN HÌNH HỌC            │ PHÁN QUYẾT KỸ THUẬT  │ Ý NGHĨA HỌC THUẬT & CÔNG NGHỆ   │
├───────────────────────────────┼──────────────────────┼─────────────────────────────────┤
│ collision_count > 0 HOẶC      │                      │ Vi phạm kích thước ngòi bút cơ  │
│ d_min < 0.20 mm               │ FAIL                 │ sở (0.20mm); nét bị dính/lem.   │
├───────────────────────────────┼──────────────────────┼─────────────────────────────────┤
│ collision_count == 0 VÀ       │                      │ Đạt mức an toàn kỹ thuật ban    │
│ 0.20 mm <= d_min < 0.50 mm    │ INCONCLUSIVE         │ đầu trong DiacriticConfig;      │
│                               │                      │ chờ TV3 hiệu chuẩn máy thật.    │
├───────────────────────────────┼──────────────────────┼─────────────────────────────────┤
│ collision_count == 0 VÀ       │ PASS                 │ Đạt mục tiêu nghiên cứu an toàn │
│ d_min >= 0.50 mm              │ (PROVISIONAL TARGET) │ tối ưu; xác nhận sau hiệu chuẩn.│
├───────────────────────────────┼──────────────────────┼─────────────────────────────────┤
│ Từ không có bridge hoặc dấu   │                      │ Không dùng trường hợp này để    │
│ (d_min == inf)                │ NOT_APPLICABLE       │ tuyên bố đạt tiêu chuẩn an toàn.│
└───────────────────────────────┴──────────────────────┴─────────────────────────────────┘
```

### 6.1. Quy tắc thực thi và nguồn sự thật

- Hàm phân loại thực thi: `backend/handwriting/metrics_evaluator.py::classify_diacritic_clearance_acceptance`.
- Ngưỡng phần mềm được đặt tên tập trung trong evaluator:
  - `DIACRITIC_CLEARANCE_TECHNICAL_MIN_MM = 0.20`.
  - `DIACRITIC_CLEARANCE_PROVISIONAL_TARGET_MM = 0.50`.
- Các ngưỡng trên là **ranh giới phán quyết đo lường**, không phải tham số sinh hình học. Khi PR3 triển khai, `DiacriticConfig` vẫn là nguồn sở hữu tham số render.
- `evaluate_ca_vhc_metrics` phải giữ full precision cho `minimum_diacritic_clearance_mm`; chỉ lớp xuất CSV/UI được làm tròn để trình bày. Không được phân loại lại từ một giá trị đã làm tròn.
- Mã phán quyết máy đọc được gồm `FAIL`, `INCONCLUSIVE`, `PASS_PROVISIONAL_TARGET`, `NOT_APPLICABLE`.
- `PASS_PROVISIONAL_TARGET` chỉ khẳng định hình học phần mềm đạt mục tiêu tạm thời; không được diễn giải thành an toàn vật lý trước khi TV3 hiệu chuẩn.
- Dữ liệu metric sai (`NaN`, khoảng cách âm, boolean, chuỗi số, collision count âm/sai kiểu hoặc ngưỡng cấu hình mâu thuẫn) phải fail closed bằng `ValueError`, không được tự động biến thành `PASS` hay `NOT_APPLICABLE`.
- Unit test khóa đúng các điểm biên `0.199`, `0.20`, `0.499`, `0.50`, hai ca sát biên `0.1996`/`0.4996`, trường hợp có va chạm và trường hợp không có cặp bridge–diacritic hợp lệ.

---

## 7. Danh Mục Ngữ Liệu Kiểm Chuẩn & Mẫu Nghiệm Thu (Specimen Sets)

### 7.1. Ma trận Kiểm chuẩn ASCII Cơ sở (ASCII Baseline Matrix — 48 trường hợp)
Dùng để bảo đảm tính tương thích ngược và không làm suy thoái hình học văn bản không dấu.

- **6 từ ngữ liệu:** `"OmniDraw"`, `"plotter"`, `"vector"`, `"minimum"`, `"connection"`, `"handwriting"`.
- **2 font packs:** `"oly"`, `"omni_casual"`.
- **4 seeds chuẩn:** `42`, `100`, `2026`, `999999`.
- **1 phong cách viết:** `"hand_hocsinh"`.
- **Tổng số trường hợp:** $6 \times 2 \times 4 = 48$ bản ghi.
- **Tập tin lưu trữ:** [`tests/fixtures/pr3_ascii_baseline_fingerprints.json`](../tests/fixtures/pr3_ascii_baseline_fingerprints.json).
- **Mã kiểm thử tự động:** [`tests/test_pr3_acceptance_baseline.py`](../tests/test_pr3_acceptance_baseline.py).

### 7.2. Tập Mẫu Nghiệm thu Dấu Tiếng Việt (Vietnamese Acceptance Specimen Set — 10 từ DEV)
Dùng để đánh giá độ chính xác của cơ chế định vị dấu và triệt tiêu va chạm bridge sau khi PR3 hoàn tất.

$$\mathcal{S}_{\text{PR3}} = \{\text{"tiếng"}, \text{"nước"}, \text{"đường"}, \text{"khuấy"}, \text{"thuở"}, \text{"nghỉ"}, \text{"trường"}, \text{"phượng"}, \text{"mượt"}, \text{"vẫy"}\}$$

- **Nguồn gốc:** Trích xuất $100\%$ từ `BENCHMARK_DEV_CORPUS_20` (thuộc tập phát triển do TV1 quản lý).
- **Kỷ luật Holdout:** Acceptance suite không lựa chọn, iterate, render hoặc ghi nhận bất kỳ case nào từ `BENCHMARK_HOLDOUT_CORPUS_20`. Mười mẫu nghiệm thu tiếng Việt chỉ sử dụng tập DEV; 48 ca ASCII là technical regression fixture độc lập, không phải thành phần của DEV hoặc Holdout corpus tiếng Việt.
- **Ghi chú kỹ thuật:** Ở thời điểm hiện tại, **chưa khóa fingerprint hình học** cho 10 từ tiếng Việt này, bởi vì PR3 được thiết kế chủ đích nhằm điều chỉnh và dịch chuyển vị trí dấu để triệt tiêu va chạm; việc khóa snapshot trước khi sửa thuật toán là không có ý nghĩa khoa học.

---

## 8. Bảng Ánh Xạ Truy Xuất Kiểm Thử (Test Suite Traceability Matrix)

| Tiêu chí | Mã kiểm thử trong Repository | Tập tin mã nguồn kiểm thử | Trạng thái hiện hành |
| :--- | :--- | :--- | :--- |
| **A1** | `test_pr3_ascii_fixture_has_exact_declared_matrix`<br>`test_pr3_ascii_baseline_fingerprints_match_current_engine` | `tests/test_pr3_acceptance_baseline.py` | `PASS` |
| **A2** | `test_pr3_ascii_svg_and_bounds_valid` | `tests/test_pr3_acceptance_baseline.py` | `PASS` |
| **A3** | `TestHandwritingStrictValidation` (34 tests) | `backend/test_handwriting_validation.py` | `PASS` |
| **D1** | `test_pr3_ascii_seed_determinism` | `tests/test_pr3_acceptance_baseline.py` | `PASS` |
| **D2** | `test_pr3_ascii_batch_order_does_not_change_fingerprint` | `tests/test_pr3_acceptance_baseline.py` | `PASS` |
| **G1** | `test_pr3_acceptance_specimens_are_dev_only` | `tests/test_pr3_acceptance_baseline.py` | `PASS` |
| **C2, C3** | `test_metrics_evaluator_calculates_all_required_keys`<br>`test_bridge_diacritic_clearance_computation`<br>`test_diacritic_clearance_acceptance_boundaries`<br>`test_diacritic_clearance_acceptance_rejects_invalid_metrics` | `tests/test_ca_vhc_metrics.py` | `PASS` (Metric engine + executable verdict boundaries) |
| **E1** | `test_runner_builds_reproducible_geometry_row`<br>`test_pr1_dev_geometry_matches_frozen_baseline`<br>`test_runner_executes_and_labels_each_baseline` | `tests/test_ca_vhc_experiment_runner.py`<br>`tests/test_ca_vhc_baselines.py` | `PASS_CURRENT` (Runner + B1/B2/B3 adapters) |
| **B1, B2, B3** | *(Dự kiến PR3)* `test_composition_state_generation`<br>`test_trellis_dag_candidate_pruning` | `tests/test_ca_vhc_composition_state.py` | `PENDING PR3` |
| **C1** | *(Dự kiến PR3)* `test_pr3_vietnamese_unicode_nfd_mark_preservation` | `tests/test_pr3_vietnamese_acceptance.py` | `PENDING PR3` |
| **C2, C3** | *(Dự kiến PR3)* `test_pr3_vietnamese_zero_collision`<br>`test_pr3_vietnamese_clearance_threshold` | `tests/test_pr3_vietnamese_acceptance.py` | `PENDING PR3` |
| **E2** | *(Dự kiến PR3)* `test_viterbi_synthetic_trellis_optimality` | `tests/test_pr3_vietnamese_acceptance.py` | `PENDING PR3` |
| **E3** | *(Dự kiến PR3)* `test_pr3_trellis_dev_specimens_run_safely` | `tests/test_pr3_vietnamese_acceptance.py` | `PENDING PR3` |
| **F1, F2, C4** | *(Downstream TV3)* Kiểm chuẩn vật lý trên máy vẽ thật | Telemetry phần cứng / quét quang học 600 DPI | `BLOCKED_CALIBRATION` (Không chặn PR3 software merge) |
| **TV1 Freeze** | *(Downstream TV1)* Rà soát & ký duyệt đóng băng ngữ liệu | Biên bản nghiệm thu ngữ liệu TV1 | `PENDING` (Không chặn PR3 software merge) |
| **PR5 Perf** | *(Downstream PR5)* Benchmark thống kê (10 warm-up, 50 lặp) | Runner ma trận thống kê median/p95 | `PENDING` (Không chặn PR3 software merge) |
