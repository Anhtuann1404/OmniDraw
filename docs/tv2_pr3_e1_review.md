# TV2 — PR3 E1 DEV pen-up review

- `REVIEWED_COMMIT: adb0417fe3748643e7b19ce5d522716f7f445b7c`
- `CONTRACT: Docs 09 E1; evidence: Docs 17 §12`
- `AI_TECHNICAL_VERDICT: PASS_SOFTWARE_DEV`
- `TV2_HUMAN_SIGN_OFF: APPROVED` — chính TV2 xác nhận verdict E1 trên DEV trong hội thoại ngày 2026-09-29; không điền tên cá nhân chưa được cung cấp.
- `PR3_EXIT_SIGN_OFF: PENDING` — biến thiên style và các exit gate khác cần quyết định riêng.

## Bằng chứng E1

`build_benchmark_rows()` nhận cùng 20 từ `BENCHMARK_DEV_CORPUS_20`, hai font `oly`/`omni_casual`, bốn seed `42, 100, 2026, 999999` và style `hand_hocsinh` cho từng method. Cùng `evaluate_ca_vhc_metrics(result)` tính `pen_lift_distance_mm` từ khoảng cách Euclid giữa các nét liên tiếp trong `result.strokes` (`backend/handwriting/experiment_runner.py`, `metrics_evaluator.py`). Tôi chạy lại trên đúng commit nêu trên; 160 ca/method cho kết quả:

| Method | `oly` (mm) | `omni_casual` (mm) | Tổng (mm) |
|---|---:|---:|---:|
| B1 Static | 2167.473 | 2606.385 | 4773.858 |
| B2 Greedy | 2127.310 | 2578.424 | 4705.734 |
| Proposed PR3 | 1941.020 | 2396.828 | 4337.848 |

Từ tổng tích lũy trên các ca ghép cặp, Proposed giảm **9.133%** so B1 và **7.818%** so B2. Phép tính độc lập khớp Docs 17 §12. Chỉ dùng DEV, không đọc/chạy HOLDOUT. `tests/test_pr3_renderer_integration.py` đạt **6 passed** trên commit này; số **236 passed, 1 warning** của toàn suite là báo cáo TV4, không phải kết quả tôi chạy lại.

## Tính công bằng, hình học và trace

- B1/B2/Proposed dùng chung runner và metric. `engine.py:1611–1613` chỉ gọi `_order_pr3_secondary_strokes()` trong `pr3_composition`; B1/B2/B3 không bị sửa. Helper tại `engine.py:809–847` hoán vị nguyên cặp `(stroke, metadata)` theo nhóm `char_idx`, giữ thứ tự các nét trong cùng ký tự và chỉ nhận phương án nếu pen-up trong từ giảm.
- Cùng tên style chưa đồng nghĩa cùng phép biến đổi cuối: B1/B2 áp dụng `apply_bio_variation()` tại `engine.py:1622–1625,1665–1668`, Proposed giữ geometry đã được E4 đánh giá. Kiểm tra độ nhạy tạm thời bằng cách tắt biến thiên cho B1/B2 (không sửa repository) cho tổng B1 = **4769.028 mm**, B2 = **4701.376 mm**; Proposed vẫn **4337.848 mm**, tức giảm **9.041%** và **7.732%**. Sai khác style không đảo chiều verdict E1 trên ma trận này; việc bảo toàn style của PR3 vẫn là exit gate riêng.
- Test `test_pr3_secondary_route_keeps_geometry_and_within_glyph_order` và `test_pr3_reordered_secondary_trace_matches_rendered_strokes` bảo vệ thứ tự nội ký tự và ánh xạ trace. Đối chứng độc lập bật/tắt helper trên từ DEV `trường` (`oly`, seed 42) cho cùng multiset tọa độ từng nét, trace khớp `result.strokes[continuous_stroke_id]`; pen-up giảm từ **50.301** xuống **37.797 mm**. Không có bằng chứng helper sửa hình học nét.

## Giới hạn và việc TV4 nên đồng bộ

- Đây là `PASS_SOFTWARE_DEV` cho tiêu chí E1 của Docs 09, **không** phải kết luận H1.1/PR5 hay thời gian vẽ trên máy thật. Helper tối ưu pen-up *trong từng từ*; không chứng minh quãng đường toàn trang hoặc thời gian cơ học đều giảm.
- Docs 17 §11 còn ghi E1 `NOT_PASSED` và “xử lý E1” là gate mở theo snapshot cũ; TV4 nên ghi rõ §12 thay thế kết luận E1 đó. §12 cũng nên lưu lệnh chạy/CSV từng ca và execution metadata để người khác tái lập. Đây là chỉnh tài liệu/bằng chứng, không yêu cầu sửa code TV4 trong phiếu này.
- Shared transition đã được TV2 ký riêng tại `0cf3de1`; E1 review không tự ký PR3 exit. Biến thiên style và các gate downstream vẫn mở.
