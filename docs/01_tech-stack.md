# OmniDraw — Tech Stack

**Cập nhật lần cuối:** *(điền ngày mỗi khi sửa)*
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
| Thuật toán tối ưu đường vẽ | Nearest Neighbor + Or-opt (candidate list qua KD-tree) | NN cho lời giải khởi tạo nhanh (O(n log n) nhờ `scipy.spatial.cKDTree`); Or-opt chỉ xét các nét *gần nhau về không gian thực tế* để cải tiến, scale tốt với hàng nghìn nét — khác 2-opt truyền thống (duyệt toàn bộ cặp O(n²), quá chậm với ảnh nhiều chi tiết như nhóm ảnh 021-030) |
| Thư viện vector hoá ảnh    | `cv2.findContours` (có sẵn trong OpenCV) + `scipy` (KD-tree) | Không cần thêm dependency ngoài; đủ đáp ứng nhu cầu trích contour làm stroke và tìm hàng xóm không gian nhanh |



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


---



## Quy ước chung toàn nhóm

- Định dạng dữ liệu trao đổi giữa các mảng: xem file riêng `OmniDraw_API_Spec.md` (không lặp lại ở đây, tránh 2 nơi lệch nhau).
- Quản lý code: *(điền: Git repo ở đâu, branch convention...)*
- Style code/naming convention: *(điền nếu nhóm thống nhất)*

