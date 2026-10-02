# OmniDraw — đọc trước khi tiếp tục công việc

**Hướng và trạng thái cập nhật ngày 02/10/2026.** Nhánh chia sẻ: `codex/tv4-pr3-slices`. Trang này là điểm vào duy nhất cho tài liệu nhóm; đọc phần của mình rồi mở nguồn chính tương ứng.

## 1. Đề tài hiện làm gì?

Nghiên cứu cách chọn đồng thời hình học thân/dấu tiếng Việt và thứ tự thực hiện nét để giảm chi phí chuyển động của máy vẽ trong tập ứng viên hữu hạn. So sánh với chọn hình học trước rồi tối ưu lịch, đo gap theo số cấu hình m, tìm khi nào có lợi/bằng nhau, kiểm chứng độc lập và phân tích độ nhạy theo tham số chuyển động.

Đóng góp dự kiến là **mô hình chữ/dấu và phân tích có kiểm soát**; DP và tính lồi được kế thừa, không tuyên bố phát minh thuật toán mới. Một thí điểm font có điều kiện, TV1–TV4 đồng chủ trì. Vật lý bổ sung khi có máy phẳng hai trục. Writer Profile/Pareto/cắt tỉa nâng cao ngoài cam kết; Art Mode và thư tay giữ là tính năng sản phẩm.

## 2. Sáu tài liệu chính — đọc theo thứ tự

| Tài liệu | Dùng để quyết định |
|---|---|
| **README này** | Hiểu hướng, trạng thái, thứ tự đọc và ranh giới tài liệu |
| [03 — Công việc hiện tại](03_current-task.md) | Việc kế tiếp theo owner, phụ thuộc và gate còn mở |
| [29 — Đề cương](29_research_proposal_consolidated.md) | Bản đối chiếu đề cương Google Docs theo Mẫu 2 |
| [30 — Kế hoạch kỹ thuật](30_research_development_plan.md) | Ownership, slices, tiến độ 8 tháng và cắt phạm vi |
| [31 — Contract thuật toán](31_joint_solver_contract.md) | Candidate, lịch, hình học, cost, state/action/forget, top-m và regret |
| [32 — API và artifacts](32_research_api_and_artifact_contract.md) | Payload/hash, scope, complete flags, errors và bàn giao adapter |

Docs 31/32 vẫn là **draft cần review trước freeze**, không tự thành sign-off vì tài liệu đã cập nhật. Hướng đã được GVHD đồng ý theo thông báo của TV4; tham số và kết quả không vì vậy mà được duyệt.

## 3. Tiến độ thật hiện tại

- Đề cương Google Docs đã chỉnh; Docs 29 đồng bộ bản nguồn.
- Lớp API/schema/manifest/adapter gateway đã có; kiểm thử mục tiêu 42 gateway + 34 hồi quy handwriting = **76 PASS**. Đây là kiểm thử giao tiếp với adapter giả lập.
- Mặc định chưa đăng ký joint/baseline/oracle/certifier. Capabilities chưa ready; không coi API đã có là thuật toán đã hoàn tất.
- DP mới đã có bản DEV no-forget/safe-forget, geometry/replay/trace và diagnostic bốn đỉnh; chưa được nghiệm thu độc lập. Oracle/primitive độc lập, top-m/beam và chứng nhận còn PENDING. Preflight và sign-off E1/E4 cũ giữ phạm vi/commit gốc.
- Holdout mới, ngưỡng/điểm vận hành/budgets và quality gate chưa khóa. Chưa có xác nhận vật lý từ việc tổ chức tài liệu này.

## 4. Mỗi bạn bắt đầu ở đâu?

| Thành viên | Đọc thêm | Bàn giao tiếp theo |
|---|---|---|
| TV4 — chủ nhiệm | Docs 31 §5, Docs 32 | State/actions, bản no-forget/safe-forget, DP và trace; tích hợp sau kiểm oracle |
| TV2 — Trần Hồng Khải | Docs 31 §4/6/8; [tài liệu nghiên cứu](support/README.md) | Đọc Balas/RTSP/PCGTSP, review cost/ranking, baseline/runner và protocol lambda |
| TV1 — Nguyễn Hoàng Thắng | Docs 30/32; [dữ liệu và font](support/README.md) | Reference/bounds/license ứng viên, fixtures dấu chồng, split mới và custody/access log |
| TV3 — Phùng Tấn Minh | Docs 31 §2/3/7; Docs 32 | Xác nhận nhận oracle; primitive và vét cạn độc lập, ca kiểm tay; đo thiết bị khi có |

Các bàn giao là phân công đề xuất cần owner xác nhận, chưa phải lời xác nhận đã nhận việc. TV4 không sửa baseline TV2, oracle/driver TV3 hoặc hardware ngoài ownership.

## 5. Tài liệu hỗ trợ và lịch sử

- [support/](support/README.md): tech, dữ liệu, nghiên cứu, chương bản thảo, font và hướng dẫn gateway. Nguồn chính vẫn là Docs 29–32; tránh sửa một spec thứ hai ở đây.
- [history/](history/README.md): checkpoint, đề cương/trao đổi trước và record Docs 35 đã hợp nhất. Chỉ dùng truy nguyên, không lấy verdict cũ ký cho hướng mới.
- [Nhật ký](04_progress-log.md): diễn tiến; mục mới nhất ở đầu.
- [Hardware](hardware/00_hardware_index.md): tài liệu thiết bị của TV3, giữ nguyên trong lần tổ chức này.
- [Reviews](reviews/README.md), [phiếu thu thập](collection_sheets/README.md), `evidence/`: bằng chứng đúng ngày/phạm vi; không tự biến thành kết quả của mô hình mới.

Bốn file Docs 01/05/08/19 ở đường dẫn gốc chỉ là chuyển hướng tương thích cho code hoặc tài liệu cũ.

## 6. Cách cập nhật để không lệch hướng

Sửa mô hình → Docs 31; payload/complete flags → Docs 32; ownership/tiến độ → Docs 30; trạng thái và bàn giao → Docs 03; diễn tiến → nhật ký. Đề cương thay đổi phải đối chiếu Google Docs và Docs 29. Thay đổi có review, fixtures và evidence trong phạm vi owner; không tự ký thay người khác.

Để xem nhánh chia sẻ: fetch `origin`, mở nhánh `origin/codex/tv4-pr3-slices` và bắt đầu ở `docs/README.md`; mỗi bạn tiếp tục code trên nhánh của mình. Không ghi đè working tree đang có việc. Commit/hash bàn giao trong Git là nguồn phiên bản, không dùng chỉ tên nhánh để nhận diện nội dung.

Không đưa nội dung Holdout mới vào repo công khai. Khóa trước khi mở, báo riêng incomplete/timeout/infeasible; không dùng test adapter hoặc mô phỏng làm bằng chứng thuật toán/máy thật.

## Bản đồ mã hiện hành

[README repo](../README.md) phân biệt sản phẩm, nghiên cứu mới, hardware và công cụ legacy. [Research README](../backend/research/README.md) là hướng dẫn code/DEV, không thay Docs 31/32; [tests README](../tests/research/README.md) ghi scope và map đường dẫn đã chuyển; [scripts README](../scripts/README.md) phân loại prototype và script PR3 đã đóng. PR đóng, code merge và nghiệm thu được ghi riêng theo commit/phạm vi.

## Bàn giao để các thành viên bắt đầu

[Handoff README](handoff/README.md) ghi nhánh/commit code, snapshot remote, conflict đã mô phỏng và cách giải theo ownership. Prompt: [TV1 dữ liệu](handoff/tv1_prompt.md), [TV2 baseline/runner](handoff/tv2_prompt.md), [TV3 oracle](handoff/tv3_prompt.md). Fetch `origin/codex/tv4-pr3-slices` và mở nhánh nghiên cứu riêng từ nền đã cập nhật; không reset checkout có việc. [Review S0 TV2](reviews/tv2_joint_contract_s0_review_20261002.md) target `8dcfe66`, không là sign-off cho DP code `510f4e1`.
