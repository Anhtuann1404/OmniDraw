# OmniDraw — TV3 Measurement Protocol & Experimental Handoff
# ===========================================================
# Phiên bản: v1.0 (21/09/2026)
# Tác giả: TV3 — Hardware, Calibration & Physical Validation Lead
# Trạng thái: DRAFT — chờ setup phần cứng để thực thi đo đạc thực tế

---

## 1. Phân biệt Thời gian Mô phỏng và Thời gian Thực tế

| Trường | Nguồn | is_simulated | actual_hardware_measured | actual_draw_time_sec | error_code | Dùng trong phân tích NCKH? |
|--------|-------|--------------|--------------------------|----------------------|------------|----------------------------|
| `estimated_draw_time_sec` | Tính toán từ hình học SVG | True/False | False | — | rỗng | Baseline đối chứng thời gian ước lượng |
| `actual_draw_time_sec` (simulator) | asyncio wall-clock (MockSimulatorAdapter) | True | False | Số đo ảo | rỗng | ❌ **KHÔNG** đưa vào phân tích vật lý |
| `actual_draw_time_sec` (fake driver) | threading giả lập CI (_FakeAxiDrawDriver) | True | False | Số đo CI | rỗng | ❌ **KHÔNG** đưa vào phân tích vật lý |
| `actual_draw_time_sec` (AxiDraw thật - Thành công) | Wall-clock đo từ lúc motor kéo nét tới lúc về gốc | False | True | Thời gian thực đo (> 0) | rỗng | ✅ **DÙNG** làm số liệu thực nghiệm chính thức |
| `actual_draw_time_sec` (AxiDraw thật - Thất bại/Mất kết nối) | Ngắt kết nối/ngoại lệ phần cứng | False | False | **Rỗng (None)** (không điền 0 hay timing giả) | `HARDWARE_NOT_CONNECTED` / `HARDWARE_ERROR` | ❌ Số liệu lỗi; dùng kiểm toán độ tin cậy hệ thống |

> **Quy tắc bắt buộc (NCKH Research Data Integrity):**
> - Cột `source_tag` trong CSV phân biệt 3 loại nguồn: `simulator`, `axidraw_fake_driver`, `axidraw_real`.
> - Cột `actual_hardware_measured` **chỉ được phép bằng `True`** khi job trên phần cứng thật hoàn tất thành công (`status == "done"`) và có thời gian thực đo hợp lệ ($> 0$).
> - Physical thất bại/mất kết nối phải ghi `is_simulated = False`, `actual_hardware_measured = False`, và `actual_draw_time_sec` để trống (None / `""`), tuyệt đối không ghi timing giả hoặc thay bằng `0`.
> - Nếu request chủ đích là `physical`, hệ thống tuyệt đối không âm thầm fallback sang `simulator`.

---

## 2. Mốc Bắt đầu / Kết thúc Đo

| Sự kiện | Mốc đo | Ghi chú |
|---------|--------|---------|
| **T_start** | Thời điểm `plot_run()` được gọi (sau `plot_setup()`) | Không tính thời gian chuẩn bị/kết nối |
| **T_end** | Thời điểm `plot_run()` trả về (bao gồm về gốc) | Bao gồm thời gian nâng bút và về (0,0) |
| **T_pause** | Tích lũy `elapsed_before_pause` | Simulator & fake driver hỗ trợ; physical trả về `HARDWARE_PAUSE_UNSUPPORTED` |
| **T_setup** | Không tính vào actual_draw_time_sec | plot_setup là đọc file, không điều khiển cơ học |

---

## 3. Schema Chuẩn Ghi Kết quả Thực nghiệm (9 Cột)

File: `logs/hardware_metrics.csv` (lưu riêng, không gộp schema vào experiment CSV; dùng `request_id` làm khóa liên kết).

```csv
request_id,timestamp,actual_draw_time_sec,estimated_draw_time_sec,is_simulated,actual_hardware_measured,hardware_status,error_code,source_tag
```

Chi tiết các trường:
1. `request_id`: Mã định danh duy nhất của tác vụ in (khóa liên kết dữ liệu với pipeline thí nghiệm).
2. `timestamp`: Thời gian ghi nhận theo chuẩn ISO 8601 UTC.
3. `actual_draw_time_sec`: Thời gian thi công thực tế (giây). Chỉ có giá trị khi `status == "done"`; nếu thất bại để rỗng (`""`), không thay bằng 0.
4. `estimated_draw_time_sec`: Thời gian dự tính từ mô hình hình học SVG (giây).
5. `is_simulated`: `True` nếu chạy qua simulator hoặc fake driver; `False` nếu chạy trên driver vật lý thật.
6. `actual_hardware_measured`: `True` duy nhất khi physical job hoàn tất thành công và có số đo thực tế $> 0$; tất cả các trường hợp khác (kể cả lỗi physical) đều bằng `False`.
7. `hardware_status`: Trạng thái kết thúc của thiết bị (`done`, `error`, `cancelled`).
8. `error_code`: Mã lỗi chuẩn (ví dụ: `HARDWARE_NOT_CONNECTED`, `HARDWARE_ERROR`, `HARDWARE_PAUSE_UNSUPPORTED`), để rỗng nếu thành công.
9. `source_tag`: Gắn nhãn nguồn thiết bị (`simulator`, `axidraw_fake_driver`, `axidraw_real`).

---

## 4. Protocol Đo Sai số Tọa độ

*(Blocked by hardware — cần camera và máy thật)*

### Bước chuẩn bị:
1. In `tests/fixtures/smoke_test_specimen.svg` lên giấy A4.
2. Chụp ảnh top-down bằng webcam đã căn chỉnh.
3. Dùng `backend/camera_inspector.py --capture` để lưu ảnh.

### Đo sai số:
1. Dùng phần mềm đo ảnh (ImageJ / GIMP) hoặc script thước đo pixel-to-mm.
2. Đo khoảng cách từ 4 góc khung viền alignment_border đến mép giấy.
3. Đo vị trí tam giác penup_target_triangle tại (250, 170).
4. Ghi vào `logs/coord_error_log.csv` với format:
   `run_id, point_id, expected_x_mm, expected_y_mm, measured_x_mm, measured_y_mm, error_mm`

### Ngưỡng pass/fail:
- Lề khung viền: `|đo - mong đợi| ≤ 0.5mm` → PASS
- Điểm hạ bút sau pen-up dài: `error ≤ 1.0mm` → PASS (step loss)

---

## 5. Protocol 5 Lượt End-to-End

*(Phối hợp với TV4 — cần environment simulator hoặc máy thật)*

Mỗi lượt chạy theo quy trình:
1. TV4 gọi POST `/api/print/start` với SVG đầu vào khác nhau.
2. TV3 ghi `request_id`, `svg_path`, thời gian bắt đầu.
3. Polling `GET /api/print/status/{request_id}` mỗi 1s cho đến khi done/error.
4. Ghi `actual_draw_time_sec`, `estimated_draw_time_sec`, `source_tag` vào CSV.

5. (Khi có máy) Chụp ảnh, đo sai số tọa độ.

| Lượt | SVG đầu vào | Mode | Kết quả | Ghi chú |
|------|------------|------|---------|---------|
| 1 | smoke_test_specimen.svg | simulator | PASS (CLI `--mode simulator`) | Đã hoàn thành qua CLI smoke-test |
| 2 | bezier_length_test.svg | simulator | PASS (Pytest Suite) | Đã hoàn thành qua Pytest |
| 3 | smoke_test_specimen.svg | fake | PASS (CLI `--mode fake`) | Đã hoàn thành (kiểm chứng ngắt/pause an toàn) |
| 4 | (art mode output từ TV2) | simulator | Chờ TV2 cung cấp SVG | Sẵn sàng chạy khi TV2 chuyển giao SVG |
| 5 | smoke_test_specimen.svg | axidraw_real | **BLOCKED BY HARDWARE** | Chờ máy vẽ & cáp vật lý sẵn sàng |

---

## 6. Kiểm tra Camera Thực tế

> **Sửa checklist cũ:** `python backend/camera_inspector.py --self-check` dùng ảnh
> tổng hợp (synthetic) — KHÔNG xác nhận webcam thật hoạt động.

### Quy trình kiểm tra camera thực tế:
```powershell
# Bước 1: Kiểm tra camera nhận diện OS
python -c "import cv2; cap=cv2.VideoCapture(0); print('Camera OK:', cap.isOpened()); cap.release()"

# Bước 2: Chụp ảnh thật trực tiếp từ webcam và lưu file
python backend/camera_inspector.py --capture --output logs/camera_test.jpg

# Bước 3: Xác nhận ảnh không bị mờ và bao quát A4
# Mở ảnh và kiểm tra bằng mắt: 4 góc giấy phải nằm trong khung hình.
```

> **Trạng thái:** BLOCKED BY HARDWARE — cần kết nối webcam vật lý.

---

## 7. Bàn giao TV3 → TV2 & TV4

### Giả định TV3 về vận tốc / gia tốc (để TV2 dùng trong mô hình chi phí):

| Tham số | Giá trị (Art Mode) | Giá trị (Handwriting) | Nguồn |
|---------|-------------------|----------------------|-------|
| Vận tốc pen-down | 40 mm/s | 25 mm/s | Calibration profile v1.0 |
| Vận tốc pen-up | 75 mm/s | 75 mm/s | Calibration profile v1.0 |
| Gia tốc | 75% driver max | 75% driver max | Calibration profile v1.0 |
| Trễ hạ bút | 120 ms | 120 ms | Calibration profile v1.0 |
| Trễ nâng bút | 100 ms | 100 ms | Calibration profile v1.0 |

### Mô hình thời gian (TV3 → TV2 & TV4):

```
T_est = L_pendown / v_pendown + L_penup_real / v_penup + N_lifts × (delay_down + delay_up) / 1000
```

Trong đó:
- $L_{\text{pendown}}$: Tổng chiều dài hình học nét vẽ (Bézier cubic/quadratic, Arc A/a, đường thẳng L/H/V, ClosePath Z).
- $L_{\text{penup\_real}}$: Quãng đường di chuyển nhấc bút thực tế nối giữa điểm kết thúc của nét trước tới điểm bắt đầu của nét sau (và từ gốc $(0,0)$ tới nét đầu, từ nét cuối về $(0,0)$).
- $N_{\text{lifts}}$: Số lần nhấc/hạ ngòi bút thực tế.

### Giới hạn phần cứng TV3 & Hợp đồng Tích hợp TV4:
- **Tính năng tạm dừng (pause_supported):**
  - Simulator & Fake driver: `pause_supported: true` (hỗ trợ ngắt an toàn và tiếp tục nét vẽ).
  - Máy vật lý AxiDraw thật: `pause_supported: false` (chưa xác minh cơ chế ngắt khẩn cấp an toàn giữa chừng nét vẽ trong pyaxidraw).
  - **Quy tắc an toàn phần cứng:** Adapter kiểm tra capability trước khi đổi trạng thái. Khi chạy máy thật, tuyệt đối không chuyển job sang `paused`; trạng thái giữ nguyên `printing`.
  - Trả lỗi có cấu trúc HTTP 400:
    ```json
    {
      "error": {
        "code": "HARDWARE_PAUSE_UNSUPPORTED",
        "message": "AxiDraw phần cứng chưa hỗ trợ hoặc chưa xác minh tính năng tạm dừng (pause) an toàn giữa chừng"
      },
      "pause_supported": false,
      "status": "printing"
    }
    ```
  - Đồng nhất trường `pause_supported` trong toàn bộ response của `start_job`, `get_status`, `pause_job`, `resume_job`.
- **Tiến độ giữa chừng (progress_percent):**
  - Trên máy thật là ước lượng dựa trên thời gian hình học.
  - Luôn đi kèm cờ `"progress_is_estimated": true` trong response của `GET /api/print/status/{request_id}`.
- **Phát hiện lỗi phần cứng:**
  - Chưa có cảm biến phần cứng (kẹt giấy, hết mực), không giả lập dữ liệu sai lệch. Khi mất kết nối hoặc ngoại lệ, trả mã lỗi chuẩn `HARDWARE_NOT_CONNECTED` hoặc `HARDWARE_ERROR`.

### Trạng thái review chéo & Bàn giao TV4:
- [x] Schema `logs/hardware_metrics.csv` 9 cột chuẩn hóa với `actual_hardware_measured` và `error_code`.
- [x] Quy tắc toàn vẹn dữ liệu: `actual_hardware_measured=True` chỉ khi máy thật hoàn tất thành công; lỗi ghi nhận trống timing và mã lỗi rõ ràng.
- [x] Capability `pause_supported` đồng nhất; từ chối an toàn với mã `HARDWARE_PAUSE_UNSUPPORTED`, không đổi sai trạng thái job.
- [x] Bộ testsuite tích hợp 32 test unit/integration PASS 100%.

---

## 8. Checklist Thao tác Khi Có Máy Thật

- [ ] Kết nối cáp USB AxiDraw → PC, xác nhận COM port trong Device Manager.
- [ ] Cập nhật `config/calibration_profile.yaml`: đặt `device.port` đúng COM port.
- [ ] Chạy `python -m pytest tests/test_hardware_adapter.py -v` → tất cả PASS.
- [ ] Gọi `adapter = AxiDrawAdapter(); adapter.connect()` → xác nhận `is_connected=True`.
- [ ] Chạy smoke test vật lý: `python backend/hardware_adapter.py` (cần thêm __main__ block).
- [ ] Lưu log vào `logs/smoke_test_YYYYMMDD.csv`.
- [ ] Chụp ảnh kết quả, đo sai số tọa độ, ghi vào `logs/coord_error_log.csv`.
- [ ] Cập nhật `calibration_profile.yaml`: `verified_on_hardware: true`.
- [ ] Cập nhật `docs/04_progress-log.md` với kết quả smoke test.
- [ ] Bàn giao số liệu cho TV4 để tổng hợp báo cáo.
