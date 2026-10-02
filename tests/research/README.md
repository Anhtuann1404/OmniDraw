# Tests nghiên cứu hiện hành

| Test | Phạm vi |
|---|---|
| `test_api.py` | Gateway/adapter giả lập, không chứng minh thuật toán |
| `test_schedule_checker.py` | Ca kiểm tay thứ tự/hướng/deadline/chi phí và arithmetic fixture |
| `test_geometry.py` | Primitive TV4, floor .19/.20/.21, suy biến/self-cross/contact vùng hữu hạn |
| `test_joint_dp.py` | Ca kiểm tay optimum/infeasible/budget; no-forget so safe-forget trên seed cố định |
| `test_fixed_configuration.py` | Inner giữ lựa chọn/hash gốc; fixed infeasible khác full-set; budget/scope và min fixed so joint (TV4 consistency) |
| `test_dev_tools.py` | JSON/hash/trace/SVG geometry, no-overwrite và ranh giới imports |
| `test_cost_arithmetic.py` | Prefix rounding/cost tie, regret cancellation, finite enclosure, adjacent-float floor/contact; TV4 regression |
| `test_method_example.py` | Witness hai geometry/ba nét, bốn lịch tính tay, optimum fixed/joint và ca deadline k=0; không oracle độc lập |
| `test_vertex_analysis.py` | Schedule cố định, đối thủ full-set ở bốn đỉnh và incomplete không chứng nhận |

Fixtures `fixtures/replay_dev_cases.json` và `fixtures/solver_dev_cases.json` là dữ liệu DEV tự tạo, có manifest/candidate hashes thực. Không là dataset TV1 đã duyệt, HOLDOUT hay oracle độc lập. Geometry/checker/DP do TV4 viết cùng nhau; TV3 không dùng lại primitive để gọi là độc lập.

Đường dẫn đã chuyển:

- `tests/test_research_api.py` → `tests/research/test_api.py`.
- `tests/test_research_schedule_checker.py` → `tests/research/test_schedule_checker.py`.
- `tests/fixtures/research_tv4_dev.json` → `tests/research/fixtures/replay_dev_cases.json`.

Lệnh lịch sử trong progress-log/evidence thuộc checkout/commit lúc ghi; tra bảng này để chạy phiên bản hiện hành. Không tạo test wrapper để tránh pytest collect trùng. Tests sản phẩm PR3/CA-VHC và CAD/hardware vẫn ở chỗ cũ theo ownership.

`fixtures/method_gap_example.json` là witness synthetic hai owners/ba nét tự tạo TV4, hash thật; [tọa độ/phép tính/lệnh](../../docs/support/36_joint_method_and_dp_argument.md). Không glyph đọc được hoặc quality TV1 đã review; tests chỉ đối chiếu recurrence/replay TV4 với biểu thức tính tay cho witness.

`fixtures/numeric_rounding_cases.json` giữ hai counterexamples synthetic hash thật; [audit/giới hạn](../../docs/reviews/tv4_numeric_audit_20261002.md). Numeric/geometry policy và oracle acceptance vẫn PENDING; không dữ liệu máy/font/HOLDOUT.
