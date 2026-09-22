# Chương 1 — Mở đầu

**Bản thảo:** 0.1  
**Trạng thái:** `DRAFT — TEAM REVIEW PENDING`  
**Phạm vi:** Handwriting Mode / CA-VHC; chưa trình bày kết quả thực nghiệm OmniDraw  
**Tên đề tài làm việc:** *OmniDraw — Tối ưu hợp thành chữ viết tay tiếng Việt theo ngữ cảnh cho máy vẽ nét đơn*

> [!IMPORTANT]
> Chương này mô tả vấn đề nghiên cứu, mục tiêu, câu hỏi, phạm vi và đóng góp **dự kiến**. OmniDraw chưa có kết quả thực nghiệm chính thức cho RQ1–RQ3; vì vậy, mọi phát biểu về hiệu quả của CA-VHC đều là giả thuyết cần kiểm chứng, không phải kết luận.

## 1.1. Bối cảnh nghiên cứu

Chữ viết tay số có thể được biểu diễn như một chuỗi tọa độ cùng trạng thái bút, nhờ đó giữ được thứ tự nét và các chuyển động pen-down/pen-up mà ảnh raster không thể hiện trực tiếp [1]. Dạng biểu diễn này phù hợp với máy vẽ hai trục vì đầu ra của hệ thống không chỉ cần giống chữ viết tay về thị giác mà còn phải trở thành một quỹ đạo có thứ tự, có thể thi công bằng đầu bút. Các nghiên cứu về robot vẽ cũng cho thấy việc tạo hình và việc lập kế hoạch đường đi là hai bài toán liên quan nhưng khác nhau: một hình vẽ hợp lệ chưa chắc có thứ tự nét hiệu quả hoặc phù hợp với chuyển động của thiết bị [8]–[11].

Đối với tiếng Việt, bài toán phức tạp hơn do một ký tự hiển thị có thể gồm chữ cái cơ sở, dấu chữ cái và dấu thanh. Unicode cho phép biểu diễn ký tự dưới dạng dựng sẵn hoặc dưới dạng chuỗi ký tự cơ sở và combining marks; dạng chuẩn hóa NFD hỗ trợ phân rã canonical để hệ thống xử lý các thành phần này một cách nhất quán [4]. Tuy nhiên, phân rã mã ký tự không quyết định hình học của dấu, không xác định thời điểm vẽ dấu và cũng không bảo đảm rằng nét nối giữa hai chữ sẽ tránh vùng dấu.

Nghiên cứu về chữ viết tay trực tuyến tiếng Việt ghi nhận vai trò đáng kể của delayed strokes, tức các nét như dấu có thể được viết sau thân chữ hoặc sau một số ký tự kế tiếp [3]. Vì vậy, trong một hệ thống viết bằng máy, vị trí dấu, thứ tự vẽ dấu, lựa chọn biến thể thân chữ và quyết định nối hay nhấc bút cần được xem là các quyết định có quan hệ với nhau. Nếu từng quyết định được thực hiện riêng lẻ, một lựa chọn tốt ở bước trước có thể tạo ra va chạm hoặc quãng di chuyển không cần thiết ở bước sau.

Từ bối cảnh đó, OmniDraw được phát triển như một engine tạo quỹ đạo vector nét đơn từ văn bản, hướng đến đầu ra có thể kiểm tra bằng hình học và có thể chuyển giao cho máy vẽ. Trọng tâm nghiên cứu P0 không phải là tạo chữ viết tay bằng mô hình sinh học sâu, mà là xây dựng một phương pháp hợp thành chữ viết tay tiếng Việt theo ngữ cảnh, có trạng thái hữu hạn, hàm chi phí minh bạch và protocol đánh giá tái lập được.

## 1.2. Vấn đề nghiên cứu

Pipeline chữ viết tay hiện hành của OmniDraw đã có Font Pack, biến thể glyph theo ngữ cảnh, Trellis DAG và bộ sinh dấu. Tuy nhiên, audit kiến trúc tại [`06_audit_trellis_dag_report.md`](06_audit_trellis_dag_report.md) xác nhận bốn giới hạn chính:

1. Trellis hiện tại chỉ lựa chọn biến thể hình học của thân chữ; node chưa chứa ứng viên dấu.
2. Dấu tiếng Việt được sinh sau bước tối ưu DAG bằng anchor hoặc offset tĩnh.
3. Chi phí va chạm của bridge chưa xét vùng hình học của dấu.
4. Thứ tự delayed strokes chưa được tối ưu trong engine.

Do đó, pipeline có thể chọn một cặp biến thể thân chữ tạo bridge ngắn hoặc đẹp, nhưng bridge này lại cắt qua dấu được thêm ở hậu xử lý. Ngược lại, việc dịch dấu để tránh va chạm cục bộ có thể làm giảm độ rõ hoặc phá vỡ tính nhất quán của Font Pack. Cách sửa từng glyph hoặc từng trường hợp đặc biệt chỉ xử lý triệu chứng và khó mở rộng thành một phương pháp nghiên cứu có thể so sánh.

Trong typography, OpenType GPOS hỗ trợ neo dấu bằng các cơ chế MarkToBase, MarkToLigature và MarkToMark [5]. Các cơ chế đó cung cấp gợi ý quan trọng về metadata hình học, nhưng không tối ưu thứ tự đi bút, quãng đường pen-up hay khả năng bridge đi xuyên qua vùng dấu. Ở chiều ngược lại, các công trình robot vẽ thường tập trung vào contour, stroke ordering hoặc tối ưu path [8]–[11], nhưng không giải quyết đồng thời quy tắc đặt dấu tiếng Việt và biến thể thân chữ theo ngữ cảnh.

Tổng quan nguồn hạt giống ở [`13_chapter_2_literature_review.md`](13_chapter_2_literature_review.md) cho thấy các hướng liên quan hiện phân tán giữa tổng hợp chữ viết tay, layout font, tối ưu chuỗi trạng thái và robot vẽ. Trong phạm vi nguồn đã sàng lọc, nhóm chưa tìm thấy phương pháp đồng thời đưa allograph theo ngữ cảnh, ứng viên dấu tiếng Việt, vùng cản bridge và chi phí chuyển động vào một trellis hữu hạn cho máy vẽ nét đơn. Đây là **khoảng trống tạm thời**, chưa phải tuyên bố mới tuyệt đối; kết luận về tính mới chỉ được khóa sau citation chaining và cross-review theo [`11_literature_review_protocol.md`](11_literature_review_protocol.md).

Vấn đề nghiên cứu của đề tài được phát biểu như sau:

> Làm thế nào để đồng tối ưu lựa chọn biến thể glyph, cấu hình dấu tiếng Việt và chuyển động nối/nhấc bút theo ngữ cảnh, sao cho giảm chuyển động không vẽ và tránh va chạm hình học, đồng thời giữ chi phí tính toán hữu hạn và tạo quỹ đạo có thể kiểm chứng trên máy vẽ hai trục?

## 1.3. Mục tiêu nghiên cứu

### 1.3.1. Mục tiêu tổng quát

Đề xuất và đánh giá phương pháp **Context-Aware Vietnamese Handwriting Composition (CA-VHC)** cho OmniDraw, trong đó biến thể thân chữ và ứng viên dấu được biểu diễn trong một trạng thái hợp thành chung, sau đó lựa chọn bằng quy hoạch động Viterbi theo các tiêu chí về hình học, chuyển động và khả năng thi công.

### 1.3.2. Mục tiêu cụ thể

1. Xây dựng `CompositionState` kết hợp `GlyphVariant` và `DiacriticCandidate`, đồng thời giữ ranh giới rõ giữa chi phí nội tại của trạng thái và chi phí chuyển tiếp.
2. Đưa vùng cản dấu và kiểm tra bridge–diacritic collision vào quá trình lựa chọn chuỗi thay vì chỉ sửa ở hậu xử lý.
3. Xây dựng hàm mục tiêu có thể giải thích, đo riêng quãng đường pen-up, số lần nhấc bút, chiều dài nét tiếp xúc giấy, độ rõ, clearance, curvature và chi phí thi công.
4. Dùng Viterbi DP để tìm chuỗi trạng thái tốt nhất dưới giới hạn số ứng viên sau pruning, đồng thời bảo toàn hành vi tương thích đối với ký tự không dấu.
5. Thiết lập ba baseline B1, B2 và B3, corpus, seed, metric, runner và quy tắc PASS/FAIL/INCONCLUSIVE để đánh giá tái lập được.
6. Kiểm chứng đầu ra vector trên simulator và, sau khi hoàn tất hiệu chuẩn, trên máy vẽ hai trục bằng số đo vật lý tách biệt với thời gian xử lý phần mềm.

## 1.4. Câu hỏi nghiên cứu và giả thuyết

### 1.4.1. RQ1 — Nối nét và tối ưu chuyển động

**RQ1:** Việc dùng Viterbi DP trên `CompositionState` để đồng thời lựa chọn biến thể glyph và vị trí dấu theo ngữ cảnh có giảm quãng đường pen-up và số lần nhấc bút so với B1/B2/B3, trong khi vẫn kiểm soát tổng chiều dài nét tiếp xúc giấy hay không?

Các giả thuyết tương ứng là Proposed CA-VHC giảm `pen_lift_distance_mm` và `pen_lift_count`, trong khi mức tăng `total_path_length_mm` vẫn nằm trong ngưỡng đã khóa. B1 là static glyph renderer, B2 là greedy contextual heuristic và B3 là Trellis DAG hiện hành chưa có ràng buộc dấu nâng cao. Các ngưỡng nghiệm thu chi tiết được quản lý tại [`05_ca_vhc_research_spec.md`](05_ca_vhc_research_spec.md) và [`10_nckh_research_plan.md`](10_nckh_research_plan.md).

### 1.4.2. RQ2 — Tránh va chạm dấu tiếng Việt

**RQ2:** Việc đưa ứng viên dấu và vùng cản trở của dấu vào `CompositionState` và hàm mục tiêu Trellis có loại bỏ giao cắt bridge–diacritic và duy trì clearance tối thiểu tốt hơn B3 hay không?

Giả thuyết của RQ2 là CA-VHC đạt `collision_count = 0` trên tập nghiệm thu và cải thiện `minimum_diacritic_clearance_mm` so với B3. Ngưỡng clearance hiện là mục tiêu kỹ thuật provisional, chưa được xem là ngưỡng an toàn vật lý trước khi TV3 hoàn tất hiệu chuẩn thiết bị.

### 1.4.3. RQ3 — Hiệu năng và khả năng thi công

**RQ3:** Với $K_{raw} \le 9$, CA-VHC có duy trì chi phí tính toán trong giới hạn thiết kế và tạo quỹ đạo vector đủ khả thi để kiểm chứng trên máy vẽ hai trục hay không?

Giả thuyết của RQ3 là số trạng thái sau pruning đủ nhỏ để recurrence Viterbi vận hành ổn định trên corpus quy định, trong khi đầu ra thỏa bounds và các tiêu chí hình học cần thiết cho bước kiểm chứng vật lý. Kết luận về thời gian vẽ thực tế chỉ được đưa ra từ `actual_draw_time_sec` đo trên máy; thời gian sinh SVG hoặc thời gian giải thuật không được dùng thay thế.

| Câu hỏi | Tác động được kiểm tra | Đối chứng chính | Gate trước khi kết luận |
| :--- | :--- | :--- | :--- |
| RQ1 | Pen-up distance, pen-lift count, pen-down path | B1, B2, B3 | PR2, PR3, corpus freeze và PR5 |
| RQ2 | Collision count và minimum clearance | B3 | PR3 và calibration ngưỡng vật lý |
| RQ3 | Số trạng thái, thời gian giải, bounds và thi công | Giới hạn thiết kế + hardware validation | PR3, PR5 và TV3 calibration |

## 1.5. Đối tượng và phạm vi nghiên cứu

### 1.5.1. Đối tượng nghiên cứu

Đối tượng nghiên cứu là quá trình hợp thành quỹ đạo chữ viết tay tiếng Việt nét đơn từ văn bản Unicode, tập trung vào quan hệ giữa biến thể hình học của thân chữ, cấu hình dấu, nét nối, chuyển động pen-up và các giới hạn thi công của máy vẽ hai trục.

Đơn vị phân tích định lượng dự kiến là một lần chạy được xác định bởi bộ `(method, corpus_item, font, seed, run_index)`. Các phương pháp được so sánh trên cùng đầu vào và điều kiện kiểm soát để hạn chế việc quy khác biệt do corpus hoặc random seed cho thuật toán.

### 1.5.2. Phạm vi thực hiện P0

- Hai Font Pack hiện có: `oly` và `omni_casual`.
- Lựa chọn allograph, ứng viên dấu và quyết định nối/nhấc bút ở cấp từ.
- Phân tích Unicode NFD và quy tắc hình học chính tả; không suy diễn ngữ nghĩa hay ngữ âm học.
- Các metric về path, pen lift, collision, clearance, curvature, bounds và thời gian xử lý.
- So sánh B1/B2/B3/Proposed trên corpus, seed và số lần lặp được kiểm soát.
- Kiểm chứng phần mềm trước; kiểm chứng máy vẽ thật chỉ sau khi hoàn tất hiệu chuẩn phần cứng.

### 1.5.3. Ngoài phạm vi câu hỏi nghiên cứu hiện hành

- Writer Profile, few-shot personalization và mô phỏng thói quen người viết thuộc P2.
- Chuyển đổi TTF/OTF sang centerline, mở rộng hàng loạt Font Pack và mô hình sinh chữ viết tay sâu thuộc P3.
- Art Mode như sketch, hatching hoặc stipple không được dùng làm bằng chứng cho CA-VHC Handwriting Mode.
- Hệ thống chưa tuyên bố hoạt động real-time, trơn $C^1$ toàn cục hoặc an toàn vật lý.
- Nhận dạng chữ viết tay không phải mục tiêu của RQ1–RQ3; corpus Writer Profile không thay thế corpus đánh giá CA-VHC.

## 1.6. Phương pháp nghiên cứu tổng quát

Đề tài sử dụng thiết kế thực nghiệm định lượng có kiểm soát, kết hợp kiểm chứng phần mềm và kiểm chứng vật lý ở giai đoạn sau. Quy trình tổng quát gồm năm bước:

1. **Mô hình hóa trạng thái:** mỗi vị trí ký tự sinh một tập `CompositionState`, trong đó mỗi state chứa biến thể thân chữ và một ứng viên cấu hình dấu hợp lệ.
2. **Pruning và kiểm tra cứng:** loại các ứng viên sai bounds, va chạm nội tại hoặc vi phạm quy tắc hình học trước khi chạy tối ưu.
3. **Tối ưu chuỗi:** dùng recurrence Viterbi [6] để tối thiểu hóa tổng state cost và transition cost; backpointer tái dựng chuỗi trạng thái được chọn.
4. **Kết xuất và đo lường:** tạo quỹ đạo vector, sau đó đo tách biệt pen-down path, pen-up movement, collision, clearance, curvature, bounds và thời gian.
5. **So sánh và kiểm chứng:** chạy B1/B2/B3/Proposed theo ma trận thực nghiệm, phân tích kết quả theo quy tắc đã khóa và thực hiện smoke test trên máy sau calibration.

Với từ gồm $N$ vị trí và tối đa $K$ trạng thái còn lại ở mỗi vị trí, recurrence đầy đủ có chi phí thời gian $O(NK^2)$ và bộ nhớ $O(NK)$ khi lưu bảng chi phí cùng backpointer. Giới hạn $K_{raw} \le 9$ là design constraint cần được kiểm chứng bằng profiling, không phải bằng chứng rằng hệ thống đã đạt real-time.

Protocol chi tiết về corpus, split DEV/Holdout, seed, warm-up, repetitions, logging, baseline và phân tích thống kê được khóa trong [`08_handwriting_dataset_spec.md`](08_handwriting_dataset_spec.md), [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md) và [`10_nckh_research_plan.md`](10_nckh_research_plan.md).

## 1.7. Đóng góp dự kiến

Nếu các giả thuyết được kiểm chứng, đề tài dự kiến tạo ra bốn nhóm đóng góp:

1. **Đóng góp phương pháp:** mô hình `CompositionState` cho phép xem lựa chọn allograph và vị trí dấu tiếng Việt như một bài toán chuỗi thống nhất thay vì hai bước tách rời.
2. **Đóng góp thuật toán:** hàm mục tiêu CA-VHC và Viterbi DP kết hợp chi phí hình học, bridge collision, pen-up movement và khả năng thi công trong một khung có thể giải thích.
3. **Đóng góp kỹ thuật:** engine vector nét đơn có baseline adapters, metric evaluator, deterministic seed, CSV logging, self-check và acceptance gate phục vụ tái lập thực nghiệm.
4. **Đóng góp đánh giá:** protocol phân biệt rõ chất lượng hình học, hiệu năng phần mềm và số đo máy thật; kèm corpus/split và tiêu chí PASS/FAIL/INCONCLUSIVE được định nghĩa trước khi chạy holdout.

Các nội dung trên là mục tiêu đầu ra của nghiên cứu. Chúng chỉ được chuyển thành tuyên bố đóng góp đã đạt sau khi code, benchmark, ablation và hardware validation tương ứng vượt qua gate.

## 1.8. Ý nghĩa khoa học và thực tiễn

Về khoa học, đề tài khảo sát khả năng đưa các ràng buộc chữ viết tiếng Việt vào một mô hình tối ưu chuỗi hữu hạn. Cấu trúc này tạo điều kiện truy vết vì sao một biến thể hoặc vị trí dấu được chọn, đồng thời cho phép ablation từng thành phần chi phí. Nếu kết quả ủng hộ giả thuyết, nghiên cứu sẽ cung cấp bằng chứng rằng composition-aware planning có thể cải thiện một số metric chuyển động và va chạm mà không cần mô hình sinh khó giải thích.

Về thực tiễn, đầu ra nét đơn có thể giảm phần xử lý trung gian giữa văn bản và máy vẽ, đồng thời hỗ trợ các ứng dụng như thư tay cá nhân hóa, thiệp, trình diễn giáo dục và prototype robot viết. Tuy nhiên, giá trị ứng dụng chỉ được đánh giá trong giới hạn thiết bị, Font Pack và corpus của nghiên cứu; đề tài không suy rộng sang mọi kiểu chữ hoặc mọi máy vẽ.

## 1.9. Giới hạn và ranh giới tuyên bố

Tại thời điểm lập bản thảo, PR1 về metric và experiment infrastructure đã hoàn thành; PR2 baseline adapters đang chờ TV2 hoàn tất; PR3 về Diacritic-Aware Trellis chưa bắt đầu; corpus formal và hardware calibration chưa được khóa. Vì vậy:

- chưa có số liệu chính thức để chấp nhận hoặc bác bỏ RQ1–RQ3;
- chưa được gọi CA-VHC là real-time hoặc tốt hơn baseline;
- chưa được gọi clearance hiện tại là ngưỡng an toàn vật lý;
- chưa được dùng kết quả simulator thay cho `actual_draw_time_sec`;
- chưa được tuyên bố novelty tuyệt đối từ bộ nguồn hạt giống;
- chưa được mô tả engine hiện tại là hệ AI đã học thói quen chữ viết.

Các ranh giới này là một phần của thiết kế nghiên cứu, giúp phân biệt năng lực đã kiểm thử, thiết kế đã khóa và mục tiêu còn chờ thực nghiệm.

## 1.10. Cấu trúc báo cáo

Phần còn lại của báo cáo được tổ chức như sau:

- **Chương 2 — Tổng quan và cơ sở lý thuyết:** tổng hợp nghiên cứu về chữ viết tay trực tuyến, dấu tiếng Việt, Unicode/OpenType, Viterbi và robot vẽ; xác lập khoảng trống nghiên cứu provisional.
- **Chương 3 — Phương pháp nghiên cứu:** mô tả `CompositionState`, hàm mục tiêu, pruning, recurrence, baseline, corpus, protocol thực nghiệm và kiểm chứng phần cứng.
- **Chương 4 — Kết quả và thảo luận:** trình bày kết quả định lượng, ablation, phân tích lỗi và threats to validity sau khi toàn bộ gate hoàn tất.
- **Chương 5 — Kết luận và hướng phát triển:** trả lời RQ theo bằng chứng thu được, nêu giới hạn và định hướng Writer Profile, Font Pack hoặc triển khai nâng cao.

## Tài liệu tham khảo

> Đánh số được giữ thống nhất với Chương 2; danh mục này sẽ được hợp nhất thành một danh mục chung khi đóng bản thảo toàn báo cáo.

[1] A. Graves, “Generating Sequences With Recurrent Neural Networks,” arXiv:1308.0850, 2013. https://arxiv.org/abs/1308.0850

[3] H. T. Nguyen, C. T. Nguyen, P. T. Bao, and M. Nakagawa, “A database of unconstrained Vietnamese online handwriting and recognition experiments by recurrent neural networks,” *Pattern Recognition*, vol. 78, pp. 291–306, 2018, doi: 10.1016/j.patcog.2018.01.013.

[4] Unicode Consortium, “Unicode Standard Annex #15: Unicode Normalization Forms,” rev. 58, 2026. https://www.unicode.org/reports/tr15/

[5] Microsoft, “GPOS — Glyph Positioning Table,” *OpenType Specification*, ver. 1.9.1. https://learn.microsoft.com/en-us/typography/opentype/spec/gpos

[6] A. J. Viterbi, “Error bounds for convolutional codes and an asymptotically optimum decoding algorithm,” *IEEE Trans. Inf. Theory*, vol. 13, no. 2, pp. 260–269, 1967, doi: 10.1109/TIT.1967.1054010.

[8] T. Wang et al., “RoboCoDraw: Robotic Avatar Drawing with GAN-Based Style Transfer and Time-Efficient Path Optimization,” *Proc. AAAI Conf. Artif. Intell.*, vol. 34, no. 6, pp. 10402–10409, 2020, doi: 10.1609/aaai.v34i06.6609.

[9] Y. Lu, J. H. M. Lam, and Y. Yam, “Preliminary study on vision-based pen-and-ink drawing by a robotic manipulator,” in *Proc. IEEE/ASME AIM*, 2009, pp. 578–583, doi: 10.1109/AIM.2009.5229949.

[10] A. Mohammed, L. Wang, and R. X. Gao, “Integrated Image Processing and Path Planning for Robotic Sketching,” *Procedia CIRP*, vol. 12, pp. 199–204, 2013, doi: 10.1016/j.procir.2013.09.035.

[11] A. Kotani and S. Tellex, “Teaching Robots to Draw,” in *Proc. IEEE ICRA*, 2019, pp. 4797–4803, doi: 10.1109/ICRA.2019.8793484.
