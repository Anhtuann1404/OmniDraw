# Prompt hiện hành cho TV1 — sau recheck ce3f92d

Sao chép nội dung dưới đây vào chat TV1. Lịch sử findings ở docs/reviews, không là backlog sửa lại.

```text
Tiếp tục OmniDraw với vai trò TV1, phân công dữ liệu/ứng viên/split/custody và đồng chủ trì font pilot giữ nguyên. Fetch origin/codex/tv4-pr3-slices và dùng docs hiện hành làm nguồn chính. Kiểm Git HEAD/branch/upstream/dirty/worktrees; bảo toàn thay đổi có sẵn, không reset/stash/ghi đè. Dùng nhánh owner nghiên cứu riêng, không sửa solverTV4/baselineTV2/oraclehardwareTV3.

Đọc docs/README.md,03_current-task.md,30_research_development_plan.md,31_joint_solver_contract.md,32_research_api_and_artifact_contract.md, handoff/README.md và pending_decisions.md. Dùng graphify định vị nguồn rồi kiểm source đúngcommit; chỉ đọc Docs29/lịch sử khi cần đề cương/câu hỏi cụ thể. PR3đãđóng; publish/merge/nghiệmthu là ba trạng thái riêng.

TV4 đã recheck ce3f92dafa156bf6dbf605c7026bbdd6c0f3b448: F1–F7 CLOSED trong scope synthetic DEV, không cần làm lại. Xem docs/reviews/tv4_tv1_final_recheck_ce3f92d_20261003.md. Manifest4c62fa2e… giữ nguyên;4ca và8runs khớp exact ratios;224tests (190research+34handwriting)PASS. Đây là bàn giao DEV có giới hạn, chưa quality/font/solver acceptance hoặc merge.

Bước tiếp theo theo kế hoạch: chuẩn bị nguồn font/reference/anchor/license và measurement policy cho Q03/Q16 để nhóm review, khai báo baseline/class/AR0=0 NA khi cần, không tự nạp font giả hoặc claim đã có sign-off. Hai flourish vượtAR10% chỉ DEV_ONLY_INTERACTION_PROBE_EXEMPT, dùng kiểm tương tác xa; qualityfilter nếu áp phải thực hiện trước khóaG, hash lại đúng artifact, không lọc ngầm giữa các phương pháp. GócNOT_EVALUATED/overallqualityPENDING; không nới hoặc freeze threshold. Chưa có yêu cầu mở hay truy cập HOLDOUT.

Q01 nhận oracleTV3 đã CLOSED_ACKNOWLEDGEMENT_ONLY tại d84c241 theo reviewTV4; oracleimplementation còn O1–O5 CHANGES_REQUESTED/Q10PENDING. Đồng bộ câu tất cả16gatesPENDING/chờTV3nhậnviệc trong logTV1 khi cập nhật tiếp. Cácgatekhác giữPROPOSED/PENDING, HOLDOUTniêmphongngoàiGit; CA-VHCcũ chỉ supplemental. BộkiểmTV4khôngthayoracleđộc lập.

Mỗi slice ghi logowner docs/handoff/tv1_progress.md: sourcecommit/artifactpolicy/hashes/lệnh/môi trường/budget/kếtquả/phạmviclaim/gate/bước tiếp. Evidence ghi source/inputcommit thực, xuất từ runner cóversion khi triển khai, không selfhash giả; commit/push nhánhowner rồi gửi fullcommit choTV4recheck. Không cùng sửa docs tổng hợp; TV4 nhập disposition. Conflict giải theo nội dung/evidence, không blanket ours/theirs. Không ký thay người khác hoặc tự đổi testPASSthànhnghiệmthu.
```
