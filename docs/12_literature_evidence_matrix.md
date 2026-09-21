# OmniDraw — Literature Evidence Matrix

**Phiên bản:** 0.1  
**Trạng thái:** `VERIFIED_SEED — TEAM REVIEW PENDING`  
**Protocol:** [`11_literature_review_protocol.md`](11_literature_review_protocol.md)

## 1. Ma trận bằng chứng

| ID | Nguồn đã xác minh | WHY / HOW / WHAT | Ánh xạ | Giới hạn chuyển giao | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- |
| S01 | A. Graves, “Generating Sequences With Recurrent Neural Networks,” 2013. [arXiv:1308.0850](https://arxiv.org/abs/1308.0850) | **WHY:** sinh chuỗi có cấu trúc dài hạn. **HOW:** RNN/LSTM với mixture-density output và attention/window để điều kiện hóa theo văn bản. **WHAT:** sinh được online handwriting và cho phép priming phong cách người viết. | LRQ1; P2 | Là mô hình học sâu trên dữ liệu tiếng Anh; không giải quyết trực tiếp dấu tiếng Việt, collision hoặc máy vẽ. | `VERIFIED_SEED` |
| S02 | E. Aksan, F. Pece, and O. Hilliges, “DeepWriting: Making Digital Ink Editable via Deep Generative Modeling,” CHI 2018. [doi:10.1145/3173574.3173779](https://doi.org/10.1145/3173574.3173779) | **WHY:** tách nội dung và phong cách trong digital ink. **HOW:** mô hình sinh sâu với biểu diễn style/content. **WHAT:** hỗ trợ tổng hợp văn bản, style transfer và chỉnh sửa ink ở cấp từ. | LRQ1; P2 | Là bằng chứng cho hướng cá nhân hóa tương lai, không phải baseline P0 cho CA-VHC hình học. | `VERIFIED_SEED` |
| S03 | H. T. Nguyen, C. T. Nguyen, P. T. Bao, and M. Nakagawa, “A database of unconstrained Vietnamese online handwriting and recognition experiments by recurrent neural networks,” *Pattern Recognition*, vol. 78, pp. 291–306, 2018. [doi:10.1016/j.patcog.2018.01.013](https://doi.org/10.1016/j.patcog.2018.01.013) | **WHY:** thiếu dữ liệu online handwriting tiếng Việt tự nhiên. **HOW:** thu thập VNOnDB và phân tích chuỗi nét/delayed strokes. **WHAT:** chỉ ra dấu tiếng Việt thường tạo delayed strokes và cung cấp dữ liệu quy mô lớn cho recognition. | LRQ3; RQ2; PR4 | Nghiên cứu recognition, không trực tiếp tối ưu vị trí dấu hoặc sinh quỹ đạo. Giá trị chính là bằng chứng hành vi nét trễ. | `VERIFIED_SEED` |
| S04 | Unicode Consortium, “Unicode Standard Annex #15: Unicode Normalization Forms,” rev. 58, 2026. [UAX #15](https://www.unicode.org/reports/tr15/) | **WHY:** chuẩn hóa các chuỗi Unicode tương đương. **HOW:** định nghĩa NFC/NFD/NFKC/NFKD và canonical ordering. **WHAT:** cung cấp cơ sở chuẩn để phân rã base character và combining marks nhất quán. | LRQ4; RQ2 | Chuẩn hóa mã ký tự không quyết định hình học dấu, âm tiết mang dấu hay thứ tự robot vẽ. | `VERIFIED_SEED` |
| S05 | Microsoft, “GPOS — Glyph Positioning Table,” OpenType 1.9.1. [OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos) | **WHY:** định vị glyph/mark chính xác trong text layout. **HOW:** anchor, cursive attachment, MarkToBase, MarkToLigature và MarkToMark. **WHAT:** cho thấy neo dấu theo base/mark và contextual attachment là mô hình chuẩn trong typography. | LRQ4; RQ2 | GPOS dành cho glyph layout, không xử lý single-stroke centerline, pen-up hoặc collision với bridge. | `VERIFIED_SEED` |
| S06 | A. J. Viterbi, “Error bounds for convolutional codes and an asymptotically optimum decoding algorithm,” *IEEE Transactions on Information Theory*, vol. 13, no. 2, pp. 260–269, 1967. [doi:10.1109/TIT.1967.1054010](https://doi.org/10.1109/TIT.1967.1054010) | **WHY:** tìm chuỗi trạng thái tối ưu trong trellis. **HOW:** dynamic programming giữ đường tốt nhất theo trạng thái. **WHAT:** đặt nền tảng cho recurrence và backpointer kiểu Viterbi. | LRQ2; RQ1; RQ3 | Bài gốc thuộc mã hóa kênh; việc dùng cho composition là chuyển giao phương pháp, không phải bằng chứng trực tiếp về chữ viết tay. | `VERIFIED_SEED` |
| S07 | T. Flash and N. Hogan, “The coordination of arm movements: an experimentally confirmed mathematical model,” *Journal of Neuroscience*, vol. 5, no. 7, pp. 1688–1703, 1985. [doi:10.1523/JNEUROSCI.05-07-01688.1985](https://doi.org/10.1523/JNEUROSCI.05-07-01688.1985) | **WHY:** giải thích tính trơn của chuyển động tay hướng đích. **HOW:** mô hình tối thiểu hóa jerk và đối chiếu thực nghiệm. **WHAT:** cung cấp cơ sở sinh học–động học để xem độ trơn là một mục tiêu tối ưu. | LRQ2; RQ3 | Không cung cấp trực tiếp ngưỡng góc, curvature cost hay bảo đảm cơ khí cho plotter; các ngưỡng OmniDraw vẫn phải hiệu chuẩn. | `VERIFIED_SEED` |
| S08 | T. Wang et al., “RoboCoDraw: Robotic Avatar Drawing with GAN-Based Style Transfer and Time-Efficient Path Optimization,” *AAAI*, vol. 34, no. 6, pp. 10402–10409, 2020. [doi:10.1609/aaai.v34i06.6609](https://doi.org/10.1609/aaai.v34i06.6609) | **WHY:** giảm thời gian thi công robot vẽ ảnh phong cách. **HOW:** GAN tạo avatar và random-key genetic algorithm tối ưu path. **WHAT:** minh họa rằng thứ tự/path là thành phần nghiên cứu độc lập với hình ảnh đầu vào. | LRQ2; RQ1; RQ3 | Robot nhiều bậc tự do và nét ảnh khác với chữ viết tay hai trục; không thể chuyển trực tiếp số liệu thời gian. | `VERIFIED_SEED` |
| S09 | Y. Lu, J. H. M. Lam, and Y. Yam, “Preliminary study on vision-based pen-and-ink drawing by a robotic manipulator,” AIM 2009, pp. 578–583. [doi:10.1109/AIM.2009.5229949](https://doi.org/10.1109/AIM.2009.5229949) | **WHY:** tự động hóa pen-and-ink drawing bằng thị giác. **HOW:** chuyển outline thành stroke trajectory, iterative hatching và visual feedback. **WHAT:** chứng minh pipeline từ hình ảnh đến quỹ đạo và thi công robot cần cả planning lẫn feedback. | LRQ2; RQ3 | Tập trung sketch/hatching, không phải dấu tiếng Việt hay contextual glyph variants. | `VERIFIED_SEED` |
| S10 | A. Mohammed, L. Wang, and R. X. Gao, “Integrated Image Processing and Path Planning for Robotic Sketching,” *Procedia CIRP*, vol. 12, pp. 199–204, 2013. [doi:10.1016/j.procir.2013.09.035](https://doi.org/10.1016/j.procir.2013.09.035) | **WHY:** nối image processing với path planning không cần lập trình tay. **HOW:** trích contour, giảm số điểm, sắp thứ tự path gần tối ưu và điều khiển robot. **WHAT:** cho thấy chất lượng hình học và thứ tự quỹ đạo phải được đánh giá cùng nhau. | LRQ2; RQ1; RQ3 | Bài toán contour sketch khác single-stroke handwriting; “near-optimal” không đồng nghĩa tối ưu CA-VHC. | `VERIFIED_SEED` |
| S11 | A. Kotani and S. Tellex, “Teaching Robots to Draw,” ICRA 2019, pp. 4797–4803. [doi:10.1109/ICRA.2019.8793484](https://doi.org/10.1109/ICRA.2019.8793484) | **WHY:** robot cần tái tạo ký tự/nét vẽ từ quan sát. **HOW:** học kế hoạch hành động từ demonstrations và thi công mỗi target stroke liên tục. **WHAT:** nêu tầm quan trọng của continuity và stroke-level plan khi chuyển ảnh/nét sang hành động robot. | LRQ1; LRQ2; RQ3 | Mục tiêu sao chép từ ảnh khác với text-to-stroke deterministic rendering và chưa xử lý cấu trúc dấu tiếng Việt. | `VERIFIED_SEED` |

## 2. Tổng hợp theo câu hỏi nghiên cứu

| RQ | Bằng chứng hỗ trợ | Điều nguồn chưa giải quyết | Vai trò dự kiến của OmniDraw |
| :--- | :--- | :--- | :--- |
| RQ1 | S06 cung cấp nền tảng trellis/DP; S08–S10 cho thấy path ordering ảnh hưởng hiệu quả thi công; S01–S02 cho thấy ngữ cảnh và phong cách có thể được mô hình hóa ở cấp chuỗi. | Chưa có nguồn hạt giống nào đồng tối ưu allograph, quyết định nối/nhấc bút và dấu tiếng Việt trong cùng trạng thái hữu hạn cho single-stroke plotter. | Kiểm chứng `CompositionState` + Viterbi bằng pen-up distance, pen-lift count và total path length với ba baseline. |
| RQ2 | S03 chứng minh delayed strokes là đặc trưng đáng kể của chữ viết tay tiếng Việt; S04 chuẩn hóa base/combining mark; S05 cung cấp tư duy anchor và mark-to-mark. | Unicode/OpenType không mô hình hóa vùng cản bridge; nghiên cứu recognition không quyết định vị trí dấu sinh ra. | Đưa ứng viên dấu và vùng cản vào state/transition, đo collision và clearance thay vì chỉ render hậu kỳ. |
| RQ3 | S07 hỗ trợ mục tiêu trơn chuyển động; S08–S11 cho thấy planning và physical execution phải được kiểm chứng; S06 hỗ trợ thuật toán chuỗi có cấu trúc. | Không nguồn nào cung cấp ngưỡng latency/clearance dùng trực tiếp cho thiết bị OmniDraw. | Báo cáo độ phức tạp, median/p95 và tách simulator khỏi số đo máy thật; ngưỡng vật lý phải do TV3 hiệu chuẩn. |

## 3. Khoảng trống tạm thời

Từ **bộ nguồn hạt giống hiện tại**, có thể phát biểu thận trọng rằng các hướng liên quan thường tách thành ba lớp:

1. mô hình sinh digital ink và phong cách người viết;
2. typography/encoding dùng normalization và mark attachment;
3. robot drawing dùng stroke/path planning để giảm thời gian hoặc bảo đảm thi công.

Chưa tìm thấy trong vòng hạt giống một công trình đồng thời mô hình hóa **allograph theo ngữ cảnh + vị trí dấu tiếng Việt + bridge collision + chi phí pen-up/curvature** trong một trellis hữu hạn dành cho máy vẽ nét đơn. Đây là **provisional gap**, chưa phải tuyên bố novelty cuối cùng. Phải hoàn tất citation chaining và team screening trước khi dùng trong phần “tính mới”.

## 4. Các nguồn cần tìm thêm

- Công trình chuyên biệt về Vietnamese handwriting synthesis, không chỉ recognition.
- Nghiên cứu định lượng về thứ tự delayed strokes trong chữ viết tay tiếng Việt.
- Tối ưu toolpath cho pen plotter hai trục có metric pen-up/turning cost.
- Đánh giá legibility/naturalness của chữ viết tay sinh tự động.
- Phương pháp contextual allograph cho Latin cursive hoặc type design có anchor/entry/exit.
