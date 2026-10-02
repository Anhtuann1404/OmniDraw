# Roadmap triển khai và kế hoạch 8 tháng

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API nghiên cứu](32_research_api_and_artifact_contract.md) là nguồn triển khai.

Bảng duy nhất có hiệu lực là **Docs 30 §5**. Tháng tính từ mốc bắt đầu thực hiện được nhóm xác nhận, không tự suy ra ngày bắt đầu từ thông báo đồng ý hướng đề tài.

## Các chặng

1. Tháng 1: contract, đọc toàn văn Balas, split mới, quy tắc xếp hạng/budget, đề xuất epsilon và tham số.
2. Tháng 2: DP một mục tiêu, oracle độc lập, top-m và beam; số đo sơ bộ nếu có thiết bị.
3. Tháng 3: đối chiếu ca nhỏ thật/ngẫu nhiên, ví dụ có lợi/bằng nhau, độ nhạy/chứng nhận; khóa code/manifest/điểm vận hành cuối tháng.
4. Tháng 4: mở Holdout mới có nhật ký sau freeze; đánh giá chính thức, báo coverage và các ca incomplete.
5. Tháng 5: phân tích kết quả, phân bố biên/nét chờ theo ngân sách; chuẩn bị thí điểm font có giấy phép.
6. Tháng 6: font và vật lý có điều kiện; viết chương kết quả. Máy chưa có không ngăn hoàn thành lõi phần mềm.
7. Tháng 7: báo cáo khoa học, giới hạn, bản thảo bài báo.
8. Tháng 8: QA, gói tái lập và hồ sơ bảo vệ.

## Thứ tự thực hiện hiện tại

S0 contract → S1 fixtures → S2 oracle/S3 DP → S4 baseline/runner → S5 lập luận/S6 độ nhạy → S7 freeze/Holdout → S8 font/máy. Các nhánh PR cũ là checkpoint tích hợp, không thay cho gate hướng mới.

## Phương án khi trượt mốc

Hết tháng 3 chưa khớp oracle: không mở Holdout, không làm font, không thêm Pareto. Giảm khảo sát w/b mở rộng trước, rồi họ ví dụ lớn; giữ ví dụ tối thiểu, oracle, baseline, mô hình và gói tái lập. Nếu lõi còn trễ tháng 6, hoãn font để giữ báo cáo tháng 7–8. Không đổi tham số sau mở Holdout để đạt ngưỡng cũ.
