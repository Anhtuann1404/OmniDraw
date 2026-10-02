> **HISTORICAL_RECORD — không là đặc tả hiện hành.** Đọc [hướng hiện tại](../../README.md), [contract](../../31_joint_solver_contract.md) và [công việc](../../03_current-task.md). Giữ kết luận đúng phạm vi/commit gốc.

# Bản trao đổi về hướng nghiên cứu và kế hoạch đã thống nhất

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](../../30_research_development_plan.md), [contract solver](../../31_joint_solver_contract.md), [API nghiên cứu](../../32_research_api_and_artifact_contract.md) là nguồn triển khai.

## 1. Trọng tâm

Nhóm nghiên cứu đồng tối ưu hình học thân/dấu và lịch nét chữ tiếng Việt trong tập ứng viên hữu hạn. So sánh với staged top-m theo hai ranking đăng ký trước và beam search; phân tích khi có lợi/bằng nhau và độ nhạy hai tham số chuyển động. Đề tài áp dụng và phân tích có kiểm soát DP ràng buộc thứ tự và tính chất lồi chuẩn; không tuyên bố thuật toán mới.

## 2. Kết quả đứng được khi gap bằng nhau

Mô hình chữ/dấu, điều kiện đủ tách được, đường gap theo m, chi phí chứng nhận chất lượng heuristic và quy trình đánh giá độc lập vẫn là đầu ra. Muốn kết luận tương đương phải có epsilon được duyệt trước, coverage và độ bất định phù hợp; nếu không ghi chưa đủ bằng chứng. Preflight 0/16 cấu hình thật và 25/40 tổng hợp chỉ thăm dò, không thay đánh giá mới.

## 3. Phạm vi, nhân lực và tiến độ

TV4 mô hình/DP/tích hợp; TV2 cost/baseline/runner/phân tích; TV1 dữ liệu/Holdout/font; TV3 oracle độc lập/thiết bị. Một thí điểm font có điều kiện. Writer Profile, Pareto và cắt tỉa nâng cao ngoài cam kết. Kế hoạch 8 tháng duy nhất và phương án cắt ở Docs 30; không giữ một bảng 4 tháng khác.

## 4. Nguồn gốc quyết định

TV4 thông báo GVHD đã đồng ý hướng đề tài ngày 02/10/2026. Những phản biện nhập vai trước đó là phân tích mô phỏng và quyết định của nhóm, không tự chuyển thành lời của GVHD thật. Việc đồng ý hướng chưa chốt epsilon, điểm vận hành, số mẫu hay sign-off kỹ thuật. Đề cương nộp được đồng bộ riêng ở Docs 29.
