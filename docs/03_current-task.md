# OmniDraw — Current Task

**Cập nhật lần cuối:** 30/08/2026

> Mỗi người tự cập nhật dòng của mình. Không cần dài, chỉ cần đủ để người khác (đặc biệt là lead) hiểu ngay tình hình.

---


| Thành viên                 | Đang làm gì                            | Bị nghẽ ở đâu (nếu có)                  | Dự kiến xong |
| -------------------------- |----------------------------------------| --------------------------------------- | ----------- |
| TV1 — AI Core              | Chuẩn bị chuyển code gọi AI từ DALL-E 3 sang Gemini API miễn phí | Chờ tạo chung một Google Gemini API Key | Sắp xong     |
| TV2 — AI Ứng dụng/CV       | *(điền)*                               | *(điền)*                                | *(điền)*    |
| TV3 — Phần cứng            | Đã tích hợp logic mock phần cứng (tính actual_draw_time_sec và các lệnh start/pause/cancel) vào backend/main.py | Không                                 | ✅ Xong     |
| TV4 — Giao diện & Tích hợp | Đã nối module TV1 vào API Gateway, fix CORS, fix path ghi log CSV, chuẩn hoá mã lỗi API sinh ảnh theo đúng spec | Không | ✅ Xong      |


**Ngày 30/8**

| Thành viên | Đang làm gì | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV1 & TV4 | Tích hợp thành công code gọi AI (TV1) vào API Gateway (TV4), fix lỗi cấu trúc JSON trả về, chuẩn bị chuyển sang dùng Gemini API (Imagen 3). | Không | Đã xong |

---
