# OmniDraw — Technical Notes: Handwriting Collection Sheet P02 Demo v0.1

**Tài liệu:** Báo cáo thông số kỹ thuật & Thiết kế hình học phiếu thu thập mẫu P02 (Demo Layout v0.1)  
**Mã tài liệu:** `NOTE-P02-DEMO-LAYOUT-v0.1`  
**Phiên bản:** `ODW-HW-P02-DEMO-v0.1`  
**Ngày lập:** 20/09/2026 (Cập nhật sau vòng Correction & Cleanup)  
**Chế độ tài liệu:** VISUAL / PRINTABLE PROTOTYPE SPECIFICATION  
**Trạng thái phê duyệt:** PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)  

---

## 1. Tóm tắt các điều chỉnh kỹ thuật & Ngữ nghĩa trong vòng Cleanup (Changelog)

1. **Sửa chú giải tiếng Việt (Vietnamese Annotation Fixes):**
  - `CTX_MED_001 — thuyền`: Đã sửa từ lỗi "dấu ngã" thành *"Cụm nguyên âm u-y-ê; dấu huyền trên ê. Dùng để quan sát ligature, spacing và diacritic interaction trong chuỗi viết liên tục"*.
  - `CTX_MED_002 — nghiêng`: Đã sửa từ lỗi "dấu sắc" thành *"Cụm i-ê; không có dấu thanh (thanh ngang). Dùng để quan sát ligature và spacing trong cụm nguyên âm/phụ âm phức tạp"*.
  - `CTX_INIT_004 — Chào mừng`: Đã chuẩn hóa mô tả thành *"Dấu huyền trên a trong 'Chào'; ư mang dấu huyền trong 'mừng'"* (phản ánh chính xác cả hai âm tiết).
  - `CTX_FINAL_004 — tình`: Đã sửa thành *"Nét kết thúc h / terminal exit stroke; dấu huyền trên i"* (chữ h mang đặc tính ascender và nét thoát ngang baseline, không phải ký tự đuôi hạ).
2. **Đồng nhất ngữ nghĩa khối kiểm chuẩn (Calibration Consistency):**
  - Xóa bỏ hoàn toàn câu mang tính tuyệt đối *"must equal exactly 50.0 mm"* trên PDF và tài liệu.
  - Thống nhất ngưỡng dung sai thước đo: `Pilot check: 50.0 ± 0.2 mm (PILOT ENGINEERING THRESHOLD — TO BE VALIDATED)`.
  - Khẳng định cả hai ngưỡng đo ($\pm 0.2\text{mm}$ và $\pm 0.005$) đều là các giá trị thử nghiệm kỹ thuật (Pilot Engineering Thresholds), chưa phải tiêu chuẩn nghiệm thu chính thức đã được chứng minh khoa học.
3. **Chuẩn hóa tuyên bố x-height (x-height Wording Cleanup):**
  - Loại bỏ claim *"x-height chuẩn công thái học cho sổ tay người lớn"*.
  - Thay bằng diễn đạt trung thực khoa học: *"Giá trị x-height thử nghiệm kỹ thuật, được chọn để đánh giá công thái học trong giai đoạn Pilot (Engineering demo x-height selected for pilot handwriting evaluation)"*.
  - Bổ sung xác nhận: Chiều cao vùng viết và khoảng cách các đường kẻ sẽ được xác minh, tinh chỉnh thực nghiệm cùng người viết trong giai đoạn Pilot (*writing-zone height and guide spacing will be validated with pilot writers*).
4. **Chuẩn hóa màu sắc Section Banners (Grayscale Cleanup):**
  - Chuyển màu nền từ xanh xám (`#e8edf2`, viền `#99aab5`) sang dải xám trung tính (`#eeeeee`, viền `#aaaaaa`, text `#222222` / `#666666`), được lựa chọn để hỗ trợ quá trình quét grayscale và giảm phụ thuộc màu sắc/ grayscale.
5. **Cập nhật trạng thái phê duyệt:**
  - Chuyển từ `READY FOR VISUAL REVIEW` thành `PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)`.

---

## 2. Mục tiêu kỹ thuật & Phạm vi thiết kế của Trang P02

Trang **P02 — Context & Ligature Collection Sheet** được thiết kế nhằm thu thập mẫu chữ viết tay tiếng Việt trong ngữ cảnh từ và cụm từ thực tế, phục vụ việc phân tích các đặc trưng động học và hình học mà trang P01 (ký tự rời và dấu đơn lẻ) không thể bao quát:

1. **Contextual Allographs:** Sự biến dạng hình dáng ký tự khi đặt cạnh các ký tự khác (vị trí đầu từ, giữa từ, cuối từ).
2. **Word-Initial / Medial / Final Variants:** Nét bắt đầu (entry stroke), biến thể thân từ, và nét thoát/kết thúc (exit stroke).
3. **Ligature & Connector Behavior:** Hành vi nối nét liên tục giữa các ký tự liền kề (vết trượt nối, khoảng cách ký tự liên từ).
4. **Diacritic Interaction trong chuỗi ký tự:** Vị trí dấu thanh và dấu phụ khi viết liền mạch trong từ có nhiều nguyên âm/phụ âm phức tạp.
5. **Bridge–Diacritic Collision Risk:** Thu thập dữ liệu thực tế tại các vùng có nguy cơ xảy ra va chạm hình học giữa nét nối cầu (bridge) và dấu thanh/dấu phụ.

> [!IMPORTANT]
> **Ranh giới công nghệ & Tính chất Demo:**
>
> - Đây là bản mẫu thị giác và in ấn thử nghiệm (**VISUAL / PRINTABLE PROTOTYPE**).
> - **Trạng thái hiện hành:** `PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)`.
> - Tuyệt đối chưa được sử dụng để thu thập dữ liệu chính thức (**NOT APPROVED FOR FORMAL DATA COLLECTION**).
> - Không sửa đổi mã nguồn backend, không can thiệp thuật toán CA-VHC, và không triển khai pipeline xử lý quét tự động trong nhiệm vụ này.

---

## 3. Thông số hình học khổ giấy & Vùng lề an toàn (Page Dimensions & Safe Margins)


| Thông số                         | Giá trị chuẩn            | Đơn vị     | Ghi chú kỹ thuật                                                    |
| -------------------------------- | ------------------------ | ---------- | ------------------------------------------------------------------- |
| **Khổ giấy vật lý**              | $210.0 \times 297.0$     | mm         | ISO 216 A4 Portrait (Khổ dọc chuẩn quốc tế)                         |
| **SVG ViewBox**                  | `0 0 210 297`            | user units | Tỷ lệ ánh xạ chính xác: $1.0$ đơn vị vector = $1.0\text{mm}$ vật lý |
| **Safe Margin (Lề an toàn)**     | $12.0$                   | mm         | Đồng nhất 4 cạnh (Trái, Phải, Trên, Dưới)                           |
| **Vùng nội dung khả dụng ($X$)** | $12.0 \rightarrow 198.0$ | mm         | Bề rộng khả dụng tối đa: $186.0\text{mm}$                           |
| **Vùng nội dung khả dụng ($Y$)** | $12.0 \rightarrow 285.0$ | mm         | Chiều cao khả dụng tối đa: $273.0\text{mm}$                         |
| **Tỷ lệ in ấn bắt buộc**         | $100$ (True Scale 1:1)   | —          | In đúng kích thước 1:1, vô hiệu hóa tính năng "Fit to Page"         |


---

## 4. Mốc định vị góc quang học (Fiducial Markers Specification)

P02 tái sử dụng hoàn toàn hệ thống 4 mốc định vị quang học góc của P01 nhằm đảm bảo tính tương thích đồng nhất cho các giải thuật nắn góc (deskew), phát hiện góc trang và xác định tỷ lệ co giãn quang học:

- **Hình dạng & Kích thước (`marker_size_mm`):** Ô vuông màu đen đặc (`#000000`), kích thước $5.0\text{mm} \times 5.0\text{mm}$.
- **Tọa độ tâm mốc (`marker_center_coordinates`):**
  - **Top-Left Center (`top_left_center_mm`):** $[14.50, 14.50]$ (tọa độ góc: $[12.00, 12.00]$)
  - **Top-Right Center (`top_right_center_mm`):** $[195.50, 14.50]$ (tọa độ góc: $[193.00, 12.00]$)
  - **Bottom-Left Center (`bottom_left_center_mm`):** $[14.50, 282.50]$ (tọa độ góc: $[12.00, 280.00]$)
  - **Bottom-Right Center (`bottom_right_center_mm`):** $[195.50, 282.50]$ (tọa độ góc: $[193.00, 280.00]$)
- **Khoảng cách giữa hai tâm theo trục ngang ($D_x$):** $181.00\text{mm}$
- **Khoảng cách giữa hai tâm theo trục dọc ($D_y$):** $268.00\text{mm}$
- **Đường chéo kiểm tra lý thuyết:** $\sqrt{181.00^2 + 268.00^2} \approx 323.39\text{mm}$
- **Khoảng hở an toàn quang học:** Mọi khối chữ, dải nhãn và đường kẻ cách mép fiducials tối thiểu $5.0\text{mm}$, bảo đảm không có nét vẽ giao cắt mốc.

---

## 5. Ranh giới các phân vùng chức năng (Section Boundaries)

Bố cục P02 được phân tách thành 3 phân vùng nghiên cứu chính, phân bố liên tục từ trên xuống dưới:


| Phân vùng             | Tên hiển thị                     | Tọa độ $Y$ bắt đầu | Tọa độ $Y$ kết thúc | Chiều cao        | Số hàng mẫu |
| --------------------- | -------------------------------- | ------------------ | ------------------- | ---------------- | ----------- |
| **Header & Metadata** | Tiêu đề, số hiệu mẫu, mã ẩn danh | $12.50\text{mm}$   | $33.50\text{mm}$    | $21.00\text{mm}$ | —           |
| **Instructions**      | Hướng dẫn viết mẫu chuẩn hóa     | $35.00\text{mm}$   | $44.50\text{mm}$    | $9.50\text{mm}$  | —           |
| **SECTION A**         | Word Initial / Phrase Initial    | $46.00\text{mm}$   | $98.20\text{mm}$    | $52.20\text{mm}$ | 4 hàng      |
| **SECTION B**         | Word Medial & Ligature Challenge | $100.00\text{mm}$  | $176.40\text{mm}$   | $76.40\text{mm}$ | 6 hàng      |
| **SECTION C**         | Word Final Variants              | $178.20\text{mm}$  | $254.60\text{mm}$   | $76.40\text{mm}$ | 6 hàng      |
| **Calibration Block** | Thước đo 50mm & Ô vuông 20×20mm  | $256.50\text{mm}$  | $278.50\text{mm}$   | $22.00\text{mm}$ | —           |
| **Footer**            | Thông số scan quang học chuẩn    | $280.00\text{mm}$  | $286.50\text{mm}$   | $6.50\text{mm}$  | —           |


- **Banner phân vùng (`section_banner`):** Chiều cao $3.50\text{mm}$, nền xám trung tính `#eeeeee`, viền xám `#aaaaaa` mỏng $0.25\text{mm}$ (chuẩn grayscale, không dùng tint màu).
- **Khoảng cách đệm giữa các Section (`section_gap`):** $1.80\text{mm}$.

---

## 6. Cấu trúc hình học hàng viết (Row & Writing Zone Geometry)

Khác với P01 sử dụng lưới ô chữ nhật ngắn ($43.5 \times 31.0\text{mm}$), P02 sử dụng **hàng viết ngang kéo dài (horizontal continuous rows)** để đáp ứng công thái học viết từ và ngữ cảnh câu:

- **Bề rộng hàng viết (`row_width`):** $184.00\text{mm}$ ($X \in [13.00, 197.00]\text{mm}$).
- **Chiều cao hàng viết (`row_height`):** $11.60\text{mm}$.
- **Khoảng cách giữa các hàng (`row_gap`):** $0.50\text{mm}$.
- **Phân tầng độc lập 2 vùng (Two-Tier Structure):**
  1. **Tầng dải nhãn in máy (`label_strip_height` = $3.50\text{mm}$):**
    - Nền xám `#f4f6f8`, viền bao `#888888` mỏng $0.28\text{mm}$.
    - Đường kẻ đáy phân cách nét liền `#777777`, dày $0.25\text{mm}$.
    - Bên trái: `Sample ID` (Courier bold $1.8\text{mm}$) + `Context Tag` (Helvetica $1.4\text{mm}$).
    - Bên phải: `Prompt: [Từ mẫu]` (Times New Roman serif bold $3.2\text{mm}$).
    - **Nguyên tắc cốt lõi:** Chữ in máy nằm hoàn toàn ở dải nhãn trên, **tuyệt đối không nằm trong vùng handwriting**, loại bỏ nguy cơ lẫn chữ in vào dữ liệu trích xuất của người viết.
  2. **Tầng viết tay thuần túy (`writing_zone_height` = $8.10\text{mm}$):**
    - $Y_{\text{local}} \in [3.50, 11.60]\text{mm}$ theo tọa độ nội bộ của hàng.
    - Hoàn toàn trống chữ in máy, chỉ chứa 4 đường kẻ hướng dẫn quang học.

---

## 7. Thông số các đường kẻ hướng dẫn viết (Guide Line Specification)

Trong hệ tọa độ nội bộ của từng hàng ($Y_{\text{local}} = 0.00\text{mm}$ tại đỉnh hàng):


| Đường kẻ                    | Tọa độ $Y_{\text{local}}$ | Kiểu nét                     | Màu sắc & Nét vẽ               | Chức năng công thái học                         |
| --------------------------- | ------------------------- | ---------------------------- | ------------------------------ | ----------------------------------------------- |
| **Đáy dải nhãn**            | $3.50\text{mm}$           | Nét liền                     | `#777777`, dày $0.25\text{mm}$ | Ranh giới cấm chạm giữa nhãn máy và nét viết    |
| **Đệm trên (Top Buffer)**   | $3.50 \rightarrow 4.70$   | Khoảng trống $1.20\text{mm}$ | —                              | Vùng đệm cho dấu mũ/dấu thanh nhô cao           |
| **Ascender Line**           | $4.70\text{mm}$           | Nét đứt (dash $1.2, 1.2$)    | `#d0d0d0`, dày $0.18\text{mm}$ | Giới hạn đỉnh chữ cao (b, d, đ, h, k, l)        |
| **x-height Line**           | $6.90\text{mm}$           | Nét đứt (dash $1.2, 1.2$)    | `#d0d0d0`, dày $0.18\text{mm}$ | Giới hạn thân chữ thường (a, c, e, m, n, o, u)  |
| **Baseline (Đường chân)**   | $9.80\text{mm}$           | Nét liền                     | `#7e7e7e`, dày $0.26\text{mm}$ | Đường đặt bút viết chuẩn; có mấu chỉ thị ở biên |
| **Descender Line**          | $11.00\text{mm}$          | Nét đứt (dash $1.2, 1.2$)    | `#d0d0d0`, dày $0.18\text{mm}$ | Giới hạn chân chữ rủ (g, y, p, q)               |
| **Đệm đáy (Bottom Buffer)** | $11.00 \rightarrow 11.60$ | Khoảng trống $0.60\text{mm}$ | —                              | Chống tràn nét viết chạm đáy khung viền         |


- **Chiều cao thân x-height:** $9.80 - 6.90 = 2.90\text{mm}$ (giá trị x-height thử nghiệm kỹ thuật, được chọn để đánh giá công thái học trong giai đoạn Pilot — *engineering demo x-height selected for pilot handwriting evaluation*).
- **Khoảng vươn Ascender:** $6.90 - 4.70 = 2.20\text{mm}$.
- **Khoảng hạ Descender:** $11.00 - 9.80 = 1.20\text{mm}$.
- **Tổng chiều cao vùng nét hữu hiệu (Descender $\rightarrow$ Ascender):** $11.00 - 4.70 = 6.30\text{mm}$.
- **Đánh giá thực nghiệm:** Chiều cao vùng viết và khoảng cách các đường kẻ sẽ được xác minh, tinh chỉnh thực nghiệm cùng người viết trong giai đoạn Pilot (*writing-zone height and guide spacing will be validated with pilot writers*).
- **Mấu chỉ thị chân đường viết (Registration Edge Ticks):** Đoạn vạch đậm $0.35\text{mm}$ màu `#555555` tại 2 mép biên ($X \in [13.0, 14.2]$ và $[195.8, 197.0]$) ngang với Baseline, hỗ trợ thuật toán căn dòng khi nét kẻ bị mờ.
- **Tính tách biệt quang học (Optical Separability):** Các guide line sử dụng màu xám nhạt (`#d0d0d0`) và nét mảnh. Khả năng tách lọc tự động guide line khỏi nét mực đen sẽ được xác minh thực nghiệm trong pha quét thử nghiệm Pilot (*guide separability will be validated during pilot scanning*).

---

## 8. Bảng ánh xạ tọa độ vùng mẫu tất định (Deterministic Bounding Box Mapping)

Mọi tọa độ dưới đây được tính theo đơn vị milimét từ gốc trên-trái trang giấy $(X=0.00, Y=0.00)$:

- `bbox_mm = [x, y, width, height]`: Khung chữ nhật bao quanh toàn bộ hàng (bao gồm dải nhãn trên).
- `writing_bbox_mm = [x, y + 3.50, width, height - 3.50]`: Vùng viết tay thuần túy phục vụ giải thuật tự động cắt ảnh (auto-crop), hoàn toàn sạch chữ in máy.


| Sample ID       | Section | Row | Prompt / Target | Context Tag              | Ghi chú nghiên cứu đã chuẩn hóa                                       | Toàn hàng (`bbox_mm`)            | Vùng viết (`writing_bbox_mm`)   |
| --------------- | ------- | --- | --------------- | ------------------------ | --------------------------------------------------------------------- | -------------------------------- | ------------------------------- |
| `CTX_INIT_001`  | A       | 1   | **Kính gửi**    | `WORD_INITIAL`           | Cụm từ mở đầu, chữ hoa K, khoảng cách từ                              | `[13.00, 50.30, 184.00, 11.60]`  | `[13.00, 53.80, 184.00, 8.10]`  |
| `CTX_INIT_002`  | A       | 2   | **Thân gửi**    | `WORD_INITIAL`           | Cụm từ mở đầu, chữ hoa T, nối nét h-â-n                               | `[13.00, 62.40, 184.00, 11.60]`  | `[13.00, 65.90, 184.00, 8.10]`  |
| `CTX_INIT_003`  | A       | 3   | **Cảm ơn**      | `WORD_INITIAL`           | Cụm từ mở đầu, dấu hỏi trên a, dấu ơ                                  | `[13.00, 74.50, 184.00, 11.60]`  | `[13.00, 78.00, 184.00, 8.10]`  |
| `CTX_INIT_004`  | A       | 4   | **Chào mừng**   | `WORD_INITIAL`           | Dấu huyền trên a trong "Chào"; ư mang dấu huyền trong "mừng"          | `[13.00, 86.60, 184.00, 11.60]`  | `[13.00, 90.10, 184.00, 8.10]`  |
| `CTX_MED_001`   | B       | 1   | **thuyền**      | `WORD_MEDIAL / LIGATURE` | Cụm u-y-ê, dấu huyền trên ê; ligature/diacritic challenge             | `[13.00, 104.30, 184.00, 11.60]` | `[13.00, 107.80, 184.00, 8.10]` |
| `CTX_MED_002`   | B       | 2   | **nghiêng**     | `WORD_MEDIAL / LIGATURE` | Cụm i-ê; không có dấu thanh (thanh ngang); ligature/spacing challenge | `[13.00, 116.40, 184.00, 11.60]` | `[13.00, 119.90, 184.00, 8.10]` |
| `CTX_MED_003_A` | B       | 3   | **trường**      | `LIGATURE CHALLENGE`     | [Trial A] Nối r-ư-ờ-n-g, nguy cơ va chạm cầu                          | `[13.00, 128.50, 184.00, 11.60]` | `[13.00, 132.00, 184.00, 8.10]` |
| `CTX_MED_003_B` | B       | 4   | **trường**      | `LIGATURE CHALLENGE`     | [Trial B] Đo lường biến thiên nội tại (intra-writer)                  | `[13.00, 140.60, 184.00, 11.60]` | `[13.00, 144.10, 184.00, 8.10]` |
| `CTX_MED_004_A` | B       | 5   | **nguyễn**      | `LIGATURE CHALLENGE`     | [Trial A] Nối u-y-ễ-n, dấu ngã trên ê phức tạp                        | `[13.00, 152.70, 184.00, 11.60]` | `[13.00, 156.20, 184.00, 8.10]` |
| `CTX_MED_004_B` | B       | 6   | **nguyễn**      | `LIGATURE CHALLENGE`     | [Trial B] Đo lường biến thiên nội tại (intra-writer)                  | `[13.00, 164.80, 184.00, 11.60]` | `[13.00, 168.30, 184.00, 8.10]` |
| `CTX_FINAL_001` | C       | 1   | **bạn**         | `WORD_FINAL`             | Nét kết thúc n, dấu nặng dưới a                                       | `[13.00, 182.50, 184.00, 11.60]` | `[13.00, 186.00, 184.00, 8.10]` |
| `CTX_FINAL_002` | C       | 2   | **nam**         | `WORD_FINAL`             | Nét kết thúc m, thân chữ thấp                                         | `[13.00, 194.60, 184.00, 11.60]` | `[13.00, 198.10, 184.00, 8.10]` |
| `CTX_FINAL_003` | C       | 3   | **nhìn**        | `WORD_FINAL`             | Nét kết thúc n, chấm i và dấu huyền                                   | `[13.00, 206.70, 184.00, 11.60]` | `[13.00, 210.20, 184.00, 8.10]` |
| `CTX_FINAL_004` | C       | 4   | **tình**        | `WORD_FINAL`             | Nét kết thúc h / terminal exit stroke; dấu huyền trên i               | `[13.00, 218.80, 184.00, 11.60]` | `[13.00, 222.30, 184.00, 8.10]` |
| `CTX_FINAL_005` | C       | 5   | **mộc**         | `WORD_FINAL`             | Nét kết thúc c, dấu ô và dấu nặng                                     | `[13.00, 230.90, 184.00, 11.60]` | `[13.00, 234.40, 184.00, 8.10]` |
| `CTX_FINAL_006` | C       | 6   | **hoa**         | `WORD_FINAL`             | Nét thoát nguyên âm mở a                                              | `[13.00, 243.00, 184.00, 11.60]` | `[13.00, 246.50, 184.00, 8.10]` |


---

## 9. Khối kiểm chuẩn tỷ lệ & Biến dạng quang học (Calibration Block Specification)

Khu vực kiểm chuẩn nằm tại đáy trang ($Y \in [256.50, 278.50]\text{mm}$), có cấu trúc và tọa độ hoàn toàn đồng nhất với trang P01:

### 9.1. Thước đo chính xác 50.0 mm (50 mm Precision Calibration Ruler)

- **Vị trí:** Đường gốc tại $Y = 270.00\text{mm}$, trải dài từ $X = 22.00 \rightarrow 72.00\text{mm}$ (chiều dài chính xác $50.00\text{mm}$).
- **Cấu trúc vạch chia:**
  - Vạch chính mỗi $10\text{mm}$ (0, 10, 20, 30, 40, 50): cao $3.2\text{mm}$, dày $0.30\text{mm}$, có nhãn số.
  - Vạch trung mỗi $5\text{mm}$: cao $2.0\text{mm}$, dày $0.22\text{mm}$.
  - Vạch nhỏ mỗi $1\text{mm}$: cao $1.0\text{mm}$, dày $0.14\text{mm}$.
- **PILOT ENGINEERING THRESHOLD — TO BE VALIDATED:**
  - *Wording trên bản in:* `Pilot check: 50.0 ± 0.2 mm span • PILOT ENGINEERING THRESHOLD — TO BE VALIDATED`.
  - *Ngưỡng dung sai kỹ thuật:* Chiều dài vạch đo $0 \rightarrow 50\text{mm}$ thực tế kiểm tra bằng thước kẹp hoặc thước lá đạt $50.0 \pm 0.2\text{mm}$.
  - *Trạng thái:* Đây là giá trị mặc định kỹ thuật (Engineering Default) phục vụ kiểm tra in thử trong pha Pilot; chưa phải ngưỡng nghiệm thu khoa học chính thức.

### 9.2. Ô vuông kiểm chuẩn tỷ lệ cạnh 20.0 × 20.0 mm (Calibration Square)

- **Vị trí & Kích thước:** $X \in [125.00, 145.00]\text{mm}$, $Y \in [257.50, 277.50]\text{mm}$ ($W = 20.00\text{mm}, H = 20.00\text{mm}$).
- **Chữ thập căn tâm (Center Crosshairs):** Chiều dài $6.0\text{mm}$ giao nhau tại $(135.00, 267.50)\text{mm}$.
- **PILOT ENGINEERING THRESHOLD — TO BE VALIDATED:**
  - Tỷ lệ khung hình (Aspect Ratio): $W / H = 1.000 \pm 0.005$.
  - *Trạng thái:* Đây là giá trị mặc định kỹ thuật (Engineering Default) để phát hiện biến dạng co dãn phi đối xứng giữa trục X và Y của máy quét; chưa phải ngưỡng nghiệm thu chính thức của đề tài.

---

## 10. Giả định kỹ thuật & Tuyên bố Engineering Demo Defaults

> [!IMPORTANT]
> **Ranh giới khoa học & Tuyên bố Engineering Demo Defaults:**
>
> 1. **Engineering Demo Defaults:** Toàn bộ các lựa chọn thiết kế trong bản P02 Demo v0.1:
>   - Quy mô 16 hàng mẫu (4 hàng Section A, 6 hàng Section B, 6 hàng Section C).
>   - Chiều cao hàng $11.60\text{mm}$ và dải nhãn $3.50\text{mm}$.
>   - Thiết kế 2 cặp lặp thử nghiệm Trial A/B (`trường`, `nguyễn`).
>   - Khoảng cách các đường kẻ guide lines (x-height $2.90\text{mm}$, ascender $2.20\text{mm}$, descender $1.20\text{mm}$).
>   - Danh mục 14 từ mẫu tiếng Việt.
>   - Ngưỡng dung sai đo lường ($\pm 0.2\text{mm}$ và $\pm 0.005$).  
>    **hiện thời đều là các giá trị mặc định thử nghiệm kỹ thuật (Engineering Demo Defaults)** nhằm phục vụ đánh giá thị giác, bố cục in ấn và tính công thái học của người viết.
> 2. **Không Overclaim:** Nhóm nghiên cứu tuyệt đối **không tuyên bố** các thông số trên là cấu hình tối ưu tuyệt đối (optimal), đã được chứng minh khoa học (scientifically validated), hay là cấu hình nghiệm thu chính thức cuối cùng (final formal collection configuration).
> 3. **Bảo vệ quyền riêng tư & Dữ liệu cá nhân (No PII):**
>   - Tuyệt đối không có trường thu thập: Họ tên, Mã số sinh viên, Email, Số điện thoại, Địa chỉ, hoặc Chữ ký.
>   - Người tham gia chỉ được định danh qua mã số ẩn danh `Writer ID: W_________` được quản lý bởi quy trình mã hóa ngoại tuyến tách biệt.
> 4. **Trạng thái phê duyệt hiện hành:**
>   ```text
>    PILOT CANDIDATE
>    AWAITING PILOT PRINT & SCAN VALIDATION
>    NOT APPROVED FOR FORMAL DATA COLLECTION
>   ```

