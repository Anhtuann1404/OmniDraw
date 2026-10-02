# RQ5 — Pilot dựng chữ Việt có dấu cho font thiết kế được chọn

**Ngày chuẩn bị:** 29/09/2026 · **Trạng thái:** `DESIGN_READY_FOR_FONT_SCREENING` · **Owner hình học/font pack:** TV4; TV1 hỗ trợ tập mẫu/đánh giá; TV2 review nếu dùng transition; TV3 chỉ xác nhận claim máy thật.

## Material Passport

| Mục | Giá trị |
| :--- | :--- |
| Câu hỏi | Trên font thiết kế được chọn có Latin cơ bản nhưng thiếu/lỗi tiếng Việt, phương pháp dựng nét và dấu có cải thiện độ phủ/độ đọc mà giữ được phong cách và tạo quỹ đạo plotter hợp lệ không? |
| Bằng chứng hiện có | Font pack nét đơn `legacy`/`omni_casual` và CA-VHC diacritic geometry; repo chưa có tệp TTF/OTF đầu vào, importer/font-repair pipeline hay benchmark RQ5 |
| Sản phẩm pilot | Font pack/quỹ đạo SVG tiếng Việt cho máy vẽ. **Không** gọi đây là bản vá TTF/OTF dùng được trong mọi phần mềm; xuất font số hoàn chỉnh là dự án khác |
| Điều kiện mở | P0/PR3 ổn định; chọn font, xác minh giấy phép, khóa test set/baseline/rubric trước khi dựng |

## 1. Chọn font và lập hồ sơ lỗi trước can thiệp

Chọn một tập nhỏ có chủ ý gồm **ít nhất hai kiểu lỗi khác nhau nếu có font hợp lệ**: (A) thiếu glyph tiếng Việt; (B) có glyph/combining mark nhưng đặt dấu sai, va chạm hoặc lệch phong cách. Có thể thêm font đối chứng hỗ trợ tiếng Việt tốt để kiểm tra phương pháp không làm giảm chất lượng. Quy mô/tên font chỉ chốt sau khi khảo sát nguồn và giấy phép; không chọn font dựa trên kết quả đẹp nhất sau sửa.

Mỗi ứng viên phải có bản ghi: tên, phiên bản/hash file, nguồn tải, giấy phép cho phép phân tích/chỉnh sửa/phân phối artifact, mã ký tự/glyph hiện có, `mark`/`mkmk`/anchor liên quan, render trước sửa trên cùng bộ chữ Việt, và lý do chọn/loại. Lưu manifest và ảnh kết quả đánh giá; không đưa font bên thứ ba vào repo khi giấy phép không cho phép. Phân biệt lỗi **thiếu glyph**, **font fallback**, **shaping/anchor sai**, **dấu trùng**, và **outline không phù hợp centerline**; mỗi nhóm có biện pháp khác nhau.

## 2. Quy trình kỹ thuật dự kiến

1. Chuẩn hóa văn bản và lập bảng ký tự/tổ hợp mục tiêu bằng Unicode NFD/NFC; xác minh base, dấu chữ cái và dấu thanh. Không coi Unicode normalization là thuật toán đặt dấu.
2. Đọc outline/glyph metrics và định vị dấu có sẵn, nếu được giấy phép. Với font thiếu glyph, chọn thành phần thân/dấu cùng phong cách hoặc xây bằng biên tập có ghi công. Với font lỗi vị trí, sửa anchor/offset trước khi tự sinh glyph mới.
3. Chuyển hoặc biên tập outline thành đường **centerline** khi hình dạng cho phép. Ghi rõ glyph nào tự động, bán tự động hoặc làm tay; phép skeleton hóa có thể tạo nhánh giả, vòng lặp hoặc mất chi tiết, nên không được coi là luôn đúng.
4. Dùng quy tắc đặt dấu theo thân chữ, dấu chữ cái/dấu thanh và vùng cản hình học; kiểm tra nhãn Unicode, bounds, va chạm, khoảng hở và độ liên tục nét. Chỉ tái sử dụng logic CA-VHC khi contract/hình học phù hợp, không sửa ngưỡng P0 để hợp một font mới.
5. Xuất font pack/quỹ đạo SVG; giữ trace từ glyph nguồn → hình học mới → bản render. Khi nói đến máy vẽ thật, cần kiểm chứng TV3; simulator chỉ là bằng chứng phần mềm.

Theo [đặc tả OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos), `MarkToBase` và `MarkToMark` là cơ chế định vị dấu; ví dụ mark-to-mark được dùng cho dấu thanh trên dấu nguyên âm tiếng Việt. GPOS là đối chứng typography, chưa giải quyết riêng đường bút centerline hoặc chi phí nhấc bút.

## 3. Thiết kế đối chứng và tập kiểm tra

| Phương pháp | Ý nghĩa | Giới hạn cần ghi |
| :--- | :--- | :--- |
| B0 — Font gốc | Render/shaping nguyên trạng theo phiên bản đã chốt | Ghi font fallback riêng, không tính glyph của font khác như thành công của font gốc |
| B1 — Gắn dấu quy tắc đơn giản | Dùng base và dấu có sẵn với offset/anchor cố định | Không dùng chỉnh tay theo từng từ kiểm tra |
| P — Phương pháp đề xuất | Centerline/anchor/collision-aware composition; ghi công chỉnh tay | Nếu manual quá nhiều, báo cáo là bán tự động và tính chi phí đó |
| Tham chiếu chuyên gia, nếu có | Mẫu chuẩn để đánh giá đọc/giữ phong cách | Là reference, không mặc nhiên là baseline thuật toán |

Tập phát triển dùng để chọn anchor và chỉnh hình học; tập đánh giá khóa trước và chứa ký tự rời, nguyên âm có dấu chữ cái + dấu thanh xếp tầng, từ, câu và trường hợp dấu dưới. Mỗi font dùng cùng nội dung, cỡ nhìn thấy, khổ SVG và điều kiện hiển thị. Tập RQ5 tách khỏi 20 từ DEV/HOLDOUT CA-VHC v1.0; không mở Holdout P0 để chọn font.

## 4. Phép đo và phán quyết

- **Độ phủ:** số tổ hợp mục tiêu hiển thị bằng đúng font/phương pháp chia tổng số tổ hợp đã khóa; ghi `missing`, `fallback`, `wrong mark`, `duplicate mark` riêng.
- **Hình học/quỹ đạo:** tỷ lệ lỗi bounds, nét suy biến, va chạm thân–dấu/dấu–dấu, khoảng hở và xuất SVG hợp lệ. Khác biệt giữa clearance phần mềm và độ tách mực máy thật phải được giữ rõ.
- **Con người:** đánh giá mù độ đọc tiếng Việt và mức giữ phong cách, mỗi font/câu được hoán thứ tự B0/B1/P; ghi số người chấm, rubric và mức đồng thuận. Không dùng OCR làm thước đo duy nhất.
- **Công sức:** phút chỉnh tay/glyph, tỷ lệ glyph cần sửa, số lần lặp và lỗi còn lại. Báo cáo cả font thất bại hoặc bị loại theo tiêu chí trước can thiệp.

Phân tích ghép cặp theo `(font, test item)`, báo cáo kết quả **theo từng font** trước khi gộp. Không tuyên bố “khắc phục lỗi font tiếng Việt” nếu mới đạt một font/ít từ. Ngưỡng PASS/FAIL và cỡ mẫu đánh giá được khóa sau screening/pilot, trước tập kiểm tra chính.

## 5. Gate và việc có thể làm ngay

| Gate | Bằng chứng cần có |
| :--- | :--- |
| R5-G0 — Font hợp lệ | Manifest tên/version/license/hash và phân loại lỗi trước sửa |
| R5-G1 — Dataset/baseline | Tập phát triển/đánh giá riêng, B0/B1 cố định và phép render không font fallback ngoài ý muốn |
| R5-G2 — Hình học | Trace nguồn–centerline–dấu, test ký tự/từ khó, báo cáo chỉnh tay và QA SVG |
| R5-G3 — Đánh giá | Raw rating mù, độ phủ, lỗi, độ đọc, mức giữ phong cách, khoảng tin cậy/giới hạn |
| R5-G4 — Máy thật (nếu nêu claim) | Calibration TV3 và mẫu in/quét thật có provenance |

**Làm ngay:** lập bảng screening font và tập test Unicode tiếng Việt **trên giấy**, chuẩn bị rubric và phương pháp phát hiện fallback; không tải/commit font hoặc chạy benchmark chính thức khi R5-G0/G1 chưa khóa. P0 và review PR3 vẫn ưu tiên trước.

## 6. Nguồn nền và giới hạn chuyển giao

- [Unicode UAX #15](https://www.unicode.org/reports/tr15/): canonical normalization; không cung cấp hình học dấu.
- [OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos): anchor và mark positioning; không tạo centerline plotter.
- [Pan et al., ICCV 2023](https://openaccess.thecvf.com/content/ICCV2023/papers/Pan_Few_Shot_Font_Generation_Via_Transferring_Similarity_Guided_Global_Style_ICCV_2023_paper.pdf): prior art cho học phong cách font từ ít glyph; nhiệm vụ/dữ liệu khác pilot hình học tiếng Việt này.

Đây là protocol chuẩn bị, chưa phải kết quả RQ5 hoặc tuyên bố tính mới đã được kiểm chứng.
