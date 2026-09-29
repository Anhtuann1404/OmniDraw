# Biên bản Kiểm tra Sẵn sàng Thao tác RQ3 (RQ3 Hardware Preflight Report)

**Vai trò thực hiện:** TV3 — Hardware, Calibration & Physical Validation Lead  
**Mục tiêu:** Kiểm tra sẵn sàng toàn diện luồng thi công tiêu bản RQ3 trên môi trường Simulator / Fake Driver trong lúc chờ nhận bàn giao máy vẽ AxiDraw vật lý và cáp USB.  
**Mã tài liệu:** `docs/hardware/08_rq3_preflight_report.md`  
**Ngày thực hiện:** 29/09/2026  
**Trạng thái kiểm chuẩn:** `PREFLIGHT VERIFIED (SOFTWARE / SIMULATOR / FAKE)`  
**Cổng đo lường vật lý:** `PENDING_TV3_CALIBRATION` (Bắt buộc phải có máy thật và cáp USB để đóng cổng).

---

## 1. Mục đích & Nguyên tắc Preflight

Nhằm bảo đảm không xảy ra bất kỳ gián đoạn kỹ thuật nào khi thiết bị máy vẽ AxiDraw về tới bàn làm việc, TV3 tiến hành chạy diễn tập toàn bộ chu trình kiểm chuẩn RQ3 trên hai môi trường giả lập (`simulator` và `fake driver`).

### Nguyên tắc bất biến:
1. **Phân tách rạch ròi dữ liệu:** Mọi số liệu sinh ra từ simulator hoặc fake driver đều mang nhãn `is_simulated = True`, `actual_hardware_measured = False`, và `physical_speed_status = "UNVERIFIED"`. Tuyệt đối không đưa số đo thời gian giả lập vào phân tích vật lý của bài báo NCKH.
2. **Không tự đóng gate:** Biên bản này xác nhận phần mềm, driver ảo, CLI runner, SVG specimen và tài liệu đã sẵn sàng 100%; cổng `PENDING_TV3_CALIBRATION` vẫn giữ nguyên trạng thái chờ máy thật.

---

## 2. Nhật ký Thực thi Lệnh & Kết quả Diễn tập

Toàn bộ các lệnh sau đã được chạy trực tiếp trên nhánh `feature/hardware` tại commit `796e918`:

### 2.1. Smoke Test Vòng đời (start → pause → resume → done)

#### A. Simulator Mode:
```powershell
python backend/hardware_adapter.py --smoke-test --mode simulator
```
- **Kết quả:** `[PASS] Bản vẽ hoàn tất thành công 100%!`
- **Telemetry:** `actual_draw_time_sec: 87.82s`, `is_simulated: True`, `actual_hardware_measured: False`, `source_tag: simulator`.
- **Hành vi Pause/Resume:** Tạm dừng và tiếp tục thành công, job chuyển tuần tự qua `printing` $\rightarrow$ `paused` $\rightarrow$ `printing` $\rightarrow$ `done`.

#### B. Fake Driver Mode:
```powershell
python backend/hardware_adapter.py --smoke-test --mode fake
```
- **Kết quả:** `[PASS] Bản vẽ hoàn tất thành công 100%!`
- **Telemetry:** `actual_draw_time_sec: 0.202s`, `is_simulated: True`, `actual_hardware_measured: False`, `source_tag: axidraw_fake_driver`.
- **Hành vi Ngắt An toàn:** Điều khiển ngắt luồng qua `threading.Event` chuẩn xác, không tự ý công bố `done` khi đang pause.

---

### 2.2. Benchmark Tự động Tiêu bản RQ3 (`--benchmark-rq3`)

Tiêu bản kiểm chuẩn: `tests/fixtures/rq3_clearance_calibration_specimen.svg`

#### A. Simulator Mode:
```powershell
python backend/hardware_adapter.py --benchmark-rq3 --mode simulator
```
- **Trạng thái:** `status: done`
- **Request ID tổng hợp:** `rq3-composite-1790669303164`
- **Phân tách 3 dải vận tốc (3 distinct jobs):**
  1. `rapid_pen_lift_20mms`: $v = 20.0\,\text{mm/s}$ (driver speed: $8\%$), job `rq3-bench-rapid_pen_lift_20mms-1790669303172`, $T_{sim} = 12.17\,\text{s}$, `is_simulated = True`, `actual_hardware_measured = False`.
  2. `rapid_pen_lift_40mms`: $v = 40.0\,\text{mm/s}$ (driver speed: $16\%$), job `rq3-bench-rapid_pen_lift_40mms-1790669304047`, $T_{sim} = 11.22\,\text{s}$, `is_simulated = True`, `actual_hardware_measured = False`.
  3. `rapid_pen_lift_60mms`: $v = 60.0\,\text{mm/s}$ (driver speed: $24\%$), job `rq3-bench-rapid_pen_lift_60mms-1790669304858`, $T_{sim} = 11.21\,\text{s}$, `is_simulated = True`, `actual_hardware_measured = False`.
- **Ranh giới tiêu bản:**
  - `block_a_clearance_ladder_tested: False`
  - `block_b_acute_turns_tested: False`
  - `block_c_rapid_pen_lift_tested: True`
  - `fixture_clearance_ladder_available_mm: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]`
  - `fixture_acute_turn_angles_available_deg: [60, 90, 120, 150]`

#### B. Fake Driver Mode:
```powershell
python backend/hardware_adapter.py --benchmark-rq3 --mode fake
```
- **Trạng thái:** `status: done`
- **Request ID tổng hợp:** `rq3-composite-1790669311985`
- **Phân tách 3 dải vận tốc (3 distinct jobs):**
  1. `rapid_pen_lift_20mms`: $v = 20.0\,\text{mm/s}$ ($8\%$), job `rq3-bench-rapid_pen_lift_20mms-1790669311986`, thời gian test CI $0.202\,\text{s}$.
  2. `rapid_pen_lift_40mms`: $v = 40.0\,\text{mm/s}$ ($16\%$), job `rq3-bench-rapid_pen_lift_40mms-1790669312244`, thời gian test CI $0.203\,\text{s}$.
  3. `rapid_pen_lift_60mms`: $v = 60.0\,\text{mm/s}$ ($24\%$), job `rq3-bench-rapid_pen_lift_60mms-1790669312491`, thời gian test CI $0.203\,\text{s}$.
- **Telemetry:** `source_tag = "axidraw_fake_driver"`, `is_simulated = True`, `actual_hardware_measured = False`, `physical_speed_status = "UNVERIFIED"`.

---

### 2.3. Kiểm thử Toàn bộ Test Suite

- **Test Suite Hardware Adapter:**
  ```powershell
  python -m pytest -q tests/test_hardware_adapter.py
  ```
  **Kết quả:** `59 passed in 12.43s` (100% PASS).
- **Toàn bộ Test Suite Repository:**
  ```powershell
  python -m pytest -q
  ```
  **Kết quả:** `185 passed in 19.57s` (100% PASS).

---

## 3. Mẫu Dữ liệu Đầu ra CSV (25 Trường Canonical)

Các dòng telemetry được tự động bổ sung vào `logs/hardware_metrics.csv` sau lượt chạy preflight:

```csv
request_id,timestamp,actual_draw_time_sec,estimated_draw_time_sec,is_simulated,actual_hardware_measured,hardware_status,error_code,source_tag,profile_version,device_model,speed_pendown_mm_s,speed_penup_mm_s,accel_pct,pen_delay_down_ms,pen_delay_up_ms,draw_distance_mm,penup_distance_mm,pen_lift_count,model_type,accel_model_applied,corner_model_applied,requested_speed_mm_s,driver_speed_pct,physical_speed_status
rq3-bench-rapid_pen_lift_20mms-1790669303172,2026-09-29T08:08:23.824128+00:00,12.17,12,True,False,done,,simulator,1.0,AxiDraw_V3,20.0,75.0,75.0,120.0,100.0,40.0,442.02,20,constant_speed_baseline,False,False,20.0,8,UNVERIFIED
rq3-bench-rapid_pen_lift_40mms-1790669304047,2026-09-29T08:08:24.715340+00:00,11.22,11,True,False,done,,simulator,1.0,AxiDraw_V3,40.0,75.0,75.0,120.0,100.0,40.0,442.02,20,constant_speed_baseline,False,False,40.0,16,UNVERIFIED
rq3-bench-rapid_pen_lift_60mms-1790669304858,2026-09-29T08:08:25.564991+00:00,11.21,11,True,False,done,,simulator,1.0,AxiDraw_V3,60.0,75.0,75.0,120.0,100.0,40.0,442.02,20,constant_speed_baseline,False,False,60.0,24,UNVERIFIED
rq3-bench-rapid_pen_lift_20mms-1790669311986,2026-09-29T08:08:32.222718+00:00,0.202,12,True,False,done,,axidraw_fake_driver,1.0,AxiDraw_V3,20.0,75.0,75.0,120.0,100.0,40.0,442.02,20,constant_speed_baseline,False,False,20.0,8,UNVERIFIED
rq3-bench-rapid_pen_lift_40mms-1790669312244,2026-09-29T08:08:32.463102+00:00,0.203,11,True,False,done,,axidraw_fake_driver,1.0,AxiDraw_V3,40.0,75.0,75.0,120.0,100.0,40.0,442.02,20,constant_speed_baseline,False,False,40.0,16,UNVERIFIED
rq3-bench-rapid_pen_lift_60mms-1790669312491,2026-09-29T08:08:32.704282+00:00,0.203,11,True,False,done,,axidraw_fake_driver,1.0,AxiDraw_V3,60.0,75.0,75.0,120.0,100.0,40.0,442.02,20,constant_speed_baseline,False,False,60.0,24,UNVERIFIED
```

### Điểm kiểm tra hợp đồng dữ liệu:
- Đủ chính xác 25 cột header theo `HARDWARE_METRICS_FIELDNAMES`.
- Phân định rõ 3 trường hợp đồng tốc độ driver:
  - `requested_speed_mm_s`: `20.0`, `40.0`, `60.0`
  - `driver_speed_pct`: `8`, `16`, `24`
  - `physical_speed_status`: `UNVERIFIED` (bảo vệ liêm chính NCKH)
- Cờ giả lập: `is_simulated = True`, `actual_hardware_measured = False`.
- Nguồn telemetry: `simulator` hoặc `axidraw_fake_driver`.

---

## 4. Kết quả Đối soát & Đồng bộ 3 Tài liệu Phần cứng

TV3 đã đối soát chéo 3 văn bản kỹ thuật:
1. `docs/hardware/calibration-checklist.md`
2. `docs/hardware/measurement-protocol.md`
3. `docs/hardware/07_physical_calibration_protocol.md`

| Hạng mục đối soát | Trạng thái trước đối soát | Điều chỉnh / Đồng bộ sau đối soát | Đánh giá |
| :--- | :--- | :--- | :---: |
| **Vật tư giấy vẽ** | Giấy in Double A A4 định lượng $80\,\text{g/m}^2$ | Thống nhất 100% trên cả 3 văn bản | ✅ KHỚP |
| **Bút vẽ tiêu chuẩn** | Bút bi gel Pentel EnerGel $0.5\,\text{mm}$ (đen) hoặc Pilot G2 $0.5\,\text{mm}$ | Thống nhất 100% trên cả 3 văn bản | ✅ KHỚP |
| **Góc gá & Lực ngòi** | Góc gá $90^\circ$ thẳng đứng; lực ngòi $50 - 80\,\text{gf}$ ($0.49 - 0.78\,\text{N}$) | Thống nhất 100% trên cả 3 văn bản | ✅ KHỚP |
| **Nguồn cấp điện** | Checklist ghi 9V/1.5A–2.1A; Protocol ghi 12V/2A | Cập nhật dải nguồn $9\text{V} - 12\text{V} / 1.5\text{A} - 2.1\text{A}$ trên `calibration-checklist.md` | ✅ ĐÃ SỬA |
| **Lệnh chạy Benchmark** | Checklist thiếu lệnh `--benchmark-rq3` | Bổ sung đầy đủ lệnh benchmark CLI vào Mục 10 của `calibration-checklist.md` | ✅ ĐÃ SỬA |
| **Tiêu bản Art Mode (Lượt 4)** | Measurement protocol ghi "Chờ TV2 cung cấp SVG" | Cập nhật ghi nhận đã nghiệm thu `output_tv2_art_mode_smoke.svg` từ TV2 | ✅ ĐÃ SỬA |
| **Số lượt lặp thực nghiệm** | 5 lượt end-to-end tích hợp vs. 3 lượt lặp kiểm chuẩn RQ3 | Phân định rõ: 5 lượt end-to-end cho luồng tích hợp hệ thống; tối thiểu 3 lượt lặp độc lập trên máy thật để đóng gate RQ3 | ✅ KHỚP |
| **Schema CSV** | 25 trường canonical | Khớp 100% với `HARDWARE_METRICS_FIELDNAMES` trong mã nguồn adapter | ✅ KHỚP |

---

## 5. Danh mục Thao tác Thực hiện Ngay khi Có Máy Vẽ & Cáp USB

Khi thiết bị máy vẽ AxiDraw và cáp USB được bàn giao, TV3 sẽ tiến hành tuần tự theo các bước thực chiến sau:

```text
[BƯỚC 1: Kiểm tra ngoại quan & Cắm cáp]
   ├── Kiểm tra khung nhôm, dây đai GT2 không bị chùng hay kẹt
   ├── Cắm nguồn 9V–12V vào bo mạch EBB (LED xanh sáng liên tục)
   └── Cắm cáp USB vào máy tính
       │
       ▼
[BƯỚC 2: Xác nhận nhận diện OS & Cổng COM]
   ├── Windows: Mở Device Manager → Ports (COM & LPT) → Ghi nhận COM port (ví dụ: COM3)
   ├── Cập nhật config/calibration_profile.yaml: device.port = "COM3" (hoặc auto-detect)
   └── Chạy kiểm tra kết nối qua Python interactive:
       python -c "from hardware_adapter import AxiDrawAdapter; ad = AxiDrawAdapter(use_fake_driver=False); print('Connected:', ad.connect())"
       │
       ▼
[BƯỚC 3: Gá đặt Giấy & Bút]
   ├── Dán phẳng giấy Double A A4 80gsm bằng băng dính giấy 4 góc
   ├── Gá bút Pentel EnerGel 0.5mm vuông góc 90° vào ngàm kẹp
   ├── Điều chỉnh đối trọng/lò xo đạt lực tì 60 ± 10 gf
   └── Cho máy về Home (origin 5mm offset an toàn)
       │
       ▼
[BƯỚC 4: Chạy Smoke Test Vật lý Thực tế]
   python backend/hardware_adapter.py --smoke-test --mode physical
   ├── Xác nhận nâng/hạ bút trơn tru, không cào giấy
   └── Kiểm tra 1 dòng telemetry ghi nhận source_tag='axidraw_real', actual_hardware_measured=True
       │
       ▼
[BƯỚC 5: Chạy Benchmark RQ3 Vật lý Tự động (Ít nhất 3 lượt lặp)]
   python backend/hardware_adapter.py --benchmark-rq3 --mode physical
   ├── Quan sát 3 dải Khối C thi công tại 3 cao độ Y (172, 180, 188 mm)
   ├── Kiểm tra không bị mất bước (step loss) ở v=60mm/s
   └── Ghi nhận 3 dòng telemetry vật lý vào logs/hardware_metrics.csv
       │
       ▼
[BƯỚC 6: Để khô 15 phút, Quét phẳng 600 DPI & Đo đạc Quang học]
   ├── Quét phẳng 600 DPI lossless PNG
   ├── Đo bề rộng nét w_ink và khoảng hở d_actual trên Khối A
   └── Đánh giá tiêu chuẩn đóng gate theo §5 của docs/hardware/07_physical_calibration_protocol.md
       │
       ▼
[BƯỚC 7: Nghiệm thu & Chuyển trạng thái PASS_TV3_CALIBRATION]
```

---

## 6. Kết luận Preflight

1. **Toàn bộ hệ thống phần mềm, CLI runner, SVG specimens và hợp đồng dữ liệu của TV3 đã hoàn toàn sẵn sàng.**
2. **Quá trình preflight trên Simulator và Fake Driver diễn ra hoàn hảo**, chứng minh tính đúng đắn của logic dispatch 3 jobs độc lập, hợp đồng đơn vị tốc độ driver, và cơ chế bảo vệ an toàn khi dừng/ngắt.
3. **Cổng đo lường vật lý tiếp tục được duy trì nghiêm ngặt ở trạng thái `PENDING_TV3_CALIBRATION`** cho đến khi hoàn tất Bước 5–7 trên máy thật.
