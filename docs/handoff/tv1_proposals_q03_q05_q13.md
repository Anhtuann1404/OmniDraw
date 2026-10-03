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

## 2. Đề xuất chuẩn hóa Q03 — Quality Bounds & Reference Geometry trên DEV

Để đảm bảo tính nhất quán giữa bộ giải DP (TV4), bộ kiểm chứng độc lập (TV3) và các baseline phân tầng (TV2), TV1 đề xuất bộ tiêu chuẩn chất lượng hình học chung trên tập DEV:

### 2.1. Ngưỡng khoảng hở tối thiểu ($c_{\text{min}}$)
* **Quy định cứng:** $c_{\text{min}} = 0.20\,\text{mm}$ cho mọi cặp nét bắt buộc phải tách rời.
* **Nguyên tắc:** Dưới $0.20\,\text{mm}$ là không khả thi (INFEASIBLE), không được dùng hàm phạt mềm (soft penalty) hay dung sai số học để làm giảm ngưỡng này.
* **Ngoại lệ tiếp xúc (Contact):** Chỉ được miễn trừ trong phạm vi đĩa tiếp xúc hữu hạn có bán kính khai báo rõ ràng ($r \le 0.25\,\text{mm}$) tại đúng **điểm đầu mút (endpoint)** của cả hai nét.

### 2.2. Giới hạn dịch dấu chuẩn hóa theo x-height
Vị trí của dấu phải được chuẩn hóa theo chiều cao thân chữ ($x\text{-height}$):
$$\Delta y_{\text{mark}} \in [0.15, 0.45] \times x\text{-height}$$
* Đảm bảo dấu không bị dính sát vào thân chữ gây lem mực ($< 0.15 \times x\text{-height}$) và không bay quá xa làm mất tính liên kết thị giác ($> 0.45 \times x\text{-height}$).

### 2.3. Dung sai góc nghiêng và tỷ lệ khung bao
* **Góc nghiêng trục nét ($\theta$):** Độ lệch so với góc chuẩn của font/phong cách phải thỏa mãn $|\Delta \theta| \le 5^\circ$ (cho chữ in/nét đơn tiêu chuẩn) và $|\Delta \theta| \le 15^\circ$ (cho chữ viết nghiêng).
* **Tỷ lệ khung bao ($\text{Aspect Ratio} - \text{AR}$):** Độ biến thiên tỷ lệ khung bao của từng glyph so với hình học tham chiếu: $|\Delta \text{AR}| \le 10\%$.
* **Topology:** Không chấp nhận hiện tượng tự cắt chéo (self-crossing) hoặc quay đầu ngược hướng (backtracking) trên cùng một nét vẽ đơn.

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
1. **Ghi nhận ranh giới sử dụng của fixtures TV4** theo đúng đánh giá tại Mục 1.
2. **Xem xét và thông qua bộ đề xuất Q03, Q05, Q13** làm căn cứ kỹ thuật để triển khai các bước tiếp theo của Slice S0/S1.
3. **Phối hợp chuẩn bị:** TV1 đã hoàn thành bộ ứng viên mẫu và test suite kiểm chuẩn tại `dataset/research/dev/candidate_builder.py` và `tests/research/test_tv1_candidates.py` (**8/8 test PASS**), sẵn sàng cung cấp dữ liệu đầu vào cho bộ giải của TV4 và oracle của TV3.
