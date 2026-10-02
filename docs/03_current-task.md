# Công việc hiện tại của nhóm

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API nghiên cứu](32_research_api_and_artifact_contract.md) là nguồn triển khai.

## Trạng thái đã xác minh

- Checkout: `codex/tv4-pr3-slices`, HEAD `c1b4696` tại lúc rà soát; có thay đổi local của nhóm. HEAD riêng không nhận diện toàn nội dung working tree.
- Có code sản phẩm/PR3, runner DEV và preflight khám phá. Chưa có nghiệm thu DP joint/oracle độc lập/top-m theo contract mới.
- GVHD đã đồng ý hướng đề tài theo thông báo của TV4. Các ngưỡng, số mẫu, chi tiết contract và hardware calibration chưa vì thế mà được ký.
- Lượt này cập nhật tài liệu, không chạy lại suite hoặc tuyên bố số test PASS mới; không xác minh thêm nhánh remote của các thành viên.

## Việc cần làm ngay

| Owner | Việc kế tiếp | Bàn giao/gate |
|---|---|---|
| TV4 | Chốt candidate/state/action schema và mapping code → Docs 31; triển khai DP theo slice | Mỗi lát có trace, tests và review; không tự viết oracle đối chiếu |
| TV2 — Trần Hồng Khải | Review cost/N_cycle, H_ref/H_geom, top-m resource handling; đọc toàn văn Balas; runner/phân tích | Bảng nguồn có trang, protocol ranking/tie/budget, provenance; không ký exit dựa preflight cũ |
| TV1 — Nguyễn Hoàng Thắng | Candidate/anchor/license manifest; split mới và access log; fixtures dấu chồng; đồng chủ trì font | Corpus cũ là bổ sung; không đưa nội dung Holdout mới vào repo công khai |
| TV3 — Phùng Tấn Minh | Xác nhận nhận oracle độc lập; primitive distance/intersection/cost; ca biên; chuẩn bị đo thiết bị | Không cần chờ máy để viết oracle; ghi driver/capabilities và số đo thật khi có máy |

Nếu TV3 chưa nhận oracle, TV1 chỉ nhận sau khi TV2 nhận custody nhật ký/split và nhóm ghi bàn giao. Đây là phương án dự phòng, không phải đã có đồng ý của các owner.

## Những quyết định chưa khóa

Số mẫu Holdout, epsilon_eq/căn cứ và duyệt, rho0/lambda0/miền quét, nguồn tham số, k từng dấu, dung sai hình học/contact, budget, tie policy, cấu hình máy và giấy phép font. Draft Docs 31/32 chứa quy ước đề xuất; cần review trước implementation/freeze. Ví dụ số trong API không phải giá trị nghiệm thu.

## Việc tạm hoãn

Writer Profile, Pareto, cắt tỉa nâng cao, hiệu chuẩn chủ động và nhiều màu. Art Mode/thư tay vẫn là phần sản phẩm; không làm trước gate lõi để thay kết quả nghiên cứu. Sign-off E1/E4/hardware cũ giữ đúng phạm vi và commit lịch sử.
