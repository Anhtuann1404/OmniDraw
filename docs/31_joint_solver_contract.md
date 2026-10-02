# Contract mô hình đồng tối ưu chữ/dấu và lịch nét

**Version:** `joint-contract-v1-draft` — 02/10/2026. **Owner:** TV4; TV2 cost/baseline; TV3 oracle; TV1 dữ liệu. Hướng đã được GVHD đồng ý theo TV4, chi tiết contract cần review trước triển khai. Không thay hồi tố contract E4 `4677aad`.

## 1. Cùng bài toán cho mọi phương pháp

Đơn vị ban đầu là một từ/cụm ngắn với bố trí cố định; ranh giới từ, dòng và hành trình đầu/cuối được khai báo. Không tự tối ưu vị trí toàn trang hay thêm glyph liên tục. Input gồm text đã chuẩn hóa, glyph nét đơn, tập ứng viên world-mm hữu hạn và quy tắc khả thi. Mỗi chữ chọn đúng một ứng viên bao gồm thân và hình học mọi dấu của nó. ID nét ổn định, sở hữu dấu rõ ràng, các ngoại lệ tiếp xúc được gắn cặp ID và vị trí; không miễn toàn bộ dấu–thân khỏi kiểm tra.

Style/slant/scale và biến đổi bố trí phải áp dụng trước tạo tập ứng viên được chấm. Không biến đổi ngẫu nhiên hình học sau solve. SVG và trace phải biểu diễn cùng tập hình học/chuyển tiếp đã chấm, trong sai số chuyển đổi đã đăng ký.

## 2. Lịch khả thi

1. Thân chữ được hoàn tất trái sang phải. Thứ tự nét trong thân theo khai báo ứng viên; trạng thái phải biết pha của thân nhiều nét. Không bắt đầu thân tiếp theo trước khi hoàn tất thân hiện tại.
2. Dấu chỉ vẽ sau khi thân sở hữu hoàn tất; mọi nét được thực hiện đúng một lần. Quan hệ thứ tự giữa dấu cấu tạo/dấu thanh, nếu có, được khai báo, không suy ra thói quen người viết từ ảnh quét.
3. Với dấu j của chữ i (chỉ số chữ bắt đầu 0), k(j) là số nguyên không âm tính theo số thân kế tiếp được hoàn tất. Phải vẽ dấu trước khi bắt đầu thân i+k(j)+1, hoặc trước kết thúc từ nếu deadline vượt từ. k=0: sau thân i, trước thân i+1. Trước bắt đầu một thân, flush mọi dấu sẽ quá hạn. Không dùng số hành động hoặc khoảng cách mm thay đơn vị cửa sổ.
4. Dấu hợp lệ có thể xen giữa các hành động thân theo precedence/deadline; thân sở hữu luôn phải hoàn tất trước. Bộ giải và oracle dùng cùng quy tắc này, không tự mở quyền hoán vị thân.
5. Chỉ đảo chiều nét gắn `reversible=true`; reverse đổi đầu/cuối và hướng traversal, không thay hình học đường cong. Chiều gốc/đảo đều nằm trong tập hữu hạn. ID nét giữ nguyên, hướng là trường riêng.
6. `CONNECT`: giữ bút hạ tại hai đầu trùng nhau trong dung sai contact đã khóa, tiếp xúc phải được cho phép. Không thêm bridge không có trong ứng viên. Bridge nếu nghiên cứu phải là nét/ứng viên khai báo trước và được kiểm tra đầy đủ.
7. `LIFT`: nâng, di chuyển tới đầu nét kế tiếp, hạ và vẽ. Dù hai điểm trùng, LIFT vẫn có chu kỳ nâng/hạ. CONNECT và LIFT là lựa chọn khác khi cả hai khả thi.
8. Bắt đầu tại p0 với bút nâng; kết thúc p_end với bút nâng. Tính hành trình p0→nét đầu và nét cuối→p_end cho mọi phương pháp. N_cycle bằng số đoạn vẽ liên tục tối đa giữa các lần bút nâng; mỗi đoạn có một lần hạ và một lần nâng, kể cả đầu/cuối. Ca không có nét có N_cycle=0. Không dùng số nhấc ở API cũ thay cho định nghĩa này mà không adapter.

## 3. Hình học và ràng buộc cứng

- `c_min=0.20 mm`: floor cho cặp nét cần tách rời. Dưới floor là không khả thi, không phải phạt mềm để đánh đổi bằng chi phí thấp.
- Kiểm tra dấu–thân, dấu–dấu, thân/bridge lân cận và tương tác xa có thể xảy ra theo hình học. Self-intersection và tiếp xúc được phép phải có quy tắc riêng, không dùng clearance giữa mọi nét làm floor vô điều kiện.
- Tập cặp tương tác được dựng bảo thủ qua toàn bộ ứng viên; kiểm tra liên quan khi lựa chọn đã xác định. Không bỏ chữ ra khỏi frontier nếu còn cặp chưa đóng. Kiểm tra cuối dùng cho đối chiếu, không dùng để cứu DP đã gộp thiếu thông tin.
- Khóa cách flatten đường cong, sai số xấp xỉ, dung sai contact/cost và phép xử lý degenerate/collinear. Khoảng hở đo trên polyline có sai số xấp xỉ phải được công bố; tolerance không được âm thầm hạ c_min.
- TV3 kiểm độc lập primitive; chỉ chia sẻ schema/hình học thô, không dùng checker/cache feasibility của DP.

**Quy ước hình học draft:** clearance là khoảng cách nhỏ nhất giữa các đường tâm polyline của hai nét được khai báo phải tách. Đây chưa là khoảng hở vùng mực: bề rộng ngòi, sai số cơ khí và vùng mực cần protocol vật lý riêng. Tiếp xúc được phép tại endpoint không miễn đoạn còn lại của cặp khỏi kiểm tra; vùng ngoại lệ phải có phạm vi hữu hạn khai báo. Với glyph không có dấu/không có cặp phải tách, minimum clearance là null (not applicable), không Infinity hoặc 0. Các đường UP trong mô hình là đoạn thẳng Euclid giữa endpoint; mô hình không chứa tránh vật cản. Nếu thiết bị cần đường tránh, phải đổi contract khả thi/cost và chứng minh tương ứng trước freeze.

## 4. Hàm mục tiêu và đơn vị

`T_hat=L_down/v_down+L_up/v_up+tau*N_cycle` (s).

`J=v_down*T_hat=L_down+rho*L_up+lambda*N_cycle` (mm), `rho=v_down/v_up>0`, `lambda=v_down*tau>=0` (mm).

L_down là chiều dài nét/bridge khai báo; L_up là mọi di chuyển khi bút nâng, kể cả hành trình đầu/cuối. Mô hình chưa có gia tốc/jerk. T_hat là thời gian ước tính theo mô hình, solver_wall_time_ms là thời gian tính toán, physical_elapsed_sec là số đo máy riêng. Không thêm penalty curvature/legibility vào J rồi dùng tính affine hai tham số như chưa thay đổi bài toán. Tiêu chí thẩm mỹ chỉ sinh/lọc ứng viên hoặc xếp H_geom theo quy tắc đã khóa.

Ưu tiên đo thiết bị tháng 1–2 để chọn theta0=(rho0,lambda0). Nếu không có, chọn theo protocol DEV đăng ký trước, dải có nguồn hoặc giả định công khai. Khóa theta0, miền chữ nhật, c_min, epsilon_eq, ứng viên, tie và budgets cuối tháng 3 trước mở Holdout.

## 5. Trạng thái, truy hồi và cận

State tối thiểu `(i, phase, frontier_assignments, pending_mask, pen_endpoint)`:

- i/phase: thân tiếp theo/pha nét trong thân hiện tại.
- frontier_assignments: lựa chọn ứng viên của các chữ còn tương tác chưa đóng, hợp với chữ sở hữu nét đang chờ.
- pending_mask: nét dấu còn chờ với owner, ID, deadline, predecessors; map mask chỉ trong cửa sổ đã định, không mất sở hữu khi đánh lại chỉ số.
- pen_endpoint: ID nét cuối, owner, candidate ID và chiều traversal hoặc endpoint tọa độ có khóa tương đương chính xác. Khi owner đã rời frontier, endpoint vẫn phải mang đủ thông tin. Không làm tròn tọa độ để gộp state nếu chưa chứng minh không đổi khả thi/chi phí.

Với tập hành động hợp lệ A(s), successor F(s,a), chi phí c(s,a;theta):

`D(s')=min_{s,a:F(s,a)=s'} [D(s)+c(s,a;theta)]`.

Khởi tạo endpoint=p0, pending rỗng, chi phí 0; mỗi nét/chuyển tiếp góp L_down/L_up/N_cycle đúng một lần. Terminal: mọi thân/dấu hoàn tất, cộng nâng cuối và đi p_end theo quy ước; backpointer tái dựng lịch. Số nét đã vẽ tăng mỗi hành động nên search graph hữu hạn và acyclic trong mô hình này.

Hai path chỉ gộp khi có cùng tập continuation khả thi và cùng hàm chi phí tương lai: cùng geometry còn tương tác, pending/deadline/precedence, phase và pen endpoint. Khi đó giữ J nhỏ nhất tại theta cố định là hợp lệ. Đây là DP một mục tiêu; không tuyên bố Pareto dominance/pruning mới.

Ký hiệu n chữ; q ứng viên trọn chữ tối đa; r nét dấu/chữ tối đa; s nét thân/chữ tối đa; k=max k(j); w số chữ giữ ở frontier tương tác; b_max<=r(k+1) là số slot nét dấu có thể chờ, khác số nét đang chờ b_observed. f là số chữ trong hợp frontier và owners pending, f<=w+k+1.

Với M<=n(s+r) nét, cận bảo thủ số endpoint `P<=2qM+1` gồm p0 và hai đầu của từng nét/ứng viên; P không là hằng số độc lập. Cận số state thô `O(n(s+1) q^f 2^b_max P)` khi stencil mask và phase được xác định như trên. Mỗi state tối đa `O(2(b_max+1))` lựa chọn nét/chiều nhân số lựa chọn ứng viên mới và CONNECT/LIFT; chi phí kiểm tra hình học phải tính riêng theo số đoạn/cặp. Đây là cận dự kiến cần đối chiếu implementation, không chứng minh thời gian thực nghiệm luôn nhỏ. Báo peak_states, transitions, w, f, b, P và bộ nhớ; giữ endpoint khỏi frontier được tính trong P, không đếm q^b như mỗi dấu thuộc chữ độc lập.

## 6. Đối chứng phân tầng top-m và beam

G là toàn cấu hình hoàn chỉnh, |G|<=q^n; không phải top-m ứng viên riêng của từng chữ. Khóa candidate IDs và thứ tự Cartesian enumeration. Tính H rồi xếp `(H,configuration_id)`; H_ref cố định thứ hạng tại theta0 trong sweep chính.

- H_ref: thân trái→phải, dấu ngay sau thân, thứ tự nội bộ/ID cố định, chiều chuẩn khai báo, LIFT giữa nét, p0/p_end và N_cycle chung. Lịch tham chiếu invalid: H=+infinity trong xếp hạng nội bộ và tie theo ID; vẫn giữ g vì có thể có lịch khác khả thi. JSON không dùng Infinity.
- H_geom: glyph nét đơn mặc định và neo mặc định của font/bộ glyph làm reference. Nếu thiếu neo, quy ước trên DEV khóa trước. 32 mẫu theo độ dài cung mỗi nét tương ứng, MSE điểm rồi mean theo nét; chuẩn hóa cùng size, giữ vị trí dấu tương đối. Thiếu correspondence xếp cuối theo ID, báo coverage. Không dùng optimal schedule/Holdout để chọn reference.
- `F(g;theta)=min_{s feasible for g} J(g,s;theta)`; `J_m=min_{g in prefix_m}F(g)`, `J_joint=min_{g in G}F(g)`. Ca prefix vô nghiệm trả NO_FEASIBLE_IN_PREFIX, không kết luận toàn G vô nghiệm.
- Prefix lồng nhau, inner solve exact: J_joint<=J_(m+1)<=J_m; m=|G| khớp joint trong dung sai. Kiểm cả complete flag trước áp dụng mệnh đề.
- Duyệt streaming + heap max-m giảm bộ nhớ, không tránh phải duyệt toàn G nếu chưa có bound/ranking certificate. Budget configurations/time/memory đăng ký trên DEV; tính cả enumerate/score/rank/solve. Hết budget: `ranking_complete=false`, kết quả chỉ thăm dò tập con, không top-m toàn cục và không chứng nhận bằng nhau.
- Beam dùng cùng G/khả thi/cost, width/tie/budget khóa trước. Nếu beam bằng exact, báo exact đã chứng nhận chất lượng trong phạm vi; không ép exact phải thắng chất lượng. Nghiệm beam chỉ là upper bound cho minimization, không lower bound.

## 7. Oracle, đồng hạng và kiểm thử

Oracle TV3 viết từ đặc tả, độc lập DP và primitive. Ca nhỏ ban đầu n<=3, q<=2, k<=1, tối đa 6 hành động thân/dấu; budget cụ thể tháng 1. Random cases seed cố định cùng ca thật có dấu chồng, marks below, distant interaction, reversed endpoints, CONNECT/LIFT, deadline k=0/1, empty, degenerate, equal-cost và infeasible. Boundary 0.19/0.20/0.21 mm có phép tính tay.

So khả thi và optimal value trong dung sai số học; kiểm riêng validity/cost của mỗi output. Chỉ so equality của action sequence khi cùng tie policy (ví dụ lexicographic candidate IDs, stroke IDs, direction, transition). Không gọi hai lịch đồng hạng khác nhau là mismatch. Không dùng kiểm trên ca nhỏ làm chứng nhận vét cạn được mọi Holdout.

## 8. Regret và kết luận

Với Pi hữu hạn cố định, khả thi không phụ thuộc theta, mỗi J affine và pi cố định thuộc Pi:

`R_pi(theta)=J_pi(theta)-min_sigma J_sigma(theta)=max_sigma[J_pi(theta)-J_sigma(theta)]` lồi. Theta trong hình chữ nhật là tổ hợp lồi bốn đỉnh, nên maximum R_pi bằng maximum tại bốn đỉnh. Không suy ra minimax schedule thuộc bốn vertex winners. Exact optima cho exact modeled certificate; valid lower bounds cho conservative upper bound. Cả certificate và float tolerance phải khai báo phạm vi/sai số; heuristic không thay optimum.

Gap_m=(J_m-J_joint)/J_m chỉ khi cả hai optimal feasible và J_m>0. J_m=0, timeout, incomplete, infeasible tách riêng. epsilon_eq có căn cứ và duyệt trước freeze, chưa có giá trị mặc định. Kết luận hữu ích vượt biên / tương đương thực dụng trong tập đã khóa với đủ coverage / chưa đủ bằng chứng. Không dùng p>0.05 để kết luận tương đương hoặc extrapolate toàn tiếng Việt.
