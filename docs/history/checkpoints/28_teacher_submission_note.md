> **HISTORICAL_RECORD — không là đặc tả hiện hành.** Đọc [hướng hiện tại](../../README.md), [contract](../../31_joint_solver_contract.md) và [công việc](../../03_current-task.md). Giữ kết luận đúng phạm vi/commit gốc.

<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** Báo cáo/contract/bằng chứng lịch sử. Giữ nguyên số liệu, sign-off và phạm vi bên dưới; không dùng corpus cũ hoặc preflight để nghiệm thu hướng mới. ID RQ/PR trong phần cũ là hệ ký hiệu lịch sử.
> Kế hoạch hiện hành: [Docs 30](../../30_research_development_plan.md); đặc tả [Docs 31](../../31_joint_solver_contract.md) và [Docs 32](../../32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

# Bản đề xuất trao đổi với thầy/cô

Bản dự thảo ngày 01/10/2026 do nhóm chuẩn bị để xin ý kiến; không ghi nhận phản biện nhập vai là ý kiến hoặc phê duyệt của GVHD thật. Phân công và các tham số còn cần được xác nhận trước triển khai.

## 1. Nội dung trao đổi

Thưa thầy/cô, nhóm em muốn xin ý kiến về việc tập trung đề tài OmniDraw vào **đồng tối ưu hình học chữ và thứ tự thực hiện nét/dấu tiếng Việt**. Nhóm giữ nền tảng tạo nét chữ và điều khiển máy viết đã xây dựng, dự kiến phát triển ba nội dung nghiên cứu có liên hệ trực tiếp:

### 1.1. Đồng tối ưu hình học và lịch thực hiện nét/dấu

Phương pháp phân tầng chọn hình học chữ, vị trí dấu trước rồi tối ưu thứ tự thực hiện nét. Các lựa chọn hình học này làm thay đổi điểm bắt đầu/kết thúc, khả năng nối và đường di chuyển để viết dấu. Nhóm muốn nghiên cứu lựa chọn đồng thời biến thể chữ, vị trí dấu, quyết định nối/nâng bút và lịch thực hiện dấu đang chờ.

**Câu hỏi chính:** đồng tối ưu có lợi so với phân tầng trong những cấu trúc chữ/dấu và điều kiện chuyển động nào?

Nhóm đang đối chiếu Balas (1999) và Balas–Simonetti (2001) như nền tảng liên quan về DP cho TSP có ràng buộc thứ tự/cửa sổ. Nhận định cụ thể về giới hạn riêng từng thành phố còn **chưa kiểm chứng toàn văn**; cuối tháng 1 phải có bảng so sánh có số trang, ghi rõ bài nào xử lý trường hợp đó. Nhóm dự kiến kế thừa nền tảng này và kiểm tra cách thích nghi với bài toán glyph. Đóng góp cần xác lập nằm ở mô hình chữ/dấu tiếng Việt, tương tác hình học và phân tích đồng tối ưu so với phân tầng. [Balas 1999](https://link.springer.com/article/10.1023/A:1018939709890), [Balas–Simonetti 2001](https://pubsonline.informs.org/doi/10.1287/ijoc.13.1.56.9748)

Nhóm sẽ định nghĩa tập ứng viên và ràng buộc rõ ràng, xây bộ giải chính xác trong phạm vi xác định, kiểm chứng bằng vét cạn do một thành viên khác viết độc lập, rồi so sánh với họ phân tầng top-m và beam search. Quy tắc xếp hạng hình học phải đăng ký trước; m bằng toàn bộ hình học phải khớp optimum chung nếu giải chính xác. Hai quy tắc xếp hạng sẽ đăng ký trước và báo riêng: chi phí của lịch tham chiếu cố định (đối chứng chính), và độ lệch hình học so với mẫu font (đối chứng bổ sung, không sử dụng lịch hay chi phí di chuyển). Đóng góp được trình bày là **áp dụng và phân tích có kiểm soát**, tập trung vào mô hình chữ/dấu tiếng Việt và quy trình đánh giá chặt . Các chỉ số gồm chi phí thời gian mô hình, quãng đường, số chu kỳ nâng/hạ, khoảng hở, số trạng thái và thời gian giải.

### 1.2. Cửa sổ không đồng nhất và quy mô trạng thái

Cửa sổ theo loại dấu được giữ như **cơ chế giới hạn tìm kiếm**. Nhóm đo tỷ lệ giữ giá trị tối ưu so với cửa sổ đồng nhất rộng nhất và chất lượng ở cùng ngân sách tính toán. Thu hẹp cửa sổ làm thu hẹp tập nghiệm, không mặc định cải thiện optimum. Không kết luận về thói quen viết người trong phạm vi kỳ này. Nhận định liên quan Balas phải được xác nhận bằng toàn văn.

Nhóm đo độ rộng biên tương tác `w` và số nét chờ `b` trên tập âm tiết có nguồn, quy tắc chuẩn hóa và manifest riêng, thay vì chỉ dựa vào 20 từ cũ. Đo theo font, tập ứng viên và cửa sổ đã khai báo; tách số đo thực nghiệm khỏi cận bảo thủ. Các phân bố này biện minh cho quy mô trạng thái trong phạm vi khảo sát, không tự chứng minh mọi từ hoặc mọi font có biên nhỏ.

### 1.3. Độ ổn định theo tham số và chứng nhận có điều kiện

Thời gian ước tính theo mô hình gồm thời gian viết, di chuyển khi nâng bút và thao tác nâng/hạ; chưa mô hình hóa gia tốc, không gọi là thời gian thực thi thực tế. Sau chuẩn hóa:

\[
J=L_{down}+\rho L_{up}+\lambda N_{cycle},
\qquad \rho=v_{down}/v_{up},\quad \lambda=v_{down}\tau.
\]

Nhóm sẽ khảo sát quyết định có thay đổi khi `(ρ,λ)` thay đổi hay không. Với tập nghiệm khả thi cố định và chi phí affine, nhóm có thể dùng giá trị tối ưu ở bốn đỉnh của miền hình chữ nhật `(ρ,λ)` để chứng nhận mức kém tối ưu của một lịch đã chọn. Đây là vận dụng tính chất lồi chuẩn, cần nêu giả thiết rõ; bảo đảm chỉ áp dụng cho tập ứng viên hữu hạn và tập lịch khả thi đã định nghĩa, không bao trùm mọi hình học chữ hoặc thời gian máy thật. Nhóm sẽ trình bày chứng minh: regret của một lịch cố định là maximum các hàm affine nên lồi; giá trị tại một tổ hợp lồi các đỉnh không vượt maximum regret ở các đỉnh.

STACS 2010 nghiên cứu đường đi có trọng số là hàm của một biến chung, nên là hướng liên quan; bài không trực tiếp bao trùm hai tham số hoặc chứng nhận bằng đỉnh của nhóm. [Chakraborty et al. 2010](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.STACS.2010.2452)

### 1.4. Bằng chứng sơ bộ

Nhóm đã thử **56 cấu hình × 25 điểm tham số = 1.400 so sánh DP mẫu–vét cạn**, gồm 1.300 so sánh hữu hạn và 100 xác nhận vô nghiệm; tất cả khớp trong tolerance số. Hai cách giải dùng chung primitive hình học nên chưa thay thế kiểm chứng độc lập giữa thành viên.

Trong đó, 16 cấu hình dùng hai font, bốn mẫu `vẫy`, `iế`, `ướ`, `yệ` và hai cửa sổ. Mẫu đã có dấu chồng `ẫ`, `ế`, `ệ`; chưa bao phủ đủ dấu huyền/hỏi trên dấu mũ và tổ hợp `ượ`. Chưa kết luận độ bao phủ hình học từ Unicode đơn thuần. Các cấu hình này cho **chi phí bằng nhau** giữa đồng tối ưu và baseline phân tầng mẫu tại các điểm đã thử. Trong cùng tập ứng viên và cùng chi phí, optimum đồng tối ưu không thể kém một phương án phân tầng khả thi.

40 ca tổng hợp được sinh ngẫu nhiên theo một khuôn cố định với seed `20260930`, có bổ sung ca vô nghiệm và biến thể bằng nhau. Có 25 ca cho lợi ích tại ít nhất một điểm tham số. Đây là bằng chứng exploration về khả năng xuất hiện lợi ích; chưa phải tỷ lệ lợi ích trên corpus tiếng Việt đại diện.

**Giới hạn phạm vi:** hoãn Pareto/cắt tỉa mở rộng và hiệu chuẩn chủ động khỏi cam kết kỳ này. Ưu tiên họ ví dụ glyph tham số hóa có lợi và điều kiện bằng nhau, rồi kiểm chứng bộ giải một mục tiêu. Chỉ giữ thí điểm font, TV1 và TV4 đồng chủ trì.

Nhóm mong thầy/cô góp ý về mức độ phù hợp của trọng tâm đồng tối ưu, phạm vi đóng góp cần thu hẹp/bổ sung và khả năng hoàn thành kế hoạch dưới đây.

## 2. Tiến độ hợp nhất 8 tháng

Tháng 1 tính từ thời điểm bắt đầu thực hiện đề tài được phê duyệt; chưa gán ngày lịch khi chưa có mốc xác nhận. Đây là **một kế hoạch đề xuất thống nhất cho hướng mới**, cần đồng bộ vào đề cương chính sau khi thống nhất với GVHD.

| Tháng | Công việc và sản phẩm | Chủ trì | Mức ưu tiên / điều kiện |
|---|---|---|---|
| 1 | Khóa đặc tả tối thiểu và quy tắc baseline top-m. Đọc hai bài Balas, nộp bảng so sánh có số trang cuối tháng. Đề xuất ε_eq có căn cứ để GVHD duyệt. TV1 định nghĩa nguồn/cỡ mẫu/quy tắc split mới. TV3 xác nhận oracle tuần đầu, thử primitive độc lập. | TV4 mô hình; TV2 baseline/tài liệu/biên; TV1 split; TV3 oracle | Không chạy coverage rộng trong tháng này. Nếu TV3 không nhận: đề xuất TV1 viết oracle, TV2 nhận quản lý split và nhật ký truy cập; xác nhận bàn giao trước đổi người. |
| 2 | DP một mục tiêu, oracle gồm primitive hình học độc lập/đối chiếu độc lập; runner và baseline top-m. Chạy DEV dấu chồng và ca ngẫu nhiên; lập tập âm tiết có manifest để đo `w/b`; dựng họ ví dụ tham số hóa có lợi trước. TV1 khóa split mới và log truy cập. TV3 đo máy nếu có. | TV4 DP; TV2 runner/baseline và đồng phân tích; TV3 oracle/đo; TV1 dữ liệu | Họ ví dụ và kiểm chứng đi trước; Pareto/cắt tỉa hoãn. Không dùng 20 từ cũ làm HOLDOUT chính. |
| 3 | DP–oracle phải khớp trên phạm vi khóa; kiểm tra primitive, top-m toàn tập và điều kiện bằng nhau. Đo phân bố `w/b` trên tập âm tiết; hoàn thiện chứng nhận bốn đỉnh/độ nhạy trong phạm vi đủ chạy. Khóa mã, ứng viên, metric, điểm vận hành và protocol cuối tháng. | TV4 phương pháp; TV2 phân tích/runner; TV3 kiểm tra độc lập; TV1 quản lý split và nhật ký truy cập | Ưu tiên cắt w/b mở rộng trước, rồi họ ví dụ lớn về ví dụ tối thiểu có kiểm chứng. Nếu mốc kiểm chứng vẫn trượt: chưa mở HOLDOUT/chưa làm font; báo lịch sửa. Không bỏ mốc kiểm chứng độc lập. |
| 4 | Mở split mới sau mốc kiểm chứng, chạy cấu hình đã khóa; 20 từ cũ chỉ bổ sung, báo riêng. Lưu gap theo m, thời gian tổng, ca vô nghiệm/timeout và kết quả bằng nhau. | TV1 quản lý split và nhật ký truy cập; TV2 đánh giá; TV3 kiểm tra độc lập; TV4 cơ chế | Bắt buộc. Không sửa baseline, biên hoặc tham số theo HOLDOUT. |
| 5 | Hoàn tất phân tích chính thức, điều kiện lợi ích/bằng nhau, chi phí chứng nhận. TV1 và TV4 chốt thiết kế pilot font, giấy phép và chuẩn tham chiếu; chỉ khởi động khi lõi đã tái lập được. | TV2 kết quả; TV4 phương pháp; TV1 + TV4 font; TV3 kiểm tra độc lập | Không mở Pareto/cắt tỉa. Font có điều kiện theo mốc kiểm chứng lõi. |
| 6 | Thí điểm font trên tập được chọn, không cam kết mọi font. TV3 kiểm chứng lõi trên máy nếu có, báo thời gian đo riêng. Mỗi thành viên viết phần phụ trách. | TV1 dữ liệu/chuẩn/đánh giá font; TV4 ứng viên/tích hợp font; TV3 máy; TV2 bản thảo | TV1 và TV4 đồng chủ trì font. Nếu lõi trễ lấn tháng 6, hoãn font để giữ thời gian báo cáo. |
| 7 | Kết thúc thí điểm/kiểm chứng, không mở nhánh mới. Hoàn thiện giới hạn glyph thật và bản thảo báo cáo/bài báo. | TV2 biên tập kết quả; TV4 phương pháp; TV1 dữ liệu/font; TV3 kiểm chứng | Báo cáo lõi bắt buộc; không cam kết lý thuyết mới chỉ vì áp dụng kết quả chuẩn. |
| 8 | Review nội bộ, sửa bản thảo, hoàn thiện gói tái lập, bảo vệ và bàn giao. Chọn nơi gửi bài theo kết quả và GVHD. | Cả nhóm; TV4 điều phối | Báo cáo bắt buộc; không cam kết được nhận bài tháng 8. |

TV2 là **Trần Hồng Khải**. TV1/TV3/TV4 là ký hiệu thành viên trong bản phân công đề xuất; nhóm sẽ xác nhận người phụ trách trước triển khai.

## 3. Các mốc khóa và phương án hoàn thành tối thiểu

- **Ưu tiên nguồn điểm vận hành:** số đo thiết bị đến kịp trước khóa cuối tháng 3; nếu không có, chọn trên DEV theo quy trình định trước và công khai tiêu chí/nguồn. Nếu chọn để đạt ngưỡng RQ1, phải nêu rõ trong báo cáo.
- TV1 lập split mới chưa dùng để tinh chỉnh trong tháng 1–2 và khóa nhật ký truy cập; 20 từ cũ chỉ là đánh giá bổ sung. Cỡ mẫu mới còn pending, phải chốt trước đánh giá.
- Sau khi mở HOLDOUT, không đổi `(ρ₀,λ₀)`, `c_min`, ứng viên, mã solver hoặc quy tắc chọn nghiệm cho thí nghiệm đã đăng ký. Lỗi cần sửa được ghi nhận thành phiên bản/thí nghiệm mới và báo GVHD; không thay kết quả cũ âm thầm.
- Pareto/cắt tỉa mở rộng hoãn khỏi cam kết kỳ này. Không triển khai trước khi bộ giải một mục tiêu và phân tích cơ chế hoàn tất.
- Chỉ giữ thí điểm font RQ5, TV1 và TV4 đồng chủ trì, chuẩn bị tháng 5 và thử tháng 6–7 sau mốc kiểm chứng lõi. RQ4 Writer Profile hoãn khỏi cam kết kỳ này; mã/protocol đã có giữ làm nền cho giai đoạn sau. Vật lý là kiểm chứng lõi nếu có máy. Art Mode giữ là chức năng ứng dụng, không thêm nhánh nghiên cứu bắt buộc.
- Nếu thiếu thiết bị, thí điểm không thành công hoặc HOLDOUT bằng nhau, phần bắt buộc vẫn gồm mô hình, bộ giải có kiểm chứng, oracle độc lập, đối chứng mạnh, điều kiện đủ cho bằng nhau, họ ví dụ hiện thực hóa được có lợi, chứng nhận trong tập ứng viên và đánh giá chính thức. Không hứa chứng minh đồng tối ưu vượt trội trên glyph thật; kết quả bằng nhau được công bố theo tiêu chí đã đăng ký trước đánh giá.
- Nếu thiếu thời gian trong lõi, cắt khảo sát w/b mở rộng trước, sau đó rút họ ví dụ lớn/ánh xạ glyph thật về ví dụ tối thiểu kiểm chứng được; không cắt kiểm chứng độc lập hoặc công bằng baseline.
- Nếu mốc kiểm chứng lõi cuối tháng 3 chưa đạt, chưa mở HOLDOUT. Chưa bắt đầu font; dừng mở rộng ứng viên/ngữ cảnh dài, ưu tiên sửa lõi trong phạm vi công khai và thống nhất lịch mới với GVHD. Nếu lấn tháng 6, hoãn font để giữ lịch báo cáo.
