# OmniDraw — Current Task

**Cập nhật lần cuối:** 14/09/2026

> Mỗi người tự cập nhật dòng của mình. Không cần dài, chỉ cần đủ để người khác (đặc biệt là lead) hiểu ngay tình hình.

---


| Thành viên                 | Đang làm gì                            | Bị nghẽ ở đâu (nếu có)                  | Dự kiến xong |
| -------------------------- |----------------------------------------| --------------------------------------- | ----------- |
| TV1 — AI Core              | Tự động hóa kiểm thử 15 prompt chuẩn (`TV1_15_prompts.docx`), thống kê latency & tỷ lệ sinh vector sạch | Không | 🟡 Đang làm |
| TV2 — AI Ứng dụng/CV       | Nghiên cứu thuật toán Context-Aware Vietnamese Handwriting Composition (CA-VHC) & Stroke Graph Optimizer; thiết kế bộ biến thể allographs nét đơn | Không | 🟡 Đang làm |
| TV3 — Phần cứng            | Đã tích hợp logic mock phần cứng & camera inspector, chuẩn bị kết nối máy vẽ AxiDraw vật lý qua pyaxidraw | Chờ setup cáp & máy vẽ thực tế | 🟡 Đang làm |
| TV4 — Giao diện & Tích hợp | Hoàn thành refactor gói `backend/handwriting/font_packs/`, cập nhật docs kỹ thuật, xây dựng khung Báo cáo NCKH 5 chương & form Turing Test | Không | 🟡 Đang làm |


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

---

