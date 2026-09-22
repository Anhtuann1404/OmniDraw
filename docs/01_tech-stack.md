# OmniDraw — Tech Stack

**Cập nhật lần cuối:** 18/09/2026
**Quy tắc:** Khi đổi công nghệ ở bất kỳ mảng nào, phải sửa file này TRƯỚC hoặc NGAY khi đổi — không để người khác code theo stack cũ đã lỗi thời.

---

## 1. AI Data & Writer Profile (TV1 — AI Data & Writer Profile Lead)

| Hạng mục             | Lựa chọn                                           | Lý do    |
| -------------------- | -------------------------------------------------- | -------- |
| Ngôn ngữ             | Python                                             | Đồng bộ backend FastAPI của hệ thống |
| Model/API sinh ảnh   | Google Gemini API                                  | Công nghệ sinh ảnh hiện hành; OpenAI DALL-E là phương án đã khảo sát/dự phòng chưa tích hợp trong luồng chính thức, không có cơ chế fallback tự động trong code |
| Model style transfer | *(chưa triển khai)*                                | Dự kiến nghiên cứu hoặc fine-tune mô hình phác thảo/line-art khi có dữ liệu |
| Thư viện chính       | `google-genai`, `requests`                         | Giao tiếp API Google Gemini hiện hành; `openai` là thư viện từng dùng trong prototype ban đầu |
| Quản trị dữ liệu & Schema | JSON Schema (versioned), Pandas/Numpy           | Định nghĩa cấu trúc `WriterProfile`, protocol thu thập mẫu chữ viết tay và bộ trích xuất đặc trưng hình học |

> *(Chi tiết quy chuẩn phân tách giữa CA-VHC Structural Dataset và Writer Profile Dataset, quy trình thu thập, schema và ranh giới ownership: xem [`08_handwriting_dataset_spec.md`](08_handwriting_dataset_spec.md)).*

---

## 2. Tối ưu đường vẽ & Quy hoạch quỹ đạo (TV2 — Stroke Optimization & Path Planning Lead)

| Hạng mục                   | Lựa chọn                                              | Lý do    |
| -------------------------- | ------------------------------------------------------ | -------- |
| Ngôn ngữ                   | Python                                                 | Đồng bộ với backend FastAPI và các mảng khác, dễ tích hợp qua function call hoặc CLI trực tiếp |
| Thư viện CV                | OpenCV (`opencv-python-headless`)                      | Có sẵn Canny edge detection + `findContours` để trích đường nét từ ảnh, phổ biến, tài liệu nhiều, tốc độ tốt |
| Thuật toán tối ưu đường vẽ tranh | Nearest Neighbor + Or-opt (candidate list qua KD-tree) + Kinematic Turn Penalty | Khởi tạo nhanh bằng NN trên `cKDTree` kết hợp hàm phạt quán tính động học $\text{dist} + \lambda(1 - \cos\theta)$ chống giật ngòi bút; Or-opt chỉ xét ứng viên không gian thực tế, scale tốt với hàng nghìn nét so với 2-opt truyền thống. |
| Thư viện vector hoá ảnh    | `cv2.findContours` (có sẵn trong OpenCV) + `scipy` (KD-tree) | Không cần thêm dependency ngoài; đủ đáp ứng nhu cầu trích contour làm stroke và tìm hàng xóm không gian nhanh |
| Stroke/Path Optimization Core | Tối ưu hóa chuyển động, pen-up distance minimization & transition cost | Chịu trách nhiệm thiết kế hàm chi phí chuyển động, phạt góc bẻ tiếp tuyến và thành phần tối ưu quỹ đạo trong Trellis DAG |

---

## 3. Phần cứng, Hiệu chuẩn & Thực nghiệm Vật lý (TV3 — Hardware, Calibration & Physical Validation Lead)

| Hạng mục                    | Lựa chọn                                                | Lý do                                                                                   |
| --------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Thiết bị máy vẽ             | AxiDraw V3 / SE (Khổ vẽ tiêu chuẩn A4/A3)              | Máy vẽ ngòi bút chính xác cao, chuyển động Cartesian XY đai curoa êm ái                  |
| Vi điều khiển               | EiBotBoard (EBB) v2.8 (Microchip PIC18F46J50)           | Board điều khiển chuyên dụng cho AxiDraw, giao tiếp USB CDC Virtual COM                 |
| Ngôn ngữ firmware           | EBB Firmware Command Protocol / Python (qua pyaxidraw)  | Đồng bộ ngôn ngữ với backend Python và tương thích trực tiếp với tập lệnh máy vẽ        |
| Camera / Cảm biến sử dụng   | USB Webcam (UVC standard, cảm biến OV5640 hoặc tương đương) | Giám sát giấy, phát hiện góc nghiêng và độ sạch (Closed-Loop Vision) qua OpenCV        |
| Thư viện điều khiển AxiDraw | `pyaxidraw` + `backend/hardware_adapter.py`             | Thư viện Python chính thức đọc file SVG và gửi lệnh, có lớp trừu tượng HAL an toàn      |

### Phân định 3 mức điều khiển phần cứng, thời gian & telemetry
1. **Mức 1 — Hiện tại (Mô phỏng phần mềm):** Preview/animation trên giao diện và tính toán thời gian vẽ mô phỏng/ước tính (`estimated_draw_time_sec` theo công thức xấp xỉ `total_path_length_mm / 40.0`). Giao tiếp REST polling hiện tại chỉ là truy vấn tiến trình mô phỏng từ backend, chưa phải điều khiển phản hồi từng nét từ máy vẽ thật. *(Lưu ý về implementation/contract debt: Backend hiện vẫn tạm thời lưu giá trị mô phỏng này vào trường `actual_draw_time_sec` khi `status="done"` theo contract API v1.4; đây là khoản nợ kỹ thuật và trường này chỉ được xem là số đo thực tế khi kết nối phần cứng vật lý ở Mức 2).*
2. **Mức 2 — Giai đoạn kết nối máy thật:** Đo đạc thực nghiệm thời gian vẽ thực tế (`actual_draw_time_sec`), vận tốc, gia tốc, thời gian nâng/hạ bút, độ mòn ngòi bút và sai số quỹ đạo vật lý từ máy vẽ AxiDraw.
3. **Mức 3 — Tương lai (Telemetry phản hồi thời gian thực):** Nhận tín hiệu telemetry từ phần cứng máy vẽ để đồng bộ tiến trình vẽ từng nét SVG với trạng thái thi công thực tế của đầu bút.
- **Mô hình ước tính thời gian thực tế trong nghiên cứu:** Phải tính đến chiều dài nét vẽ, quãng đường pen-up, vận tốc vẽ, gia tốc/giảm tốc tại các góc đổi hướng nhọn, thời gian nâng/hạ bút cơ học, và hệ số hiệu chuẩn theo từng loại máy và bề mặt giấy/bút.

---

## 4. Nền tảng, Tích hợp & Quản trị Hệ thống (TV4 — Project Lead & Handwriting / CA-VHC Composition Lead)

| Hạng mục           | Lựa chọn          | Lý do                                                |
| ------------------ | ----------------- | ---------------------------------------------------- |
| Kiến trúc hệ thống | Modular Monolith / API Gateway | TV4 điều phối kiến trúc tổng thể OmniDraw, quản lý contract và kết nối liên mảng |
| Frontend framework | React.js          | Render SPA mượt mà, quản lý component tốt            |
| Backend framework  | Python / FastAPI  | Tốc độ cao, đồng bộ ngôn ngữ với toàn bộ pipeline    |
| Handwriting Subsystem | `backend/handwriting/` | TV4 trực tiếp thiết kế và lập trình toàn bộ engine thư tay nét đơn, kiến trúc Font Pack, Unicode NFD, ghép dấu tiếng Việt, contextual allographs, smoothing và auditor (đặc tả dữ liệu cấu trúc CA-VHC và ranh giới với dữ liệu cá nhân hóa xem tại `08_handwriting_dataset_spec.md`) |
| Giao tiếp realtime | REST polling      | Theo quyết định đã chốt trong `OmniDraw_API_Spec-4.md` |
| Database (nếu cần) | SQLite            | Gọn nhẹ, lưu file cục bộ, khởi tạo nhanh chóng       |
| Trích xuất văn bản (.docx) | `python-docx` | Hỗ trợ người dùng tải file Word lên trong chế độ Viết Thư Tay để tự động trích xuất nội dung |
| Framework thực nghiệm | CSV Logging & Experiment Runner (TV4 lead) | TV4 xây dựng experiment runner, API orchestration và CSV logging; TV1 chuẩn bị corpus/fixtures/protocol; TV2 cung cấp thuật toán chuyển động, baseline và metrics; TV3 cung cấp số liệu đo máy thật |

---

## 5. Khung giải thuật Context-Aware Vietnamese Handwriting Composition (CA-VHC)

> **Định nghĩa:** Context-Aware Vietnamese Handwriting Composition (CA-VHC) là khung nghiên cứu phối hợp nhằm tối ưu đồng thời biến thể glyph theo ngữ cảnh, cách bố trí/thứ tự viết dấu tiếng Việt và quỹ đạo bút để sinh SVG centerline dễ đọc, ít va chạm và có thể thi công trên máy vẽ.

### Phân rã hai lõi kỹ thuật của CA-VHC

1. **Handwriting Composition Core (TV4 sở hữu chính):**
   - Quản lý và kiến trúc Font Pack nét đơn độc lập (`font_packs/`: `__init__.py`, `geometry.py`, `legacy.py`, `omni_casual.py`, `letter_variants.py`). Tách biệt tầng dữ liệu hình học khỏi tầng giải thuật render/auditor.
   - Phân rã Unicode NFD và ghép dấu tiếng Việt theo tọa độ mỏ neo (anchors) và tính toán khoảng dịch tâm (offset).
   - Cơ chế lựa chọn biến thể glyph theo ngữ cảnh (contextual allographs selection) và quy tắc loại thư (letter type).
   - Biểu diễn không gian trạng thái/ngữ cảnh (state/context representation) phía handwriting của Trellis DAG: tập biến thể glyph ứng viên, ràng buộc âm tiết, quy tắc chính tả dấu tiếng Việt, chi phí độ dễ đọc ($C_{\text{legibility}}$) và cảnh báo nguy cơ va chạm dấu sơ bộ ($C_{\text{collision}}$).
   - Bộ xuất SVG single-stroke centerline qua Catmull–Rom sang Cubic Bézier kết hợp auto-deskew.
   - Bộ kiểm tra hình học polyline (`audit_font_pack_geometry()`, `_stroke_min_distance()`) và công cụ QA thị giác (`qa_specimens.py`).
   - Kiểm soát seed số nguyên 32-bit không dấu bảo đảm tính tái lập kết quả render.

2. **Stroke/Path Optimization Core (TV2 sở hữu chính):**
   - Tối ưu hóa thứ tự nét vẽ tranh: thuật toán Nearest Neighbor kết hợp Or-opt (candidate search qua `cKDTree`) và hàm phạt quán tính ngòi bút Kinematic Turn Penalty $\text{dist} + \lambda(1 - \cos\theta)$.
   - Tối thiểu hóa quãng đường pen-up (pen-up distance minimization) và mô hình chi phí chuyển động trên mặt phẳng vẽ.
   - Thành phần quy hoạch quỹ đạo và chuyển trạng thái (transition/path optimization) của Trellis DAG: tính toán khoảng cách pen-up giữa các nét ($D_{\text{penup}}$), số lần nhấc bút ($N_{\text{lift}}$), góc bẻ tiếp tuyến ($C_{\text{curvature}}$) trong hàm `eval_transition()`.
   - Thiết lập các baseline chuyển động đối chứng và ablation study về chi phí động học.

3. **Thành phần đồng thiết kế (Co-designed / Shared Contribution):**
   - **Trellis DAG / Viterbi DP Optimizer (`optimize_word_dag()`):** TV4 phụ trách cấu trúc dữ liệu đồ thị, các node trạng thái glyph, ràng buộc chính tả dấu tiếng Việt và ngữ cảnh văn bản; TV2 phụ trách thuật toán quy hoạch động, hàm chi phí chuyển tiếp giữa các nét (transition cost) và tối ưu hóa quỹ đạo chuyển động.
   - **Định nghĩa hàm mục tiêu $J$:** Hàm mục tiêu tổng hợp $J = w_1 D_{\text{penup}} + w_2 N_{\text{lift}} + w_3 C_{\text{curvature}} + w_4 C_{\text{collision}} + w_5 C_{\text{legibility}}$ tích hợp cả tiêu chí chuyển động cơ học (TV2) và tiêu chí thẩm mỹ/chính tả hình học (TV4).

---

### Chi tiết trạng thái giải thuật CA-VHC

#### A. Đã triển khai (Implemented)
- **Font Pack nét đơn độc lập (TV4):** Cấu trúc dữ liệu hình học tách rời (`omnidraw_legacy`, `omni_casual`) định nghĩa tọa độ centerline chuẩn hóa.
- **Unicode NFD & Modular Accents (TV4):** Phân rã ký tự tiếng Việt thành ký tự gốc và dấu thanh riêng biệt, tự động ghép dấu theo tọa độ mỏ neo (anchors) và tính toán khoảng dịch tâm (offset).
- **Contextual allographs hiện có (TV4):** Biến thể chữ hoa mở đầu văn bản trang trọng (`formal_initial` cho K, T, C trên font pack legacy) và biến thể hình học kết thúc từ (`word_final` cho n, m trong Omni Casual).
- **Stroke Graph Optimizer (Đồng thiết kế TV4 & TV2):** Giải thuật quy hoạch động Viterbi DP trên Trellis DAG theo từng từ (`optimize_word_dag()`), kết hợp state representation của TV4 và transition optimization của TV2.
- **Hàm chi phí chuyển trạng thái (Đồng thiết kế TV4 & TV2):** Hàm mục tiêu $J = w_1 D_{\text{penup}} + w_2 N_{\text{lift}} + w_3 C_{\text{curvature}} + w_4 C_{\text{collision}} + w_5 C_{\text{legibility}}$ lựa chọn biến thể glyph và quyết định nối nét/nhấc bút dựa trên khoảng cách pen-up, số lần nhấc bút, góc bẻ tiếp tuyến, nguy cơ va chạm hình học sơ bộ qua `bridge_collision_cost`, và độ dễ đọc.
- **Đầu ra SVG Centerline (TV4):** Xuất đường nét đơn mượt mà qua Catmull–Rom sang Cubic Bézier kết hợp auto-deskew, duy trì đầu ra centerline theo cấu trúc Font Pack để máy vẽ thi công đúng một nét vẽ liên tục.
- **Seed tái lập (TV4):** Seed số nguyên 32-bit không dấu giúp tái lập nhất quán kết quả render giữa các lần chạy.
- **Auditor hình học (TV4):** Bộ kiểm tra polyline (`audit_font_pack_geometry()`, `_stroke_min_distance()`) phát hiện đoạn suy biến, nét đè lặp, và phát hiện các va chạm thuộc phạm vi bộ kiểm tra hiện tại; chưa phải bảo đảm hình học cho mọi văn bản và cấu hình.

#### B. Đang phát triển (In Progress)
- Đưa dấu tiếng Việt và vùng cấm va chạm trực tiếp vào bài toán tối ưu DAG (TV4 phụ trách chính về ràng buộc chính tả, TV2 phối hợp về chuyển động).
- Mở rộng hàm chi phí theo loại thư (`letter_type`) và vị trí từ/câu/dòng cụ thể (TV4).
- Đánh giá định lượng chất lượng lựa chọn allograph và tính tự nhiên của nét nối (TV4 phối hợp TV2).
- Hoàn thiện bộ QA trực quan cho toàn bộ chữ và dấu tiếng Việt (mở rộng từ `qa_specimens.py` — TV4).

#### C. Định hướng nghiên cứu (Research Directions)
- **Tối ưu hóa đa cấp:** Tối ưu hóa quỹ đạo nét ở cấp độ từ và dòng văn bản thay vì chỉ xử lý cục bộ từng vị trí; dấu hiện chưa được tối ưu đầy đủ như một trạng thái/ràng buộc chung trong DAG (hiện mới đặt bằng anchor/offset và hậu kiểm).
- **Mô hình hóa dấu tiếng Việt & thứ tự nét trễ (Định hướng nghiên cứu):** Bố trí dấu theo base vowel, quy tắc chính tả và cấu trúc âm tiết tiếng Việt (Vietnamese orthography-aware diacritic composition; engine không tự nhận hiểu ngữ nghĩa hay ngữ âm); mô hình hóa vùng cấm va chạm quanh glyph/dấu; xử lý tổ hợp nhiều dấu; quyết định viết dấu ngay, sau từ hoặc theo nhóm nét trễ để cân bằng giữa quãng đường di chuyển quay lại, số lần nhấc bút và độ dễ đọc khi đưa dấu tham gia đầy đủ vào tối ưu DAG (TV4 lead chính tả/dấu, TV2 lead tối ưu quỹ đạo nét trễ).
- **Mở rộng các cấp ngữ cảnh allographs:** Hướng tới đầy đủ các cấp ngữ cảnh: đầu đoạn, đầu câu, đầu từ, giữa từ, cuối từ, cuối câu, cuối dòng và theo loại thư (TV4).
- **Thực nghiệm & So sánh:** Xây dựng bộ thực nghiệm so sánh với các phương pháp cơ sở (baseline) và ablation study bóc tách từng thành phần trong hàm chi phí DAG (TV2 lead baseline chuyển động, TV1 chuẩn bị corpus dữ liệu, TV4 lead experiment runner và logging).
- **Đánh giá đa tiêu chí:** Đánh giá đồng thời cả chất lượng hình học, độ dễ đọc và chi phí chuyển động của máy vẽ.

#### D. Phân biệt 5 khái niệm trong hệ thống chữ viết
1. **Font Pack:** Tập dữ liệu hình học nét đơn chuẩn hóa (`geometry`, `metrics`, `anchors`, `contextual variants`) định nghĩa tọa độ centerline của các ký tự (do TV4 thiết kế và quản lý).
2. **Render Profile:** Tham số biến đổi hình học khi kết xuất (độ nghiêng `slant`, tỷ lệ co giãn `scale`, khoảng cách dòng `line_spacing`) áp dụng đồng nhất lên font pack trong một phiên vẽ.
3. **Letter Type:** Ngữ cảnh văn bản quy định quy tắc lựa chọn biến thể glyph và bố cục (hiện tại: `general`, `formal`; tương lai: thân mật, tình cảm, thiệp mời, học sinh...).
4. **Writer Profile:** Hồ sơ đặc trưng thói quen và phong cách cá nhân hóa của một người viết cụ thể (độ nghiêng, jitter baseline, spacing, thiên hướng chọn allograph) phục vụ few-shot personalization (thuộc nhánh nghiên cứu mở rộng P2 do TV1 chủ trì; chưa tích hợp vào engine lõi).
5. **CA-VHC Structural Dataset:** Tập dữ liệu mẫu chữ viết tay tiếng Việt tập trung vào CẤU TRÚC và CHÍNH TẢ (tọa độ mỏ neo anchor, độ lệch diacritic offset, vùng cấm va chạm, biến thể allograph theo vị trí từ và tổ hợp dấu thanh). Do TV1 thu thập và chuẩn bị dữ liệu, nhưng toàn bộ quy tắc sử dụng và logic chính tả do TV4 sở hữu phục vụ calibrate và đánh giá CA-VHC engine.
*(Xem phân định chi tiết tại [`08_handwriting_dataset_spec.md`](08_handwriting_dataset_spec.md)).*

#### E. Phân biệt lõi nghiên cứu và tính năng trình diễn
- **Lõi nghiên cứu (Core Contributions):**
  - Contextual glyph selection (TV4).
  - Vietnamese diacritic constraints & delayed stroke ordering (TV4 lead chính tả, TV2 lead tối ưu chuyển động nét trễ).
  - Stroke/pen trajectory optimization (TV2 lead tối ưu quỹ đạo, TV4 lead biểu diễn đồ thị Trellis DAG).
  - Khả năng thực thi trên máy vẽ (plotter execution — TV3 lead phần cứng/hiệu chuẩn).
- **Tính năng trình diễn / mở rộng (Demos & Embellishments):**
  - Nét kéo dài lượn sóng dưới từ cuối câu (Terminal swash).
  - Chữ hoa đầu đoạn trang trí (Drop cap).
  - Cụm từ nối liền khối (Logograms: "Kính gửi", "Thân gửi", "Cảm ơn").
  - Tiêu đề uốn lượn vòm cong Bézier.
  - Hoa văn phân đoạn centerline (trái tim, dây leo).

#### F. Nghiên cứu mở rộng: AI cá nhân hóa thói quen chữ viết (Writer Profile — TV1 chủ trì)
- **Mô hình luồng nghiên cứu tương lai (chưa triển khai trong code hiện tại):**
  ```text
  Mẫu chữ người dùng
  → Chuẩn hóa và trích đặc trưng (TV1)
  → Writer Profile (TV1)
  → Điều chỉnh Font Pack / Allograph / Render Profile (TV4)
  → CA-VHC + Stroke Graph Optimizer (TV4 & TV2)
  → SVG centerline cá nhân hóa cho máy vẽ (TV3 thi công)
  ```
- **Đặc trưng dự kiến của Writer Profile:** Độ nghiêng; tỷ lệ cao/rộng; baseline và độ dao động baseline; khoảng cách chữ/từ; độ cong và hình dáng nét; kiểu nối nét; phân bố xác suất sử dụng từng allograph; cách đặt và thứ tự viết dấu; biến thiên tự nhiên có kiểm soát.
- **Phương pháp tiếp cận:** Ưu tiên few-shot personalization từ tập mẫu nhỏ của người dùng; đầu ra mục tiêu vẫn là quỹ đạo centerline nét đơn chạy được trên máy vẽ vật lý.
- **Đạo đức và quản trị dữ liệu:** Yêu cầu sự đồng ý rõ ràng của người cung cấp mẫu chữ; ẩn danh hóa dữ liệu Writer Profile; tuyệt đối không thu thập hoặc công khai chữ ký và dữ liệu định danh nhạy cảm; phân tách nghiêm ngặt tập huấn luyện và đánh giá; lưu trữ seed và phiên bản profile để đảm bảo tính tái lập khoa học.

#### G. Nghiên cứu mở rộng: Bố cục trang, Cỡ chữ & Phân trang (TV4 phụ trách)
- **Lộ trình phát triển:** Tùy biến cỡ chữ (`font_size_pt`), lề trang (`margins_mm`), tọa độ bắt đầu viết, tỷ lệ giãn dòng/giãn chữ, căn lề văn bản (trái/giữa/phải), tự động ngắt dòng thông minh theo ascender/descender/dấu.
- **Phân trang đa trang (Multi-page):** Hướng tới tự động phân trang và xuất mảng nhiều file SVG kèm metadata `page_index`, `page_count`.
- **Trạng thái hiện tại:** Backend hiện chỉ xử lý trên 1 trang duy nhất và từ chối xử lý bằng lỗi `TEXT_OVERFLOW` khi văn bản vượt quá khổ giấy thiết lập.

#### H. Font tương lai và định dạng TTF/OTF
- Hiện tại hệ thống không hỗ trợ tải trực tiếp tệp font TTF/OTF để tạo đường centerline vẽ nét đơn.
- Chuyển đổi từ font viền đôi (Outline font TTF/OTF) sang nét đơn (Single-stroke centerline) là bài toán nghiên cứu dài hạn vì đường viền outline không đồng nhất với quỹ đạo ngòi bút vật lý.
- Mỗi Font Pack mới muốn đưa vào hệ thống bắt buộc phải có đầy đủ dữ liệu hình học, mỏ neo dấu, biến thể allographs và bộ test QA riêng.

---

## Quy ước chung toàn nhóm

- Định dạng dữ liệu trao đổi giữa các mảng: xem file riêng `OmniDraw_API_Spec-4.md` (không lặp lại ở đây, tránh 2 nơi lệch nhau).
- Quản lý code: Git repo tập trung, nhánh tính năng theo đường chạy (feature branches), TV4 điều phối review và merge code.
- Style code/naming convention: PEP 8 cho Python backend, ESLint/Prettier cho React frontend.

