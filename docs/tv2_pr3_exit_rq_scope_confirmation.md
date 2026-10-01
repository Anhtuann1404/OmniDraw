# TV2 — Xác nhận PR3 software exit và phạm vi RQ chuyển động

- `CONFIRMATION_DATE: 2026-10-01 (Asia/Saigon)`
- `TV2_HUMAN_CONFIRMATION: APPROVED` — TV2 xác nhận trực tiếp cả hai mục trong hội thoại ngày 01/10/2026; phiếu này ghi lại quyết định đó, không tự nhận chữ ký của thành viên khác.
- `REVIEWED_TV4_COMMIT: c1b4696bbc426dfe76e0453557575ec03ea5d651`
- `REVIEWED_TV2_HEAD: 0b21232ae84911713e7040a9643f5ebe4a27ffb9`
- `RESEARCH_PLAN_SNAPSHOT: docs/10_nckh_research_plan.md` tại `0b21232` (blob `af6fb9e70197a80080ae60f3734b9132d3212cb6`)
- `PR3_SOFTWARE_EXIT_SIGN_OFF: APPROVED_WITH_DOCUMENTED_SCOPE`
- `TV2_RQ_MOTION_SCOPE_VERDICT: PASS`
- `GLOBAL_RQ_FREEZE: PENDING_TEAM_APPROVAL`

## 1. PR3 software exit tại `c1b4696`

`TV2-PR3-R04: VERIFIED_CLOSED`. Bridge trace của PR3 lấy `v_exit`/`v_entry` từ `pr3_world` của đúng hai state đã chọn sau biến đổi style; port và `curvature_cost` vẫn lấy cùng transition đã chấm. Regression test so sánh các trường này cho cả bốn preset. Bản vá chỉ đổi metadata trace của PR3, không đổi geometry bridge hay đường B3/default. TV2 đã chạy độc lập bộ test được Git theo dõi cùng `backend/test_handwriting_validation.py`: **278 passed, 1 warning** (Starlette deprecation).

TV2 chấp nhận phạm vi style đã công bố ở Docs 17 §13: giãn chữ, slant affine và drift xác định được áp dụng trước prune/DAG; PR3 không thêm micro-jitter ngẫu nhiên sau DAG. TV2 cũng chấp nhận giới hạn hard collision của §13.3 cho **software exit**: transition kiểm tra bridge với base/dấu của hai state kề nhau, ngoại lệ tiếp xúc đúng port theo E4. Nét gạch `đ/Đ` được render sau DAG nên chưa thuộc tập vật cản; `collision_count=0` chỉ đo bridge–diacritic và không chứng minh mọi nét trong toàn văn bản không va chạm. Không mở rộng claim này nếu chưa đưa nét gạch vào geometry trước DAG và kiểm thử lại.

`E1_VERDICT: PASS_SOFTWARE_DEV` tiếp tục áp dụng: bản vá `c1b4696` không đổi geometry/CSV E1 đã tái sinh trùng byte ở phiếu `tv2_pr3_style_e1_exit_recheck.md` cho `18b1962`. Đây là nghiệm thu phần mềm trên DEV, **không** phải kết luận H1.1/PR5, HOLDOUT, thời gian máy thật hoặc calibration vật lý.

## 2. Phạm vi TV2 của Research Freeze Pack

TV2 xác nhận **phạm vi chuyển động/RQ1–RQ3 được giao cho TV2**, gồm định nghĩa B1/B2/B3 so với Proposed, công thức Viterbi và nhánh `CONNECT`/`LIFT` của `J_transition`, quy tắc tổng hợp pen-up/pen-lift theo corpus ghép cặp, curvature và ranh giới metric chưa triển khai. Phiếu `reviews/tv2_chapter_1_3_review.md` đã có `WORKFLOW_STATUS: CLOSED`, `HUMAN_VERDICT: PASS`, checkpoint v0.2 `7ae43e6`, recheck `e26af4f` và xác minh tích hợp `031d198`; TV2-R01–R06 đều `VERIFIED_CLOSED`. Xác nhận hiện tại ràng buộc thêm với snapshot Docs 10 nêu trên, không diễn giải lại các finding đã đóng.

`acute_turn_count_120deg` vẫn chưa triển khai: cần định nghĩa, test và tích hợp evaluator trước khi đánh giá H3.2 ở PR5. Các giá trị H1.1/H1.2/H3.1/H3.2 và bảng kết quả formal vẫn `PENDING`; không dùng E1 DEV để kết luận giả thuyết. `GLOBAL_RQ_FREEZE` vẫn cần các owner còn lại và TV4 đối chiếu trạng thái/disposition trên bản hợp nhất. Câu trong Docs 10 §7.1 nói checkpoint phiếu TV2 còn chờ đồng bộ là trạng thái cũ so với phiếu TV2 hiện hành đã ghi `REVIEW_TARGET_COMMIT: 7ae43e6`; TV4 cần đồng bộ wording, không yêu cầu TV2 review lại từ đầu.

Không sửa mã TV4, không chạy HOLDOUT và không push trực tiếp `develop` trong lượt xác nhận này.
