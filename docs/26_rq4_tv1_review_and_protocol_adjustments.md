# Báo cáo Đánh giá Protocol RQ4 và Kiến nghị Điều chỉnh Kỹ thuật Trước khi Tích hợp Writer Profile

**Tài liệu:** `docs/26_rq4_tv1_review_and_protocol_adjustments.md`<br>
**Ngày lập:** 29/09/2026 · **Trạng thái:** `SUBMITTED_FOR_TV4_REVIEW`<br>
**Người gửi:** TV1 — AI Data & Writer Profile Lead<br>
**Người nhận:** TV4 — Project Lead & Integration Lead<br>
**Tham chiếu kỹ thuật:**
- `docs/22_nckh_extended_scope.md` (Phạm vi nghiên cứu mở rộng P0–P3)
- `docs/23_rq4_writer_habit_study_protocol.md` (Protocol nghiên cứu thói quen viết cá nhân RQ4)
- `docs/25_rq4_consent_and_anonymization_protocol.md` (Quy chuẩn Consent, Ẩn danh hóa & Provenance)
- `tests/test_profile_generator_edge_cases.py` (Kiểm thử thực nghiệm bẫy lỗi tách dấu & dính chữ)

---

## 1. Đánh giá Tổng thể Protocol RQ4 (Docs 23)

TV1 hoàn toàn tán thành và đánh giá cao tính chuẩn mực, chặt chẽ trong thiết kế nghiên cứu của TV4 tại [`docs/23_rq4_writer_habit_study_protocol.md`](23_rq4_writer_habit_study_protocol.md). Cụ thể:

### 1.1. Các Điểm Mạnh Cốt Lõi
1. **Phân định Ranh giới Nhiệm vụ Minh bạch:** Định vị rõ RQ4 thuộc nhóm ưu tiên **P2 (Nghiên cứu mở rộng có điều kiện)**, tuyệt đối không làm ảnh hưởng đến tiến độ khóa nhánh lõi P0 (RQ1–RQ3 / CA-VHC / PR3).
2. **Kiểm soát Triệt để Rò rỉ Dữ liệu (No Data Leakage):** Thiết lập nguyên tắc chia tập kép (**Writer-disjoint** và **Text-disjoint**); bảo đảm tập từ/câu dùng để trích xuất profile và tập văn bản đánh giá hoàn toàn độc lập; cô lập hoàn toàn khỏi 20 DEV / 20 HOLDOUT của CA-VHC Corpus v1.0 đã đóng băng.
3. **Thiết kế Đối chứng Ba Nhánh Công bằng:** Phân biệt rõ **B0** (Font mặc định), **B1** (Ánh xạ quy tắc cố định - Rule-based) và **P** (Mô hình học phong cách). Tránh việc ngộ nhận việc map tham số hình học cố định là "AI đã học được phong cách".
4. **Đạo đức & Quyền riêng tư:** Đồng thuận với chủ trương không đưa ảnh chữ viết thật và dữ liệu cá nhân lên Git; sử dụng mã ẩn danh `writer_id`.

### 1.2. Khoảng trống Kỹ thuật Cần Bổ sung từ Góc độ Xử lý Dữ liệu Ảnh
Qua rà soát mã nguồn `profile_generator.py` đối chiếu với thực tế ảnh quét tĩnh, TV1 nhận diện một rủi ro kỹ thuật lớn: **Phương pháp phân đoạn ảnh dựa trên thành phần liên thông (Connected Components) gặp hiện tượng sai lệch nghiêm trọng trên chữ viết tay tiếng Việt**.

---

## 2. Kết quả Thực nghiệm: Bẫy Lỗi Tách Dấu & Chữ Viết Thảo Dính Nét

TV1 đã thiết lập bộ kiểm thử thực nghiệm chuyên sâu tại [`tests/test_profile_generator_edge_cases.py`](../tests/test_profile_generator_edge_cases.py) nhằm định lượng chính xác sai số khi bóc tách ảnh chữ viết tay:

### 2.1. Hiện tượng 1: Dấu Tách Rời (Detached Diacritics Anomaly)
- **Cơ chế phát sinh:** Trong chữ tiếng Việt, hầu hết dấu phụ (sắc, huyền, hỏi, ngã, nặng, mũ, trăng, râu) đều không dính mực vào thân chữ cơ sở.
- **Dữ liệu thực nghiệm:** Thử nghiệm trên chữ `ế` chuẩn 600 DPI:
  - `cv2.connectedComponentsWithStats` bóc tách thành **3 bounding boxes độc lập** (thân chữ 'e', dấu mũ '^', dấu sắc '/').
  - Hộp dấu sắc có kích thước $W \times H \approx 1.5 \times 1.7\,\text{mm}$; hộp dấu mũ $3.0 \times 1.5\,\text{mm}$.
- **Hệ quả sai số:**
  1. *Sai lệch Tỷ lệ Khung chữ:* Nếu coi mỗi box là một ký tự, tỷ lệ khung chữ $W/H$ bị phân mảnh thành các giá trị dị thường ($1.5/1.7 \approx 0.88$ và $3.0/1.5 = 2.0$), làm sai lệch `aspect_ratio_mean`.
  2. *Nhiễu Nhân tạo Baseline Jitter:* Đáy của dấu sắc ($y=4.2\,\text{mm}$) và dấu mũ ($y=6.5\,\text{mm}$) nằm cao hơn nhiều so với đường chân dòng thực sự ($y=11.5\,\text{mm}$). Nếu thuật toán ngây thơ lấy đáy của mọi box làm điểm chân dòng, `baseline_jitter_std` bị thổi phồng từ **$0.0\,\text{mm}$ lên $2.88\,\text{mm}$** (sai lệch nhân tạo gấp nhiều lần độ rung thực tế của người viết).

### 2.2. Hiện tượng 2: Chữ Viết Thảo Dính Nét (Touching Cursive Ligatures)
- **Cơ chế phát sinh:** Ở các biểu mẫu P02 (từ ngữ cảnh) và P03 (câu liên tục), người viết thường nối nét liên tục giữa các con chữ mà không nhấc bút (ví dụ: chữ `nam`, `tiến`).
- **Dữ liệu thực nghiệm:** Thử nghiệm trên từ viết thảo liền nét 3 chữ:
  - `connectedComponentsWithStats` chỉ nhận diện được **đúng 1 bounding box duy nhất** bao trọn toàn bộ từ.
- **Hệ quả sai số:**
  - Không thể trích xuất được khoảng cách giữa các ký tự trong từ (`char_spacing`). Hàm buộc phải rơi về giá trị fallback mặc định ($0.25$).

### 2.3. Khảo sát Hình học của Trang P01 (Isolated Character Cells) trên Ảnh Giả lập
- **Thực nghiệm xác nhận:** Trang P01 gồm **24 ô định chuẩn** (lưới 4 × 6 theo Docs 20 Section 3.1). Vì mỗi ô viết chỉ chứa duy nhất 1 ký tự đích đã biết trước (known isolated character ground truth), toàn bộ nét trong ô được gom thành 1 tổ hợp ký tự (`char_stroke_groups`).
- **Kết quả trên test giả lập:**
  - Tỷ lệ khung chữ của tổ hợp `ế` đo được xấp xỉ $0.78$ (nằm trong khoảng hình học học sinh $0.4..1.2$).
  - Điểm đáy chân dòng lấy $\max(y)$ của toàn bộ nét $\rightarrow$ tự động bắt đúng đáy thân chữ 'e', tránh được việc dấu tách rời phía trên làm méo chân dòng, giữ `baseline_jitter_std` đúng bằng $0.0\,\text{mm}$ trong ca thử nghiệm này.
- **Giới hạn cần lưu ý:** Kết quả này phản ánh điều kiện lý tưởng của ảnh nhân tạo. Trên ảnh quét chữ viết thật, nếu người viết viết tràn qua biên ô, đè lên đường kẻ quang học xám hoặc mực bị đứt gãy, việc phân đoạn ô vẫn có thể gặp sai số và bắt buộc phải qua bước rà soát QC bằng mắt (manual verification).

---

### 2.4. Hiện tượng 3: Sai số Chân dòng trên Từ Ngữ cảnh P02 Có Dấu (Contextual Word Diacritic Distortion)
- **Cơ chế phát sinh:** Ở biểu mẫu P02 (từ ngữ cảnh), một từ tiếng Việt có dấu (ví dụ: chữ `tê`) chứa cả thân chữ cơ sở và dấu phụ tách rời phía trên. Khi bóc tách bằng connected components, thuật toán nhận diện được cả thân chữ 't', 'e' và dấu mũ '^'.
- **Dữ liệu thực nghiệm (Thực nghiệm 5):** Thử nghiệm trên từ `tê` giả lập với baseline chuẩn phẳng tại $y = 11.0\,\text{mm}$:
  - Đáy của dấu mũ nằm tại $y = 6.5\,\text{mm}$.
  - Nếu thuật toán lấy đáy của toàn bộ các bounding boxes làm điểm chân dòng, `baseline_jitter_std` bị thổi phồng nhân tạo lên **$> 1.5\,\text{mm}$** dù chữ viết của người viết hoàn toàn phẳng.
  - **Kiểm chứng giải pháp:** Khi áp dụng bộ lọc loại bỏ các thành phần nằm ở nửa trên dòng ($y_{\text{bottom}} < 8.0\,\text{mm}$), chỉ còn 2 hộp thân chữ 't' và 'e' tham gia tính toán, đưa `baseline_jitter_std` trở về mức phẳng chuẩn **$< 0.1\,\text{mm}$**.

### 2.5. Năng lực Chống Nhiễu Quang học & Đứt Nét (Optical Noise & Stroke Resilience)
- **Thực nghiệm 6:** Kiểm chứng khả năng lọc nhiễu của `profile_generator.py` đối với các chấm bụi quang học hoặc xơ giấy quét nhỏ ($1\text{--}2\,\text{px}$):
  - Phép biến đổi hình thái học `cv2.morphologyEx(..., cv2.MORPH_OPEN)` kết hợp ngưỡng chu vi tối thiểu `min_perimeter_px=10.0` đã loại bỏ hoàn toàn các chấm nhiễu đơn lẻ, bảo toàn chính xác nét chữ hợp lệ.
  - Khẳng định: Việc quét ở độ phân giải cao $600\,\text{DPI}$ với độ tương phản tốt là điều kiện tiên quyết để tránh đứt gãy nét thành các mảnh vụn nhỏ bị bộ lọc ngộ nhận là nhiễu.

---

## 3. Bốn Đề xuất Kỹ thuật Sơ bộ (Preliminary Proposals) từ TV1 Gửi TV4 Thảo luận

Để đóng góp cho việc hoàn thiện protocol RQ4 và chuẩn bị dữ liệu cho TV4, TV1 nêu 4 đề xuất kỹ thuật sơ bộ dưới đây để nhóm cùng thảo luận (các bộ lọc và ngưỡng tham số **chưa khóa cứng**, sẽ được thử nghiệm và tinh chỉnh khi có dữ liệu pilot thực tế):

### Đề xuất 1: Thử nghiệm Chính sách Trích xuất Đặc trưng Phân tầng (2-Stage Profile Extraction Proposal)
Đề xuất phân tách nguồn trích xuất cho từng nhóm đặc trưng theo tính chất hình học của mẫu:
- **Tầng 1 — Đặc trưng Cấu trúc Ký tự (Từ 24 ô định chuẩn P01):**
  - Các chỉ số: `mean_slant_deg` (độ nghiêng), `aspect_ratio_mean` (tỷ lệ khung), `stroke_width_mean_mm` (bề rộng nét), và `diacritic_tendencies` (độ lệch mỏ neo dấu) trích xuất từ 24 ô ký tự rời P01.
  - *Lý do đề xuất:* P01 có nhãn ký tự đích đã biết trước theo từng ô, giảm thiểu tối đa hiện tượng tách dấu thành ký tự độc lập so với việc bóc tách tự do trên dòng chữ.
- **Tầng 2 — Đặc trưng Dòng chảy & Khoảng cách (Từ P02, P03, P04):**
  - Các chỉ số: `word_spacing_mean_ratio` (khoảng cách từ), `line_spacing_mean_ratio` (khoảng cách dòng), và `baseline_jitter_std` (dao động chân dòng) được khảo sát từ P03 (câu) và P04 (đoạn văn).
  - Khuyến nghị nghiên cứu bổ sung **phép chiếu ngang (horizontal projection profile)** và hồi quy tuyến tính dòng kẻ để tìm trục baseline thực tế, thay vì phụ thuộc hoàn toàn vào tọa độ đáy của từng connected component đơn lẻ.

### Đề xuất 2: Nghiên cứu Bộ Lọc Dấu khi Ước lượng Baseline trên Dòng Chữ
Trong module `profile_generator.py`, khi xử lý ảnh từ hoặc dòng chữ có chứa nhiều connected components:
- Đề xuất thử nghiệm ngưỡng lọc tọa độ Y: Chỉ những component có tọa độ tâm nằm ở nửa dưới của dòng chữ ($y_{\text{center}} > y_{\text{line\_median}}$) mới được xem xét làm ứng viên điểm chân dòng (`baseline_points`).
- Cần kiểm chứng giải pháp này trên mẫu thật có gán nhãn trước khi chốt thành quy tắc chính thức, nhằm tránh lọc nhầm các chữ có đuôi descender (như 'g', 'y', 'p').

### Đề xuất 3: Khung Gợi ý Tham số Giữa Profile và Engine (Contract Discussion)
TV1 đề xuất TV4 cân nhắc danh mục tham số engine mà `WriterProfile` có thể tác động khi render văn bản mới:
1. `global_style.mean_slant_deg` $\rightarrow$ Áp dụng vào góc xoay ma trận ngòi bút (ví dụ kẹp trong biên an toàn $[-20^\circ, +20^\circ]$).
2. `global_style.aspect_ratio_mean` $\rightarrow$ Scale hệ số co giãn ngang $s_x$ của glyph (ví dụ kẹp trong $[0.85, 1.15]$).
3. `spacing.char_spacing_mean_ratio` $\rightarrow$ Điều chỉnh bước dịch ngòi bút $dx_{\text{advance}}$ giữa các ký tự.
4. `spacing.word_spacing_mean_ratio` $\rightarrow$ Điều chỉnh khoảng cách phím cách (space width).
5. `diacritic_tendencies.diacritic_offset_bias` $\rightarrow$ Bổ sung bias $[\Delta x, \Delta y]$ vào mỏ neo dấu gốc, **nhưng bắt buộc phải tuân thủ bộ kiểm tra va chạm clearance $\ge 0.20\,\text{mm}$ của TV4**; nếu vi phạm va chạm thì hủy bỏ bias cá nhân hóa để ưu tiên tính đúng đắn của chữ Việt.
*(Các ngưỡng trên là gợi ý biên kỹ thuật từ phía dữ liệu, TV4 toàn quyền quyết định contract tích hợp vào engine).*

### Đề xuất 4: Nhất quán Tuyên bố Khoa học Trung thực (Faithful Claims)
- Nhất quán với khuyến cáo của TV4: Toàn bộ kết quả kiểm thử trên dữ liệu giả lập (13 tests hiện có + 4 tests edge cases mới) **chỉ có giá trị kiểm chứng kỹ thuật phần mềm (software verification)**, tuyệt đối không được dùng để khẳng định "AI đã cá nhân hóa thành công phong cách người viết".
- Đợt Pilot 3–5 người viết **chỉ nhằm kiểm tra tính khả thi kỹ thuật (feasibility check)** của quy trình in, viết, quét 600 DPI, và pipeline bóc tách, tuyệt đối **không dùng để kết luận về năng lực tổng quát hóa hay hiệu quả của việc học phong cách cá nhân hóa**.
- Kết luận khoa học về RQ4 chỉ được đưa ra sau khi hoàn tất nghiên cứu quy mô đủ lớn với bản in/quét 600 DPI, đánh giá mù hoán vị B0/B1/P và kiểm định độ đồng thuận giữa những người chấm theo đúng rubric của Doc 23.

---

## 4. Kế hoạch Hành động Triển khai Pilot Khả thi P01–P04 (3–5 Người viết)

Để sẵn sàng dữ liệu ngay khi thiết bị máy in và máy quét 600 DPI có mặt tại lab, TV1 chuẩn bị kế hoạch kiểm tra khả thi:

| Bước | Nội dung công việc | Đầu ra kỹ thuật | Trách nhiệm |
| :--- | :--- | :--- | :--- |
| **B1** | Chuẩn bị bản in tiêu chuẩn P01–P04 (giấy A4 $80\,\text{g/m}^2$, mực xám $10\%$, 4 góc fiducial) | 5 bộ phiếu in định chuẩn P01–P04 | TV1 |
| **B2** | Trình duyệt mẫu Consent (Doc 25) với TV4 và Đơn vị phụ trách trước khi tuyển tình nguyện viên | Mẫu Consent đã được phê duyệt | TV1 + TV4 |
| **B3** | Hướng dẫn viết mẫu bằng bút gel $0.5\,\text{mm}$ chuẩn, không dùng bút xóa, giữ nhịp tự nhiên | 5 bộ phiếu đã hoàn thành nét viết | TV1 + Tình nguyện viên |
| **B4** | Quét phẳng quang học 600 DPI (True Color RGB, lossless PNG, không auto-filter) | 20 tệp ảnh quét gốc `W001_S01_P01.png`... | TV1 |
| **B5** | Chạy Scan-Validation Pipeline (affine deskew, kiểm định thước, bóc tách ô mẫu, lập manifest) | `collection_manifest.jsonl` hợp lệ schema | TV1 |
| **B6** | Chạy `profile_generator.py` thử nghiệm, ghi nhận nhật ký lỗi tách dấu/dính nét thực tế | Báo cáo feasibility & các ca thất bại | TV1 |

---

## 5. Kết luận & Đề xuất Bước tiếp theo

1. TV1 đã đồng bộ toàn bộ tài liệu từ `f5445ef`, khóa an toàn `.gitignore` chống rò rỉ dữ liệu thật, soạn thảo quy chuẩn Consent & Mã hóa định danh ([`docs/25`](25_rq4_consent_and_anonymization_protocol.md) ở trạng thái chờ duyệt), và lập trình bộ kiểm thử thực nghiệm bẫy lỗi tách dấu/dính chữ ([`tests/test_profile_generator_edge_cases.py`](../tests/test_profile_generator_edge_cases.py)).
2. Kính chuyển bản báo cáo này đến **TV4** để cùng thảo luận và thống nhất các đề xuất kỹ thuật trước khi bắt đầu tích hợp Writer Profile vào engine. Chờ phê duyệt biểu mẫu Consent trước khi tiến hành Pilot.
