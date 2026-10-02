# Kế hoạch nghiên cứu và nghiệm thu

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API nghiên cứu](32_research_api_and_artifact_contract.md) là nguồn triển khai.

## Phạm vi hoàn thành tối thiểu

Hoàn thành mô hình ứng viên hữu hạn, DP một mục tiêu có kiểm chứng độc lập, staged top-m/beam, phân tích điều kiện có lợi/bằng nhau, độ nhạy hai tham số và gói tái lập. Kết quả bằng nhau vẫn có giá trị khi coverage và biên tương đương được khóa trước; kết quả thiếu coverage phải ghi chưa đủ bằng chứng.

## Kế hoạch chính thức

Dùng một bảng 8 tháng tại [Docs 30 §5](30_research_development_plan.md). Không có bảng 4 tháng song song. Thứ tự slice và cắt phạm vi ở Docs 30; backlog hiện tại ở Docs 03. Đọc và lập bảng toàn văn Balas/Balas–Simonetti có số trang trong tháng 1, chưa tuyên bố bài nào hỗ trợ cửa sổ riêng khi chưa đối chiếu.

## Trước Holdout

- TV1 lập split mới chưa dùng tinh chỉnh, chốt cỡ mẫu trong tháng 1, quản lý nhật ký truy cập; từ cũ trong repo chỉ bổ sung.
- TV3 oracle và primitive độc lập; random seed cố định và ca thật, giới hạn ca nhỏ theo Docs 31; không dùng Holdout để debug.
- TV2 đăng ký H_ref/H_geom, top-m/beam/budget/tie, unit từ cho thống kê và cách xử lý ca không đủ coverage.
- TV3 ưu tiên số đo sơ bộ thiết bị nếu có; nếu không dùng nguồn tham số/DEV protocol khai báo. rho0/lambda0 là điểm vận hành chính, sweep là kết quả bổ sung.
- TV4 cùng nhóm khóa code, candidate hash, parameters/c_min, epsilon_eq được duyệt, cỡ mẫu và manifest trước mở tháng 4. Sau mở không điều chỉnh để đạt mục tiêu.

## Thí điểm và sản phẩm

Chọn duy nhất font thiết kế (TV1–TV4), chỉ triển khai khi lõi đã qua gate. Writer Profile/Pareto/cắt tỉa nâng cao ngoài cam kết. Máy vẽ phẳng hai trục khi sẵn sàng; ghi thiết bị, giấy/bút, tốc độ và nguồn đo. Art Mode/thư tay giữ chức năng sản phẩm và không lẫn vào N-RQ.

## Đầu ra bắt buộc

Báo cáo, contract, code/commit, manifest, validation độc lập, bảng raw/per-case và script tái lập; hash patch nếu checkout dirty; licenses/access rules. Phần không được phép công bố có metadata/cách truy cập hợp lệ thay thế, không cam kết public mọi font/dữ liệu. Bài báo là bản thảo dự kiến, không cam kết được nhận.
