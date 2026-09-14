# OmniDraw — Roadmap

**Cập nhật lần cuối:** 13/09/2026
**Deadline cuối cùng (nộp/bảo vệ):** *(điền ngày)*

> Đánh dấu trạng thái mỗi mục nhỏ: `⬜ Chưa bắt đầu` / `🟡 Đang làm` / `✅ Xong`
> Mỗi giai đoạn lớn chỉ được coi là xong khi TẤT CẢ mục nhỏ bên trong đã ✅.

---

## Giai đoạn 1 — Khảo sát & Nền tảng

**Hạn giai đoạn:** *(điền)*

### 1.1 Khảo sát & chốt hướng AI

**Trạng thái:** ✅ | **Phụ trách:** TV1, TV2 | **Hạn:** *(điền)*

- [x] So sánh 2-3 phương án model/API sinh ảnh (chi phí, tốc độ, chất lượng)
- [x] So sánh phương án CV cho căn giấy/nhận diện
- [x] Chốt lựa chọn cuối, ghi vào `01_tech-stack.md` (Chốt dùng Gemini API free)



### 1.2 Kiến trúc & chuẩn dữ liệu

**Trạng thái:** ✅ | **Phụ trách:** TV4 (lead) | **Hạn:** *(điền)*

- [x] Chốt sơ đồ luồng dữ liệu tổng thể
- [x] Viết `OmniDraw_API_Spec.md` (schema JSON/SVG, mã lỗi chuẩn)
- [x] Gửi tài liệu cho cả nhóm, xác nhận mọi người đã đọc & hiểu



### 1.3 Phần cứng cơ bản

**Trạng thái:** ⬜ | **Phụ trách:** TV3 | **Hạn:** *(điền)*

- [ ] Lắp ráp máy AxiDraw, test vẽ tay bằng file SVG mẫu có sẵn
- [ ] Gắn thử camera, kiểm tra góc nhìn/độ phân giải đủ dùng
- [ ] Xác nhận kết nối máy tính ↔ máy vẽ ổn định (USB/Serial)



### 1.4 Khung UI/UX (mock data)

**Trạng thái:** ✅ | **Phụ trách:** TV4 | **Hạn:** *(điền)*

- [x] Thiết kế luồng màn hình chính (upload/nhập mô tả → preview → gửi vẽ → theo dõi tiến độ)
- [x] Dựng giao diện chạy được với dữ liệu giả
- [x] Dựng khung tích hợp rỗng (chỗ trống để sau này cắm API thật vào)

---



## Giai đoạn 2 — Phát triển song song

**Hạn giai đoạn:** *(điền)*

### 2.1 AI Core — Sinh ảnh cơ bản

**Trạng thái:** ✅ | **Phụ trách:** TV1 | **Hạn:** *(điền)*

- [x] Gọi được model/API sinh ảnh từ text, nhận kết quả đúng chuẩn ở mục 3 trong API Spec
- [x] Test với 5-10 prompt mẫu, đánh giá chất lượng đầu ra



### 2.2 AI Core — Style transfer

**Trạng thái:** ⬜ | **Phụ trách:** TV1 | **Hạn:** *(điền)*

- [ ] Chuyển ảnh chụp thường sang phong cách phác thảo/line-art
- [ ] (Tuỳ chọn) Thử fine-tune (LoRA) nếu còn thời gian



### 2.3 AI Ứng dụng — Computer Vision

**Trạng thái:** ⬜ | **Phụ trách:** TV2 | **Hạn:** *(điền)*

- [ ] Nhận diện & căn chỉnh giấy tự động qua camera
- [ ] Nhận diện khuôn mặt/chân dung (nếu triển khai tính năng này)



### 2.4 AI Ứng dụng — Tối ưu đường vẽ & Tạo chữ viết tay thích ứng ngữ cảnh (CA-VHC)

**Trạng thái:** 🟡 Đang hoàn thiện nâng cao | **Phụ trách:** TV2 | **Hạn:** *(điền)*

- [x] Thuật toán chuyển ảnh → vector line-art
- [x] Thuật toán tối ưu thứ tự nét vẽ (giảm thời gian/quãng đường nhấc bút qua cKDTree + Or-opt + Kinematic Cost)
- [x] Xuất ra đúng chuẩn SVG ở mục 4 trong API Spec
- [x] Module viết thư tay nét đơn (Single-stroke Centerline Engine) mô phỏng bàn tay người, chuẩn tiếng Việt (Unicode NFD, 4 font phong cách: Học sinh, Thảo nghiêng, Thư pháp, Ký tên)
- [x] Tái cấu trúc cơ học, tách riêng gói `backend/handwriting/font_packs/` (`__init__.py`, `geometry.py`, `legacy.py`, `omni_casual.py`, `letter_variants.py`)
- [x] Hoàn thiện 81 ký tự nét đơn Omni Casual v1 (26 hoa, 26 thường, 10 số, 19 dấu câu)
- [ ] Xây dựng giải thuật **Stroke Graph Optimizer** (Quy hoạch động Viterbi trên Trellis DAG mở rộng với chi phí ngữ cảnh)
- [ ] Bổ sung kho biến thể Allographs nét đơn: Chữ hoa đầu đoạn trang trí (Illuminated Drop Cap), nét kéo dài dưới từ cuối câu (Terminal Swash), cụm từ nối liền khối (Logograms: "Thân gửi", "Cảm ơn", "Kính gửi")
- [ ] Tích hợp thuật toán né tránh va chạm dấu phụ đa tầng tiếng Việt (diacritic obstacle-avoidance)
- [ ] Hỗ trợ các thành phần trang trí nét đơn: Tiêu đề vòm cong Bézier, đường phân đoạn centerline (trái tim, dây leo)




### 2.5 Phần cứng — Firmware & chuyển động

**Trạng thái:** ⬜ | **Phụ trách:** TV3 | **Hạn:** *(điền)*

- [ ] Firmware đọc file SVG chuẩn và điều khiển máy vẽ đúng
- [ ] Xử lý các lệnh dừng/tạm dừng/tiếp tục



### 2.6 Phần cứng — Cảm biến & trạng thái

**Trạng thái:** ⬜ | **Phụ trách:** TV3 | **Hạn:** *(điền)*

- [ ] Gửi trạng thái/tiến độ về đúng chuẩn JSON ở mục 5 trong API Spec
- [ ] Phát hiện lỗi cơ bản (kẹt giấy, hết mực) và trả đúng mã lỗi chuẩn



### 2.7 Giao diện — Hoàn chỉnh với API thật (song song)

**Trạng thái:** ✅ | **Phụ trách:** TV4 | **Hạn:** *(điền)*

- [x] Hoàn thiện toàn bộ giao diện (CreateScreen, PreviewScreen, MonitorScreen, HistoryScreen, SettingsScreen)
- [x] Viết sẵn các hàm gọi API theo đúng chuẩn, tích hợp cả chế độ sinh tranh line-art và viết thư tay (Handwriting Mode)



### 2.8 Checklist module (mỗi người tự làm cho phần mình)

**Trạng thái:** 🟡 | **Phụ trách:** Cả 4 người

- [x] Đã tự test module với ít nhất 1 input giả đúng chuẩn
- [x] Đã test với 1 input lỗi, xác nhận trả đúng mã lỗi chuẩn
- [x] Đã log đầy đủ `request_id` theo quy định

---



## Giai đoạn 3 — Tích hợp

**Hạn giai đoạn:** *(điền)*

### 3.1 Tích hợp AI vào giao diện

**Trạng thái:** ✅ | **Phụ trách:** TV1 + TV4 | **Hạn:** *(điền)*

- [x] Thay mock data bằng gọi AI thật (sinh ảnh + style transfer)
- [x] Xử lý lỗi/timeout hiển thị đúng trên giao diện



### 3.2 Tích hợp CV & tối ưu vẽ

**Trạng thái:** ✅ | **Phụ trách:** TV2 + TV4 | **Hạn:** *(điền)*

- [x] Nối module CV/tối ưu vào luồng thật sau bước AI sinh ảnh
- [x] Kiểm tra SVG xuất ra đúng khổ giấy, đúng chuẩn
- [x] Nối module sinh chữ viết tay tiếng Việt nét đơn vào API Gateway `/api/ai/generate` và tích hợp hiển thị preview SVG thời gian thực



### 3.3 Tích hợp máy vẽ

**Trạng thái:** ⬜ | **Phụ trách:** TV3 + TV4 | **Hạn:** *(điền)*

- [ ] Giao diện gửi lệnh vẽ thật xuống máy, nhận trạng thái thật về
- [ ] Test các trường hợp lỗi thật (rút dây, hết mực...) xem hệ thống phản ứng đúng không



### 3.4 Test end-to-end toàn hệ thống

**Trạng thái:** ⬜ | **Phụ trách:** Cả nhóm | **Hạn:** *(điền)*

- [ ] Chạy thử toàn bộ luồng từ nhập input đến ra tranh vẽ thật, tối thiểu 5 lần với input khác nhau
- [ ] Ghi lại lỗi phát sinh vào `04_progress-log.md`, phân công người sửa

---



## Giai đoạn 4 — Hoàn thiện & Báo cáo

**Hạn giai đoạn:** *(điền)*

### 4.1 Tối ưu chất lượng & Benchmark Thực nghiệm Định lượng

**Trạng thái:** ⬜ | **Phụ trách:** Cả nhóm | **Hạn:** *(điền)*

- [ ] Chạy bộ thực nghiệm định lượng (Quantitative Benchmarks) so sánh 3 phương pháp (Naive vs Greedy NN vs OmniDraw cKDTree+Or-opt+Kinematic Cost): đo chiều dài nhấc bút ($mm$), số lần nhấc bút, thời gian tính toán ($ms$), và độ mượt góc đổi hướng.
- [ ] Tổ chức khảo sát mù kiểm định Turing (Double-blind Handwriting Turing Test) với 30-50 tình nguyện viên để đánh giá mức độ chân thực so với chữ người viết thật.
- [ ] Đo lường độ chính xác nắn thẳng giấy tự động của module thị giác máy tính ($MAE$ góc nghiêng $\Delta\theta$).
- [ ] Cải thiện chất lượng đầu ra AI dựa trên kết quả test thật trên máy vẽ AxiDraw vật lý.



### 4.2 Demo & video

**Trạng thái:** ⬜ | **Phụ trách:** TV4 (điều phối) | **Hạn:** *(điền)*

- [ ] Quay video minh hoạ toàn bộ quy trình từ nhập prompt/văn bản đến lúc máy vẽ hoàn tất bức thư nghệ thuật.
- [ ] Chuẩn bị kịch bản demo trực tiếp (chữ hoa đầu đoạn, nét lượn chân chữ cuối câu, hoa văn centerline).



### 4.3 Báo cáo khoa học (Chuẩn mực Báo cáo NCKH / Bài báo)

**Trạng thái:** ⬜ | **Phụ trách:** Mỗi người viết phần mình, TV4 tổng hợp | **Hạn:** *(điền)*

- [ ] Xây dựng Báo cáo NCKH chuẩn cấu trúc 5 chương (Chương 1: Mở đầu; Chương 2: Tổng quan & Cơ sở lý thuyết; Chương 3: Phương pháp & Thiết kế Thuật toán CA-VHC; Chương 4: Thực nghiệm & Đánh giá kết quả; Chương 5: Kết luận & Hướng phát triển).
- [ ] Bổ sung mô hình hóa toán học hình thức: Phương trình Bellman của Viterbi DP, biểu thức hàm phạt quán tính Kinematic Cost, phân tích độ phức tạp thuật toán Big-O.
- [ ] Thiết kế đồ thị Ablation Study (nghiên cứu độ nhạy tham số $\lambda_{\text{turn}}$ và bộ trọng số DAG).
- [ ] TV4 tổng hợp, biên tập thống nhất văn phong học thuật, kiểm tra đạo văn và trích dẫn chuẩn IEEE/APA.



### 4.4 Slide & bảo vệ

**Trạng thái:** ⬜ | **Phụ trách:** Cả nhóm | **Hạn:** *(điền)*

- [ ] Chuẩn bị slide trình bày
- [ ] Phân công ai thuyết trình phần nào, tập dượt trả lời câu hỏi phản biện