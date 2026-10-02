> **SUPPORTING_REFERENCE / DRAFT_REVIEW_REQUIRED.** Owner TV4. Nguồn đặc tả là [Docs 31](../31_joint_solver_contract.md); giao diện/evidence là [Docs 32](../32_research_api_and_artifact_contract.md), ownership là [Docs 30](../30_research_development_plan.md). Tài liệu này giải thích và lập luận từ contract/code, không thay contract, oracle độc lập hoặc sign-off.

# Mô hình, lập luận DP và ví dụ geometry–lịch

Cập nhật 02/10/2026. Nền kiểm `f07a4a8`, code solver `bf68d0b`, contract `joint-contract-v1-draft`, artifact `joint-artifact-v1-draft`. Phân công giữ nguyên: TV4 mô hình/DP/trace/tích hợp; TV2 cost/baseline/runner; TV1 dữ liệu/quality/custody; TV3 oracle/primitive/hardware. Các số trong ví dụ là synthetic, không chọn theta0 hoặc tham số nghiệm thu. PR3 giữ đóng, HOLDOUT chưa mở.

## 1. Bài toán và điều cần giải thích trong báo cáo

Đầu vào là một từ/cụm ngắn đã bố trí trong world-mm. Với chữ i, C_i là tập hữu hạn các ứng viên trọn chữ: thân, dấu, thứ tự nét thân, quyền đảo chiều, precedence dấu và ID ổn định. Style/scale/slant/layout được áp dụng trước tạo tập ứng viên/hash; không biến đổi geometry sau solve. G là tích Cartesian của các C_i sau shared quality gate, gồm cả cấu hình không có lịch khả thi. Tập chưa qua quality review chỉ được gọi là tập DEV/synthetic.

Một phương án hoàn chỉnh pi=(g,sigma) chọn đúng một candidate mỗi owner và một lịch các nét: thứ tự, hướng và CONNECT/LIFT. Lịch phải tuân thân trái→phải, body_order, dấu sau thân sở hữu, precedence và deadline theo số thân hoàn tất. Reverse chỉ cho nét reversible. CONNECT cần contact đã khai báo; DEV hiện yêu cầu endpoint trùng chính xác, không thêm bridge ngầm. Hard floor .20 mm áp dụng theo policy cặp phải tách; vùng tiếp xúc được miễn có phạm vi hữu hạn. Đây là geometry đường tâm, chưa là khoảng hở vùng mực hoặc an toàn cơ khí.

Tại theta=(rho,lambda), mục tiêu là:

`J(pi;theta) = L_down(pi) + rho L_up(pi) + lambda N_cycle(pi)`.

L_up gồm p0→nét đầu, mọi chuyển động bút nâng và nét cuối→p_end. N_cycle đếm maximal pen-down runs, không lấy thẳng số nhấc của API sản phẩm cũ. `rho=v_down/v_up>0`, `lambda=v_down*tau>=0`; J có đơn vị mm, T_hat=J/v_down có đơn vị s trong mô hình vận tốc đơn giản. Thời gian tính solver và thời gian đo máy là hai metric riêng. Không thêm penalty thẩm mỹ vào J; quality gate xử lý trước solve.

Gọi Sigma(g) là tập lịch khả thi cho g. Về toán học, đặt `F(g;theta)=min_{sigma in Sigma(g)} J(g,sigma;theta)`; nếu Sigma(g) rỗng thì F=+infinity nội bộ. `J_joint=min_{g in G} F(g;theta)`. JSON thiếu J dùng null/outcome đúng scope, không xuất Infinity.

Baseline TV2 xếp g bằng H_ref/H_geom rồi giải lịch exact cho prefix_m. `J_m=min_{g in prefix_m}F(g;theta)`. Inner TV4 [solve_fixed_configuration](../../backend/research/joint_dp.py) giữ case/hash gốc; không lọc/re-hash case thành một bài toán khác. OPTIMAL/INFEASIBLE inner chỉ trong một cấu hình; TV2 chịu ranking, coverage và budget tổng trước báo verdict prefix. Joint không phải duyệt Cartesian tường minh để bao phủ G.

**Đóng góp cần trình bày:** mô hình finite geometry–schedule cho thân/dấu và phân tích có kiểm soát về gap, cấu trúc state và độ nhạy. DP/best-prefix/đường đi DAG là công cụ dùng trong mô hình; tài liệu này không tuyên bố thuật toán nền hoàn toàn mới hoặc ánh xạ đã được chứng minh từ một bài báo ngoài repo. TV2 phụ trách bảng toàn văn/trang và giới hạn đối chiếu tài liệu.

## 2. Giả thiết của lập luận tính đúng đắn

Các mệnh đề §3–6 là lập luận TV4 cho mô hình hữu hạn với số học/cost chính xác, cần review. Chúng cần đồng thời:

- Input immutable, ứng viên hữu hạn, đầy đủ IDs/owner/body_order/precedence/k/boundary; feasibility không đổi theo theta.
- Khả thi geometry phân rã thành validity từng candidate và compatibility từng cặp candidates. Mọi cặp có thể đồng thời được chọn đã kiểm trước gộp state; không có ràng buộc ba chữ/toàn trang ẩn hoặc geometry sinh sau solve.
- GeometryIndex đúng và graph tương tác bảo thủ: nếu một cặp lựa chọn có thể không tương thích, graph có cạnh owners đó. Policy loại suy biến/tiếp xúc/flatten là một phần input, không tự suy từ ảnh.
- Chi phí lịch là tổng action costs ở §4; không có gia tốc, jerk, lịch sử mực, tránh vật cản hoặc trạng thái máy ẩn cần nhớ thêm. Endpoint descriptor xác định tọa độ lẫn ID cần cho contact.
- Search xét hết actions hợp lệ trong scope, xử lý theo thứ tự DAG và kết thúc đầy đủ. Timeout/resource limit không thỏa giả thiết hoàn tất.

Code DEV dùng float, nên chứng minh số học chính xác không tự chứng nhận sai số geometry, equality/tie hoặc optimal value thực của implementation. Review policy/numeric và đối chiếu TV3 vẫn PENDING. Nếu mở rộng constraint/cost, phải kiểm lại state và chứng minh trước dùng lại kết luận.

## 3. State đủ thông tin: bất biến và khả năng nối tiếp

State là `S=(i,t,A,P,e)`:

| Trường | Thông tin và bất biến cần giữ |
|---|---|
| i,t | Các thân j<i đã xong. Nếu t>0, i đã chọn candidate và vẽ đúng t nét đầu body_order; nếu t=0 chưa bắt đầu thân i. Các thân j>i chưa bắt đầu |
| A | No-forget: mọi assignment đã chọn. Safe-forget: candidate active, owner còn pending và owner còn tương tác với chữ chưa chọn. Không có hai candidates cho cùng owner |
| P | Tập ID đầy đủ của dấu đã được kích hoạt sau khi thân owner xong nhưng chưa vẽ; k/precedence tra từ candidate immutable. Không thay P bằng số dấu |
| e | p0 trước action đầu, hoặc `(owner,candidate,stroke,orientation)` của nét cuối đã vẽ. Tra trực tiếp geometry registry, kể cả owner đã bỏ khỏi A |

Với owner có thân xong, mọi mark nằm trong candidate mà không còn trong P đã được vẽ. Marks của thân active chưa được kích hoạt; t và candidate active đủ xác định tiến độ body. Precedence DEV chỉ giữa marks cùng candidate; mọi predecessor không còn pending đã hoàn tất. Sau mỗi action vẽ, bút đang hạ tại e; action tiếp theo chọn CONNECT hoặc LIFT. Vì không có trạng thái trung gian UP tự do, không cần thêm pen-state vào key hiện tại; START/END dùng boundary riêng.

**Bổ đề 1 — tương đương continuation của no-forget.** Hai partial histories có cùng S có cùng tập continuation hợp lệ và cùng phần chi phí tương lai cho từng continuation, dưới §2.

Lập luận: i,t và A xác định thân/nét/candidate còn được chọn; P xác định những dấu còn lại, precedence và deadline. Geometry compatibility của lựa chọn mới được kiểm với A; geometry nội bộ đã kiểm khi chọn. e xác định đầu chuyển động và whitelist contact của nét tiếp theo. Cùng continuation thêm cùng action costs; quá khứ chỉ còn ảnh hưởng qua J đã tích lũy. Vì vậy có thể giữ history rẻ nhất ở S và backpointer của nó. Khi bằng cost, tie phải khai báo riêng; không yêu cầu lịch giống oracle có tie khác.

## 4. Truy hồi, tính hợp lệ và bao phủ

Khởi tạo `S0=(0,0,empty,empty,p0)`, D(S0)=0. Với action a hợp lệ dẫn tới S', cập nhật:

`D(S') = min(D(S'), D(S)+deltaJ(a))`.

| Action | Điều kiện và cập nhật | deltaJ |
|---|---|---|
| BODY khi t=0 | Flush marks có owner+k+1≤i trước bắt đầu thân. Chọn candidate local-valid và compatible với assignments cần giữ. Vẽ body đầu theo direction hợp lệ; đưa assignment vào A | LIFT: length+rho*distance(e,start)+lambda; CONNECT: length |
| BODY khi t>0 | Vẽ đúng body_order[t] của candidate active; t tăng. Khi thân xong: đưa đủ marks vào P, i tăng, t=0 | Như trên |
| MARK | ID nằm trong P và mọi predecessor đã vẽ. Vẽ đúng candidate/direction, xóa ID khỏi P | Như trên, MARK cũng có CONNECT/LIFT nếu hợp lệ |
| END | i=n,t=0,P rỗng; đi tới p_end với bút nâng | rho*distance(e,p_end), không cộng thêm lambda |

Ở DEV, CONNECT cần có nét trước, endpoint=start=contact.location và cặp ID whitelist. START chỉ LIFT. Mỗi LIFT mở một maximal pen-down run nên cộng đúng một lambda; CONNECT không mở run, END đã có lần nâng thuộc run cuối. Ca rỗng chỉ END, N_cycle=0.

**Bổ đề 2 — soundness.** Quy nạp từ S0: BODY bảo toàn thứ tự/phase và kiểm candidate trước chọn; MARK chỉ từ tập kích hoạt và đúng precedence; kiểm deadline trước BODY mới cấm vượt cửa sổ; direction/contact bảo toàn traversal. Nội bộ và mọi cặp selected geometry đã kiểm trước merging. END chỉ khi đủ nét. Mọi đường tới END do recurrence sinh biểu diễn một lịch khả thi trong policy/scope §2, mọi nét đúng một lần.

**Bổ đề 3 — completeness.** Lấy một phương án khả thi bất kỳ trong scope. Đọc nét theo thứ tự lịch: nếu body đầu, quy tắc khả thi bảo đảm deadline và compatibility nên BODY sinh đúng candidate; nếu body tiếp theo, t/body_order khớp; nếu mark, owner đã xong và predecessors không còn P nên MARK sinh nó. Direction và transition đều có trong choices. Quy nạp cho toàn lịch rồi END. Vì vậy recurrence bao phủ mọi lịch; pruning chỉ giữ best-prefix của state tương đương, không cần giữ mọi history của lịch đó để giữ một optimum.

**Bổ đề 4 — DAG.** Key `K(S)=(i,t,-|P|)` tăng lexicographic sau mỗi action vẽ: BODY chưa xong tăng t; BODY xong tăng i dù t reset và P tăng; MARK giữ i,t nhưng giảm |P|. K không phụ thuộc A/e, nên merging và forgetting không tạo chu trình. Heap hiện tại dùng K rồi serial, không dùng J làm ưu tiên Dijkstra. Mọi predecessor có key nhỏ hơn được xử lý trước state; khi state được processed, best label/backpointer đã ổn định. END là cạnh đến terminal hoặc phép cộng terminal tương đương.

**Mệnh đề — DP no-forget tối ưu trong mô hình.** Với §2, graph hữu hạn; soundness, completeness, state sufficiency và DAG cho phép quy nạp theo K rằng D(S) là cost prefix nhỏ nhất tại S. Min các terminal costs cho optimum trong scope. Nếu không có END sau search đầy đủ thì scope vô nghiệm. Restricted fixed-configuration chỉ bỏ BODY choices khác cấu hình đã khai báo, nên cùng lập luận cho F(g;theta); không suy full-set infeasible từ fixed infeasible.

## 5. Quên an toàn và các trường hợp không được quên

Gọi U(S) là owners chưa chọn candidate: `{i,...,n-1}` nếu t=0, `{i+1,...,n-1}` nếu t>0. Assignment owner j chỉ được xóa khi:

1. Thân j đã xong, j<i.
2. Không có mark của j trong P.
3. Không có cạnh j–h trong graph tương tác với bất kỳ h thuộc U(S).
4. Mọi pair constraints với owners đã chọn đã kiểm xong; e vẫn giữ descriptor đầy đủ, không tra qua A.

**Bổ đề 5 — projection bảo toàn continuation.** Với một state hợp lệ, bỏ assignment thỏa bốn điều kiện không đổi tập continuation hay cost suffix. Thân/marks j không còn action tương lai. Không cạnh tới U nghĩa mọi lựa chọn mới của h đều compatible với candidate j theo graph bảo thủ. Owners đã chọn không đổi geometry, nên pair checks đã đóng không cần lặp. J tương lai phụ thuộc j chỉ nếu e còn ở j; descriptor độc lập đã giữ tọa độ và contact IDs. Không có ràng buộc toàn cục ẩn theo §2.

Điều kiện quên chỉ trở nên dễ hơn về sau: U thu hẹp, không có pending mới cho owner đã xong. Vì vậy sau khi quên không cần phục hồi A_j. Hai histories có cùng projected state có cùng continuation; giữ prefix rẻ nhất là hợp lệ. Áp dụng bổ đề sau từng transition và lập luận DAG ở §4 cho safe-forget cùng optimum/feasibility với no-forget trong mô hình. Quá khứ g đã quên vẫn tái dựng từ backpointer actions, không lấy candidate_ids cuối chỉ từ A terminal.

Graph DEV trong [geometry.py](../../backend/research/geometry.py) có cạnh khi tồn tại cặp candidates không compatible; cặp compatible không tạo cạnh. Điều này đủ cho pairwise feasibility đã precompute: nếu không cạnh, mọi cặp choices hợp lệ local đều compatible. Không phải graph chỉ của candidates đã thắng hoặc chỉ của hai chữ kề. Contact giữa owner đã quên và nét mới vẫn cần descriptor e, registry và whitelist; không thể chỉ giữ tọa độ e vì hai ID cùng tọa độ có contact khác nhau.

| Quên sai / gộp thiếu | Vì sao mất thông tin |
|---|---|
| Thân xong là bỏ ngay | Owner có mark pending: mất candidate/precedence/deadline của marks |
| Bỏ chỉ vì không có chữ kề xung đột | Candidate có tương tác xa; choice mới có thể va vào geometry đã quên |
| Bỏ e theo A hoặc chỉ lưu tọa độ | UP cost hoặc quyền CONNECT phụ thuộc endpoint/ID đã mất |
| Chỉ nhớ số pending | Cùng số nhưng khác stroke/owner/deadline có continuation khác |
| Gộp trước kiểm geometry rồi kiểm cuối | Prefix tốt hơn nhưng bất khả thi có thể thay mất prefix cần thiết; kiểm cuối không khôi phục history đã bỏ |

Bổ đề dựa trên graph đúng, không tự chứng minh code primitive đúng. Kiểm no-forget/safe-forget cùng tác giả chỉ là consistency; TV3 phải dùng primitive/enumerator độc lập.

## 6. Đối chiếu implementation và giới hạn

| Nghĩa vụ trong lập luận | Điểm nối hiện tại |
|---|---|
| Hash/input/policy và scope | ResearchCase validation; solve_joint/solve_fixed_configuration; DEV/synthetic only |
| Local/pair compatibility trước merging | compile_geometry → GeometryIndex.compatible trong available(BODY) |
| Phase/deadline/predecessors | available và successor trong joint_dp.py |
| Forget sau update, e độc lập | successor: owner>=i hoặc pending_owner hoặc future neighbor; endpoint tra index.strokes[e[:3]] |
| DAG relaxation/terminal/backpointer | queue theo (i,t,-len(P),serial); best/processed; consider_end/reconstruct |
| Chi phí và trace một lịch | check_schedule_cost, không là independent checker |
| Renderer giữ traversal | render_dev.py; không sinh bridge/style sau solve |

Lập luận trên dùng phép cộng/so sánh chính xác. Code cộng float từng delta và so tie trực tiếp; replay tổng coefficients bằng fsum rồi tính J. Hai cách cộng có thể khác làm tròn. Monotonic float addition không tự chứng minh tie toàn cục hoặc optimum toán học qua ca gần bằng; geometry float cũng có rủi ro gần ngưỡng. Cần numeric policy/error bound, tolerance và oracle review trước claim exact modeled được nghiệm thu. Không tự thêm epsilon hoặc đổi policy trong slice này.

Search guard gồm preprocessing/search/replay; incomplete không có chứng minh phủ hết graph, kể cả có incumbent. Tracemalloc process-wide và cooperative guard là DEV/offline, không worker cưỡng bức dừng hoặc đo RSS. Không tuyên bố O(1) backpointer/memory mỗi state: best giữ path_tie tuple dài và actions/heap/index; mode safe-forget chưa phải rolling-layer implementation. Cận dự kiến Docs 31 §5.5 cần đối chiếu stencil/owner IDs/endpoint/precompute cùng bookkeeping thực tế; bảng này không hoàn tất chứng minh cận thực thi hoặc benchmark.

## 7. Ví dụ synthetic: geometry có thứ hạng tốt hơn nhưng lịch tối ưu kém hơn

[Fixture có hash](../../tests/research/fixtures/method_gap_example.json) biểu diễn hai owners/ba nét trừu tượng cho text NFD áb; đây không là glyph tiếng Việt đọc được, font TV1 đã duyệt hay quality gate đã khóa. Không font/license nguồn ngoài; hình học tự tạo TV4. Hai cấu hình A/B khác vị trí mark của owner 0:

| Nét | A: a-local | B: a-delayed |
|---|---|---|
| body 0 | (0,0)→(1,0) | giống A |
| tone 0 | (0,1)→(1,1) | (3,1)→(4,1) |
| body 1: b-fixed | (2,0)→(3,0) | giống A |

p0=(0,0), p_end=(4,1), k(tone)=1; mọi nét forward-only, không contact/CONNECT, chỉ LIFT. Các cặp selected strokes tách ít nhất 1 mm, cao hơn floor .20. Mỗi lịch có L_down=3 và N_cycle=3. Thân 0 trước thân 1; mark sau thân 0 nên chỉ có hai thứ tự: **early** body0→tone0→body1 và **late** body0→body1→tone0. Liệt kê hai thứ tự này là phép tính tay của witness, không triển khai baseline TV2 hay oracle TV3.

| Cấu hình / lịch | Các khoảng UP khác 0 | L_up | J tại rho=.5, lambda=2 |
|---|---|---|---|
| A early, lịch reference | sqrt(2), sqrt(2), sqrt(2) | 3sqrt(2) | 9+1.5sqrt(2) ≈ 11.121320 |
| A late | 1, sqrt(10), 3 | 4+sqrt(10) | 11+.5sqrt(10) ≈ 12.581139 |
| B early, lịch reference | sqrt(5), sqrt(5), sqrt(2) | 2sqrt(5)+sqrt(2) | 9+sqrt(5)+.5sqrt(2) ≈ 11.943175 |
| B late | 1, 1 | 2 | 10 |

Reference immediate-mark/forward/LIFT của Docs 31 cho H_ref(A)<H_ref(B), nên top-1 theo reference chọn A; inner tối ưu của A vẫn early. Joint xét cả geometry/lịch chọn B late, cost 10. Đây là phân tích witness đúng chính sách reference cụ thể, chưa là kết quả chạy module H_ref/staged_top_m TV2.

Với mọi rho>0, lambda≥0 trong ví dụ, J1=3+3lambda+3sqrt(2)rho, J_joint=3+3lambda+2rho. Chênh lệch là `(3sqrt(2)-2)rho>0`; prefix đủ hai cấu hình bằng joint. Ví dụ giải thích geometry có thể làm đổi lịch tốt nhất và reference ranking không bảo toàn thứ hạng F. Nó không chứng minh joint luôn hơn top-m, không nói geometry B đẹp hoặc qua quality gate. N_cycle bằng nhau nên không chứng minh vai trò lambda/switching; gap tương đối thay theo lambda do mẫu số, quyết định winner không đổi.

Nếu chỉ đổi k=0, late bị cấm cho cả hai; reference early cũng là lịch khả thi duy nhất. A thắng, top-1 bằng joint. Hash candidate-set đổi vì delay policy thuộc input đã hash. Đây là một đối chiếu điều kiện mô hình, không điều chỉnh dữ liệu HOLDOUT hoặc đề xuất k nghiệm thu.

**Điều kiện đủ bằng nhau:** nếu prefix đã chứng nhận chứa g* có F(g*)=J_joint và mọi inner exact, J_m=J_joint. Một trường hợp cụ thể là F(g;theta)=A(g;theta)+C(theta) cho mọi g và ranker thực sự xếp đúng A (cùng xử lý infeasible/tie); prefix chứa minimizer A. Không tự suy H_ref/H_geom thỏa điều kiện này: cần chứng minh trên mô hình/scope riêng. Nested prefix và inner exact cho J_joint≤J_(m+1)≤J_m; incomplete không dùng để chứng nhận chuỗi bất đẳng thức trên toàn G.

## 8. Tái lập witness và việc review tiếp theo

```sh
PYTHONPATH=backend backend/venv/bin/python3 -m pytest tests/research/test_method_example.py -q

backend/venv/bin/python3 -m backend.research.dev_solve \
  --manifest tests/research/fixtures/method_gap_example.json \
  --case-id tv4-method-geometry-schedule-gap --rho 0.5 --lambda-mm 2 \
  --mode both --wall-time-ms 10000 --max-states 100000 --memory-limit-mb 64 \
  --output output/research_dev/method-gap-v1.json \
  --svg-output output/research_dev/method-gap-v1.svg
```

CLI không overwrite, lần sau chọn tên mới. Budget là ví dụ DEV. Tests witness kiểm bốn lịch tính tay, fixed/joint và no-forget/safe-forget ở ba theta minh họa, cùng ca k=0. agreement/PASS của TV4 chưa là validation độc lập; SVG DEV_ONLY không cấp quyền in. Manifest SHA-256 `8b2b8d073b88ebe8ea9623d2cdf7bbdeaa19913e64876dea14fef270331681eb`; candidate-set SHA-256 `04d6bd6b29a190d37bc59f2373e3566d34c1d2b8e32a7eae5ff21db93e37be14`.

TV2 review mô hình/cost, witness reference ranking và điều kiện bằng nhau; TV3 review state/projection/primitive và chạy oracle tự viết trên fixture thô; TV1 review giới hạn glyph/reference/quality và thiết kế ca thật riêng. TV4 xử lý counterexample và cập nhật Docs 31 khi có thay đổi đã review. Liên quan [Q02/Q04/Q05/Q06/Q10/Q11](../handoff/pending_decisions.md), tất cả vẫn PENDING; thêm bản lập luận không đóng gate hoặc ký thay owner.
