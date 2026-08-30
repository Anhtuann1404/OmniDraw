# OmniDraw — Current Task

**Cập nhật lần cuối:** 30/08/2026

> Mỗi người tự cập nhật dòng của mình. Không cần dài, chỉ cần đủ để người khác (đặc biệt là lead) hiểu ngay tình hình.

---


| Thành viên                 | Đang làm gì                            | Bị nghẽ ở đâu (nếu có)                  | Dự kiến xong |
| -------------------------- |----------------------------------------| --------------------------------------- | ----------- |
| TV1 — AI Core              | Chuẩn bị chuyển code gọi AI từ DALL-E 3 sang Gemini API miễn phí | Chờ tạo chung một Google Gemini API Key | Sắp xong     |
| TV2 — AI Ứng dụng/CV       | Xây dựng thuật toán chuyển đổi ảnh sang SVG tối ưu nét vẽ (Nearest Neighbor + Or-opt) | Không                                   | ✅ Xong     |
| TV3 — Phần cứng            | Đã tích hợp logic mock phần cứng (tính actual_draw_time_sec và các lệnh start/pause/cancel) vào backend/main.py | Không                                 | ✅ Xong     |
| TV4 — Giao diện & Tích hợp | Nối module TV2 (chuyển SVG) vào Gateway, cache svg_metrics tự động cho log CSV, thêm endpoint preview SVG | Không | ✅ Xong      |


**Ngày 30/8**

| Thành viên | Đang làm gì | Bị nghẽn ở đâu | Trạng thái |
|---|---|---|---|
| TV1 & TV4 | Tích hợp thành công code gọi AI (TV1) vào API Gateway (TV4), fix lỗi cấu trúc JSON, chuẩn bị chuyển sang dùng Gemini API. | Không | Đã xong |
| TV2 & TV4 | Đưa code thuật toán tối ưu (TV2) vào Gateway. Tạo luồng: AI Sinh ảnh -> Chuyển SVG (lưu cache metrics) -> Ghi log CSV. | Không | Đã xong |

---
