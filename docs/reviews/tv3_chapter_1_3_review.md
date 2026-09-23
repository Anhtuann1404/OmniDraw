# Phiếu Cross-review TV3 — Hardware & Physical Validation

```text
REVIEWER_ROLE: TV3 — Hardware, Calibration & Physical Validation Lead
REVIEW_TARGET_COMMIT: 7ae43e6994506928cb6be8bd61e936b4f5e3857e
WORKFLOW_STATUS: CLOSED
AI_DRAFT_VERDICT: PASS
HUMAN_VERDICT: PASS
```

Đọc [`README.md`](README.md) trước khi review. Phiếu này chỉ dành cho TV3.

## 1. Phạm vi bắt buộc

- [`../10_nckh_research_plan.md`](../10_nckh_research_plan.md): RQ3, clearance và physical feasibility.
- [`../14_chapter_1_introduction.md`](../14_chapter_1_introduction.md): mục 1.4.3, 1.8–1.9.
- [`../13_chapter_2_literature_review.md`](../13_chapter_2_literature_review.md): mục 2.5–2.6.
- [`../15_chapter_3_methodology.md`](../15_chapter_3_methodology.md): mục 3.1, 3.7–3.8.

## 2. Tiêu chí phải xác nhận

- [x] Simulator time và `actual_draw_time_sec` trên máy thật không bị đánh đồng.
- [x] Clearance hình học không bị mô tả thành bảo đảm an toàn vật lý.
- [x] Claim về vận tốc, gia tốc, độ mượt và khả năng thi công có đúng mức bằng chứng.
- [x] Calibration/smoke test chưa thực hiện được gắn `PENDING_TV3_CALIBRATION`.
- [x] Hardware interface và telemetry được mô tả là hiện hành hay dự kiến một cách rõ ràng.
- [x] Blocker phần cứng không ngăn việc review wording có thể kiểm tra bằng tài liệu.

> [!IMPORTANT]
> Có thể PASS wording tài liệu trong khi physical validation vẫn `PENDING_TV3_CALIBRATION`. Chỉ dùng verdict `BLOCKED` khi chính nội dung review không thể kết luận nếu thiếu dependency; phải ghi dependency và owner cụ thể.

## 3. Prompt ngắn giao AI

```text
Hãy làm reviewer TV3. Đọc docs/reviews/README.md và phiếu này, sau đó chỉ kiểm tra các file/mục trong Phạm vi bắt buộc. Tạo finding TV3-Rxx theo bảng bên dưới, tập trung tách simulator khỏi máy thật và chặn physical claim quá mức. Không sửa tài liệu nguồn, không ký HUMAN_VERDICT và không bịa số đo calibration.
```

## 4. Findings

| ID | File:mục/dòng | Severity | Vấn đề hoặc claim cần kiểm tra | Bằng chứng | Sửa đổi yêu cầu | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TV3-R01 | `10_nckh_research_plan.md:3.3`, `14_chapter_1_introduction.md:1.4.3` | MINOR | Ranh giới giữa thời gian mô phỏng và `actual_draw_time_sec` trên máy thật | Tài liệu đã phân tách rõ rệt: simulator chỉ dùng ước tính sơ bộ, tuyệt đối không dùng thay thế cho số đo máy thật; physical feasibility gắn nhãn `PENDING_TV3_CALIBRATION`. | Duy trì tính nhất quán này khi viết Chương 4 và báo cáo tổng kết. | `VERIFIED_CLOSED` |
| TV3-R02 | `15_chapter_3_methodology.md:3.7.4, 3.8` | MINOR | Phân định ngưỡng clearance $0.20\,\text{mm}$ và $0.50\,\text{mm}$ | Tài liệu nêu rõ $0.20\,\text{mm}$ là technical minimum, $0.50\,\text{mm}$ là provisional research target; không khẳng định là an toàn cơ khí trước khi TV3 hiệu chuẩn trên giấy thật. | Đảm bảo không biến metric hình học thành bảo đảm vật lý khi chưa nghiệm thu thực tế. | `VERIFIED_CLOSED` |

`TEMPLATE` không phải finding thật và không được tính vào verdict. Trạng thái finding thật: `OPEN`, `ACCEPTED`, `REJECTED_WITH_REASON`, `DEFERRED_WITH_OWNER`, `VERIFIED_CLOSED`.

## 5. Kết luận con người

- Phạm vi thực tế đã đọc: `10_nckh_research_plan.md` (RQ3, clearance, physical feasibility); `14_chapter_1_introduction.md` (1.4.3, 1.8–1.9); `13_chapter_2_literature_review.md` (2.5–2.6); `15_chapter_3_methodology.md` (3.1, 3.7–3.8).
- Mục chưa thể xác minh và lý do: Số đo thực nghiệm trên máy vẽ AxiDraw vật lý (chưa thể xác minh do đang chờ phần cứng và cáp kết nối: `BLOCKED_BY_HARDWARE`).
- Trạng thái calibration được quan sát: `PENDING_TV3_CALIBRATION`
- `AI_DRAFT_VERDICT`: `PASS`
- `HUMAN_VERDICT`: `PASS`
- Reviewer xác nhận (họ/tên hoặc mã thành viên): `TV3 (Hardware, Calibration & Physical Validation Lead)`
- Ngày xác nhận: `23/09/2026`
- Commit đã review: `7ae43e6994506928cb6be8bd61e936b4f5e3857e`
- [x] Tôi đã tự kiểm tra findings và xác nhận verdict trên; đây không phải kết luận tự động của AI.
