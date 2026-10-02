# Prompt cho TV2 — đối chứng, cost review và runner

Sao chép nội dung dưới đây vào chat TV2. [Hướng dẫn đồng bộ/conflict](README.md) là một phần của bàn giao.

```text
Tiếp tục OmniDraw với vai trò TV2, hỗ trợ trưởng nhóm. Dùng tài liệu repo làm nguồn chính.

Nguồn chia sẻ: origin/codex/tv4-pr3-slices; code TV4 510f4e108d29d5597cb7e82ed3dd53d2ba5c806a. Fetch để có docs/prompt mới nhất. Review S0 TV2 ở docs/reviews/tv2_joint_contract_s0_review_20261002.md là bản nguyên bytes từ efe323779e899d860442d60f138575687e297888 trên codex/tv2-motion-handoff; target 8dcfe66, REVIEWED_WITH_OPEN_GATES và chưa là human sign-off cho DP mới. PR3 đã đóng; không mở lại PR3. Phân biệt PR đóng, code merge và nghiệm thu.

Kiểm nhánh/HEAD/upstream/dirty/staged và worktrees; bảo toàn công việc. Fetch origin và xác nhận 510f4e1 là ancestor nguồn chia sẻ. Ưu tiên worktree/nhánh nghiên cứu mới:
git worktree add -b codex/tv2-research-baselines-20261002 ../OmniDraw-tv2-research origin/codex/tv4-pr3-slices
Nếu nhánh/path tồn tại thì kiểm/reuse hoặc chọn tên mới. Không reset/stash checkout dirty một cách mặc định hoặc cherry-pick riêng code trên nền thiếu gateway/migration.

Đọc: docs/README.md; docs/03_current-task.md; docs/30_research_development_plan.md; docs/31_joint_solver_contract.md; docs/32_research_api_and_artifact_contract.md; docs/handoff/README.md; docs/handoff/pending_decisions.md; backend/research/README.md; review S0 TV2 nêu trên. Docs 29/lịch sử chỉ khi cần nội dung cụ thể. Dùng graphify rồi kiểm source thật vì semantic graph có thể cũ.

Hướng nghiên cứu: đồng tối ưu geometry/lịch trong finite candidates; gap baseline phân tầng top-m và độ nhạy rho/lambda. TV4 có geometry/DP no-forget/safe-forget/replay/trace DEV, SVG diagnostic và bốn đỉnh NOT_CERTIFIED. 313 tests liên quan PASS không là nghiệm thu solver hoặc oracle. Default HTTP adapters chưa ready; HOLDOUT chưa mở; các policy/quality/parameters/budget/tie/freeze/sign-off còn PENDING.

Việc TV2:
1. Recheck hàm J=L_down+rho*L_up+lambda*N_cycle và boundary/maximal runs; review code DEV mới, không chuyển verdict PR3/E4 cũ sang đây. DEV chỉ CONNECT exact endpoint; near-contact/tolerance cho freeze vẫn cần rule shared hashed geometry, không tự thêm connector/bridge.
2. Thực hiện H_ref/H_geom staged_top_m trên toàn G Cartesian sau shared quality gate. Không lọc cấu hình có reference invalid: H_ref internal +infinity, stable config-ID tie, không Infinity JSON. M là số cấu hình toàn chữ, không số candidates mỗi owner.
3. Khởi đầu finite enumeration/heap trên ca nhỏ DEV; k-best chỉ sau chứng minh decomposition/path-config/tie/validity. Inner exact cùng geometry/feasibility/theta; enumeration_complete, ranking_complete, search_complete độc lập. Prefix infeasible trả NO_FEASIBLE_IN_PREFIX, không toàn G INFEASIBLE. Timeout ranking là explored_subset/incomplete.
4. Implement beam như heuristic với FEASIBLE/upper bound, không giả lower bound/exact. Giữ scope và ngân sách từng stage. Dùng interface TV4 solve_fixed_configuration(case, candidate_ids, theta, budget, safe_forget=True) trong backend/research/joint_dp.py; list/tuple ID theo owner, case/hash gốc sau shared quality gate, không trim/re-hash variants. JointRun có scope=fixed_configuration, candidate_set_sha256 và configuration_candidate_ids; OPTIMAL/INFEASIBLE chỉ trong một cấu hình, incomplete giữ nguyên. Outer TV2 chịu ranking/coverage và budget tổng (inner gồm cả preprocessing/replay); không tái cấp toàn budget mỗi cấu hình. Không đưa run inner vào dev_solve.result_packet/HTTP hoặc gọi global OPTIMAL. Đọc research README và test_fixed_configuration.py. Trao đổi với TV4 trước khi sửa joint_dp hoặc đăng ký adapter; không dùng runner B1/B2/B3 legacy như baseline mới.
5. Viết runner/versioned JSONL giữ đủ error/timeout/infeasible và provenance/hash, stage/total timing, peak allocation/RSS đúng nghĩa, environment/seed. Gap chỉ khi exact/feasible/certified-prefix/cùng hash/theta và J_m>0; không lấy thiếu coverage làm mất denominator. Sparse m chỉ smallest_tested_m.
6. Đăng ký protocol lambda trên DEV, multi-N/không bị trội/optimal switching; incomplete là UNKNOWN. theta0/domain/cutoff/epsilon_eq/exact scope/budgets phải review, chưa tự điền. Tiếp tục bảng Balas/RTSP/PCGTSP với nguồn toàn văn/trang thật; thiếu thì PENDING, không giả đã đọc.
7. Code mới dự kiến backend/research/staged_top_m.py, beam.py, runner.py và tests TV2 riêng. Ghi docs/handoff/tv2_progress.md, commit/contract/hash/lệnh/kết quả/gate sau mỗi slice, bàn giao TV4 nhập current-task tổng hợp. Không viết/sửa oracle primitive TV3 hoặc hardware; không mở HOLDOUT.

Conflict: merge codex/tv2-motion-handoff@efe3237 với code TV4 snapshot không có textual conflict. Điều đó không chứng minh semantic/API tương thích. Nhánh cũ còn docs Sprint/PR3 và review ở root; ưu tiên nhánh mới từ nguồn chia sẻ, không merge cả gói review cũ chỉ để mang S0 review vì bản đã có ở docs/reviews/. Nếu buộc merge, dùng checkout tích hợp sạch, inspect git diff --cc, giữ nguồn Docs 31/32 hiện hành và scope của review gốc; không blanket ours/theirs. Tests gateway đã chuyển tests/research/test_api.py; port chỉnh sửa sang path mới và tránh collect trùng. Recheck merge nếu remote tiến thêm, chạy tests/research + handwriting validation + tests baseline/runner liên quan.

Bắt đầu bằng trạng thái Git/contract đã xác minh, xác nhận phạm vi review S0 đã có, rồi thực hiện slice baseline DEV đầu tiên. Không tự coi review nháp AI là human sign-off.
Bàn giao theo mẫu trong docs/handoff/pending_decisions.md, ghi Q-ID, commit/evidence và gate còn mở. Phân công giữ nguyên: oracle TV3, custody TV1, baseline/runner TV2, DP/tích hợp TV4. Không tự ghi người khác đã nhận việc hoặc ký thay owner.
Review Docs 36 (docs/support/36_joint_method_and_dp_argument.md): kiểm J/boundary, H_ref immediate-mark của witness, điều kiện bằng nhau và giả thiết state/recurrence. Witness do TV4 tính tay, chưa là module baseline TV2; bàn giao bất đồng bằng Q-ID/commit/counterexample.
Đọc docs/reviews/tv4_numeric_audit_20261002.md: core DEV cost_policy_id=tv4-dev-dyadic-primitive-cost-v1, tie v2/replay dev-v3. Review arithmetic/provenance cùng policy trước ghép J/gap; display rounding không là tie. Numeric/geometry freeze vẫn PENDING; oracle TV3 không import cost helper TV4 để gọi độc lập.
```

Ghi bàn giao theo [mẫu và bảng PENDING](pending_decisions.md), nêu Q-ID liên quan và evidence/commit thực. Phân công TV1–TV4 giữ nguyên theo trưởng nhóm; không tự chuyển oracle/custody hoặc ký thay owner. Các trạng thái PENDING chỉ đóng khi có review/xác nhận trong phạm vi.
