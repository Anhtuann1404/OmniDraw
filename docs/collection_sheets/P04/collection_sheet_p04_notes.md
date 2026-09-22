# OmniDraw — Technical Notes: Handwriting Collection Sheet P04 Demo v0.1

**Tài liệu:** Báo cáo thông số kỹ thuật & Thiết kế hình học phiếu thu thập mẫu P04 (Demo Layout v0.1)  
**Mã tài liệu:** `NOTE-P04-DEMO-LAYOUT-v0.1`  
**Phiên bản:** `ODW-HW-P04-DEMO-v0.1`  
**Ngày lập:** 20/09/2026 (Cập nhật sau vòng P04 Scientific-Method & Wording Cleanup)  
**Chế độ tài liệu:** VISUAL / PRINTABLE PROTOTYPE SPECIFICATION  
**Trạng thái phê duyệt:** PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)  

---

## 1. Tóm tắt các điều chỉnh kỹ thuật & Ngữ nghĩa khoa học (Changelog)

1. **Chuẩn hóa ranh giới dữ liệu quét tĩnh vs. động học (Static Scan vs. Kinematic Data):**
   - Loại bỏ toàn bộ các khái niệm "động học", "nhịp điệu cơ học", "độ mượt" khỏi tài liệu, do ảnh quét tĩnh phẳng (flatbed scan / static image) không thể cung cấp dữ liệu vận tốc bút (velocity), gia tốc (acceleration), thời gian nét vẽ (stroke timing), thứ tự nét (stroke order), áp lực theo thời gian hay nhịp điệu vận động thực tế.
   - Chuyển sang thuật ngữ khoa học chuẩn xác: *các đặc trưng hình học dài hạn của chữ viết tay ở cấp đoạn văn (long-range handwriting geometry)*, *bố cục không gian dòng viết (paragraph-level spatial flow / writing layout continuity)*, và làm rõ *visual/spatial rhythm* (nhịp điệu thị giác / không gian), tuyệt đối không suy diễn nhịp điệu thời gian (temporal rhythm).
2. **Chuẩn hóa diễn giải về độ mỏi & Hiệu ứng thứ tự trang (Writer Comfort & Page-Order Considerations):**
   - Loại bỏ giả định suy diễn chưa được kiểm chứng: không quy kết sự biến thiên góc nghiêng (slant), khoảng cách (spacing) hay độ lệch baseline giữa đầu và cuối trang là "ngưỡng xuất hiện độ mỏi" (fatigue threshold). Các biến thiên trên ảnh quét tĩnh có thể bắt nguồn từ nhiều nguyên nhân (hiệu ứng thứ tự trang, tư thế tay, sự thích ứng, biến thiên tự nhiên, nhịp độ viết, tương tác bố cục).
   - Đổi tên phân mục thành *Yếu tố vận hành thu thập & Hiệu ứng thứ tự trang (Writer Comfort & Collection Burden Considerations)*.
   - Xóa bỏ hoàn toàn các từ ngữ y tế hóa trải nghiệm người viết (*co cứng cơ tay, nhịp điệu sinh học*). Định vị mục tiêu theo dõi: ghi nhận thời gian hoàn thành (`completion time`) và tần suất yêu cầu nghỉ giải lao phục vụ công tác vận hành pilot; quan sát sự biến đổi hình học từ đầu đến cuối trang như một hiệu ứng theo tiến trình viết (*page progression / page-order effects*).
3. **Chuẩn hóa cơ sở thu thập 1 lần lặp (Single Repetition Rationale):**
   - Xác định rõ: Thu thập 1 lần cho `PARA_001` nhằm mục đích giảm tải thu thập (*reduce collection burden*) và ưu tiên diện tích vùng viết thoải mái trên trang giấy; không tuyên bố 1 lần lặp là tối ưu khoa học hay ngăn ngừa triệt để độ mỏi.
4. **Hạ các khẳng định mang tính tuyệt đối (Absolute Claims Removal):**
   - Chuyển "kế thừa đồng nhất 100%" thành "tái sử dụng cùng đặc tả mốc định vị góc quang học (fiducial specification) chuẩn hóa của P01–P03".
   - Chuyển "tối ưu không gian viết" thành "ưu tiên không gian viết".
   - Chuyển khẳng định thuật toán "không bao giờ lẫn chữ in máy" thành mô tả trung thực: "cấu trúc phân tầng được thiết kế nhằm tách biệt rõ ràng vùng chữ in máy khỏi `writing_bbox_mm` và giảm thiểu nguy cơ chữ in xuất hiện trong vùng crop handwriting".
   - Giữ nguyên tắc chỉ dùng từ "tuyệt đối" cho các quy tắc quản trị dữ liệu (Governance rule: tuyệt đối không thu PII) và tuyên bố không overclaim.
5. **Nâng trạng thái phê duyệt:**
   - Nâng từ `READY FOR VISUAL REVIEW` thành `PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)`.

---

## 2. Mục tiêu kỹ thuật & Phạm vi nghiên cứu của Trang P04

Trang **P04 — Natural Paragraph Writing Collection Sheet** là trang cuối cùng trong bộ phiếu thu thập mẫu chữ viết tay 4 trang (**OmniDraw Handwriting Collection Sheet Pack v1**). Phiếu được thiết kế chuyên biệt để thu thập mẫu chữ viết tay liên tục ở cấp độ đoạn văn (continuous paragraph level) trong điều kiện tự nhiên, phục vụ việc phân tích các đặc trưng hình học dài hạn của chữ viết tay ở cấp đoạn văn (long-range handwriting geometry & spatial flow) mà các trang mẫu trước không thể bao quát:

1. **Long-Range Baseline Stability & Drift:** Sự ổn định hoặc độ trôi dần của đường chân viết (baseline drift) khi người viết di chuyển tay liên tục qua 5 dòng kẻ trên bề rộng $184.0\,\text{mm}$.
2. **Global Slant Consistency:** Tính nhất quán và xu hướng biến thiên của góc nghiêng nét chữ xuyên suốt toàn bộ đoạn văn bản.
3. **Character & Word Spacing Distribution:** Phân phối khoảng cách giữa các ký tự trong từ và giữa các từ trong dòng văn tự nhiên.
4. **Natural Line Wrapping & Break Behavior:** Hành vi xuống dòng tự nhiên của người viết (vị trí ngắt dòng, khoảng trống biên lề phải) khi không bị ép buộc số từ trên từng dòng.
5. **Inter-Line Spacing & Interaction:** Khoảng cách giữa các dòng và sự tương tác giữa nét hạ (descender) của dòng trên với nét vươn (ascender) và dấu thanh tiếng Việt của dòng dưới.
6. **Paragraph-Level Spatial Flow & Layout Continuity:** Quan sát sự liên tục về đường chân viết (baseline), góc nghiêng (slant), khoảng cách (spacing) và bố cục chữ viết xuyên suốt đoạn văn (nhịp điệu thị giác / visual-spatial rhythm; không suy diễn nhịp điệu thời gian/temporal rhythm từ ảnh scan tĩnh).
7. **Diacritic Behavior trong chuỗi dài:** Vị trí, góc đặt và độ ổn định của hệ thống dấu tiếng Việt khi viết ở tốc độ tự nhiên trong văn bản dài.
8. **Writer-Style Geometric Features:** Thu thập các đặc trưng hình học mang tính cá nhân hóa ở cấp đoạn văn, phục vụ nghiên cứu mở rộng trong tương lai.

### Phân định ranh giới chức năng trong Collection Sheet Pack v1:
- **P01 — Isolated Characters & Diacritics:** Ký tự rời và dấu chuẩn hóa hình học.
- **P02 — Context & Ligature Sheet:** Từ ngữ cảnh, biến thể vị trí đầu/giữa/cuối từ và hành vi nối nét.
- **P03 — Sentence Flow & Pangram Sheet:** Dòng viết câu liên tục và bộ câu kiểm thử toàn diện.
- **P04 — Natural Paragraph Writing Sheet:** Đoạn văn tự nhiên liên tục dài (Paragraph-level writing).

> [!IMPORTANT]
> **Ranh giới công nghệ & Bản chất Prototype:**
> - Đây là bản mẫu thị giác và in ấn thử nghiệm (**VISUAL / PRINTABLE PROTOTYPE**).
> - **Trạng thái hiện hành:** `PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)`.
> - Tuyệt đối chưa được sử dụng để thu thập dữ liệu chính thức.
> - Không sửa đổi mã nguồn backend, không can thiệp thuật toán CA-VHC engine, và không triển khai scanning pipeline trong nhiệm vụ này.
> - Các đặc trưng hình học cấp đoạn văn được thu thập cho mục tiêu nghiên cứu dài hạn; nhóm nghiên cứu **không tuyên bố** các đặc trưng này đã đủ để xây dựng một Writer Profile hoàn chỉnh (Writer Profile vẫn là mục tiêu nghiên cứu P2 trong tương lai).

---

## 3. Thông số hình học khổ giấy & Vùng lề an toàn (Page Dimensions & Safe Margins)

Toàn bộ thông số hình học của P04 tuân thủ chặt chẽ nguyên tắc lấy đơn vị milimét vật lý làm nguồn chuẩn chân lý (Source of Truth):

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

P04 tái sử dụng cùng đặc tả mốc định vị góc quang học (fiducial specification) chuẩn hóa của P01, P02 và P03:

- **Hình dạng & Kích thước (`marker_size_mm`):** Ô vuông màu đen đặc (`#000000`), kích thước $5.0\,\text{mm} \times 5.0\,\text{mm}$.
- **Tọa độ tâm mốc (`marker_center_coordinates`):**
  - **Top-Left Center (`top_left_center_mm`):** $[14.50, 14.50]$ (tọa độ góc: $[12.00, 12.00]$)
  - **Top-Right Center (`top_right_center_mm`):** $[195.50, 14.50]$ (tọa độ góc: $[193.00, 12.00]$)
  - **Bottom-Left Center (`bottom_left_center_mm`):** $[14.50, 282.50]$ (tọa độ góc: $[12.00, 280.00]$)
  - **Bottom-Right Center (`bottom_right_center_mm`):** $[195.50, 282.50]$ (tọa độ góc: $[193.00, 280.00]$)
- **Khoảng cách giữa hai tâm theo trục ngang ($D_x$):** $181.00\,\text{mm}$
- **Khoảng cách giữa hai tâm theo trục dọc ($D_y$):** $268.00\,\text{mm}$
- **Đường chéo kiểm tra lý thuyết:** $\sqrt{181.00^2 + 268.00^2} \approx 323.39\,\text{mm}$
- **Khoảng hở an toàn quang học:** Mọi khối nội dung (khung viết, dải nhãn, thước đo) cách mép fiducials tối thiểu $5.0\,\text{mm}$. Khoảng hở an toàn quang học được thiết kế nhằm duy trì vùng tách biệt giữa nội dung trang và các fiducial markers, qua đó giảm nguy cơ nét viết hoặc thành phần in giao cắt mốc định vị.

---

## 5. Ranh giới các phân vùng chức năng trên trang (Section Boundaries)

Bố cục P04 được tổ chức theo kiến trúc **1 Paragraph Block duy nhất** thoáng đãng, ưu tiên không gian viết:

| Phân vùng | Tên hiển thị | Tọa độ $Y$ bắt đầu | Tọa độ $Y$ kết thúc | Chiều cao | Chức năng kỹ thuật |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Header & Metadata** | Tiêu đề, số hiệu mẫu, mã ẩn danh | $12.50\,\text{mm}$ | $33.50\,\text{mm}$ | $21.00\,\text{mm}$ | Quản lý mẫu nghiên cứu, tuân thủ chuẩn No PII |
| **Instructions** | Hướng dẫn viết mẫu tự nhiên | $35.00\,\text{mm}$ | $45.00\,\text{mm}$ | $10.00\,\text{mm}$ | Hướng dẫn chép tự nhiên, không áp lực tốc độ |
| **Paragraph Block** | Khối đoạn văn duy nhất (`PARA_001`) | $48.00\,\text{mm}$ | $228.00\,\text{mm}$ | $180.00\,\text{mm}$ | Gồm Prompt Region ($30\,\text{mm}$) và Writing Zone ($150\,\text{mm}$) |
| **Calibration Block** | Thước đo 50mm & Ô vuông 20×20mm | $256.50\,\text{mm}$ | $278.50\,\text{mm}$ | $22.00\,\text{mm}$ | Khối kiểm chuẩn tỷ lệ quang học và biến dạng quét |
| **Footer** | Thông số scan phẳng 600 DPI | $280.00\,\text{mm}$ | $286.50\,\text{mm}$ | $6.50\,\text{mm}$ | Tiêu chuẩn quét phẳng 1:1, ảnh PNG lossless |

- **Khoảng đệm từ Instructions đến Paragraph Block:** $3.00\,\text{mm}$.
- **Khoảng đệm từ Paragraph Block đến Calibration Block:** $28.50\,\text{mm}$ (vùng đệm quang học được bố trí nhằm giảm nguy cơ tương tác hoặc nhiễu giữa vùng viết tay và calibration block).

---

## 6. Cấu trúc hai tầng của Paragraph Block (Two-Tier Architecture)

Paragraph Block được thiết kế theo cấu trúc hai tầng nhằm tách biệt rõ ràng vùng chữ in máy và vùng viết tay về mặt bố cục, đồng thời giảm nguy cơ chữ in xuất hiện trong handwriting crop:

- **Bề rộng khối (`block_width`):** $184.00\,\text{mm}$ ($X \in [13.00, 197.00]\,\text{mm}$).
- **Chiều cao tổng thể (`block_height`):** $180.00\,\text{mm}$ ($Y \in [48.00, 228.00]\,\text{mm}$).

### 6.1. Vùng nhãn in máy (Prompt Header Region — Tier 1)
- **Kích thước:** $184.00\,\text{mm} \times 30.00\,\text{mm}$ ($Y \in [48.00, 78.00]\,\text{mm}$).
- **Màu nền & Viền:** Nền xám nhạt trung tính `#f4f6f8`, viền `#888888` mỏng $0.30\,\text{mm}$.
- **Dải nhận diện trên cùng ($Y = 52.20\,\text{mm}$):**
  - Trái: Mã định danh `PARA_001` (Courier bold $2.2\,\text{mm}$) kèm nhãn `[NATURAL_PARAGRAPH]` (Courier $1.5\,\text{mm}$, fill `#666666`).
  - Phải: Tiêu đề phân vùng `SECTION A — CONTINUOUS PARAGRAPH` (Helvetica bold $1.9\,\text{mm}$, fill `#333333`).
- **Đường phân cách phụ ($Y = 54.20\,\text{mm}$):** Nét liền `#d8d8d8`, dày $0.20\,\text{mm}$.
- **Nhãn chỉ dẫn:** `Prompt (Đoạn văn mẫu chép tay):` (Helvetica bold $1.8\,\text{mm}$, fill `#444444`) tại $Y = 58.50\,\text{mm}$.
- **Đoạn văn mẫu in máy (Machine Printed Text):** Font Times New Roman bold $2.7\,\text{mm}$, màu `#111111`, được ngắt dòng tự nhiên thành 3 dòng rõ ràng:
  - Dòng 1 ($Y = 63.20\,\text{mm}$): *"Mỗi dòng chữ nắn nót trên trang giấy trắng là nhịp cầu nối liền*
  - Dòng 2 ($Y = 68.20\,\text{mm}$): *những tấm lòng thân thương, gửi gắm trọn vẹn niềm tin cùng*
  - Dòng 3 ($Y = 73.20\,\text{mm}$): *bao ước vọng tốt đẹp nhất."*
- **Đường đáy cô lập Tier 1 ($Y = 78.00\,\text{mm}$):** Nét liền đậm `#777777`, dày $0.28\,\text{mm}$.
- **Nguyên tắc cô lập nhãn máy:** Toàn bộ văn bản in máy kết thúc tại $Y = 73.20\,\text{mm}$, tạo khoảng đệm an toàn $4.80\,\text{mm}$ trước đường biên $78.00\,\text{mm}$. Cấu trúc phân tầng này được thiết kế nhằm tách biệt rõ ràng vùng chữ in máy khỏi `writing_bbox_mm` và giảm thiểu nguy cơ chữ in xuất hiện trong vùng crop handwriting.

### 6.2. Vùng viết tay tự nhiên (Natural Writing Zone — Tier 2)
- **Kích thước:** $184.00\,\text{mm} \times 150.00\,\text{mm}$ ($Y \in [78.00, 228.00]\,\text{mm}$).
- **Cấu trúc không gian:** Một vùng phẳng duy nhất màu trắng (`#ffffff`), không chia ô chữ nhật nhỏ, không phân mảnh câu thành từng từ rời rạc.
- **Số lượng dòng hướng dẫn:** Gồm 5 dòng viết tự nhiên (5 natural writing lines), được phân bổ đều với khe rãnh hình học $30.00\,\text{mm}$ cho mỗi dòng.

---

## 7. Thông số hình học đường kẻ & Khoảng cách dòng (Natural Line Geometry)

Writing Zone gồm 5 dòng viết tự nhiên. Mỗi dòng kẻ được định vị trong khe trượt hình học cao $30.00\,\text{mm}$ (local slot: $Y_{\text{slot}} \in [0.00, 30.00]\,\text{mm}$):

| Thành phần trong khe dòng | Tọa độ nội bộ $Y_{\text{slot}}$ | Kiểu nét | Màu sắc & Nét vẽ | Ý nghĩa kỹ thuật |
| :--- | :---: | :--- | :--- | :--- |
| **Đệm đỉnh khe dòng** | $0.00 \rightarrow 7.00$ | Khoảng trống $7.00\,\text{mm}$ | — | Vùng đệm cho dấu thanh tiếng Việt vươn cao |
| **Ascender Line (Đỉnh vươn)** | $7.00\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Giới hạn đỉnh chữ vươn cao (b, d, đ, h, k, l) |
| **x-height Line (Thân chữ)** | $11.00\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Chiều cao thân chữ thường (a, c, e, o, u...) |
| **Baseline (Đường chân viết)** | $16.00\,\text{mm}$ | Nét liền | `#7e7e7e`, dày $0.28\,\text{mm}$ | Đường đặt bút chuẩn; có mấu định vị biên |
| **Descender Line (Chân hạ)** | $20.00\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Giới hạn chân chữ hạ thấp (g, y, p, q) |
| **Đệm đáy khe dòng** | $20.00 \rightarrow 30.00$ | Khoảng trống $10.00\,\text{mm}$ | — | Khoảng hở bảo vệ chống va chạm dòng |

### Bảng tọa độ 5 dòng viết thực tế trên trang (Tuyệt đối $Y_{\text{page}}$):

| Dòng viết | Ascender Line | x-height Line | Baseline ($Y_{\text{base}}$) | Descender Line | Khe dòng (`line_x_bbox_mm`) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Line 1** | $85.00\,\text{mm}$ | $89.00\,\text{mm}$ | **$94.00\,\text{mm}$** | $98.00\,\text{mm}$ | `[13.00, 78.00, 184.00, 30.00]` |
| **Line 2** | $115.00\,\text{mm}$ | $119.00\,\text{mm}$ | **$124.00\,\text{mm}$** | $128.00\,\text{mm}$ | `[13.00, 108.00, 184.00, 30.00]` |
| **Line 3** | $145.00\,\text{mm}$ | $149.00\,\text{mm}$ | **$154.00\,\text{mm}$** | $158.00\,\text{mm}$ | `[13.00, 138.00, 184.00, 30.00]` |
| **Line 4** | $175.00\,\text{mm}$ | $179.00\,\text{mm}$ | **$184.00\,\text{mm}$** | $188.00\,\text{mm}$ | `[13.00, 168.00, 184.00, 30.00]` |
| **Line 5** | $205.00\,\text{mm}$ | $209.00\,\text{mm}$ | **$214.00\,\text{mm}$** | $218.00\,\text{mm}$ | `[13.00, 198.00, 184.00, 30.00]` |

### Các thông số đo lường công thái học:
- **Chiều cao thân x-height:** $16.00 - 11.00 = 5.00\,\text{mm}$ (*Engineering demo default selected for pilot handwriting evaluation; to be validated with pilot writers*).
- **Khoảng vươn Ascender:** $11.00 - 7.00 = 4.00\,\text{mm}$.
- **Khoảng hạ Descender:** $20.00 - 16.00 = 4.00\,\text{mm}$.
- **Khoảng cách giữa hai Baseline (Line Pitch):** $124.00 - 94.00 = 30.00\,\text{mm}$.
- **Khoảng đệm thông thủy giữa 2 dòng (Clear Inter-Line Spacing):** $(30.00 - 20.00) + 7.00 = 17.00\,\text{mm}$.  
  Khoảng đệm $17.00\,\text{mm}$ được thiết kế nhằm **giảm thiểu nguy cơ va chạm** giữa nét hạ của dòng trên và nét vươn/dấu thanh của dòng dưới trong điều kiện chép văn bản dài. Mức độ hiệu quả thực tế và nguy cơ chồng lấn đối với các nét vung tự do (flourishes / exaggerated descenders) sẽ được quan sát và xác minh trong giai đoạn Pilot Collection.
- **Mấu chỉ thị Baseline (Registration Ticks):** Nét đậm $0.35\,\text{mm}$ màu `#555555` tại 2 mép biên ($X \in [13.0, 14.2]$ và $[195.8, 197.0]$) trên cả 5 Baseline. Giúp thuật toán thị giác máy tính nhận diện và ước lượng đường chân dòng một cách tất định.
- **Tính tách lọc quang học (Optical Separability):** Các guide line sử dụng màu xám nhạt (`#d0d0d0`) nét đứt và baseline `#7e7e7e`. Khả năng tách lọc tự động guide line khỏi nét mực đen của người viết sẽ được kiểm chứng thực nghiệm trong pha quét thử nghiệm Pilot (*guide-line separability will be validated during pilot scanning*).

---

## 8. Nguyên tắc chép tự nhiên & Cho phép ngắt dòng tự do (Natural Wrap Allowed)

Phiếu P04 xác lập rõ bản chất thu thập mẫu:
1. **Bản chất mẫu thu thập (Copy Paragraph, Not Free Composition):** Đây là mẫu **chép lại đoạn văn chuẩn** (Copy Paragraph / Natural Handwriting Sample), không phải bài tập làm văn tự do (Free-text composition). Người tham gia chép đúng văn bản mẫu nhưng được bảo toàn hoàn toàn nét chữ, thói quen và sự tự nhiên của bản thân.
2. **Cho phép ngắt dòng tự nhiên (Natural Line Wrapping Allowed):** Nhóm nghiên cứu không quy định từ nào phải nằm ở dòng nào, mỗi dòng phải chứa bao nhiêu từ. Người viết tự quyết định khi nào xuống dòng dựa trên kích cỡ chữ và khoảng cách quen thuộc của cá nhân.
3. **Mục tiêu trích xuất chính (Primary Extraction Target):** Downstream analysis pipeline xác định **toàn bộ vùng viết tay `writing_bbox_mm` là mẫu dữ liệu chính (Primary Sample)** của `PARA_001`. Các khung bao cấp dòng (`line_1_bbox_mm` $\rightarrow$ `line_5_bbox_mm`) chỉ đóng vai trò hướng dẫn hình học (geometric guides) phục vụ việc ước lượng baseline, đo lường độ dốc và kiểm soát chất lượng, không phải là phân đoạn ngữ nghĩa độc lập.

---

## 9. Bảng ánh xạ tọa độ tất định (Deterministic Bounding Box Mapping)

Mọi tọa độ được tính toán tất định theo đơn vị milimét từ gốc trên-trái trang giấy $(X=0.00, Y=0.00)$:

| Thuộc tính metadata | Giá trị thiết kế | Ghi chú kỹ thuật |
| :--- | :--- | :--- |
| **Sample ID** | `PARA_001` | Mã định danh mẫu đoạn văn duy nhất trong Pack v1 |
| **Context Tag** | `NATURAL_PARAGRAPH` | Thẻ phân loại ngữ cảnh đoạn văn tự nhiên |
| **Văn bản Prompt chuẩn** | *"Mỗi dòng chữ nắn nót trên trang giấy trắng là nhịp cầu nối liền những tấm lòng thân thương, gửi gắm trọn vẹn niềm tin cùng bao ước vọng tốt đẹp nhất."* | Chuẩn hóa theo Dataset Specification 08 |
| **Độ dài đoạn văn** | **32 từ • 149 điểm mã Unicode** | Bao gồm khoảng trắng và dấu câu kết thúc |
| **Số lần lặp lại (Repetition)** | 1 lần (Single repetition) | P04 v0.1 chỉ thu PARA_001 một lần nhằm giảm tải thu thập (collection burden) và ưu tiên không gian viết trên trang |
| **Khung bao toàn khối (`bbox_mm`)** | `[13.00, 48.00, 184.00, 180.00]` | Bao gồm cả phần in máy và vùng viết tay |
| **Vùng nhãn in máy (`prompt_bbox_mm`)** | `[13.00, 48.00, 184.00, 30.00]` | Chứa nhãn và đoạn văn mẫu in máy |
| **Vùng viết tay (`writing_bbox_mm`)** | `[13.00, 78.00, 184.00, 150.00]` | Vùng viết tay tự nhiên 5 dòng |
| **Dòng 1 slot (`line_1_bbox_mm`)** | `[13.00, 78.00, 184.00, 30.00]` | Baseline tại $Y = 94.00\,\text{mm}$ |
| **Dòng 2 slot (`line_2_bbox_mm`)** | `[13.00, 108.00, 184.00, 30.00]` | Baseline tại $Y = 124.00\,\text{mm}$ |
| **Dòng 3 slot (`line_3_bbox_mm`)** | `[13.00, 138.00, 184.00, 30.00]` | Baseline tại $Y = 154.00\,\text{mm}$ |
| **Dòng 4 slot (`line_4_bbox_mm`)** | `[13.00, 168.00, 184.00, 30.00]` | Baseline tại $Y = 184.00\,\text{mm}$ |
| **Dòng 5 slot (`line_5_bbox_mm`)** | `[13.00, 198.00, 184.00, 30.00]` | Baseline tại $Y = 214.00\,\text{mm}$ |

> [!NOTE]
> **Quy ước đếm tất định (Deterministic Counting Convention):**
> - **Số từ (Words):** $32$ từ, tính bằng số lượng token phân tách bởi khoảng trắng (`len(prompt.split())`).
> - **Số ký tự (Characters):** $149$ điểm mã Unicode (`len(prompt)` Unicode code points), bao gồm toàn bộ chữ cái tiếng Việt, khoảng trắng và dấu chấm câu kết thúc.
> - **Ký tự không tính khoảng trắng:** $118$ ký tự (`len(prompt.replace(" ", ""))`).
> - **Chữ cái thuần túy (Letters only):** $116$ chữ cái (`len([c for c in prompt if c.isalpha()])`).

---

## 10. Khối kiểm chuẩn tỷ lệ & Biến dạng quang học (Calibration Block Specification)

Kế thừa chính xác thiết kế khối kiểm chuẩn chuẩn hóa từ P01, P02 và P03 ($Y \in [256.50, 278.50]\,\text{mm}$):

### 10.1. Thước đo chính xác 50.0 mm (50 mm Precision Calibration Ruler)
- **Vị trí:** Đường gốc tại $Y = 270.00\,\text{mm}$, trải dài từ $X = 22.00 \rightarrow 72.00\,\text{mm}$ (chiều dài chính xác $50.00\,\text{mm}$).
- **Cấu trúc vạch chia:**
  - Vạch chính mỗi $10\,\text{mm}$ (0, 10, 20, 30, 40, 50): cao $3.2\,\text{mm}$, dày $0.30\,\text{mm}$, có nhãn số.
  - Vạch trung mỗi $5\,\text{mm}$: cao $2.0\,\text{mm}$, dày $0.22\,\text{mm}$.
  - Vạch nhỏ mỗi $1\,\text{mm}$: cao $1.0\,\text{mm}$, dày $0.14\,\text{mm}$.
- **PILOT ENGINEERING THRESHOLD — TO BE VALIDATED:**
  - *Wording trên bản in:* `Pilot check: 50.0 ± 0.2 mm span • PILOT ENGINEERING THRESHOLD — TO BE VALIDATED`.
  - *Ngưỡng dung sai kỹ thuật:* Chiều dài đo thực tế $0 \rightarrow 50\,\text{mm}$ kiểm tra bằng thước kẹp hoặc kính lúp đo lường đạt $50.0 \pm 0.2\,\text{mm}$.
  - *Bản chất:* Giá trị mặc định thử nghiệm kỹ thuật (Engineering Default) để phát hiện sai số tỷ lệ quét (scale factor); chưa phải tiêu chuẩn nghiệm thu khoa học chính thức.

### 10.2. Ô vuông kiểm chuẩn tỷ lệ cạnh 20.0 × 20.0 mm (Calibration Square)
- **Vị trí & Kích thước:** $X \in [125.00, 145.00]\,\text{mm}$, $Y \in [257.50, 277.50]\,\text{mm}$ ($W = 20.00\,\text{mm}, H = 20.00\,\text{mm}$).
- **Chữ thập căn tâm (Center Crosshairs):** Chiều dài $6.0\,\text{mm}$ giao nhau tại $(135.00, 267.50)\,\text{mm}$.
- **PILOT ENGINEERING THRESHOLD — TO BE VALIDATED:**
  - Tỷ lệ khung hình (Aspect Ratio): $W / H = 1.000 \pm 0.005$.
  - *Bản chất:* Giá trị mặc định kỹ thuật (Engineering Default) phát hiện biến dạng co giãn phi đối xứng trục X/Y của máy quét phẳng.

---

## 11. Yếu tố vận hành thu thập & Hiệu ứng thứ tự trang (Writer Comfort & Collection Burden Considerations)

1. **Vị trí trong chuỗi thu thập mẫu (Pack Sequence):** Trang P04 là trang cuối cùng trong bộ phiếu 4 trang (sau P01 ký tự rời, P02 từ ngữ cảnh, P03 câu văn liên tục).
2. **Kiểm soát tải thu thập & Sự thoải mái của người viết (Writer Comfort & Burden Management):**
   - P04 v0.1 chỉ thu `PARA_001` một lần (Single repetition) nhằm giảm tải thu thập và ưu tiên diện tích vùng viết thoải mái trên trang giấy. Nhóm nghiên cứu không tuyên bố 1 lần lặp là cấu hình tối ưu khoa học.
   - Hạn chế ảnh hưởng của phiên viết kéo dài: Giao thức thực nghiệm cho phép người tham gia nghỉ giải lao ngắn ($1 - 3$ phút) giữa trang P03 và P04 nếu người tham gia có nhu cầu.
   - Người tham gia không bị ép buộc thời gian viết hay áp lực tốc độ; được khuyến khích viết theo tốc độ và nhịp tự nhiên của bản thân.
3. **Mục tiêu quan sát trong Pilot & Hiệu ứng thứ tự trang (Page-Order Effects):**
   - Ghi nhận thời gian hoàn thành trang P04 (`completion time`) và tần suất yêu cầu nghỉ ngắn phục vụ mục đích vận hành pilot.
   - Quan sát sự thay đổi hình học của chữ viết từ đầu đến cuối trang (góc nghiêng nét chữ, khoảng cách chữ, độ trôi baseline) như một hiệu ứng theo thứ tự trang / tiến trình viết (page progression / page-order effects).
   - **Ranh giới suy luận khoa học:** Nhóm nghiên cứu tuyệt đối không quy kết các thay đổi hình học này là bằng chứng trực tiếp của độ mỏi hay "ngưỡng xuất hiện độ mỏi" (fatigue threshold) khi chưa có giao thức đo lường độ mỏi độc lập.
4. **Bảo mật & Quyền riêng tư (Strict No PII):**
   - Tuyệt đối không thu thập thông tin sức khỏe, trạng thái tâm lý, bệnh sử, cảm giác đau mỏi, hay bất kỳ dữ liệu sinh trắc nhạy cảm nào.
   - Chỉ sử dụng mã số ẩn danh `Writer ID: W_________` và số phiên `Session: S______`.

---

## 12. Giả định kỹ thuật & Tuyên bố Engineering Demo Defaults

> [!IMPORTANT]
> **Ranh giới khoa học & Tuyên bố Engineering Demo Defaults:**
> 1. **Engineering Demo Defaults:** Toàn bộ các lựa chọn thiết kế trong bản P04 Demo v0.1:
>    - Chiều cao Paragraph Block ($180.00\,\text{mm}$) và chiều cao Writing Zone ($150.00\,\text{mm}$).
>    - Số lượng 5 dòng viết tự nhiên với khoảng cách bước dòng (Line Pitch) $30.00\,\text{mm}$.
>    - Khoảng đệm thông thủy giữa các dòng $17.00\,\text{mm}$.
>    - Chiều cao thân x-height ($5.00\,\text{mm}$), ascender ($4.00\,\text{mm}$) và descender ($4.00\,\text{mm}$).
>    - Chiều cao dải nhãn in máy ($30.00\,\text{mm}$) ngắt thành 3 dòng in máy.
>    - Thu thập 1 lần lặp duy nhất cho đoạn văn `PARA_001` nhằm giảm tải thu thập và ưu tiên không gian viết.
>    - Các ngưỡng kiểm chuẩn đo lường ($\pm 0.2\,\text{mm}$ và $\pm 0.005$).  
>    **hiện thời đều là các giá trị mặc định thử nghiệm kỹ thuật (Engineering Demo Defaults)** nhằm phục vụ đánh giá thị giác và chuẩn bị cho pha in quét thử nghiệm.
> 2. **Không Overclaim:** Nhóm nghiên cứu tuyệt đối **không tuyên bố** các thông số trên là cấu hình tối ưu (optimal), đã được chứng minh khoa học (scientifically validated), hay là cấu hình hoàn chỉnh cuối cùng (final formal collection configuration). Các giá trị sẽ được đánh giá và hiệu chỉnh dựa trên dữ liệu thực nghiệm cùng người viết trong pha Pilot.
> 3. **Bảo vệ quyền riêng tư & Dữ liệu cá nhân (No PII):**
>    - Tuyệt đối không có trường thu thập: Họ tên, Mã số sinh viên, Email, Số điện thoại, Địa chỉ, hoặc Chữ ký.
>    - Người tham gia chỉ được định danh qua mã số ẩn danh `Writer ID: W_________` được quản lý bởi quy trình mã hóa ngoại tuyến tách biệt.
> 4. **Trạng thái phê duyệt hiện hành:**
>    ```text
>    PILOT CANDIDATE
>    AWAITING PILOT PRINT & SCAN VALIDATION
>    NOT APPROVED FOR FORMAL DATA COLLECTION
>    ```
