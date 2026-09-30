# TV2 — PR3 style, E1 và exit recheck

- `REVIEWED_BRANCH: codex/tv4-pr3-slices`
- `REVIEWED_COMMIT: 18b19623d1089b7ba148ef827593c9337ffa3779`
- `STYLE_CODE_COMMIT: 072029bd1e703021c4ad643d53692e81e0a022a4`
- `STYLE_VERDICT: CHANGES_REQUESTED` — phạm vi bỏ micro-jitter sau DAG là hợp lý và hình học style đã được đánh giá trước khi render, nhưng metadata tiếp tuyến trong bridge trace chưa khớp hình học đã chọn.
- `E1_VERDICT: PASS_SOFTWARE_DEV` — chỉ cho Docs 09 E1 trên ma trận DEV tại commit được review.
- `PR3_EXIT_SIGN_OFF: PENDING` — cần đóng finding `TV2-PR3-R04` và recheck trace trước khi TV2 ký exit.
- `TV2_HUMAN_SIGN_OFF: PENDING` — các verdict kỹ thuật trong phiếu này chưa thay thế xác nhận của TV2.

## Style, dấu, bridge và hard collision

`engine.py::_style_pr3_world()` áp dụng shear và drift xác định cho base strokes, dấu, port và tiếp tuyến trong world mm. `prune_composition_states()` nhận chính geometry này; DAG đánh giá state/transition trên các layer đã biến đổi; renderer lấy lại `pr3_world` của state được chọn. Độ giãn chữ đã nằm trong `scale_vec`. Vì vậy phạm vi bốn preset ở Docs 17 §13 (giãn chữ, slant, drift; không có random micro-jitter sau DAG) là một phạm vi phần mềm có thể chấp nhận theo nguyên tắc E4: geometry được chấm phải là geometry được vẽ. Đây không phải khẳng định parity đầy đủ với B1/B2/B3 có jitter.

Kiểm tra độc lập trên `18b1962`:

- Nhóm test PR3/Composition/Baselines/ASCII liên quan: **100 passed**. Lần chạy đầu có 99 passed và một lỗi setup do thư mục temp Windows không cho đọc; chạy lại đúng test với `--basetemp` trong worktree đạt 1 passed. Không coi lỗi môi trường đó là lỗi PR3. Con số full suite **270 passed, 1 warning** là báo cáo TV4, chưa chạy độc lập ở lượt này.
- Hai từ DEV `tiếng`, `nguyễn` × bốn preset, font `cursive`, seed 42: toàn bộ nét dấu render khớp byte với nét dấu của state được DAG chọn; **20 bridge CONNECT** khớp byte với transition bridge trong trace; hard collision không chạm base/dấu và clearance đạt ngưỡng 0,20 mm.
- Từ DEV `đường` × bốn preset, font `cursive`, seed 42: mỗi ca có một bridge và một nét gạch `đ`, không có tiếp xúc giữa hai nét trong bốn ca đã kiểm tra. Nét gạch `đ` hiện được thêm sau DAG; phép kiểm tra này không chứng minh hard collision với nét gạch cho mọi đầu vào.

### `TV2-PR3-R04` — bridge trace lưu tiếp tuyến trước style

Ở `engine.py:1522–1525`, `v_ex_world`/`v_en_world` cho metadata được tính từ variant và `scale_vec`, chưa qua `_style_pr3_world()`. `engine.py:1559–1560` lưu các vector đó trong `bridge_stroke.meta`. Trong khi đó transition đã dùng `pr3_world[*].v_exit/v_entry` sau slant. Đối chiếu độc lập trên từ DEV `tiếng`, font `cursive`, seed 42 cho một bridge CONNECT mỗi preset:

| Style | Sai khác `v_exit` | Sai khác `v_entry` |
|---|---:|---:|
| `hand_hocsinh` | 0,113214 | 0,112108 |
| `hand_nguoilon` | 0,241494 | 0,239005 |
| `hand_thuphap` | 0,202466 | 0,200126 |
| `hand_chukinhanh` | 0,313918 | 0,310835 |

Tọa độ bridge và `p_exit/p_entry` vẫn khớp; `curvature_cost` lấy từ transition breakdown đã chấm đúng. Finding này là sai lệch metadata trace, không phải bằng chứng va chạm hay render bridge sai. Để đóng R04, TV4 cần ghi tiếp tuyến từ `pr3_world` đã chọn vào trace của PR3 (hoặc bỏ trường không còn đúng nếu contract không cần), rồi thêm assertion cho cả bốn preset rằng metadata bridge khớp tiếp tuyến của geometry đã chấm. Không thay đường B3/default.

## E1 trên mã style mới

Đã đối chiếu `docs/evidence/pr3_e1_dev_rows.csv` và metadata: **480 dòng**, 20 ID DEV, 160 ca/method, đủ 2 font × 4 seed, không có khóa ca lặp hoặc ID HOLDOUT; SHA-256 CSV khớp `pr3_e1_dev_metadata.json`. Tái tính tổng từ các dòng CSV; dựng lại độc lập 9 ca DEV rải ở đầu/giữa/cuối corpus cho B1/B2/Proposed, trong đó `pen_lift_distance_mm`, lift count, collision count và stroke fingerprint đều khớp dòng đã lưu. Sau đó chạy lại toàn bộ script evidence trên `18b1962`: CSV 480 dòng tái sinh **trùng byte** với bản đã commit (SHA-256 `f8b6d13bf432c5aba0be8b36b8003ac73922f4ed36561c9d684d622f2981de40`). Metadata tái sinh chỉ khác `source_commit` (`18b1962` thay `072029b`) và phiên bản môi trường Python/NumPy (3.12.10/2.5.3 thay 3.14.6/2.5.2); không có thay đổi dữ liệu hoặc tổng E1.

| Method | Tổng pen-up (mm) |
|---|---:|
| B1 Static | 4773,858 |
| B2 Greedy | 4705,734 |
| Proposed PR3 | 4343,360 |

Proposed giảm **9,018%** so B1 và **7,701%** so B2. Điều này đáp ứng tiêu chí so sánh phần mềm E1 trên DEV tại `18b1962`; phiếu `f1b309c` chỉ áp dụng cho `adb0417`. Metadata ghi `source_commit=072029b` là commit mã đã sinh CSV; Docs 17 §13 được thêm ở `18b1962`. Kết luận H1.1/PR5, thời gian máy thật và hiệu quả trên HOLDOUT vẫn mở.

## PR3 exit

**Chưa ký exit.** Gate TV2 còn thiếu là sửa hoặc loại metadata tiếp tuyến bridge không khớp geometry style (`TV2-PR3-R04`) và recheck assertion tương ứng. TV4 cũng nên xác định phạm vi hard collision cho nét gạch `đ` vì nét này được thêm sau DAG và không nằm trong bốn tập base/dấu mà transition kiểm tra; bốn ca DEV đã thử không phát hiện va chạm, nhưng `collision_count=0` trong CSV chỉ đo bridge–diacritic. Việc này cần quyết định phạm vi/test rõ trước khi tuyên bố bảo đảm hard collision cho mọi nét render.

TV2 không sửa code TV4 trong lượt review này. E1 DEV không tự đóng H1.1/PR5, và kết quả phần mềm không thay thế calibration vật lý.
