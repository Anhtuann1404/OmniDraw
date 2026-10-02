# Thiết kế trạng thái đồng tối ưu

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API nghiên cứu](32_research_api_and_artifact_contract.md) là nguồn triển khai.

## Trạng thái cần mã hóa

`(body_index, body_phase, frontier_assignments, pending_mask, pen_endpoint)` theo Docs 31 §5. Body phase giữ tiến độ thân nhiều nét; pending mask giữ nét dấu còn chờ, owners/deadlines; frontier giữ các lựa chọn hình học còn ảnh hưởng tới tương tác tương lai. Endpoint gồm owner/candidate/stroke/direction khi cần, kể cả owner đã rời frontier.

Không được gộp hai state chỉ vì cùng vị trí chữ nếu pending, hình học tương tác hoặc endpoint khác. Tương tác xa/dòng lân cận cần đưa vào biên bảo thủ hoặc kiểm tra từ cấu hình cố định đầy đủ, không chỉ kiểm hai chữ kề nhau. Precompute clearance cho cặp ứng viên có thể được dùng trong solver; oracle kiểm độc lập.

## Bellman và tiến độ

`V(s') = min(V(s') , V(s)+delta_J(a))` cho action hợp lệ theo contract: chọn ứng viên đúng một lần, vẽ thân/dấu đúng một lần, hướng khai báo, CONNECT hoặc LIFT. Backpointer lưu cả action/candidate/direction và transition. Flush dấu quá hạn trước bắt đầu thân mới; cuối từ xả toàn bộ dấu rồi đi p_end với bút UP. Chuyển chọn hình học không được tạo chu trình zero-action; cần thứ tự tiến độ rõ trong implementation.

## Cận và số đo

Theo Docs 31: f≤w+k+1, b_max≤r(k+1), M≤n(s+r), P≤2qM+1. P không là hằng số; số state dự kiến `O(n(s+1)q^f 2^b_max P)` là cận bảo thủ phải đối chiếu khi mã hóa. Báo w/f/b/P thực tế, transitions, peak_states và memory; không dùng q^b nếu nhiều dấu thuộc cùng một chữ.

## Kiểm chứng và migration

TV4 triển khai DP; TV3 triển khai oracle/primitive độc lập; TV2 review cost; TV1 fixtures/ứng viên. So feasibility và giá trị optimum, chỉ so lịch khi cùng phá hòa. Test dấu chồng, deadline k=0/1, reverse, tiếp xúc cho phép, clearance biên, vô nghiệm và đồng hạng.

`CompositionState`/DAG PR3 là mã tiền nhiệm có thể tái sử dụng qua mapping và gate mới. Tách WHERE/WHEN lịch sử không được coi là mô hình hiện hành đã chứng minh tách được. Điều kiện đủ bằng nhau phải kèm phân tầng chọn g tối thiểu hóa A(g), không áp dụng cho ranking bất kỳ.
