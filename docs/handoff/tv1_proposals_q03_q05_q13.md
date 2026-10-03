# Đề xuất Chuẩn hóa Dữ liệu TV1: Review Fixtures TV4, Quality Bounds (Q03), Bảng Trễ k (Q05) và Quy chế Custody HOLDOUT (Q13)

**Tác giả:** TV1 (Nguyễn Hoàng Thắng — Lead AI Data & Candidates)  
**Đơn vị phối hợp soạn thảo:** DeepSeek Architect Bridge  
**Ngày lập:** 03/10/2026  
**Nhánh làm việc:** `codex/tv1-research-candidates-20261002` (Worktree: `OmniDraw-tv1-research`)  
**Tài liệu tham chiếu:** Docs 30, Docs 31, Docs 32, Docs handoff README và `pending_decisions.md`

---

## 1. Đánh giá độc lập về các fixtures DEV tự tạo của TV4 (`solver_dev_cases.json`, `method_gap_example.json`)

### 1.1. Mục đích và bản chất kỹ thuật
Các tệp fixture do TV4 khởi tạo trong `tests/research/fixtures/` (`solver_dev_cases.json`, `replay_dev_cases.json`, `method_gap_example.json`) được xây dựng nhằm phục vụ việc kiểm thử nội bộ giải thuật Quy hoạch động (DP recurrence), kiểm tra tính đúng đắn của logic chuyển tiếp (BODY/MARK/END) và kiểm tra tính toán chi phí (arithmetic replay).

### 1.2. Các giới hạn hình học và học thuật
1. **Hình học nhân tạo (Toy straight lines):** Các nét thân và nét dấu trong fixtures của TV4 chủ yếu là các đoạn thẳng ngang 1D nhân tạo song song (ví dụ: `[0,0]->[1,0]`, `[0,1]->[1,1]`, `[0,2]->[1,2]`). Chúng không phản ánh cấu trúc hình học thực tế của chữ viết tay (các đường cong Bézier, nét móc, khuyên, hay nét oval).
2. **Thiếu thông tin font, anchor và license thật:**
   - Không có metadata font gốc (font family, weight, foundry) để truy xuất nguồn gốc nét.
   - Không có tọa độ mỏ neo thật (ground-truth anchor) được kiểm chuẩn ngôn ngữ học tiếng Việt.
   - Không có tuyên bố bản quyền hoặc giấy phép sử dụng hợp pháp (license manifest).
3. **Phân loại nhãn dấu chưa chuẩn:** Cả dấu mũ và dấu thanh đều được gán nhãn chung là `dev-tone` thay vì phân định rõ ràng giữa dấu cấu tạo chữ cái (`shape`: mũ `^`, móc `?`, trăng `˘`) và dấu thanh điệu (`tone`: sắc, huyền, hỏi, ngã, nặng).

### 1.3. Kết luận về phạm vi sử dụng của TV1
TV1 xác nhận:
* Bộ fixture của TV4 **chỉ có giá trị kiểm thử giải thuật solver nội bộ**.
* **TV1 KHÔNG thẩm duyệt và KHÔNG công nhận** các tệp này là font, glyph, hay dataset chữ viết tay tiếng Việt chính thức của đề tài.
* Các tệp này không được dùng làm bằng chứng kết luận về năng lực tạo chữ hay đưa vào các tập đánh giá chính thức.

---

## 2. Đề xuất chuẩn hóa Q03 — Quality Bounds & Reference Geometry trên DEV (PROPOSED / PENDING)

> [!IMPORTANT]
> **Tình trạng Gate Q03: PROPOSED / PENDING.** Các giá trị tham số ($c_{\min}$, $r_{\text{contact}}$, $\Delta y$, $\Delta \theta$, $\Delta \text{AR}$) dưới đây là đề xuất kỹ thuật từ TV1 dựa trên đo đạc thực nghiệm các ứng viên DEV. Chúng **CHƯA PHẢI là ngưỡng đã freeze** và cần sự thẩm định, đối chiếu cùng TV2 (baseline runner) và TV3 (hardware oracle).
> Khoảng hở đường tâm (centerline clearance) là đại diện hình học trong mô hình tối ưu, **không tự bảo đảm chống lem mực thực tế** nếu chưa qua nghiệm thu vật lý với đầu bút/mực của TV3.

Để đảm bảo tính nhất quán giữa bộ giải DP (TV4), bộ kiểm chứng độc lập (TV3) và các baseline phân tầng (TV2), TV1 đề xuất bộ định nghĩa toán học và tiêu chuẩn chất lượng hình học chung trên tập DEV:

### 2.1. Định nghĩa chuẩn chiều cao thân chữ ($x$-height, ký hiệu $h_x$)
* **Định nghĩa:** Chiều cao thẳng đứng của phần thân chữ cái nguyên âm thường (không tính ascender/descender), đo từ baseline ($y_{\min}$) đến meanline ($y_{\max}$):
  $$h_x = \max_{(x, y) \in \text{body}} y - \min_{(x, y) \in \text{body}} y$$
* **Trong hệ tọa độ tham số DEV:** Baseline được chuẩn hóa tại $y = 0.0\,\text{mm}$. Với các glyph tiêu chuẩn ('a', 'o', 'e'), $h_x = 1.80\,\text{mm}$ hoặc $2.00\,\text{mm}$.

### 2.2. Định nghĩa độ dịch dấu ($\Delta y_{\text{mark}}$) và xử lý phân biệt dấu trên / dấu dưới / dấu chồng
Để tránh nhầm lẫn giữa tọa độ có dấu (signed coordinates) và khoảng cách hình học, $\Delta y_{\text{mark}}$ được định nghĩa là **khoảng hở thẳng đứng dương (positive vertical clearance)**:

1. **Dấu trên (Marks Above — mũ `^`, sắc, huyền, hỏi, ngã):**
   Khoảng hở từ đỉnh thân chữ cơ sở đến điểm thấp nhất của dấu:
   $$\Delta y_{\text{mark, above}} = \min_{(x, y) \in \text{mark}} y - \max_{(x, y) \in \text{body}} y$$
   * **Ngưỡng đề xuất:** $\Delta y_{\text{mark, above}} \in [0.15, 0.45] \times h_x$.
   * Với $h_x = 1.80\,\text{mm}$, dải cho phép là $[0.27\,\text{mm}, 0.81\,\text{mm}]$. Giá trị cận dưới $0.27\,\text{mm} > c_{\min} = 0.20\,\text{mm}$ đảm bảo không vi phạm clearance tối thiểu.

2. **Dấu dưới chân chữ (Marks Below — dấu nặng `.`):**
   Khoảng hở từ điểm cao nhất của dấu dưới đến đáy baseline của thân chữ:
   $$\Delta y_{\text{mark, below}} = \min_{(x, y) \in \text{body}} y - \max_{(x, y) \in \text{mark}} y$$
   *(Do dấu nằm dưới baseline $y=0$, $y_{\max}(\text{mark}) < 0$, nên $\Delta y_{\text{mark, below}} = 0 - y_{\max}(\text{mark}) > 0$).*
   * **Ngưỡng đề xuất:** $\Delta y_{\text{mark, below}} \in [0.15, 0.45] \times h_x = [0.27\,\text{mm}, 0.81\,\text{mm}]$.

3. **Dấu chồng (Stacked Diacritics — ví dụ dấu thanh đặt trên dấu mũ `ấ, ề, ổ`):**
   Khoảng hở từ điểm cao nhất của dấu cấu tạo (circumflex) đến điểm thấp nhất của dấu thanh (acute):
   $$\Delta y_{\text{mark, stacked}} = \min_{(x, y) \in \text{tone}} y - \max_{(x, y) \in \text{circumflex}} y$$
   * **Ngưỡng đề xuất:** $\Delta y_{\text{mark, stacked}} \in [0.15, 0.45] \times h_x$.

4. **Phân biệt Clearance nội bộ DEV và Sai lệch Anchor tham chiếu ($\delta_{\text{anchor}}$):**
   * Trên tập DEV hiện tại (synthetic polylines, chưa có font typography chuẩn), ta đo clearance hình học $\Delta y$ đối với thân chữ.
   * Khi Font Pilot (Q16) được mở với font tham chiếu thực sự, sai lệch điểm mỏ neo sẽ được đo bằng khoảng cách Euclidean so với ground truth font anchor:
     $$\delta_{\text{anchor}} = \|\mathbf{p}_{\text{mark}} - \mathbf{p}_{\text{ref}}\|_2 \le \epsilon_{\text{anchor}}$$
     Khi đó với glyph tham chiếu gốc, $\delta_{\text{anchor}} = 0$.

### 2.3. Định nghĩa độ lệch góc nghiêng ($\Delta \theta$) và biến thiên tỷ lệ khung bao ($\Delta \text{AR}$)
* **Góc trục chính ($\theta$):** Góc của đường hồi quy tuyến tính (hoặc đoạn thẳng chính) của nét thân chính so với trục hoành:
  $$\theta = \arctan2(\Delta y, \Delta x)$$
  * Sai lệch so với góc danh định ($\theta_{\text{nominal}} = 90^\circ$ cho kiểu đứng, $75^\circ$ cho kiểu nghiêng $15^\circ$):
    $$|\Delta \theta| = |\theta_{\text{candidate}} - \theta_{\text{nominal}}| \le 5^\circ \text{ (kiểu đứng)}, \quad |\Delta \theta| \le 15^\circ \text{ (kiểu nghiêng)}$$
* **Tỷ lệ khung bao ($\text{Aspect Ratio} - \text{AR}$):** Cho hộp bao bounding box $[w, h]$, $\text{AR} = w / h$.
  * Biến thiên tương đối so với biến thể chuẩn danh định $\text{AR}_0$:
    $$|\Delta \text{AR}| = \frac{|\text{AR}_{\text{candidate}} - \text{AR}_0|}{\text{AR}_0} \le 10\%$$
* **Topology:** Không chấp nhận tự cắt chéo (self-crossing) hoặc quay đầu ngược hướng (backtracking) trên cùng một nét vẽ đơn.

### 2.4. Bảng đo đạc thực nghiệm các ứng viên DEV (Empirical Measurements)

Dưới đây là số liệu đo đạc thực tế trên toàn bộ các ứng viên trong manifest DEV hiện hành (`tv1_dev_manifest.json`):

| Ca & Ứng viên | Thân chữ $h_x$ | Chiều rộng $w$ | AR ($w/h_x$) | Loại dấu & Tên nét | Vị trí dấu | Đo đạc $\Delta y_{\text{mark}}$ | Tỷ lệ $\Delta y / h_x$ | Kết luận tiêu chuẩn |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **01: a-std** | 2.00 mm | 1.50 mm | 0.75 | Mũ (`shape_circumflex`)<br>Sắc (`tone_acute`) | Trên thân<br>Chồng mũ | 0.40 mm<br>0.40 mm | 0.20<br>0.20 | ĐẠT ($[0.15, 0.45]$)<br>ĐẠT ($[0.15, 0.45]$) |
| **01: a-alt** | 2.00 mm | 1.60 mm | 0.80 ($\Delta 6.7\%$) | Mũ (`shape_circumflex`)<br>Sắc (`tone_acute`) | Trên thân<br>Chồng mũ | 0.50 mm<br>0.40 mm | 0.25<br>0.20 | ĐẠT ($[0.15, 0.45]$)<br>ĐẠT ($[0.15, 0.45]$) |
| **01: b-std** | 4.00 mm | 1.20 mm | 0.30 | *(Thân phụ có ascender)* | — | — | — | ĐẠT |
| **02: e-std** | 1.80 mm | 1.50 mm | 0.83 | Mũ (`shape_circumflex`)<br>Nặng (`tone_dot_below`) | Trên thân<br>Dưới baseline | 0.60 mm<br>0.50 mm | 0.33<br>0.28 | ĐẠT ($[0.15, 0.45]$)<br>ĐẠT ($[0.15, 0.45]$) |
| **02: c-std** | 1.80 mm | 1.40 mm | 0.78 | *(Thân phụ)* | — | — | — | ĐẠT |
| **03: o-std** | 1.80 mm | 1.60 mm | 0.89 | Sắc (`tone_acute`) | Trên thân | 0.60 mm | 0.33 | ĐẠT ($[0.15, 0.45]$) |
| **03: t-std** | 3.50 mm | 0.80 mm | 0.23 | *(Thân đa nét có tiếp xúc)* | — | Contact (3.0, 3.5) | — | $r = 0.25\,\text{mm}$ |
| **03: o2-std** | 1.80 mm | 1.60 mm | 0.89 | *(Thân phụ)* | — | — | — | ĐẠT |
| **04: o-compact** | 1.80 mm | 1.50 mm | 0.83 | Dấu trên (`mark`) | Trên thân | 0.60 mm | 0.33 | ĐẠT ($[0.15, 0.45]$) |
| **04: o-swash** | 1.80 mm | 3.95 mm | 2.19 (flourish) | Dấu trên (`mark`) | Trên thân | 0.60 mm | 0.33 | ĐẠT ($[0.15, 0.45]$) |
| **04: t-std** | 2.50 mm | 0.00 mm | 0.00 (stem) | *(Thân giữa)* | — | — | — | ĐẠT |
| **04: o2-compact** | 1.80 mm | 1.00 mm | 0.56 | *(Thân phụ)* | — | — | — | ĐẠT |
| **04: o2-flourish** | 1.80 mm | 1.45 mm | 0.81 (flourish) | *(Thân phụ)* | — | — | — | ĐẠT |

### 2.5. Ngưỡng khoảng hở tối thiểu ($c_{\text{min}}$) và Ngoại lệ tiếp xúc (Contact)
* **Quy định cứng:** $c_{\text{min}} = 0.20\,\text{mm}$ cho mọi cặp nét bắt buộc phải tách rời.
* **Nguyên tắc:** Dưới $0.20\,\text{mm}$ là không khả thi (INFEASIBLE), không được dùng hàm phạt mềm (soft penalty) hay dung sai số học để làm giảm ngưỡng này.
* **Ngoại lệ tiếp xúc (Contact):** Chỉ được miễn trừ trong phạm vi đĩa tiếp xúc hữu hạn có bán kính khai báo rõ ràng ($r \le 0.25\,\text{mm}$) tại đúng **điểm đầu mút (endpoint)** của cả hai nét. Điểm tiếp xúc phải được whitelist rõ ràng trong contract; nếu không có whitelist hoặc lệch endpoint, kết nối trực tiếp (CONNECT) bị coi là vi phạm và ném ngoại lệ.

---

## 3. Đề xuất chuẩn hóa Q05 — Bảng trễ $k$ và Quy tắc Ưu tiên Dấu (Mark Precedence)

Theo quy định tại Docs 31 §2, đơn vị của trễ $k(j)$ là **số thân chữ kế tiếp được hoàn tất**:
* Dấu $j$ của chữ $i$ phải được hoàn tất trước khi bắt đầu thân chữ $i + k(j) + 1$.

### 3.1. Bảng quy định trễ $k$ theo nhóm dấu tiếng Việt

| Nhóm dấu | Các dấu cụ thể | Giá trị $k$ đề xuất | Cơ sở âm vị học và thực nghiệm viết |
| :--- | :--- | :---: | :--- |
| **Dấu cấu tạo chữ cái (Base Shape Marks)** | Mũ (`â, ê, ô`), Móc (`ơ, ư`), Trăng (`ă`) | **$k = 0$** | Bắt buộc hoàn tất ngay sau thân chữ sở hữu, trước khi bắt đầu thân chữ kế tiếp, nhằm khóa hình thái nguyên âm cơ sở. *(Chỉ cho phép $k=1$ nếu có ligatures đã khai báo).* |
| **Dấu thanh điệu (Tone Marks)** | Sắc, Huyền, Hỏi, Ngã, Nặng | **$k \in \{0, 1, 2\}$** | Người viết thường có xu hướng hoãn đánh dấu thanh đến cuối âm tiết hoặc sau 1–2 chữ cái kế tiếp. $k=1$ hoặc $k=2$ cho phép thuật toán tìm đường đi nối nét tối ưu hơn. |
| **Dấu dưới chân chữ (Marks Below)** | Dấu nặng (`ạ, ệ, ị, ọ, ụ`) | **$k = 0$** | Vị trí nằm dưới đường baseline ($y < 0\,\text{mm}$), ưu tiên hoàn tất sớm để tránh va chạm với dòng kẻ hoặc nét descender lân cận. |

### 3.2. Quy tắc ưu tiên thứ tự vẽ dấu (Mark Precedence)
Khi một chữ cái mang đồng thời **dấu cấu tạo** và **dấu thanh** (ví dụ: `ấ, ề, ổ, ứ, ặ`):
1. **Dấu cấu tạo PHẢI vẽ trước dấu thanh:**
   $$\text{mark\_precedence} = [(\text{"shape\_circumflex"}, \text{"tone\_acute"})]$$
   Cơ sở: Định hình thân chữ gốc trước, sau đó mới đặt dấu thanh lên trên đỉnh hoặc bên cạnh dấu cấu tạo.
2. **Quy tắc ưu tiên cấu hình:** Khai báo $k$ theo ID cụ thể của nét (`qualified_id`) luôn có độ ưu tiên cao hơn khai báo theo loại dấu chung (`mark_type`).

---

## 4. Đề xuất chuẩn hóa Q13 — Quy chế Quản lý Tách biệt (Custody) và Niêm phong HOLDOUT

Nhằm đảm bảo tính liêm chính học thuật tuyệt đối theo chuẩn quốc tế:

### 4.1. Phân loại dữ liệu và cách ly
1. **Dữ liệu DEV (Development / Synthetic):**
   - Lưu trữ tại `dataset/research/dev/` và `tests/research/fixtures/`.
   - Được mở công khai trong Git repository để phục vụ việc phát triển thuật toán của TV4, xây dựng baseline của TV2 và viết oracle của TV3.
2. **Dữ liệu CA-VHC cũ (20 từ DEV / 20 từ Holdout):**
   - Được gán nhãn chính thức là **`supplemental`** theo Docs 32 §2.
   - Chỉ dùng để kiểm tra tính tương thích ngược và hồi quy, tuyệt đối không được dùng thay thế cho tập Holdout mới của bài toán đồng tối ưu.
3. **Tập dữ liệu HOLDOUT mới (Đánh giá chính thức):**
   - **NIÊM PHONG TUYỆT ĐỐI NGOÀI GIT:** Toàn bộ nội dung tập Holdout mới được lưu trữ tại phân vùng cách ly an toàn ngoài repo Git.
   - Trên Git chỉ lưu trữ duy nhất mã băm niêm phong: `manifest_sha256` và metadata phân bố âm tiết.

### 4.2. Quy trình mở niêm phong 2 người (Two-Person Rule)
Tập dữ liệu HOLDOUT chỉ được mở ra để chạy đánh giá khi thỏa mãn đồng thời các điều kiện:
1. **Gate Q14 (Freeze Gate) đã đóng:** Toàn bộ mã nguồn solver của TV4, baseline của TV2, oracle của TV3, bộ tham số $\theta_0 = (\rho_0, \lambda_0)$, ngưỡng $c_{\text{min}}$, và chính sách đồng hạng đã được chốt và ký duyệt (freeze).
2. **Sự đồng thuận của 2 thành viên:** Quá trình mở niêm phong phải có sự chứng kiến và ký xác nhận của **TV1 (Custody Owner)** và ít nhất một thành viên độc lập (**TV2 / TV3 / Trưởng nhóm TV4**).
3. **Nhật ký truy cập bất biến (Custody Access Log):** Mọi thao tác truy cập dữ liệu Holdout phải được ghi nhận vào nhật ký truy cập (thời gian, người thực hiện, mã hash commit thực thi, mục đích chạy).
4. **Không tinh chỉnh hồi tố:** Tuyệt đối không điều chỉnh mã nguồn hay thay đổi tham số sau khi tập Holdout đã được mở.

---

## 5. Kết luận và Kiến nghị

TV1 kính trình Trưởng nhóm (TV4) và các thành viên phản biện (TV2, TV3):
1. **Ghi nhận ranh giới sử dụng của fixtures TV4** theo đúng đánh giá tại Mục 1 (chỉ dùng nội bộ solver DEV, không phải font/dataset đã nghiệm thu).
2. **Xem xét và thông qua bộ đề xuất Q03, Q05, Q13** làm căn cứ kỹ thuật để triển khai các bước tiếp theo của Slice S0/S1. Các tham số giữ trạng thái **PROPOSED / PENDING** chờ thẩm định chung.
3. **Phối hợp chuẩn bị:** TV1 đã hoàn thành bộ ứng viên mẫu DEV (4 ca kiểm chứng), trích xuất bằng chứng số học khớp TV4 tại `docs/evidence/tv1_dev_cases_evidence.json`, và test suite kiểm chuẩn tại `tests/research/test_tv1_candidates.py` (**13/13 test PASS**), toàn bộ test suite nghiên cứu đạt **190/190 test PASS**, sẵn sàng cung cấp dữ liệu đầu vào cho bộ giải của TV4, baseline của TV2 và oracle của TV3.
