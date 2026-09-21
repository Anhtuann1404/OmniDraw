# Phiếu Cross-review TV3 — Hardware & Physical Validation

```text
REVIEWER_ROLE: TV3 — Hardware, Calibration & Physical Validation Lead
REVIEW_TARGET_COMMIT: PENDING_CHECKPOINT_COMMIT
WORKFLOW_STATUS: NOT_STARTED
AI_DRAFT_VERDICT: PENDING
HUMAN_VERDICT: PENDING
```

Đọc [`README.md`](README.md) trước khi review. Phiếu này chỉ dành cho TV3.

## 1. Phạm vi bắt buộc

- [`../10_nckh_research_plan.md`](../10_nckh_research_plan.md): RQ3, clearance và physical feasibility.
- [`../14_chapter_1_introduction.md`](../14_chapter_1_introduction.md): mục 1.4.3, 1.8–1.9.
- [`../13_chapter_2_literature_review.md`](../13_chapter_2_literature_review.md): mục 2.5–2.6.
- [`../15_chapter_3_methodology.md`](../15_chapter_3_methodology.md): mục 3.1, 3.7–3.8.

## 2. Tiêu chí phải xác nhận

- [ ] Simulator time và `actual_draw_time_sec` trên máy thật không bị đánh đồng.
- [ ] Clearance hình học không bị mô tả thành bảo đảm an toàn vật lý.
- [ ] Claim về vận tốc, gia tốc, độ mượt và khả năng thi công có đúng mức bằng chứng.
- [ ] Calibration/smoke test chưa thực hiện được gắn `PENDING_TV3_CALIBRATION`.
- [ ] Hardware interface và telemetry được mô tả là hiện hành hay dự kiến một cách rõ ràng.
- [ ] Blocker phần cứng không ngăn việc review wording có thể kiểm tra bằng tài liệu.

> [!IMPORTANT]
> Có thể PASS wording tài liệu trong khi physical validation vẫn `PENDING_TV3_CALIBRATION`. Chỉ dùng verdict `BLOCKED` khi chính nội dung review không thể kết luận nếu thiếu dependency; phải ghi dependency và owner cụ thể.

## 3. Prompt ngắn giao AI

```text
Hãy làm reviewer TV3. Đọc docs/reviews/README.md và phiếu này, sau đó chỉ kiểm tra các file/mục trong Phạm vi bắt buộc. Tạo finding TV3-Rxx theo bảng bên dưới, tập trung tách simulator khỏi máy thật và chặn physical claim quá mức. Không sửa tài liệu nguồn, không ký HUMAN_VERDICT và không bịa số đo calibration.
```

## 4. Findings

| ID | File:mục/dòng | Severity | Vấn đề hoặc claim cần kiểm tra | Bằng chứng | Sửa đổi yêu cầu | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TV3-Rxx *(dòng mẫu — thay thế hoặc xóa)* | PENDING | PENDING | PENDING | PENDING | PENDING | `TEMPLATE` |

`TEMPLATE` không phải finding thật và không được tính vào verdict. Trạng thái finding thật: `OPEN`, `ACCEPTED`, `REJECTED_WITH_REASON`, `DEFERRED_WITH_OWNER`, `VERIFIED_CLOSED`.

## 5. Kết luận con người

- Phạm vi thực tế đã đọc: `PENDING`
- Mục chưa thể xác minh và lý do: `PENDING`
- Trạng thái calibration được quan sát: `PENDING_TV3_CALIBRATION`
- `AI_DRAFT_VERDICT`: `PENDING`
- `HUMAN_VERDICT`: `PENDING`
- Reviewer xác nhận (họ/tên hoặc mã thành viên): `PENDING`
- Ngày xác nhận: `PENDING`
- Commit đã review: `PENDING_CHECKPOINT_COMMIT`
- [ ] Tôi đã tự kiểm tra findings và xác nhận verdict trên; đây không phải kết luận tự động của AI.
