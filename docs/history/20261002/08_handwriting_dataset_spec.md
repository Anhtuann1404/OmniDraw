# OmniDraw — Đặc tả Kỹ thuật Dataset Chữ viết tay (Handwriting Dataset Specification)

**Tài liệu mã số:** `DOC-SPEC-08-DATASET`  
**Phiên bản:** `v1.0.0` (Chuẩn hóa ranh giới CA-VHC Dataset vs. Writer Profile Dataset)  
**Ngày ban hành:** 19/09/2026 | **Đồng bộ trạng thái:** 21/09/2026 (Đồng bộ sau TV2 Cross-Review & Ủy quyền bắt đầu triển khai phần mềm Step C)<br>
**Chủ trì soạn thảo & Quản trị dữ liệu:** TV1 (AI Data & Writer Personalization Lead)  
**Chủ trì kiến trúc giải thuật & Phê duyệt:** TV4 (Project Lead & Handwriting / CA-VHC Composition Lead)  
**Đồng thẩm định:** TV2 (Stroke Optimization & Path Planning Lead), TV3 (Hardware, Calibration & Physical Validation Lead)  

---

## 1. Mục đích và phạm vi (Purpose & Scope)

Tài liệu này xác lập tiêu chuẩn kỹ thuật, quy trình thu thập, cấu trúc lưu trữ và schema dữ liệu cho toàn bộ các tập dữ liệu chữ viết tay phục vụ dự án nghiên cứu khoa học **OmniDraw**.

### 1.1. Tách biệt hai loại Dataset độc lập

Trong nghiên cứu chữ viết tay của OmniDraw, tồn tại hai bài toán khoa học hoàn toàn khác nhau về bản chất, mục tiêu tối ưu và downstream consumer. Hệ thống **tuyệt đối không gộp hai bài toán này thành một khái niệm duy nhất**:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        HAI NHÁNH DỮ LIỆU CHỮ VIẾT TAY CỦA OMNIDRAW                     │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│ 1. Vietnamese Diacritic / CA-VHC Dataset  │ 2. Writer Profile / Personalization Dataset│
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Câu hỏi trung tâm:                        │ Câu hỏi trung tâm:                         │
│ "Chữ và dấu tiếng Việt nên được cấu tạo,  │ "Một người cụ thể có thói quen viết        │
│  bố trí và biến đổi theo ngữ cảnh như thế │  như thế nào?"                             │
│  nào?"                                    │                                            │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Bản chất:                                 │ Bản chất:                                  │
│ CẤU TRÚC, CHÍNH TẢ & RÀNG BUỘC HÌNH HỌC   │ ĐẶC TRƯNG CÁ NHÂN & PHONG CÁCH VIẾT        │
│ (Orthography, Glyphs & Geometric Anchors) │ (Writer Biometrics & Few-Shot Style Vector)│
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Trọng tâm dữ liệu:                        │ Trọng tâm dữ liệu:                         │
│ - Tọa độ mỏ neo dấu (anchors)             │ - Góc nghiêng nét chữ (slant angle)        │
│ - Độ dịch tâm dấu (diacritic offset dx,dy)│ - Tỷ lệ co giãn khung chữ (aspect ratio)   │
│ - Khoảng cách an toàn chống đè nét        │ - Dao động đường chân dòng (baseline jitter│
│ - Biến thể chữ theo vị trí (allographs)   │ - Phân bố khoảng cách chữ / từ / dòng      │
│ - Ràng buộc tổ hợp dấu thanh + dấu mũ/móc │ - Thiên hướng chọn biến thể nét (ligatures)│
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Downstream Consumer:                      │ Downstream Consumer:                       │
│ Handwriting Composition Core (TV4) &      │ Module trích đặc trưng cá nhân hóa (TV1)   │
│ Stroke Graph Optimizer DAG (TV4 + TV2)    │ (Định hướng P2 / Future Research)          │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Quyền sở hữu logic/quy tắc:               │ Quyền sở hữu logic/quy tắc:                │
│ TV4 (Handwriting Core Lead)               │ TV1 (AI Data & Writer Personalization Lead)│
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ Trạng thái trong hệ thống:                │ Trạng thái trong hệ thống:                │
│ Nền tảng P0/P1 (Core Research Path)       │ Nghiên cứu mở rộng P2 (Future Research)    │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

### 1.2. Mối quan hệ và Nguyên tắc "Shared Raw Input"

Mặc dù hai loại dataset phục vụ hai mục đích khoa học khác nhau, quy trình thu thập thực tế có thể tối ưu hóa nguồn lực thông qua cơ chế **Shared Raw Input (Chia sẻ ảnh quét gốc)**:

```text
                             [Người tình nguyện viết mẫu]
                                          │
                                          ▼ (Viết trên phiếu chuẩn)
                             [Bản quét ảnh gốc / Raw Scan]
                             (dataset/raw/images/W001_S01_P01.png)
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
                   ▼ (Pipeline A: TV1 trích xuất theo TV4 spec)   ▼ (Pipeline B: TV1 trích xuất đặc trưng)
     ┌───────────────────────────────┐             ┌───────────────────────────────┐
     │  CA-VHC Structural Dataset    │             │ Writer Profile Dataset (P2)   │
     │  - Bóc tách âm tiết / dấu     │             │ - Đo độ nghiêng toàn cục      │
     │  - Tọa độ anchor & offset     │             │ - Đo jitter đường chân dòng   │
     │  - Gán nhãn ngữ cảnh từ       │             │ - Đo tỷ lệ khung chữ & từ     │
     └─────────────┬─────────────────┘             └───────────────┬───────────────┘
                   │                                               │
                   ▼ (Lưu trữ độc lập)                             ▼ (Lưu trữ độc lập)
     dataset/processed/ca_vhc/                     dataset/processed/writer_profiles/
     (annotations JSONL)                           (profiles JSON)
```

**Nguyên tắc chia sẻ ảnh gốc:**
1. **Độc lập tuyệt đối về Schema:** Kết quả trích xuất của CA-VHC và Writer Profile được lưu trữ trong hai thư mục riêng biệt với schema JSON độc lập. Không lồng ghép schema này vào schema kia.
2. **Tham chiếu một chiều qua Reference ID:** Mọi bản ghi annotation trong cả hai dataset đều chứa trường `source_image_id` và `writer_id` để truy vết nguồn gốc hình ảnh mà không tạo phụ thuộc dữ liệu vòng.
3. **Không ràng buộc phụ thuộc:** Việc trích xuất hoặc vắng mặt của Writer Profile không ảnh hưởng đến tính hợp lệ của CA-VHC Dataset, và ngược lại.

---

## 2. Phân công trách nhiệm (Dataset Ownership)

Quy định phân định quyền sở hữu và trách nhiệm giữa các thành viên nhóm nghiên cứu tuân thủ nghiêm ngặt theo kiến trúc 4 đường chạy của OmniDraw:

| Thành viên / Vai trò | Trách nhiệm đối với Dataset Chữ viết tay | Ranh giới phạm vi (Boundary & Non-goals) |
| :--- | :--- | :--- |
| **TV1 — AI Data & Writer Personalization Lead** | • Quản trị kho dữ liệu (`dataset/raw`, `dataset/processed`).<br>• Xây dựng phiếu thu thập mẫu (Collection Form) và Scanning Protocol.<br>• Thực thi quy trình thu thập, ẩn danh hóa và quản lý đạo đức dữ liệu.<br>• Định nghĩa schema dữ liệu thô và annotation metadata.<br>• Chuẩn bị dữ liệu thực nghiệm, benchmark fixtures cung cấp cho TV4.<br>• Trích xuất đặc trưng hình học phong cách người viết (Writer Profile P2). | **KHÔNG** sở hữu quy tắc phân rã Unicode NFD, quy tắc chính tả, vị trí mỏ neo hay logic đồ thị Trellis DAG của Handwriting Engine (đây là thẩm quyền của TV4).<br>**KHÔNG** tự ý nâng trạng thái Writer Profile thành đã tích hợp engine khi chưa qua cổng kiểm duyệt. |
| **TV4 — Project Lead & Handwriting / CA-VHC Composition Lead** | • Toàn quyền sở hữu kiến trúc Context-Aware Vietnamese Handwriting Composition (CA-VHC).<br>• Thiết lập quy chuẩn phân rã ký tự Unicode NFD và quy tắc chính tả dấu tiếng Việt.<br>• Xác lập quy chuẩn tọa độ mỏ neo (anchors), khoảng dịch tâm (offsets) và vùng cấm va chạm (collision clearance).<br>• Thiết kế logic lựa chọn biến thể glyph theo ngữ cảnh (Contextual Allographs).<br>• Tiếp nhận dữ liệu từ TV1 để calibrate và đánh giá giải thuật.<br>• Xây dựng Experiment Runner, CSV logging và điều phối tích hợp toàn hệ thống. | Quy tắc và logic sử dụng dấu tiếng Việt thuộc quyền quyết định của TV4, TV1 chỉ đóng vai trò thu thập và chuẩn bị dữ liệu theo tiêu chuẩn do TV4 ban hành. |
| **TV2 — Stroke Optimization & Path Planning Lead** | • Phối hợp với TV4 xác định yêu cầu dữ liệu đối với bài toán tối ưu hóa nét trễ (delayed strokes: dấu thanh, nét gạch ngang của chữ 'đ', 't').<br>• Định nghĩa các tham số chi phí động học ($D_{\text{penup}}$, $N_{\text{lift}}$, $C_{\text{curvature}}$) để định hướng thu thập các mẫu nét nối. | **KHÔNG** sở hữu quy tắc chính tả hoặc cấu trúc ngữ âm của dấu tiếng Việt. |
| **TV3 — Hardware, Calibration & Physical Validation Lead** | • Cung cấp các giới hạn cơ học của máy vẽ AxiDraw (độ phân giải bước micro-step, quán tính ngòi bút, độ dày nét mực vật lý) để làm căn cứ thiết lập ngưỡng an toàn hình học cho dataset.<br>• Thực hiện kiểm chứng thi công thực tế trên giấy khi có tập mẫu. | **KHÔNG** can thiệp vào schema phần mềm nếu không liên quan trực tiếp đến giới hạn vật lý. |

---

## 3. Quy trình thu thập dữ liệu (Data Collection Protocol)

Quy trình thu thập được thiết kế theo 7 giai đoạn khép kín nhằm bảo đảm độ tin cậy khoa học, tính nhất quán hình học và tuân thủ đạo đức nghiên cứu:

```text
[1. Tuyển chọn & Consent]
        │
        ▼
[2. Phát phiếu thu thập chuẩn]
        │
        ▼
[3. Thực hiện viết mẫu]
        │
        ▼
[4. Quét ảnh phẳng 600 DPI]
        │
        ▼
[5. Tiền xử lý & Căn chỉnh hình học]
        │
        ▼
[6. Ẩn danh hóa (Gán Writer ID)]
        │
        ├───────────────────────────────────────┐
        ▼                                       ▼
[7A. Pipeline gán nhãn CA-VHC]          [7B. Pipeline trích đặc trưng Writer Profile]
(Do TV1 gán nhãn theo spec TV4)         (Do TV1 nghiên cứu trích xuất P2)
```

### 3.1. Các bước thực hiện chi tiết

1. **Tuyển chọn người viết & Ký cam kết đồng thuận (Informed Consent):**
   - Giới thiệu rõ mục đích phi thương mại của đề tài NCKH.
   - Người tham gia ký thỏa thuận chấp thuận chia sẻ mẫu chữ viết tay cho mục đích nghiên cứu học thuật.
   - Tuyệt đối không lưu trữ thông tin cá nhân trên phiếu viết.

2. **Phát phiếu thu thập chuẩn (Standard Collection Sheet):**
   - Phiếu in trên giấy trắng định lượng tiêu chuẩn $80\,\text{g/m}^2$, kích thước A4.
   - Phiếu chứa lưới định chuẩn (grid boxes) có đánh dấu đường baseline, ascender line, descender line bằng mực xám nhạt ($10\%$ K) để dễ dàng lọc bỏ bằng ngưỡng nhị phân mà không làm mất nét chữ.
   - Phiếu có 4 dấu mốc định vị góc (fiducial markers) phục vụ tự động deskew và căn chỉnh tọa độ.

3. **Thực hiện viết mẫu (Writing Phase):**
   - Sử dụng một loại bút quy chuẩn chung: bút bi ngòi gel đen $0.5\,\text{mm}$ (ví dụ: Pentel EnerGel hoặc Pilot G2) để giữ đồng nhất độ tương phản và bề rộng nét.
   - Người tham gia viết với tốc độ tự nhiên, không cố tình tô đậm, không dùng bút xóa hoặc đè nét sửa lỗi.

4. **Quét ảnh độ phân giải cao (Scanning Protocol):**
   - Sử dụng máy quét phẳng (Flatbed Scanner), đặt độ phân giải quang học tối thiểu $300\,\text{DPI}$ (khuyến nghị chuẩn $600\,\text{DPI}$ để phục vụ trích xuất curvature mượt mà).
   - Chế độ quét: 24-bit True Color (RGB) hoặc 8-bit Grayscale, lưu định dạng không nén (TIFF) hoặc nén bảo toàn dữ liệu (Lossless PNG).
   - Tắt toàn bộ các tính năng tự động can thiệp của phần mềm máy quét (tắt auto-contrast, unsharp mask, despeckle).

5. **Tiền xử lý ảnh thô (Raw Image Preprocessing):**
   - Tự động phát hiện 4 fiducial markers để thực hiện phép biến đổi affine xoay phẳng (affine deskew).
   - Kiểm tra chất lượng tự động: cảnh báo nếu ảnh bị mờ nét, bị bóng đổ hoặc thiếu góc.

6. **Ẩn danh hóa dữ liệu (Anonymization):**
   - Gán mã định danh duy nhất `writer_id` theo định dạng `W{xxx}` (ví dụ: `W001`, `W002`).
   - Tách biệt hoàn toàn phiếu đăng ký ban đầu sang kho lưu trữ cách ly ngoại tuyến (air-gapped registry).

7. **Bóc tách và gán nhãn dữ liệu (Dual Annotation):**
   - Bóc tách theo bounding box của từng ký tự, âm tiết và từ ngữ cảnh.
   - Chuyển tiếp vào hai pipeline chuyên biệt theo phân công trách nhiệm.

---

## 4. Bộ mẫu thu thập chuẩn (Standard Prompt Set)

Để một bộ phiếu thu thập phục vụ tối ưu cho cả hai bài toán (CA-VHC và Writer Profile), nội dung thu thập được thiết kế theo 4 nhóm mẫu phân bổ tương ứng vào 4 trang của bộ **OmniDraw Handwriting Collection Sheet Pack v1** (`docs/collection_sheets/P01..P04/`):

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               CẤU TRÚC BỘ PHIẾU THU THẬP CHỮ VIẾT TAY (COLLECTION SHEET PACK)           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Trang P01 — Bảng ký tự rời & Tổ hợp dấu (Single Characters & Diacritic Coverage)       │
│ • Mã phiếu: P01 — Isolated Characters & Diacritics Collection Sheet                    │
│ • Phạm vi prototype hiện tại: Tập mẫu đại diện tiêu biểu (representative subset) gồm   │
│   26 chữ cái thường, 26 chữ cái hoa, 10 chữ số, và 18 nguyên âm có dấu tiêu biểu đại   │
│   diện cho các thanh điệu (sắc, huyền, hỏi, ngã, nặng) và dấu mũ/móc (â, ă, ê, ô, ơ, ư)│
│   trong các ô viết định chuẩn 14 × 14 mm với clearance an toàn quang học.              │
│ • Mục tiêu dài hạn: Ma trận 67 dạng nguyên âm có dấu (Mục 4.1) được mở rộng qua các    │
│   phiên bổ sung hoặc bộ phiếu nâng cao.                                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Trang P02 — Từ ngữ cảnh & Cặp ký tự nối nét (Contextual Words & Ligatures)             │
│ • Mã phiếu: P02 — Contextual Words & Ligatures Collection Sheet                         │
│ • Phạm vi: 12 từ ngữ cảnh tiêu biểu đại diện cho 3 nhóm vị trí:                        │
│   - Word-Initial Uppercase: "Kính gửi", "Thân gửi", "Cảm ơn", "Chào mừng"              │
│   - Medial Ligatures & Diacritic Clearance: "thuyền", "nghiêng", "trường", "nguyễn"    │
│   - Word-Final Terminals: "bạn", "nam", "nhìn", "tình"                                 │
│ • Mục tiêu: Khảo sát nối nét thực tế, biến thể đầu/cuối từ và khoảng hở tránh đè dấu.  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Trang P03 — Câu Pangram tiếng Việt chuẩn mực (Sentence Flow & Vietnamese Pangrams)     │
│ • Mã phiếu: P03 — Sentence Flow & Pangram Collection Sheet                             │
│ • Phạm vi: 3 câu văn chuẩn mực (mỗi câu gồm 2 dòng kẻ viết có guiding lines):          │
│   - SENT_001 (16 từ, 69 ký tự không dấu cách):                                         │
│     "Do bạch kim rất quý nên qua thời gian phong thổ vẫn giữ màu sáng rực rỡ."         │
│   - SENT_002 (12 từ, 54 ký tự không dấu cách):                                         │
│     "Cậu bé xinh đẹp này phóng vèo qua dãy phố cổ mù sương."                           │
│   - SENT_003 (13 từ, 53 ký tự không dấu cách):                                         │
│     "Hoàng tử nhảy múa cùng các cô gái vùng biển xanh biếc."                            │
│ • Mục tiêu: Khảo sát dòng chảy câu liên tục, độ ổn định baseline và nhịp viết tự nhiên.│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Trang P04 — Đoạn văn xuôi liền mạch (Natural Paragraph Writing)                        │
│ • Mã phiếu: P04 — Natural Paragraph Writing Collection Sheet                           │
│ • Phạm vi: 1 đoạn văn xuôi liên tục 5 dòng kẻ (`PARA_001`: 35 từ, 172 ký tự không cách):│
│   "Mỗi dòng chữ nắn nót trên trang giấy trắng là nhịp cầu nối liền những tấm lòng      │
│    thân thương, gửi gắm trọn vẹn niềm tin cùng bao ước vọng tốt đẹp nhất về một tương │
│    lai tươi sáng phía trước."                                                          │
│ • Mục tiêu: Khảo sát độ trôi baseline dài hạn, mật độ chữ, khoảng cách dòng và phong  │
│   cách người viết ở cấp đoạn văn trên bản quét tĩnh.                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1. Độ phủ ký tự có dấu tiếng Việt (Chi tiết 67 dạng nguyên âm)

Hệ thống ghi nhận và kiểm tra đầy đủ 12 nguyên âm cơ sở và các dạng kết hợp dấu (ma trận mục tiêu toàn diện):
- **Nguyên âm A:** `a, á, à, ả, ã, ạ`
- **Nguyên âm Ă:** `ă, ắ, ằ, ẳ, ẵ, ặ`
- **Nguyên âm Â:** `â, ấ, ầ, ẩn, ẫ, ậ`
- **Nguyên âm E:** `e, é, è, ẻ, ẽ, ẹ`
- **Nguyên âm Ê:** `ê, ế, ề, ể, ễ, ệ`
- **Nguyên âm I:** `i, í, ì, ỉ, ĩ, ị`
- **Nguyên âm O:** `o, ó, ò, ỏ, õ, ọ`
- **Nguyên âm Ô:** `ô, ố, ồ, ổ, ỗ, ộ`
- **Nguyên âm Ơ:** `ơ, ớ, ờ, ở, ỡ, ợ`
- **Nguyên âm U:** `u, ú, ù, ủ, ũ, ụ`
- **Nguyên âm Ư:** `ư, ứ, ừ, sử, ữ, ự`
- **Nguyên âm Y:** `y, ý, ỳ, ỷ, ỹ, ỵ`

> [!NOTE]
> Trong phiếu P01 prototype hiện hành, do giới hạn diện tích trang A4 để bảo đảm ô viết đủ lớn ($14 \times 14\,\text{mm}$), một tập con đại diện gồm 18 nguyên âm có dấu tiêu biểu được sử dụng. Ma trận 67 dạng nguyên âm đầy đủ nêu trên là mục tiêu độ phủ ngữ âm tổng thể của dự án.

### 4.2. Độ phủ ngữ cảnh (Contextual Positions)

Mỗi ký tự mục tiêu cần được xuất hiện ở tối thiểu 4 trạng thái ngữ cảnh:
1. `isolated`: Viết riêng lẻ trong ô định chuẩn (thu thập tại P01).
2. `word_initial`: Nằm ở vị trí ký tự đầu tiên của từ (thu thập tại P02).
3. `word_medial`: Nằm kẹp giữa hai ký tự khác trong một âm tiết (thu thập tại P02, P03).
4. `word_final`: Nằm ở vị trí kết thúc của từ (thu thập tại P02, P03).

---

## 5. Đặc tả dữ liệu thô (Raw Data Specification)

### 5.1. Quy cách kỹ thuật của tệp quét gốc

| Tham số | Quy định bắt buộc | Ghi chú kỹ thuật |
| :--- | :--- | :--- |
| **Định dạng file** | `.png` (Lossless PNG) | Tuyệt đối không dùng `.jpg` cho ảnh gốc do hiện tượng nén khối DCT (blocking artifacts) làm biến dạng viền nét mực khi trích xuất vector. |
| **Độ phân giải** | $600\,\text{DPI}$ ($23.62\,\text{pixels/mm}$) | Cho phép bóc tách chi tiết ngòi bút $0.5\,\text{mm}$ tương đương bề rộng xấp xỉ 12 pixels. |
| **Không gian màu** | RGB 24-bit hoặc Grayscale 8-bit | Khuyến nghị lưu RGB để hỗ trợ phân tích độ đậm nhạt của mực bút bi. |
| **Tỷ lệ co giãn** | 1:1 (True scale) | Giữ nguyên kích thước vật lý tờ giấy ($210 \times 297\,\text{mm}$). |

### 5.2. Quy tắc đặt tên file thô (Raw Image Naming Convention)

Mọi tệp quét gốc được lưu trữ tại `dataset/raw/images/` theo cấu trúc danh định:

$$\text{\{writer\_id\}\_\{session\_id\}\_\{page\_number\}.png}$$

**Phân định rạch ròi các thành phần định danh:**
- `writer_id`: Mã định danh người viết ẩn danh gồm chữ `W` và 3 chữ số (ví dụ: `W001`, `W012`). Mỗi tình nguyện viên tham gia chỉ được cấp duy nhất một `writer_id`.
- `session_id`: Mã phiên thu thập gồm chữ `S` và 2 chữ số (ví dụ: `S01`, `S02`). Phản ánh thời điểm hoặc đợt viết cụ thể của người đó (cho phép theo dõi sự ổn định chữ viết qua các buổi khác nhau).
- `page_number`: Mã trang trong bộ phiếu gồm chữ `P` và 2 chữ số (`P01`, `P02`, `P03`, `P04`).
- **Form Version (`vX.Y`):** Phiên bản kỹ thuật của mẫu thiết kế phiếu (ví dụ `v0.1` pilot prototype, `v1.0` formal release). Phiên bản phiếu được quản lý chặt chẽ trong metadata manifest (`collection_manifest.jsonl`) và technical notes, **TUYỆT ĐỐI KHÔNG gộp cứng vào tên file ảnh thô** nhằm bảo đảm cấu trúc tên file bất biến, ngắn gọn và tương thích tự nhiên với các pipeline xử lý tự động.
- *Ví dụ mẫu:* `W001_S01_P01.png`, `W001_S01_P02.png`, `W001_S01_P03.png`, `W001_S01_P04.png`.

### 5.3. Tính bất biến của dữ liệu thô (Immutability Principle)

> [!IMPORTANT]
> **Nguyên tắc bất biến:** Toàn bộ thư mục `dataset/raw/` là kho dữ liệu chỉ đọc (**read-only**). 
> Tuyệt đối không chỉnh sửa trực tiếp, không cắt xén ghi đè, không lưu đè ảnh đã lọc nhị phân vào thư mục này. Mọi biến đổi hoặc trích xuất đều phải ghi sang thư mục `dataset/processed/`.

---

## 6. Cấu trúc thư mục dữ liệu (Directory Layout)

Cấu trúc cây thư mục được thiết kế rõ ràng, tách biệt hoàn toàn giữa dữ liệu thô, dữ liệu CA-VHC và dữ liệu Writer Profile:

```text
OmniDraw/
├── dataset/
│   ├── README.md                           # Hướng dẫn tổng quan về dataset
│   ├── raw/
│   │   ├── images/                         # Ảnh quét gốc bất biến (PNG 600 DPI)
│   │   │   ├── W001_S01_P01.png
│   │   │   ├── W001_S01_P02.png
│   │   │   └── ...
│   │   └── manifests/                      # Bảng kê khai đợt thu thập (metadata)
│   │       └── collection_manifest.jsonl
│   ├── processed/
│   │   ├── ca_vhc/                         # Phân nhánh CA-VHC (TV4 sở hữu quy tắc, TV1 chuẩn bị data)
│   │   │   ├── annotations/                # Dữ liệu gán nhãn cấu trúc và mỏ neo dấu
│   │   │   │   ├── ca_vhc_train.jsonl
│   │   │   │   ├── ca_vhc_val.jsonl
│   │   │   │   └── ca_vhc_test.jsonl
│   │   │   ├── crops/                      # Ảnh trích xuất từng ký tự / âm tiết chuẩn hóa
│   │   │   │   ├── glyphs/
│   │   │   │   └── diacritics/
│   │   │   └── splits/                     # Danh sách phân chia train/val/test cố định
│   │   │       └── split_metadata_v1.json
│   │   └── writer_profiles/                # Phân nhánh Writer Profile (TV1 sở hữu, P2 Future Research)
│   │       ├── profiles/                   # File JSON hồ sơ người viết hoàn chỉnh
│   │       │   ├── profile_W001_v1.json
│   │       │   ├── profile_W002_v1.json
│   │       │   └── ...
│   │       └── features/                   # Bảng tổng hợp vector đặc trưng trung gian
│   │           └── writer_features_summary.jsonl
│   └── schemas/                            # Định nghĩa JSON Schema kiểm thực
│       ├── ca_vhc_annotation.schema.json   # Schema gán nhãn CA-VHC (PROPOSED / NON-BINDING)
│       ├── writer_profile.schema.json      # Schema Writer Profile (P2 / NON-BINDING)
│       └── collection_manifest.schema.json # Schema quản lý phiên thu thập
```

### 6.1. Quy định định dạng lưu trữ (Storage Format Governance)

- **Giai đoạn hiện tại (Pilot & Development Phase):**
  - Sử dụng chuẩn định dạng `.jsonl` (JSON Lines) cho toàn bộ annotations và features.
  - *Lý do:* Dễ đọc hiểu trực tiếp bằng mắt (human-readable), tương thích tự nhiên với Git diff, xử lý streaming từng dòng bằng Python mà không chiếm dụng bộ nhớ RAM lớn.
- **Định hướng mở rộng quy mô lớn (Recommended Future Format):**
  - Khi tập dữ liệu vượt quá $50.000$ mẫu bóc tách, nhóm khuyến nghị chuyển đổi bảng dữ liệu gán nhãn sang định dạng **Apache Parquet** (`.parquet`).
  - *Lý do:* Nén dung lượng cột vượt trội ($>70\%$), tối ưu tốc độ đọc lọc dữ liệu số học với DuckDB / Pandas / PyArrow phục vụ huấn luyện máy học.

---

## 7. Schema dữ liệu CA-VHC (CA-VHC Annotation Schema)

> [!NOTE]
> **Trạng thái:** `PROPOSED / NON-BINDING`  
> Schema dưới đây được định nghĩa phục vụ chuẩn hóa dữ liệu nghiên cứu và huấn luyện ngoại tuyến (offline calibration). Schema này **KHÔNG ràng buộc** lên các cấu trúc dữ liệu nội bộ của `backend/handwriting/engine.py` hay Font Pack hiện hành.

Tệp định nghĩa: `dataset/schemas/ca_vhc_annotation.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OmniDraw_CA_VHC_Annotation_Schema",
  "type": "object",
  "required": [
    "sample_id",
    "writer_id",
    "source_image_id",
    "char_raw",
    "unicode_nfd",
    "base_char",
    "diacritics",
    "context_info",
    "geometry",
    "quality_flags"
  ],
  "properties": {
    "sample_id": {
      "type": "string",
      "description": "Định danh duy nhất của mẫu ký tự/âm tiết trích xuất, ví dụ: 'SMP_W001_00421'"
    },
    "writer_id": {
      "type": "string",
      "description": "Mã định danh người viết tham chiếu, ví dụ: 'W001'"
    },
    "source_image_id": {
      "type": "string",
      "description": "Tên tệp ảnh gốc nguồn, ví dụ: 'W001_S01_P01.png'"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Thời điểm thực hiện trích xuất và gán nhãn"
    },
    "char_raw": {
      "type": "string",
      "description": "Ký tự hoặc âm tiết tiếng Việt nguyên bản (Unicode NFC), ví dụ: 'ế'"
    },
    "unicode_nfd": {
      "type": "string",
      "description": "Chuỗi phân rã chuẩn NFD, ví dụ: 'e\\u0302\\u0301'"
    },
    "base_char": {
      "type": "string",
      "description": "Ký tự gốc không dấu, ví dụ: 'e'"
    },
    "diacritics": {
      "type": "array",
      "description": "Danh sách các dấu cấu trúc và dấu thanh hiện diện trên ký tự",
      "items": {
        "type": "object",
        "required": ["type", "unicode_codepoint"],
        "properties": {
          "type": {
            "type": "string",
            "enum": [
              "circumflex", "breve", "horn",
              "acute", "grave", "hook_above", "tilde", "dot_below"
            ]
          },
          "unicode_codepoint": { "type": "string" },
          "bounding_box": {
            "type": "array",
            "items": { "type": "number" },
            "minItems": 4,
            "maxItems": 4,
            "description": "[x_min, y_min, x_max, y_max] tính bằng pixel trên ảnh gốc"
          }
        }
      }
    },
    "tone_mark": {
      "type": "string",
      "enum": ["none", "acute", "grave", "hook_above", "tilde", "dot_below"],
      "description": "Dấu thanh chính của âm tiết"
    },
    "context_info": {
      "type": "object",
      "required": ["position"],
      "properties": {
        "position": {
          "type": "string",
          "enum": ["isolated", "word_initial", "word_medial", "word_final"],
          "description": "Vị trí ngữ cảnh trong từ"
        },
        "prev_char": { "type": ["string", "null"] },
        "next_char": { "type": ["string", "null"] },
        "syllable_text": { "type": ["string", "null"] },
        "letter_type": { "type": "string", "default": "general" }
      }
    },
    "geometry": {
      "type": "object",
      "required": ["bounding_box", "baseline_y", "base_anchor", "diacritic_offset"],
      "properties": {
        "bounding_box": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 4,
          "maxItems": 4,
          "description": "[x_min, y_min, x_max, y_max] của toàn bộ cụm glyph (pixel)"
        },
        "baseline_y": {
          "type": "number",
          "description": "Tung độ trục chân dòng định chuẩn (pixel)"
        },
        "base_anchor": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 2,
          "maxItems": 2,
          "description": "Tọa độ điểm mỏ neo trên đỉnh glyph cơ sở [x, y] tính bằng mm chuẩn hóa"
        },
        "diacritic_anchor": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 2,
          "maxItems": 2,
          "description": "Tọa độ tâm hình học của dấu [x, y] tính bằng mm chuẩn hóa"
        },
        "diacritic_offset": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 2,
          "maxItems": 2,
          "description": "Độ dịch tương đối giữa dấu và mỏ neo [dx, dy] (mm)"
        },
        "clearance_box": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 4,
          "maxItems": 4,
          "description": "Vùng bao an toàn chống va chạm xung quanh dấu [xmin, ymin, xmax, ymax]"
        }
      }
    },
    "quality_flags": {
      "type": "object",
      "required": ["legibility_score", "is_degenerate", "is_ambiguous"],
      "properties": {
        "legibility_score": {
          "type": "integer",
          "minimum": 1,
          "maximum": 5,
          "description": "Đánh giá độ đọc được định tính (1: rất tệ/mất nét, 5: hoàn hảo chuẩn mực)"
        },
        "is_degenerate": {
          "type": "boolean",
          "description": "True nếu nét bị đứt đoạn, chấm mực bẩn hoặc méo mó không thể phân tích"
        },
        "is_ambiguous": {
          "type": "boolean",
          "description": "True nếu dấu bị mập mờ giữa hỏi/ngã hoặc sắc/nặng"
        },
        "annotator_id": { "type": "string" }
      }
    }
  }
}
```

---

## 8. Schema dữ liệu Writer Profile (Writer Profile Schema)

> [!NOTE]
> **Trạng thái:** `P2 / FUTURE RESEARCH / NON-BINDING`  
> Schema này phục vụ nghiên cứu trích xuất đặc trưng phong cách cá nhân hóa do TV1 chủ trì. Schema này **tách biệt hoàn toàn** khỏi `FontPack` và các cấu hình kết xuất hiện có của core engine.

Tệp định nghĩa: `dataset/schemas/writer_profile.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OmniDraw_Writer_Profile_Schema",
  "type": "object",
  "required": [
    "profile_id",
    "writer_id",
    "version",
    "created_at",
    "num_samples_analyzed",
    "global_style",
    "spacing",
    "diacritic_tendencies"
  ],
  "properties": {
    "profile_id": {
      "type": "string",
      "description": "Mã định danh duy nhất của hồ sơ phong cách, ví dụ: 'profile_W001_v1'"
    },
    "writer_id": {
      "type": "string",
      "description": "Mã tham chiếu người viết ẩn danh, ví dụ: 'W001'"
    },
    "version": {
      "type": "string",
      "description": "Phiên bản thuật toán trích xuất đặc trưng, ví dụ: '1.0.0'"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "num_samples_analyzed": {
      "type": "integer",
      "minimum": 1,
      "description": "Số lượng mẫu ký tự/từ dùng để ước lượng vector đặc trưng"
    },
    "global_style": {
      "type": "object",
      "required": [
        "mean_slant_deg",
        "aspect_ratio_mean",
        "stroke_width_mean_mm",
        "baseline_jitter_std"
      ],
      "properties": {
        "mean_slant_deg": {
          "type": "number",
          "minimum": -45.0,
          "maximum": 45.0,
          "description": "Góc nghiêng trung bình của nét dọc so với phương thẳng đứng (độ)"
        },
        "aspect_ratio_mean": {
          "type": "number",
          "minimum": 0.3,
          "maximum": 2.5,
          "description": "Tỷ lệ chiều rộng / chiều cao trung bình của thân chữ (x-height body)"
        },
        "stroke_width_mean_mm": {
          "type": "number",
          "description": "Bề rộng nét bút ước tính (mm)"
        },
        "baseline_jitter_std": {
          "type": "number",
          "minimum": 0.0,
          "description": "Độ lệch chuẩn dao động của chân chữ quanh baseline danh định (mm)"
        }
      }
    },
    "spacing": {
      "type": "object",
      "required": [
        "char_spacing_mean_ratio",
        "word_spacing_mean_ratio",
        "line_spacing_mean_ratio"
      ],
      "properties": {
        "char_spacing_mean_ratio": {
          "type": "number",
          "description": "Tỷ lệ khoảng cách giữa các ký tự so với chiều rộng trung bình"
        },
        "word_spacing_mean_ratio": {
          "type": "number",
          "description": "Tỷ lệ khoảng cách giữa các từ so với chiều rộng ký tự"
        },
        "line_spacing_mean_ratio": {
          "type": "number",
          "description": "Tỷ lệ khoảng cách giữa các dòng văn bản"
        }
      }
    },
    "diacritic_tendencies": {
      "type": "object",
      "required": ["diacritic_offset_bias", "diacritic_scale_ratio"],
      "properties": {
        "diacritic_offset_bias": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 2,
          "maxItems": 2,
          "description": "Độ lệch dịch tâm dấu trung bình của cá nhân người viết so với chuẩn [dx, dy] (mm)"
        },
        "diacritic_scale_ratio": {
          "type": "number",
          "description": "Tỷ lệ kích thước dấu trung bình so với kích thước thân chữ (scale)"
        }
      }
    },
    "allograph_tendencies": {
      "type": "object",
      "description": "Bảng tần suất/xác suất lựa chọn biến thể glyph cụ thể (ví dụ tỷ lệ dùng nét móc cuối từ)",
      "additionalProperties": { "type": "number" }
    }
  }
}
```

---

## 9. Quy trình chia tập dữ liệu (Train / Validation / Test Protocol)

Để bảo đảm tính hợp lệ học thuật cho các bài báo khoa học xuất bản từ đề tài, quy trình phân chia dữ liệu tuân thủ các nguyên tắc nghiêm ngặt chống rò rỉ dữ liệu (Data Leakage):

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               NGUYÊN TẮC PHÂN CHIA WRITER-DISJOINT (TÁCH BIỆT NGƯỜI VIẾT)               │
├───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│ TẬP HUẤN LUYỆN (TRAIN SET)    │ TẬP HIỆU CHUẨN (VAL SET)      │ TẬP ĐÁNH GIÁ (TEST SET)│
│ Tỷ lệ: ~70% số lượng Writer   │ Tỷ lệ: ~15% số lượng Writer   │ Tỷ lệ: ~15% số lượng W │
├───────────────────────────────┼───────────────────────────────┼────────────────────────┤
│ Kế hoạch: W001 – W028 (28)    │ Kế hoạch: W029 – W034 (6)     │ Kế hoạch: W035 – W040 (6)│
├───────────────────────────────┴───────────────────────────────┴────────────────────────┤
│ RÀNG BUỘC SẮT:                                                                         │
│ 1. Toàn bộ mẫu của một Writer chỉ xuất hiện DUY NHẤT trong một tập (Disjoint).          │
│ 2. Tuyệt đối không chia ngẫu nhiên ở cấp độ ký tự (tránh cùng 1 người vừa học vừa thi).│
│ 3. Đánh giá tính tổng quát hóa (Generalization) trên người viết hoàn toàn mới.         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Trạng thái thực tế:** Quy mô ~40 người viết và tỷ lệ phân chia 28 Train / 6 Val / 6 Test là **KẾ HOẠCH MỤC TIÊU DỰ KIẾN (PLANNED TARGET PROTOCOL)** cho giai đoạn thu thập chính thức.
> Dự án hiện **CHƯA** thực hiện thu thập quy mô lớn này và **CHƯA** có dữ liệu của 40 người viết. Toàn bộ công việc dữ liệu hiện tại mới dừng ở mức hoàn thiện thiết kế bộ phiếu thu thập mẫu v1 (P01–P04 Pilot Candidate) và chuẩn bị công cụ scan-validation.

### 9.1. Quy tắc phân chia

1. **Phân chia theo cụm người viết (Writer-Disjoint Split):**
   - Mọi bản ghi trích xuất từ cùng một `writer_id` bắt buộc phải nằm trọn vẹn trong duy nhất một phân tập: Train, Validation hoặc Test.
   - Việc phân chia ngẫu nhiên ở cấp độ ký tự (sample-level random split) bị **nghiêm cấm tuyệt đối** vì sẽ gây rò rỉ đặc trưng phong cách cá nhân vào tập đánh giá, làm sai lệch kết quả nghiên cứu.
2. **Phân tầng độ phủ ngữ âm (Stratified Coverage Check):**
   - Sau khi phân bổ theo writer, thuật toán phân chia phải kiểm tra bảo đảm cả 3 tập đều chứa đầy đủ 67 nguyên âm có dấu và các tổ hợp dấu thanh tiếng Việt phức tạp.
3. **Cố định Random Seed & Metadata Reproducibility:**
   - Quá trình phân chia được thực thi bằng mã nguồn tự động với hạt giống ngẫu nhiên cố định: `DATA_SPLIT_SEED = 20260919`.
   - Danh sách phân bổ chi tiết từng `writer_id` vào các tập được lưu cố định tại `dataset/processed/ca_vhc/splits/split_metadata_v1.json`.

---

## 10. Bảo mật, đạo đức và tuân thủ (Privacy, Consent & Ethics)

Dự án OmniDraw cam kết tuân thủ các chuẩn mực đạo đức nghiên cứu học thuật quốc tế đối với dữ liệu sinh trắc học hành vi:

1. **Quyền riêng tư & Ẩn danh hóa một chiều (One-Way Anonymization):**
   - Không lưu trữ tên thật, mã sinh viên, email, số điện thoại hoặc địa chỉ của người tham gia trong kho dữ liệu Git hoặc các tệp JSON công khai.
   - Mỗi người tham gia được định danh bằng một mã số ngẫu nhiên `W{xxx}`.
   - Bảng ánh xạ giữa danh tính thực tế và `writer_id` được mã hóa mạnh (AES-256) và lưu trữ ngoại tuyến trên thiết bị lưu trữ vật lý cách ly (Air-gapped offline storage), chỉ người quản trị dữ liệu TV1 và Project Lead TV4 được quyền truy cập khi có yêu cầu pháp lý.
2. **Tuyệt đối nghiêm cấm thu thập chữ ký cá nhân thật:**
   - Phiếu thu thập **không có mục ký tên**.
   - Người tham gia được hướng dẫn rõ ràng: **Tuyệt đối không ký chữ ký sử dụng trong ngân hàng, giao dịch dân sự hoặc giấy tờ tùy thân** vào bất kỳ vị trí nào trên phiếu thu thập.
   - Nếu phát hiện mẫu viết có dấu hiệu là chữ ký thật hoặc tên riêng cá nhân, dữ liệu đó lập tức bị hủy bỏ (redacted / purged) khỏi dataset.
3. **Quyền rút lui khỏi nghiên cứu (Right of Withdrawal):**
   - Người tham gia có quyền rút lại sự đồng thuận bất kỳ lúc nào trước khi bộ dữ liệu được đóng gói đóng băng phiên bản phục vụ bảo vệ đề tài. Khi nhận được yêu cầu, toàn bộ tệp quét gốc và dữ liệu trích xuất của `writer_id` tương ứng sẽ bị xóa vĩnh viễn.

---

## 11. Quản trị phiên bản dữ liệu (Dataset Versioning Protocol)

Để bảo đảm tính kiểm chứng độc lập và khả năng tái lập thí nghiệm khoa học, bộ dữ liệu được quản lý phiên bản theo chuẩn **Semantic Versioning for Datasets**:

$$\text{v<Major>.<Minor>.<Patch>[-Tag]}$$

- **Major (Đại phiên bản):** Tăng khi có thay đổi cấu trúc schema làm gãy tương thích ngược (breaking changes), thay đổi chuẩn tọa độ hình học, hoặc thay đổi định dạng phiếu thu thập.
- **Minor (Trung phiên bản):** Tăng khi bổ sung thêm số lượng người viết (`writer_id`) mới hoặc mở rộng thêm prompt set mà không làm thay đổi cấu trúc schema hiện có.
- **Patch (Tiểu phiên bản):** Tăng khi sửa lỗi nhãn gán sai (re-annotation), loại bỏ mẫu suy biến, hoặc cập nhật tọa độ bounding box/offset chính xác hơn.
- **Tag:** Nhãn giai đoạn, ví dụ: `-pilot` (dữ liệu thử nghiệm ban đầu), `-formal` (dữ liệu chính thức).
- *Ví dụ:* `v1.0.0-pilot`, `v1.1.0-expanded`.

### 11.1. Khuyến nghị công cụ DVC (Data Version Control)

- **Trạng thái:** *Khuyến nghị tương lai (Recommended Future Tool)*.
- **Định hướng:** Nhóm khuyến nghị sử dụng DVC (`dvc`) phối hợp với Git để theo dõi các tệp ảnh nhị phân lớn (`.png`) thông qua tệp con trỏ `.dvc` lưu trữ trên Google Drive hoặc Cloud Storage, tránh làm phình to dung lượng kho chứa Git của dự án.
- **Hiện tại:** Chưa bắt buộc cài đặt DVC trong môi trường phát triển cục bộ hiện thời để giữ hệ thống gọn nhẹ.

---

## 12. Bảng trạng thái thực tế hệ thống (Implementation Status Matrix)

Nhằm duy trì tính trung thực khoa học tuyệt đối trong toàn bộ hồ sơ dự án, bảng dưới đây tổng hợp chính xác trạng thái thực tế của từng hạng mục kỹ thuật tính đến thời điểm hiện tại:

| Hạng mục | Trách nhiệm | Trạng thái thực tế | Ghi chú & Ranh giới hiện hành |
| :--- | :--- | :--- | :--- |
| **Đặc tả ranh giới 2 Dataset (CA-VHC vs Writer Profile)** | TV1 & TV4 | **IMPLEMENTED** | Đã chuẩn hóa toàn diện trong tài liệu `08_handwriting_dataset_spec.md`. |
| **Bảng chữ cái & Ghép dấu Unicode NFD chuẩn** | TV4 | **IMPLEMENTED** | Đã hoạt động trong `backend/handwriting/engine.py` cho các font hiện có. |
| **Kiến trúc Font Pack nét đơn độc lập** | TV4 | **IMPLEMENTED** | Đã tách thành package `backend/handwriting/font_packs/` (`legacy`, `omni_casual`). |
| **Auditor kiểm tra hình học polyline** | TV4 | **IMPLEMENTED** | Đã có `audit_font_pack_geometry()` và `qa_specimens.py`. |
| **Strict Validation trên API Gateway** | TV4 | **IMPLEMENTED** | 34/34 tests pass trong `backend/test_handwriting_validation.py`. |
| **Thiết kế bộ phiếu thu thập mẫu (P01–P04 Design)** | TV1 | **DESIGN COMPLETE / PILOT CANDIDATE** | Hoàn tất thiết kế hình học, fiducial markers, calibration bar, bounding boxes cho P01–P04 (`docs/collection_sheets/P01..P04/`). Chưa được phê duyệt cho đợt thu thập chính thức. |
| **Scan-Validation Pipeline & Bench Test** | TV1 | **IMPLEMENTED & VALIDATED IN AUTOMATED TESTS / PHYSICAL BENCH SCAN PENDING** | Gói pipeline hoàn chỉnh (`backend/scan_validator/`, CLI runner) tự động phát hiện fiducial, perspective rectification sang khổ chuẩn A4 600 DPI, kiểm tra dung sai thước đo 50mm và ô vuông 20x20mm, tự động cắt ảnh theo tọa độ tất định và kiểm định QC tràn viền đã hoàn thiện (11/11 tests pass trong `tests/test_scan_validation_pipeline.py`); chờ bench-test trên bản in/quét thực tế khi có máy in laser/máy quét phẳng quang học. |
| **Phân tích độ phủ & Quyết định Protocol** | TV1 | **PENDING** | Chờ kiểm chứng ma trận độ phủ thực tế và chốt phương án xử lý lỗi nét lem/tràn viền (`PENDING PROTOCOL DECISION`). |
| **Thu thập thử nghiệm quy mô nhỏ (Pilot 3–5 writers)** | TV1 | **PENDING** | Chờ hoàn tất scan-validation pipeline và protocol chốt; chưa triển khai pilot. |
| **Thu thập chính thức (~40 writers)** | TV1 | **NOT STARTED** | Kế hoạch dự kiến ~40 người viết (28 Train, 6 Val, 6 Test); chưa triển khai. |
| **Đưa dấu tiếng Việt & Vùng cấm va chạm vào DAG (CA-VHC)** | TV4 & TV2 | **STEP B APPROVED AND CLOSED / STEP C AUTHORIZED — NOT YET IMPLEMENTED** | Step A complete; TV2 cross-review completed/pass; READY FOR STEP C: YES; PR1 đang được khởi động; formal experiment readiness vẫn NO. |
| **Tối ưu hóa thứ tự nét trễ (Delayed Strokes)** | TV2 & TV4 | **DESIGN POLICY RESOLVED / PRODUCTION IMPLEMENTATION NOT STARTED** | Khóa chính sách thiết kế P0 (gom nét trễ sau thân từ + Nearest Neighbor có tie-break bằng stroke index gốc); PR4 trong Step C chưa triển khai; P1 Exact Enumeration và P2 Writer Profile thuộc nghiên cứu tiếp nối. |
| **Tập ngữ liệu Benchmark tiếng Việt (Corpus)** | TV1 | **APPROVED AND FROZEN (CA-VHC-CORPUS-v1.0)** | TV1 hoàn tất phân tích độ phủ ngữ âm/ngôn ngữ học và chính thức đóng băng phiên bản `CA-VHC-CORPUS-v1.0-FROZEN` tại [`docs/19_benchmark_corpus_freeze_report.md`](19_benchmark_corpus_freeze_report.md); 20 từ DEV và 20 từ Holdout bảo đảm tính rời nhau tuyệt đối ($DEV \cap HOLDOUT = \emptyset$) và được bảo vệ bằng rào chắn chống rò rỉ dữ liệu. |
| **Framework ghi log thực nghiệm CSV & Runner** | TV4 | **INTERNAL EVALUATOR AND STRUCTURED TRACE IMPLEMENTED AND TESTED / EXPERIMENT PIPELINE–CSV INTEGRATION AND AUTOMATED RUNNER IN PROGRESS / PUBLIC API EXPOSURE PENDING** | Bộ đánh giá nội bộ `metrics_evaluator.py` và structured render trace đã hoạt động và có test; PR1 đang tích hợp các metric thực sự đã tồn tại vào experiment pipeline và CSV; public API chỉ mở rộng sau khi backend metric ổn định; API Spec sẽ được cập nhật bằng PR tài liệu riêng; không thay đổi API contract trong đợt này. |
| **Schema Annotation CA-VHC** | TV1 & TV4 | **PROPOSED / NON-BINDING** | Schema mẫu đề xuất trong mục 7 tài liệu này, chưa binding vào core engine. |
| **Schema Writer Profile cá nhân hóa** | TV1 | **PROPOSED / P2 RESEARCH** | Thuộc nhánh nghiên cứu mở rộng P2, chưa tích hợp vào engine lõi. |
| **Bộ trích xuất đặc trưng Writer Profile độc lập** | TV1 | **PROPOSED / P2 RESEARCH** | Đang chuẩn bị kịch bản trích xuất 4 đặc trưng hình học độc lập. |
| **Kiểm chứng thực nghiệm trên máy vẽ AxiDraw** | TV3 | **BLOCKED BY HARDWARE** | Chờ thiết lập phần cứng vật lý; hiện đang sử dụng mô phỏng phần mềm. |

---

*Tài liệu này là căn cứ pháp lý và kỹ thuật cao nhất về dữ liệu chữ viết tay trong dự án OmniDraw. Mọi thành viên tham gia thu thập, xử lý hoặc khai thác dữ liệu có trách nhiệm tuân thủ nghiêm ngặt các quy định nêu trên.*
