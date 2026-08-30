# OmniDraw — Progress & Decisions Log

**Mục đích:** Ghi lại các mốc quan trọng và quyết định đã chốt — không log chi tiết từng ngày, chỉ ghi những gì đáng nhớ (quyết định kỹ thuật, thay đổi hướng đi, hoàn thành mốc lớn). File này sẽ tiết kiệm rất nhiều thời gian khi viết báo cáo cuối kỳ.

> Ghi mới nhất lên đầu (thêm dòng phía dưới tiêu đề, không xoá log cũ).

---

## Log


| Ngày     | Loại           | Nội dung                                                                                                                                      |
| -------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| (30/8)   | Hoàn thành mốc | Tích hợp thành công thuật toán tối ưu nét vẽ (TV2) vào Backend. Nối toàn bộ pipeline: AI Sinh ảnh → Tạo SVG → Caching Metrics → Ghi Log CSV. |
| (30/8)   | Hoàn thành mốc | Nối thành công API sinh ảnh (TV1) vào API Gateway (TV4). Sửa triệt để lỗi path ghi CSV, CORS, và đồng bộ mã lỗi JSON trả về đúng API Spec.  |
| (30/8)   | Quyết định     | Chốt sử dụng Google Gemini API (Imagen 3) thay thế OpenAI để tối ưu chi phí (tận dụng free tier), cả nhóm dùng chung 1 key.                   |
| *(24/8)* | Quyết định     | Chốt định hướng đề tài: AI là trọng tâm, phối hợp toàn diện 4 mảng (xem file định hướng gốc)                                                  |
| *(24/8)* | Quyết định     | Chốt chuẩn giao tiếp dữ liệu giữa các mảng: ảnh base64/JSON, SVG cho lệnh vẽ, REST polling cho trạng thái (chi tiết ở `OmniDraw_API_Spec.md`) |
| *(24/8)* | Quyết định     | Chốt phân công 4 mảng: AI Core, AI Ứng dụng/CV, Phần cứng, Giao diện & Tích hợp                                                               |
| (26/8)   | Hoàn thành mốc | Đã xây dựng được khung UI/UX (sử dụng mock data)                                                                                              |


**Loại log gợi ý:** `Quyết định` / `Hoàn thành mốc` / `Thay đổi hướng đi` / `Sự cố & cách xử lý`