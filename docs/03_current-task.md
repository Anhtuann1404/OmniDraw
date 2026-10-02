# Công việc hiện tại — mô hình đồng tối ưu chữ/dấu

**Cập nhật 02/10/2026; nhánh chia sẻ `codex/tv4-pr3-slices`.** [Đọc trước](README.md). Nguồn chính: [kế hoạch](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API/artifacts](32_research_api_and_artifact_contract.md). Hướng đã được GVHD đồng ý theo TV4; chi tiết còn chờ review/freeze.

## Đã có và chưa có

| Hạng mục | Trạng thái xác minh |
|---|---|
| Đề cương Google Docs và Docs 29 | Đã chỉnh và đồng bộ nội dung; không là nghiệm thu thuật toán |
| API gateway `backend/research/` | Đã có schema/hash/manifest/routes và kiểm output adapter; mặc định solver/certifier chưa ready |
| Kiểm thử gateway/hồi quy API | 42 + 34 = 76 PASS; adapter test không là bộ giải nghiên cứu |
| DP joint, baseline top-m/beam, oracle và certifier | Chưa nghiệm thu hướng mới; đang ở đặc tả và bàn giao adapter |
| Holdout mới và freeze | Chưa mở/chưa khóa theo kế hoạch mới; không đưa dữ liệu niêm phong lên repo |
| Máy thật/font pilot | Có điều kiện; chưa tự tạo kết quả hoặc sign-off |

Không suy ra trạng thái nhánh remote TV1–TV3 từ checkout TV4. E1/E4/PR3/hardware cũ giữ verdict đúng phạm vi và commit.

## Việc kế tiếp theo owner

| Owner | Làm ngay | Bàn giao và gate |
|---|---|---|
| TV4 | Mã hóa S=(i,t,A,P,e), BODY/MARK/END, cost và forget theo Docs 31 §5 | Trace ca nhỏ; so no-forget/safe-forget rồi đối chiếu oracle độc lập; chưa tự ký solver |
| TV2 — Trần Hồng Khải | Review cost/N_cycle, ranker decomposition/tie/prefix evidence; đọc Balas và RTSP/PCGTSP | Bảng nguồn có trang, baseline/runner cùng scope; protocol lambda và completion trên DEV |
| TV1 — Nguyễn Hoàng Thắng | Glyph/reference/anchor/license, quality bounds trên DEV; fixtures dấu chồng; split/custody | Manifest/hash trước–sau lọc và lý do, access log, dữ liệu mới chưa dùng tinh chỉnh |
| TV3 — Phùng Tấn Minh | Xác nhận nhận oracle, viết primitive/vét cạn độc lập từ đặc tả | Ca biên 0,19/0,20/0,21 mm, deadline/reverse/connect/đồng hạng/vô nghiệm; không chờ máy để làm oracle |

Bảng là việc cần làm, không xác nhận các bạn đã nhận/hoàn thành. Nếu TV3 không nhận oracle, TV1 chỉ tiếp nhận sau bàn giao custody/log cho TV2; cần ghi xác nhận. TV4 là tác giả DP, không tự viết oracle rồi gọi độc lập.

## Thứ tự ưu tiên và điểm khóa

1. Review contract/fixtures và xác nhận oracle; khóa cách hiểu trước viết bộ giải.
2. State/actions/no-forget của TV4 song song dữ liệu TV1, oracle TV3 và review/ranker TV2.
3. Safe-forget và DP–oracle khớp khả thi/value; lịch chỉ cần khớp nếu cùng phá hòa.
4. Baseline/runner, chẩn đoán lambda, điều kiện bằng nhau/có lợi và chứng nhận trong scope.
5. Freeze mã/ứng viên/tham số/budgets trước Holdout; font chỉ sau gate lõi.

Còn PENDING: cỡ mẫu Holdout, epsilon_eq/căn cứ và duyệt, theta0/miền/nguồn tham số, k từng dấu, dung sai/contact, quality bounds/reference, scope exact n/q/k/số nét/w, budget và tỷ lệ hoàn tất, cutoff lambda, tie. Không tự điền từ ví dụ minh họa.

Pareto/cắt tỉa nâng cao, Writer Profile, hiệu chuẩn chủ động và nhiều màu ngoài cam kết. Art Mode/thư tay giữ phần sản phẩm. Nếu trượt gate cuối tháng 3 thì giảm khảo sát mở rộng, lùi Holdout/font; không bỏ kiểm chứng độc lập để kịp số liệu.

## Handoff

Mỗi owner gửi commit, contract/version đã dùng, lệnh tái lập, kết quả/giới hạn, gate còn mở và yêu cầu review. Cập nhật đúng nguồn chính; record bổ sung Docs 35 đã nhập Docs 31/30/32 và chuyển lịch sử, không cần đọc riêng để triển khai.
