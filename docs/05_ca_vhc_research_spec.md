# OmniDraw — Đặc Tả Nghiên Cứu & Thiết Kế Kỹ Thuật Lõi CA-VHC
*(Phiên bản Cập nhật Đồng bộ Kiến trúc Bước B & TV2 Technical Cross-Review)*

**Tài liệu:** Khung thuật toán Context-Aware Vietnamese Handwriting Composition (CA-VHC)
**Tác giả / Owner:** Thành viên 2 — Stroke Optimization & Kinematic Planning Lead (Chủ trì Lõi thuật toán CA-VHC)
**Phối hợp kiến trúc & Typography:** Thành viên 4 — Platform, Data & Vietnamese Typography Lead
**Cập nhật lần cuối:** 21/09/2026 (Đồng bộ sau Cross-Review Bước B: `docs/07_diacritic_aware_state_design.md` & `docs/08_handwriting_dataset_spec.md`)
**Trạng thái:** APPROVED WITH CHANGES — Sẵn sàng chuyển giao sang BƯỚC C (Implementation)

---

## Giới thiệu & Phân định quyền sở hữu (Module Ownership Matrix)

Tài liệu này xác lập cơ sở lý thuyết, mô hình toán học hình thức, thiết kế thuật toán tối thiểu và kế hoạch thực nghiệm cho **Context-Aware Vietnamese Handwriting Composition (CA-VHC)** trên máy vẽ 2 trục (pen plotter).

Để bảo đảm tính phân tách trách nhiệm rõ ràng (Separation of Concerns) và tuân thủ kiến trúc đã khóa tại Bước B (`docs/07_diacritic_aware_state_design.md` và `docs/08_handwriting_dataset_spec.md`), quyền sở hữu module và ranh giới kỹ thuật giữa các thành viên được xác lập như sau:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MA TRẬN QUYỀN SỞ HỮU                                   │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ THÀNH VIÊN 4 (Typography)│ MODULE CHUNG (Giao diện)    │ THÀNH VIÊN 2 (Kinematics/DP)  │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ - Tiền xử lý tiếng Việt  │ - Cấu trúc dữ liệu          │ - Mô hình động học đầu bút    │
│   & Unicode NFD          │   `CompositionState`        │   ($D_{penup}, N_{lift},      │
│ - Diacritic positioning  │   (`state.py`)              │    C_{curvature}$)            │
│   (mũ, thanh, móc, nặng) │ - Giao diện chuyển tiếp     │ - Hàm mục tiêu chuyển động    │
│ - Sinh ứng viên glyph    │   `eval_transition(...)`    │   $J_{transition}$            │
│   và dấu (candidates)    │ - Va chạm đường nối         │ - Thuật toán Trellis Viterbi  │
│ - Quản lý font / dataset │   `bridge_collision_cost`   │   DP sequence decoder         │
│   (file 08 spec)         │ - Viterbi Trellis runner    │ - Quy hoạch đường đi (path)   │
│ - Va chạm nội ký tự      │   `optimize_word_dag(...)`  │ - Benchmark năng lượng, quãng │
│   $C_{internal\_collision}$│                           │   đường và thời gian vẽ bút   │
│ - Đóng gói               │                             │ - Trọng số chuyển động        │
│   `CompositionState`     │                             │   ($w_1, w_2, w_3, w_4$)      │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

### Chi tiết phân công trách nhiệm:

1. **Thành viên 4 (Platform, Data & Vietnamese Typography Lead):**
   - Tiền xử lý chuỗi tiếng Việt, chuẩn hóa Unicode NFD;
   - Cấu trúc ký tự tổ hợp (composite character structure);
   - Mô hình định vị dấu thanh/mũ/móc (diacritic positioning model, anchor points, clearance zones);
   - Sinh ứng viên biến thể thân chữ và dấu (glyph/diacritic candidate generation);
   - Quản lý font pack, variant pool và quy chuẩn bộ dữ liệu chữ viết tay (`docs/08_handwriting_dataset_spec.md`);
   - Giải quyết va chạm nội ký tự (internal collision resolution giữa thân chữ và dấu);
   - Xác định bounding box và anchor offset của dấu;
   - Đóng gói trạng thái tổ hợp `CompositionState = (base_variant, diacritic_candidate)` phục vụ bài toán tối ưu.

2. **Thành viên 2 (Stroke Optimization & Kinematic Planning Lead - Owner tài liệu nghiên cứu CA-VHC):**
   - Mô hình chuyển động của đầu bút vẽ (pen kinematics: penup distance, lift count, curvature continuity, stroke direction transition);
   - Hàm mục tiêu chuyển động (motion objective terms: $D_{\text{penup}}, N_{\text{lift}}, C_{\text{curvature}}$);
   - Đánh giá va chạm đường nối liên ký tự (cross-character bridge collision evaluation) trong không gian tọa độ thế giới (world coordinates);
   - Thuật toán tối ưu chuỗi/đường đi trên Trellis (Viterbi trellis search, DP sequence decoder, path optimization);
   - Benchmark định lượng năng lượng, quãng đường di chuyển bút và thời gian vẽ thực tế.

3. **Module chung / Giao diện tích hợp (Shared Interface — TV4 + TV2):**
   - Giao diện state giữa TV4 và TV2: Cấu trúc dữ liệu `CompositionState` (`backend/handwriting/state.py`);
   - Hàm tính chi phí chuyển tiếp `eval_transition(s_prev, s_next)`: kết hợp kinematic cost của TV2 và bridge obstacle avoidance;
   - Logic kiểm tra va chạm đường nối liên ký tự (cross-character bridge collision) giữa điểm thoát ký tự trước và điểm đón ký tự sau với các ứng viên dấu xung quanh;
   - Viterbi Trellis runner (`optimize_word_dag`): nhận danh sách ứng viên tổ hợp `List[List[CompositionState]]` từ TV4 và tìm ra chuỗi trạng thái tối ưu toàn cục.

> [!IMPORTANT]
> **Nguyên tắc trung thực học thuật & Code-first:**
> - Mọi viện dẫn mã nguồn trong tài liệu này lấy **tên file và tên hàm/lớp làm nguồn định danh chính** (line number chỉ là thông tin tham khảo phụ).
> - Tài liệu phân biệt rõ ràng giữa **Mục tiêu thiết kế (Design Target)** và **Kết quả đo lường thực nghiệm (Measured Result)**; tuyệt đối không khẳng định "real-time guaranteed" hoặc "instant execution" khi chưa có số liệu đo đạc thực tế trên phần cứng.
> - Engine hoàn toàn **không** nhận là hiểu ngữ nghĩa (semantics) hay ngữ âm học (phonetics/phonology); mọi cơ chế xử lý dấu tiếng Việt đều dựa trên **quy tắc chính tả hình học (orthographic geometry)** và chuẩn phân rã Unicode NFD.

---

## 1. Ba Câu Hỏi Nghiên Cứu & Giả Thuyết Khoa Học

Khung nghiên cứu của CA-VHC tập trung giải quyết ba câu hỏi nghiên cứu (Research Questions — RQ) độc lập nhưng bổ trợ chặt chẽ cho nhau:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 KHUNG NGHIÊN CỨU CA-VHC                                │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ RQ1: Nối nét & Động học  │ RQ2: Tránh va chạm dấu      │ RQ3: Hiệu năng & Khả thi      │
│  - Giảm pen-up distance  │  - Clearance envelope dấu   │  - Độ phức tạp Viterbi DP     │
│  - Giảm pen-lift count   │  - Hard collision rejection │  - Tính trơn hình học C1      │
│  - Kiểm soát độ dài nét  │  - Tách va chạm nội/cầu nối │  - Target latency vs phần cứng│
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
  *Việc áp dụng giải thuật quy hoạch động Trellis DAG (Viterbi DP) trên không gian trạng thái tổ hợp `CompositionState` để đồng thời lựa chọn biến thể glyph và vị trí dấu theo ngữ cảnh có thể giảm đáng kể quãng đường di chuyển pen-up ($D_{\text{penup}}$) và số lần nhấc bút ($N_{\text{lift}}$) so với phương pháp render tĩnh (B1) và Trellis chỉ tối ưu chuyển động trên biến thể thân chữ, chưa nhận thức dấu (B2) hay không, trong khi vẫn duy trì tổng chiều dài nét vẽ tiếp xúc giấy ở mức tương đương?*

- **Giả thuyết H1.1 (Giảm quãng đường pen-up):**
  Gọi $\Delta D_{\text{B1}} = \frac{D_{\text{penup}}(\text{B1}) - D_{\text{penup}}(\text{CA-VHC})}{D_{\text{penup}}(\text{B1})}$ và $\Delta D_{\text{B2}} = \frac{D_{\text{penup}}(\text{B2}) - D_{\text{penup}}(\text{CA-VHC})}{D_{\text{penup}}(\text{B2})}$.
  - **FAIL (Ưu tiên 1):** $(\Delta D_{\text{B1}} < 15.0\%)$ **HOẶC** $(\Delta D_{\text{B2}} < 5.0\%)$.
  - **PASS (Ưu tiên 2):** $(\Delta D_{\text{B1}} \ge 25.0\%)$ **VÀ** $(\Delta D_{\text{B2}} \ge 10.0\%)$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại (tức là $\Delta D_{\text{B1}} \ge 15.0\%$ và $\Delta D_{\text{B2}} \ge 5.0\%$, nhưng chưa đồng thời đạt $\Delta D_{\text{B1}} \ge 25.0\%$ và $\Delta D_{\text{B2}} \ge 10.0\%$).

- **Giả thuyết H1.2 (Giảm số lần nhấc bút):**
  Gọi $\Delta N_{\text{lift}} = \frac{N_{\text{lift}}(\text{B1}) - N_{\text{lift}}(\text{CA-VHC})}{N_{\text{lift}}(\text{B1})}$ trên các từ hỗ trợ nối nét.
  - **FAIL (Ưu tiên 1):** $\Delta N_{\text{lift}} < 20.0\%$.
  - **PASS (Ưu tiên 2):** $\Delta N_{\text{lift}} \ge 35.0\%$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại (tức là $20.0\% \le \Delta N_{\text{lift}} < 35.0\%$).

- **Giả thuyết H1.3 (Kiểm soát chiều dài nét vẽ tiếp xúc giấy):**
  Gọi tỷ lệ tăng chiều dài nét vẽ là $\Delta L = \frac{total\_path\_length\_mm(\text{CA-VHC}) - total\_path\_length\_mm(\text{B1})}{total\_path\_length\_mm(\text{B1})}$.
  - **FAIL (Ưu tiên 1):** $\Delta L > 15.0\%$.
  - **PASS (Ưu tiên 2):** $\Delta L \le 10.0\%$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại (tức là $10.0\% < \Delta L \le 15.0\%$).

---

### 1.2. RQ2: Tránh Va Chạm Giữa Dấu Tiếng Việt, Thân Chữ và Nét Nối

- **Câu hỏi nghiên cứu (RQ2):**
  *Cơ chế đồng tối ưu trạng thái tổ hợp `CompositionState` kết hợp vùng cản trở an toàn của dấu (`bridge diacritic obstacle avoidance`) vào hàm mục tiêu Trellis DAG có loại bỏ được hoàn toàn các giao cắt hình học giữa cầu nối và dấu phụ/dấu thanh, đồng thời duy trì khoảng cách an toàn tối thiểu giữa nét nối và tổ hợp dấu chồng tầng so với Trellis DAG chưa có nhận thức dấu (B3) hay không?*

- **Giả thuyết H2.1 (Triệt tiêu va chạm hình học):**
  - **FAIL (Ưu tiên 1):** Phát hiện $collision\_count \ge 1$ trên bất kỳ mẫu kiểm thử nào.
  - **PASS (Ưu tiên 2):** $collision\_count = 0$ trên $100\%$ mẫu thử nghiệm.
  - **INCONCLUSIVE (Ưu tiên 3):** Không áp dụng (tiêu chuẩn nhị phân cứng).

- **Giả thuyết H2.2 (Khoảng cách an toàn tối thiểu với dấu):**
  Với cấu hình chuẩn $font\_size\_mm = 7.0\text{ mm}$, gọi $d_{\min} = minimum\_diacritic\_clearance\_mm$.
  - **FAIL (Ưu tiên 1):** $d_{\min} < 0.20\text{ mm}$ (xâm phạm vùng ngòi bút cơ sở $0.20\text{ mm}$).
  - **PASS (Ưu tiên 2):** $d_{\min} \ge 0.50\text{ mm}$ (đạt biên an toàn nghiên cứu mục tiêu).
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại ($0.20\text{ mm} \le d_{\min} < 0.50\text{ mm}$).
  > [!NOTE]
  > **Ghi chú về ngưỡng an toàn:** Hiện tại mã nguồn nguyên mẫu sử dụng giá trị mặc định kỹ thuật $0.20\text{ mm}$, trong khi tài liệu nghiên cứu đề xuất biên an toàn lý tưởng là $0.50\text{ mm}$ cho các ngòi bút máy vẽ thực tế ($0.3\text{ mm} - 0.5\text{ mm}$). Hạng mục này được đánh dấu là `[OPEN REVIEW DECISION: 0.20mm vs 0.50mm]` để hai nhóm thử nghiệm và tinh chỉnh trên máy vẽ vật lý trong Bước C.

---

### 1.3. RQ3: Hiệu Năng Tính Toán & Tính Khả Thi Thi Công Trên Máy Vẽ

- **Câu hỏi nghiên cứu (RQ3):**
  *Giải thuật CA-VHC trên không gian trạng thái $K_{\text{raw}} \le 9$ có duy trì được thời gian tính toán trong giới hạn tương tác người dùng và sinh ra quỹ đạo vector đơn trị, trơn tiếp tuyến hình học $C^1$, tạo tiền đề khả thi để thi công an toàn trên máy vẽ 2 trục hay không?*

> [!NOTE]
> **Ranh giới tuyên bố khoa học (Scientific Scope Boundary):**
> Về mặt thuật toán, TV2 chứng minh và bảo đảm **tính trơn tiếp tuyến hình học ($C^1$ geometric smoothness)** của đường cong vector centerline. Các hệ quả cơ lý tính trên thực tế (độ rung giật động học của đầu bút, mức độ hao mòn cơ khí, thời gian thi công thực tế) là giả thuyết ngoại suy và **bắt buộc phải được kiểm chứng, xác nhận bằng số liệu thực nghiệm phần cứng do TV3 đo đạc trên máy AxiDraw**.

- **Giả thuyết H3.1 (Thời gian tính toán giải thuật Viterbi DP):**
  Thời gian giải quy hoạch động trên từng từ ($N \le 7$ ký tự) đo độc lập qua `time.perf_counter()`. Gọi $M = \text{Median}(optimize\_time\_ms)$ và $P = \text{p95}(optimize\_time\_ms)$.
  - **FAIL (Ưu tiên 1):** $(M > 15.0\text{ ms})$ **HOẶC** $(P > 30.0\text{ ms})$.
  - **PASS (Ưu tiên 2):** $(M \le 5.0\text{ ms})$ **VÀ** $(P \le 10.0\text{ ms})$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại (tức là $M \le 15.0\text{ ms}$ và $P \le 30.0\text{ ms}$, nhưng chưa đồng thời đạt $M \le 5.0\text{ ms}$ và $P \le 10.0\text{ ms}$).
  *(Lưu ý: Đây là Design Target, không tuyên bố "real-time guaranteed" khi chưa có benchmark đo lường chính thức).*

- **Giả thuyết H3.2 (Độ trơn hình học & Kiểm soát đổi hướng tiếp tuyến):**
  Gọi $\Delta C_{\text{curv}} = \frac{curvature\_cost(\text{B2}) - curvature\_cost(\text{CA-VHC})}{curvature\_cost(\text{B2})}$ và biến cố $has\_acute\_turn$ là sự xuất hiện của bất kỳ góc lệch tiếp tuyến nào $> 120^\circ$ trên cầu nối.
  - **FAIL (Ưu tiên 1):** $(\Delta C_{\text{curv}} \le 0.0\%)$ **HOẶC** $(has\_acute\_turn == \text{True})$.
  - **PASS (Ưu tiên 2):** $(\Delta C_{\text{curv}} \ge 15.0\%)$ **VÀ** $(has\_acute\_turn == \text{False})$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại (tức là $has\_acute\_turn == \text{False}$ và $0.0\% < \Delta C_{\text{curv}} < 15.0\%$).

---

## 2. Mô Hình Toán Học Hình Thức

### 2.1. Không Gian Trạng Thái Tổ Hợp (`CompositionState`)

Xét một từ tiếng Việt gồm chuỗi $N$ ký tự liên tiếp: $\mathbf{C} = (c_1, c_2, \dots, c_N)$.

Tại mỗi vị trí $i \in \{1, \dots, N\}$, ký tự $c_i$ sau khi phân rã Unicode NFD gồm:
- Ký tự gốc (base character): $b_i \in \Sigma_{\text{base}}$ (ví dụ: `a`, `e`, `o`, `d`, `K`).
- Tập dấu đi kèm: $\mathcal{A}_i = \{a_{i,1}, a_{i,2}, \dots\}$ (ví dụ: nón `\u0302`, sắc `\u0301`, móc `\u031b`, hoặc $\emptyset$ nếu là ký tự không dấu).
- Thông số biến đổi hình học cục bộ: tỷ lệ phóng/thu $\mathbf{s}_i = [s_{x,i}, s_{y,i}]^T$, độ lệch tọa độ thế giới $\mathbf{o}_i = [x_i, y_i]^T$, chiều rộng ký tự $w_i$, và trọng tâm ngang $cx_i$.

Khác với mô hình cũ xem dấu là chướng ngại vật tĩnh hoặc chỉ tối ưu trên biến thể thân chữ, kiến trúc Bước B (`docs/07_diacritic_aware_state_design.md`) định nghĩa mỗi nút trong đồ thị Trellis là một **Trạng thái tổ hợp (CompositionState)**:
$$s_{i, j} = \left( v_{\text{base}}, c_{\text{diacritic}} \right) \in \mathcal{S}_i$$

Trong đó:
- $v_{\text{base}} \in \mathcal{V}_{\text{base}, i}$ là biến thể thân chữ cái chọn từ tập ứng viên thân chữ ($K_{\text{base}} \le 3$, ví dụ: `std`, `alt`, `flourish`).
- $c_{\text{diacritic}} \in \mathcal{C}_{\text{diacritic}, i}$ là ứng viên định vị dấu chọn từ tập vị trí khả dĩ do TV4 sinh ra ($K_{\text{diacritic}} \le 3$, ví dụ: `canonical`, `safe_left`, `safe_right`). Đối với ký tự không mang dấu, $c_{\text{diacritic}} = \emptyset$ và $K_{\text{diacritic}} = 1$.

#### Cận trên không gian trạng thái lý thuyết (Theoretical Raw State Bound)
Số lượng trạng thái tổ hợp thô tại mỗi vị trí ký tự bị chặn trên bởi:
$$K_{\text{raw}, i} = |\mathcal{S}_i| = K_{\text{base}} \times K_{\text{diacritic}} \le 3 \times 3 = 9$$

> [!IMPORTANT]
> **Đính chính về số lượng trạng thái:**
> - Giá trị $K_{\text{raw}} \le 9$ là **Theoretical Raw State Bound** (Cận trên lý thuyết của không gian trạng thái thô), **KHÔNG PHẢI** là kết quả benchmark runtime và **KHÔNG PHẢI** là số lượng trạng thái bị cắt tỉa cứng (fixed pruned size).
> - Trong giai đoạn P0 / Bước C v1, hệ thống **KHÔNG sử dụng các kỹ thuật cắt tỉa phỏng đoán (heuristic pruning)** như top-6 cutoff, beam search hay early pruning.
> - Toàn bộ tối đa 9 trạng thái tổ hợp hợp lệ đều được đưa vào giải thuật Viterbi. Các trạng thái chỉ bị loại bỏ nếu vi phạm **ràng buộc cứng (hard constraints)** như va chạm nội ký tự nặng hoặc vượt khung biên (bounding box).
> - Với $K_{\text{raw}} \le 9$, số lượng đánh giá chuyển tiếp giữa hai cột Trellis tối đa là $9 \times 9 = 81$ phép tính, hoàn toàn nằm trong khả năng xử lý của CPU thông thường trong khoảng thời gian $< 1\text{ ms}$.

Mỗi trạng thái tổ hợp $s_{i, j} \in \mathcal{S}_i$ tương ứng với cấu trúc dữ liệu `CompositionState` (`backend/handwriting/state.py`) và được đặc trưng bởi:
$$s_{i, j} = \left( \mathcal{S}_{\text{local}}, \mathbf{p}_{\text{in}}, \mathbf{p}_{\text{out}}, \mathbf{v}_{\text{in}}, \mathbf{v}_{\text{out}}, \text{can\_in}, \text{can\_out}, \text{bbox}_{\text{local}}, c_{\text{leg}}, c_{\text{place}}, c_{\text{int\_coll}} \right)$$

Trong đó:
- $\mathcal{S}_{\text{local}} = \mathcal{S}_{\text{base}} \cup \mathcal{S}_{\text{diac}}$: Tập các nét polyline cục bộ trong hệ tọa độ chuẩn hóa font (0..14 đơn vị), gồm nét thân chữ và nét dấu đã ghép.
- $\mathbf{p}_{\text{in}}, \mathbf{p}_{\text{out}} \in \mathbb{R}^2$: Tọa độ cục bộ điểm vào nét đầu tiên và điểm ra nét cuối cùng của thân chữ.
- $\mathbf{v}_{\text{in}}, \mathbf{v}_{\text{out}} \in \mathbb{R}^2$: Vector tiếp tuyến đơn vị tại điểm vào và điểm ra:
  $$\mathbf{v}_{\text{in}} = \frac{S_1[1] - S_1[0]}{\|S_1[1] - S_1[0]\|}, \quad \mathbf{v}_{\text{out}} = \frac{S_{\text{last}}[-1] - S_{\text{last}}[-2]}{\|S_{\text{last}}[-1] - S_{\text{last}}[-2]\|}$$
- $\text{can\_in}, \text{can\_out} \in \{0, 1\}$: Cờ nhị phân cho phép nhận nét nối vào và thoát nét nối ra.
- $\text{bbox}_{\text{local}}$: Hộp bao hình học cục bộ $[x_{\min}, y_{\min}, x_{\max}, y_{\max}]$.
- $c_{\text{leg}}, c_{\text{place}}, c_{\text{int\_coll}}$: Các thành phần chi phí nội tại của trạng thái tổ hợp do TV4 tính toán.

---

### 2.2. Ánh Xạ Sang Tọa Độ Thế Giới & Quy Ước Hệ Tọa Độ (Coordinate Conventions)

Để bảo đảm tính nhất quán toán học giữa hình học glyph và chuyển động thực tế của máy vẽ, hệ thống áp dụng quy ước tọa độ hai cấp:

1. **Hệ tọa độ cục bộ (Local Coordinates):**
   - Đơn vị font chuẩn hóa: $0..14$ đơn vị font, trong đó chiều cao thiết kế $H_{\text{font}} = 14.0$.
   - Các nét trong `CompositionState` (`strokes_local`), điểm đón $\mathbf{p}_{\text{in}}$, điểm thoát $\mathbf{p}_{\text{out}}$ và vector tiếp tuyến cục bộ được định nghĩa trong hệ tọa độ này.
   - Chi phí nội ký tự $C_{\text{state}}$ do TV4 đánh giá trên hệ tọa độ cục bộ (hoặc sau khi scale tỷ lệ glyph).

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

Để phản ánh chính xác kiến trúc Bước B và loại bỏ hoàn toàn việc tính trùng lặp chi phí (double-counting), hàm mục tiêu tổng thể của CA-VHC được phân rã thành hai cấp độc lập: **Chi phí trạng thái tổ hợp ($C_{\text{state}}$)** và **Chi phí chuyển tiếp chuyển động ($J_{\text{transition}}$)**:

$$J_{\text{total}}(\mathbf{s}, \mathbf{a}) = \sum_{i=1}^N C_{\text{state}}(s_i) + \sum_{i=1}^{N-1} J_{\text{transition}}(s_i, s_{i+1}, a_i)$$

```
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
Chi phí gắn liền với từng trạng thái tổ hợp $s = (v_{\text{base}}, c_{\text{diacritic}})$, độc lập với ký tự đứng trước hay đứng sau:
$$C_{\text{state}}(s) = w_{4a} \cdot C_{\text{internal\_collision}}(s) + w_5 \cdot C_{\text{legibility}}(s) + w_6 \cdot C_{\text{placement}}(s)$$

Trong đó:
- $C_{\text{internal\_collision}}(s)$: Chi phí phạt va chạm giữa nét thân chữ và nét dấu trong cùng ký tự (nếu có xâm phạm nhẹ; nếu va chạm nặng, ứng viên bị loại bỏ ngay từ bước sinh state).
- $C_{\text{legibility}}(s)$: Chi phí độ dễ đọc của biến thể thân chữ ($0.0$ cho `std`, phạt nhẹ $0.02 - 0.05$ cho biến thể hoa mỹ hoặc biến thể hiếm).
- $C_{\text{placement}}(s)$: Chi phí lệch vị trí dấu so với vị trí chuẩn thẩm mỹ (canonical typography anchor).
- **Ghi chú trọng số:** $w_{4a}, w_5, w_6$ được đánh dấu là `[REQUIRES EXPERIMENTAL TUNING]` — giá trị cụ thể sẽ được xác lập qua thực nghiệm của TV4 tại Bước C.

#### Cấp 2: Chi phí chuyển tiếp động học ($J_{\text{transition}}$ — Thuộc TV2 chủ trì)
Chi phí chuyển tiếp giữa hai trạng thái liên tiếp $u \in \mathcal{S}_{i-1}$ và $w \in \mathcal{S}_i$:

##### Trường hợp 1: Nhấc bút ($a = \text{LIFT}$)
- $D_{\text{penup}} = \|\mathbf{P}_{\text{entry}}(w) - \mathbf{P}_{\text{exit}}(u)\|$ ($mm$ trong tọa độ thế giới).
- $N_{\text{lift}} = 1$.
- $C_{\text{curvature}} = 0.0$, $C_{\text{bridge\_collision}} = 0.0$ (ngòi bút di chuyển trên không).
$$J_{\text{lift}}(u, w) = w_1 \cdot D_{\text{penup}}(u, w) + w_2 \cdot 1.0$$

##### Trường hợp 2: Nối nét liên tục ($a = \text{CONNECT}$)
- $D_{\text{penup}} = 0.0$, $N_{\text{lift}} = 0$.
- Chi phí độ cong tiếp tuyến ($C_{\text{curvature}}$):
  Với vector chuyển dịch đơn vị thế giới $\mathbf{u}_d = \frac{\mathbf{P}_{\text{entry}}(w) - \mathbf{P}_{\text{exit}}(u)}{\|\mathbf{P}_{\text{entry}}(w) - \mathbf{P}_{\text{exit}}(u)\|}$:
  $$\cos\theta_1 = \text{clip}(\mathbf{V}_{\text{exit}}(u) \cdot \mathbf{u}_d, -1.0, 1.0), \quad \cos\theta_2 = \text{clip}(\mathbf{u}_d \cdot \mathbf{V}_{\text{entry}}(w), -1.0, 1.0)$$
  $$C_{\text{curvature}} = (1.0 - \cos\theta_1) + (1.0 - \cos\theta_2) \in [0.0, 4.0]$$
- Chi phí va chạm đường nối thế giới ($C_{\text{bridge\_collision}}$):
  Kiểm tra tương tác giữa cầu nối Bézier thế giới $\mathcal{B}(u, w)$ với tập nét chướng ngại vật xung quanh $\mathcal{S}_{\text{obstacles}}$ (bao gồm thân chữ và dấu của ký tự $i-1$ và $i$):
  $$C_{\text{bridge\_collision}} = \text{Penalty}_{\text{geom}} + \text{Cost}_{\text{obstacle}}(\mathcal{B})$$
  với $\text{Penalty}_{\text{geom}} = 2.0$ nếu $\Delta x \le 0.0$ và $+0.4 \cdot (d - 8.0)$ nếu $d > 8.0\text{ mm}$.
  Nếu phát hiện cắt ngang đoạn thẳng bất kỳ (`segments_intersect == True`): $C_{\text{bridge\_collision}} \to +\infty$.
$$J_{\text{conn}}(u, w) = w_3 \cdot C_{\text{curvature}}(u, w) + w_4 \cdot C_{\text{bridge\_collision}}(u, w)$$

##### Chi phí chuyển tiếp tối ưu giữa 2 node:
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

Để tránh nhầm lẫn giữa hai bài toán va chạm có bản chất vật lý và không gian tính toán khác nhau, hệ thống phân định:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          PHÂN TÁCH HAI BÀI TOÁN VA CHẠM                                │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│ 1. VA CHẠM NỘI KÝ TỰ (Internal Collision) │ 2. VA CHẠM CẦU NỐI (Bridge Collision)      │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ - Phạm vi: Bên trong 1 ký tự              │ - Phạm vi: Giữa ký tự i-1 và ký tự i       │
│ - Tương tác: Nét thân chữ vs Nét dấu      │ - Tương tác: Cầu nối Bézier vs Thân + Dấu  │
│ - Không gian: Tọa độ cục bộ (Local BBox)  │ - Không gian: Tọa độ thế giới (World mm)   │
│ - Chủ trì: THÀNH VIÊN 4                   │ - Chủ trì: THÀNH VIÊN 2 + THÀNH VIÊN 4     │
│ - Thời điểm: Sinh ứng viên state          │ - Thời điểm: Đánh giá transition DP        │
│ - Cơ chế: Loại bỏ ứng viên va chạm nặng   │ - Cơ chế: Hard reject -> ép LIFT nếu cắt;   │
│   (hard cut); phạt nhẹ vào C_state        │   phạt mềm nếu xâm phạm clearance          │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

1. **Va chạm nội ký tự ($C_{\text{internal\_collision}}$):**
   - Xảy ra khi nét của diacritic candidate đè lên nét của base variant (ví dụ dấu mũ đè vào đỉnh chữ `a`, `o`, `e`).
   - Thuộc trách nhiệm của **Thành viên 4** trong quá trình sinh ứng viên dấu.
   - Nếu khoảng cách vi phạm nghiêm trọng ngưỡng va chạm cơ học, TV4 loại bỏ hoàn toàn ứng viên đó khỏi candidate pool (hard pruning). Nếu chỉ chạm nhẹ trong biên an toàn cho phép, TV4 tính điểm phạt vào $C_{\text{internal\_collision}}(s)$ trong $C_{\text{state}}(s)$.

2. **Va chạm đường nối liên ký tự ($C_{\text{bridge\_collision}}$):**
   - Xảy ra khi đường nối bút (ligature bridge) từ điểm thoát của ký tự $i-1$ đến điểm đón của ký tự $i$ cắt qua thân chữ hoặc dấu phụ của các ký tự xung quanh.
   - Thuộc trách nhiệm phối hợp của **Thành viên 2 và Thành viên 4** trong hàm `eval_transition`.
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

## 3. Định Nghĩa Chuẩn Hóa Bốn Baseline / Phương Pháp Đối Chứng

Để đánh giá khoa học và bóc tách hiệu quả đóng góp của từng thành phần trong CA-VHC, nghiên cứu thiết lập 4 phương pháp đối chứng chuẩn hóa:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MA TRẬN ĐỐI CHỨNG CA-VHC                               │
├─────────────────────┬─────────────────────┬─────────────────────┬──────────────────────┤
│ B1: Static Glyphs   │ B2: Pure Motion     │ B3: Static          │ Proposed CA-VHC      │
│     Renderer        │     Trellis         │     Diacritic Layout│ (Co-Optimization)    │
├─────────────────────┼─────────────────────┼─────────────────────┼──────────────────────┤
│ - Luôn nhấc bút     │ - Viterbi DP trên   │ - Tối ưu/điều chỉnh │ - Trellis trên       │
│   giữa các chữ cái  │   biến thể thân chữ │   vị trí dấu bằng   │   CompositionState   │
│ - Chỉ dùng variant  │ - Dấu đặt cố định   │   quy tắc typography│ - Đồng tối ưu thân chữ│
│   canonical 'std'   │   (canonical static)│   tĩnh              │   và vị trí dấu      │
│ - Dấu đặt mặc định  │ - Chưa nhận thức    │ - Không đồng tối ưu │ - Tránh va chạm cầu  │
│ - Luôn chọn LIFT    │   dấu khi nối nét   │   chuyển động       │   nối và dấu triệt để│
└─────────────────────┴─────────────────────┴─────────────────────┴──────────────────────┘
```

### 3.1. Baseline 1: Static Glyphs Renderer (B1)
- **Bản chất:** Mô phỏng phương pháp kết xuất ký tự nét đơn tĩnh truyền thống (canonical `std`, luôn `LIFT`).
- **Hành vi:** Tắt toàn bộ Trellis DAG; chỉ dùng duy nhất biến thể canonical `std` ($K_{\text{base}} = 1$); dấu đặt ở vị trí mặc định; mọi bước chuyển tiếp liên ký tự đều nhấc bút ($a \equiv \text{LIFT}$); số lần nhấc bút giữa các thân chữ luôn là $N - 1$.
- **Mục đích đối chứng:** Xác lập mốc sàn về quãng đường pen-up tối đa và số lần nhấc bút tối đa.

### 3.2. Baseline 2: Pure Motion Trellis (B2)
- **Bản chất:** Thuật toán Viterbi DP trên các biến thể thân chữ, chưa nhận thức dấu tiếng Việt.
- **Hành vi:** Không gian trạng thái chỉ gồm $K_{\text{base}} \le 3$ biến thể thân chữ. Dấu được đặt cố định ở vị trí canonical tĩnh hoặc sinh sau khi đã giải xong Trellis. Cầu nối không kiểm tra va chạm với nét dấu.
- **Mục đích đối chứng:** Cô lập lợi ích của việc nối nét thân chữ thuần túy, bộc lộ các lỗi va chạm dấu khi chưa có nhận thức dấu (`diacritic-unaware`).

### 3.3. Baseline 3: Static Diacritic Layout (B3)
- **Bản chất:** Tối ưu hoặc điều chỉnh vị trí dấu bằng quy tắc typography tĩnh, không đồng tối ưu chuyển động toàn cục.
- **Hành vi:** Dấu được điều chỉnh tránh va chạm thân chữ bằng quy tắc bounding box / anchor dịch chuyển cục bộ, nhưng các quyết định nối nét giữa các ký tự không được đồng tối ưu chuyển động toàn cục (không xét đồng thời độ cong tiếp tuyến $C_{\text{curvature}}$ và chi phí nhấc bút $N_{\text{lift}}$).
- **Mục đích đối chứng:** Chứng minh rằng việc chỉ tối ưu hình học dấu tĩnh mà không kết hợp đồ thị chuyển động động học sẽ dẫn đến quỹ đạo bút gãy khúc hoặc quãng đường pen-up lớn.

### 3.4. Proposed Method: Context-Aware Vietnamese Handwriting Composition (CA-VHC)
- **Bản chất:** Đồng tối ưu `CompositionState` $(v_{\text{base}}, c_{\text{diacritic}})$ và chuyển động, giải bằng Viterbi DP toàn cục theo từng từ.
- **Hành vi:** Đồng thời chọn biến thể thân chữ, vị trí dấu khả dĩ và quyết định nối nét/nhấc bút sao cho cực tiểu hóa $J_{\text{total}}$, bảo đảm $collision\_count = 0$ và đạt độ trơn hình học $C^1$.

---

## 4. Thiết Kế Diacritic-Aware DAG & Giới Hạn Phạm Vi Nét Trễ

### 4.1. Biểu Diễn Hình Học & Vùng Cấm An Toàn

```
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
  > `[OPEN REVIEW DECISION: 0.20mm vs 0.50mm]` — Ngưỡng khoảng cách an toàn sẽ được đo kiểm thực tế trên máy vẽ trong Bước C để chốt giá trị dung hòa giữa thẩm mỹ nét vẽ và độ dày vệt mực vật lý.

### 4.2. Cơ Chế Đưa Dấu Vào Trellis DAG Qua `CompositionState`

Khác với quan điểm cũ coi dấu là chướng ngại vật cố định hoàn toàn, kiến trúc Bước B xác định: **Dấu tiếng Việt là một biến tối ưu hữu hạn (finite search candidate)** do TV4 cung cấp trong `CompositionState`:

1. **Sinh ứng viên dấu (Candidate Generation — TV4):**
   Với mỗi ký tự mang dấu, TV4 sinh tối đa 3 ứng viên vị trí/hình dáng dấu ($K_{\text{diacritic}} \le 3$):
   - `canonical`: Vị trí chuẩn typographic theo trọng tâm glyph;
   - `safe_left`: Dấu dịch chuyển nhẹ sang trái khi phía bên phải có nét thoát cao hoặc ascender;
   - `safe_right`: Dấu dịch chuyển nhẹ sang phải khi phía bên trái có nét vào vướng víu.
2. **Ghép trạng thái tổ hợp (Composition — TV4):**
   Tổ hợp với $K_{\text{base}} \le 3$ biến thể thân chữ tạo ra tối đa $K_{\text{raw}} \le 9$ trạng thái `CompositionState`.
3. **Đánh giá chuyển tiếp thế giới (World Transition — TV2):**
   TV2 nhận các trạng thái tổ hợp đã chuyển sang tọa độ thế giới và đánh giá va chạm của cầu nối với toàn bộ nét thân chữ và nét dấu xung quanh trong hàm `bridge_collision_cost`.

### 4.3. Phân Định Collision Cứng vs Penalty Mềm Trên Cầu Nối

1. **Ràng buộc cứng (Hard Collision Rejection):**
   Nếu đoạn thẳng của cầu nối $\mathcal{B}$ cắt ngang bất kỳ đoạn thẳng nào của nét thân hoặc nét dấu (`segments_intersect == True`):
   $$C_{\text{bridge\_collision}} = +\infty \implies J_{\text{conn}} = +\infty$$
   Quyết định $\text{CONNECT}$ bị loại trừ ngay lập tức; giải thuật bắt buộc chọn $\text{LIFT}$.
2. **Penalty mềm (Soft Clearance Penalty):**
   Nếu khoảng cách $\text{dist} < \delta_{\text{clearance}}$ nhưng không giao cắt:
   $$\text{penetration} = \frac{\delta_{\text{clearance}} - \text{dist}}{\delta_{\text{clearance}}} \in (0.0, 1.0]$$
   $$C_{\text{bridge\_collision}} = 2.0 + 4.0 \cdot \text{penetration}$$

### 4.4. Quy Hoạch Thứ Tự Nét Trễ (Delayed-Stroke Ordering) & Ranh Giới Phạm Vi (Scope Boundary)

> [!IMPORTANT]
> **Ranh giới kỹ thuật: Bài toán WHERE vs Bài toán WHEN:**
> - **Bước C v1 tập trung giải quyết bài toán WHERE:** Lựa chọn biến thể thân chữ và vị trí dấu tối ưu tại chỗ thông qua giải thuật Viterbi DP trên `CompositionState`, bảo đảm không va chạm và trơn tiếp tuyến.
> - **Bài toán WHEN (Delayed-Stroke Ordering):** Chiến lược gom toàn bộ dấu thanh/mũ vẽ sau cùng của cả từ hoặc cả dòng để tối ưu thứ tự nhấc bút là một chiến lược nâng cao (advanced scheduling), **NẰM NGOÀI phạm vi cốt lõi của Bước C v1** và được xếp lịch triển khai dưới dạng tính năng mở rộng thực nghiệm ở Bước C v2.

#### Cơ sở lý thuyết của Delayed-Stroke Ordering (Dành cho nghiên cứu mở rộng v2):
Tập hợp $M$ nét thứ cấp của một từ $\mathcal{D}_{\text{word}} = \{d_1, d_2, \dots, d_M\}$ bao gồm: dấu thanh, dấu phụ nguyên âm, gạch ngang đ/t, chấm i/j.
1. **Trường hợp $M \le 6$ (chiếm $\ge 99\%$ các từ tiếng Việt):**
   Không gian hoán vị tối đa $M! \le 6! = 720$. Áp dụng giải thuật **vét cạn chính xác (Exact Enumeration)** để tìm thứ tự $\pi^*$ đạt cực tiểu toàn cục quãng đường pen-up thực tế xuất phát từ điểm kết thúc thân từ $\mathbf{P}_{\text{last}}$:
   $$\pi^* = \arg\min_{\pi \in \mathcal{P}_M} \left[ \|\mathbf{P}_{\text{last}} - \text{start}(\pi_1)\| + \sum_{k=1}^{M-1} \|\text{end}(\pi_k) - \text{start}(\pi_{k+1})\| \right]$$
2. **Trường hợp $M > 6$ (trường hợp biên hoặc từ ghép đặc biệt):**
   Sử dụng giải thuật **Nearest Neighbor Heuristic** kết hợp Kinematic Cost (`path_optimizer.py::nearest_neighbor_order`) làm phương án dự phòng (fallback) để đảm bảo độ phức tạp thời gian đa thức $\mathcal{O}(M^2)$.

---

## 5. Kế Hoạch Benchmark Định Lượng

### 5.1. Hai Tập Ngữ Liệu: Development Corpus & Holdout Corpus

> [!WARNING]
> Để chống hiện tượng quá khớp (overfitting) trọng số và quy tắc, nghiên cứu thiết kế tách biệt 2 tập ngữ liệu độc lập:

1. **Development Corpus (`BENCHMARK_DEV_CORPUS_20`):** 20 từ đại diện bao phủ các tổ hợp nguyên âm biến âm, thanh điệu và phụ âm nhô cao/thấp (ascender/descender). Dùng trong quá trình phát triển, tinh chỉnh tham số và kiểm thử hồi quy:
   ```python
   BENCHMARK_DEV_CORPUS_20 = [
       "tiếng", "việt", "nguyễn", "nước", "đường",
       "khuấy", "thuở", "nghỉ", "hoặc", "chuẩn",
       "trường", "quyện", "nghĩ", "phượng", "kiều",
       "hướng", "mượt", "bước", "vẫy", "nhánh"
   ]
   ```
2. **Holdout Corpus (`BENCHMARK_HOLDOUT_CORPUS_20`):** 20 từ độc lập **tuyệt đối không dùng khi phát triển hoặc tinh chỉnh trọng số**, dùng để nghiệm thu đánh giá tính tổng quát hóa (generalization) của giải thuật:
   ```python
   BENCHMARK_HOLDOUT_CORPUS_20 = [
       "nghiêng", "khoác", "truyền", "hoàng", "nguyệt",
       "thoáng", "quỳnh", "nhuộm", "duyệt", "khoảnh",
       "giường", "chuyện", "xoay", "bỗng", "quét",
       "khẽ", "nhặt", "nguồn", "sưởi", "vẹn"
   ]
   ```

### 5.2. Môi Trường Thực Nghiệm & Giao Thức Đo Đạc (Benchmark Protocol)

Mọi thực nghiệm phải ghi nhận chi tiết siêu dữ liệu môi trường vận hành thực tế (Execution Metadata):
1. **CPU Model:** Tên đầy đủ vi xử lý, số nhân vật lý và số luồng logic.
2. **OS & Version:** Bản phát hành và build cụ thể.
3. **Python Version:** Phiên bản patch release chính xác.
4. **NumPy Version & BLAS Backend:** Phiên bản thư viện và backend tính toán.
5. **Git Commit Hash:** Mã hash commit của repository OmniDraw tại thời điểm thực thi.
6. **Power / Performance Mode:** Chế độ cấp nguồn của hệ thống.

> [!IMPORTANT]
> **Quy tắc tách biệt môi trường:**
> Tuyệt đối không gộp (aggregate/pool) kết quả đo độ trễ và thời gian tính toán (`optimize_time_ms`) giữa các môi trường Windows và Linux. Bắt buộc phải báo cáo và phân tích riêng từng môi trường thực nghiệm.

#### Giao thức đo đạc:
- **Khởi động (Warm-up):** Chạy trước 10 lượt warm-up để nạp bytecode, thư viện C-extensions và ổn định CPU cache.
- **Số lần lặp (Iterations):** $N_{\text{runs}} = 50$ lần lặp cho mỗi cấu hình với ma trận 4 seed cố định: `[42, 100, 2026, 999999]`.
- **Chỉ số thống kê:** Báo cáo đồng thời giá trị **Median (Trung vị)** và **p95 (Phân vị thứ 95)**.

### 5.3. Bảy Chỉ Số Đo Đạc Tối Thiểu (Minimum Metrics Set)

| Tên chỉ số | Ký hiệu | Đơn vị | Định nghĩa & Phương pháp đo |
| :--- | :--- | :--- | :--- |
| **1. Chiều dài nét vẽ** | `total_path_length_mm` | $mm$ | Tổng độ dài các đoạn nét tiếp xúc mặt giấy |
| **2. Quãng đường nhấc bút** | `pen_lift_distance_mm` | $mm$ | Tổng khoảng cách di chuyển trên không giữa các nét rời rạc |
| **3. Số lần nhấc bút** | `pen_lift_count` | Lần | Tổng số lần trục Z nâng đầu bút khỏi giấy trong một từ |
| **4. Số va chạm hình học** | `collision_count` | Lần | Số điểm giao cắt hình học giữa cầu nối với nét thân chữ hoặc nét dấu |
| **5. Khoảng cách cách ly dấu** | `minimum_diacritic_clearance_mm` | $mm$ | Khoảng cách Euclid ngắn nhất từ thân cầu nối tới nét dấu gần nhất |
| **6. Chi phí độ cong tiếp tuyến** | `curvature_cost` | Điểm | Tổng chi phí bẻ tiếp tuyến $\sum (1 - \cos\theta_1) + (1 - \cos\theta_2)$ của các cầu nối |
| **7. Thời gian tối ưu DAG** | `optimize_time_ms` | $ms$ | Thời gian thực thi riêng biệt của `optimize_word_dag` đo qua `time.perf_counter()` |

### 5.4. Quy Định Lưu Trữ Dữ Liệu Benchmark

- Toàn bộ kết quả benchmark chạy tự động phải được ghi vào thư mục được ignore trong git (ví dụ: `logs/` hoặc đường dẫn do cờ `--output <path>` chỉ định).
- **Tuyệt đối không đưa các tệp log CSV tạm thời (`logs/experiment_log.csv`) vào danh sách commit của Git.**

### 5.5. Bảng Tiêu Chí Đánh Giá Thống Nhất (Acceptance Thresholds)

Áp dụng quy tắc ưu tiên phân loại: **(1) FAIL nếu bất kỳ điều kiện FAIL đúng $\to$ (2) PASS nếu TẤT CẢ điều kiện PASS đúng $\to$ (3) INCONCLUSIVE cho mọi trường hợp còn lại**:

| Chỉ số | Vùng Đạt (PASS — Ưu tiên 2) | Vùng Thất Bại / Bác Bỏ (FAIL — Ưu tiên 1) | Vùng Chưa Đủ Cơ Sở (INCONCLUSIVE — Ưu tiên 3) |
| :--- | :--- | :--- | :--- |
| **Tính hợp lệ SVG & Bounds** | $100\%$ file SVG hợp lệ, nằm trọn trong khổ giấy | $\ge 1$ file lỗi XML hoặc vượt bounds | — |
| **H1.1: Quãng đường pen-up** | Giảm $\ge 25.0\%$ vs B1 **VÀ** $\ge 10.0\%$ vs B2 | Giảm $< 15.0\%$ vs B1 **HOẶC** $< 5.0\%$ vs B2 | Mọi trường hợp còn lại |
| **H1.2: Số lần nhấc bút** | Giảm $\ge 35.0\%$ vs B1 | Giảm $< 20.0\%$ vs B1 | Giảm $[20.0\%, 35.0\%)$ vs B1 |
| **H1.3: Chiều dài nét vẽ** | Tăng $\le 10.0\%$ vs B1 | Tăng $> 15.0\%$ vs B1 | Tăng $(10.0\%, 15.0\%]$ vs B1 |
| **H2.1: Va chạm dấu** | $collision\_count = 0$ trên $100\%$ mẫu | $collision\_count \ge 1$ | — |
| **H2.2: Khoảng cách cách ly** | $d_{\min} \ge 0.50\text{ mm}$ | $d_{\min} < 0.20\text{ mm}$ | $0.20\text{ mm} \le d_{\min} < 0.50\text{ mm}$ |
| **H3.1: Thời gian Viterbi DP** | Median $\le 5.0\text{ ms}$ **VÀ** p95 $\le 10.0\text{ ms}$ | Median $> 15.0\text{ ms}$ **HOẶC** p95 $> 30.0\text{ ms}$ | Mọi trường hợp còn lại |
| **H3.2: Chi phí độ cong tiếp tuyến** | Giảm $\ge 15.0\%$ vs B2 **VÀ** không góc $> 120^\circ$ | Giảm $\le 0.0\%$ vs B2 **HOẶC** có góc $> 120^\circ$ | Mọi trường hợp còn lại (giảm $0\text{–}15\%$ và không góc $> 120^\circ$) |

---

## 6. Ma Trận Truy Vết Khoa Học (Traceability Matrix)

| RQ | Giả thuyết | Metrics đo đạc | Đối chứng | Kịch bản kiểm thử | Vùng FAIL (Ưu tiên 1) | Vùng PASS (Ưu tiên 2) | Vùng INCONCLUSIVE (Ưu tiên 3) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RQ1** | H1.1 | `pen_lift_distance_mm` | B1, B2 | Dev & Holdout corpus × 2 font × 4 seeds | Giảm $< 15\%$ vs B1 hoặc $< 5\%$ vs B2 | Giảm $\ge 25\%$ vs B1 và $\ge 10\%$ vs B2 | Mọi trường hợp còn lại |
| **RQ1** | H1.2 | `pen_lift_count` | B1 | Đếm trên các từ hỗ trợ nối nét | Giảm $< 20\%$ vs B1 | Giảm $\ge 35\%$ vs B1 | Giảm $20\text{–}35\%$ vs B1 |
| **RQ1** | H1.3 | `total_path_length_mm` | B1 | Đo tổng chiều dài nét tiếp xúc giấy | Tăng $> 15\%$ vs B1 | Tăng $\le 10\%$ vs B1 | Tăng $10\text{–}15\%$ vs B1 |
| **RQ2** | H2.1 | `collision_count` | B3 | Kiểm tra giao cắt đoạn thẳng bridge vs dấu | $collision\_count \ge 1$ | $collision\_count = 0$ | — |
| **RQ2** | H2.2 | `minimum_diacritic_clearance_mm` | B3 | Đo khoảng cách ngắn nhất bridge vs dấu | $< 0.20\text{ mm}$ | $\ge 0.50\text{ mm}$ | $0.20\text{–}0.50\text{ mm}$ |
| **RQ3** | H3.1 | `optimize_time_ms` (perf_counter) | B2, B3 | 50 lần lặp sau warm-up trên môi trường ghi nhận | Median $> 15\text{ ms}$ hoặc p95 $> 30\text{ ms}$ | Median $\le 5\text{ ms}$ và p95 $\le 10\text{ ms}$ | Mọi trường hợp còn lại |
| **RQ3** | H3.2 | `curvature_cost` | B2 | Đo tổng chi phí bẻ tiếp tuyến ngòi bút | Giảm $\le 0\%$ vs B2 hoặc có góc $> 120^\circ$ | Giảm $\ge 15\%$ vs B2 và không góc $> 120^\circ$ | Mọi trường hợp còn lại |

---

## 7. Kế Hoạch Triển Khai Kỹ Thuật (Lộ Trình Bước C)

Lộ trình triển khai kỹ thuật được phân rã thành các PR tuần tự, bảo toàn chữ ký API công khai và tuân thủ ranh giới giữa TV2 và TV4:

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│  PR1   │ ──▶ │  PR2   │ ──▶ │  PR3   │ ──▶ │  PR4   │ ──▶ │  PR5   │
│Trace & │     │ 3 Base-│     │CA-VHC  │     │Delayed │     │Bench-  │
│Metrics │     │ lines  │     │Trellis │     │Stroke  │     │mark &  │
│Fixtures│     │(B1,B2, │     │(State &│     │(Experi-│     │Ablation│
│(Shared)│     │  B3)   │     │ Motion)│     │ mental)│     │ Study  │
└────────┘     └────────┘     └────────┘     └────────┘     └────────┘
```

### PR1: Structured Render Trace, Benchmark Corpus & Metrics Fixtures (Shared TV2 + TV4)
- **Phạm vi kỹ thuật:**
  - Định nghĩa 2 tập ngữ liệu `BENCHMARK_DEV_CORPUS_20` và `BENCHMARK_HOLDOUT_CORPUS_20`.
  - Thiết kế Structured Render Trace: module đo đạc phân biệt rõ từng tag nét (`base_stroke`, `bridge_stroke`, `diacritic_stroke`).
  - **Bảo toàn tuyệt đối chữ ký API công khai:** `generate_handwriting_svg()` và `text_to_strokes()` giữ nguyên đầu vào, đầu ra và kiểu dữ liệu `List[np.ndarray]`.
  - Triển khai bộ đo hình học độc lập: `minimum_diacritic_clearance_mm`, `collision_count`, `curvature_cost`, và đo độc lập thời gian `optimize_word_dag` qua `time.perf_counter()`.
- **Files liên quan:** `benchmark_fixtures.py`, `metrics_evaluator.py`, `tests/test_ca_vhc_metrics.py`.

### PR2: Chuẩn Hóa và Khóa Ba Baseline Đối Chứng B1, B2, B3 (TV2 chủ trì)
- **Phạm vi kỹ thuật:**
  - Đóng gói các adapter thực nghiệm độc lập cho B1 (Static Glyphs Renderer), B2 (Pure Motion Trellis), B3 (Static Diacritic Layout).
  - Cho phép benchmark runner gọi độc lập từng baseline thông qua cờ nội bộ `_algorithm_mode`.
- **Files liên quan:** `baselines.py`, `tests/test_baselines.py`.

### PR3: CA-VHC Diacritic-Aware Trellis với `CompositionState` (TV2 + TV4 tích hợp)
- **Phạm vi kỹ thuật:**
  - Tích hợp `CompositionState` (`state.py` do TV4 cung cấp) vào hàm giải quy hoạch động `optimize_word_dag`.
  - Triển khai hàm chi phí hai cấp: $C_{\text{state}}(s)$ và $J_{\text{transition}}(u, w)$.
  - Tích hợp `bridge_collision_cost` kiểm tra va chạm trong hệ tọa độ thế giới với tập nét thân và dấu xung quanh.
  - Thiết lập hard rejection: loại bỏ quyết định `CONNECT` nếu cắt ngang nét dấu.
- **Files liên quan:** `backend/handwriting/engine.py`, `backend/handwriting/state.py`, `tests/test_diacritic_dag.py`.

### PR4: Delayed-Stroke Ordering Optimizer (Experimental Extension — Step C v2)
- **Phạm vi kỹ thuật:**
  - Triển khai module sắp xếp thứ tự nét trễ: Exact Enumeration khi số nét phụ/dấu $M \le 6$ và fallback Nearest Neighbor khi $M > 6$.
  - Tích hợp thử nghiệm ở chế độ experimental mở rộng sau khi core Viterbi v1 đã ổn định.
- **Files liên quan:** `backend/handwriting/delayed_strokes.py`, `tests/test_delayed_strokes.py`.

### PR5: Benchmark Runner, Automated Reporting & Ablation Study (Shared TV2 + TV4)
- **Phạm vi kỹ thuật:**
  - Xây dựng CLI runner thực thi toàn bộ ma trận kiểm thử (Proposed CA-VHC vs 3 Baselines × 20 từ Dev + 20 từ Holdout × 2 font × 4 seed × 50 iterations).
  - Tự động ghi nhận log CSV ra thư mục ignore `logs/`, tính toán Median và p95.
  - Báo cáo riêng kết quả theo từng môi trường thực tế (Windows / Linux).
  - Bóc tách độ nhạy (ablation) các thành phần trọng số $w_1 \dots w_6$.
- **Files liên quan:** `backend/handwriting/benchmark_runner.py`, `tests/test_benchmark_runner.py`.

---

## 8. Đối Chiếu Code Hiện Tại & Khoảng Trống Triển Khai (Implementation Gaps)

| STT | Hạng mục trên tài liệu / Roadmap | Hiện trạng trong Code thực tế | Phân loại khoảng trống | Hướng xử lý kỹ thuật Bước C |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Trạng thái Trellis `CompositionState`** | `engine.py` hiện chỉ nhận `char_info_list` với nét thân chữ (`scaled_prim`). Dấu sinh sau khi DP đã giải xong. | **Gap kiến trúc cốt lõi (P0)** | Triển khai PR3: Nạp `CompositionState` (TV4) vào `optimize_word_dag`, giải đồng thời thân chữ và vị trí dấu. |
| **2** | **Va chạm cầu nối với nét dấu** | `engine.py::bridge_collision_cost` chỉ kiểm tra va chạm với nét thân chữ lân cận, chưa nhận diện nét dấu trong tọa độ thế giới. | **Gap hình học chuyển động (P0)** | Triển khai PR3: Mở rộng `bridge_collision_cost` nhận toàn bộ nét thế giới $\mathcal{S}_{\text{world}}$ từ `CompositionState`. |
| **3** | **Tách biệt hàm mục tiêu hai cấp** | Hàm mục tiêu chuyển tiếp hiện tại chưa nhận $C_{\text{state}}$, nguy cơ lẫn lộn giữa va chạm nội và va chạm cầu nối. | **Gap mô hình toán (P0)** | Triển khai PR3: Triển khai công thức Bellman hai cấp $DP[i, j] = C_{\text{state}} + \min(DP + J_{\text{transition}})$. |
| **4** | **Bộ ba Baseline đối chứng chuẩn hóa** | Chưa có adapter chạy độc lập cho Baseline 1 (Static Glyphs Renderer) và Baseline 2 (Pure Motion Trellis). | **Gap framework thực nghiệm (P0)** | Triển khai PR2: Đóng gói 3 baseline thành adapter phục vụ runner thực nghiệm. |
| **5** | **Thời gian tối ưu hóa DAG** | `svg_metrics.optimize_time_ms` trong `engine.py` đang trả về placeholder cố định `0.0`. | **Gap đo đạc thực nghiệm (P0)** | Triển khai PR1: Đo riêng thời gian thực thi của `optimize_word_dag` qua `time.perf_counter()`. |
| **6** | **Trích xuất nét có cấu trúc** | `text_to_strokes` flatten toàn bộ nét thành `List[np.ndarray]`, không phân biệt được nét thân, nét nối và nét dấu. | **Gap đo đạc thực nghiệm (P0)** | Triển khai PR1: Thêm helper nội bộ trích xuất structured trace giữ nguyên tag của từng nét mà không đổi public API. |
| **7** | **Thứ tự nét trễ (Delayed-stroke)** | Nét phụ và dấu được append tuần tự theo thứ tự xuất hiện. | **Gap mở rộng v2 (P1)** | Triển khai PR4 ở giai đoạn sau: Exact Enumeration ($M \le 6$) và Nearest Neighbor ($M > 6$). |

---

## 9. Cross-review Alignment with Step B Architecture

Bảng đối chiếu kỹ thuật dưới đây xác nhận sự đồng thuận và điều chỉnh chi tiết giữa tài liệu nghiên cứu CA-VHC của TV2 (`docs/05_ca_vhc_research_spec.md`) và kiến trúc thiết kế Bước B của TV4 (`docs/07_diacritic_aware_state_design.md` và `docs/08_handwriting_dataset_spec.md`):

| STT | Hạng mục kỹ thuật | File 05 (Phiên bản Cũ) | File 07 / 08 (Kiến trúc Bước B) | File 05 (Đã chỉnh sửa & Đồng bộ) | Trạng thái đồng thuận |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **1** | **Phân định quyền sở hữu (Ownership)** | TV2 sở hữu toàn bộ subsystem chữ viết tay (từ NFD, dấu, font pack đến engine và DAG). | TV4 sở hữu typography, NFD, diacritic model, candidate generation, font/dataset. TV2 sở hữu kinematics, objective, Viterbi search. | Cập nhật Ownership Matrix: phân tách rõ TV4 (Typography/Data/State) vs TV2 (Kinematics/DP/Path) vs Shared (Runner/Transition). | ✅ APPROVED |
| **2** | **Đơn vị nút Trellis (Trellis Node)** | Nút là `GlyphVariant` (chỉ thân chữ, dấu sinh sau khi DP giải xong). | Nút là `CompositionState = (base_variant, diacritic_candidate)`. | Định nghĩa lại Trellis node là `CompositionState` ($s = (v_{\text{base}}, c_{\text{diacritic}})$). | ✅ APPROVED |
| **3** | **Không gian trạng thái & Giới hạn tổ hợp** | $K_i \le 3$ (chỉ đếm số biến thể thân chữ cái). | $K_{\text{raw}} = K_{\text{base}} \times K_{\text{diacritic}} \le 3 \times 3 = 9$. | Xác lập $K_{\text{raw}} \le 9$ là Cận lý thuyết (Theoretical Raw State Bound), không áp dụng heuristic pruning ở P0. | ✅ APPROVED |
| **4** | **Bản chất của dấu tiếng Việt** | Dấu là chướng ngại vật hình học xác định trước (deterministic static obstacles). | Dấu là biến tối ưu hữu hạn (finite search candidate) gồm `canonical`, `safe_left`, `safe_right`. | Đổi định nghĩa dấu thành biến tìm kiếm hữu hạn trong không gian trạng thái tổ hợp phối hợp giữa TV4 và TV2. | ✅ APPROVED |
| **5** | **Phân rã hàm mục tiêu** | $J$ gộp chung mọi thành phần vào một hàm chi phí chuyển tiếp. | Phân rã 2 cấp: $C_{\text{state}}(s)$ (TV4) và $J_{\text{transition}}(u, w)$ (TV2). | Tách bạch hàm mục tiêu 2 cấp $J_{\text{total}} = \sum C_{\text{state}} + \sum J_{\text{transition}}$, loại bỏ hoàn toàn double-counting. | ✅ APPROVED |
| **6** | **Trọng số chi phí trạng thái** | Gán cứng $w_4 = 15.0, w_5 = 1.0$ như tham số cố định. | Trọng số nội ký tự cần được kiểm chứng qua thực nghiệm thị giác. | Đánh dấu các trọng số $w_{4a}, w_5, w_6$ là `[REQUIRES EXPERIMENTAL TUNING]`. | ⚠️ APPROVED WITH NOTE |
| **7** | **Phân tách bài toán va chạm** | Dùng chung một khái niệm $C_{\text{collision}}$ cho mọi trường hợp. | Tách biệt: va chạm nội thân-dấu ($C_{\text{internal\_collision}}$) vs va chạm cầu nối ($C_{\text{bridge\_collision}}$). | Phân tách rõ ràng: $C_{\text{internal\_collision}}$ (TV4 xử lý trong $C_{\text{state}}$) vs $C_{\text{bridge\_collision}}$ (TV2+TV4 trong $J_{\text{transition}}$). | ✅ APPROVED |
| **8** | **Quy ước hệ tọa độ** | Không phân định rõ giữa tọa độ font pack và tọa độ trang giấy. | Tách biệt Local Coordinate (0..14 đơn vị) và World Coordinate ($mm$). | Quy định rõ: Local cho biểu diễn state và $C_{\text{state}}$; World cho tính toán chuyển động và $C_{\text{bridge\_collision}}$. | ✅ APPROVED |
| **9** | **Ngưỡng an toàn va chạm (Clearance)** | Đặt cứng $\delta_{\text{clearance}} = 0.50\text{ mm}$. | Prototype code đang dùng $0.20\text{ mm}$. | Ghi nhận rõ sự khác biệt giữa kỹ thuật mặc định ($0.20\text{ mm}$) và nghiên cứu lý tưởng ($0.50\text{ mm}$), đánh dấu `[OPEN REVIEW DECISION: 0.20mm vs 0.50mm]`. | ⚠️ APPROVED WITH NOTE |
| **10**| **Phạm vi nét trễ (Delayed-Stroke)** | Đưa Delayed-Stroke Ordering vào PR4 cốt lõi của P0. | Phân định rõ bài toán WHERE (chọn state & bridge) vs WHEN (thứ tự nét trễ). | Xác định Delayed-Stroke nằm ngoài phạm vi cốt lõi Step C v1; xếp lịch triển khai dưới dạng Experimental Extension ở Bước C v2. | ⚠️ APPROVED WITH NOTE |

---

## 10. Final Cross-review Verdict

Căn cứ vào kết quả đối chiếu kỹ thuật toàn diện giữa tài liệu nghiên cứu CA-VHC (`docs/05_ca_vhc_research_spec.md`) và thiết kế hệ thống Bước B (`docs/07_diacritic_aware_state_design.md`, `docs/08_handwriting_dataset_spec.md`), đại diện nhóm Nghiên cứu Thuật toán & Tối ưu chuyển động đưa ra kết luận đánh giá chéo như sau:

- **TV2 Cross-review status:** `APPROVED WITH CHANGES` (Đã phê duyệt và hoàn tất đồng bộ toàn diện vào tài liệu 05).
- **Blocking issues:** `NONE` (Không còn điểm nghẽn kỹ thuật hay mâu thuẫn kiến trúc giữa hai bên).
- **TV2 recommendation:** `Step B architecture may proceed to Step C implementation.` (Kiến trúc Bước B hoàn toàn đủ điều kiện chuyển giao sang Bước C — Implementation theo đúng lộ trình 5 PR).

**Đại diện ký duyệt:**
- **Thành viên 2** — *Stroke Optimization & Kinematic Planning Lead* (Chủ trì Lõi thuật toán CA-VHC)
- **Thành viên 4** — *Platform, Data & Vietnamese Typography Lead* (Đồng thuận kỹ thuật & Tích hợp hệ thống)

---

## 11. Tài Liệu Tham Khảo (References)

1. Graves, A., et al. (2008). *Offline Handwriting Recognition with Multidimensional Recurrent Neural Networks*. Advances in Neural Information Processing Systems (NeurIPS).
2. Plamondon, R., & Maarse, F. J. (1989). *An evaluation of motor models for handwriting analysis and synthesis*. IEEE Transactions on Systems, Man, and Cybernetics, 19(5), 1060–1072.
3. Viterbi, A. J. (1967). *Error bounds for convolutional codes and an asymptotically optimum decoding algorithm*. IEEE Transactions on Information Theory, 13(2), 260–269.
4. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press. (Chương quy hoạch động & đường đi ngắn nhất trên DAG).
5. Unicode Consortium. (2024). *The Unicode Standard, Version 15.1 — Vietnamese Diacritical Marks and Combining Characters*.
6. OmniDraw Technical Specifications:
   - `docs/01_tech-stack.md`: Kiến trúc công nghệ tổng thể và phân công trách nhiệm.
   - `docs/02_roadmap.md`: Lộ trình phát triển sản phẩm qua các Sprint.
   - `docs/06_audit_trellis_dag_report.md`: Báo cáo kiểm định toàn diện hiện trạng Trellis DAG.
   - `docs/07_diacritic_aware_state_design.md`: Thiết kế kỹ thuật chi tiết không gian trạng thái `CompositionState` (Bước B).
   - `docs/08_handwriting_dataset_spec.md`: Quy chuẩn kỹ thuật bộ dữ liệu chữ viết tay tiếng Việt (Bước B).
