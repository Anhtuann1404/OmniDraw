# Đề cương đề tài nghiên cứu khoa học

**Tên đề tài:** Mô hình đồng tối ưu hình học và lịch thực hiện nét chữ tiếng Việt dưới ràng buộc tương tác dấu và bất định tham số chuyển động

**Lĩnh vực nghiên cứu:** Khoa học tự nhiên — Khoa học máy tính và Tự động hóa.

**Loại hình đề tài:** Nghiên cứu ứng dụng.

**Giảng viên hướng dẫn — học hàm, học vị, họ tên, đơn vị công tác:** ........................................................

**Nhóm sinh viên thực hiện:** CN là chủ nhiệm; TV1, TV2 và TV3 là ba thành viên, tương ứng với bảng phân công dưới đây.

| Thành viên | Họ và tên | MSSV / Lớp | Khoa / Trường | Email / SĐT | Vai trò |
|---|---|---|---|---|---|
| CN | ................ | ................ | ................ | ................ | Chủ nhiệm; mô hình, bộ giải và tích hợp |
| TV1 | ................ | ................ | ................ | ................ | Dữ liệu; đồng chủ trì font |
| TV2 | ................ | ................ | ................ | ................ | Đối chứng, chương trình thực nghiệm và phân tích |
| TV3 | ................ | ................ | ................ | ................ | Bộ vét cạn độc lập, kiểm chứng và thiết bị |

**NỘI DUNG THUYẾT MINH ĐỀ TÀI**

## 1. Tóm tắt đề tài (Abstract)

Đề tài nghiên cứu việc lựa chọn đồng thời hình học thân chữ, vị trí dấu và lịch thực hiện nét để tạo quỹ đạo chữ tiếng Việt bằng máy vẽ. Mục tiêu là xác định khi nào đồng tối ưu có lợi so với chọn hình học trước rồi tối ưu lịch, và khi nào hai cách cho kết quả bằng nhau. Phương pháp xây dựng tập ứng viên hữu hạn, áp dụng quy hoạch động có ràng buộc thứ tự và tối ưu chi phí thời gian ước tính theo mô hình. Bộ giải dự kiến được kiểm chứng bằng vét cạn với phép tính hình học độc lập, so sánh với tìm kiếm chùm và họ đối chứng phân tầng giữ m cấu hình hình học. Nghiên cứu khảo sát tương tác dấu chồng, độ rộng biên tương tác, số nét chờ và độ nhạy theo hai tham số chuyển động. Sai lệch của một lịch cố định so với tối ưu được chứng nhận tại bốn đỉnh miền tham số trong tập ứng viên đã xác định. Đánh giá sử dụng tập dữ liệu độc lập chưa dùng để tinh chỉnh; quy tắc đối chứng, điểm vận hành và tiêu chí kết luận được đăng ký trước. Thí điểm font thiết kế và kiểm chứng máy được thực hiện khi điều kiện cho phép. Đóng góp dự kiến là mô hình chữ/dấu tiếng Việt và phân tích có kiểm soát, kèm quy trình kiểm chứng và dữ liệu tái lập.


## 2. Tính cấp thiết, ý nghĩa khoa học và thực tiễn của đề tài

### 2.1. Tính cấp thiết

Các tổ hợp như ế, ề, ể, ệ, ướ và ượ đặt ra quan hệ hình học giữa thân chữ, dấu cấu tạo nguyên âm và dấu thanh. Lựa chọn biến thể chữ hoặc vị trí dấu thay đổi điểm đầu/cuối nét, khả năng nối và đường di chuyển bút. Đề tài cần làm rõ việc chọn hình học và lịch nét đồng thời có đáng trả thêm chi phí tính toán hay không, thay vì chỉ giả định rằng ghép thêm một bộ tối ưu sẽ tốt hơn.

Trong hệ thống viết bằng máy, văn bản phải được chuyển thành các đường hình học để bút thực hiện. Chữ tiếng Việt có dấu cấu tạo nguyên âm và dấu thanh; vị trí các dấu ảnh hưởng đến khoảng hở với thân chữ và chữ lân cận. Vì vậy, một hình dạng chữ phù hợp về mặt thị giác chưa chắc tạo ra quỹ đạo di chuyển bút có chi phí thấp. Nghiên cứu mối quan hệ này là cơ sở để xây dựng phương pháp tạo quỹ đạo có kiểm soát cho chữ tiếng Việt.

### 2.2. Ý nghĩa khoa học

Đề tài mô hình hóa lựa chọn chữ/dấu có tương tác hình học và cấu hình bút phụ thuộc lựa chọn; áp dụng các kết quả tối ưu chuẩn trong một phạm vi được khai báo. Giá trị nghiên cứu dự kiến nằm ở phân tích điều kiện có lợi/bằng nhau, đường gap theo số hình học được giữ, và bằng chứng về quy mô trạng thái trên dữ liệu cấu trúc tiếng Việt. Một quy trình đánh giá có đối chứng và kiểm chứng độc lập cho phép báo cáo kết quả bằng nhau mà không biến nó thành tuyên bố ưu thế chưa được chứng minh.

### 2.3. Ý nghĩa thực tiễn

Kết quả hỗ trợ chọn mức tìm kiếm phù hợp với chi phí tính toán, tạo quỹ đạo chữ Việt có kiểm tra hình học và nhận biết các quyết định nhạy với tham số chuyển động. Thí điểm font có thể hỗ trợ dựng lại dấu trên các font đủ chữ cơ sở và có quyền sử dụng phù hợp. Chức năng vẽ tranh giữ vai trò ứng dụng chuyển ảnh thành nét vẽ, báo cáo riêng; hiệu quả chữ viết không được dùng thay cho đánh giá vẽ tranh.

## 3. Tổng quan tình hình nghiên cứu và Tính mới của đề tài

### 3.1. Tổng quan các công trình liên quan

Balas (1999) nghiên cứu các lớp bài toán người bán hàng tổng quát có thể giải hiệu quả. Balas và Simonetti (2001) trình bày quy hoạch động cho các lớp bài toán người bán hàng có ràng buộc thứ tự. Các công trình này cung cấp nền tảng để giới hạn phạm vi thay đổi thứ tự và tổ chức trạng thái tìm kiếm. Việc áp dụng cho chữ viết cần bổ sung lựa chọn biến thể hình học, quan hệ giữa thân chữ và dấu, cùng thông tin vị trí bút phụ thuộc lựa chọn đó. Trong giai đoạn tổng quan, nhóm sẽ đối chiếu toàn văn về giả thiết, trạng thái và độ phức tạp để xác định chính xác phần kế thừa và phần mô hình hóa cho tiếng Việt.

Chakraborty và cộng sự (2010) nghiên cứu đường đi ngắn nhất tham số với trọng số là hàm của một biến chung. Công trình này cung cấp bối cảnh cho phân tích đường đi theo tham số; phạm vi một biến khác với miền hai tham số của đề tài. Chứng nhận trong đề tài sẽ được lập luận từ tính lồi của sai lệch so với tối ưu đối với một lịch cố định.

Tổng quan được tổ chức theo ba nhóm: tối ưu lịch có ràng buộc thứ tự; lựa chọn và bố trí hình học chữ/dấu; phân tích quyết định theo tham số chi phí. Việc so sánh tập trung vào giả thiết, đại lượng tối ưu, ràng buộc hình học và phạm vi kiểm chứng của từng phương pháp.

### 3.2. Phân tích "khoảng trống" nghiên cứu và khẳng định Tính mới, sáng tạo của đề tài

Khoảng trống đề tài tập trung khảo sát là mối liên hệ giữa chọn hình học thân chữ/dấu tiếng Việt và lập lịch thực hiện nét: khi nào hai bước có thể tách riêng mà vẫn đạt cùng chi phí, khi nào tương tác giữa các lựa chọn khiến cần tối ưu đồng thời, và lợi ích đó có đáng với chi phí tính toán hay không. Các tổ hợp dấu chồng là nhóm trường hợp cần được kiểm tra có chủ đích.

Tính mới dự kiến nằm ở mô hình hữu hạn cho chữ/dấu tiếng Việt, trong đó lựa chọn hình học tác động đồng thời đến ràng buộc khoảng hở, điểm đầu/cuối nét và lịch di chuyển bút; cùng quy trình đánh giá lợi ích theo số cấu hình hình học được giữ. Đề tài áp dụng và phân tích có kiểm soát các công cụ quy hoạch động và tối ưu tham số đã có, kết hợp kiểm chứng hình học độc lập và đánh giá trên dữ liệu chưa dùng để tinh chỉnh.

Đóng góp được xác định trong phạm vi mô hình và tập ứng viên nghiên cứu. Nếu hai cách tối ưu cho kết quả bằng nhau, phân tích điều kiện bằng nhau, mức tìm kiếm cần thiết và chi phí chứng nhận vẫn là kết quả nghiên cứu cần báo cáo.

## 4. Mục tiêu và Nội dung nghiên cứu

### 4.1. Mục tiêu

Mục tiêu tổng quát là xây dựng và đánh giá mô hình đồng tối ưu hình học chữ/dấu và lịch nét tiếng Việt, xác định khi nào lựa chọn đồng thời tạo lợi ích so với phân tầng và khi nào không, trong tập ứng viên và điều kiện chuyển động được khai báo.

Các mục tiêu cụ thể và đại lượng đánh giá gồm:

| Mục tiêu | Nội dung | Sản phẩm đo lường | Mức cam kết |
|---|---|---|---|
| 1 | Lợi ích đồng tối ưu thay đổi thế nào khi phân tầng giữ m hình học? | Gap theo m, thời gian tổng, m nhỏ nhất đạt biên thực dụng; điều kiện có lợi/bằng nhau | Bắt buộc |
| 2 | Mô hình tương tác dấu có kiểm soát khả thi và quy mô trạng thái được không? | Khoảng hở/va chạm, cận trạng thái, phân bố độ rộng biên w và số nét chờ b | Bắt buộc trong phạm vi khóa |
| 3 | Quyết định ổn định thế nào theo tham số chuyển động và chứng nhận được đến đâu? | Bản đồ quyết định, sai lệch so với tối ưu bốn đỉnh, chi phí chứng nhận; số đo máy nếu có | Phần mềm bắt buộc; vật lý có điều kiện |
| 4 | Quy trình ứng viên và neo dấu hỗ trợ font thiết kế được chọn đến đâu? | Độ phủ, lỗi dấu, mức sửa tay, dễ đọc và độ trung thành hình học | Một thí điểm có điều kiện |

Nghiên cứu tập trung vào tối ưu quỹ đạo chữ viết bằng máy. Cửa sổ trì hoãn theo loại dấu được sử dụng như cơ chế giới hạn tìm kiếm; việc suy luận thói quen viết cá nhân cần dữ liệu có thứ tự nét và nằm ngoài phạm vi này.

### 4.2. Nội dung nghiên cứu

Nội dung 1: Tổng quan cơ sở lý thuyết, xây dựng cấu trúc dữ liệu chữ/nét/dấu, ứng viên hình học, quan hệ sở hữu và đồ thị tương tác; khóa ràng buộc cùng các ngoại lệ tiếp xúc hợp lệ.

Nội dung 2: Xây dựng bộ giải quy hoạch động (DP) một mục tiêu có biên tương tác và nét chờ; xác định đủ thông tin trạng thái, cấu hình bút và cận phụ thuộc tham số trước khi tuyên bố khả năng mở rộng.

Nội dung 3: Xây bộ vét cạn và phép tính hình học độc lập; họ đối chứng phân tầng top-m, tìm kiếm chùm (beam search) và chương trình thực nghiệm chung với quy tắc xếp hạng đăng ký trước.

Nội dung 4: Dựng ví dụ glyph tham số hóa có lợi, điều kiện đủ cho bằng nhau; đo w/b trên tập âm tiết có danh mục dữ liệu và khảo sát độ nhạy/chứng nhận sai lệch so với tối ưu.

Nội dung 5: Khóa phân chia dữ liệu, mã, ứng viên, chỉ số đánh giá, biên và điểm vận hành; chạy đánh giá chính thức, phân tích kết quả bằng nhau, vô nghiệm và hết thời gian tính toán; chuẩn bị gói tái lập.

Nội dung 6: Thí điểm trên các font thiết kế được lựa chọn: kiểm tra chữ cơ sở và quyền sử dụng, chuyển hình dạng cơ sở thành nét đơn trong phạm vi có thể xử lý, dựng dấu theo điểm neo, kiểm tra va chạm và so sánh với font gốc hoặc bản chỉnh tay. Kiểm chứng quỹ đạo trên máy được thực hiện khi có thiết bị.

## 5. Đối tượng, phạm vi và phương pháp nghiên cứu

### 5.1. Đối tượng và phạm vi nghiên cứu

Đối tượng là quan hệ giữa lựa chọn hình học chữ/dấu, lịch thực hiện nét và chi phí chuyển động bút. Phạm vi khởi đầu gồm từ/đoạn ngắn với tập glyph nét đơn và ứng viên hữu hạn; không tối ưu trên mọi hình học liên tục hoặc mọi TTF/OTF.

Sàn khoảng hở phần mềm c_min = 0,20 mm là ràng buộc cứng cho các cặp được đặc tả là cần tách rời; nghiệm vi phạm bị loại. Các tiếp xúc có chủ ý được gắn nhãn và xử lý theo quy tắc đã định. Ngưỡng này chưa tự bảo đảm khoảng hở trên giấy thật.

Font thí điểm phải đủ chữ cơ sở, quyền sử dụng và tham chiếu phù hợp; không cam kết khôi phục glyph cơ sở thiếu. Thử nghiệm vật lý sử dụng máy vẽ hai trục khi có thiết bị; cấu hình máy, bút, giấy và điều kiện đo được ghi nhận. Vẽ tranh là chức năng ứng dụng riêng, không mở thêm câu hỏi nghiên cứu bắt buộc.

### 5.2. Phương pháp nghiên cứu

**Thiết kế nghiên cứu**

Nghiên cứu kết hợp mô hình hóa toán học, xây dựng bộ giải, kiểm chứng bằng vét cạn và thực nghiệm so sánh. Các phương pháp được đánh giá trên cùng tập ứng viên, ràng buộc khả thi và hàm chi phí. Quy tắc đối chứng, dữ liệu đánh giá, điểm vận hành và tiêu chí kết luận được xác định trước khi chạy đánh giá chính thức.

**Mô hình chữ và bộ giải**

Đầu vào dự kiến gồm văn bản tiếng Việt, kích thước chữ, tập hình dạng chữ và các tham số chuyển động bút. Đầu ra là lựa chọn hình học cho từng chữ/dấu và một lịch thực hiện các nét thỏa ràng buộc. Trong đề tài, glyph là hình dạng của một ký tự; glyph nét đơn được biểu diễn bằng các đường mà bút có thể đi theo. Một ứng viên là một phương án hình học hợp lệ của chữ và dấu đi kèm. Lịch nét quy định thứ tự thực hiện, chiều đi của nét trong phạm vi cho phép và các thao tác nâng/hạ bút.

Một ứng viên glyph gồm các nét có mã định danh, đường hình học, điểm đầu/cuối, quan hệ sở hữu dấu và các tiếp xúc được phép. Mỗi chữ có tối đa q ứng viên; k giới hạn trì hoãn dấu, w là độ rộng biên tương tác và b là số nét chờ. Bộ giải giữ các lựa chọn hình học còn ảnh hưởng đến phần chưa vẽ, tập nét chờ và cấu hình bút. Nhóm xây dựng công thức truy hồi và cận số trạng thái theo các tham số này, bao gồm thông tin ứng viên gắn với điểm cuối bút; đối chiếu cận với trạng thái thực tế.

Phân tích điều kiện bằng nhau bắt đầu từ mô hình tách được: nếu tập khả thi là tích của hai tập lựa chọn và chi phí có dạng A(g)+B(s), hai bước tối ưu riêng đạt cùng giá trị với tối ưu chung. Khi tương tác phá vỡ điều kiện này, nhóm dựng họ glyph tham số hóa có thể kiểm tra hình học để khảo sát chênh lệch, rồi kiểm tra các trường hợp chữ Việt thực tế. Ví dụ tổng hợp chứng minh sự tồn tại lợi ích trong mô hình, không đại diện cho tần suất lợi ích trên ngôn ngữ.

**Mô hình chi phí và điểm vận hành**

Dùng thời gian ước tính theo mô hình:

T_hat = L_down / v_down + L_up / v_up + τ N_cycle.

Trong đó L_down và L_up là chiều dài quỹ đạo khi bút hạ và nâng; v_down, v_up là vận tốc tương ứng; τ là thời gian một chu kỳ nâng/hạ; N_cycle là số chu kỳ. Chiều dài tính bằng mm, vận tốc bằng mm/s và thời gian bằng giây.

Chuẩn hóa: J = v_down T_hat = L_down + ρ L_up + λ N_cycle; ρ = v_down/v_up, λ = v_down τ. Một chu kỳ nâng/hạ được đếm theo quy ước bắt đầu/kết thúc thống nhất. Mô hình chưa có gia tốc; thời gian chạy bộ giải, thời gian mô hình và thời gian thực thi đo máy là ba chỉ số khác nhau.

Ưu tiên đo thiết bị để chọn điểm vận hành (ρ₀, λ₀) trước khóa cuối tháng 3. Nếu thiếu máy, dùng quy trình lựa chọn trên tập phát triển được đăng ký trước và công khai nguồn dải, tiêu chí chọn. Không đổi điểm vận hành, c_min hoặc quy tắc đồng hạng sau mở đánh giá chính. Chỉ số chính là chi phí J tại điểm vận hành đã xác định; quãng đường khi vẽ, quãng đường khi nâng bút và số chu kỳ nâng/hạ được báo cáo riêng để giải thích đánh đổi.

**Đối chứng phân tầng top-m**

G ký hiệu tập cấu hình hình học hoàn chỉnh được xác định và khóa trước đánh giá. Xếp hạng trước, lấy tập đầu danh sách G_m, rồi tối ưu lịch chính xác cho từng cấu hình trong tập đầu danh sách. Đối chứng chính H_ref dùng chi phí một lịch tham chiếu cố định: thân trái sang phải, dấu ngay sau thân sở hữu, nâng giữa các nét, cùng vị trí bút ban đầu. Không tối ưu lịch ở bước xếp hạng. Nếu lịch tham chiếu không hợp lệ hoặc thiếu ánh xạ nét hình học, xếp ứng viên cuối theo mã định danh dùng phân xử đồng hạng; không tự loại cấu hình có thể còn lịch khả thi khác. Đối chứng bổ sung H_geom chỉ dùng độ lệch hình học so với mẫu font; không dùng lịch, vị trí bút ban đầu hoặc tham số chuyển động.

H_geom dự kiến dùng các nét có ID tương ứng, lấy 32 điểm đều theo độ dài cung, tính trung bình bình phương khoảng cách rồi trung bình theo nét. Mẫu tham chiếu, chuẩn hóa cỡ chữ, ánh xạ nét, ngoại lệ và mã định danh dùng phân xử đồng hạng phải được đăng ký trước. Đây là chỉ số đại diện cho độ trung thành hình học, không phải thang đo thẩm mỹ con người. Hai họ được báo riêng, không chọn họ có gap lớn hơn sau khi xem tập đánh giá độc lập.

J_m = min theo g thuộc G_m của chi phí lịch khả thi tốt nhất; J_joint là giá trị nhỏ nhất trên toàn bộ G. Với các tập đầu danh sách lồng nhau và giải chính xác: J_joint ≤ J_(m+1) ≤ J_m. Khi m = |G|, giá trị phải bằng đồng tối ưu. m=1 chỉ giữ ít lựa chọn nhất trong họ, không được gọi là đối chứng yếu nói chung.

Ca nhỏ chạy mọi m; ca lớn dùng dãy 1, 2, 4, 8,… và toàn bộ nếu hoàn thành. Báo cả sinh/xếp hạng hình học, giải lịch, bộ nhớ và hết thời gian tính toán; tập đầu danh sách vô nghiệm không được gán gap 0. Beam search dùng cùng bài toán, đo chất lượng và tốc độ; bộ giải chính xác cung cấp chứng nhận ngay cả khi heuristic tìm cùng giá trị.

**Kiểm chứng độc lập và phân tích cấu trúc**

Người viết bộ vét cạn dự kiến khác người viết bộ giải quy hoạch động. Bộ vét cạn tự duyệt lịch, tính chi phí và viết hoặc đối chiếu độc lập các phép tính khoảng cách, giao cắt, chồng lấn và khoảng hở. Chỉ chia sẻ cấu trúc dữ liệu/hình học thô, không dùng chung kết luận khả thi. Bộ ca kiểm gồm đoạn suy biến, tiếp xúc hợp lệ, dưới/đúng/trên sàn, tương tác xa, vô nghiệm và nhiều nghiệm bằng nhau; ca ngẫu nhiên có hạt giống cố định.

Ca nhỏ khởi đầu đề xuất n ≤ 3 chữ, q ≤ 2 cấu hình/chữ, k ≤ 1 và tối đa 6 hành động thân/dấu. Đây là giới hạn thử ban đầu, phải khóa cùng giới hạn thời gian tính toán trong tháng 1; không coi đủ để xác nhận mọi từ dài. Bộ vét cạn và DP được đối chiếu cả giá trị, lịch đại diện và khả thi.

Tập âm tiết khảo sát w/b có nguồn, quy tắc Unicode, độ phủ và danh mục dữ liệu riêng. w là số chữ cần giữ lựa chọn ở biên tương tác; b là số hành động nét phụ/dấu đang chờ. Báo theo font, ứng viên, cửa sổ; phân biệt giá trị lớn nhất được liệt kê chính xác, số quan sát trên đường chạy và cận bảo thủ. Phân bố thực nghiệm hỗ trợ cận lý thuyết trong phạm vi khảo sát, không chứng minh mọi font có biên nhỏ.

**Phân tích độ nhạy và chứng nhận sai lệch so với tối ưu**

Với tập lịch khả thi Π cố định và chi phí là hàm affine, tức hàm tuyến tính cộng hằng số, theo θ=(ρ,λ), giá trị tối ưu V(θ)=min J_σ(θ). Sai lệch so với tối ưu của lịch cố định π là R_π(θ)=max theo σ thuộc Π của [J_π(θ)−J_σ(θ)], nên lồi. Tại một tổ hợp lồi các đỉnh, sai lệch so với tối ưu không vượt giá trị lớn nhất ở các đỉnh; do đó giá trị lớn nhất trên hình chữ nhật đạt ở một trong bốn đỉnh.

Bốn giá trị tối ưu chính xác ở đỉnh đủ chứng nhận sai lệch so với tối ưu của lịch cố định trong tập ứng viên này. Nếu dùng cận dưới cho giá trị tối ưu, phải báo chứng nhận bảo thủ; nghiệm heuristic không thay được bộ vét cạn theo cách làm giảm sai lệch so với tối ưu giả. Không suy ra lịch tối ưu sai lệch lớn nhất thuộc bốn lịch thắng ở đỉnh, hoặc chứng nhận áp dụng cho thời gian máy thật. Triển khai phải báo sai số số học và giới hạn số học.

**Phương pháp thu thập số liệu**

Dữ liệu gồm tập phát triển để xây dựng mô hình và tập đánh giá độc lập chưa dùng để lựa chọn tham số. Nhóm xây dựng danh sách từ/đoạn chữ tiếng Việt, phân nhóm theo tổ hợp dấu và bổ sung các trường hợp dấu chồng như ế, ề, ể và ượ. Từ thực tế, đoạn thử kỹ thuật và glyph tổng hợp được ghi nhãn riêng. Các trường hợp tổng hợp gồm mẫu dựng có kiểm soát và mẫu ngẫu nhiên với hạt giống cố định, phục vụ kiểm tra khả thi và tính đúng của bộ giải.

Cỡ mẫu đánh giá được xác định trong tháng 1 dựa trên độ phủ các nhóm dấu và mục tiêu phân tích. Tập đánh giá được tách riêng trong tháng 1–2, lưu danh mục, dấu kiểm tra tệp và nhật ký truy cập; chỉ mở sau khi khóa mã, tham số và quy tắc đánh giá. Người quản lý dữ liệu phối hợp với một thành viên khác kiểm tra tính toàn vẹn khi mở. Các biến thể font hoặc hạt giống của cùng từ không được tính như các từ độc lập.

Tập âm tiết dùng khảo sát cấu trúc được ghi rõ nguồn, quy tắc chuẩn hóa Unicode và phạm vi bao phủ. Dữ liệu này phục vụ đo độ rộng biên tương tác và số nét chờ; các mẫu đã dùng để tinh chỉnh được phân biệt với tập đánh giá lợi ích. Khi có máy, thu số đo vận tốc và độ trễ nâng/hạ bút theo quy trình lặp lại, kèm cấu hình bút, giấy và điều kiện vận hành.

**Phương pháp phân tích số liệu**

Với cặp khả thi có J_m > 0, gap_m = (J_m−J_joint)/J_m. Báo chênh lệch tuyệt đối, trung bình/lớn nhất, theo nhóm dấu, thời gian và các ca thiếu kết quả. Mẫu số 0, vô nghiệm và hết thời gian tính toán báo riêng.

Biên lợi ích thực dụng ε_eq được đề xuất trong tháng 1 dựa trên chi phí chạy bộ giải và sai số mô hình nếu có số đo, xin ý kiến giảng viên hướng dẫn trước khóa; không chọn sau khi xem kết quả. Ngưỡng bằng nhau số học khác biên thực dụng. Tiêu chí hữu hạn đề xuất là max gap_m ≤ ε_eq trên toàn bộ cặp định trước có kết quả, kèm độ phủ và mọi ca thiếu. Khi thiếu ca bắt buộc, chưa kết luận cho toàn tập thực nghiệm. Không suy ra không có lợi ích trên toàn bộ tiếng Việt từ tập dữ liệu chọn có chủ ý. Nếu suy luận thống kê, cần đăng ký phương pháp lấy mẫu, cỡ mẫu, biên và khoảng tin cậy; không dùng p > 0,05 để kết luận tương đương.

Thời gian tính toán báo môi trường, số lượt làm nóng/đo đã đăng ký, trung vị và phân vị 95% và toàn bộ chi phí quy trình. Font thí điểm đánh giá riêng độ phủ, lỗi dấu/va chạm, thời gian sửa tay, dễ đọc và độ trung thành phong cách; mọi chỉnh tay được ghi nhận. Các kết luận từ người chấm chỉ thực hiện khi có quy trình và dữ liệu được phép sử dụng.

## 6. Năng lực của nhóm nghiên cứu và Giảng viên hướng dẫn

### 6.1. Nhóm sinh viên thực hiện

Đề tài dự kiến được thực hiện bởi bốn sinh viên. Các kiến thức cần huy động gồm lập trình, cấu trúc dữ liệu và giải thuật, hình học tính toán, phương pháp thực nghiệm và phân tích số liệu. Nhóm dự kiến thống nhất đặc tả và rà soát khả năng nhận nhiệm vụ trong tháng đầu.

Học phần, kỹ năng và kinh nghiệm liên quan của các thành viên: ........................................................

Phân công dự kiến: CN chủ trì mô hình chữ/dấu, bộ giải quy hoạch động, tích hợp và điều phối; đồng chủ trì thí điểm font. TV1 phụ trách nguồn dữ liệu, phân chia tập dữ liệu, tập âm tiết và chuẩn tham chiếu đánh giá font. TV2 phụ trách tổng quan tài liệu, mô hình chi phí, các phương pháp đối chứng, chương trình thực nghiệm và phân tích số liệu. TV3 phụ trách bộ kiểm chứng hình học độc lập, đối chiếu tính đúng, đo tham số và thử nghiệm thiết bị.

Bộ vét cạn và bộ giải chính được giao cho hai người khác nhau; khi điều chỉnh nhân lực, việc quản lý tập đánh giá được bàn giao cho thành viên không đồng thời phụ trách bộ vét cạn. Nhóm ưu tiên tính độc lập của kiểm chứng trước thí điểm font.

### 6.2. Thông tin giảng viên hướng dẫn

Họ tên, học hàm, học vị, đơn vị công tác: ........................................................

Hướng nghiên cứu và nội dung hỗ trợ chuyên môn: ........................................................

## 7. Sản phẩm cam kết của đề tài

### 7.1. Sản phẩm bắt buộc

01 báo cáo tổng kết toàn văn; mô hình và bộ giải trong phạm vi khóa; bộ vét cạn độc lập; đối chứng top-m và heuristic; số liệu đánh giá chính cùng gói mã và dữ liệu tái lập. Báo cáo gồm điều kiện có lợi/bằng nhau, chứng nhận có điều kiện và giới hạn. Kết quả bằng nhau được báo trung thực; không cam kết phần trăm cải thiện trên glyph thật.

### 7.2. Sản phẩm khác (nếu có)

Nguyên mẫu và báo cáo thí điểm font khi kiểm chứng lõi hoàn tất; bản trình diễn chữ viết và vẽ tranh; biên bản kiểm chứng máy nếu có thiết bị. Dự kiến chuẩn bị bản thảo bài báo theo kết quả, không cam kết được nhận bài. Dữ liệu/font chỉ được chia sẻ trong phạm vi giấy phép và quyền sử dụng.

## 8. Kế hoạch thực hiện (Tiến độ chi tiết)

Thời gian thực hiện dự kiến là 8 tháng kể từ khi đề tài được phê duyệt. Tháng/năm cụ thể được điền theo lịch triển khai của khoa.

| STT | Nội dung công việc chi tiết | Người thực hiện | Sản phẩm dự kiến | Thời gian |
|---|---|---|---|---|
| 1 | Khóa đặc tả tối thiểu, hai quy tắc xếp hạng; đọc Balas; đề xuất biên và quy tắc phân chia dữ liệu; phân công kiểm chứng độc lập | CN mô hình; TV2 tài liệu/đối chứng; TV1 phân chia dữ liệu; TV3 bộ vét cạn | Đặc tả, bảng nguồn có trang, đề xuất ε_eq và phân công | Tháng 1 |
| 2 | DP, bộ vét cạn và hình học độc lập, chương trình thực nghiệm và đối chứng; tập phát triển dấu chồng; ví dụ tham số hóa tối thiểu; hoàn tất tập đánh giá độc lập | CN DP; TV3 bộ vét cạn; TV2 chương trình thực nghiệm; TV1 dữ liệu | Bộ giải thử, bộ vét cạn, danh mục dữ liệu và nhật ký | Tháng 2 |
| 3 | Khớp DP–bộ vét cạn; điều kiện bằng nhau, chứng nhận/độ nhạy; w/b trong phạm vi đủ chạy; khóa mã/tham số | Cả nhóm theo phân công | Biên bản kiểm chứng và gói cấu hình đóng băng | Tháng 3 |
| 4 | Mở tập đánh giá sau kiểm chứng; đánh giá top-m/heuristic, gap, thời gian và ca thất bại | TV1 quản lý dữ liệu; TV2 chương trình thực nghiệm; TV3 kiểm tra chéo; CN phân tích | Kết quả chính, nhật ký và số liệu từng ca | Tháng 4 |
| 5 | Hoàn tất phân tích, điều kiện lợi ích/bằng nhau; thiết kế thí điểm font sau kiểm chứng lõi | TV2/CN phân tích; TV1/CN font | Báo cáo lõi và quy trình font | Tháng 5 |
| 6 | Thí điểm một nhóm font được chọn; thử máy nếu có; viết các phần báo cáo | TV1/CN font; TV3 máy; TV2 bản thảo | Báo cáo thí điểm, số đo máy nếu có, bản thảo | Tháng 6 |
| 7 | Kết thúc thí điểm/kiểm chứng; ghép báo cáo, rà nguồn và giới hạn | Cả nhóm | Báo cáo toàn văn và bản thảo bài báo | Tháng 7 |
| 8 | Rà soát, sửa báo cáo, gói tái lập, bảo vệ và bàn giao | Cả nhóm; CN điều phối | Báo cáo cuối, mã/dữ liệu và trình diễn | Tháng 8 |

Nếu có nguy cơ trượt tháng 3, cắt w/b mở rộng nhiều font/ngữ cảnh trước, giữ tập có danh mục dữ liệu và cận bảo thủ; sau đó rút họ ví dụ lớn/ánh xạ glyph thật về ví dụ tối thiểu kiểm chứng được. Ưu tiên giữ kiểm chứng tính đúng, công bằng đối chứng và tính toàn vẹn của tập đánh giá. Nếu cuối tháng 3 chưa khớp bộ giải với vét cạn, lùi đánh giá chính thức và thí điểm font để hoàn tất kiểm chứng. Nếu lõi trễ lấn tháng 6, hoãn font để giữ tháng 7–8 viết báo cáo.

## 9. Tài liệu tham khảo

Balas, E. (1999). New classes of efficiently solvable generalized traveling salesman problems. Annals of Operations Research, 86, 529–558. https://doi.org/10.1023/A:1018939709890

Balas, E., & Simonetti, N. (2001). Linear time dynamic-programming algorithms for new classes of restricted TSPs: A computational study. INFORMS Journal on Computing, 13(1), 56–75. https://doi.org/10.1287/ijoc.13.1.56.9748

Chakraborty, S., Fischer, E., Lachish, O., & Yuster, R. (2010). Two-phase algorithms for the parametric shortest path problem. In STACS 2010 (LIPIcs, Vol. 5, pp. 167–178). https://doi.org/10.4230/LIPIcs.STACS.2010.2452

Đà Nẵng, ngày ........ tháng ........ năm ........

| Trưởng khoa | Giảng viên hướng dẫn | Sinh viên chủ nhiệm |
|---|---|---|
| Ký và ghi rõ họ tên | Ký và ghi rõ họ tên | Ký và ghi rõ họ tên |
| ........................ | ........................ | ........................ |
