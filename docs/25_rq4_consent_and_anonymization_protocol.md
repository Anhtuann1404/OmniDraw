# Quy chuẩn Đạo đức Nghiên cứu: Cam kết Đồng thuận (Informed Consent), Mã hóa Định danh (Pseudonymization) & Quản lý Xuất xứ Mẫu (Provenance/QC)

**Tài liệu:** `docs/25_rq4_consent_and_anonymization_protocol.md`<br>
**Ngày ban hành:** 29/09/2026 · **Phiên bản:** v1.0 · **Trạng thái:** `DRAFT_AWAITING_TV4_AND_INSTITUTIONAL_APPROVAL`<br>
**Đường chạy:** TV1 — AI Data & Writer Profile Lead<br>
**Phục vụ:** Nghiên cứu RQ4 (Thói quen viết cá nhân P2) & Pilot P01–P04 (3–5 người viết)

---

## 1. Nguyên tắc Đạo đức Nghiên cứu & Phạm vi Áp dụng

Nhằm bảo đảm tính liêm chính học thuật, tuân thủ pháp luật về bảo vệ dữ liệu cá nhân (Nghị định 13/2023/NĐ-CP) và chuẩn mực đạo đức nghiên cứu quốc tế trong thu thập dữ liệu chữ viết tay con người, tài liệu này thiết lập các nguyên tắc bắt buộc:

1. **Thuần túy Học thuật & Phi thương mại:** Dữ liệu chữ viết tay chỉ được sử dụng cho mục đích nghiên cứu khoa học, công bố bài báo và thẩm định mô hình trong khuôn khổ đề tài OmniDraw. Tuyệt đối không khai thác thương mại hoặc chuyển giao cho bên thứ ba ngoài mục đích học thuật đã công bố.
2. **Nguyên tắc No-PII & Mã hóa Định danh (Pseudonymization):** Phiếu thu thập chữ viết tay (P01, P02, P03, P04) và các tệp dữ liệu số hóa trong Git repository **tuyệt đối không chứa bất kỳ thông tin nhận dạng cá nhân nào** (họ tên, chữ ký, số căn cước, số điện thoại, địa chỉ, tài khoản mạng xã hội). Dữ liệu được quản lý dưới dạng mã hóa định danh (pseudonymized data) thông qua mã số `writer_id`, kèm khóa đối chiếu lưu ngoại tuyến cách ly; không gọi là "ẩn danh tuyệt đối" không thể đảo ngược do vẫn duy trì khóa ngoại tuyến phục vụ quyền rút lui của người tham gia.
3. **Nguyên tắc Tự nguyện & Quyền Rút lui (Right to Withdraw):** Người tham gia có quyền rút khỏi nghiên cứu bất kỳ lúc nào trước khi tập dữ liệu được đóng băng phục vụ công bố chính thức. Khi nhận được yêu cầu hợp lệ qua mã số bí mật, điều phối viên TV1 có trách nhiệm xóa hoàn toàn bản quét gốc và các tệp bóc tách liên quan khỏi kho lưu trữ ngoại tuyến. Các chỉ số thống kê tổng hợp (aggregated metrics) đã công bố hoặc đưa vào báo cáo nghiệm thu trước thời điểm rút lui sẽ không thể bóc tách hồi tố.
4. **Phân định Rõ Bản quét Tĩnh vs. Động học:** Ảnh quét tĩnh 600 DPI chỉ phản ánh dấu vết hình học nhìn thấy (geometry traces), **tuyệt đối không được suy diễn ngụy tạo thành áp lực bút (pen pressure) hay vận tốc thời gian thực (real-time velocity)**.

---

## 2. Quy trình Mã hóa Định danh & Cách ly Dữ liệu (Air-Gapped Registry Protocol)

Cơ chế này sử dụng kỹ thuật **mã hóa định danh (pseudonymization)** theo quy chuẩn quốc tế: tách rời dữ liệu nghiên cứu khỏi danh tính thực bằng mã định danh duy nhất (`writer_id`), đồng thời bảo vệ khóa liên kết bằng lưu trữ cách ly vật lý. Đây không phải là "ẩn danh tuyệt đối" không thể đảo ngược, do nhóm nghiên cứu chủ động duy trì khóa đối chiếu ngoại tuyến để hỗ trợ quyền rút lui của người viết và bảo đảm tính liêm chính dữ liệu.

Quy trình được thiết kế theo mô hình **Cách ly 3 Tầng**:

```text
[Người tham gia]
       │
       ▼ (Ký Phiếu Đồng thuận Consent ngoài giấy)
[Tầng 1: Hồ sơ Giấy Consent] ──► Lưu trữ vật lý có khóa, độc lập hoàn toàn
       │
       ▼ (Gán mã định danh W001..W005)
[Tầng 2: Bảng Đối chiếu Mã hóa (Air-Gapped Registry)]
       │ • Lưu trên USB mã hóa phần cứng (BitLocker / LUKS)
       │ • Không kết nối mạng Internet, KHÔNG commit lên Git
       ▼
[Tầng 3: Dữ liệu Số hóa Nghiên cứu (Research Dataset)]
       │ • Mã người viết: W001, W002,...
       │ • Phiếu P01–P04, tọa độ bounding box, vector đặc trưng
       │ • Công khai minh bạch cho nhóm nghiên cứu & Git repo (chỉ metadata & JSON)
```

### 2.1. Cấu trúc Mã định danh
- **Mã Người viết (`writer_id`):** Định dạng `W{xxx}` (ví dụ: `W001`, `W002`, `W003`). Không mã hóa giới tính, năm sinh hay đặc điểm nhân khẩu học vào chuỗi định danh.
- **Mã Phiên thu thập (`session_id`):** Định dạng `S{xx}` (ví dụ: `S01`, `S02`).
- **Mã Trang phiếu (`page_id`):** `P01` (Ký tự rời & Dấu), `P02` (Từ & Nối nét), `P03` (Câu dòng chảy), `P04` (Đoạn văn).
- **Mã Mẫu bóc tách (`sample_id`):** `SMP_{writer_id}_{sequence:05d}` (ví dụ: `SMP_W001_00042`).

### 2.2. Kiểm soát An toàn Git Repository
- File cấu hình `.gitignore` được thiết lập loại trừ nghiêm ngặt:
  - `dataset/raw/images/` (ảnh quét độ phân giải cao).
  - `dataset/raw/consent/` (bản scan phiếu đồng thuận có chữ ký).
  - `dataset/processed/ca_vhc/crops/` (ảnh bóc tách ô chữ thật).
  - Mọi tệp định dạng `*_pii.*`, `*registry*.json`, `*.tif`, `*.tiff`.

---

## 3. Biểu mẫu Cam kết Đồng thuận Nghiên cứu (Informed Consent Form Template)

*(Biểu mẫu dự thảo cần trình TV4 và Đơn vị phụ trách duyệt trước khi triển khai thu mẫu thực tế)*

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║              PHIẾU CAM KẾT ĐỒNG THUẬN THAM GIA NGHIÊN CỨU                   ║
║                     (INFORMED CONSENT FORM)                                  ║
║                                                                              ║
║ Đề tài: OmniDraw — Nghiên cứu Khung Tối ưu Hóa Nét và Tái tạo Chữ Viết Tay   ║
║         Tiếng Việt Có Dấu theo Phong Cách Cá Nhân Trên Máy Vẽ Plotter        ║
║ Đơn vị thực hiện: Nhóm Nghiên cứu Sinh viên NCKH                             ║
║ Điều phối viên dữ liệu (TV1): ............................................   ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. MỤC ĐÍCH NGHIÊN CỨU:
Chúng tôi mời bạn tham gia đóng góp mẫu chữ viết tay tiếng Việt nhằm phục vụ mục
đích nghiên cứu khoa học: phân tích hình học nét chữ, cấu trúc dấu thanh tiếng
Việt và đánh giá thuật toán tối ưu đường vẽ ngòi bút trên máy vẽ tự động.

2. QUYỀN LỢI VÀ TRÁCH NHIỆM:
- Bạn sẽ thực hiện viết mẫu trên bộ phiếu in định chuẩn P01–P04 bằng bút gel đen
  0.5 mm do ban nghiên cứu cung cấp (thời gian ước tính: 15–25 phút).
- Bạn viết với phong cách tự nhiên nhất, không gò ép, không sử dụng bút xóa.

3. CAM KẾT BẢO MẬT & MÃ HÓA ĐỊNH DANH:
- Toàn bộ mẫu chữ của bạn sẽ được gán một Mã Số Ẩn Danh duy nhất (ví dụ: W001).
- Phiếu viết tay KHÔNG YÊU CẦU và TUYỆT ĐỐI KHÔNG GHI họ tên, chữ ký, địa chỉ
  hay bất kỳ thông tin nhận dạng cá nhân nào của bạn.
- Bản cam kết này được lưu trữ độc lập tại tủ hồ sơ an toàn, tách biệt hoàn toàn
  khỏi các bản quét số hóa và mã nguồn của dự án.
- Dữ liệu nét chữ và các chỉ số hình học trích xuất (độ nghiêng, tỷ lệ khung,
  khoảng cách) chỉ được sử dụng trong các bài báo khoa học và báo cáo học thuật
  dưới dạng dữ liệu gán mã định danh (pseudonymized data).

4. PHẠM VI CÔNG BỐ ẢNH & ĐIỀU KHOẢN RÚT MẪU:
- Lựa chọn công bố ảnh (Người tham gia tích chọn):
  [ ] Tôi đồng ý cho phép sử dụng hình ảnh bóc tách nét chữ/ô mẫu (không chứa thông
      tin nhận dạng cá nhân) trong các công bố khoa học học thuật.
  [ ] Tôi chỉ đồng ý chia sẻ các chỉ số hình học tổng hợp (vector đặc trưng/profile),
      không cho phép đưa ảnh chụp nét chữ vào bài báo.
- Quyền rút lui: Việc tham gia là hoàn toàn tự nguyện. Bạn có quyền từ chối hoặc dừng
  viết bất kỳ lúc nào mà không gặp bất kỳ bất lợi nào. Sau khi viết xong, bạn được cấp
  một "Mã Rút Lui Bí Mật". Nếu bạn muốn hủy mẫu, hãy gửi mã này cho điều phối viên trước
  ngày đóng băng dữ liệu nghiên cứu (Data Freeze); toàn bộ bản quét gốc và ảnh crop
  bóc tách của bạn sẽ bị xóa vĩnh viễn khỏi kho lưu trữ ngoại tuyến.
  Lưu ý: các chỉ số thống kê tổng hợp (aggregated metrics) đã công bố hoặc đưa vào
  báo cáo nghiệm thu trước thời điểm rút lui sẽ không thể bóc tách hồi tố.

--------------------------------------------------------------------------------
XÁC NHẬN CỦA NGƯỜI THAM GIA:
Tôi xác nhận đã đọc, hiểu rõ các điều khoản trên và tự nguyện đồng ý tham gia.

Mã số Người viết (do điều phối viên gán): W [ ___ ]
Mã số Rút lui Bí mật (cấp cho người tham gia): [ _______________________ ]

Ngày ký: ..... / ..... / 2026
Chữ ký người tham gia: .......................... Họ và tên: ....................
Chữ ký điều phối viên: .......................... Họ và tên: ....................
--------------------------------------------------------------------------------
```

---

## 4. Quản lý Xuất xứ Dữ liệu & Kiểm soát Chất lượng (Provenance & QC Specification)

Để bảo đảm mọi mẫu dữ liệu bóc tách phục vụ trích xuất hồ sơ phong cách (`WriterProfile`) đều có thể truy vết nguồn gốc (provenance) và đạt tiêu chuẩn chất lượng (QC), cấu trúc dữ liệu lưu trữ tuân thủ định dạng JSON Lines:

### 4.1. Cấu trúc Bản ghi Kê khai Thu thập (`collection_manifest.jsonl`)
Tuân thủ 100% JSON Schema: [`dataset/schemas/collection_manifest.schema.json`](../dataset/schemas/collection_manifest.schema.json):
```json
{
  "scan_id": "W001_S01_P01",
  "writer_id": "W001",
  "session_id": "S01",
  "page_id": "P01",
  "is_spare": false,
  "scan_timestamp": "2026-10-02T09:15:00+07:00",
  "scanner_model": "Epson Perfection V39 II",
  "optical_dpi": 600,
  "calibration_metrics": {
    "ruler_length_mm": 50.02,
    "ruler_error_mm": 0.02,
    "square_aspect_ratio": 1.001,
    "deskew_angle_deg": 0.12
  },
  "qc_status": "QC_AUTO_PASS",
  "qc_operator": "TV1",
  "cell_anomalies": []
}
```

### 4.2. Vòng đời Trạng thái QC (QC State Machine)
Mọi ô viết tay hoặc mẫu bóc tách trải qua 5 trạng thái kiểm định rõ ràng khớp với JSON Schema:
1. `QC_RAW`: Ảnh thô vừa quét, chưa qua căn chỉnh góc xoay hoặc bóc tách.
2. `QC_AUTO_PASS`: Đã vượt qua kiểm định tự động: 4 fiducial markers tìm thấy, góc lệch deskew $< 1.0^\circ$, sai số thước $< 0.5\,\text{mm}$, tỷ lệ ô vuông $[0.98, 1.02]$.
3. `QC_AUTO_FLAGGED`: Cảnh báo tự động: phát hiện ô có độ tương phản bất thường, nét viết tràn ra ngoài biên ô, hoặc mực nhòe.
4. `QC_VERIFIED_PASS`: Đã qua thẩm định thủ công bằng mắt của điều phối viên TV1, xác nhận nét chữ hợp lệ, không dùng bút xóa, đủ độ tương phản.
5. `QC_REJECTED`: Ô bị loại bỏ khỏi tập huấn luyện do gạch xóa, viết sai ô, hoặc rách giấy (vẫn lưu vết trong manifest để bảo đảm tính toàn vẹn mẫu số nghiên cứu).

### 4.3. Quản lý Xuất xứ Dữ liệu & Ranh giới Chia sẻ (Data Provenance & Release Boundary)
Đối tượng `WriterProfile` được sinh bởi `profile_generator.py` tuân thủ nghiêm ngặt 100% định nghĩa cấu trúc của [`dataset/schemas/writer_profile.schema.json`](../dataset/schemas/writer_profile.schema.json), bao gồm 9 trường dữ liệu chuẩn (`profile_id`, `writer_id`, `version`, `created_at`, `num_samples_analyzed`, `global_style`, `spacing`, `diacritic_tendencies`, `allograph_tendencies`).

Để bảo đảm tính tương thích với schema, nguyên tắc phân tách trách nhiệm và an toàn dữ liệu:
1. **Hồ sơ `WriterProfile` KHÔNG chứa trường `provenance_manifest` bên trong JSON profile:**
   - Mọi metadata xuất xứ được tách rời hoàn toàn khỏi đối tượng profile để bảo vệ tính bất biến của JSON Schema.
2. **Cơ chế Truy vết Xuất xứ Cấp độ Ô Cắt (Crop-level Provenance Ledger) cho Pilot:**
   - Để bảo toàn xuất xứ dữ liệu mà không làm biến dạng schema JSON của `WriterProfile`, TV1 đã thiết lập cơ chế ghi nhật ký độc lập thông qua hàm `record_profile_crop_provenance()` trong `backend/writer_profile/profile_generator.py` (tham số `--provenance-ledger`).
   - Tệp nhật ký lưu tại `dataset/processed/writer_profiles/provenance/crop_provenance_ledger.jsonl`, ghi nhận bộ ba định danh (`profile_id`, `scan_id`, `cell_id`/`sample_id`) kèm trạng thái QC của từng ô cắt thực tế được nạp vào tính toán profile trong đợt pilot P01–P04.
   - Cơ chế này hoàn toàn tách biệt khỏi cấu trúc 9 trường dữ liệu của `writer_profile.schema.json`, bảo đảm truy vết 100% từ hồ sơ phong cách ngược về đúng tọa độ ô quét ban đầu.
3. **Chính sách Loại trừ Git & Phạm vi Chia sẻ Dữ liệu (Git Exclusion & Release Policy):**
   - Mặc định loại trừ khỏi Git (`.gitignore`):
     - `dataset/raw/manifests/`: Chứa toàn bộ metadata quét chi tiết và nhật ký dị thường.
     - `dataset/processed/writer_profiles/profiles/`: Chứa file JSON hồ sơ phong cách chi tiết của từng người viết.
     - `dataset/processed/writer_profiles/features/`: Do mỗi dòng mang `writer_id` và vector đặc trưng của từng cá nhân riêng lẻ, thư mục này được mặc định loại trừ khỏi Git ở vị trí dữ liệu thật để bảo vệ quyền riêng tư.
     - `dataset/processed/writer_profiles/provenance/`: Nhật ký xuất xứ ô quét chi tiết.
   - **Test Fixture Giả lập:** Dữ liệu mẫu dùng trong unit tests được lưu độc lập tại [`tests/fixtures/synthetic_writer_features_summary.jsonl`](../tests/fixtures/synthetic_writer_features_summary.jsonl) và được ghi chú rõ ràng là dữ liệu giả lập.
   - **Quy tắc Xuất bản & Chia sẻ Kết quả:** Nếu sau này cần chia sẻ kết quả nghiên cứu, nhóm nghiên cứu sẽ lập **bản xuất riêng đã được thẩm định và phê duyệt chính thức bởi TV4 và đơn vị phụ trách**; tuyệt đối không commit trực tiếp dữ liệu thô, manifest quét hay vector đặc trưng người viết cá nhân lên Git.
