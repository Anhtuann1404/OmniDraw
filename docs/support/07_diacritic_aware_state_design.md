> **SUPPORTING_REFERENCE.** Nguồn quyết định: [kế hoạch](../30_research_development_plan.md), [contract solver](../31_joint_solver_contract.md), [API](../32_research_api_and_artifact_contract.md). Nội dung trùng hoặc khác phải đề xuất sửa nguồn chính; không tự ghi đè đặc tả.

# Ghi chú state DP — tài liệu hỗ trợ

Định nghĩa có hiệu lực nằm trong [Contract solver §5](../31_joint_solver_contract.md). File này là chỉ dẫn đọc, không là một đặc tả cạnh tranh.

- Đọc state `(i,t,A,P,e)`, BODY/MARK/END, deadline và ví dụ tại §5.1–5.3.
- Quên assignment nhưng giữ endpoint độc lập tại §5.4; cận tại §5.5.
- TV4 kiểm no-forget/safe-forget trước đối chiếu oracle TV3 độc lập; hai kiểm tra có vai trò khác nhau.
- Không thêm geometry/style sau solve. Thay state phải sửa contract chính và fixtures trước code.
