# OmniDraw — Tech Stack

**Cập nhật lần cuối:** 13/09/2026
**Quy tắc:** Khi đổi công nghệ ở bất kỳ mảng nào, phải sửa file này TRƯỚC hoặc NGAY khi đổi — không để người khác code theo stack cũ đã lỗi thời.

---

## 1. AI Core — Sinh ảnh & Chuyển phong cách (Thành viên 1)


| Hạng mục             | Lựa chọn                                           | Lý do    |
| -------------------- | -------------------------------------------------- | -------- |
| Ngôn ngữ             | Python                                             | Đồng bộ backend FastAPI của hệ thống |
| Model/API sinh ảnh   | Google Gemini API (Imagen 3) / OpenAI DALL-E 3     | Gemini có free tier tốt (15 req/phút, 1.500 req/ngày), đủ sức test miễn phí cho cả nhóm |
| Model style transfer | *(điền)*                                           | *(điền)* |
| Thư viện chính       | `google-genai` / `openai`, `requests`              | Giao tiếp API chuẩn, phổ biến |


**Cập nhật lần cuối:** 30/08/2026

...

## 2. AI Ứng dụng — Thị giác máy tính & Tối ưu vẽ (Thành viên 2)

| Hạng mục                   | Lựa chọn                                              | Lý do    |
| -------------------------- | ------------------------------------------------------ | -------- |
| Ngôn ngữ                   | Python                                                 | Đồng bộ với backend FastAPI và các mảng khác, dễ tích hợp qua function call hoặc CLI trực tiếp |
| Thư viện CV                | OpenCV (`opencv-python-headless`)                      | Có sẵn Canny edge detection + `findContours` để trích đường nét từ ảnh, phổ biến, tài liệu nhiều, tốc độ tốt |
| Thuật toán tối ưu đường vẽ | Nearest Neighbor + Or-opt (candidate list qua KD-tree) + Kinematic Turn Penalty | Khởi tạo nhanh bằng NN trên `cKDTree` kết hợp hàm phạt quán tính động học $\text{dist} + \lambda(1 - \cos\theta)$ chống giật ngòi bút; Or-opt chỉ xét ứng viên không gian thực tế, scale tốt với hàng nghìn nét so với 2-opt truyền thống. |
| Thư viện vector hoá ảnh    | `cv2.findContours` (có sẵn trong OpenCV) + `scipy` (KD-tree) | Không cần thêm dependency ngoài; đủ đáp ứng nhu cầu trích contour làm stroke và tìm hàng xóm không gian nhanh |
| Định hướng CA-VHC và lõi Stroke Graph Optimizer | **Context-Aware Vietnamese Handwriting Composition (CA-VHC)** kết hợp **Stroke Graph Optimizer** (Python, NumPy, Viterbi trên Trellis DAG, Cubic Bézier và Catmull–Rom-to-Bézier smoothing, NFD Modular Accents) | Hiện đã có lõi Font Pack độc lập, NFD Modular Accents và quy hoạch động Viterbi trên Trellis DAG để chọn chuỗi biến thể và nét nối tối ưu trong một từ. Định hướng CA-VHC sẽ mở rộng lõi này bằng khả năng thích ứng ngữ cảnh thể loại văn bản, vị trí từ/dòng (đầu đoạn, giữa câu, cuối từ), bổ sung kho contextual allographs, chữ hoa đầu đoạn trang trí (illuminated drop cap), nét kéo dài lượn sóng dưới từ (terminal swash) và cụm từ nối liền khối (contextual logograms: "Thân gửi", "Cảm ơn", "Kính gửi"). Đảm bảo tính bất biến 100% nét đơn centerline không viền đôi, cơ chế bố trí dấu theo quy tắc hình học, kết hợp auditor hậu kiểm khoảng cách giữa các polyline bằng _stroke_min_distance. |
| Kiến trúc quản lý Font Pack | Module hóa hướng gói (`backend/handwriting/font_packs/`: `__init__.py`, `geometry.py`, `legacy.py`, `omni_casual.py`, `letter_variants.py`) | Tách biệt hoàn toàn tầng dữ liệu hình học (Geometry/Metrics) khỏi tầng giải thuật (Engine/Auditor), cho phép mở rộng không giới hạn các bộ chữ và biến thể allographs mà không làm phình to engine lõi. |




## 3. Phần cứng, Cơ khí & Cảm biến (Thành viên 3)


| Hạng mục                    | Lựa chọn                 | Lý do    |
| --------------------------- | ------------------------ | -------- |
| Vi điều khiển               | *(vd: Arduino/ESP32...)* | *(điền)* |
| Ngôn ngữ firmware           | Python (qua pyaxidraw)   | Đồng bộ ngôn ngữ với backend Python và tương thích trực tiếp với tập lệnh máy vẽ |
| Camera/cảm biến sử dụng     | *(điền)*                 | *(điền)* |
| Thư viện điều khiển AxiDraw | pyaxidraw                | Thư viện Python chính thức để đọc file SVG và gửi lệnh trực tiếp xuống phần cứng |




## 4. Phần mềm điều khiển, Giao diện & Tích hợp (Thành viên 4)


| Hạng mục           | Lựa chọn          | Lý do                                                |
| ------------------ | ----------------- | ---------------------------------------------------- |
| Frontend framework | *React.js*        | *Render SPA mượt mà, quản lý component tốt*          |
| Backend framework  | *python(FastApi)* | *Tốc độ cao, đồng bộ ngôn ngữ vói team AI*           |
| Giao tiếp realtime | REST polling      | Theo quyết định đã chốt trong `OmniDraw_API_Spec.md` |
| Database (nếu cần) | *sqlite*          | *gọn nhẹ lưu file cục bộ khời tạo nhanh chóng*       |
| Trích xuất văn bản (.docx) | `python-docx` | Hỗ trợ người dùng tải file Word lên trong chế độ Viết Thư Tay để tự động trích xuất nội dung |


---



## Quy ước chung toàn nhóm

- Định dạng dữ liệu trao đổi giữa các mảng: xem file riêng `OmniDraw_API_Spec.md` (không lặp lại ở đây, tránh 2 nơi lệch nhau).
- Quản lý code: *(điền: Git repo ở đâu, branch convention...)*
- Style code/naming convention: *(điền nếu nhóm thống nhất)*

