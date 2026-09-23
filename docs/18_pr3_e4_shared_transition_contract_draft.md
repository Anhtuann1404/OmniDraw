# OmniDraw — Dự thảo hợp đồng giao diện chuyển tiếp E4 cho PR3

**Trạng thái:** `DRAFT — TV2/TV4 REVIEW REQUIRED`

**Ngày:** 2026-09-23

**Owner đề xuất:** TV4 (composition) và TV2 (motion/transition)

**Phạm vi:** hợp đồng nội bộ của CA-VHC PR3; không thay đổi public API, renderer hoặc code production.

> Tài liệu này chuẩn bị quyết định E4, **không phải biên bản ký duyệt**. E4 vẫn `WAITING_TV2_TV4_SIGNOFF`; PR3 production implementation chưa được mở. Review Bước B về công thức là `PASS`, nhưng chưa khóa giao diện callable và migration từ code PR2.

## 1. Bằng chứng nền và nguồn ưu tiên

- PR2 B1/B2/B3 đã merge qua PR #32 (merge commit `bcc1a7a`) và có `backend/handwriting/baselines.py`, runner method tags, `tests/test_ca_vhc_baselines.py`. Kiểm tra trên checkout ngày 2026-09-23: `backend/venv/bin/python3 -m pytest -q tests backend/test_handwriting_validation.py` → **115 passed, 1 warning** (warning thư viện Starlette/AnyIO).
- `backend/handwriting/engine.py:eval_transition()` hiện nhận hai `GlyphVariant`, các điểm/tangent và nét chính ở world frame; trả `(total_cost, is_conn)`. Hàm cộng `weights[4] * w.cost_legibility` vào cả lựa chọn nối và nhấc bút. `optimize_word_dag()` cộng legibility của state đầu tại layer 0.
- [`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md) khóa công thức `C_state = internal_collision + legibility + placement` và `J_transition = pen-up + lift + curvature + bridge_collision`, không double-count. [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md) là nguồn chuẩn Entry/Exit Gate. Nếu dự thảo này khác hai tài liệu trên, phải giải quyết mâu thuẫn trước khi ký E4.
- Phiếu cross-review Chương 1–3 tại `docs/reviews/` là quy trình học thuật riêng, không phải chữ ký E4.
- Dòng trạng thái E4 trong Chương 3 được chỉnh sau `REVIEW_TARGET_COMMIT` của gói cross-review v0.2; reviewer cần recheck mục 3.1.3 trên bản mới trước khi ký verdict học thuật. Không tự sửa hoặc ký phiếu thay reviewer.

## 2. Hợp đồng đề xuất (chưa phê duyệt)

### 2.1. Đầu vào, đầu ra và khả năng tương thích

Giữ nguyên `eval_transition()` và `optimize_word_dag()` hiện hành cho B3/default trong giai đoạn tích hợp. PR3 nên có một entry point nội bộ nhận **hai `CompositionState` đã chọn làm ứng viên**, hình học world của mỗi state, trọng số transition và một `DiacriticConfig` duy nhất; tên symbol và vị trí module là quyết định E4 của TV2/TV4. Không truyền payload UI/API vào cost function.

Đầu ra nội bộ cần đủ để Viterbi so sánh và kiểm thử: `total_cost` hữu hạn, không âm; `is_connected`/`is_lift`; breakdown `D_penup_mm`, `N_lift`, `C_curvature`, `C_bridge_collision`; và hình học bridge ứng viên hoặc tham chiếu tất định đến cùng builder mà renderer dùng. `total_cost` là chi phí của **quyết định được chọn**, không trộn các thành phần của phương án nối và phương án nhấc bút. `C_state` không nằm trong kết quả transition.

Đề xuất pseudo-signature, **không phải API đã khóa**:

```python
evaluate_composition_transition(
    prev_state, curr_state, prev_world, curr_world,
    transition_weights, diacritic_config,
) -> TransitionResult
```

`prev_world`/`curr_world` là geometry snapshot nội bộ gồm điểm vào/ra, tangent, base strokes, diacritic strokes và bounding box theo cùng một frame. Nếu muốn giữ chữ ký `eval_transition()` và mở rộng bằng keyword arguments, TV2/TV4 phải chứng minh B3/default không đổi; không tự đổi chữ ký public renderer.

### 2.2. Quy ước tọa độ và va chạm

- `DiacriticCandidate.strokes_local` và `bounds_local` chỉ thuộc frame cục bộ của glyph. Code hiện hành dùng `stroke * scale_vec + offset` (scale X/Y có thể khác nhau) trước khi kiểm tra bridge hoặc render. Vì vậy E4 phải khóa **một transform helper** dùng chung cho base, dấu, điểm vào/ra và tangent; không được dùng scalar `scale` trong một nhánh và `scale_vec` trong nhánh khác.
- `world_bbox` của dấu phải tính từ **world strokes sau transform**, không cộng offset lần hai vào local bbox. Bbox chỉ dùng broad-phase; phán quyết collision/clearance phải dựa trên hình học polyline/segment ở world frame để tránh false positive/negative.
- Bridge nối hai ký tự được xây ở world frame từ cùng điểm/tangent và cùng builder mà renderer thực sự dùng. Kiểm tra bridge với bốn tập nét: base và dấu của state trước, base và dấu của state sau. Quy tắc bỏ qua vùng tiếp xúc hợp lệ ở hai đầu bridge phải nhất quán với code hiện hành.
- Đơn vị của khoảng cách world là **mm trên giấy**; `D_penup_mm` và clearance có đơn vị mm, còn curvature/collision/cost đã ánh xạ là vô hướng. TV4 đề xuất gọi dữ liệu local của `engine.py` là **glyph-local units**, với `scale_vec` mang đơn vị mm/glyph-unit và `offset` mang đơn vị mm. Pseudocode scalar `scale` và cách gọi local là mm tại Docs 07 cần được chỉnh sau khi TV2+TV4 đồng ý, không để hai quy ước cùng tồn tại trong implementation.

### 2.3. Phân bổ chi phí và tránh double-count

`C_state(s)` do TV4 sở hữu: internal base–diacritic/mark–mark collision, base legibility và placement penalty của dấu, mỗi thành phần cộng đúng một lần cho **state được chọn**. `J_transition(prev, curr)` do TV2/TV4 đồng thiết kế: pen-up distance, lift, curvature và bridge collision với base/dấu của hai state; không cộng lại legibility hoặc placement của `curr`.

**Điểm cần quyết định khi migrate:** `eval_transition()` hiện cộng `weights[4] * curr.cost_legibility` vào transition. Với PR3, khoản này phải được chuyển vào `C_state`; không được gọi nguyên hàm rồi cộng `C_state` đầy đủ. Có thể dùng adapter tách phần này hoặc triển khai transition core mới; TV2/TV4 chọn phương án sau khi chạy synthetic optimality và 48/48 ASCII fingerprints. B3/default giữ nguyên đường chạy cũ cho đến khi parity được chứng minh. `force_lift` và tie-break tất định cũng phải được kiểm tra riêng.

Nếu một candidate vi phạm hard constraint hoặc geometry/weight/cost là NaN, Inf, âm hoặc sai shape, phải từ chối tường minh; không thay bằng cost 0, không hồi sinh candidate đã loại và không tự ép nối nét. Nếu không còn state/transition hợp lệ, trả lỗi có cấu trúc theo thiết kế Bước B thay vì render một kết quả giả hợp lệ.

### 2.4. Ownership và test trước khi code PR3

| Phần | Owner | Reviewer bắt buộc |
| :--- | :--- | :--- |
| `DiacriticConfig`, candidate, `C_state`, transform dấu và renderer | TV4 | TV2 khi chạm shared transition |
| Trọng số động học, breakdown pen-up/lift/curvature | TV2 | TV4 khi chạm engine handwriting |
| Interface `CompositionState` ↔ transition, bridge collision, Viterbi recurrence | TV2 + TV4 | Cả hai |

Trước khi E4 đóng, hai owner cần duyệt test plan: synthetic trellis có nghiệm biết trước; lift-vs-connect và breakdown không âm/hữu hạn; bbox/polyline world dưới scale X/Y khác nhau; bridge chạm dấu của state trước/sau; no double-count; invalid geometry fail-closed; B3/default parity; 48/48 ASCII fingerprints, strict validation và DEV-only guard. PR3 mới thêm test implementation tương ứng; không tạo `xfail`/placeholder để báo PASS.

### 2.5. Kết quả rà soát kỹ thuật phía TV4

**Trạng thái rà soát:** `TV4_SCOPE_APPROVED_WITH_OPEN_INTERFACE_ITEMS` (2026-09-23). Đã đối chiếu mục này với engine, Docs 07/09 và chạy 12 test PR3 ASCII/baseline cùng engine self-check: đều PASS. TV4 xác nhận đồng ý với kết luận rà soát kỹ thuật trong cuộc trao đổi ngày 2026-09-23; sự xác nhận này chỉ áp dụng cho đề xuất thuộc phạm vi TV4 ở mục 2.5, không phải chữ ký cuối cho toàn bộ E4. Các điểm giao diện ở mục 3 vẫn cần TV2 và TV4 thống nhất trước khi triển khai.

| ID | Đề xuất phía TV4 | Bằng chứng hiện hành / điều kiện PR3 |
| :--- | :--- | :--- |
| TV4-01 — NFD và nguồn ký tự | Giữ pipeline chuẩn hóa `normalize_vietnamese_final_uy_tone()` rồi mới `group_nfd_graphemes()`; `CompositionState.base_char` và `accents` phải bám **chuỗi sau chuẩn hóa**, không tự chuyển dấu thêm lần nữa. Test C1 cần kiểm tra riêng phép ánh xạ input → normalized text và normalized text → state/trace; không so NFD của raw input với output khi quy tắc `uy` đã chủ động chuyển dấu. | `engine.py:_text_to_strokes_impl()` gọi normalize trước khi tạo `char_queue`; `group_nfd_graphemes()` bảo toàn thứ tự combining marks của text đã chuẩn hóa. Cần đối chiếu/cập nhật cách diễn đạt C1 trong Docs 09 trước khi viết test PR3. |
| TV4-02 — Hình học dấu | Dùng `generate_accents()` hiện hành và `font_pack["dot_below_x_offsets"]` làm canonical geometry provider; `safe_left`/`safe_right` chỉ dịch cụm dấu trong local frame, không sửa glyph/font pack trong PR3. Độ dịch khai báo bằng mm phải được quy đổi qua `scale_vec` trước khi cộng vào tọa độ local, hoặc áp dụng trong world frame đúng một lần; TV2/TV4 phải khóa cách làm thống nhất ở mục 3. Giữ từng mark stroke riêng để audit va chạm nội tại. | Renderer hiện gọi `generate_accents()` sau DAG và scale/offset từng nét; PR3 chỉ thay nguồn dấu bằng candidate được chọn, không gọi provider lần hai lúc render. Docs 07 hiện gọi `dx_candidates_mm` là mm nhưng pseudocode dùng local frame. |
| TV4-03 — World transform | Dùng một phép affine theo từng ký tự: `world_point = local_point * scale_vec + offset`; transform tangent bằng `scale_vec` rồi normalize, không cộng offset vào vector; tính `world_bbox` từ world polyline. Không dùng scalar `scale` của pseudocode Docs 07 làm implementation khi X/Y khác nhau. | `char_info_list` hiện chứa `scale_vec=[c_scale_x, scale_y]` và `offset`; DAG lẫn renderer đang dùng vector này. Cần test anisotropic scale và một lần-transform-duy-nhất. |
| TV4-04 — `C_state` và giới hạn | `C_state` cộng internal collision, base legibility và placement đúng một lần; không chứa pen-up/lift/curvature/bridge cost. Ký tự không dấu có `diacritic_candidate=None` và placement=0. Hard-invalid candidate bị loại, không hồi sinh; `K_raw ≤ 9`. | Docs 07 §§6, 8–9. `eval_transition()` hiện cộng `cost_legibility`, nên PR3 không được vừa giữ khoản đó vừa cộng vào `C_state`; B3 cũ phải bảo toàn. |
| TV4-05 — Bất biến dữ liệu | `frozen=True` một mình chưa đủ khi field chứa `np.ndarray`, `dict` hoặc `DiacriticConfig.dx_candidates_mm`; PR3 phải copy/read-only hóa geometry và dùng mapping bất biến hoặc bản sao phòng vệ. Không cho mutation làm đổi kết quả giữa các lần chạy cùng seed. | Schema ý niệm tại Docs 07 dùng frozen dataclass nhưng có field mutable; cần unit test mutation attempt và deterministic replay. |
| TV4-06 — Renderer, trace và lỗi | Renderer PR3 vẽ đúng cụm dấu thuộc state đã chọn, giữ `TraceStroke.stroke_type="diacritic_stroke"` và chỉ sinh một lần; giữ chữ `đ/Đ`, dấu chấm `i/j` và secondary stroke hiện hành. Nếu không còn state hợp lệ, fail closed theo Docs 07; không trả SVG giả hợp lệ. | `engine.py` hiện thêm dấu sau DAG, tách secondary và diacritic trace; `tests/test_pr3_acceptance_baseline.py` khóa 48 ASCII cases. |
| TV4-07 — Ngưỡng hình học | `DiacriticConfig.clearance_threshold_mm=0.20` là mặc định kỹ thuật ban đầu; `0.50 mm` chỉ là research target chờ TV3 đo máy thật. Metric acceptance không được trở thành tham số render ngầm. | Docs 07 §4, Docs 09 §5 và `metrics_evaluator.py` phân biệt technical minimum với provisional target. |

**Kết luận rà soát kỹ thuật TV4 đã được owner xác nhận:** chấp nhận có điều kiện hướng tách `C_state` khỏi `J_transition`, bảo toàn đường B3/default và yêu cầu một world transform thống nhất. Chưa chấp nhận đóng E4 cho đến khi TV2 đồng ý interface thực tế và hai bên xử lý các câu hỏi mục 3.

## 3. Câu hỏi còn mở cho TV2 và TV4

1. Symbol và module chính thức của PR3 transition là gì? Giữ `eval_transition()` cũ nguyên trạng cho B3 hay mở rộng nó bằng adapter có version?
2. `TransitionResult` lưu bridge geometry trực tiếp hay chỉ lưu quyết định rồi renderer dựng lại bằng cùng builder? Cách nào bảo đảm hình học được đánh giá là hình học được vẽ?
3. `cost_legibility` hiện trong `eval_transition()` sẽ được di chuyển/tách thế nào để `C_state` cộng đúng một lần mà không làm đổi B3/ASCII?
4. TV4 đề xuất local là glyph-local units, world là mm và dùng `scale_vec`/`offset` như mục 2.5. TV2 có chấp thuận quy ước này và cách normalize tangent khi scale không đều không? Sau đồng thuận cần sửa pseudocode scalar/local-mm ở Docs 07.
5. Khi một cạnh transition không hợp lệ, biểu diễn “không có cạnh” bằng kết quả có status hay exception nội bộ nào? Ai chuyển lỗi này lên renderer?
6. Cost breakdown/weights có cần một dataclass versioned, hay mapping nội bộ là đủ cho PR3? Khóa thứ tự và mặc định trước khi code.
7. `dx_candidates_mm`/`dy_candidates_mm` và clearance của Docs 07 đang mang đơn vị mm, còn glyph/anchor local của engine chưa phải mm. Độ dịch ứng viên được quy đổi bằng `scale_vec` vào local frame hay áp dụng trong world frame? Khóa công thức, thứ tự transform và test với scale X/Y khác nhau để tránh đổi cỡ chữ làm đổi độ dịch vật lý.

## 4. Cổng ký duyệt E4

- [ ] TV2 kiểm tra và xác nhận contract motion/transition, chi phí, geometry, test plan và file ownership.
- [x] TV4 xác nhận đề xuất kỹ thuật thuộc phạm vi state/diacritic, transform, renderer và regression ở mục 2.5, với các điểm giao diện chung mục 3 còn mở.
- [ ] TV4 xác nhận contract E4 cuối cùng sau khi hai owner chốt các điểm giao diện chung.
- [ ] Các câu hỏi mục 3 được trả lời bằng quyết định cụ thể; cập nhật Docs 07/09 nếu quyết định thay đổi nguồn chuẩn.
- [ ] Ghi người xác nhận, ngày, commit tài liệu đã duyệt và bằng chứng review trong repository.
- [ ] Sau đó mới cập nhật E4=`PASS`, PR3=`READY_TO_IMPLEMENT` và bắt đầu Slice 0 của [`17_pr3_implementation_readiness.md`](17_pr3_implementation_readiness.md).

**TV2 sign-off:** `PENDING`

**TV4 scope approval:** `CONFIRMED_WITH_OPEN_INTERFACE_ITEMS` (owner xác nhận ngày 2026-09-23; mục 2.5)

**TV4 final E4 sign-off:** `PENDING_SHARED_DECISIONS`

**TV4 technical review:** `PASS_WITH_OPEN_INTERFACE_ITEMS` (mục 2.5, 12 test và engine self-check PASS)

**E4 verdict:** `WAITING_TV2_TV4_SIGNOFF`
