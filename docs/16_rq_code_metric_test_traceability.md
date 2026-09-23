# OmniDraw — Ma trận Truy vết RQ–Code–Metric–Test

## Material Passport

| Trường | Giá trị |
| :--- | :--- |
| Material ID | `OMNIDRAW-RQ-TRACE-v0.1` |
| Loại tài liệu | Working traceability artifact / experiment-readiness map |
| Ngày đối chiếu | 22/09/2026 |
| Code snapshot đã kiểm tra | `cda92eb` |
| Review target hiện hành | Xem `REVIEW_TARGET_COMMIT` tại [`reviews/README.md`](reviews/README.md) |
| Verification status | `ANALYZED_WITH_TARGETED_TESTS` |
| Phạm vi | CA-VHC P0: RQ1–RQ3, giả thuyết H1.1–H3.2, hạ tầng metric và các gate phần mềm/phần cứng |
| Ngoài phạm vi | Không công bố kết quả; không mở Holdout; không sửa Chương 1–3 đang review; không xác nhận hiệu quả thuật toán chưa triển khai |

> [!IMPORTANT]
> Đây là tài liệu truy vết hỗ trợ review; chỉ thuộc vòng review khi được liệt kê trong phạm vi của gói hiện hành. Các trạng thái dưới đây mô tả khả năng kiểm chứng hiện tại, không phải kết quả nghiên cứu.

---

## 1. Mục đích và quy tắc đọc

Ma trận trả lời tám câu hỏi cho mỗi giả thuyết:

1. Claim nào cần được kiểm chứng?
2. Baseline/phương pháp nào phải được so sánh?
3. Metric nào tạo ra bằng chứng?
4. Module nào sinh metric đó?
5. Test nào đang bảo vệ module?
6. Hiện đã kiểm chứng được tới đâu?
7. Gate nào còn thiếu trước formal experiment?
8. Ai chịu trách nhiệm đóng gate?

### 1.1. Nhãn trạng thái bằng chứng

| Nhãn | Ý nghĩa |
| :--- | :--- |
| `VERIFIED_INFRASTRUCTURE` | Code/hạ tầng đo đã tồn tại và test tương ứng PASS; không đồng nghĩa giả thuyết đã được chứng minh. |
| `PARTIAL` | Một phần chuỗi đo đã có, nhưng thiếu baseline, phương pháp đề xuất, aggregation hoặc corpus/gate chính thức. |
| `PLANNED` | Chỉ mới có đặc tả/thiết kế; chưa có implementation và test production. |
| `BLOCKED_EXTERNAL` | Phụ thuộc dữ liệu hoặc phần cứng ngoài codebase hiện tại. |
| `NOT_APPLICABLE` | Metric không áp dụng cho mẫu cụ thể; ví dụ clearance bằng `inf` khi không có cặp bridge–diacritic. |

Không được đổi một hàng thành `VERIFIED_INFRASTRUCTURE` chỉ vì tài liệu thiết kế đã được duyệt. Không được đổi một giả thuyết thành PASS/FAIL/INCONCLUSIVE trước formal experiment.

---

## 2. Bản đồ artifact hiện hành

| Lớp | Artifact hiện có | Bằng chứng hiện tại | Giới hạn |
| :--- | :--- | :--- | :--- |
| Render/DP hiện hành | [`backend/handwriting/engine.py`](../backend/handwriting/engine.py): `GlyphVariant`, `eval_transition()`, `optimize_word_dag()`, `text_to_strokes_structured()` | Trellis hiện hành, structured trace và `optimize_time_ms` đã có | Node vẫn là `GlyphVariant`; dấu còn hậu xử lý, chưa có `CompositionState` production |
| Metric nội bộ | [`backend/handwriting/metrics_evaluator.py`](../backend/handwriting/metrics_evaluator.py): `evaluate_ca_vhc_metrics()` | Sinh 7 metric tối thiểu và stroke counts | `collision_count` hiện chỉ đếm cặp bridge–diacritic; chưa có acute-turn/C1/bounds diagnostics đầy đủ |
| Runner | [`backend/handwriting/experiment_runner.py`](../backend/handwriting/experiment_runner.py) | Ma trận corpus × font × seed; CSV 19 cột; chống ghi đè; khóa Holdout bằng xác nhận tường minh | Chỉ chạy `METHOD_TAG = "b3_current_trellis"`; chưa chạy B1, B2 hoặc Proposed; chưa có warm-up/repeat/median/p95 |
| Corpus kỹ thuật | [`backend/handwriting/benchmark_fixtures.py`](../backend/handwriting/benchmark_fixtures.py) | DEV 20, Holdout 20, 2 font, 4 seed; hai corpus rời nhau | Chưa phải formal corpus cho đến khi TV1 review/freeze |
| CSV | [`backend/logs/csv_logger.py`](../backend/logs/csv_logger.py) | Kiểm tra schema nhất quán và ghi dòng deterministic | Internal research schema chưa tự động trở thành public API contract |
| Regression fixtures | [`tests/fixtures/ca_vhc_pr1_fingerprints.json`](../tests/fixtures/ca_vhc_pr1_fingerprints.json), [`tests/fixtures/pr3_ascii_baseline_fingerprints.json`](../tests/fixtures/pr3_ascii_baseline_fingerprints.json) | Khóa 160 DEV cases và 48 ASCII cases | Fingerprint bảo vệ hình học, không chứng minh chất lượng hoặc hiệu năng |
| Metric tests | [`tests/test_ca_vhc_metrics.py`](../tests/test_ca_vhc_metrics.py) | Collision, clearance, curvature, trace, corpus disjointness và compatibility | Chủ yếu là unit/synthetic evidence; chưa phải formal comparative experiment |
| Runner tests | [`tests/test_ca_vhc_experiment_runner.py`](../tests/test_ca_vhc_experiment_runner.py), [`tests/test_ca_vhc_baselines.py`](../tests/test_ca_vhc_baselines.py) | Reproducibility, CSV schema, overwrite guard, Holdout guard, frozen DEV snapshot; B1/B2/B3 method-tag execution | Ba baseline PR2 đã có; parity với Proposed còn chờ PR3, formal comparison còn chờ downstream gates |
| Pre-PR3 tests | [`tests/test_pr3_acceptance_baseline.py`](../tests/test_pr3_acceptance_baseline.py) | ASCII fingerprint, seed determinism, bounds/SVG, batch-order independence, DEV-only scope | Là precondition/regression lock; không phải PR3 exit evidence |

---

## 3. Ma trận truy vết chính

| RQ / giả thuyết | Claim cần kiểm chứng | Baseline / phương pháp | Metric chính | Producer hiện tại | Test/bằng chứng hiện có | Trạng thái hiện tại | Phần còn thiếu trước kết luận | Owner / gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RQ1 / H1.1** | Proposed giảm quãng đường pen-up so với B1 và B2 | B1, B2, Proposed | `pen_lift_distance_mm`; % thay đổi vs baseline | `evaluate_ca_vhc_metrics()`; runner ghi CSV | Reproducibility row và frozen B3 DEV geometry PASS | `PARTIAL` | B1/B2 adapters; Proposed PR3/PR4; input parity; aggregation theo corpus; formal PR5 | TV2: PR2/PR4; TV4: PR3/PR5; TV1: corpus freeze |
| **RQ1 / H1.2** | Proposed giảm số lần nhấc bút so với B1 | B1, Proposed | `pen_lift_count`; % thay đổi vs B1 | `evaluate_ca_vhc_metrics()` | Unit/runner contract có metric; chưa có comparative test | `PARTIAL` | B1 adapter; định nghĩa stroke continuity thống nhất giữa methods; Proposed; formal aggregation | TV2 + TV4; PR2–PR5 |
| **RQ1 / H1.3** | Proposed không làm tổng chiều dài nét tiếp xúc giấy tăng quá ngưỡng | B1, Proposed | `total_path_length_mm`; % tăng vs B1 | `evaluate_ca_vhc_metrics()` | Fingerprint/metric reproducibility và regression snapshot PASS | `PARTIAL` | B1 adapter; Proposed; parity về font/style/seed; formal PR5 | TV2: B1; TV4: Proposed/runner |
| **RQ2 / H2.1** | Diacritic-aware Trellis loại bỏ giao cắt bridge–diacritic | B3, Proposed | `collision_count` | `count_bridge_diacritic_collisions()` qua evaluator | Zero-collision, synthetic collision và endpoint-touch tests PASS | `PARTIAL` | `CompositionState`, dấu trong DAG, world-coordinate collision và 10/10 DEV acceptance specimens | TV4 lead PR3; TV2 transition interface |
| **RQ2 / H2.2** | Proposed duy trì clearance tốt hơn B3 và đạt vùng kỹ thuật đã định | B3, Proposed | `minimum_diacritic_clearance_mm` | `compute_diacritic_clearance()` qua evaluator | Known-distance và collision-distance tests PASS | `PARTIAL` | Proposed PR3; quy tắc N/A; aggregation; TV3 calibration trước physical claim | TV4 PR3/PR5; TV3 calibration |
| **RQ3 / H3.1** | Viterbi duy trì median/p95 trong vùng nghiệm thu | B2, B3, Proposed | `optimize_time_ms` median/p95 | `StructuredRenderResult.optimize_time_ms`; evaluator; runner | Giá trị không âm và CSV field đã được test | `PARTIAL` | B2/Proposed; 10 warm-up + 50 repeats; environment metadata; median/p95 reporter | TV2 PR2; TV4 PR3/PR5 |
| **RQ3 / H3.2** | Proposed giảm curvature cost vs B2 và không có góc vượt ngưỡng | B2, Proposed | `curvature_cost`; `acute_turn_count_120deg` | Curvature cost đã có trong evaluator | Công thức thẳng/90°/180° và bridge metadata PASS | `PARTIAL` | B2 adapter; Proposed; acute-turn metric; định nghĩa aggregation và formal PR5 | TV2 metric/PR2; TV4 integration |
| **RQ3 / Physical feasibility** | Quỹ đạo có thể thi công trên máy vẽ và timing vật lý được đo đúng nguồn | SVG/simulator vs máy thật | `actual_draw_time_sec`, sai số quỹ đạo, lỗi thi công | Backend hiện có trường timing nhưng đang mang giá trị mô phỏng trong luồng hiện hành | Chưa có hardware measurement evidence | `BLOCKED_EXTERNAL` | Hardware adapter, calibration, smoke test, nguồn timestamp thật và telemetry provenance | TV3; `PENDING_TV3_CALIBRATION` |

### 3.1. Quy tắc nghiệm thu đã khóa nhưng chưa được áp dụng

| Giả thuyết | FAIL | PASS | INCONCLUSIVE | Có thể áp dụng hiện nay? |
| :--- | :--- | :--- | :--- | :--- |
| H1.1 | Giảm `<15%` vs B1 hoặc `<5%` vs B2 | Giảm `>=25%` vs B1 và `>=10%` vs B2 | Còn lại | **Chưa** — thiếu B1/B2/Proposed |
| H1.2 | Giảm `<20%` vs B1 | Giảm `>=35%` vs B1 | `[20%, 35%)` | **Chưa** — thiếu B1/Proposed |
| H1.3 | Tăng `>15%` vs B1 | Tăng `<=10%` vs B1 | `(10%, 15%]` | **Chưa** — thiếu B1/Proposed |
| H2.1 | Có mẫu `collision_count >= 1` | Toàn bộ bằng `0` | Không áp dụng | **Chưa** — metric có, Proposed chưa có |
| H2.2 | `<0.20 mm` | `>=0.50 mm` | `[0.20, 0.50) mm` | **Chưa** — Proposed và formal corpus chưa có; physical claim còn chờ TV3 |
| H3.1 | Median `>15 ms` hoặc p95 `>30 ms` | Median `<=5 ms` và p95 `<=10 ms` | Còn lại | **Chưa** — runner chưa có protocol timing chính thức |
| H3.2 | Giảm `<=0%` vs B2 hoặc có góc `>120°` | Giảm `>=15%` và không góc `>120°` | Còn lại | **Chưa** — thiếu B2, Proposed và acute-turn metric |

---

## 4. Gate map và thứ tự mở khóa

| Gate | Điều kiện đóng gate | Bằng chứng bắt buộc | Hiện trạng | Chặn |
| :--- | :--- | :--- | :--- | :--- |
| **G0 — Research cross-review** | TV1–TV3 có human verdict; TV4 disposition mọi finding | Ba phiếu review + `review_disposition.md` | `IN_PROGRESS` | `RQ FREEZE: APPROVED` |
| **G1 — PR2 baseline parity / E4 interface** | B1/B2/B3 chạy độc lập qua cùng interface và schema; TV2+TV4 thống nhất interface transition cho Proposed | PR #32 (`bcc1a7a`), adapter tests PASS; hợp đồng E4 và hai owner sign-off còn thiếu | `E3_PASS_E4_PENDING` | E4 chặn PR3 implementation; formal H1/H3 còn cần PR3–PR5 |
| **G2 — PR3 software exit** | `CompositionState` production; 10/10 DEV specimens; 0 crash/NaN; bounds/regression đạt | PR3 unit/integration/acceptance suite | `PENDING_PR3` | H2; Proposed rows; PR4 |
| **G3 — PR4 delayed-stroke P0** | Deterministic delayed-stroke scheduling và tie-break | Unit/regression tests; stroke-order trace | `PENDING_PR4` | H1 về pen-lift đầy đủ; PR5 |
| **G4 — Formal corpus freeze** | TV1 duyệt coverage/version và khóa DEV/Holdout | Corpus manifest/version; leakage check | `PENDING_TV1_FREEZE` | Formal PR5 / mở Holdout |
| **G5 — Formal PR5** | B1/B2/B3/Proposed × corpus × font × seed × repetitions; reporting tự động | Immutable raw CSV, environment manifest, aggregation report | `PENDING_PR5` | PASS/FAIL/INCONCLUSIVE cho H1–H3 |
| **G6 — Physical validation** | Calibration và smoke test trên máy thật | Hardware log có provenance; actual timing; error measurements | `BLOCKED_EXTERNAL` | Physical feasibility claim |

```text
G0 ──> RQ FREEZE

G1 ──┐
     ├──> G2 ──> G3 ──┐
PR1 ─┘                ├──> G5 ──> Kết luận phần mềm RQ1–RQ3
G4 ───────────────────┘

G6 ───────────────────────> Kết luận khả thi vật lý
```

---

## 5. Evidence ledger hiện hành

| Evidence ID | Loại | Artifact/kiểm tra | Phạm vi chứng minh được | Không chứng minh được |
| :--- | :--- | :--- | :--- | :--- |
| E-RUN-01 | Automated test run | `test_ca_vhc_metrics.py`, `test_ca_vhc_experiment_runner.py`, `test_pr3_acceptance_baseline.py`: **25 passed** ngày 22/09/2026 | Hạ tầng metric/runner, geometry regression và Pre-PR3 lock đang chạy được tại snapshot kiểm tra | Không chứng minh B1/B2/Proposed hoặc hiệu quả khoa học |
| E-FIX-01 | Frozen fixture | PR1 DEV fingerprint: 160 cases | B3 geometry không đổi so với fixture ở hai font × bốn seed × DEV 20 | Không phải formal result; không đo baseline comparison |
| E-FIX-02 | Frozen fixture | Pre-PR3 ASCII fingerprint: 48 cases | ASCII regression, seed determinism và batch-order independence | Không kiểm tra dấu tiếng Việt trong Proposed PR3 |
| E-MET-01 | Unit evidence | Synthetic collision/endpoint/clearance tests | Hàm hình học phát hiện các trường hợp test đã khai báo | Không bảo đảm mọi hình học thực tế hoặc physical clearance |
| E-RUNNER-01 | Contract evidence | CSV schema, overwrite guard, Holdout acknowledgement | Runner giảm rủi ro schema drift và mở Holdout nhầm | Không có preregistered execution manifest hay statistical reporter |
| E-DESIGN-01 | Approved design | [`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md) | Kiến trúc `CompositionState` và ownership đã được khóa ở mức thiết kế | Không phải implementation evidence |

### 5.1. Lệnh verification đã chạy

```bash
backend/venv/bin/python -m pytest -q \
  tests/test_ca_vhc_metrics.py \
  tests/test_ca_vhc_experiment_runner.py \
  tests/test_pr3_acceptance_baseline.py
```

Kết quả quan sát: `25 passed in 1.11s`. Đây là lần chạy kỹ thuật tại máy hiện tại, không phải formal benchmark.

---

## 6. Các điểm không nhất quán và nợ bằng chứng cần theo dõi

| ID | Phát hiện | Ảnh hưởng | Cách xử lý đề xuất | Thời điểm |
| :--- | :--- | :--- | :--- | :--- |
| TRACE-DOC-01 | [`05_ca_vhc_research_spec.md`](05_ca_vhc_research_spec.md) mục PR1 vẫn ghi `PR1: IN PROGRESS`, trong khi Current Task/Research Freeze Pack ghi PR1 đã hoàn tất ở commit `daca566` | Có thể khiến reviewer hiểu sai readiness | Chờ cross-review kết thúc rồi đồng bộ trạng thái và mô tả phần còn thiếu thuộc PR5, không phải PR1 | Sau G0 |
| TRACE-CODE-01 | Runner mang tên baseline nhưng chỉ có `METHOD_TAG = "b3_current_trellis"` | Không thể sinh comparison B1/B2/Proposed | PR2 cung cấp adapter/interface; sau đó runner nhận method tường minh | G1 |
| TRACE-METRIC-01 | `collision_count` hiện chỉ đo bridge–diacritic | Claim “mọi va chạm bằng 0” sẽ quá rộng | Giữ wording chính xác là bridge–diacritic hoặc triển khai taxonomy collision tách biệt | G2/G5 |
| TRACE-METRIC-02 | `minimum_diacritic_clearance_mm = inf` khi không có cặp áp dụng | Nếu aggregate trực tiếp sẽ làm sai thống kê | Ghi `NOT_APPLICABLE`, loại khỏi median clearance và báo cáo riêng số N/A | G5 |
| TRACE-TIME-01 | Runner ghi timing từng render nhưng chưa warm-up/repeat/median/p95/environment manifest | Chưa thể dùng H3.1 | Triển khai protocol 10 warm-up, 50 repeats và reporter ở PR5 | G5 |
| TRACE-TIME-02 | `actual_draw_time_sec` hiện có thể chứa thời gian mô phỏng | Nguy cơ claim sai về máy thật | Tách provenance hoặc trường simulated/estimated trước physical reporting | G6 |
| TRACE-METRIC-03 | Chưa có `acute_turn_count_120deg`, `c1_violation_count` và physical trajectory error | H3.2/C1/physical claim chưa đủ evidence | Triển khai metric riêng, test công thức và khóa schema trước formal run | G1/G5/G6 |

---

## 7. Checklist cập nhật ma trận

Mỗi PR liên quan phải cập nhật tài liệu này theo quy tắc sau:

- [ ] Ghi commit/PR tạo bằng chứng mới.
- [ ] Liên kết đúng module và test, không chỉ ghi tên tính năng.
- [ ] Chạy test liên quan và ghi số lượng PASS; không dùng “test pass” chung chung.
- [ ] Nếu thêm metric, ghi rõ đơn vị, N/A policy và aggregation policy.
- [ ] Nếu thêm method, chứng minh input/config parity với các baseline.
- [ ] Không mở Holdout trước G4.
- [ ] Không dùng timing đơn lẻ làm kết quả H3.1.
- [ ] Không dùng simulator timing làm `actual_draw_time_sec` vật lý.
- [ ] Không đổi hypothesis verdict trước khi G5 hoàn tất.
- [ ] Mọi physical claim phải chờ G6.

## 8. Công việc TV4 có thể chuẩn bị khi chờ PR2 và cross-review

1. Giữ Chương 1–3 bất biến trong vòng review hiện tại.
2. Chuẩn bị test skeleton và interface checklist cho `CompositionState` ở mức thiết kế; chưa merge production PR3 trước G1.
3. Định nghĩa N/A policy cho clearance và schema environment manifest của PR5.
4. Chuẩn bị bảng aggregation FAIL → PASS → INCONCLUSIVE nhưng không chạy Holdout.
5. Khi nhận finding từ TV1–TV3, cập nhật disposition trước khi sửa bản thảo.

Tài liệu này được cập nhật theo evidence mới; không dùng nó như giấy chứng nhận rằng thuật toán đã hoàn thiện hoặc đề tài đã đạt kết quả nghiên cứu.
