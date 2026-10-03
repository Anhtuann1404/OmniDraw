# Prompt cho TV1 — ứng viên, dữ liệu và custody

Sao chép nội dung dưới đây vào chat TV1. [Hướng dẫn đồng bộ/conflict](README.md) là một phần của bàn giao.

```text
Tiếp tục OmniDraw với vai trò TV1, hỗ trợ trưởng nhóm. Dùng tài liệu repo làm nguồn chính.

Nguồn chia sẻ: origin/codex/tv4-pr3-slices. Code TV4 đã commit tại 510f4e108d29d5597cb7e82ed3dd53d2ba5c806a; fetch nhánh chia sẻ để có docs/prompt mới hơn. PR3 đã đóng; không mở lại backlog PR3. PR đóng, code merge vào main/develop và nghiệm thu là ba trạng thái riêng.

Trước tiên kiểm nhánh/HEAD/upstream/dirty/staged và git worktree list; bảo toàn công việc cũ. Fetch origin và xác nhận code commit trên là ancestor của nhánh chia sẻ. Nếu checkout đang dirty hoặc nhánh nền quá cũ, mở worktree/nhánh mới từ nguồn chia sẻ, không reset hoặc tự stash công việc:
git worktree add -b codex/tv1-research-candidates-20261002 ../OmniDraw-tv1-research origin/codex/tv4-pr3-slices
Nếu path/nhánh đã tồn tại, kiểm và reuse đúng checkout hoặc chọn tên mới. Không cherry-pick riêng commit code lên nền thiếu gateway/migration.

Đọc theo thứ tự: docs/README.md; docs/03_current-task.md; docs/30_research_development_plan.md; docs/31_joint_solver_contract.md; docs/32_research_api_and_artifact_contract.md; docs/handoff/README.md; docs/handoff/pending_decisions.md; backend/research/README.md; tests/research/README.md. Chỉ đọc Docs 29 khi cần đề cương, lịch sử khi có câu hỏi cụ thể. Dùng graphify để tìm quan hệ file rồi đối chiếu source thật; graph có thể chưa refresh semantic docs.

Hướng: đồng tối ưu chọn geometry thân/dấu và lịch nét trong tập ứng viên hữu hạn đã khóa; đo gap top-m và độ nhạy chuyển động. Đóng góp mô hình/phân tích có kiểm soát, không tuyên bố thuật toán hoàn toàn mới. TV4 có DP/checker DEV và 313 tests liên quan PASS, chưa là nghiệm thu độc lập. Policy/numeric/quality/parameters/freeze còn PENDING; HOLDOUT mới chưa mở.

Việc TV1:
1. Review fixtures DEV tự tạo của TV4; không coi chúng là glyph/font/dataset TV1 đã duyệt.
2. Cung cấp IDs/mapping NFD/grapheme, owner thân/dấu, candidates world-mm đã áp dụng style, body_order, precedence và nguồn/reference/anchor/license.
3. Chuẩn bị ca dấu chồng, marks below, interactions xa, zero/reverse và k khác nhau; delay có ID/type rõ, không tự điền k thiếu. Xuất manifest/candidate hashes thật, lý do lọc và source provenance; không đổi candidate set theo method.
4. Đề xuất quality bounds/correspondence trên DEV với reviewer, không tự ký hoặc dùng theta/radius/budget ví dụ thành ngưỡng đã duyệt. Gate cùng cho joint/baseline/oracle.
5. Lập split/custody/access-log đề xuất; corpus cũ chỉ supplemental. HOLDOUT niêm phong ở ngoài Git, không mở trước freeze và quy trình hai người. Font pilot giữ điều kiện và license/reference.
6. Làm slice nhỏ trong dataset/research/dev/ và fixture TV1 riêng; tests meaningful; ghi log docs/handoff/tv1_progress.md và bàn giao commit/hash/lệnh/kết quả/gate cho TV4. Không tự sửa core DP, baseline TV2 hoặc hardware/oracle TV3. Chỉ nhận oracle sau phân công lại và chuyển custody được ghi xác nhận.

Conflict: merge nhánh cũ feature/tv1-data-corpus với snapshot TV4 đã mô phỏng có 11 file conflict, gồm dataset README, current-task/progress-log, các docs redirect/migration, evidence CSV và hai history snapshots; danh sách/hash đầy đủ trong docs/handoff/README.md. Ưu tiên nhánh nghiên cứu mới từ nguồn chia sẻ. Nếu buộc merge nhánh cũ, dùng checkout tích hợp riêng và git diff --cc; giữ docs nguồn mới, chuyển cập nhật phù hợp về support/source, nhập tiến độ TV1 có provenance. Không ghi đè history hoặc nối evidence CSV add/add; giữ riêng hai bản và yêu cầu owner xử lý. Không chọn toàn bộ ours/theirs, không force-push. Sau giải chạy tests/research, handwriting validation và tests dataset/scan-validator liên quan.

Bắt đầu bằng tóm tắt tình trạng Git/contract đã xác minh rồi thực hiện slice TV1 đầu tiên. Các xác nhận nhận việc/sign-off cần ghi đúng bằng chứng, không giả định đã có.
Bàn giao theo mẫu trong docs/handoff/pending_decisions.md, ghi Q-ID, commit/evidence và gate còn mở. Phân công giữ nguyên: oracle TV3, custody TV1, baseline/runner TV2, DP/tích hợp TV4. Không tự ghi người khác đã nhận việc hoặc ký thay owner.
Review Docs 36 (docs/support/36_joint_method_and_dp_argument.md): witness áb là hình học synthetic, không glyph/reference/quality đã duyệt. Đề xuất ca thật và quality limits trong phần ownership của bạn; không chuyển ví dụ thành dataset/font được nghiệm thu.
Review TV4 ngày 03/10/2026 cho commit 1f583e9 nằm ở docs/reviews/tv4_tv1_candidates_review_20261003.md, verdict CHANGES_REQUESTED cho evidence/coverage. Nếu tiếp tục bàn giao này, xử lý F1–F6 trên nhánh TV1 đang có, không tạo lại/bỏ công việc cũ; sửa J/provenance, reference, k=2 boundary, interaction/contact coverage và metric Q03, gửi commit mới/manifest/artifacts để TV4 review lại. Tests PASS không đóng Q03/Q05/Q13, không mở HOLDOUT.
```

Ghi bàn giao theo [mẫu và bảng PENDING](pending_decisions.md), nêu Q-ID liên quan và evidence/commit thực. Phân công TV1–TV4 giữ nguyên theo trưởng nhóm; không tự chuyển oracle/custody hoặc ký thay owner. Các trạng thái PENDING chỉ đóng khi có review/xác nhận trong phạm vi.

## Follow-up TV1 sau review c970a18 — ưu tiên bản này so F1–F6 cũ

```text
TV4 đã review c970a18: F1–F5 CLOSED trong scope DEV, 13 TV1/190 research/34 handwriting PASS, manifest4c62fa2e… tái sinh đúng,8runs khớp exact ratios. Xem docs/reviews/tv4_tv1_candidates_rereview_c970a18_20261003.md.
Chỉ sửa F6 và F7 còn mở: (1) AR o-swash so compact +163.33%, o2-flourish +45% vượt10%; giới hạn nhãn ĐẠT vào clearance đã đo, ghi angle/overall quality NOT_EVALUATED hoặc cung cấp policy/AR0/class exemptions/measurements. Phân biệt body bbox height và x-height cho ascenders. Không freeze hoặc nới threshold. (2) evidence head_commit ff23687 chứa manifest cũ3ca; chạy lại clean snapshot c970a18 và ghi source/input commit+lệnh+môi trường đúng, commit evidence ở follow-up sau đó; không yêu cầu self hash. Giữ Q01–Q16 PROPOSED/PENDING, reference_geometry null/DEV_ONLY, TV3 NOT_RUN/HOLDOUT đóng. Không sửa code TV2/TV3/TV4 hoặc docs tổng hợp; log owner riêng. Bảo toàn dirty work, fetch nhánh chia sẻ và merge có kiểm tra conflict, không blanket ours/theirs. Bàn giao commit mới và evidence cho TV4 recheck, không tự claim nghiệm thu.
```
