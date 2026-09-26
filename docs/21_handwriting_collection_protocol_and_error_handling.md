# Quy trình Vận hành Thu thập Mẫu Chữ viết tay và Chính sách Xử lý Lỗi (Collection Protocol & Error Handling Policy)

**Mã tài liệu:** `DOC-POL-21-COLLECTION-PROTOCOL`  
**Phiên bản:** `v1.0.0` (Dự thảo quy trình vận hành trước thử nghiệm Pilot)  
**Ngày cập nhật:** 25/09/2026 | **Chủ trì soạn thảo:** TV1 (AI Data & Writer Profile Lead)  
**Đơn vị phối hợp:** TV4 (Project Lead & Handwriting / CA-VHC Composition Lead)  
**Trạng thái tài liệu:** `PILOT CANDIDATE — PENDING 600 DPI BENCH PRINT/SCAN AND TV4 REVIEW`  
**Đơn vị áp dụng:** Toàn bộ thành viên điều phối thu thập dữ liệu đề tài NCKH OmniDraw

---

## 1. Nguyên tắc Cốt lõi & Đạo đức Dữ liệu (Core Ethics & Principles)

1. **Tuyệt đối Ẩn danh (Strict No-PII Policy):**
   - Không thu thập bất kỳ thông tin nhận dạng cá nhân nào (Họ tên, MSSV, SĐT, Email, Chữ ký).
   - Mọi người tham gia được định danh bằng mã số duy nhất: `Writer ID: W{001..999}`.
   - Phiếu thỏa thuận đồng thuận tham gia nghiên cứu (Informed Consent Form) được lưu trữ tại hồ sơ giấy cách ly (air-gapped), không liên kết số hóa trực tiếp với ảnh quét.

2. **Bảo toàn Tính Trung thực của Nét viết Tự nhiên (Natural Writing Integrity):**
   - Thu thập thói quen viết thực tế, không yêu cầu người viết cố tình nắn nót đẹp bất thường.
   - **Tuyệt đối cấm sử dụng bút xóa, băng xóa hoặc gạch đè nét lên lỗi sai**.
   - Nếu viết sai, giữ nguyên hiện trạng nét viết để hệ thống gắn cờ QC phân loại.

3. **Tính Tái lập & Kiểm chuẩn Kỹ thuật (Reproducibility & Optical Rigor):**
   - Chỉ sử dụng ảnh quét phẳng không nén $600\,\text{DPI}$ (Lossless PNG, tỷ lệ 1:1).
   - Mọi bản quét bắt buộc vượt qua kiểm định mốc định vị quang học (Fiducial Markers) và khối kiểm chuẩn kích thước (Calibration Ruler & Square).

---

## 2. Quy chuẩn Vật tư & Điều kiện Thu thập (Standard Apparatus)

| Hạng mục | Quy chuẩn Bắt buộc | Mục đích Kỹ thuật |
| :--- | :--- | :--- |
| **Giấy in phiếu** | Giấy Double A chuẩn ISO A4 ($210 \times 297\,\text{mm}$), định lượng $80\,\text{g/m}^2$, độ trắng $\ge 95\%$. | Bảo đảm độ phẳng, chống thấm nhòe mực sang mặt sau, hệ số phản xạ quang học chuẩn. |
| **Bút viết** | Bút bi ngòi gel mực đen $0.5\,\text{mm}$ (Pentel EnerGel BLN105 hoặc Pilot G2 0.5mm). | Bề rộng nét chuẩn $0.50 \pm 0.05\,\text{mm}$, độ tương phản đen-trắng cao phục vụ bóc tách centerline. |
| **Mặt phẳng kê viết** | Bàn phẳng cứng, lót dưới tờ phiếu 2–3 tờ giấy trắng đệm để tạo cảm giác tay êm tự nhiên. | Tránh biến dạng nét do gồ ghề của mặt bàn gỗ/nhựa. |
| **Thiết bị số hóa** | Máy quét phẳng quang học (Flatbed Scanner) hỗ trợ $600\,\text{DPI}$ True Optical. | Chống biến dạng phối cảnh, triệt tiêu méo phi đối xứng của camera điện thoại. |

---

## 3. Chính sách Phân loại Lỗi và Biện pháp Xử lý (Error Handling Policy)

Trong quá trình thu thập, các sự cố phát sinh được phân loại nghiêm ngặt thành 3 nhóm lỗi với quy trình xử lý chuẩn hóa:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        BA NHÓM LỖI TRONG QUY TRÌNH THU THẬP DỮ LIỆU                     │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ Nhóm 1: Lỗi Người Viết   │ Nhóm 2: Lỗi Bố Cục Hình Học │ Nhóm 3: Lỗi Thiết Bị Số Hóa   │
│ (Human Writing Errors)   │ (Spatial / Boundary Errors) │ (Scanner & Optical Artifacts) │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ • Viết nhầm ký tự đích   │ • Tràn nét vào dải nhãn in  │ • Mất góc mốc fiducial        │
│ • Viết thiếu dấu thanh   │ • Viết vượt khung ngoài     │ • Biến dạng tỷ lệ thước đo    │
│ • Vệt mực quẹt ngoài ý   │ • Nét chạm khung ô kế bên   │ • Sọc bẩn cảm biến quét CCD   │
│ • Tự ý tô đè nét sửa sai │ • Viết trôi hoàn toàn dòng  │ • Ảnh bị lóa sáng / bóng đen  │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

---

### 3.1. Nhóm 1: Xử lý Lỗi do Người viết (Human Writing Errors)

1. **Trường hợp viết sai ký tự/từ (Wrong Target / Missing Diacritic):**
   - **Quy tắc thao tác:** Người viết **KHÔNG gạch xóa**, bỏ qua ô/từ đó và tiếp tục viết ô tiếp theo.
   - **Quy tắc bóc tách:** Khi chạy pipeline gán nhãn, điều phối viên gắn cờ metadata `USER_MISWRITTEN`.
   - **Xử lý cấp ô (P01):** Chỉ loại bỏ riêng ô bị viết sai (`CELL_REJECTED`). Toàn bộ các ô còn lại trên trang P01 vẫn được lưu giữ và sử dụng bình thường.
   - **Xử lý cấp từ (P02):** Chỉ loại bỏ riêng dòng bị sai (`ROW_REJECTED`), các dòng khác vẫn trích xuất bình thường.
   - **Xử lý cấp câu/đoạn (P03, P04):** Nếu câu hoặc đoạn văn bị viết thiếu từ hoặc sai từ nghiêm trọng làm hỏng cấu trúc câu, câu/đoạn đó bị gắn cờ `STRUCT_DEGRADED` và không dùng cho bài toán đo nhịp câu chuẩn.

2. **Trường hợp tự ý dùng bút xóa hoặc tô đè sửa nét:**
   - Ô/dòng có dấu vết bút xóa hoặc tô đè nét bị **HỦY BỎ NGAY LẬP TỨC** (`QC_REJECTED`), do hóa chất bút xóa làm đổi hệ số phản xạ quang học và gây biến dạng giải thuật bóc tách centerline vector.

3. **Ngưỡng hủy trang (Page Replacement Threshold):**
   - Nếu một trang có **trên $25\%$ số mẫu bị viết sai** (ví dụ: $> 6/24$ ô trên P01, hoặc $> 4/16$ dòng trên P02):
     $\rightarrow$ Toàn bộ trang đó bị hủy (`PAGE_ABORTED`). Phát phiếu dự phòng (**Spare Sheet**) để người viết thực hiện lại trang đó.

---

### 3.2. Nhóm 2: Xử lý Lỗi Bố cục & Tràn Viền (Boundary & Spatial Errors)

1. **Tràn nét vào dải nhãn in máy (Label Strip Intrusion):**
   - Dải nhãn trên cùng của ô P01 và các header P02 chứa text in máy (`Sample ID`, `Target: [x]`).
   - Nếu nét viết tay chạm hoặc đè vào dải nhãn: Pipeline tự động gán nhãn `LABEL_COLLISION`. Ô đó bị loại khỏi tập dữ liệu huấn luyện/kiểm chuẩn tự động nhằm tránh trộn lẫn mực in máy với nét viết tay.

2. **Tràn nét ra ngoài vùng viết khả dụng (Writing Bounding Box Overflow):**
   - Nét viết chạm vào viền ngoài của ô hoặc tràn sang ô bên cạnh: Gán cờ `MARGIN_OVERFLOW`.
   - Nét vẫn được lưu ở kho raw nhưng bị loại khỏi tập benchmark baseline chuẩn.

---

### 3.3. Nhóm 3: Xử lý Lỗi Thiết bị Quét & Quang học (Scanner & Optical Artifacts)

Toàn bộ các lỗi Nhóm 3 được phát hiện tự động bởi bộ phần mềm `backend/scan_validator/`:

1. **Mất mốc định vị (`FIDUCIAL_DETECTION_FAILED`):**
   - Xảy ra khi ảnh scan bị cắt mép, tờ giấy bị đặt lệch góc kính làm che mất ít nhất 1 trong 4 mốc đen $5 \times 5\,\text{mm}$.
   - **Biện pháp:** **QUÉT LẠI NGAY LẬP TỨC (MANDATORY RESCAN)**. Điều chỉnh lại vị trí tờ giấy ngay ngắn trên mặt kính máy quét phẳng.

2. **Lỗi kiểm chuẩn đo lường thước đo & ô vuông (`CALIBRATION_FAILED`):**
   - Sai số chiều dài thước $50.0\,\text{mm}$ vượt ngưỡng dung sai: $|\Delta L| > 0.20\,\text{mm}$.
   - Sai số tỷ lệ cạnh ô vuông $20.0 \times 20.0\,\text{mm}$ vượt ngưỡng: $\text{Aspect Ratio} \notin [0.995, 1.005]$.
   - **Biện pháp:** Máy quét bị méo trục cơ học hoặc chọn sai chế độ DPI (phải là True Optical, không dùng Digital Interpolation). Kiểm tra cài đặt máy quét, vệ sinh kính và quét lại.

3. **Vệt sọc bẩn hoặc bóng đen nắp máy (`SCAN_DEFECT_FLAGGED`):**
   - Vệ sinh sạch mặt kính máy quét bằng khăn vi sợi và cồn y tế; đóng chặt nắp máy quét khi số hóa để tránh ánh sáng phòng lọt vào tạo bóng đen viền.

---

## 4. Chính sách Cấp phát và Quản lý Phiếu Dự phòng (Spare Sheet Policy)

1. **Định mức Phiếu Dự phòng:**
   - Mỗi bộ thu thập chính thức được chuẩn bị kèm **1 bộ phiếu dự phòng (Spare Pack)** gồm: `P01-S`, `P02-S`, `P03-S`, `P04-S`.
   - Mỗi người tham gia chỉ được cấp tối đa **1 phiếu dự phòng cho mỗi mã trang** nếu trang chính thức bị hủy theo ngưỡng quy định.

2. **Quy tắc Đặt tên File & Mã định danh Phiếu Dự phòng:**
   - Phiếu chính thức: `W001_S01_P01.png`
   - Phiếu dự phòng thay thế: `W001_S01_P01_SPARE.png` (hoặc `_SPARE2.png` trong trường hợp bất khả kháng).

3. **Thu hồi và Lưu trữ Phiếu Hỏng:**
   - Phiếu bị hủy không được vứt bỏ bừa bãi.
   - Điều phối viên gạch chéo đỏ lớn trên trang phiếu hỏng, ghi rõ lý do hủy (ví dụ: *"Hủy do viết nhầm 8 ô - Cấp phiếu dự phòng"*) và lưu vào thư mục hồ sơ giấy hủy: `Hồ sơ thu hồi / Voided Sheets`.
   - Bản quét của phiếu hủy (nếu đã quét) được chuyển vào thư mục cách ly: `dataset/quarantine/`.

---

## 5. Vòng đời Trạng thái Kiểm định Chất lượng (QC Lifecycle & Machine-Readable Flags)

Mọi tệp dữ liệu số hóa trong hệ thống OmniDraw đều trải qua 5 trạng thái vòng đời bất biến:

```text
[Bản quét phẳng PNG]
        │
        ▼
   (QC_RAW) ──────────► [Chạy backend/scan_validator/ CLI]
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
       (QC_AUTO_PASS)                (QC_AUTO_FLAGGED)
              │                               │
              ▼                               ▼
     [TV1 thẩm định mắt]             [TV1 phân tích lỗi]
              │                               │
       ┌──────┴──────┐                 ┌──────┴──────┐
       ▼             ▼                 ▼             ▼
(QC_VERIFIED_PASS) (QC_REJECTED)  (Quét lại)   (QC_REJECTED)
       │             │                 │             │
       ▼             ▼                 ▼             ▼
[Kho Processed] [Cách ly]        [Thực hiện lại] [Cách ly]
```

### Bảng định nghĩa các mã trạng thái QC:
| Mã Trạng thái | Ý nghĩa Kỹ thuật | Hành động Tiếp theo |
| :--- | :--- | :--- |
| `QC_RAW` | Ảnh quét gốc mới tạo, chưa chạy qua bộ thẩm định tự động. | Chạy pipeline `scan_validator`. |
| `QC_AUTO_PASS` | Vượt qua 100% tiêu chí tự động: đủ 4 fiducials, nắn phẳng chuẩn, thước đo $\pm 0.2\,\text{mm}$, không tràn viền. | Chuyển sang bước duyệt mắt TV1. |
| `QC_AUTO_FLAGGED` | Bị cảnh báo tự động: sai số thước đo, nghi ngờ tràn viền lề, hoặc nền dơ. | TV1 mở ảnh trực quan kiểm tra nguyên nhân. |
| `QC_VERIFIED_PASS` | TV1 xác nhận mẫu hợp lệ, đạt độ tự nhiên, không vi phạm quy tắc. | Đưa vào kho dữ liệu chính thức (`dataset/processed/`). |
| `QC_REJECTED` | Mẫu bị từ chối do vi phạm quy chuẩn nghiêm trọng hoặc không thể phục hồi. | Chuyển sang kho cách ly (`dataset/quarantine/`). |

---

## 6. Cấu trúc Thư mục Lưu trữ và Nhật ký Phiên Thu thập (Manifest Schema)

### 6.1. Cấu trúc Thư mục Dữ liệu:
```text
dataset/
├── raw/                          # Bản quét phẳng PNG gốc 600 DPI (chỉ đọc)
│   ├── W001_S01_P01.png
│   ├── W001_S01_P02.png
│   └── ...
├── processed/                    # Dữ liệu đã nắn thẳng, kiểm chuẩn và bóc tách
│   ├── ca_vhc/                   # Dữ liệu cấu trúc mỏ neo và dấu tiếng Việt (TV4)
│   └── writer_profiles/          # Đặc trưng phong cách người viết (TV1 - P2)
├── quarantine/                   # Bản quét hỏng, phiếu bị loại bỏ
│   └── W001_S01_P01_REJECTED.png
└── metadata/                     # Nhật ký phiên và nhãn kiểm định
    └── collection_manifest.jsonl # File JSONL lưu trạng thái từng bản ghi
```

### 6.2. Cấu trúc Bản ghi JSONL (`collection_manifest.jsonl`):
Mỗi tệp quét tương ứng một bản ghi JSON có cấu trúc tối thiểu như sau:
```json
{
  "scan_id": "W001_S01_P01",
  "writer_id": "W001",
  "session_id": "S01",
  "page_id": "P01",
  "is_spare": false,
  "scan_timestamp": "2026-09-25T10:00:00Z",
  "scanner_model": "Epson Perfection V39 II",
  "optical_dpi": 600,
  "calibration_metrics": {
    "ruler_length_mm": 50.04,
    "ruler_error_mm": 0.04,
    "square_aspect_ratio": 1.001,
    "deskew_angle_deg": -0.15
  },
  "qc_status": "QC_VERIFIED_PASS",
  "qc_operator": "TV1",
  "cell_anomalies": [
    {"cell_id": "TONE_002", "status": "USER_MISWRITTEN", "note": "Viết nhầm dấu sắc thay vì huyền"}
  ]
}
```

---

## 7. Kế hoạch Vận hành Thử nghiệm Pilot (Limited Pilot Plan: 3–5 Writers)

1. **Quy mô thử nghiệm:** 3 đến 5 người viết tình nguyện (sinh viên/nghiên cứu viên).
2. **Quy trình thực hiện:**
   - Mỗi người viết thực hiện trọn vẹn 1 bộ 4 trang (`P01`, `P02`, `P03`, `P04`).
   - Tổng số trang cần số hóa: $4 \times 5 = 20$ trang.
   - Ghi nhận thời gian hoàn thành từng trang (`completion_time_minutes`) để theo dõi tiến độ và nhịp độ viết tự nhiên.
3. **Tiêu chí Nghiệm thu Pilot (Pilot Exit Gate):**
   - Tỷ lệ phát hiện mốc fiducial tự động thành công: $\ge 95\%$.
   - Tỷ lệ sai số thước đo kiểm chuẩn đạt chuẩn pilot: $100\%$ các bản quét đạt $\pm 0.20\,\text{mm}$.
   - Tỷ lệ bóc tách ô tự động chính xác: $\ge 98\%$.
   - Không có trường hợp nào vi phạm bảo mật PII.

---

*Dự thảo quy trình do TV1 đề xuất; chờ TV4 phê duyệt và hoàn tất bench scan 600 DPI trước khi áp dụng.*  
**Chủ trì soạn thảo (TV1):** *Bản dự thảo đề xuất*
