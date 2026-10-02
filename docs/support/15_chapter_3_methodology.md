> **SUPPORTING_REFERENCE.** Nguồn quyết định: [kế hoạch](../30_research_development_plan.md), [contract solver](../31_joint_solver_contract.md), [API](../32_research_api_and_artifact_contract.md). Nội dung trùng hoặc khác phải đề xuất sửa nguồn chính; không tự ghi đè đặc tả.

# Chương 3 — Phương pháp và quy trình thực nghiệm

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](../30_research_development_plan.md), [contract solver](../31_joint_solver_contract.md), [API nghiên cứu](../32_research_api_and_artifact_contract.md) là nguồn triển khai.

## 1. Chuẩn hóa input

TV1 chuẩn bị glyph/marks/anchors/license và finite candidate manifest. Mỗi ứng viên trọn chữ có stroke ownership, direction, precedence, contacts và tọa độ mm. Style và bố trí được áp dụng trước solve; trace/SVG không biến đổi hình học sau chấm.

## 2. Bộ giải và đối chứng

TV4 DP theo Docs 31: thân trái sang phải, dấu sau thân và trước deadline, endpoint/CONNECT/LIFT/boundary; hard clearance trước tối ưu J. TV2 staged top-m trên cấu hình hoàn chỉnh theo H_ref và H_geom đăng ký trước, inner solve exact cùng bài toán; beam cùng feasibility/cost và budget khai báo. Tính toàn enumerate/rank/solve, không bỏ chi phí q^n. Incomplete enumeration chỉ là explored subset.

## 3. Kiểm chứng độc lập

TV3 oracle vét cạn và primitive hình học/cost độc lập. Kiểm giới hạn ca nhỏ, seed random cố định, glyph tham số hóa và ca thật dấu chồng, vô nghiệm/đồng hạng/biên clearance. So feasibility và optimum trong tolerance, không ép lịch đồng hạng giống nhau. Bộ preflight cũ dùng primitive chung chỉ là thăm dò.

## 4. Phân tích có lợi/bằng nhau và độ nhạy

Nghiên cứu điều kiện đủ tách được, bao gồm baseline chọn g tối thiểu hóa A(g); họ ví dụ tối thiểu hiện thực hóa trên glyph tham số hóa. Quét hai tham số rho/lambda và báo quyết định ổn định, w/b/state/time/memory. Với tập lịch khả thi hữu hạn cố định và lịch đánh giá cố định, regret lồi; cực đại miền chữ nhật bằng cực đại bốn đỉnh. Chứng nhận giới hạn trong tập đã khóa, không phải mọi font/lịch liên tục; heuristic không thay optimum.

## 5. Holdout và thống kê

Split mới do TV1 custody; old20 bổ sung. Cuối tháng 3 khóa code/candidates/ranking/tie/budget/point/theta box/c_min/epsilon trước mở tháng 4, ghi access log. Từ là đơn vị độc lập; nhiều seed/font không tự tăng cỡ mẫu từ. Gap_m chỉ trên ca đủ exact coverage; báo riêng infeasible/incomplete và ba kết cục. Epsilon chưa có giá trị được duyệt; không chọn sau kết quả hoặc suy tương đương từ p>0.05.

## 6. Font và vật lý có điều kiện

TV1–TV4 font có base glyph và license phù hợp, anchors/default reference khóa, so gốc/chỉnh tay và kiểm độc lập. TV3 máy vẽ phẳng hai trục khi sẵn sàng, thông số và nguồn đo theo run. Không dùng tốc độ mô phỏng làm đo thật. Gói tái lập và báo cáo là bắt buộc; nguồn hạn chế giấy phép được tách quyền truy cập.
