# TV4 — rà soát số học và đồng hạng trên DEV

Ngày 02/10/2026; nền trước sửa `289125a`, cùng core trước đó `bf68d0b`. Owner TV4; trạng thái **IMPLEMENTED_DEV_FIX / REVIEW_PENDING**, không là oracle độc lập, human sign-off hoặc numerical freeze. Nguồn: [Docs 31](../31_joint_solver_contract.md), [Docs 32](../32_research_api_and_artifact_contract.md), [lập luận](../support/36_joint_method_and_dp_argument.md). Phân công giữ nguyên, HOLDOUT đóng.

## Lỗi có counterexample

Trước sửa, DP cộng float mỗi delta và END rồi so `(cost,path_tie)`; replay fsum các coefficients rồi tính J. Làm tròn theo hai cách có thể khác nhau, dẫn tới chọn sai theo J xuất ra. [Manifest synthetic](../../tests/research/fixtures/numeric_rounding_cases.json) giữ hai ca hash thật; [tests](../../tests/research/test_cost_arithmetic.py) giữ công thức và lệnh tái lập. Các nét trừu tượng không là font/quality đã duyệt.

Ca hai owners:

- Owner 0 có v0: (0,0)→(.3,sqrt(.1125))→(.6,0), chiều dài float ≈.9; v1: (0,0)→(.6,0), chiều dài .6. Cả hai forward-only, cùng endpoint; v0 đứng trước lexicographic.
- Owner 1 cố định v0: (1,0)→(1.9,0), chiều dài float ≈.9; gap giữa owners ≥.4, không contact; mọi transition LIFT.
- p0=(0,0), p_end=(1.9,0), rho=1, lambda=2^53; L_up=.4, N_cycle=2. Tham số rất lớn là stress-test trên input hợp lệ, không đề xuất tham số máy/miền nghiệm thu.

| Trường | v0 dài | v1 ngắn |
|---|---|---|
| L_down replay | ≈1.8 | 1.5 |
| J replay trước sửa | 18014398509481988 | 18014398509481984 |
| DP trước sửa | Coi cost bằng nhau do làm tròn delta/prefix, chọn v0 theo tie | Có cost replay thấp hơn nhưng không được chọn |
| DP sau sửa | Giữ cost nội bộ lớn hơn | Chọn v1 cả no-forget/safe-forget, khớp inner fixed/replay |

Ca một owner bỏ owner 1 và p_end=(.6,0): cả hai J hiển thị cùng 2^53 nhưng cost nội bộ vẫn khác .3. Vì vậy không dùng equality của J đã làm tròn để định nghĩa tie hoặc compare_modes PASS. Diagnostic regret cần trừ các cost nội bộ trước round; nếu trừ hai J hiển thị sẽ báo 0 thay vì ≈.3.

## Sửa trong phạm vi TV4

`cost_arithmetic.py` khai báo **cost_policy_id=tv4-dev-dyadic-primitive-cost-v1**. Mỗi chiều dài nét được tính bằng fsum các math.dist segment và đã là binary64; mỗi UP dùng math.dist, theta là input binary64. Những giá trị này chuyển sang Fraction chính xác theo biểu diễn binary64; phép nhân rho, cộng cost và lambda*N_cycle giữ chính xác trong mô hình primitive đó. DP label/END và replay dùng cùng định nghĩa; J output round một lần. Có assertion exact DP–replay cho incumbent.

Tie **tv4-dev-dyadic-lex-actions-v2** chỉ so path_tie khi cost nội bộ thực sự bằng nhau trong policy này; replay version **dev-v3**, CLI runtime **2**. Equal displayed J có thể là hai objective khác nhau. `JointRun`/replay giữ objective_exact; JSON CLI ghi objective_exact_ratio dạng chuỗi, cost_policy_id trong config đã hash; SVG/vertex diagnostics ghi cost policy. No-forget/safe-forget CLI compare exact internal values, không dùng tolerance debug cũ.

CLI lower/upper bounds được làm tròn ra ngoài quanh objective primitive: min/max hai binary64 kề bao quanh Fraction. Lower chỉ có khi search complete, incumbent incomplete chỉ có upper. Khoảng này chỉ bao giá trị arithmetic của primitive float; không là biên sai số geometry/flatten hoặc numerical certificate thật. Overflow hoặc enclosure không có finite output bị từ chối, không xuất Infinity. Subnormal objective có thể hiển thị 0 nhưng ratio và enclosure giữ thông tin; trường hợp J_m hiển thị 0 vẫn không được tính gap theo schema hiện hành.

Geometry policy `tv4-dev-float-v1` giữ nguyên, floor .20 không trừ epsilon, CONNECT vẫn exact endpoint. Chưa chốt tolerance, epsilon_eq, rho/lambda miền chính thức hoặc gate numeric freeze. Cost policy DEV mới là thay đổi implementation có version cần owner review, không ký duyệt thay các TV. Runtime và config hashes phải được ghi; cùng candidate hash/theta chưa đủ để trộn số liệu giữa cost policies cũ/mới.

## Kiểm thử và giới hạn

```sh
PYTHONPATH=backend backend/venv/bin/python3 -m pytest tests/research/test_cost_arithmetic.py -q
```

17 tests: counterexamples một/hai owners và hai modes; tie thật dưới thay thứ tự variants; CLI cùng J hiển thị khác exact phải FAIL; regret không mất chênh lệch; underflow/overflow/enclosure finite; floor tại .20 và binary64 ngay dưới/trên; contact khác đúng một ULP không được snap. Tests cùng tác giả TV4, không thay oracle TV3. Kết quả suite đầy đủ ghi progress-log theo lệnh thực đã chạy.

Không chứng minh mọi primitive Euclid/segment/intersection/clip đều chính xác; stroke-length fsum và tọa độ đã round trước accumulator. Ca floor song song có đáp án tay không chứng minh geometry tổng quát hoặc c_min trên vùng mực. Fraction tăng thời gian/bộ nhớ mỗi label; budget guard giữ nguyên, cần scope/completion measurement trên DEV. path_tie/backpointer vẫn có overhead, slice này không hoàn tất cận bộ nhớ.

TV2 review cost-policy và tái lập baseline/ranking theo cùng primitive arithmetic hoặc khai báo policy khác, không ghép J/gap ngang phiên bản. TV3 xây phép kiểm độc lập từ định nghĩa/input thô, không import helper TV4 để gọi độc lập; kiểm geometry và sai số thật vẫn cần evidence. Q04/Q06/Q08/Q09/Q10/Q11 và sign-off còn PENDING; diagnostic bốn đỉnh vẫn NOT_CERTIFIED, API adapters vẫn chưa đăng ký.
