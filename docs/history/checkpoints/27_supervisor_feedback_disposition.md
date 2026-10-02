> **HISTORICAL_RECORD — không là đặc tả hiện hành.** Đọc [hướng hiện tại](../../README.md), [contract](../../31_joint_solver_contract.md) và [công việc](../../03_current-task.md). Giữ kết luận đúng phạm vi/commit gốc.

<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** Tài liệu hỗ trợ được chuyển phạm vi. Phần hiện hành là kế hoạch/contract được dẫn dưới đây; các ID RQ, mốc thời gian và giả thuyết khác trong phần nội dung trước cập nhật chỉ áp dụng cho giai đoạn cũ.
> Kế hoạch hiện hành: [Docs 30](../../30_research_development_plan.md); đặc tả [Docs 31](../../31_joint_solver_contract.md) và [Docs 32](../../32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

## Cập nhật trạng thái phê duyệt hướng

Ngày 02/10/2026, TV4 thông báo GVHD đã đồng ý hướng đề tài. Chỉ ghi nhận phạm vi này; không quy các phản biện nhập vai trước đó thành phát biểu thật của GVHD. Contract solver/API chi tiết, epsilon/cỡ mẫu/điểm vận hành và ownership nhận việc còn cần review/khóa tương ứng.

Các quyết định được mã hóa ở Docs 30–32: một bảng 8 tháng, oracle độc lập TV3 và custody fallback TV2, H_ref/H_geom, lịch khả thi/boundary, top-m budget/incomplete, tie theo giá trị, một fontpilot và cắt phạm vi khi trượt tháng 3. Đây là quyết định kế hoạch nhóm, chưa là bằng chứng thực nghiệm.



# Quyết định thiết kế của nhóm sau phản biện mô phỏng

## Material Passport

- Ngày: 01/10/2026. Nguồn: trao đổi trong hội thoại và phản biện mô phỏng vai GVHD; không phải ý kiến hoặc phê duyệt của thầy/cô thật.
- Các điều chỉnh dưới đây là quyết định thiết kế/đề xuất của nhóm do TV4 ghi nhận. Chỉ bổ sung ý kiến GVHD thật khi có nguồn trực tiếp được xác nhận; hiện chưa có xác nhận đó cho các đoạn nhập vai.
- Loại: điều chỉnh thiết kế nghiên cứu và kế hoạch; không phải kết quả đánh giá mới.
- Trạng thái: `PLAN_REVISED; PARAMETERS_AND_TEAM_ASSIGNMENT_PENDING`.
- Bằng chứng đã kiểm tra: danh sách cấu hình trong script preflight và khai báo corpus; chưa chạy lại thí nghiệm hoặc chạy HOLDOUT.
- Tiến độ duy nhất cho hướng mới: [Docs 26](26_teacher_discussion_and_8_month_plan.md). Preflight lịch sử: [Docs 25](25_joint_parametric_preflight_review.md).
- Nhóm chọn font vì gắn trực tiếp với tập ứng viên hình học; TV1 và TV4 được đề xuất đồng chủ trì thí điểm font. Writer Profile hoãn. Pareto/cắt tỉa mở rộng hoãn khỏi cam kết kỳ này để tập trung lõi.

## 1. Chuyển phản biện mô phỏng thành yêu cầu thiết kế của nhóm

| Góp ý | Điều chỉnh | Owner / hạn | Trạng thái |
|---|---|---|---|
| Nếu HOLDOUT bằng nhau, còn đóng góp gì? | Đăng ký trước câu hỏi điều kiện lợi ích, điều kiện bằng nhau và chi phí của chứng nhận; không dùng vượt trội trên glyph thật làm điều kiện duy nhất để đề tài có kết quả | TV4 + TV2, tháng 1 đặc tả; tháng 3 lập luận cơ bản | Đã ghi phương án; chưa có chứng minh chuyên biệt cho glyph |
| Dấu chồng trong 16 cấu hình? | Đã có `ẫ`, `ế`, `ệ`; bổ sung coverage DEV trước kết luận rộng | TV1 manifest; TV4 mô hình; TV3 kiểm tra, tháng 1–2 | Đã kiểm tra danh sách; đợt bổ sung chưa chạy |
| Lợi ích/không lợi ích phải bắt buộc | Chuyển khỏi mục nếu còn thời gian sang lõi | TV4 + TV2, tháng 3 | Đã sửa kế hoạch |
| So với Balas | Đọc toàn văn cả hai bài, lập bảng bài toán/trạng thái/chi phí/giả thiết và số trang, phân biệt kế thừa với thích nghi | TV2 chủ trì, TV4 đối chiếu, tháng 1 | PENDING_FULL_TEXT_READING; hiện mới kiểm tra abstract; nhận định về giới hạn riêng từng thành phố chưa kiểm chứng toàn văn |
| Chứng nhận bằng đỉnh | Phát biểu trong tập ứng viên cố định, minh chứng §4 | TV4; TV2 review, tháng 3 | Lập luận đã ghi; review độc lập còn pending |
| Hai người quá tải | TV4 giữ mô hình/DP; TV2 giữ runner/baseline/phân tích; TV3 oracle độc lập/QA và đo; TV1 corpus/HOLDOUT | Cả nhóm xác nhận tháng 1 | Phân công đề xuất, chưa phải cam kết của các thành viên khác |
| Chỉ một thí điểm | Giữ font RQ5; hoãn Writer Profile và Pareto/cắt tỉa mở rộng | TV1 + TV4 đồng chủ trì font | Đã sửa lịch; không xóa tài liệu/mã cũ |
| HOLDOUT và tương đương | §3 phân biệt benchmark hữu hạn và suy luận quần thể; khóa biên trước mở dữ liệu | TV1 dữ liệu; TV2 metric; GVHD chốt biên | Quy trình có; giá trị biên chưa khóa |
| Nguồn điểm vận hành | Ưu tiên đo; DEV là fallback công khai, chưa có giá trị được duyệt | TV3 số đo; TV2 protocol; TV4 khóa, tháng 3 | PENDING |
| Không có gia tốc | Gọi thời gian ước tính theo mô hình; số đo máy báo cáo riêng | Cả nhóm | Đã sửa cách gọi trong kế hoạch |

## 2. Phương án nếu không có lợi ích trên HOLDOUT

Câu hỏi đăng ký là **khi nào việc chọn hình học và lịch nét cùng nhau tạo lợi ích**, không đăng ký kết luận chắc chắn luôn tốt hơn. Các sản phẩm bắt buộc dù kết quả HOLDOUT bằng nhau:

1. Mô hình hữu hạn có lựa chọn glyph/dấu, tương tác khoảng hở, pen pose và cửa sổ dấu chờ; bộ giải chính xác được kiểm chứng trên phạm vi đã định nghĩa.
2. Đối chứng phân tầng trong cùng tập ứng viên, cùng ràng buộc và cùng chi phí; beam search đánh giá tốc độ và khoảng cách tối ưu. Bộ giải chính xác cung cấp chứng nhận, có thể không thắng heuristic về chất lượng.
3. Điều kiện đủ cho bằng nhau và một họ ví dụ hình học tham số hóa có chênh lệch nghiêm ngặt. Họ tổng hợp minh họa tồn tại, không chứng minh tần suất lợi ích trên tiếng Việt. Ánh xạ sang glyph thật là việc phải khảo sát, không hứa luôn tìm được.
4. Đánh giá trường hợp thật có/không có tương tác, ổn định theo `(ρ,λ)`, và chi phí tính toán để biết khi nào đáng dùng bộ giải đồng tối ưu.
5. Chứng nhận regret cho một lịch cố định trong miền tham số và trong tập ứng viên đã khóa; gói dữ liệu/mã để tái lập.

**Lập luận nền:** nếu phương pháp phân tầng xuất một lịch khả thi thuộc tập lịch của bộ giải đồng tối ưu, optimum đồng tối ưu không lớn hơn chi phí lịch đó. Không được áp dụng nếu hai cách dùng tập ứng viên hoặc ràng buộc khác nhau.

**Điều kiện đủ đơn giản để bằng nhau:** nếu tập khả thi là tích `G × S`, lịch hợp lệ không phụ thuộc hình học, và `C(g,s)=A(g)+B(s)`, chọn `g` tối thiểu hóa `A` rồi chọn `s` tối thiểu hóa `B` đạt đúng optimum chung. Điều này là kết quả chuẩn về tính tách được, không tự nhận là định lý mới. Trong glyph thật, khả thi và chuyển tiếp thường phụ thuộc hình học; phải kiểm tra giả thiết trước khi dùng điều kiện này để giải thích kết quả.

Nếu chỉ có các kết quả chuẩn được thích nghi mà chưa tìm được đóng góp chuyên biệt có ý nghĩa, nhóm phải báo GVHD để thu hẹp/đổi câu hỏi; tính đúng của phần mềm và một kết quả bằng nhau đơn lẻ chưa đủ để tuyên bố tính mới học thuật.

## 3. Dữ liệu và tiêu chí bằng nhau / không có lợi ích đáng kể về thực dụng

### 3.1. Quy mô và coverage

Repo hiện khai báo **20 từ HOLDOUT**. Hai font và bốn seed tạo 160 lượt chạy mỗi phương pháp trong benchmark cũ, không phải 160 từ độc lập. Phải kiểm tra xem seed còn tác động gì trong bộ giải mới trước khi giữ thiết kế lặp; nếu thuật toán xác định và hình học đã khóa thì các lượt giống nhau không tăng bằng chứng.

**Nhóm quyết định coi 20 từ cũ là có nguy cơ nhiễm vì chúng đã nằm trong repo, và chỉ dùng làm tập bổ sung**, không dùng làm HOLDOUT chính cho hướng mới. Việc này không phụ thuộc nhóm có chứng minh đã tinh chỉnh trên chúng hay không.

TV1 phải lập split mới trong tháng 1–2, trước tháng 4: xác định nguồn, tiêu chí chọn, coverage dấu chồng/độ dài, loại trùng với DEV và các ca exploration theo quy tắc định trước; khóa manifest/hash và nhật ký ai truy cập, vào lúc nào, mục đích gì. Cỡ mẫu của split mới là **PENDING**, đề xuất cuối tháng 1 theo mục tiêu hữu hạn hoặc suy luận đã đăng ký; không gọi split mới là 20 từ hay 160 lượt khi chưa xây xong. TV1 giữ nội dung đánh giá ngoài vùng tinh chỉnh của người viết solver, nhóm chỉ xem thống kê coverage cần thiết trước khóa. Chỉ mở để chạy cấu hình đóng băng sau gate tháng 3. Ghi version và lý do thay split công khai; không chọn từ vì đã biết gap của chúng.

Preflight cũ: `vẫy`, `iế`, `ướ`, `yệ` × hai font × `k=0,1` = 16 cấu hình. Dấu mũ + thanh có ở `ẫ`, `ế`, `ệ`; `ướ` có dấu móc và thanh sắc. Coverage chưa có đầy đủ huyền/hỏi trên mũ hoặc `ượ`. Không coi bốn mẫu là đại diện cho toàn bộ tiếng Việt.

**Đợt DEV bổ sung cần khóa manifest trước khi chạy:** tối thiểu nhóm mũ + năm thanh (`ế/ề/ể/ễ/ệ`), móc + năm thanh (`ớ/ờ/ở/ỡ/ợ`, `ứ/ừ/ử/ữ/ự`) và hai nguyên âm có móc cạnh nhau như `ướ/ượ`; thêm nhóm `ă/â` với thanh nếu engine hỗ trợ. Đặt trong ngữ cảnh hai–ba chữ có tương tác, không chỉ glyph đứng riêng. Ghi mẫu là từ thật hay đoạn thử, font, ứng viên, cửa sổ, ID dấu và kiểu tiếp xúc hợp lệ. Đánh giá cả va chạm/vô nghiệm và giới hạn biểu diễn; không nới ràng buộc để tạo gap dương. Ca sinh mới là DEV/exploration, không thêm vào HOLDOUT đã khóa.

### 3.2. Đại lượng và biên

Với mỗi cặp khả thi cùng cấu hình tại điểm vận hành đã khóa:

`g = (J_staged − J_joint) / J_staged` khi `J_staged > 0`.

Báo cáo cả chênh lệch tuyệt đối theo đơn vị `J` (mm tương đương), `L_down`, `L_up`, `N_cycle`, khoảng hở và thời gian giải. Ca mẫu số 0, vô nghiệm hoặc timeout tách riêng; không quy thành gap 0. Nếu exact chưa được chứng nhận, ghi cận thay vì gán giá trị tối ưu.

- **Bằng nhau về số trên tập hữu hạn:** từng cặp có chênh lệch trong tolerance tuyệt đối/tương đối đã đăng ký; tolerance số không phải biên lợi ích thực dụng.
- **Không có lợi ích thực dụng trên benchmark này:** đề xuất tiêu chí bảo thủ `max g ≤ ε_eq` trên toàn bộ cặp khả thi đã định trước, kèm mọi ca thiếu kết quả. Báo cáo cả trung bình và lớn nhất, không che nhóm dấu chồng bằng trung bình toàn tập.
- **`ε_eq` còn PENDING_GVHD:** chọn theo mức lợi ích tối thiểu đáng trả chi phí bộ giải và sai số mô hình có căn cứ, TV2 và TV3 đề xuất giá trị/căn cứ trong tháng 1, GVHD duyệt trước khóa; không chọn theo kết quả HOLDOUT. Căn cứ gồm chi phí chạy solver và sai số thời gian mô hình nếu đã đo được máy. Nếu thiếu máy, ghi rõ phần sai số chưa biết, không bịa sai số vật lý. Một ngưỡng như 1% chỉ được dùng nếu có lý do và được chốt, hiện chưa mặc định 1%.
- **Kết luận quần thể:** tập cũ 20 từ chọn có chủ ý chưa đủ để khẳng định tương đương trên toàn bộ tiếng Việt. Nếu muốn suy luận thống kê, cần xác định quần thể/cách lấy mẫu, đơn vị độc lập là từ, biên, mức tin cậy và cỡ mẫu bằng DEV hoặc mô phỏng trước đánh giá. Khi kiểm định tương đương, khoảng tin cậy phải nằm trong biên đăng ký; `p > 0,05` của phép kiểm khác biệt không đủ.
- Nếu khoảng tin cậy còn vượt biên hoặc coverage thiếu, kết luận **chưa đủ bằng chứng**, không kết luận không có lợi ích. Không dùng bootstrap suy biến của toàn gap 0 làm bảo đảm tổng quát cho corpus mới.

**Trạng thái nguồn thống kê:** bỏ tham chiếu CONSORT khỏi bản đề xuất hiện hành vì phiên trước chưa ghi nhận đọc đầy đủ nội dung liên quan. TV2 phải đọc và ghi phạm vi đọc của một tài liệu thống kê về tương đương trước khi dùng làm nguồn chính thức. Quy tắc benchmark hữu hạn ở trên là định nghĩa vận hành nhóm đề xuất, không được trình bày thành một kiểm định thống kê đã được nguồn xác nhận. Phương án suy luận thống kê và cỡ mẫu còn chờ thiết kế/duyệt.

## 4. Chứng minh ngắn cho chứng nhận bằng đỉnh

Gọi `Π` là tập hữu hạn cố định các lịch khả thi, chứa mọi ứng viên mà nhóm cho phép; `Ω` là đa diện lồi compact. Với mỗi lịch, `J_π(θ)` affine theo `θ=(ρ,λ)` và `V(θ)=min_{σ∈Π} J_σ(θ)`.

Với lịch cố định `π`, regret là:

`R_π(θ)=J_π(θ)−V(θ)=max_{σ∈Π}[J_π(θ)−J_σ(θ)]`.

Đây là maximum của các hàm affine, nên lồi. Nếu `θ=Σ a_i v_i` là tổ hợp lồi các đỉnh, `R_π(θ) ≤ Σ a_i R_π(v_i) ≤ max_i R_π(v_i)`. Vì các đỉnh thuộc `Ω`, suy ra `max_{θ∈Ω} R_π(θ)=max_i R_π(v_i)`.

Miền hình chữ nhật có bốn đỉnh: bốn giá trị tối ưu chính xác đủ chứng nhận regret của **một lịch cố định**. Không suy ra lịch minimax nằm trong bốn lịch thắng ở đỉnh. Nếu chỉ có cận dưới cho `V`, cận regret thu được là bảo thủ; nghiệm heuristic khả thi cho cận trên của `V` không thể thay oracle để chứng nhận an toàn.

Phạm vi: tập `Π` đã khóa, khả thi không đổi theo tham số. Không chứng nhận hình học liên tục chưa liệt kê, font bất kỳ hoặc thời gian máy thật. Sai số số học cần được xử lý trong triển khai; kiểm tra float với tolerance chưa phải chứng nhận bằng số học có bảo đảm.

## 5. Điểm vận hành và ranh giới thời gian

`T_hat=L_down/v_down + L_up/v_up + τ N_cycle`, `J=v_down T_hat`, `ρ=v_down/v_up`, `λ=v_down τ`.

Ưu tiên số đo thiết bị trước khóa cuối tháng 3. Nếu không có, TV2 viết quy trình chọn trên DEV trước khi chạy chọn tham số, ghi nguồn dải và tiêu chí; TV4 công bố rõ lựa chọn phụ thuộc DEV. Không tự ghi giả định là số đo nhà sản xuất nếu chưa có nguồn phù hợp cho đúng máy.

Chưa khóa giá trị `(ρ₀,λ₀)`; đây là việc phải hoàn tất trước đánh giá, không phải lỗi để dùng giá trị tùy ý. RQ1 cũ về quãng đường/lần nhấc là chỉ số phụ và ngưỡng lịch sử; nếu giữ làm nghiệm thu hướng mới, phải đăng ký cách chấm tại điểm vận hành và không suy ra tối ưu `J` bảo đảm đạt cả ba ngưỡng.

Mô hình chưa có gia tốc, jerk và sai số điều khiển. Tên chỉ số là **thời gian ước tính theo mô hình**. Thời gian thực thi đo trên máy là chỉ số riêng, kèm thiết bị và protocol. Sau mở HOLDOUT không đổi điểm vận hành, sàn `c_min=0,20 mm`, ứng viên, mã hoặc quy tắc tie cho thí nghiệm đã khóa.

## 6. Việc cần làm trước khi nộp đề cương

1. Đồng bộ bản đề cương nộp: một bảng 8 tháng, lý thuyết lợi ích/bằng nhau bắt buộc, một pilot font, thuật ngữ thời gian và ownership theo Docs 26.
2. Gửi GVHD phương án kết quả bằng nhau và xin thống nhất tiêu chí/biên thực dụng; không nói biên đã khóa khi còn pending.
3. Ghi rõ tháng 1 phải đọc đầy đủ hai bài Balas; không tuyên bố đã đọc toàn văn khi hiện chỉ xác minh abstract.
4. Nhóm xác nhận TV3 có thể nhận oracle độc lập và TV2 runner; TV4 giữ đóng góp phương pháp/DP, không giữ mọi đầu việc vận hành.
5. Khóa manifest đợt DEV dấu chồng rồi mới chạy; giữ nguyên bằng chứng 0/16 cũ. Chưa mở HOLDOUT trong giai đoạn chuẩn bị đề cương.

Không cần hoàn thành DP mới hay có lợi ích glyph thật trong ba ngày nộp đề cương. Cần chốt một kế hoạch có giả thuyết kiểm được, giới hạn trung thực và phương án kết quả bằng nhau đủ rõ để GVHD đánh giá.

## 7. Baseline phân tầng top-m — đề xuất phải đăng ký trước

### 7.1. Cùng bài toán, khác quy tắc chọn hình học

Gọi `G` là toàn bộ cấu hình hình học hoàn chỉnh trong tập ứng viên đã khóa (không phải top-m ứng viên riêng lẻ của từng chữ). Với mỗi `g`, `S(g)` chứa các lịch thỏa cùng cửa sổ, khoảng hở và quy tắc nối/nâng. Đặt `F(g;θ)=min_{s∈S(g)} J(g,s;θ)`; nếu không có lịch hợp lệ thì `F=+∞`.

**Quy tắc xếp hạng chính đề xuất (H_ref):** tạo lịch tham chiếu xác định cho từng `g`: thân theo thứ tự trái sang phải, mỗi nét phụ/dấu ngay sau thân sở hữu, thứ tự nét nội bộ/ID dấu cố định; nâng giữa các nét, cùng home và quy ước chu kỳ với bộ giải chung. Dùng `H(g)=J(g,s_ref(g);θ₀)` để xếp hình học tại điểm vận hành đã khóa. Tiêu chí này xét đầy đủ thân, dấu, khoảng cách chuyển và nâng/hạ, không chỉ chiều dài thân; không chạy tối ưu lịch khi xếp hạng. Nếu mô hình không cho phép lịch tham chiếu này, không tự loại hình học có thể còn lịch khác: xếp `H=+∞` và giữ ở cuối. Tie theo ID cấu hình, khóa trước thí nghiệm. Cần TV2/GVHD duyệt quy tắc này trong tháng 1, hiện chưa là baseline đã sign-off.

**Quy tắc thứ hai chỉ nhìn hình học (H_geom), đăng ký cùng quy tắc chính:** xếp cấu hình theo độ lệch hình học so với mẫu tham chiếu của font đã chọn. Chuẩn hóa cùng cỡ chữ và khung bố trí, nhưng giữ vị trí dấu tương đối so với thân; với các nét có ID tương ứng, lấy 32 điểm cách đều theo độ dài cung, tính trung bình bình phương khoảng cách tới nét tham chiếu, rồi lấy trung bình theo nét để tránh nét nhiều điểm lấn át. Mẫu tham chiếu, ánh xạ ID nét, xử lý nét suy biến và ngoại lệ được khóa trước thử nghiệm. Nếu thiếu tương ứng, ghi chưa biểu diễn được, xếp cuối bằng tie ID thay vì âm thầm bỏ ứng viên. Tiêu chí không dùng lịch vẽ, home, quãng di chuyển nâng bút, thời gian hoặc `(ρ,λ)`; cùng các ràng buộc khả thi vẫn được áp dụng ở bước giải lịch. Đây là proxy độ trung thành hình học, chưa phải thang đo thẩm mỹ đã xác thực. Nếu font được chọn theo sở thích người dùng, giữ font cố định trước so sánh, không coi H_geom là mô hình chọn font của con người.

Báo hai họ top-m **riêng biệt** theo H_ref và H_geom; không chọn họ có gap lớn hơn trên HOLDOUT để làm kết quả chính. H_ref là đối chứng có xét chi phí chuyển động qua lịch cố định, vì vậy m=1 chỉ là prefix nhỏ nhất trong họ này, không gọi là phân tầng yếu nói chung. Các thông số hình học nêu trên là đề xuất cần review và khóa trong tháng 1, chưa phải kết quả đã chạy.

Trong khảo sát độ nhạy, giữ nguyên thứ hạng tại `θ₀` cho baseline chính để phản ánh quyết định hình học đã khóa; nếu thêm baseline xếp lại theo `θ`, báo cáo thành đối chứng khác với quy tắc riêng, không trộn hai đường cong.

Lấy prefix `G_m` gồm m hình học theo thứ hạng đó và tính:

`J_m(θ)=min_{g∈G_m} F(g;θ)`, `J_joint(θ)=min_{g∈G} F(g;θ)`.

- `m=1`: phân tầng chọn một hình học rồi tối ưu lịch chính xác.
- `m=|G|`: liệt kê mọi hình học rồi tối ưu lịch chính xác cho từng cái, tương đương đồng tối ưu về giá trị; đây là kiểm tra tính đúng và chi phí thuật toán, không phải baseline để tuyên bố gap dương.
- Khi các prefix lồng nhau và lịch được giải chính xác: `J_joint ≤ J_(m+1) ≤ J_m`; tại toàn bộ hình học phải bằng nhau trong tolerance. Nếu không, điều tra khác tập/ràng buộc hoặc lỗi triển khai.

Với ca nhỏ, chạy mọi `m=1..|G|`. Với ca lớn, đăng ký các m `1,2,4,8,...` và `|G|` nếu hoàn thành được; nếu điểm cuối timeout thì không gán bằng nhau hay gọi đó là optimum. Báo cáo số cấu hình `|G|`, chi phí sinh/xếp hạng, giải lịch, bộ nhớ và timeout. Nếu top-m không có lịch khả thi, báo `NO_FEASIBLE_IN_PREFIX`, không gán gap 0 hoặc tự tăng m. Chỉ tuyên bố toàn bài toán vô nghiệm khi đã chứng nhận hết tập.

Báo cáo đường cong gap theo m, thời gian tổng và m nhỏ nhất đạt biên `ε_eq`. Đại lượng này trả lời cần giữ bao nhiêu hình học để phân tầng đủ tốt. Các m dùng để đánh giá theo protocol, không dùng HOLDOUT để chọn lại m triển khai. Nếu quy tắc xếp hạng khác được khảo sát trên DEV, phải công bố mọi quy tắc và khóa baseline chính trước HOLDOUT.

Các baseline mẫu body-first của preflight cũ chỉ là exploration; không đổi tên chúng thành baseline top-m mới hoặc diễn giải 25/40 thành kết quả trên quy tắc mới.

## 8. Oracle độc lập, nguồn đọc và phương án cắt khi trượt mốc

### 8.1. Gate xác nhận người viết oracle

Cuối tuần đầu tháng 1, TV3 xác nhận có thể nhận oracle; chưa có xác nhận trong phiên này. Trước khi công nhận oracle độc lập, phải có:

- Truy hồi/duyệt lịch, tính chi phí và xác định khả thi từ đặc tả, không dùng solver hoặc cache kết quả solver.
- Primitive khoảng cách đoạn–đoạn, giao cắt/chồng lấn, khoảng hở dấu–thân/dấu–dấu và ngoại lệ tiếp xúc hợp lệ được viết độc lập hoặc đối chiếu bằng một triển khai độc lập có nguồn/phiên bản. Không nhập checker production rồi gọi là độc lập.
- Bộ ca chuẩn có giá trị kiểm tay/đối chiếu: khoảng cách dưới/đúng/trên 0,20 mm, đoạn suy biến, đầu nối, chồng lấn, giao cắt, tương tác không kề; ghi quy ước tolerance và cách phân loại.
- Nhật ký nguồn/phần dùng chung: chỉ chia sẻ schema đầu vào và hình học thô, không chia sẻ kết luận khả thi. TV2 review primitive và các lịch minh họa; TV1 kiểm tra manifest đầu vào. Mọi bất đồng DP–oracle phải tìm nguyên nhân, không chọn kết quả có lợi.

Nếu TV3 không nhận được, đề xuất TV1 viết oracle; TV2 nhận custody split, nhật ký truy cập, thao tác khóa/mở dữ liệu và chuẩn bị lần chạy đánh giá bằng cấu hình đã khóa. TV1 bàn giao nguồn/manifest trước khi nhận oracle, không tự mở hoặc giữ HOLDOUT một mình. TV3 review primitive/QA theo khả năng; TV2 review đặc tả và lịch kiểm tay. TV1 chỉ đồng chủ trì font sau gate lõi; nếu oracle còn tồn đọng thì hoãn phần font, không dồn cả hai vào TV1. Phương án thay thế phải được nhóm xác nhận, với ít nhất người thứ hai đối chiếu hash và nhật ký khi mở dữ liệu. Nếu chưa có người/checker đủ độc lập, chưa được mở HOLDOUT với tuyên bố exact đã kiểm chứng. Không chuyển tác giả oracle sang TV4 là người viết DP.

### 8.2. Gate tài liệu cuối tháng 1

TV2 lập bảng so sánh Balas 1999/Balas–Simonetti 2001: bài toán gốc, quy tắc cửa sổ/precedence, giới hạn riêng từng thành phố bài nào xử lý, trạng thái/độ phức tạp, cấu hình điểm cuối, phạm vi kế thừa và phần tương tác glyph khác biệt. Mỗi hàng trích số trang/mục đúng phiên bản toàn văn, kèm nhật ký phần đã đọc. **Nhận định hiện có về giới hạn riêng từng thành phố chưa kiểm chứng toàn văn**, không ghi thành kết luận đã xác nhận trong đề cương.

### 8.3. Thứ tự ưu tiên và cắt phạm vi

- Tháng 1 chỉ khóa đặc tả tối thiểu, baseline top-m, đề xuất biên, nguồn đọc và quy tắc split mới; chuyển chạy coverage rộng/đo biên trạng thái sang tháng 2. TV4 + TV2 dựng họ ví dụ tham số hóa đơn giản từ tháng 2, trước mọi mở rộng.
- Pareto/cắt tỉa mở rộng và hiệu chuẩn chủ động hoãn khỏi cam kết kỳ này. Không triển khai chúng để cứu số liệu lợi ích hoặc song song trước gate lõi.
- Thứ tự giảm việc trong lõi nếu có nguy cơ trượt tháng 3: **(1)** cắt khảo sát w/b mở rộng trên nhiều font/ngữ cảnh, giữ một tập cấu trúc có manifest và cận bảo thủ đúng; **(2)** rút họ ví dụ lớn/ánh xạ sang glyph thật về một ví dụ tham số hóa có lợi kiểm chứng được và điều kiện đủ bằng nhau. Nếu ngay cả ví dụ tối thiểu chưa hoàn tất thì ghi thiếu sản phẩm, xin điều chỉnh phạm vi; không tuyên bố phần lý thuyết đã hoàn thành. Không cắt tính đúng DP–oracle, baseline công bằng, chứng minh chứng nhận hoặc nhật ký split.
- Nếu trượt cuối tháng 3: không mở HOLDOUT, không bắt đầu font; dừng mở rộng ứng viên/font/ngữ cảnh dài, giữ lõi trên phạm vi ngắn đã khai báo, sửa DP–oracle và thống nhất lịch mới với GVHD. Không cắt các gate độc lập, công bằng baseline hoặc log dữ liệu để kịp tiến độ.
- Font chỉ bắt đầu sau đánh giá lõi đủ tái lập; nếu mốc mới lấn tháng 6 thì hoãn pilot font thay vì rút thời gian báo cáo tháng 7–8. TV1 đồng chủ trì dữ liệu/giấy phép/chuẩn tham chiếu và đánh giá font; TV4 đồng chủ trì mô hình ứng viên/tích hợp, không nhận mọi đầu việc font.

## 9. Cách viết đóng góp trong đề cương

> Đề tài áp dụng và phân tích có kiểm soát các phương pháp quy hoạch động có ràng buộc thứ tự và chứng nhận dưới miền tham số cho mô hình chữ/dấu tiếng Việt. Đóng góp dự kiến tập trung vào mô hình lựa chọn hình học có tương tác dấu, cấu hình bút phụ thuộc lựa chọn, và quy trình đánh giá tái lập với đối chứng phân tầng top-m, oracle hình học độc lập và split đánh giá chưa dùng để tinh chỉnh. Nghiên cứu xác định điều kiện tạo lợi ích hoặc cho kết quả bằng nhau trong tập ứng viên đã khai báo, thay vì mặc định đề xuất một thuật toán mới hay cam kết vượt trội trên mọi chữ/font tiếng Việt.

Đây là mục tiêu đóng góp dự kiến; mức độ mới và giá trị học thuật thực tế phải được kiểm tra bằng đọc tài liệu đầy đủ và kết quả nghiên cứu.

## 10. Quyết định phạm vi bổ sung của nhóm

### 10.1. Cửa sổ và các phần ngoài cam kết

Cửa sổ không đồng nhất là cơ chế giới hạn tìm kiếm, không phải mô hình thói quen viết người đã được xác thực. Báo cáo tỷ lệ giữ optimum và chi phí tính toán so với cửa sổ đồng nhất rộng nhất trong cùng tập ứng viên; không dùng thay đổi tập nghiệm để tuyên bố tìm được optimum tốt hơn. Pareto và cắt tỉa mở rộng tiếp tục ngoài cam kết kỳ này.

### 10.2. Đo cấu trúc trên tập âm tiết

- **TV1:** chuẩn bị danh sách âm tiết có nguồn/quyền sử dụng, quy tắc NFC/NFD, loại trùng, dấu thanh và nhãn coverage; khóa manifest, hash và số lượng thực tế. Nếu chỉ sinh tổ hợp theo quy tắc, gọi là tập cấu trúc tổng hợp và phân biệt với âm tiết được nguồn từ vựng xác nhận. Chưa có tập được khóa hoặc số lượng đã xác minh trong phiên này.
- **TV4:** định nghĩa biên theo đồ thị tương tác hình học bảo thủ của các ứng viên và thứ tự xử lý thân. `w` là số chữ có lựa chọn hình học phải giữ tại biên để kiểm tra tương tác với phần chưa xử lý. `b` là số hành động nét phụ/dấu đã mở nhưng chưa thực hiện trong trạng thái hợp lệ; đơn vị là nét/hành động theo schema, không tự đồng nhất với số ký tự Unicode kết hợp.
- **TV2:** vận hành đo theo font, số ứng viên và cửa sổ; ghi `w_max` trên các biên và cận `b_max` theo deadline. Nếu liệt kê được mọi trạng thái hợp lệ thì ghi maximum chính xác; nếu chỉ quan sát trên đường chạy hoặc dùng cận tổ hợp, phải ghi loại số đo riêng, không gọi là maximum chính xác của toàn bộ không gian.
- **TV3:** kiểm tra độc lập các ca nhỏ và đồ thị tương tác, nhất là tiếp xúc hợp lệ/va chạm xa. Báo số trường hợp không biểu diễn được, không loại âm tiết khó khỏi mẫu mà không ghi lý do.
- Báo phân bố, quantile và maximum, cùng thời gian/số trạng thái/bộ nhớ thực đo. Tách ảnh hưởng font, ứng viên và `k`; liên hệ `w/b` với cận trạng thái đã chứng minh, không thay cận lý thuyết bằng phân bố thực nghiệm. Thực hiện tháng 2–3; không dùng lợi ích tối ưu trên HOLDOUT để chọn lại tập hoặc cấu hình.
- Tập âm tiết khảo sát cấu trúc không phải HOLDOUT đánh giá lợi ích. Ghi mức giao nhau; nếu cấu hình được chỉnh dựa trên một âm tiết thì không coi ca đó là chưa dùng để tinh chỉnh trong đánh giá chính.

### 10.3. Ba sản phẩm đánh giá bắt buộc

1. Đường gap và chi phí chạy theo m của baseline top-m: `m=1` giữ ít lựa chọn nhất trong họ đã khóa, không gọi là baseline yếu nhất trong mọi phương pháp; `m=|G|` tương đương giá trị đồng tối ưu khi đều giải chính xác.
2. Phân bố độ rộng biên và số nét chờ trên tập âm tiết có manifest, làm bằng chứng thực nghiệm cho độ phức tạp trong phạm vi khảo sát.
3. Chứng nhận regret của lịch cố định bằng bốn đỉnh miền hình chữ nhật `(ρ,λ)`, với tập ứng viên/khả thi cố định và chi phí affine; đối chiếu oracle và báo giới hạn số học.

DP kế thừa nền tảng Balas, chứng nhận đỉnh và điều kiện bằng nhau là các kết quả chuẩn được áp dụng. Cách gọi thống nhất là **áp dụng và phân tích có kiểm soát**; phần nghiên cứu của nhóm tập trung mô hình chữ/dấu tiếng Việt và quy trình đánh giá chặt, kể cả khi kết quả bằng nhau. Không tự nâng các mục này thành tuyên bố thuật toán mới.
