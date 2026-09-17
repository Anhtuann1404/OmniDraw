# OmniDraw — Progress & Decisions Log

**Mục đích:** Ghi lại các mốc quan trọng và quyết định đã chốt — không log chi tiết từng ngày, chỉ ghi những gì đáng nhớ (quyết định kỹ thuật, thay đổi hướng đi, hoàn thành mốc lớn). File này sẽ tiết kiệm rất nhiều thời gian khi viết báo cáo cuối kỳ.

> Ghi mới nhất lên đầu (thêm dòng phía dưới tiêu đề, không xoá log cũ).

---

## Log


| Ngày     | Loại           | Nội dung                                                                                                                                      |
| -------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| (17/9)   | Quyết định     | Khóa ba trụ cột nghiên cứu cốt lõi của đề tài: (1) Bố trí dấu tiếng Việt theo quy tắc chính tả, cấu trúc âm tiết và ràng buộc hình học (Vietnamese orthography-aware diacritic composition; không tuyên bố engine hiện đã hiểu ngữ nghĩa hoặc ngữ âm, đây là định hướng nghiên cứu khi dấu chưa tham gia đầy đủ vào DAG); (2) Tối ưu hóa đồ thị nét dựa trên Trellis DAG Viterbi mở rộng (Context-aware stroke graph optimization); (3) Cá nhân hóa nét chữ có thể thực thi trên máy vẽ (Plotter-executable personalization) là hướng mở rộng dài hạn. Xác nhận rõ ràng trong toàn bộ tài liệu dự án: mô hình Writer Profile, phân trang đa trang (multi-page) và telemetry đồng bộ thời gian thực từ phần cứng đều là các định hướng nghiên cứu tương lai, chưa triển khai trong mã nguồn hiện hành. |
| (14/9)   | Quyết định     | Đột phá định hướng đề tài học thuật: Nâng cấp bộ sinh chữ viết tay từ "preset font tĩnh" sang "Context-Aware Vietnamese Handwriting Composition (CA-VHC)" kết hợp "Stroke Graph Optimizer" (Viterbi trên Trellis DAG). Định hướng CA-VHC sẽ phân tích ngữ cảnh (thể loại thư, vị trí từ/dòng, cấu trúc âm tiết và dấu tiếng Việt) để chọn biến thể allographs nét đơn tối ưu (chữ hoa đầu đoạn trang trí drop cap, nét lượn dưới chân từ cuối câu terminal swash, cụm từ nối khối đặc biệt "Thân gửi", "Cảm ơn", tiêu đề vòm cong Bézier và hoa văn centerline), nhằm tăng tính tự nhiên của chữ viết. |
| (14/9)   | Hoàn thành mốc | Tái cấu trúc cơ học toàn diện mã nguồn font pack ra khỏi engine lõi: tạo package `backend/handwriting/font_packs/` (`__init__.py`, `geometry.py`, `legacy.py`, `omni_casual.py`, `letter_variants.py`), giảm hơn 1.000 dòng code khỏi `handwriting_engine.py`, tách biệt rạch ròi giữa tầng dữ liệu hình học và tầng giải thuật render/auditor mà vẫn bảo toàn tính nhất quán fingerprint và hành vi hệ thống. |
| (14/9)   | Hoàn thành mốc | Hoàn thiện bộ font nét đơn Omni Casual v1 với đầy đủ 81 glyphs custom (26 chữ hoa, 26 chữ thường, 10 chữ số, 19 dấu câu thư tay tiếng Việt), audit tự động 72 biến thể nguyên âm tiếng Việt viết thường đạt 0 finding theo bộ kiểm tra polyline hiện tại với min_clearance=0.12 (trong phạm vi bộ kiểm tra hình học hiện được cài đặt). |
| (13/9)   | Hoàn thành mốc | Hoàn thiện Module Viết Thư Tay Nét Đơn (Single-Stroke Vietnamese Handwriting Engine), hỗ trợ bảng chữ cái và hệ dấu thanh tiếng Việt theo chuẩn Unicode NFD trong tập ký tự đã định nghĩa, 4 phong cách nét viết (Học sinh, Thảo nghiêng, Thư pháp, Ký tên) và tích hợp API Gateway `/api/ai/generate`. |
| (13/9)   | Quyết định     | Tự nghiên cứu và phát triển bộ Single-Stroke Vector Centerline Engine sử dụng Cubic Bézier kết hợp Catmull–Rom smoothing, duy trì tính liên tục tiếp tuyến C1 tại các nút nội bộ thay vì dùng font TTF viền đôi (Outline font) để máy vẽ thi công đúng 1 nét đơn centerline chuẩn xác, tránh nét mực kép gây rách giấy hoặc đậm bất thường. |
| (13/9)   | Hoàn thành mốc | Chuẩn hóa hình học toàn diện các glyph tiếng Việt đặc thù (r, s, x, k, h, e, t, i) và hệ thống dấu thanh điệu (hỏi, huyền, sắc, ngã, nặng) chuẩn Bộ GD&ĐT (QĐ 31/2002/QĐ-BGD&ĐT); áp dụng quy tắc tách tầng và điều chỉnh vị trí dấu, kết hợp auditor hình học để phát hiện va chạm và nối nét có chọn lọc (selective ligatures). |
| (13/9)   | Hoàn thành mốc | Nâng cấp giao diện CreateScreen & PreviewScreen hỗ trợ chế độ Viết Thư Tay (Handwriting Mode), cho phép tùy biến font, căn lề trang, giãn dòng, nhập text trực tiếp hoặc tải file văn bản (.docx, .txt). |
| (30/8)   | Hoàn thành mốc | Tích hợp thành công thuật toán tối ưu nét vẽ (TV2) vào Backend. Nối toàn bộ pipeline: AI Sinh ảnh → Tạo SVG → Caching Metrics → Ghi Log CSV. |
| (30/8)   | Hoàn thành mốc | Nối thành công API sinh ảnh (TV1) vào API Gateway (TV4). Sửa triệt để lỗi path ghi CSV, CORS, và đồng bộ mã lỗi JSON trả về đúng API Spec.  |
| (30/8)   | Quyết định     | Chốt sử dụng Google Gemini API (developer tier) thay thế OpenAI để tối ưu chi phí, cả nhóm dùng chung 1 key kiểm thử. |
| *(24/8)* | Quyết định     | Chốt định hướng đề tài: AI là trọng tâm, phối hợp toàn diện 4 mảng (xem file định hướng gốc)                                                  |
| *(24/8)* | Quyết định     | Chốt chuẩn giao tiếp dữ liệu giữa các mảng: ảnh base64/JSON, SVG cho lệnh vẽ, REST polling cho trạng thái (chi tiết ở `OmniDraw_API_Spec-4.md`) |
| *(24/8)* | Quyết định     | Chốt phân công 4 mảng: AI Core, AI Ứng dụng/CV, Phần cứng, Giao diện & Tích hợp                                                               |
| (26/8)   | Hoàn thành mốc | Đã xây dựng được khung UI/UX (sử dụng mock data)                                                                                              |


**Loại log gợi ý:** `Quyết định` / `Hoàn thành mốc` / `Thay đổi hướng đi` / `Sự cố & cách xử lý`