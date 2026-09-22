# OmniDraw — Technical Notes: Handwriting Collection Sheet P01 Demo v0.2

**Tài liệu:** Báo cáo thông số kỹ thuật & Thiết kế hình học phiếu thu thập mẫu P01 (Demo Layout v0.2)  
**Mã tài liệu:** `NOTE-P01-DEMO-LAYOUT-v0.2`  
**Phiên bản:** `ODW-HW-P01-DEMO-v0.2`  
**Ngày lập:** 20/09/2026  
**Chế độ tài liệu:** VISUAL / PRINTABLE PROTOTYPE SPECIFICATION  
**Trạng thái phê duyệt:** PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)  

---

## 1. Tóm tắt các điều chỉnh kỹ thuật & ngữ nghĩa trong v0.2 (Changelog)

Bản cập nhật `v0.2` tập trung vào việc làm sạch ngữ nghĩa (wording cleanup) và chuẩn hóa thông số kỹ thuật hình học (technical cleanup) để sẵn sàng làm ứng viên thử nghiệm in/quét (Pilot Candidate):

1. **Page Metadata:** Sửa `Page: P01 / P02` thành `Page: P01` duy nhất. Trang P02 trong bộ Collection Sheet Pack được dành riêng cho *Context & Ligature Sheet* (từ ngữ cảnh và cặp ký tự nối nét), không phải là trang nối dài của P01.
2. **Header Terminology:** Thay thế `CONFIDENTIAL RESEARCH PROTOCOL` bằng `RESEARCH USE ONLY` để diễn đạt chuẩn mực cho một phiếu khảo sát học thuật phi thương mại khi chưa có chính sách bảo mật nội bộ chính thức.
3. **Quy định về bút viết (Pen Specification):** Bỏ việc áp đặt bắt buộc các thương hiệu cụ thể; chuyển thành quy định chung: *"Dùng bút gel đen 0.5 mm do nhóm cung cấp (hoặc tương thích); không dùng bút xanh, dạ hoặc chì"*. Các dòng bút Pentel EnerGel hoặc Pilot G2 đóng vai trò tài liệu tham khảo khuyến nghị cho tính tương thích quang học.
4. **Calibration Block Wording:** Đơn giản hóa nội dung hình vuông kiểm chuẩn thành *"Supports checking X/Y scale consistency and scan distortion"*, tránh các kết luận tuyệt đối về bước động cơ máy quét.
5. **Đánh dấu Pilot Engineering Thresholds:** Toàn bộ các ngưỡng dung sai kiểm chuẩn ($\pm 0.2\,\text{mm}$ và $\pm 0.005$) được phân loại rõ ràng là các ngưỡng mặc định kỹ thuật (Pilot Engineering Thresholds — To be validated), không tuyên bố là các chuẩn nghiệm thu nghiên cứu chính thức đã được chứng minh.
6. **Làm sạch mô tả quang học Guide Line:** Bỏ claim `<15% K` lý thuyết, thay bằng mô tả trung tính xác nhận màu sắc `#d0d0d0` và cơ chế thực nghiệm trong pha Pilot.
7. **Bổ sung Technical Geometry & Bounding Box Mapping:** Lập bảng tham chiếu tọa độ chi tiết từng milimét cho 24 ô viết (`bbox_mm` và `writing_bbox_mm`), phục vụ giải thuật tự động cắt ảnh (auto-crop) tất định.

---

## 2. Thông số hình học khổ giấy & Vùng lề (Page & Margins)

| Thông số | Giá trị chuẩn | Đơn vị | Ghi chú kỹ thuật |
| :--- | :---: | :---: | :--- |
| **Khổ giấy** | $210.0 \times 297.0$ | mm | ISO 216 A4 Portrait (Khổ dọc chuẩn) |
| **Hệ tọa độ vector (SVG ViewBox)** | `0 0 210 297` | user units | $1.0$ đơn vị vector tương ứng chính xác $1.0\,\text{mm}$ vật lý |
| **Safe Margin (Lề an toàn)** | $12.0$ | mm | Đều 4 cạnh (Trái, Phải, Trên, Dưới) |
| **Vùng nội dung khả dụng ($X$)** | $12.0 \rightarrow 198.0$ | mm | Bề rộng khả dụng: $186.0\,\text{mm}$ |
| **Vùng nội dung khả dụng ($Y$)** | $12.0 \rightarrow 285.0$ | mm | Chiều cao khả dụng: $273.0\,\text{mm}$ |
| **Tỷ lệ in ấn bắt buộc** | $100\%$ (True Scale 1:1) | — | Tắt các chế độ co giãn tự động của máy in |

---

## 3. Mốc định vị góc (Fiducial Markers Specification)

4 mốc vuông màu đen đặc phục vụ các giải thuật thị giác máy tính tự động phát hiện góc trang, nắn thẳng (deskew) và kiểm tra tỷ lệ co dãn quang học:

- **Kích thước mốc (`marker_size_mm`):** $5.0\,\text{mm} \times 5.0\,\text{mm}$
- **Tọa độ tâm mốc (`marker_center_coordinates`):**
  - **Top-Left Center (`top_left_center_mm`):** $[14.50, 14.50]$
  - **Top-Right Center (`top_right_center_mm`):** $[195.50, 14.50]$
  - **Bottom-Left Center (`bottom_left_center_mm`):** $[14.50, 282.50]$
  - **Bottom-Right Center (`bottom_right_center_mm`):** $[195.50, 282.50]$
- **Khoảng cách giữa hai tâm theo trục ngang ($D_x$):** $181.00\,\text{mm}$
- **Khoảng cách giữa hai tâm theo trục dọc ($D_y$):** $268.00\,\text{mm}$
- **Khoảng cách đường chéo lý thuyết:** $\sqrt{181.00^2 + 268.00^2} \approx 323.39\,\text{mm}$
- **Khoảng hở an toàn:** Cách mép các khối chữ và lưới tối thiểu $5.0\,\text{mm}$, bảo đảm không có nét vẽ nào giao cắt hoặc chạm vào marker.

---

## 4. Thông số lưới & Cấu trúc ô thu thập (Grid & Cell Dimensions)

### 4.1. Lưới tổng thể (Grid Dimensions)
- **Gốc tọa độ lưới (`grid_origin_mm`):** $[13.00, 53.50]$ (Góc trên-trái của ô đầu tiên)
- **Số cột (`column_count`):** $4$
- **Số hàng (`row_count`):** $6$
- **Tổng số ô mẫu (`total_sample_cells`):** $24$
- **Tổng bề rộng lưới:** $184.00\,\text{mm}$ (từ $X = 13.00$ đến $197.00\,\text{mm}$)
- **Tổng chiều cao lưới:** $201.00\,\text{mm}$ (từ $Y = 53.50$ đến $254.50\,\text{mm}$)
- **Khoảng cách ngang giữa các ô (`horizontal_gap`):** $3.333\,\text{mm}$
- **Khoảng cách dọc giữa các ô (`vertical_gap`):** $3.000\,\text{mm}$

### 4.2. Cấu trúc nội bộ từng ô (Cell Internal Anatomy)
- **Kích thước bao ô (`cell_width` $\times$ `cell_height`):** $43.50\,\text{mm} \times 31.00\,\text{mm}$
- **Độ dày viền ngoài:** $0.30\,\text{mm}$, màu xám trung tính `#888888`, bo góc $R = 0.50\,\text{mm}$
- **Phân tách hai tầng độc lập:**
  1. **Tầng dải nhãn in máy (`label_strip_height`):**
     - Chiều cao: $6.50\,\text{mm}$ ($Y \in [0.00, 6.50]\,\text{mm}$ theo tọa độ nội bộ ô).
     - Nền: Xám nhạt `#f4f6f8` với đường kẻ đáy $0.30\,\text{mm}$ (`#777777`).
     - Chứa: Mã định danh mẫu (`Sample ID`) bên trái và ký tự mẫu chuẩn (`Target: [x]`) bên phải.
  2. **Tầng viết tay (`writing_zone_height`):**
     - Chiều cao: $24.50\,\text{mm}$ ($Y \in [6.50, 31.00]\,\text{mm}$ theo tọa độ nội bộ ô).
     - Hoàn toàn trống chữ in máy, chỉ chứa 4 đường kẻ hướng dẫn quang học.

---

## 5. Tọa độ các đường kẻ hướng dẫn viết (Guide Line Specification)

Trong hệ tọa độ nội bộ ô (Local Cell Coordinate, gốc tại đỉnh ô $Y_{\text{local}} = 0.00\,\text{mm}$):

| Đường kẻ | Tọa độ $Y_{\text{local}}$ | Kiểu nét | Màu sắc & Độ dày | Ý nghĩa công thái học |
| :--- | :---: | :--- | :--- | :--- |
| **Đáy dải nhãn** | $6.50\,\text{mm}$ | Nét liền | `#777777`, dày $0.30\,\text{mm}$ | Ranh giới cấm chạm giữa chữ in và chữ viết |
| **Đệm an toàn trên** | $6.50 \rightarrow 10.50$ | Vùng trống $4.00\,\text{mm}$ | — | Khoảng không gian đệm cho dấu mũ, dấu thanh |
| **Ascender Line** | $10.50\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Giới hạn đỉnh vươn của chữ cao (d, đ, h, k, l, b) |
| **x-height Line** | $16.50\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Chiều cao thân chữ cái thường (a, e, o, u, n, m) |
| **Baseline (Đường chân)** | $22.50\,\text{mm}$ | Nét liền | `#7e7e7e`, dày $0.28\,\text{mm}$ | Đường đặt bút chuẩn; có mấu chỉ thị ở 2 biên |
| **Descender Line** | $27.50\,\text{mm}$ | Nét đứt (dash $1.2, 1.2$) | `#d0d0d0`, dày $0.18\,\text{mm}$ | Giới hạn đuôi chữ rủ xuống (g, y, p, q) |
| **Đệm an toàn đáy** | $27.50 \rightarrow 31.00$ | Vùng trống $3.50\,\text{mm}$ | — | Chống tràn nét xuống khung viền ô dưới |

- **Khoảng vươn Ascender:** $16.50 - 10.50 = 6.00\,\text{mm}$
- **Chiều cao thân x-height:** $22.50 - 16.50 = 6.00\,\text{mm}$
- **Khoảng hạ Descender:** $27.50 - 22.50 = 5.00\,\text{mm}$
- **Đặc tính quang học khi quét (Optical Separability):** Các guide line sử dụng màu xám nhạt (`#d0d0d0`) và nét mảnh nhằm giảm mức độ chi phối thị giác trong ảnh scan. Khả năng tách guide line khỏi nét mực viết tay sẽ được xác minh thực nghiệm trong giai đoạn Pilot Collection.

---

## 6. Bảng tọa độ vùng mẫu tất định (Deterministic Sample Bounding Box Mapping)

Mọi tọa độ dưới đây được tính theo milimét từ góc trên-trái trang giấy $(X=0.00, Y=0.00)$:
- `bbox_mm = [x, y, width, height]`: Toàn bộ ô bao gồm dải nhãn.
- `writing_bbox_mm = [x, y + 6.50, width, height - 6.50]`: Vùng viết tay thuần túy phục vụ cắt ảnh (auto-crop) ký tự viết tay.

| Sample ID | Target | Row | Col | Toàn ô (`bbox_mm`) | Vùng viết (`writing_bbox_mm`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `BASE_001` | **a** | 1 | 1 | `[13.00, 53.50, 43.50, 31.00]` | `[13.00, 60.00, 43.50, 24.50]` |
| `BASE_002` | **e** | 1 | 2 | `[59.83, 53.50, 43.50, 31.00]` | `[59.83, 60.00, 43.50, 24.50]` |
| `BASE_003` | **o** | 1 | 3 | `[106.67, 53.50, 43.50, 31.00]` | `[106.67, 60.00, 43.50, 24.50]` |
| `BASE_004` | **u** | 1 | 4 | `[153.50, 53.50, 43.50, 31.00]` | `[153.50, 60.00, 43.50, 24.50]` |
| `STR_001` | **ă** | 2 | 1 | `[13.00, 87.50, 43.50, 31.00]` | `[13.00, 94.00, 43.50, 24.50]` |
| `STR_002` | **â** | 2 | 2 | `[59.83, 87.50, 43.50, 31.00]` | `[59.83, 94.00, 43.50, 24.50]` |
| `STR_003` | **ê** | 2 | 3 | `[106.67, 87.50, 43.50, 31.00]` | `[106.67, 94.00, 43.50, 24.50]` |
| `STR_004` | **ơ** | 2 | 4 | `[153.50, 87.50, 43.50, 31.00]` | `[153.50, 94.00, 43.50, 24.50]` |
| `TONE_001` | **á** | 3 | 1 | `[13.00, 121.50, 43.50, 31.00]` | `[13.00, 128.00, 43.50, 24.50]` |
| `TONE_002` | **à** | 3 | 2 | `[59.83, 121.50, 43.50, 31.00]` | `[59.83, 128.00, 43.50, 24.50]` |
| `TONE_003` | **ả** | 3 | 3 | `[106.67, 121.50, 43.50, 31.00]` | `[106.67, 128.00, 43.50, 24.50]` |
| `TONE_004` | **ạ** | 3 | 4 | `[153.50, 121.50, 43.50, 31.00]` | `[153.50, 128.00, 43.50, 24.50]` |
| `SEC_001` | **đ** | 4 | 1 | `[13.00, 155.50, 43.50, 31.00]` | `[13.00, 162.00, 43.50, 24.50]` |
| `STR_005` | **ư** | 4 | 2 | `[59.83, 155.50, 43.50, 31.00]` | `[59.83, 162.00, 43.50, 24.50]` |
| `BASE_005` | **n** | 4 | 3 | `[106.67, 155.50, 43.50, 31.00]` | `[106.67, 162.00, 43.50, 24.50]` |
| `BASE_006` | **m** | 4 | 4 | `[153.50, 155.50, 43.50, 31.00]` | `[153.50, 162.00, 43.50, 24.50]` |
| `CMP_001` | **ắ** | 5 | 1 | `[13.00, 189.50, 43.50, 31.00]` | `[13.00, 196.00, 43.50, 24.50]` |
| `CMP_002` | **ấ** | 5 | 2 | `[59.83, 189.50, 43.50, 31.00]` | `[59.83, 196.00, 43.50, 24.50]` |
| `CMP_003` | **ố** | 5 | 3 | `[106.67, 189.50, 43.50, 31.00]` | `[106.67, 196.00, 43.50, 24.50]` |
| `CMP_004` | **ở** | 5 | 4 | `[153.50, 189.50, 43.50, 31.00]` | `[153.50, 196.00, 43.50, 24.50]` |
| `REP_001` | **ế (Trial A)** | 6 | 1 | `[13.00, 223.50, 43.50, 31.00]` | `[13.00, 230.00, 43.50, 24.50]` |
| `REP_002` | **ế (Trial B)** | 6 | 2 | `[59.83, 223.50, 43.50, 31.00]` | `[59.83, 230.00, 43.50, 24.50]` |
| `REP_003` | **ử (Trial A)** | 6 | 3 | `[106.67, 223.50, 43.50, 31.00]` | `[106.67, 230.00, 43.50, 24.50]` |
| `REP_004` | **ử (Trial B)** | 6 | 4 | `[153.50, 223.50, 43.50, 31.00]` | `[153.50, 230.00, 43.50, 24.50]` |

---

## 7. Khối kiểm chuẩn tỷ lệ (Calibration Block Specifications)

Khu vực kiểm chuẩn nằm tại $Y \in [256.50, 278.50]\,\text{mm}$ (chiều cao $22.00\,\text{mm}$):

### 7.1. 50 mm Precision Calibration Ruler
- **Chiều dài:** $50.00\,\text{mm}$ ($X \in [22.00, 72.00]\,\text{mm}$, tại $Y = 270.00\,\text{mm}$).
- **Cấu trúc vạch:** Vạch lớn $10\,\text{mm}$ ($3.2\,\text{mm}$), vạch trung $5\,\text{mm}$ ($2.0\,\text{mm}$), vạch nhỏ $1\,\text{mm}$ ($1.0\,\text{mm}$).
- **PILOT ENGINEERING THRESHOLD — TO BE VALIDATED:**
  - *Pilot engineering tolerance:* Khoảng cách thực tế in ấn vạch $0 \rightarrow 50\,\text{mm}$ = $50.0 \pm 0.2\,\text{mm}$.
  - *Trạng thái:* Đây là giá trị mặc định kỹ thuật (Engineering default) để kiểm tra in thử trong pha Pilot; chưa phải ngưỡng nghiệm thu chính thức đã được xác thực của đề tài.

### 7.2. 20.0 × 20.0 mm Aspect Ratio Square
- **Kích thước:** chính xác $20.00\,\text{mm} \times 20.00\,\text{mm}$ ($X \in [125.00, 145.00]\,\text{mm}$, $Y \in [257.50, 277.50]\,\text{mm}$).
- **Chữ thập tâm:** dài $6.00\,\text{mm}$ tại $(135.00, 267.50)\,\text{mm}$.
- **PILOT ENGINEERING THRESHOLD — TO BE VALIDATED:**
  - *Pilot engineering check:* Tỷ lệ chiều rộng / chiều cao $W/H = 1.000 \pm 0.005$.
  - *Trạng thái:* Đây là giá trị mặc định kỹ thuật (Engineering default) nhằm phát hiện các biến dạng co giãn tỷ lệ quang học lộ liễu; ngưỡng chấp nhận cuối cùng sẽ được xác định sau các phiên đo đạc thực nghiệm Pilot.

---

## 8. Giả định kỹ thuật & Tuyên bố Engineering Demo Defaults

> [!IMPORTANT]
> **Ranh giới kỹ thuật & Tính trung thực khoa học:**
> 1. **Engineering Demo Defaults:** Toàn bộ các thông số kích thước ô ($43.50 \times 31.00\,\text{mm}$), chiều cao dòng kẻ, quy mô 24 ô, 2 lượt lặp Trial A/B, cùng các ngưỡng dung sai ($\pm 0.2\,\text{mm}$ và $\pm 0.005$) là các giá trị mặc định thử nghiệm kỹ thuật (Engineering Defaults) phục vụ đánh giá bố cục in ấn và kiểm thử thị giác.
> 2. **Không tuyên bố tối ưu tuyệt đối:** Nhóm nghiên cứu tuyệt đối không tuyên bố các giá trị hình học hay ngưỡng đo đạc này là tối ưu tuyệt đối về mặt khoa học hoặc đã được xác thực thực nghiệm diện rộng.
> 3. **Bảo vệ dữ liệu cá nhân (No PII):** Phiếu không thu thập bất kỳ thông tin định danh cá nhân nào (họ tên, MSSV, SĐT, email, chữ ký). Người viết chỉ được quản lý qua mã ẩn danh `Writer ID: W___` tách biệt ngoại tuyến.
> 4. **Trạng thái phê duyệt:** Chưa được phê duyệt cho giai đoạn Pilot Collection (**NOT YET APPROVED FOR PILOT COLLECTION**).  
>    **Trạng thái hiện hành:** `PILOT CANDIDATE — AWAITING PILOT PRINT & SCAN VALIDATION (NOT APPROVED FOR FORMAL DATA COLLECTION)`.
