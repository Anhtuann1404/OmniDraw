# TV2 — Review giả định chuyển động và đo thời gian phần cứng

```text
REVIEWER_ROLE: TV2 — Stroke Optimization & Path Planning Lead
REVIEW_TARGET_COMMIT: 7d1c1d3b7388ce3ff76dd823c19bd8607f994d19
HARDWARE_RECHECK_COMMIT: f41bb20 (integration snapshot containing 4f7c978980892bf8efc8e5d7664dca76db52d65e)
REVIEW_DATE: 2026-09-25
WORKFLOW_STATUS: CHANGES_REQUESTED
VERDICT: PASS_WITH_CHANGES
TV2_APPROVAL: CHANGES_REQUIRED
```

## 1. Phạm vi đã kiểm tra

- `backend/hardware_adapter.py`
- `config/calibration_profile.yaml`
- `docs/hardware/measurement-protocol.md`
- `docs/hardware/07_physical_calibration_protocol.md`
- `tests/fixtures/rq3_clearance_calibration_specimen.svg`
- `tests/test_hardware_adapter.py`

Không có file hardware hoặc calibration nào được sửa trong review này.

## 2. Kết luận theo yêu cầu TV3

1. `25 mm/s` pen-down, `75 mm/s` pen-up, `accel_pct=75` và delay `120/100 ms` có thể dùng làm cấu hình mô phỏng ban đầu. Đây là provisional configuration, không phải giá trị đã hiệu chuẩn trên máy thật.
2. Công thức hiện tại có pen-down distance, pen-up distance, vận tốc và thời gian nâng/hạ bút, nhưng chưa mô hình hóa acceleration/deceleration hoặc corner slowdown.
3. Simulator/fake/real đã được phân biệt bằng `is_simulated`, `actual_hardware_measured` và `source_tag`. Không được dùng `actual_draw_time_sec` của simulator/fake như số đo vật lý.
4. Metrics hiện chưa đủ cho phân tích chuyển động vì benchmark trả `draw_distance_mm`, `penup_distance_mm`, `pen_lift_count` nhưng job không ghi các trường này; CSV cũng chưa lưu motion profile và breakdown cần tái lập.
5. Bộ góc danh nghĩa `60°/90°/120°/150°` phù hợp về mặt thiết kế thí nghiệm, nhưng geometry hiện tại trong fixture không tạo đúng các thay đổi hướng được ghi nhãn.
6. Trước khi chạy máy thật cần sửa specimen, khóa định nghĩa góc, bổ sung estimate breakdown và metadata calibration/motion vào output.

Review motion `TV2-HW-R01–R06` là lớp kiểm tra bổ sung. Nó không thay thế contract CSV mở rộng hoặc quyết định `pause_supported` mà TV3 đã gửi TV4; hai hạng mục đó vẫn `CHANGES_REQUIRED` và do TV3/TV4 xử lý.

## 3. Findings

| ID | Severity | Bằng chứng | Finding | Thay đổi yêu cầu |
| :--- | :---: | :--- | :--- | :--- |
| TV2-HW-R01 | MAJOR | `backend/hardware_adapter.py::estimate_svg_draw_time()`; `docs/hardware/measurement-protocol.md` §7 | Mô hình chỉ dùng vận tốc không đổi: $L_{down}/v_{down}+L_{up}/v_{up}+N_{lift}(t_{down}+t_{up})$. `accel_pct` và góc cua không tham gia phép tính. | Trước calibration, gọi rõ đây là `constant-speed baseline` và ghi cờ `accel_model_applied=false`, `corner_model_applied=false`. Sau khi đo được gia tốc theo `mm/s²`, dùng profile tam giác/thang theo từng segment; corner penalty phải fit từ dữ liệu thật. |
| TV2-HW-R02 | MAJOR | `backend/hardware_adapter.py::run_rq3_calibration_benchmark()` | `draw_distance_mm`, `penup_distance_mm`, `pen_lift_count` được đọc từ status nhưng không được ghi vào job, nên có thể luôn là `None`. | Cho estimator trả breakdown có typed fields và chuyển nguyên vẹn vào job/status/benchmark result. |
| TV2-HW-R03 | MAJOR | `tests/fixtures/rq3_clearance_calibration_specimen.svg`, block B; `tests/test_hardware_adapter.py::test_rq3_benchmark_simulator_run` | Các path được gắn nhãn 60/90/120/150 nhưng hướng segment thực tế không khớp; test chỉ kiểm tra danh sách nhãn hard-code, không kiểm tra geometry. | Tạo lại path theo một định nghĩa góc duy nhất (`heading_change_deg` hoặc interior angle) và thêm test parse geometry để tính lại từng góc. |
| TV2-HW-R04 | MAJOR | Fixture block C; `docs/hardware/07_physical_calibration_protocol.md` §3.3 | Protocol mô tả chu kỳ 2 mm pen-down / 2 mm pen-up ở 20/40/60 mm/s, nhưng fixture hiện dùng các nét khoảng 5 mm, khoảng nhấc khoảng 4 mm và không tách ba dải tốc độ. | Đồng bộ fixture với protocol hoặc sửa protocol theo specimen thực; mỗi dải tốc độ phải có ID/metadata riêng và được chạy với profile tương ứng. |
| TV2-HW-R05 | MINOR | `record_metric()` và `docs/hardware/measurement-protocol.md` §3 | CSV 7 cột chưa đủ tái lập mô hình chuyển động. | Trước physical benchmark, thêm tối thiểu `profile_version`, device/model, pen-down/up speed, `accel_pct`, delays, draw/pen-up distances, lift count và model flags. |
| TV2-HW-R06 | MAJOR — OPEN (RESIDUAL) | `4f7c978:backend/hardware_adapter.py::AxiDrawAdapter.start_job()` khoảng dòng 1670–1718; `get_status()` khoảng dòng 1889–1931 | Recheck snapshot tích hợp `f41bb20` chứa `4f7c978`: phần khởi tạo đã được sửa đúng — job bắt đầu với `actual_hardware_measured=false` và worker chỉ ghi `true` trong payload `done` của lượt chạy physical thành công. Phần còn mở là `get_status()` vẫn tự tính lại cờ từ `_use_fake_driver`, terminal status và actual time, đồng thời lấy `source_tag` từ trạng thái adapter hiện tại, thay vì đọc provenance đã lưu trong job. Vì vậy provenance trả về chưa được bảo đảm bất biến theo chính lượt chạy. | Cho `get_status()` trả nguyên `job["actual_hardware_measured"]` và `job["source_tag"]` đã chốt khi job hoàn tất. Bổ sung test terminal physical job có provenance đã lưu, sau đó thay đổi/ngắt trạng thái kết nối và xác nhận status vẫn trả đúng provenance của job; giữ test physical failure/cancel luôn `false`. Không đóng toàn bộ R06 cho tới khi test này PASS. |

## 4. Công thức đề xuất

### Recheck phần mềm trên `a138e58637d2accbdeb78d25ec22d1a4650dee72`

Kết quả AI recheck ngày 2026-09-26: `PASS_WITH_CHANGES`; `TV2_APPROVAL: CHANGES_REQUIRED`. Giữ phần review gốc ở trên làm lịch sử. Bộ test `tests/test_hardware_adapter.py` chạy trên snapshot riêng: **42 passed in 16.70s**. Các test physical dùng mock driver; chưa có bằng chứng đo trên thiết bị thật.

| Finding | Kết luận recheck | Bằng chứng và phần còn mở |
| :--- | :--- | :--- |
| TV2-HW-R01 | `VERIFIED_CLOSED` | `backend/hardware_adapter.py::calculate_svg_draw_breakdown()` dòng 923–1043; protocol §7 ghi `constant_speed_baseline`, hai model flags `false`, phân biệt `accel_pct` với gia tốc vật lý. Test `test_calculate_svg_draw_breakdown_contract` PASS. |
| TV2-HW-R02 | `VERIFIED_CLOSED` | `MockSimulatorAdapter.start_job/get_status` và `AxiDrawAdapter.start_job/get_status` truyền draw/pen-up distances và lift count qua job/status; `run_rq3_calibration_benchmark()` dòng 2256–2258 đọc các trường này. Breakdown có các thành phần thời gian riêng. |
| TV2-HW-R03 | `VERIFIED_CLOSED` | SVG Block B đã tạo heading change 60/90/120/150 độ, mỗi segment 20 mm; test `test_specimen_fixture_block_b_exact_angles` tính lại từ tọa độ và PASS. |
| TV2-HW-R04 | `OPEN` | SVG Block C và test geometry đã xác nhận 3 ID tốc độ, 20 nét dài 2 mm và 19 khoảng pen-up dài 2 mm mỗi dải. Tuy nhiên `run_rq3_calibration_benchmark()` dòng 2238–2239 chỉ gọi một job cho toàn bộ SVG, dùng một profile; không chọn từng band hoặc đổi vận tốc 20/40/60 mm/s. Nhãn SVG không điều khiển tốc độ driver. Cần tách từng band thành job/specimen riêng với profile tốc độ tương ứng, hoặc ghi rõ đây chỉ là template geometry và cung cấp protocol chạy riêng từng band. Test cần chứng minh các band thực sự được gửi với 3 cấu hình tốc độ tương ứng. |
| TV2-HW-R05 | `VERIFIED_CLOSED` | `HARDWARE_METRICS_FIELDNAMES` dòng 369–394 và protocol §3 cùng schema 22 trường: 9 trường core + 13 trường motion/profile/model. `record_metric()` ghi các trường mở rộng; migration và test CSV/provenance chạy PASS. Review này chưa thay thế phê duyệt contract tích hợp của TV4. |
| TV2-HW-R06 | `VERIFIED_CLOSED` | `AxiDrawAdapter.get_status()` dòng 2038–2067 đọc cờ và source tag đã lưu trong job; khởi tạo vẫn false, worker chỉ chốt true cho physical success. Test `test_completed_physical_job_provenance_immutability_on_disconnect` và các test failure/cancel PASS. |

TV3 cần xử lý residual R04; TV4 review contract CSV 22 trường và `pause_supported` trong PR hardware. Không đóng physical calibration hoặc formal experiment từ kết quả test này. Sign-off bên dưới là quyết định lịch sử, chưa phải human sign-off cho snapshot `a138e58`.

### Trước khi có dữ liệu hiệu chuẩn

Giữ công thức hiện tại nhưng ghi rõ là lower-order baseline:

$$
T_{const}=\frac{L_{down}}{v_{down}}+\frac{L_{up}}{v_{up}}+N_{lift}(t_{down}+t_{up}).
$$

Không suy gia tốc vật lý từ `accel_pct`; đây là driver setting, không có đơn vị $mm/s^2$.

### Sau khi đo được gia tốc vật lý

Với mỗi segment dài $d$, vận tốc trần $v$ và gia tốc đo được $a$:

- nếu $d \ge v^2/a$: $t=2v/a+(d-v^2/a)/v$;
- nếu $d < v^2/a$: $t=2\sqrt{d/a}$.

Phần góc cua dùng $t_{corner}(\theta)$ hoặc speed cap được fit từ các lượt đo specimen; không đặt hệ số tùy ý trước thực nghiệm.

## 5. Sign-off TV2

- **Verdict:** `PASS_WITH_CHANGES`
- **TV2_APPROVAL:** `CHANGES_REQUIRED`
- **Reviewer:** `Khải (TV2)`
- **Ngày:** `2026-09-25`
- **Commit đã review:** `7d1c1d3b7388ce3ff76dd823c19bd8607f994d19`
- **Điều kiện recheck:** TV3 xử lý TV2-HW-R01–R06 hoặc ghi disposition rõ ràng; TV2 recheck trước khi dùng kết quả physical benchmark cho RQ3. Contract CSV mở rộng và `pause_supported` vẫn là các hạng mục `CHANGES_REQUIRED` riêng của TV3/TV4.
