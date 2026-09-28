# TV2 — Motion research handoff (28/09/2026)

**Trạng thái:** đề xuất kỹ thuật của TV2 để TV4 tích hợp vào RQ chung; không phải kết quả thực nghiệm hay phê duyệt RQ freeze. PR3/PR4 và các gate máy thật vẫn độc lập.

## Câu hỏi và giả thuyết kiểm chứng

1. **Art Mode / tối ưu thứ tự nét.** Trên *cùng tập polyline đã trích xuất và nối chuỗi*, thứ tự hiện hành có giảm `pen_lift_distance_mm` so với (a) thứ tự contour gốc và (b) greedy nearest-neighbor Euclid hay không? Giả thuyết hướng: giảm quãng đường pen-up mà không thay hình học pen-down hoặc số nét. Báo cáo cả `pen_lift_count`, `total_path_length_mm`, thời gian tối ưu median/p95 và hình ảnh SVG; không đặt ngưỡng PASS từ một mẫu smoke test.
2. **Handwriting / RQ1.** Dùng H1.1 và H1.2, ba baseline B1/B2/B3 và corpus ghép cặp đúng theo [Research Plan §3.1](10_nckh_research_plan.md). H1.2 lấy tỷ lệ trên **tổng** `pen_lift_count` của cùng các ca, không lấy median theo từ. B3/default phải giữ hành vi hiện hành; phương pháp CA-VHC là đối tượng nghiên cứu, không phải baseline thứ tư.
3. **Động học / RQ3.** Kiểm tra H3.1/H3.2 theo [Research Plan §3.3](10_nckh_research_plan.md). `acute_turn_count_120deg` **chưa triển khai**, do đó không thể tuyên bố H3.2 PASS trước khi có định nghĩa, test và số đo của metric này. Các ngưỡng H3.1 trong Research Plan hiện hành là nguồn cho runner; nếu tài liệu cũ còn ngưỡng khác, TV4 cần giải quyết trước freeze.
4. **Thời gian thi công.** Phân biệt `optimize_time_ms` (thời gian CPU), `estimated_draw_time_sec` (mô phỏng) và `actual_draw_time_sec` (chỉ từ job máy thật có provenance). Mô hình constant-speed ở [measurement protocol §7](hardware/measurement-protocol.md) là baseline mô phỏng; `accel_pct=75` là phần trăm cấu hình driver, không phải gia tốc đo bằng mm/s². Chưa suy ra thời gian máy thật hoặc góc cua thực tế từ SVG hay simulator.

## Ký hiệu và so sánh công bằng

Với một thứ tự nét $\pi$ và hướng $r_i$, đặt $e_i$ là điểm cuối nét $i$ và $s_j$ là điểm đầu nét $j$. Quãng đường di chuyển nhấc bút nội bộ là $L_{up}=\sum_{i=1}^{N-1}\lVert e_{\pi_i,r_i}-s_{\pi_{i+1},r_{i+1}}\rVert_2$. Nếu dùng gốc máy/điểm về nhà, báo cáo riêng phần từ gốc tới nét đầu và từ nét cuối về gốc; không cộng hai phần này vào một baseline nhưng bỏ ở baseline khác. Chi phí chọn ứng viên theo code Art Mode là $c=\operatorname{dist}+\lambda(1-\cos\theta)$, với vector tiếp tuyến bằng 0 hoặc khoảng cách bằng 0 thì chỉ dùng `dist`. $\lambda$ có đơn vị cùng hệ tọa độ với `dist` (pixel trong optimizer hiện tại), **không** phải thời gian hoặc gia tốc vật lý. Phép cải tiến Or-opt hiện tối ưu quãng đường hình học; không diễn giải `kinematic_cost` là toàn bộ hàm mục tiêu của pipeline.

So sánh ba phương pháp trên cùng raster, style, tham số trích xuất, tập stroke sau chain, khổ A4, scale và điểm bắt đầu cố định. Baseline (a) dùng thứ tự gốc, không đảo nét; (b) gọi greedy nearest-neighbor với `lambda_turn=0`; (c) chạy pipeline hiện hành `nearest_neighbor_order` + `two_opt_improve` + `or_opt_improve`. Ghi commit, OS, CPU, Python/NumPy/BLAS, chế độ nguồn; không pool latency Windows và Linux. Chạy warm-up và lặp nhiều lần trước khi báo cáo median/p95, giữ kết quả từng ca và bản SVG để đối chiếu bằng mắt. Một fixture tổng hợp chỉ kiểm tra đường chạy, không chứng minh giả thuyết.

## Fixture Art Mode bàn giao TV3

- Input tất định: `tests/fixtures/tv2_art_mode_smoke_input.png`, sinh lại bằng `make_art_mode_smoke_input.py` cùng thư mục.
- Output qua `backend/path_optimizer.py --style line_art --paper_width_mm 210 --paper_height_mm 297`: `tests/fixtures/output_tv2_art_mode_smoke.svg`. Đây là **Art Mode**, không phải specimen RQ3 hay đường viết tay.
- TV3 có thể dùng SVG này cho lượt chạy số 4 trong protocol để kiểm tra khả năng parse, vận tốc pen-down/pen-up và CSV 22 trường. Kết quả simulator phải mang nhãn simulator; chỉ job vật lý thành công mới có `actual_hardware_measured=true`.
- Hình tổng hợp không đủ để đánh giá thẩm mỹ hay độ chính xác ảnh thật. Trước benchmark chính thức cần corpus Art Mode có nguồn, quyền sử dụng, ảnh đầu vào và khóa train/dev/holdout rõ ràng.

**Kiểm tra kỹ thuật ngày 28/09/2026:** Pipeline `line_art` trích 23 stroke thô, nối còn 16; SVG A4 có `pen_lift_count=15`, `pen_lift_distance_mm=215.662`. Lệnh `python scripts/tv2_art_mode_compare.py tests/fixtures/tv2_art_mode_smoke_input.png` trả về quãng đường pen-up lần lượt 2158.464 px (gốc), 657.257 px (greedy) và 657.257 px (pipeline hiện hành). Vì pipeline **không hơn greedy trên mẫu này**, không có kết luận ưu thế thuật toán. Thời gian order một lượt cũng không được dùng làm median/p95. CLI TV3 `--smoke-test --mode simulator --svg tests/fixtures/output_tv2_art_mode_smoke.svg` PASS; `actual_draw_time_sec=85.27` là thời gian **giả lập**, `actual_hardware_measured=false`, không phải số đo máy thật.

**Cần TV4/TV3 xác nhận:** TV4 quyết định đưa các giả thuyết/công thức này vào bản RQ freeze và thời điểm triển khai metric góc; TV3 chạy fixture trên simulator trước, sau đó dùng máy thật khi có thiết bị và giữ log provenance. Tài liệu này không tự đóng E4, PR3, PR4 hay gate thực nghiệm.
