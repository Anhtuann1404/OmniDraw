# OmniDraw — Literature Evidence Matrix

**Phiên bản:** 0.2
**Trạng thái:** `CITATION_CHAINING_R1 VERIFIED — TEAM REVIEW PENDING`
**Protocol:** [`11_literature_review_protocol.md`](11_literature_review_protocol.md)

**Material Passport**

- **Origin Skill:** `academic-research-suite/deep-research`
- **Origin Mode:** Literature review — Phase 2 Investigation
- **Origin Date:** 2026-09-22
- **Verification Status:** `METADATA VERIFIED — FULL-TEXT REVIEW PARTIAL`

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
| S12 | E. F. Bilgin Taşdemir and B. Yanıkoğlu, “A comparative study of delayed stroke handling approaches in online handwriting,” *International Journal on Document Analysis and Recognition*, vol. 22, no. 1, pp. 15–28, 2019. [doi:10.1007/s10032-018-0313-2](https://doi.org/10.1007/s10032-018-0313-2) | **WHY:** delayed strokes làm sai thứ tự không gian–thời gian của chuỗi viết. **HOW:** so sánh chiến lược loại bỏ và nhúng lại delayed strokes trên UNIPEN và dữ liệu tiếng Thổ Nhĩ Kỳ với HMM/BLSTM. **WHAT:** hiệu quả phụ thuộc dữ liệu và recognizer; không có một chiến lược xử lý duy nhất luôn tốt nhất. | LRQ3; RQ2 | Là nghiên cứu recognition, không xác định vị trí hình học tối ưu hay thứ tự robot phải vẽ dấu tiếng Việt. | `VERIFIED_CHAIN_R1` |
| S13 | U. Bhattacharya, R. Plamondon, S. Dutta Chowdhury, P. Goyal, and S. K. Parui, “A sigma-lognormal model-based approach to generating large synthetic online handwriting sample databases,” *International Journal on Document Analysis and Recognition*, vol. 20, no. 3, pp. 155–171, 2017. [doi:10.1007/s10032-017-0287-5](https://doi.org/10.1007/s10032-017-0287-5) | **WHY:** dữ liệu online handwriting gán nhãn khó thu thập ở quy mô lớn. **HOW:** dùng mô hình sigma-lognormal để sinh các mẫu quỹ đạo tổng hợp mang biến thiên động học. **WHAT:** cung cấp đối chứng cho hướng mô phỏng vận động người viết và tạo dữ liệu tổng hợp. | LRQ1; P2; RQ3 | Không giải quyết ngữ âm/chính tả tiếng Việt, anchor dấu hay giới hạn cơ khí của plotter; không thể thay cho dữ liệu người dùng thật. | `VERIFIED_CHAIN_R1` |
| S14 | Q. Li, Z. Guo, F. Chao, X. Chang, L. Yang, C.-M. Lin, C. Shang, and Q. Shen, “Solving Robotic Trajectory Sequential Writing Problem via Learning Character’s Structural and Sequential Information,” *IEEE Transactions on Cybernetics*, vol. 54, no. 2, pp. 1096–1108, 2024. [doi:10.1109/TCYB.2022.3194700](https://doi.org/10.1109/TCYB.2022.3194700) | **WHY:** robot cần sinh thứ tự quỹ đạo hợp lý khi thông tin tuần tự huấn luyện hạn chế. **HOW:** GRU kết hợp trajectory-sequence vector có nhãn để học cấu trúc và trình tự ký tự. **WHAT:** chứng minh structural/sequential information có thể được đánh giá riêng trong robotic writing. | LRQ1; LRQ2; RQ1; RQ3 | Hệ học dữ liệu cho robot calligraphy, không phải finite-state deterministic composition; chưa xử lý Latin/Vietnamese combining marks hay two-axis pen plotter. | `VERIFIED_CHAIN_R1` |
| S15 | S. Wang, J. Chen, X. Deng, S. Hutchinson, and F. Dellaert, “Robot Calligraphy using Pseudospectral Optimal Control in Conjunction with a Novel Dynamic Brush Model,” IROS 2020, pp. 6696–6703. [doi:10.1109/IROS45743.2020.9341787](https://doi.org/10.1109/IROS45743.2020.9341787) | **WHY:** quỹ đạo robot và biến dạng công cụ viết phải được tối ưu cùng nhau để tái tạo thư pháp. **HOW:** tham số hóa trajectory bằng đa thức Chebyshev, tối ưu pseudospectral và dùng dynamic brush model trong hàm mục tiêu. **WHAT:** củng cố cách xem robotic writing là trajectory optimization có ràng buộc công cụ. | LRQ2; RQ3 | Bút lông, chữ Hán và manipulator khác đáng kể với bút bi/plotter hai trục; không chuyển trực tiếp mô hình brush hoặc số liệu thời gian. | `VERIFIED_CHAIN_R1` |
| S16 | J. Shin, S. Hong, and J. Bak, “CASHG: Context-Aware Stylized Online Handwriting Generation,” arXiv:2604.02103, 2026. [arXiv:2604.02103](https://arxiv.org/abs/2604.02103) | **WHY:** sinh câu viết tay cần ký tự phụ thuộc ngữ cảnh, continuity và spacing ổn định. **HOW:** Character Context Encoder, bigram-aware sliding-window Transformer, curriculum ba giai đoạn và Connectivity/Spacing Metrics. **WHAT:** báo cáo cải thiện metric biên ký tự và human evaluation, cho thấy context-aware connectivity đã là hướng nghiên cứu trực tiếp. | LRQ1; LRQ5; P2 | **Preprint, chưa peer-reviewed.** Không xử lý chính tả/dấu tiếng Việt, collision với bridge, finite-state Viterbi hay chi phí thi công plotter. Đây là phản chứng đối với tuyên bố novelty rộng, không phải bằng chứng rằng OmniDraw đã đạt kết quả tương đương. | `VERIFIED_METADATA_PREPRINT` |

## 2. Kiểm chứng nguồn và chất lượng bằng chứng

`Level` mô tả thiết kế bằng chứng, không phải thứ hạng venue. `Grade` đánh giá khả năng dùng nguồn cho đúng luận điểm trong tổng quan này: A = trực tiếp/metadata mạnh; B = phù hợp nhưng có giới hạn chuyển giao; C = chỉ dùng thận trọng. COI chưa đọc đủ toàn văn được ghi `PENDING`, không được hiểu là “không có COI”.

| ID | Trạng thái xuất bản | Level / Grade | Kiểm chứng và cảnh báo |
| :--- | :--- | :--- | :--- |
| S01 | Preprint | Algorithmic study / B | Metadata arXiv xác minh; chưa peer-reviewed; COI `PENDING`. |
| S02 | Peer-reviewed conference | System/generative-model study / B | DOI và ACM venue xác minh; bằng chứng gần P2 nhưng không đặc thù tiếng Việt; COI `PENDING`. |
| S03 | Peer-reviewed journal | Dataset + recognition experiments / A | DOI/venue xác minh; trực tiếp cho Vietnamese online handwriting và delayed strokes; không suy sang synthesis; COI `PENDING`. |
| S04 | Normative standard | Standard / A | Nguồn Unicode chính thức; có thẩm quyền cho normalization, không phải bằng chứng hình học. |
| S05 | Normative specification | Standard / A | Nguồn Microsoft OpenType chính thức; có thẩm quyền cho GPOS, không phải plotter execution. |
| S06 | Peer-reviewed journal | Foundational algorithm / A | DOI/IEEE metadata xác minh; chuyển giao phương pháp sang composition phải ghi là suy luận. |
| S07 | Peer-reviewed journal | Controlled movement experiment / A | DOI/venue xác minh; cơ sở động học mạnh nhưng không hiệu chuẩn thiết bị OmniDraw; COI `PENDING`. |
| S08 | Peer-reviewed conference | Robotic drawing system / B | DOI/AAAI venue xác minh; khác morphology thiết bị và loại nét; COI `PENDING`. |
| S09 | Peer-reviewed conference | Robotic drawing proof-of-concept / B | DOI/IEEE venue xác minh; bằng chứng pipeline, không phải handwriting synthesis; COI `PENDING`. |
| S10 | Peer-reviewed proceedings | Integrated system study / B | DOI/venue xác minh; contour sketch khác single-stroke text; COI `PENDING`. |
| S11 | Peer-reviewed conference | Learning-from-demonstration robot study / B | DOI/IEEE venue xác minh; phù hợp continuity/stroke plan; COI `PENDING`. |
| S12 | Peer-reviewed journal | Comparative recognition experiment / A | DOI và kho Sabancı xác minh; so sánh delayed-stroke handling trực tiếp; không suy sang vị trí dấu; COI `PENDING`. |
| S13 | Peer-reviewed journal | Generative algorithm + empirical evaluation / B | DOI và kho Polytechnique Montréal xác minh; phù hợp mô hình động học/synthetic data; COI `PENDING`. |
| S14 | Peer-reviewed journal | Learned robotic writing system / B | DOI và institutional repository xác minh; published issue 2024, online-first 2022; COI `PENDING`. |
| S15 | Peer-reviewed conference | Optimal-control robotic system / B | DOI/IEEE metadata và proceedings xác minh; khác brush/robot; COI `PENDING`. |
| S16 | Preprint | Generative-model study / C | arXiv v2 ngày 2026-04-06 xác minh; chưa peer-reviewed, gắn cờ `PREPRINT`; COI `PENDING`. |

Không phát hiện dấu hiệu venue săn mồi trong metadata đã kiểm tra. Nhận định này không thay cho kiểm tra toàn văn, funding và competing-interest statement.

## 3. Tổng hợp theo câu hỏi nghiên cứu

| RQ | Bằng chứng hỗ trợ | Điều nguồn chưa giải quyết | Vai trò dự kiến của OmniDraw |
| :--- | :--- | :--- | :--- |
| RQ1 | S06 cung cấp nền tảng trellis/DP; S08–S10 cho thấy path ordering ảnh hưởng hiệu quả thi công; S01–S02 và S16 cho thấy ngữ cảnh, phong cách, continuity và spacing có thể được mô hình hóa ở cấp chuỗi; S14 là đối chứng robotic sequential writing. | Context-aware generation và sequence learning đã tồn tại. Chưa có bằng chứng trong matrix về hệ kết hợp chúng với chính tả/dấu tiếng Việt, collision/clearance và trạng thái hữu hạn cho single-stroke plotter. | Kiểm chứng `CompositionState` + Viterbi bằng pen-up distance, pen-lift count và total path length với ba baseline; không tuyên bố novelty rộng về contextual handwriting. |
| RQ2 | S03 chứng minh delayed strokes trong Vietnamese handwriting; S12 cho thấy chiến lược xử lý nét trễ phụ thuộc dữ liệu/mô hình; S04 chuẩn hóa base/combining mark; S05 cung cấp tư duy anchor và mark-to-mark. | Unicode/OpenType không mô hình hóa vùng cản bridge; nghiên cứu recognition không quyết định vị trí dấu sinh ra hoặc thứ tự robot thi công. | Đưa ứng viên dấu và vùng cản vào state/transition, đo collision và clearance thay vì chỉ render hậu kỳ; đánh giá placement tách khỏi ordering. |
| RQ3 | S07 và S13 hỗ trợ mô hình độ trơn/động học; S08–S11, S14–S15 cho thấy planning, sequence và physical execution phải được kiểm chứng; S06 hỗ trợ thuật toán chuỗi có cấu trúc. | Không nguồn nào cung cấp ngưỡng latency/clearance dùng trực tiếp cho thiết bị OmniDraw; mô hình brush/robot arm không chuyển nguyên trạng sang plotter hai trục. | Báo cáo độ phức tạp, median/p95 và tách simulator khỏi số đo máy thật; ngưỡng vật lý phải do TV3 hiệu chuẩn. |

## 4. Khoảng trống tạm thời đã thu hẹp

Từ **bộ nguồn hạt giống hiện tại**, có thể phát biểu thận trọng rằng các hướng liên quan thường tách thành ba lớp:

1. mô hình sinh digital ink, phong cách người viết và liên kết theo ngữ cảnh;
2. typography/encoding dùng normalization và mark attachment;
3. robot drawing dùng stroke/path planning để giảm thời gian hoặc bảo đảm thi công.

S16 cho thấy không còn hợp lệ nếu phát biểu chung rằng “chưa có context-aware handwriting generation”; S14 cũng cho thấy robotic sequential writing đã được nghiên cứu bằng mô hình học. Sau citation chaining vòng 1, khoảng trống có thể giữ ở dạng hẹp hơn:

> Chưa tìm thấy trong 16 nguồn đã sàng lọc một hệ thống đồng thời mô hình hóa **ràng buộc chính tả và ứng viên vị trí dấu tiếng Việt + bridge collision/clearance + quyết định allograph/nối–nhấc bút trong finite-state trellis + chi phí thi công single-stroke plotter**.

Đây vẫn là **provisional gap**, không phải tuyên bố “đầu tiên trên thế giới”. Phải hoàn tất team screening, citation chaining vòng 2 và tra cứu prior art gần nhất trước khi đưa vào phần “tính mới”.

## 5. Các nguồn cần tìm thêm

- Công trình chuyên biệt về Vietnamese handwriting synthesis, không chỉ recognition.
- Nghiên cứu định lượng về thứ tự delayed strokes riêng cho chữ viết tay tiếng Việt; S12 mới chỉ bổ sung bằng chứng đa ngôn ngữ cho bài toán xử lý nét trễ.
- Tối ưu toolpath cho pen plotter hai trục có metric pen-up/turning cost.
- Đánh giá legibility/naturalness của chữ viết tay sinh tự động.
- Nguồn peer-reviewed về contextual allograph cho Latin cursive hoặc type design có anchor/entry/exit; S16 mới là preprint và tập trung connectivity/spacing.
- Nghiên cứu human factors để định nghĩa protocol đánh giá tự nhiên, dễ đọc và mức giống phong cách người viết.
