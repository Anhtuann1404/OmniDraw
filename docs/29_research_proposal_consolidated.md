# Đề cương nghiên cứu — bản đối chiếu nguồn đã tinh chỉnh

**Đồng bộ ngày 02/10/2026** từ [Google Docs](https://docs.google.com/document/d/1iyEXfAvh8kaw7xXrF6vM6z6nSn2qfhkG0xmg62eto1Y/edit). Revision nguồn: `ANLCKQldz8jcpvwBNbyq82qDhLfstPrh-4qvmj3tmr0fn-mai05fqjYukJSxx-YAYlG9zj9DsJtfQotVMp34hMA7ujLjagNm-HjBFcZEO64`. Giữ nội dung và các bảng của bản nguồn; bản Markdown phục vụ đối chiếu, không thay bản nộp có định dạng Mẫu 2. Phân công/contract triển khai ở [Docs 30](30_research_development_plan.md), [Docs 31](31_joint_solver_contract.md), [Docs 32](32_research_api_and_artifact_contract.md). ID MT1–MT4 trong đề cương tương ứng N-RQ1–N-RQ4 của tài liệu kỹ thuật; RQ cũ trong báo cáo lịch sử không đổi nghĩa hồi tố.

ĐỀ CƯƠNG ĐỀ TÀI NGHIÊN CỨU KHOA HỌC

TÊN ĐỀ TÀI: Đồng tối ưu hình học–lịch nét cho chữ tiếng Việt: Mô hình tương tác dấu và phân tích độ nhạy theo tham số chuyển động

Lĩnh vực nghiên cứu: Khoa học tự nhiên (Khoa học máy tính và Tự động hóa)

Loại hình đề tài: Nghiên cứu ứng dụng

Giảng viên hướng dẫn (Học hàm, học vị, Họ và tên, Đơn vị công tác):

-TS. Nguyễn Hoàng Hải - Khoa Toán Tin - Trường Đại học Sư phạm

Nhóm sinh viên thực hiện: Nhóm nghiên cứu gồm 04 sinh viên, phân công vai trò Chủ nhiệm (CN) và ba Thành viên (TV1, TV2, TV3) với thông tin chi tiết như sau:

| STT | Thành viên | Họ và tên | MSSV / Lớp | Khoa / Trường | Email& SĐT | Vai trò trong đề tài |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | CN | Nguyễn Tài Anh Tuấn | 3120225170<br>25CNTT3 | Toán-Tin<br>Đại Học Sư Phạm Đà Nẵng | nguyentaianhtuan1407@gmail.com<br>0869693872 | Chủ nhiệm đề tài: Mô hình toán, bộ giải DP, tích hợp và điều phối |
| 2 | TV1 | Nguyễn Hoàng Thắng | 3120225137<br>25CNTT3 | Toán-Tin<br>Đại Học Sư Phạm Đà Nẵng | thanghoangnguyen19012007@gmail.com<br>0792751901 | Thành viên: Quản trị dữ liệu, tập Holdout, âm tiết và font |
| 3 | TV2 | Trần Hồng Khải | 3120225068<br>25CNTT3 | Toán-Tin<br>Đại Học Sư Phạm Đà Nẵng | hongkhai55@gmail.com<br>0768567600 | Thành viên: Đối chứng, mô hình chi phí, thực nghiệm và phân tích |
| 4 | TV3 | Phùng Tấn Minh | 3120225092<br>25CNTT3 | Toán-Tin<br>Đại Học Sư Phạm Đà Nẵng | phgtminh168@gmail.com<br>0905241565 | Thành viên: Bộ vét cạn & hình học độc lập, kiểm chứng và thiết bị |

NỘI DUNG THUYẾT MINH ĐỀ TÀI

## 1. Tóm tắt đề tài (Abstract)

Tóm tắt tiếng Việt:

Đề tài dự kiến nghiên cứu việc lựa chọn đồng thời hình học thân chữ, vị trí dấu và lịch thực hiện nét để tạo quỹ đạo chữ tiếng Việt bằng máy vẽ. Mục tiêu là xác định khi nào đồng tối ưu có lợi so với chọn hình học trước rồi tối ưu lịch, và khi nào hai cách cho kết quả bằng nhau. Phương pháp sẽ xây dựng tập ứng viên hữu hạn, áp dụng quy hoạch động có ràng buộc thứ tự và tối ưu chi phí thời gian ước tính theo mô hình. Bộ giải dự kiến được kiểm chứng bằng vét cạn trên ca nhỏ với các phép tính hình học độc lập, rồi so sánh với tìm kiếm chùm và họ đối chứng phân tầng giữ m cấu hình hình học. Nghiên cứu sẽ khảo sát tương tác dấu, độ rộng biên tương tác, số nét chờ và độ nhạy theo hai tham số chuyển động. Với tập lịch khả thi cố định, sai lệch của một lịch so với tối ưu được phân tích bằng tính lồi và đánh giá tại bốn đỉnh miền tham số. Thực nghiệm được thiết kế trên tập dữ liệu độc lập chưa dùng để tinh chỉnh, với quy tắc đối chứng, điểm vận hành và tiêu chí kết luận đăng ký trước. Thí điểm font và kiểm chứng máy sẽ thực hiện khi điều kiện cho phép. Đóng góp dự kiến gồm mô hình chữ/dấu tiếng Việt, đường cong lợi ích theo m, phân tích có kiểm soát và gói tái lập.

English Abstract:

This proposal investigates the joint selection of glyph geometry, diacritic positions, and stroke schedules for Vietnamese pen-plotter trajectories. It aims to determine when joint optimization improves on a staged approach that selects geometry before optimizing the stroke schedule, and when both approaches produce equal costs. The study will define a finite candidate space and apply precedence-constrained dynamic programming to an estimated motion-time cost model. The solver will be checked against an independently implemented brute-force solver and geometric routines on small test cases, then compared with beam search and two preregistered families of staged top-m baselines. Experiments will examine diacritic interactions, interaction frontier widths, pending strokes, and sensitivity to two motion parameters. For a fixed feasible schedule set with affine costs, convexity of the regret function permits evaluation of its maximum over a rectangular parameter domain at the four vertices. This certificate applies within the specified model and candidate space. The evaluation will use a frozen holdout dataset that is not used for tuning, with baseline rules, an operating point, and decision criteria fixed beforehand. Results will distinguish practically useful improvements, equivalence within the evaluated cases, and insufficient evidence. A selected-font pilot and physical validation are conditional on resources. Expected contributions are a Vietnamese glyph-and-diacritic model, gap curves across m, controlled analysis, and a reproducibility package subject to data and font licenses.

## 2. Tính cấp thiết, ý nghĩa khoa học và thực tiễn của đề tài

### 2.1. Tính cấp thiết

Chữ tiếng Việt kết hợp dấu thanh (sắc, huyền, hỏi, ngã, nặng) với dấu cấu tạo nguyên âm: dấu mũ ở â, ê, ô; dấu trăng ở ă; dấu móc ở ơ, ư. Những chữ và cụm chữ như ế, ề, ể, ệ, ướ, ượ có nhiều dấu với các quan hệ hình học khác nhau. Lựa chọn biến thể thân chữ hoặc vị trí neo dấu có thể thay đổi điểm đầu/cuối nét, khả năng nối nét và quỹ đạo di chuyển của bút trong mặt phẳng.

Trong hệ thống máy vẽ, văn bản cần được chuyển thành các nét hình học và thao tác nâng/hạ bút. Cấu hình cân đối về thị giác chưa chắc có chi phí chuyển động thấp; vị trí dấu và nét nối cần được xét cùng nhau để kiểm soát giao cắt và khoảng hở. Nguyen và cộng sự (2018) giới thiệu cơ sở dữ liệu chữ viết tay trực tuyến tiếng Việt và các thực nghiệm nhận dạng bằng mạng nơ-ron hồi quy. Công trình cung cấp bối cảnh dữ liệu có thông tin trình tự nét; không được dùng làm bằng chứng về hiệu quả tối ưu quỹ đạo máy vẽ hoặc tính hợp lý của cửa sổ trì hoãn trong đề tài.

Đề tài tập trung đánh giá liệu việc lựa chọn hình học và lịch nét đồng thời có đem lại mức giảm chi phí đủ hữu ích so với chi phí tính toán bổ sung, và trong điều kiện nào hai bước có thể tách riêng. Kết quả dự kiến cung cấp căn cứ lựa chọn mức tìm kiếm phù hợp trong mô hình tạo quỹ đạo chữ tiếng Việt.

### 2.2. Ý nghĩa khoa học

Đề tài dự kiến mô hình hóa quan hệ giữa lựa chọn chữ/dấu tiếng Việt, tương tác hình học và cấu hình bút. Phương pháp áp dụng quy hoạch động có ràng buộc thứ tự và các tính chất tối ưu tham số đã có để phân tích bài toán trong tập ứng viên hữu hạn.

Giá trị khoa học nổi bật nằm ở việc thiết lập các điều kiện đủ để phương pháp phân tầng đạt kết quả tương đương đồng tối ưu, xây dựng hàm suy giảm khoảng cách chi phí (gap curve) theo số lượng cấu hình m được giữ lại, và cung cấp bằng chứng định lượng về quy mô trạng thái thực tế (w, b) trên không gian ngữ liệu tiếng Việt có cấu trúc.

Nghiên cứu dự kiến sử dụng bộ kiểm chứng độc lập, quy tắc đối chứng và tiêu chí kết luận đăng ký trước nhằm giảm nguy cơ thiên kiến. Các kết quả có lợi, bằng nhau và chưa đủ bằng chứng đều được báo cáo cùng phạm vi và giới hạn.

### 2.3. Ý nghĩa thực tiễn

Kết quả nghiên cứu dự kiến cung cấp cơ sở định lượng để lựa chọn mức tìm kiếm m phù hợp với ngân sách tính toán, thông qua quan hệ giữa chất lượng nghiệm và thời gian chạy trong môi trường thực nghiệm của đề tài.

Kết quả dự kiến hỗ trợ tạo quỹ đạo chữ tiếng Việt trên máy vẽ hai trục, kiểm soát giao cắt và khoảng hở theo ràng buộc đã xác định. Độ dễ đọc, độ trung thành hình học và sai lệch trên giấy thật cần được đánh giá riêng.

Quy trình neo dấu và tạo nét đơn dự kiến được thí điểm để bổ sung dấu tiếng Việt cho một số font thiết kế có chữ cơ sở và quyền sử dụng phù hợp. Khả năng ứng dụng sẽ được đánh giá theo độ phủ, lỗi hình học, độ dễ đọc, độ trung thành và công sức chỉnh sửa; kết luận phụ thuộc kết quả thí điểm, không áp dụng cho mọi font.

Chức năng chuyển đổi ảnh thành nét vẽ nghệ thuật (Art Mode) được định vị rõ ràng là một phân hệ ứng dụng mở rộng nhằm trình diễn năng lực thiết bị; kết quả chữ viết và vẽ tranh được báo cáo độc lập, minh bạch.

## 3. Tổng quan tình hình nghiên cứu và Tính mới của đề tài

### 3.1. Tổng quan các công trình liên quan

Tổng quan nghiên cứu được nhóm tổ chức có chọn lọc theo ba trục nghiên cứu chính:

- Trục 1 — Tối ưu lịch có ràng buộc thứ tự: Balas (1999) và Balas & Simonetti (2001) nghiên cứu các lớp bài toán người bán hàng và phương pháp quy hoạch động liên quan đến giới hạn thay đổi thứ tự. Nhóm sẽ đối chiếu toàn văn về mô hình lựa chọn, cửa sổ thứ tự, trạng thái và độ phức tạp, ghi rõ bài và số trang cho từng nội dung kế thừa. Việc so sánh với bài toán chữ/dấu tập trung vào lựa chọn hình học có tương tác và vị trí bút phụ thuộc lựa chọn; chưa kết luận rằng các công trình này chỉ xử lý các nút cố định.

- Trục 2 — Biểu diễn và bố trí chữ/dấu: UAX #15 quy định các dạng chuẩn hóa Unicode, trong đó NFD thực hiện phân rã chuẩn tắc (The Unicode Consortium, 2026). Bảng GPOS của OpenType mô tả các cơ chế định vị glyph, gồm định vị dấu theo điểm neo (Microsoft Corporation, n.d.). Các đặc tả này là cơ sở biểu diễn và bố trí ký tự; đề tài sẽ bổ sung mô hình nét đơn và chi phí chuyển động bút cho mục đích tạo quỹ đạo.

- Trục 3 — Phân tích đường đi theo tham số: Chakraborty và cộng sự (2010) nghiên cứu đường đi ngắn nhất với trọng số phụ thuộc một biến chung. Đây là hướng nghiên cứu liên quan; đề tài sử dụng miền hai tham số và lập luận trực tiếp từ tính lồi của sai lệch so với tối ưu cho một lịch cố định, không xem chứng nhận bốn đỉnh là kết quả của bài STACS. Về ứng dụng robot vẽ, Wang và cộng sự (2020) kết hợp chuyển phong cách với tối ưu đường vẽ trong RoboCoDraw. Công trình cung cấp bối cảnh ứng dụng, không trực tiếp xác nhận mô hình tương tác dấu tiếng Việt.

### 3.2. Phân tích "khoảng trống" nghiên cứu và khẳng định Tính mới, sáng tạo của đề tài

- Vấn đề nghiên cứu 1: Làm rõ quan hệ giữa lựa chọn hình học thân chữ/dấu tiếng Việt và lịch nét: khi nào có thể tách hai bước mà vẫn đạt cùng chi phí, khi nào tương tác tạo ra lợi ích của đồng tối ưu. Phạm vi tổng quan sẽ gồm tối ưu lịch có ràng buộc thứ tự, bố trí glyph/dấu và tạo quỹ đạo máy vẽ; nguồn tra cứu, từ khóa và thời điểm tìm kiếm sẽ được ghi lại trong giai đoạn tổng quan.

- Vấn đề nghiên cứu 2: Định lượng đánh đổi giữa chi phí chuyển động và chi phí tính toán khi phương pháp phân tầng giữ m cấu hình hình học, với quy tắc xếp hạng đăng ký trước và cùng tập ứng viên.

- Vấn đề nghiên cứu 3: Đánh giá độ ổn định của lịch nét khi thay đổi hai tham số chuyển động trong miền xác định trước, và giới hạn phạm vi chứng nhận theo mô hình chi phí.

- Đóng góp dự kiến 1 — Mô hình chữ/dấu tiếng Việt: Xây dựng mô hình ứng viên hữu hạn thể hiện tương tác khoảng hở, điểm đầu/cuối nét và lịch bút. Mức độ khác biệt so với các công trình liên quan sẽ được xác định qua tổng quan có đối chiếu.

- Đóng góp dự kiến 2 — Phân tích đồng tối ưu và phân tầng: Báo cáo đường cong gap theo m, điều kiện có lợi hoặc bằng nhau và chi phí tìm kiếm. Điều kiện tách được là kết quả chuẩn được áp dụng; ví dụ glyph tham số hóa phục vụ phân tích trong mô hình, không đại diện cho tần suất lợi ích trên tiếng Việt.

- Nội dung phân tích — Độ nhạy theo tham số: Áp dụng tính lồi của sai lệch để chứng nhận tại bốn đỉnh miền tham số cho một lịch cố định trong tập ứng viên. Đây là công cụ phân tích được áp dụng, không đăng ký một định lý hoặc phương pháp chứng nhận mới.

- Quy trình đánh giá — Kiểm chứng và tái lập: Đối chiếu DP với vét cạn và phép tính hình học độc lập trên ca kiểm thử nhỏ trước khi mở tập đánh giá. Sau đó đánh giá trên tập Holdout với cấu hình đăng ký trước. Quy trình này hỗ trợ độ tin cậy và khả năng tái lập, không được xem riêng là tính mới thuật toán.

## 4. Mục tiêu và Nội dung nghiên cứu

### 4.1. Mục tiêu

- Mục tiêu tổng quát: Xây dựng và đánh giá mô hình đồng tối ưu hình học chữ/dấu và lịch thực hiện nét tiếng Việt; xác định các điều kiện khi nào lựa chọn đồng thời mang lại lợi ích so với phương pháp phân tầng và khi nào hai cách tiếp cận cho kết quả tương đương, trong không gian ứng viên và điều kiện chuyển động được xác định.

- Mục tiêu cụ thể: Được cụ thể hóa thành 4 mục tiêu đo lường được:

| Mục tiêu | Nội dung khoa học | Sản phẩm đo lường | Mức cam kết |
| --- | --- | --- | --- |
| MT1 | Khảo sát quy luật thay đổi của lợi ích đồng tối ưu khi phương pháp phân tầng lưu giữ m cấu hình hình học | Đường cong suy giảm khoảng cách chi phí gap_m theo m; thời gian tính toán tổng; giá trị m* nhỏ nhất đạt biên thực dụng epsilon_eq; điều kiện đủ cho kết quả bằng nhau | Bắt buộc |
| MT2 | Kiểm chứng tính khả thi và đo đạc quy mô không gian trạng thái của mô hình tương tác dấu tiếng Việt | Số vi phạm khoảng hở / va chạm do kiểm tra độc lập phát hiện trên nghiệm xuất ra (kỳ vọng 0); tỷ lệ ca được xác nhận vô nghiệm; cận số trạng thái; phân bố độ rộng biên w và số nét chờ b | Bắt buộc trong phạm vi khóa |
| MT3 | Đánh giá độ ổn định của quyết định lập lịch theo tham số chuyển động và phạm vi chứng nhận sai lệch | Bản đồ phân vùng quyết định (decision map); giá trị sai lệch lớn nhất tại 4 đỉnh miền tham số; chi phí tính toán chứng nhận; số đo kiểm chứng vật lý trên máy thật (nếu có) | Phần mềm: Bắt buộc; Vật lý: Có điều kiện |
| MT4 | Đánh giá năng lực của quy trình ứng viên và neo dấu trong việc hỗ trợ các font thiết kế được lựa chọn | Tỷ lệ bao phủ ký tự tiếng Việt; số lỗi dấu / va chạm; thời gian chỉnh sửa thủ công; điểm đánh giá độ dễ đọc và độ trung thành hình học | Thí điểm có điều kiện |

Ghi chú phạm vi: Đề tài tập trung tối ưu quỹ đạo máy vẽ. Cửa sổ trì hoãn theo loại dấu là cơ chế giới hạn không gian tìm kiếm; chưa coi đó là phép cắt tỉa bảo toàn nghiệm tối ưu của không gian không giới hạn. Việc suy luận thói quen viết cá nhân cần dữ liệu có thứ tự nét và nằm ngoài phạm vi cốt lõi.

### 4.2. Nội dung nghiên cứu

Đề tài triển khai 06 nội dung và nhiệm vụ nghiên cứu khoa học trọng tâm sau:

- Nội dung 1 — Khảo sát cơ sở lý thuyết, mô hình hóa dữ liệu và ràng buộc hình học: Tổng quan có đối chiếu toàn văn các công trình của Balas (1999), Balas & Simonetti (2001), Chakraborty et al. (2010). Xây dựng cấu trúc dữ liệu hình học cho ký tự nét đơn, nét bút, dấu tiếng Việt, tập ứng viên hình học, quan hệ sở hữu dấu và đồ thị tương tác. Khóa danh mục ràng buộc hình học cùng bảng phân loại các trường hợp tiếp xúc hợp lệ có chủ ý.

- Nội dung 2 — Xây dựng bộ giải quy hoạch động: Xác định trạng thái gồm lựa chọn hình học còn ảnh hưởng đến phần chưa vẽ, nét chờ và vị trí bút, cùng thông tin ứng viên của nét vừa thực hiện khi cần. Xây dựng truy hồi Bellman, cận số trạng thái và kiểm chứng trong phạm vi khai báo; không bổ sung hướng tiếp tuyến như một biến tối ưu nếu mô hình chi phí chưa sử dụng nó.

- Nội dung 3 — Xây dựng bộ kiểm chứng độc lập và hệ thống đối chứng: Lập trình bộ giải vét cạn (brute-force) độc lập hoàn toàn với bộ giải DP, tự xây dựng các hàm tính toán khoảng cách, giao cắt và khoảng hở hình học. Xây dựng họ đối chứng phân tầng top-m (với các thang đo H_ref và H_geom), thuật toán tìm kiếm chùm (beam search) và khung chạy thực nghiệm chung với quy tắc xếp hạng đăng ký trước.

- Nội dung 4 — Phân tích lý thuyết điều kiện tương đương, đo đạc cấu trúc và chứng nhận sai lệch: Xây dựng họ ví dụ glyph tham số hóa chứng minh sự tồn tại của lợi ích đồng tối ưu; thiết lập điều kiện đủ để hai phương pháp cho kết quả bằng nhau. Thu thập và phân tích phân bố của độ rộng biên tương tác w và số nét chờ b trên tập âm tiết tiếng Việt chuẩn hóa. Khảo sát độ nhạy tham số chuyển động và thực hiện quy trình chứng nhận sai lệch so với tối ưu tại 4 đỉnh miền (rho, lambda).

- Nội dung 5 — Đóng băng hệ thống, đánh giá thực nghiệm chính thức và chuẩn bị gói tái lập: Khóa toàn bộ phân chia dữ liệu (Dev/Holdout), mã nguồn, tập ứng viên, chỉ số đo lường, biên lợi ích epsilon_eq và điểm vận hành chuẩn (rho_0, lambda_0). Tiến hành đánh giá thực nghiệm chính thức; thống kê chi tiết các ca có lợi, ca bằng nhau, ca vô nghiệm và trường hợp vượt ngưỡng thời gian (timeout); hoàn thiện gói dữ liệu và mã nguồn tái lập (replication package).

- Nội dung 6 — Thí điểm trên font thiết kế và thử nghiệm thiết bị vật lý: Khảo sát các font thiết kế đủ chữ cơ sở và quyền sử dụng; chuyển đổi outline sang nét đơn trong phạm vi xử lý được; tái dựng dấu tiếng Việt theo tọa độ mỏ neo; kiểm tra va chạm hình học và so sánh đối chuẩn với font gốc. Thực hiện kiểm chứng quỹ đạo và đo đạc động học trên máy vẽ hai trục thực tế khi điều kiện thiết bị sẵn sàng.

## 5. Đối tượng, phạm vi và phương pháp nghiên cứu

### 5.1. Đối tượng và phạm vi nghiên cứu

- Đối tượng nghiên cứu: Mối quan hệ tương tác giữa việc lựa chọn hình học thân chữ/dấu tiếng Việt, lịch trình tự thực hiện các nét vẽ và hàm chi phí chuyển động ngòi bút trên máy vẽ tự động hai trục.

- Phạm vi nghiên cứu: Được xác định chặt chẽ qua các giới hạn kỹ thuật:

- Về mặt dữ liệu và ngôn ngữ: Khởi đầu tập trung trên các từ và cụm từ ngắn tiếng Việt với tập glyph nét đơn và không gian ứng viên hữu hạn được khóa trước; không mở rộng ra việc tối ưu hóa trên mọi đường cong hình học liên tục hoặc mọi định dạng font TTF/OTF thương mại.

- Ràng buộc khoảng hở an toàn: Quy định sàn khoảng hở hình học phần mềm c_min = 0,20 mm là một ràng buộc cứng (hard constraint) cho các cặp nét được định nghĩa là phải tách rời; các nghiệm vi phạm sàn này bị loại bỏ ngay lập tức. Các điểm tiếp xúc có chủ ý được gắn nhãn ngoại lệ rõ ràng. Ngưỡng c_min phần mềm được hiểu là điều kiện cần trên mô hình, chưa tự động đồng nhất với khoảng hở vật lý đo được trên giấy thật.

- Phạm vi font thí điểm: Chỉ áp dụng trên các font thiết kế có đầy đủ chữ cái Latin cơ sở, có giấy phép bản quyền phù hợp và có mẫu tham chiếu; không cam kết khôi phục các ký tự cơ sở bị thiếu.

- Phần cứng và thi công vật lý: Thử nghiệm vật lý được thực hiện trên máy vẽ phẳng hai trục khi thiết bị sẵn sàng. Cấu hình truyền động, bộ điều khiển, đầu bút, giấy và tham số chuyển động được ghi nhận trong từng thực nghiệm.

- Phân hệ Art Mode: Là chức năng ứng dụng độc lập chuyển đổi ảnh sang nét vẽ nhằm minh họa khả năng của máy; không đặt thêm câu hỏi nghiên cứu bắt buộc trong đề cương này.

### 5.2. Phương pháp nghiên cứu

- Thiết kế nghiên cứu: Nghiên cứu áp dụng phương pháp kết hợp giữa mô hình hóa toán học hình thức, xây dựng thuật toán tối ưu, kiểm chứng chéo độc lập bằng vét cạn và thực nghiệm định lượng có đối chứng. Mọi phương pháp so sánh đều được thực thi trên cùng một tập ứng viên hình học, cùng hệ thống ràng buộc và cùng hàm chi phí chuẩn hóa. Toàn bộ quy tắc đối chứng, phân chia dữ liệu, điểm vận hành và tiêu chí kết luận đều được đăng ký và đóng băng trước khi chạy thực nghiệm chính thức.

- Mô hình hóa chữ viết và bộ giải DP: Đầu vào gồm văn bản tiếng Việt, kích thước chữ, tập glyph nét đơn và tham số chuyển động; đầu ra dự kiến là cấu hình hình học cùng lịch nét khả thi. Một ứng viên gồm các nét có mã định danh, đường vector, điểm đầu/cuối, quan hệ sở hữu dấu và tiếp xúc được phép. Mỗi chữ có tối đa q ứng viên; n là số chữ; k giới hạn trì hoãn dấu; w là độ rộng biên tương tác; b là số nét chờ. Trạng thái phải giữ các lựa chọn còn ảnh hưởng đến tương lai, nét chờ và vị trí bút, kể cả thông tin ứng viên của điểm cuối khi chữ sở hữu đã ra khỏi biên. Nhóm sẽ phân tích cận số trạng thái theo các tham số này. Nếu tập khả thi là tích Descartes và J(g,s)=A(g)+B(s), phân tầng đạt cùng giá trị với đồng tối ưu khi bước hình học chọn g tối thiểu hóa A(g) và bước lịch chọn s tối thiểu hóa B(s). Kết luận này không tự áp dụng cho mọi quy tắc H_ref hoặc H_geom.

- Đặc tả lịch khả thi dùng chung: Trong mô hình đăng ký, các thân chữ được hoàn tất theo thứ tự trái sang phải; thứ tự các nét bên trong mỗi thân được khai báo trong ứng viên. Mỗi nét được vẽ đúng một lần, với một ứng viên cho mỗi chữ. Dấu chỉ được thực hiện sau khi hoàn tất thân sở hữu. Giới hạn k(j) đếm số thân chữ kế tiếp đã hoàn tất: dấu của chữ i phải được vẽ trước khi bắt đầu thân i+k(j)+1; k(j)=0 yêu cầu vẽ trước thân kế tiếp, và mọi dấu phải hoàn tất trước khi kết thúc từ. Quan hệ thứ tự giữa các dấu, nếu có, được khai báo trước. Chỉ cho phép đảo chiều nét được gắn cờ khả đảo; chiều gốc và chiều đảo là các lựa chọn hữu hạn đã khóa. CONNECT giữ bút hạ khi hai đầu nét trùng tại tiếp xúc được phép theo dung sai đã đăng ký; không tự thêm đường nối chưa có trong ứng viên. Các chuyển tiếp khác dùng LIFT: nâng bút, di chuyển rồi hạ bút. Lịch bắt đầu tại điểm p0 với bút nâng và kết thúc tại p_end với bút nâng; tọa độ và quy ước về hành trình đầu/cuối, chu kỳ nâng/hạ được khóa và tính giống nhau cho mọi phương pháp. Mọi lịch phải qua kiểm tra khoảng hở, giao cắt và tiếp xúc ngoại lệ. Đặc tả này được cụ thể hóa thành dữ liệu kiểm thử trong tháng 1 trước khi viết hai bộ giải.

- Mô hình chi phí và điểm vận hành: T_hat = L_down/v_down + L_up/v_up + tau*N_cycle. L_down và L_up là chiều dài khi bút hạ và nâng (mm); v_down, v_up là vận tốc tương ứng (mm/s); tau là thời gian một chu kỳ nâng/hạ (s); N_cycle là số chu kỳ theo quy ước bắt đầu/kết thúc chung. Chuẩn hóa J = v_down*T_hat = L_down + rho*L_up + lambda*N_cycle, với rho = v_down/v_up và lambda = v_down*tau (mm). Mô hình chưa xét gia tốc; T_hat là thời gian ước tính, khác thời gian thực thi đo máy và thời gian chạy bộ giải. Ưu tiên số đo sơ bộ thiết bị ở tháng 1–2 để xác định miền tham số và điểm vận hành (rho_0, lambda_0). Nếu chưa có máy, sử dụng dải từ tài liệu thiết bị có nguồn và quy trình chọn trên Dev đăng ký trước; công khai căn cứ và giới hạn. Chốt điểm vận hành trước cuối tháng 3, không điều chỉnh điểm này, c_min hoặc quy tắc đồng hạng sau khi mở Holdout. J tại điểm vận hành là chỉ số chính; các chiều dài và số chu kỳ được báo riêng.

- Họ đối chứng phân tầng top-m và tìm kiếm chùm: G là tập cấu hình hình học hoàn chỉnh đã xác định, có tối đa q^n phần tử. Sinh cấu hình theo thứ tự mã định danh cố định; mỗi cấu hình được tính điểm H và xếp theo (điểm H, mã định danh). Có thể duyệt lần lượt và dùng heap giữ top-m để giảm bộ nhớ, nhưng top-m chính xác vẫn cần duyệt hết G nếu không có chứng minh cho phép bỏ qua cấu hình. Hai họ xếp hạng riêng được đăng ký trước. H_ref dùng chi phí một lịch tham chiếu cố định: thân từ trái sang phải, dấu ngay sau thân sở hữu, nâng giữa các nét, cùng vị trí bút ban đầu; không tối ưu lịch ở bước xếp hạng. Lịch tham chiếu không hợp lệ được xếp cuối theo mã định danh, không tự loại cấu hình khỏi G. Mẫu tham chiếu của H_geom là glyph nét đơn mặc định cùng vị trí neo dấu mặc định của font hoặc bộ glyph đầu vào, được cố định trước khi xếp hạng các biến thể. Nếu nguồn không có neo dấu, dùng quy ước neo được đăng ký trước trên Dev; không chọn mẫu tham chiếu theo nghiệm tối ưu hay kết quả Holdout. H_geom chỉ dùng độ lệch hình học với mẫu tham chiếu này: 32 điểm đều theo độ dài cung cho các nét tương ứng, trung bình bình phương khoảng cách rồi trung bình theo nét; giữ vị trí tương đối của dấu khi chuẩn hóa cỡ chữ. Ánh xạ, ngoại lệ và đồng hạng được khóa trước. Lấy m cấu hình đầu danh sách G_m rồi tối ưu lịch chính xác cho từng cấu hình. Với các tập G_m lồng nhau và bài toán thống nhất, J_joint <= J_(m+1) <= J_m; m=|G| cho cùng giá trị với đồng tối ưu. Ca nhỏ chạy mọi m; ca lớn dùng dãy 1,2,4,8,... và toàn bộ nếu hoàn thành. Khóa trước giới hạn số cấu hình, thời gian và bộ nhớ trên Dev; ghi số cấu hình đã duyệt và trạng thái hoàn tất. Nếu dừng trước khi duyệt hết G, không gọi danh sách thu được là top-m toàn cục; báo riêng kết quả thăm dò trên tập con đã sinh, không gộp vào đường gap_m chính thức của G hoặc dùng để chứng nhận toàn cục. Mệnh đề m=|G| chỉ áp dụng khi toàn bộ cấu hình và các bài toán lịch liên quan đã được giải chính xác. Beam search dùng cùng bài toán để so sánh chất lượng và tốc độ. Chi phí tính toán gồm sinh ứng viên, duyệt cấu hình, tính điểm H, xếp hạng và giải lịch; ca vô nghiệm hoặc hết thời gian được báo riêng.

- Quy trình kiểm chứng độc lập và phân tích cấu trúc: TV3 viết bộ vét cạn và phép tính hình học độc lập với DP do CN xây dựng; chỉ chia sẻ đặc tả và dữ liệu thô. Các phép khoảng cách, giao cắt, chồng lấn và khả thi được viết hoặc đối chiếu bằng triển khai độc lập. Ca nhỏ ban đầu dự kiến n<=3, q<=2, k<=1 và tối đa 6 hành động thân/dấu; giới hạn thời gian được chốt trong tháng 1. Bộ kiểm gồm glyph tổng hợp ngẫu nhiên có hạt giống cố định, đoạn suy biến, tiếp xúc hợp lệ, tương tác xa, ca vô nghiệm, đồng hạng và khoảng hở 0,19/0,20/0,21 mm. Đối chiếu tính khả thi và giá trị tối ưu trong dung sai số học đã đăng ký trước mở Holdout; kiểm tra độc lập tính hợp lệ và chi phí của từng lịch xuất ra. Chỉ yêu cầu hai bộ giải xuất cùng lịch khi dùng chung quy tắc phá hòa đã khóa; các lịch tối ưu đồng hạng khác nhau vẫn được chấp nhận; không yêu cầu vét cạn mọi ca Holdout. Tập âm tiết khảo sát w/b có nguồn, quy tắc Unicode và danh mục dữ liệu; báo riêng cận bảo thủ, số trạng thái quan sát và giá trị lớn nhất được liệt kê chính xác. Số vi phạm được đếm theo các cặp nét vi phạm ràng buộc khoảng hở hoặc giao cắt, không tính tiếp xúc được phép. Tỷ lệ vô nghiệm chỉ tính các ca đã chứng minh không có lịch khả thi trong tập ứng viên khóa, trên tổng số ca có kết luận khả thi/vô nghiệm; ca hết thời gian hoặc chưa kết luận được báo riêng.

- Phân tích độ nhạy và chứng nhận sai lệch: Xét tập lịch khả thi Pi hữu hạn, cố định và không phụ thuộc theta=(rho,lambda), với J_sigma(theta) affine. Với lịch pi cố định thuộc Pi, R_pi(theta)=J_pi(theta)-min_{sigma thuộc Pi} J_sigma(theta)=max_{sigma thuộc Pi}[J_pi(theta)-J_sigma(theta)] là hàm lồi. Mỗi điểm trong miền hình chữ nhật là tổ hợp lồi của bốn đỉnh, nên R_pi tại điểm đó không vượt giá trị lớn nhất ở các đỉnh; cực đại trên miền bằng cực đại tại bốn đỉnh. Tính chính xác giá trị tối ưu tại bốn đỉnh đủ để xác định cực đại này; dùng cận dưới hợp lệ cho optimum cho chứng nhận giới hạn trên bảo thủ. Nghiệm heuristic không thay được optimum để chứng nhận chính xác. Kết quả chỉ áp dụng trong tập ứng viên và mô hình; không suy ra nghiệm tối ưu sai lệch lớn nhất thuộc bốn lịch thắng ở đỉnh hoặc chứng nhận cho thời gian máy thật. Báo sai số số học và bản đồ quyết định theo miền tham số.

- Phương pháp thu thập số liệu: Xây dựng tập phát triển Dev và tập đánh giá Holdout chưa sử dụng để tinh chỉnh. Phân nhóm ngữ liệu theo dấu, gồm dấu chồng phía trên, dấu phía dưới và tương tác giữa chữ lân cận; ghi rõ từ thực tế, đoạn thử và dữ liệu tổng hợp. Cỡ mẫu Holdout được chốt cuối tháng 1 theo mục tiêu đánh giá và độ phủ, trước khi xem kết quả đánh giá. Holdout được tách riêng trong tháng 1–2, lưu danh mục, mã băm và nhật ký truy cập; chỉ mở sau kiểm chứng DP–vét cạn và khóa mã/tham số cuối tháng 3. Font hoặc hạt giống của cùng từ không được xem như từ độc lập. Việc mở dữ liệu có kiểm tra chéo bởi hai thành viên. Nếu người giữ dữ liệu tiếp nhận viết bộ vét cạn, quản lý Holdout và nhật ký được bàn giao cho thành viên khác.

- Phương pháp phân tích số liệu: Với cặp có kết quả khả thi và J_m>0, tính gap_m=(J_m-J_joint)/J_m; báo chênh lệch tuyệt đối, trung bình, lớn nhất và theo nhóm dấu. Mẫu số bằng 0, vô nghiệm, hết thời gian hoặc thiếu kết quả được báo riêng, không gán gap=0. Biên thực dụng epsilon_eq được đề xuất tháng 1 dựa trên chi phí tính toán và sai số mô hình nếu có số đo, xin ý kiến GVHD rồi khóa trước đánh giá. Phân biệt ngưỡng bằng nhau số học với biên thực dụng. Kết luận gồm: lợi ích vượt biên, tương đương thực dụng trong tập ca khóa khi max gap_m<=epsilon_eq và đủ kết quả bắt buộc, hoặc chưa đủ bằng chứng khi thiếu độ phủ/kết quả. Không suy rộng thành toàn bộ tiếng Việt. Nếu thực hiện suy luận thống kê, đăng ký phương pháp lấy mẫu, cỡ mẫu, biên và khoảng tin cậy; khoảng tin cậy chưa nằm trong biên tương đương được báo là chưa đủ bằng chứng, không dùng p>0,05 để kết luận tương đương. Thời gian tính toán báo trung vị, p95, môi trường, số lượt làm nóng/đo và toàn bộ chi phí quy trình. Thí điểm font báo độ phủ, lỗi dấu, thời gian sửa tay và độ trung thành; đánh giá người đọc cần quy trình và quyền sử dụng dữ liệu phù hợp.

## 6. Năng lực của nhóm nghiên cứu và Giảng viên hướng dẫn

### 6.1. Nhóm sinh viên thực hiện

- Tổ chức và năng lực thực hiện: Nhóm có kiến thức và kỹ năng về lập trình Python, cấu trúc dữ liệu và thuật toán, hình học tính toán và xử lý dữ liệu tiếng Việt; có kinh nghiệm bước đầu trong xây dựng phần mềm tạo quỹ đạo nét chữ, kiểm thử tự động và quản lý mã nguồn bằng Git. Các thành viên có khả năng phối hợp mô hình hóa bài toán, triển khai quy hoạch động và phương pháp đối chứng, tổ chức dữ liệu thực nghiệm, phân tích kết quả và tích hợp thiết bị. Điểm mạnh của nhóm là sự bổ trợ giữa thuật toán, dữ liệu, kiểm chứng độc lập và phần cứng, phù hợp với yêu cầu nghiên cứu đồng tối ưu hình học chữ/dấu tiếng Việt và lịch thực hiện nét.

- Phân công nhiệm vụ chi tiết: Được xác lập rõ ràng theo chuyên môn:

- Sinh viên chủ nhiệm (CN) — Họ và tên: Nguyễn Tài Anh Tuấn: Chủ trì xây dựng mô hình toán học chữ/dấu tiếng Việt và công thức truy hồi quy hoạch động. Trực tiếp cài đặt bộ giải DP, thiết kế hàm mục tiêu và tích hợp hệ thống phần mềm. Đồng chủ trì nhánh thí điểm font thiết kế; điều phối chung tiến độ và chịu trách nhiệm về tính toàn vẹn của báo cáo tổng kết.

- Thành viên 1 (TV1) — Họ và tên: Nguyễn Hoàng Thắng: Phụ trách thu thập, chuẩn hóa và quản trị kho ngữ liệu tiếng Việt; phân chia và bảo mật tập dữ liệu đánh giá độc lập (Holdout). Khảo sát tập âm tiết tiếng Việt; xác định chuẩn tham chiếu hình học và đồng chủ trì quy trình thí điểm font thiết kế.

- Thành viên 2 (TV2) — Họ và tên: Trần Hồng Khải: Phụ trách tổng quan tài liệu có đối chiếu toàn văn; xây dựng mô hình chi phí động học và các phương pháp đối chứng (H_ref, H_geom, Beam Search). Thiết kế và vận hành chương trình thực nghiệm tự động; xử lý số liệu thống kê và lập bảng biểu phân tích.

- Thành viên 3 (TV3) — Họ và tên: Phùng Tấn Minh: Độc lập xây dựng bộ giải vét cạn (brute-force) và các thư viện hình học kiểm chứng chéo. Tiến hành đối chiếu tính đúng giữa bộ giải DP và bộ vét cạn; phụ trách đo đạc tham số động học thiết bị và vận hành thử nghiệm trên máy vẽ thật.

### 6.2. Thông tin Giảng viên hướng dẫn

- Họ và tên, học hàm, học vị, đơn vị công tác: TS. Nguyễn Hoàng Hải - Khoa Toán Tin - Trường Đại học Sư phạm

- Hướng nghiên cứu chính của giảng viên: ........................................................

- Nội dung hỗ trợ chuyên môn: Định hướng phương pháp luận nghiên cứu; góp ý chuẩn hóa mô hình toán học; giám sát tính khách quan của quy trình kiểm chứng độc lập và phản biện báo cáo tổng kết toàn văn.

## 7. Sản phẩm cam kết của đề tài

### 7.1. Sản phẩm bắt buộc

- 01 báo cáo tổng kết toàn văn, trình bày cơ sở lý thuyết, mô hình, kiểm chứng tính đúng, đánh giá đối chứng, điều kiện có lợi/bằng nhau, độ nhạy và giới hạn. Sản phẩm bắt buộc kèm theo gồm gói tái lập: mã bộ giải, vét cạn độc lập, đối chứng, ca kiểm thử, kịch bản thực nghiệm, cấu hình đăng ký trước và số liệu từng ca; danh mục nguồn, mã băm và nhật ký dữ liệu. Dữ liệu và font được chia sẻ theo giấy phép; phần không được phép công bố có mô tả và hướng dẫn tái lập trong phạm vi quyền sử dụng.

### 7.2. Sản phẩm khác (nếu có)

- Quy trình và nguyên mẫu thí điểm font: Báo cáo thí điểm quy trình tạo nét đơn và tái dựng dấu trên nhóm font thiết kế được chọn, kèm bảng phân tích độ phủ, lỗi dấu và đánh giá độ trung thành phong cách.

- Nguyên mẫu phần mềm tạo quỹ đạo chữ tiếng Việt: Tích hợp mô hình, bộ giải và mô phỏng; chức năng vẽ tranh là ứng dụng trình diễn riêng. Biên bản kiểm chứng trên máy vẽ được bổ sung khi có thiết bị.

- Bản thảo bài báo khoa học (dự kiến): Chuẩn bị theo kết quả nghiên cứu và định dạng của nơi dự kiến gửi; không cam kết được chấp nhận công bố.

## 8. Kế hoạch thực hiện (Tiến độ chi tiết)

Thời gian thực hiện đề tài dự kiến là 08 tháng kể từ ngày được cấp có thẩm quyền phê duyệt chính thức. Tiến độ chi tiết được xác lập qua các giai đoạn:

| STT | Nội dung công việc chi tiết | Người thực hiện | Sản phẩm dự kiến | Thời gian |
| --- | --- | --- | --- | --- |
| 1 | Tổng quan có đối chiếu; khóa đặc tả và hai quy tắc xếp hạng; chốt cỡ mẫu Holdout, đề xuất epsilon_eq và phân chia dữ liệu; phân công kiểm chứng. TV3 chuẩn bị đo sơ bộ hoặc thu tài liệu thiết bị cho miền tham số. | CN, TV2, TV1, TV3 | Bản đặc tả chi tiết, bảng ma trận tài liệu, đề xuất biên epsilon_eq, biên bản phân công. | Tháng 1 |
| 2 | Cài đặt DP, vét cạn và hình học độc lập; đối chứng và chương trình thực nghiệm; xây dựng Dev và ví dụ tham số hóa; tách Holdout. TV3 đo sơ bộ nếu có máy; xác định phương án chọn điểm vận hành trên Dev khi thiếu thiết bị. | CN, TV3, TV2, TV1 | Mã nguồn bộ giải thử nghiệm, mã nguồn bộ vét cạn, bộ fixtures kiểm thử, danh mục Holdout có mã băm. | Tháng 2 |
| 3 | Đối chiếu tính khả thi, giá trị và lịch đại diện giữa DP và vét cạn trên ca nhỏ; phân tích điều kiện bằng nhau và chứng nhận bốn đỉnh; đo w/b; khóa mã, miền tham số, điểm vận hành và tiêu chí trước mở Holdout. | Cả nhóm | Biên bản nghiệm thu kiểm chứng chéo DP–Vét cạn; bảng số liệu w/b; gói cấu hình đóng băng. | Tháng 3 |
| 4 | Mở khóa tập đánh giá độc lập Holdout; chạy thực nghiệm đánh giá chính thức họ đối chứng top-m và Beam Search; thu thập số liệu gap_m, thời gian tính toán và phân tích các ca thất bại. | TV1, TV2, TV3, CN | Bảng dữ liệu thực nghiệm toàn diện, nhật ký chạy máy, phân tích số liệu từng ca thử nghiệm. | Tháng 4 |
| 5 | Hoàn tất phân tích thống kê, xác lập kết luận về điều kiện lợi ích và điều kiện bằng nhau; xây dựng thiết kế và quy trình thí điểm font thiết kế sau khi phần lõi đã kiểm chứng vững chắc. | TV2, CN, TV1 | Báo cáo phân tích chuyên sâu phần lõi; tài liệu đặc tả quy trình tái dựng dấu font thiết kế. | Tháng 5 |
| 6 | Triển khai thí điểm trên nhóm font thiết kế lựa chọn; tiến hành đo đạc thông số và thử nghiệm trên máy vẽ thật (khi có thiết bị); biên soạn các chương của báo cáo tổng kết. | TV1, CN, TV3, TV2 | Báo cáo kết quả thí điểm font; biên bản đo đạc thực nghiệm máy thật (nếu có); dự thảo các chương 1–4. | Tháng 6 |
| 7 | Kết thúc toàn bộ thí điểm và kiểm chứng; ghép nối hoàn chỉnh Báo cáo tổng kết toàn văn đề tài; rà soát trích dẫn khoa học, kiểm tra tính nhất quán số liệu và tuyên bố giới hạn nghiên cứu. | Cả nhóm (CN chủ trì) | Dự thảo Báo cáo tổng kết toàn văn hoàn chỉnh; dự thảo bản thảo bài báo khoa học. | Tháng 7 |
| 8 | Rà soát tổng thể, chỉnh sửa định dạng báo cáo theo quy chuẩn; đóng gói Replication Package; chuẩn bị slide và hồ sơ nghiệm thu; bảo vệ và bàn giao kết quả đề tài. | Cả nhóm (CN điều phối) | 01 Báo cáo tổng kết toàn văn chính thức; gói dữ liệu & mã nguồn tái lập; sản phẩm trình diễn; hồ sơ nghiệm thu. | Tháng 8 |

Kế hoạch quản trị rủi ro và phương án dự phòng:

- Rủi ro tiến độ kiểm chứng (mốc tháng 3): Nếu có nguy cơ chậm tiến độ tại tháng 3, nhóm sẽ ưu tiên cắt giảm phạm vi khảo sát w/b mở rộng trên nhiều ngữ cảnh, chỉ duy trì tập âm tiết có danh mục dữ liệu chuẩn và cận bảo thủ; đồng thời thu hẹp họ ví dụ tham số hóa về mức tối thiểu có thể kiểm chứng được. Ưu tiên hàng đầu là bảo vệ tính đúng đắn của việc đối chiếu DP–Vét cạn, tính công bằng của các đối chứng và tính toàn vẹn của tập Holdout.

- Trường hợp chưa khớp bộ giải: Nếu cuối tháng 3 chưa đối chiếu được tính khả thi và giá trị của DP với vét cạn trong sai số số học đã định, lùi mở Holdout và thí điểm font để xử lý lỗi. Khi có nhiều lịch tối ưu đồng hạng, chỉ so trùng lịch nếu hai bộ giải dùng chung quy tắc phá hòa đã khóa; nếu không, chấp nhận các lịch khác nhau đã được kiểm tra hợp lệ và đạt cùng giá trị trong dung sai số học.

- Rủi ro thiết bị và tải công việc: Nếu chưa có máy, đánh giá phần mềm dùng miền và điểm vận hành từ phương án dự phòng đã đăng ký; công khai giả định và giới hạn, chưa kết luận hiệu quả vật lý. Nếu lõi trễ sang tháng 6, lùi thí điểm font để dành tháng 7–8 hoàn thiện báo cáo và gói tái lập.

## 9. Tài liệu tham khảo

Balas, E. (1999). New classes of efficiently solvable generalized traveling salesman problems. Annals of Operations Research, 86, 529–558. https://doi.org/10.1023/A:1018939709890

Balas, E., & Simonetti, N. (2001). Linear time dynamic-programming algorithms for new classes of restricted TSPs: A computational study. INFORMS Journal on Computing, 13(1), 56–75. https://doi.org/10.1287/ijoc.13.1.56.9748

Chakraborty, S., Fischer, E., Lachish, O., & Yuster, R. (2010). Two-phase algorithms for the parametric shortest path problem. In Proceedings of the 27th International Symposium on Theoretical Aspects of Computer Science (STACS 2010) (LIPIcs, Vol. 5, pp. 167–178). Schloss Dagstuhl–Leibniz-Zentrum für Informatik. https://doi.org/10.4230/LIPIcs.STACS.2010.2452

Microsoft Corporation. (n.d.). GPOS — Glyph positioning table. OpenType Specification. https://learn.microsoft.com/en-us/typography/opentype/spec/gpos

Nguyen, H. T., Nguyen, C. T., Bao, P. T., & Nakagawa, M. (2018). A database of unconstrained Vietnamese online handwriting and recognition experiments by recurrent neural networks. Pattern Recognition, 78, 291–306. https://doi.org/10.1016/j.patcog.2018.01.013

The Unicode Consortium. (2026). Unicode Standard Annex #15: Unicode normalization forms (Revision 58). https://www.unicode.org/reports/tr15/tr15-58.html

Wang, T., Toh, W. Q., Zhang, H., Sui, X., Li, S., Liu, Y., & Jing, W. (2020). RoboCoDraw: Robotic avatar drawing with GAN-based style transfer and time-efficient path optimization. In Proceedings of the AAAI Conference on Artificial Intelligence, 34(6), 10402–10409. https://doi.org/10.1609/aaai.v34i06.6609

Đà Nẵng, ngày ........ tháng ........ năm 2026

| TRƯỞNG KHOA<br>(Ký và ghi rõ họ tên) | GIẢNG VIÊN HƯỚNG DẪN<br>(Ký và ghi rõ họ tên) | SINH VIÊN CHỦ NHIỆM<br>(Ký và ghi rõ họ tên) |
| --- | --- | --- |
| .................................................... | .................................................... | .................................................... |
