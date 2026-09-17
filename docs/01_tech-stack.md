# OmniDraw — Tech Stack

**Cập nhật lần cuối:** 17/09/2026
**Quy tắc:** Khi đổi công nghệ ở bất kỳ mảng nào, phải sửa file này TRƯỚC hoặc NGAY khi đổi — không để người khác code theo stack cũ đã lỗi thời.

---

## 1. AI Core — Sinh ảnh & Chuyển phong cách (Thành viên 1)

| Hạng mục             | Lựa chọn                                           | Lý do    |
| -------------------- | -------------------------------------------------- | -------- |
| Ngôn ngữ             | Python                                             | Đồng bộ backend FastAPI của hệ thống |
| Model/API sinh ảnh   | Google Gemini API / OpenAI DALL-E                  | Hỗ trợ sinh ảnh từ prompt text qua API chuẩn, tận dụng developer tier để kiểm thử và tích hợp |
| Model style transfer | *(chưa triển khai)*                                | Dự kiến nghiên cứu hoặc fine-tune mô hình phác thảo/line-art khi có dữ liệu |
| Thư viện chính       | `google-genai` / `openai`, `requests`              | Giao tiếp API chuẩn, phổ biến |

---

## 2. AI Ứng dụng — Thị giác máy tính & Tối ưu vẽ (Thành viên 2)

| Hạng mục                   | Lựa chọn                                              | Lý do    |
| -------------------------- | ------------------------------------------------------ | -------- |
| Ngôn ngữ                   | Python                                                 | Đồng bộ với backend FastAPI và các mảng khác, dễ tích hợp qua function call hoặc CLI trực tiếp |
| Thư viện CV                | OpenCV (`opencv-python-headless`)                      | Có sẵn Canny edge detection + `findContours` để trích đường nét từ ảnh, phổ biến, tài liệu nhiều, tốc độ tốt |
| Thuật toán tối ưu đường vẽ tranh | Nearest Neighbor + Or-opt (candidate list qua KD-tree) + Kinematic Turn Penalty | Khởi tạo nhanh bằng NN trên `cKDTree` kết hợp hàm phạt quán tính động học $\text{dist} + \lambda(1 - \cos\theta)$ chống giật ngòi bút; Or-opt chỉ xét ứng viên không gian thực tế, scale tốt với hàng nghìn nét so với 2-opt truyền thống. |
| Thư viện vector hoá ảnh    | `cv2.findContours` (có sẵn trong OpenCV) + `scipy` (KD-tree) | Không cần thêm dependency ngoài; đủ đáp ứng nhu cầu trích contour làm stroke và tìm hàng xóm không gian nhanh |
| Quản lý Font Pack nét đơn  | Module hóa hướng gói (`backend/handwriting/font_packs/`: `__init__.py`, `geometry.py`, `legacy.py`, `omni_casual.py`, `letter_variants.py`) | Tách biệt tầng dữ liệu hình học (Geometry/Metrics) khỏi tầng giải thuật (Engine/Auditor). Cho phép bổ sung Font Pack hoặc allograph mới mà không phải đưa dữ liệu hình học trở lại engine; mỗi pack mới vẫn phải có glyph geometry, metrics và bộ kiểm tra tương ứng. Không hỗ trợ tải trực tiếp file TTF/OTF do định dạng outline viền đôi không tương thích máy vẽ nét đơn. |

### Chi tiết giải thuật: Context-Aware Vietnamese Handwriting Composition (CA-VHC)

> **Định nghĩa:** Context-Aware Vietnamese Handwriting Composition (CA-VHC) hướng tới tối ưu đồng thời biến thể glyph theo ngữ cảnh, cách bố trí/thứ tự viết dấu tiếng Việt và quỹ đạo bút để sinh SVG centerline dễ đọc, ít va chạm và có thể thi công trên máy vẽ.

#### A. Đã triển khai (Implemented)
- **Font Pack nét đơn độc lập:** Cấu trúc dữ liệu hình học tách rời (`omnidraw_legacy`, `omni_casual`) định nghĩa tọa độ centerline chuẩn hóa.
- **Unicode NFD & Modular Accents:** Phân rã ký tự tiếng Việt thành ký tự gốc và dấu thanh riêng biệt, tự động ghép dấu theo tọa độ mỏ neo (anchors) và tính toán khoảng dịch tâm (offset).
- **Contextual allographs hiện có:** Biến thể chữ hoa mở đầu văn bản trang trọng (`formal_initial` cho K, T, C trên font pack legacy) và biến thể hình học kết thúc từ (`word_final` cho n, m trong Omni Casual).
- **Stroke Graph Optimizer:** Giải thuật quy hoạch động Viterbi DP trên Trellis DAG theo từng từ (`optimize_word_dag()`).
- **Hàm chi phí chuyển trạng thái:** Hàm mục tiêu $J = w_1 D_{\text{penup}} + w_2 N_{\text{lift}} + w_3 C_{\text{curvature}} + w_4 C_{\text{collision}} + w_5 C_{\text{legibility}}$ lựa chọn biến thể glyph và quyết định nối nét/nhấc bút dựa trên khoảng cách pen-up, số lần nhấc bút, góc bẻ tiếp tuyến, nguy cơ va chạm hình học sơ bộ qua `bridge_collision_cost`, và độ dễ đọc.
- **Đầu ra SVG Centerline:** Xuất đường nét đơn mượt mà qua Catmull–Rom sang Cubic Bézier kết hợp auto-deskew, duy trì đầu ra centerline theo cấu trúc Font Pack để máy vẽ thi công đúng một nét vẽ liên tục.
- **Seed tái lập:** Seed số nguyên 32-bit không dấu giúp tái lập nhất quán kết quả render giữa các lần chạy.
- **Auditor hình học:** Bộ kiểm tra polyline (`audit_font_pack_geometry()`, `_stroke_min_distance()`) phát hiện đoạn suy biến, nét đè lặp, và phát hiện các va chạm thuộc phạm vi bộ kiểm tra hiện tại; chưa phải bảo đảm hình học cho mọi văn bản và cấu hình.

#### B. Đang phát triển (In Progress)
- Đưa dấu tiếng Việt và vùng cấm va chạm trực tiếp vào bài toán tối ưu DAG.
- Mở rộng hàm chi phí theo loại thư (`letter_type`) và vị trí từ/câu/dòng cụ thể.
- Đánh giá định lượng chất lượng lựa chọn allograph và tính tự nhiên của nét nối.
- Hoàn thiện bộ QA trực quan cho toàn bộ chữ và dấu tiếng Việt (mở rộng từ `qa_specimens.py`).

#### C. Định hướng nghiên cứu (Research Directions)
- **Tối ưu hóa đa cấp:** Tối ưu hóa quỹ đạo nét ở cấp độ từ và dòng văn bản thay vì chỉ xử lý cục bộ từng vị trí; dấu hiện chưa được tối ưu đầy đủ như một trạng thái/ràng buộc chung trong DAG (hiện mới đặt bằng anchor/offset và hậu kiểm).
- **Mô hình hóa dấu tiếng Việt & thứ tự nét trễ (Định hướng nghiên cứu):** Bố trí dấu theo base vowel, quy tắc chính tả và cấu trúc âm tiết tiếng Việt (Vietnamese orthography-aware diacritic composition; engine không tự nhận hiểu ngữ nghĩa hay ngữ âm); mô hình hóa vùng cấm va chạm quanh glyph/dấu; xử lý tổ hợp nhiều dấu; quyết định viết dấu ngay, sau từ hoặc theo nhóm nét trễ để cân bằng giữa quãng đường di chuyển quay lại, số lần nhấc bút và độ dễ đọc khi đưa dấu tham gia đầy đủ vào tối ưu DAG.
- **Mở rộng các cấp ngữ cảnh allographs:** Hướng tới đầy đủ các cấp ngữ cảnh: đầu đoạn, đầu câu, đầu từ, giữa từ, cuối từ, cuối câu, cuối dòng và theo loại thư.
- **Thực nghiệm & So sánh:** Xây dựng bộ thực nghiệm so sánh với các phương pháp cơ sở (baseline) và ablation study bóc tách từng thành phần trong hàm chi phí DAG.
- **Đánh giá đa tiêu chí:** Đánh giá đồng thời cả chất lượng hình học, độ dễ đọc và chi phí chuyển động của máy vẽ.

#### D. Phân biệt 4 khái niệm trong hệ thống chữ viết
1. **Font Pack:** Tập dữ liệu hình học nét đơn chuẩn hóa (`geometry`, `metrics`, `anchors`, `contextual variants`).
2. **Render Profile:** Tham số biến đổi hình học khi kết xuất (độ nghiêng `slant`, tỷ lệ co giãn `scale`, khoảng cách dòng `line_spacing`).
3. **Letter Type:** Ngữ cảnh văn bản quy định quy tắc lựa chọn biến thể glyph và bố cục (hiện tại: `general`, `formal`; tương lai: thân mật, tình cảm, thiệp mời, học sinh...).
4. **Writer Profile:** Hồ sơ đặc trưng thói quen người viết (thuộc nhánh nghiên cứu AI cá nhân hóa nét chữ).

#### E. Phân biệt lõi nghiên cứu và tính năng trình diễn
- **Lõi nghiên cứu (Core Contributions):**
  - Contextual glyph selection.
  - Vietnamese diacritic constraints & delayed stroke ordering.
  - Stroke/pen trajectory optimization (Trellis DAG / Viterbi).
  - Khả năng thực thi trên máy vẽ (plotter execution).
- **Tính năng trình diễn / mở rộng (Demos & Embellishments):**
  - Nét kéo dài lượn sóng dưới từ cuối câu (Terminal swash).
  - Chữ hoa đầu đoạn trang trí (Drop cap).
  - Cụm từ nối liền khối (Logograms: "Kính gửi", "Thân gửi", "Cảm ơn").
  - Tiêu đề uốn lượn vòm cong Bézier.
  - Hoa văn phân đoạn centerline (trái tim, dây leo).

#### F. Nghiên cứu mở rộng: AI cá nhân hóa thói quen chữ viết (Writer Profile)
- **Mô hình luồng nghiên cứu tương lai (chưa triển khai trong code hiện tại):**
  ```text
  Mẫu chữ người dùng
  → Chuẩn hóa và trích đặc trưng
  → Writer Profile
  → Điều chỉnh Font Pack / Allograph / Render Profile
  → CA-VHC + Stroke Graph Optimizer
  → SVG centerline cá nhân hóa cho máy vẽ
  ```
- **Đặc trưng dự kiến của Writer Profile:** Độ nghiêng; tỷ lệ cao/rộng; baseline và độ dao động baseline; khoảng cách chữ/từ; độ cong và hình dáng nét; kiểu nối nét; phân bố xác suất sử dụng từng allograph; cách đặt và thứ tự viết dấu; biến thiên tự nhiên có kiểm soát.
- **Phương pháp tiếp cận:** Ưu tiên few-shot personalization từ tập mẫu nhỏ của người dùng; đầu ra mục tiêu vẫn là quỹ đạo centerline nét đơn chạy được trên máy vẽ vật lý.
- **Đạo đức và quản trị dữ liệu:** Yêu cầu sự đồng ý rõ ràng của người cung cấp mẫu chữ; ẩn danh hóa dữ liệu Writer Profile; tuyệt đối không thu thập hoặc công khai chữ ký và dữ liệu định danh nhạy cảm; phân tách nghiêm ngặt tập huấn luyện và đánh giá; lưu trữ seed và phiên bản profile để đảm bảo tính tái lập khoa học.

#### G. Nghiên cứu mở rộng: Bố cục trang, Cỡ chữ & Phân trang
- **Lộ trình phát triển:** Tùy biến cỡ chữ (`font_size_pt`), lề trang (`margins_mm`), tọa độ bắt đầu viết, tỷ lệ giãn dòng/giãn chữ, căn lề văn bản (trái/giữa/phải), tự động ngắt dòng thông minh theo ascender/descender/dấu.
- **Phân trang đa trang (Multi-page):** Hướng tới tự động phân trang và xuất mảng nhiều file SVG kèm metadata `page_index`, `page_count`.
- **Trạng thái hiện tại:** Backend hiện chỉ xử lý trên 1 trang duy nhất và từ chối xử lý bằng lỗi `TEXT_OVERFLOW` khi văn bản vượt quá khổ giấy thiết lập.

#### H. Font tương lai và định dạng TTF/OTF
- Hiện tại hệ thống không hỗ trợ tải trực tiếp tệp font TTF/OTF để tạo đường centerline vẽ nét đơn.
- Chuyển đổi từ font viền đôi (Outline font TTF/OTF) sang nét đơn (Single-stroke centerline) là bài toán nghiên cứu dài hạn vì đường viền outline không đồng nhất với quỹ đạo ngòi bút vật lý.
- Mỗi Font Pack mới muốn đưa vào hệ thống bắt buộc phải có đầy đủ dữ liệu hình học, mỏ neo dấu, biến thể allographs và bộ test QA riêng.

---

## 3. Phần cứng, Cơ khí & Cảm biến (Thành viên 3)

| Hạng mục                    | Lựa chọn                 | Lý do    |
| --------------------------- | ------------------------ | -------- |
| Vi điều khiển               | *(vd: Arduino/ESP32...)* | *(điền)* |
| Ngôn ngữ firmware           | Python (qua pyaxidraw)   | Đồng bộ ngôn ngữ với backend Python và tương thích trực tiếp với tập lệnh máy vẽ |
| Camera/cảm biến sử dụng     | *(điền)*                 | *(điền)* |
| Thư viện điều khiển AxiDraw | pyaxidraw                | Thư viện Python chính thức để đọc file SVG và gửi lệnh trực tiếp xuống phần cứng (hiện backend đang chạy mô phỏng phần mềm) |

### Phân định 3 mức điều khiển phần cứng, thời gian & telemetry
1. **Mức 1 — Hiện tại (Mô phỏng phần mềm):** Preview/animation trên giao diện và tính toán thời gian mô phỏng (`actual_draw_time_sec = total_distance / 40.0`). Giao tiếp REST polling hiện tại chỉ là truy vấn tiến trình mô phỏng từ backend, chưa phải điều khiển phản hồi từng nét từ máy vẽ thật.
2. **Mức 2 — Giai đoạn kết nối máy thật:** Đo đạc thực nghiệm thời gian vẽ thực tế, vận tốc, gia tốc, thời gian nâng/hạ bút, độ mòn ngòi bút và sai số quỹ đạo vật lý.
3. **Mức 3 — Tương lai (Telemetry phản hồi thời gian thực):** Nhận tín hiệu telemetry từ phần cứng máy vẽ để đồng bộ tiến trình vẽ từng nét SVG với trạng thái thi công thực tế của đầu bút.
- **Mô hình ước tính thời gian thực tế trong nghiên cứu:** Phải tính đến chiều dài nét vẽ, quãng đường pen-up, vận tốc vẽ, gia tốc/giảm tốc tại các góc đổi hướng nhọn, thời gian nâng/hạ bút cơ học, và hệ số hiệu chuẩn theo từng loại máy và bề mặt giấy/bút.

---

## 4. Phần mềm điều khiển, Giao diện & Tích hợp (Thành viên 4)

| Hạng mục           | Lựa chọn          | Lý do                                                |
| ------------------ | ----------------- | ---------------------------------------------------- |
| Frontend framework | React.js          | Render SPA mượt mà, quản lý component tốt            |
| Backend framework  | Python / FastAPI  | Tốc độ cao, đồng bộ ngôn ngữ với team AI             |
| Giao tiếp realtime | REST polling      | Theo quyết định đã chốt trong `OmniDraw_API_Spec-4.md` |
| Database (nếu cần) | SQLite            | Gọn nhẹ, lưu file cục bộ, khởi tạo nhanh chóng       |
| Trích xuất văn bản (.docx) | `python-docx` | Hỗ trợ người dùng tải file Word lên trong chế độ Viết Thư Tay để tự động trích xuất nội dung |

---

## Quy ước chung toàn nhóm

- Định dạng dữ liệu trao đổi giữa các mảng: xem file riêng `OmniDraw_API_Spec-4.md` (không lặp lại ở đây, tránh 2 nơi lệch nhau).
- Quản lý code: *(điền: Git repo ở đâu, branch convention...)*
- Style code/naming convention: *(điền nếu nhóm thống nhất)*

