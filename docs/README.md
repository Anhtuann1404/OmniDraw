# Tài liệu OmniDraw — hướng nghiên cứu hiện hành

**Cập nhật 02/10/2026:** TV4 thông báo GVHD đã đồng ý hướng nghiên cứu. Đây là thông tin phê duyệt hướng; không thay duyệt tham số, gate triển khai hoặc sign-off các thành viên.

## Đọc trước khi triển khai

| Tài liệu | Vai trò |
|---|---|
| [29 — Đề cương](29_research_proposal_consolidated.md) | Bản đối chiếu nội dung Google Docs đã tinh chỉnh, cấu trúc Mẫu 2 |
| [30 — Kế hoạch kỹ thuật](30_research_development_plan.md) | Ownership, slice, một bảng 8 tháng và phương án cắt phạm vi |
| [31 — Contract solver](31_joint_solver_contract.md) | Ứng viên/lịch khả thi, clearance, J, state, top-m, oracle và regret |
| [32 — API/artifact nghiên cứu](32_research_api_and_artifact_contract.md) | Schema draft và interface offline dự kiến; chưa là endpoint đã triển khai |
| [API sản phẩm](OmniDraw_API_Spec-4.md) | Contract kế thừa, đối chiếu route local, capability và kế hoạch tích hợp |
| [03 — Công việc hiện tại](03_current-task.md) | Việc cần làm của TV1–TV4 và quyết định chưa khóa |
| [33 — Chỉ mục migration](33_document_migration_index.md) | Trạng thái từng tài liệu, archive và phạm vi kiểm tra |

## Trọng tâm và phân công

Nghiên cứu mô hình đồng tối ưu hình học thân/dấu và lịch nét chữ tiếng Việt trong tập ứng viên hữu hạn; so staged top-m/beam, phân tích có lợi/bằng nhau, độ nhạy rho/lambda và chứng nhận regret trong phạm vi đã khóa. Áp dụng và phân tích có kiểm soát các kết quả chuẩn; không khẳng định phát minh DP mới.

- TV4: mô hình, DP, trace/SVG và tích hợp.
- TV2: tài liệu, cost, baseline, runner và phân tích.
- TV1: dữ liệu/split/custody và đồng chủ trì font.
- TV3: oracle/primitive độc lập, thiết bị và số đo.

Một thí điểm font có điều kiện. Writer Profile, Pareto và cắt tỉa mở rộng ngoài cam kết. Art Mode/thư tay là chức năng sản phẩm vẫn được giữ. Thiết bị nghiên cứu là máy vẽ phẳng hai trục khi sẵn sàng; không chốt dòng máy/cơ cấu qua tên đề tài.

## Các nhóm tài liệu

- [01 — Công nghệ](01_tech-stack.md), [02 — Roadmap](02_roadmap.md), [05 — Spec nghiên cứu](05_ca_vhc_research_spec.md), [07 — State](07_diacritic_aware_state_design.md), [10 — Kế hoạch nghiên cứu](10_nckh_research_plan.md), [16 — Traceability](16_rq_code_metric_test_traceability.md).
- [08 — Dữ liệu](08_handwriting_dataset_spec.md), [11 — Protocol tài liệu](11_literature_review_protocol.md), [12 — Evidence matrix](12_literature_evidence_matrix.md), [13–15 — Chương nghiên cứu](13_chapter_2_literature_review.md).
- [22 — Phạm vi mở rộng](22_nckh_extended_scope.md), [23 — Writer Profile backlog](23_rq4_writer_habit_study_protocol.md), [24 — Fontpilot](24_rq5_vietnamese_design_font_pilot.md).
- [Hardware](hardware/00_hardware_index.md), [Reviews](reviews/README.md), [Collection sheets](collection_sheets/README.md): giữ thiết kế/phiếu lịch sử theo nhãn phạm vi từng file.
- [04 — Nhật ký](04_progress-log.md), báo cáo 06/17–21/25/28 và `evidence/`: kết quả/checkpoint lịch sử, không tự nâng verdict cho hướng mới.
- [26 — Bản trao đổi](26_teacher_discussion_and_8_month_plan.md), [27 — Quyết định và provenance](27_supervisor_feedback_disposition.md): phân biệt quyết định nhóm/phản biện mô phỏng với thông báo đồng ý hướng thật.

## Quy tắc nguồn và tái lập

ID N-RQ1–4 hiện hành tương ứng MT1–4 của đề cương; ID RQ/PR cũ trong bằng chứng giữ nghĩa lịch sử. Tài liệu archived không là kế hoạch hiện hành. [Bản lưu trước sửa](history/20261002/ARCHIVE_NOTES.md) giữ cả thay đổi local đã có trước migration, kèm manifest SHA-256; không chỉ là bản từ HEAD.

Không đưa nội dung Holdout mới vào repo công khai; 20 từ cũ chỉ bổ sung. Tất cả parameter/ranking/tie/budget phải khóa trước mở. Không dùng mô phỏng làm số đo máy hoặc API draft làm implemented. Các PDF/SVG phiếu thu thập, dữ liệu CSV/JSON và script tạo phiếu cũ giữ nguyên; chúng không được tái phát hành thành kết quả mới trong lần cập nhật docs này.
