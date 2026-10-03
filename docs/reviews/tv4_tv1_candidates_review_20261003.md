# TV4 review bàn giao TV1 — ứng viên/fixtures và Q03/Q05/Q13

Ngày review 03/10/2026. Commit được review **1f583e9476d928c311be61ee6603ba832282fab7**, nhánh `origin/codex/tv1-research-candidates-20261002`. Merge-base với nhánh TV4 là `5b0f32854a659a0b64c87c50718e8448cef39d21`; TV1 không sửa core TV4, baseline hoặc hardware. Nguồn đặc tả: [Docs 30](../30_research_development_plan.md), [Docs 31](../31_joint_solver_contract.md), [Docs 32](../32_research_api_and_artifact_contract.md).

**Verdict: CHANGES_REQUESTED cho gói bàn giao/evidence/coverage; fixtures tương thích DEV được xác nhận.** Chưa merge nhánh TV1, chưa duyệt reference/font/quality, chưa đóng Q03/Q05/Q13 hoặc nghiệm thu solver. Phân công TV1–TV4 giữ nguyên, HOLDOUT đóng. DeepSeek APPROVED là kết quả TV1 báo; sáu file diff không chứa phiếu nguyên văn target/diff/verdict để TV4 xác minh phạm vi approval. AI review không thay oracle độc lập TV3 (vẫn NOT_RUN).

## Findings theo mức ưu tiên

### F1 — P1: J trong handoff không khớp commit/fixture/theta đã bàn giao

[Handoff TV1 L70–73](https://github.com/Anhtuann1404/OmniDraw/blob/1f583e9476d928c311be61ee6603ba832282fab7/docs/handoff/tv1_progress.md#L70) ghi 13.06 / 17.51 / 17.84 mm. Tái lập tại cùng commit với theta của tests (rho=.5, lambda=2), budget 10000ms/100000 states/10000 configurations/64MB cho cả no-forget/safe-forget:

| Ca | L_down | L_up | N_cycle | J tái lập |
|---|---:|---:|---:|---:|
| stacked-diacritic-01 | 15.338315569973318 | 8.816578365470374 | 4 | 27.746604752708503 |
| mark-below-02 | 12.23421246039155 | 12.84899559237939 | 4 | 26.658710256581244 |
| distant-interaction-03 | 16.337541126091548 | 15.269925772104335 | 5 | 33.972504012143716 |

Mỗi mode complete/OPTIMAL trong DEV primitive policy, cùng exact objective. [Evidence TV4](../evidence/tv1_review_1f583e9_20261003.json) giữ manifest/candidate hashes, theta/budget/cost-policy, coefficients, exact ratio và môi trường Python 3.14. TV1 báo Windows Python 3.13, nhưng khác biệt này chưa là bằng chứng giải thích các giá trị đã ghi. Tests TV1 chỉ kiểm OPTIMAL/order/validity, không assert các J trong handoff nên PASS không xác nhận bảng số đó.

**Đề nghị:** TV1 tái chạy, xuất artifact per-case từ đúng commit/manifest/config và sửa handoff. Nếu số cũ từ run khác, ghi provenance/scope của run đó, không gán cho commit hiện tại. Đây chặn chấp nhận bảng kết quả; không chứng minh fixture hay DP bị lỗi.

### F2 — P2, chặn Q03/H_geom: reference/source hashes mới là hash của tên

[Builder L196–199](https://github.com/Anhtuann1404/OmniDraw/blob/1f583e9476d928c311be61ee6603ba832282fab7/dataset/research/dev/candidate_builder.py#L196) và L448–451 khai báo `source_hash=canonical_hash("tv1-ref-font-open-sans-viet-v1")`; các glyph cũng hash tên như `tv1-glyph-a-std-v1`. Diff không cung cấp font/reference geometry, anchors/correspondence, x-height convention, source artifact hoặc license gắn với các ID này. Hash envelope/geometry thật và đúng không tự biến hash tên nguồn thành bằng chứng nguồn Open Sans.

**Đề nghị:** nếu tự vẽ DEV, ghi provenance tự tạo/mapping cụ thể và source digest có artifact/authoring record kiểm được; reference chưa có thì null hoặc nhãn rõ chưa sẵn sàng theo contract. Nếu dùng font thật, cung cấp nguồn/version/license, geometry/anchors/correspondence và hash artifact; chỉ sau đó TV2 dùng H_geom. Chưa gọi fixtures hiện tại là glyph/font/reference đã nghiệm thu.

### F3 — P2: test k=2 chưa phân biệt với k=1

[Test L228–265](https://github.com/Anhtuann1404/OmniDraw/blob/1f583e9476d928c311be61ee6603ba832282fab7/tests/research/test_tv1_candidates.py#L228) đặt tone trước thân owner 2, chỉ hoãn sau **một thân owner 1**. Hai nét `t_stem/t_crossbar` vẫn thuộc một thân, không phải hai chữ. Lịch này hợp lệ cả k=1, nên thay k=2 bằng 1 vẫn qua positive test hiện tại.

TV4 probe lịch `body0 → t_stem → t_crossbar → body2 → tone0`: k=2 PASS, k=1/k=0 FAIL deadline. Đây là ca hiện có có thể dùng để kiểm đúng ranh giới hai thân.

**Đề nghị:** thêm positive sau hoàn tất body owner 2 và negative cùng lịch tại k=1; giữ test k=0. Muốn kiểm ranh giới vượt k=2 cần owner 3 và lịch bắt đầu nó khi tone0 còn pending. Đơn vị deadline giữ theo Docs 31, không sửa solver để làm test PASS.

### F4 — P2: fixture “distant interaction” không kích hoạt frontier tương tác xa

Tại commit này, `compile_geometry` trả graph owners rỗng cho cả ba ca; ca 03 chỉ có một variant/owner và không có cặp candidates incompatible. Nó kiểm multi-body/k/contact geometry, nhưng không thể phát hiện DP quên một lựa chọn còn ảnh hưởng chữ xa chưa chọn.

**Đề nghị:** đổi nhãn/claim thành ca delayed-mark/multi-body nếu giữ geometry, và thêm ca có owner 0–2 xung đột với ít nhất một lựa chọn nhưng còn một lựa chọn khả thi. Assert cạnh 0–2/incompatible, feasibility/value và selection; so modes sau đó. Tests TV4 cũ có ví dụ tương tác xa nhưng không tự chuyển coverage đó thành coverage của dataset TV1.

### F5 — P2: contact khai báo không kiểm được CONNECT traversal hiện tại

[Builder L355–380](https://github.com/Anhtuann1404/OmniDraw/blob/1f583e9476d928c311be61ee6603ba832282fab7/dataset/research/dev/candidate_builder.py#L355) có contact hợp lệ tại (3,3.5), nhưng stem forward-only kết thúc (3.8,0); crossbar start/end là (3,3.5)/(3.8,3.5). Theo body_order stem→crossbar, endpoint cuối stem không trùng đầu crossbar ở cả hai hướng; CONNECT giữa chúng không thể thực hiện. Cả hai mode trên ba ca đều có 0 CONNECT. Test hiện tại chỉ assert contact count/location, không action chuyển tiếp.

Đây không làm declared-contact clearance geometry sai. **Đề nghị:** tách claim “contact geometry whitelist hợp lệ” khỏi “CONNECT schedule đã kiểm”. Nếu muốn ca CONNECT, tạo candidate có traversal/reversibility/order cho endpoint khớp, assert CONNECT hợp lệ và negative khi bỏ whitelist/đổi endpoint. Đổi shape/direction phải được TV1 review, không tự đảo stem để cứu test.

### F6 — P2: Q03 chưa có định nghĩa đo hoặc căn cứ duyệt ngưỡng

[Đề xuất L41–49](https://github.com/Anhtuann1404/OmniDraw/blob/1f583e9476d928c311be61ee6603ba832282fab7/docs/handoff/tv1_proposals_q03_q05_q13.md#L41) nêu Delta_y trong [.15,.45] x-height, góc 5/15 độ và AR 10%, nhưng chưa định nghĩa Delta_y là clearance, offset anchor hay displacement so reference; xử lý dấu dưới/dấu chồng, quy ước góc và relative AR cũng chưa đo được từ input đã cung cấp. Nếu là displacement, reference gốc có displacement 0; nếu là tọa độ signed, dấu dưới có y<0. Cần định nghĩa để tránh loại reference/dấu dưới ngoài ý muốn, không suy hiện tại chắc chắn vi phạm một metric chưa định nghĩa.

**Đề nghị:** định nghĩa metric/correspondence/x-height và phép đo dấu dưới/chồng, lập báo cáo DEV theo candidate, lý do chọn bounds và lý do lọc/hash trước–sau chung mọi method. Radius≤.25 cũng là đề xuất, chưa tự thành policy đã freeze. Giữ các số PROPOSED/PENDING, không kết luận bảo đảm lem mực/đẹp từ clearance đường tâm.

## Đánh giá theo Q-ID

| Gate | Kết luận TV4 tại commit đã review | Cần tiếp nối |
|---|---|---|
| Q03 | Có đề xuất, chưa đủ reference/measurement/quality evidence; còn PENDING | F2/F6, TV1 phối hợp TV2/TV3 |
| Q05 | k/precedence khai báo hợp schema, solver xử lý được; policy từng loại vẫn PENDING | F3, nguồn/lý do chọn k/precedence; rule dấu nặng thuộc tone và nhóm below cần ghi cách resolve rõ |
| Q13 | Nguyên tắc ngoài Git, freeze trước mở và hai người/access-log phù hợp hướng contract | Cỡ mẫu/split mới, vị trí/quyền/log template và người đối chiếu chưa có evidence hoàn tất; TV1 custody giữ nguyên, ưu tiên TV2/TV3 đối chiếu theo phân công |
| Q10/oracle | TV4 checker + hai modes đồng thuận trên ba ca | Không oracle TV3; DeepSeek/code review không thay primitive/enumerator độc lập |

Đề xuất ghi 8/8 tests ở phần kết luận trong khi handoff/source hiện có 11 tests; sửa cho cùng snapshot. Không yêu cầu mở HOLDOUT để trả lời findings hoặc tạo nguồn font chưa có. Các vấn đề về thói quen viết/âm vị học là giả thuyết/đề xuất cần nguồn/evidence TV1–TV2, không được TV4 ký chỉ từ hình học DEV.

## Những gì đã xác minh đạt

- Base `5b0f328`, ownership diff sáu file, không sửa core/nhánh owner khác.
- 11 tests TV1 PASS; cả bộ 188 research + 34 handwriting = **222 PASS**, 1 AnyIO warning có sẵn, 3.19s. TV1-only 11 PASS trong .13s. Tests dùng cùng tác giả checker TV4, không độc lập.
- Fixture và DEV manifest trùng bytes; builder tái sinh ra file tạm trùng bytes, manifest hash `c69090b7ceb1f7c70e7859836f82860111a19aecd7ff0800fbb7be8f7d8bbb81` hợp lệ. Không chạy main builder để ghi đè file của TV1.
- NFD/grouped owner, dấu chồng/dưới, body_order/precedence/reverse schema hoạt động; local geometry/selected geometry qua policy DEV hiện hành, hai modes cùng feasibility/value.
- Không HOLDOUT mới trong sáu file diff; proposal giữ gate mở dữ liệu sau freeze. Không suy không có dữ liệu trong diff thành đã kiểm custody ngoài repo.

## Tái lập và phạm vi thao tác

TV4 dùng `git archive 1f583e9476d928c311be61ee6603ba832282fab7` vào `/private/tmp/omnidraw-tv1-review-1f583e9`, chạy venv của repo nhưng cwd/PYTHONPATH trỏ snapshot archive; không checkout/merge/reset/stash dirty tree. Archive không là worktree được sửa, không phản ánh cập nhật TV1 sau hash này.

```sh
PYTHONPATH=backend /Users/yingjunn_/Study_/Nckh_2026-2027/OmniDraw/backend/venv/bin/python3 -m pytest tests/research/test_tv1_candidates.py -q
PYTHONPATH=backend /Users/yingjunn_/Study_/Nckh_2026-2027/OmniDraw/backend/venv/bin/python3 -m pytest tests/research backend/test_handwriting_validation.py -q
```

Chạy trong snapshot archive, không trên checkout TV4 thiếu sáu file TV1. [Evidence JSON](../evidence/tv1_review_1f583e9_20261003.json) và các probes dưới đây là review TV4, không ký độc lập. Tái sinh manifest qua `export_tv1_manifest(path_tạm)` rồi so bytes; tính bằng `load_manifest`, `solve_joint(case,Theta(rho=.5,lambda_mm=2),Budget(...),safe_forget=...)`; graph qua `compile_geometry(case).future_neighbors`. Lịch probe k=2 là thứ tự năm refs nêu F3, mọi action forward/LIFT.

TV1 sửa trên nhánh của mình, bàn giao commit mới/manifest hash/log artifact; TV4 review lại diff và findings trước tích hợp. Nhánh TV1 chưa merge vào nhánh chia sẻ/main/develop. Review này có thể gửi cho TV1 nhưng TV4 không tự nhắn sang chat khác trong turn này.
