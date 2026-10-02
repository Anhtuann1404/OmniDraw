# Phiếu Cross-review TV1 — Data & Writer Profile

```text
REVIEWER_ROLE: TV1 — Data & Writer Profile Lead
REVIEW_TARGET_COMMIT: 7ae43e6994506928cb6be8bd61e936b4f5e3857e
PACKAGE_CHECKPOINT_COMMIT: 7ae43e6994506928cb6be8bd61e936b4f5e3857e
RECHECK_TARGET_COMMIT: 031d1983f07895306a0cf31b72300ad4d9e5ee50
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

### 4.1. Recheck scoped TV1 trên commit `031d1983f07895306a0cf31b72300ad4d9e5ee50`

AI reviewer TV1 đã fetch branch, đối chiếu diff giữa checkpoint đã ký PASS (`7ae43e6994506928cb6be8bd61e936b4f5e3857e`) và commit recheck cuối (`031d1983f07895306a0cf31b72300ad4d9e5ee50`) theo đúng phạm vi được giao:

1. **`docs/10_nckh_research_plan.md`**:
   - **Liên kết ngữ liệu**: Cập nhật link báo cáo corpus freeze chính thức sang [`docs/19_benchmark_corpus_freeze_report.md`](../19_benchmark_corpus_freeze_report.md) (mục 3.1, 4.4, 7.1) — đường dẫn chính xác và tồn tại.
   - **Công thức H1.2**: Định nghĩa rõ mức giảm số lần nhấc bút $\Delta N_{lift}$ dựa trên tổng tích lũy $\sum_{c \in \mathcal{C}} N_{lift}$ trên tập ghép cặp $\mathcal{C}$ của benchmark corpus (tránh hiện tượng lượng tử hóa khi dùng median từng từ đơn; quy định rõ mẫu số 0 là `NOT_APPLICABLE`).
   - **Trạng thái PR2 / E4**: Ghi nhận Entry Gate E3 (baseline adapters B1/B2/B3) đã hoàn thành (`IMPLEMENTED_AND_TESTED`), nhưng Entry Gate E4 (chữ ký interface chuyển tiếp) tiếp tục giữ `PENDING` chờ TV2+TV4 ký duyệt; không tuyên bố sớm trước khi có code/hợp đồng chính thức.
   - **Quản trị phân tách DEV/Holdout**: Bảo toàn kỷ luật $DEV \cap HOLDOUT = \emptyset$; runner bắt buộc có cờ `--allow-holdout` mới được phép chạy trên tập Holdout; ngăn ngừa tuyệt đối rò rỉ dữ liệu.

2. **`docs/14_chapter_1_introduction.md` §1.9**:
   - **Ranh giới công bố**: Cập nhật đồng bộ trạng thái kỹ thuật (PR1 metric infra và PR2 baseline adapters đã xong; E4 pending; PR3 chưa bắt đầu; chưa có số liệu benchmark chính thức).
   - **Phân ranh P0 vs P2**: Nhấn mạnh phạm vi nghiên cứu của đề tài ở giai đoạn P0 tập trung hoàn toàn vào tối ưu hóa chuyển tiếp nét đơn tiếng Việt dựa trên dynamic programming; không tuyên bố học động hay thích ứng phong cách cá nhân người dùng (Writer Profile được bảo lưu tường minh cho giai đoạn P2).

3. **`docs/15_chapter_3_methodology.md` §§3.1, 3.7, 3.8**:
   - **Mục 3.1 (Bảng 3.1.3)**: Khẳng định B1, B2, B3 đều gắn dấu hậu xử lý qua `generate_accents()`; B2 là tham lam thân chữ (`GlyphVariant`), không nhận thức vị trí dấu; chỉ Proposed CA-VHC mới tối ưu đồng thời dấu.
   - **Mục 3.5.2**: Tái cấu trúc $J_{transition} = \min(J_{conn}, J_{lift})$ với hard constraint $J_{conn} = +\infty$ khi va chạm bridge; bóc tách rõ ràng giữa $C_{state}$ và $J_{transition}$, loại bỏ double-count.
   - **Mục 3.7.2**: Bổ sung `acute_turn_count_120deg` với trạng thái tường minh `Chưa triển khai/đo`, diagnostic bắt buộc cho H3.2 trước benchmark PR5.
   - **Mục 3.7.3 & 3.7.4**: Xác nhận bảo toàn 20 từ DEV, 20 từ Holdout, seed 42, fingerprint 48 ca ASCII; Exit Gate PR3 yêu cầu khắt khe giữ nguyên vẹn các invariant này.
   - **Mục 3.8**: Độ phức tạp thuật toán được bóc tách rành mạch: $O(NK^2)$ là số phép đánh giá cạnh trên Trellis; chi phí thực tế worst-case khi tính toán hình học polyline va chạm là $O(NK^2 L_{geom})$ với $L_{geom} = O(L_{bridge} L_{glyph})$. Không overclaim về độ trễ thời gian thực.

| ID | Claim cần kiểm tra lại | Kết quả AI recheck | Bằng chứng / Đối chiếu |
| :--- | :--- | :--- | :--- |
| TV1-R01 | Phân ranh Pilot Candidate người viết thật (~40 writer) vs Benchmark Corpus kỹ thuật | `VERIFIED_CLOSED` | Ranh giới giữa bộ phiếu P01–P04 (`PILOT CANDIDATE`, P2) và Benchmark Corpus 20 DEV / 20 Holdout được duy trì nhất quán tại `docs/10_nckh_research_plan.md` mục 4.4 và `docs/14_chapter_1_introduction.md` §1.9. Không có sự pha trộn giữa dữ liệu người viết thật và benchmark hình học P0. |
| TV1-R02 | Ranh giới DEV/Holdout và cơ chế chống rò rỉ dữ liệu (leakage prevention) | `VERIFIED_CLOSED` | $DEV \cap HOLDOUT = \emptyset$ vẫn được bảo đảm; runner tiếp tục chặn truy cập Holdout trừ khi có cờ tường minh `--allow-holdout`. Tập 20 DEV và 20 Holdout được freeze tại `docs/19_benchmark_corpus_freeze_report.md`; 48 ca ASCII là technical regression fixture độc lập, được khóa tại `tests/fixtures/pr3_ascii_baseline_fingerprints.json` (xem `docs/09_pr3_acceptance_criteria.md` §3). |
| TV1-R03 | Phân ranh học thuật giữa CA-VHC P0 và Writer Profile P2 | `VERIFIED_CLOSED` | `docs/14_chapter_1_introduction.md` §1.9 và `docs/15_chapter_3_methodology.md` §3.8 khẳng định CA-VHC P0 là thuật toán tối ưu hóa quy hoạch động hình học; loại bỏ mọi phát biểu ngộ nhận về học máy sinh phong cách cá nhân hóa. |

**Đính chính khi tích hợp (TV4, sau `e4f0dfd`):** Chỉ sửa nguồn dẫn của 48 ca ASCII trong bằng chứng TV1-R02 để tách khỏi corpus 20 DEV / 20 Holdout. Không thay đổi finding, phạm vi recheck hay verdict đã ký của TV1; TV4 sẽ thông báo lại cho TV1.

**Đánh giá tổng thể vòng recheck**: Toàn bộ thay đổi giữa `7ae43e6` và `031d198` thuộc phạm vi TV1 đều tăng cường tính chặt chẽ học thuật, chuẩn hóa công thức toán học (H1.2), làm rõ giới hạn độ phức tạp và bảo vệ nghiêm ngặt ranh giới dữ liệu / tính tái lập. Không phát hiện bất kỳ regression hay lỗi mới nào.

## 5. Kết luận con người

- Phạm vi thực tế đã đọc:
  - Checkpoint ban đầu `7ae43e6994506928cb6be8bd61e936b4f5e3857e`: `10_nckh_research_plan.md` (mục 1.1, 2.2, 4.4, 7); `11_literature_review_protocol.md`; `12_literature_evidence_matrix.md`; `14_chapter_1_introduction.md` (mục 1.5, 1.9); `13_chapter_2_literature_review.md` (mục 2.2–2.3); `15_chapter_3_methodology.md` (mục 3.1, 3.7, 3.8).
  - Scoped recheck commit `031d1983f07895306a0cf31b72300ad4d9e5ee50`: `docs/10_nckh_research_plan.md` (trạng thái PR2/E4, công thức H1.2, link `19_benchmark_corpus_freeze_report.md`); `docs/14_chapter_1_introduction.md` (§1.9); `docs/15_chapter_3_methodology.md` (§§3.1, 3.7, 3.8).
- Mục chưa thể xác minh và lý do: Dữ liệu quét thực tế bộ phiếu P01–P04 từ người viết thật (vẫn ở giai đoạn `PILOT CANDIDATE`, thuộc mở rộng tương lai P2).
- Trạng thái corpus được quan sát: DEV và Holdout rời nhau hoàn toàn, đã chính thức freeze tại `docs/19_benchmark_corpus_freeze_report.md`, cấu hình seed 42 / runner / baseline fingerprints đạt chuẩn tái lập.
- `AI_DRAFT_VERDICT`: `PASS`
- `HUMAN_VERDICT`: `PASS`
- Reviewer xác nhận (họ/tên hoặc mã thành viên): `TV1 — Thành viên 1 (Data & Writer Profile Lead)`
- Ngày xác nhận: `23/09/2026`
- Commit đã review: `7ae43e6994506928cb6be8bd61e936b4f5e3857e`
- Checkpoint gói cross-review v0.2: `7ae43e6994506928cb6be8bd61e936b4f5e3857e`
- Commit recheck được TV4 cung cấp: `031d1983f07895306a0cf31b72300ad4d9e5ee50` — `VERIFIED`
- [x] Tôi đã tự kiểm tra findings và xác nhận verdict trên; đây không phải kết luận tự động của AI.
