# OmniDraw — PR3 Implementation Readiness Pack

**Phiên bản:** 0.2
**Ngày lập:** 2026-09-24
**Owner:** TV4 — Handwriting / CA-VHC Composition Lead
**Trạng thái:** `IMPLEMENTATION_IN_PROGRESS — E1–E5 PASS; EXIT REVIEW PENDING`
**Review boundary:** `OUTSIDE_REVIEW_TARGET_7ae43e6` — tài liệu chuẩn bị này không thay đổi Chương 1–3 và không yêu cầu mở lại gói cross-review v0.2.

> [!IMPORTANT]
> Quyết định ngày 2026-09-24 từng bị mở lại sau TV2 review ngày 2026-09-25. TV4 và TV2 đã recheck, cùng phê duyệt phiên bản contract `4677aad` ngày 2026-09-26; E4 hiện `PASS` và PR3 trở lại `READY_TO_IMPLEMENT`. Phần triển khai cũ vẫn đã revert tại `7d1c1d3`; mọi triển khai mới phải đi theo contract đã khóa và qua exit criteria PR3.

## 1. Mục tiêu

Cho phép TV4 bắt đầu PR3 ngay sau khi TV2 bàn giao PR2 mà không phải đọc lại toàn bộ kiến trúc. Pack này khóa:

1. dependency cần nhận từ PR2;
2. các điểm chạm mã nguồn tối thiểu;
3. thứ tự triển khai có thể review theo lát cắt nhỏ;
4. test và visual specimen phải bổ sung;
5. ranh giới giữa PR3 **WHERE** và PR4 **WHEN**;
6. điều kiện dừng nếu contract chưa đủ hoặc hồi quy ASCII xuất hiện.

Nguồn chuẩn vẫn là:

- [`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md): kiến trúc `DiacriticCandidate` và `CompositionState`.
- [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md): Entry/Exit Gate.
- [`16_rq_code_metric_test_traceability.md`](16_rq_code_metric_test_traceability.md): ánh xạ RQ–metric–test.
- [`18_pr3_e4_shared_transition_contract_draft.md`](18_pr3_e4_shared_transition_contract_draft.md): nguồn trạng thái hiện hành của E4; `PASS` trên phiên bản hai owner cùng ký `4677aad`.

Nếu pack này mâu thuẫn với Docs 07 hoặc 09, Docs 07/09 có quyền ưu tiên và pack phải được sửa trước khi code.

## 2. Snapshot Entry Gate

| Gate | Trạng thái | Bằng chứng/Dependency | Quyết định |
| :--- | :--- | :--- | :--- |
| E1 — PR1 metrics/runner | `PASS` | Evaluator, CSV logger, experiment runner và DEV fingerprint fixture đã tồn tại | Không sửa lại trong PR3 trừ khi cần metadata thật sự mới |
| E2 — ASCII geometry lock | `PASS` | 48 cấu hình tại `pr3_ascii_baseline_fingerprints.json` | Mọi lát cắt PR3 phải giữ 48/48 fingerprint |
| E3 — B1/B2/B3 adapters | `PASS` | PR #32 merge commit `bcc1a7a`; `baselines.py`, runner method tags và `tests/test_ca_vhc_baselines.py`; full suite 136 passed | Dependency PR2 đã nhận; E3 hoàn tất |
| E4 — Shared transition interface | `PASS` | TV4 và TV2 cùng phê duyệt contract `4677aad`; Q1–Q7, pseudo-types, error semantics, immutability, contract version và test plan đã khóa tại [`18_pr3_e4_shared_transition_contract_draft.md`](18_pr3_e4_shared_transition_contract_draft.md) | Cho phép bắt đầu PR3 theo contract; test implementation vẫn thuộc exit gate |
| E5 — Corpus integrity | `PASS` | Acceptance specimens chỉ lấy từ DEV; Holdout guard đã có | Cấm `--corpus holdout/all` và `--allow-holdout` trong PR3 |

**Quy tắc mở PR3:** E1–E5 đều `PASS`. PR3 ở trạng thái `READY_TO_IMPLEMENT`; trạng thái này không đồng nghĩa implementation hoặc các gate thực nghiệm đã hoàn tất.

## 3. Checklist nhận bàn giao PR2

TV4 dùng bảng này khi review PR2. Tên symbol cuối cùng do PR2 quyết định; yêu cầu hành vi dưới đây mới là bắt buộc.

### 3.1. Baseline adapters

- [x] Có ba method độc lập: B1 Static, B2 Greedy và B3 Current Trellis.
- [x] Cùng một input text/font/style/seed tạo đầu ra có schema chung để runner so sánh.
- [x] Mỗi method có `method_tag` ổn định, không suy từ tên hiển thị UI.
- [x] B3 bảo toàn hành vi engine hiện hành trước PR3.
- [x] Adapter không đọc Holdout mặc định và không tự chọn corpus.
- [ ] Cùng input/seed chạy lặp lại cho cùng fingerprint và metric hình học.
- [x] Không adapter nào gọi Proposed CA-VHC hoặc dùng logic dấu của PR3 trước khi PR3 tồn tại.

### 3.2. Shared transition contract

- [ ] Chữ ký transition chấp nhận trạng thái trước/sau hoặc một protocol tối thiểu tương đương, không phụ thuộc trực tiếp vào UI/API payload.
- [ ] Kết quả tách được `D_penup`, `N_lift`, `C_curvature`, `C_bridge_collision`, tổng cost và quyết định nối/nhấc bút.
- [ ] Mọi cost hữu hạn, không âm; invalid geometry fail closed.
- [ ] Quy ước local/world coordinate và đơn vị millimét được ghi rõ.
- [ ] Có đường lấy `world_bbox`/world strokes của dấu để bridge collision kiểm tra đúng hai state kề nhau.
- [ ] `C_state` không bị tính lại trong `J_transition`.
- [ ] Trọng số động học thuộc TV2/shared contract; placement/legibility/internal-diacritic cost vẫn thuộc TV4.
- [ ] Có synthetic test với nghiệm tối ưu biết trước và test bảo toàn B3.

### 3.3. Câu hỏi bắt buộc khi PR2 tới

1. Runner gọi adapter bằng symbol nào và output type nào?
2. Transition có trả cost breakdown hay chỉ tổng cost?
3. Điểm vào/ra và tangent đã ở local hay world coordinates?
4. Bridge geometry được tạo trong transition hay renderer?
5. B3 adapter có bọc nguyên engine hiện hành hay sao chép logic?
6. Test nào chứng minh B1/B2/B3 dùng cùng input và seed?
7. PR2 thay đổi file nào trong `backend/handwriting/` và có giao nhau với vùng TV4 sẽ sửa không?

PR2 đã trả lời các câu về method tag, schema và B3; các quyết định về transition breakdown, world geometry và migration `cost_legibility` đang được ghi tại [`18_pr3_e4_shared_transition_contract_draft.md`](18_pr3_e4_shared_transition_contract_draft.md). Nếu một câu E4 chưa có câu trả lời được hai owner xác nhận, E4 giữ `WAITING`.

## 4. Bản đồ điểm chạm mã nguồn PR3

| Khu vực hiện hành | Vai trò hiện tại | Thay đổi dự kiến trong PR3 | Không được làm |
| :--- | :--- | :--- | :--- |
| `backend/handwriting/engine.py:get_glyph_variants()` | Sinh `GlyphVariant` thân chữ | Tái sử dụng làm vế base của `CompositionState` | Không thay hình học Font Pack |
| `engine.py:generate_accents()` | Sinh dấu hậu DAG | Giữ wrapper tương thích; tách hình học canonical để sinh candidate | Không xóa public behavior đột ngột |
| `engine.py:eval_transition()` | Cost giữa hai `GlyphVariant` cho B3/default | Giữ nguyên implementation và đường gọi hiện hành | Không đưa shared PR3 contract vào hàm này; không làm đổi hành vi B3/default |
| `engine.py:optimize_word_dag()` | Viterbi trên `GlyphVariant` cho B3/default | Giữ nguyên implementation và đường gọi hiện hành | Không chuyển layer B3/default sang `CompositionState` |
| `composition.py::evaluate_composition_transition()` *(planned)* | Shared transition giữa hai `CompositionState` của PR3 | Triển khai contract Docs 18 và được gọi qua đường PR3 riêng | Không gọi vòng qua hoặc thay thế `engine.eval_transition()` |
| `engine.py:_text_to_strokes_impl()` | Chuẩn bị `char_info`, gọi DAG, render dấu post-DAG | Truyền accents/context vào builder; render dấu từ state đã chọn | Không đặt lại dấu lần hai ở hậu xử lý |
| `engine.py:text_to_strokes_structured()` | Public structured trace | Bảo toàn signature; bổ sung trace metadata theo hướng tương thích | Không đổi public API ngoài contract |
| `backend/handwriting/metrics_evaluator.py` | Collision, clearance, curvature và fingerprint | Chỉ bổ sung producer/trace nếu metric thật sự thiếu | Không đổi ngưỡng đo thành tham số render |
| `backend/handwriting/experiment_runner.py` | Chạy B3 DEV hiện tại | Sau PR2, gọi B1/B2/B3/Proposed qua interface chung | Không chạy Holdout trong tuning |
| `backend/handwriting/qa_specimens.py` | Báo cáo visual QA | Thêm section chẩn đoán PR3 sau khi core chạy | Không dùng visual QA thay automated acceptance |

### 4.1. Vị trí kiểu dữ liệu

Quyết định tạo module mới hay đặt type trong `engine.py` chỉ được khóa sau khi nhìn diff PR2. Tiêu chí lựa chọn:

- Nếu type/helper không phụ thuộc render loop và có thể unit-test độc lập, ưu tiên module nội bộ nhỏ như `backend/handwriting/composition.py`.
- Nếu tách module tạo import cycle hoặc buộc di chuyển nhiều symbol đang ổn định, giữ tối thiểu trong `engine.py` cho PR3 và ghi debt rõ ràng.
- Không tái cấu trúc Font Pack, API Gateway hoặc frontend trong cùng PR3.

## 5. Các lát cắt triển khai sau khi Gate mở

### Slice 0 — Contract freeze

- Chốt symbol/output type PR2.
- Ghi decision note cho local/world frame, cost breakdown và default `DiacriticConfig`.
- Chạy toàn bộ test hiện hành trước thay đổi; lưu commit nền.

**Dừng ngay nếu:** B1/B2/B3 chưa cùng schema, transition chưa có cost breakdown cần thiết hoặc B3 không bảo toàn hành vi hiện hành.

### Slice 1 — Types và candidate generation, chưa nối DAG

- Hiện thực `DiacriticConfig`, `DiacriticCandidate`, `CompositionState` bất biến.
- Tạo canonical/safe-left/safe-right từ geometry hiện hành.
- Ký tự không dấu chỉ có `diacritic_candidate=None`.
- Hard-invalid candidate bị loại vĩnh viễn; không hồi sinh bằng fallback.

**Test mục tiêu:** B1, B2, B3 của acceptance contract và nhóm test candidate tại Docs 07.

### Slice 2 — Transform và state cost

- Thêm local-to-world helper duy nhất.
- Tính `bounds_local`, world strokes/bbox và `C_state`.
- Tách geometry metric có đơn vị mm khỏi cost metric vô hướng.
- Synthetic tests cho NaN/Inf, rỗng, vượt biên và internal collision.

### Slice 3 — Diacritic-aware Viterbi

- Thay layer `GlyphVariant` bằng `CompositionState`.
- Recurrence dùng `C_state + J_transition` và backpointer.
- Kiểm tra bridge với base và dấu của hai state kề nhau trong world frame.
- Synthetic trellis phải chọn nghiệm biết trước.

**Dừng ngay nếu:** bất kỳ cost nào âm/không hữu hạn, state/layer vượt 9 hoặc hard-invalid candidate xuất hiện lại.

### Slice 4 — Renderer integration

- Renderer lấy base và dấu trực tiếp từ state đã chọn.
- Chặn double-render từ `generate_accents()` hậu DAG.
- Giữ metadata `TraceStroke` đúng loại `base/bridge/secondary/diacritic`.
- Bảo toàn `text_to_strokes()` và `text_to_strokes_structured()`.

### Slice 5 — Acceptance và visual diagnostics

- Chạy 48/48 ASCII fingerprints và strict validation.
- Chạy 10 DEV acceptance specimens cho NFD, collision, clearance và state bound.
- Thêm visual diagnostics: `lụy`, `thụy`, `quỹ`, `nguyễn`, `nghiễm`.
- Nhóm diagnostics chỉ giúp tìm lỗi; không được trộn vào acceptance corpus hoặc báo cáo như kết quả formal.

### Slice 6 — Runner Proposed adapter

- Thêm Proposed method qua interface chung của PR2.
- Chỉ chạy DEV technical dry-run.
- Không tổng hợp kết quả khoa học, không mở Holdout và không làm PR4 delayed-stroke scheduling trong slice này.

## 6. Test map phải hiện thực khi PR3 bắt đầu

### `tests/test_ca_vhc_composition_state.py`

- `test_composition_state_without_accent`
- `test_acute_accent_candidate_generation`
- `test_circumflex_acute_geometry_clearance`
- `test_circumflex_acute_internal_collision_cost`
- `test_horn_tone_candidate_generation`
- `test_dot_below_candidate_generation`
- `test_internal_diacritic_base_collision`
- `test_candidate_pruning_never_revives_hard_invalid`
- `test_composition_state_is_immutable`
- `test_transform_state_to_world_uses_single_frame_contract`

### `tests/test_pr3_vietnamese_acceptance.py`

- `test_pr3_vietnamese_unicode_nfd_mark_preservation`
- `test_pr3_vietnamese_zero_collision`
- `test_pr3_vietnamese_clearance_threshold`
- `test_viterbi_synthetic_trellis_optimality`
- `test_pr3_trellis_dev_specimens_run_safely`
- `test_pr3_state_layer_bound_is_at_most_nine`
- `test_pr3_same_seed_is_deterministic`
- `test_pr3_renderer_does_not_duplicate_diacritics`

### Regression bắt buộc giữ nguyên

- `tests/test_pr3_acceptance_baseline.py`
- `tests/test_ca_vhc_metrics.py`
- `tests/test_ca_vhc_experiment_runner.py`
- `backend/test_handwriting_validation.py`
- Engine self-check hiện hành.

Không tạo test `xfail` chỉ để làm dashboard trông đầy đủ. Trước khi Gate mở, danh mục trên là specification; test file chỉ được thêm khi có slice implementation tương ứng và assertion thật.

## 7. Ranh giới PR3

### Trong phạm vi

- `CompositionState` và `DiacriticCandidate`.
- Diacritic placement candidates và hard-invalid pruning.
- State/transition cost integration trong Viterbi.
- Bridge–diacritic collision trong world coordinates.
- Renderer dùng dấu đã được DAG chọn.
- Trace/metric cần thiết cho nghiệm thu phần mềm.

### Ngoài phạm vi

- PR4: quyết định **WHEN** và delayed-stroke scheduling.
- Writer Profile, ML/fine-tuning hoặc học thói quen người dùng.
- Font Pack mới, TTF/OTF conversion.
- Frontend, API public hoặc phân trang nhiều trang.
- Hardware calibration và `actual_draw_time_sec` máy thật.
- Formal benchmark/ablation và mọi kết luận RQ.

## 8. Quy tắc chống xung đột TV2–TV4

- TV2 sở hữu baseline adapters và thành phần động học của transition cost.
- TV4 sở hữu chính tả, candidate dấu, state cost và integration renderer.
- Shared symbols chỉ được sửa sau E4 sign-off.
- Nếu PR2 và PR3 cùng cần sửa một function, PR2 merge trước; PR3 rebase lên contract đã kiểm thử, không copy diff PR2 thủ công.
- Không đổi trọng số hoặc ngưỡng để “làm test pass” nếu chưa có decision note.
- Mọi thay đổi geometry tiếng Việt phải có automated test và visual specimen tương ứng.

## 9. Definition of Ready

PR3 được phép bắt đầu khi toàn bộ mục sau đạt:

- [x] E3 đóng: B1/B2/B3 đã merge và test pass (PR #32, `bcc1a7a`; full suite 136 passed).
- [x] E4 đóng lại: TV4 và TV2 cùng phê duyệt contract `4677aad` ([`Docs 18`](18_pr3_e4_shared_transition_contract_draft.md)).
- [x] Working tree PR3 không chứa thay đổi chưa review của PR2.
- [x] 48 ASCII baseline và toàn bộ suite hiện hành pass trên commit nền (136/136 tests PASS).
- [x] DEV/holdout guard vẫn hoạt động.
- [x] File ownership và danh sách symbol shared đã được ghi rõ.
- [x] Không có yêu cầu mở rộng phạm vi sang PR4/P2/hardware.

Definition of Ready hiện **đã đạt** vì E1–E5 đều `PASS` và hai owner đã ký cùng phiên bản E4. Việc triển khai PR3 vẫn phải đáp ứng toàn bộ exit criteria trước khi được coi là hoàn thành.

## 10. Tiến độ triển khai mới của TV4 (2026-09-27)

Nhánh local `codex/tv4-pr3-slices` được tạo từ nhánh tích hợp tại `e62f361`. Nhánh `backup/pr3-implementation` chỉ làm tham khảo; không lấy lại diff từ nhánh đó.

| Slice | Commit | Bằng chứng hiện tại |
| :--- | :--- | :--- |
| 1 — State và ứng viên dấu | `369db23` | Kiểu dữ liệu, ba vị trí P0, test immutability và invalid candidate |
| 2 — World geometry và state cost | `b01bd8c` | Transform scale X/Y, offset mm, `C_state`, hard pruning |
| 3 — Transition và Viterbi | `2556672` | Đường PR3 riêng, test `CONNECT`/`LIFT`/`REJECT` và trellis synthetic |
| 4 — Renderer opt-in | `e2cc4cd` | Dấu lấy từ state đã chọn, bridge lấy từ transition; B3/default giữ đường cũ |
| 5 — Acceptance/visual diagnostics | `a5b0c17` | 10/10 DEV specimens đạt test NFD, collision 0, clearance ≥ 0.20 mm, layer ≤ 9; báo cáo soi hình học riêng cho 5 từ ngoài acceptance |
| 6 — Proposed runner | `4428045` | `pr3_composition` chỉ chạy DEV; technical dry-run 20 dòng, không mở Holdout |

Suite tại mốc slice 6: **199 passed** (bao gồm `backend/test_handwriting_validation.py`). Đây là bằng chứng software technical dry-run, chưa phải benchmark chính thức hay kết luận RQ.

**Còn mở trước exit sign-off:** TV2 review thành phần động học của shared transition, đặc biệt bridge–glyph hard collision so với tiếp xúc hợp lệ ở mút nối; xác nhận xử lý biến thiên sinh học của PR3. Chế độ PR3 hiện không áp dụng biến thiên ngẫu nhiên sau DAG để geometry được chấm và geometry được render trùng nhau. Cần chốt cách giữ đặc tính style mà vẫn tuân E4 trước khi coi renderer integration hoàn tất. Không thay đổi TV2 baseline adapters hoặc hardware trong các slice trên.

## 11. TV4 exit-gate evidence sau `d4ed1a4` (2026-09-29)

**Lưu ý lịch sử:** Bảng dưới là snapshot trước tối ưu E1 ở `adb0417`; kết luận `NOT_PASSED` của E1 và danh sách gate mở tại thời điểm này đã được thay thế bởi §12–13. Không dùng bảng này làm verdict hiện hành.

Đây là kiểm tra phần mềm trên nhánh `codex/tv4-pr3-slices`, sau khi TV4 sửa ba finding `TV2-PR3-R01–R03` tại `d4ed1a4` và mở rộng test Proposed D1 lên 5 lượt. TV2 chưa recheck hoặc ký sign-off implementation. Lệnh `git ls-files -z 'tests/test*.py' | xargs -0 backend/venv/bin/python -m pytest -q backend/test_handwriting_validation.py` đạt **231 passed, 1 warning**. Các file hardware/CAD chưa commit trong checkout không nằm trong thay đổi TV4 này.

| Exit criterion Docs 09 | Bằng chứng hiện có | Trạng thái TV4 |
| :--- | :--- | :--- |
| A1–A3; D2; G1 | 48/48 fingerprint ASCII, SVG/bounds, strict validation, batch-order parity; 10 acceptance specimens chỉ thuộc DEV; test Holdout guard ở runner | `PASS_SOFTWARE` |
| B1–B3; E2 | State/world geometry, giới hạn layer ≤ 9, state cost cộng đúng một lần, trellis synthetic; `d4ed1a4` thêm hard-prune bridge–base/mark và test trọng số không mặc định | `PASS_TESTS; PENDING_TV2_RECHECK` |
| C1–C3; E3 | `tests/test_pr3_vietnamese_acceptance.py`: 10/10 mẫu DEV qua NFD/mark, 0 bridge–mark collision, clearance tối thiểu 1.130866671 mm, không NaN metric và layer ≤ 9 (font `cursive`, seed 42) | `PASS_SOFTWARE` cho ma trận đã test |
| D1 | ASCII/default và PR3 Proposed (`tiếng`, font `cursive`, seed 42) đều lặp 5 lần cùng seed và giữ fingerprint | `PASS_SOFTWARE` trên các ca đã test |
| E1 | Runner có B1/B2/Proposed. Dry-run **10 mẫu DEV, font `cursive`, seed 42**: tổng pen-up B1 = 302.070 mm, B2 = 279.322 mm, Proposed = 288.056 mm; Proposed giảm 4.639% so B1 nhưng **tăng 3.127% so B2** | `NOT_PASSED`; chưa có bằng chứng giảm so với cả B1 và B2 trên DEV đầy đủ |

E1 trong bảng lịch sử của Docs 09 ghi `PASS_CURRENT` vì runner và baseline adapters đã có. Trạng thái đó chỉ xác nhận **hạ tầng đo**, chưa xác nhận tiêu chí giảm quãng đường pen-up của Proposed. Số trên là chẩn đoán DEV một font/seed, không phải benchmark PR5 hoặc kết luận H1.1. Trước khi ký PR3 exit, TV4/TV2 cần thống nhất cách xử lý E1 theo contract và chạy ma trận DEV được khóa; không điều chỉnh thuật toán bằng HOLDOUT.

**Gate còn mở:** (1) TV2 ký human sign-off R01–R03 và recheck ca biên hình học mới; (2) xử lý E1 như trên; (3) chốt biến thiên style của PR3 mà vẫn bảo đảm geometry được chấm khớp geometry render. Physical calibration và formal benchmark vẫn là downstream gates độc lập.

**TV2 recheck tại `73bc9e2` (2026-09-29):** AI recheck ghi R01–R03 `VERIFIED_CLOSED`, còn `TV2_HUMAN_SIGN_OFF: PENDING`. TV2 phát hiện thêm ca biên `np.allclose` dùng relative tolerance mặc định tại tọa độ lớn. TV4 đã đổi so khớp cổng sang `rtol=0` và thêm test tự động cho off-port touch, overlap tại exit và near-port overlap; nhóm PR3 liên quan đạt 30/30, toàn bộ test được Git theo dõi đạt **233 passed**. Cần TV2 recheck commit sửa ca biên trước khi coi phần hình học chuyển tiếp đã ký xong.

## 12. E1 DEV dry-run sau tối ưu thứ tự nét phụ (2026-09-29)

TV2 đã ký riêng shared transition tại `0cf3de1` trên PR #35 cho mã TV4 `1aa6ce2`. PR3 exit sign-off vẫn mở. TV4 tiếp tục E1 bằng cách xếp lại các **nhóm nét phụ/dấu sau thân chữ** theo khoảng cách từ vị trí bút hiện tại, giữ nguyên thứ tự nét trong từng ký tự và chỉ nhận thứ tự mới nếu quãng đường trong từ giảm. Hình học từng nét, state/transition E4, B1/B2/B3 và hardware không đổi. Renderer và trace cùng dùng thứ tự mới.

Đo bằng `build_benchmark_rows` trên **20 từ DEV đóng băng**, hai font `oly`/`omni_casual`, bốn seed chuẩn `42, 100, 2026, 999999`, cùng style mặc định `hand_hocsinh` cho cả ba method. Mỗi ô là tổng `pen_lift_distance_mm` của 80 ca theo font (đơn vị mm):

| Font | B1 Static | B2 Greedy | Proposed PR3 |
| :--- | ---: | ---: | ---: |
| `oly` | 2167.473 | 2127.310 | **1941.020** |
| `omni_casual` | 2606.385 | 2578.424 | **2396.828** |
| **Tổng 160 ca/method** | **4773.858** | **4705.734** | **4337.848** |

Proposed giảm **9.133% so B1** và **7.818% so B2** trên ma trận DEV này; E1 đạt tiêu chí so sánh phần mềm. Regression test `test_pr3_e1_dev_acceptance_penup_beats_b1_and_b2` khóa thêm mẫu DEV acceptance 10 từ, font `cursive`, seed 42 và collision count bằng 0; test thứ tự nhóm và trace bảo vệ hình học. Toàn bộ test được Git theo dõi cùng `backend/test_handwriting_validation.py`: **236 passed, 1 warning**. Đây là technical DEV dry-run, chưa dùng HOLDOUT và chưa phải benchmark chính thức; quyết định biến thiên style và PR3 exit sign-off vẫn cần hoàn tất.

**TV2 sign-off cho đúng mốc `adb0417`:** [Phiếu E1 của TV2](https://github.com/Anhtuann1404/OmniDraw/blob/codex/tv2-motion-handoff/docs/tv2_pr3_e1_review.md) tại `f1b309c` ghi `PASS_SOFTWARE_DEV` và `TV2_HUMAN_SIGN_OFF: APPROVED` riêng cho E1; `PR3_EXIT_SIGN_OFF: PENDING`. TV2 tái lập đủ 160 ca/method và kiểm tra độ nhạy khi tắt biến thiên style của B1/B2. Phạm vi ký này không tự chuyển sang mã style mới ở §13.

## 13. Bằng chứng E1 có thể tái lập và phạm vi style PR3 sau `072029b` (2026-09-29)

### 13.1. Phạm vi style đã chốt để TV2 recheck

PR3 opt-in hỗ trợ bốn preset `hand_hocsinh`, `hand_nguoilon`, `hand_thuphap`, `hand_chukinhanh` với **giãn chữ, độ nghiêng affine và độ lượn dòng xác định**. Engine áp dụng biến đổi hình học trước bước prune, đánh giá state/transition và hard collision; renderer dùng đúng `GlyphWorldGeometry` đã chọn. Nét gạch ngang `đ` được biến đổi cùng hệ tọa độ. `jitter_amp` ngẫu nhiên của pipeline B1/B2/B3 **không áp dụng trong PR3** vì sẽ làm nét vẽ sau DAG lệch khỏi geometry đã kiểm tra va chạm. Đây là phạm vi style PR3 được công bố, không phải xác nhận nó tương đương mọi hiệu ứng style của B3.

Test nghiệm thu DEV trên 10 từ × 4 preset, font `cursive`, seed 42: NFD/mark, layer ≤ 9, collision = 0, clearance ≥ 0.20 mm đều PASS; D1 lặp 5 lần cho từng preset PASS. Test renderer xác nhận bốn fingerprint style khác nhau và từng nét dấu được render trùng byte với geometry đã đưa vào DAG. Dry-run bổ sung 10 từ × 2 font benchmark × 4 preset, seed 42: **80/80 ca chạy xong, tổng collision = 0**. Toàn bộ suite được Git theo dõi cùng `backend/test_handwriting_validation.py`: **270 passed, 1 warning**.

### 13.2. E1 sau thay đổi style

Script [`generate_pr3_e1_dev_evidence.py`](../scripts/generate_pr3_e1_dev_evidence.py) tạo [`pr3_e1_dev_rows.csv`](evidence/pr3_e1_dev_rows.csv) gồm **480 dòng** (160 ca/method) và [`pr3_e1_dev_metadata.json`](evidence/pr3_e1_dev_metadata.json) chứa commit mã `072029b`, corpus/hash, font, seed, style, phiên bản Python/NumPy, lệnh chạy và hash CSV. Chỉ đọc `BENCHMARK_DEV_CORPUS_20`; không mở HOLDOUT. Chạy lại từ gốc repo bằng `backend/venv/bin/python3 scripts/generate_pr3_e1_dev_evidence.py`.

| Method | `oly` (mm) | `omni_casual` (mm) | Tổng (mm) |
| :--- | ---: | ---: | ---: |
| B1 Static | 2167.473 | 2606.385 | 4773.858 |
| B2 Greedy | 2127.310 | 2578.424 | 4705.734 |
| Proposed PR3 | 1941.020 | 2402.340 | **4343.360** |

Proposed giảm **9.018% so B1** và **7.701% so B2** trên ma trận DEV hiện hành. Sự khác biệt 5.512 mm so với §12 đến từ việc `omni_casual` giờ áp dụng slant/drift trước DAG; số §12 là bằng chứng lịch sử tại `adb0417`. E1 vẫn đạt ở mức TV4 software DEV; **TV2 cần recheck phiên bản style mới** trước khi coi sign-off E1 bao phủ commit hiện tại. H1.1/PR5, quyết định chấp nhận giới hạn jitter của style và PR3 exit sign-off vẫn mở; physical calibration cũng là gate riêng.
