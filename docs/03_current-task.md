# OmniDraw — Current Task & Sprint Backlog

**Cập nhật lần cuối:** 20/09/2026
**Chu kỳ hiện tại:** Sprint 1–2 (2 tuần tới: Khóa nền nghiên cứu CA-VHC & Thiết lập framework thực nghiệm)
**Nguyên tắc:** Mỗi người làm chủ một đường chạy độc lập, tuân thủ Definition of Done và review chéo định kỳ.

---

## 1. Trạng thái hiện tại theo 4 đường chạy (Current Sprint Status)


| Thành viên                 | Đang làm gì                            | Bị nghẽ ở đâu (nếu có)                  | Dự kiến xong |
| -------------------------- |----------------------------------------| --------------------------------------- | ----------- |
| TV1 — AI Core              | Đã chốt và up 15 prompt test lên Drive | *(điền, hoặc để trống nếu không nghẽn)* | Đã xong     |
| TV2 — AI Ứng dụng/CV       | *(điền)*                               | *(điền)*                                | *(điền)*    |
| TV3 — Phần cứng            | xong phần code main.py                 | đợi lead xem rồi thêm bớt để nâng cấp                                  | today     |
| TV4 — Giao diện & Tích hợp | (điền)                                 | *(điền)*                                | *(điền)*    |


**Ngày 26/8**


|                            |                                |         |           |
| -------------------------- | ------------------------------ | ------- | --------- |
| TV4 — Giao diện & Tích hợp | *Dựng khung UI UX( mock data)* | *Không* | *Đã Xong* |


---

| Thành viên / Đường chạy | Nhiệm vụ trọng tâm Sprint 1–2 | Điểm nghẽn (Blocker) | Trạng thái |
| :--- | :--- | :--- | :--- |
| **TV4 — Project Lead & Handwriting / CA-VHC Composition Lead** | Hoàn tất Strict Validation (34/34 PASS); hoàn tất BƯỚC A — Trellis DAG / CA-VHC Architecture Audit (`docs/06_audit_trellis_dag_report.md`); hoàn tất bản thảo BƯỚC B — Thiết kế kiến trúc Diacritic-Aware State Representation (`docs/07_diacritic_aware_state_design.md`) (chờ TV2 cross-review trước khi sang Bước C); chuẩn hóa schema logging CSV; xây dựng experiment runner; tổng hợp và khóa Research Questions (RQ1–RQ3); dựng khung báo cáo Chương 3 & 4 | Không | 🟡 Đang làm |
| **TV2 — Stroke Optimization & Path Planning Lead** | Soạn thảo Research Questions (RQ) & giả thuyết về tối ưu chuyển động; chuẩn hóa ký hiệu toán học hàm mục tiêu $J$ (phần transition cost & kinematics); chuẩn hóa 2 bộ baseline đối chứng (Art Mode & CA-VHC motion); phối hợp thiết kế hàm chi phí di chuyển ngòi bút cho Trellis DAG | Không | 🟡 Đang làm |
| **TV1 — AI Data & Writer Profile Lead** | Chuẩn bị benchmark corpus và data fixtures phục vụ CA-VHC (cung cấp cho TV4); chuẩn bị P2 Writer Profile: định nghĩa JSON schema (versioned), soạn thảo protocol thu thập & ẩn danh hóa dữ liệu, code prototype trích xuất 4 đặc trưng hình học độc lập (tuân thủ `08_handwriting_dataset_spec.md`, chưa tích hợp engine, không huấn luyện mô hình lớn) | Không | 🟡 Đang làm |
| **TV3 — Hardware, Calibration & Physical Validation Lead** | Chuẩn hóa interface chung giữa simulator và máy vẽ thật; chuẩn bị SVG smoke test fixture; lập checklist hiệu chuẩn phần cứng; xác định metrics phần cứng bắt buộc (phân biệt simulator time và `actual_draw_time_sec` thật) | *Blocked by hardware:* chờ setup cáp & máy vẽ thực tế (tập trung hoàn thiện simulator & test protocol) | 🟡 Đang làm |

---

## 2. Backlog chi tiết Sprint 1–2 (Kế hoạch hành động 2 tuần tới)

### TV4 — Project Lead & Handwriting / CA-VHC Composition Lead
- [ ] **Điều phối kỹ thuật & Khóa Research Questions (Project Lead):** Tổng hợp, điều phối và khóa cấu trúc Research Questions (RQ1–RQ3) và giả thuyết khoa học toàn đề tài (kết nối giả thuyết chuyển động của TV2, giả thuyết thi công phần cứng của TV3 và giả thuyết Writer Profile P2 của TV1); rà soát tính nhất quán giữa Roadmap, Current Task, API Spec v1.4 và codebase.
- [x] **✅ Strict Validation completed (34/34 automated tests PASS):** Đã loại bỏ triệt để silent fallback, khóa chặt chẽ mode-aware validation theo từng `input_type`, bảo đảm validation diễn ra trước mọi side effect, và bảo đảm an toàn toàn diện cho pipeline backend; toàn bộ 34 automated tests trong `backend/test_handwriting_validation.py` đạt 34/34 passed:
  - *Handwriting Mode (`input_type in {"handwriting", "letter"}`):* Bắt buộc có `style` trong `STYLE_CONFIGS`, khuyết/null/sai kiểu trả `INPUT_INVALID_FORMAT`; text rỗng trả `EMPTY_TEXT`; `options.font` không truyền default `"oly"`, sai/null trả `UNSUPPORTED_FONT`; `options.letter_type` không truyền default `"general"`, sai/null/không tương thích trả `UNSUPPORTED_LETTER_TYPE`; `options.seed` sai kiểu/biên trả `INVALID_SEED`; `options.target_paper_size_mm` khuyết nhận default A4 `[210, 297]`, explicit `null`/sai kiểu/len $\neq 2$/không dương/NaN/Inf trả `INPUT_INVALID_FORMAT`.
  - *Art Mode (`input_type in {"text", "image"}`):* Phong cách hợp lệ thuộc `ART_MODE_STYLES` (`sketch`, `line_art`, `stipple`, `hatching`). Khi `style` khuyết hoặc `null`, tự động giải quyết an toàn thành `effective_style = "sketch"` trước pipeline; khi truyền `style` không hợp lệ (`""`, số, mảng, bool, hoặc chuỗi ngoài enum kể cả style handwriting) $\rightarrow$ từ chối ngay với `INPUT_INVALID_FORMAT` không gọi pipeline; `text` bắt buộc có `prompt` không rỗng; `image` bắt buộc có `image_base64` không rỗng; toàn bộ downstream (`call_openai_image_api`, `svg_process`, metadata logging) được assert kiểm chứng luôn nhận `effective_style`, không bao giờ nhận `None`.
  - *Invalid input_type:* Mọi `input_type` lạ (kể cả `null`, số, chuỗi rỗng) đều được Gateway xử lý trả lỗi có cấu trúc `INPUT_INVALID_FORMAT`.
  - *Validation trước side effect:* Request invalid tuyệt đối không gọi `_clear_cached_svg_for_request` và không xóa/thay đổi SVG hay cache hiện có; request hợp lệ thực hiện cleanup đúng 1 lần trước khi pipeline chạy.
- [x] **✅ BƯỚC A — Trellis DAG / CA-VHC Architecture Audit completed:** Hoàn tất rà soát read-only toàn diện kiến trúc hiện tại, ban hành báo cáo kỹ thuật [`docs/06_audit_trellis_dag_report.md`](file:///Users/yingjunn_/Study_/Nckh_2026-2027/OmniDraw/docs/06_audit_trellis_dag_report.md). Audit xác nhận các điểm then chốt:
  - Current DAG chỉ tối ưu base glyph variants (`std`, `mid_in`, `high_out`, `closed`, `isolated`).
  - `GlyphVariant` chưa chứa diacritics hay thông tin dấu.
  - Tiền xử lý Unicode NFD đã tách đúng base character + combining marks.
  - `generate_accents()` hiện đang chạy hoàn toàn POST-DAG theo tọa độ mỏ neo tĩnh.
  - Runtime bridge collision (`bridge_collision_cost`) chưa xét va chạm với dấu tiếng Việt.
  - Delayed-stroke optimization chưa được triển khai trong engine.
  - Current DAG recurrence vẫn là Viterbi chuẩn: $DP[i, j] = \min_p (DP[i-1, p] + \text{transition\_cost})$.
- [ ] **🟡 BƯỚC B — Diacritic-Aware State Architecture Design (Design specification completed, pending TV2 cross-review before Step C):** Khóa kiến trúc state mới cho CA-VHC: `GlyphVariant` giữ nguyên semantic biến thể hình học thân chữ gốc (base-glyph), `DiacriticCandidate` biểu diễn cấu hình dấu ở tọa độ cục bộ (local coordinates: marks, placement, clearance zone, offsets), `CompositionState` trở thành node logic chính thức của Trellis DAG. Phân tách rõ State Cost $C_{\text{state}}$ (TV4) và Transition Cost $J_{\text{transition}}$ (TV2/TV4), kiểm soát cắt tỉa cứng các ứng viên bất hợp lệ ($K_{\text{raw}} \le 9$), xác lập mục tiêu bảo toàn hành vi cho ký tự không dấu (ASCII), và xây dựng chiến lược 12 unit tests trước khi triển khai mã nguồn (Đặc tả thiết kế: [`docs/07_diacritic_aware_state_design.md`](file:///Users/yingjunn_/Study_/Nckh_2026-2027/OmniDraw/docs/07_diacritic_aware_state_design.md)).
  - *Sub-status:*
    - Architecture draft: DONE
    - Internal design review & technical cleanup: DONE
    - TV2 cross-review: PENDING
    - Source implementation: NOT STARTED
    - Step C readiness: NO (Pending TV2 cross-review)
- [ ] **Tiêu chuẩn kiểm thử dấu:** Xây dựng tiêu chuẩn định lượng pass/fail cho kiểm tra va chạm dấu tiếng Việt (`diacritic collision clearance threshold`) và mở rộng kịch bản kiểm thử trong `backend/handwriting/qa_specimens.py`.
- [ ] **Chuẩn hóa CSV Logging:** Chuẩn hóa cấu trúc file log thực nghiệm CSV ở backend (`backend/main.py:append_experiment_log`), đảm bảo ghi nhận đầy đủ các trường phục vụ phân tích RQ.
- [ ] **Experiment Runner & CSV Logging:** Lập kế hoạch và viết script experiment runner chạy tự động một loạt câu văn tiếng Việt chuẩn qua nhiều phương pháp (`method_tag`) và các `seed` khác nhau, ghi nhận log CSV đầy đủ metrics (nhận benchmark corpus và data fixtures từ TV1).
- [ ] **Khung Báo cáo NCKH:** Dựng khung cấu trúc chi tiết cho Chương 3 (Phương pháp & Thiết kế Thuật toán) và Chương 4 (Thực nghiệm & Đánh giá) trong Báo cáo NCKH 5 chương.
- [ ] *Lưu ý phạm vi:* Chưa cần thiết kế thêm Font Pack mới trong sprint này; tập trung tối ưu trên 2 pack hiện có (`omnidraw_legacy` và `omni_casual`).

### TV2 — Stroke Optimization & Path Planning Lead
- [ ] **Đặc tả học thuật tối ưu chuyển động:** Xây dựng và soạn thảo câu hỏi nghiên cứu / giả thuyết chuyên sâu về tối ưu đường nét, quãng đường nhấc bút (pen-up distance minimization), chi phí động học và thời gian thi công trên máy vẽ vật lý (đóng góp vào khung RQ chung do TV4 tổng hợp).
- [ ] **Toán học hóa chi phí chuyển động:** Chuẩn hóa ký hiệu toán học hình thức: Phương trình Bellman Viterbi DP cho transition cost, biểu thức chi phí động học Kinematic Turn Penalty $\text{dist} + \lambda(1 - \cos\theta)$, và pen-up distance.
- [ ] **Chuẩn hóa 2 bộ baseline đối chứng:**
  - *Bộ baseline Art Mode / Path Optimization (TV2 lead):* (1) Original contour order / Naive; (2) Greedy Nearest Neighbor; (3) OmniDraw `cKDTree + Or-opt + Kinematic Turn Penalty`.
  - *Bộ baseline Handwriting CA-VHC (TV2 phụ trách metric chuyển động, TV4 lead composition & runner):* (1) Static Glyph Renderer; (2) Greedy contextual/connection heuristic; (3) Current Trellis DAG (chưa có ràng buộc dấu nâng cao). *(Phương pháp đề xuất CA-VHC mở rộng là đối tượng nghiên cứu được đánh giá, không tính là baseline đối chứng thứ tư).*
- [ ] **Phối hợp hàm mục tiêu $J$:** Phối hợp với TV4 thiết kế thành phần chi phí chuyển dịch ngòi bút giữa các nét ($D_{\text{penup}}$, $N_{\text{lift}}$, $C_{\text{curvature}}$) trong hàm `eval_transition()` của Trellis DAG.
- [ ] **Định lượng hiệu năng:** Xây dựng tiêu chuẩn định lượng đánh giá hiệu quả giảm quãng đường pen-up và độ mượt chuyển động ngòi bút trên tập corpus thử nghiệm.
- [ ] *Lưu ý phạm vi:* Tập trung vào thuật toán tối ưu chuyển động, không sửa logic hình học hay quy tắc ngữ cảnh trong `backend/handwriting/`.

### TV1 — AI Data & Writer Profile Lead
- [ ] **Chuẩn bị benchmark corpus và data fixtures cho CA-VHC:** Chuẩn bị tập ngữ liệu câu/từ chuẩn tiếng Việt và synthetic fixtures đầu vào cho experiment runner của TV4 (tuân thủ quy chuẩn CA-VHC Dataset trong `08_handwriting_dataset_spec.md`).
- [ ] **Chuẩn bị nghiên cứu Writer Profile (P2 Preparation):** Xây dựng bản nháp JSON schema `WriterProfile` (có trường `version`, `metadata`, `feature_vector`) và protocol thu thập & ẩn danh hóa dữ liệu (tuân thủ quy chuẩn Writer Profile Dataset trong `08_handwriting_dataset_spec.md`, cam kết có sự đồng thuận của người viết, loại bỏ chữ ký và thông tin định danh cá nhân nhạy cảm).
- [ ] **Prototype trích xuất đặc trưng độc lập (P2 Preparation):** Lập trình module prototype trích xuất tối thiểu 4 đặc trưng hình học định lượng cơ bản:
  1. Độ nghiêng trung bình (`slant_deg`);
  2. Tỷ lệ kích thước chữ (`aspect_ratio`);
  3. Khoảng cách chữ và từ (`letter_spacing`, `word_spacing`);
  4. Độ dao động baseline (`baseline_jitter_sigma`).
- [ ] **Tạo fixture dữ liệu mẫu giả lập:** Tạo synthetic data fixtures để kiểm thử bộ trích xuất độc lập, không phụ thuộc vào tiến độ thu thập dữ liệu người dùng thật.
- [ ] *Lưu ý phạm vi:* Đây là công việc chuẩn bị P2; chưa tích hợp Writer Profile vào engine, chưa được xem là Writer Profile MVP hoàn thành; không huấn luyện mô hình học sâu (deep learning) phức tạp trong sprint này; ưu tiên hoàn thiện quy trình rule-based rõ ràng và có thể kiểm chứng (chi tiết xem [`08_handwriting_dataset_spec.md`](file:///Users/yingjunn_/Study_/Nckh_2026-2027/OmniDraw/docs/08_handwriting_dataset_spec.md)).

### TV3 — Hardware, Calibration & Physical Validation Lead
- [ ] Chuẩn hóa và đồng nhất interface phần mềm chung (`HardwareAdapterInterface`) dùng chung cho cả phần cứng AxiDraw thật và bộ giả lập `mock_grbl`.
- [ ] Chuẩn bị một file SVG fixture chuẩn (chứa đầy đủ nét thẳng, nét cong Bézier, chữ viết tay và nhấc bút) để phục vụ smoke test tự động.
- [ ] Soạn thảo Checklist hiệu chuẩn phần cứng máy vẽ: căn góc 0 tọa độ giấy, vận tốc vẽ, gia tốc ngòi bút, độ nảy và độ trễ cơ học nâng/hạ bút.
- [ ] Xác định danh mục các metrics phần cứng bắt buộc cần đo: thời gian vẽ thực tế (`actual_draw_time_sec`), quãng đường di chuyển đầu bút, sai số tọa độ vật lý. Ghi nhận rõ: `actual_draw_time_sec` chỉ áp dụng khi đo đạc trên máy thật vật lý (Mức 2); việc backend hiện tạm thời ghi thời gian mô phỏng vào trường này là implementation/contract debt cần tách biệt.
- [ ] *Nếu có máy vẽ và cáp kết nối:* Chạy smoke test trên giấy thật và lưu lại log dữ liệu thực nghiệm đầu tiên.
- [ ] *Nếu chưa có máy:* Ghi nhận rõ blocker phần cứng, tập trung hoàn thiện simulator để TV4 và TV2 có thể gọi giả lập mà không bị lỗi crash.

### Quy định phối hợp toàn nhóm trong Sprint
- **Họp đồng bộ kỹ thuật (Weekly Sync):** Họp ngắn 30 phút mỗi tuần một lần để rà soát blocker giữa các mảng do TV4 chủ trì.
- **Milestone cuối Sprint:** Chạy một phiên demo chung tích hợp: cùng một văn bản mẫu tiếng Việt, cùng seed cố định, chạy qua API Gateway, ghi log CSV đầy đủ và kiểm tra SVG xuất xưởng.
- **Quy trình Review chéo (Cross-review):**
  - **TV1 review TV4 & TV2:** Kiểm tra tính tái lập của dữ liệu, seed và khả năng trích xuất metrics của engine.
  - **TV2 review TV1 & TV4:** Đánh giá tính khả thi khi ánh xạ tham số động học và mô hình chuyển động vào cấu trúc nét chữ / Writer Profile.
  - **TV3 review TV2 & TV4:** Đánh giá tính thực tế của các giả định về vận tốc, gia tốc và mô hình thời gian thi công trên máy vẽ thật.
  - **TV4 review cả nhóm:** Kiểm tra tính tuân thủ contract API Spec, tính toàn vẹn của handwriting subsystem, cấu trúc log CSV và điều phối tích hợp toàn hệ thống.
- **Kỷ luật Contract:** Bất kỳ thay đổi nào liên quan đến tên trường, kiểu dữ liệu, mã lỗi hoặc cấu trúc SVG bắt buộc phải được ghi nhận và thống nhất trước khi cập nhật code.

---

## 3. Tiêu chí Hoàn thành (Definition of Done) cho từng Task
Một task trong backlog chỉ được tích `[x]` khi:
1. Đã có code/tài liệu trong git repo;
2. Có lệnh hoặc kịch bản kiểm chứng đi kèm;
3. Kết quả test/số liệu đã được lưu lại;
4. Không phá vỡ chức năng cũ (no regression);
5. Đã cập nhật tài liệu liên quan nếu có thay đổi hành vi;
6. Không tuyên bố vượt quá bằng chứng thực tế;
7. Đã được reviewer tương ứng nghiệm thu chéo.

---

## 4. Nhật ký tiến độ theo ngày (Progress Log by Date)

**Ngày 20/9**

| Thành viên | Nội dung thực hiện | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV4 | (1) Kiểm chứng và hoàn tất dứt điểm Strict Validation hardening toàn diện: 34/34 regression tests passed, bảo đảm nguyên tắc validation-before-side-effect.<br>(2) Hoàn tất BƯỚC A — Audit kiến trúc Trellis DAG / CA-VHC hiện tại ([`docs/06_audit_trellis_dag_report.md`](file:///Users/yingjunn_/Study_/Nckh_2026-2027/OmniDraw/docs/06_audit_trellis_dag_report.md)).<br>(3) Hoàn thành bản dự thảo thiết kế BƯỚC B — Diacritic-Aware State Architecture ([`docs/07_diacritic_aware_state_design.md`](file:///Users/yingjunn_/Study_/Nckh_2026-2027/OmniDraw/docs/07_diacritic_aware_state_design.md)) theo mô hình Hybrid (`GlyphVariant` + `DiacriticCandidate` $\rightarrow$ `CompositionState`), chuẩn hóa quy ước hệ tọa độ local/world, loại bỏ double-count chi phí vị trí, xác lập Single Source of Truth `DiacriticConfig`, khống chế candidate thô $K_{\text{raw}} \le 9$ chỉ cắt tỉa hard-invalid, và xây dựng danh mục 12 unit tests; chuyển sang trạng thái chờ review chéo từ TV2 trước khi sang Bước C (chưa sửa mã nguồn). | Không | Đang làm |

**Ngày 19/9**

| Thành viên | Nội dung thực hiện | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV1 & TV4 | Rà soát và chuẩn hóa toàn diện tài liệu kỹ thuật Dataset Chữ viết tay: tách bạch hoàn toàn giữa **Vietnamese Diacritic / CA-VHC Dataset** (cấu trúc, chính tả, anchor mỏ neo, offset, allographs do TV4 sở hữu quy tắc, TV1 chuẩn bị data) và **Writer Profile / Personalization Dataset** (đặc trưng cá nhân hóa, TV1 sở hữu, nghiên cứu mở rộng P2); xác lập nguyên tắc Shared Raw Input; ban hành tài liệu đặc tả kỹ thuật `08_handwriting_dataset_spec.md` gồm 12 chương; đồng bộ cross-references trên `01_tech-stack.md`, `02_roadmap.md`, `03_current-task.md`, `04_progress-log.md` và `OmniDraw_API_Spec-4.md`. | Không | Đã xong |

**Ngày 18/9**

| Thành viên | Nội dung thực hiện | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV4 | Hoàn tất Strict Validation & Final Validation Hardening toàn diện cho cả Handwriting Mode và Art Mode: loại bỏ triệt để silent fallback cho các trường `style`, `font`, `letter_type`, `seed`, `target_paper_size_mm`; chuẩn hóa mã lỗi `INPUT_INVALID_FORMAT`, `UNSUPPORTED_FONT`, `UNSUPPORTED_LETTER_TYPE`, `INVALID_SEED`, `EMPTY_TEXT`; chuẩn hóa contract Art Mode với resolving default `effective_style = "sketch"`, chặn trước pipeline đối với style sai/payload rỗng và kiểm chứng downstream (`call_args`) luôn nhận đúng style; validation xảy ra trước mọi side effect (request invalid không xóa/thay đổi cache); bộ test tự động `backend/test_handwriting_validation.py` đạt 34/34 passed trong repository đầy đủ. | Không | Đã xong |
| Cả nhóm | Rà soát và đồng bộ toàn bộ 4 tài liệu quản lý dự án OmniDraw, loại bỏ triệt để xung đột về ownership, baseline, mức ưu tiên P2 và phân định thời gian vẽ thực tế vs mô phỏng. | Không | Đã xong |

**Ngày 17/9**

| Thành viên | Nội dung thực hiện | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| Cả nhóm | Rà soát và đồng bộ toàn bộ tài liệu kỹ thuật/nghiên cứu theo code thực tế và định hướng CA-VHC; phân định rõ 4 trạng thái (Đã triển khai, Đang phát triển, Định hướng nghiên cứu, Demo); loại bỏ toàn bộ tuyên bố quá mức. | Không | Đã xong |
| Cả nhóm | Tinh chỉnh toàn diện Roadmap và phân công 4 đường chạy độc lập (TV1, TV2, TV3, TV4), thiết lập hệ thống ưu tiên P0–P3, lộ trình theo Decision Gates, DoD và quy tắc merge code do TV4 điều phối. | Không | Đã xong |
| TV4 | Chuẩn hóa API Spec v1.4 bảo toàn contract hiện hành, bổ sung phụ lục mở rộng non-binding cho Writer Profile, Layout & Phân trang, và Telemetry phần cứng. | Không | Đã xong |
| TV4 | Thiết kế cơ chế đưa dấu tiếng Việt theo chính tả và vùng cấm va chạm vào Trellis DAG; chuẩn bị khung Báo cáo NCKH 5 chương; theo dõi tính nhất quán code–contract. | Không | Đang làm |
| TV2 | Soạn thảo câu hỏi nghiên cứu (RQ) về tối ưu đường vẽ và chi phí động học (đóng góp vào khung RQ toàn đề tài do TV4 điều phối); chuẩn bị chuẩn hóa hàm mục tiêu chuyển động và 2 bộ baseline đối chứng. | Không | Đang làm |

**Ngày 14/9**

| Thành viên | Đang làm gì | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV4 | Tái cấu trúc cơ học toàn diện font pack ra khỏi `handwriting_engine.py` thành gói `backend/handwriting/font_packs/` (`__init__.py`, `geometry.py`, `legacy.py`, `omni_casual.py`, `letter_variants.py`), giảm hơn 1.000 dòng code khỏi engine; hoàn thiện font Omni Casual v1 với 81 glyphs custom. | Không | Đã xong |
| TV4 & TV2 | Định hình khung thuật toán CA-VHC (TV4: Handwriting Composition Core & state representation; TV2: Stroke/Path Optimization Core & transition cost). | Không | Đang làm |
| TV4 | Cập nhật toàn bộ hệ thống tài liệu `docs/` (`01_tech-stack.md`, `02_roadmap.md`, `03_current-task.md`, `04_progress-log.md`) và tài liệu định hướng đề tài với vai trò Project Lead. | Không | Đã xong |

**Ngày 13/9**

| Thành viên | Đang làm gì | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV4 | Thiết kế và hoàn thiện phiên bản nền tảng v1 của Single-Stroke Vector Centerline Engine (`backend/handwriting/`), chuẩn hóa các glyph tiếng Việt nét đơn chuẩn Bộ GD&ĐT (e, c, k, s, x, i, t, h và hệ thống dấu hỏi, huyền, ngã, nặng, sắc); tích hợp vào luồng sinh SVG (chưa bao gồm diacritic-aware DAG, delayed-stroke ordering, Writer Profile và máy thật). | Không | Đã xong |
| TV4 | Cập nhật UI CreateScreen với giao diện viết thư tay chuyên dụng (chọn font, UI controls căn lề trang và giãn dòng, tải file văn bản), kết nối trực tiếp với backend `handwriting_engine` (lưu ý backend layout engine, áp dụng lề thực tế và font size chưa hoàn thiện). | Không | Đã xong |

**Ngày 30/8**

| Thành viên | Đang làm gì | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV1 & TV4 | Tích hợp thành công code gọi AI sinh ảnh (TV1) vào API Gateway (TV4), fix lỗi cấu trúc JSON, chuẩn bị chuyển sang dùng Gemini API. | Không | Đã xong |
| TV2 & TV4 | Đưa code thuật toán tối ưu nét vẽ tranh (TV2) vào Gateway (TV4). Tạo luồng: AI Sinh ảnh -> Chuyển SVG (lưu cache metrics) -> Ghi log CSV. | Không | Đã xong |
>>>>>>> develop
