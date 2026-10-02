# Chương 1 — Định hướng và bài toán nghiên cứu

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API nghiên cứu](32_research_api_and_artifact_contract.md) là nguồn triển khai.

## Bối cảnh

Để máy vẽ thực hiện chữ tiếng Việt bằng nét đơn, nhóm phải chọn hình học thân/dấu và lịch vẽ các nét. Hai lựa chọn có thể tác động đến đường di chuyển, số chu kỳ bút và khoảng hở. Đề tài nghiên cứu tương tác đó trong tập ứng viên hữu hạn với bố trí từ cố định.

## Vấn đề và mục tiêu

So sánh đồng tối ưu với phân tầng top-m, tìm điều kiện có lợi/bằng nhau, đánh giá độ nhạy theo tham số chuyển động. Mục tiêu vô hướng J dùng chiều dài vẽ, di chuyển UP và chu kỳ bút; mô hình chưa có gia tốc nên không gọi là thời gian thực. Ràng buộc clearance c_min=0.20 mm trên cặp cần tách và contacts khai báo là thành phần khả thi.

## Đóng góp dự kiến

Mô hình chữ/dấu tiếng Việt; đường gap theo số cấu hình m; phân tích cấu trúc/độ phức tạp và kiểm chứng độc lập; quy trình đánh giá đăng ký trước. Áp dụng DP ràng buộc thứ tự và tính chất lồi chuẩn, không khẳng định lần đầu hoặc thuật toán mới. Khảo sát toàn văn và phạm vi tra cứu phải được báo trước kết luận khoảng trống.

## Phạm vi

Lõi nghiên cứu phần mềm với split Holdout mới. Font chọn lọc là một thí điểm có điều kiện; không cam kết sửa mọi TTF/OTF. Máy phẳng hai trục là kiểm chứng bổ sung khi sẵn sàng. Art Mode/thư tay là chức năng sản phẩm. Writer Profile, Pareto và cắt tỉa mở rộng ngoài cam kết. Câu hỏi/đầu ra chi tiết tại Docs 05 và đề cương Docs 29.
