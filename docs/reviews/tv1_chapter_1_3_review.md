# Phiếu Cross-review TV1 — Data & Writer Profile

```text
REVIEWER_ROLE: TV1 — Data & Writer Profile Lead
REVIEW_TARGET_COMMIT: 7ae43e6994506928cb6be8bd61e936b4f5e3857e
WORKFLOW_STATUS: NOT_STARTED
AI_DRAFT_VERDICT: PENDING
HUMAN_VERDICT: PENDING
```

Đọc [`README.md`](README.md) trước khi review. Phiếu này chỉ dành cho TV1.

## 1. Phạm vi bắt buộc

- [`../10_nckh_research_plan.md`](../10_nckh_research_plan.md), tập trung corpus, split, leakage và reproducibility.
- [`../11_literature_review_protocol.md`](../11_literature_review_protocol.md).
- [`../12_literature_evidence_matrix.md`](../12_literature_evidence_matrix.md).
- [`../14_chapter_1_introduction.md`](../14_chapter_1_introduction.md): mục 1.5 và 1.9.
- [`../13_chapter_2_literature_review.md`](../13_chapter_2_literature_review.md): mục 2.2–2.3.
- [`../15_chapter_3_methodology.md`](../15_chapter_3_methodology.md): mục 3.1, 3.7 và 3.8.

## 2. Tiêu chí phải xác nhận

- [ ] Planned corpus không bị mô tả như dữ liệu đã thu.
- [ ] DEV/Holdout và writer-disjoint split không tạo leakage.
- [ ] Seed, commit, config và môi trường đủ để tái lập.
- [ ] CA-VHC P0 và Writer Profile P2 được phân ranh rõ.
- [ ] Evidence matrix không bị dùng để tuyên bố systematic review hoặc novelty cuối cùng quá sớm.
- [ ] Mọi số liệu chưa đo mang trạng thái `PENDING`/`NOT AVAILABLE` phù hợp.

## 3. Prompt ngắn giao AI

```text
Hãy làm reviewer TV1. Đọc docs/reviews/README.md và phiếu này, sau đó chỉ kiểm tra các file/mục trong Phạm vi bắt buộc. Tạo finding TV1-Rxx theo bảng bên dưới. Không sửa tài liệu nguồn, không ký HUMAN_VERDICT và không biến dữ liệu planned thành kết quả đã có.
```

## 4. Findings

| ID | File:mục/dòng | Severity | Vấn đề hoặc claim cần kiểm tra | Bằng chứng | Sửa đổi yêu cầu | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TV1-Rxx *(dòng mẫu — thay thế hoặc xóa)* | PENDING | PENDING | PENDING | PENDING | PENDING | `TEMPLATE` |

`TEMPLATE` không phải finding thật và không được tính vào verdict. Trạng thái finding thật: `OPEN`, `ACCEPTED`, `REJECTED_WITH_REASON`, `DEFERRED_WITH_OWNER`, `VERIFIED_CLOSED`.

## 5. Kết luận con người

- Phạm vi thực tế đã đọc: `PENDING`
- Mục chưa thể xác minh và lý do: `PENDING`
- `AI_DRAFT_VERDICT`: `PENDING`
- `HUMAN_VERDICT`: `PENDING`
- Reviewer xác nhận (họ/tên hoặc mã thành viên): `PENDING`
- Ngày xác nhận: `PENDING`
- Commit đã review: `7ae43e6994506928cb6be8bd61e936b4f5e3857e`
- [ ] Tôi đã tự kiểm tra findings và xác nhận verdict trên; đây không phải kết luận tự động của AI.
