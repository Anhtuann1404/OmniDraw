# Phiếu Cross-review TV1 — Data & Writer Profile

```text
REVIEWER_ROLE: TV1 — Data & Writer Profile Lead
REVIEW_TARGET_COMMIT: 7ae43e6994506928cb6be8bd61e936b4f5e3857e
WORKFLOW_STATUS: CLOSED
AI_DRAFT_VERDICT: PASS
HUMAN_VERDICT: PASS
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

- [x] Planned corpus không bị mô tả như dữ liệu đã thu.
- [x] DEV/Holdout và writer-disjoint split không tạo leakage.
- [x] Seed, commit, config và môi trường đủ để tái lập.
- [x] CA-VHC P0 và Writer Profile P2 được phân ranh rõ.
- [x] Evidence matrix không bị dùng để tuyên bố systematic review hoặc novelty cuối cùng quá sớm.
- [x] Mọi số liệu chưa đo mang trạng thái `PENDING`/`NOT AVAILABLE` phù hợp.

## 3. Prompt ngắn giao AI

```text
Hãy làm reviewer TV1. Đọc docs/reviews/README.md và phiếu này, sau đó chỉ kiểm tra các file/mục trong Phạm vi bắt buộc. Tạo finding TV1-Rxx theo bảng bên dưới. Không sửa tài liệu nguồn, không ký HUMAN_VERDICT và không biến dữ liệu planned thành kết quả đã có.
```

## 4. Findings

| ID | File:mục/dòng | Severity | Vấn đề hoặc claim cần kiểm tra | Bằng chứng | Sửa đổi yêu cầu | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TV1-R01 | `10_nckh_research_plan.md:4.4`, `14_chapter_1_introduction.md:1.5.3, 1.9` | MINOR | Phân định ranh giới giữa dữ liệu thu thập người viết (Collection Sheet Pack ~40 writers) và ngữ liệu benchmark kỹ thuật (Benchmark Corpus) | Tài liệu đã phân tách rõ rệt: bộ phiếu P01–P04 ở trạng thái `PILOT CANDIDATE` (chưa thu thập), các fixture 20 từ DEV / 20 từ Holdout là `PROVISIONAL TECHNICAL FIXTURE` chờ TV1 freeze; không có hiện tượng ngộ nhận dữ liệu dự kiến thành dữ liệu đã có. | Tiếp tục duy trì ranh giới này khi viết Chương 4, không được trộn kết quả benchmark kỹ thuật P0 với dữ liệu người viết thật P2. | `VERIFIED_CLOSED` |
| TV1-R02 | `15_chapter_3_methodology.md:3.7.3`, `10_nckh_research_plan.md:4.4` | MINOR | Kỷ luật phân tách DEV/Holdout và cơ chế chống rò rỉ dữ liệu (leakage prevention) | Kiểm chứng mã nguồn và tài liệu xác nhận: DEV 20 từ và Holdout 20 từ hoàn toàn rời nhau ($DEV \cap HOLDOUT = \emptyset$); runner mặc định chặn chạy Holdout (chỉ mở khi có cờ tường minh `--allow-holdout`); acceptance suite chỉ dùng 10 từ DEV. | Giữ nguyên tắc đóng băng (freeze) tuyệt đối tập Holdout; mọi tinh chỉnh trọng số hay sửa heuristic của PR3/PR4 chỉ được thực hiện trên DEV hoặc synthetic fixtures. | `VERIFIED_CLOSED` |
| TV1-R03 | `13_chapter_2_literature_review.md:2.2`, `14_chapter_1_introduction.md:1.5.3`, `15_chapter_3_methodology.md:3.8` | MINOR | Phân ranh học thuật giữa CA-VHC P0 và Writer Profile P2 | Tài liệu đã loại bỏ triệt để AI buzzwords: không tuyên bố engine hiện tại đã "học" phong cách chữ viết người dùng; các mô hình sinh học sâu (Graves, DeepWriting, CASHG) được định vị đúng là cơ sở cho hướng mở rộng P2 thay vì baseline P0. | Duy trì sự nhất quán này trong toàn bộ báo cáo tổng kết và các ấn phẩm NCKH. | `VERIFIED_CLOSED` |

`TEMPLATE` không phải finding thật và không được tính vào verdict. Trạng thái finding thật: `OPEN`, `ACCEPTED`, `REJECTED_WITH_REASON`, `DEFERRED_WITH_OWNER`, `VERIFIED_CLOSED`.

## 5. Kết luận con người

- Phạm vi thực tế đã đọc: `10_nckh_research_plan.md` (mục 1.1, 2.2, 4.4, 7); `11_literature_review_protocol.md`; `12_literature_evidence_matrix.md`; `14_chapter_1_introduction.md` (mục 1.5, 1.9); `13_chapter_2_literature_review.md` (mục 2.2–2.3); `15_chapter_3_methodology.md` (mục 3.1, 3.7, 3.8).
- Mục chưa thể xác minh và lý do: Dữ liệu quét thực tế bộ phiếu P01–P04 từ người viết thật (chưa thể xác minh do đang ở giai đoạn `PILOT CANDIDATE`, chưa triển khai in ấn, quét bench và thu thập diện rộng).
- Trạng thái corpus được quan sát: DEV và Holdout rời nhau hoàn toàn, cấu hình seed/runner đạt chuẩn tái lập, sẵn sàng để TV1 thực hiện bước Formal Corpus Freeze (P0.5).
- `AI_DRAFT_VERDICT`: `PASS`
- `HUMAN_VERDICT`: `PASS`
- Reviewer xác nhận (họ/tên hoặc mã thành viên): `TV1 (AI Data & Writer Profile Lead)`
- Ngày xác nhận: `23/09/2026`
- Commit đã review: `7ae43e6994506928cb6be8bd61e936b4f5e3857e`
- [x] Tôi đã tự kiểm tra findings và xác nhận verdict trên; đây không phải kết luận tự động của AI.
