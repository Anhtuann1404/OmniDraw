# Đặc tả nghiên cứu chữ/dấu tiếng Việt

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API nghiên cứu](32_research_api_and_artifact_contract.md) là nguồn triển khai.

CA-VHC là tên làm việc của mô hình chữ/dấu trong OmniDraw; không dùng tên này để khẳng định một thuật toán mới chưa đối chiếu tài liệu. Đề tài áp dụng và phân tích có kiểm soát DP ràng buộc thứ tự và tính chất lồi chuẩn trong tập ứng viên hữu hạn.

## Mục tiêu và câu hỏi

| ID hiện hành | Câu hỏi | Kết quả cần có |
|---|---|---|
| N-RQ1 / MT1 | Đồng tối ưu có lợi thế nào so staged top-m khi m tăng, khi nào bằng nhau? | Gap theo m, m*, hai ranking, chi phí toàn pipeline; điều kiện đủ tách được, ví dụ glyph tham số hóa; m=toàn bộ khớp joint |
| N-RQ2 / MT2 | Mô hình tương tác dấu có khả thi và không gian trạng thái lớn đến đâu? | Vi phạm kiểm độc lập kỳ vọng 0, tỷ lệ ca xác nhận vô nghiệm, cận state và phân bố w/b/P; DP khớp oracle |
| N-RQ3 / MT3 | Quyết định và regret đổi thế nào theo rho/lambda? | Bản đồ độ nhạy, chứng nhận lịch cố định ở bốn đỉnh, chi phí chứng nhận; vật lý có điều kiện |
| N-RQ4 | Thí điểm tinh chỉnh font chọn lọc có tạo glyph tiếng Việt khả thi? | License/base glyph/anchor/collision checks và so bản gốc/bản chỉnh tay; có điều kiện |

ID N-RQ tránh lẫn RQ1–RQ5 của kế hoạch cũ. Ngưỡng giảm pen-up 25%, lift 35% và tăng chiều dài ≤10% cũ chỉ còn là chỉ số lịch sử, không là nghiệm thu tự động của J mới. Đề cương mới không cam kết trước cải thiện số cụ thể.

## Đặc tả bắt buộc

[Docs 31](31_joint_solver_contract.md) quy định lịch khả thi, c_min, cost, state/recurrence, ranking, budget, tie và regret. [Docs 32](32_research_api_and_artifact_contract.md) quy định input/output và artifact. Thay đổi các quy ước cần version và cùng áp dụng cho DP, oracle, staged và beam.

Phần lõi bắt buộc: mô hình, solver một mục tiêu, oracle độc lập, top-m/beam, phân tích có lợi/bằng nhau, độ nhạy và gói tái lập. Không suy luận thói quen viết người từ ảnh; cửa sổ dấu là cơ chế giới hạn tìm kiếm. Pareto và cắt tỉa mở rộng ngoài cam kết.

## Đánh giá trung thực

Chỉ kết luận trong tập đã khóa và đủ coverage. Ca infeasible, timeout, ranking incomplete và kết quả thiếu chứng nhận được báo riêng. Kết cục có thể hữu ích, tương đương thực dụng hoặc chưa đủ bằng chứng; epsilon_eq cần căn cứ, duyệt và khóa trước Holdout. Không kết luận tương đương từ p>0.05. Dữ liệu cũ/preflight có nguy cơ nhiễm, không thay split mới.
