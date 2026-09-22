# Chương 3 — Phương pháp nghiên cứu và thiết kế thuật toán

**Bản thảo:** 0.1

**Ngày đối chiếu code và tài liệu:** 22/09/2026

**Trạng thái:** `DRAFT — PR2 IMPLEMENTED; PR3 IMPLEMENTATION AND TEAM REVIEW PENDING`

**Phạm vi:** Handwriting Mode / CA-VHC; không trình bày kết quả thực nghiệm

**Nguồn thiết kế chính:** [`05_ca_vhc_research_spec.md`](05_ca_vhc_research_spec.md), [`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md)
**Nguồn đối chiếu hiện trạng:** [`06_audit_trellis_dag_report.md`](06_audit_trellis_dag_report.md), [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md), mã nguồn `backend/handwriting/`

> [!IMPORTANT]
> Chương này phân biệt bắt buộc giữa thành phần **đã triển khai và kiểm thử**, thiết kế **đã khóa nhưng chưa triển khai**, và hạng mục **còn phụ thuộc**. Công thức CA-VHC mô tả phương pháp đề xuất; chúng không phải bằng chứng rằng PR3 đã tồn tại trong engine hoặc đã tốt hơn baseline.

## 3.1. Thiết kế nghiên cứu và kiến trúc tổng thể

### 3.1.1. Thiết kế nghiên cứu

OmniDraw sử dụng thiết kế thực nghiệm định lượng có đối chứng. Đối tượng đánh giá là quỹ đạo vector nét đơn được sinh từ cùng văn bản dưới bốn phương pháp B1, B2, B3 và Proposed CA-VHC. Đơn vị phân tích được xác định bởi bộ:

$$
u=(\text{method},\ \text{corpus item},\ \text{font},\ \text{seed},\ \text{run index}).
$$

Mỗi phép so sánh phải giữ cố định văn bản, cấu hình font, Render Profile, cỡ chữ, giãn dòng, khổ giấy, seed và commit phần mềm. Thiết kế này nhằm cô lập ảnh hưởng của phương pháp lựa chọn trạng thái khỏi biến thiên do dữ liệu đầu vào hoặc môi trường chạy. Tập DEV được dùng để phát triển, sửa lỗi và lựa chọn tham số. Holdout chỉ được mở cho đánh giá chính thức sau khi corpus được TV1 freeze; không được dùng để điều chỉnh heuristic hoặc trọng số.

Đánh giá được chia thành ba tầng bằng chứng. Tầng phần mềm kiểm tra tính đúng của SVG, bounds, tính tất định và metric hình học. Tầng thực nghiệm thuật toán so sánh B1/B2/B3/Proposed trên cùng ma trận cấu hình. Tầng vật lý đo quỹ đạo trên máy vẽ sau khi TV3 hoàn tất hiệu chuẩn. Ba tầng không thay thế cho nhau: thời gian tối ưu nội bộ không phải thời gian vẽ thực tế, và clearance hình học trên simulator chưa phải ngưỡng an toàn cơ khí.

### 3.1.2. Kiến trúc xử lý của OmniDraw

OmniDraw có hai đường xử lý tách biệt: Art Mode dành cho ảnh/sketch và Handwriting Mode dành cho văn bản. Nghiên cứu CA-VHC chỉ thuộc Handwriting Mode. Luồng xử lý chính của đường này gồm:

```text
Văn bản + cấu hình
        │
        ▼
API Gateway và strict validation
        │
        ▼
Chuẩn hóa Unicode + phân nhóm grapheme NFD
        │
        ▼
Resolve Font Pack / Render Profile / letter type
        │
        ▼
Sinh hình học glyph và các biến thể theo ngữ cảnh
        │
        ▼
Trellis DAG ở cấp từ + Viterbi DP
        │
        ▼
Ghép dấu và các nét phụ
        │
        ▼
Bio-variation có seed + bố trí dòng/trang
        │
        ▼
SVG smoothing, bounds và metric
        │
        ▼
Simulator / hardware adapter
```

Gateway kiểm tra kiểu đầu vào, style, font, `letter_type`, seed và khổ giấy trước khi gọi engine. Handwriting engine chịu trách nhiệm hình học glyph, dấu, biến thể, nối nét và bố trí văn bản. `path_optimizer` chuyển polyline thành SVG, áp dụng smoothing và trả thông tin bounds cùng metric. Hardware adapter là tầng downstream; engine không được suy diễn khả năng thi công vật lý chỉ từ một SVG hợp lệ.

### 3.1.3. Trạng thái triển khai tại thời điểm lập bản thảo

| Thành phần | Trạng thái | Bằng chứng hoặc phụ thuộc |
| :--- | :--- | :--- |
| Font Pack, Render Profile, Unicode NFD, `GlyphVariant` và Trellis hiện hành | `IMPLEMENTED_AND_TESTED` | `backend/handwriting/engine.py`, `backend/handwriting/font_packs/` |
| Structured render trace, metric evaluator, runner và CSV schema | `IMPLEMENTED_AND_TESTED` | PR1, commit `daca566`; các test PR1 hiện hành |
| Snapshot ASCII 48 cấu hình, seed determinism và DEV-only guard | `IMPLEMENTED_AND_TESTED` | [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md) |
| `DiacriticCandidate`, `CompositionState` và hàm mục tiêu hai cấp | `DESIGN_LOCKED` | Bước B đã được TV2 cross-review và PASS |
| Baseline adapters B1/B2/B3 | `IMPLEMENTED_AND_TESTED` | TV2 hoàn tất Entry Gate E3; adapter và runner method tags có test bảo vệ |
| Interface chuyển tiếp dùng chung | `PENDING_PR2_E4` | Chờ TV2+TV4 ký duyệt `CompositionState`, `world_bbox`, `DiacriticConfig` |
| Diacritic-Aware Trellis production | `PENDING_PR3` | Chưa có trong engine hiện hành |
| Delayed-stroke scheduler | `PENDING_PR4` | Chỉ có thiết kế phân tầng WHERE/WHEN |
| Formal benchmark và ablation | `PENDING_PR5` | Chờ PR2–PR4 và corpus freeze |
| Clearance và thời gian vẽ trên máy thật | `PENDING_TV3_CALIBRATION` | Chưa có số đo vật lý |

## 3.2. Biểu diễn chữ viết tay nét đơn

### 3.2.1. Font Pack và Render Profile

OmniDraw tách dữ liệu hình học khỏi tham số kết xuất. **Font Pack** chứa các polyline glyph, width, center, default metrics, contextual glyph và metadata liên quan. **Render Profile** chứa các tham số như độ nghiêng, tỷ lệ, độ đậm, ligature hoặc flourish. Nhờ sự phân tách này, hai profile có thể dùng chung hình học mà không bị mô tả sai thành hai bộ font độc lập.

Hai cấu hình font được dùng trong protocol CA-VHC là `oly` và `omni_casual`. `oly` ánh xạ tới Font Pack legacy; `omni_casual` ánh xạ tới Font Pack Omni Casual v1. Cả hai đều cung cấp centerline polyline thay vì outline kép của TTF/OTF. Việc chuyển đổi TTF/OTF bất kỳ sang centerline không thuộc P0 và chưa được triển khai.

Mỗi nét được biểu diễn bằng một mảng điểm hai chiều:

$$
S=(p_1,p_2,\ldots,p_m),\qquad p_k=(x_k,y_k)\in\mathbb{R}^2.
$$

Một glyph có thể gồm nhiều nét. Width và center được lấy từ Font Pack để xác định advance, kerning và mỏ neo hình học. Các nét phụ của `i`, `j`, `t` và `f` được tách khỏi nét chính để tránh đưa chấm hoặc gạch ngang vào phép nối thân chữ.

### 3.2.2. Chuẩn hóa Unicode và nhóm grapheme

Đầu vào được chuẩn hóa theo Unicode NFD [4]. Hàm `group_nfd_graphemes()` nhóm một base character với các combining marks đứng sau nó. Ví dụ, `ế` được biểu diễn thành `e + U+0302 + U+0301`. Cách biểu diễn này cho phép engine giữ riêng thân chữ, dấu cấu trúc và dấu thanh.

Pipeline hiện hành đã hỗ trợ tập combining marks dùng cho tiếng Việt và từ chối ký tự không có glyph thay vì âm thầm thay bằng dấu hỏi. Một bước chuẩn hóa dự án cũng xử lý vị trí dấu thanh ở vần cuối `uy` theo các điều kiện được mã hóa rõ ràng; đây là quy tắc chính tả hình học, không phải mô hình hiểu ngữ nghĩa hoặc ngữ âm.

### 3.2.3. Biến thể glyph và thông tin nối nét

`GlyphVariant` là node hình học của Trellis hiện hành. Mỗi biến thể chứa:

- danh sách nét của thân chữ;
- điểm vào và điểm ra;
- vector tiếp tuyến vào và ra;
- cờ `can_in`, `can_out`;
- chi phí dễ đọc `cost_legibility`;
- nhãn biến thể như `std`, `mid_in`, `high_out`, `closed` hoặc `isolated`.

Hàm `get_glyph_variants()` sinh từ một đến ba biến thể tùy ký tự. `std` giữ hình học chuẩn; `mid_in` hoặc `high_out` điều chỉnh điểm đón/thoát; `closed` ngăn nối tại một số thân chữ; `isolated` chủ động buộc nhấc bút. Trong kiến trúc đề xuất, `GlyphVariant` tiếp tục chỉ đại diện cho thân chữ. Dấu không được nhồi vào đối tượng này, nhằm tránh tạo một cấu trúc chịu đồng thời quá nhiều trách nhiệm.

### 3.2.4. Hệ tọa độ cục bộ và tọa độ trang giấy

Hình học glyph và dấu được định nghĩa trong hệ tọa độ cục bộ của ký tự. Khi tính quan hệ giữa các ký tự hoặc render, điểm cục bộ được biến đổi sang tọa độ trang giấy:

$$
p_{world}=p_{local}\odot s+o,
$$

trong đó $s=(s_x,s_y)$ là vector scale và $o=(x_0,y_0)$ là offset của ký tự trên dòng. Mọi kiểm tra bridge giữa hai ký tự phải thực hiện trong cùng hệ tọa độ world. Quy ước này ngăn lỗi so sánh một vùng dấu local với một bridge đã được dịch chuyển sang vị trí trang giấy.

## 3.3. Baseline và Trellis hiện hành

### 3.3.1. Ba baseline đối chứng

Ba baseline được định nghĩa trước khi triển khai Proposed nhằm tránh thay đổi đối chứng sau khi thấy kết quả:

| Phương pháp | Quy tắc | Vai trò | Trạng thái adapter |
| :--- | :--- | :--- | :--- |
| B1 — Static Glyph Renderer | Dùng canonical glyph và luôn nhấc bút giữa ký tự | Mốc cơ sở về path và số lần nhấc bút | `IMPLEMENTED_AND_TESTED` (`b1_static`) |
| B2 — Greedy Contextual Heuristic | Chọn quyết định tốt nhất tại từng vị trí theo trạng thái đã chọn trước đó | Đối chứng giữa tham lam và tối ưu chuỗi | `IMPLEMENTED_AND_TESTED` (`b2_greedy`) |
| B3 — Current Trellis DAG | Viterbi trên `GlyphVariant`, dấu được gắn post-DAG | Đối chứng trực tiếp để đo tác động của state nhận thức dấu | `IMPLEMENTED_AND_TESTED` (`b3_current_trellis`) |

`experiment_runner.py` hiện nhận `--method` để chạy riêng B1, B2 hoặc B3 trên cùng input/output contract. Các adapter phục vụ technical dry-run; Chương 4 chỉ được điền kết quả chính thức sau PR3–PR5 và các validation gate dữ liệu/phần cứng.

### 3.3.2. Trellis dựa trên `GlyphVariant`

Với từ gồm $N$ ký tự, layer $i$ chứa tập biến thể $V_i$. Mỗi cạnh nối một biến thể ở $V_{i-1}$ với một biến thể ở $V_i$. `eval_transition()` so sánh hai quyết định: tạo bridge hoặc nhấc bút. Thành phần chi phí hiện hành gồm khoảng cách pen-up, số lần nhấc bút, curvature, collision giữa bridge với thân chữ và legibility.

Nếu hai biến thể cho phép nối, khoảng cách và hướng tương đối hợp lệ, engine dựng một candidate bridge Bézier. `bridge_collision_cost()` kiểm tra giao cắt và khoảng cách bằng sampled polyline/segment-distance. Đây là heuristic hình học, không phải bộ kiểm tra va chạm tuyệt đối kiểu CAD. Nếu chi phí nối thấp hơn chi phí nhấc bút, cạnh được đánh dấu nối; ngược lại engine giữ quyết định lift.

Quy hoạch động lưu chi phí tốt nhất và backpointer cho mỗi node. Sau khi xử lý layer cuối, thuật toán truy ngược để thu chuỗi biến thể và quyết định nối. Cấu trúc này tuân theo nguyên lý Viterbi trên trellis [6].

### 3.3.3. Giới hạn của pipeline hiện hành

Audit mã nguồn xác nhận dấu chỉ được sinh sau khi chuỗi `GlyphVariant` đã được chọn. `bridge_collision_cost()` nhìn thấy nét chính của hai ký tự kề nhau nhưng không nhận vùng dấu. Vì vậy, B3 có thể chọn một bridge tốt theo thân chữ rồi để bridge đi qua dấu được gắn sau đó. `cost_legibility` cũng là heuristic cố định, chưa phải metric khả đọc được hiệu chuẩn bằng người dùng.

Giới hạn này tạo ra nhu cầu mở rộng node của trellis. Thay vì sửa bridge hoặc dịch dấu hoàn toàn ở hậu xử lý, CA-VHC đưa cấu hình dấu vào trạng thái trước khi Viterbi lựa chọn đường đi.

## 3.4. Phương pháp CA-VHC đề xuất

### 3.4.1. Kiến trúc lai

CA-VHC giữ `GlyphVariant` làm biểu diễn thân chữ và bổ sung hai thực thể:

1. `DiacriticCandidate`: một phương án hình học cụ thể cho cụm dấu;
2. `CompositionState`: tổ hợp giữa biến thể thân chữ và ứng viên dấu, trở thành node chính thức của trellis.

Với ký tự không dấu, `diacritic_candidate=None`; bài toán dự kiến suy biến về không gian biến thể thân chữ hiện hành. Với ký tự có dấu, mỗi biến thể thân chữ được tổ hợp với các phương án `canonical`, `safe_left` và `safe_right` còn hợp lệ.

### 3.4.2. `DiacriticCandidate`

Một `DiacriticCandidate` dự kiến lưu combining marks, nhãn placement, các nét dấu local, anchor, độ dịch $(\Delta x,\Delta y)$, bounding box, clearance zone và placement penalty. Candidate biểu diễn toàn bộ cụm dấu nhưng vẫn giữ các nét cấu trúc và dấu thanh tách biệt, nhờ đó có thể phát hiện va chạm giữa các thành phần.

P0 không số hóa lại hệ anchor phức tạp cho toàn bộ Font Pack. Hình học từ `generate_accents()` hiện hành được dùng làm canonical geometry provider; `safe_left` và `safe_right` được tạo bằng phép tịnh tiến local. Các offset và ngưỡng phải đọc từ `DiacriticConfig`, không rải literal trong nhiều hàm. Giá trị ban đầu là engineering defaults phục vụ kiểm thử, chưa phải tham số tối ưu đã được chứng minh.

### 3.4.3. `CompositionState`

Tại vị trí $i$, một state được định nghĩa ý niệm bởi:

$$
s_{i,j}=(v_{i,a},d_{i,b},c_i,m_{i,j}),
$$

trong đó $v_{i,a}$ là `GlyphVariant`, $d_{i,b}$ là `DiacriticCandidate` hoặc `None`, $c_i$ chứa base character và chuỗi mark NFD, còn $m_{i,j}$ là metadata phục vụ trace. State giữ chi phí va chạm nội tại và legibility riêng, nhưng không chứa chi phí quan hệ với ký tự trước.

Thiết kế dùng dataclass bất biến để hạn chế thay đổi state sau khi đã đưa vào bảng DP. Renderer chỉ được kết xuất đúng state mà Viterbi chọn; không được tự chạy lại anchor heuristic vì hành vi đó sẽ làm mất quan hệ giữa nghiệm tối ưu và SVG đầu ra.

### 3.4.4. Sinh ứng viên và hard pruning

Trong P0, mỗi ký tự có tối đa ba biến thể thân chữ và ba ứng viên dấu:

$$
K_{raw}\le K_{base}K_{diacritic}\le 3\times3=9.
$$

Pipeline chỉ loại các state bất hợp lệ cứng:

- hình học rỗng, malformed hoặc chứa NaN/Inf;
- vi phạm biên dòng hoặc biên trang;
- tổ hợp combining marks không hợp lệ;
- va chạm nội tại vượt ngưỡng cấu hình.

Không áp dụng top-$k$ heuristic hoặc beam search chỉ để giảm số state trong P0. Candidate có placement penalty cao nhưng vẫn hợp lệ phải được giữ để Viterbi cân nhắc trade-off toàn cục. Nếu toàn bộ candidate vi phạm hard constraints, engine phải trả lỗi có cấu trúc như `NO_VALID_STATE`; không được hồi sinh một candidate đã bị loại.

## 3.5. Hàm mục tiêu và Viterbi DP

### 3.5.1. Chi phí trạng thái

Chi phí nội tại của state được định nghĩa:

$$
C_{state}(s)=w_{4a}C_{internal\_collision}(s)
+w_5C_{legibility}(s)
+w_6C_{placement}(s).
$$

$C_{internal\_collision}$ đo xung đột bên trong cùng ký tự, gồm dấu với thân chữ hoặc giữa các tầng dấu. $C_{legibility}$ chỉ phản ánh biến thể thân chữ. $C_{placement}$ phạt khoảng dịch khỏi vị trí canonical, có thể chuẩn hóa bằng:

$$
C_{placement}(s)=
\frac{\sqrt{\Delta x^2+\Delta y^2}}
{\text{max\_placement\_shift\_mm}}.
$$

Geometry metric và cost metric phải được phân biệt. `minimum_diacritic_clearance_mm` có đơn vị millimet, còn các $C$ trong hàm mục tiêu là đại lượng vô hướng sau ánh xạ. Không được cộng trực tiếp một khoảng cách vật lý với một penalty không thứ nguyên nếu chưa chuẩn hóa.

### 3.5.2. Chi phí chuyển tiếp

Chi phí giữa hai state kề nhau được định nghĩa:

$$
J_{transition}(s',s)=
w_1D_{penup}+w_2N_{lift}+w_3C_{curvature}
+w_4C_{bridge\_collision}.
$$

$D_{penup}$ là quãng di chuyển không vẽ; $N_{lift}$ biểu diễn quyết định nhấc bút; $C_{curvature}$ phạt thay đổi hướng tại vùng nối; $C_{bridge\_collision}$ xét candidate bridge với thân chữ và clearance zone của dấu trong tọa độ world. Một bridge giao vùng dấu ở mức không thể chấp nhận bị hard reject; bridge còn hợp lệ có thể nhận soft penalty theo clearance.

Việc tách $C_{state}$ và $J_{transition}$ tránh double-count. Legibility và placement của state không được cộng lại trong transition; ngược lại, khoảng cách và curvature giữa hai ký tự không thuộc state cost.

### 3.5.3. Phương trình truy hồi

Với $S_i$ là tập state hợp lệ tại layer $i$, base case là:

$$
DP[0,j]=C_{state}(s_{0,j}).
$$

Tại các layer sau:

$$
DP[i,j]=C_{state}(s_{i,j})+
\min_{p}\left(
DP[i-1,p]+J_{transition}(s_{i-1,p},s_{i,j})
\right).
$$

Backpointer lưu chỉ số $p$ tạo ra giá trị nhỏ nhất. Sau khi tìm $j^*=\arg\min_jDP[N-1,j]$, thuật toán truy ngược từ $j^*$ để thu chuỗi state và quyết định bridge/lift. Kiểm thử synthetic trellis với nghiệm biết trước là bắt buộc trước khi dùng kết quả trên corpus.

### 3.5.4. Điều kiện khả thi và failure path

Một transition chỉ được xét nối khi hai biến thể cho phép nối, hướng đi hợp lệ, khoảng cách không vượt giới hạn và candidate bridge không vi phạm hard collision. Nếu không, cạnh lift vẫn có thể tồn tại với chi phí tương ứng. Nếu một layer không có state hợp lệ, cả từ phải thất bại tường minh thay vì âm thầm quay về B3 hoặc glyph mặc định. Quy tắc này giữ cho metric và log phản ánh đúng phương pháp thực sự đã chạy.

## 3.6. Bố trí dấu và delayed-stroke

CA-VHC phân tách hai câu hỏi:

- **WHERE:** dấu nằm ở vị trí nào; PR3 xử lý bằng `DiacriticCandidate` và `CompositionState`.
- **WHEN:** dấu được vẽ vào thời điểm nào; PR4 xử lý bằng delayed-stroke scheduler.

Sự phân tách này phù hợp với quan sát rằng delayed strokes là đặc điểm quan trọng của chữ viết tay trực tuyến tiếng Việt [3]. Một dấu có vị trí hình học tốt không nhất thiết phải được vẽ ngay sau thân chữ; ngược lại, thay đổi thứ tự vẽ không được phép thay đổi chủ sở hữu hoặc vị trí của dấu.

Thiết kế P0 dự kiến vẽ thân từ trước, thu thập các secondary/diacritic strokes còn lại, sau đó sắp thứ tự bằng deterministic nearest neighbor. Khi hai lựa chọn có cùng khoảng cách, original character index được dùng làm tie-break. Đây là chiến lược xác định được và dễ kiểm thử, chưa phải nghiệm tối ưu toàn cục cho bài toán sắp thứ tự nét.

Hiện tại engine vẫn giữ thứ tự đọc tự nhiên và chưa có delayed-stroke scheduler hoàn chỉnh. Vì vậy, nội dung mục này mang trạng thái `DESIGN_LOCKED/PENDING_PR4`, không được mô tả như chức năng production.

## 3.7. Tính tái lập, metric và kiểm thử

### 3.7.1. Seed và structured trace

Bio-variation có thể tạo jitter, slant và baseline drift. Mọi lần chạy nghiên cứu phải truyền seed tường minh; cùng input và seed phải tạo cùng geometry fingerprint. Timing không được đưa vào fingerprint vì thời gian thay đổi theo môi trường.

`text_to_strokes_structured()` trả `StructuredRenderResult` gồm strokes, trace và `optimize_time_ms`. Mỗi `TraceStroke` mang loại nét (`base_stroke`, `bridge_stroke`, `secondary_stroke`, `diacritic_stroke`), ký tự, chỉ số từ và metadata. Trace cho phép metric evaluator phân biệt nét tiếp xúc giấy với quan hệ bridge–diacritic thay vì suy luận loại nét từ SVG đã làm mượt.

### 3.7.2. Bộ metric

Hạ tầng PR1 hiện tính được:

| Metric | Ý nghĩa | Phạm vi sử dụng hiện tại |
| :--- | :--- | :--- |
| `total_path_length_mm` | Tổng chiều dài các nét được vẽ | Technical dry-run |
| `pen_lift_distance_mm` | Tổng quãng di chuyển giữa các nét | Chờ baseline comparability |
| `pen_lift_count` | Số lần chuyển giữa các nét liên tục | Chờ baseline comparability |
| `collision_count` | Số cặp bridge–diacritic giao nhau | Metric validation; chờ PR3 |
| `minimum_diacritic_clearance_mm` | Khoảng hở nhỏ nhất giữa bridge và dấu | Chờ PR3 và calibration cho claim vật lý |
| `curvature_cost` | Chi phí thay đổi hướng tại bridge | Diagnostic; chờ PR2 định nghĩa cuối |
| `optimize_time_ms` | Thời gian tối ưu nội bộ | Diagnostic; chưa phải benchmark |

`actual_draw_time_sec`, `c1_violation_count` và một số chẩn đoán cơ khí chưa tồn tại đầy đủ. Chúng không được suy ra từ các metric hiện hành.

### 3.7.3. Corpus, cấu hình và chống leakage

PR1 định nghĩa 20 từ DEV, 20 từ Holdout, hai cấu hình font `oly`/`omni_casual` và bốn seed `42`, `100`, `2026`, `999999`. Runner mặc định chỉ dùng DEV và yêu cầu cờ xác nhận riêng nếu người dùng cố mở Holdout. Pre-PR3 acceptance sử dụng 10 từ lấy hoàn toàn từ DEV và một fixture ASCII độc lập gồm 48 cấu hình.

Đối với formal benchmark, mỗi cấu hình dự kiến chạy 10 lượt warm-up rồi 50 lần lặp. Báo cáo hiệu năng phải dùng median và p95, đồng thời ghi CPU, hệ điều hành, phiên bản Python, NumPy/BLAS backend, power mode và commit hash. Không gộp số liệu giữa simulator và máy thật hoặc giữa các môi trường không tương đương.

### 3.7.4. Cổng nghiệm thu PR3

PR3 chỉ được bắt đầu sau khi Entry Gate E1–E5 hoàn tất. Hiện E1, E2, E3 và E5 đã đạt; E4 về shared transition interface còn chờ TV2+TV4 ký duyệt. Exit Gate yêu cầu:

- bảo toàn fingerprint 48/48 cấu hình ASCII;
- giữ 34/34 strict-validation tests;
- khống chế $K_{valid}\le9$;
- bảo toàn đúng base character và ordered combining marks trên 10 từ DEV;
- đạt `collision_count=0` và clearance kỹ thuật tối thiểu $0.20$ mm trên trường hợp áp dụng;
- xác nhận Viterbi chọn đúng nghiệm synthetic;
- không crash, không NaN và không đọc Holdout.

Ngưỡng $0.50$ mm là mục tiêu nghiên cứu provisional. Nó chỉ được nâng thành tuyên bố vật lý sau calibration; trường hợp không có bridge hoặc dấu có clearance bằng vô cùng phải được ghi `NOT_APPLICABLE`, không được tính như một ca đạt chuẩn.

## 3.8. Độ phức tạp và giới hạn phương pháp

Với $N$ vị trí và tối đa $K$ state hợp lệ mỗi layer, Viterbi đầy đủ xét tối đa $K^2$ transition giữa hai layer. Độ phức tạp thời gian là:

$$
T(N,K)=O(NK^2),
$$

và bộ nhớ là $O(NK)$ khi lưu bảng chi phí cùng backpointer. Với $K_{raw}\le9$, đây là cận thiết kế của không gian trạng thái, không phải bằng chứng về latency. Collision geometry, transform và candidate generation vẫn phải được profiling theo protocol PR5.

Phương pháp có các giới hạn sau:

1. State space chỉ bao phủ các candidate do nhóm định nghĩa; Viterbi không thể chọn một hình học không có trong tập ứng viên.
2. `bridge_collision_cost()` và metric hiện dùng polyline/segment geometry; chúng không mô phỏng đầy đủ độ dày mực, độ nảy ngòi bút hoặc sai số cơ khí.
3. Legibility và các trọng số ban đầu là engineering assumptions cần ablation và, nếu có điều kiện, đánh giá người dùng.
4. CA-VHC xử lý Unicode và quy tắc hình học; hệ thống không tuyên bố hiểu nghĩa hoặc phát âm tiếng Việt.
5. Writer Profile, few-shot personalization, TTF/OTF centerline conversion và deep generative handwriting nằm ngoài RQ1–RQ3.
6. Hiện chưa có bằng chứng để tuyên bố real-time, liên tục $C^1$ toàn cục hoặc an toàn vật lý.
7. Hai Font Pack và corpus dự kiến giới hạn khả năng khái quát hóa; mọi kết luận sau này phải gắn với đúng phạm vi đánh giá.

## 3.9. Kết luận chương

Chương này mô tả CA-VHC như một mở rộng có kiểm soát của Trellis hiện hành. Thay đổi trung tâm là chuyển node từ `GlyphVariant` sang `CompositionState`, nhờ đó biến thể thân chữ và cấu hình dấu có thể được đánh giá trong cùng một chuỗi Viterbi. Hàm mục tiêu tách chi phí nội tại khỏi chi phí chuyển tiếp, hard pruning loại state không khả thi và structured trace cung cấp dữ liệu cho metric.

Tại thời điểm cập nhật, hạ tầng metric, runner, seed, regression guard và baseline adapters B1/B2/B3 đã tồn tại; `CompositionState` và delayed-stroke scheduler vẫn chưa tồn tại trong production. Chương 4 chỉ được điền kết quả sau PR3–PR5 cùng các gate dữ liệu/phần cứng liên quan.

## Tài liệu tham khảo

> Đánh số được giữ thống nhất với Chương 1–2 và sẽ được hợp nhất thành một danh mục chung trong báo cáo hoàn chỉnh.

[3] H. T. Nguyen, C. T. Nguyen, P. T. Bao, and M. Nakagawa, “A database of unconstrained Vietnamese online handwriting and recognition experiments by recurrent neural networks,” *Pattern Recognition*, vol. 78, pp. 291–306, 2018, doi: 10.1016/j.patcog.2018.01.013.

[4] Unicode Consortium, “Unicode Standard Annex #15: Unicode Normalization Forms,” rev. 58, 2026. https://www.unicode.org/reports/tr15/

[6] A. J. Viterbi, “Error bounds for convolutional codes and an asymptotically optimum decoding algorithm,” *IEEE Trans. Inf. Theory*, vol. 13, no. 2, pp. 260–269, 1967, doi: 10.1109/TIT.1967.1054010.
