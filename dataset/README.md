# OmniDraw Handwriting Dataset Repository

Tài liệu quản trị cấu trúc thư mục dữ liệu chữ viết tay tiếng Việt phục vụ nghiên cứu đề tài OmniDraw:
- **CA-VHC (Context-Aware Vietnamese Handwriting Synthesis with Viterbi Diacritic Placement)**
- **Writer Profile P2 (Personalized Handwriting Style Modeling)**

Tuân thủ nghiêm ngặt theo đặc tả chuẩn: [`docs/08_handwriting_dataset_spec.md`](../docs/08_handwriting_dataset_spec.md).

---

## 1. Cấu trúc thư mục (Directory Layout)

```text
dataset/
├── README.md                           # Tài liệu hướng dẫn quản trị dữ liệu (tệp này)
├── raw/                                # Kho lưu trữ dữ liệu thô (READ-ONLY / BẤT BIẾN / GITIGNORED)
│   ├── images/                         # [GITIGNORED] Ảnh quét phẳng PNG 600 DPI không nén suy hao
│   │   └── W{xxx}_S{yy}_P{zz}.png      # Đặt tên danh định: writer_id, session_id, page_no
│   ├── consent/                        # [GITIGNORED] Bản quét phiếu đồng thuận có chữ ký
│   └── manifests/                      # [GITIGNORED] Bảng kê khai phiên thu thập và metadata chi tiết
│       └── collection_manifest.jsonl
├── processed/                          # Kho dữ liệu sau tiền xử lý và kiểm chuẩn quang học
│   ├── ca_vhc/                         # Phân nhánh CA-VHC (Offline calibration)
│   │   ├── annotations/                # Dữ liệu gán nhãn mỏ neo và cấu trúc dấu tiếng Việt
│   │   │   ├── ca_vhc_train.jsonl
│   │   │   ├── ca_vhc_val.jsonl
│   │   │   └── ca_vhc_test.jsonl
│   │   ├── crops/                      # [GITIGNORED] Ảnh trích xuất từng ký tự / âm tiết chuẩn hóa
│   │   │   ├── glyphs/
│   │   │   └── diacritics/
│   │   └── splits/                     # Danh sách phân chia Writer-Disjoint cố định
│   │       └── split_metadata_v1.json
│   └── writer_profiles/                # Phân nhánh Hồ sơ Người viết (Writer Profile P2)
│       ├── profiles/                   # [GITIGNORED] File JSON hồ sơ cá nhân theo từng người viết
│       │   ├── profile_W001_v1.json
│       │   ├── profile_W002_v1.json
│       │   └── ...
│       ├── features/                   # [GITIGNORED] Vector đặc trưng trung gian theo từng người viết
│       │   └── writer_features_summary.jsonl
│       └── provenance/                 # [GITIGNORED] Nhật ký liên kết xuất xứ cấp ô cắt
│           └── crop_provenance_ledger.jsonl
└── schemas/                            # JSON Schema kiểm thực tính toàn vẹn cấu trúc (Tracked)
    ├── writer_profile.schema.json      # Schema hồ sơ người viết P2
    ├── ca_vhc_annotation.schema.json   # Schema gán nhãn mỏ neo CA-VHC (Proposed)
    └── collection_manifest.schema.json # Schema phiên thu thập
```

---

## 2. Nguyên tắc Bất biến Dữ liệu Thô (Immutability Principle)

> [!IMPORTANT]
> **Toàn bộ thư mục `dataset/raw/` là kho dữ liệu chỉ đọc (read-only):**
> 1. Tuyệt đối không chỉnh sửa trực tiếp, không cắt xén, không ghi đè lên ảnh gốc.
> 2. Mọi kết quả nắn chỉnh (deskew), cắt ô (cropping), lọc nhị phân (binarization) hoặc trích xuất vector nét đều bắt buộc phải lưu sang `dataset/processed/`.

---

## 3. Chính sách Bảo mật, Đạo đức & Kiểm soát Phiên bản Git

### 3.1. Mã hóa Định danh & Bảo vệ Quyền riêng tư (Pseudonymization)
Theo quy định tại [`docs/21_handwriting_collection_protocol_and_error_handling.md`](../docs/21_handwriting_collection_protocol_and_error_handling.md) và [`docs/25_rq4_consent_and_anonymization_protocol.md`](../docs/25_rq4_consent_and_anonymization_protocol.md):
- **Tuyệt đối không lưu PII:** Không lưu trữ thông tin định danh cá nhân (PII: Họ tên, email, số điện thoại, CCCD) trong kho dữ liệu `dataset/`.
- **Mã hóa người viết:** Mỗi người viết được định danh bằng mã duy nhất dạng `W{xxx}` (ví dụ: `W001`, `W002`).
- Bảng ánh xạ danh tính người tham gia được lưu trữ ngoại tuyến tại kho lưu trữ độc lập cách ly mạng (air-gapped registry) do điều phối viên bảo mật phụ trách.

### 3.2. Chính sách Loại trừ Git & Phạm vi Chia sẻ Dữ liệu (Git Exclusion & Release Boundary)
- **Mặc định chặn khỏi Git (`.gitignore`):**
  1. Toàn bộ ảnh quét và tài liệu pháp lý thô: `dataset/raw/images/`, `dataset/raw/consent/`.
  2. Bảng kê khai phiên thu thập thô chứa metadata chi tiết: `dataset/raw/manifests/`.
  3. Toàn bộ ảnh crop bóc tách: `dataset/processed/ca_vhc/crops/`.
  4. Toàn bộ hồ sơ phong cách chi tiết theo từng cá nhân: `dataset/processed/writer_profiles/profiles/` (và các file `profile_*.json`).
  5. Toàn bộ vector đặc trưng trung gian và nhật ký xuất xứ ô cắt: `dataset/processed/writer_profiles/features/`, `dataset/processed/writer_profiles/provenance/`.
- **Quy định Chia sẻ Kết quả & Test Fixtures:**
  - Vì mỗi dòng trong `writer_features_summary.jsonl` chứa `writer_id` và vector đặc trưng riêng lẻ của từng người viết, tệp này được **loại trừ khỏi Git** ở vị trí dữ liệu thật để bảo vệ quyền riêng tư.
  - Dữ liệu phục vụ kiểm thử đơn vị được lưu độc lập tại [`tests/fixtures/synthetic_writer_features_summary.jsonl`](../tests/fixtures/synthetic_writer_features_summary.jsonl) và được gắn nhãn rõ là **dữ liệu giả lập (synthetic test fixture)**.
  - **Nếu sau này cần chia sẻ kết quả nghiên cứu:** Nhóm nghiên cứu sẽ tạo **bản xuất riêng đã được thẩm định và phê duyệt chính thức bởi TV4 và đơn vị phụ trách**; tuyệt đối không commit trực tiếp dữ liệu thô hoặc dữ liệu người viết cá nhân lên Git.

## 4. Công cụ Xử lý Dữ liệu Đi kèm

1. **Scan-Validation Pipeline (`backend/scan_validator/`):**
   - Tự động phát hiện 4 mốc quang học fiducial marker $5 \times 5\,\text{mm}$.
   - Nắn phối cảnh đưa về canvas A4 tại $600\,\text{DPI}$ ($4960 \times 7016\,\text{pixels}$).
   - Kiểm định dung sai thước chuẩn $50\,\text{mm}$ và hình vuông tỷ lệ $20 \times 20\,\text{mm}$.
   - Cắt tự động các ô viết tay và phân loại trạng thái QC (`QC_PASS`, `QC_EMPTY`, `QC_FLAGGED`, `QC_REJECTED`).
2. **Writer Profile Generator (`backend/writer_profile/profile_generator.py`):**
   - Trích xuất 4 nhóm vector đặc trưng: Góc nghiêng ($\theta_{\text{slant}}$), Tỷ lệ khung chữ ($\text{AR}_{\text{mean}}$), Khoảng cách (ký tự/từ/dòng), và Độ dao động chân dòng ($\sigma_{\text{jitter}}$).
   - Kiểm định đối tượng với JSON Schema và tự động xuất bản ghi tổng hợp vào `writer_features_summary.jsonl`.
