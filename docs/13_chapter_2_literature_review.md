# Chương 2 — Tổng quan và Cơ sở lý thuyết

**Bản thảo:** 0.1  
**Trạng thái:** `DRAFT — CITATION CHAINING AND TEAM REVIEW PENDING`  
**Phạm vi:** Handwriting Mode / CA-VHC; không trình bày kết quả thực nghiệm OmniDraw

## 2.1. Phạm vi tổng quan

OmniDraw hướng đến chuyển văn bản thành quỹ đạo chữ viết tay nét đơn có thể thi công bằng máy vẽ. Bài toán không chỉ là tạo hình dáng giống chữ viết tay. Một hệ hoàn chỉnh còn phải xác định chuỗi nét, vị trí và thứ tự dấu, quyết định khi nào nối hoặc nhấc bút, kiểm soát va chạm hình học và tạo đầu ra phù hợp với giới hạn chuyển động của thiết bị. Vì vậy, chương này tổng hợp bốn nền tảng: tổng hợp chữ viết tay trực tuyến, biểu diễn dấu tiếng Việt, tối ưu chuỗi trạng thái và lập kế hoạch quỹ đạo robot.

Quy trình tìm và chọn nguồn được ghi tại [`11_literature_review_protocol.md`](11_literature_review_protocol.md); dữ liệu trích xuất từng nguồn nằm tại [`12_literature_evidence_matrix.md`](12_literature_evidence_matrix.md). Đây là tổng quan có cấu trúc ở giai đoạn đầu, chưa phải systematic review.

## 2.2. Chữ viết tay trực tuyến và biểu diễn chuỗi nét

Chữ viết tay trực tuyến thường được biểu diễn như một chuỗi tọa độ theo thời gian kèm trạng thái bút. Cách biểu diễn này giữ được thông tin mà ảnh raster không có, gồm thứ tự nét, vị trí pen-down/pen-up và chuyển động giữa các nét. Graves [1] mô hình hóa online handwriting như một chuỗi giá trị thực và dùng mạng hồi quy với mixture-density output để dự đoán điểm tiếp theo. Khi điều kiện hóa theo chuỗi ký tự, mô hình có thể sinh chữ viết tay từ văn bản và giữ một phần đặc trưng phong cách thông qua priming.

DeepWriting của Aksan, Pece và Hilliges [2] tiếp tục xem digital ink là đối tượng có thể sinh và chỉnh sửa. Công trình tách nội dung khỏi phong cách để hỗ trợ tổng hợp văn bản mới trong một phong cách đã quan sát. Hai hướng này chứng minh rằng tính tự nhiên và phong cách có thể được học từ dữ liệu. Tuy nhiên, chúng phụ thuộc vào tập dữ liệu và mô hình sinh xác suất, trong khi P0 của OmniDraw cần đường nét xác định, dễ kiểm tra và có thể giải thích bằng các thành phần chi phí hình học.

Do đó, OmniDraw không dùng các mô hình học sâu trên làm baseline trực tiếp cho CA-VHC. Chúng tạo cơ sở cho hướng Writer Profile và few-shot personalization ở P2. Trong phạm vi hiện tại, hệ thống biểu diễn mỗi glyph bằng hình học nét đơn, sau đó lựa chọn biến thể và kết nối theo ngữ cảnh. Sự phân biệt này giúp tránh một tuyên bố sai rằng engine heuristic hiện tại đã “học” thói quen người viết.

## 2.3. Đặc thù chữ viết tay tiếng Việt

Tiếng Việt sử dụng nhiều tổ hợp chữ cái cơ sở, dấu phụ và dấu thanh. Với dữ liệu số, cùng một biểu hiện thị giác có thể tồn tại dưới dạng ký tự dựng sẵn hoặc chuỗi base character + combining marks. Unicode Standard Annex #15 [4] định nghĩa các dạng chuẩn hóa, trong đó NFD tạo phân rã canonical. NFD vì vậy là bước phù hợp để engine tách thân chữ khỏi các dấu đi kèm. Dù vậy, normalization chỉ giải quyết tính tương đương và thứ tự mã; nó không xác định dấu phải neo tại tọa độ nào trong glyph nét đơn.

Trong typography, bảng GPOS của OpenType [5] cung cấp các cơ chế MarkToBase, MarkToLigature và MarkToMark dựa trên anchor. Đặc biệt, MarkToMark phù hợp với các trường hợp dấu thanh đặt trên một dấu chữ cái khác. Mô hình anchor này gợi ý rằng metadata dấu nên thuộc Font Pack hoặc trạng thái composition thay vì hard-code một offset dùng chung. Tuy nhiên, OpenType giả định quá trình layout glyph và không quản lý đường đi của đầu bút. Một vị trí dấu hợp lệ về typography vẫn có thể bị nét nối của plotter cắt qua.

Nguyen và cộng sự [3] xây dựng cơ sở dữ liệu chữ viết tay trực tuyến tiếng Việt và chỉ ra vai trò nổi bật của delayed strokes. Dấu có thể được viết sau một số nét hoặc sau các ký tự tiếp theo, tùy người viết và ngữ cảnh. Kết quả này quan trọng đối với OmniDraw ở hai mức. Thứ nhất, dấu không nên bị xem như chi tiết trang trí có thể bỏ qua. Thứ hai, bài toán “đặt dấu ở đâu” và “vẽ dấu khi nào” là hai quyết định khác nhau. Thiết kế CA-VHC vì vậy tách PR3 phụ trách vị trí dấu khỏi PR4 phụ trách delayed-stroke ordering.

## 2.4. Lựa chọn chuỗi trạng thái bằng quy hoạch động

Khi mỗi vị trí ký tự có nhiều allograph và nhiều ứng viên đặt dấu, số tổ hợp toàn từ tăng theo cấp số nhân nếu duyệt vét cạn. Thuật toán Viterbi [6] cung cấp nguyên lý quy hoạch động trên trellis: tại mỗi trạng thái chỉ giữ đường đi tốt nhất dẫn đến trạng thái đó, đồng thời lưu backpointer để tái dựng chuỗi tối ưu. Giá trị chuyển giao cho OmniDraw nằm ở cấu trúc phương pháp chứ không ở miền mã hóa kênh của bài báo gốc.

Với từ gồm (N) vị trí và tối đa (K) trạng thái sau pruning ở mỗi vị trí, recurrence đầy đủ có chi phí thời gian (O(NK^2)) và bộ nhớ (O(NK)) nếu lưu bảng chi phí cùng backpointer. Trong thiết kế CA-VHC, một `CompositionState` kết hợp biến thể thân chữ và ứng viên dấu. State cost đo thuộc tính nội tại như legibility, placement và va chạm bên trong; transition cost đo quan hệ giữa hai trạng thái kề nhau như quãng đường pen-up, số lần nhấc bút, curvature và bridge collision. Việc tách hai nhóm chi phí giúp hạn chế double-count và giữ recurrence có thể kiểm tra.

Khác với cách đặt dấu hậu xử lý, state có nhận thức dấu cho phép loại sớm một bridge đi qua vùng cản. Đây là giả thuyết thiết kế của OmniDraw, chưa phải kết quả đã được chứng minh. Hiệu quả phải được so sánh với renderer tĩnh, heuristic tham lam và trellis hiện hành trên cùng corpus, font và seed.

## 2.5. Tối ưu quỹ đạo và chuyển động bút

Trong hệ robot vẽ, hình học đầu ra và thứ tự thi công liên quan nhưng không đồng nhất. Lu, Lam và Yam [9] xây dựng pipeline chuyển outline thành stroke trajectory, sau đó dùng visual feedback cho hatching. Zhang và cộng sự [10] kết hợp trích contour, giảm số điểm và sắp thứ tự path gần tối ưu nhằm giảm thời gian di chuyển robot. RoboCoDraw [8] cũng tách phần sinh ảnh phong cách khỏi phần tối ưu path và dùng random-key genetic algorithm để tìm quỹ đạo vẽ hiệu quả về thời gian. Các nghiên cứu này cho thấy một hình vẽ hợp lệ chưa chắc đã có thứ tự thi công tốt.

Kotani và cộng sự [11] nhấn mạnh continuity ở cấp nét khi robot học tái tạo ký tự hoặc line drawing. Đối với OmniDraw, điều này hỗ trợ việc đo riêng nét tiếp xúc giấy và chuyển động trên không. Ba đại lượng `total_path_length_mm`, `pen_lift_distance_mm` và `pen_lift_count` vì vậy trả lời những khía cạnh khác nhau; không nên gộp chúng thành một “độ tối ưu” duy nhất.

Độ mượt chuyển động cũng cần được xem như mục tiêu, nhưng không được suy diễn quá mức. Mô hình minimum-jerk của Flash và Hogan [7] cho thấy chuyển động tay hướng đích có thể được mô tả bằng nguyên lý tối ưu độ trơn. Đây là cơ sở để OmniDraw đưa curvature hoặc thay đổi tiếp tuyến vào hàm chi phí. Nó không tự cung cấp ngưỡng góc (120^\circ), không chứng minh mọi junction Bézier đạt liên tục (C^1), và không thay thế thử nghiệm trên máy thật. Các ngưỡng đó phải được định nghĩa như design target rồi hiệu chuẩn theo thiết bị.

## 2.6. Từ quỹ đạo vector đến máy vẽ

Các công trình robotic sketching [8]–[11] đều cho thấy physical execution cần thêm các yếu tố ngoài hình học lý tưởng, chẳng hạn hiệu chuẩn, giới hạn workspace, sai số cơ khí, vận tốc và phản hồi cảm biến. Bởi vậy, thời gian tạo SVG không thể được gọi là thời gian vẽ thực tế. Tương tự, `is_within_bounds` chỉ cho biết hình học nằm trong khổ dự kiến, không bảo đảm đầu bút theo đúng quỹ đạo sau khi truyền sang phần cứng.

OmniDraw phân tách ba tầng bằng chứng: thời gian tối ưu nội bộ của CA-VHC, thời gian xử lý phần mềm đầu-cuối và `actual_draw_time_sec` đo trên máy. RQ3 chỉ có thể kết luận về khả năng thi công vật lý sau khi TV3 hoàn tất calibration và smoke test. Cách phân tách này tránh trộn số đo khác bản chất và giúp kết quả có thể tái lập.

## 2.7. So sánh hướng tiếp cận

| Nhóm phương pháp | Biểu diễn chính | Điểm mạnh | Giới hạn đối với OmniDraw |
| :--- | :--- | :--- | :--- |
| Neural handwriting synthesis [1], [2] | Chuỗi điểm xác suất + latent style | Tự nhiên, đa dạng, có tiềm năng cá nhân hóa | Cần dữ liệu; khó bảo đảm collision, bounds và khả năng giải thích |
| Unicode/OpenType [4], [5] | Character decomposition + glyph anchors | Chuẩn hóa văn bản và neo dấu có cấu trúc | Không mô hình hóa centerline, pen-up hay đường đi robot |
| Trellis/Viterbi [6] | Chuỗi trạng thái hữu hạn | Tối ưu toàn cục trong trellis với recurrence rõ | Chất lượng phụ thuộc state, cost và pruning do nhóm thiết kế |
| Robotic drawing/path planning [8]–[11] | Stroke/path/robot trajectory | Gắn thứ tự nét với thời gian và thi công | Phần lớn tập trung ảnh/sketch, không xử lý chính tả dấu tiếng Việt |
| CA-VHC đề xuất | Allograph + diacritic candidate trong `CompositionState` | Có thể đồng tối ưu hình học dấu, nối nét và chuyển động với metric giải thích được | Chưa có kết quả formal; novelty cuối cùng còn chờ rà soát tài liệu mở rộng và thực nghiệm |

## 2.8. Khoảng trống nghiên cứu và định vị CA-VHC

Bộ nguồn hạt giống cho thấy ba cộng đồng giải quyết các phần khác nhau của bài toán: handwriting synthesis tập trung vào chuỗi nét và phong cách; font layout tập trung vào phân rã và neo glyph; robot drawing tập trung vào stroke planning và thi công. Trong phạm vi nguồn đã sàng lọc, chưa thấy một phương pháp đồng thời đưa biến thể thân chữ theo ngữ cảnh, ứng viên dấu tiếng Việt, vùng cản bridge và chi phí chuyển động vào một trellis hữu hạn cho máy vẽ nét đơn.

Từ đó, CA-VHC được định vị là một phương pháp composition hình học có thể giải thích: mở rộng trạng thái Viterbi từ `GlyphVariant` sang `CompositionState`, đưa dấu vào quá trình chọn đường thay vì đặt hoàn toàn sau tối ưu, và đánh giá bằng metric tách biệt cho chất lượng nét, chuyển động và va chạm. Đây mới là **định vị tạm thời**, chưa phải tuyên bố độc quyền hay mới tuyệt đối. Kết luận về tính mới chỉ được khóa sau backward/forward citation chaining và cross-review của nhóm.

## 2.9. Kết luận chương

Tổng quan cho thấy OmniDraw cần kết hợp kiến thức từ nhiều miền nhưng phải giữ ranh giới bằng chứng. Unicode và OpenType cung cấp cơ sở biểu diễn dấu; nghiên cứu chữ viết tay tiếng Việt cung cấp bằng chứng về delayed strokes; Viterbi cung cấp cấu trúc tối ưu chuỗi; nghiên cứu robot vẽ cung cấp tiêu chí về path và thi công. Trên nền đó, Chương 3 sẽ mô tả `CompositionState`, hàm mục tiêu CA-VHC, pruning, recurrence và protocol đánh giá. Chương 4 chỉ điền kết quả khi các gate corpus, baseline, phần mềm và phần cứng đã hoàn tất.

## Tài liệu tham khảo

[1] A. Graves, “Generating Sequences With Recurrent Neural Networks,” arXiv:1308.0850, 2013. https://arxiv.org/abs/1308.0850

[2] E. Aksan, F. Pece, and O. Hilliges, “DeepWriting: Making Digital Ink Editable via Deep Generative Modeling,” in *Proc. CHI*, 2018, Art. no. 205, doi: 10.1145/3173574.3173779.

[3] H. T. Nguyen, C. T. Nguyen, P. T. Bao, and M. Nakagawa, “A database of unconstrained Vietnamese online handwriting and recognition experiments by recurrent neural networks,” *Pattern Recognition*, vol. 78, pp. 291–306, 2018, doi: 10.1016/j.patcog.2018.01.013.

[4] Unicode Consortium, “Unicode Standard Annex #15: Unicode Normalization Forms,” rev. 58, 2026. https://www.unicode.org/reports/tr15/

[5] Microsoft, “GPOS — Glyph Positioning Table,” *OpenType Specification*, ver. 1.9.1. https://learn.microsoft.com/en-us/typography/opentype/spec/gpos

[6] A. J. Viterbi, “Error bounds for convolutional codes and an asymptotically optimum decoding algorithm,” *IEEE Trans. Inf. Theory*, vol. 13, no. 2, pp. 260–269, 1967, doi: 10.1109/TIT.1967.1054010.

[7] T. Flash and N. Hogan, “The coordination of arm movements: an experimentally confirmed mathematical model,” *J. Neurosci.*, vol. 5, no. 7, pp. 1688–1703, 1985, doi: 10.1523/JNEUROSCI.05-07-01688.1985.

[8] T. Wang et al., “RoboCoDraw: Robotic Avatar Drawing with GAN-Based Style Transfer and Time-Efficient Path Optimization,” *Proc. AAAI Conf. Artif. Intell.*, vol. 34, no. 6, pp. 10402–10409, 2020, doi: 10.1609/aaai.v34i06.6609.

[9] Y. Lu, J. H. M. Lam, and Y. Yam, “Preliminary study on vision-based pen-and-ink drawing by a robotic manipulator,” in *Proc. IEEE/ASME AIM*, 2009, pp. 578–583, doi: 10.1109/AIM.2009.5229949.

[10] A. Mohammed, L. Wang, and R. X. Gao, “Integrated Image Processing and Path Planning for Robotic Sketching,” *Procedia CIRP*, vol. 12, pp. 199–204, 2013, doi: 10.1016/j.procir.2013.09.035.

[11] A. Kotani and S. Tellex, “Teaching Robots to Draw,” in *Proc. IEEE ICRA*, 2019, pp. 4797–4803, doi: 10.1109/ICRA.2019.8793484.
