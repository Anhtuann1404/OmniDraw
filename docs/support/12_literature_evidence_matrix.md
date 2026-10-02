> **SUPPORTING_REFERENCE.** Nguồn quyết định: [kế hoạch](../30_research_development_plan.md), [contract solver](../31_joint_solver_contract.md), [API](../32_research_api_and_artifact_contract.md). Nội dung trùng hoặc khác phải đề xuất sửa nguồn chính; không tự ghi đè đặc tả.

<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** Tài liệu hỗ trợ được chuyển phạm vi. Phần hiện hành là kế hoạch/contract được dẫn dưới đây; các ID RQ, mốc thời gian và giả thuyết khác trong phần nội dung trước cập nhật chỉ áp dụng cho giai đoạn cũ.
> Kế hoạch hiện hành: [Docs 30](../30_research_development_plan.md); đặc tả [Docs 31](../31_joint_solver_contract.md) và [Docs 32](../32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

## Ma trận cần hoàn tất cho lõi mới

| Nguồn | Vai trò | Trạng thái nội dung | Việc cần làm |
|---|---|---|---|
| Balas (1999), *New classes of efficiently solvable generalized traveling salesman problems*, [DOI 10.1023/A:1018939709890](https://link.springer.com/article/10.1023/A:1018939709890) | Restricted-order/generalized DP; choice semantics chờ toàn văn | Metadata có nguồn; đối chiếu toàn văn PENDING | Ghi trang, đúng giả thiết và giới hạn riêng từng thành phố |
| Balas & Simonetti (2001), *Linear time dynamic-programming algorithms for new classes of restricted TSPs: a computational study*, [DOI 10.1287/ijoc.13.1.56.9748](https://pubsonline.informs.org/doi/10.1287/ijoc.13.1.56.9748) | Restricted-order DP | Đối chiếu toàn văn PENDING | Bảng trang và cận trạng thái; không tự gán novelty |
| Chakraborty et al. (2010), STACS, pp. 167–178, [DOI 10.4230/LIPIcs.STACS.2010.2452](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.STACS.2010.2452) | Parametric shortest paths, một tham số | Hướng liên quan; không thay chứng minh regret | Phân biệt phạm vi một/two parameters |

## Đối chiếu gần lõi bổ sung — 02/10/2026

| Nguồn / phần đã kiểm | Lựa chọn cấu hình | Tương tác lựa chọn | Thứ tự | Thuật toán / chi phí | Giới hạn kết luận |
|---|---|---|---|---|---|
| [RoboTSP, preprint v2 (2017)](https://arxiv.org/html/1709.09343v2), §I–III | Nhiều IK configurations mỗi target | Chi phí chuyển giữa configurations; collision-free planning bước sau | Chọn tour task-space trước | Near-optimal TSP, rồi shortest path chọn configs cho tour cố định, rồi motion planning | Không gọi là bộ giải đồng tối ưu exact; endpoint phụ thuộc lựa chọn không mới riêng lẻ |
| [Khachai et al., PCGTSP (2023)](https://doi.org/10.1016/j.ejor.2023.01.039), metadata/abstract | Một vertex mỗi cluster | Chưa kiểm toàn văn về conflict/clearance | Partial order giữa clusters | Formulations, polyhedral study và branch-and-cut; min-cost tour | Không khẳng định bài thiếu ràng buộc cặp khi chưa đọc toàn văn |
| [RoboCoDraw](https://arxiv.org/abs/1912.05099), abstract | Chi tiết chưa kiểm | Chi tiết chưa kiểm | Path optimization | GAN + random-key genetic algorithm | Bối cảnh robot vẽ; không suy ra tính mới glyph scheduling từ abstract |
| Balas 1999 / Balas–Simonetti 2001, nguồn trên | Cần đối chiếu định nghĩa toàn văn | PENDING | Restricted-order DP | Cần bảng trang, biến thể k(i), state/cận | Không suy ra choose-one-cluster chỉ từ chữ generalized trong tên |
| STACS 2010, nguồn trên | Shortest path tham số | Không dùng làm bằng chứng mô hình glyph | Không cùng contract | Một tham số trọng số | Hướng liên quan; không nguồn trực tiếp chứng nhận bốn đỉnh hai tham số |
| [Eppstein & Kurz (2017)](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2017.16), abstract | K-best solutions | Có điều kiện bounded treewidth/MSO/weighted model | Tùy mô hình | K-best có giả thiết cấu trúc | Không suy ra top-m của nhóm đa thức theo n,q,m nếu frontier không chặn |
| Mô hình nhóm, Docs 31/35 | Candidate trọn chữ + hình học dấu | Cặp clearance qua graph bảo thủ | Thân có thứ tự, dấu có owner/deadline | DP dự kiến; J affine hai tham số, CONNECT/LIFT | Khác biệt mô hình là giả thuyết cần mapping so tiền lệ; novelty chưa được xác lập |

Chi tiết đặc tả đã nhập vào [Docs 31](../31_joint_solver_contract.md); Docs 35 trong lịch sử là hồ sơ diễn tiến. TV2 tiếp tục đọc toàn văn, ghi trang/đoạn, đặc biệt PCGTSP và Balas; không biến UNKNOWN thành “không có”.

Ma trận cũ bên dưới giữ lịch sử tra cứu. Mỗi kết luận dùng trong bản thảo mới cần evidence span/page đã đọc; metadata hoặc tóm tắt không đủ xác nhận giới hạn thuật toán.

Bản seed trước được giữ tại [lịch sử](../history/checkpoints/12_literature_matrix_seed.md); không dùng nhãn VERIFIED_SEED thay toàn văn hoặc kết luận tính mới.
