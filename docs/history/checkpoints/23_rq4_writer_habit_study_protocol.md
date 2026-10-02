> **HISTORICAL_RECORD — không là đặc tả hiện hành.** Đọc [hướng hiện tại](../../README.md), [contract](../../31_joint_solver_contract.md) và [công việc](../../03_current-task.md). Giữ kết luận đúng phạm vi/commit gốc.

<!-- scope-migration-20261002 -->
> **Phạm vi ngày 02/10/2026:** BACKLOG ngoài cam kết kỳ này. Phần protocol bên dưới là đề xuất trước đây, chưa là nhiệm vụ hiện hành. Chỉ thí điểm font được giữ có điều kiện; không suy diễn thói quen thứ tự nét từ ảnh quét.
> Kế hoạch hiện hành: [Docs 30](../../30_research_development_plan.md); đặc tả [Docs 31](../../31_joint_solver_contract.md) và [Docs 32](../../32_research_api_and_artifact_contract.md). Thông báo GVHD đồng ý hướng không thay sign-off kỹ thuật hoặc duyệt tham số.

# RQ4 — Protocol nghiên cứu thói quen viết cá nhân

**Ngày chuẩn bị:** 29/09/2026 · **Trạng thái:** `DESIGN_READY_FOR_TV1_REVIEW` · **Owner dữ liệu/profile:** TV1 · **Owner tích hợp/đánh giá:** TV4.

## Material Passport

| Mục | Giá trị |
| :--- | :--- |
| Câu hỏi | Từ một số mẫu chữ viết tay được phép sử dụng, hệ thống có thể tạo **văn bản mới** gần phong cách của đúng người viết hơn baseline, mà vẫn giữ chữ Việt dễ đọc và dấu đúng không? |
| Bằng chứng hiện có | `writer_profile.schema.json`, `extractor.py`, `profile_generator.py` và 13 test extractor/generator PASS trên fixture giả lập ngày 29/09; chưa có dữ liệu người viết thật, model cá nhân hóa trong engine hoặc kết quả so sánh |
| Phạm vi | P2; độc lập với 20 DEV/20 HOLDOUT CA-VHC đã frozen và PR3/PR5 |
| Quyết định còn mở | Số người/mẫu sau pilot, mức ít mẫu cần thử, rubric đánh giá mù, ngưỡng kết luận và cơ chế consent phù hợp quy định đơn vị |

## 1. Thiết kế thực nghiệm

**Đơn vị đánh giá:** một người viết, một văn bản chưa thấy, một phương pháp, một seed. Chia tập ở hai tầng: (a) người dùng để phát triển/điều chỉnh mô hình và người đánh giá hoàn toàn khác nhau; (b) trong mỗi người đánh giá, các mẫu cấp để lập profile không chứa văn bản dùng kiểm tra. Tập CA-VHC Holdout không tham gia lựa chọn hoặc tinh chỉnh RQ4.

| Nhánh | Vai trò | Điều kiện công bằng |
| :--- | :--- | :--- |
| B0 — Font mặc định | Mốc không cá nhân hóa | Cùng nội dung, cỡ, giấy, bộ nét và seed được kiểm soát |
| B1 — Ánh xạ rule-based | Áp dụng các đặc trưng profile bằng quy tắc cố định | Quy tắc và giới hạn hình học chốt trên tập phát triển |
| P — Phương pháp học profile | Ước lượng/ánh xạ tham số phong cách từ mẫu ít bằng mô hình được định nghĩa trước | Không dùng mẫu kiểm tra hoặc nhãn người đánh giá để điều chỉnh; báo cáo kích thước mô hình và dữ liệu học |

Nếu chỉ triển khai B1 thì kết quả phải gọi là **cá nhân hóa theo quy tắc**, chưa gọi là bằng chứng AI đã học thói quen viết. Nghiên cứu P chỉ bắt đầu khi dữ liệu, baseline và năng lực tính toán đủ; không cần mô hình sâu nếu mô hình gọn đáp ứng câu hỏi.

## 2. Dữ liệu và kiểm soát rò rỉ

1. TV1 dùng protocol P01–P04, QC và mã ẩn danh trong [Docs 08](../../support/08_handwriting_dataset_spec.md) và [Docs 21](21_handwriting_collection_protocol_and_error_handling.md). Pilot 3–5 người viết chỉ kiểm tra khả thi của phiếu/scan/extractor; không đủ làm tập kết luận về tổng quát hóa.
2. Trước thu mẫu, chốt quyền sử dụng, lưu trữ và rút mẫu theo phê duyệt của đơn vị. Không đưa ảnh thô, chữ ký hay thông tin nhận dạng lên Git hoặc dịch vụ ngoài.
3. Đóng băng danh sách `writer_id`, phiên, form version, QC status, ảnh crop và prompt ID. Mỗi dòng profile phải truy về đúng ảnh nguồn, DPI, mã phiên, phiên bản extractor và thời điểm tạo.
4. Kế hoạch 40 writer/28–6–6 trong Docs 08 là **mục tiêu dự kiến**, chưa phải số mẫu đạt. Sau pilot, tính lại cỡ mẫu/độ chính xác cần thiết từ biến thiên thực; khóa split writer-disjoint và tập văn bản kiểm tra trước đánh giá.
5. Ảnh quét tĩnh chỉ cho hình học nhìn thấy. `profile_generator.py` hiện lấy contour/connected components từ crop; contour và hộp thành phần liên thông chưa chứng minh là nét bút nguyên thủy hoặc ký tự đã phân đoạn đúng. Cần kiểm tra thủ công lỗi tách dấu và ký tự dính trước khi dùng đặc trưng làm ground truth.

## 3. Đầu ra và phép đo

**Kết quả chính dự kiến:** mức giống phong cách của đúng người viết trên **văn bản chưa thấy**, qua đánh giá mù có người viết đích, các mẫu tham chiếu và các bản B0/B1/P được hoán thứ tự. Quy định số người chấm, thang/rubric, cách ẩn phương pháp và kiểm tra mức đồng thuận trước khi chạy. Tính theo từng writer trước rồi mới tổng hợp; không coi nhiều chữ của cùng writer là nhiều quan sát độc lập.

**Kết quả phụ:** sai khác đặc trưng độ nghiêng, tỷ lệ khung, khoảng cách và dao động chân dòng so với mẫu kiểm tra; độ đọc và độ đúng dấu/Unicode; `collision_count`, clearance, bounds và tỷ lệ lỗi render. Chuẩn hóa từng đặc trưng bằng thống kê từ tập phát triển, không dùng tập kiểm tra để đặt trọng số. Báo cáo riêng độ giống và độ đọc; cải thiện một chỉ số không được che lỗi dấu hoặc va chạm.

**Phân tích:** so sánh ghép cặp B0/B1/P trên cùng writer và văn bản; báo cáo trung bình/trung vị theo writer, khoảng tin cậy và các ca thất bại. Pilot chỉ dùng để chỉnh protocol, không đặt verdict hiệu quả. Chốt chiều cải thiện, ngưỡng ý nghĩa thực tiễn và phân tích thống kê trước khi mở tập đánh giá chính.

## 4. Các gate và đầu ra bàn giao

| Gate | Bằng chứng cần có | Owner |
| :--- | :--- | :--- |
| R4-G0 — Dữ liệu hợp lệ | Consent, bản in/quét bench, QC và manifest P01–P04; không có ảnh thật trong repo | TV1 |
| R4-G1 — Đặc trưng đáng tin | Sai số extractor trên mẫu được gắn nhãn/soi tay; xử lý dấu tách rời và ký tự dính; test phiên bản profile | TV1 |
| R4-G2 — Baseline và mô hình | B0/B1/P được mô tả, freeze config và split trước đánh giá | TV1 + TV4 |
| R4-G3 — Engine an toàn | Mapping profile chỉ vào tham số được phê duyệt; render/trace đồng nhất, kiểm tra dấu và va chạm | TV4; TV2 review nếu đụng transition |
| R4-G4 — Đánh giá độc lập | Văn bản/người viết giữ kín, rubric mù, raw ratings, thống kê theo writer và bất định | TV1 + TV4 |

**Việc có thể làm ngay khi chờ máy in/quét:** TV1 review protocol và kiểm tra lỗi phân đoạn trên synthetic/ảnh nội bộ được phép; TV4 chuẩn bị bảng tham số engine nhận profile và test contract ở mức thiết kế, không thay đổi schema/TV1 code. Chỉ bắt đầu tích hợp khi R4-G0/G1 đủ bằng chứng và P0 không bị chậm.

## 5. Nguồn nền và giới hạn chuyển giao

- [Aksan et al., DeepWriting (CHI 2018)](https://ait.ethz.ch/deepwriting): prior art tách nội dung và phong cách digital ink; không phải bằng chứng cho kết quả OmniDraw hay dữ liệu tiếng Việt.
- [Pippi et al., Handwritten Text Generation from Visual Archetypes (CVPR 2023)](https://openaccess.thecvf.com/content/CVPR2023/papers/Pippi_Handwritten_Text_Generation_From_Visual_Archetypes_CVPR_2023_paper.pdf): nghiên cứu few-shot style và văn bản mới; cần so sánh ở mức nhiệm vụ/dữ liệu, không áp số liệu của họ cho plotter.

Đây là protocol chuẩn bị, chưa phải preregistration đã phê duyệt hoặc kết quả RQ4.
