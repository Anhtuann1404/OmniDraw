# Prompt cho TV3 — oracle độc lập và kiểm chứng

Sao chép nội dung dưới đây vào chat TV3. [Hướng dẫn đồng bộ/conflict](README.md) là một phần của bàn giao.

```text
Tiếp tục OmniDraw với vai trò TV3, hỗ trợ trưởng nhóm. Dùng tài liệu repo làm nguồn chính.

Nguồn chia sẻ origin/codex/tv4-pr3-slices, code TV4 510f4e108d29d5597cb7e82ed3dd53d2ba5c806a. Fetch để có docs/prompt mới nhất. PR3 đã đóng; không mở lại backlog PR3 hoặc nâng sign-off hardware/E4 cũ sang solver mới. Phân biệt PR đóng, code merge và nghiệm thu.

Kiểm nhánh/HEAD/upstream/dirty/staged và worktrees trước khi sửa; giữ nguyên công việc hardware đang có. Fetch origin, xác nhận commit code là ancestor nguồn chia sẻ. Nên mở nhánh nghiên cứu riêng từ nguồn chia sẻ để viết oracle, hardware vẫn ở checkout/nhánh owner:
git worktree add -b codex/tv3-research-oracle-20261002 ../OmniDraw-tv3-research origin/codex/tv4-pr3-slices
Nếu nhánh/path tồn tại thì kiểm/reuse hoặc chọn tên mới. Không reset/stash/ghi đè hardware dirty, không cherry-pick riêng code trên nền thiếu gateway/migration.

Đọc theo thứ tự docs/README.md; docs/03_current-task.md; docs/30_research_development_plan.md; docs/31_joint_solver_contract.md; docs/32_research_api_and_artifact_contract.md; docs/handoff/README.md. Docs 29/lịch sử chỉ khi cần câu hỏi cụ thể. Dùng graphify để xác định schema/adapter và ownership; primitive/oracle phải được viết từ đặc tả, không chép logic DP/checker TV4 làm kiểm chứng độc lập.

Hướng nghiên cứu finite geometry/lịch chữ/dấu; đóng góp mô hình và phân tích có kiểm soát. TV4 đã có DP DEV no-forget/safe-forget, geometry/replay/trace và 313 tests liên quan PASS. Chưa nghiệm thu độc lập; quality/numeric/contact/theta0/domain/k/tie/budget/freeze/sign-off PENDING. HOLDOUT chưa mở. Bốn đỉnh DEV luôn NOT_CERTIFIED. Đầu tiên xác nhận bằng log khả năng nhận oracle theo phân công; không đợi máy để viết oracle.

Việc TV3:
1. Primitive độc lập cho polyline centerline distance/intersection/degenerate/collinear/self/contact, kiểm tay .19/.20/.21 mm. Chỉ chia sẻ schema và geometry thô; không import geometry.py, schedule_checker.py, joint_dp.py hoặc cache feasibility/cost của TV4. Không import primitive/cost TV2 thay cho bản độc lập.
2. Vét cạn các lựa chọn trọn candidates, BODY trái→phải/pha thân nhiều nét, MARK sau chủ thân/precedence/deadline k theo số thân, direction reversible và CONNECT/LIFT hữu hạn. Boundary UP đầu/cuối; empty vẫn tính travel; N_cycle là maximal pen-down runs. Không tự thêm bridge.
3. Review policy DEV: all-pairs và contact disk hữu hạn; tiếp xúc endpoint không miễn phần còn lại. DEV hiện chỉ exact endpoint, near-contact rule cho freeze chưa chốt. Nếu đề xuất tolerance/flatten/error bound khác, ghi proposal và giữ cùng contract cho mọi phương pháp trước so sánh; không tự ký/mặc định .25 mm radius hay theta từ fixtures.
4. Ca nhỏ dự kiến n<=3,q<=2,k<=1,tối đa 6 actions nét trong budget đăng ký DEV. Có empty, reverse, CONNECT/LIFT ở cùng endpoint, mixed k0/k1, dấu chồng/below, distant interaction, equal cost, infeasible và interruption. Dùng ca kiểm tay cộng seed cố định, không lấy ca nhỏ làm certificate toàn HOLDOUT.
5. Adapter oracle independent có scope/completion/status/bounds/provenance đúng Docs 32. Giữ NOT_RUN trước check thực; disagreement record chứa hash/policy/case/schedule/cost và primitive finding. So feasibility và optimal value trong tolerance được review; action sequence chỉ cần giống khi cùng tie policy.
6. Code mới dự kiến backend/research/independent_oracle/, tests/fixtures oracle riêng. Đối chiếu với output/trace TV4 bằng harness bên ngoài primitive, không dùng DP làm oracle. Ghi docs/handoff/tv3_progress.md, commit/contract/hash/lệnh/kết quả/gate và bàn giao TV4 sau mỗi slice.
7. Hardware giữ công việc riêng; measured/simulator/assumed timing và sign-off đúng commit/phạm vi. Không sửa candidate/feasibility theo máy thật chưa chọn, không chạy physical draw vì solve/certify. Không mở HOLDOUT.

Conflict: feature/hardware@f0df948 khi merge snapshot TV4 có conflict docs/03_current-task.md, docs/04_progress-log.md và docs/hardware/00_hardware_index.md. backend/main.py auto-merge nhưng phải kiểm lại API pause/resume/capabilities và research routes khi tích hợp thật. Ưu tiên oracle branch mới để không cần merge cả hardware. Nếu buộc merge nhánh hardware, dùng checkout tích hợp sạch: giữ docs nghiên cứu hiện hành, nhập tiến độ hardware có provenance, TV3 giải hardware index để giữ liên kết và measured/PENDING đúng nghĩa. Không blanket ours/theirs, không ghi đè driver/status đã kiểm hoặc snapshot lịch sử. Chạy tests/research + handwriting validation, thêm tests/test_hardware_adapter.py và smoke simulator/fake phù hợp nếu thực sự tích hợp hardware; không tự chạy máy thật. Hash/danh sách conflict đầy đủ trong handoff README, recheck nếu remote tiến thêm.

Bắt đầu bằng trạng thái Git/contract đã xác minh và xác nhận nhận oracle, rồi triển khai slice primitive kiểm tay đầu tiên. Không tự đổi AI-assisted finding thành human sign-off.
Bàn giao theo mẫu trong docs/handoff/pending_decisions.md, ghi Q-ID, commit/evidence và gate còn mở. Phân công giữ nguyên: oracle TV3, custody TV1, baseline/runner TV2, DP/tích hợp TV4. Không tự ghi người khác đã nhận việc hoặc ký thay owner.
Review Docs 36 (docs/support/36_joint_method_and_dp_argument.md): kiểm giả thiết state đủ, DAG và projection quên an toàn. Có thể lấy fixture method_gap_example.json làm input thô cho oracle tự viết; không import geometry/replay/DP TV4 để gọi độc lập. Ghi numeric/feasibility/value mismatch riêng.
```

Ghi bàn giao theo [mẫu và bảng PENDING](pending_decisions.md), nêu Q-ID liên quan và evidence/commit thực. Phân công TV1–TV4 giữ nguyên theo trưởng nhóm; không tự chuyển oracle/custody hoặc ký thay owner. Các trạng thái PENDING chỉ đóng khi có review/xác nhận trong phạm vi.
