# OmniDraw — Current Task

**Cập nhật lần cuối:** 13/09/2026

> Mỗi người tự cập nhật dòng của mình. Không cần dài, chỉ cần đủ để người khác (đặc biệt là lead) hiểu ngay tình hình.

---


| Thành viên                 | Đang làm gì                            | Bị nghẽ ở đâu (nếu có)                  | Dự kiến xong |
| -------------------------- |----------------------------------------| --------------------------------------- | ----------- |
| TV1 — AI Core              | Tối ưu prompt template sinh ảnh line-art, duy trì fallback giữa Google Gemini API và OpenAI | Không | ✅ Xong     |
| TV2 — AI Ứng dụng/CV       | Hoàn thiện Single-Stroke Bio-Mimetic Vietnamese Handwriting Engine (chuẩn glyph tiểu học QĐ 31, NFD accents, selective cursive ligature, bio-drift) | Không | ✅ Xong     |
| TV3 — Phần cứng            | Đã tích hợp logic mock phần cứng & camera inspector, chuẩn bị test trên máy vẽ AxiDraw vật lý | Chờ setup máy vẽ thực tế | 🟡 Đang làm |
| TV4 — Giao diện & Tích hợp | Tích hợp chế độ Viết Thư Tay (Handwriting Mode) vào UI CreateScreen/PreviewScreen, hỗ trợ nhập text & upload docx/txt, preview realtime, nối API Gateway `/api/ai/generate` | Không | ✅ Xong      |


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

---

