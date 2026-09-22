# OmniDraw — TV3 Measurement Protocol & Experimental Handoff
# ===========================================================
# Phiên bản: v1.0 (21/09/2026)
# Tác giả: TV3 — Hardware, Calibration & Physical Validation Lead
# Trạng thái: DRAFT — chờ setup phần cứng để thực thi đo đạc thực tế

---

## 1. Phân biệt Thời gian Mô phỏng và Thời gian Thực tế

| Trường | Nguồn | is_simulated | actual_hardware_measured | Dùng trong phân tích học thuật NCKH? |
|--------|-------|--------------|--------------------------|-------------------------------------|
| `estimated_draw_time_sec` | Tính toán từ hình học SVG | True/False | False | Chỉ dùng làm baseline đối chứng thời gian ước lượng |
| `actual_draw_time_sec` (simulator) | asyncio wall-clock (MockSimulatorAdapter) | True | False | ❌ **KHÔNG** đưa vào bảng số liệu vật lý thực nghiệm |
| `actual_draw_time_sec` (fake driver) | threading giả lập CI (_FakeAxiDrawDriver) | True | False | ❌ **KHÔNG** đưa vào bảng số liệu vật lý thực nghiệm |
| `actual_draw_time_sec` (AxiDraw thật) | Wall-clock đo từ lúc motor bắt đầu kéo nét tới lúc về gốc | False | True | ✅ **DÙNG** làm số liệu thực nghiệm vật lý chính thức |

> **Quy tắc bắt buộc:** Cột `source_tag` trong CSV phân biệt 3 loại nguồn:
> - `simulator` → thời gian ảo mô phỏng phần mềm
> - `axidraw_fake_driver` → môi trường CI test (kiểm tra logic ngắt/pause không làm máy chuyển động)
> - `axidraw_real` → dữ liệu thực nghiệm vật lý hợp lệ cho bài báo NCKH


---

## 2. Mốc Bắt đầu / Kết thúc Đo

| Sự kiện | Mốc đo | Ghi chú |
|---------|--------|---------|
| **T_start** | Thời điểm `plot_run()` được gọi (sau `plot_setup()`) | Không tính thời gian chuẩn bị/kết nối |
| **T_end** | Thời điểm `plot_run()` trả về (bao gồm về gốc) | Bao gồm thời gian nâng bút và về (0,0) |
| **T_pause** | Tích lũy `elapsed_before_pause` | Hiện chỉ có trong simulator; thật chưa hỗ trợ |
| **T_setup** | Không tính vào actual_draw_time_sec | plot_setup là đọc file, không điều khiển cơ học |

---

## 3. Schema Mẫu Ghi Kết quả Thực nghiệm

File: `logs/hardware_metrics.csv`
Columns: `request_id, timestamp, actual_draw_time_sec, estimated_draw_time_sec, is_simulated, hardware_status, source_tag`

> **Đề xuất mở rộng cho TV4** (cần thống nhất trước khi sửa schema):
> Khi sẵn sàng đo sai số tọa độ, đề nghị thêm các cột:
> - `svg_path`: đường dẫn SVG đầu vào (để tái lập thực nghiệm)
> - `profile_version`: phiên bản calibration profile dùng
> - `coord_error_mean_mm`: sai số tọa độ trung bình (mm)
> - `coord_error_max_mm`: sai số cực đại
> - `pass_fail`: "PASS" | "FAIL" | "PENDING"
> - `notes`: ghi chú tự do

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

### Giới hạn phần cứng TV3 cần TV4 biết:
- Pause/resume thực sự: pyaxidraw hiện chưa có API ngắt khẩn cấp giữa nét và tiếp tục an toàn.
  → TV3 đã cấu hình: trên fake driver hỗ trợ pause/resume an toàn qua event; trên máy thật gửi lệnh an toàn và trả cờ `"pause_supported": false`.
  → Đề xuất TV4 cập nhật endpoint `POST /api/print/pause` và hiển thị thông báo cảnh báo trên UI.
- Tiến độ giữa chừng (progress_percent) trên máy thật chỉ là ước lượng dựa trên thời gian.
  → Đã bổ sung `"progress_is_estimated": true` trong response của `GET /api/print/status/{request_id}`.
- Phát hiện lỗi phần cứng (kẹt giấy, hết mực): CHƯA có nguồn tín hiệu cảm biến từ EBB firmware hiện hành.
  → Đang ghi nhận rõ rệt là giới hạn phần cứng, không tạo số liệu giả lập khi chưa có cảm biến thật.

  → Sẽ bổ sung sau khi nghiên cứu EBB firmware documentation.

### Trạng thái review chéo:
- [ ] TV3 chờ TV2 cung cấp feedback về giả định vận tốc/gia tốc.
- [ ] TV3 chờ TV4 thống nhất schema CSV mở rộng (xem đề xuất Section 3).
- [ ] TV3 chờ TV4 review cảnh báo pause_supported trong API response.
- [ ] TV3 → TV4: cần bổ sung `pause_supported: false` vào OmniDraw_API_Spec-4.md.

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
