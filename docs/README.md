# OmniDraw Documentation Hub

File này là điểm vào chính của toàn bộ tài liệu OmniDraw. Chọn nhóm theo mục đích thay vì tìm theo số thứ tự file.

## Bắt đầu nhanh

| Khi cần biết | Mở tài liệu |
| :--- | :--- |
| Nhóm đang làm gì | [`03_current-task.md`](03_current-task.md) |
| Các mốc phát triển | [`02_roadmap.md`](02_roadmap.md) |
| Kiến trúc phần mềm hiện tại | [`01_tech-stack.md`](01_tech-stack.md) |
| API và data contract | [`OmniDraw_API_Spec-4.md`](OmniDraw_API_Spec-4.md) |
| Câu hỏi nghiên cứu và kế hoạch thực nghiệm | [`10_nckh_research_plan.md`](10_nckh_research_plan.md) |
| Cross-review Chương 1–3 | [`reviews/README.md`](reviews/README.md) |
| Thiết kế phần cứng | [`hardware/00_hardware_index.md`](hardware/00_hardware_index.md) |

## Quản lý dự án

- [`02_roadmap.md`](02_roadmap.md): lộ trình, milestone và dependency.
- [`03_current-task.md`](03_current-task.md): backlog và trạng thái sprint hiện tại.
- [`04_progress-log.md`](04_progress-log.md): nhật ký tiến độ theo ngày.

## Phần mềm và contract

- [`01_tech-stack.md`](01_tech-stack.md): kiến trúc hệ thống và trạng thái triển khai.
- [`OmniDraw_API_Spec-4.md`](OmniDraw_API_Spec-4.md): API/data contract công khai.

## Nghiên cứu CA-VHC

- [`05_ca_vhc_research_spec.md`](05_ca_vhc_research_spec.md): RQ, giả thuyết, baseline và metric contract.
- [`06_audit_trellis_dag_report.md`](06_audit_trellis_dag_report.md): audit Trellis DAG hiện hành.
- [`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md): thiết kế `CompositionState` và diacritic-aware DAG.
- [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md): Entry/Exit Gate PR3.
- [`16_rq_code_metric_test_traceability.md`](16_rq_code_metric_test_traceability.md): truy vết RQ–code–metric–test và evidence ledger.
- [`17_pr3_implementation_readiness.md`](17_pr3_implementation_readiness.md): dependency PR2, bản đồ symbol, các lát cắt triển khai, test map và Definition of Ready cho PR3.
- [`18_pr3_e4_shared_transition_contract_draft.md`](18_pr3_e4_shared_transition_contract_draft.md): dự thảo giao diện chuyển tiếp TV2–TV4 để đóng Entry Gate E4; chưa được ký duyệt.

## Dữ liệu chữ viết tay

- [`08_handwriting_dataset_spec.md`](08_handwriting_dataset_spec.md): đặc tả corpus, Writer Profile và quản trị dữ liệu.
- [`collection_sheets/README.md`](collection_sheets/README.md): bộ phiếu P01–P04 và hướng dẫn sinh artifact.

## Tổng quan tài liệu và báo cáo

- [`10_nckh_research_plan.md`](10_nckh_research_plan.md): Research Freeze Pack và khung Chương 3–4.
- [`11_literature_review_protocol.md`](11_literature_review_protocol.md): protocol tìm kiếm và chọn nguồn.
- [`12_literature_evidence_matrix.md`](12_literature_evidence_matrix.md): evidence matrix.
- [`14_chapter_1_introduction.md`](14_chapter_1_introduction.md): Chương 1 — Mở đầu.
- [`13_chapter_2_literature_review.md`](13_chapter_2_literature_review.md): Chương 2 — Tổng quan.
- [`15_chapter_3_methodology.md`](15_chapter_3_methodology.md): Chương 3 — Phương pháp.
- [`reviews/README.md`](reviews/README.md): quy trình và phiếu cross-review.

## Phần cứng

Toàn bộ kiến trúc, cụm cơ khí, điện tử và validation plan nằm tại [`hardware/`](hardware/00_hardware_index.md).

## Quy tắc nguồn sự thật

1. Trạng thái công việc hiện tại lấy từ `03_current-task.md`.
2. Public API lấy từ `OmniDraw_API_Spec-4.md`; tài liệu nghiên cứu không tự động thay đổi API.
3. RQ, giả thuyết và ngưỡng nghiên cứu lấy từ `05_ca_vhc_research_spec.md` và `10_nckh_research_plan.md` sau khi qua freeze gate.
4. Code và automated tests là nguồn kiểm chứng trạng thái triển khai; thiết kế được duyệt không đồng nghĩa implementation đã hoàn thành.
5. Kết quả máy thật chỉ hợp lệ khi có log/calibration của TV3; timing mô phỏng không phải `actual_draw_time_sec` vật lý.

## Kế hoạch tái cấu trúc

Tài liệu đang được chuẩn bị chuyển sang các nhóm `project/`, `software/`, `research/`, `data/` và `hardware/`. Việc di chuyển được thực hiện trên worktree riêng để không làm thay đổi đường dẫn trong vòng cross-review hiện hành.
