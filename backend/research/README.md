# Lõi nghiên cứu mới — Docs 31/32

Owner: TV4 core/gateway; TV2 baseline/runner/cost review; TV1 dữ liệu; TV3 oracle độc lập. Contract vẫn DRAFT/REVIEW_PENDING. Mã hiện có dùng policy DEV khai báo tường minh, không là release đã freeze.

| File | Nhiệm vụ | Tình trạng |
|---|---|---|
| `schemas.py` | Strict input/output, hashes, IDs và cấu trúc schedule | Gateway đã có tests; STRUCTURALLY_VALID không là geometry PASS |
| `router.py`, `service.py` | HTTP, manifest phía server, adapter/output guards | Default solver/certifier chưa đăng ký |
| `geometry.py` | Polyline distance/intersection, contact disk, mọi cặp ứng viên, graph tương tác | TV4 DEV; không dùng cho oracle TV3 |
| `schedule_checker.py` | Replay BODY/MARK/END và hệ số/J | TV4; kiểm thời gian/hướng/transition, không tự kiểm clearance |
| `joint_dp.py` | DP no-forget và safe-forget, backpointer, budget và incumbent | Full-set DEV float model; review/đối chiếu oracle PENDING |
| `dev_solve.py` | Debug một ca, so hai mode và xuất JSON/trace | Không là runner thí nghiệm TV2; không mở HOLDOUT |
| `render_dev.py` | SVG DEV cùng geometry/hướng/thứ tự đã replay | Metadata ghi independent validation NOT_RUN; không cấp quyền print |
| `vertex_analysis.py` | Diagnostic regret ở bốn đỉnh, giữ schedule cố định | Budget chung wall-time/states; luôn NOT_CERTIFIED |

## Chính sách DEV và giới hạn

- `tv4-dev-polyline-v1`: nhận polyline world-mm, không flatten curve hoặc style sau solve.
- `tv4-dev-float-v1`: phép tính float, không trừ epsilon khỏi c_min=.20; overflow bị từ chối. Chưa là chứng nhận sai số số học. Tie `tv4-dev-float-lex-actions-v1` chọn theo chuỗi `(stroke-ref,orientation,transition)` khi float cost bằng nhau; không tự chốt tie freeze.
- `tv4-dev-all-pairs-v1`: kiểm mọi cặp nét có thể đồng thời được chọn, gồm cùng/chữ khác và tương tác xa; không tin danh sách separation_pairs do client bỏ bớt. Cặp khác variant cùng owner được bỏ vì loại trừ nhau. Self crossing và backtracking bị từ chối; zero-length chỉ khi policy cho phép.
- `tv4-dev-exact-endpoint-v1`: CONNECT cần whitelist, endpoint và location trùng chính xác. Radius là vùng ngoại lệ geometry hữu hạn; clip vùng này trước đo clearance phần còn lại. Radius=0 không thể miễn phần lân cận khỏi floor. Policy khác chưa hỗ trợ sẽ bị từ chối, không fallback.
- Graph giữ cạnh owner nếu có bất kỳ cặp candidate không tương thích. Mọi cặp đã kiểm trước gộp state. Safe-forget chỉ bỏ owner đã hoàn tất, hết pending và không còn cạnh với owner chưa chọn; e giữ `(owner,candidate,stroke,direction)` riêng. No-forget lưu toàn bộ A; không áp cận frontier nhỏ của safe-forget cho bộ nhớ no-forget.
- Budget theo từng mode gồm preprocessing/search/replay: cooperative wall-time/state/allocated-memory guard, không là worker có khả năng cưỡng bức dừng. Bộ nhớ ghi lượng allocation tracemalloc, không là process RSS. `max_states` tính mọi state được giữ; không enumerate Cartesian nên không tiêu thụ `max_configurations`. Không chạy đồng thời trong HTTP vì tracemalloc là process-wide.
- Có incumbent khi timeout/resource limit vẫn giữ outcome incomplete. Không dùng replay hoặc no-forget/safe-forget agreement làm independent PASS. Default HTTP capabilities vẫn chưa ready.

## Tái lập trên DEV

Từ root repo:

```sh
PYTHONPATH=backend backend/venv/bin/python3 -m pytest tests/research backend/test_handwriting_validation.py -q

backend/venv/bin/python3 -m backend.research.dev_solve \
  --manifest tests/research/fixtures/solver_dev_cases.json \
  --case-id tv4-solver-dev-stacked-3 --rho 0.5 --lambda-mm 2 \
  --mode both --wall-time-ms 10000 --max-states 100000 --memory-limit-mb 64 \
  --output output/research_dev/joint-dev.json \
  --svg-output output/research_dev/joint-dev.svg
```

Số ở lệnh là ví dụ DEV, không chốt theta0/k/budget nghiên cứu. Không ghi đè output có sẵn; lần chạy sau chọn tên mới. JSON chứa SolveResult, config/hash Git dirty (gồm hash file untracked), diagnostics và trace. `OPTIMAL`/`INFEASIBLE` là kết quả search trong policy DEV đang khai báo; quality gate, owner review và independent validation vẫn PENDING/NOT_RUN. So hai mode dùng tolerance debug tuyệt đối 1e-9 mm và tương đối 1e-12, không phải epsilon_eq nghiên cứu.

`solver_dev_cases.json` có contact disk radius .25 mm và policy geometry DEV; `replay_dev_cases.json` giữ ca arithmetic ban đầu với contact radius=0 và geometry chưa review. Hai bộ khác hash, không hoán đổi để báo nghiệm thu. Không có font/source/dataset TV1 đã duyệt ở đây.

## Bàn giao còn mở

TV2 triển khai staged_top_m/beam/runner và review mục tiêu; TV3 viết oracle bằng primitive độc lập, chỉ dùng schema/dữ liệu thô; TV1 cung cấp ứng viên/reference/quality/custody. Chưa tạo các module này. Sau đối chiếu độc lập, mới tích hợp adapter/renderer sản phẩm và certifier bốn đỉnh. Font pilot/máy thật/HOLDOUT vẫn theo gate Docs 30–32.
