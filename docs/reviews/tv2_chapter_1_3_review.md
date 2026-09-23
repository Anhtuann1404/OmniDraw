# Phiếu Cross-review TV2 — Path Planning & Transition Cost

```text
REVIEWER_ROLE: TV2 — Stroke Optimization & Path Planning Lead
REVIEW_TARGET_COMMIT: 5e9c857e42021f8a48d45b1fdaefcfdb87e82ff3
PACKAGE_CHECKPOINT_COMMIT: 7ae43e6994506928cb6be8bd61e936b4f5e3857e
RECHECK_TARGET_COMMIT: e26af4fd2559c2e28672fff1a11865bf427683a8
WORKFLOW_STATUS: CLOSED
AI_DRAFT_VERDICT: PASS
HUMAN_VERDICT: PASS
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
| TV2-R01 | `docs/15_chapter_3_methodology.md`:3.5.2 (dòng 229–235) & `docs/10_nckh_research_plan.md`:3.5 (dòng 172) | MAJOR | Biểu thức $J_{transition}$ viết dạng tổng tuyến tính không điều kiện của cả 4 số hạng ($w_1 D_{penup} + w_2 N_{lift} + w_3 C_{curvature} + w_4 C_{bridge\_collision}$) gây hiểu nhầm rằng mọi bước chuyển tiếp đều chịu đồng thời cả chi phí pen-up lẫn curvature. | Khi nhấc bút ($\text{LIFT}$), $D_{penup} > 0$ và $N_{lift} = 1$, nhưng không có bridge nên $C_{curvature} = 0$ và $C_{bridge\_collision} = 0$. Ngược lại, khi nối nét ($\text{CONNECT}$), $D_{penup} = 0$ và $N_{lift} = 0$. Trong mã nguồn `backend/handwriting/engine.py:eval_transition` (dòng 680, 712) và `docs/05_ca_vhc_research_spec.md` (mục 2.3), transition cost được tính riêng cho `cost_lift` và `cost_conn`, sau đó chọn $\min$. | Tái cấu trúc công thức thành $J_{transition}(s', s) = \min(J_{conn}(s', s), J_{lift}(s', s))$ với định nghĩa tường minh cho từng nhánh: $J_{lift} = w_1 D_{penup} + w_2 N_{lift}$ và $J_{conn} = w_3 C_{curvature} + w_4 C_{bridge\_collision}$, kèm điều kiện $J_{conn} = +\infty$ khi vi phạm hard collision. | VERIFIED_CLOSED |
| TV2-R02 | `docs/10_nckh_research_plan.md`:4.3 (dòng 122–133) & `docs/15_chapter_3_methodology.md`:3.7.2 (dòng 286–295) | MAJOR | Metric `acute_turn_count_120deg` là tiêu chí nghiệm thu bắt buộc của giả thuyết H3.2 nhưng bị bỏ sót trong các bảng danh mục metric chính thức. | Trong `docs/10_nckh_research_plan.md` mục 3.3 (dòng 94) và Bảng 4.6 (dòng 236), giả thuyết H3.2 quy định điều kiện PASS bắt buộc là "không có góc > 120°" với biến phụ thuộc `acute_turn_count_120deg`. Tuy nhiên, metric này không xuất hiện trong Bảng 4.3 (file 10) và Bảng 3.7.2 (file 15), đồng thời chưa có code tính toán trong `backend/handwriting/metrics_evaluator.py`. | Bổ sung `acute_turn_count_120deg` vào Bảng 4.3 (file 10) và Bảng 3.7.2 (file 15) với trạng thái `Chưa triển khai / Diagnostic`; ghi nhận dependency cần bổ sung hàm tính góc gập nhọn trong `metrics_evaluator.py` trước khi chạy benchmark PR5. | VERIFIED_CLOSED |
| TV2-R03 | `docs/13_chapter_2_literature_review.md`:2.4 (dòng 33) & `docs/15_chapter_3_methodology.md`:3.8 (dòng 320–325) | MINOR | Phân tích độ phức tạp thời gian Viterbi $O(N K^2)$ chưa nêu rõ chi phí kiểm tra hình học polyline của từng transition edge. | Công thức $O(N K^2)$ giả định mỗi transition tốn $O(1)$. Thực tế trong CA-VHC, mỗi transition phải dựng candidate bridge và kiểm tra va chạm hình học (`bridge_collision_cost`) với các đoạn polyline của thân chữ và dấu, tốn chi phí $O(L_{geom})$ với $L_{geom} = L_{bridge} \cdot L_{glyph}$. Tổng chi phí tính toán là $O(N K^2 \cdot L_{geom})$. | Bổ sung ghi chú kỹ thuật tại mục 2.4 (Chương 2) và mục 3.8 (Chương 3) làm rõ rằng $O(N K^2)$ là số lượng cạnh transition trên Trellis; chi phí thời gian thực tế phụ thuộc thêm vào hàm kiểm tra va chạm $O(L_{geom})$, giải thích tầm quan trọng của việc khống chế số điểm sampled trong bridge. | VERIFIED_CLOSED |
| TV2-R04 | `docs/14_chapter_1_introduction.md`:1.4.1 (dòng 61) & `docs/15_chapter_3_methodology.md`:3.3.1 (dòng 137) | MINOR | Mô tả Baseline B2 (Greedy Contextual Heuristic) chưa nêu rõ cơ chế gắn dấu, dễ gây ngộ nhận B2 đồng thời chọn cả thân chữ và vị trí dấu. | Mã nguồn `backend/handwriting/baselines.py` (`greedy_contextual_baseline`, dòng 50–106) xác nhận B2 chỉ tham lam trên danh sách `GlyphVariant` (thân chữ). Dấu tiếng Việt trong B2 vẫn được gắn ở pha hậu xử lý qua `generate_accents()` giống hệt B3. Nếu không nêu rõ, người đọc có thể hiểu nhầm B2 là thuật toán tham lam có nhận thức dấu. | Bổ sung thuyết minh rõ ràng tại mục 1.4.1 (file 14) và Bảng 3.3.1 (file 15): cả ba baseline B1, B2 và B3 đều dùng chung cơ chế gắn dấu hậu xử lý bằng anchor tĩnh; chỉ duy nhất Proposed CA-VHC mới đưa ứng viên dấu vào không gian tối ưu đồng thời. | VERIFIED_CLOSED |
| TV2-R05 | `docs/10_nckh_research_plan.md`:3.1 (dòng 71) & Bảng 4.4 (dòng 220) | MINOR | Quy tắc nghiệm thu H1.2 (giảm `pen_lift_count` $\ge 35\%$) chưa chỉ định rõ phương pháp tổng hợp số liệu trên corpus (tổng tích lũy vs trung vị). | Số lần nhấc bút trên mỗi từ đơn ngắn là số nguyên rất nhỏ (thường 1–4). Nếu tính mức giảm theo trung vị (median) của từng từ, giá trị có thể bị lượng tử hóa và biến thiên giật cục. `docs/05_ca_vhc_research_spec.md` (dòng 128) quy định "Tổng số lần nhấc bút trên toàn bộ tập benchmark giảm ít nhất 35.0%". | Chuẩn hóa quy tắc tính mức giảm H1.2 tại mục 3.1 và chú thích Bảng 4.4 trong `10_nckh_research_plan.md`: tỷ lệ giảm phần trăm được tính trên tổng tích lũy $\sum \text{pen\_lift\_count}$ của toàn bộ corpus benchmark. | VERIFIED_CLOSED |
| TV2-R06 | `docs/15_chapter_3_methodology.md`:3.1.3 (dòng 76–77) & 3.7.4 (dòng 306) | MINOR | Cần duy trì tính độc lập nghiêm ngặt giữa việc hoàn tất PR2 baseline adapters (Gate E3) và việc ký duyệt interface chuyển tiếp (Gate E4). | TV2 đã hoàn tất PR2 baseline adapters trong `backend/handwriting/baselines.py` (73/73 tests PASS tại `tests/test_ca_vhc_baselines.py`), đáp ứng Entry Gate E3. Tuy nhiên, Entry Gate E4 (chữ ký `eval_transition(s_prev, s_next)`, `world_bbox` và `DiacriticConfig`) vẫn đang ở trạng thái `PENDING_PR2_E4`. | Giữ nguyên ranh giới trong Bảng 3.1.3 và Mục 3.7.4: ghi nhận E3 đã hoàn thành (`IMPLEMENTED_AND_TESTED`), nhưng nhấn mạnh E4 vẫn là dependency chưa đóng trước khi bắt đầu mã nguồn PR3; không coi review tài liệu là hoàn tất Gate E4. | VERIFIED_CLOSED |

`TEMPLATE` không phải finding thật và không được tính vào verdict. Trạng thái finding thật: `OPEN`, `ACCEPTED`, `REJECTED_WITH_REASON`, `DEFERRED_WITH_OWNER`, `VERIFIED_CLOSED`.

### 4.1. Recheck R01–R06 trên commit `e26af4fd2559c2e28672fff1a11865bf427683a8`

AI đã fetch `origin/feature/frontend-intergration`, xác minh branch chứa đúng commit recheck `e26af4fd2559c2e28672fff1a11865bf427683a8`, đọc diff và đối chiếu nội dung tại chính commit này. Commit chỉ sửa tài liệu; không thay đổi file trong `backend/` hoặc `tests/`.

| ID | Claim sửa đổi cần recheck | Kết quả AI recheck | Bằng chứng / blocker |
| :--- | :--- | :--- | :--- |
| TV2-R01 | Tách `CONNECT`/`LIFT`, không double-count legibility và không đổi B3 | `VERIFIED_CLOSED` | `docs/10_nckh_research_plan.md` mục 3.5, dòng 181–185 và `docs/15_chapter_3_methodology.md` mục 3.5.2, dòng 231–241 tại commit recheck tách $J_{conn}$/$J_{lift}$, hard reject bằng $+\infty$, tách state/transition legibility. Commit không sửa code/test; `tests/test_ca_vhc_baselines.py::test_b3_remains_the_default_frozen_geometry` vẫn khóa fingerprint B3 mặc định. |
| TV2-R02 | Ghi `acute_turn_count_120deg` là chưa triển khai và dependency trước PR5 | `VERIFIED_CLOSED` | `docs/10_nckh_research_plan.md` dòng 138 và `docs/15_chapter_3_methodology.md` dòng 299 ghi rõ `Chưa triển khai/đo`, diagnostic dự kiến, phải định nghĩa/kiểm thử/tích hợp evaluator trước PR5/H3.2. Finding tài liệu đã đóng; dependency code vẫn mở ngoài finding này. |
| TV2-R03 | Tách số cạnh DP $O(NK^2)$ khỏi chi phí hình học trên mỗi cạnh | `VERIFIED_CLOSED` | `docs/13_chapter_2_literature_review.md` mục 2.4, dòng 44 và `docs/15_chapter_3_methodology.md` mục 3.8, dòng 326–332 phân biệt $O(NK^2)$ phép đánh giá cạnh với $L_{geom}=O(L_{bridge}L_{glyph})$ và cận $O(NK^2L_{geom})$; candidate/transform/cache được tách riêng. |
| TV2-R04 | Làm rõ B1/B2/B3 gắn dấu hậu xử lý; B2 không tối ưu vị trí dấu | `VERIFIED_CLOSED` | `docs/14_chapter_1_introduction.md` mục 1.4.1, dòng 61 và `docs/15_chapter_3_methodology.md` mục 3.3.1, dòng 136–142 ghi B2 chỉ chọn `GlyphVariant`, không chọn vị trí dấu; B1/B2/B3 dùng `generate_accents()` hậu xử lý. |
| TV2-R05 | H1.2 dùng tỷ lệ trên tổng `pen_lift_count` của các ca ghép cặp | `VERIFIED_CLOSED` | `docs/10_nckh_research_plan.md` mục 3.1, dòng 76–82 định nghĩa $\Delta N_{lift}$ bằng chênh lệch hai tổng trên cùng tập ca ghép cặp $\mathcal C$, mẫu số 0 là `NOT_APPLICABLE`; mục 4.4 nhắc lại không dùng median tỷ lệ từng từ. |
| TV2-R06 | E3 đã PASS; E4 vẫn chờ ký duyệt riêng | `VERIFIED_CLOSED` | `docs/05_ca_vhc_research_spec.md` dòng 570, 650–651, 699–702; `docs/10_nckh_research_plan.md` dòng 33, 70–71, 102; `docs/14_chapter_1_introduction.md` dòng 139; `docs/15_chapter_3_methodology.md` dòng 76–77 và 312 đều ghi E3/PR2 hoàn tất nhưng E4 còn pending, PR3 chưa bắt đầu. |

**Đối chiếu disposition:** `docs/reviews/review_disposition.md` tại commit recheck vẫn khóa checkpoint gói v0.2 ở `7ae43e6994506928cb6be8bd61e936b4f5e3857e`, giữ riêng review gốc `5e9c857e42021f8a48d45b1fdaefcfdb87e82ff3`, chép đủ TV2-R01–R06 với disposition `ACCEPTED` và trạng thái `PENDING_TV2_RECHECK`. Kết quả AI recheck ở trên là bằng chứng để TV4 cập nhật cột recheck; TV2 không tự sửa sổ disposition.

**Phạm vi còn mở:** không còn finding bắt buộc mở trong TV2-R01–R06. `acute_turn_count_120deg` vẫn là dependency triển khai trước PR5; E4 vẫn chờ TV2+TV4 ký duyệt; PR3 và formal experiment chưa bắt đầu/hoàn tất. Recheck học thuật này không đóng các gate đó. TV2 con người phải tự kiểm tra bằng chứng trước khi điền verdict, tên, ngày, checkbox và chuyển workflow sang `CLOSED`.

## 5. Kết luận con người

- Phạm vi thực tế đã đọc: `docs/10_nckh_research_plan.md (RQ1/RQ3, B1/B2/B3, metric chuyển động); docs/14_chapter_1_introduction.md (mục 1.4); docs/13_chapter_2_literature_review.md (mục 2.4–2.6); docs/15_chapter_3_methodology.md (mục 3.3–3.5, 3.8); đối chiếu mã nguồn backend/handwriting/baselines.py, engine.py, metrics_evaluator.py và tests/test_ca_vhc_baselines.py`
- Mục chưa thể xác minh và lý do: `Hiệu năng thực tế của PR3 Trellis DAG và delayed-stroke scheduler (chưa có code trong engine, thuộc PR3 và PR4); số đo actual_draw_time_sec và c1_violation_count trên máy vẽ thật (chờ TV3 calibration và implementation).`
- Trạng thái PR2 được quan sát: `IMPLEMENTED_AND_TESTED (3 baseline adapters b1_static, b2_greedy, b3_current_trellis đã hoàn tất trong backend/handwriting/baselines.py và 73/73 tests PASS; Entry Gate E3 đạt, Entry Gate E4 chờ ký duyệt shared interface).`
- `AI_DRAFT_VERDICT`: `PASS` — TV2-R01–R06 đều được AI đối chiếu và đề xuất `VERIFIED_CLOSED`; chờ TV2 con người xác nhận.
- `HUMAN_VERDICT`: `PASS`
- Reviewer xác nhận (họ/tên hoặc mã thành viên): `TV2 — Thành viên 2`
- Ngày xác nhận: `23/09/2026`
- Commit đã review: `5e9c857e42021f8a48d45b1fdaefcfdb87e82ff3`
- Checkpoint gói cross-review v0.2: `7ae43e6994506928cb6be8bd61e936b4f5e3857e`
- Commit recheck được TV4 cung cấp: `e26af4fd2559c2e28672fff1a11865bf427683a8` — `VERIFIED`
- [x] Tôi đã tự kiểm tra findings và xác nhận verdict trên; đây không phải kết luận tự động của AI.
