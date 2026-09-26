# OmniDraw — PR3 Implementation Readiness Pack

**Phiên bản:** 0.2
**Ngày lập:** 2026-09-24
**Owner:** TV4 — Handwriting / CA-VHC Composition Lead
**Trạng thái:** `NOT_READY — E4 REOPENED FOR TV4 CHANGES AND TV2 RECHECK`
**Review boundary:** `OUTSIDE_REVIEW_TARGET_7ae43e6` — tài liệu chuẩn bị này không thay đổi Chương 1–3 và không yêu cầu mở lại gói cross-review v0.2.

> [!IMPORTANT]
> Quyết định ngày 2026-09-24 từng ghi E4 `PASS` và PR3 `READY_TO_IMPLEMENT`. TV2 review ngày 2026-09-25 đã mở lại E4 với verdict `PASS_WITH_CHANGES`; trạng thái hiện hành là chờ TV4 xử lý contract và TV2 recheck. Phần triển khai PR3 trên nhánh tích hợp cũng đã bị revert tại `7d1c1d3`; tài liệu này không cấp phép khôi phục implementation.

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
- [`18_pr3_e4_shared_transition_contract_draft.md`](18_pr3_e4_shared_transition_contract_draft.md): nguồn trạng thái hiện hành của E4; đang `CHANGES_REQUIRED`.

Nếu pack này mâu thuẫn với Docs 07 hoặc 09, Docs 07/09 có quyền ưu tiên và pack phải được sửa trước khi code.

## 2. Snapshot Entry Gate

| Gate | Trạng thái | Bằng chứng/Dependency | Quyết định |
| :--- | :--- | :--- | :--- |
| E1 — PR1 metrics/runner | `PASS` | Evaluator, CSV logger, experiment runner và DEV fingerprint fixture đã tồn tại | Không sửa lại trong PR3 trừ khi cần metadata thật sự mới |
| E2 — ASCII geometry lock | `PASS` | 48 cấu hình tại `pr3_ascii_baseline_fingerprints.json` | Mọi lát cắt PR3 phải giữ 48/48 fingerprint |
| E3 — B1/B2/B3 adapters | `PASS` | PR #32 merge commit `bcc1a7a`; `baselines.py`, runner method tags và `tests/test_ca_vhc_baselines.py`; full suite 136 passed | Dependency PR2 đã nhận; E3 hoàn tất |
| E4 — Shared transition interface | `REOPENED / CHANGES_REQUIRED` | TV2 đã trả lời Q1–Q7 và yêu cầu đồng bộ pseudo-types, error semantics, immutability, contract version và ranh giới gate/test tại [`18_pr3_e4_shared_transition_contract_draft.md`](18_pr3_e4_shared_transition_contract_draft.md) | TV4 cập nhật contract; TV2 recheck trước khi E4 đóng lại |
| E5 — Corpus integrity | `PASS` | Acceptance specimens chỉ lấy từ DEV; Holdout guard đã có | Cấm `--corpus holdout/all` và `--allow-holdout` trong PR3 |

**Quy tắc mở PR3:** E1, E2, E3 và E5 vẫn `PASS`; E4 đang mở lại. PR3 không ở trạng thái `READY_TO_IMPLEMENT` cho tới khi TV4 xử lý contract và TV2 ký recheck.

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
| `engine.py:eval_transition()` | Cost giữa hai `GlyphVariant` | Tích hợp shared PR2 contract và bridge-vs-diacritic world geometry sau E4 | Không tự định nghĩa lại cost TV2 |
| `engine.py:optimize_word_dag()` | Viterbi trên `GlyphVariant` | Chuyển layer sang `CompositionState`, cộng `C_state + J_transition` | Không dùng beam/top-k heuristic chưa được duyệt |
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
- [ ] E4 đóng lại: TV4 xử lý contract và TV2 xác nhận recheck ([`Docs 18`](18_pr3_e4_shared_transition_contract_draft.md)).
- [x] Working tree PR3 không chứa thay đổi chưa review của PR2.
- [x] 48 ASCII baseline và toàn bộ suite hiện hành pass trên commit nền (136/136 tests PASS).
- [x] DEV/holdout guard vẫn hoạt động.
- [x] File ownership và danh sách symbol shared đã được ghi rõ.
- [x] Không có yêu cầu mở rộng phạm vi sang PR4/P2/hardware.

Definition of Ready hiện **chưa đạt** vì E4 đang `CHANGES_REQUIRED`. Các dấu `[x]` còn lại chỉ ghi nhận dependency đã đạt và không thay thế chữ ký E4 mới.

