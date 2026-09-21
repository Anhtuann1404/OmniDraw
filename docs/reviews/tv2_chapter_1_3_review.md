# Phiếu Cross-review TV2 — Path Planning & Transition Cost

```text
REVIEWER_ROLE: TV2 — Stroke Optimization & Path Planning Lead
REVIEW_TARGET_COMMIT: 5e9c857e42021f8a48d45b1fdaefcfdb87e82ff3
WORKFLOW_STATUS: NOT_STARTED
AI_DRAFT_VERDICT: PENDING
HUMAN_VERDICT: PENDING
```

Đọc [`README.md`](README.md) trước khi review. Phiếu này chỉ dành cho TV2.

## 1. Phạm vi bắt buộc

- [`../10_nckh_research_plan.md`](../10_nckh_research_plan.md): RQ1/RQ3, B1/B2/B3 và metric chuyển động.
- [`../14_chapter_1_introduction.md`](../14_chapter_1_introduction.md): mục 1.4.
- [`../13_chapter_2_literature_review.md`](../13_chapter_2_literature_review.md): mục 2.4–2.6.
- [`../15_chapter_3_methodology.md`](../15_chapter_3_methodology.md): mục 3.3–3.5 và 3.8.

## 2. Tiêu chí phải xác nhận

- [ ] B1/B2/B3 có định nghĩa so sánh được và không nhầm với Proposed CA-VHC.
- [ ] $C_{state}$ và $J_{transition}$ không double-count.
- [ ] Viterbi recurrence, backpointer và độ phức tạp được mô tả đúng.
- [ ] Pen-up, pen-lift, curvature và acute-turn metrics có định nghĩa nhất quán.
- [ ] Ranh giới code hiện hành, PR2 và PR3 được gắn trạng thái đúng.
- [ ] Claim hiệu năng chưa vượt quá evidence hiện có.

> [!IMPORTANT]
> PASS tài liệu trong phiếu này không đồng nghĩa PR2 baseline adapters đã hoàn tất hoặc Entry Gate PR3 đã mở. Nếu interface PR2 chưa đủ để kiểm tra một claim, ghi finding/blocker riêng.

## 3. Prompt ngắn giao AI

```text
Hãy làm reviewer TV2. Đọc docs/reviews/README.md và phiếu này, sau đó chỉ kiểm tra các file/mục trong Phạm vi bắt buộc. Tạo finding TV2-Rxx theo bảng bên dưới, ưu tiên tính đúng của B1/B2/B3, J_transition, Viterbi và metric chuyển động. Không sửa tài liệu nguồn, không ký HUMAN_VERDICT và không coi review tài liệu là hoàn tất PR2.
```

## 4. Findings

| ID | File:mục/dòng | Severity | Vấn đề hoặc claim cần kiểm tra | Bằng chứng | Sửa đổi yêu cầu | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TV2-Rxx *(dòng mẫu — thay thế hoặc xóa)* | PENDING | PENDING | PENDING | PENDING | PENDING | `TEMPLATE` |

`TEMPLATE` không phải finding thật và không được tính vào verdict. Trạng thái finding thật: `OPEN`, `ACCEPTED`, `REJECTED_WITH_REASON`, `DEFERRED_WITH_OWNER`, `VERIFIED_CLOSED`.

## 5. Kết luận con người

- Phạm vi thực tế đã đọc: `PENDING`
- Mục chưa thể xác minh và lý do: `PENDING`
- Trạng thái PR2 được quan sát: `PENDING` *(không suy ra từ verdict tài liệu)*
- `AI_DRAFT_VERDICT`: `PENDING`
- `HUMAN_VERDICT`: `PENDING`
- Reviewer xác nhận (họ/tên hoặc mã thành viên): `PENDING`
- Ngày xác nhận: `PENDING`
- Commit đã review: `5e9c857e42021f8a48d45b1fdaefcfdb87e82ff3`
- [ ] Tôi đã tự kiểm tra findings và xác nhận verdict trên; đây không phải kết luận tự động của AI.
