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

### 3.1 Gate chất lượng ứng viên

TV1/TV4 lập reference glyph/anchor, correspondence, x-height/size convention và giấy phép. Trước solve, chốt trên DEV giới hạn dịch dấu chuẩn hóa theo x-height, slant/scale/độ lệch thân, topology và H_geom. Các giá trị hiện **PENDING**, không lấy ví dụ làm ngưỡng mặc định. Gate chung cho mọi phương pháp, giữ manifest/hash số candidate trước/sau lọc và lý do loại.

Báo H_geom/độ dịch dấu của phương án được chọn và clearance kiểm độc lập. Đánh giá đọc thử nhỏ có thể dùng hai người chấm, ẩn nhãn phương pháp, rubric dấu/thân/đọc được và bất đồng; chốt sample/rubric trước đánh giá. Đây là kiểm chất lượng ứng viên, không nghiên cứu thói quen viết hoặc bảo đảm đẹp mọi font. Nếu chưa làm, kết luận giới hạn trong tập hình học hợp lệ đã khóa.

## 4. Hàm mục tiêu và đơn vị

`T_hat=L_down/v_down+L_up/v_up+tau*N_cycle` (s).

`J=v_down*T_hat=L_down+rho*L_up+lambda*N_cycle` (mm), `rho=v_down/v_up>0`, `lambda=v_down*tau>=0` (mm).

L_down là chiều dài nét/bridge khai báo; L_up là mọi di chuyển khi bút nâng, kể cả hành trình đầu/cuối. Mô hình chưa có gia tốc/jerk. T_hat là thời gian ước tính theo mô hình, solver_wall_time_ms là thời gian tính toán, physical_elapsed_sec là số đo máy riêng. Không thêm penalty curvature/legibility vào J rồi dùng tính affine hai tham số như chưa thay đổi bài toán. Tiêu chí thẩm mỹ chỉ sinh/lọc ứng viên hoặc xếp H_geom theo quy tắc đã khóa.

Ưu tiên đo thiết bị tháng 1–2 để chọn theta0=(rho0,lambda0). Nếu không có, chọn theo protocol DEV đăng ký trước, dải có nguồn hoặc giả định công khai. Khóa theta0, miền chữ nhật, c_min, epsilon_eq, ứng viên, tie và budgets cuối tháng 3 trước mở Holdout.

### 4.1 Chẩn đoán vai trò lambda

Multi-N khả thi chưa đủ: CONNECT và LIFT ở cùng endpoint có thể cho cùng độ dài, khi lambda>0 CONNECT trội LIFT. Vì vậy ghi riêng: số ca có ≥2 giá trị N_cycle khả thi; có ≥2 giá trị N_cycle trong tập phương án không bị trội theo (L_down,L_up,N_cycle); và tỷ lệ đổi phương án tối ưu khi quét lambda tại rho cố định. Tìm chưa đầy đủ: UNKNOWN, không kết luận chỉ có một N_cycle.

Hai phương án hoàn chỉnh A/B có điểm bằng nhau tại `lambda*=(L_down_B-L_down_A+rho*(L_up_B-L_up_A))/(N_A-N_B)` nếu N_A≠N_B. Chỉ gọi switching tối ưu nếu nằm trong miền và không có phương án thứ ba tốt hơn. Ví dụ nối 5mm so UP 4mm ở rho=.5 cho ngưỡng 3mm chỉ hợp lệ nếu phần nối đã khai báo trong tập ứng viên, mọi chi phí còn lại bằng nhau và geometry/contact khả thi; đây là minh họa đại số, không kết quả glyph thật. API hiện không thêm bridge ngầm.

TV2 đăng ký trên DEV cách quét, quy tắc phá hòa, coverage và cutoff để hạ trọng tâm về rho nếu lambda ít ảnh hưởng; TV4 cung cấp trace. Nếu mọi lịch có cùng N_cycle, ghi thẳng phân tích lambda thoái hóa. Không sửa tập ứng viên trên Holdout để tạo switching.

## 5. Trạng thái, truy hồi và cận

Đặc tả triển khai một mục tiêu, **DRAFT_REVIEW_REQUIRED**; có bản DP DEV TV4, chưa là DP đã nghiệm thu. Bản DEV no-forget/safe-forget và policy hạn chế được mô tả trong [research README](../backend/research/README.md); không tự freeze policy vì code đã có.

### 5.1 Ngữ nghĩa trạng thái

`s=(i,t,A,P,e)`: i là chữ có thân đang vẽ hoặc chữ tiếp theo nếu t=0; t là số nét thân của i đã thực hiện. t=0 nghĩa chưa chọn/bắt đầu thân i. Sau nét thân cuối, tăng i và đặt t=0. A lưu candidate của chữ đang vẽ, owners dấu còn chờ và chữ còn tương tác tương lai. P lưu ID dấu chưa vẽ, owner, deadline và precedence. Với owner có dấu, lưu đủ tập dấu của candidate để xác định dấu nào đã hoàn tất từ P; không chỉ lưu số dấu. e là endpoint descriptor `(owner,candidate,stroke,direction)` hoặc p0.

w đếm frontier tương tác **bao gồm chữ đang vẽ**; hợp A với owners pending có f≤w+k+1 theo contract. e độc lập A và có thể tham chiếu một owner đã quên khỏi A; P_endpoint≤2qM+1 vẫn phải nhân trong cận state. Không được vừa bỏ thông tin candidate trong e vừa giữ cận này. Tên P ở đây là tập pending; P_endpoint là số descriptor, tránh nhầm hai đại lượng.

Chỉ thêm dấu của i vào P sau khi thân i hoàn tất; trước đó candidate của i nằm trong A. Dấu của chữ trước có thể xen giữa hai nét thân i. Quan hệ giữa dấu đã vẽ/đang chờ được suy ra từ candidate còn giữ và mask, không mất khi dịch cửa sổ.

Với action hợp lệ a, successor F(S,a) và cost delta_J(a), truy hồi tại theta cố định là `D(S') = min_{S,a:F(S,a)=S'} [D(S)+delta_J(a)]`. Khởi tạo state tại p0 với chi phí 0; backpointer giữ action và candidate để tái dựng phương án.

### 5.2 Ba chuyển tiếp

**BODY:** nếu t=0, kiểm trước khi bắt đầu thân i rằng không có dấu pending phải hoàn tất trước i (owner j có deadline j+k(mark)+1≤i). Chọn một candidate của i, kiểm mọi cặp với geometry đã chọn mà cần tách, từ chối dưới c_min; giữ lựa chọn trong A. Chọn chiều được phép của nét thân đầu và CONNECT/LIFT hợp lệ, rồi vẽ. Nếu t>0, vẽ nét thân kế tiếp theo body_order trong candidate đã chọn. Hoàn tất thân thì phát sinh pending dấu, tăng i, đặt t=0. Việc chọn geometry và vẽ thân đầu là một bước để tránh chu trình chọn zero-cost.

**MARK:** chọn một dấu trong P có thân sở hữu hoàn tất và predecessors đã vẽ; vẽ theo chiều/transition hợp lệ, xóa dấu khỏi P. Không mặc định MARK luôn LIFT: áp dụng cùng quy tắc contact như BODY. Nếu chính sách thực nghiệm chỉ cho LIFT ở dấu, phải đăng ký nó thành hạn chế chung cho mọi phương pháp.

**END:** chỉ khi i=n, t=0, P rỗng. Đưa bút về p_end ở trạng thái UP. Không cộng thêm lambda cho nâng cuối vì chu kỳ đã tính khi bắt đầu đoạn vẽ liên tục.

Với một action vẽ nét a dài l(a), bắt đầu tại u(a):

- LIFT: `deltaJ=l(a)+rho*distance(e,u(a))+lambda`.
- CONNECT: `deltaJ=l(a)`; chỉ khi có nét trước, endpoint trùng trong dung sai và contact được phép. Không tự thêm đoạn nối.
- END: `deltaJ=rho*distance(e,p_end)`.

Khởi đầu e=p0, action đầu phải LIFT. Ca rỗng chỉ END, có chi phí UP nếu p0≠p_end và N_cycle=0. Backpointer ghi candidate, ID, chiều và transition; mỗi action BODY/MARK tăng số nét đã vẽ nên graph acyclic. Với hai path cùng state và cùng continuation, giữ J nhỏ hơn tại theta cố định. Tiền xử lý tương tác hình học xa phải hoàn tất trước gộp state.

### 5.3 Ví dụ logic, không phải số liệu thực nghiệm

Chữ 0 có thân hai nét và dấu m0, k(m0)=1; chữ 1 có thân một nét. Sau thân 0: `(i=1,t=0,P={m0})`. Có thể vẽ m0 ngay hoặc bắt đầu thân 1. Nếu vẽ thân 1 trước, i thành 2; m0 bắt buộc hoàn tất trước bắt đầu thân 2. Với k(m0)=0, không được bắt đầu thân 1. Nếu chữ 1 nhiều nét, m0 có thể xen giữa các nét thân 1; dấu riêng của chữ 1 chưa được vẽ trước hoàn tất thân 1.

### 5.4 Điều kiện quên

Xóa assignment của j khỏi A chỉ khi thân j hoàn tất, không còn nét pending của j và không còn cạnh tương tác với chữ chưa chọn. Các cặp đã đóng phải được kiểm trước. Nếu e còn tham chiếu j, **giữ candidate/endpoint trong e độc lập**, không tra lại A. Hoặc giữ j trong A đến khi e đổi; phương án này phải cập nhật f/cận riêng, không dùng lẫn hai biểu diễn.

Cơ sở: khi không còn pending/tương tác tương lai, geometry j không ảnh hưởng continuation; chi phí chuyển động còn phụ thuộc j chỉ qua e đã giữ. Cần chứng minh theo graph tương tác bảo thủ thực tế và đối chiếu khi mã hóa. Gate TV4: DP không quên và DP quên phải khớp feasibility/value trên ca nhỏ. Mismatch có thể do graph thiếu cạnh, state, deadline, cost hoặc code; phép kiểm này **không thay oracle TV3 độc lập**.

### 5.5 Cận bảo thủ cần đối chiếu

Ký hiệu n chữ; q ứng viên trọn chữ tối đa; r nét dấu/chữ tối đa; s nét thân/chữ tối đa; k=max k(j); w số chữ giữ ở frontier tương tác, gồm chữ đang vẽ; b_max<=r(k+1) là số slot nét dấu có thể chờ, khác số nét đang chờ b_observed. f là số chữ trong hợp frontier và owners pending, f<=w+k+1.

Với M<=n(s+r) nét, cận bảo thủ số endpoint `P_endpoint<=2qM+1` gồm p0 và hai đầu của từng nét/ứng viên; P_endpoint không là hằng số độc lập. Cận số state thô `O(n(s+1) q^f 2^b_max P_endpoint)` khi stencil mask và phase được xác định như trên. Mỗi state tối đa `O(2(b_max+1))` lựa chọn nét/chiều nhân số lựa chọn ứng viên mới và CONNECT/LIFT; chi phí kiểm tra hình học phải tính riêng theo số đoạn/cặp. Đây là cận dự kiến cần đối chiếu implementation, không chứng minh thời gian thực nghiệm luôn nhỏ. Báo peak_states, transitions, w, f, b, P_endpoint và bộ nhớ; giữ endpoint khỏi frontier được tính trong P_endpoint, không đếm q^b như mỗi dấu thuộc chữ độc lập.

## 6. Đối chứng phân tầng top-m và beam

G là toàn cấu hình hoàn chỉnh, |G|<=q^n; không phải top-m ứng viên riêng của từng chữ. Khóa candidate IDs và thứ tự Cartesian enumeration. Tính H rồi xếp `(H,configuration_id)`; H_ref cố định thứ hạng tại theta0 trong sweep chính.

- H_ref: thân trái→phải, dấu ngay sau thân, thứ tự nội bộ/ID cố định, chiều chuẩn khai báo, LIFT giữa nét, p0/p_end và N_cycle chung. Lịch tham chiếu invalid: H=+infinity trong xếp hạng nội bộ và tie theo ID; vẫn giữ g vì có thể có lịch khác khả thi. JSON không dùng Infinity.
- H_geom: glyph nét đơn mặc định và neo mặc định của font/bộ glyph làm reference. Nếu thiếu neo, quy ước trên DEV khóa trước. 32 mẫu theo độ dài cung mỗi nét tương ứng, MSE điểm rồi mean theo nét; chuẩn hóa cùng size, giữ vị trí dấu tương đối. Thiếu correspondence xếp cuối theo ID, báo coverage. Không dùng optimal schedule/Holdout để chọn reference.
- `F(g;theta)=min_{s feasible for g} J(g,s;theta)`; `J_m=min_{g in prefix_m}F(g)`, `J_joint=min_{g in G}F(g)`. Ca prefix vô nghiệm trả NO_FEASIBLE_IN_PREFIX, không kết luận toàn G vô nghiệm.
- Prefix lồng nhau, inner solve exact: J_joint<=J_(m+1)<=J_m; m=|G| khớp joint trong dung sai. Kiểm cả complete flag trước áp dụng mệnh đề.
- Có thể dùng k-best trên DAG xếp hạng nếu chứng minh phân rã H, đường đi–cấu hình một-một, tie đúng và prefix toàn G. Độ phức tạp phụ thuộc kích thước DAG, có thể tăng theo q^w; không mặc định đa thức theo n,q,m. Lọc cấu hình vô nghiệm trước ranking làm đổi baseline hiện hành. H_geom chỉ cộng được khi mẫu/denominator/correspondence được kiểm; H_ref cần xử lý cả reference invalid. ranking_complete là chứng nhận prefix, không yêu cầu enumeration_complete.
- Duyệt streaming + heap max-m giảm bộ nhớ, không tránh phải duyệt toàn G nếu chưa có bound/ranking certificate. Budget configurations/time/memory đăng ký trên DEV; tính cả enumerate/score/rank/solve. Hết budget trước chứng nhận prefix: `ranking_complete=false`, kết quả chỉ thăm dò tập con, không top-m toàn cục và không chứng nhận bằng nhau.
- Beam dùng cùng G/khả thi/cost, width/tie/budget khóa trước. Nếu beam bằng exact, báo exact đã chứng nhận chất lượng trong phạm vi; không ép exact phải thắng chất lượng. Nghiệm beam chỉ là upper bound cho minimization, không lower bound.

### 6.1 Điều kiện sinh prefix và scope đánh giá

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

## 7. Oracle, đồng hạng và kiểm thử

Oracle TV3 viết từ đặc tả, độc lập DP và primitive. Ca nhỏ ban đầu n<=3, q<=2, k<=1, tối đa 6 hành động thân/dấu; budget cụ thể tháng 1. Random cases seed cố định cùng ca thật có dấu chồng, marks below, distant interaction, reversed endpoints, CONNECT/LIFT, deadline k=0/1, empty, degenerate, equal-cost và infeasible. Boundary 0.19/0.20/0.21 mm có phép tính tay.

So khả thi và optimal value trong dung sai số học; kiểm riêng validity/cost của mỗi output. Chỉ so equality của action sequence khi cùng tie policy (ví dụ lexicographic candidate IDs, stroke IDs, direction, transition). Không gọi hai lịch đồng hạng khác nhau là mismatch. Không dùng kiểm trên ca nhỏ làm chứng nhận vét cạn được mọi Holdout.

## 8. Regret và kết luận

Pi là tập phương án hoàn chỉnh hữu hạn: mỗi pi gồm lựa chọn hình học, thứ tự, hướng nét và CONNECT/LIFT, cùng boundary đã khóa. Phương án pi triển khai tại theta0 giữ nguyên khi chứng nhận; đối thủ sigma tại từng đỉnh được chọn tự do trong toàn Pi, kể cả hình học khác. Với Pi cố định, khả thi không phụ thuộc theta và mỗi J affine:

`R_pi(theta)=J_pi(theta)-min_sigma J_sigma(theta)=max_sigma[J_pi(theta)-J_sigma(theta)]` lồi. Theta trong hình chữ nhật là tổ hợp lồi bốn đỉnh, nên maximum R_pi bằng maximum tại bốn đỉnh. Không suy ra minimax schedule thuộc bốn vertex winners. Exact optima cho exact modeled certificate; valid lower bounds cho conservative upper bound. Cả certificate và float tolerance phải khai báo phạm vi/sai số; heuristic không thay optimum.

Gap_m=(J_m-J_joint)/J_m chỉ khi cả hai optimal feasible và J_m>0. J_m=0, timeout, incomplete, infeasible tách riêng. epsilon_eq có căn cứ và duyệt trước freeze, chưa có giá trị mặc định. Kết luận hữu ích vượt biên / tương đương thực dụng trong tập đã khóa với đủ coverage / chưa đủ bằng chứng. Không dùng p>0.05 để kết luận tương đương hoặc extrapolate toàn tiếng Việt.

## Checkpoint triển khai DEV TV4

`geometry.py` dựng mọi cặp nét đồng thời chọn được và kiểm trước gộp state; graph owner có cạnh nếu một cặp candidates không tương thích. `joint_dp.py` giữ toàn bộ A trước, mode safe-forget bỏ assignment khi thân xong/hết pending/hết cạnh tương lai và giữ endpoint descriptor e riêng. Replay độc lập với recurrence nhưng cùng tác giả TV4, không là oracle TV3. Tests có ca kiểm tay, tương tác xa, boundary .19/.20/.21, incomplete và seed cố định so hai mode. Lệnh/path ở [tests README](../tests/research/README.md).

DEV geometry dùng polyline float, all-pairs và ngoại lệ contact disk hữu hạn; chưa có chứng nhận sai số số học hoặc quality gate. Policy này là phạm vi thử nghiệm có ID riêng, không thay điều kiện review/freeze và không coi kiểm no-forget/safe-forget là kiểm chứng độc lập. `vertex_analysis.py` xuất diagnostic bốn đỉnh cho schedule cố định; đối thủ full-set DEV và status luôn NOT_CERTIFIED.

Review S0 TV2 target `8dcfe66` đã tiếp nhận ở [phiếu review](reviews/tv2_joint_contract_s0_review_20261002.md), trạng thái REVIEWED_WITH_OPEN_GATES. Near-contact có hai tọa độ khác nhau mà nằm trong tolerance cần quy tắc chung trước freeze: snap trong geometry đã hash trước solve hoặc khai báo/đo/kiểm connector hữu hạn; chưa tự chọn một quy tắc. DEV hiện chỉ nhận endpoint trùng chính xác, không dùng tolerance để thêm chuyển động bút hạ chưa khai báo. Review này không ký code DP `510f4e1`.

### Checkpoint inner solve geometry cố định (02/10/2026)

TV4 cung cấp `solve_fixed_configuration(case, candidate_ids, theta, budget, safe_forget=...)` trong [joint_dp.py](../backend/research/joint_dp.py) cho bài toán F(g,theta). Giữ case/tập ứng viên/hash gốc; chỉ giới hạn lựa chọn geometry tại BODY theo ID từng owner, không lọc/re-hash case. Dùng chung feasibility/recurrence/replay DEV với joint; kết quả OPTIMAL/INFEASIBLE chỉ trong `fixed_configuration`, timeout/resource limit không exact dù có incumbent. Tests consistency không là oracle độc lập. H_ref/H_geom/top-m và aggregate budgets/verdicts thuộc TV2, chưa triển khai trong checkpoint này. Chi tiết interface/giới hạn ở [research README](../backend/research/README.md); không thay contract draft hoặc gate PENDING.

### Bản lập luận và witness để review (02/10/2026)

[Supporting Docs 36](support/36_joint_method_and_dp_argument.md) trình bày giả thiết, state sufficiency, soundness/completeness/DAG và projection safe-forget tương ứng code. Mệnh đề dùng số học chính xác; không tự chứng nhận primitive/cost/tie float hoặc đóng cận dự kiến §5.5. Witness synthetic hai owners/ba nét cho thấy H_ref immediate-mark có thể xếp khác F(g;theta), cùng ca k=0 bằng nhau; fixture/tests do TV4, không oracle TV3/baseline TV2 hoặc quality TV1. Contract draft, numeric/quality/review/freeze vẫn PENDING.

### Checkpoint số học DEV (02/10/2026)

[Audit TV4](reviews/tv4_numeric_audit_20261002.md) có counterexample prefix rounding chọn sai; core/replay hiện accumulate/compare Fraction chính xác trên primitive binary64 dưới cost_policy_id riêng, tie v2 và replay dev-v3. J hiển thị round cuối không quyết định tie; không trộn cost policies. Geometry/flatten vẫn float, c_min/contact không đổi; tolerance/epsilon/numerical freeze và oracle độc lập PENDING. Không đổi công thức J hoặc chứng minh error bound thật bằng sửa accumulator.
