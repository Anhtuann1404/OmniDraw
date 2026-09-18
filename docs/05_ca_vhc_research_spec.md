# OmniDraw — Đặc Tả Nghiên Cứu & Thiết Kế Kỹ Thuật Lõi CA-VHC

**Tài liệu:** Khung thuật toán Context-Aware Vietnamese Handwriting Composition (CA-VHC)  
**Tác giả / Owner:** Thành viên 2 — Stroke Optimization & Path Planning Lead (Chủ trì Lõi thuật toán CA-VHC)  
**Phối hợp nền tảng & Tích hợp:** Thành viên 4 — Project Lead & Platform / API Gateway Lead  
**Cập nhật lần cuối:** 18/09/2026  
**Trạng thái:** Khóa đặc tả nghiên cứu & thiết kế kỹ thuật tối thiểu (P0 — Sprint 1–2)  

---

## Giới thiệu & Phân định quyền sở hữu (Module Ownership)

Tài liệu này xác lập cơ sở lý thuyết, mô hình toán học hình thức, thiết kế thuật toán tối thiểu và kế hoạch thực nghiệm cho **Context-Aware Vietnamese Handwriting Composition (CA-VHC)** trên máy vẽ 2 trục (pen plotter).

Theo phân công trách nhiệm cập nhật trong `docs/01_tech-stack.md` và `docs/02_roadmap.md`:
- **Thành viên 2 (Owner chính của tài liệu này):** Sở hữu toàn diện subsystem chữ viết tay `backend/handwriting/` bao gồm:
  - Công cụ sinh nét `engine.py` và kiến trúc dữ liệu nét đơn `font_packs/`;
  - Đồ thị Trellis DAG, thuật toán quy hoạch động Viterbi DP theo từng từ (`optimize_word_dag`) và hàm đánh giá chuyển tiếp (`eval_transition`);
  - Ràng buộc hình học dấu tiếng Việt, phát hiện va chạm (`bridge_collision_cost`) và quy hoạch thứ tự nét trễ (`delayed-stroke ordering`);
  - Thiết kế và triển khai 3 baseline đối chứng (B1, B2, B3) cùng bộ đo đạc chỉ số nghiên cứu (`metrics`).
- **Thành viên 4 (Platform & Integration Lead):** Sở hữu API Gateway (`backend/main.py`), giao diện người dùng frontend React, kết nối REST polling, điều phối tích hợp toàn hệ thống và framework thực nghiệm tổng thể.

> [!IMPORTANT]
> **Nguyên tắc trung thực học thuật & Code-first:**
> - Mọi viện dẫn mã nguồn trong tài liệu này lấy **tên file và tên hàm/lớp làm nguồn định danh chính** (line number chỉ là thông tin tham khảo phụ do có thể trôi theo các commit).
> - Tài liệu không mô tả các tính năng chưa tồn tại là "đã triển khai".
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
│  - Kiểm soát độ dài nét  │  - Chống đè dấu chồng tầng  │  - Đo kiểm phần cứng (TV3)    │
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
  *Việc áp dụng giải thuật quy hoạch động Trellis DAG (Viterbi DP) để đồng thời lựa chọn biến thể glyph theo ngữ cảnh và quyết định nối nét có thể giảm đáng kể quãng đường di chuyển pen-up ($D_{\text{penup}}$) và số lần nhấc bút ($N_{\text{lift}}$) so với phương pháp render tĩnh (B1) và tham lam cục bộ (B2) hay không, trong khi vẫn duy trì tổng chiều dài nét vẽ tiếp xúc giấy ở mức tương đương?*

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
  *Cơ chế tích hợp vùng cấm an toàn (clearance envelope) và chi phí cản trở của dấu tiếng Việt (`diacritic obstacle-avoidance`) vào hàm mục tiêu Trellis DAG có loại bỏ được hoàn toàn các giao cắt hình học giữa cầu nối và dấu phụ/dấu thanh, đồng thời bảo đảm khoảng cách tối thiểu giữa nét nối và tổ hợp dấu chồng tầng so với Trellis DAG hiện tại chưa có ràng buộc dấu (B3) hay không?*

- **Giả thuyết H2.1 (Triệt tiêu va chạm hình học):**  
  - **FAIL (Ưu tiên 1):** Phát hiện $collision\_count \ge 1$ trên bất kỳ mẫu kiểm thử nào.
  - **PASS (Ưu tiên 2):** $collision\_count = 0$ trên $100\%$ mẫu thử nghiệm.
  - **INCONCLUSIVE (Ưu tiên 3):** Không áp dụng (tiêu chuẩn nhị phân cứng).

- **Giả thuyết H2.2 (Khoảng cách an toàn tối thiểu với dấu):**  
  Với cấu hình chuẩn $font\_size\_mm = 7.0\text{ mm}$, gọi $d_{\min} = minimum\_diacritic\_clearance\_mm$.
  - **FAIL (Ưu tiên 1):** $d_{\min} < 0.35\text{ mm}$ (dưới ngưỡng dung sai độ dày ngòi bút $0.30\text{ mm}$).
  - **PASS (Ưu tiên 2):** $d_{\min} \ge 0.50\text{ mm}$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại (tức là $0.35\text{ mm} \le d_{\min} < 0.50\text{ mm}$).

---

### 1.3. RQ3: Hiệu Năng Tính Toán & Tính Khả Thi Thi Công Trên Máy Vẽ

- **Câu hỏi nghiên cứu (RQ3):**  
  *Giải thuật CA-VHC (kết hợp Viterbi DP theo từng từ và quy hoạch thứ tự nét trễ delayed-stroke ordering) có duy trì được thời gian tính toán ở mức tương tác thời gian thực và sinh ra quỹ đạo vector đơn trị, trơn tiếp tuyến hình học $C^1$, tạo tiền đề khả thi để thi công an toàn trên máy vẽ 2 trục hay không?*

> [!NOTE]
> **Ranh giới tuyên bố khoa học (Scientific Scope Boundary):**
> Về mặt thuật toán, TV2 chứng minh và bảo đảm **tính trơn tiếp tuyến hình học ($C^1$ geometric smoothness)** của đường cong vector centerline. Các hệ quả cơ lý tính trên thực tế (độ rung giật động học của đầu bút, mức độ hao mòn cơ khí, thời gian thi công thực tế) là giả thuyết ngoại suy và **bắt buộc phải được kiểm chứng, xác nhận bằng số liệu thực nghiệm phần cứng do TV3 đo đạc trên máy AxiDraw**.

- **Giả thuyết H3.1 (Thời gian tính toán giải thuật Viterbi DP):**  
  Thời gian giải quy hoạch động trên từng từ ($N \le 7$ ký tự) đo độc lập qua `time.perf_counter()`. Gọi $M = \text{Median}(optimize\_time\_ms)$ và $P = \text{p95}(optimize\_time\_ms)$.
  - **FAIL (Ưu tiên 1):** $(M > 10.0\text{ ms})$ **HOẶC** $(P > 20.0\text{ ms})$.
  - **PASS (Ưu tiên 2):** $(M \le 5.0\text{ ms})$ **VÀ** $(P \le 10.0\text{ ms})$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại (tức là $M \le 10.0\text{ ms}$ và $P \le 20.0\text{ ms}$, nhưng chưa đồng thời đạt $M \le 5.0\text{ ms}$ và $P \le 10.0\text{ ms}$).

- **Giả thuyết H3.2 (Độ trơn hình học & Kiểm soát đổi hướng tiếp tuyến):**  
  Gọi $\Delta C_{\text{curv}} = \frac{curvature\_cost(\text{B2}) - curvature\_cost(\text{CA-VHC})}{curvature\_cost(\text{B2})}$ và biến cố $has\_acute\_turn$ là sự xuất hiện của bất kỳ góc lệch tiếp tuyến nào $> 120^\circ$ trên cầu nối.
  - **FAIL (Ưu tiên 1):** $(\Delta C_{\text{curv}} \le 0.0\%)$ **HOẶC** $(has\_acute\_turn == \text{True})$.
  - **PASS (Ưu tiên 2):** $(\Delta C_{\text{curv}} \ge 15.0\%)$ **VÀ** $(has\_acute\_turn == \text{False})$.
  - **INCONCLUSIVE (Ưu tiên 3):** Mọi trường hợp còn lại (tức là $has\_acute\_turn == \text{False}$ và $0.0\% < \Delta C_{\text{curv}} < 15.0\%$).

---

## 2. Mô Hình Toán Học Hình Thức

### 2.1. Không Gian Trạng Thái Tại Vị Trí Ký Tự

Xét một từ tiếng Việt gồm chuỗi $N$ ký tự liên tiếp: $\mathbf{C} = (c_1, c_2, \dots, c_N)$.

Tại mỗi vị trí $i \in \{1, \dots, N\}$, ký tự $c_i$ sau khi phân rã Unicode NFD gồm:
- Ký tự gốc (base character): $b_i \in \Sigma_{\text{base}}$ (ví dụ: `a`, `e`, `o`, `d`, `K`).
- Tập dấu đi kèm: $\mathcal{A}_i = \{a_{i,1}, a_{i,2}, \dots\}$ (ví dụ: `{\u0302}` cho nón, `{\u0301}` cho sắc, hoặc $\emptyset$ nếu không có dấu).
- Thông số biến đổi hình học cục bộ: tỷ lệ phóng/thu $\mathbf{s}_i = [s_{x,i}, s_{y,i}]^T$, độ lệch tọa độ thế giới $\mathbf{o}_i = [x_i, y_i]^T$, chiều rộng ký tự $w_i$, và trọng tâm ngang $cx_i$.

Tập biến thể ứng viên (Candidate Allographs) tại vị trí $i$ được định nghĩa là:
$$\mathcal{V}_i = \{ v_{i, 1}, v_{i, 2}, \dots, v_{i, K_i} \}, \quad K_i = |\mathcal{V}_i| \in \{1, 2, 3\}$$

Mỗi biến thể $v_{i, j} \in \mathcal{V}_i$ tương ứng với cấu trúc dữ liệu `GlyphVariant` (`engine.py::GlyphVariant`) và được đặc trưng bởi bộ 8 tham số:
$$v_{i, j} = \left( \mathcal{S}_{i, j}, \mathbf{p}_{\text{in}}, \mathbf{p}_{\text{out}}, \mathbf{v}_{\text{in}}, \mathbf{v}_{\text{out}}, \text{can\_in}, \text{can\_out}, c_{\text{leg}} \right)$$

Trong đó:
- $\mathcal{S}_{i, j} = \{S_1, S_2, \dots\}$: Tập các nét đa tuyến (polylines) trong hệ tọa độ chuẩn hóa của font pack (0..14 đơn vị), phân rã thành nét chính ($\text{prim}$) và nét phụ nội bộ ($\text{sec}$) qua `engine.py::split_glyph_strokes`.
- $\mathbf{p}_{\text{in}}, \mathbf{p}_{\text{out}} \in \mathbb{R}^2$: Tọa độ cục bộ điểm bắt đầu nét đầu tiên và điểm kết thúc nét cuối cùng của thân chữ.
- $\mathbf{v}_{\text{in}}, \mathbf{v}_{\text{out}} \in \mathbb{R}^2$: Vector tiếp tuyến đơn vị tại điểm vào và điểm ra:
  $$\mathbf{v}_{\text{in}} = \frac{S_1[1] - S_1[0]}{\|S_1[1] - S_1[0]\|}, \quad \mathbf{v}_{\text{out}} = \frac{S_{\text{last}}[-1] - S_{\text{last}}[-2]}{\|S_{\text{last}}[-1] - S_{\text{last}}[-2]\|}$$
- $\text{can\_in}, \text{can\_out} \in \{0, 1\}$: Cờ nhị phân cho phép nhận nét nối vào và thoát nét nối ra (dựa trên bảng giải phẫu `engine.py::ENTRY_TYPES` và `engine.py::EXIT_TYPES`).
- $c_{\text{leg}} = C_{\text{legibility}}(v_{i, j}) \ge 0$: Chi phí độ dễ đọc nội tại của biến thể.

### 2.2. Ánh Xạ Sang Tọa Độ Thế Giới & Quy Đổi Kích Thước Chữ

Kích thước chữ trong toàn bộ tài liệu được chuẩn hóa theo đơn vị milimét:
$$\text{Cấu hình chữ chuẩn: } font\_size\_mm = 7.0\text{ mm}$$

- **Mối liên hệ hình học trong Font Pack:** Hệ tọa độ chuẩn của Font Pack có chiều cao thiết kế $H_{\text{font}} = 14.0\text{ đơn vị}$. Khi render với $font\_size\_mm = 7.0\text{ mm}$, hệ số tỷ lệ hình học là:
  $$scale = \frac{font\_size\_mm}{H_{\text{font}}} = \frac{7.0}{14.0} = 0.50\text{ mm / đơn vị font}$$
  Chiều cao thân chữ x-height ($7.0\text{ đơn vị}$) tương ứng $3.5\text{ mm}$; ascender/descender đạt tối đa $7.0\text{ mm}$.
- **Quy đổi điểm in ấn (Typography Points):** Theo chuẩn quốc tế $1\text{ pt} = \frac{25.4}{72}\text{ mm} \approx 0.35278\text{ mm}$. Do đó, $font\_size\_mm = 7.0\text{ mm}$ tương đương xấp xỉ $19.84\text{ pt}$ (hoặc chữ $14\text{ pt}$ tương đương $4.94\text{ mm}$). Tài liệu này thống nhất dùng tham số chuẩn hóa $font\_size\_mm = 7.0\text{ mm}$.

Tọa độ các điểm mút và vector tiếp tuyến thế giới (đơn vị $mm$):
$$\mathbf{P}_{\text{entry}}(v_{i, j}) = \mathbf{p}_{\text{in}} \odot \mathbf{s}_i + \mathbf{o}_i, \quad \mathbf{P}_{\text{exit}}(v_{i, j}) = \mathbf{p}_{\text{out}} \odot \mathbf{s}_i + \mathbf{o}_i$$
$$\mathbf{V}_{\text{entry}}(v_{i, j}) = \frac{\mathbf{v}_{\text{in}} \odot \mathbf{s}_i}{\|\mathbf{v}_{\text{in}} \odot \mathbf{s}_i\| + \epsilon}, \quad \mathbf{V}_{\text{exit}}(v_{i, j}) = \frac{\mathbf{v}_{\text{out}} \odot \mathbf{s}_i}{\|\mathbf{v}_{\text{out}} \odot \mathbf{s}_i\| + \epsilon}$$

với $\odot$ là phép nhân từng phần tử và $\epsilon = 10^{-6}$.

### 2.3. Quyết Định Chuyển Trạng Thái: Nối Nét hay Nhấc Bút

Tại mỗi bước chuyển tiếp giữa biến thể $u \in \mathcal{V}_{i-1}$ và biến thể $w \in \mathcal{V}_i$, thuật toán đưa ra quyết định nhị phân:
$$a_{i-1, i} \in \{ \text{LIFT}, \text{CONNECT} \}$$

#### Ràng buộc hình học khả thi (Feasibility Condition)
Quyết định $\text{CONNECT}$ chỉ được phép đánh giá nếu thỏa mãn đồng thời 4 ràng buộc tiên quyết:
$$\text{FeasibleConn}(u, w) \iff (u.\text{can\_out} = 1) \land (w.\text{can\_in} = 1) \land (\Delta x > -0.2\text{ mm}) \land (d < 12.0\text{ mm})$$

trong đó:
- $d = \|\mathbf{P}_{\text{entry}}(w) - \mathbf{P}_{\text{exit}}(u)\|$ là khoảng cách Euclid giữa điểm thoát và điểm đón.
- $\Delta x = P_{\text{entry}, x}(w) - P_{\text{exit}, x}(u)$ là độ tiến ngang.

Nếu $\text{FeasibleConn}(u, w) = \text{False}$, áp đặt ràng buộc cứng: bắt buộc $a_{i-1, i} = \text{LIFT}$.

### 2.4. Hàm Mục Tiêu $J$ & Chi Phí Chuyển Tiếp

Hàm mục tiêu chuyển tiếp tổng hợp:
$$J(u, w, a) = w_1 \cdot D_{\text{penup}} + w_2 \cdot N_{\text{lift}} + w_3 \cdot C_{\text{curvature}} + w_4 \cdot C_{\text{collision}} + w_5 \cdot C_{\text{legibility}}$$

#### Trường hợp 1: Nhấc bút ($a = \text{LIFT}$)
- $D_{\text{penup}} = \|\mathbf{P}_{\text{entry}}(w) - \mathbf{P}_{\text{exit}}(u)\|$ ($mm$).
- $N_{\text{lift}} = 1$.
- $C_{\text{curvature}} = 0.0$, $C_{\text{collision}} = 0.0$ (ngòi bút di chuyển trên không).
- $C_{\text{legibility}} = w.c_{\text{leg}}$.

$$\text{Cost}_{\text{lift}}(u, w) = w_1 \cdot \|\mathbf{P}_{\text{entry}}(w) - \mathbf{P}_{\text{exit}}(u)\| + w_2 \cdot 1.0 + w_5 \cdot w.c_{\text{leg}}$$

#### Trường hợp 2: Nối nét liên tục ($a = \text{CONNECT}$)
- $D_{\text{penup}} = 0.0$, $N_{\text{lift}} = 0$.
- Chi phí độ cong tiếp tuyến ($C_{\text{curvature}}$):  
  Với vector chuyển dịch $\mathbf{u}_d = \frac{\mathbf{P}_{\text{entry}}(w) - \mathbf{P}_{\text{exit}}(u)}{\|\mathbf{P}_{\text{entry}}(w) - \mathbf{P}_{\text{exit}}(u)\|}$:
  $$\cos\theta_1 = \text{clip}(\mathbf{V}_{\text{exit}}(u) \cdot \mathbf{u}_d, -1.0, 1.0), \quad \cos\theta_2 = \text{clip}(\mathbf{u}_d \cdot \mathbf{V}_{\text{entry}}(w), -1.0, 1.0)$$
  $$C_{\text{curvature}} = (1.0 - \cos\theta_1) + (1.0 - \cos\theta_2) \in [0.0, 4.0]$$
- Chi phí va chạm hình học ($C_{\text{collision}}$):  
  Kiểm tra tương tác giữa cầu nối Bézier $\mathcal{B}(u, w)$ sinh bởi `engine.py::build_ligature_bridge` với tập nét chướng ngại vật $\mathcal{S}_{\text{obstacles}}$:
  $$C_{\text{collision}} = \text{Penalty}_{\text{geom}} + \text{Cost}_{\text{obstacle}}(\mathcal{B})$$
  với $\text{Penalty}_{\text{geom}} = 2.0$ nếu $\Delta x \le 0.0$ và $+0.4 \cdot (d - 8.0)$ nếu $d > 8.0\text{ mm}$.  
  Nếu phát hiện cắt ngang đoạn thẳng bất kỳ (`engine.py::segments_intersect` trả về `True`): $C_{\text{collision}} \to +\infty$.
- $C_{\text{legibility}} = w.c_{\text{leg}}$.

$$\text{Cost}_{\text{conn}}(u, w) = w_3 \cdot C_{\text{curvature}} + w_4 \cdot C_{\text{collision}} + w_5 \cdot w.c_{\text{leg}}$$

#### Chi phí chuyển tiếp tối ưu giữa 2 node:
$$\text{TransCost}(u, w) = \begin{cases} 
\text{Cost}_{\text{conn}}(u, w), & \text{nếu } \text{FeasibleConn}(u, w) \land (\text{Cost}_{\text{conn}}(u, w) < \text{Cost}_{\text{lift}}(u, w)) \\
\text{Cost}_{\text{lift}}(u, w), & \text{ngược lại}
\end{cases}$$

### 2.5. Bảng Chi Tiết Thành Phần Hàm Mục Tiêu $J$

| Thành phần | Ký hiệu | Đơn vị | Miền giá trị | Cách chuẩn hóa & Ý nghĩa vật lý | Trọng số mặc định trong code |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Quãng đường pen-up** | $D_{\text{penup}}$ | $mm$ | $[0, +\infty)$ | Khoảng cách Euclid thực tế giữa điểm thoát và điểm đón trên không | $w_1 = 0.5$ |
| **Số lần nhấc bút** | $N_{\text{lift}}$ | Lần | $\{0, 1\}$ | Phạt cơ học cho mỗi lần trục Z nâng/hạ bút (gây rung và trễ cơ học) | $w_2 = 4.0$ (bật ligature) / $0.0$ (khi ép nhấc) |
| **Góc bẻ tiếp tuyến** | $C_{\text{curvature}}$ | Điểm | $[0.0, 4.0]$ | Đo độ lệch tiếp tuyến $(1-\cos\theta_1) + (1-\cos\theta_2)$; triệt tiêu khi tiếp tuyến trơn $C^1$ | $w_3 = 2.0$ |
| **Va chạm hình học** | $C_{\text{collision}}$ | Điểm | $[0.0, +\infty)$ | Đo tỷ lệ xâm phạm vùng an toàn hoặc phạt vô cùng khi cắt nét chữ/dấu | $w_4 = 15.0$ |
| **Độ dễ đọc biến thể** | $C_{\text{legibility}}$ | Điểm | $[0.0, 1.0]$ | Phạt các biến thể xa chuẩn: `std`=0.0, `isolated`=0.02, `mid_in`/`high_out`=0.05 | $w_5 = 1.0$ |

### 2.6. Phân Biệt Node Cost, Transition Cost và Ràng Buộc Cứng

1. **Node Cost ($C_{\text{node}}$):**  
   Gắn liền nội tại với biến thể $v_{i, j}$, độc lập với nguồn gốc chuyển đến:
   $$C_{\text{node}}(v_{i, j}) = w_5 \cdot C_{\text{legibility}}(v_{i, j})$$
2. **Transition Cost ($C_{\text{trans}}$):**  
   Chi phí chuyển dịch động học và hình học giữa cặp biến thể $(u \in \mathcal{V}_{i-1}, w \in \mathcal{V}_i)$:
   $$C_{\text{trans}}(u, w) = \min_{a \in \{\text{LIFT}, \text{CONN}\}} J(u, w, a)$$
3. **Ràng buộc cứng (Hard Constraints):**  
   Điều kiện bắt buộc không được vi phạm (tương đương chi phí $+\infty$):
   - Ký tự không hỗ trợ cổng vào/ra ($\text{can\_in}=0$ hoặc $\text{can\_out}=0$).
   - Giật lùi sang trái quá mức ($\Delta x \le -0.2\text{ mm}$) hoặc vượt tầm với ($d \ge 12.0\text{ mm}$).
   - Cầu nối cắt ngang bất kỳ đoạn thẳng nào của thân chữ hoặc dấu tiếng Việt.
   - Nét vẽ vượt ra ngoài khổ giấy ($[0, W_{\text{paper}}] \times [0, H_{\text{paper}}]$).

### 2.7. Phương Trình Bellman / Viterbi DP Trên Trellis DAG

Quy hoạch động thực hiện trên từng từ qua hàm `engine.py::optimize_word_dag`:
- **Khởi tạo tầng đầu ($i = 1$):**
  $$V(1, j) = w_5 \cdot C_{\text{legibility}}(v_{1, j}), \quad \forall j \in \{1, \dots, K_1\}$$
- **Quy hoạch động chuyển tiếp ($i = 2, \dots, N$):**
  $$V(i, j) = \min_{p \in \{1, \dots, K_{i-1}\}} \left[ V(i-1, p) + \text{TransCost}(v_{i-1, p}, v_{i, j}) \right]$$
  $$BP(i, j) = \arg\min_{p \in \{1, \dots, K_{i-1}\}} \left[ V(i-1, p) + \text{TransCost}(v_{i-1, p}, v_{i, j}) \right]$$
  $$\text{Conn}(i, j) = \text{Decision}_{\text{conn}}(v_{i-1, BP(i, j)}, v_{i, j})$$
- **Truy hồi ngược:** Bắt đầu từ trạng thái kết thúc $j_N^* = \arg\min_j V(N, j)$ và truy hồi qua $BP(i, j)$ để trích xuất chuỗi biến thể $\mathbf{v}^*$ và quyết định nối nét $\mathbf{a}^*$.

---

## 3. Định Nghĩa Chính Xác Ba Baseline Đối Chứng

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MA TRẬN ĐỐI CHỨNG CA-VHC                               │
├─────────────────────┬─────────────────────┬─────────────────────┬──────────────────────┤
│ B1: Static Glyphs   │ B2: Greedy          │ B3: Current Trellis │ Proposed CA-VHC      │
│  - Luôn nhấc bút    │  - Nối nét tham lam │  - Viterbi DP từ    │  - Viterbi DP từ     │
│  - Chỉ dùng 'std'   │  - Không nhìn xa    │  - Chưa xét dấu     │  - Diacritic-aware   │
│  - Không biến thể   │  - Dễ kẹt cực tiểu  │  - Dấu dồn cuối từ  │  - Delayed-ordering  │
└─────────────────────┴─────────────────────┴─────────────────────┴──────────────────────┘
```

### 3.1. Baseline 1: Static Glyphs Renderer (B1)
- **Bản chất:** Mô phỏng phương pháp kết xuất ký tự nét đơn tĩnh truyền thống.
- **Input:** Chuỗi văn bản tiếng Việt Unicode, Font Pack (`oly`, `omni_casual`), Render Profile ($font\_size\_mm = 7.0$).
- **Output:** Tập nét polyline trong đó mọi ký tự đứng riêng rẽ.
- **Hành vi bị tắt:** Tắt toàn bộ Trellis DAG; chỉ dùng duy nhất biến thể canonical `std` ($K_i = 1$); mọi bước $a_{i-1, i} \equiv \text{LIFT}$; không gọi `build_ligature_bridge`; số lần nhấc bút giữa các thân chữ luôn là $N - 1$.
- **Seed:** Cùng seed 32-bit.
- **Metrics thu thập:** `total_path_length_mm`, `pen_lift_distance_mm`, `pen_lift_count`, `collision_count` (= 0), `optimize_time_ms` (= 0.0 ms).

### 3.2. Baseline 2: Greedy Heuristic (B2)
- **Bản chất:** Tại mỗi bước $i-1 \to i$, chọn biến thể $w \in \mathcal{V}_i$ và quyết định $a$ có chi phí chuyển tiếp $\text{TransCost}(v_{i-1}^*, w)$ nhỏ nhất ngay tại bước đó, không nhìn trước các ký tự tiếp theo.
- **Input:** Cùng chuỗi văn bản, Font Pack, Render Profile, Seed.
- **Output:** Tập nét có một số cầu nối cục bộ.
- **Hành vi bị tắt:** Tắt bảng quy hoạch động toàn cục $V(i, j)$ và con trỏ truy hồi $BP(i, j)$. Khóa cứng trạng thái bước $i$ ngay sau khi xét bước $i-1$.
- **Seed:** Cùng seed 32-bit.
- **Metrics thu thập:** Đầy đủ 7 metrics.

### 3.3. Baseline 3: Current Trellis DAG (B3 — Hiện Trạng Chưa Có Ràng Buộc Dấu)
- **Bản chất:** Thuật toán Viterbi DP hiện có trong mã nguồn (`engine.py::optimize_word_dag`). Tối ưu toàn cục thân chữ cái nhưng **chưa có ràng buộc dấu tiếng Việt trong quá trình tối ưu**.
- **Input:** Cùng chuỗi văn bản, Font Pack, Render Profile, Seed.
- **Output:** Tập nét tối ưu thân chữ; dấu tiếng Việt sinh sau bằng `engine.py::generate_accents` và append tuần tự ở cuối từ (`word_secondary_strokes`).
- **Hành vi bị tắt / Giới hạn:** `bridge_collision_cost` chỉ nhận nét thân chữ chính (`scaled_prim`), hoàn toàn không nhận diện nét dấu. Thứ tự nét phụ/dấu dồn về cuối từ chưa qua quy hoạch chuyển động.
- **Seed:** Cùng seed 32-bit.
- **Metrics thu thập:** Đầy đủ 7 metrics.

---

## 4. Thiết Kế Diacritic-Aware DAG & Quy Hoạch Nét Trễ

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
  - Ngưỡng cách ly an toàn: $\delta_{\text{clearance}} = 0.50\text{ mm}$ (với $font\_size\_mm = 7.0\text{ mm}$).
  - Vùng mỏ neo an toàn: $\delta_{\text{anchor}} = 0.35\text{ mm}$ quanh $\mathbf{P}_{\text{entry}}$ và $\mathbf{P}_{\text{exit}}$ của chính glyph để tránh tự phạt điểm tiếp giáp.

### 4.2. Cơ Chế Đưa Dấu Vào Trellis DAG (Không Bùng Nổ Trạng Thái)

> [!NOTE]
> Trong chính tả tiếng Việt, vị trí mỏ neo và sự tồn tại của dấu được xác định đơn trị bởi ký tự Unicode NFD. Dấu là **chướng ngại vật hình học xác định trước (deterministic geometric obstacles)**, không phải biến thể tìm kiếm. Do đó $K_i \le 3$ được bảo toàn nguyên vẹn.

1. **Tiền tính toán tọa độ dấu (Pre-DP):**
   $$\mathcal{S}_{\text{diac\_world}, i} = \left\{ s \odot \mathbf{s}_i + \mathbf{o}_i \mid s \in \text{generate\_accents}(b_i, \mathcal{A}_i, cx_i) \right\}$$
2. **Đưa vào hàm đánh giá chuyển tiếp (`eval_transition`):**
   Mở rộng tập nét cản trở trong `bridge_collision_cost`:
   $$\mathcal{S}_{\text{obstacles}} = \mathcal{S}_{\text{prim\_world}, i-1} \cup \mathcal{S}_{\text{prim\_world}, i} \cup \mathcal{S}_{\text{diac\_world}, i-1} \cup \mathcal{S}_{\text{diac\_world}, i}$$

### 4.3. Phân Định Collision Cứng vs Penalty Mềm

1. **Ràng buộc cứng (Hard Collision Rejection):**
   Nếu đoạn thẳng của cầu nối $\mathcal{B}$ cắt ngang đoạn thẳng của nét dấu (`engine.py::segments_intersect` trả về `True`):
   $$C_{\text{collision}} = +\infty \implies \text{Cost}_{\text{conn}} = +\infty$$
   Quyết định $\text{CONNECT}$ bị loại trừ ngay lập tức; giải thuật bắt buộc chọn $\text{LIFT}$.
2. **Penalty mềm (Soft Clearance Penalty):**
   Nếu khoảng cách $\text{dist} < \delta_{\text{clearance}} = 0.50\text{ mm}$ nhưng không cắt:
   $$\text{penetration} = \frac{\delta_{\text{clearance}} - \text{dist}}{\delta_{\text{clearance}}} \in (0.0, 1.0]$$
   $$C_{\text{collision}} = 2.0 + 4.0 \cdot \text{penetration}$$

### 4.4. Thiết Kế Quy Hoạch Thứ Tự Nét Trễ (Delayed-Stroke Ordering)

Tập hợp $M$ nét thứ cấp của một từ $\mathcal{D}_{\text{word}} = \{d_1, d_2, \dots, d_M\}$ bao gồm: dấu thanh, dấu phụ nguyên âm, gạch ngang đ/t, chấm i/j.

Thay vì append tuần tự ngây thơ dồn về cuối từ (gây hiện tượng đầu bút bay giật ngược nhiều lần):
1. **Trường hợp $M \le 6$ (chiếm $\ge 99\%$ các từ tiếng Việt):**
   Không gian hoán vị tối đa $M! \le 6! = 720$. Áp dụng giải thuật **vét cạn chính xác (Exact Enumeration)** để tìm thứ tự $\pi^*$ đạt cực tiểu toàn cục ($\arg\min$) quãng đường di chuyển pen-up thực tế xuất phát từ điểm kết thúc thân từ $\mathbf{P}_{\text{last}}$:
   $$\pi^* = \arg\min_{\pi \in \mathcal{P}_M} \left[ \|\mathbf{P}_{\text{last}} - \text{start}(\pi_1)\| + \sum_{k=1}^{M-1} \|\text{end}(\pi_k) - \text{start}(\pi_{k+1})\| \right]$$
   *Lưu ý khoa học:* Không gian hoán vị tối đa là $6! = 720$; thời gian thực thi (runtime) thực tế phải được đo đạc bằng thực nghiệm cụ thể và không tuyên bố trước khi có benchmark.
2. **Trường hợp $M > 6$ (trường hợp biên hoặc từ ghép đặc biệt):**
   Sử dụng giải thuật **Nearest Neighbor Heuristic** kết hợp Kinematic Cost (`path_optimizer.py::nearest_neighbor_order`) làm phương án dự phòng (fallback) để đảm bảo độ phức tạp thời gian đa thức $O(M^2)$.

---

## 5. Kế Hoạch Benchmark Định Lượng

### 5.1. Hai Tập Ngữ Liệu: Development Corpus & Holdout Corpus

> [!WARNING]
> Loại bỏ hoàn toàn nhận định "bộ 20 từ bao phủ 100% tiếng Việt". Để chống hiện tượng quá khớp (overfitting) trọng số và quy tắc, nghiên cứu thiết kế tách biệt 2 tập ngữ liệu độc lập:

1. **Development Corpus (`BENCHMARK_DEV_CORPUS_20`):** 20 từ đại diện bao phủ các tổ hợp nguyên âm biến âm, thanh điệu và phụ âm nhô cao/thấp (ascender/descender). Dùng trong quá trình phát triển, tinh chỉnh tham số và kiểm thử hồi quy:
   ```python
   BENCHMARK_DEV_CORPUS_20 = [
       "tiếng", "việt", "nguyễn", "nước", "đường",
       "khuấy", "thuở", "nghỉ", "hoặc", "chuẩn",
       "trường", "quyện", "nghĩ", "phượng", "kiều",
       "hướng", "mượt", "bước", "vẫy", "nhánh"
   ]
   ```
2. **Holdout Corpus (`BENCHMARK_HOLDOUT_CORPUS_20`):** 20 từ/cụm từ độc lập **tuyệt đối không dùng khi phát triển hoặc tinh chỉnh trọng số**, dùng để nghiệm thu đánh giá tính tổng quát hóa (generalization) của giải thuật:
   ```python
   BENCHMARK_HOLDOUT_CORPUS_20 = [
       "nghiêng", "khoác", "truyền", "hoàng", "nguyệt",
       "thoáng", "quỳnh", "nhuộm", "duyệt", "khoảnh",
       "giường", "chuyện", "xoay", "bỗng", "quét",
       "khẽ", "nhặt", "nguồn", "sưởi", "vẹn"
   ]
   ```

### 5.2. Môi Trường Thực Nghiệm & Giao Thức Đo Đạc (Benchmark Protocol)

Để bảo đảm tính tái lập khoa học, mọi thực nghiệm phải **ghi nhận chi tiết siêu dữ liệu môi trường vận hành thực tế (Execution Metadata)** thay vì chỉ nêu cấu hình tối thiểu:
1. **CPU Model:** Tên đầy đủ vi xử lý (ví dụ: `Intel(R) Core(TM) i7-11800H @ 2.30GHz`), số nhân vật lý và số luồng logic.
2. **OS & Version:** Bản phát hành và build cụ thể (ví dụ: `Windows 11 Pro 64-bit Build 22631` hoặc `Ubuntu 22.04 LTS Kernel 5.15`).
3. **Python Version:** Phiên bản patch release chính xác (ví dụ: `Python 3.11.9 64-bit`).
4. **NumPy Version & BLAS Backend:** Phiên bản thư viện và backend tính toán (ví dụ: `NumPy 1.26.4 + OpenBLAS`).
5. **Git Commit Hash:** Mã hash commit của repository OmniDraw tại thời điểm thực thi.
6. **Power / Performance Mode:** Chế độ cấp nguồn của hệ thống (ví dụ: `AC Connected, High Performance Mode`).

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
| **7. Thời gian tối ưu DAG** | `optimize_time_ms` | $ms$ | Thời gian thực thi riêng biệt của `engine.py::optimize_word_dag` đo qua `time.perf_counter()` |

> [!NOTE]
> **Về `optimize_time_ms` trong mã nguồn hiện tại:**  
> Hiện tại trường `svg_metrics.optimize_time_ms` trong `backend/handwriting/engine.py` đang trả về giá trị placeholder cố định `0.0`. PR1 có trách nhiệm đo lường độc lập thời gian thực thi của `optimize_word_dag` bằng `time.perf_counter()` để cung cấp số liệu thực tế cho báo cáo benchmark.

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
| **H2.2: Khoảng cách cách ly** | $d_{\min} \ge 0.50\text{ mm}$ | $d_{\min} < 0.35\text{ mm}$ | $0.35\text{ mm} \le d_{\min} < 0.50\text{ mm}$ |
| **H3.1: Thời gian Viterbi DP** | Median $\le 5.0\text{ ms}$ **VÀ** p95 $\le 10.0\text{ ms}$ | Median $> 10.0\text{ ms}$ **HOẶC** p95 $> 20.0\text{ ms}$ | Mọi trường hợp còn lại |
| **H3.2: Chi phí độ cong tiếp tuyến** | Giảm $\ge 15.0\%$ vs B2 **VÀ** không góc $> 120^\circ$ | Giảm $\le 0.0\%$ vs B2 **HOẶC** có góc $> 120^\circ$ | Mọi trường hợp còn lại (giảm $0\text{–}15\%$ và không góc $> 120^\circ$) |

---

## 6. Ma Trận Truy Vết Khoa Học (Traceability Matrix)

| RQ | Giả thuyết | Metrics đo đạc | Đối chứng | Kịch bản kiểm thử | Vùng FAIL (Ưu tiên 1) | Vùng PASS (Ưu tiên 2) | Vùng INCONCLUSIVE (Ưu tiên 3) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RQ1** | H1.1 | `pen_lift_distance_mm` | B1, B2 | Dev & Holdout corpus × 2 font × 4 seeds | Giảm $< 15\%$ vs B1 hoặc $< 5\%$ vs B2 | Giảm $\ge 25\%$ vs B1 và $\ge 10\%$ vs B2 | Mọi trường hợp còn lại |
| **RQ1** | H1.2 | `pen_lift_count` | B1 | Đếm trên các từ hỗ trợ nối nét | Giảm $< 20\%$ vs B1 | Giảm $\ge 35\%$ vs B1 | Giảm $20\text{–}35\%$ vs B1 |
| **RQ1** | H1.3 | `total_path_length_mm` | B1 | Đo tổng chiều dài nét tiếp xúc giấy | Tăng $> 15\%$ vs B1 | Tăng $\le 10\%$ vs B1 | Tăng $10\text{–}15\%$ vs B1 |
| **RQ2** | H2.1 | `collision_count` | B3 | Kiểm tra giao cắt đoạn thẳng bridge vs dấu | $collision\_count \ge 1$ | $collision\_count = 0$ | — |
| **RQ2** | H2.2 | `minimum_diacritic_clearance_mm` | B3 | Đo khoảng cách ngắn nhất bridge vs dấu | $< 0.35\text{ mm}$ | $\ge 0.50\text{ mm}$ | $0.35\text{–}0.50\text{ mm}$ |
| **RQ3** | H3.1 | `optimize_time_ms` (perf_counter) | B2, B3 | 50 lần lặp sau warm-up trên môi trường ghi nhận | Median $> 10\text{ ms}$ hoặc p95 $> 20\text{ ms}$ | Median $\le 5\text{ ms}$ và p95 $\le 10\text{ ms}$ | Mọi trường hợp còn lại |
| **RQ3** | H3.2 | `curvature_cost` | B2 | Đo tổng chi phí bẻ tiếp tuyến ngòi bút | Giảm $\le 0\%$ vs B2 hoặc có góc $> 120^\circ$ | Giảm $\ge 15\%$ vs B2 và không góc $> 120^\circ$ | Mọi trường hợp còn lại |

---

## 7. Kế Hoạch Triển Khai Tiếp Theo (Chia 5 PR Nhỏ)

Tuân thủ nguyên tắc thay đổi tối thiểu, bảo toàn API công khai và có tiêu chí nghiệm thu rõ ràng:

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│  PR1   │ ──▶ │  PR2   │ ──▶ │  PR3   │ ──▶ │  PR4   │ ──▶ │  PR5   │
│Trace & │     │ 3 Base-│     │Diacritic│    │Delayed │     │Bench-  │
│Metrics │     │ lines  │     │Obstacle│     │Stroke  │     │mark &  │
│Fixtures│     │        │     │  Cost  │     │Order   │     │Ablation│
└────────┘     └────────┘     └────────┘     └────────┘     └────────┘
```

### PR1: Structured Render Trace, Benchmark Corpus & Metrics Fixtures
- **Phạm vi kỹ thuật:**
  - Định nghĩa 2 tập ngữ liệu `BENCHMARK_DEV_CORPUS_20` và `BENCHMARK_HOLDOUT_CORPUS_20`.
  - **Thiết kế Structured Render Trace:** Để đo chính xác khoảng cách cách ly và đếm va chạm mà không làm sai lệch do tự kiểm tra mút tiếp xúc, bộ đo cần phân biệt được từng loại nét (`base_stroke`, `bridge_stroke`, `secondary_stroke`, `diacritic_stroke`).  
    Xây dựng hàm helper nội bộ `text_to_strokes_structured(...)` (hoặc tùy chọn cờ nội bộ `_return_trace=True`).  
    **Bảo toàn tuyệt đối chữ ký API công khai:** `generate_handwriting_svg()` và `text_to_strokes()` giữ nguyên $100\%$ đầu vào, đầu ra và kiểu dữ liệu `List[np.ndarray]`.
  - Triển khai module đo đạc hình học độc lập: tính `minimum_diacritic_clearance_mm`, đếm `collision_count`, tính `curvature_cost`, và đo riêng thời gian `optimize_word_dag` qua `time.perf_counter()`.
- **Files dự kiến chạm:**
  - `backend/handwriting/benchmark_fixtures.py` (Mới)
  - `backend/handwriting/metrics_evaluator.py` (Mới)
  - `backend/handwriting/engine.py` (Bổ sung helper nội bộ trích xuất trace nét, không đổi public API)
  - `tests/test_ca_vhc_metrics.py` (Mới)
- **Definition of Done (DoD):**
  - Unit test cho các hàm đo đạc pass 100%.
  - Public API `generate_handwriting_svg` không bị thay đổi bất kỳ tham số nào.
  - Đo đạc chính xác trên trace cấu trúc, phân biệt rõ nét dấu và cầu nối.

### PR2: Chuẩn Hóa và Khóa Ba Baseline Đối Chứng (B1, B2, B3)
- **Phạm vi kỹ thuật:**
  - Đóng gói các adapter thực nghiệm độc lập cho B1 (Static Glyphs), B2 (Greedy Heuristic), B3 (Current Trellis DAG).
  - Cho phép runner benchmark gọi độc lập từng baseline thông qua tham số thực nghiệm nội bộ mà không tác động luồng ứng dụng chính.
- **Files dự kiến chạm:**
  - `backend/handwriting/baselines.py` (Mới)
  - `backend/handwriting/engine.py` (Thêm cờ nội bộ `_algorithm_mode` phục vụ thí nghiệm)
  - `tests/test_baselines.py` (Mới)
- **Definition of Done (DoD):**
  - B1 luôn tạo số lần nhấc bút $N - 1$ giữa các thân chữ.
  - B2 đưa ra quyết định cục bộ không đổi khi ký tự phía sau biến thiên.
  - B3 tái lập $100\%$ kết quả hình học của `engine.py` hiện tại.

### PR3: Diacritic Obstacle Cost Trong Trellis DAG
- **Phạm vi kỹ thuật:**
  - Đưa tập nét dấu `diacritic_strokes_world` vào `engine.py::eval_transition`.
  - Mở rộng `engine.py::bridge_collision_cost` để kiểm tra giao cắt và tính phạt mềm khi vi phạm khoảng cách an toàn $\delta_{\text{clearance}} = 0.50\text{ mm}$.
  - Thiết lập hard rejection: loại bỏ quyết định $\text{CONNECT}$ nếu cắt ngang nét dấu.
- **Files dự kiến chạm:**
  - `backend/handwriting/engine.py`
  - `tests/test_diacritic_dag.py` (Mới)
- **Definition of Done (DoD):**
  - $collision\_count$ giảm về đúng 0 trên toàn bộ các từ kiểm thử có dấu phức tạp (`tiếng`, `kiều`, `khuấy`).
  - Không gây thoái lui (regression) trên các bài test QA hiện có trong `backend/handwriting/qa_specimens.py`.

### PR4: Delayed-Stroke Ordering Optimizer
- **Phạm vi kỹ thuật:**
  - Triển khai module sắp xếp thứ tự nét trễ: vét cạn chính xác (Exact Enumeration) khi số nét phụ/dấu $M \le 6$ (không gian hoán vị tối đa $6! = 720$) và fallback Nearest Neighbor Heuristic khi $M > 6$.
  - Tích hợp lời gọi sắp xếp nét trễ vào cuối từ trước khi áp dụng bio-mimetic variation.
- **Files dự kiến chạm:**
  - `backend/handwriting/delayed_strokes.py` (Mới)
  - `backend/handwriting/engine.py` (Gọi bộ sắp xếp nét trễ)
  - `tests/test_delayed_strokes.py` (Mới)
- **Definition of Done (DoD):**
  - Quãng đường pen-up giữa các nét phụ/dấu cuối từ giảm $\ge 20\%$ so với thứ tự append tuần tự ban đầu.
  - Bộ kiểm thử xác nhận vét cạn chính xác tìm ra đúng nghiệm tối ưu toàn cục quãng đường pen-up cho $M \le 6$; runtime được đo đạc và ghi nhận đầy đủ.

### PR5: Benchmark Runner, Automated Reporting & Ablation Study
- **Phạm vi kỹ thuật:**
  - Xây dựng CLI runner thực thi toàn bộ ma trận (Proposed CA-VHC vs 3 Baseline × 20 từ Dev + 20 từ Holdout × 2 font × 2 style × 4 seed × 50 iterations).
  - Tự động ghi nhận log CSV ra đường dẫn được chỉ định (hoặc thư mục ignore `logs/`), tính toán Median và p95.
  - Báo cáo riêng kết quả độ trễ theo từng hệ điều hành và môi trường thực tế được ghi nhận.
  - Bóc tách độ nhạy (ablation) từng thành phần trọng số $w_1 \dots w_5$.
- **Files dự kiến chạm:**
  - `backend/handwriting/benchmark_runner.py` (Mới)
  - `tests/test_benchmark_runner.py` (Mới)
- **Definition of Done (DoD):**
  - Script chạy trọn vẹn không crash, tự động xuất bảng số liệu định dạng Markdown/LaTeX.
  - Không commit tệp log CSV vào git.

---

## 8. Đối Chiếu Code Hiện Tại & Khoảng Trống Triển Khai (Implementation Gaps)

| STT | Hạng mục trên tài liệu / Roadmap | Hiện trạng trong Code thực tế | Phân loại khoảng trống | Hướng xử lý kỹ thuật |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Ràng buộc dấu trong Trellis DAG** | `engine.py::optimize_word_dag` hiện chỉ nhận `char_info_list` với nét thân chữ (`scaled_prim`). Dấu chỉ được sinh sau khi DP đã giải xong (`engine.py:1381`). | **Gap thuật toán cốt lõi (P0)** | Triển khai PR3: Tính trước tọa độ nét dấu và truyền vào `eval_transition` để tham gia vào hàm chi phí va chạm của DAG. |
| **2** | **Phát hiện va chạm với dấu** | `engine.py::bridge_collision_cost` chỉ kiểm tra va chạm giữa cầu nối với nét thân chữ lân cận, hoàn toàn chưa có tham số nhận tập nét dấu. | **Gap hình học cốt lõi (P0)** | Triển khai PR3: Mở rộng `bridge_collision_cost` để kiểm tra giao cắt và khoảng cách an toàn với tập nét dấu $\mathcal{S}_{\text{diacritics}}$. |
| **3** | **Thứ tự nét trễ (Delayed-stroke)** | Trong `engine.py:1322-1393`, các nét phụ và dấu (`word_secondary_strokes`) được gom thuần túy bằng lệnh `.append()` tuần tự theo thứ tự xuất hiện. | **Gap tối ưu chuyển động (P0)** | Triển khai PR4: Áp dụng Exact Enumeration ($M \le 6$) và Nearest Neighbor heuristic ($M > 6$) xuất phát từ điểm cuối thân từ. |
| **4** | **Bộ ba Baseline đối chứng** | Chưa có module hoặc cờ chạy độc lập cho Baseline 1 (Static Glyphs) và Baseline 2 (Greedy Heuristic) trong mã nguồn. Hiện tại chỉ có duy nhất Baseline 3. | **Gap framework thực nghiệm (P0)** | Triển khai PR2: Tách và đóng gói 3 baseline thành các adapter/hàm chuẩn hóa phục vụ runner thực nghiệm. |
| **5** | **Thời gian tối ưu hóa DAG** | `svg_metrics.optimize_time_ms` trong `engine.py` đang trả về placeholder cố định `0.0`. | **Gap đo đạc thực nghiệm (P0)** | Triển khai PR1: Đo riêng thời gian thực thi của `optimize_word_dag` qua `time.perf_counter()`. |
| **6** | **Trích xuất nét có cấu trúc** | `text_to_strokes` hiện tại flatten toàn bộ nét thành `List[np.ndarray]`, khiến bộ đo va chạm không thể phân biệt mút tiếp xúc hợp lệ và nét dấu. | **Gap đo đạc thực nghiệm (P0)** | Triển khai PR1: Thêm helper nội bộ `text_to_strokes_structured` giữ nguyên tag của từng nét mà không đổi public API. |

---

## Kết Luận & Hành Động Tiếp Theo

Tài liệu này đã khóa toàn diện cơ sở nghiên cứu, mô hình toán học và lộ trình kỹ thuật tối thiểu cho lõi giải thuật **CA-VHC**.

**Hành động kỹ thuật kế tiếp:** Tiến hành triển khai **PR1 (Structured Render Trace, Benchmark Corpus & Metrics Fixtures)** theo đúng phạm vi đã định nghĩa.
