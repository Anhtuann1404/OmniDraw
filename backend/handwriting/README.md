# Luồng sản phẩm handwriting hiện hữu

`engine.py` và font packs tạo chữ/SVG cho API sản phẩm. `composition.py`, `baselines.py`, `metrics_evaluator.py`, `experiment_runner.py` phục vụ contract CA-VHC/PR cũ và kiểm hồi quy. Mã vẫn đang dùng; PR3 đã đóng không có nghĩa phải xóa mã sản phẩm.

Hướng nghiên cứu mới ở [../research/](../research/README.md), theo Docs 31/32. Không đổi tên runner B1/B2/B3/Proposed thành top-m/beam hoặc dùng CSV 19 cột thay artifact mới.

`evaluate_composition_state` có legibility/placement; `evaluate_composition_transition` có curvature/collision và sinh bridge; `optimize_composition_dag` tối ưu theo mục tiêu cũ. Các hàm này không là DP S=(i,t,A,P,e) hoặc hàm J nghiên cứu mới. Dùng lại glyph/world geometry chỉ qua adapter sau kiểm IDs/ownership/coordinates/representation; biến đổi style phải trước khi hash tập ứng viên, không sau solve.

Tests `test_pr3_*` và `test_ca_vhc_*` giữ phạm vi hồi quy cũ. Mốc PASS/sign-off chỉ có hiệu lực tại commit/phạm vi đã ký; không tự chứng minh solver nghiên cứu mới.
