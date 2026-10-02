# Thí điểm font thiết kế tiếng Việt — N-RQ4

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API nghiên cứu](32_research_api_and_artifact_contract.md) là nguồn triển khai.

Tên file giữ để tương thích link lịch sử RQ5; trong hướng mới thí điểm mang ID N-RQ4, không có hai thí điểm Writer Profile và font song song.

## Phạm vi và owner

TV1 chủ trì license/base glyph/anchor/data/quality fixtures; TV4 chủ trì candidate model, nét đơn, solver/SVG và tích hợp. TV2 thiết kế đối chứng/phân tích; TV3 kiểm hình học độc lập. Sau lõi qua freeze/Holdout gate mới thực hiện; trượt mốc thì hoãn, không ảnh hưởng phương án hoàn thành tối thiểu.

## Quy trình dự kiến

1. Chọn trước số font và tiêu chí trên DEV; quyền sử dụng/chỉnh sửa/redistribute tách riêng. Có base glyph, không khôi phục chữ cơ sở thiếu.
2. Ghi mapping Unicode/base/mark; xác định glyph và neo mặc định làm mẫu tham chiếu; thiếu neo thì quy tắc dựng phải khóa trên DEV.
3. Chuyển outline sang nét đơn chỉ trên lớp glyph mà phương pháp kiểm được; outline TTF/OTF không mặc nhiên là nét bút. Case không đạt báo unsupported, không che bằng solver.
4. Sinh ứng viên hình học hữu hạn; kiểm contact/clearance c_min=0.20 mm trên cặp phải tách; bản render khớp bản chấm.
5. So bản gốc (nếu có nét đơn tương ứng hợp lệ), bản chỉnh tay và bản dựng; ghi khác biệt biểu diễn, công chỉnh tay và coverage. Không so cost trực tiếp outline nhiều biên với skeleton nếu không chuẩn hóa bài toán.
6. Chạy solver theo contract chung, xác nhận independent violations kỳ vọng 0 và tỷ lệ ca vô nghiệm/unsupported; không dùng ca fail để chỉnh Holdout đã mở.

## Chỉ tiêu và sản phẩm

License manifest, candidate/anchor hashes, base/mark coverage, clearance/violations kiểm độc lập, infeasible/unsupported rate, paired quality rubric khóa trước và per-case artifacts. J/runtime chỉ so cùng representation/candidate scope. Kết quả là khả năng thí điểm trên font đã chọn, không tuyên bố sửa mọi font hoặc luôn giữ nguyên thẩm mỹ.
