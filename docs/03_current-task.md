# Công việc hiện tại — mô hình đồng tối ưu chữ/dấu

**Cập nhật 02/10/2026; nhánh chia sẻ `codex/tv4-pr3-slices`.** [Đọc trước](README.md). Nguồn chính: [kế hoạch](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API/artifacts](32_research_api_and_artifact_contract.md). Hướng đã được GVHD đồng ý theo TV4; chi tiết còn chờ review/freeze.

## Đã có và chưa có

| Hạng mục | Trạng thái xác minh |
|---|---|
| Đề cương Google Docs và Docs 29 | Đã chỉnh và đồng bộ nội dung; không là nghiệm thu thuật toán |
| API gateway `backend/research/` | Đã có schema/hash/manifest/routes và kiểm output adapter; mặc định solver/certifier chưa ready |
| Kiểm thử gateway/hồi quy API | 42 + 34 = 76 PASS; adapter test không là bộ giải nghiên cứu |
| DP joint | Có bản DEV no-forget/safe-forget, geometry/replay/trace; review và oracle độc lập PENDING |
| Baseline top-m/beam, oracle và certifier | Chưa nghiệm thu hướng mới; thuộc bàn giao TV2/TV3; chưa có adapter mặc định |
| Holdout mới và freeze | Chưa mở/chưa khóa theo kế hoạch mới; không đưa dữ liệu niêm phong lên repo |
| Máy thật/font pilot | Có điều kiện; chưa tự tạo kết quả hoặc sign-off |

Không suy ra trạng thái nhánh remote TV1–TV3 từ checkout TV4. E1/E4/PR3/hardware cũ giữ verdict đúng phạm vi và commit.

**PR3 đã đóng theo xác nhận trưởng nhóm ngày 02/10/2026.** Không mở lại việc PR3 đã hoàn tất. Trạng thái PR đóng, code đã merge và kết quả nghiệm thu là ba thông tin riêng: checkout này không xác minh merge vào nhánh đích; sign-off chỉ áp dụng commit/phạm vi đã ký. Tên nhánh có `pr3` không đổi slice nghiên cứu mới thành việc của PR3 cũ.

## Slice TV4 mới — DEV DP và tổ chức mã (02/10/2026)

- Nền: nhánh `codex/tv4-pr3-slices`, HEAD `8dcfe663df61745b9b0cfe2d2dc5a1fd3c283b22`, sau `34810eb`; upstream local cùng hash, chưa fetch remote. PR3 đã đóng. Các thay đổi có sẵn của bridge/CAD/hardware, file bị xóa và prototype được giữ nguyên; không dùng `backup/pr3-implementation`.
- Lõi mới `backend/research/`: geometry polyline/all-pairs/contact disk và graph tương tác; DP S=(i,t,A,P,e) no-forget/safe-forget, backpointer/tie DEV, guard wall-time/state/allocated-memory và incumbent khi incomplete; replay BODY/MARK/END và chi phí. Không import solver/cost/bridge sản phẩm hoặc hardware.
- Policy DEV khai báo tường minh: floor .20 mm, all simultaneously selectable pairs, self-cross/backtracking reject, CONNECT exact endpoint với whitelist; ngoại lệ geometry chỉ trong disk radius hữu hạn. Unknown policy/overflow bị từ chối. Không tự chốt policy/numeric error/quality gate/parameter freeze. Chi tiết giới hạn và lệnh: [research README](../backend/research/README.md).
- `dev_solve.py`: debug một ca DEV/synthetic, so hai mode, JSON SolveResult/config/hash/trace. `render_dev.py`: SVG giữ nguyên geometry/hướng/order và metadata independent NOT_RUN; không cấp quyền print. `vertex_analysis.py`: giữ schedule cố định, đối thủ full candidate set tại bốn đỉnh; mọi output vẫn NOT_CERTIFIED, incomplete không có maximum claim. Đây không là runner TV2 hoặc oracle TV3.
- Tests và fixtures gom vào `tests/research/`; manifest riêng replay arithmetic và solver geometry có hash thật. Dữ liệu tự tạo ba chữ NFD, tối đa hai candidates/chữ/sáu nét và empty; không là font/dataset TV1 đã duyệt. Các số theta/k/contact radius/budget chỉ cho DEV.
- Tổ chức: README root và từng vùng mã nêu ownership/current/legacy/PENDING; script tái lập PR3 chuyển `scripts/legacy/`, giữ wrapper đường dẫn cũ; update references nguồn đang dùng. Historical commands/evidence giữ phạm vi gốc, migration map ở [tests README](../tests/research/README.md). Ignore riêng tool workspaces và output DEV, giữ bytes công việc có sẵn.
- Kiểm thử cuối: **313 PASS** (133 research, 34 handwriting validation, 146 hồi quy legacy), một warning AnyIO/TestClient; `git diff --check` sạch. Lệnh và giới hạn ghi trong progress-log. DEV CLI hai mode cùng J=19.914213562373096 mm; independent NOT_RUN. Hồi quy PASS không mở lại PR3. Code TV4 đã commit tại `510f4e108d29d5597cb7e82ed3dd53d2ba5c806a`; chưa merge vào main/develop hoặc nghiệm thu. API default solver/certifier vẫn chưa ready. Giá trị OPTIMAL/INFEASIBLE là search claim trong policy DEV, không là nghiệm thu độc lập.

**Tiếp nối:** TV2 review cost/ranking và nhận baseline/runner; TV3 xác nhận nhận oracle và viết primitive/vét cạn độc lập trên fixtures; TV1 review dữ liệu/reference/quality/custody. TV4 xử lý bất đồng và chỉ tích hợp adapter/export/certifier sản phẩm sau gate độc lập. HOLDOUT vẫn chưa mở; contract freeze, epsilon_eq/theta0/domain/k/tolerance/quality/budgets/tie và sign-off PENDING. Không mở lại backlog PR3.

## Slice TV4 tiếp nối — inner solve geometry cố định (02/10/2026)

Từ HEAD `1991fca` đã fetch upstream và bảo toàn dirty work. `solve_fixed_configuration` dùng chung lõi DP no-forget/safe-forget, giới hạn đúng ID từng owner, giữ case/candidate hash gốc và scope fixed_configuration. Timeout/resource limit giữ incomplete và incumbent đúng cấu hình nếu có; INFEASIBLE không suy toàn G/prefix. CLI chặn xuất inner result thành full-set. Hướng dẫn TV2, Docs 31/32 và research/tests README đã cập nhật cùng code. Không sửa baseline/cost/runner/hardware, không đăng ký adapter hoặc mở HOLDOUT. Kiểm độc lập/freeze/sign-off PENDING.

TV2 có thể bắt đầu baseline DEV bằng interface này, kiểm aggregate budget/ranking/coverage theo contract; TV3 tiếp tục oracle độc lập. TV4 tiếp theo đối chiếu bất đồng bằng counterexample từ TV2/TV3 rồi tích hợp sau gate. Kiểm thử **332 PASS** (152 research + 34 handwriting + 146 legacy), một warning có sẵn; diff-check sạch. Slice được publish lên nhánh chia sẻ; commit mang entry tương ứng trong progress-log, fetch HEAD mới nhất để tiếp nối. Không là merge vào nhánh đích hoặc nghiệm thu.

## Việc kế tiếp theo owner

| Owner | Làm ngay | Bàn giao và gate |
|---|---|---|
| TV4 | Bàn giao code/fixtures DEV DP no-forget/safe-forget và trace; phối hợp review policy | Đối chiếu oracle độc lập TV3, xử lý mismatch; chưa tự ký solver hoặc mở HOLDOUT |
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

## Nhận việc từ remote và xử lý conflict

Nguồn bàn giao: `origin/codex/tv4-pr3-slices`; fetch để có cả commit code `510f4e1` và commit docs/prompt theo sau. [Handoff README](handoff/README.md) chứa snapshot remote/merge-tree và quy trình đồng bộ; [TV1](handoff/tv1_prompt.md), [TV2](handoff/tv2_prompt.md), [TV3](handoff/tv3_prompt.md) có prompt tự đủ ngữ cảnh. Các thành viên nên tạo nhánh/worktree nghiên cứu riêng từ nền này, giữ nguyên công việc cũ.

TV2 đã có review S0 `REVIEWED_WITH_OPEN_GATES` tại `efe3237`, target `8dcfe66`; [bản nguyên bytes](reviews/tv2_joint_contract_s0_review_20261002.md) được tiếp nhận, chưa ký cho DP mới. Near-contact khác tọa độ vẫn PENDING trước freeze; DEV chỉ exact endpoint. Mô phỏng merge code TV4 với remote: TV1 11 conflicts, hardware 3, main 1, TV2/develop 0; không là merge thực hoặc nghiệm thu. Log riêng từng owner ở docs/handoff giảm việc cùng sửa current-task/progress-log tổng hợp.

## Slice điều phối — bảng PENDING (02/10/2026)

Đã rà Docs 30–32 và review S0 TV2, lập [bảng 16 quyết định/gate](handoff/pending_decisions.md) có ưu tiên, chủ trì/reviewer, evidence để chốt và mẫu bàn giao chung. Trưởng nhóm giữ các TV như cũ; oracle vẫn TV3, custody vẫn TV1. Toàn bộ hàng PENDING; không tự ghi nhận owner đã nhận việc, chọn tham số hoặc nâng review thành nghiệm thu. Bước ngay: TV3 log nhận oracle, các owner review contract/fixtures và bàn giao counterexamples; TV4 tổng hợp. Không đổi runtime, không mở HOLDOUT hoặc PR3.

## Slice phương pháp TV4 — lập luận và witness (02/10/2026)

[Bản phương pháp Docs 36](support/36_joint_method_and_dp_argument.md) đã giải thích input/phương án/J, state sufficiency, soundness/completeness/DAG và projection safe-forget với giả thiết rõ. Đối chiếu code và giới hạn float/precompute/budget/bookkeeping; không tự chứng nhận numerical exactness hoặc đóng cận §5.5. Witness synthetic hai owners/ba nét có hai geometry/bốn lịch tính tay, reference chọn A nhưng joint chọn B với k=1; đổi k=0 cho trường hợp bằng nhau. Fixture/hash/tests/lệnh dùng vùng nghiên cứu hiện hành, không code baseline/oracle mới hoặc font/quality TV1 đã duyệt.

Nguồn liên quan Docs 30–32, chương phương pháp, traceability, README code/tests và prompt TV1–TV3 đã nối cùng bản review. Phân công giữ nguyên, Q02/Q04/Q05/Q06/Q10/Q11 vẫn PENDING. TV2 review cost/reference/lập luận, TV3 oracle độc lập trên input thô, TV1 quality/reference; TV4 xử lý counterexample. Kiểm thử 194 PASS (160 research + 34 handwriting), 1 warning có sẵn; CLI hai mode cùng J=10 và compare PASS. Test evidence/commit/push ghi progress-log; HOLDOUT/default adapters/PR3 giữ trạng thái hiện hành.

## Slice TV4 số học/đồng hạng (02/10/2026)

[Audit numeric](reviews/tv4_numeric_audit_20261002.md) tìm ca prefix rounding chọn J replay lớn hơn; đã sửa core/replay bằng exact Fraction trên primitive binary64, cost policy DEV riêng/tie v2/replay dev-v3. CLI compare internal objective, ghi ratio/enclosure và policy trong config; vertex regret trừ trước round, SVG giữ policy. Có manifest synthetic hai ca và 17 tests numeric; floor/contact không đổi. Hồi quy 356 PASS trên batch trước test CLI bổ sung, focused research/API 211 PASS và numeric final 17 PASS; 1 warning AnyIO có sẵn. Không cộng số test các batch. Review numeric/geometry/tie/budget và oracle độc lập vẫn PENDING, default adapters/HOLDOUT/PR3 không đổi. TV2/TV3 đọc audit/prompt cập nhật trước ghép kết quả, TV4 xử lý counterexamples tiếp theo; progress-log giữ lệnh/phiên bản thực.
