# OmniDraw — Roadmap

**Cập nhật lần cuối:** *(điền ngày mỗi khi sửa)*
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

**Trạng thái:** ⬜ | **Phụ trách:** TV4 | **Hạn:** *(điền)*

- [x] Thiết kế luồng màn hình chính (upload/nhập mô tả → preview → gửi vẽ → theo dõi tiến độ)
- [x] Dựng giao diện chạy được với dữ liệu giả
- [ ] Dựng khung tích hợp rỗng (chỗ trống để sau này cắm API thật vào)

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



### 2.4 AI Ứng dụng — Tối ưu đường vẽ

**Trạng thái:** ⬜ | **Phụ trách:** TV2 | **Hạn:** *(điền)*

- [ ] Thuật toán chuyển ảnh → vector line-art
- [ ] Thuật toán tối ưu thứ tự nét vẽ (giảm thời gian/quãng đường nhấc bút)
- [ ] Xuất ra đúng chuẩn SVG ở mục 4 trong API Spec



### 2.5 Phần cứng — Firmware & chuyển động

**Trạng thái:** ⬜ | **Phụ trách:** TV3 | **Hạn:** *(điền)*

- [ ] Firmware đọc file SVG chuẩn và điều khiển máy vẽ đúng
- [ ] Xử lý các lệnh dừng/tạm dừng/tiếp tục



### 2.6 Phần cứng — Cảm biến & trạng thái

**Trạng thái:** ⬜ | **Phụ trách:** TV3 | **Hạn:** *(điền)*

- [ ] Gửi trạng thái/tiến độ về đúng chuẩn JSON ở mục 5 trong API Spec
- [ ] Phát hiện lỗi cơ bản (kẹt giấy, hết mực) và trả đúng mã lỗi chuẩn



### 2.7 Giao diện — Hoàn chỉnh với API thật (song song)

**Trạng thái:** ⬜ | **Phụ trách:** TV4 | **Hạn:** *(điền)*

- [ ] Hoàn thiện toàn bộ giao diện, vẫn dùng mock data
- [ ] Viết sẵn các hàm gọi API theo đúng chuẩn, chỉ chờ module thật để nối vào



### 2.8 Checklist module (mỗi người tự làm cho phần mình)

**Trạng thái:** ⬜ | **Phụ trách:** Cả 4 người

- [ ] Đã tự test module với ít nhất 1 input giả đúng chuẩn
- [ ] Đã test với 1 input lỗi, xác nhận trả đúng mã lỗi chuẩn
- [ ] Đã log đầy đủ `request_id` theo quy định

---



## Giai đoạn 3 — Tích hợp

**Hạn giai đoạn:** *(điền)*

### 3.1 Tích hợp AI vào giao diện

**Trạng thái:** ✅ | **Phụ trách:** TV1 + TV4 | **Hạn:** *(điền)*

- [x] Thay mock data bằng gọi AI thật (sinh ảnh + style transfer)
- [x] Xử lý lỗi/timeout hiển thị đúng trên giao diện



### 3.2 Tích hợp CV & tối ưu vẽ

**Trạng thái:** ⬜ | **Phụ trách:** TV2 + TV4 | **Hạn:** *(điền)*

- [ ] Nối module CV/tối ưu vào luồng thật sau bước AI sinh ảnh
- [ ] Kiểm tra SVG xuất ra đúng khổ giấy, đúng chuẩn



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

### 4.1 Tối ưu chất lượng

**Trạng thái:** ⬜ | **Phụ trách:** Cả nhóm | **Hạn:** *(điền)*

- [ ] Cải thiện chất lượng đầu ra AI dựa trên kết quả test thật
- [ ] Tối ưu tốc độ vẽ/thời gian xử lý nếu còn chậm



### 4.2 Demo & video

**Trạng thái:** ⬜ | **Phụ trách:** TV4 (điều phối) | **Hạn:** *(điền)*

- [ ] Quay video minh hoạ toàn bộ quy trình
- [ ] Chuẩn bị kịch bản demo trực tiếp (phòng khi cần demo live)



### 4.3 Báo cáo khoa học

**Trạng thái:** ⬜ | **Phụ trách:** Mỗi người viết phần mình, TV4 tổng hợp | **Hạn:** *(điền)*

- [ ] Mỗi thành viên viết phần báo cáo cho mảng mình phụ trách
- [ ] TV4 tổng hợp, biên tập thống nhất văn phong



### 4.4 Slide & bảo vệ

**Trạng thái:** ⬜ | **Phụ trách:** Cả nhóm | **Hạn:** *(điền)*

- [ ] Chuẩn bị slide trình bày
- [ ] Phân công ai thuyết trình phần nào, tập dượt trả lời câu hỏi phản biện