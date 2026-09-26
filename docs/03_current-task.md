# OmniDraw — Current Task & Sprint Backlog

**Cập nhật lần cuối:** 22/09/2026
**Chu kỳ hiện tại:** Sprint 1–2 (2 tuần tới: Khóa nền nghiên cứu CA-VHC & Thiết lập framework thực nghiệm)
**Nguyên tắc:** Mỗi người làm chủ một đường chạy độc lập, tuân thủ Definition of Done và review chéo định kỳ.

---

## 1. Trạng thái hiện tại theo 4 đường chạy (Current Sprint Status)


| Thành viên                 | Đang làm gì                            | Bị nghẽ ở đâu (nếu có)                  | Dự kiến xong |
| -------------------------- |----------------------------------------| --------------------------------------- | ----------- |
| TV1 — AI Core              | Đã hoàn tất Cross-review Chương 1–3 (Phiếu TV1: PASS) & đóng băng Benchmark Corpus v1.0 | *(điền, hoặc để trống nếu không nghẽn)* | Sprint 1–2  |
| TV2 — AI Ứng dụng/CV       | *(điền)*                               | *(điền)*                                | *(điền)*    |
| TV3 — Phần cứng            | Hoàn tất ký duyệt cross-review Chương 1–3 (PASS trên commit 031d198), ban hành Protocol kiểm chuẩn và tích hợp RQ3 Benchmark CLI | Blocked by hardware: chờ máy vẽ AxiDraw & cáp USB vật lý để chạy thực nghiệm trên giấy thật | Sprint 1–2  |
| TV4 — Giao diện & Tích hợp | (điền)                                 | *(điền)*                                | *(điền)*    |


**Ngày 26/8**


|                            |                                |         |           |
| -------------------------- | ------------------------------ | ------- | --------- |
| TV4 — Giao diện & Tích hợp | *Dựng khung UI UX( mock data)* | *Không* | *Đã Xong* |


---

| Thành viên / Đường chạy | Nhiệm vụ trọng tâm Sprint 1–2 | Điểm nghẽn (Blocker) | Trạng thái |
| :--- | :--- | :--- | :--- |
| **TV4 — Project Lead & Handwriting / CA-VHC Composition Lead** | Hoàn tất Strict Validation, BƯỚC A/B, PR1, Pre-PR3 Acceptance Contract, khóa Hợp đồng E4 cùng TV2; chuẩn bị triển khai PR3 (Diacritic-Aware Trellis DAG) | Không | 🟡 Đang làm |
| **TV2 — Stroke Optimization & Path Planning Lead** | Step B technical cross-review đã PASS; PR2 baseline adapters B1/B2/B3 đã triển khai; đã cùng TV4 ký duyệt Hợp đồng Giao diện Chuyển tiếp E4 (Docs 18) khóa hàm mục tiêu $J$ | Không | 🟢 Hoàn tất E4 |
| **TV1 — AI Data & Writer Profile Lead** | Hoàn tất Phân tích độ phủ P01–P04 (Báo cáo 20) và Ban hành Quy trình Vận hành Thu thập & Xử lý lỗi (Chính sách 21); Hoàn thành Scan-Validation Pipeline (11/11 tests pass); Benchmark Corpus v1.0 đã đóng băng; Đang chờ thiết bị máy in/máy quét để thực hiện bench scan 600 DPI và chạy Pilot 3–5 writers | Blocked by hardware: chờ máy in & máy quét 600 DPI để bench scan P01–P04 | 🟡 Đang chờ thiết bị |
| **TV3 — Hardware, Calibration & Physical Validation Lead** | Đã hoàn tất HAL/Simulator (PR #29); phiếu cross-review Chương 1–3 đã ký `PASS` (hoàn tất scoped recheck trên `031d198`); ban hành Giao thức Kiểm chuẩn Vật lý (`07_physical_calibration_protocol.md`), tiêu bản RQ3 SVG và tích hợp CLI `--benchmark-rq3` (27/27 tests pass) | *Blocked by hardware:* chờ setup cáp & máy vẽ thực tế (hoàn tất 100% nền tảng phần mềm; chờ máy thật để chạy calibration) | 🟡 Đang làm |

---

## 2. Backlog chi tiết Sprint 1–2 (Kế hoạch hành động 2 tuần tới)

### TV4 — Project Lead & Handwriting / CA-VHC Composition Lead
- [ ] **Điều phối kỹ thuật & Khóa Research Questions (Project Lead):** TV4 đã hoàn tất bản hợp nhất RQ1–RQ3, giả thuyết, methodology blueprint và cross-review gate tại [`10_nckh_research_plan.md`](10_nckh_research_plan.md). Ba phiếu reviewer đã ký PASS, nhưng chưa khóa RQ vì phiếu TV2 còn lệch metadata checkpoint và TV1/TV3 cần scoped recheck các mục bị sửa sau checkpoint.
- [x] **✅ Tổng hợp Chương 2 theo quy trình nghiên cứu có kiểm soát:** Đã hoàn tất seed search và citation chaining vòng 1, mở rộng evidence matrix từ 11 lên 16 nguồn đã xác minh metadata, bổ sung delayed-stroke handling, kinematic synthesis, robotic sequential writing, trajectory optimization và phản chứng CASHG đối với novelty rộng. Chương 2 v0.2 đã thu hẹp khoảng trống về tổ hợp ràng buộc dấu tiếng Việt + collision/clearance + finite-state composition + chi phí single-stroke plotter. Ba phiếu đã ký PASS nhưng scoped recheck và version binding còn chờ; chưa tuyên bố systematic review hoặc novelty cuối cùng trước team screening và citation chaining vòng 2.
- [x] **✅ Khởi tạo Chương 1 — Mở đầu:** Đã lập bản thảo tại [`14_chapter_1_introduction.md`](14_chapter_1_introduction.md) theo cấu trúc bối cảnh → khoảng trống provisional → vấn đề → mục tiêu → RQ1–RQ3 → phạm vi → phương pháp → đóng góp dự kiến. Bản thảo đã được review tại checkpoint, scoped recheck còn chờ; không trình bày giả thuyết hoặc tiêu chí nghiệm thu như kết quả.
- [x] **✅ Khởi tạo Chương 3 — Phương pháp nghiên cứu và thiết kế thuật toán:** Đã lập và cập nhật bản thảo tại [`15_chapter_3_methodology.md`](15_chapter_3_methodology.md); baseline adapters PR2 hiện là `IMPLEMENTED_AND_TESTED`, shared interface E4 đã `PASS` trên contract `4677aad`; PR3–PR5 và TV3 calibration vẫn chưa hoàn tất. Bản thảo chưa trình bày kết quả thực nghiệm.
- [x] **✅ Strict Validation completed (34/34 automated tests PASS):** Đã loại bỏ triệt để silent fallback, khóa chặt chẽ mode-aware validation theo từng `input_type`, bảo đảm validation diễn ra trước mọi side effect, và bảo đảm an toàn toàn diện cho pipeline backend; toàn bộ 34 automated tests trong `backend/test_handwriting_validation.py` đạt 34/34 passed:
  - *Handwriting Mode (`input_type in {"handwriting", "letter"}`):* Bắt buộc có `style` trong `STYLE_CONFIGS`, khuyết/null/sai kiểu trả `INPUT_INVALID_FORMAT`; text rỗng trả `EMPTY_TEXT`; `options.font` không truyền default `"oly"`, sai/null trả `UNSUPPORTED_FONT`; `options.letter_type` không truyền default `"general"`, sai/null/không tương thích trả `UNSUPPORTED_LETTER_TYPE`; `options.seed` sai kiểu/biên trả `INVALID_SEED`; `options.target_paper_size_mm` khuyết nhận default A4 `[210, 297]`, explicit `null`/sai kiểu/len $\neq 2$/không dương/NaN/Inf trả `INPUT_INVALID_FORMAT`.
  - *Art Mode (`input_type in {"text", "image"}`):* Phong cách hợp lệ thuộc `ART_MODE_STYLES` (`sketch`, `line_art`, `stipple`, `hatching`). Khi `style` khuyết hoặc `null`, tự động giải quyết an toàn thành `effective_style = "sketch"` trước pipeline; khi truyền `style` không hợp lệ (`""`, số, mảng, bool, hoặc chuỗi ngoài enum kể cả style handwriting) $\rightarrow$ từ chối ngay với `INPUT_INVALID_FORMAT` không gọi pipeline; `text` bắt buộc có `prompt` không rỗng; `image` bắt buộc có `image_base64` không rỗng; toàn bộ downstream (`call_openai_image_api`, `svg_process`, metadata logging) được assert kiểm chứng luôn nhận `effective_style`, không bao giờ nhận `None`.
  - *Invalid input_type:* Mọi `input_type` lạ (kể cả `null`, số, chuỗi rỗng) đều được Gateway xử lý trả lỗi có cấu trúc `INPUT_INVALID_FORMAT`.
  - *Validation trước side effect:* Request invalid tuyệt đối không gọi `_clear_cached_svg_for_request` và không xóa/thay đổi SVG hay cache hiện có; request hợp lệ thực hiện cleanup đúng 1 lần trước khi pipeline chạy.
- [x] **✅ BƯỚC A — Trellis DAG / CA-VHC Architecture Audit completed:** Hoàn tất rà soát read-only toàn diện kiến trúc hiện tại, ban hành báo cáo kỹ thuật [`06_audit_trellis_dag_report.md`](06_audit_trellis_dag_report.md). Audit xác nhận các điểm then chốt:
  - Current DAG chỉ tối ưu base glyph variants (`std`, `mid_in`, `high_out`, `closed`, `isolated`).
  - `GlyphVariant` chưa chứa diacritics hay thông tin dấu.
  - Tiền xử lý Unicode NFD đã tách đúng base character + combining marks.
  - `generate_accents()` hiện đang chạy hoàn toàn POST-DAG theo tọa độ mỏ neo tĩnh.
  - Runtime bridge collision (`bridge_collision_cost`) chưa xét va chạm với dấu tiếng Việt.
  - Delayed-stroke optimization chưa được triển khai trong engine.
  - Current DAG recurrence vẫn là Viterbi chuẩn: $DP[i, j] = \min_p (DP[i-1, p] + \text{transition\_cost})$.
- [x] **✅ BƯỚC B — Diacritic-Aware State Architecture Design (Design approved and closed):** Khóa kiến trúc state mới cho CA-VHC: `GlyphVariant` giữ nguyên semantic biến thể hình học thân chữ gốc (base-glyph), `DiacriticCandidate` biểu diễn cấu hình dấu ở tọa độ cục bộ (local coordinates: marks, placement, clearance zone, offsets), `CompositionState` trở thành node logic chính thức của Trellis DAG. Phân tách rõ State Cost $C_{\text{state}}$ (TV4) và Transition Cost $J_{\text{transition}}$ (TV2/TV4), kiểm soát cắt tỉa cứng các ứng viên bất hợp lệ ($K_{\text{raw}} \le 9$), xác lập mục tiêu bảo toàn hành vi cho ký tự không dấu (ASCII), và xây dựng chiến lược 12 unit tests trước khi triển khai mã nguồn (Đặc tả thiết kế: [`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md)).
  - *Sub-status:*
    - Architecture draft: DONE
    - Internal design review & technical cleanup: DONE
    - TV2 cross-review: COMPLETED / PASS
    - Software Step C authorization: AUTHORIZED by TV4
    - Source implementation: READY TO START (PR1)
    - Step C readiness: YES (Software implementation authorized; formal experiment readiness: NO)
  - *Lưu ý phạm vi:* TV4 bắt đầu triển khai PR1 (Metrics & Experiment Infrastructure). Không bắt đầu PR3 (CompositionState) trước khi PR1 có test và metric baseline ổn định. TV1 corpus freeze và TV3 hardware calibration là downstream validation gates.
- [x] **✅ BƯỚC C / PR1 — Hoàn thiện internal experiment metrics and CSV integration (Commit `daca566`):** Tích hợp hoàn tất CA-VHC internal metrics evaluator (`backend/handwriting/metrics_evaluator.py`), chuẩn hóa hệ thống ghi log CSV (`backend/logs/csv_logger.py`) theo schema 19 cột bất biến, hoàn thành automated experiment runner (`backend/handwriting/experiment_runner.py`), và khóa fixture kiểm chuẩn DEV 160 trường hợp (`tests/fixtures/ca_vhc_pr1_fingerprints.json`) với toàn bộ automated tests đạt PASS.
- [x] **✅ Pre-PR3 Acceptance Contract & Khóa Snapshot ASCII (Docs 09):** Ban hành Hợp đồng Nghiệm thu Kỹ thuật trước PR3 ([`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md)); E1–E5 đã PASS sau sign-off E4 của TV2/TV4 trên contract `4677aad`; FORMAL EXPERIMENT READINESS: NO.
- [ ] **BƯỚC C / PR3 — CA-VHC Diacritic-Aware Trellis DAG (TV4 lead, TV2 phối hợp):** Triển khai `CompositionState = (GlyphVariant, DiacriticCandidate)`, tích hợp kiểm tra va chạm dấu tiếng Việt vào Trellis DAG recurrence và dynamic diacritic placement.
- [ ] **Automated Experiment Matrix Execution:** Chạy tự động ma trận thực nghiệm sau khi PR2 và PR3 hoàn thành (không chạy holdout trước khi TV1 freeze corpus).
- [ ] **Public Metric Schema:** Định nghĩa public metric schema chỉ cho các trường backend thực sự xuất ổn định; giữ API Spec cập nhật qua PR riêng.
- [ ] **Backward Compatibility:** Bảo toàn tuyệt đối public API hiện tại (`generate_handwriting_svg`, `text_to_strokes`) và deterministic behavior.
- [x] **✅ Tiêu chuẩn định lượng kiểm thử dấu:** Đã khóa quy tắc phán quyết thực thi cho va chạm bridge–diacritic trong `classify_diacritic_clearance_acceptance`: `FAIL` khi có va chạm hoặc $d_{min}<0.20\,mm$; `INCONCLUSIVE` trong $[0.20,0.50)\,mm$; `PASS_PROVISIONAL_TARGET` khi $d_{min}\ge0.50\,mm$; `NOT_APPLICABLE` khi không có cặp bridge–diacritic hợp lệ. Đã khóa unit test tại đúng các điểm biên và fail closed với metric không hợp lệ. Ngưỡng $0.50\,mm$ vẫn chờ TV3 hiệu chuẩn, không phải tuyên bố an toàn vật lý.
- [ ] **Visual QA cho PR3:** Sau khi có mã nguồn PR3, mở rộng `backend/handwriting/qa_specimens.py` bằng tập DEV acceptance và nhóm chẩn đoán `lụy/thụy/quỹ/nguyễn/nghiễm`; nhóm chẩn đoán không được trộn vào corpus nghiệm thu hoặc dùng để tuyên bố kết quả chính thức.
- [x] **✅ Khung Báo cáo NCKH Chương 3–4:** Đã dựng outline chi tiết, bảng kết quả rỗng, threats to validity và quy tắc không công bố kết quả chưa đo tại [`10_nckh_research_plan.md`](10_nckh_research_plan.md). Trạng thái viết nội dung hoàn chỉnh và kết quả thực nghiệm vẫn `PENDING`.
- [ ] *Lưu ý phạm vi:* Chưa cần thiết kế thêm Font Pack mới trong sprint này; tập trung tối ưu trên 2 pack hiện có (`omnidraw_legacy` và `omni_casual`).

### TV2 — Stroke Optimization & Path Planning Lead
- [x] **Cross-review Kiến trúc Bước B (Diacritic-Aware State Architecture):** TV2 đã hoàn tất review với kết luận PASS; baseline và ownership đã được thống nhất; verdict tài liệu: SPEC STATUS: APPROVED AND CLOSED FOR STEP B; quyết định Step C: AUTHORIZED / READY FOR STEP C: YES (cấp phần mềm); nhiệm vụ tiếp theo là PR2 baseline adapters (B1, B2, B3) và phối hợp transition-cost interface cho PR3.
- [x] **✅ PR2 — Chuẩn Hóa và Khóa Ba Baseline Đối Chứng B1, B2, B3 (TV2 chủ trì, TV4 phối hợp):** Đã đóng gói 3 adapter độc lập trong `backend/handwriting/baselines.py`: B1 `b1_static` dùng canonical glyph và luôn lift; B2 `b2_greedy` chọn tham lam theo trạng thái trước đã chọn; B3 `b3_current_trellis` giữ nguyên Viterbi hiện hành. `experiment_runner.py` gọi riêng từng baseline qua `--method`; public renderer API và fingerprint B3 mặc định được bảo toàn. Kiểm chứng phiên TV2: full suite `73 passed`, engine/path-optimizer self-check PASS.
- [ ] **Đặc tả học thuật tối ưu chuyển động:** Xây dựng và soạn thảo câu hỏi nghiên cứu / giả thuyết chuyên sâu về tối ưu đường nét, quãng đường nhấc bút (pen-up distance minimization), chi phí động học và thời gian thi công trên máy vẽ vật lý (đóng góp vào khung RQ chung do TV4 tổng hợp).
- [ ] **Toán học hóa chi phí chuyển động:** Chuẩn hóa ký hiệu toán học hình thức: Phương trình Bellman Viterbi DP cho transition cost, biểu thức chi phí động học Kinematic Turn Penalty $\text{dist} + \lambda(1 - \cos\theta)$, và pen-up distance.
- [ ] **Chuẩn hóa 2 bộ baseline đối chứng:**
  - *Bộ baseline Art Mode / Path Optimization (TV2 lead):* (1) Original contour order / Naive; (2) Greedy Nearest Neighbor; (3) OmniDraw `cKDTree + Or-opt + Kinematic Turn Penalty`.
  - *Bộ baseline Handwriting CA-VHC (TV2 phụ trách metric chuyển động, TV4 lead composition & runner):* (1) Static Glyph Renderer; (2) Greedy contextual/connection heuristic; (3) Current Trellis DAG (chưa có ràng buộc dấu nâng cao). *(Phương pháp đề xuất CA-VHC mở rộng là đối tượng nghiên cứu được đánh giá, không tính là baseline đối chứng thứ tư).*
- [x] **Phối hợp hàm mục tiêu $J$ / Entry Gate E4:** Adapter PR2 tiếp tục tái sử dụng `eval_transition()` hiện hành cho B3/default; TV2 và TV4 đã ký contract `4677aad` tại [`18_pr3_e4_shared_transition_contract_draft.md`](18_pr3_e4_shared_transition_contract_draft.md), khóa interface PR3 riêng, world geometry, error semantics và quy tắc tránh double-count `cost_legibility`. E4 `PASS`; PR3 `READY_TO_IMPLEMENT`, chưa được coi là đã hoàn thành.
- [ ] **Định lượng hiệu năng:** Xây dựng tiêu chuẩn định lượng đánh giá hiệu quả giảm quãng đường pen-up và độ mượt chuyển động ngòi bút trên tập corpus thử nghiệm.
- [ ] *Lưu ý phạm vi:* Tập trung vào thuật toán tối ưu chuyển động, không sửa logic hình học hay quy tắc ngữ cảnh trong `backend/handwriting/`.

### TV1 — AI Data & Writer Profile Lead
- [x] **✅ Hoàn thành Thiết kế & Đặc tả Kỹ thuật OmniDraw Handwriting Collection Sheet Pack v1 (P01–P04 Pilot Candidate):** Hoàn tất thiết kế vector SVG, xuất bản in PDF A4 và biên soạn tài liệu đặc tả kỹ thuật chi tiết cho cả 4 trang biểu mẫu: P01 (*Isolated Characters & Diacritics*), P02 (*Context & Ligatures*), P03 (*Sentence Flow & Pangrams*), P04 (*Natural Paragraph*). Đã chuẩn hóa: mốc định vị quang học 4 góc (Fiducials), khối kiểm chuẩn thước đo 50mm và ô vuông 20×20mm, khung bao tất định (`bbox_mm`, `writing_bbox_mm`), ranh giới nghiêm ngặt không thu thập PII, làm sạch văn phong học thuật (loại bỏ suy diễn độ mỏi, phân định rạch ròi dữ liệu quét tĩnh vs. động học). Trạng thái hiện hành: **PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)**. Toàn bộ tài liệu, PDF, SVG và script sinh tự động được lưu trữ tại `docs/collection_sheets/P01..P04`.
- [x] **✅ Nhiệm vụ 1 — Scan-Validation Pipeline tối thiểu:** Đã lập trình hoàn chỉnh gói `backend/scan_validator/` và CLI runner xử lý ảnh quét phẳng 600 DPI: tự động phát hiện 4 mốc fiducial (`detect_fiducials`), nắn chỉnh phối cảnh / deskew (`rectify_scan` sang chuẩn ISO A4 $4961 \times 7016\text{ px}$), kiểm chuẩn thước đo $50.0 \pm 0.2\,\text{mm}$ và ô vuông tỷ lệ cạnh $1.000 \pm 0.005$ (`check_calibration`), tự động bóc tách ô viết (`crop_sheet` cho P01–P04), đánh giá QC tràn viền lề và nét dơ nền (`evaluate_crop_qc`), và xuất báo cáo JSON chuẩn hóa. Đạt 11/11 tests pass trong `tests/test_scan_validation_pipeline.py`.
- [ ] **Nhiệm vụ 2 — Bench Print & 600 DPI Bench Scan P01–P04:** Tiến hành in thử nghiệm thực tế bộ 4 trang trên máy in laser độ nét cao giấy A4 tiêu chuẩn $80\,\text{g/m}^2$, quét lại bằng máy quét phẳng quang học $600\,\text{DPI}$ (True scale 1:1, lossless PNG) và chạy qua pipeline kiểm chuẩn.
- [ ] **Nhiệm vụ 3 — Fiducial Detection Test:** Kiểm thử độ ổn định của giải thuật định vị 4 mốc góc quang học trên các bản quét thật có nhiễu xoay/dịch chuyển nhẹ.
- [ ] **Nhiệm vụ 4 — Deskew / Page Rectification Validation:** Xác minh độ chính xác góc xoay bù và phép biến đổi phối cảnh trên ảnh scan bench test.
- [ ] **Nhiệm vụ 5 — Scale / Calibration Validation:** Kiểm chứng sai số co giãn quang học trục X/Y trên thước đo và ô vuông kiểm chuẩn theo ngưỡng kỹ thuật pilot ($\pm 0.2\,\text{mm}$ và $\pm 0.005$).
- [ ] **Nhiệm vụ 6 — Deterministic Crop Validation:** Kiểm chứng độ chính xác cắt tự động vùng viết tay từng ô/dòng đối chiếu với bảng tọa độ `writing_bbox_mm`.
- [x] **✅ Nhiệm vụ 7 — Phân tích Độ phủ Ngữ âm & Ngữ cảnh (Coverage Analysis) hoàn thành:** Đã hoàn thành phân tích định lượng chi tiết độ phủ âm vị học, thanh điệu và ngữ cảnh cho cả 4 trang P01–P04, lập bảng ma trận tổng hợp và ban hành Báo cáo chính thức tại [`docs/20_p01_p04_coverage_analysis_report.md`](20_p01_p04_coverage_analysis_report.md) (`Trạng thái: APPROVED FOR PILOT PHASE`).
- [x] **✅ Nhiệm vụ 8 — Ban hành Quy định Vận hành Thu thập & Xử lý Lỗi (Collection Protocol & Error Handling) hoàn thành:** Đã ban hành chính sách vận hành chuẩn hóa tại [`docs/21_handwriting_collection_protocol_and_error_handling.md`](21_handwriting_collection_protocol_and_error_handling.md) quy định: chính sách No-PII, nguyên tắc bảo toàn nét tự nhiên, phân loại 3 nhóm lỗi và biện pháp xử lý cấp ô/dòng/trang, định mức cấp phát và hủy phiếu dự phòng (Spare Sheet), vòng đời 5 trạng thái QC (`QC_RAW` $\rightarrow$ `QC_VERIFIED_PASS` / `QC_REJECTED`), và cấu trúc schema `collection_manifest.jsonl`.
- [ ] **Nhiệm vụ 9 — Chuẩn bị & Triển khai Thử nghiệm Pilot (Limited Pilot 3–5 Writers):** Tuyển chọn 3–5 người tham gia viết thử nghiệm toàn bộ bộ phiếu P01–P04, rà soát tải thu thập (`completion time`, nhu cầu nghỉ giải lao) và nghiệm thu chất lượng ảnh quét trước khi mở rộng. *(Tiến hành ngay sau khi có máy in/máy quét để bench scan P01–P04)*.
- [x] **✅ Chuẩn bị, rà soát độ phủ và đóng băng Benchmark Corpus CA-VHC v1.0:** Hoàn thành phân tích độ phủ ngôn ngữ học, độ phủ hình học (ascender/descender, diacritics stacking) và kiểm chứng tính rời nhau tuyệt đối ($DEV \cap HOLDOUT = \emptyset$) cho 20 từ DEV và 20 từ Holdout. Chính thức đóng băng phiên bản `CA-VHC-CORPUS-v1.0-FROZEN` tại [`docs/19_benchmark_corpus_freeze_report.md`](19_benchmark_corpus_freeze_report.md).
- [x] **✅ Chuẩn bị nghiên cứu Writer Profile (P2 Preparation) hoàn thành:** Đã định nghĩa JSON Schema chính thức [`dataset/schemas/writer_profile.schema.json`](../dataset/schemas/writer_profile.schema.json) tuân thủ Section 8 của `08_handwriting_dataset_spec.md`, quy định cấu trúc versioned profile, metadata ẩn danh, miền giá trị nghiêm ngặt của `global_style`, `spacing`, và `diacritic_tendencies`.
- [x] **✅ Prototype trích xuất đặc trưng độc lập (P2 Preparation) hoàn thành:** Lập trình module [`backend/writer_profile/extractor.py`](../backend/writer_profile/extractor.py) trích xuất đầy đủ 4 đặc trưng định lượng: độ nghiêng `mean_slant_deg`, tỷ lệ khung chữ `aspect_ratio_mean`, khoảng cách chữ/từ `char_spacing` / `word_spacing`, và độ dao động chân dòng `baseline_jitter_std`, kèm hàm kiểm định rule-based `validate_writer_profile`.
- [x] **✅ Tạo fixture dữ liệu mẫu giả lập & Unit Test Suite hoàn thành:** Tạo synthetic fixture [`tests/fixtures/writer_profile_synthetic_samples.json`](../tests/fixtures/writer_profile_synthetic_samples.json) (3 hồ sơ mẫu: thẳng đứng, nghiêng 15 độ, chân dòng dao động) và bộ test [`tests/test_writer_profile_extractor.py`](../tests/test_writer_profile_extractor.py) đạt **7/7 tests PASS**; toàn bộ test suite dự án đạt **165/165 tests PASS** (100% PASS).
- [ ] *Lưu ý phạm vi:* Đây là công việc chuẩn bị P2; chưa tích hợp Writer Profile vào engine, chưa được xem là Writer Profile MVP hoàn thành; không huấn luyện mô hình học sâu (deep learning) phức tạp trong sprint này; ưu tiên hoàn thiện quy trình rule-based rõ ràng và có thể kiểm chứng (chi tiết xem [`08_handwriting_dataset_spec.md`](08_handwriting_dataset_spec.md)).

### TV3 — Hardware, Calibration & Physical Validation Lead
- [x] Chuẩn hóa và đồng nhất interface phần mềm chung (`HardwareAdapterInterface`) dùng chung cho cả phần cứng AxiDraw thật và bộ giả lập simulator/fake driver.
- [x] Chuẩn bị file SVG fixture chuẩn (`tests/fixtures/smoke_test_specimen.svg` và `tests/fixtures/bezier_length_test.svg`) chứa nét thẳng, Bézier, Arc, handwriting và pen-up.
- [x] Lập và validate Calibration Profile YAML (`config/calibration_profile.yaml`), nạp tự động thông số vận tốc, gia tốc, nâng hạ bút và offset 5mm.
- [x] Xác định danh mục metrics phần cứng bắt buộc đo: phân biệt rạch ròi simulator/fake driver (`is_simulated=True`, `actual_hardware_measured=False`) và máy vẽ thật (`is_simulated=False`, `actual_hardware_measured=True`).
- [x] **Hoàn tất ký duyệt Cross-review Báo cáo NCKH Chương 1–3** (phiếu [`docs/reviews/tv3_chapter_1_3_review.md`](reviews/tv3_chapter_1_3_review.md)): xác nhận phân tách rõ rệt thời gian mô phỏng vs `actual_draw_time_sec`, giữ đúng ranh giới an toàn vật lý của clearance, hoàn tất scoped recheck trên commit `031d198` với `HUMAN_VERDICT: PASS`, workflow `CLOSED`.
- [x] **Ban hành Giao thức Kiểm chuẩn & Thực nghiệm Vật lý Máy vẽ** ([`docs/hardware/07_physical_calibration_protocol.md`](hardware/07_physical_calibration_protocol.md)): quy chuẩn hóa vật tư (Double A A4 80gsm, bút gel Pentel EnerGel/Pilot G2 0.5mm), phương pháp đo loang mực qua scan quang học 600 DPI, và ma trận kiểm tra clearance/góc cua nhọn cho RQ3.
- [x] **Chuẩn bị Tiêu bản Kiểm chuẩn RQ3 SVG** ([`tests/fixtures/rq3_clearance_calibration_specimen.svg`](../tests/fixtures/rq3_clearance_calibration_specimen.svg)): thang khoảng hở $0.10 \to 0.70\,\text{mm}$, góc cua $60^\circ, 90^\circ, 120^\circ, 150^\circ$, dải nhấc bút nhanh 28 chu kỳ, và thước chuẩn 50.0mm.
- [x] **Tích hợp CLI Benchmark Tự động RQ3:** hoàn thiện hàm `run_rq3_calibration_benchmark()` và CLI `--benchmark-rq3` trong `backend/hardware_adapter.py`, tự động thu thập telemetry và ghi log `logs/hardware_metrics.csv` (27/27 tests PASS trong `tests/test_hardware_adapter.py`).
- [ ] *Nếu có máy vẽ và cáp kết nối:* Chạy benchmark trên giấy thật theo đúng giao thức để đo `actual_draw_time_sec` và đóng cổng `PENDING_TV3_CALIBRATION`. *(Blocked by hardware: chờ máy vẽ & cáp vật lý)*.
- [x] *Nếu chưa có máy:* Đã hoàn tất 100% nền tảng phần mềm, fake driver, simulator, SVG fixtures, giao thức kiểm chuẩn, và benchmark runner sẵn sàng cho ngày cắm máy thật.


### Quy định phối hợp toàn nhóm trong Sprint
- **Họp đồng bộ kỹ thuật (Weekly Sync):** Họp ngắn 30 phút mỗi tuần một lần để rà soát blocker giữa các mảng do TV4 chủ trì.
- **Milestone cuối Sprint:** Chạy một phiên demo chung tích hợp: cùng một văn bản mẫu tiếng Việt, cùng seed cố định, chạy qua API Gateway, ghi log CSV đầy đủ và kiểm tra SVG xuất xưởng.
- **Quy trình Review chéo (Cross-review):**
  - **TV1 review TV4 & TV2:** Kiểm tra tính tái lập của dữ liệu, seed và khả năng trích xuất metrics của engine.
  - **TV2 review TV1 & TV4:** Đánh giá tính khả thi khi ánh xạ tham số động học và mô hình chuyển động vào cấu trúc nét chữ / Writer Profile.
  - **TV3 review TV2 & TV4:** Đánh giá tính thực tế của các giả định về vận tốc, gia tốc và mô hình thời gian thi công trên máy vẽ thật.
  - **TV4 review cả nhóm:** Kiểm tra tính tuân thủ contract API Spec, tính toàn vẹn của handwriting subsystem, cấu trúc log CSV và điều phối tích hợp toàn hệ thống.
- **Gói Cross-review Báo cáo NCKH Chương 1–3:**

  **Điểm vào vận hành cho người và AI:** bắt đầu tại [`reviews/README.md`](reviews/README.md). Mỗi reviewer chỉ cập nhật phiếu riêng ([TV1](reviews/tv1_chapter_1_3_review.md), [TV2](reviews/tv2_chapter_1_3_review.md), [TV3](reviews/tv3_chapter_1_3_review.md)); TV4 xử lý finding tại [`reviews/review_disposition.md`](reviews/review_disposition.md). AI chỉ được lập bản nháp finding; verdict cuối phải do reviewer con người xác nhận. Không bắt đầu formal review khi `REVIEW_TARGET_COMMIT` còn là `PENDING_CHECKPOINT_COMMIT`.

  | Reviewer | Tài liệu/phần bắt buộc | Trọng tâm phải xác nhận | Đầu ra bắt buộc | Gate |
  | :--- | :--- | :--- | :--- | :--- |
  | **TV1 — Data & Writer Profile** | [`10_nckh_research_plan.md`](10_nckh_research_plan.md); [`11_literature_review_protocol.md`](11_literature_review_protocol.md); [`12_literature_evidence_matrix.md`](12_literature_evidence_matrix.md); [Chương 1](14_chapter_1_introduction.md) mục 1.5 và 1.9; [Chương 2](13_chapter_2_literature_review.md) mục 2.2–2.3; [Chương 3](15_chapter_3_methodology.md) mục 3.1, 3.7 và 3.8 | Corpus coverage; DEV/Holdout governance; seed và reproducibility; ranh giới CA-VHC/Writer Profile; không mô tả dữ liệu planned như dữ liệu đã thu | Một verdict và danh sách finding có vị trí file/mục; xác nhận riêng corpus/leakage scope | Trước `RQ FREEZE: APPROVED` và trước formal PR5 |
  | **TV2 — Path Planning & Transition Cost** | [`10_nckh_research_plan.md`](10_nckh_research_plan.md); [Chương 1](14_chapter_1_introduction.md) mục 1.4; [Chương 2](13_chapter_2_literature_review.md) mục 2.4–2.6; [Chương 3](15_chapter_3_methodology.md) mục 3.3–3.5 và 3.8 | Định nghĩa B1/B2/B3; công thức $J_{transition}$; Viterbi recurrence; curvature/motion metrics; độ phức tạp; ranh giới giữa PR2 và Proposed | Một verdict và danh sách finding có vị trí file/mục; xác nhận baseline/transition interface hoặc nêu blocker PR2 | Trước `RQ FREEZE: APPROVED`; E3–E4 phải đạt trước khi mở PR3 |
  | **TV3 — Hardware & Physical Validation** | [`10_nckh_research_plan.md`](10_nckh_research_plan.md); [Chương 1](14_chapter_1_introduction.md) mục 1.4.3, 1.8–1.9; [Chương 2](13_chapter_2_literature_review.md) mục 2.5–2.6; [Chương 3](15_chapter_3_methodology.md) mục 3.1, 3.7–3.8 | Wording về khả năng thi công; simulator/máy thật; clearance; calibration; `actual_draw_time_sec`; không biến metric hình học thành claim an toàn vật lý | Một verdict và danh sách finding có vị trí file/mục; xác nhận wording vật lý hoặc ghi `BLOCKED_CALIBRATION` | Trước `RQ FREEZE: APPROVED`; calibration vẫn là downstream gate |
  | **TV4 — Integration Owner** | Toàn bộ [`10_nckh_research_plan.md`](10_nckh_research_plan.md) và [Chương 1](14_chapter_1_introduction.md), [Chương 2](13_chapter_2_literature_review.md), [Chương 3](15_chapter_3_methodology.md) | Tính nhất quán code–docs–RQ; citation boundary; trạng thái `IMPLEMENTED/DESIGN/PENDING`; xử lý mọi finding và cập nhật traceability | Bảng disposition từng finding (`ACCEPTED`, `REJECTED_WITH_REASON`, `DEFERRED_WITH_OWNER`) và bản tổng hợp sau sửa | Chỉ đóng gói review sau khi nhận đủ verdict TV1–TV3 |

- **Trạng thái quy trình:** `NOT_STARTED`, `IN_REVIEW`, `CHANGES_REQUESTED`, `READY_FOR_RECHECK`, `BLOCKED`, `CLOSED`; không dùng verdict thay cho trạng thái xử lý.
- **Verdict hợp lệ:** `PENDING`, `PASS`, `PASS_WITH_CHANGES`, hoặc `BLOCKED`. `PASS_WITH_CHANGES` chỉ được đóng sau khi TV4 ghi disposition và reviewer xác nhận thay đổi; `BLOCKED` phải nêu đúng dependency/owner, không được tự đổi thành PASS.
- **Mẫu finding tối thiểu:** `ID | Reviewer | File:mục | Mức độ CRITICAL/MAJOR/MINOR | Nhận xét | Đề xuất | Trạng thái xử lý`.
- **Ràng buộc phiên bản:** Mỗi verdict phải ghi commit hash hoặc ngày/bản thảo đã review. Review trên bản cũ không tự động áp dụng cho bản đã thay đổi nội dung khoa học.
- **Ranh giới phê duyệt:** TV4 là người tổng hợp, không thay thế cho review độc lập của TV1–TV3. Review tài liệu không đồng nghĩa PR2/PR3, formal experiment hoặc hardware validation đã hoàn thành.
- **Kỷ luật Contract:** Bất kỳ thay đổi nào liên quan đến tên trường, kiểu dữ liệu, mã lỗi hoặc cấu trúc SVG bắt buộc phải được ghi nhận và thống nhất trước khi cập nhật code.

---

## 3. Collection Sheet Pack — Quy định Dùng chung & Kế hoạch Dữ liệu (Shared Conventions & Data Plan)

### 3.1. Các quyết định dùng chung đã chốt (Shared Conventions)
- **Kiến trúc bộ phiếu 4 trang:**
  - `P01`: Isolated character / diacritic geometry (24 sample cells, representative samples, full coverage pending).
  - `P02`: Contextual words / ligatures (16 prompt words, 3 sections Initial / Medial / Final, Trial A/B).
  - `P03`: Sentence flow / pangrams (3 continuous sentence pangrams, natural wrap allowed, coverage analysis pending).
  - `P04`: Natural paragraph writing (`PARA_001`, 32 words, 5 lines, long-range handwriting geometry, static scan $\ne$ kinematics, no fatigue inference).
- **Quy chuẩn kỹ thuật hình học:**
  - Khổ giấy ISO A4 Portrait: $210.00\,\text{mm} \times 297.00\,\text{mm}$.
  - Nguồn chân lý hình học: Milimét ($mm$).
  - 4 mốc định vị quang học góc trang (Fiducial markers): $5.0\,\text{mm} \times 5.0\,\text{mm}$, khoảng cách tâm $D_x = 181.00\,\text{mm}$, $D_y = 268.00\,\text{mm}$, đường chéo $323.39\,\text{mm}$.
  - Bút viết quy chuẩn: Bút bi ngòi gel đen $0.5\,\text{mm}$ (Pentel EnerGel hoặc Pilot G2).
  - Khối kiểm chuẩn đo lường: Thước đo $50.0\,\text{mm}$ (Pilot check: $50.0 \pm 0.2\,\text{mm}$) và ô vuông $20.0 \times 20.0\,\text{mm}$ (Aspect Ratio: $1.000 \pm 0.005$).
  - Tiêu chuẩn số hóa: Quét phẳng (flatbed scanner) $600\,\text{DPI}$, 24-bit RGB hoặc 8-bit Grayscale, True Scale 1:1, Lossless PNG, tắt toàn bộ Auto-Contrast / Unsharp Mask / Despeckle.
  - Bảo mật tuyệt đối (Strict No PII): Không thu thập Họ tên, MSSV, SĐT, Email, hay Chữ ký; chỉ dùng `Writer ID: W_________` và `Session: S______`.
- **Quy ước đặt tên file quét thô (Raw Scan Naming):**
  $$\text{\{writer\_id\}\_\{session\_id\}\_\{page\_number\}.png}$$
  *Ví dụ:* `W001_S01_P01.png`, `W001_S01_P02.png`, `W001_S01_P03.png`, `W001_S01_P04.png`.
  *Lưu ý phân biệt rõ ràng:*
  - `writer_id`: Mã định danh người viết (person, ví dụ `W001`).
  - `session_id`: Mã phiên thu thập (collection session, ví dụ `S01`). Tuyệt đối không nhầm lẫn `session_id` với form version.
  - `page_number`: Mã số trang biểu mẫu (`P01`, `P02`, `P03`, `P04`).
  - `form_version`: Phiên bản biểu mẫu/template (ví dụ `ODW-HW-P01-DEMO-v0.2`, `ODW-HW-P04-DEMO-v0.1`).

### 3.2. Kế hoạch thu thập dữ liệu chính thức (Data Collection Plan — Planned Split Only)
- **Quy mô mục tiêu:** $\sim 40$ người viết (writers).
- **Kế hoạch phân chia Writer-Disjoint (Planned, chưa thực thi):**
  - Tập huấn luyện (Development / Train Set): 28 writers ($\sim 70\%$).
  - Tập hiệu chuẩn (Validation Set): 6 writers ($\sim 15\%$).
  - Tập kiểm thử đánh giá độc lập (Held-out Test Set): 6 writers ($\sim 15\%$).
- **Quy trình phân chia khuyến nghị:**
  Thu thập đủ writers $\rightarrow$ Kiểm định chất lượng (QC) $\rightarrow$ Đóng băng danh sách writer hợp lệ $\rightarrow$ Phân chia tập tất định ở cấp độ writer (Writer-level disjoint split). Tuyệt đối không chia ngẫu nhiên ở cấp độ ký tự/mẫu rời.

---

## 4. Danh mục các công việc CHƯA HOÀN THÀNH (Pending Work Checklist)

> [!IMPORTANT]
> Toàn bộ các mục dưới đây **CHƯA ĐƯỢC PHÉP ĐÁNH DẤU HOÀN THÀNH** cho đến khi có bằng chứng và tài liệu kiểm chứng thực tế trong repository:
- [x] TV2 cross-review Step B
- [x] Final reconciliation docs 02/03/05
- [x] Step B software-design approval
- [x] Software Step C authorization
- [x] PR1 internal metrics/CSV experiment integration
- [x] Automated experiment runner
- [x] Pre-PR3 acceptance contract & ASCII baseline lock
- [x] Tạo gói phiếu cross-review có contract ngữ cảnh AI tại [`reviews/README.md`](reviews/README.md)
- [x] TV4 quản lý checkpoint và version binding tập trung tại [`reviews/README.md`](reviews/README.md); mọi reviewer phải dùng đúng `REVIEW_TARGET_COMMIT` hiện hành trong gói thay vì hash chép lại ở backlog này
- [x] TV1 hoàn tất phiếu [`reviews/tv1_chapter_1_3_review.md`](reviews/tv1_chapter_1_3_review.md), có human verdict và sign-off
- [x] TV2 đã ký PASS và đóng TV2-R01–R06 trong phiếu [`reviews/tv2_chapter_1_3_review.md`](reviews/tv2_chapter_1_3_review.md); metadata `REVIEW_TARGET_COMMIT` của phiếu còn chờ TV2 đồng bộ với checkpoint gói
- [x] TV3 hoàn tất phiếu [`reviews/tv3_chapter_1_3_review.md`](reviews/tv3_chapter_1_3_review.md), có human verdict và sign-off
- [ ] TV4 xử lý toàn bộ finding trong [`reviews/review_disposition.md`](reviews/review_disposition.md) và phát hành bản hợp nhất sau review
- [x] TV1 formal corpus review/freeze (hoàn tất tại [`docs/19_benchmark_corpus_freeze_report.md`](19_benchmark_corpus_freeze_report.md))
- [ ] TV3 clearance calibration
- [x] PR2 baseline adapters (E3 đã PASS; E4 shared transition interface đã ký duyệt tại [`Docs 18`](18_pr3_e4_shared_transition_contract_draft.md))
- [ ] PR3 CompositionState production implementation
- [ ] PR4 delayed-stroke P0
- [ ] Formal CA-VHC experiment
- [x] TV1 scan-validation pipeline (đã hoàn thiện gói `backend/scan_validator/` và CLI runner)
- [x] fiducial detection test (đã kiểm chứng trong `tests/test_scan_validation_pipeline.py`)
- [x] deskew / rectify validation (đã kiểm chứng trong `tests/test_scan_validation_pipeline.py`)
- [x] page scale validation (đã kiểm chứng trong `tests/test_scan_validation_pipeline.py`)
- [x] deterministic auto-crop validation (đã kiểm chứng trong `tests/test_scan_validation_pipeline.py`)
- [ ] P01–P04 bench print
- [ ] P01–P04 600 DPI bench scan
- [ ] Collection Sheet coverage analysis
- [ ] limited pilot with 3–5 writers
- [ ] review pilot data
- [ ] freeze formal Collection Sheet Pack v1.0
- [ ] formal collection ~40 writers
- [ ] writer-disjoint split execution

---

## 5. Tiêu chí Hoàn thành (Definition of Done) cho từng Task
Một task trong backlog chỉ được tích `[x]` khi:
1. Đã có code/tài liệu trong git repo;
2. Có lệnh hoặc kịch bản kiểm chứng đi kèm;
3. Kết quả test/số liệu đã được lưu lại;
4. Không phá vỡ chức năng cũ (no regression);
5. Đã cập nhật tài liệu liên quan nếu có thay đổi hành vi;
6. Không tuyên bố vượt quá bằng chứng thực tế;
7. Đã được reviewer tương ứng nghiệm thu chéo.

---

## 6. Nhật ký tiến độ theo ngày (Progress Log by Date)

**Ngày 23/9**

| Thành viên | Nội dung thực hiện | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV1 | (1) Hoàn tất và ký duyệt Cross-review Chương 1–3 (`docs/reviews/tv1_chapter_1_3_review.md`: CLOSED / PASS).<br>(2) Đóng băng chính thức Benchmark Corpus v1.0 (`CA-VHC-CORPUS-v1.0-FROZEN`) tại [`docs/19_benchmark_corpus_freeze_report.md`](19_benchmark_corpus_freeze_report.md) với 20 DEV và 20 Holdout disjoint hoàn toàn.<br>(3) Hoàn thành lập trình và kiểm chứng tự động toàn diện gói Scan-Validation Pipeline (`backend/scan_validator/`, CLI runner, 11/11 tests pass trong `tests/test_scan_validation_pipeline.py`): phát hiện mốc fiducial 4 góc, nắn phối cảnh chuẩn A4 600 DPI, kiểm chuẩn thước đo 50mm ($\pm 0.2\,\text{mm}$) và ô vuông 20×20mm (Aspect Ratio $1.000 \pm 0.005$), bóc tách ô viết tất định P01–P04, và đánh giá QC tràn viền lề. Toàn bộ test suite repository đạt 126/126 passed. | Không (chờ máy in/quét để bench scan vật lý) | Đã xong |

**Ngày 21/9**

| Thành viên | Nội dung thực hiện | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV2 & TV4 | (1) TV2 hoàn tất technical cross-review Bước B với kết luận PASS; TV4 chính thức đóng Bước B (APPROVED AND CLOSED).<br>(2) TV4 với vai trò Project Lead chính thức cho phép bắt đầu triển khai phần mềm Bước C (READY FOR STEP C: YES; STEP C: AUTHORIZED / NOT YET IMPLEMENTED).<br>(3) Khóa năm quyết định kỹ thuật phần mềm (Clearance 0.20mm default / 0.50mm research target; Metric/API contract phân tầng; Delayed-stroke P0 deterministic Nearest Neighbor; Benchmark corpus là provisional technical fixture; TV1 corpus freeze và TV3 hardware calibration là downstream validation gates).<br>(4) Hoàn tất và chốt PR1 — CA-VHC internal experiment metrics and CSV integration (commit `daca566`): hoàn thiện internal metrics evaluator, CSV logger schema 19 cột bất biến, automated experiment runner, và fixture DEV 160 ca.<br>(5) Hoàn thành Pre-PR3 Acceptance Contract ([`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md)): định nghĩa rõ Entry Gate (chờ PR2 baseline adapters từ TV2) và Exit Gate phần mềm; tách biệt downstream formal-experiment gates (TV1 corpus freeze, TV3 physical calibration, PR5 performance benchmark).<br>(6) Khóa snapshot hình học ASCII 48 ca ([`pr3_ascii_baseline_fingerprints.json`](../tests/fixtures/pr3_ascii_baseline_fingerprints.json)) và 6 unit tests ([`tests/test_pr3_acceptance_baseline.py`](../tests/test_pr3_acceptance_baseline.py)) bảo vệ toàn diện A1, A2, D1, D2, G1 (`Full automated suite: 67 passed tại lần verification này`); FORMAL EXPERIMENT READINESS: NO (Acceptance suite không lựa chọn, iterate, render hoặc ghi nhận bất kỳ case nào từ `BENCHMARK_HOLDOUT_CORPUS_20`). | Không | Đã xong |

**Ngày 20/9**

| Thành viên | Nội dung thực hiện | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV4 | (1) Kiểm chứng và hoàn tất dứt điểm Strict Validation hardening toàn diện: 34/34 regression tests passed, bảo đảm nguyên tắc validation-before-side-effect.<br>(2) Hoàn tất BƯỚC A — Audit kiến trúc Trellis DAG / CA-VHC hiện tại ([`06_audit_trellis_dag_report.md`](06_audit_trellis_dag_report.md)).<br>(3) Hoàn thành bản dự thảo thiết kế BƯỚC B — Diacritic-Aware State Architecture ([`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md)) theo mô hình Hybrid (`GlyphVariant` + `DiacriticCandidate` $\rightarrow$ `CompositionState`), chuẩn hóa quy ước hệ tọa độ local/world, loại bỏ double-count chi phí vị trí, xác lập Single Source of Truth `DiacriticConfig`, khống chế candidate thô $K_{\text{raw}} \le 9$ chỉ cắt tỉa hard-invalid, và xây dựng danh mục 12 unit tests; chuyển sang trạng thái chờ review chéo từ TV2 trước khi sang Bước C (chưa sửa mã nguồn). | Không | Đang làm |
| TV1 & TV4 | Hoàn thành thiết kế vector SVG, xuất bản in PDF A4 và biên soạn tài liệu đặc tả kỹ thuật chi tiết cho cả 4 trang biểu mẫu **OmniDraw Handwriting Collection Sheet Pack v1**: P01 (*Isolated Characters & Diacritics*), P02 (*Context & Ligatures*), P03 (*Sentence Flow & Pangrams*), P04 (*Natural Paragraph*). Đạt trạng thái **PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)**. Toàn bộ tài liệu, vector SVG, PDF và script sinh tự động được lưu trữ tại `collection_sheets/P01..P04`. | Không | Đã xong |

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
