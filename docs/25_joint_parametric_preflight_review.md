<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** Báo cáo/contract/bằng chứng lịch sử. Giữ nguyên số liệu, sign-off và phạm vi bên dưới; không dùng corpus cũ hoặc preflight để nghiệm thu hướng mới. ID RQ/PR trong phần cũ là hệ ký hiệu lịch sử.
> Kế hoạch hiện hành: [Docs 30](30_research_development_plan.md); đặc tả [Docs 31](31_joint_solver_contract.md) và [Docs 32](32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

# Kiểm tra trước đề cương: đồng tối ưu, chứng nhận dưới bất định và hiệu chuẩn theo quyết định

> **Cập nhật phạm vi theo quyết định nhóm sau phản biện mô phỏng 01/10:** số liệu dưới đây là lịch sử preflight. Kế hoạch hiện hành nằm ở [Docs 26](26_teacher_discussion_and_8_month_plan.md), tiêu chí và disposition ở [Docs 27](27_supervisor_feedback_disposition.md). Phân tích khi đồng tối ưu có lợi/bằng nhau trở thành bắt buộc; chỉ giữ pilot font do TV1/TV4 đồng chủ trì, hoãn Writer Profile và Pareto/cắt tỉa mở rộng. Hiệu chuẩn chủ động không thuộc cam kết kỳ này. Baseline top-m và split mới thay cho 20 từ cũ ở đánh giá chính được quy định trong Docs 27; các nhận định Balas bên dưới chỉ là đối chiếu abstract, chưa kiểm chứng toàn văn.

## Material Passport

- Ngày kiểm tra: 30/09/2026.
- Hiệu đính cách diễn giải nguồn và bằng chứng: 01/10/2026; xem [bản trao đổi và tiến độ 8 tháng](26_teacher_discussion_and_8_month_plan.md).
- Loại: rà soát tài liệu có trọng tâm, lập luận toán học và thử nghiệm phần mềm nhỏ.
- Trạng thái: `PREFLIGHT_COMPLETED; FORMAL_VALIDATION_PENDING`.
- Người thực hiện: Codex trong phiên TV4; các vai trò phản biện được thực hiện trong cùng phiên, chưa có review độc lập của TV1/TV2 hoặc human sign-off.
- Mục đích: quyết định phạm vi đăng ký nghiên cứu khi còn khoảng ba ngày trước hạn đề cương.
- Không phải systematic review, kiểm chứng toàn bộ production, formal benchmark hoặc xác nhận thiết bị thật.
- Nguồn chương trình local: `scripts/research_parametric_preflight.py`; script đang chưa được commit trên nhánh này và không nằm trong commit riêng phần docs. Các lệnh bên dưới ghi lại lần chạy local, chưa là hướng dẫn tái lập hoàn chỉnh từ checkout remote. Dữ liệu snapshot để review: [summary](evidence/research_preflight_20260930/summary.json), [kết quả từng ca](evidence/research_preflight_20260930/case_results.csv), [hình học và toàn bộ lịch khả thi](evidence/research_preflight_20260930/cases_and_plans.json).

## 1. Kết luận để quyết định đề cương

**Giữ đồng tối ưu hình học và lịch thực hiện nét/dấu làm câu hỏi nghiên cứu chính. Thêm phân tích độ ổn định và chứng nhận có điều kiện vào phương pháp. Đặt hiệu chuẩn chủ động theo quyết định ở phạm vi mở rộng.**

Các kết quả hiện có hỗ trợ tính khả thi của một mô hình nhỏ và cho thấy tham số chuyển động có thể làm đổi lựa chọn nét. Chưa đủ cơ sở để tuyên bố một thuật toán mới hoàn chỉnh, sự vượt trội trên chữ Việt thật hoặc tiết kiệm phép đo hiệu chuẩn.

Phát hiện quan trọng khi đối chiếu tài liệu: bài toán chọn phép đo để xác định phương án có chi phí tuyến tính tốt nhất đã được nghiên cứu trong linear bandits, transductive experimental design và combinatorial pure exploration. Khác biệt rời rạc so với GoBOED cũng chưa đủ để khẳng định khoảng trống, vì công trình AAAI 2021 đã xét cả không gian tổ hợp và đường đi. Một đóng góp phương pháp riêng sẽ cần khai thác cấu trúc tương tác glyph và cửa sổ dấu chờ, kèm phân tích/đối chứng.

Ở bước tính toán, đồng tối ưu cải thiện baseline phân tầng mẫu trên 25/40 ca tổng hợp. **Trên 16 cấu hình glyph thực trong phép thử này, hai phương pháp cho chi phí bằng nhau tại toàn bộ 25 điểm tham số đã thử, trong tolerance số.** Với cùng tập ứng viên khả thi và cùng chi phí cuối, tối ưu đồng thời không thể kém phương án phân tầng khả thi. Kết quả bằng nhau phải giữ trong kết luận; chưa xác nhận lợi ích trên dữ liệu tiếng Việt thực.

## 2. Rà soát hiện trạng repo

- `backend/handwriting/composition.py:536`: Viterbi chọn các trạng thái hình học trên từng lớp, với chi phí trạng thái và chuyển tiếp. Chưa phải bộ giải đồng tối ưu mới chứa đầy đủ lịch dấu chờ và biên tương tác.
- `backend/handwriting/engine.py:812`: thứ tự nét phụ của PR3 có cơ chế riêng. Kết quả PR3/E1 không tự xác nhận một DP mới giải đồng thời hình học và lịch thực hiện dấu.
- Dữ liệu E1 hiện có lưu quãng đường pen-up, số lần nhấc, va chạm và fingerprint. Chưa đủ để nghiệm thu mục tiêu thời gian mới; cần tách rõ `L_down`, `L_up`, chu kỳ nâng/hạ và nguồn tham số.
- Nền tảng tái sử dụng được: hình học nét đơn, biến thể glyph, sinh dấu, nối nét, simulator, runner và bằng chứng DEV.
- Khối thử nghiệm ở tài liệu này được thêm dưới `scripts/` và `docs/evidence/`; không thay đổi production hoặc phần hardware/TV2.

## 3. Đối chiếu các tiền lệ gần nhất

### 3.1. Các nguồn và mức độ đã đọc

**Tiền lệ gần với bộ giải lõi:** Balas (1999), *New classes of efficiently solvable generalized Traveling Salesman Problems*, và Balas & Simonetti (2001), *Linear Time Dynamic-Programming Algorithms for New Classes of Restricted TSPs: A Computational Study*. Đã đối chiếu abstract trên trang nhà xuất bản. Các bài xét ràng buộc thứ tự/cửa sổ trong TSP, xây mạng phân lớp/DP; Balas 1999 còn nêu cửa sổ riêng `k(i)`. Nhóm cần đối chiếu chi tiết cách mã hóa trạng thái trước khi khẳng định mức kế thừa. Đóng góp dự kiến nằm ở mô hình chữ/dấu, tương tác hình học và phân tích đồng tối ưu so với phân tầng, không phải phát minh DP cửa sổ hoặc cửa sổ không đồng nhất. [Balas 1999](https://link.springer.com/article/10.1023/A:1018939709890), [Balas & Simonetti 2001](https://pubsonline.informs.org/doi/10.1287/ijoc.13.1.56.9748)

1. **Chakraborty et al., STACS 2010 — Two-phase Algorithms for the Parametric Shortest Path Problem.** Đã đối chiếu abstract chính thức. Công trình nghiên cứu tiền xử lý/truy vấn đường đi với trọng số là hàm của **một biến chung**. Đây là hướng nghiên cứu liên quan; nguồn này không trực tiếp bao trùm mô hình hai tham số của nhóm và không được dùng làm nguồn cho chứng nhận bằng các đỉnh ở §4.3. [Nguồn chính thức](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.STACS.2010.2452)

2. **Soare, Lazaric & Munos, NeurIPS 2014 — Best-Arm Identification in Linear Bandits.** Đã đọc abstract và phần giới thiệu của PDF. Chọn mẫu để phân biệt phương án gần tối ưu trong mô hình tuyến tính là vấn đề đã được nghiên cứu. [Nguồn chính thức](https://papers.neurips.cc/paper_files/paper/2014/hash/f8d84caae48546d0934d637ab54f7086-Abstract.html)

3. **Fiez et al., NeurIPS 2019 — Sequential Experimental Design for Transductive Linear Bandits.** Đã đọc PDF, đặc biệt định nghĩa ở §2 và mô hình ở §1. Tập phép đo và tập phương án quyết định có thể khác nhau; các phép đo tuyến tính nhiễu được chọn tuần tự để nhận diện phương án tốt nhất. Đây là hướng nghiên cứu liên quan. Ánh xạ sang hiệu chuẩn thiết bị viết là suy luận của nhóm ở §3.2, có điều kiện mô hình đo; bài không trực tiếp trình bày ứng dụng OmniDraw hoặc hiệu chuẩn máy viết. [PDF chính thức](https://proceedings.neurips.cc/paper_files/paper/2019/file/8ba6c657b03fc7c8dd4dff8e45defcd2-Paper.pdf)

4. **Du, Kuroki & Chen, AAAI 2021 — Combinatorial Pure Exploration with Full-Bandit or Partial Linear Feedback.** Đã đọc abstract, PDF §4.1 và điều kiện oracle. Công trình xét hành động tổ hợp, phản hồi tuyến tính một phần, bao gồm đường đi; hiệu quả tính toán dựa trên oracle tối ưu tương ứng. Vì vậy cần đối chiếu cả chi phí xây oracle glyph/lịch dấu, thay vì chỉ viện dẫn khác biệt rời rạc/lồi. [Nguồn chính thức](https://ojs.aaai.org/index.php/AAAI/article/view/16892)

5. **Wan et al., 2026 — Decision-Focused Sequential Experimental Design: A Directional Uncertainty-Guided Approach.** Bản tiền công bố arXiv; đã đọc abstract và §2.2. Công trình dùng bất định theo hướng chi phí phục vụ quyết định, có cập nhật tập predictor và quy tắc chọn thí nghiệm. Chưa xác nhận trạng thái xuất bản qua hội nghị/tạp chí. [Bản tác giả](https://arxiv.org/abs/2602.05340)

6. **Go, Qian & Yoon, 2026 — Goal-driven Bayesian Optimal Experimental Design for Robust Decision-Making Under Model Uncertainty.** Bản tiền công bố arXiv; đã đọc §3.1–3.3 và kết luận. Phiên bản này dùng thiết kế một bước và tầng quyết định lồi có thể vi phân. Đây là khác biệt phạm vi, không phải bằng chứng toàn bộ bài toán rời rạc còn trống. [Bản tác giả](https://arxiv.org/abs/2605.26093)

7. **Gilbert & Spanjaard, arXiv 2016 — A double oracle approach for minmax regret optimization problems with interval data.** Đã đối chiếu abstract bản arXiv; chưa xác nhận journal version trong đợt này. Có tiền lệ cho tối ưu minmax regret và cận anytime trong bài toán tổ hợp, ứng dụng đường đi. [Bản tác giả](https://arxiv.org/abs/1602.01764)

8. **Wang et al., AAAI 2020 — RoboCoDraw.** Đã đối chiếu abstract chính thức: hệ thống robot vẽ sử dụng thuật toán tối ưu đường đi theo thời gian. [Nguồn chính thức](https://ojs.aaai.org/index.php/AAAI/article/view/6609)

9. **Le et al., CONSTANT, WACV 2026.** Đã đối chiếu trang tác giả về sinh ảnh chữ viết từ một mẫu phong cách và dữ liệu tiếng Việt. Đợt này không kiểm tra lại toàn bộ thực nghiệm của bài. Học phong cách/sinh ảnh tiếng Việt đã có đối chứng mạnh riêng. [Trang tác giả](https://duylebkhcm.github.io/constant_website/)

Các tìm kiếm gồm nhóm từ khóa về robot handwriting + calibration/uncertainty; stroke planning + regret; parametric shortest path; transductive linear bandits; combinatorial pure exploration; Vietnamese + joint stroke optimization. Đây là rà soát có trọng tâm, không có tuyên bố PRISMA hoặc bao phủ toàn bộ cơ sở dữ liệu. Không tìm thấy đúng một cụm từ trong kết quả tìm kiếm không được xem là chứng minh tính mới.

### 3.2. Ánh xạ bài toán của nhóm vào tiền lệ

Với một phương án viết hoàn chỉnh `π`, đặt:

\[
z_\pi=(L_{down,\pi},L_{up,\pi},N_{cycle,\pi}),\qquad
\theta=(\alpha,\beta,\tau),\quad
\alpha=1/v_{down},\ \beta=1/v_{up}.
\]

Khi đó thời gian mô hình là `z_πᵀθ`. **Ánh xạ do nhóm đề xuất, không phải phát biểu ứng dụng của Fiez et al.:** nếu một đoạn đo có đặc trưng biết trước `x` cung cấp quan sát dạng `xᵀθ + noise`, và nhiễu/các tập phương án thỏa giả thiết của mô hình tương ứng, thì có thể xem xét bài toán hiệu chuẩn trong khuôn transductive linear bandits. Chưa có dữ liệu xác nhận các điều kiện đó trên thiết bị. Chỉ chuyển tên các phương án thành glyph/lịch viết chưa tạo ra một bài toán tổng quát mới.

Điểm cần phát triển để có đóng góp: biểu diễn không gian phương án ngầm; oracle chính xác khai thác độ rộng tương tác và cửa sổ trì hoãn; chứng nhận khi oracle giới hạn thời gian; chi phí phép đo khác nhau; hoặc một mô hình vật lý có đặc tính mà các phương pháp tiền lệ chưa xử lý. Mỗi điểm phải được kiểm tra riêng với baseline thích hợp.

## 4. Kiểm tra lập luận toán học

### 4.1. Các giả thiết bắt buộc

1. Tập lịch khả thi `Π` hữu hạn và giống nhau với mọi tham số trong miền đang xét.
2. Glyph candidates, khoảng hở và luật nối/trì hoãn đã cố định. Mọi vi phạm cứng bị loại trước tối ưu.
3. Chi phí mỗi lịch có dạng affine trong tham số. Không đưa ảnh hưởng tốc độ lên hình học/khả thi vào cùng chứng nhận nếu chưa mô hình hóa.
4. Miền tham số `Ω` là đa diện lồi, hữu hạn; trong preflight là một hình chữ nhật.
5. Oracle cho giá trị tối ưu thật hoặc cận dưới hợp lệ của cùng bài toán; một tập nghiệm beam chưa có cận không đủ.

### 4.2. Chuẩn hóa thời gian

\[
\widehat T_\pi=\frac{L_{down,\pi}}{v_{down}}
+\frac{L_{up,\pi}}{v_{up}}+\tau N_{cycle,\pi},
\qquad
J_\pi=v_{down}\widehat T_\pi
=L_{down,\pi}+\rho L_{up,\pi}+\lambda N_{cycle,\pi}.
\]

Trong đó `ρ=v_down/v_up`, `λ=v_down τ`, đơn vị `λ` là mm. Hai lịch được so ở cùng một thiết bị có cùng hệ số dương `v_down`, nên thứ hạng được bảo toàn. Các số regret theo `J` ở preflight là mm tương đương, không phải giây thực đo. Điểm đầu/cuối có cùng trạng thái bút nâng để mỗi phiên tiếp xúc tương ứng một chu kỳ nâng/hạ.

### 4.3. Chứng nhận bằng các đỉnh miền tham số

Đặt:

\[
V(\theta)=\min_{\sigma\in\Pi}J_\sigma(\theta),\qquad
R(\pi;\Omega)=\max_{\theta\in\Omega}\{J_\pi(\theta)-V(\theta)\}.
\]

**Bổ đề.** Với các giả thiết trên, đối với một lịch `π` cố định:

\[
R(\pi;\Omega)=\max_{v\in Vert(\Omega)}\{J_\pi(v)-V(v)\}.
\]

**Chứng minh.** `V` là minimum của các hàm affine nên là hàm lõm. `J_π−V` là hàm lồi. Viết một điểm trong đa diện thành tổ hợp lồi của các đỉnh, tính lồi cho thấy regret ở điểm đó không vượt giá trị lớn nhất tại các đỉnh. Các đỉnh cũng thuộc miền, nên đạt đẳng thức. QED.

Hệ quả: một lịch tối ưu ở bốn góc hình chữ nhật sẽ tối ưu trên toàn hình chữ nhật. Nếu regret tại bốn góc không vượt `ε`, lịch có chứng nhận kém tối ưu tối đa `ε` trên miền. Các lịch tối ưu ở các góc được phép khác nhau; chỉ lịch cần chứng nhận phải là một lịch cố định khả thi.

**Chi phí vận dụng:** sau khi có một lịch ở điểm vận hành, chỉ cần bốn lần gọi oracle chính xác tại bốn góc để kiểm tra lịch đó; không cần liệt kê toàn bộ bản đồ vùng tối ưu. Đây là ứng dụng một tính chất lồi chuẩn, chưa được coi là định lý mới của nhóm.

Nếu oracle giới hạn thời gian cho cận dưới `LB(v)≤V(v)`, thì
`max_v[J_π(v)−LB(v)]` là cận trên regret hợp lệ. Ngược lại, thay `V(v)` bằng giá trị của một nghiệm heuristic sẽ đánh giá thấp regret và có thể tạo chứng nhận sai.

### 4.4. Chọn nghiệm minimax và các phản ví dụ

Để chọn một lịch minimax regret, không được giới hạn ứng viên chỉ vào các lịch thắng tại bốn góc. Ca đại số kiểm tra có ba bộ hệ số `(L_down,L_up,N)`:

- A = `(10,10,1)`;
- B = `(15,0,1)`;
- C = `(13.5,4,1)`.

Trong miền `ρ∈[0.2,1]`, `λ∈[0.5,2]`, regret lần lượt là `5`, `3`, `2.5`. C không tối ưu tại bất kỳ `ρ` nào trong miền nhưng là lựa chọn minimax tốt nhất của ba lịch. Đây là ví dụ đại số minh họa, chưa được hiện thực hóa thành glyph.

Các điều kiện khác được kiểm tra: hai lịch bằng điểm; thiếu một ứng viên dẫn tới chứng nhận giả; một lịch khả thi ở góc nhưng vô nghiệm ở giữa nếu tính khả thi phụ thuộc tham số. Chứng nhận theo chi phí không thay thế kiểm tra tính khả thi.

### 4.5. Sai số mô hình và mức độ chính xác số

Nếu thời gian thật của **mọi** lịch liên quan sai khác mô hình tối đa `δ` giây, một chứng nhận regret `ε` giây trong mô hình chuyển thành cận `ε+2δ` giây. Hiện chưa có số đo xác nhận `δ`; preflight không chứng nhận thời gian vật lý.

Chương trình dùng floating point, tolerance `1e-8`; có sai số lớn nhất khoảng `1.42e-14` khi so hai cách giải. Đây là kiểm tra số học, chưa phải chứng nhận số học máy bằng interval arithmetic hoặc số hữu tỉ.

## 5. Đặc tả phép thử và tính độc lập

### 5.1. Phạm vi hữu hạn được kiểm tra

- 16 cấu hình glyph: hai font `oly`, `omni_casual`; từ DEV `vẫy` và ba đoạn `iế`, `ướ`, `yệ` lấy từ từ DEV đã dùng; mỗi trường hợp chạy `k=0` và `k=1`.
- Đoạn glyph phải được gọi là **đoạn**, không tính thành những từ đầy đủ hoặc corpus đại diện.
- 40 ca hình học tổng hợp được sinh bằng `random.Random(20260930)` theo một khuôn nhỏ: hai hoặc ba chữ, hai biến thể mỗi chữ, tọa độ thân biến thiên ngẫu nhiên có giới hạn và một dấu ở chữ đầu. Cứ mỗi mười ca, một ca được sửa có chủ ý thành vô nghiệm và một ca có biến thể bằng nhau. Đây là tập sinh có kiểm soát kèm ca biên, không phải lấy mẫu đại diện cho tiếng Việt.
- Mỗi chữ tối đa hai ứng viên hoàn chỉnh. Mỗi ứng viên gồm thân và toàn bộ dấu; hướng và thứ tự các nét trong thân cố định.
- Tối đa ba chữ và sáu macro-actions: một macro-action cho thân chữ, một cho mỗi nét phụ/dấu. Các chuyển bút nội bộ thân vẫn được tính chi phí.
- Thân chữ giữ thứ tự trái sang phải; dấu chỉ được thực hiện sau thân sở hữu nó và trước khi số thân tiếp theo hoàn tất vượt `k`.
- Hai thân kề nhau được phép nối khi liên tiếp trong lịch, quyền nối phù hợp và bridge qua kiểm tra hình học. Các trường hợp còn lại phải nâng bút.
- Mỗi lịch bắt đầu/kết thúc tại cùng vị trí home với trạng thái bút nâng.
- `c_min=0.20 mm` với tolerance số đã nêu. Preflight dùng tập con bảo thủ: mọi cặp dấu–thân và dấu–dấu phải giữ khoảng hở; chưa xử lý ngoại lệ gắn dấu vào thân có chủ ý. Va chạm bridge được kiểm tra trên mọi glyph, gồm tương tác không kề nhau.
- Miền thăm dò `ρ∈[0.2,1.0]`, `λ∈[0.5,6.0] mm`; 25 điểm so DP/vét cạn và lưới 21×21 kiểm tra regret. Đây là giá trị giả định cho exploration, chưa đăng ký điểm vận hành hay miền thiết bị.

### 5.2. Hai cách giải

**Vét cạn:** liệt kê mọi tổ hợp hình học, mọi hoán vị hành động, lọc thứ tự thân/precedence/deadline rồi liệt kê mọi lựa chọn nối/nâng hợp lệ. Tính độ dài và số chu kỳ trực tiếp từ lịch hoàn chỉnh.

**DP mẫu:** với từng tổ hợp hình học cố định, xây trạng thái prefix `(mask,last)` và cập nhật chi phí từng hành động; lấy minimum trên mọi tổ hợp hình học. Khi mở một thân mới, các dấu đến hạn phải đã hoàn tất.

**Truy hồi trong mô hình mẫu:** với `a` là hành động được phép tiếp theo,

\[
D[M\cup\{a\},a]=\min_{\ell}\{D[M,\ell]+\Delta J(\ell,a)\}.
\]

`ΔJ` chứa chiều dài tiếp xúc của hành động, đường nâng bút nội bộ, chi phí tới điểm bắt đầu và số chu kỳ. Nếu nối hai thân được phép, lấy minimum của chi phí nối và chi phí nâng. Giá trị cuối cộng đường pen-up về home.

Hai cách giải không dùng chung hàm cập nhật trạng thái hoặc hàm tính chi phí lịch. Chúng dùng chung đầu vào, primitive hình học và kiểm tra khả thi. Vì vậy đây là kiểm tra chéo triển khai trong một phiên, **chưa đạt mức độc lập giữa người viết oracle và người viết DP** theo kế hoạch TV1/TV4.

DP mẫu vẫn liệt kê hình học bên ngoài, nên có hệ số `q^n`. Kết quả không xác minh cận trạng thái theo `w`, `f`, `P` của bộ giải dự kiến và không chứng minh khả năng mở rộng đến từ dài. Bộ giải giữ biên tương tác cần được triển khai/kiểm chứng riêng trong giai đoạn thực hiện.

### 5.3. Baseline phân tầng mẫu

Baseline chọn một tổ hợp hình học khả thi theo optimum của thân chữ, rồi tối ưu lịch dấu với hình học đó. Baseline và đồng tối ưu dùng cùng tập ứng viên, luật khả thi và chi phí cuối. Đây là ablation **body-first** nhỏ, không phải B1/B2 production và chưa bao gồm mọi cách phân tầng mạnh hơn.

## 6. Kết quả đã chạy

- Tổng 56 cấu hình; 52 khả thi, 4 vô nghiệm.
- Vét cạn liệt kê tổng 788 lịch khả thi, giữ lịch đại diện và bộ hệ số trong JSON.
- 1.400 so sánh DP–vét cạn = **56 cấu hình × 25 điểm `(ρ,λ)`**: 1.300 so sánh giá trị hữu hạn và 100 xác nhận vô nghiệm; **0 mismatch**; sai số tuyệt đối lớn nhất `1.4210854715202004e-14`. Không phải 1.400 mẫu độc lập.
- 22.932 điểm nội miền được kiểm tra lại regret cho lịch chọn ở trung tâm; giá trị lớn nhất trên lưới khớp cận đỉnh trong phép thử (`max_vertex_dense_error=0`). Lưới là kiểm tra triển khai bổ sung; chứng minh nằm ở §4.3.
- 12 kiểm tra điều kiện/ca biên đều qua: bằng điểm; không có lịch tối ưu chung; thiếu ứng viên; khả thi phụ thuộc tham số; sai số mô hình `2δ`; nghiệm minimax không thắng tại điểm nào; dưới sàn; đúng sàn; giao cắt; tương tác xa; deadline `k=0/1`; tiếp xúc tại đầu nối so với chồng lấn bridge/thân.
- 35 cấu hình đổi bộ hệ số tối ưu khi quét tham số, gồm **6/16 cấu hình glyph thực**. Ở 16 cấu hình glyph thực, tổ hợp hình học thắng vẫn cố định; thay đổi ở lịch/nối/nâng. Không được diễn giải thành 6 từ độc lập hay suy diễn tỷ lệ dân số/corpus.
- Đồng tối ưu có gap dương tại ít nhất một điểm lưới trên **25/40 ca tổng hợp**, gap lớn nhất khoảng `0.841606` đơn vị `J` (mm tương đương). Bốn ca vô nghiệm nằm trong mẫu số 40; trong 36 ca tổng hợp khả thi, có 25 ca có gap dương. Đây là mô tả tập exploration, chưa là ước lượng tần suất lợi ích trên ngôn ngữ/glyph thực.
- **16/16 cấu hình glyph thực cho chi phí bằng nhau giữa hai phương pháp tại 25 điểm lưới đã chạy**, trong tolerance số. Không suy ra hai phương pháp bằng nhau tại mọi điểm ngoài lưới hoặc trên mọi glyph.
- Chọn minimax không cải thiện regret so với chọn trung tâm trên 16 cấu hình glyph thực này. Có cải thiện nhỏ ở một số ca tổng hợp; chưa đủ làm kết quả chính.

Các con số trên là descriptive cho tập exploration. Không có kiểm định thống kê, không có kết luận H1, không phải E1 mới hay PR3 exit sign-off.

## 7. Phần chưa được kiểm chứng

1. Lợi ích của đồng tối ưu trên corpus glyph thực rộng hơn và baseline phân tầng mạnh hơn.
2. Bộ giải dùng biên tương tác và dấu chờ, cận kích thước trạng thái, khả năng mở rộng.
3. Miền tham số và mô hình sai số lấy từ thiết bị; quy tắc đo tạo confidence set có coverage phù hợp.
4. Chọn phép đo chủ động, chi phí đo và mức tiết kiệm mẫu. **Chưa chạy thí nghiệm hiệu chuẩn chủ động:** dựng quan sát giả định quá đơn giản có thể tạo lợi ích giả và không giải quyết overlap với tài liệu.
5. Hình dạng chữ, vị trí dấu và chất lượng đọc của các ứng viên mới. Khoảng hở hợp lệ chưa bảo đảm chất lượng chữ.
6. Phạm vi Writer Profile, font thiết kế và máy thật: vẫn cần protocol và đánh giá riêng.

Việc chưa có số đo thiết bị không ngăn các kiểm tra phần mềm trên giả thiết công khai. Tuy nhiên, nó giới hạn mọi phát biểu về thời gian vật lý và hiệu chuẩn.

## 8. Phạm vi nên đăng ký khi còn ba ngày

### Bắt buộc

- Xây mô hình đồng tối ưu có ràng buộc hình học và cửa sổ dấu chờ; phân tích khi nào phân tầng có thể mất nghiệm tốt hơn.
- Thiết kế bộ giải chính xác trong phạm vi được định nghĩa; dùng oracle độc lập và heuristic mạnh để kiểm chứng/đối chứng.
- Phân tích độ nhạy theo `(ρ,λ)`; cố định điểm vận hành, lựa chọn tie và protocol trước HOLDOUT.
- Đánh giá xem đồng tối ưu có lợi trong những cấu trúc/miền tham số nào. Đăng ký một câu hỏi có thể cho kết quả âm; không hứa luôn vượt phân tầng hoặc đạt đồng thời mọi ngưỡng cũ.

### Bổ sung vào phương pháp với giả thiết rõ

- Chứng nhận regret cho một lịch trong miền tham số bằng oracle ở các đỉnh.
- Dùng cận dưới khi oracle có giới hạn thời gian, ghi rõ mức chứng nhận.
- Đánh giá thời gian tính chứng nhận và độ hữu ích của nó; tính chất lồi chuẩn được trình bày như cơ sở phương pháp.

### Mở rộng có điều kiện

- Hiệu chuẩn theo quyết định sau khi khóa mô hình đo và tìm được cải tiến cụ thể so với transductive/combinatorial pure exploration hoặc các baseline tương ứng.
- Pareto khoảng hở và cắt tỉa, dữ liệu thứ tự nét online, kiểm chứng vật lý; RQ4/RQ5 tiếp tục là thí điểm.

### Đoạn mô tả có thể đưa vào đề cương

> Nghiên cứu xây dựng mô hình đồng tối ưu lựa chọn hình học chữ và lịch thực hiện nét phụ/dấu tiếng Việt dưới các ràng buộc khoảng hở và giới hạn trì hoãn. Phương pháp dự kiến khai thác cấu trúc tương tác cục bộ để giải bài toán trong phạm vi xác định, được kiểm chứng bằng vét cạn độc lập và đối chiếu với phương pháp phân tầng cùng heuristic tìm kiếm. Độ nhạy theo tham số chuyển động và chứng nhận mức kém tối ưu trong miền tham số được khảo sát để đánh giá sự ổn định của quyết định. Hiệu chuẩn chủ động theo quyết định được xem xét như hướng mở rộng khi mô hình đo và lợi ích so với phương pháp hiện có được xác lập.

## 9. Việc cần thành viên khác review

- **TV2 — Trần Hồng Khải:** review độc lập các giả thiết §4, ánh xạ với Fiez 2019/Du 2021, điều kiện cận dưới và đơn vị regret; xác nhận đây chưa phải sign-off thuật toán đầy đủ.
- **TV1:** xây oracle độc lập từ đặc tả sau khi khóa mô hình; xác nhận quy tắc tách nét/dấu, phạm vi dữ liệu DEV, và không sử dụng bộ thử ở đây như corpus đánh giá chính thức.
- **TV3:** trong giai đoạn thực hiện, xác định phép đo `v_down`, `v_up`, `τ` và sai số mô hình. Review tài liệu này không yêu cầu sửa code hardware ngay.
- **TV4:** chủ trì mô hình đồng tối ưu, core solver và integration; phát triển ví dụ glyph thực có gap hoặc giải thích miền mà phân tầng đã đủ tốt.

Các mục trên là đề xuất review; chưa gửi thông điệp cho các thành viên và chưa thay đổi ownership đã thống nhất.

## 10. Tái lập và giới hạn provenance

Chạy từ repo root:

```sh
backend/venv/bin/python3 scripts/research_parametric_preflight.py
```

Chương trình tự xuất ba file evidence vào thư mục của đợt preflight. Seed, cấu hình, phiên bản Python, commit và SHA-256 các nguồn được lưu trong `summary.json`; mã và font ở working tree mới là đầu vào thực tế. Commit `c1b4696` được ghi làm mốc; không suy ra working tree sạch hoặc đồng nhất với commit.

Các nhóm ca, tham số và lịch được ghi đầy đủ trong JSON/CSV. `elapsed_seconds` thay đổi giữa các lần chạy và chưa được dùng làm benchmark tốc độ. Hai bộ giải dùng chung checker hình học nên một lỗi ở checker có thể tác động cả hai; các ca biên giảm rủi ro đó nhưng không thay thế review độc lập.

**Verdict cuối:** `PASS_SMALL_MODEL_CORRECTNESS`; `NOVELTY_NOT_ESTABLISHED_FOR_ACTIVE_CALIBRATION`; `REAL_GLYPH_ADVANTAGE_NOT_ESTABLISHED`; đề cương đủ cơ sở đăng ký hướng đồng tối ưu như câu hỏi nghiên cứu có kiểm chứng, với chứng nhận có điều kiện và hiệu chuẩn chủ động là mở rộng.
