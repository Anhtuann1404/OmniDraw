# Bàn giao nghiên cứu mới cho TV1–TV3 — 02/10/2026

Nguồn chung: `origin/codex/tv4-pr3-slices`. Commit code TV4: **`510f4e108d29d5597cb7e82ed3dd53d2ba5c806a`**, nền `8dcfe66` sau `34810eb`. Docs/prompt được commit sau code; fetch nhánh chia sẻ để có bản tài liệu mới nhất, không chỉ checkout commit code.

| Owner | Prompt bắt đầu | Công việc |
|---|---|---|
| TV1 | [tv1_prompt.md](tv1_prompt.md) | Ứng viên/reference/quality và split/custody |
| TV2 | [tv2_prompt.md](tv2_prompt.md) | Cost/ranking review, top-m/beam, runner và protocol lambda |
| TV3 | [tv3_prompt.md](tv3_prompt.md) | Oracle/primitive độc lập và đối chiếu DP; hardware theo nhánh riêng |

PR3 đã đóng. Code nghiên cứu đã có commit không tự có nghĩa đã merge vào main/develop hoặc nghiệm thu. 313 tests PASS có scope ở progress-log; oracle, freeze, chất lượng, tham số/sign-off còn PENDING; HOLDOUT mới chưa mở. Default HTTP solver/certifier chưa ready.

## Khởi động để giảm conflict

Nghiên cứu mới nên bắt đầu bằng nhánh riêng **từ nhánh TV4 chia sẻ**, không tiếp tục trên nền Docs Sprint/PR3 cũ. Nếu checkout cũ đang có việc, giữ nguyên và mở worktree khác. Không đem uncommitted work sang nhánh mới một cách mặc định.

```sh
git status --short --branch
git log -5 --oneline
git fetch origin --prune
git merge-base --is-ancestor 510f4e108d29d5597cb7e82ed3dd53d2ba5c806a origin/codex/tv4-pr3-slices
git worktree list
```

Sau đó dùng lệnh worktree trong prompt đúng vai trò; nếu nhánh/path đã tồn tại thì kiểm tra và tái sử dụng đúng checkout, hoặc chọn tên mới. Ghi hash nhánh chia sẻ thực tế đã dùng vào log bàn giao. Không đổi/reset nhánh cũ để có một tree sạch.

Chỉ đưa commit cũ vào nhánh nghiên cứu nếu nội dung thực sự cần và đã kiểm phù hợp contract mới. Không cherry-pick lại PR đã merge vào nền. Không cherry-pick riêng `510f4e1` lên nền quá cũ vì code phụ thuộc gateway/schema và migration tài liệu trước nó.

## Conflict đã mô phỏng

TV4 đã fetch và chạy `git merge-tree --write-tree --name-only 510f4e1 <remote-ref>` ngày 02/10/2026. Đây là mô phỏng với Git objects, **không merge vào working tree/nhánh remote**. Các hash dưới đây khóa phạm vi kết quả; local chưa commit và thay đổi remote sau fetch không nằm trong phép kiểm.

| Remote ref | Hash đã kiểm | Conflict văn bản |
|---|---|---|
| `origin/feature/tv1-data-corpus` | `0cd03a99ece556e738c43ba1620dd334da4c301f` | 11 file; phần lớn docs migration và evidence cũ |
| `origin/codex/tv2-motion-handoff` | `efe323779e899d860442d60f138575687e297888` | Không có tại snapshot này |
| `origin/feature/hardware` | `f0df94878971f5335c3066e168aa67d749b0f713` | 3 file docs |
| `origin/develop` | `ded5fbfb3fd875f9f4f6427c18566274101d08d3` | Không có tại snapshot này |
| `origin/main` | `b8aca0d659d7b9d00115df92f617d6bfbbf8aa30` | `docs/01_tech-stack.md` |

TV1: `dataset/README.md`, `docs/01_tech-stack.md`, `docs/03_current-task.md`, `docs/04_progress-log.md`, `docs/05_ca_vhc_research_spec.md`, `docs/08_handwriting_dataset_spec.md`, `docs/19_benchmark_corpus_freeze_report.md`, `docs/README.md`, `docs/evidence/pr3_e1_dev_rows.csv`, `docs/history/20261002/10_nckh_research_plan.md`, `docs/history/20261002/17_pr3_implementation_readiness.md`.

TV3: `docs/03_current-task.md`, `docs/04_progress-log.md`, `docs/hardware/00_hardware_index.md`. `backend/main.py` auto-merge trong mô phỏng, nhưng vẫn cần test API khi tích hợp thật. Không có textual conflict không chứng minh code/contract tương thích.

Kết quả được recheck sau commit docs trước khi push; số conflict ở các nhánh trên giữ nguyên. Không đảm bảo lần merge sau sẽ giống snapshot.

## Khi cần hợp nhất nhánh cũ

Ưu tiên nhánh/worktree mới từ nền chia sẻ. Nếu phải giữ toàn bộ lịch sử một nhánh cũ, tạo nhánh tích hợp riêng từ nhánh đó trong checkout sạch rồi merge nhánh chia sẻ tại đó; không thao tác merge trên checkout có công việc chưa commit.

```sh
git fetch origin --prune
git merge --no-commit --no-ff origin/codex/tv4-pr3-slices
git diff --name-only --diff-filter=U
git diff --cc
```

Giải theo nội dung và ownership, không chọn toàn bộ `ours`/`theirs` hoặc chiến lược bỏ một phía:

- **Docs 03/README và Docs 30–32:** giữ hướng nghiên cứu mới/PR3 đã đóng; nhập thêm tiến độ thật của owner. Không kéo trạng thái Sprint/PR3 cũ trở lại thành backlog hiện hành.
- **Đường dẫn docs đã chuyển:** giữ trang chuyển hướng ở gốc; đưa nội dung cập nhật phù hợp vào `docs/support/` hoặc nguồn chính tương ứng. Ví dụ conflict `docs/01_tech-stack.md`: giữ redirect, rà nội dung product stack phía main và cập nhật phần tương ứng trong `docs/support/01_tech-stack.md` sau xác minh. Không chép giả định giá/quota/API cũ thành thông tin mới đã kiểm.
- **Progress-log:** giữ cả hai entry có ngày/hash/phạm vi; không biến verdict cũ thành sign-off mới. Cập nhật cuối slice vào log riêng owner để giảm việc cùng sửa đầu file.
- **History:** không ghi đè snapshot đã lưu. Nội dung khác cần giữ được lưu dưới tên gắn source commit trong record bổ sung có provenance, không thay bytes bản lịch sử gốc.
- **Evidence CSV add/add:** so source commit/hash/schema và giữ riêng cả hai nếu khác. Không nối hàng, chọn theo số dòng hoặc mặc nhiên gọi một bản là kết quả hiện hành. Đề xuất xử lý cho TV4/owner; chưa đủ provenance thì giữ conflict/integration chưa hoàn tất.
- **Dataset/quality/custody:** TV1 giải semantic và giữ nhãn supplemental/HOLDOUT đúng nguồn; không đưa HOLDOUT niêm phong lên Git.
- **Hardware:** TV3 giữ driver/contract/status vật lý đã kiểm; nghiên cứu giữ router riêng. Không thay driver/config bằng code TV4 hoặc suy mô phỏng thành số đo máy thật.
- **Tests chuyển thư mục:** port chỉnh sửa cần thiết từ đường dẫn cũ sang `tests/research/`, rồi bỏ bản trùng để pytest chỉ collect một lần; giữ tests PR3/CA-VHC trong scope hồi quy cũ.

Sau giải: stage từng file đã kiểm, `git diff --cached --check`, chạy tests nghiên cứu và hồi quy liên quan; nếu đã merge hardware/dataset thì chạy thêm suite của owner. Chỉ commit merge khi không còn unmerged paths, kiểm cả textual và semantic conflict. Nếu không đủ thông tin, dùng `git merge --abort` ở checkout tích hợp này và ghi lý do để owner xử lý; không force-push nhánh đã chia sẻ.

## Ranh giới sửa để các PR dễ ghép

| Owner | Vùng làm việc dự kiến | Log/review riêng |
|---|---|---|
| TV1 | `dataset/research/dev/`, fixture candidates có nguồn trong `tests/research/fixtures/` | `docs/handoff/tv1_progress.md`, phiếu review riêng TV1 |
| TV2 | `backend/research/staged_top_m.py`, `beam.py`, `runner.py`, tests TV2 | `docs/handoff/tv2_progress.md`, phiếu review riêng TV2 |
| TV3 | `backend/research/independent_oracle/`, tests/fixture oracle riêng; hardware giữ nhánh owner | `docs/handoff/tv3_progress.md`, phiếu review riêng TV3 |
| TV4 | Schema/API/DP/checker/renderer và hợp nhất Docs 03/30–32 | Current-task/progress-log tổng hợp |

Các path TV1/TV2/TV3 là phân công tiếp theo, không có nghĩa module đã được tạo/owner đã nhận việc. Hết slice ghi commit, contract/candidate hashes, lệnh tái lập, kết quả/giới hạn và gate mở vào log riêng owner; gửi bàn giao để TV4 nhập bản tổng hợp. Thay contract cần proposal/review thay vì tự sửa ba đặc tả cùng lúc.

## Review TV2 đã tiếp nhận

[Review S0 TV2](../reviews/tv2_joint_contract_s0_review_20261002.md) được chép nguyên bytes từ `efe323779e899d860442d60f138575687e297888:docs/tv2_joint_contract_s0_review_20261002.md`; SHA-256 `6dcc002ee541f8f9bdc110a509999e854061b837a623f73d382410b6bd09a2da`. Trạng thái `REVIEWED_WITH_OPEN_GATES`, bản nháp AI cần TV2 con người kiểm; target là `8dcfe66`, không ký cho code `510f4e1`. Bản DEV hiện dùng endpoint trùng chính xác; quy tắc near-contact cho freeze vẫn PENDING như review yêu cầu.

## Slice tiếp nối: inner solve TV4 (02/10/2026)

Sau nền code `510f4e1` và docs `1991fca`, nhánh chia sẻ bổ sung `solve_fixed_configuration` và test/sources/handoff đồng bộ. Fetch HEAD mới nhất; không dừng ở baseline code 510f4e1. TV2 dùng [interface offline](../../backend/research/README.md) và [prompt cập nhật](tv2_prompt.md) để triển khai top-m thuộc ownership TV2. Hash case giữ gốc; inner verdict không là prefix/global verdict. Snapshot conflict ở trên là lịch sử; phải recheck với hashes merge thực. Owner đã có nhánh nghiên cứu cần merge nhánh chia sẻ trong checkout sạch, review docs cùng sửa và giữ log riêng owner; không blanket ours/theirs.

Trước buổi đối chiếu đầu tiên, dùng [bảng PENDING và mẫu bàn giao](pending_decisions.md). Phân công TV1–TV4 giữ nguyên theo xác nhận trưởng nhóm; mỗi TV gửi log riêng, TV4 tổng hợp. Phân công không thay lời xác nhận nhận việc hoặc sign-off của owner.

Bản phương pháp TV4 để review: [Docs 36](../support/36_joint_method_and_dp_argument.md), gồm state/recurrence/forget có giả thiết và witness synthetic tái lập. TV2 review cost/reference/điều kiện bằng nhau; TV3 đọc lập luận rồi oracle độc lập từ input thô; TV1 review giới hạn quality. Không dùng code checker làm oracle.
