# OmniDraw — Phạm vi nghiên cứu mở rộng và trạng thái bằng chứng

**Cập nhật:** 29/09/2026 · **Owner tổng hợp:** TV4 · **Trạng thái:** định hướng nghiên cứu, chờ phản biện và thực nghiệm.

**Tên đề tài làm việc:** **OmniDraw: Nghiên cứu tái tạo chữ Việt có dấu theo phong cách cá nhân và font thiết kế trên máy vẽ**.

Tài liệu này thống nhất phạm vi đề tài sau khi bổ sung hai hướng nghiên cứu. Nó không thay đổi hợp đồng hoặc ngưỡng đã khóa của CA-VHC RQ1–RQ3 tại [Docs 05](05_ca_vhc_research_spec.md), không thay thế [dataset protocol TV1](08_handwriting_dataset_spec.md) hay [hợp đồng E4 TV2–TV4](18_pr3_e4_shared_transition_contract_draft.md). Mỗi hướng phải có bằng chứng riêng trước khi được đưa vào kết luận của báo cáo.

## 1. Câu hỏi nghiên cứu và mức ưu tiên

| Hướng | Câu hỏi cần trả lời | Trạng thái 29/09/2026 |
| :--- | :--- | :--- |
| RQ1–RQ3 · P0 | Hợp thành chữ Việt có dấu theo ngữ cảnh, giảm chuyển động bút, tránh va chạm và kiểm tra khả năng thi công | PR3 đang triển khai theo slice; E4 PASS; E1 chỉ có kết quả DEV phần mềm; PR3 exit, PR5 Holdout và máy thật chưa hoàn tất |
| **RQ4 · P2** | Có thể suy ra thói quen viết của một người từ ít mẫu được phép sử dụng, rồi tạo văn bản chưa thấy với phong cách gần mẫu hơn baseline mặc định/rule-based mà vẫn đúng chữ Việt và an toàn hình học không? | TV1 đã có schema, extractor và generator profile từ ảnh crop, kiểm tra trên fixture giả lập; chưa có học mô hình, tích hợp end-to-end hay đánh giá người viết thật |
| **RQ5 · P3 pilot** | Với một số font thiết kế chọn trước có chữ Latin nhưng thiếu hoặc đặt sai dấu tiếng Việt, quy trình dựng centerline và bố trí dấu dựa trên hình học/anchor có cải thiện độ phủ và độ đọc so với font gốc hoặc bổ sung dấu thủ công theo quy tắc không? | Ý tưởng/methodology; chưa có importer font, bộ dữ liệu font, kết quả hay tuyên bố khắc phục mọi font |
| **Art Mode · nhánh đánh giá hệ thống** | Chuyển ảnh/tranh thành quỹ đạo nét vẽ và so sánh hiệu quả sắp thứ tự nét | Pipeline phần mềm và bộ tối ưu đã có; benchmark Naive/Greedy/OmniDraw trong roadmap còn chờ thực hiện; không dùng kết quả này để kết luận RQ1–RQ5 |

P0 là kết quả lõi cần khóa trước. RQ4 và RQ5 là **mục tiêu nghiên cứu có điều kiện**, không phải tính năng hiện hành hay bằng chứng đã đạt. Nếu thời gian, dữ liệu hoặc thiết bị không đủ, báo cáo phải ghi rõ phần nào chỉ dừng ở thiết kế/pilot.

## 2. RQ4 — Học phong cách theo thói quen người viết

1. **Đầu vào và đồng ý tham gia:** mẫu P01–P04 đã qua QC, mã người viết ẩn danh và phạm vi đồng ý sử dụng; không thu thập họ tên, chữ ký hay nhận dạng cá nhân. Ảnh quét tĩnh không được diễn giải thành tốc độ/áp lực bút.
2. **Đặc trưng ban đầu:** độ nghiêng, tỷ lệ khung chữ, khoảng cách ký tự/từ và dao động chân dòng theo [schema/extractor/generator TV1](08_handwriting_dataset_spec.md). Module generator đã nối ảnh crop sang profile trên fixture giả lập; contour/connected components chưa chứng minh phân đoạn đúng mọi chữ/dấu thật. Các đặc trưng này chưa chứng minh đã học được thói quen.
3. **Phương pháp dự kiến:** xây baseline font mặc định và ánh xạ rule-based; thử mô hình cá nhân hóa gọn trên số mẫu được quy định trước. TV1 phụ trách dữ liệu/profile, TV4 phụ trách mapping vào engine; mọi thay đổi contract phải được owner duyệt.
4. **Đánh giá:** chia theo **người viết** và **văn bản**; văn bản kiểm tra chưa dùng để trích profile/điều chỉnh tham số. So sánh cùng nội dung, cỡ và điều kiện render. Đo sai khác đặc trưng hình học, độ đúng/dễ đọc của chữ Việt, vi phạm dấu/va chạm và đánh giá mù về độ giống phong cách nếu có đủ người tham gia. Công bố cỡ mẫu, độ bất định và trường hợp thất bại; ngưỡng kết luận được chốt trước khi mở tập đánh giá.
5. **Gate:** bench print/scan và pilot của TV1; consent/QC; dữ liệu đủ để tách train–validation–test; baseline; tích hợp có test; đánh giá độc lập. Synthetic fixture không thay thế đánh giá trên người viết thật.

Protocol có thể review cho RQ4: [Docs 23](23_rq4_writer_habit_study_protocol.md).

## 3. RQ5 — Dựng lại chữ Việt cho font thiết kế được chọn

1. **Phạm vi font:** chọn và ghi phiên bản/giấy phép của một số font có Latin base glyph nhưng lỗi hoặc thiếu tổ hợp tiếng Việt; lập danh sách lỗi trước khi sửa. Font thiếu hoàn toàn nét cơ sở phù hợp hoặc có hình học quá phức tạp có thể bị loại khỏi pilot kèm lý do.
2. **Pipeline dự kiến:** đọc glyph và metrics hợp lệ → chuyển/biên tập nét thành centerline khi khả thi → gắn anchor cho thân chữ/dấu → tạo dấu chữ cái và dấu thanh theo tổ hợp Unicode hợp lệ → dùng kiểm tra va chạm/clearance và điều chỉnh hình học → xuất quỹ đạo SVG để đánh giá. Việc chuyển outline thành centerline là bài toán riêng, không thể giả định tự động cho mọi font.
3. **Đối chứng:** font gốc, phương án gắn dấu cố định/rule-based, và phương pháp đề xuất trên cùng tập chữ/từ/câu Việt; ghi cả công chỉnh tay. Chỉ so sánh khi quyền sử dụng font cho phép.
4. **Metric:** độ phủ tổ hợp tiếng Việt, tỷ lệ lỗi dấu/đè nét, độ đọc qua đánh giá mù, mức giữ phong cách, thời gian/chỉnh sửa thủ công và tính hợp lệ của quỹ đạo. Không gọi một font đã “sửa hoàn toàn” chỉ từ vài ví dụ đẹp.
5. **Gate:** xác định font/corpus/giấy phép; chốt baseline và rubric trước pilot; test hình học và đánh giá người đọc; kiểm tra trên máy thật nếu nêu claim thi công. Kết quả RQ5 tách khỏi benchmark CA-VHC đã đóng băng.

Protocol screening và pilot RQ5: [Docs 24](24_rq5_vietnamese_design_font_pilot.md).

## 4. Kỷ luật bằng chứng và việc hiện tại

**Vị trí phần vẽ tranh trong đề tài.** OmniDraw là hệ thống có hai luồng: Art Mode (ảnh/tranh → nét vẽ) và Handwriting Mode (văn bản → chữ Việt có dấu). Art Mode có giá trị như sản phẩm phần mềm, demo máy vẽ và một phép đối sánh độc lập về tối ưu thứ tự nét. [Roadmap](02_roadmap.md) đã dự kiến so sánh Naive, Greedy Nearest Neighbor và `cKDTree + Or-opt + Kinematic Turn Penalty`; code hiện có ở `backend/path_optimizer.py`. Nhánh này cần dữ liệu ảnh cố định, cùng điều kiện phần cứng/metric và báo cáo riêng. Không gộp số đo Art Mode vào corpus hay giả thuyết CA-VHC, và không gọi một demo là kết quả benchmark. Tên đề tài hiện đặt trọng tâm vào đóng góp nghiên cứu về chữ Việt; phần vẽ tranh được trình bày trong kiến trúc, phạm vi ứng dụng và đánh giá hệ thống, không bị loại khỏi OmniDraw.

- **PR3 hiện hành:** tham chiếu [Docs 17](17_pr3_implementation_readiness.md) và [current task](03_current-task.md). E1 DEV ở bản có biến thiên style tất định (`072029b`) là 4.343,360 mm, giảm 9,018% so B1 và 7,701% so B2 trên cùng runner; thấp hơn ngưỡng PASS H1.1. Đây không phải verdict PR3 exit hoặc kết quả Holdout.
- **Không dùng chung tập kết luận:** RQ4 cần split theo writer/text; RQ5 cần tập font và nội dung riêng. Corpus CA-VHC v1.0 đã frozen tại [Docs 19](19_benchmark_corpus_freeze_report.md); không sửa corpus đó để phục vụ RQ4/RQ5.
- **Rà soát văn liệu:** [Chương 2](13_chapter_2_literature_review.md) hiện đủ nền cho P0, còn cần tìm và thẩm định nguồn chuyên biệt cho cá nhân hóa từ ít mẫu, font Việt/OpenType và outline-to-centerline trước khi nêu claim novelty RQ4/RQ5. Không gán kết quả thực nghiệm cho các hướng chưa thử.
- **Phê duyệt:** thay đổi ở dữ liệu/profile cần TV1; transition/motion cần TV2; thiết bị/claim vật lý cần TV3; TV4 tích hợp và tổng hợp. Review Chương 1–3 trước đây không tự động ký duyệt nội dung mở rộng này.
