# OmniDraw — Giao thức Tổng quan Tài liệu Chương 2

**Phiên bản:** 0.2
**Ngày tìm kiếm khởi tạo:** 2026-09-21
**Cập nhật citation chaining vòng 1:** 2026-09-22
**Loại tổng quan:** Structured scoping review
**Trạng thái:** `CITATION CHAINING ROUND 1 COMPLETE — TEAM SCREENING PENDING`

**Material Passport**

- **Origin Skill:** `academic-research-suite/deep-research`
- **Origin Mode:** Literature review — Phase 2 Investigation
- **Origin Date:** 2026-09-22
- **Verification Status:** `METADATA VERIFIED — FULL-TEXT REVIEW PARTIAL`

> [!IMPORTANT]
> Tài liệu này là nhật ký phương pháp tìm và chọn tài liệu, không phải kết quả thực nghiệm của OmniDraw. Chưa được gọi là systematic review hoặc PRISMA review cho đến khi có ít nhất hai người sàng lọc độc lập, lưu đầy đủ bản ghi loại trùng và lý do loại từng tài liệu.

## 1. Mục tiêu

Tổng quan tài liệu phục vụ ba câu hỏi nghiên cứu đã khóa cấu trúc tại [`10_nckh_research_plan.md`](10_nckh_research_plan.md):

1. Cơ sở cho biểu diễn chữ viết tay dạng chuỗi nét, lựa chọn biến thể theo ngữ cảnh và tối ưu thứ tự/chuyển động bút.
2. Cơ sở cho xử lý dấu tiếng Việt, Unicode normalization, delayed strokes và ràng buộc vị trí dấu.
3. Cơ sở cho việc chuyển quỹ đạo vector sang hệ robot/máy vẽ và đánh giá tính khả thi.

Mục tiêu của vòng tìm kiếm đầu tiên là xây dựng **bộ nguồn hạt giống đã xác minh** để viết Chương 2 và xác định khoảng trống nghiên cứu tạm thời. Vòng này không nhằm chứng minh rằng đã tìm được toàn bộ công trình liên quan.

## 2. Câu hỏi tổng quan

| ID | Câu hỏi tổng quan | Liên hệ nghiên cứu |
| :--- | :--- | :--- |
| LRQ1 | Chữ viết tay trực tuyến được biểu diễn và sinh dưới dạng chuỗi nét như thế nào? | RQ1, định hướng Writer Profile P2 |
| LRQ2 | Các phương pháp nào tối ưu thứ tự nét, quãng đường pen-up và độ mượt quỹ đạo cho hệ vẽ robot? | RQ1, RQ3 |
| LRQ3 | Dấu tiếng Việt và các nét viết trễ đặt ra yêu cầu gì đối với biểu diễn trạng thái và thứ tự nét? | RQ2, PR3–PR4 |
| LRQ4 | Chuẩn Unicode/OpenType cung cấp cơ chế nào cho phân rã và neo dấu, và giới hạn của chúng đối với single-stroke plotting là gì? | RQ2 |
| LRQ5 | Khoảng trống nào còn lại giữa tổng hợp chữ viết tay, typography và tối ưu quỹ đạo robot? | Đóng góp CA-VHC |

## 3. Nguồn tìm kiếm

### 3.1. Nguồn học thuật và tiêu chuẩn

- IEEE Xplore: thuật toán Viterbi, robot viết/vẽ và trajectory planning.
- ACM Digital Library: digital ink và handwriting synthesis.
- ScienceDirect/Pattern Recognition: dữ liệu chữ viết tay tiếng Việt.
- AAAI Proceedings và arXiv: robotic drawing, path optimization và handwriting generation.
- Journal of Neuroscience: mô hình minimum-jerk của chuyển động tay.
- Unicode Consortium và Microsoft OpenType Specification: nguồn tiêu chuẩn cho normalization và mark attachment.
- Trang kho lưu trữ chính thức của trường/nhóm tác giả chỉ dùng để truy cập bản toàn văn hoặc đối chiếu metadata.

### 3.2. Chuỗi truy vấn hạt giống

```text
("online handwriting" OR "handwriting synthesis") AND (stroke OR trajectory)
("robotic drawing" OR plotter OR "robot writing") AND ("stroke order" OR "path optimization" OR "pen-up")
(Vietnamese AND handwriting AND (diacritic OR "delayed stroke"))
(Unicode AND NFD AND combining marks)
(OpenType AND (MarkToBase OR MarkToMark OR "cursive attachment"))
(Viterbi OR "dynamic programming") AND (sequence OR trellis)
("minimum jerk" AND movement trajectory)
```

Các truy vấn được thực hiện bằng tiếng Anh để tăng độ phủ. Citation chaining vòng 1 dùng các nguồn S03, S08 và S11 làm điểm xuất phát, kết hợp tìm theo tiêu đề, DOI, tài liệu tham khảo lùi và công trình liên quan tiến. Vòng sau team review sẽ bổ sung truy vấn tiếng Việt và citation chaining vòng 2 cho các khoảng trống còn lại.

### 3.3. Nhật ký citation chaining vòng 1 (2026-09-22)

| Nhóm | Kết quả giữ lại | Lý do |
| :--- | :--- | :--- |
| Delayed strokes | S12 | So sánh trực tiếp các chiến lược xử lý nét viết trễ trên nhiều bộ dữ liệu online handwriting. |
| Kinematic synthesis | S13 | Sinh dữ liệu handwriting trực tuyến bằng mô hình sigma-lognormal, bổ sung cơ sở động học ngoài minimum-jerk. |
| Robotic sequence writing | S14 | Học thứ tự quỹ đạo và cấu trúc ký tự cho robot viết, là đối chứng gần với bài toán sequence composition. |
| Trajectory optimization | S15 | Mô hình hóa viết thư pháp robot như bài toán tối ưu quỹ đạo có mô hình công cụ viết. |
| Context-aware generation | S16 | Mô hình hóa rõ liên kết và khoảng cách giữa ký tự ở mức câu; là nguồn phản biện trực tiếp buộc thu hẹp tuyên bố novelty. |

Các ứng viên chỉ liên quan recognition chung, chữ Nôm lịch sử, chữ ký trên không hoặc không xác minh được trạng thái xuất bản được loại/defer khỏi matrix. Đây là targeted citation chaining, không phải thống kê exhaustive và không được trình bày như PRISMA flow.

## 4. Tiêu chí chọn và loại

### 4.1. Tiêu chí chọn

- Bài báo gốc, kỷ yếu chính thức, preprint của chính tác giả hoặc tiêu chuẩn kỹ thuật chính thức.
- Trình bày ít nhất một trong các nội dung: chuỗi nét viết tay, sinh chữ viết tay, delayed strokes/dấu tiếng Việt, tối ưu đường vẽ, điều khiển chuyển động hoặc neo dấu.
- Có metadata đủ kiểm chứng: tác giả, năm, tiêu đề và DOI/URL ổn định.
- Có phương pháp hoặc bằng chứng có thể ánh xạ rõ sang LRQ/RQ của OmniDraw.

### 4.2. Tiêu chí loại

- Blog, Wikipedia, nội dung quảng bá hoặc bản tóm tắt không truy nguyên được nguồn gốc.
- Bài chỉ nói về OCR chung mà không cung cấp bằng chứng liên quan đến nét, dấu hoặc chuỗi thời gian.
- Công trình robot không có hoạt động viết/vẽ tiếp xúc hoặc không có thành phần trajectory/stroke planning.
- Tài liệu thứ cấp lặp lại tuyên bố nhưng không cung cấp dữ liệu hay phương pháp gốc.
- Bản ghi không thể xác minh metadata.

## 5. Quy trình sàng lọc

1. Tìm theo các chuỗi truy vấn hạt giống.
2. Đọc tiêu đề và tóm tắt; loại tài liệu lệch chủ đề.
3. Đối chiếu DOI, trang nhà xuất bản hoặc kho chính thức.
4. Trích xuất theo mẫu WHY–HOW–WHAT và ánh xạ sang RQ1–RQ3.
5. Ghi giới hạn chuyển giao: bằng chứng recognition không tự động chứng minh synthesis; typography màn hình không tự động chứng minh an toàn máy vẽ.
6. TV2 cross-review nhóm motion/path; TV3 cross-review nhóm robot/hardware; TV4 cross-review nhóm dấu và composition.
7. Thực hiện citation chaining, ghi rõ nguồn mới là peer-reviewed hay preprint và cập nhật phản chứng đối với tuyên bố novelty.
8. Chỉ sau khi hoàn tất cross-review mới đổi trạng thái nguồn từ `VERIFIED_SEED`/`VERIFIED_CHAIN_R1` sang `TEAM_VERIFIED`.

Không dùng tổng số kết quả do công cụ tìm kiếm ước lượng làm số liệu sàng lọc. Sau vòng chaining thứ nhất, matrix có 16 nguồn: 11 nguồn hạt giống, 4 nguồn peer-reviewed/kỷ yếu chính thức mới và 1 preprint 2026. Sơ đồ PRISMA và số bản ghi bị loại chi tiết vẫn là `PENDING`.

## 6. Trường trích xuất bắt buộc

| Trường | Nội dung |
| :--- | :--- |
| `citation_id` | Mã tham chiếu duy nhất |
| `bibliographic_record` | Tác giả, tiêu đề, venue, năm, DOI/URL |
| `study_type` | Empirical / algorithm / dataset / standard |
| `why` | Vấn đề nghiên cứu |
| `how` | Phương pháp và dữ liệu |
| `what` | Kết quả hoặc đóng góp chính, không phóng đại |
| `rq_mapping` | RQ1, RQ2, RQ3 hoặc P2 |
| `transfer_limit` | Điều không được suy ra cho OmniDraw |
| `verification` | Trạng thái kiểm chứng nguồn |
| `evidence_grade` | Mức thiết kế nghiên cứu và grade chất lượng, không đồng nhất với độ phù hợp cho OmniDraw |
| `publication_status` | Peer-reviewed / standard / preprint |
| `coi_note` | Xung đột lợi ích được công bố hoặc trạng thái chưa đánh giá đủ |

## 7. Kiểm soát chất lượng và tính liêm chính

- Không chép nguyên văn dài; diễn giải và trích nguồn tại đúng luận điểm.
- Không dùng số liệu của công trình khác làm target cho OmniDraw nếu khác thiết bị, corpus hoặc điều kiện đo.
- Tách rõ ba lớp: **bằng chứng từ nguồn**, **suy luận của nhóm**, và **quyết định thiết kế OmniDraw**.
- “Khoảng trống nghiên cứu” trong bản nháp chỉ được gọi là **khoảng trống tạm thời** cho đến khi citation chaining hoàn tất.
- S16 là preprint và chỉ được dùng làm bằng chứng có nghiên cứu gần chủ đề; không được dùng như xác nhận peer-reviewed.
- CASHG đã bao phủ context-aware character generation và inter-character connectivity. Vì vậy OmniDraw không được tuyên bố rộng là hệ đầu tiên xử lý chữ viết tay theo ngữ cảnh; novelty tạm thời phải giới hạn ở tổ hợp **chính tả/dấu tiếng Việt + collision/clearance + finite-state composition + chi phí thi công plotter**.
- Mọi kết quả của OmniDraw trong Chương 4 tiếp tục mang nhãn `PENDING FORMAL EXPERIMENT — DO NOT REPORT AS RESULT`.

### 7.1. Cảnh báo độ phủ

- Bộ nguồn nghiêng về thuật toán, hệ thống và robotics, phù hợp với LRQ kỹ thuật nhưng chưa đủ mạnh cho đánh giá cảm nhận người dùng.
- Nguồn kinh điển cũ được giữ vì là nền tảng phương pháp; tính cập nhật được bổ sung bằng S14 và S16, không thay thế yêu cầu tìm thêm nghiên cứu đánh giá legibility/naturalness.
- Chưa hoàn tất đọc toàn văn và đánh giá COI cho tất cả 16 nguồn; mọi ô chưa đủ thông tin phải mang nhãn `PENDING`, không được suy đoán.

## 8. Gate hoàn tất Chương 2

- [x] Có protocol và chuỗi truy vấn tái sử dụng được.
- [x] Có bộ nguồn hạt giống đã xác minh.
- [x] Có evidence matrix ánh xạ sang RQ1–RQ3.
- [x] Có bản nháp Chương 2 không chứa kết quả giả.
- [ ] TV2 review nguồn motion/path optimization.
- [ ] TV3 review nguồn physical execution/robotics.
- [ ] TV1 kiểm tra phạm vi corpus và thuật ngữ dữ liệu.
- [x] Thực hiện backward/forward citation chaining vòng 1 và ghi nhận phản chứng novelty.
- [ ] Thực hiện citation chaining vòng 2 sau team review cho các khoảng trống còn lại.
- [ ] Khóa danh mục tài liệu tham khảo theo định dạng của cuộc thi/trường.
