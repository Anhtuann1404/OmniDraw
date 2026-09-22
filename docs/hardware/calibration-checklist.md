# OmniDraw — Hardware Calibration Checklist & Protocol (TV3)

**Phiên bản:** v1.0  
**Người lập:** TV3 — Hardware, Calibration & Physical Validation Lead  
**Cập nhật lần cuối:** 18/09/2026  
**Áp dụng cho:** Máy vẽ AxiDraw (v2/v3/SE A4), firmware EBB (EiBotBoard), và hệ thống giả lập `MockSimulatorAdapter`.

---

## 1. Danh mục Kiểm tra Trước khi Vận hành (Pre-flight Inspection Checklist)

Trước khi gửi bất kỳ lệnh vẽ nào xuống máy vẽ vật lý, TV3 bắt buộc phải thực hiện kiểm tra theo checklist sau:

| STT | Hạng mục kiểm tra | Tiêu chuẩn đạt | Trạng thái |
| :---: | :--- | :--- | :---: |
| 1 | **Nguồn cấp điện (Power Supply)** | Adapter 9V/1.5A–2.1A cấp nguồn ổn định cho mạch EBB, đèn LED xanh sáng liên tục. | ⬜ Chưa kiểm tra |
| 2 | **Cáp kết nối USB/Serial** | Dây cáp cắm chắc chắn từ PC vào cổng USB của EBB, máy tính nhận diện thiết bị CDC COM port (trên Windows: Device Manager hiển thị cổng COM, trên Linux: `/dev/ttyACM0`). | ⬜ Chưa kiểm tra |
| 3 | **Cơ cấu dây đai & Ổ bi (Belts & Pulleys)** | Dây đai GT2 hai trục X và Y có độ căng vừa phải (không chùng gây rơ bước, không quá căng làm quá tải động cơ bước). | ⬜ Chưa kiểm tra |
| 4 | **Bút vẽ & Cơ cấu kẹp bút** | Bút được kẹp vuông góc $90^\circ$ so với mặt giấy, ngòi bút không bị lỏng khi di chuyển nhanh. | ⬜ Chưa kiểm tra |
| 5 | **Bàn vẽ & Giấy A4** | Giấy A4 đặt phẳng phiu trên tấm lót, cố định 4 góc bằng băng dính giấy (tránh xê dịch khi bút tì lên mặt giấy). | ⬜ Chưa kiểm tra |
| 6 | **Camera thị giác (Webcam/Closed-Loop Vision)** | Camera đặt góc nhìn từ trên xuống (top-down), bao quát toàn bộ khổ giấy A4, chạy script `python backend/camera_inspector.py --self-check` trả về `recommendation: "ready"`. | ⬜ Chưa kiểm tra |

---

## 2. Quy trình Căn gốc Tọa độ Vật lý (Origin & Homing Protocol)

1. **Vị trí gốc (0, 0):**
   - Góc trên bên trái (Top-Left) của bàn vẽ là gốc tọa độ $(X=0, Y=0)$.
   - Chiều dương trục $X$ hướng từ trái sang phải ($0 \to 297\text{ mm}$).
   - Chiều dương trục $Y$ hướng từ trên xuống dưới ($0 \to 210\text{ mm}$).
2. **Quy trình về Home bằng tay / phần mềm:**
   - Bước 1: Nâng bút lên vị trí an toàn (`pen-up`).
   - Bước 2: Tắt động cơ bước (disengage motors) hoặc bấm lệnh `ad.options.mode = "align"`.
   - Bước 3: Đưa đầu bút thủ công hoặc qua lệnh về đúng góc mép trên-trái của khổ giấy A4 (cách mép giấy $5\text{ mm}$ biên an toàn).
   - Bước 4: Khóa động cơ bước và xác lập vị trí gốc $(0, 0)$.

---

## 3. Bảng Thông số Hiệu chuẩn Động học (Kinematic Calibration Profile)

Để đảm bảo nét chữ viết tay tiếng Việt và nét vẽ tranh đạt chất lượng cao nhất, không bị rung mực hoặc rách giấy:

| Tham số cấu hình | Giá trị mặc định đề xuất | Phạm vi cho phép | Ý nghĩa kỹ thuật |
| :--- | :---: | :---: | :--- |
| **Vận tốc vẽ nét (speed_pendown)** | $25\text{ mm/s}$ (Handwriting)<br>$40\text{ mm/s}$ (Art Mode) | $10 - 50\text{ mm/s}$ | Vận tốc đầu bút khi tì lên mặt giấy. Chữ viết tay cần đi chậm hơn để mực ra đều. |
| **Vận tốc nhấc bút di chuyển (speed_penup)** | $75\text{ mm/s}$ | $50 - 110\text{ mm/s}$ | Vận tốc di chuyển đầu bút giữa các nét không vẽ (Rapid travel). |
| **Góc nâng servo (pen_pos_up)** | $60\%$ | $40\% - 75\%$ | Chiều cao ngòi bút khi nhấc lên khỏi mặt giấy (tránh quệt mực vào giấy). |
| **Góc hạ servo (pen_pos_down)** | $35\%$ | $20\% - 45\%$ | Áp lực ngòi bút tì lên mặt giấy (điều chỉnh theo loại ngòi bi / ngòi gel / bút kim). |
| **Độ trễ hạ bút (pen_delay_down)** | $120\text{ ms}$ | $80 - 200\text{ ms}$ | Thời gian chờ servo hạ ngòi chạm hẳn vào giấy trước khi trục XY bắt đầu di chuyển (tránh bị mất đầu nét). |
| **Độ trễ nâng bút (pen_delay_up)** | $100\text{ ms}$ | $60 - 150\text{ ms}$ | Thời gian chờ servo nhấc hẳn ngòi lên trước khi trục XY phi nhanh (tránh vệt mực đuôi). |
| **Gia tốc (accel)** | $75\%$ | $50\% - 100\%$ | Độ mượt khi tăng/giảm tốc độ qua các đoạn cua gấp Bézier. |

---

## 4. Phân định Hệ Metrics Thực nghiệm (Resolving Contract Debt)

Để bài báo NCKH và báo cáo đề tài đạt độ chuẩn mực học thuật cao nhất:

1. **`estimated_draw_time_sec` (Thời gian Ước lượng / Mô phỏng):**
   - Được tính bằng công thức: $T_{\text{est}} = \frac{\sum L_{\text{path}}}{V_{\text{pen}}} + N_{\text{lifts}} \times \Delta t_{\text{servo}}$.
   - Áp dụng trong toàn bộ quá trình chờ đợi và hiển thị % trên giao diện Web UI.
   - Khi chạy ở chế độ `MockSimulatorAdapter`, trường này phản ánh thời gian chạy ảo.
2. **`actual_draw_time_sec` (Thời gian Thi công Vật lý Thực tế):**
   - **Định nghĩa bắt buộc:** Chỉ được đo bằng đồng hồ bấm giờ phần cứng / wall-clock time thực tế khi máy vẽ AxiDraw vật lý bắt đầu kéo nét đầu tiên đến khi nâng bút về gốc $(0,0)$.
   - **Xóa nợ Contract:** Trong kết quả trả về của `backend/hardware_adapter.py`:
     - Nếu chạy mô phỏng: Cờ `is_simulated = True` và `actual_hardware_measured = False`.
     - Nếu chạy máy thật: Cờ `is_simulated = False` và `actual_hardware_measured = True`.
   - Trong log CSV của bài báo NCKH, chỉ những mẫu chạy máy thật mới được đưa số liệu `actual_draw_time_sec` vào phân tích đối chứng.

---

## 5. Quy trình Kiểm thử Tự động với SVG Fixture (Smoke Test Protocol)

Trước khi đưa máy vào vẽ các tác phẩm lớn:
1. Nạp file fixture chuẩn: [`tests/fixtures/smoke_test_specimen.svg`](file:///d:/UED/NCKH/OmniDraw/tests/fixtures/smoke_test_specimen.svg).
2. Chạy lệnh kiểm thử độc lập:
   ```powershell
   python -m unittest tests/test_hardware_adapter.py
   ```
3. Đánh giá chất lượng nét vẽ trên giấy thật:
   - Khung viền A4: Đo khoảng cách 4 lề bằng thước kẻ cơ học ($\pm 0.5\text{ mm}$ là đạt chuẩn).
   - Nét sóng Bézier: Không bị gãy khúc, không có hiện tượng giật cục bước động cơ.
   - Dòng chữ "OmniDraw": Nét đơn sắc sảo, đầu nét và đuôi nét không bị đọng mực giọt.
   - Tam giác đích sau bước nhấc bút dài: Điểm hạ ngòi chuẩn xác tại tọa độ $(250, 170)$, không bị mất bước (step loss).

---

## 6. Calibration Profile YAML

File cấu hình hiệu chuẩn: [`config/calibration_profile.yaml`](file:///d:/UED/NCKH/OmniDraw/config/calibration_profile.yaml)

- Chứa đầy đủ: phiên bản, thiết bị, khổ/hướng giấy, gốc tọa độ + offset 5 mm, tốc độ, gia tốc, servo bút.
- Được nạp tự động bởi `MockSimulatorAdapter` và `AxiDrawAdapter` khi khởi tạo.
- Để áp dụng profile tùy chỉnh: `adapter.load_profile("path/to/custom.yaml")`.

**Phân biệt gốc tọa độ và offset an toàn:**
- `(0,0)` cơ học của AxiDraw = góc trên-trái bàn vẽ.
- `origin.x_mm = 5`, `origin.y_mm = 5` = điểm `(0,0)` logic của SVG trên giấy (biên an toàn 5 mm).
- SVG viewBox tọa độ `(0,0)` tương ứng vật lý với `(5mm, 5mm)` trên mặt bàn.

---

## 7. Ghi nhận Metrics Hardware (Metric Logging)

File log: `logs/hardware_metrics.csv`

Columns: `request_id, timestamp, actual_draw_time_sec, estimated_draw_time_sec, is_simulated, hardware_status, source_tag`

**Quy tắc sử dụng trong báo cáo NCKH (Data Integrity):**

| `source_tag` | `is_simulated` | `actual_hardware_measured` | Dùng trong phân tích vật lý NCKH? |
|---|---|---|---|
| `simulator` | True | False | ❌ Không — thời gian ảo mô phỏng phần mềm |
| `axidraw_fake_driver` | True | False | ❌ Không — môi trường CI test |
| `axidraw_real` | False | True | ✅ Có — số đo thực tế từ thiết bị vật lý |

---

## 8. Kiểm tra Camera Thực tế

> ⚠️ **Cảnh báo:** `python backend/camera_inspector.py --self-check` dùng ảnh tổng hợp
> (synthetic image). Lệnh này **KHÔNG xác nhận webcam thật hoạt động.**

### Quy trình kiểm tra camera thực tế (blocked by hardware):
```powershell
# Bước 1: Kiểm tra nhận diện OS
python -c "import cv2; cap=cv2.VideoCapture(0); print('Camera OK:', cap.isOpened()); cap.release()"

# Bước 2: Chụp ảnh thật trực tiếp từ webcam
python backend/camera_inspector.py --capture --output logs/camera_test.jpg

# Bước 3: Xác nhận bằng mắt — 4 góc A4 phải nằm trong khung hình
```

---

## 9. Phối hợp TV3 → TV4 (Đề xuất cần thống nhất)

| Mục | Nội dung đề xuất | Endpoint chuẩn (theo API Spec v1.4) | Trạng thái |
|-----|-----------------|--------------------------------------|------------|
| API response pause | Thêm `"pause_supported": false` khi chạy máy thật | `POST /api/print/pause` | Chờ TV4 review |
| progress trung gian | `"progress_is_estimated": true` trong status response | `GET /api/print/status/{request_id}` | Đã implement |
| CSV schema mở rộng | Thêm `svg_path, profile_version, coord_error_mean_mm, pass_fail` | N/A (file CSV) | Chờ TV4 thống nhất |
| Cảnh báo UI | Hiển thị cảnh báo khi pause trên máy thật | Frontend Confirm/Printing Screen | Chờ TV4 implement |

---

## 10. CLI Smoke Test Tự động của TV3

TV3 cung cấp script CLI tích hợp sẵn để kiểm tra vòng đời phần cứng và adapter mà không phụ thuộc backend:

```powershell
# Chạy mô phỏng Simulator
python backend/hardware_adapter.py --smoke-test --mode simulator

# Chạy với Fake Driver (kiểm tra điều khiển ngắt/pause như máy thật trong CI)
python backend/hardware_adapter.py --smoke-test --mode fake

# Chạy với Máy vẽ AxiDraw thật (khi có thiết bị cắm vào cổng USB)
python backend/hardware_adapter.py --smoke-test --mode physical
```

