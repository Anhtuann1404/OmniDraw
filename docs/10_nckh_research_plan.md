# OmniDraw — Research Freeze Pack & Khung Báo cáo NCKH

**Phiên bản:** TV4 consolidated draft v0.1  
**Trạng thái:** `READY FOR CROSS-REVIEW`  
**Khóa RQ toàn nhóm:** `PENDING`  
**Kết quả thực nghiệm chính thức:** `NOT AVAILABLE`  
**Formal experiment readiness:** `NO`

> [!IMPORTANT]
> Tài liệu này khóa cấu trúc nghiên cứu và khung trình bày, không công bố kết quả. Mọi ô kết quả đều phải giữ trạng thái `PENDING FORMAL EXPERIMENT — DO NOT REPORT AS RESULT` cho đến khi các gate dữ liệu, phần mềm và phần cứng tương ứng đã hoàn tất.

---

## 1. Mục tiêu và nguồn sự thật

Research Freeze Pack này hợp nhất các quyết định đã có thành một đầu mối để cả nhóm cross-review trước khi khóa RQ1–RQ3 và viết báo cáo chính thức.

| Nội dung | Nguồn chuẩn |
| :--- | :--- |
| RQ, giả thuyết, ngưỡng PASS/FAIL/INCONCLUSIVE | [`05_ca_vhc_research_spec.md`](05_ca_vhc_research_spec.md) |
| Thiết kế `CompositionState`, hàm mục tiêu và Viterbi DP | [`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md) |
| Corpus, split và quản trị dữ liệu | [`08_handwriting_dataset_spec.md`](08_handwriting_dataset_spec.md) |
| Entry/Exit Gate phần mềm PR3 | [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md) |
| Roadmap, ưu tiên và phân công | [`02_roadmap.md`](02_roadmap.md), [`03_current-task.md`](03_current-task.md) |
| Public contract hiện hành | [`OmniDraw_API_Spec-4.md`](OmniDraw_API_Spec-4.md) |

### 1.1. Phân loại trạng thái bằng chứng

- `IMPLEMENTED_AND_TESTED`: đã có code và kiểm thử trong repository.
- `DESIGN_LOCKED`: thiết kế đã được TV2/TV4 review nhưng chưa triển khai production.
- `PENDING_PR2`: cần baseline adapter hoặc transition interface của TV2.
- `PENDING_PR3`: cần `CompositionState` và Diacritic-Aware Trellis.
- `PENDING_TV1_FREEZE`: chưa được dùng cho formal experiment.
- `PENDING_TV3_CALIBRATION`: chưa được dùng cho tuyên bố vật lý.
- `PENDING_PR5`: chưa có benchmark/ablation chính thức.

---

## 2. Phạm vi nghiên cứu

### 2.1. Trong phạm vi P0

1. Tối ưu lựa chọn biến thể glyph, vị trí dấu và quyết định nối/nhấc bút theo ngữ cảnh ở cấp từ.
2. Đo quãng đường pen-up, số lần nhấc bút và chiều dài nét tiếp xúc giấy.
3. Phát hiện và giảm va chạm giữa bridge, thân chữ và dấu tiếng Việt.
4. Đánh giá clearance hình học theo ngưỡng kỹ thuật và mục tiêu nghiên cứu provisional.
5. Đo thời gian giải Viterbi, chi phí đổi hướng và khả năng thi công trên máy vẽ.
6. So sánh Proposed CA-VHC với B1, B2 và B3 bằng corpus, font và seed được kiểm soát.

### 2.2. Ngoài phạm vi RQ hiện hành

- Writer Profile, few-shot personalization và style transfer thuộc P2; không được dùng làm bằng chứng trả lời RQ1–RQ3 hiện tại.
- Chuyển đổi TTF/OTF sang centerline, font pack mới hàng loạt và deep generative handwriting thuộc P3.
- Art Mode có bộ baseline riêng; kết quả Art Mode không thay thế bằng chứng cho CA-VHC Handwriting Mode.
- Hệ thống không tuyên bố hiểu ngữ nghĩa hoặc ngữ âm học; xử lý tiếng Việt dựa trên Unicode NFD và quy tắc hình học chính tả.
- Không tuyên bố real-time, trơn $C^1$ toàn cục hay an toàn vật lý trước khi có metric và kiểm chứng tương ứng.

---

## 3. Research Questions và giả thuyết

### 3.1. RQ1 — Nối nét và tối ưu chuyển động

**RQ1:** Việc dùng Viterbi DP trên `CompositionState` để đồng thời lựa chọn biến thể glyph và vị trí dấu theo ngữ cảnh có giảm quãng đường pen-up và số lần nhấc bút so với B1/B2/B3, trong khi vẫn kiểm soát tổng chiều dài nét tiếp xúc giấy hay không?

| Giả thuyết | Biến độc lập | Biến phụ thuộc | Baseline | Quy tắc nghiệm thu | Owner | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| H1.1 — Giảm pen-up distance | Phương pháp B1/B2/B3/Proposed | `pen_lift_distance_mm` | B1, B2; B3 là đối chiếu chẩn đoán | FAIL: giảm `<15%` vs B1 hoặc `<5%` vs B2; PASS: giảm `>=25%` vs B1 và `>=10%` vs B2; còn lại INCONCLUSIVE | TV2 lead motion, TV4 runner | `PENDING_PR2`, `PENDING_PR5` |
| H1.2 — Giảm pen-lift count | Phương pháp | `pen_lift_count` | B1 | FAIL `<20%`; PASS `>=35%`; còn lại INCONCLUSIVE | TV2 + TV4 | `PENDING_PR2`, `PENDING_PR5` |
| H1.3 — Kiểm soát chiều dài nét | Phương pháp | `total_path_length_mm` | B1 | FAIL: tăng `>15%`; PASS: tăng `<=10%`; còn lại INCONCLUSIVE | TV4 | `PENDING_PR3`, `PENDING_PR5` |

**Điểm cần TV2 cross-review:** định nghĩa chính xác B1/B2/B3, transition-cost interface, cách tách pen-down/pen-up và công thức tổng hợp theo corpus.

### 3.2. RQ2 — Tránh va chạm dấu tiếng Việt

**RQ2:** Việc đưa ứng viên dấu và vùng cản trở của dấu vào `CompositionState` và hàm mục tiêu Trellis có loại bỏ giao cắt bridge–diacritic và duy trì clearance tối thiểu tốt hơn B3 hay không?

| Giả thuyết | Biến độc lập | Biến phụ thuộc | Baseline | Quy tắc nghiệm thu | Owner | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| H2.1 — Không va chạm | B3/Proposed | `collision_count` | B3 | FAIL nếu bất kỳ mẫu nào có `collision_count >= 1`; PASS nếu toàn bộ tập nghiệm thu bằng `0` | TV4 | `PENDING_PR3` |
| H2.2 — Clearance tối thiểu | B3/Proposed | `minimum_diacritic_clearance_mm` | B3 | FAIL `<0.20 mm`; PASS provisional `>=0.50 mm`; `[0.20, 0.50)` INCONCLUSIVE; `inf` là NOT_APPLICABLE | TV4 geometry, TV3 calibration | `PENDING_PR3`, `PENDING_TV3_CALIBRATION` |

**Ranh giới tuyên bố:** `0.20 mm` là prototype technical minimum; `0.50 mm` là provisional research target, chưa phải ngưỡng vật lý chính thức.

### 3.3. RQ3 — Hiệu năng và khả năng thi công

**RQ3:** Với $K_{raw} \le 9$, CA-VHC có duy trì chi phí tính toán trong giới hạn thiết kế và tạo quỹ đạo vector đủ khả thi để kiểm chứng trên máy vẽ hai trục hay không?

| Giả thuyết | Biến độc lập | Biến phụ thuộc | Baseline | Quy tắc nghiệm thu | Owner | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| H3.1 — Thời gian Viterbi | Phương pháp và độ dài từ | `optimize_time_ms` median/p95 | B2, B3 | FAIL: median `>15 ms` hoặc p95 `>30 ms`; PASS: median `<=5 ms` và p95 `<=10 ms`; còn lại INCONCLUSIVE | TV4 runner, TV2 algorithm | `PENDING_PR5` |
| H3.2 — Kiểm soát đổi hướng | Phương pháp | `curvature_cost`, `acute_turn_count_120deg` | B2 | FAIL: giảm `<=0%` hoặc có góc `>120°`; PASS: giảm `>=15%` và không có góc `>120°`; còn lại INCONCLUSIVE | TV2 | `PENDING_PR2`, `PENDING_PR5` |
| Physical feasibility | Simulator vs máy thật | `actual_draw_time_sec`, sai số quỹ đạo, lỗi thi công | SVG/simulator | Chỉ kết luận sau calibration và smoke test trên máy thật | TV3 | `PENDING_TV3_CALIBRATION` |

**Ranh giới tuyên bố:** Catmull–Rom sang Bézier không tự động chứng minh $C^1$ ở mọi junction. `c1_violation_count` và dữ liệu máy thật phải tồn tại trước khi đưa ra tuyên bố tương ứng.

---

## 4. Methodology Blueprint

### 4.1. Thiết kế nghiên cứu

- **Loại nghiên cứu:** thực nghiệm định lượng có đối chứng, kết hợp kiểm chứng phần mềm và validation vật lý downstream.
- **Đơn vị phân tích:** một tổ hợp `(method, corpus_item, font, seed, run_index)`.
- **Phương pháp:** B1, B2, B3 và Proposed CA-VHC.
- **Font chính:** `oly`, `omni_casual`.
- **Seed:** `42`, `100`, `2026`, `999999`.
- **Corpus:** DEV dùng phát triển; Holdout chỉ mở cho formal evaluation sau TV1 freeze.
- **Hiệu năng:** 10 warm-up, 50 lần lặp mỗi cấu hình; báo cáo median và p95.

### 4.2. Biến kiểm soát

- Cùng text, font, style, font size, paper size, seed và commit hash giữa các method.
- Ghi CPU, OS, Python, NumPy/BLAS backend và power mode.
- Không trộn kết quả Windows/Linux hoặc simulator/máy thật thành cùng một quần thể đo.
- Timing không được đưa vào geometry fingerprint.

### 4.3. Metric contract theo mức bằng chứng

| Metric | Hiện trạng | Dùng được hiện nay | Điều kiện để dùng trong kết luận |
| :--- | :--- | :--- | :--- |
| `total_path_length_mm` | Internal evaluator/runner đã có | Technical dry-run | Baseline adapters + formal corpus |
| `pen_lift_distance_mm` | Internal evaluator/runner đã có | Technical dry-run | PR2 baseline comparability |
| `pen_lift_count` | Internal evaluator/runner đã có | Technical dry-run | PR2 baseline comparability |
| `collision_count` | Internal evaluator đã có | Metric validation | PR3 + acceptance corpus |
| `minimum_diacritic_clearance_mm` | Internal evaluator đã có | Metric validation | PR3; physical claim cần TV3 |
| `curvature_cost` | Internal evaluator đã có | Technical dry-run | PR2 definition + PR5 |
| `optimize_time_ms` | Internal timing đã có | Diagnostic only | PR5 protocol median/p95 |
| `actual_draw_time_sec` | Chưa có số đo máy thật | Không | TV3 hardware run |
| `c1_violation_count` | Chưa triển khai | Không | Metric implementation + validation |

### 4.4. Data governance và chống leakage

1. Không dùng Holdout để chọn trọng số, sửa heuristic hoặc debug PR1–PR4.
2. Mọi thay đổi thuật toán phải dựa trên DEV hoặc synthetic fixtures.
3. TV1 review/freeze corpus trước formal PR5.
4. Ghi commit, config, seed và môi trường cho mọi formal run.
5. Nếu rerun sau khi nhìn Holdout, phải ghi nhận contamination và không trình bày đó là đánh giá độc lập ban đầu.

---

## 5. Khung Chương 3 — Phương pháp và thiết kế thuật toán

### 3.1. Kiến trúc tổng thể OmniDraw
- Hai đường chạy Art Mode và Handwriting Mode.
- Ranh giới frontend, API Gateway, handwriting engine, optimizer và hardware adapter.
- Chỉ mô tả chức năng đã có; phần dự kiến phải gắn nhãn design target.

### 3.2. Biểu diễn chữ viết tay nét đơn
- Font Pack và Render Profile.
- Glyph geometry, metrics, anchors và contextual variants.
- Unicode NFD và quy tắc hình học chính tả tiếng Việt.

### 3.3. Baseline và Trellis hiện hành
- B1 Static Glyph Renderer.
- B2 Greedy Contextual Heuristic.
- B3 Current Trellis DAG.
- Trạng thái hiện tại `GlyphVariant`, recurrence và giới hạn post-DAG accent placement.

### 3.4. Proposed CA-VHC
- `DiacriticCandidate` và `CompositionState`.
- Local/world coordinate system.
- Candidate generation, hard pruning và $K_{raw} \le 9$.
- Phân tách $C_{state}$ và $J_{transition}$.

### 3.5. Hàm mục tiêu và Viterbi DP

$$C_{state}=w_{4a}C_{internal\_collision}+w_5C_{legibility}+w_6C_{placement}$$

$$J_{transition}=w_1D_{penup}+w_2N_{lift}+w_3C_{curvature}+w_4C_{bridge\_collision}$$

$$DP[i,j]=C_{state}(s_{i,j})+\min_p\left(DP[i-1,p]+J_{transition}(s_{i-1,p},s_{i,j})\right)$$

- Giải thích không double-count giữa state cost và transition cost.
- Hard rejection khi bridge cắt vùng dấu không thể chấp nhận.
- Backpointer và tái dựng chuỗi trạng thái tối ưu.

### 3.6. Bố trí dấu và delayed-stroke
- PR3 trả lời **WHERE**: vị trí dấu.
- PR4 trả lời **WHEN**: thứ tự vẽ dấu.
- P0 delayed-stroke: viết thân từ, gom dấu, deterministic nearest neighbor, original-index tie-break.

### 3.7. Tính tái lập và QA
- Seed contract.
- Structured trace và geometry fingerprint.
- PR1 experiment runner, ASCII regression snapshot và Pre-PR3 acceptance contract.
- Strict validation và bounds/SVG checks.

### 3.8. Độ phức tạp và giới hạn phương pháp
- Số state theo layer và độ phức tạp Viterbi.
- Không suy diễn semantic understanding.
- Không đồng nhất geometric smoothness với mechanical performance.
- Writer Profile và TTF conversion là future work.

---

## 6. Khung Chương 4 — Thực nghiệm và đánh giá

> **PENDING FORMAL EXPERIMENT — DO NOT REPORT AS RESULT**

### 4.1. Câu hỏi, giả thuyết và protocol
- Ánh xạ RQ1–RQ3 sang H1.1–H3.2.
- Trình bày thứ tự FAIL → PASS → INCONCLUSIVE.
- Công bố preregistered thresholds trước khi mở Holdout.

### 4.2. Dataset và cấu hình
- DEV/Holdout governance.
- Hai font và bốn seed.
- Environment metadata, warm-up và số lần lặp.

### 4.3. Baseline comparability
- Phiên bản B1/B2/B3.
- Input/config parity.
- Kiểm tra output schema và failure policy.

### 4.4. Kết quả RQ1

| Method | Pen-up distance median | Pen-lift count | Total path length | So với B1 | So với B2 | Phán quyết |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| B1 | PENDING | PENDING | PENDING | — | — | PENDING |
| B2 | PENDING | PENDING | PENDING | PENDING | — | PENDING |
| B3 | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| Proposed CA-VHC | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

### 4.5. Kết quả RQ2

| Method | Collision count | Minimum clearance | N/A cases | FAIL | PASS | INCONCLUSIVE |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| B3 | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| Proposed CA-VHC | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

### 4.6. Kết quả RQ3

| Method | Optimize median | Optimize p95 | Curvature cost | Acute turns | Physical draw time |
| :--- | ---: | ---: | ---: | ---: | ---: |
| B2 | PENDING | PENDING | PENDING | PENDING | NOT AVAILABLE |
| B3 | PENDING | PENDING | PENDING | PENDING | NOT AVAILABLE |
| Proposed CA-VHC | PENDING | PENDING | PENDING | PENDING | NOT AVAILABLE |

### 4.7. Ablation Study
- Bỏ state collision cost.
- Bỏ bridge–diacritic collision cost.
- Bỏ curvature term.
- Canonical-only diacritic placement.
- Delayed-stroke off/on sau PR4.
- Mỗi ablation phải giữ nguyên corpus, seed và environment.

### 4.8. Kiểm chứng vật lý
- Simulator smoke test không được gọi là physical validation.
- Báo cáo `actual_draw_time_sec`, sai số quỹ đạo và quan sát lem/dính nét khi có máy thật.
- Tách kết quả theo cấu hình phần cứng và thông số calibration.

### 4.9. Threats to validity

| Nhóm | Nguy cơ | Giảm thiểu |
| :--- | :--- | :--- |
| Internal validity | Baseline không cùng config | Shared runner/config; snapshot và schema tests |
| Construct validity | Metric hình học không phản ánh hoàn toàn thẩm mỹ/thi công | Tách geometry, motion và physical validation |
| External validity | Corpus nhỏ, chỉ hai font | Holdout độc lập; ghi rõ phạm vi; không suy rộng quá mức |
| Measurement validity | Timing phụ thuộc máy | Ghi environment; warm-up; median/p95; không trộn OS |
| Data leakage | Tinh chỉnh trên Holdout | DEV-only development; TV1 freeze; contamination log |
| Reproducibility | Ngẫu nhiên hoặc code drift | Seed, commit hash, config và frozen snapshots |

### 4.10. Thảo luận và giới hạn
- Giải thích kết quả theo từng RQ, không chỉ theo metric riêng lẻ.
- Báo cáo cả FAIL và INCONCLUSIVE.
- Phân biệt design target, software evidence và physical evidence.
- Future work: Writer Profile, exact delayed-stroke enumeration, nhiều font hơn và telemetry.

---

## 7. Cross-review và Freeze Gate

| Reviewer | Phạm vi phải duyệt | Trạng thái |
| :--- | :--- | :--- |
| TV1 | Corpus coverage, DEV/Holdout governance, Writer Profile nằm ngoài RQ P0 | `PENDING` |
| TV2 | RQ1, B1/B2/B3, transition cost, curvature và motion metrics | `PENDING` |
| TV3 | RQ3 physical feasibility, calibration, actual draw time và physical clearance | `PENDING` |
| TV4 | RQ2, composition geometry, metric/runner integrity và tính nhất quán tài liệu | `DRAFT COMPLETE` |

### 7.1. Điều kiện chuyển sang `RQ FREEZE: APPROVED`

- [ ] TV2 xác nhận baseline và các giả thuyết chuyển động.
- [ ] TV1 xác nhận phạm vi corpus và quy tắc leakage.
- [ ] TV3 xác nhận wording cho các tuyên bố vật lý.
- [ ] TV4 xử lý toàn bộ nhận xét và kiểm tra chéo Docs 02/03/05/07/08/09/10.
- [ ] Không có metric chưa triển khai nào bị mô tả là measured result.
- [ ] Không có bảng PENDING nào bị dùng làm kết quả báo cáo.

### 7.2. Trạng thái hiện tại

```text
RESEARCH FREEZE PACK:          READY FOR CROSS-REVIEW
RQ1–RQ3 STRUCTURE:             CONSOLIDATED
RQ FREEZE:                     PENDING TEAM APPROVAL
CHAPTER 3 OUTLINE:             READY
CHAPTER 4 OUTLINE:             READY, RESULTS EMPTY
FORMAL EXPERIMENT READINESS:   NO
```

