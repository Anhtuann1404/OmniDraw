# OmniDraw — Technical Notes: Handwriting Collection Sheet P03 Demo v0.1

**Tài liệu:** Báo cáo thông số kỹ thuật & Thiết kế hình học phiếu thu thập mẫu P03 (Demo Layout v0.1)  
**Mã tài liệu:** `NOTE-P03-DEMO-LAYOUT-v0.1`  
**Phiên bản:** `ODW-HW-P03-DEMO-v0.1`  
**Ngày lập:** 20/09/2026 (Cập nhật sau vòng P03 Correction & Scientific Wording Cleanup)  
**Chế độ tài liệu:** VISUAL / PRINTABLE PROTOTYPE SPECIFICATION  
**Trạng thái phê duyệt:** PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)  

---

## 1. Tóm tắt các điều chỉnh kỹ thuật & Ngữ nghĩa trong vòng Cleanup (Changelog)

1. **Hiệu chỉnh số lượng từ và ký tự câu mẫu (Sentence Count Correction):**
   - Thay thế các giá trị đếm ước lượng thủ công bằng thuật toán đếm tất định chuẩn xác:
     - `SENT_001`: 17 từ • 72 Unicode code points (bao gồm khoảng trắng và dấu câu).
     - `SENT_002`: 13 từ • 54 Unicode code points (bao gồm khoảng trắng và dấu câu).
     - `SENT_003`: 12 từ • 54 Unicode code points (bao gồm khoảng trắng và dấu câu).
   - Quy định rõ quy ước đếm (Counting Convention): Số từ tính theo token tách bởi khoảng trắng (`len(text.split())`); độ dài ký tự tính theo số lượng điểm mã Unicode thực tế (`len(text)` Unicode code points), bao gồm toàn bộ khoảng trắng và dấu câu kết thúc.
2. **Chuẩn hóa tuyên bố x-height (x-height Wording Cleanup):**
   - Loại bỏ khẳng định mang tính chủ quan *"chiều cao chuẩn công thái học cho chữ viết câu tự nhiên"* ("standard ergonomic height").
   - Xác định rõ: `x-height = 5.00 mm` là một **giá trị thử nghiệm kỹ thuật (Engineering Demo Default / Pilot Baseline)** được chọn cho prototype này để phục vụ đánh giá công thái học chữ viết tay trong giai đoạn Pilot, chưa phải chuẩn công thái học đã được chứng minh khoa học trên người viết tiếng Việt.
   - Bổ sung cam kết thực nghiệm: Kích thước Writing Zone và khoảng cách các đường kẻ sẽ được kiểm chuẩn, tinh chỉnh cùng người viết trong giai đoạn Pilot (*writing-zone dimensions and guide spacing will be validated with pilot writers*).
3. **Chuẩn hóa tuyên bố khoảng cách đệm giữa 2 dòng (Inter-Line Spacing Wording Cleanup):**
   - Xóa bỏ claim tuyệt đối *"hoàn toàn không có nguy cơ giao cắt chồng lấn"* ("zero risk of collision").
   - Thay bằng diễn đạt khoa học chính xác: Khoảng đệm $10.00\,\text{mm}$ được thiết kế nhằm **giảm thiểu nguy cơ va chạm** giữa nét hạ (descender) của Line 1 và nét vươn (ascender) của Line 2 trong điều kiện viết thông thường.
   - Thừa nhận thực tế: Người viết thực tế có thể vung nét tự do (flourish / exaggerated descenders) vượt ra ngoài biên độ $4.0\,\text{mm}$; mức độ hiệu quả thực tế và nguy cơ chồng lấn nét sẽ được quan sát, xác minh trong giai đoạn Pilot Collection.
4. **Cập nhật trạng thái phê duyệt:**
   - Nâng trạng thái từ `READY FOR VISUAL REVIEW` thành `PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)`.

---

## 2. Mục tiêu kỹ thuật & Phạm vi thiết kế của Trang P03

Trang **P03 — Sentence Flow & Pangram Collection Sheet** được thiết kế nhằm thu thập mẫu chữ viết tay ở cấp độ câu văn hoàn chỉnh và liên tục trong điều kiện công thái học tự nhiên, phục vụ việc phân tích các đặc trưng động học dòng viết mà các trang mẫu rời không thể bao quát:

1. **Natural Sentence Flow & Rhythm:** Nhịp điệu và độ mượt khi người viết duy trì nét bút liên tục qua nhiều cụm từ.
2. **Character & Word Spacing:** Khoảng cách giữa các ký tự trong từ và khoảng cách giữa các từ trong chuỗi câu dài.
3. **Baseline Stability & Drift:** Độ ổn định và độ lệch của đường chân viết (baseline) khi di chuyển cổ tay và cẳng tay qua bề rộng $184\,\text{mm}$.
4. **Slant Consistency:** Tính nhất quán của góc nghiêng nét chữ xuyên suốt câu văn.
5. **Line Transition & Natural Wrap:** Hành vi chuyển dòng tự nhiên từ dòng 1 sang dòng 2 khi câu văn vượt quá một dòng kẻ.
6. **Diacritic Placement trong chuỗi dài:** Tương tác vị trí và độ ổn định của hệ thống dấu tiếng Việt khi viết nhanh trong ngữ cảnh câu.

### Phân định ranh giới trong Collection Sheet Pack v1:
- **P01:** Isolated Characters & Diacritics (Ký tự rời và dấu chuẩn hóa hình học).
- **P02:** Context & Ligature Sheet (Từ ngữ cảnh, biến thể vị trí đầu/giữa/cuối từ và nối nét).
- **P03:** Continuous Sentence Flow & Pangrams (Dòng viết câu liên tục và bộ câu kiểm thử toàn diện).
- **P04:** Natural Paragraph Writing (Đoạn văn tự nhiên dài — *tuyệt đối không đưa đoạn văn P04 vào P03*).

> [!IMPORTANT]
> **Ranh giới công nghệ & Tính chất Demo:**
> - Đây là bản mẫu thị giác và in ấn thử nghiệm (**VISUAL / PRINTABLE PROTOTYPE**).
> - **Trạng thái hiện hành:** `PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)`.
> - Tuyệt đối chưa được sử dụng để thu thập dữ liệu chính thức.
> - Không sửa đổi mã nguồn backend, không can thiệp thuật toán CA-VHC, và không triển khai pipeline xử lý quét tự động trong nhiệm vụ này.

---

## 3. Thông số hình học khổ giấy & Vùng lề an toàn (Page Dimensions & Safe Margins)

| Thông số | Giá trị chuẩn | Đơn vị | Ghi chú kỹ thuật |
| :--- | :---: | :---: | :--- |
| **Khổ giấy vật lý** | $210.0 \times 297.0$ | mm | ISO 216 A4 Portrait (Khổ dọc chuẩn quốc tế) |
| **SVG ViewBox** | `0 0 210 297` | user units | Tỷ lệ ánh xạ chính xác: $1.0$ đơn vị vector = $1.0\,\text{mm}$ vật lý |
| **Safe Margin (Lề an toàn)** | $12.0$ | mm | Đồng nhất 4 cạnh (Trái, Phải, Trên, Dưới) |
| **Vùng nội dung khả dụng ($X$)** | $12.0 \rightarrow 198.0$ | mm | Bề rộng khả dụng tối đa: $186.0\,\text{mm}$ |
| **Vùng nội dung khả dụng ($Y$)** | $12.0 \rightarrow 285.0$ | mm | Chiều cao khả dụng tối đa: $273.0\,\text{mm}$ |
| **Tỷ lệ in ấn bắt buộc** | $100\%$ (True Scale 1:1) | — | In đúng tỷ lệ 1:1, không co giãn hoặc Fit to Page |

---

## 4. Mốc định vị góc quang học (Fiducial Markers Specification)

P03 kế thừa chuẩn xác hệ thống 4 mốc định vị góc quang học từ P01 và P02:

- **Hình dạng & Kích thước (`marker_size_mm`):** Ô vuông màu đen đặc (`#000000`), kích thước $5.0\,\text{mm} \times 5.0\,\text{mm}$.
- **Tọa độ tâm mốc (`marker_center_coordinates`):**
  - **Top-Left Center (`top_left_center_mm`):** $[14.50, 14.50]$ (tọa độ góc: $[12.00, 12.00]$)
  - **Top-Right Center (`top_right_center_mm`):** $[195.50, 14.50]$ (tọa độ góc: $[193.00, 12.00]$)
  - **Bottom-Left Center (`bottom_left_center_mm`):** $[14.50, 282.50]$ (tọa độ góc: $[12.00, 280.00]$)
  - **Bottom-Right Center (`bottom_right_center_mm`):** $[195.50, 282.50]$ (tọa độ góc: $[193.00, 280.00]$)
- **Khoảng cách giữa hai tâm theo trục ngang ($D_x$):** $181.00\,\text{mm}$
- **Khoảng cách giữa hai tâm theo trục dọc ($D_y$):** $268.00\,\text{mm}$
- **Đường chéo kiểm tra lý thuyết:** $\sqrt{181.00^2 + 268.00^2} \approx 323.39\,\text{mm}$
- **Khoảng hở an toàn quang học:** Mọi khối chữ, dải nhãn và đường kẻ cách mép fiducials tối thiểu $5.0\,\text{mm}$, bảo đảm không có nét vẽ giao cắt mốc.

---

## 5. Ranh giới các phân vùng chức năng (Section Boundaries)

Bố cục P03 được phân bổ thoáng đãng theo trục dọc với 3 Sentence Blocks độc lập:

| Phân vùng | Tên hiển thị | Tọa độ $Y$ bắt đầu | Tọa độ $Y$ kết thúc | Chiều cao | Nội dung / Chức năng |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Header & Metadata** | Tiêu đề, số hiệu mẫu, mã ẩn danh | $12.50\,\text{mm}$ | $33.50\,\text{mm}$ | $21.00\,\text{mm}$ | Thông tin quản lý mẫu, chuẩn No PII |
| **Instructions** | Hướng dẫn viết mẫu chuẩn hóa | $35.00\,\text{mm}$ | $45.00\,\text{mm}$ | $10.00\,\text{mm}$ | Hướng dẫn tốc độ tự nhiên, cho phép xuống dòng |
| **SECTION A** | Sentence 01 (`SENT_001`) | $48.00\,\text{mm}$ | $106.00\,\text{mm}$ | $58.00\,\text{mm}$ | Pangram 01 (17 từ, 72 Unicode code points) |
| **SECTION B** | Sentence 02 (`SENT_002`) | $114.00\,\text{mm}$ | $172.00\,\text{mm}$ | $58.00\,\text{mm}$ | Pangram 02 (13 từ, 54 Unicode code points) |
| **SECTION C** | Sentence 03 (`SENT_003`) | $180.00\,\text{mm}$ | $238.00\,\text{mm}$ | $58.00\,\text{mm}$ | Pangram 03 (12 từ, 54 Unicode code points) |
| **Calibration Block** | Thước đo 50mm & Ô vuông 20×20mm | $256.50\,\text{mm}$ | $278.50\,\text{mm}$ | $22.00\,\text{mm}$ | Khối kiểm chuẩn tỷ lệ quang học đồng nhất |
| **Footer** | Thông số scan quang học chuẩn | $280.00\,\text{mm}$ | $286.50\,\text{mm}$ | $6.50\,\text{mm}$ | Tiêu chuẩn quét phẳng 600 DPI 1:1 |

- **Khoảng cách đệm giữa các Sentence Block (`block_gap`):** $8.00\,\text{mm}$.
- **Khoảng cách từ Section C đến Calibration Block:** $18.50\,\text{mm}$ (vùng đệm rộng rãi chống nhiễu quang học).

---

## 6. Cấu trúc hình học Sentence Block (Block Dimensions & Two-Tier Architecture)

Mỗi Sentence Block được xây dựng với bề rộng hào phóng và phân tầng độc lập nhằm bảo đảm chữ in máy và nét viết tay không bao giờ giao nhau:

- **Bề rộng khối (`block_width`):** $184.00\,\text{mm}$ ($X \in [13.00, 197.00]\,\text{mm}$).
- **Chiều cao khối (`block_height`):** $58.00\,\text{mm}$ (nằm trong khoảng thiết kế đề xuất $50 - 58\,\text{mm}$).
- **Phân tầng độc lập 2 vùng (Two-Tier Structure):**
  1. **Vùng nhãn in máy (`prompt_header_height` = $12.00\,\text{mm}$):**
     - $Y \in [Y_{\text{start}}, Y_{\text{start}} + 12.00]\,\text{mm}$.
     - Nền xám nhạt trung tính `#f4f6f8`, viền `#888888` mỏng $0.30\,\text{mm}$.
     - Dòng trên ($Y_{\text{local}} = 4.20\,\text{mm}$): Mã định danh `SENT_xxx` (Courier bold $2.2\,\text{mm}$) kèm tag `SENTENCE_FLOW / PANGRAM_SET` bên trái, và tiêu đề phân vùng `SECTION x — SENTENCE xx` bên phải.
     - Dòng dưới ($Y_{\text{local}} = 9.80\,\text{mm}$): Nhãn `Prompt:` (Helvetica bold $1.7\,\text{mm}$) và toàn văn câu mẫu in máy kiểu có chân chuẩn mực (Times New Roman bold $2.7\,\text{mm}$).
     - Đường kẻ đáy phân cách nét liền `#777777`, dày $0.28\,\text{mm}$.
     - **Nguyên tắc cô lập tuyệt đối:** Toàn bộ câu mẫu in máy nằm trọn trong vùng header $12.0\,\text{mm}$, **tuyệt đối không nằm trong handwriting zone**, bảo đảm giải thuật cắt ảnh tự động không bao giờ lẫn chữ in máy vào mẫu viết.
  2. **Vùng viết tay tự nhiên (`writing_zone_height` = $46.00\,\text{mm}$):**
     - $Y \in [Y_{\text{start}} + 12.00, Y_{\text{start}} + 58.00]\,\text{mm}$.
     - Hoàn toàn sạch chữ in máy, chứa 2 đường dòng viết tự nhiên có khoảng cách công thái học rộng rãi.

---

## 7. Thông số hình học dòng viết tự nhiên (Natural Line Geometry & Guide Line Specification)

Trong hệ tọa độ nội bộ của Writing Zone (gốc $Y_{\text{wz}} = 0.00\,\text{mm}$ tại đáy dải nhãn prompt):

| Dòng / Đường kẻ | Tọa độ $Y_{\text{wz}}$ | Kiểu nét | Màu sắc & Nét vẽ | Chức năng công thái học |
| :--- | :---: | :--- | :--- | :--- |
| **Đáy Prompt Header** | $0.00\,\text{mm}$ | Nét liền | `#777777`, dày $0.28\,\text{mm}$ | Ranh giới cấm chạm giữa nhãn máy và nét viết |
| **Đệm trên Line 1** | $0.00 \rightarrow 4.50$ | Khoảng trống $4.50\,\text{mm}$ | — | Vùng đệm cho dấu thanh vươn cao trên dòng 1 |
| **Line 1 — Ascender Line** | $4.50\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Giới hạn đỉnh chữ vươn cao dòng 1 (b, d, đ, h, k, l) |
| **Line 1 — x-height Line** | $8.50\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Chiều cao thân chữ thường dòng 1 (a, c, e, m, n, o, u) |
| **Line 1 — Baseline (Chân)** | $13.50\,\text{mm}$ | Nét liền | `#7e7e7e`, dày $0.28\,\text{mm}$ | Đường đặt bút viết chuẩn Line 1; có mấu chỉ thị biên |
| **Line 1 — Descender Line** | $17.50\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Giới hạn chân chữ hạ dòng 1 (g, y, p, q) |
| **Đệm an toàn giữa 2 dòng** | $17.50 \rightarrow 27.50$ | Khoảng trống $10.00\,\text{mm}$ | — | **Khoảng hở an toàn chống va chạm Line 1 và Line 2** |
| **Line 2 — Ascender Line** | $27.50\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Giới hạn đỉnh chữ vươn cao dòng 2 |
| **Line 2 — x-height Line** | $31.50\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Chiều cao thân chữ thường dòng 2 |
| **Line 2 — Baseline (Chân)** | $36.50\,\text{mm}$ | Nét liền | `#7e7e7e`, dày $0.28\,\text{mm}$ | Đường đặt bút viết chuẩn Line 2; có mấu chỉ thị biên |
| **Line 2 — Descender Line** | $40.50\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Giới hạn chân chữ hạ dòng 2 |
| **Đệm đáy Writing Zone** | $40.50 \rightarrow 46.00$ | Khoảng trống $5.50\,\text{mm}$ | — | Chống tràn nét chạm đáy khung viền Sentence Block |

- **Chiều cao thân x-height:** $13.50 - 8.50 = 5.00\,\text{mm}$ (giá trị thử nghiệm kỹ thuật / engineering demo default được lựa chọn cho đánh giá handwriting ergonomics trong giai đoạn Pilot; chưa phải chuẩn công thái học đã được chứng minh khoa học. Kích thước vùng viết và khoảng cách các đường kẻ sẽ được kiểm chuẩn, tinh chỉnh cùng người viết: *writing-zone dimensions and guide spacing will be validated with pilot writers*).
- **Khoảng vươn Ascender:** $8.50 - 4.50 = 4.00\,\text{mm}$.
- **Khoảng hạ Descender:** $17.50 - 13.50 = 4.00\,\text{mm}$.
- **Khoảng cách giữa 2 Baseline (Line Pitch):** $36.50 - 13.50 = 23.00\,\text{mm}$.
- **Khoảng cách đệm giữa 2 dòng (Clear Inter-Line Spacing):** $27.50 - 17.50 = 10.00\,\text{mm}$. Khoảng đệm $10.00\,\text{mm}$ được thiết kế nhằm giảm thiểu nguy cơ va chạm giữa nét hạ (descender) của Line 1 (như *g, y*) và nét đỉnh vươn (ascender) của Line 2 (như *h, l, đ*) trong điều kiện viết thông thường. Do người viết thực tế có thể vung nét tự do (flourish / exaggerated descenders) vượt qua đường descender $4.0\,\text{mm}$, mức độ hiệu quả thực tế và nguy cơ chồng lấn nét sẽ được quan sát, xác minh trong giai đoạn Pilot Collection.
- **Mấu chỉ thị Baseline (Registration Ticks):** Đoạn vạch đậm $0.35\,\text{mm}$ màu `#555555` tại 2 mép biên ($X \in [13.0, 14.2]$ và $[195.8, 197.0]$) trên cả 2 Baseline, hỗ trợ thuật toán định vị dòng viết tự động.
- **Tính tách lọc quang học (Optical Separability):** Các guide line sử dụng màu xám nhạt (`#d0d0d0`) nét đứt và baseline `#7e7e7e`. Khả năng tách lọc tự động guide line khỏi nét mực viết tay sẽ được xác minh thực nghiệm trong pha quét thử nghiệm Pilot (*guide-line separability will be validated during pilot scanning*).

---

## 8. Nguyên tắc không ép dòng & Cho phép ngắt dòng tự nhiên (Natural Wrap Allowed)

Phiếu P03 tuân thủ triệt để nguyên tắc nghiên cứu ngôn ngữ học chữ viết tay:
1. **Không phân mảnh câu (No Tokenization):** Không in các ô chữ nhật rời rạc hay chia câu thành từng từ cố định.
2. **Không ép điểm xuống dòng (No Forced Line-Break):** Nhóm nghiên cứu không quy định từ nào phải nằm ở Dòng 1 hay Dòng 2. Người viết được tự do viết với tốc độ, kích cỡ chữ và khoảng cách từ quen thuộc của bản thân; khi hết dòng 1 thì tự nhiên ngắt dòng và viết tiếp trên dòng 2 (*natural wrap*).
3. **Mục tiêu trích xuất (Extraction Intent):** Mẫu phân tích chính của downstream pipeline là **toàn bộ vùng viết tay của câu (`writing_bbox_mm`)**, nắm bắt toàn vẹn nhịp điệu dòng chảy ngôn ngữ (sentence flow).

---

## 9. Bảng ánh xạ tọa độ tất định (Deterministic Sample Bounding Box Mapping)

Mọi tọa độ được tính theo đơn vị milimét vật lý từ gốc trên-trái trang giấy $(X=0.00, Y=0.00)$:
- `bbox_mm = [x, y, width, height]`: Khung bao toàn bộ Sentence Block (gồm nhãn máy và vùng viết).
- `prompt_bbox_mm = [x, y, width, prompt_height]`: Vùng nhãn in máy chứa câu mẫu chuẩn.
- `writing_bbox_mm = [x, y + prompt_height, width, writing_height]`: Toàn bộ vùng viết tay tự nhiên 2 dòng.
- `line_1_bbox_mm / line_2_bbox_mm`: Khung bao hình học từng dòng viết (*chỉ mang tính chất hướng dẫn hình học — geometric guides only, không phải là phân đoạn ngữ nghĩa câu*).

### Bảng tổng hợp tọa độ:

| Tham số | `SENT_001` (Section A) | `SENT_002` (Section B) | `SENT_003` (Section C) |
| :--- | :--- | :--- | :--- |
| **Câu prompt chuẩn** | *"Do bạch kim rất quý nên qua thời gian phong thổ vẫn giữ màu sáng rực rỡ."* | *"Cậu bé xinh đẹp này phóng vèo qua dãy phố cổ mù sương."* | *"Hoàng tử nhảy múa cùng các cô gái vùng biển xanh biếc."* |
| **Độ dài câu** | 17 từ • 72 Unicode code points (bao gồm khoảng trắng và dấu câu) | 13 từ • 54 Unicode code points (bao gồm khoảng trắng và dấu câu) | 12 từ • 54 Unicode code points (bao gồm khoảng trắng và dấu câu) |
| **Context Tag** | `SENTENCE_FLOW / PANGRAM_SET` | `SENTENCE_FLOW / PANGRAM_SET` | `SENTENCE_FLOW / PANGRAM_SET` |
| **Mục đích nghiên cứu** | Continuous sentence flow, word spacing, diacritic placement, baseline stability | Mixed character shapes, spacing, ascender/descender behavior, sentence rhythm | Continuous writing, multi-word spacing, diacritic-rich flow, line stability |
| **Toàn khối (`bbox_mm`)** | `[13.00, 48.00, 184.00, 58.00]` | `[13.00, 114.00, 184.00, 58.00]` | `[13.00, 180.00, 184.00, 58.00]` |
| **Vùng nhãn (`prompt_bbox_mm`)** | `[13.00, 48.00, 184.00, 12.00]` | `[13.00, 114.00, 184.00, 12.00]` | `[13.00, 180.00, 184.00, 12.00]` |
| **Vùng viết (`writing_bbox_mm`)** | `[13.00, 60.00, 184.00, 46.00]` | `[13.00, 126.00, 184.00, 46.00]` | `[13.00, 192.00, 184.00, 46.00]` |
| **Dòng 1 (`line_1_bbox_mm`)** | `[13.00, 60.00, 184.00, 23.00]` | `[13.00, 126.00, 184.00, 23.00]` | `[13.00, 192.00, 184.00, 23.00]` |
| **Dòng 2 (`line_2_bbox_mm`)** | `[13.00, 83.00, 184.00, 23.00]` | `[13.00, 149.00, 184.00, 23.00]` | `[13.00, 215.00, 184.00, 23.00]` |

> [!NOTE]
> **Quy ước đếm tất định (Deterministic Counting Convention):**
> - **Số từ (Words):** Được tính chính xác bằng số lượng token phân tách bởi khoảng trắng (`len(prompt.split())`).
> - **Số ký tự (Characters):** Được tính theo số lượng điểm mã Unicode (`len(prompt)` Unicode code points), bao gồm toàn bộ ký tự chữ, khoảng trắng và dấu chấm câu kết thúc:
>   - `SENT_001`: 17 từ | 72 Unicode code points (56 ký tự không tính khoảng trắng; 55 chữ cái tiếng Việt).
>   - `SENT_002`: 13 từ | 54 Unicode code points (42 ký tự không tính khoảng trắng; 41 chữ cái tiếng Việt).
>   - `SENT_003`: 12 từ | 54 Unicode code points (43 ký tự không tính khoảng trắng; 42 chữ cái tiếng Việt).

---

## 10. Khối kiểm chuẩn tỷ lệ & Biến dạng quang học (Calibration Block Specification)

Kế thừa chính xác thiết kế khối kiểm chuẩn chuẩn hóa của P01 và P02 ($Y \in [256.50, 278.50]\,\text{mm}$):

### 10.1. Thước đo chính xác 50.0 mm (50 mm Precision Calibration Ruler)
- **Vị trí:** Đường gốc tại $Y = 270.00\,\text{mm}$, trải dài từ $X = 22.00 \rightarrow 72.00\,\text{mm}$ (chiều dài chính xác $50.00\,\text{mm}$).
- **Cấu trúc vạch chia:**
  - Vạch chính mỗi $10\,\text{mm}$ (0, 10, 20, 30, 40, 50): cao $3.2\,\text{mm}$, dày $0.30\,\text{mm}$, có nhãn số.
  - Vạch trung mỗi $5\,\text{mm}$: cao $2.0\,\text{mm}$, dày $0.22\,\text{mm}$.
  - Vạch nhỏ mỗi $1\,\text{mm}$: cao $1.0\,\text{mm}$, dày $0.14\,\text{mm}$.
- **PILOT ENGINEERING THRESHOLD — TO BE VALIDATED:**
  - *Wording trên bản in:* `Pilot check: 50.0 ± 0.2 mm span • PILOT ENGINEERING THRESHOLD — TO BE VALIDATED`.
  - *Ngưỡng dung sai kỹ thuật:* Chiều dài vạch đo $0 \rightarrow 50\,\text{mm}$ thực tế kiểm tra bằng thước kẹp hoặc thước lá đạt $50.0 \pm 0.2\,\text{mm}$.
  - *Trạng thái:* Đây là giá trị mặc định kỹ thuật (Engineering Default) phục vụ kiểm tra in thử trong pha Pilot; chưa phải ngưỡng nghiệm thu khoa học chính thức.

### 10.2. Ô vuông kiểm chuẩn tỷ lệ cạnh 20.0 × 20.0 mm (Calibration Square)
- **Vị trí & Kích thước:** $X \in [125.00, 145.00]\,\text{mm}$, $Y \in [257.50, 277.50]\,\text{mm}$ ($W = 20.00\,\text{mm}, H = 20.00\,\text{mm}$).
- **Chữ thập căn tâm (Center Crosshairs):** Chiều dài $6.0\,\text{mm}$ giao nhau tại $(135.00, 267.50)\,\text{mm}$.
- **PILOT ENGINEERING THRESHOLD — TO BE VALIDATED:**
  - Tỷ lệ khung hình (Aspect Ratio): $W / H = 1.000 \pm 0.005$.
  - *Trạng thái:* Đây là giá trị mặc định kỹ thuật (Engineering Default) để phát hiện biến dạng co dãn phi đối xứng giữa trục X và Y của máy quét; chưa phải ngưỡng nghiệm thu chính thức của đề tài.

---

## 11. Giả định kỹ thuật & Tuyên bố Engineering Demo Defaults

> [!IMPORTANT]
> **Ranh giới khoa học & Tuyên bố Engineering Demo Defaults:**
> 1. **Engineering Demo Defaults:** Toàn bộ các lựa chọn thiết kế trong bản P03 Demo v0.1:
>    - Chiều cao Sentence Block ($58.00\,\text{mm}$) và chiều cao Writing Zone ($46.00\,\text{mm}$).
>    - Thiết kế 2 dòng viết tự nhiên có khoảng cách đệm an toàn $10.00\,\text{mm}$.
>    - Chiều cao thân x-height ($5.00\,\text{mm}$), ascender ($4.00\,\text{mm}$) và descender ($4.00\,\text{mm}$).
>    - Chiều cao dải nhãn in máy ($12.00\,\text{mm}$).
>    - Lựa chọn bộ 3 câu pangram tiếng Việt.
>    - Các ngưỡng dung sai đo lường kiểm chuẩn ($\pm 0.2\,\text{mm}$ và $\pm 0.005$).  
>    **hiện thời đều là các giá trị mặc định thử nghiệm kỹ thuật (Engineering Demo Defaults)** nhằm phục vụ đánh giá thị giác, bố cục in ấn và tính công thái học của người viết.
> 2. **Không Overclaim:** Nhóm nghiên cứu tuyệt đối **không tuyên bố** các thông số trên là cấu hình tối ưu tuyệt đối (optimal), đã được chứng minh khoa học (scientifically validated), hay là cấu hình nghiệm thu chính thức cuối cùng (final formal collection configuration). Bộ câu pangrams chưa được tuyên bố là bao phủ toàn bộ tổ hợp ký tự toán học cho đến khi có báo cáo phân tích độ phủ (coverage analysis) độc lập.
> 3. **Bảo vệ quyền riêng tư & Dữ liệu cá nhân (No PII):**
>    - Tuyệt đối không có trường thu thập: Họ tên, Mã số sinh viên, Email, Số điện thoại, Địa chỉ, hoặc Chữ ký.
>    - Người tham gia chỉ được định danh qua mã số ẩn danh `Writer ID: W_________` được quản lý bởi quy trình mã hóa ngoại tuyến tách biệt.
> 4. **Trạng thái phê duyệt hiện hành:**
>    ```text
>    PILOT CANDIDATE
>    AWAITING PILOT PRINT & SCAN VALIDATION
>    NOT APPROVED FOR FORMAL DATA COLLECTION
>    ```
