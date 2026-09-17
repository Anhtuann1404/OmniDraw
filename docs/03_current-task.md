# OmniDraw — Current Task & Sprint Backlog

**Cập nhật lần cuối:** 17/09/2026
**Chu kỳ hiện tại:** Sprint 1–2 (2 tuần tới: Khóa nền nghiên cứu CA-VHC & Thiết lập framework thực nghiệm)
**Nguyên tắc:** Mỗi người làm chủ một đường chạy độc lập, tuân thủ Definition of Done và review chéo định kỳ.

---

## 1. Trạng thái hiện tại theo 4 đường chạy (Current Sprint Status)

| Thành viên / Đường chạy | Nhiệm vụ trọng tâm Sprint 1–2 | Điểm nghẽn (Blocker) | Trạng thái |
| :--- | :--- | :--- | :--- |
| **TV2 — Trưởng lõi CA-VHC** | Khóa Research Questions (RQ) & giả thuyết; chuẩn hóa ký hiệu toán học hàm mục tiêu $J$; chốt 3 baseline; thiết kế cơ chế đưa dấu tiếng Việt và vùng cấm va chạm vào Trellis DAG | Không | 🟡 Đang làm |
| **TV1 — Dữ liệu & Writer Profile** | Định nghĩa JSON schema `WriterProfile` (versioned); soạn thảo protocol thu thập & ẩn danh hóa dữ liệu; code prototype trích xuất 4 đặc trưng hình học cơ bản trên fixture giả lập | Không | 🟡 Đang làm |
| **TV3 — Phần cứng & Hiệu chuẩn** | Chuẩn hóa interface chung giữa simulator và máy vẽ thật; chuẩn bị SVG smoke test fixture; lập checklist hiệu chuẩn phần cứng; xác định metrics phần cứng bắt buộc | *Blocked by hardware:* chờ setup cáp & máy vẽ thực tế (tập trung hoàn thiện simulator & test protocol) | 🟡 Đang làm |
| **TV4 — Nền tảng & Tích hợp** | Khắc phục khoảng lệch strict validation của `style` (loại bỏ fallback ngầm); chuẩn hóa schema logging CSV; thiết kế kế hoạch dataset runner cho nhiều `method_tag`/`seed`; dựng khung báo cáo Chương 3 & 4 | Không | 🟡 Đang làm |

---

## 2. Backlog chi tiết Sprint 1–2 (Kế hoạch hành động 2 tuần tới)

### TV2 — Trưởng lõi thuật toán CA-VHC
- [ ] Soạn thảo tài liệu đặc tả học thuật: Xác định rõ 3 câu hỏi nghiên cứu (RQ1: Chất lượng nét nối & tối ưu pen-up; RQ2: Khả năng né tránh va chạm dấu tiếng Việt; RQ3: Tính khả thi và hiệu năng trên máy vẽ vật lý) và giả thuyết tương ứng.
- [ ] Chuẩn hóa ký hiệu toán học hình thức cho bài toán: Phương trình Bellman Viterbi DP, biểu thức chi phí chuyển trạng thái $J = w_1 D_{\text{penup}} + w_2 N_{\text{lift}} + w_3 C_{\text{curvature}} + w_4 C_{\text{collision}} + w_5 C_{\text{legibility}}$.
- [ ] Chốt định nghĩa và cấu hình của **3 phương pháp baseline đối chứng**:
  1. *Baseline 1:* Static Glyphs (renderer ký tự tĩnh, không allographs).
  2. *Baseline 2:* Greedy Heuristic (chọn biến thể và nối nét theo bước gần nhất tham lam).
  3. *Baseline 3:* Current Trellis DAG (giải thuật DP hiện tại chưa có ràng buộc dấu).
- [ ] Thiết kế giải pháp đưa dấu tiếng Việt theo quy tắc chính tả, cấu trúc âm tiết và vùng cấm va chạm vào trạng thái/chi phí của Trellis DAG.
- [ ] Xây dựng tiêu chuẩn định lượng pass/fail cho kiểm tra va chạm dấu tiếng Việt (`diacritic collision clearance threshold`).
- [ ] *Lưu ý phạm vi:* Chưa cần thiết kế thêm Font Pack mới trong sprint này; tập trung tối ưu trên 2 pack hiện có (`omnidraw_legacy` và `omni_casual`).

### TV1 — AI cá nhân hóa và dữ liệu Writer Profile
- [ ] Xây dựng bản nháp đầu tiên của JSON schema `WriterProfile` (có trường `version`, `metadata`, `feature_vector`).
- [ ] Soạn thảo quy chuẩn thu thập mẫu chữ viết tay và protocol đạo đức: cam kết có sự đồng thuận của người viết, quy trình ẩn danh hóa, quy tắc loại bỏ chữ ký và thông tin định danh cá nhân nhạy cảm.
- [ ] Lập trình module prototype trích xuất tối thiểu 4 đặc trưng hình học định lượng cơ bản:
  1. Độ nghiêng trung bình (`slant_deg`);
  2. Tỷ lệ kích thước chữ (`aspect_ratio`);
  3. Khoảng cách chữ và từ (`letter_spacing`, `word_spacing`);
  4. Độ dao động baseline (`baseline_jitter_sigma`).
- [ ] Tạo fixture dữ liệu mẫu giả lập (synthetic data fixtures) để kiểm thử bộ trích xuất độc lập, không phụ thuộc vào tiến độ thu thập dữ liệu người dùng thật.
- [ ] *Lưu ý phạm vi:* Không huấn luyện mô hình học sâu (deep learning) phức tạp trong sprint này; ưu tiên hoàn thiện quy trình rule-based rõ ràng và có thể kiểm chứng.

### TV3 — Phần cứng, hiệu chuẩn và thị giác máy tính
- [ ] Chuẩn hóa và đồng nhất interface phần mềm chung (`HardwareAdapterInterface`) dùng chung cho cả phần cứng AxiDraw thật và bộ giả lập `mock_grbl`.
- [ ] Chuẩn bị một file SVG fixture chuẩn (chứa đầy đủ nét thẳng, nét cong Bézier, chữ viết tay và nhấc bút) để phục vụ smoke test tự động.
- [ ] Soạn thảo Checklist hiệu chuẩn phần cứng máy vẽ: căn góc 0 tọa độ giấy, vận tốc vẽ, gia tốc ngòi bút, độ nảy và độ trễ cơ học nâng/hạ bút.
- [ ] Xác định danh mục các metrics phần cứng bắt buộc cần đo: thời gian vẽ thực tế (`actual_draw_time_sec`), quãng đường di chuyển đầu bút, sai số tọa độ vật lý.
- [ ] *Nếu có máy vẽ và cáp kết nối:* Chạy smoke test trên giấy thật và lưu lại log dữ liệu thực nghiệm đầu tiên.
- [ ] *Nếu chưa có máy:* Ghi nhận rõ blocker phần cứng, tập trung hoàn thiện simulator để TV4 và TV2 có thể gọi giả lập mà không bị lỗi crash.

### TV4 — Nền tảng, tích hợp và framework đánh giá
- [ ] Khắc phục khoảng lệch triển khai của `style`: chỉnh sửa validator để từ chối các style không thuộc `STYLE_CONFIGS`, trả lỗi có cấu trúc thay vì tự ý fallback ngầm về `hand_hocsinh`.
- [ ] Chuẩn hóa cấu trúc file log thực nghiệm CSV ở backend (`backend/main.py:append_experiment_log`), đảm bảo ghi nhận đầy đủ 14 trường dữ liệu phục vụ phân tích.
- [ ] Lập kế hoạch và viết script dataset runner chạy tự động một loạt câu văn tiếng Việt chuẩn qua nhiều phương pháp (`method_tag`) và các `seed` khác nhau.
- [ ] Kiểm tra tính nhất quán giữa Roadmap, Current Task, API Spec v1.4 và mã nguồn thực tế; đảm bảo không có mâu thuẫn trạng thái.
- [ ] Dựng khung cấu trúc chi tiết cho Chương 3 (Phương pháp & Thiết kế Thuật toán) và Chương 4 (Thực nghiệm & Đánh giá) trong Báo cáo NCKH.
- [ ] *Lưu ý phạm vi:* Chưa phát triển thêm các thành phần trang trí giao diện mới trong sprint này; tập trung tối đa cho pipeline thực nghiệm NCKH.

### Quy định phối hợp toàn nhóm trong Sprint
- **Họp đồng bộ kỹ thuật (Weekly Sync):** Họp ngắn 30 phút mỗi tuần một lần để rà soát blocker giữa các mảng.
- **Milestone cuối Sprint:** Chạy một phiên demo chung tích hợp: cùng một văn bản mẫu tiếng Việt, cùng seed cố định, chạy qua API Gateway, ghi log CSV đầy đủ và kiểm tra SVG xuất xưởng.
- **Quy trình Review chéo (Cross-review):**
  - **TV1 review TV2:** Kiểm tra tính tái lập của dữ liệu, seed và khả năng trích xuất metrics của engine.
  - **TV2 review TV1:** Đánh giá tính khả thi khi ánh xạ schema Writer Profile vào tham số hình học của engine.
  - **TV3 review TV2 & TV4:** Đánh giá tính thực tế của các giả định về vận tốc, gia tốc và mô hình thời gian thi công.
  - **TV4 review cả nhóm:** Kiểm tra tính tuân thủ contract API Spec, cấu trúc log CSV và khả năng tích hợp hệ thống.
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

**Ngày 17/9**

| Thành viên | Nội dung thực hiện | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| Cả nhóm | Rà soát và đồng bộ toàn bộ tài liệu kỹ thuật/nghiên cứu theo code thực tế và định hướng CA-VHC; phân định rõ 4 trạng thái (Đã triển khai, Đang phát triển, Định hướng nghiên cứu, Demo); loại bỏ toàn bộ tuyên bố quá mức. | Không | Đã xong |
| Cả nhóm | Tinh chỉnh toàn diện Roadmap và phân công 4 đường chạy độc lập (TV1, TV2, TV3, TV4), thiết lập hệ thống ưu tiên P0–P3, lộ trình theo Decision Gates, DoD và quy tắc merge code. | Không | Đã xong |
| TV2 | Khóa phạm vi và câu hỏi nghiên cứu (RQ) cho CA-VHC; chuẩn bị tích hợp ràng buộc dấu tiếng Việt và né tránh va chạm vào hàm mục tiêu DAG. | Không | Đang làm |
| TV4 | Chuẩn hóa API Spec v1.4 bảo toàn contract hiện hành, bổ sung phụ lục mở rộng non-binding cho Writer Profile, Layout & Phân trang, và Telemetry phần cứng. | Không | Đã xong |
| TV4 | Chuyển tiếp sang hỗ trợ khóa RQ, chuẩn bị khung Báo cáo NCKH 5 chương, thiết lập backlog Sprint 1–2 và theo dõi tính nhất quán code–contract. | Không | Đang làm |

**Ngày 14/9**

| Thành viên | Đang làm gì | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV2 & TV4 | Tái cấu trúc cơ học toàn diện font pack ra khỏi `handwriting_engine.py` thành gói `backend/handwriting/font_packs/` (`__init__.py`, `geometry.py`, `legacy.py`, `omni_casual.py`, `letter_variants.py`). | Không | Đã xong |
| TV2 | Định hình khung thuật toán Context-Aware Vietnamese Handwriting Composition (CA-VHC) & Stroke Graph Optimizer (Viterbi trên Trellis DAG). | Không | Đang làm |
| TV4 | Cập nhật toàn bộ hệ thống tài liệu `docs/` (`01_tech-stack.md`, `02_roadmap.md`, `03_current-task.md`, `04_progress-log.md`) và tài liệu định hướng đề tài. | Không | Đã xong |

**Ngày 13/9**

| Thành viên | Đang làm gì | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV2 & TV4 | Hoàn thiện và tinh chỉnh toàn diện bộ ký tự tiếng Việt nét đơn (chuẩn hóa e, c, k, s, x, i, t, h và hệ thống dấu hỏi, huyền, ngã, nặng, sắc) chuẩn Bộ GD&ĐT; tích hợp trọn vẹn vào luồng sinh SVG và UI. | Không | Đã xong |
| TV4 | Cập nhật UI CreateScreen với giao diện viết thư tay chuyên dụng (chọn font, căn chỉnh lề trang, giãn dòng, tải file văn bản), kết nối trực tiếp với backend `handwriting_engine`. | Không | Đã xong |

**Ngày 30/8**

| Thành viên | Đang làm gì | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV1 & TV4 | Tích hợp thành công code gọi AI (TV1) vào API Gateway (TV4), fix lỗi cấu trúc JSON, chuẩn bị chuyển sang dùng Gemini API. | Không | Đã xong |
| TV2 & TV4 | Đưa code thuật toán tối ưu (TV2) vào Gateway. Tạo luồng: AI Sinh ảnh -> Chuyển SVG (lưu cache metrics) -> Ghi log CSV. | Không | Đã xong |
