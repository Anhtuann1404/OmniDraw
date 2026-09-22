# OmniDraw Handwriting Collection Sheet Pack v1

Thư mục lưu trữ bộ biểu mẫu thu thập dữ liệu chữ viết tay tiếng Việt (**OmniDraw Handwriting Collection Sheet Pack v1**) phục vụ đề tài nghiên cứu **OmniDraw (NCKH 2026–2027)** và mô hình hóa **CA-VHC** (Context-Aware Vector Handwriting Core).

---

## 1. Cấu trúc thư mục

```text
collection_sheets/
├── README.md
├── P01/
│   ├── collection_sheet_p01.svg
│   ├── collection_sheet_p01.pdf
│   ├── collection_sheet_p01_notes.md
│   └── generate_sheet_p01.py
├── P02/
│   ├── collection_sheet_p02.svg
│   ├── collection_sheet_p02.pdf
│   ├── collection_sheet_p02_notes.md
│   └── generate_sheet_p02.py
├── P03/
│   ├── collection_sheet_p03.svg
│   ├── collection_sheet_p03.pdf
│   ├── collection_sheet_p03_notes.md
│   └── generate_sheet_p03.py
└── P04/
    ├── collection_sheet_p04.svg
    ├── collection_sheet_p04.pdf
    ├── collection_sheet_p04_notes.md
    └── generate_sheet_p04.py
```

---

## 2. Tổng quan các trang thu thập

| Trang | Tên biểu mẫu | Mục tiêu thu thập chính | Quy mô mẫu | Trạng thái kỹ thuật |
| :--- | :--- | :--- | :--- | :--- |
| **P01** | *Isolated Characters & Diacritics Sheet* | Ký tự rời, dấu thanh tiếng Việt, các biến thể chữ cái cơ bản và cấu trúc glyph độc lập | 24 ô mẫu ($4 \times 6$ grid) | `PILOT CANDIDATE` |
| **P02** | *Context & Ligature Collection Sheet* | Từ ngữ cảnh, biến thể vị trí (*initial / medial / final*), hành vi nối nét (*ligatures*) và tương tác dấu thanh | 16 dòng mẫu (3 sections A/B/C) | `PILOT CANDIDATE` |
| **P03** | *Sentence Flow & Pangram Collection Sheet* | Dòng chảy câu liên tục, ổn định baseline, bố cục không gian, khoảng cách từ/ký tự trên chuỗi dài | 3 khối câu pangram tiếng Việt | `PILOT CANDIDATE` |
| **P04** | *Natural Paragraph Writing Collection Sheet* | Chép đoạn văn tự nhiên, độ trôi baseline dài hạn, góc nghiêng nhất quán, ngắt dòng tự do | 1 đoạn văn chuẩn 32 từ (5 dòng) | `PILOT CANDIDATE` |

---

## 3. Đặc tả kỹ thuật chung (Pack Specifications)

1. **Khổ giấy:** Chuẩn quốc tế ISO A4 Portrait ($210.00\,\text{mm} \times 297.00\,\text{mm}$).
2. **Hệ thống mốc định vị quang học (Fiducial Markers):**
   - 4 ô vuông màu đen đặc $5.0\,\text{mm} \times 5.0\,\text{mm}$ tại 4 góc trang giấy.
   - Tọa độ tâm mốc: $[14.50, 14.50]$, $[195.50, 14.50]$, $[14.50, 282.50]$, $[195.50, 282.50]\,\text{mm}$.
   - Khoảng cách giữa 2 tâm ngang: $181.00\,\text{mm}$; khoảng cách giữa 2 tâm dọc: $268.00\,\text{mm}$; đường chéo: $323.39\,\text{mm}$.
   - Tái sử dụng đồng bộ trên cả 4 trang để chuẩn hóa giải thuật nắn chỉnh phối cảnh tự động (perspective transform).
3. **Khối kiểm chuẩn đo lường (Calibration Block Specification):**
   - Thước đo chính xác $50.0\,\text{mm}$ (Pilot check: $50.0 \pm 0.2\,\text{mm}$ span).
   - Ô vuông kiểm chuẩn tỷ lệ cạnh $20.0 \times 20.0\,\text{mm}$ (Aspect Ratio: $1.000 \pm 0.005$).
   - Nhằm phát hiện sai số tỷ lệ quét (scale factor) và biến dạng co giãn phi đối xứng trục X/Y của máy quét phẳng.
4. **Tiêu chuẩn số hóa (Digitization Standard):**
   - Thiết bị: Máy quét phẳng (flatbed scanner) quang học.
   - Độ phân giải: $600\,\text{DPI}$ thực, tỷ lệ 1:1, ảnh màu 24-bit hoặc grayscale 8-bit, định dạng PNG không nén (lossless).
5. **Bảo mật & Quyền riêng tư (Strict No PII):**
   - Tuyệt đối không thu thập thông tin danh tính cá nhân: Họ tên, MSSV, Số điện thoại, Email, Địa chỉ, hoặc Chữ ký.
   - Chỉ sử dụng mã số ẩn danh `Writer ID: W_________` và số phiên `Session: S______`.
