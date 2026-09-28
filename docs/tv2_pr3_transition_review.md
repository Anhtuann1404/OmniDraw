# TV2 — PR3 shared-transition implementation review

- `REVIEWED_BRANCH: codex/tv4-pr3-slices`
- `REVIEWED_COMMIT: 983ebe7d4271d4b3bf48c75d51eb35a04c1e20e8`
- `SLICE_3_ORIGIN: 2556672ca943786a74f67c01618da1930e7c9a40`
- `CONTRACT: E4 e4-v1, ký tại 4677aad và ee7c214`
- `AI_DRAFT_STATUS: CHANGES_REQUESTED`
- `TV2_HUMAN_SIGN_OFF: PENDING`

Phạm vi: chỉ đọc `backend/handwriting/composition.py::evaluate_composition_transition()`, `engine.py::bridge_collision_cost()` được gọi từ đó, `tests/test_ca_vhc_composition_dag.py`, và E4. Không sửa code TV4, B3/default hay hardware. Đây là review implementation, không mở lại E4 và không đóng gate thực nghiệm.

## Đã đối chiếu

- `composition.py:457–491`: `LIFT` dùng $w_1D_{penup}+w_2$, `CONNECT` dùng $w_3C_{curvature}+w_4C_{bridge\_collision}$; nhánh không nối được trả `LIFT`.
- `composition.py:448–450,499–543`: transition chỉ dùng kết quả state evaluator để xét hard internal collision; DP cộng `C_state` tại layer đầu và một lần ở mỗi layer tiếp theo. Không thấy cộng `cost_legibility` vào $J_{transition}$.
- `composition.py:400–434`: kết quả `CONNECT`/`LIFT` có breakdown hữu hạn; `REJECT` có `+inf`, `breakdown=None`, `bridge_strokes=None`; bridge được copy read-only.

## Finding mở cho TV4

| ID | Mức | Bằng chứng và vấn đề | Điều kiện recheck tối thiểu |
|---|---|---|---|
| TV2-PR3-R01 | MAJOR | `composition.py:481–490` nhận `bridge_collision_cost()` hữu hạn từ `engine.py:557–665`, rồi chỉ nhân trọng số. Giao cắt bridge–thân chữ vì thế có thể thành `CONNECT` nếu `w_bridge_collision=0` và lift đắt, thay vì hard-invalid độc lập với trọng số. Heuristic B3 không phải bộ hard-prune PR3. | Giao cắt thật với nét thân trước/sau phải loại nhánh `CONNECT` trước so sánh cost; nếu `LIFT` hợp lệ thì chọn `LIFT`. Test với trọng số collision bằng 0 và `w_lift` lớn. |
| TV2-PR3-R02 | MAJOR | `engine.py:604–635` gộp nét thân hai glyph rồi miễn `shares_exit`/`shares_entry` với *bất kỳ* segment nào chung tọa độ, không kiểm tra segment thuộc glyph trước ở exit hoặc glyph sau ở entry. Tiếp xúc sai chủ thể có thể được coi là cổng hợp lệ. | Test cho tiếp xúc đúng hai cổng; test đối chứng nét glyph sau chạm exit, nét glyph trước chạm entry, và giao cắt lệch cổng. Chỉ miễn đúng tiếp xúc được xác nhận theo vai trò. |
| TV2-PR3-R03 | MAJOR | `composition.py:477–480` chỉ loại bridge–dấu khi `clearance < clearance_threshold_mm`, nhưng `DiacriticConfig` cho ngưỡng bằng 0. Khi bridge chạm mút/giao cắt dấu, clearance bằng 0 và `0 < 0` sai: nhánh nối không bị loại. | Tách hard collision/touch khỏi ngưỡng clearance mềm, hoặc cấm cấu hình 0 nếu contract yêu cầu. Test bridge chạm mút dấu và cắt dấu khi threshold bằng 0; cả dấu state trước và sau. |

`tests/test_ca_vhc_composition_dag.py` hiện có 5 test, chưa có các ca đối chứng của R01–R03. Cần thêm test chi phí với trọng số không mặc định cho cả `CONNECT`/`LIFT`, và test DP chứng minh legibility của state đầu/state sau chỉ cộng một lần trong cả hai nhánh. Test hiện tại chỉ kiểm tra no-double-count trực tiếp cho `LIFT`; các DEV specimen nghiệm thu không thay thế synthetic hard-collision boundary tests.

**Chưa xác minh:** chưa chạy suite trên checkout của TV4; finding dựa trên diff/code tại commit đã nêu. TV2 chỉ sign-off sau khi TV4 sửa và có test chạy PASS trên commit recheck cụ thể.
