> **HISTORICAL_RECORD — không là đặc tả hiện hành.** Đọc [hướng hiện tại](../../README.md), [contract](../../31_joint_solver_contract.md) và [công việc](../../03_current-task.md). Giữ kết luận đúng phạm vi/commit gốc.

# Bổ sung đặc tả sau phản biện mô hình và hướng sửa của nhóm

**Ngày:** 02/10/2026. **Owner:** TV4; review TV2; fixtures TV1; oracle độc lập TV3. **Trạng thái:** DRAFT_REVIEW_REQUIRED. Áp dụng cùng [Docs 31](../../31_joint_solver_contract.md), không thay sign-off cũ hoặc tuyên bố đã nghiệm thu bộ giải mới.

Nguồn: các điểm phản biện và văn bản hướng sửa do TV4 cung cấp trong cuộc trao đổi. Đây là quyết định/đề xuất của nhóm, không tự gán cho GVHD. Đề cương [Docs 29](../../29_research_proposal_consolidated.md) giữ vai trò bản đối chiếu Google Docs; các nội dung cốt lõi đã được chỉnh trực tiếp trên Google Docs và đồng bộ Docs 29 trong lượt tiếp theo cùng ngày. Chi tiết kỹ thuật và gate trong file này vẫn chờ owner review.

## 1. Những điểm tiếp nhận và điều kiện đi kèm

| Điểm | Hướng xử lý |
|---|---|
| RTSP/GTSP gần lõi | Bổ sung đối chiếu có trạng thái đọc; không coi lựa chọn cấu hình hoặc endpoint phụ thuộc lựa chọn là mới riêng lẻ |
| DP mẫu và quên thông tin | Giữ pha thân nhiều nét, deadline từng dấu; endpoint vẫn tự mang candidate sau khi geometry map quên owner |
| Top-m không nhất thiết enumerate hết | K-best có điều kiện; chứng nhận prefix khác enumerate toàn G; không hứa đa thức theo n,q,m |
| Lambda có thể thoái hóa | Đo multi-N khả thi, multi-N không bị trội và switching riêng; không tạo bridge ngầm để làm đẹp kết quả |
| Chất lượng ứng viên | Gate chung trước solve, ngưỡng DEV chưa khóa; báo độ lệch và coverage |
| Chứng nhận bốn đỉnh | Cố định một phương án hoàn chỉnh; đối thủ được thay cả geometry trong cùng Pi |

Pareto/cắt tỉa nâng cao vẫn ngoài cam kết kỳ này. Phần dưới không mở lại chúng.

## 2. Trạng thái và chuyển tiếp đề xuất cho DP một mục tiêu

### 2.1 Ngữ nghĩa trạng thái

`s=(i,t,A,P,e)`: i là chữ có thân đang vẽ hoặc chữ tiếp theo nếu t=0; t là số nét thân của i đã thực hiện. t=0 nghĩa chưa chọn/bắt đầu thân i. Sau nét thân cuối, tăng i và đặt t=0. A lưu candidate của chữ đang vẽ, owners dấu còn chờ và chữ còn tương tác tương lai. P lưu ID dấu chưa vẽ, owner, deadline và precedence. Với owner có dấu, lưu đủ tập dấu của candidate để xác định dấu nào đã hoàn tất từ P; không chỉ lưu số dấu. e là endpoint descriptor `(owner,candidate,stroke,direction)` hoặc p0.

w đếm frontier tương tác **bao gồm chữ đang vẽ**; hợp A với owners pending có f≤w+k+1 theo contract. e độc lập A và có thể tham chiếu một owner đã quên khỏi A; P_endpoint≤2qM+1 vẫn phải nhân trong cận state. Không được vừa bỏ thông tin candidate trong e vừa giữ cận này. Tên P ở đây là tập pending; P_endpoint là số descriptor, tránh nhầm hai đại lượng.

Chỉ thêm dấu của i vào P sau khi thân i hoàn tất; trước đó candidate của i nằm trong A. Dấu của chữ trước có thể xen giữa hai nét thân i. Quan hệ giữa dấu đã vẽ/đang chờ được suy ra từ candidate còn giữ và mask, không mất khi dịch cửa sổ.

### 2.2 Ba chuyển tiếp

**BODY:** nếu t=0, kiểm trước khi bắt đầu thân i rằng không có dấu pending phải hoàn tất trước i (owner j có deadline j+k(mark)+1≤i). Chọn một candidate của i, kiểm mọi cặp với geometry đã chọn mà cần tách, từ chối dưới c_min; giữ lựa chọn trong A. Chọn chiều được phép của nét thân đầu và CONNECT/LIFT hợp lệ, rồi vẽ. Nếu t>0, vẽ nét thân kế tiếp theo body_order trong candidate đã chọn. Hoàn tất thân thì phát sinh pending dấu, tăng i, đặt t=0. Việc chọn geometry và vẽ thân đầu là một bước để tránh chu trình chọn zero-cost.

**MARK:** chọn một dấu trong P có thân sở hữu hoàn tất và predecessors đã vẽ; vẽ theo chiều/transition hợp lệ, xóa dấu khỏi P. Không mặc định MARK luôn LIFT: áp dụng cùng quy tắc contact như BODY. Nếu chính sách thực nghiệm chỉ cho LIFT ở dấu, phải đăng ký nó thành hạn chế chung cho mọi phương pháp.

**END:** chỉ khi i=n, t=0, P rỗng. Đưa bút về p_end ở trạng thái UP. Không cộng thêm lambda cho nâng cuối vì chu kỳ đã tính khi bắt đầu đoạn vẽ liên tục.

Với một action vẽ nét a dài l(a), bắt đầu tại u(a):

- LIFT: `deltaJ=l(a)+rho*distance(e,u(a))+lambda`.
- CONNECT: `deltaJ=l(a)`; chỉ khi có nét trước, endpoint trùng trong dung sai và contact được phép. Không tự thêm đoạn nối.
- END: `deltaJ=rho*distance(e,p_end)`.

Khởi đầu e=p0, action đầu phải LIFT. Ca rỗng chỉ END, có chi phí UP nếu p0≠p_end và N_cycle=0. Backpointer ghi candidate, ID, chiều và transition; mỗi action BODY/MARK tăng số nét đã vẽ nên graph acyclic. Với hai path cùng state và cùng continuation, giữ J nhỏ hơn tại theta cố định. Tiền xử lý tương tác hình học xa phải hoàn tất trước gộp state.

### 2.3 Ví dụ logic, không phải số liệu thực nghiệm

Chữ 0 có thân hai nét và dấu m0, k(m0)=1; chữ 1 có thân một nét. Sau thân 0: `(i=1,t=0,P={m0})`. Có thể vẽ m0 ngay hoặc bắt đầu thân 1. Nếu vẽ thân 1 trước, i thành 2; m0 bắt buộc hoàn tất trước bắt đầu thân 2. Với k(m0)=0, không được bắt đầu thân 1. Nếu chữ 1 nhiều nét, m0 có thể xen giữa các nét thân 1; dấu riêng của chữ 1 chưa được vẽ trước hoàn tất thân 1.

### 2.4 Điều kiện quên

Xóa assignment của j khỏi A chỉ khi thân j hoàn tất, không còn nét pending của j và không còn cạnh tương tác với chữ chưa chọn. Các cặp đã đóng phải được kiểm trước. Nếu e còn tham chiếu j, **giữ candidate/endpoint trong e độc lập**, không tra lại A. Hoặc giữ j trong A đến khi e đổi; phương án này phải cập nhật f/cận riêng, không dùng lẫn hai biểu diễn.

Cơ sở: khi không còn pending/tương tác tương lai, geometry j không ảnh hưởng continuation; chi phí chuyển động còn phụ thuộc j chỉ qua e đã giữ. Cần chứng minh theo graph tương tác bảo thủ thực tế và đối chiếu khi mã hóa. Gate TV4: DP không quên và DP quên phải khớp feasibility/value trên ca nhỏ. Mismatch có thể do graph thiếu cạnh, state, deadline, cost hoặc code; phép kiểm này **không thay oracle TV3 độc lập**.

## 3. Top-m: xếp hạng chính xác và giới hạn tài nguyên

Baseline hiện hành xếp toàn G, kể cả cấu hình có lịch tham chiếu invalid với H_ref=+infinity. Không lọc vô nghiệm trước ranking rồi gọi đó là cùng prefix: muốn dùng G khả thi phải đổi phiên bản baseline, định nghĩa và so sánh riêng.

K-best trên DAG chỉ dùng sau khi chứng minh: (1) mỗi đường biểu diễn duy nhất một cấu hình; (2) H bằng tổng trọng số đúng, kể cả boundary; (3) tie `(H,configuration_id)` nhất quán; (4) xử lý validity giữ đúng thứ hạng toàn G. Không dùng các lịch khác của cùng geometry như nhiều cấu hình. H_geom có mẫu/correspondence và mẫu số mean; nếu số nét khác nhau theo candidate, chưa mặc định là additive. H_ref cần chứng minh decomposition của lịch tham chiếu và giữ quy tắc invalid, kể cả tương tác không kề.

Nếu cần nhớ lựa chọn xa để tính H/validity, mở rộng frontier của DAG. K-best có thể giảm liệt kê, nhưng độ phức tạp phụ thuộc V/E của DAG đã dựng; V có thể tăng theo q^w. Không cam kết đa thức theo n,q,m. Duyệt theo thứ hạng toàn cục rồi lọc cũng chỉ sinh top-m của tập đã lọc, không giữ baseline G gốc.

- `enumeration_complete`: đã duyệt hết G.
- `ranking_complete`: chứng minh đúng prefix min(m,|G|) theo ranker/tie đã khóa, có thể true khi enumeration_complete=false.
- `search_complete`: inner solver exact trong scope đã khai báo.

Gateway chỉ kiểm các khai báo/scope, không tự chứng minh ranking; adapter phải xuất bằng chứng tái lập vào artifact offline. Có prefix đúng và inner exact mới báo OPTIMAL/NO_FEASIBLE_IN_PREFIX. Hết budget trước chứng nhận: explored_subset/thăm dò, không dùng để khẳng định gap toàn G.

| Tầng | Scope dự kiến | Quy tắc |
|---|---|---|
| A — oracle | n≤3,q≤2,k≤1, ≤6 action nét | Seed cố định, vô nghiệm/đồng hạng/tương tác xa; mọi ca nằm trong budget khóa mới chấm exact |
| B — DP/top-m chính xác | Giới hạn n,q,k,số nét,w và m chốt từ DEV | Đo riêng ranking/inner solve, peak_states, RAM, completion; không tự chọn giới hạn sau Holdout |
| C — mở rộng | Ca ngoài B, DP/beam theo budget | Báo completion và bounds; không timeout→exact |

Cuối tháng 1 chốt bảng giới hạn định lượng, budgets và tỷ lệ hoàn tất tối thiểu. Giới hạn HTTP 30s/200k states/100k configurations/512MB là giới hạn gateway, **không** phải ngưỡng nghiệm thu nghiên cứu. Nếu tầng B không đạt trên DEV, thu hẹp scope trước freeze; không loại ca khó sau nhìn kết quả Holdout.

## 4. Kiểm tra vai trò lambda

Multi-N khả thi chưa đủ: CONNECT và LIFT ở cùng endpoint có thể cho cùng độ dài, khi lambda>0 CONNECT trội LIFT. Vì vậy ghi riêng: số ca có ≥2 giá trị N_cycle khả thi; có ≥2 giá trị N_cycle trong tập phương án không bị trội theo (L_down,L_up,N_cycle); và tỷ lệ đổi phương án tối ưu khi quét lambda tại rho cố định. Tìm chưa đầy đủ: UNKNOWN, không kết luận chỉ có một N_cycle.

Hai phương án hoàn chỉnh A/B có điểm bằng nhau tại `lambda*=(L_down_B-L_down_A+rho*(L_up_B-L_up_A))/(N_A-N_B)` nếu N_A≠N_B. Chỉ gọi switching tối ưu nếu nằm trong miền và không có phương án thứ ba tốt hơn. Ví dụ nối 5mm so UP 4mm ở rho=.5 cho ngưỡng 3mm chỉ hợp lệ nếu phần nối đã khai báo trong tập ứng viên, mọi chi phí còn lại bằng nhau và geometry/contact khả thi; đây là minh họa đại số, không kết quả glyph thật. API hiện không thêm bridge ngầm.

TV2 đăng ký trên DEV cách quét, quy tắc phá hòa, coverage và cutoff để hạ trọng tâm về rho nếu lambda ít ảnh hưởng; TV4 cung cấp trace. Nếu mọi lịch có cùng N_cycle, ghi thẳng phân tích lambda thoái hóa. Không sửa tập ứng viên trên Holdout để tạo switching.

## 5. Gate chất lượng chữ

TV1/TV4 lập reference glyph/anchor, correspondence, x-height/size convention và giấy phép. Trước solve, chốt trên DEV giới hạn dịch dấu chuẩn hóa theo x-height, slant/scale/độ lệch thân, topology và H_geom. Các giá trị hiện **PENDING**, không lấy ví dụ làm ngưỡng mặc định. Gate chung cho mọi phương pháp, giữ manifest/hash số candidate trước/sau lọc và lý do loại.

Báo H_geom/độ dịch dấu của phương án được chọn và clearance kiểm độc lập. Đánh giá đọc thử nhỏ có thể dùng hai người chấm, ẩn nhãn phương pháp, rubric dấu/thân/đọc được và bất đồng; chốt sample/rubric trước đánh giá. Đây là kiểm chất lượng ứng viên, không nghiên cứu thói quen viết hoặc bảo đảm đẹp mọi font. Nếu chưa làm, kết luận giới hạn trong tập hình học hợp lệ đã khóa.

## 6. Văn bản đề xuất bổ sung vào đề cương

Đề tài so sánh đồng tối ưu với phân tầng top-m trong cùng tập ứng viên hình học đã kiểm tra và khóa. Prefix được chứng nhận theo quy tắc xếp hạng đăng ký trước; có thể sinh bằng k-best khi phân rã chi phí và tính đúng thứ hạng được chứng minh, hoặc dùng duyệt hữu hạn trong ngân sách. Các ca chưa hoàn tất được báo riêng. Lịch khả thi tuân thủ thứ tự thân chữ, deadline từng dấu, quyền đảo chiều và CONNECT/LIFT đã khai báo, với trạng thái giữ tiến độ thân nhiều nét, dấu chờ, tương tác hình học và endpoint phụ thuộc ứng viên.

Phân tích độ nhạy kiểm tra trước liệu N_cycle có thay đổi và lambda có thực sự làm đổi phương án tối ưu. Chứng nhận regret áp dụng cho một phương án hoàn chỉnh cố định gồm hình học, thứ tự, hướng nét và quyết định nối/nhấc, so với toàn tập phương án khả thi đã khóa. Đóng góp dự kiến là mô hình chữ/dấu tiếng Việt và phân tích có kiểm soát; chưa khẳng định mới dựa riêng vào DP, lựa chọn cấu hình hoặc tính lồi chuẩn.

## 7. Gate bàn giao

TV4: state/action, safe-forget/no-forget, trace và adapter. TV2: ranker decomposition/k-best proof, lambda protocol và bảng toàn văn Balas/RTSP/PCGTSP có trang. TV1: bounds/reference ứng viên, fixtures dấu chồng và split/custody. TV3: oracle/primitive độc lập theo cùng contract, không sửa code solver TV4. Những nhiệm vụ mới là đề xuất phân công cần owner xác nhận, không được coi đã hoàn thành.
