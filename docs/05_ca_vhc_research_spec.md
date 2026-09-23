# OmniDraw — Đặc Tả Nghiên Cứu & Thiết Kế Kỹ Thuật Lõi CA-VHC
*(Phiên bản Đồng bộ Toàn diện Tài liệu Dự án & TV2 Cross-Review)*

**Tài liệu:** Khung thuật toán Context-Aware Vietnamese Handwriting Composition (CA-VHC)
**Tác giả / Lead phần chuyển động:** Thành viên 2 — Stroke Optimization & Path Planning Lead; owner phần motion/DP của CA-VHC
**Chủ trì đề tài & Handwriting:** Thành viên 4 — Project Lead & Handwriting / CA-VHC Composition Lead
**Phối hợp dữ liệu & Phần cứng:** Thành viên 1 (Data/Corpus) & Thành viên 3 (Hardware/Validation)
**Cập nhật lần cuối:** 21/09/2026 (Đồng bộ theo Roadmap, Current Task, Tech Stack & Dataset Spec)
**Trạng thái:** STEP B: APPROVED AND CLOSED | TV2 CROSS-REVIEW: COMPLETED / PASS | READY FOR STEP C: YES | STEP C: AUTHORIZED — NOT YET IMPLEMENTED

---

## Giới thiệu & Phân định quyền sở hữu (Module Ownership Matrix)

Tài liệu này xác lập cơ sở lý thuyết, mô hình toán học hình thức, thiết kế thuật toán tối thiểu và kế hoạch thực nghiệm cho **Context-Aware Vietnamese Handwriting Composition (CA-VHC)** trên máy vẽ 2 trục (pen plotter).

Để bảo đảm tính phân tách trách nhiệm rõ ràng (Separation of Concerns) và tuân thủ chặt chẽ kiến trúc đã được đồng thuận trong hệ thống tài liệu quản lý dự án (`01_tech-stack.md`, `02_roadmap.md`, `03_current-task.md`, `07_diacritic_aware_state_design.md` và `08_handwriting_dataset_spec.md`), quyền sở hữu module và ranh giới kỹ thuật giữa 4 thành viên được xác lập như sau:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          MA TRẬN PHÂN CÔNG QUYỀN SỞ HỮU (4 THÀNH VIÊN)                 │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ THÀNH VIÊN               │ MODULE SỞ HỮU CHÍNH         │ ĐẦU RA / PHẠM VI TRÁCH NHIỆM  │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ TV1 — AI Data & Writer   │ Dataset, benchmark corpus,  │ - Benchmark corpus (Dev/Hold) │
│ Profile Lead             │ synthetic fixtures & data   │ - Fixtures & annotation       │
│                          │ protocol (file 08 spec)     │ - Schema WriterProfile (P2)   │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ TV2 — Stroke Optimization│ Mô hình chuyển động,        │ - Motion cost ($D_{penup},     │
│ & Path Planning Lead     │ transition cost, Trellis DP │    N_{lift}, C_{curvature}$)  │
│ (Owner motion/DP CA-VHC) │ sequence decoder, path plan │ - Thuật toán Viterbi DP search│
│                          │                             │ - Benchmark động học/quãng đg │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ TV3 — Hardware, Calib &  │ Hardware adapter, AxiDraw,  │ - Interface máy thật/simulator│
│ Physical Validation Lead │ simulator, hiệu chuẩn máy,  │ - Log thời gian vẽ thực tế    │
│                          │ đo đạc thực tế              │ - Sai số tọa độ & rung giật   │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ TV4 — Project Lead &     │ Tiền xử lý NFD, typography, │ - Cấu trúc `CompositionState` │
│ Handwriting / CA-VHC     │ diacritic anchors/offsets,  │ - Pipeline sinh ứng viên dấu  │
│ Composition Lead         │ font/state model, runner,   │ - $C_{internal\_collision}$   │
│                          │ CSV logging, API Gateway,   │ - Runner & CSV experiment log │
│                          │ Frontend React              │                               │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ GIAO DIỆN CHUNG (SHARED) │ Tích hợp CA-VHC             │ - `eval_transition(s_p, s_c)` │
│ (TV4 + TV2)              │                             │ - `bridge_collision_cost`     │
│                          │                             │ - `optimize_word_dag` runner  │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

### Chi tiết phân công trách nhiệm:

1. **Thành viên 1 (AI Data & Writer Profile Lead):**
   - Xây dựng và quản lý toàn bộ tập ngữ liệu đối chuẩn: Development Corpus và Holdout Corpus (`08_handwriting_dataset_spec.md`);
   - Chuẩn bị synthetic data fixtures phục vụ kiểm thử đơn vị và runner thực nghiệm của TV4;
   - Quản lý quy chuẩn thu thập, gán nhãn và ẩn danh hóa dữ liệu người viết cho giai đoạn P2;
   - *Lưu ý:* TV1 là owner và provider độc quyền của dữ liệu benchmark và fixtures; TV2 và TV4 không sở hữu tập dữ liệu mẫu này.

2. **Thành viên 2 (Stroke Optimization & Path Planning Lead — Owner phần motion/DP của CA-VHC):**
   - Xây dựng mô hình chuyển động của đầu bút vẽ (pen kinematics: penup distance, lift count, curvature continuity, stroke direction transition);
   - Chuẩn hóa các thành phần chi phí chuyển động trong hàm mục tiêu: $D_{\text{penup}}, N_{\text{lift}}, C_{\text{curvature}}$;
   - Đánh giá tính khả thi chuyển tiếp và va chạm đường nối liên ký tự ($C_{\text{bridge\_collision}}$) trong không gian tọa độ thế giới (world coordinates);
   - Chủ trì thuật toán quy hoạch động Trellis Viterbi DP sequence decoder và quy hoạch đường đi (path optimization);
   - Thực hiện benchmark định lượng về năng lượng, quãng đường di chuyển bút và chi phí động học.

3. **Thành viên 3 (Hardware, Calibration & Physical Validation Lead):**
   - Xây dựng lớp giao tiếp phần cứng chung (`HardwareAdapterInterface`) kết nối máy vẽ AxiDraw thực tế và bộ giả lập simulator;
   - Hiệu chuẩn tham số vật lý: tốc độ, gia tốc, độ nảy ngòi bút, độ trễ nhấc/hạ bút trục Z;
   - Đo đạc các chỉ số thi công thực tế trên máy vẽ thật (`actual_draw_time_sec`), phân biệt với thời gian mô phỏng phần mềm;
   - Phối hợp với TV4 kiểm thử UI trạng thái phần cứng và kiểm thử trực quan.

4. **Thành viên 4 (Project Lead & Handwriting / CA-VHC Composition Lead):**
   - Tiền xử lý chuỗi tiếng Việt, chuẩn hóa phân rã Unicode NFD;
   - Cấu trúc ký tự tổ hợp (composite character structure);
   - Mô hình định vị dấu thanh/mũ/móc (diacritic positioning model, anchor points, clearance zones);
   - Sinh ứng viên biến thể thân chữ và cấu hình dấu (glyph/diacritic candidate generation);
   - Quản lý font pack, variant pool và giải quyết va chạm nội ký tự ($C_{\text{internal\_collision}}$);
   - Đóng gói trạng thái tổ hợp `CompositionState = (base_variant, diacritic_candidate)`;
   - Phát triển Frontend React, API Gateway, xây dựng experiment runner, chuẩn hóa hệ thống CSV logging, điều phối tích hợp toàn hệ thống và tổng hợp Báo cáo NCKH 5 chương.

5. **Giao diện tích hợp chung (Shared Interface — TV4 + TV2):**
   - Cấu trúc dữ liệu trung tâm `CompositionState` (`backend/handwriting/state.py` — module dự kiến triển khai ở Bước C);
   - Hàm đánh giá chuyển tiếp `eval_transition(s_prev, s_next)`;
   - Logic kiểm tra va chạm cầu nối liên ký tự `bridge_collision_cost`;
   - Bộ giải Viterbi Trellis runner `optimize_word_dag(states_per_char)`.

> [!IMPORTANT]
> **Nguyên tắc trung thực học thuật & Code-first:**
> - Mọi viện dẫn mã nguồn trong tài liệu này lấy **tên file và tên hàm/lớp làm nguồn định danh chính** (line number chỉ là thông tin tham khảo phụ).
> - Tài liệu phân biệt rõ ràng giữa **Mục tiêu thiết kế (Design Target)**, **Tiêu chí nghiệm thu kỳ vọng (Acceptance Criteria)** và **Kết quả đo lường thực nghiệm (Measured Result)**; tuyệt đối không khẳng định "real-time guaranteed" hoặc "instant execution" khi chưa có số liệu đo đạc thực tế trên phần cứng.
> - Engine hoàn toàn **không** nhận là hiểu ngữ nghĩa (semantics) hay ngữ âm học (phonetics/phonology); mọi cơ chế xử lý dấu tiếng Việt đều dựa trên **quy tắc chính tả hình học (orthographic geometry)** và chuẩn phân rã Unicode NFD.

---

## 1. Ba Câu Hỏi Nghiên Cứu & Giả Thuyết Khoa Học

Khung nghiên cứu của CA-VHC tập trung giải quyết ba câu hỏi nghiên cứu (Research Questions — RQ) độc lập nhưng bổ trợ chặt chẽ cho nhau:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 KHUNG NGHIÊN CỨU CA-VHC                                │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ RQ1: Nối nét & Động học  │ RQ2: Tránh va chạm dấu      │ RQ3: Hiệu năng & Khả thi      │
│  - Giảm pen-up distance  │  - Clearance envelope dấu   │  - Độ phức tạp Viterbi DP     │
│  - Giảm pen-lift count   │  - Giảm thiểu va chạm cầu   │  - Thiết kế hướng C1 junction │
│  - Kiểm soát độ dài nét  │  - Tách va chạm nội/cầu nối │  - Target latency vs máy thật │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

### Nguyên tắc phân loại đánh giá kết quả (Evaluation Priority Rule)
Mọi giả thuyết kiểm chứng trong tài liệu này đều được phân loại nghiêm ngặt vào 3 vùng **loại trừ lẫn nhau (mutually exclusive và collectively exhaustive)** theo đúng thứ tự ưu tiên:
1. **FAIL:** Nếu **bất kỳ điều kiện hard-fail nào** đúng.
2. **PASS:** Nếu **TẤT CẢ các điều kiện pass** đều đồng thời thỏa mãn.
3. **INCONCLUSIVE:** Cho **mọi trường hợp còn lại** (khi kết quả không vi phạm bất kỳ điều kiện FAIL nào nhưng chưa thỏa mãn đồng thời toàn bộ điều kiện PASS; cần mở rộng mẫu hoặc hiệu chỉnh tham số).

---

### 1.1. RQ1: Nối Nét, Quãng Đường Pen-up và Số Lần Nhấc Bút

- **Câu hỏi nghiên cứu (RQ1):**
  *Việc áp dụng giải thuật quy hoạch động Trellis DAG (Viterbi DP) trên không gian trạng thái tổ hợp `CompositionState` để đồng thời lựa chọn biến thể glyph và vị trí dấu theo ngữ cảnh có thể giảm đáng kể quãng đường di chuyển pen-up ($D_{\text{penup}}$) và số lần nhấc bút ($N_{\text{lift}}$) so với phương pháp render tĩnh (B1), heuristic nối nét tham lam (B2) và Trellis hiện tại chưa có ràng buộc dấu nâng cao (B3) hay không, trong khi vẫn duy trì tổng chiều dài nét vẽ tiếp xúc giấy ở mức tương đương?*

- **Giả thuyết H1.1 (Giảm quãng đường pen-up):**
  Gọi $\Delta D_{\text{B1}} = \frac{D_{\text{penup}}(\text{B1}) - D_{\text{penup}}(\text{CA-VHC})}{D_{\text{penup}}(\text{B1})}$ và $\Delta D_{\text{B2}} = \frac{D_{\text{penup}}(\text{B2}) - D_{\text{penup}}(\text{CA-VHC})}{D_{\text{penup}}(\text{B2})}$.
  - **FAIL (Ưu tiên 1):** $(\Delta D_{\text{B1}} < 15.0\%)$ **HOẶC** $(\Delta D_{\text{B2}} < 5.0\%)$.
  - **PASS (Ưu tiên 2):** $(\Delta D_{\text{B1}} \ge 25.0\%)$ **VÀ** $(\Delta D_{\text{B2}} \ge 10.0\%)$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại.

- **Giả thuyết H1.2 (Giảm số lần nhấc bút):**
  Trên cùng tập ca benchmark $\mathcal C$ gồm các cấu hình văn bản × font × seed được ghép cặp giữa hai phương pháp và hỗ trợ nối nét, gọi $\Delta N_{\text{lift}} = \frac{\sum_{x\in\mathcal C}N_{\text{lift}}(\text{B1},x) - \sum_{x\in\mathcal C}N_{\text{lift}}(\text{CA-VHC},x)}{\sum_{x\in\mathcal C}N_{\text{lift}}(\text{B1},x)}$. Tỷ lệ này tính trên tổng tích lũy, không lấy trung vị tỷ lệ theo từng từ; mẫu số bằng 0 thì ghi `NOT_APPLICABLE`, không suy ra PASS.
  - **FAIL (Ưu tiên 1):** $\Delta N_{\text{lift}} < 20.0\%$.
  - **PASS (Ưu tiên 2):** $\Delta N_{\text{lift}} \ge 35.0\%$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại ($20.0\% \le \Delta N_{\text{lift}} < 35.0\%$).

- **Giả thuyết H1.3 (Kiểm soát chiều dài nét vẽ tiếp xúc giấy):**
  Gọi tỷ lệ tăng chiều dài nét vẽ là $\Delta L = \frac{total\_path\_length\_mm(\text{CA-VHC}) - total\_path\_length\_mm(\text{B1})}{total\_path\_length\_mm(\text{B1})}$.
  - **FAIL (Ưu tiên 1):** $\Delta L > 15.0\%$.
  - **PASS (Ưu tiên 2):** $\Delta L \le 10.0\%$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại ($10.0\% < \Delta L \le 15.0\%$).

---

### 1.2. RQ2: Tránh Va Chạm Giữa Dấu Tiếng Việt, Thân Chữ và Nét Nối

- **Câu hỏi nghiên cứu (RQ2):**
  *Cơ chế đồng tối ưu trạng thái tổ hợp `CompositionState` kết hợp vùng cản trở an toàn của dấu (`bridge diacritic obstacle avoidance`) vào hàm mục tiêu Trellis DAG có loại bỏ được các giao cắt hình học giữa cầu nối và dấu phụ/dấu thanh (mục tiêu thiết kế: $collision\_count = 0$), đồng thời duy trì khoảng cách an toàn tối thiểu giữa nét nối và tổ hợp dấu chồng tầng so với Trellis DAG hiện tại chưa có nhận thức dấu (B3) hay không?*

- **Giả thuyết H2.1 (Triệt tiêu va chạm hình học — Acceptance Criterion kỳ vọng):**
  - **FAIL (Ưu tiên 1):** Phát hiện $collision\_count \ge 1$ trên bất kỳ mẫu nghiệm thu nào.
  - **PASS (Ưu tiên 2):** Đạt $collision\_count = 0$ trên toàn bộ tập kiểm thử nghiệm thu chính thức.
  - **INCONCLUSIVE (Ưu tiên 3):** Không áp dụng (tiêu chuẩn nhị phân cứng).
  *(Lưu ý: $collision\_count = 0$ là acceptance target của giải thuật, không phải trạng thái đã đạt được ở hiện tại).*

- **Giả thuyết H2.2 (Khoảng cách an toàn tối thiểu với dấu):**
  Với cấu hình chuẩn $font\_size\_mm = 7.0\text{ mm}$, gọi $d_{\min} = minimum\_diacritic\_clearance\_mm$.
  - **FAIL (Ưu tiên 1):** $d_{\min} < 0.20\text{ mm}$ (xâm phạm vùng ngòi bút cơ sở $0.20\text{ mm}$).
  - **PASS (Ưu tiên 2):** $d_{\min} \ge 0.50\text{ mm}$ (đạt biên an toàn nghiên cứu mục tiêu).
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại ($0.20\text{ mm} \le d_{\min} < 0.50\text{ mm}$).
  > [!NOTE]
  > **Quy chuẩn ngưỡng an toàn:** $0.20\text{ mm}$ là giá trị khởi tạo mặc định kỹ thuật ban đầu trong `DiacriticConfig` để bảo toàn tương thích code hiện hành; $0.50\text{ mm}$ là mục tiêu an toàn nghiên cứu cần TV3 hiệu chuẩn thực nghiệm (calibration) trên máy vẽ vật lý ở Bước C. Chi tiết quy chuẩn và ma trận nghiệm thu trước PR3 được xác lập tại [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md).

---

### 1.3. RQ3: Hiệu Năng Tính Toán & Tính Khả Thi Thi Công Trên Máy Vẽ

- **Câu hỏi nghiên cứu (RQ3):**
  *Giải thuật CA-VHC trên không gian trạng thái $K_{\text{raw}} \le 9$ có duy trì được thời gian tính toán trong giới hạn tương tác người dùng và thiết kế hướng tới quỹ đạo vector đơn trị, trơn tiếp tuyến hình học $C^1$, tạo tiền đề khả thi để thi công an toàn trên máy vẽ 2 trục hay không?*

> [!NOTE]
> **Ranh giới tuyên bố khoa học về tính trơn tiếp tuyến $C^1$:**
> - Việc chuyển đổi spline Catmull–Rom sang Bézier chỉ bảo đảm tính trơn tiếp tuyến nội bộ bên trong từng phân đoạn đường cong đơn lẻ. Nó **KHÔNG tự động bảo đảm tính trơn tiếp tuyến $C^1$ tại mọi điểm nối tiếp giáp (junctions)** giữa thân chữ cái, cầu nối ligature và nét dấu.
> - Do đó, tính trơn tiếp tuyến $C^1$ được định vị là **Mục tiêu thiết kế (Design Target)**; chỉ số `c1_violation_count` bắt buộc phải được đo đạc và kiểm chứng tại các điểm tiếp giáp cụ thể.
> - Mọi hệ quả cơ lý tính thực tế (độ rung giật của đầu bút, hao mòn cơ khí, thời gian thi công thực tế) là giả thuyết ngoại suy và **bắt buộc phải được kiểm chứng, xác nhận bằng số liệu thực nghiệm phần cứng do TV3 đo đạc trên máy AxiDraw thật**.

- **Giả thuyết H3.1 (Thời gian tính toán giải thuật Viterbi DP — Design Target):**
  Thời gian giải quy hoạch động trên từng từ ($N \le 7$ ký tự) đo độc lập qua `time.perf_counter()`. Gọi $M = \text{Median}(optimize\_time\_ms)$ và $P = \text{p95}(optimize\_time\_ms)$.
  - **FAIL (Ưu tiên 1):** $(M > 15.0\text{ ms})$ **HOẶC** $(P > 30.0\text{ ms})$.
  - **PASS (Ưu tiên 2):** $(M \le 5.0\text{ ms})$ **VÀ** $(P \le 10.0\text{ ms})$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại.
  *(Lưu ý: Đây là Design Target, không tuyên bố "real-time guaranteed" khi chưa có benchmark đo lường chính thức).*

- **Giả thuyết H3.2 (Độ trơn hình học & Kiểm soát đổi hướng tiếp tuyến):**
  Gọi $\Delta C_{\text{curv}} = \frac{curvature\_cost(\text{B2}) - curvature\_cost(\text{CA-VHC})}{curvature\_cost(\text{B2})}$ và biến cố $has\_acute\_turn$ là sự xuất hiện của bất kỳ góc lệch tiếp tuyến nào $> 120^\circ$ trên cầu nối.
  `acute_turn_count_120deg`/`has_acute_turn` hiện **chưa được evaluator tính**; đây là diagnostic bắt buộc phải triển khai, định nghĩa và kiểm thử trước khi H3.2 có thể nhận verdict trong PR5.
  - **FAIL (Ưu tiên 1):** $(\Delta C_{\text{curv}} \le 0.0\%)$ **HOẶC** $(has\_acute\_turn == \text{True})$.
  - **PASS (Ưu tiên 2):** $(\Delta C_{\text{curv}} \ge 15.0\%)$ **VÀ** $(has\_acute\_turn == \text{False})$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại.

---

## 2. Mô Hình Toán Học Hình Thức

### 2.1. Không Gian Trạng Thái Tổ Hợp (`CompositionState`)

Xét một từ tiếng Việt gồm chuỗi $N$ ký tự liên tiếp: $\mathbf{C} = (c_1, c_2, \dots, c_N)$.

Tại mỗi vị trí $i \in \{1, \dots, N\}$, ký tự $c_i$ sau khi phân rã Unicode NFD gồm:
- Ký tự gốc (base character): $b_i \in \Sigma_{\text{base}}$ (ví dụ: `a`, `e`, `o`, `d`, `K`).
- Tập dấu đi kèm: $\mathcal{A}_i = \{a_{i,1}, a_{i,2}, \dots\}$ (ví dụ: nón `\u0302`, sắc `\u0301`, móc `\u031b`, hoặc $\emptyset$ nếu là ký tự không dấu).
- Thông số biến đổi hình học cục bộ: tỷ lệ phóng/thu $\mathbf{s}_i = [s_{x,i}, s_{y,i}]^T$, độ lệch tọa độ thế giới $\mathbf{o}_i = [x_i, y_i]^T$, chiều rộng ký tự $w_i$, và trọng tâm ngang $cx_i$.

Kiến trúc Bước B (`07_diacritic_aware_state_design.md`) định nghĩa mỗi nút trong đồ thị Trellis là một **Trạng thái tổ hợp (CompositionState)**:
$$s_{i, j} = \left( v_{\text{base}}, c_{\text{diacritic}} \right) \in \mathcal{S}_i$$

Trong đó:
- $v_{\text{base}} \in \mathcal{V}_{\text{base}, i}$ là biến thể thân chữ cái chọn từ tập ứng viên thân chữ ($K_{\text{base}} \le 3$, ví dụ: `std`, `alt`, `flourish`).
- $c_{\text{diacritic}} \in \mathcal{C}_{\text{diacritic}, i}$ là ứng viên định vị dấu chọn từ tập vị trí khả dĩ do TV4 sinh ra ($K_{\text{diacritic}} \le 3$, ví dụ: `canonical`, `safe_left`, `safe_right`). Đối với ký tự không mang dấu, $c_{\text{diacritic}} = \emptyset$ và $K_{\text{diacritic}} = 1$.

#### Cận trên không gian trạng thái lý thuyết (Theoretical Raw State Bound)
Số lượng trạng thái tổ hợp thô tại mỗi vị trí ký tự bị chặn trên bởi:
$$K_{\text{raw}, i} = |\mathcal{S}_i| = K_{\text{base}} \times K_{\text{diacritic}} \le 3 \times 3 = 9$$

> [!IMPORTANT]
> **Nguyên tắc không gian trạng thái & Kỷ luật cắt tỉa P0:**
> - Giá trị $K_{\text{raw}} \le 9$ là **Theoretical Raw State Bound** (Cận trên lý thuyết của không gian trạng thái thô), **KHÔNG PHẢI** là kết quả benchmark runtime và **KHÔNG PHẢI** là số lượng trạng thái bị cắt tỉa cứng.
> - Ở P0 / Bước C v1, hệ thống **KHÔNG sử dụng các kỹ thuật cắt tỉa phỏng đoán (heuristic pruning)** như top-6 cutoff, beam search hay early pruning.
> - Toàn bộ tối đa 9 trạng thái tổ hợp hợp lệ đều được đưa vào giải thuật Viterbi. Các trạng thái chỉ bị loại bỏ nếu vi phạm **ràng buộc cứng (hard constraints)**: va chạm nội ký tự nghiêm trọng, vượt biên trần dòng chữ hoặc dữ liệu hình học suy biến (NaN/Inf).

Mỗi trạng thái tổ hợp $s_{i, j} \in \mathcal{S}_i$ tương ứng với cấu trúc dữ liệu `CompositionState` (`backend/handwriting/state.py` — module dự kiến triển khai ở Bước C) và được đặc trưng bởi:
$$s_{i, j} = \left( \mathcal{S}_{\text{local}}, \mathbf{p}_{\text{in}}, \mathbf{p}_{\text{out}}, \mathbf{v}_{\text{in}}, \mathbf{v}_{\text{out}}, \text{can\_in}, \text{can\_out}, \text{bbox}_{\text{local}}, c_{\text{leg}}, c_{\text{place}}, c_{\text{int\_coll}} \right)$$

---

### 2.2. Ánh Xạ Sang Tọa Độ Thế Giới & Quy Ước Hệ Tọa Độ (Coordinate Conventions)

Để bảo đảm tính nhất quán toán học giữa hình học glyph và chuyển động thực tế của máy vẽ, hệ thống áp dụng quy ước tọa độ hai cấp:

1. **Hệ tọa độ cục bộ (Local Coordinates):**
   - Đơn vị font chuẩn hóa: $0..14$ đơn vị font, trong đó chiều cao thiết kế $H_{\text{font}} = 14.0$.
   - Các nét trong `CompositionState` (`strokes_local`), điểm đón $\mathbf{p}_{\text{in}}$, điểm thoát $\mathbf{p}_{\text{out}}$ và vector tiếp tuyến cục bộ được định nghĩa trong hệ tọa độ này.
   - Chi phí nội ký tự $C_{\text{state}}$ do TV4 đánh giá trên hệ tọa độ cục bộ.

2. **Hệ tọa độ thế giới (World Coordinates — Canvas / Paper Space):**
   - Đơn vị vật lý chuẩn hóa: milimét ($mm$).
   - Với cấu hình chuẩn $font\_size\_mm = 7.0\text{ mm}$, hệ số tỷ lệ chuyển đổi là:
     $$scale = \frac{font\_size\_mm}{H_{\text{font}}} = \frac{7.0}{14.0} = 0.50\text{ mm / đơn vị font}$$
   - Để đánh giá chuyển động động học ($D_{\text{penup}}$), độ cong tiếp tuyến ($C_{\text{curvature}}$), hình học cầu nối Bézier và va chạm cầu nối ($C_{\text{bridge\_collision}}$), **TV2 bắt buộc phải chuyển đổi tọa độ các điểm mút và nét sang tọa độ thế giới**:
     $$\mathbf{P}_{\text{entry}}(s) = \mathbf{p}_{\text{in}} \odot \mathbf{s}_i + \mathbf{o}_i, \quad \mathbf{P}_{\text{exit}}(s) = \mathbf{p}_{\text{out}} \odot \mathbf{s}_i + \mathbf{o}_i$$
     $$\mathbf{V}_{\text{entry}}(s) = \frac{\mathbf{v}_{\text{in}} \odot \mathbf{s}_i}{\|\mathbf{v}_{\text{in}} \odot \mathbf{s}_i\| + \epsilon}, \quad \mathbf{V}_{\text{exit}}(s) = \frac{\mathbf{v}_{\text{out}} \odot \mathbf{s}_i}{\|\mathbf{v}_{\text{out}} \odot \mathbf{s}_i\| + \epsilon}$$
     $$\mathcal{S}_{\text{world}}(s) = \left\{ S \odot \mathbf{s}_i + \mathbf{o}_i \mid S \in \mathcal{S}_{\text{local}}(s) \right\}$$
     với $\mathbf{o}_i = [\text{cursor\_x}_i, \text{baseline\_y}_i]^T$ là vị trí đặt bút của ký tự thứ $i$ trên trang giấy.

---

### 2.3. Quyết Định Chuyển Trạng Thái: Nối Nét hay Nhấc Bút

Tại mỗi bước chuyển tiếp giữa trạng thái $u \in \mathcal{S}_{i-1}$ và trạng thái $w \in \mathcal{S}_i$, thuật toán đưa ra quyết định nhị phân:
$$a_{i-1, i} \in \{ \text{LIFT}, \text{CONNECT} \}$$

#### Ràng buộc hình học khả thi (Feasibility Condition)
Quyết định $\text{CONNECT}$ chỉ được phép đánh giá nếu thỏa mãn đồng thời 4 ràng buộc tiên quyết:
$$\text{FeasibleConn}(u, w) \iff (u.\text{can\_out} = 1) \land (w.\text{can\_in} = 1) \land (\Delta x > -0.2\text{ mm}) \land (d < 12.0\text{ mm})$$

trong đó:
- $d = \|\mathbf{P}_{\text{entry}}(w) - \mathbf{P}_{\text{exit}}(u)\|$ là khoảng cách Euclid thế giới giữa điểm thoát và điểm đón.
- $\Delta x = P_{\text{entry}, x}(w) - P_{\text{exit}, x}(u)$ là độ tiến ngang thế giới.

Nếu $\text{FeasibleConn}(u, w) = \text{False}$, áp đặt ràng buộc cứng: bắt buộc $a_{i-1, i} = \text{LIFT}$.

---

### 2.4. Hàm Mục Tiêu Hai Cấp (Two-Level Objective Function)

Hàm mục tiêu tổng thể của CA-VHC được phân rã thành hai cấp độc lập: **Chi phí trạng thái tổ hợp ($C_{\text{state}}$)** và **Chi phí chuyển tiếp chuyển động ($J_{\text{transition}}$)**, qua đó tách biệt trách nhiệm tính chi phí ở cấp đặc tả nhằm tránh double-counting; production implementation và regression test vẫn đang chờ Step C:

$$J_{\text{total}}(\mathbf{s}, \mathbf{a}) = \sum_{i=1}^N C_{\text{state}}(s_i) + \sum_{i=1}^{N-1} J_{\text{transition}}(s_i, s_{i+1}, a_i)$$

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CẤU TRÚC HÀM MỤC TIÊU HAI CẤP                                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. CHI PHÍ TRẠNG THÁI NỘI TẠI CỦA NÚT: C_state(s) [Do TV4 tính]                        │
│    C_state(s) = w_4a · C_internal_collision(s) + w_5 · C_legibility(s) + w_6 · C_placement(s) │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. CHI PHÍ CHUYỂN TIẾP ĐỘNG HỌC: J_transition(u, w, a) [Do TV2 chủ trì tính]           │
│    - Nếu a = LIFT:                                                                     │
│        J_lift(u, w) = w_1 · D_penup(u, w) + w_2 · 1.0                                  │
│    - Nếu a = CONNECT:                                                                  │
│        J_conn(u, w) = w_3 · C_curvature(u, w) + w_4 · C_bridge_collision(u, w)         │
│    J_transition(u, w) = min_{a} J_transition(u, w, a)                                  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Cấp 1: Chi phí trạng thái tổ hợp nội tại ($C_{\text{state}}$ — Thuộc TV4)
$$C_{\text{state}}(s) = w_{4a} \cdot C_{\text{internal\_collision}}(s) + w_5 \cdot C_{\text{legibility}}(s) + w_6 \cdot C_{\text{placement}}(s)$$
*(Lưu ý: Các trọng số $w_{4a}, w_5, w_6$ được đánh dấu là `[REQUIRES EXPERIMENTAL TUNING]` — sẽ được xác lập qua thực nghiệm của TV4 tại Bước C).*

#### Cấp 2: Chi phí chuyển tiếp động học ($J_{\text{transition}}$ — Thuộc TV2 chủ trì)
- **Khi nhấc bút ($a = \text{LIFT}$):**
  $$J_{\text{lift}}(u, w) = w_1 \cdot D_{\text{penup}}(u, w) + w_2 \cdot 1.0$$
- **Khi nối nét liên tục ($a = \text{CONNECT}$):**
  $$J_{\text{conn}}(u, w) = w_3 \cdot C_{\text{curvature}}(u, w) + w_4 \cdot C_{\text{bridge\_collision}}(u, w)$$
- **Chi phí chuyển tiếp tối ưu giữa 2 node:**
  $$J_{\text{transition}}(u, w) = \begin{cases}
  J_{\text{conn}}(u, w), & \text{nếu } \text{FeasibleConn}(u, w) \land (J_{\text{conn}}(u, w) < J_{\text{lift}}(u, w)) \\
  J_{\text{lift}}(u, w), & \text{ngược lại}
  \end{cases}$$

> [!IMPORTANT]
> **Nguyên tắc chống tính trùng chi phí (No Double-Counting Rule):**
> - Chi phí độ dễ đọc ($C_{\text{legibility}}$), độ lệch vị trí dấu ($C_{\text{placement}}$) và va chạm thân-dấu nội ký tự ($C_{\text{internal\_collision}}$) chỉ tính **DUY NHẤT một lần trong $C_{\text{state}}(s)$**.
> - Chi phí va chạm cầu nối liên ký tự ($C_{\text{bridge\_collision}}$) chỉ tính **DUY NHẤT một lần trong $J_{\text{transition}}(u, w)$** khi quyết định nối nét.
> - Tuyệt đối không đưa $C_{\text{legibility}}$ hay $C_{\text{internal\_collision}}$ vào hàm chuyển tiếp $J_{\text{transition}}$.

---

### 2.5. Bảng Chi Tiết Thành Phần Hàm Mục Tiêu

| Cấp chi phí | Thành phần | Ký hiệu | Đơn vị | Miền giá trị | Trách nhiệm | Trọng số đề xuất & Tình trạng |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **State** | **Va chạm nội ký tự** | $C_{\text{internal\_collision}}$ | Điểm | $[0.0, +\infty)$ | TV4 | $w_{4a} = 15.0$ `[REQUIRES EXPERIMENTAL TUNING]` |
| **State** | **Độ dễ đọc biến thể** | $C_{\text{legibility}}$ | Điểm | $[0.0, 1.0]$ | TV4 | $w_5 = 1.0$ `[REQUIRES EXPERIMENTAL TUNING]` |
| **State** | **Độ lệch vị trí dấu** | $C_{\text{placement}}$ | Điểm | $[0.0, 1.0]$ | TV4 | $w_6 = 2.0$ `[REQUIRES EXPERIMENTAL TUNING]` |
| **Transition**| **Quãng đường pen-up** | $D_{\text{penup}}$ | $mm$ | $[0, +\infty)$ | TV2 | $w_1 = 0.5$ (Baseline Kinematics) |
| **Transition**| **Số lần nhấc bút** | $N_{\text{lift}}$ | Lần | $\{0, 1\}$ | TV2 | $w_2 = 4.0$ (Phạt trễ trục Z) |
| **Transition**| **Góc bẻ tiếp tuyến** | $C_{\text{curvature}}$ | Điểm | $[0.0, 4.0]$ | TV2 | $w_3 = 2.0$ (Độ trơn hình học $C^1$) |
| **Transition**| **Va chạm cầu nối** | $C_{\text{bridge\_collision}}$| Điểm | $[0.0, +\infty)$ | Shared (TV2+TV4)| $w_4 = 15.0$ (Hard cut / clearance) |

---

### 2.6. Tách Biệt Rõ Ràng Hai Bài Toán Va Chạm (Collision Separation)

1. **Va chạm nội ký tự ($C_{\text{internal\_collision}}$):**
   - Xảy ra khi nét của diacritic candidate đè lên nét của base variant trong cùng 1 ký tự.
   - Thuộc trách nhiệm của **Thành viên 4** trong quá trình sinh ứng viên dấu (tọa độ cục bộ).
   - Nếu khoảng cách vi phạm nghiêm trọng ngưỡng va chạm cơ học, TV4 loại bỏ hoàn toàn ứng viên đó khỏi candidate pool (hard pruning). Nếu chỉ chạm nhẹ trong biên an toàn cho phép, TV4 tính điểm phạt vào $C_{\text{internal\_collision}}(s)$ trong $C_{\text{state}}(s)$.

2. **Va chạm đường nối liên ký tự ($C_{\text{bridge\_collision}}$):**
   - Xảy ra khi đường nối bút (ligature bridge) từ điểm thoát của ký tự $i-1$ đến điểm đón của ký tự $i$ cắt qua thân chữ hoặc dấu phụ của các ký tự xung quanh.
   - Thuộc trách nhiệm phối hợp của **Thành viên 2 và Thành viên 4** trong hàm `eval_transition` (tọa độ thế giới).
   - Nếu cầu nối cắt ngang đoạn thẳng bất kỳ (`segments_intersect == True`), chi phí là $+\infty$, loại bỏ quyết định `CONNECT` và ép buộc chọn `LIFT`. Nếu cầu nối đi vào vùng an toàn nhưng không cắt, áp dụng hàm phạt mềm (soft penalty).

---

### 2.7. Phương Trình Bellman / Viterbi DP Trên Trellis Đa Trạng Thái

Quy hoạch động thực hiện trên từng từ qua hàm `optimize_word_dag` với không gian trạng thái tổ hợp `CompositionState`:

- **Khởi tạo tầng đầu ($i = 1$):**
  $$DP[1, j] = C_{\text{state}}(s[1, j]), \quad \forall j \in \{1, \dots, |\mathcal{S}_1|\}$$
- **Quy hoạch động chuyển tiếp ($i = 2, \dots, N$):**
  $$DP[i, j] = C_{\text{state}}(s[i, j]) + \min_{p \in \{1, \dots, |\mathcal{S}_{i-1}|\}} \left[ DP[i-1, p] + J_{\text{transition}}(s[i-1, p], s[i, j]) \right]$$
  $$BP[i, j] = \arg\min_{p \in \{1, \dots, |\mathcal{S}_{i-1}|\}} \left[ DP[i-1, p] + J_{\text{transition}}(s[i-1, p], s[i, j]) \right]$$
  $$\text{Action}[i, j] = \arg\min_{a \in \{\text{LIFT}, \text{CONN}\}} J_{\text{transition}}(s[i-1, BP(i, j)], s[i, j], a)$$
- **Truy hồi ngược (Backtracking):** Bắt đầu từ trạng thái kết thúc có tổng chi phí nhỏ nhất:
  $$j_N^* = \arg\min_{j \in \{1, \dots, |\mathcal{S}_N|\}} DP[N, j]$$
  Truy hồi tuần tự qua con trỏ $BP[i, j]$ để trích xuất chuỗi trạng thái tối ưu $\mathbf{s}^* = (s_1^*, \dots, s_N^*)$ và chuỗi hành động nối nét $\mathbf{a}^* = (a_1^*, \dots, a_{N-1}^*)$.

---

## 3. Hệ Thống Baseline Đối Chứng Chuẩn Hóa Theo Roadmap

Tuân thủ nghiêm ngặt chuẩn quy định trong Roadmap (`02_roadmap.md`) và Current Task (`03_current-task.md`), hệ thống phân định rõ rệt: **3 Baseline đối chứng chuẩn**, **1 Phương pháp đề xuất (Proposed CA-VHC)**, và **các nghiên cứu bóc tách thành phần tùy chọn (Optional Ablation Studies)**:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MA TRẬN ĐỐI CHỨNG CA-VHC                               │
├─────────────────────┬─────────────────────┬─────────────────────┬──────────────────────┤
│ B1: Static Glyph    │ B2: Greedy          │ B3: Current Trellis │ Proposed:            │
│     Renderer        │     Heuristic       │     DAG (No Diac)   │ Full CA-VHC          │
├─────────────────────┼─────────────────────┼─────────────────────┼──────────────────────┤
│ - Luôn nhấc bút     │ - Quyết định nối nét│ - Viterbi DP hiện có│ - Trellis trên       │
│   giữa các chữ cái  │   cục bộ tham lam   │   trong engine.py   │   CompositionState   │
│ - Chỉ dùng variant  │   giữa 2 ký tự      │ - Tối ưu thân chữ   │ - Đồng tối ưu thân   │
│   canonical 'std'   │ - Không có Viterbi  │   nhưng CHƯA xét dấu│   và vị trí dấu      │
│ - Dấu đặt mặc định  │   nhìn xa toàn cục  │ - Dấu sinh hậu kỳ   │ - Né va chạm cầu nối │
│ - Luôn chọn LIFT    │ - Dễ kẹt cực tiểu   │   bằng mỏ neo tĩnh  │   và dấu triệt để    │
└─────────────────────┴─────────────────────┴─────────────────────┴──────────────────────┘
```

### 3.1. Baseline 1: Static Glyph Renderer (B1)
- **Bản chất:** Mô phỏng phương pháp kết xuất ký tự nét đơn tĩnh truyền thống (canonical `std`, luôn `LIFT`).
- **Hành vi:** Tắt toàn bộ Trellis DAG; chỉ dùng duy nhất biến thể canonical `std` ($K_{\text{base}} = 1$); dấu đặt ở vị trí mặc định; mọi bước chuyển tiếp liên ký tự đều nhấc bút ($a \equiv \text{LIFT}$); số lần nhấc bút giữa các thân chữ luôn là $N - 1$.
- **Mục đích đối chứng:** Xác lập mốc sàn về quãng đường pen-up tối đa và số lần nhấc bút tối đa.

### 3.2. Baseline 2: Greedy Contextual/Connection Heuristic (B2)
- **Bản chất:** Phương pháp nối nét dựa trên heuristic tham lam cục bộ giữa 2 ký tự liên tiếp.
- **Hành vi:** Tại mỗi bước $i-1 \to i$, chọn biến thể và quyết định nối nét có chi phí chuyển tiếp tại chỗ nhỏ nhất, không sử dụng bảng quy hoạch động Viterbi để nhìn trước các ký tự tiếp theo trong từ.
- **Mục đích đối chứng:** Chứng minh ưu thế vượt trội của quy hoạch động toàn cục Viterbi DP so với quyết định tham lam cục bộ trong việc tránh các cực tiểu địa phương.

### 3.3. Baseline 3: Current Trellis DAG Without Advanced Diacritic Constraints (B3)
- **Bản chất:** Thuật toán Viterbi DP hiện trạng trong mã nguồn (`backend/handwriting/engine.py:optimize_word_dag`).
- **Hành vi:** Tối ưu hóa toàn cục trên biến thể thân chữ cái gốc, nhưng **hoàn toàn chưa có nhận thức hay ràng buộc dấu tiếng Việt trong DAG**. Dấu tiếng Việt được sinh sau khi giải xong DP bằng hàm mỏ neo tĩnh `generate_accents()` và append tuần tự về cuối từ.
- **Mục đích đối chứng:** Bộc lộ các lỗi va chạm hình học giữa cầu nối và dấu trong hệ thống hiện tại, làm bằng chứng khoa học cho sự cần thiết của CA-VHC.

### 3.4. Phương pháp Đề xuất: Full CA-VHC (Proposed Method)
- **Bản chất:** Giải thuật đồng tối ưu trạng thái tổ hợp `CompositionState` $(v_{\text{base}}, c_{\text{diacritic}})$ và chuyển động, giải bằng Viterbi DP toàn cục theo từng từ.
- **Hành vi:** Đồng thời chọn biến thể thân chữ, vị trí dấu khả dĩ và quyết định nối nét/nhấc bút sao cho cực tiểu hóa $J_{\text{total}}$, hướng tới tiêu chí nghiệm thu $collision\_count = 0$ và độ trơn hình học $C^1$.

### 3.5. Các Nghiên Cứu Bóc Tách Thành Phần Tùy Chọn (Optional Ablation Studies)
Để phục vụ phân tích sâu cơ chế đóng góp của từng thành phần trong bài báo khoa học, hai biến thể đối chứng chuyên biệt dưới đây được xếp vào danh mục nghiên cứu bóc tách (Ablation Studies), không thay thế 3 baseline chuẩn:
1. **Ablation Study 1 — Pure Motion Trellis (B2-alt):** Giữ nguyên thuật toán Viterbi DP nhưng chỉ tối ưu chuyển động trên thân chữ cái, khóa cứng dấu ở vị trí canonical tĩnh để cô lập tác động của việc né dấu động.
2. **Ablation Study 2 — Static Diacritic Layout (B3-alt):** Áp dụng quy tắc kiểu chữ tĩnh (bounding box / anchor dịch chuyển cục bộ) để né va chạm thân chữ, nhưng nối nét kiểu greedy không đồng tối ưu chuyển động toàn cục.

---

## 4. Thiết Kế Diacritic-Aware DAG & Phân Tầng Quy Hoạch Nét Trễ

### 4.1. Biểu Diễn Hình Học & Vùng Cấm An Toàn

```text
        ┌────────────────────────────────────────────────────────┐
        │ Tầng 2: Dấu thanh (Sắc/Huyền/Hỏi/Ngã)                  │  y ≈ 0.5 - 2.5
        ├────────────────────────────────────────────────────────┤
        │ Tầng 1: Dấu định dạng nguyên âm (Nón/Trăng/Móc)        │  y ≈ 2.5 - 4.6
        ├────────────────────────────────────────────────────────┤
        │ Vùng thân chữ chính (x-height) & Nét nối (Bridge)      │  y ≈ 4.6 - 14.0
        ├────────────────────────────────────────────────────────┤
        │ Tầng đáy: Dấu nặng (Dot Below)                         │  y ≈ 14.5 - 16.0
        └────────────────────────────────────────────────────────┘
```

- **Clearance Envelope của nét dấu:**
  $$\mathcal{E}(S_{\text{diac}}) = \left\{ \mathbf{x} \in \mathbb{R}^2 \mid \min_{k} \text{dist}(\mathbf{x}, [p_k, p_{k+1}]) \le \delta_{\text{clearance}} \right\}$$
  - Ngưỡng an toàn mục tiêu nghiên cứu: $\delta_{\text{clearance}} = 0.50\text{ mm}$ (với $font\_size\_mm = 7.0\text{ mm}$).
  - Ngưỡng mặc định kỹ thuật nguyên mẫu: $\delta_{\text{clearance\_default}} = 0.20\text{ mm}$ (dùng trong code hiện hành).
  - Vùng mỏ neo an toàn: $\delta_{\text{anchor}} = 0.35\text{ mm}$ quanh $\mathbf{P}_{\text{entry}}$ và $\mathbf{P}_{\text{exit}}$ của chính glyph để tránh tự phạt điểm tiếp giáp.
  > **Quy chuẩn ngưỡng an toàn:** $0.20\text{ mm}$ là mặc định kỹ thuật ban đầu trong `DiacriticConfig`; $0.50\text{ mm}$ là mục tiêu nghiên cứu chờ TV3 hiệu chuẩn thực nghiệm trên máy vẽ vật lý.

### 4.2. Cơ Chế Đưa Dấu Vào Trellis DAG Qua `CompositionState`

Dấu tiếng Việt được định nghĩa là **biến tối ưu hữu hạn (finite search candidate)** do TV4 cung cấp trong `CompositionState`:
1. **Sinh ứng viên dấu (TV4):** Tối đa 3 ứng viên vị trí (`canonical`, `safe_left`, `safe_right`).
2. **Ghép trạng thái tổ hợp (TV4):** Tổ hợp với $K_{\text{base}} \le 3$ biến thể thân tạo ra tối đa $K_{\text{raw}} \le 9$ trạng thái `CompositionState`.
3. **Đánh giá chuyển tiếp thế giới (TV2):** TV2 nhận trạng thái tổ hợp đã chuyển sang tọa độ thế giới và đánh giá va chạm của cầu nối với toàn bộ nét thân chữ và nét dấu xung quanh.

### 4.3. Phân Định Collision Cứng vs Penalty Mềm Trên Cầu Nối

1. **Ràng buộc cứng (Hard Collision Rejection):**
   Nếu đoạn thẳng của cầu nối $\mathcal{B}$ cắt ngang bất kỳ đoạn thẳng nào của nét thân hoặc nét dấu (`segments_intersect == True`):
   $$C_{\text{bridge\_collision}} = +\infty \implies J_{\text{conn}} = +\infty$$
   Quyết định $\text{CONNECT}$ bị loại trừ ngay lập tức; giải thuật bắt buộc chọn $\text{LIFT}$.
2. **Penalty mềm (Soft Clearance Penalty):**
   Nếu khoảng cách $\text{dist} < \delta_{\text{clearance}}$ nhưng không giao cắt:
   $$\text{penetration} = \frac{\delta_{\text{clearance}} - \text{dist}}{\delta_{\text{clearance}}} \in (0.0, 1.0]$$
   $$C_{\text{bridge\_collision}} = 2.0 + 4.0 \cdot \text{penetration}$$

### 4.4. Quy Hoạch Thứ Tự Nét Trễ (Delayed-Stroke Ordering) — Kiến Trúc Phân Tầng

Theo Roadmap (`02_roadmap.md`), Delayed-Stroke là **P0 design requirement** của CA-VHC. Để vừa đáp ứng yêu cầu P0 vừa bảo đảm tính khả thi triển khai theo từng bước, kiến trúc quy hoạch nét trễ được phân tầng như sau:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHÂN TẦNG QUY HOẠCH NÉT TRỄ (DELAYED-STROKE)                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TẦNG P0: Hỗ trợ State/Action & Policy Tối Thiểu (Step C v1 — Bắt buộc)                 │
│  - Mở rộng cấu trúc state/action hỗ trợ ghi nhận và xuất nét trễ có thứ tự             │
│  - Triển khai policy tối thiểu có thể kiểm thử: gom nét phụ/dấu sau thân từ            │
│    áp dụng Nearest Neighbor Heuristic cơ bản để giảm thiểu quãng đường pen-up          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TẦNG P1: Lookahead Scheduling Nâng Cao (Step C v2 — Nghiên cứu chuyên sâu)              │
│  - Exact Enumeration cho số nét phụ/dấu M <= 6 (không gian hoán vị M! <= 720)          │
│  - Branch-and-Bound / Kinematic Lookahead cho M > 6 xuất phát từ điểm cuối P_last      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TẦNG P2: Personalized Scheduling (Research Extension — Writer Profile)                 │
│  - Tích hợp phong cách cá nhân hóa người viết: học thứ tự đặt dấu theo thói quen       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Cơ sở toán học của bộ lập lịch nét trễ:
Tập hợp $M$ nét thứ cấp của một từ $\mathcal{D}_{\text{word}} = \{d_1, d_2, \dots, d_M\}$ bao gồm: dấu thanh, dấu phụ nguyên âm, gạch ngang đ/t, chấm i/j.
- Trường hợp $M \le 6$ (chiếm phần lớn các từ đơn âm tiết tiếng Việt thông dụng, cần đo đạc và kiểm chứng định lượng trên corpus do TV1 cung cấp):
  Không gian hoán vị tối đa $M! \le 6! = 720$. Tìm thứ tự hoán vị $\pi^*$ tối ưu quãng đường pen-up xuất phát từ điểm kết thúc thân từ $\mathbf{P}_{\text{last}}$:
  $$\pi^* = \arg\min_{\pi \in \mathcal{P}_M} \left[ \|\mathbf{P}_{\text{last}} - \text{start}(\pi_1)\| + \sum_{k=1}^{M-1} \|\text{end}(\pi_k) - \text{start}(\pi_{k+1})\| \right]$$
- Trường hợp $M > 6$: Áp dụng Nearest Neighbor Heuristic kết hợp Kinematic Cost (`path_optimizer.py::nearest_neighbor_order`) bảo đảm thời gian giải đa thức $\mathcal{O}(M^2)$.

---

## 5. Bảng Ánh Xạ Nghiên Cứu: RQ — Metric Contract Mục Tiêu

Bảng ánh xạ duy nhất dưới đây chuẩn hóa mối quan hệ giữa câu hỏi nghiên cứu, chỉ số đo đạc, trạng thái hiện tại trong codebase và kế hoạch triển khai:

| Research Question | Primary Metrics | Secondary / Diagnostic Metrics | Trạng thái hiện tại trong Codebase | Nơi được xuất ra | Việc còn thiếu cần làm ở Step C |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RQ1: Nối Nét & Động Học** (Hiệu quả đường đi và số lần nhấc bút) | `total_path_length_mm`<br>`pen_lift_distance_mm`<br>`pen_lift_count` | `mean_penup_speed`<br>`idle_motion_ratio`<br>`path_length_growth_rate` | **Đã có trong codebase** qua `path_optimizer.py::compute_svg_metrics` (gọi từ `engine.py::generate_handwriting_svg`) | Trường `svg_metrics` (API response JSON) và CSV experiment log | Chuẩn hóa trace cấu trúc để tách bạch nét vẽ tiếp xúc giấy vs đường di chuyển trên không; hiệu chuẩn đơn vị mm với máy vẽ thật. |
| **RQ2: Tránh Va Chạm Dấu** (Chất lượng composition và dấu tiếng Việt) | `collision_count`<br>`minimum_diacritic_clearance_mm`<br>`accent_base_collision_count`<br>`bridge_collision_count` | `placement_penalty_mean`<br>`diacritic_envelope_violations`<br>`accent_shift_dx_mean` | **Internal evaluator đã triển khai và test** `collision_count` và `minimum_diacritic_clearance_mm` qua `backend/handwriting/metrics_evaluator.py::evaluate_ca_vhc_metrics`; quy tắc phán quyết biên `0.20/0.50 mm` đã có bản thực thi fail-closed tại `classify_diacritic_clearance_acceptance`.<br>`accent_base_collision_count` và `bridge_collision_count` tách riêng vẫn là **metric mục tiêu chưa triển khai**.<br>Tích hợp public API/CSV contract đang chờ Step C. | Hai metric hiện có được xuất qua evaluator nội bộ; verdict hiện chỉ dùng cho nghiệm thu phần mềm, không phải xác nhận an toàn vật lý; các metric tách riêng dự kiến mở rộng ra public `svg_metrics` và `logs/experiment_log.csv` | Tích hợp metric contract từ trace nội bộ vào API response/CSV, triển khai hai bộ đếm va chạm tách riêng và cập nhật API Spec trong một PR tài liệu riêng. |
| **RQ3: Hiệu Năng & Khả Thi** (Tính khả thi chuyển động và chi phí tính toán) | `optimize_time_ms`<br>`processing_time_ms`<br>`max_curvature`<br>`c1_violation_count`<br>`bounds_violation_count` | `p95_optimize_time_ms`<br>`acute_turn_count_120deg`<br>`tangent_discontinuity_max` | `processing_time_ms` đã có trong Gateway.<br>Internal DAG timing đã triển khai qua `time.perf_counter()` trong `StructuredRenderResult.optimize_time_ms` và `compute_svg_metrics`; internal evaluator hiện có `curvature_cost`.<br>Chưa có benchmark thống kê chính thức (median/p95); `max_curvature`, `c1_violation_count` và `bounds_violation_count` **chưa được triển khai**. | Metadata API Gateway, `compute_svg_metrics` và internal evaluator; các metric còn thiếu chưa được xuất ra public API/CSV | Thực hiện benchmark thống kê chính thức (median/p95) trên toàn bộ ma trận thực nghiệm; triển khai và tích hợp các chẩn đoán tiếp tuyến/khổ giấy vào runner chính thức; cập nhật API Spec trong một PR tài liệu riêng; không dùng một lần đo nội bộ làm bằng chứng hiệu năng khoa học. |

> [!IMPORTANT]
> **Quy định kỷ luật về Metric Contract và API Spec:**
> - Bảng trên là **Metric Contract mục tiêu của Step C**, phục vụ công tác nghiên cứu và kiểm thử thực nghiệm.
> - Tài liệu `OmniDraw_API_Spec-4.md` hiện tại **tuyệt đối không được sửa đổi** để mô tả những trường mà backend chưa thực sự triển khai. API Spec sẽ chỉ được cập nhật trong một PR riêng biệt sau khi backend đã xuất các trường metric này ổn định.
> - Internal DAG timing đã được triển khai qua `time.perf_counter()` (`StructuredRenderResult.optimize_time_ms` chuyển sang `compute_svg_metrics`); tuy nhiên đây là đo đạc nội bộ đơn lẻ, **chưa có benchmark thống kê chính thức (median/p95) trên toàn bộ ma trận thực nghiệm**; API Spec hiện còn mô tả cũ và sẽ cần cập nhật trong một PR tài liệu riêng; **tuyệt đối không dùng một lần đo nội bộ làm bằng chứng hiệu năng khoa học**.

---

### 5.1. Hai Tập Ngữ Liệu Benchmark do TV1 Quản Lý

Tuân thủ quy chuẩn dữ liệu tại `08_handwriting_dataset_spec.md`, hai tập ngữ liệu độc lập do **Thành viên 1** cung cấp:

1. **Development Corpus (`BENCHMARK_DEV_CORPUS_20` — TV1 cung cấp):** 20 từ đại diện bao phủ các tổ hợp nguyên âm biến âm, thanh điệu và phụ âm nhô cao/thấp (ascender/descender), dùng trong quá trình phát triển và kiểm thử hồi quy.
2. **Holdout Corpus (`BENCHMARK_HOLDOUT_CORPUS_20` — TV1 cung cấp):** 20 từ độc lập tuyệt đối không dùng khi phát triển hoặc tinh chỉnh trọng số, dùng để nghiệm thu đánh giá tính tổng quát hóa.
*(Lưu ý: Benchmark fixtures kỹ thuật `BENCHMARK_DEV_CORPUS_20` và `BENCHMARK_HOLDOUT_CORPUS_20` đã tồn tại trong codebase và test pass độc lập; việc còn thiếu là TV1 nghiệm thu chính thức nội dung/coverage và đóng băng version corpus trước khi bước vào thực nghiệm chính thức).*

### 5.2. Môi Trường Thực Nghiệm & Giao Thức Đo Đạc

Mọi thực nghiệm phải ghi nhận chi tiết siêu dữ liệu môi trường vận hành thực tế (Execution Metadata):
1. **CPU Model:** Tên đầy đủ vi xử lý, số nhân vật lý và số luồng logic.
2. **OS & Version:** Bản phát hành và build cụ thể (Windows / Linux báo cáo riêng, không gộp số liệu).
3. **Python Version & NumPy BLAS Backend:** Phiên bản patch release chính xác.
4. **Git Commit Hash & Power Mode:** Mã hash commit và chế độ cấp nguồn hệ thống.
- **Giao thức:** 10 lượt warm-up; $N_{\text{runs}} = 50$ lần lặp cho mỗi cấu hình với 4 seed cố định: `[42, 100, 2026, 999999]`. Báo cáo đồng thời Median và p95.

### 5.3. Bảng Tiêu Chí Nghiệm Thu Kỳ Vọng (Acceptance Thresholds)

| Chỉ số | Vùng Đạt (PASS — Ưu tiên 2) | Vùng Thất Bại / Bác Bỏ (FAIL — Ưu tiên 1) | Vùng Chưa Đủ Cơ Sở (INCONCLUSIVE — Ưu tiên 3) |
| :--- | :--- | :--- | :--- |
| **Tính hợp lệ SVG & Bounds** | Toàn bộ file SVG hợp lệ trên tập kiểm thử | $\ge 1$ file lỗi XML hoặc vượt bounds | — |
| **H1.1: Quãng đường pen-up** | Giảm $\ge 25.0\%$ vs B1 **VÀ** $\ge 10.0\%$ vs B2 | Giảm $< 15.0\%$ vs B1 **HOẶC** $< 5.0\%$ vs B2 | Mọi trường hợp còn lại |
| **H1.2: Số lần nhấc bút** | Giảm $\ge 35.0\%$ vs B1 | Giảm $< 20.0\%$ vs B1 | Giảm $[20.0\%, 35.0\%)$ vs B1 |
| **H1.3: Chiều dài nét vẽ** | Tăng $\le 10.0\%$ vs B1 | Tăng $> 15.0\%$ vs B1 | Tăng $(10.0\%, 15.0\%]$ vs B1 |
| **H2.1: Va chạm dấu** | $collision\_count = 0$ trên toàn bộ tập nghiệm thu | $collision\_count \ge 1$ | — |
| **H2.2: Khoảng cách cách ly** | $d_{\min} \ge 0.50\text{ mm}$ | $d_{\min} < 0.20\text{ mm}$ | $0.20\text{ mm} \le d_{\min} < 0.50\text{ mm}$ |
| **H3.1: Thời gian Viterbi DP** | Median $\le 5.0\text{ ms}$ **VÀ** p95 $\le 10.0\text{ ms}$ | Median $> 15.0\text{ ms}$ **HOẶC** p95 $> 30.0\text{ ms}$ | Mọi trường hợp còn lại |
| **H3.2: Chi phí độ cong tiếp tuyến** | Giảm $\ge 15.0\%$ vs B2 **VÀ** không góc $> 120^\circ$ | Giảm $\le 0.0\%$ vs B2 **HOẶC** có góc $> 120^\circ$ | Mọi trường hợp còn lại |

---

## 6. Ma Trận Truy Vết Khoa Học (Traceability Matrix)

| RQ | Giả thuyết | Metrics đo đạc | Đối chứng chuẩn | Kịch bản kiểm thử | Vùng FAIL (Ưu tiên 1) | Vùng PASS (Ưu tiên 2) | Vùng INCONCLUSIVE (Ưu tiên 3) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RQ1** | H1.1 | `pen_lift_distance_mm` | B1, B2 | Corpus do TV1 cung cấp × 2 font × 4 seeds | Giảm $< 15\%$ vs B1 hoặc $< 5\%$ vs B2 | Giảm $\ge 25\%$ vs B1 và $\ge 10\%$ vs B2 | Mọi trường hợp còn lại |
| **RQ1** | H1.2 | `pen_lift_count` | B1 | Đếm trên các từ hỗ trợ nối nét | Giảm $< 20\%$ vs B1 | Giảm $\ge 35\%$ vs B1 | Giảm $20\text{–}35\%$ vs B1 |
| **RQ1** | H1.3 | `total_path_length_mm` | B1 | Đo tổng chiều dài nét tiếp xúc giấy | Tăng $> 15\%$ vs B1 | Tăng $\le 10\%$ vs B1 | Tăng $10\text{–}15\%$ vs B1 |
| **RQ2** | H2.1 | `collision_count` | B3 | Kiểm tra giao cắt đoạn thẳng bridge vs dấu | $collision\_count \ge 1$ | $collision\_count = 0$ | — |
| **RQ2** | H2.2 | `minimum_diacritic_clearance_mm` | B3 | Đo khoảng cách ngắn nhất bridge vs dấu | $< 0.20\text{ mm}$ | $\ge 0.50\text{ mm}$ | $0.20\text{–}0.50\text{ mm}$ |
| **RQ3** | H3.1 | `optimize_time_ms` (perf_counter) | B2, B3 | 50 lần lặp sau warm-up trên môi trường ghi nhận | Median $> 15\text{ ms}$ hoặc p95 $> 30\text{ ms}$ | Median $\le 5\text{ ms}$ và p95 $\le 10\text{ ms}$ | Mọi trường hợp còn lại |
| **RQ3** | H3.2 | `curvature_cost` | B2 | Đo tổng chi phí bẻ tiếp tuyến ngòi bút | Giảm $\le 0\%$ vs B2 hoặc có góc $> 120^\circ$ | Giảm $\ge 15\%$ vs B2 và không góc $> 120^\circ$ | Mọi trường hợp còn lại |

---

## 7. Kế Hoạch Triển Khai Kỹ Thuật (Lộ Trình Phụ Thuộc Của Bước C)

Lộ trình kỹ thuật của Bước C không phải là chuỗi tuần tự tuyệt đối mà được tổ chức theo đồ thị phụ thuộc (dependency graph), cho phép triển khai song song giữa hạ tầng đo đạc và adapter đối chứng:

```text
PR1 Metrics/Runner ──┐
                     ├──> PR3 CompositionState/DAG
PR2 Baseline Adapters┘
                              │
                              v
                     PR4 Delayed-Stroke P0
                              │
                              v
                     PR5 Benchmark/Ablation
```

**Quy tắc điều phối & Phụ thuộc:**
- **PR1 & PR2 song song:** PR1 (TV4 chủ trì runner/logging/metric integration, TV1 cung cấp fixtures, TV2 đặc tả motion metrics) và PR2 (TV2 chủ trì baseline adapters) có thể triển khai song song, độc lập.
- **Điều kiện tiên quyết cho PR3:** Cả PR1 và PR2 phải đạt interface, snapshot và test cần thiết trước khi hợp nhất vào PR3 (`CompositionState` và Diacritic-Aware DAG).
- **Thứ tự PR3 ➔ PR4 ➔ PR5:** PR3 phải hoàn thành trước PR4 (Delayed-Stroke P0); PR4 phải hoàn thành trước PR5 (Benchmark & Ablation).
- **Ranh giới dữ liệu thực nghiệm:** Việc TV1 chưa đóng băng formal corpus không chặn việc viết mã nguồn PR1–PR4. PR1–PR4 được phép phát triển và kiểm thử bằng các `provisional technical fixtures`. TV1 review và đóng băng formal corpus là điều kiện tiên quyết để chạy PR5 ở chế độ thực nghiệm chính thức (formal experiment) và đưa số liệu vào báo cáo khoa học.

### PR1: Hoàn Thiện CA-VHC Metrics & Experiment Infrastructure (TV4 chủ trì, TV1 + TV2 phối hợp)
- **Trạng thái hiện tại:** `PR1: IN PROGRESS`
  - *Completed foundation (Nền tảng đã hoàn thành & có test bảo vệ):*
    - `StructuredRenderResult` / structured render trace nội bộ (`TraceStroke`, `text_to_strokes_structured`) đã tồn tại.
    - `backend/handwriting/metrics_evaluator.py` đã tồn tại và được kiểm thử tự động pass (12/12 tests).
    - Provisional benchmark fixtures (`BENCHMARK_DEV_CORPUS_20`, `BENCHMARK_HOLDOUT_CORPUS_20`) đã tồn tại và kiểm thử tính rời nhau.
  - *Remaining (Các hạng mục còn lại đang triển khai):*
    - Tích hợp các metric thực sự đã triển khai ổn định từ trace nội bộ vào experiment pipeline.
    - Mở rộng log CSV tương ứng cho các trường đo đạc.
    - Xây dựng automated experiment runner theo ma trận corpus × font × seed × baseline.
    - Chụp baseline snapshot trước khi đưa state mới vào engine.
    - Kiểm thử hồi quy tương thích ngược (backward-compatibility tests) bảo đảm không làm biến đổi hành vi API công khai.
- **Ranh giới phụ thuộc corpus:** PR1 không bắt buộc phải chờ TV1 đóng băng formal corpus; PR1 được phép vận hành và kiểm thử bằng provisional technical fixtures. TV1 corpus review/freeze là validation gate downstream để khóa dữ liệu thực nghiệm phục vụ PR5.
- **Phân công:** TV4 chủ trì runner/logging/metric integration; TV1 cung cấp và rà soát corpus/fixtures; TV2 đặc tả motion metrics.

### PR2: Chuẩn Hóa và Khóa Ba Baseline Đối Chứng B1, B2, B3 (TV2 chủ trì, TV4 phối hợp)
- **Trạng thái:** `IMPLEMENTED AND TESTED` — Entry Gate E3 hoàn tất; E4 shared interface agreement vẫn chờ TV2+TV4 ký duyệt.
- **Phạm vi kỹ thuật:**
  - Đóng gói 3 adapter thực nghiệm độc lập: B1 (Static Glyph Renderer), B2 (Greedy Contextual/Connection Heuristic), B3 (Current Trellis DAG without advanced diacritic constraints).
  - Adapter nằm tại `backend/handwriting/baselines.py`; runner gọi độc lập qua internal `_algorithm_mode` hoặc CLI `--method` với các tag `b1_static`, `b2_greedy`, `b3_current_trellis`.
  - B3 mặc định giữ nguyên đường gọi `optimize_word_dag`; public API và snapshot hình học hiện hành không thay đổi.
- **Phân công:** TV2 chủ trì phần motion adapter; TV4 điều phối tích hợp engine.

### PR3: CA-VHC Diacritic-Aware Trellis với `CompositionState` (TV4 chủ trì composition, TV2 chủ trì transition cost)
- **Phạm vi kỹ thuật:**
  - Tích hợp cấu trúc `CompositionState` (module `backend/handwriting/state.py` do TV4 xây dựng) vào hàm quy hoạch động `optimize_word_dag`.
  - Triển khai hàm chi phí hai cấp: $C_{\text{state}}(s)$ (TV4) và $J_{\text{transition}}(u, w)$ (TV2).
  - Tích hợp `bridge_collision_cost` kiểm tra va chạm trong tọa độ thế giới với toàn bộ nét thân và dấu xung quanh.
  - Thiết lập hard rejection: loại bỏ quyết định `CONNECT` nếu cắt ngang nét dấu.
  - Gắn metadata tối thiểu (`stroke_order_hint`) để làm tiền đề cho bài toán lập lịch nét trễ ở PR4.

### PR4: Delayed-Stroke Ordering Optimizer — Tầng P0 (TV2 chủ trì, TV4 phối hợp)
- **Phạm vi kỹ thuật:**
  - Triển khai chính sách P0 có thể kiểm thử tất định: viết xong thân từ $\rightarrow$ gom toàn bộ nét phụ/dấu trễ của từ $\rightarrow$ sắp xếp thứ tự vẽ dấu bằng thuật toán tất định Nearest Neighbor xuất phát từ điểm kết thúc nét cuối thân từ $\rightarrow$ dùng original stroke index làm tie-break chống bất định.
  - Khung kiến trúc mở rộng sẵn sàng cho Tầng P1 (Exact Enumeration $M \le 6$) và Tầng P2 (Writer Profile).
- **Phân công:** TV2 chủ trì thuật toán tối ưu chuyển động; TV4 tích hợp state và kiểm tra chính tả.

### PR5: Benchmark Runner, Automated Reporting & Ablation Study (Toàn nhóm phối hợp)
- **Phạm vi kỹ thuật:**
  - CLI runner thực thi toàn bộ ma trận (Proposed CA-VHC vs 3 Baselines × 20 từ Dev + 20 từ Holdout × 2 font × 4 seed × 50 iterations).
  - Tự động xuất log CSV ra thư mục ignore `logs/`, tính toán Median và p95.
  - Phân biệt rõ hai chế độ thực thi:
    - **Technical dry-run:** Được phép chạy thử nghiệm bằng provisional technical fixtures để kiểm tra luồng runner và định dạng CSV.
    - **Formal experiment:** Chỉ được phép công bố số liệu chính thức sau khi TV1 đã rà soát và freeze formal benchmark corpus, và TV3 đã hoàn tất hiệu chuẩn phần cứng máy vẽ (hardware calibration) cho các tuyên bố liên quan tới máy vẽ và ngưỡng clearance.
  - Thực hiện Ablation Studies đối với các thành phần trọng số và các phương án đối chứng mở rộng (Pure Motion Trellis, Static Diacritic Layout).
- **Phân công:** TV4 chủ trì runner/logging; TV2 phân tích chuyển động; TV1 kiểm tra tính toàn vẹn dữ liệu; TV3 hỗ trợ đối chiếu simulator/phần cứng.

---

## 8. Đối Chiếu Code Hiện Tại & Khoảng Trống Triển Khai (Implementation Gaps)

| STT | Hạng mục trên tài liệu / Roadmap | Hiện trạng trong Code thực tế | Phân loại khoảng trống | Hướng xử lý kỹ thuật Bước C |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Trạng thái Trellis `CompositionState`** | `engine.py` hiện chỉ nhận `char_info_list` với nét thân chữ (`scaled_prim`). Dấu sinh sau khi DP đã giải xong. | **Gap kiến trúc cốt lõi (P0)** | Triển khai PR3: Nạp `CompositionState` (TV4) vào `optimize_word_dag`, giải đồng thời thân chữ và vị trí dấu. |
| **2** | **Va chạm cầu nối với nét dấu** | `engine.py::bridge_collision_cost` chỉ kiểm tra va chạm với nét thân chữ lân cận, chưa nhận diện nét dấu trong tọa độ thế giới. | **Gap hình học chuyển động (P0)** | Triển khai PR3: Mở rộng `bridge_collision_cost` nhận toàn bộ nét thế giới $\mathcal{S}_{\text{world}}$ từ `CompositionState`. |
| **3** | **Tách biệt hàm mục tiêu hai cấp** | Hàm mục tiêu chuyển tiếp hiện tại chưa nhận $C_{\text{state}}$, nguy cơ lẫn lộn giữa va chạm nội và va chạm cầu nối. | **Gap mô hình toán (P0)** | Triển khai PR3: Triển khai công thức Bellman hai cấp $DP[i, j] = C_{\text{state}} + \min(DP + J_{\text{transition}})$. |
| **4** | **Bộ ba Baseline đối chứng chuẩn hóa** | Chưa có adapter chạy độc lập cho B1 (Static Glyph Renderer) và B2 (Greedy Contextual Heuristic). | **Gap framework thực nghiệm (P0)** | Triển khai PR2: Đóng gói 3 baseline thành adapter phục vụ runner thực nghiệm theo đúng Roadmap. |
| **5** | **Thời gian tối ưu hóa DAG** | Internal DAG timing đã triển khai qua `time.perf_counter()` trong structured trace và `compute_svg_metrics`; chưa có benchmark thống kê (median/p95) trên ma trận thực nghiệm. | **Gap thống kê & nghiệm thu thực nghiệm** | Chạy benchmark tự động trên toàn ma trận corpus, tính median/p95; cập nhật API Spec qua PR tài liệu riêng. |
| **6** | **Trích xuất nét có cấu trúc** | Structured render trace nội bộ (`TraceStroke`, `StructuredRenderResult`, `text_to_strokes_structured`) đã triển khai và có test; chưa tích hợp toàn bộ metric từ trace vào public API/CSV contract. | **Gap tích hợp contract API/CSV** | Hoàn thiện tích hợp các metric từ structured trace sang public API và CSV experiment runner. |
| **7** | **Thứ tự nét trễ (Delayed-stroke) P0** | Nét phụ và dấu được append tuần tự theo thứ tự xuất hiện. | **Gap tối ưu P0 theo Roadmap** | Triển khai PR4: Tầng P0 hỗ trợ state/action và policy tối thiểu (Nearest Neighbor cơ bản giảm penup). |

---

## 9. Cross-review Alignment with Project Standards

Bảng đối chiếu kỹ thuật dưới đây xác nhận sự đồng thuận và điều chỉnh chi tiết giữa tài liệu nghiên cứu CA-VHC của TV2 (`05_ca_vhc_research_spec.md`) và toàn bộ hệ thống tài liệu chuẩn của dự án:

| STT | Hạng mục kỹ thuật | File 05 (Phiên bản Cũ) | Tài liệu chuẩn (Roadmap, Task, Spec) | File 05 (Đã chỉnh sửa & Đồng bộ) | Trạng thái đồng thuận |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **1** | **Phân định quyền sở hữu (Ownership)** | TV2 sở hữu toàn bộ subsystem chữ viết tay. | TV1 sở hữu Dataset/Corpus; TV2 sở hữu Motion/DP; TV3 sở hữu Hardware/Validation; TV4 sở hữu Project Lead, Composition, State & Runner. | Đồng bộ Ma trận Quyền sở hữu 4 thành viên; TV2 là owner phần motion/DP của CA-VHC. | ✅ SYNCHRONIZED |
| **2** | **Đơn vị nút Trellis (Trellis Node)** | Nút là `GlyphVariant` (chỉ thân chữ). | Nút là `CompositionState = (base_variant, diacritic_candidate)`. | Định nghĩa lại Trellis node là `CompositionState` ($s = (v_{\text{base}}, c_{\text{diacritic}})$). | ✅ SYNCHRONIZED |
| **3** | **Không gian trạng thái & Giới hạn tổ hợp** | $K_i \le 3$ (chỉ đếm số biến thể thân). | $K_{\text{raw}} = K_{\text{base}} \times K_{\text{diacritic}} \le 9$. | Xác lập $K_{\text{raw}} \le 9$ là Cận lý thuyết, không áp dụng heuristic pruning ở P0. | ✅ SYNCHRONIZED |
| **4** | **Bản chất của dấu tiếng Việt** | Chướng ngại vật hình học xác định trước. | Biến tối ưu hữu hạn (`canonical`, `safe_left`, `safe_right`). | Đổi định nghĩa dấu thành biến tìm kiếm hữu hạn trong không gian trạng thái tổ hợp. | ✅ SYNCHRONIZED |
| **5** | **Phân rã hàm mục tiêu** | $J$ gộp chung mọi thành phần. | Phân rã 2 cấp: $C_{\text{state}}(s)$ (TV4) và $J_{\text{transition}}(u, w)$ (TV2). | Tách bạch hàm mục tiêu 2 cấp ở cấp đặc tả; production implementation và regression test vẫn đang chờ Step C. | ✅ SYNCHRONIZED |
| **6** | **Hệ thống Baseline đối chứng** | Dùng Pure Motion Trellis và Static Diacritic Layout làm baseline chính. | Roadmap quy định chuẩn: B1 (Static), B2 (Greedy Heuristic), B3 (Current Trellis DAG). | Đồng bộ chuẩn 3 baseline B1, B2, B3; chuyển Pure Motion và Static Diacritic sang mục Optional Ablation Studies. | ✅ SYNCHRONIZED |
| **7** | **Phân tầng Delayed-Stroke** | Đưa ra ngoài phạm vi Step C v1. | Roadmap quy định Delayed-Stroke là P0 design requirement. | Phân tầng rõ rệt: Tầng P0 (Step C v1 — policy tối thiểu có thể kiểm thử), Tầng P1 (Exact Enumeration $M \le 6$), Tầng P2 (Personalization). | ✅ SYNCHRONIZED |
| **8** | **Quy ước hệ tọa độ** | Không phân định rõ cục bộ vs thế giới. | Local (0..14 đơn vị) cho state; World ($mm$) cho chuyển động. | Quy định rõ: Local cho state biểu diễn; World cho transition và va chạm cầu nối. | ✅ SYNCHRONIZED |
| **9** | **Ngưỡng an toàn va chạm (Clearance)** | Đặt cứng $0.50\text{ mm}$ là chuẩn duy nhất. | Code đang dùng $0.20\text{ mm}$, đề xuất nghiên cứu là $0.50\text{ mm}$. | Ghi nhận rõ: $0.20\text{ mm}$ là mặc định kỹ thuật ban đầu trong `DiacriticConfig`; $0.50\text{ mm}$ là mục tiêu nghiên cứu chờ TV3 hiệu chuẩn máy thật. | ✅ RESOLVED FOR SOFTWARE STEP C |
| **10**| **Metric Contract & Tuyên bố hiệu năng** | Tuyên bố real-time guaranteed / instant và gộp chung metric. | Roadmap/Task yêu cầu tách biệt contract mục tiêu vs code thực tế. | Thiết lập bảng ánh xạ duy nhất RQ–Metric; phân biệt rõ Target vs Measured; ghi rõ API Spec sẽ cập nhật trong PR riêng. | ✅ SYNCHRONIZED |

---

## 10. Trạng Thái Phê Duyệt & Checklist Sẵn Sàng Cho Bước C

### 10.1 Bảng Kiểm Tra Điều Kiện Chuyển Giao (Readiness Checklist)

- [x] **CompositionState design thống nhất:** Cấu trúc `(base_variant, diacritic_candidate)` được xác lập làm node Trellis chính thức.
- [x] **Local/World coordinate design thống nhất:** Local cho glyph/state, World cho transition, bridge và SVG.
- [x] **Two-level objective design thống nhất:** Phân rã $C_{\text{state}}$ và $J_{\text{transition}}$, tách biệt double-counting ở cấp đặc tả.
- [x] **Ownership thống nhất:** Ranh giới 4 thành viên (TV1: Data, TV2: Motion/DP, TV3: Hardware, TV4: Composition/Lead) được phản ánh chuẩn xác.
- [x] **Baseline specification thống nhất:** Khóa chuẩn B1 (Static), B2 (Greedy Heuristic), B3 (Current Trellis DAG); chuyển các biến thể khác sang Ablation Studies.
- [x] **TV2 technical cross-review PASS:** Rà soát kỹ thuật hoàn tất và thông qua thiết kế kiến trúc Bước B.
- [x] **Five software decisions resolved:** Khóa 5 quyết định kỹ thuật cho triển khai phần mềm Bước C.
- [x] **Software Step C authorized by TV4:** Project Lead phê duyệt bắt đầu triển khai phần mềm (`READY FOR STEP C: YES`).
- [x] **PR1 — CA-VHC internal experiment metrics and CSV integration (Commit `daca566`):** Đã hoàn tất tích hợp metrics evaluator, CSV logger schema 19 cột, automated runner và fixture DEV 160 ca.
- [x] **Pre-PR3 Acceptance Contract defined (Docs 09):** Khóa tiêu chí nghiệm thu trước PR3 ([`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md)) và snapshot ma trận ASCII 48 ca ([`pr3_ascii_baseline_fingerprints.json`](../tests/fixtures/pr3_ascii_baseline_fingerprints.json)).
- [x] **PR2 baseline adapters:** Đã hoàn thành 3 adapter B1, B2, B3 độc lập (TV2 chủ trì; E3 PASS). E4 shared transition interface vẫn chờ TV2+TV4 ký duyệt.
- [ ] **PR3 CompositionState production implementation:** Triển khai mã nguồn cấu trúc trạng thái tổ hợp vào engine sau khi đạt Entry Gate; E3/PR2 đã PASS, còn chờ E4 shared interface agreement của TV2+TV4.
- [ ] **TV1 corpus formal freeze:** TV1 rà soát độ phủ và đóng băng phiên bản benchmark corpus chính thức.
- [ ] **TV3 physical clearance calibration:** TV3 hiệu chuẩn ngưỡng khoảng cách an toàn $0.20\text{ mm}$ vs $0.50\text{ mm}$ trên máy vẽ thật.
- [ ] **PR4 delayed-stroke P0:** Triển khai policy gom nét trễ Nearest Neighbor cơ bản.
- [ ] **Formal benchmark and ablation:** Chạy thực nghiệm chính thức 50 lượt và phân tích kết quả khoa học.

---

### 10.2 Danh Mục Năm Quyết Định Kỹ Thuật Phần Mềm Đã Khóa (Resolved for Software Step C)

Năm quyết định kỹ thuật dưới đây đã được thống nhất giữa TV4 (Project Lead) và TV2 (Stroke Optimization Lead) sau khi TV2 hoàn tất cross-review (verdict: **PASS**), chính thức đóng Bước B và cho phép bắt đầu triển khai phần mềm Bước C:

1. **Quyết định 1 — Ngưỡng khoảng cách an toàn (Clearance Tolerance):**
   - $0.20\text{ mm}$ là giá trị mặc định kỹ thuật ban đầu trong `DiacriticConfig` nhằm bảo toàn tương thích với mã nguồn hiện hành.
   - $0.50\text{ mm}$ là mục tiêu an toàn nghiên cứu cần TV3 hiệu chuẩn thực tế trên máy vẽ vật lý.
   - Toàn bộ giá trị clearance phải được quản lý tập trung qua `DiacriticConfig` khi triển khai Bước C (tuyệt đối không hard-code rải rác).
   - Không tuyên bố $0.50\text{ mm}$ đã được xác nhận thực nghiệm trước khi TV3 hoàn thành đo đạc phần cứng.
2. **Quyết định 2 — Đồng bộ Metric Contract & API Spec:**
   - Internal evaluator (`metrics_evaluator.py`) và structured trace đã hoàn thành và có test bảo vệ.
   - Metric CA-VHC mới chỉ được tích hợp vào public API và log CSV sau khi backend thực sự xuất dữ liệu ổn định và tin cậy.
   - `OmniDraw_API_Spec-4.md` sẽ được cập nhật đồng bộ trong một PR tài liệu riêng sau khi tích hợp phần mềm hoàn tất.
   - Việc API Spec hiện tại còn mô tả cũ về `optimize_time_ms` được ghi nhận là technical/documentation debt đã biết; không sửa API Spec trong đợt này.
3. **Quyết định 3 — Chính sách xử lý nét trễ P0 (Delayed-Stroke Policy):**
   - Step C v1 policy: Viết xong thân từ $\rightarrow$ gom toàn bộ nét phụ/dấu trễ của từ $\rightarrow$ sắp xếp thứ tự vẽ bằng deterministic Nearest Neighbor bắt đầu từ điểm kết thúc nét cuối của thân từ $\rightarrow$ sử dụng original stroke index làm tie-break để chống bất định.
   - Kỹ thuật Exact Enumeration cho $M \le 6$ thuộc phạm vi P1; mô hình cá nhân hóa theo phong cách người viết (Writer Profile) thuộc phạm vi P2.
   - Đây là quyết định thiết kế kiến trúc đã khóa cho Bước C, chưa phải là mã nguồn đã triển khai trong engine hiện tại.
4. **Quyết định 4 — Bộ dữ liệu chuẩn đối chứng (Benchmark Corpus Governance):**
   - Hai tập fixture `BENCHMARK_DEV_CORPUS_20` và `BENCHMARK_HOLDOUT_CORPUS_20` đã tồn tại và vượt qua kiểm thử tính rời nhau ở mức **PROVISIONAL TECHNICAL FIXTURE**.
   - TV1 vẫn có nghĩa vụ rà soát độ phủ ngôn ngữ học/ngữ âm học và chính thức đóng băng (freeze) phiên bản dữ liệu trước khi thực hiện benchmark chính thức.
   - Việc TV1 chưa đóng băng ngữ liệu không cản trở việc triển khai code phần mềm Step C (PR1 và PR3), nhưng ngăn chặn mọi tuyên bố về kết quả thực nghiệm học thuật chính thức. Acceptance suite không lựa chọn, iterate, render hoặc ghi nhận bất kỳ case nào từ `BENCHMARK_HOLDOUT_CORPUS_20`. Mười mẫu nghiệm thu tiếng Việt được lấy hoàn toàn từ `BENCHMARK_DEV_CORPUS_20`; 48 ca ASCII là technical regression fixture độc lập, không thuộc DEV hoặc Holdout corpus tiếng Việt.
5. **Quyết định 5 — Thẩm quyền cho phép bắt đầu triển khai phần mềm Bước C:**
   - TV2 technical cross-review đạt kết luận: **COMPLETED / PASS**.
   - TV4 (Project Lead & Handwriting / CA-VHC Composition Lead) chính thức cho phép bắt đầu triển khai phần mềm Bước C (`READY FOR STEP C: YES`).
   - Việc TV1 đóng băng corpus và TV3 hiệu chuẩn phần cứng máy vẽ được phân định là các cổng kiểm định downstream (validation gates), không phải là blocker cho việc viết mã nguồn phần mềm.
   - Ranh giới thẩm quyền được phân định rõ ràng, không tuyên bố mập mờ "toàn nhóm đã ký duyệt nghiệm thu".

---

### 10.3 Phán Quyết Kỹ Thuật Cuối Cùng (Final Technical Verdict)

```text
═══════════════════════════════════════════════════════════════════════════════════════════
                    KẾT LUẬN RÀ SOÁT ĐỒNG BỘ ĐẶC TẢ CA-VHC (BƯỚC B ➔ BƯỚC C)
═══════════════════════════════════════════════════════════════════════════════════════════
• SPEC STATUS:                 APPROVED AND CLOSED FOR STEP B
• TV2 TECHNICAL CROSS-REVIEW:  PASS
• SOFTWARE STEP C:             AUTHORIZED / IN PROGRESS (PR1 & Pre-PR3 Contract DONE)
• PR3 ACCEPTANCE CONTRACT:     DEFINED (See docs/09_pr3_acceptance_criteria.md)
• PR3 ENTRY GATE:             WAITING FOR E4 (TV2+TV4 Shared Interface Agreement)
• READY FOR STEP C:            YES (Software implementation authorized by TV4)
• FORMAL EXPERIMENT READINESS: NO (Pending TV1 corpus freeze & TV3 hardware calibration)
• HÀNH ĐỘNG KẾ TIẾP:           TV2+TV4 ký duyệt E4; PR2/E3 đã hoàn tất, PR3 chưa bắt đầu
═══════════════════════════════════════════════════════════════════════════════════════════
```

**Đại diện ký duyệt & Phê duyệt:**
- **Thành viên 2** — *Stroke Optimization & Path Planning Lead; owner phần motion/DP của CA-VHC* (Technical Reviewer: PASS)
- **Thành viên 4** — *Project Lead & Handwriting / CA-VHC Composition Lead* (Software Step C Authorized)

---

## 11. Tài Liệu Tham Khảo (References)

1. Graves, A., et al. (2008). *Offline Handwriting Recognition with Multidimensional Recurrent Neural Networks*. Advances in Neural Information Processing Systems (NeurIPS).
2. Plamondon, R., & Maarse, F. J. (1989). *An evaluation of motor models for handwriting analysis and synthesis*. IEEE Transactions on Systems, Man, and Cybernetics, 19(5), 1060–1072.
3. Viterbi, A. J. (1967). *Error bounds for convolutional codes and an asymptotically optimum decoding algorithm*. IEEE Transactions on Information Theory, 13(2), 260–269.
4. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press. (Chương quy hoạch động & đường đi ngắn nhất trên DAG).
5. Unicode Consortium. (2024). *The Unicode Standard, Version 15.1 — Vietnamese Diacritical Marks and Combining Characters*.
6. OmniDraw Technical Specifications:
   - `01_tech-stack.md`: Kiến trúc công nghệ tổng thể và phân công trách nhiệm 4 đường chạy.
   - `02_roadmap.md`: Lộ trình phát triển sản phẩm qua các Sprint, hệ thống P0–P3 và Definition of Done.
   - `03_current-task.md`: Báo cáo tiến độ chi tiết Sprint 1–2 và nhật ký công việc theo ngày.
   - `06_audit_trellis_dag_report.md`: Báo cáo kiểm định toàn diện hiện trạng Trellis DAG (Bước A).
   - `07_diacritic_aware_state_design.md`: Thiết kế kỹ thuật chi tiết không gian trạng thái `CompositionState` (Bước B).
   - `08_handwriting_dataset_spec.md`: Quy chuẩn kỹ thuật bộ dữ liệu chữ viết tay tiếng Việt và Writer Profile (Bước B).
   - `09_pr3_acceptance_criteria.md`: Bộ tiêu chí nghiệm thu trước PR3 (Hợp đồng nghiệm thu kỹ thuật, ma trận ASCII 48 ca và quy chuẩn clearance).
   - `10_nckh_research_plan.md`: Research Freeze Pack, methodology blueprint và khung Chương 3–4; trạng thái chờ cross-review toàn nhóm.
