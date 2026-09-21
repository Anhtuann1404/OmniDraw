# BÁO CÁO AUDIT KIẾN TRÚC: TRELLIS DAG / CA-VHC HIỆN TẠI (BƯỚC A)
**Dự án:** OmniDraw — Single-Stroke Vector Centerline Engine  
**Chế độ audit:** READ-ONLY ARCHITECTURE AUDIT (Mã nguồn được bảo toàn nguyên vẹn 100%)  
**Thời điểm thực hiện:** 19/09/2026 (Cập nhật chuẩn hóa DOCS-ONLY CORRECTION)  
**File báo cáo:** `docs/06_audit_trellis_dag_report.md`  
**Trạng thái kiểm thử:** 34/34 API tests PASS | Inline self-check PASS  

---

## A. Executive Summary

- **Trellis DAG hiện tại làm gì?**  
  Trellis DAG trong engine (`backend/handwriting/engine.py:optimize_word_dag()`) hiện tại hoạt động như một bộ tối ưu chuyển động (motion/trajectory optimizer) cấp từ (word-level) dựa trên thuật toán Quy hoạch động Viterbi. Mục tiêu duy nhất của nó là chọn ra chuỗi biến thể kết nối nét chính (primary strokes: `std`, `mid_in`, `high_out`, `closed`, `isolated`) và quyết định có nối nét liền mạch bằng cầu nối Bézier (`build_ligature_bridge()`) hay nhấc bút giữa các ký tự liên tiếp để tối thiểu hóa chi phí chuyển động $J$. `[CONFIRMED BY CODE: engine.py:L707-L791]`
- **State hiện tại là gì?**  
  Một state/node trong Trellis DAG là một đối tượng `GlyphVariant` (`engine.py:L329-L343`) biểu diễn **riêng biệt thân chữ cái gốc (base character)**. State chỉ chứa thông tin hình học tọa độ vào/ra (`entry_pt`, `exit_pt`), vector tiếp tuyến (`v_entry`, `v_exit`), cờ cho phép nối nét (`can_in`, `can_out`), chi phí ưu tiên (`cost_legibility`) và nhãn biến thể (`tag`). State **hoàn toàn không chứa** thông tin dấu thanh, dấu mũ, dấu phụ hay trạng thái nét trễ. `[CONFIRMED BY CODE: engine.py:L329-L343]`
- **Dấu tiếng Việt hiện được xử lý ở đâu?**  
  Dấu tiếng Việt được tách ra từ bước tiền xử lý Unicode NFD (`group_nfd_graphemes()`), nhưng sau đó bị **bỏ qua hoàn toàn trong suốt quá trình chạy Trellis DAG**. Chỉ sau khi Viterbi DAG kết thúc và đã chọn xong chuỗi glyph gốc, hàm `generate_accents()` mới được gọi ở pha hậu kỳ (`text_to_strokes():L1385-L1395`) để sinh tọa độ nét dấu theo quy tắc hình học cứng (hard-coded procedural anchors) dựa trên tâm `cx` và đẩy vào danh sách nét phụ cuối từ (`word_secondary_strokes`). `[CONFIRMED BY CODE: engine.py:L1320-L1396]`
- **Khoảng cách (Gap) lớn nhất là gì?**  
  **Sự tách rời hoàn toàn giữa không gian trạng thái Trellis DAG và hệ thống dấu tiếng Việt (Post-DAG Diacritic Attachment)**:
  1. DAG không biết có dấu phía trên hay dưới ký tự, dẫn đến không thể tối ưu hóa né tránh va chạm giữa nét nối (ligature bridge) với dấu thanh của chữ đứng trước/sau ở runtime.
  2. Viterbi không có không gian trạng thái cho các biến thể đặt dấu (allographs/diacritic placements) hoặc thứ tự nét trễ (delayed-stroke ordering).
  3. Xung đột giữa Tài liệu kiến trúc (`docs/01_tech-stack.md`, `docs/02_roadmap.md` ghi nhận Proposed CA-VHC có ràng buộc dấu và delayed-stroke) và Mã nguồn thực tế (hiện chỉ là Static Procedural Accent Placement hậu kỳ). `[CONFIRMED BY CODE vs DOCS CONFLICT]`

---

## B. Current Call Graph

### 1. Sơ đồ luồng thực thi (End-to-End Call Chain)

```text
POST /api/ai/generate (input_type="handwriting" | "letter")
   │
   ▼
backend/main.py:generate_ai_image() [L360-L540]
   │  ├── Validation: input_type, prompt/text, style, target_paper_size_mm, skew_angle, font, seed, letter_type
   │  ├── backend/handwriting/engine.py:resolve_letter_type() [L901]
   │  └── _clear_cached_svg_for_request() [L496]
   │
   ▼
backend/handwriting/engine.py:generate_handwriting_svg() [L1432-L1470]
   │  └── Setup margin, layout bounds, gọi text_to_strokes()
   │
   ▼
backend/handwriting/engine.py:text_to_strokes() [L1179-L1430]
   │  ├── engine.py:normalize_vietnamese_final_uy_tone() [L955]  (Chuẩn hóa vần 'uy': luỵ -> lụy)
   │  ├── engine.py:find_unsupported_characters() [L132]
   │  ├── engine.py:analyze_text_contexts() [L1022] (CA-VHC v1: is_word_initial, is_word_final, ...)
   │  │
   │  └── Loop qua từng từ (Word Loop):
   │        ├── engine.py:group_nfd_graphemes() [L922] (Tách 'ế' -> ['e', '\u0302', '\u0301'])
   │        ├── Loop qua từng ký tự trong từ:
   │        │     └── engine.py:select_contextual_glyph() [L1092] (Chọn formal initial K/T/C hoặc word-final n/m)
   │        │     └── Thu thập char_info_list (chỉ base characters + metadata)
   │        │
   │        ├── engine.py:optimize_word_dag() [L707] ◄── [TRELLIS DAG / VITERBI DP]
   │        │     ├── engine.py:get_glyph_variants() [L359] (Sinh 1-3 biến thể: std, mid_in, high_out, ...)
   │        │     │     └── engine.py:split_glyph_strokes() [L345] (Tách primary/secondary)
   │        │     └── Nested Pairwise Loops:
   │        │           └── engine.py:eval_transition() [L657] (Tính chi phí J)
   │        │                 ├── engine.py:build_ligature_bridge() [L426] (Dựng cầu nối Cubic Bézier)
   │        │                 └── engine.py:bridge_collision_cost() [L546] (Kiểm tra cắt nét chính)
   │        │                       └── engine.py:segments_intersect() [L484]
   │        │
   │        └── Render Word Loop (Áp dụng kết quả DAG & Gắn dấu hậu kỳ):
   │              ├── Lấy chosen GlyphVariant từ dp_sol["variants"]
   │              ├── Nối nét bridge nếu dp_sol["conns"][i-1] == True
   │              ├── Nét phụ thân chữ: thanh đậm, flourish đuôi từ, gạch ngang đ/Đ
   │              ├── engine.py:generate_accents() [L175] ◄── [GẮN DẤU HẬU KỲ / POST-DAG]
   │              └── engine.py:apply_bio_variation() [L1148] (Slant, jitter, baseline drift trên toàn bộ nét)
   │
   ▼
backend/path_optimizer.py:build_svg() & compute_svg_metrics() [L1451-L1460]
   │  └── Chuyển polyline mm sang thẻ SVG <path d="..." fill="none"/>
   │
   ▼
HTTP 200 JSON Response (Handwriting Mode Contract v1.4)
{
  "status": "success",
  "result_image_base64": null,
  "svg_ready": true,
  "svg_metrics": {...}
}
```

### 2. Bảng đặc tả từng bước trong Call Chain

| Bước | File | Function / Class | Input | Output | Vai trò & Nhãn bằng chứng |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `backend/main.py` | `generate_ai_image()` | `GenerateRequest` (Pydantic model) | `dict` (JSON Response) | API Endpoint Gateway tiếp nhận request, xác thực 8 tầng tham số (style, font, seed, paper, letter_type...). `[CONFIRMED BY CODE: main.py:L360-L540]` |
| **2** | `backend/handwriting/engine.py` | `generate_handwriting_svg()` | `text`, `font`, `style`, `target_paper_size_mm`, `seed`, `letter_type` | `(svg_content, metrics, in_bounds)` | Entry point của handwriting engine, cấu hình khổ giấy và điều phối render SVG. `[CONFIRMED BY CODE: engine.py:L1432-L1470]` |
| **3** | `backend/handwriting/engine.py` | `text_to_strokes()` | `text`, `font`, `style`, `paper_size_mm`, `seed`, `letter_type` | `List[np.ndarray(N, 2)]` | Pipeline lõi: layout trên khổ giấy hiện tại, word/line wrapping, xử lý từng từ, gọi Trellis DAG, render strokes (hỗ trợ đơn trang hiện tại; multi-page pagination là mục tiêu tương lai). `[CONFIRMED BY CODE: engine.py:L1179-L1430]` |
| **4** | `backend/handwriting/engine.py` | `normalize_vietnamese_final_uy_tone()` | `text: str` | `str` (NFC) | Chuẩn hóa chính tả vị trí dấu cho vần "uy" ở cuối âm tiết (chuyển dấu từ y sang u: luỵ -> lụy). `[CONFIRMED BY CODE: engine.py:L955-L1017]` |
| **5** | `backend/handwriting/engine.py` | `analyze_text_contexts()` | `text: str` | `List[dict]` | Context Analyzer v1 (CA-VHC): gán nhãn vị trí từ/câu/văn bản (`is_word_initial`, `is_word_final`, `is_sentence_final`). `[CONFIRMED BY CODE: engine.py:L1022-L1090]` |
| **6** | `backend/handwriting/engine.py` | `group_nfd_graphemes()` | `sub_w: str` | `List[List[str]]` | Chuẩn hóa Unicode NFD, bóc tách ký tự gốc và mảng combining diacritics. `[CONFIRMED BY CODE: engine.py:L922-L943]` |
| **7** | `backend/handwriting/engine.py` | `select_contextual_glyph()` | `base_char`, `font_pack`, `font_pack_id`, `letter_type`, `context` | `(raw_s, width, cx, tag)` | Greedy Contextual Override: chọn allograph mở đầu trang trọng (K/T/C) hoặc kết thúc từ (n/m) trước DAG. `[CONFIRMED BY CODE: engine.py:L1092-L1145]` |
| **8** | `backend/handwriting/engine.py` | `optimize_word_dag()` | `char_info_list`, `weights`, `force_lift` | `{"variants": [...], "conns": [...]}` | Quy hoạch động Viterbi DP trên Trellis DAG tìm chuỗi biến thể nét chính và cầu nối ligature tối ưu. `[CONFIRMED BY CODE: engine.py:L707-L791]` |
| **9** | `backend/handwriting/engine.py` | `get_glyph_variants()` | `base_char`, `raw_strokes` | `List[GlyphVariant]` | Sinh 1-3 biến thể hình học kết nối (std, mid_in/high_out/closed, isolated) cho ký tự gốc. `[CONFIRMED BY CODE: engine.py:L359-L424]` |
| **10** | `backend/handwriting/engine.py` | `eval_transition()` | `u`, `w`, `p_exit`, `p_entry`, `weights`, vectors, strokes | `(cost, is_conn: bool)` | Tính chi phí chuyển trạng thái giữa 2 node theo hàm mục tiêu $J$ (so sánh cost nối nét vs nhấc bút). `[CONFIRMED BY CODE: engine.py:L657-L705]` |
| **11** | `backend/handwriting/engine.py` | `build_ligature_bridge()` | `p_exit`, `v_exit`, `p_entry`, `v_entry`, `scale_hint`, `n=6` | `np.ndarray(n, 2)` | Dựng đường cong Cubic Bézier làm cầu nối mượt mà giữa điểm thoát và điểm đón. `[CONFIRMED BY CODE: engine.py:L426-L458]` |
| **12** | `backend/handwriting/engine.py` | `bridge_collision_cost()` | `bridge`, `prev_strokes`, `curr_strokes`, `scale_hint` | `float` | Heuristic kiểm tra giao cắt và khoảng cách clearance giữa cầu nối với nét chính lân cận. `[CONFIRMED BY CODE: engine.py:L546-L655]` |
| **13** | `backend/handwriting/engine.py` | `generate_accents()` | `base_char`, `accents`, `cx`, `dot_below_x_offset` | `List[np.ndarray(M, 2)]` | **Hậu kỳ**: Tạo nét dấu phụ/thanh điệu tiếng Việt dựa trên tọa độ tâm `cx` cố định. `[CONFIRMED BY CODE: engine.py:L175-L303]` |
| **14** | `backend/handwriting/engine.py` | `apply_bio_variation()` | `stroke`, `slant`, `jitter_amp`, `drift_y`, `rng` | `np.ndarray(N, 2)` | Mô phỏng biến thiên cơ sinh học người: nghiêng chữ, rung tay, võng dòng. `[CONFIRMED BY CODE: engine.py:L1148-L1176]` |
| **15** | `backend/path_optimizer.py` | `build_svg()` | `strokes`, `paper_size_mm`, `stroke_width_mm` | `str` (XML SVG) | Xuất vector path SVG centerline (`fill="none"`, `stroke="black"`). `[CONFIRMED BY CODE: path_optimizer.py:L316-L352]` |

---

## C. Current Trellis Model

### 1. Kiến trúc đồ thị và biểu diễn thực tế

- **Tồn tại Graph Object không?**  
  **KHÔNG**. Trong mã nguồn không có bất kỳ class nào tên là `Graph`, `DAG`, `Trellis`, hay `TrellisNode`. Toàn bộ đồ thị được biểu diễn ngầm định (implicitly) thông qua danh sách các lớp biến thể `variants_per_char` và ba cấu trúc bảng từ điển DP của hàm `optimize_word_dag()`:
  - `dp = [{} for _ in range(n)]`: Lưu giá trị chi phí tích lũy nhỏ nhất tại mỗi trạng thái.
  - `bp = [{} for _ in range(n)]`: Bảng backpointer lưu chỉ số node cha tốt nhất ở layer trước.
  - `conn = [{} for _ in range(n)]`: Bảng lưu quyết định chuyển tiếp (True = nối cầu nét ligature, False = nhấc bút pen-lift).  
  `[CONFIRMED BY CODE: engine.py:L734-L736]`

### 2. Cấu trúc Trellis Layer, Node, Edge

- **Trellis Layer ($i$):**  
  Mỗi layer $i \in \{0, \dots, n-1\}$ đại diện cho **vị trí của một ký tự gốc (base character)** trong từ đang xét. Số lượng layer bằng đúng độ dài từ $n$.  
  `[CONFIRMED BY CODE: engine.py:L712-L716]`
- **Node / State ($v_{i, j}$):**  
  Mỗi node trong layer $i$ là một thực thể của class `GlyphVariant` (`engine.py:L329`), đại diện cho biến thể hình học thứ $j$ của ký tự thứ $i$.  
  Số lượng candidate mỗi layer: $K_i \in \{1, 2, 3\}$.
  - Chữ cái thường tiếng Anh/Việt (`a-z`): Thường có 2 đến 3 candidate (vd: `std`, `mid_in`/`high_out`, `isolated`).
  - Ký tự hoa (`A-Z`), chữ số (`0-9`), dấu câu: Chỉ có 1 candidate duy nhất (`std`, `can_in=False, can_out=False`).  
  `[CONFIRMED BY CODE: engine.py:L368-L423]`
- **Edge / Transition ($e = (v_{i-1, p} \to v_{i, j})$):**  
  Cạnh có hướng nối từ biến thể $p$ ở layer $i-1$ sang biến thể $j$ ở layer $i$.  
  Mỗi cạnh có chi phí chuyển tiếp $J(v_{i-1, p}, v_{i, j})$ được tính toán thông qua hàm `eval_transition()`.
- **Start State & Terminal State:**  
  - *Start state*: Toàn bộ các node tại layer $i=0$. Giá trị khởi tạo:  
    $$DP[0, j] = w_5 \cdot v_{0, j}.\text{cost\_legibility}$$  
    `[CONFIRMED BY CODE: engine.py:L738-L739]`
  - *Terminal state*: Node $j^*$ tại layer $n-1$ đạt chi phí tích lũy nhỏ nhất:  
    $$j^* = \arg\min_{j} DP[n-1, j]$$  
    `[CONFIRMED BY CODE: engine.py:L778]`
- **Backtracking:**  
  Truy vết ngược từ $i = n-1$ về $i=1$ qua bảng `bp[i][curr_j]` để thu được chuỗi chỉ số biến thể `chosen_var_indices` và chuỗi cờ nối nét `chosen_conns`.  
  `[CONFIRMED BY CODE: engine.py:L781-L791]`

---

## D. Current Cost Function

### 1. Hàm mục tiêu chuyển động (Transition Objective)

Trong hàm `eval_transition()` (`engine.py:L657-L705`), chi phí giữa node trước $u$ (tại tọa độ $p_{\text{exit}}$) và node sau $w$ (tại tọa độ $p_{\text{entry}}$) được đánh giá thông qua hai kịch bản cạnh tranh: **Nhấc bút (Pen-lift)** và **Nối nét (Ligature Connection)**.

$$J_{\text{lift}} = w_1 \cdot D_{\text{penup}} + w_2 \cdot 1.0 + w_5 \cdot C_{\text{legibility}}(w)$$

Nếu thỏa mãn điều kiện hình học cho phép nối nét:
$$(u.\text{can\_out} = \text{True}) \land (w.\text{can\_in} = \text{True}) \land (dx > -0.2) \land (\text{dist} < 12.0)$$
thì thuật toán tính tiếp chi phí nối nét:

$$J_{\text{conn}} = w_1 \cdot 0.0 + w_2 \cdot 0.0 + w_3 \cdot C_{\text{curvature}} + w_4 \cdot C_{\text{collision}} + w_5 \cdot C_{\text{legibility}}(w)$$

Quy tắc quyết định:
$$\text{Nếu } J_{\text{conn}} < J_{\text{lift}} \implies \text{Chọn nối nét } (\text{cost} = J_{\text{conn}}, \text{is\_conn} = \text{True})$$
$$\text{Ngược lại } \implies \text{Chọn nhấc bút } (\text{cost} = J_{\text{lift}}, \text{is\_conn} = \text{False})$$

Vector trọng số mặc định trong code:
$$\mathbf{w} = (w_1, w_2, w_3, w_4, w_5) = (0.5, 4.0, 2.0, 15.0, 1.0)$$
*(Khi font tắt ligature, $w_2$ được gán về $0.0$ và `force_lift=True`).* `[CONFIRMED BY CODE: engine.py:L1321-L1324]`

### 2. Bảng đối chiếu 5 thành phần chi phí

| Thành phần | Có code thật? | Biến / Hàm trong code | Công thức thực tế trong mã nguồn | Phân tích & Giới hạn |
| :--- | :--- | :--- | :--- | :--- |
| **$D_{\text{penup}}$** | **CONFIRMED BY CODE** | `dist` trong `eval_transition()` [L666, L669] | $\text{dist} = \|p_{\text{entry}} - p_{\text{exit}}\|_2$ (khi nhấc bút); $0.0$ (khi nối nét). | Khoảng cách Euclide giữa điểm thoát của chữ trước và điểm đón của chữ sau trong world coordinates. |
| **$N_{\text{lift}}$** | **CONFIRMED BY CODE** | Hằng số `1.0` [L669] | $1.0$ khi nhấc bút; $0.0$ khi nối nét. | Phạt rời rạc cho hành động nhấc ngòi bút máy vẽ. Trọng số $w_2=4.0$ đủ lớn để ưu tiên nối nét khi hình học thuận lợi. |
| **$C_{\text{curvature}}$** | **CONFIRMED BY CODE** | `c_curvature` [L678-L686] | $(1.0 - \cos \theta_1) + (1.0 - \cos \theta_2)$ với $\cos \theta_1 = \mathbf{v}_{\text{ex}} \cdot \mathbf{u}_d$, $\cos \theta_2 = \mathbf{u}_d \cdot \mathbf{v}_{\text{en}}$, $\mathbf{u}_d = \frac{p_{\text{entry}} - p_{\text{exit}}}{\|p_{\text{entry}} - p_{\text{exit}}\|}$ | Đo góc lệch tiếp tuyến giữa hướng thoát, hướng dây cung nối, và hướng đón nét. Phạt gập góc nhọn. |
| **$C_{\text{collision}}$** | **CONFIRMED BY CODE** | `c_collision` & `bridge_collision_cost()` [L546-L654, L692-L699] | $C_{\text{collision}} = C_{\text{direction}} + C_{\text{long\_dist}} + C_{\text{penetration}}$<br>• $dx \le 0 \implies +2.0$<br>• $\text{dist} > 8.0 \implies +(\text{dist}-8.0)\cdot 0.4$<br>• Nếu bridge cắt nét chính hoặc vi phạm clearance: $2.0 + 4.0 \cdot \text{pen}$ | **Chỉ kiểm tra va chạm giữa candidate bridge với primary strokes của 2 glyph liền kề**. HOÀN TOÀN CHƯA kiểm tra va chạm với dấu tiếng Việt (diacritics). |
| **$C_{\text{legibility}}$** | **CONFIRMED BY CODE** | `w.cost_legibility` [L333, L341, L669, L701] | Scalar gán sẵn trên biến thể:<br>• `std`: $0.0$<br>• `mid_in`, `high_out`: $0.05$<br>• `closed`, `isolated`: $0.02$ | **Chỉ là một heuristic phạt độ lệch so với nét chuẩn canonical**. Không phải mô hình ML hay đánh giá độ dễ đọc thực nghiệm. |

---

## E. Vietnamese Diacritic Pipeline

### 1. Luồng xử lý dấu từ Unicode đến SVG Render

```text
Chuỗi Unicode đầu vào (VD: "tiếng")
   │
   ▼
normalize_vietnamese_final_uy_tone() [L955]  ──► Chuẩn hóa âm tiết (luỵ -> lụy)
   │
   ▼
group_nfd_graphemes() [L922]
   │  ├── unicodedata.normalize('NFD', text)
   │  └── Phân nhóm: ['t'], ['i', '\u0301'], ['e', '\u0302'], ['n'], ['g']
   │
   ▼
Loop Word & Grapheme:
   │  ├── analyze_text_contexts() [L1022] ──► context: is_word_initial, is_word_final...
   │  ├── select_contextual_glyph() [L1092] ──► Chọn raw glyph base ('t', 'i', 'e', 'n', 'g')
   │  └── Tạo char_info_list (lưu accents riêng biệt: accents=['\u0301'], accents=['\u0302'])
   │
   ▼
optimize_word_dag(char_info_list) [L707]
   │  └── [CHỈ TỐI ƯU TRÊN BASE GLYPHS - HOÀN TOÀN BỎ QUA ACCENTS]
   │
   ▼
Render Word Loop (Sau khi DAG kết thúc):
   │  ├── Dựng base strokes + ligature bridges
   │  └── if info["accents"]:
   │            generate_accents(b_char, info["accents"], info["cx"], dot_below_x_offset) [L175]
   │                 ├── Xác định is_upper -> y_shift = -5.0 if isupper else 0.0
   │                 ├── Dựng structural mark (nón \u0302, trăng \u0306, móc \u031b) tại cx
   │                 ├── Dựng tone mark (\u0301, \u0300, \u0309, \u0303, \u0323) lệch tầng/lệch tâm
   │                 └── Scale tọa độ: acc_scaled = acc_s * scale_vec + offset
   │                 └── Append vào word_secondary_strokes
   │
   ▼
apply_bio_variation() [L1148] ──► Toàn bộ base + secondary strokes nhận cùng biến thiên
   │
   ▼
build_svg() [path_optimizer.py:L316] ──► Xuất path SVG
```

### 2. Phân loại hai nhóm dấu tiếng Việt trong mã nguồn

Mã nguồn trong hàm `generate_accents()` (`engine.py:L175-L303`) và hàm audit (`engine.py:L1674-L1676`) phân biệt rõ hai nhóm dấu theo Unicode combining marks:

#### Nhóm A: Structural Diacritics (Dấu định dạng nguyên âm)
- **Ký tự combining**:
  - `\u0302`: Nón / Mũ (â, ê, ô)
  - `\u0306`: Trăng / Á (ă)
  - `\u031b`: Móc (ơ, ư)
- **Biểu diễn hình học**:
  - `\u0302` (Mũ): Nét gãy 3 điểm `[[cx - 1.6, 4.6 + y_shift], [cx, 2.5 + y_shift], [cx + 1.6, 4.6 + y_shift]]`. `[L197]`
  - `\u0306` (Trăng): Nét cong Bézier lòng máng 6 điểm từ `cx - 1.6` đến `cx + 1.6`, đáy võng xuống `4.6`. `[L202]`
  - `\u031b` (Móc): Hai đoạn Bézier nối tiếp gắn vào góc trên bên phải của nguyên âm tại `cx + 1.8`, `y = 7.0 + y_shift`. `[L208-L212]`

#### Nhóm B: Tone Marks (Dấu thanh điệu)
- **Ký tự combining**:
  - `\u0301`: Sắc
  - `\u0300`: Huyền
  - `\u0309`: Hỏi
  - `\u0303`: Ngã
  - `\u0323`: Nặng
- **Cơ chế xếp tầng (Stacked Base) khi gặp nguyên âm phức tạp**:
  Trong `generate_accents()`, cờ `has_stacked_base = has_non or has_trang` được dùng để né tránh va chạm giữa dấu thanh và dấu định dạng:
  - **Tổ hợp ấ, ầ, ẩ, ẫ, ậ / ắ, ằ, ẳ, ẵ, ặ**:
    - Dấu sắc (`\u0301`): Nâng lên tầng cao và dạt sang sườn phải của mũ: `[[cx + 0.7, 2.4], [cx + 2.2, 0.2]]`. `[L230-L231]`
    - Dấu huyền (`\u0300`): Nâng lên tầng cao và dạt sang sườn trái của mũ: `[[cx - 0.7, 2.4], [cx - 2.2, 0.2]]`. `[L241-L242]`
    - Dấu hỏi (`\u0309`): Đặt trên đỉnh chóp nón: từ `y = 0.8` lên `y = -0.2` rồi xuống `y = 2.2`. `[L254-L263]`
    - Dấu ngã (`\u0303`): Nâng lên cao trên nón: `y` dao động từ `0.1` đến `2.0`. `[L292-L293]`
    - Dấu nặng (`\u0323`): Nằm dưới baseline tại `y = 15.2 .. 16.3`, không bị ảnh hưởng bởi mũ phía trên. `[L217-L225]`
  - **Tổ hợp ớ, ờ, ở, ỡ, ợ / ứ, ừ, sử, ữ, ự (`has_moc = True`)**:
    - Dấu hỏi (`\u0309`): Dạt sang bên trái tâm (`cx_h = cx - 0.9`) để nhường chỗ cho móc ở sườn phải. `[L265-L275]`
    - Dấu sắc (`\u0301`), huyền (`\u0300`), ngã (`\u0303`): Đều có nhánh tọa độ riêng dạt sang trái né râu móc.

### 3. Bản đồ Anchor và Offset

Dữ liệu định vị dấu hiện tại:
1. **Tọa độ $X$ (Trọng tâm ngang)**:
   - Được lấy trực tiếp từ từ điển `font_pack["centers"][base_char]` (hoặc fallback về `DEFAULT_CENTER = 4.8`).
   - Riêng dấu nặng (`\u0323`), offset bổ sung `dot_below_x_offset` được tra từ `font_pack.get("dot_below_x_offsets", {})`:
     - Trên `omnidraw_legacy`: mặc định `y` và `Y` offset `+2.2`. `[L218]`
     - Trên `omni_casual`: cấu hình tường minh `{"y": 0.4, "Y": 0.0}`. `[font_packs/__init__.py:L36-L39]`
2. **Tọa độ $Y$ (Cao độ dọc)**:
   - Được gán cứng (hard-coded) theo hệ trục tọa độ tiêu chuẩn của glyph ($x\text{-height} = 7.0$, $\text{cap-height} = 2.0$, $\text{baseline} = 14.0$).
   - Nếu ký tự gốc viết hoa (`base_char.isupper()`), toàn bộ dấu phía trên được tịnh tiến nâng cao lên:
     $$y_{\text{shift}} = -5.0$$
3. **Phụ thuộc hình học**:
   - Anchor **KHÔNG** phụ thuộc vào biến thể được chọn trong DAG (`GlyphVariant`). Dù DAG chọn biến thể `std`, `mid_in` hay `isolated`, dấu vẫn rơi vào cùng tọa độ `cx` cố định của base char.
   - Anchor **KHÔNG** thích ứng theo độ dốc nét nối hoặc các nét lân cận ở runtime.

---

## F. Current vs Target Gap

Bảng đối chiếu giữa Hiện trạng mã nguồn (Current Implementation) và Yêu cầu phương pháp nghiên cứu đề xuất P0 (Proposed CA-VHC Target):

| Tiêu chí kiến trúc | Hiện trạng mã nguồn (`backend/handwriting/`) | Mục tiêu thiết kế P0 (Proposed CA-VHC) | Mức độ Gap & Đánh giá |
| :--- | :--- | :--- | :--- |
| **Không gian trạng thái Trellis DAG** | **Chỉ chứa Base Glyphs**. `GlyphVariant` chỉ có strokes thân chữ, entry/exit và flags nối nét. `[CONFIRMED BY CODE: engine.py:L329]` | **Diacritic-Aware State Representation**. Node biểu diễn tổ hợp (Base Glyph Variant $\times$ Diacritic Placement / Allograph). | **GAP CỐT LÕI (P0)**: DAG hoàn toàn "mù" trước dấu tiếng Việt. |
| **Thời điểm gắn dấu** | **Hậu kỳ (Post-DAG)**. Sinh dấu bằng `generate_accents()` sau khi Viterbi đã kết thúc. `[CONFIRMED BY CODE: engine.py:L1385]` | **Nội tại trong DAG (In-DAG)**. Quyết định vị trí dấu và biến thể ký tự diễn ra đồng thời trong quá trình tối ưu. | **GAP CỐT LÕI (P0)**: Không thể lựa chọn biến thể dấu theo ngữ cảnh kết nối. |
| **Kiểm tra va chạm dấu (Collision)** | **Chỉ có Offline Auditor** (`audit_vietnamese_lowercase_accents()`). Runtime DAG chỉ kiểm tra va chạm giữa bridge với thân chữ. `[CONFIRMED BY CODE: engine.py:L546, L1660]` | **Runtime Diacritic Collision Penalty**. Đưa va chạm dấu-thân chữ, dấu-dấu, và dấu-cầu nối vào hàm chi phí $J$. | **GAP LỚN (P0)**: Cầu nối chữ viết có thể đâm xuyên qua dấu của ký tự kề cận mà DAG không phát hiện được. |
| **Thứ tự nét trễ (Delayed Strokes)** | **Chưa triển khai (NOT IMPLEMENTED)**. Nét phụ được append tĩnh vào cuối mỗi từ (`word_secondary_strokes`). `[CONFIRMED BY CODE: engine.py:L1338-L1395]` | **Delayed-Stroke Optimization**. Tối ưu động thứ tự viết dấu: viết ngay, viết sau từ, hay gom nhóm nét trễ để giảm quãng đường di chuyển. | **GAP LỚN (P0)**: Đang là giả định nghiên cứu trong tài liệu, chưa có thuật toán trong code. |
| **Lựa chọn Allograph ngữ cảnh** | **Greedy Override trước DAG** (`select_contextual_glyph()`). Chỉ chọn 1 candidate duy nhất cho formal K/T/C hoặc word-final n/m. `[CONFIRMED BY CODE: engine.py:L1092]` | **Multi-Candidate Contextual Trellis**. Đưa các biến thể ngữ cảnh vào Trellis layer để DAG tự cân bằng giữa phong cách và chi phí chuyển động. | **GAP TRUNG BÌNH (P1)**: Quyết định cứng trước DAG làm mất tính tối ưu toàn cục. |
| **Chi phí dễ đọc ($C_{\text{legibility}}$)** | **Scalar heuristic tĩnh** ($0.0, 0.02, 0.05$ gán cứng theo tag). `[CONFIRMED BY CODE: engine.py:L392-L421]` | **Mô hình đánh giá độ dễ đọc có cơ sở thực nghiệm** (dựa trên biến dạng ký tự và khoảng cách nhận dạng). | **GAP NHỎ (P2)**: Hiện tại chỉ đóng vai trò tie-breaker ưu tiên biến thể "std". |

---

## G. Technical Debt

Dưới đây là danh mục nợ kỹ thuật (Technical Debt) được xác thực trực tiếp từ mã nguồn:

### `DAG-01`: Diacritics are Attached Exclusively Post-DAG (Hậu kỳ tách rời)
- **Problem**: Dấu tiếng Việt hoàn toàn không tham gia vào cấu trúc Trellis DAG và thuật toán Viterbi DP. Hàm `generate_accents()` được gọi độc lập sau khi `optimize_word_dag()` đã chọn xong toàn bộ glyph.
- **Impact**: Viterbi không thể cân nhắc các cách đặt dấu khác nhau hoặc chọn biến thể ký tự thân chữ phù hợp với dấu để tránh va chạm.
- **Evidence**: `backend/handwriting/engine.py:optimize_word_dag()` [L707-L791] không nhận tham số `accents`; hàm `generate_accents()` được gọi tại [L1386-L1395].
- **Priority**: **P0** (Chặn nghiên cứu Proposed CA-VHC).

---

### `DAG-02`: Zero Runtime Diacritic Collision Checking in Transition Evaluation
- **Problem**: Hàm `bridge_collision_cost()` chỉ nhận `prev_strokes_world` và `curr_strokes_world` của các nét chính (primary strokes). Không có nét dấu nào được đưa vào kiểm tra va chạm khi dựng cầu nối ligature.
- **Impact**: Nét nối chữ (ligature bridge) từ các ký tự có điểm thoát cao (high exit) hoặc nét đón cao có thể cắt ngang qua dấu nặng của chữ trước hoặc dấu thanh của chữ sau mà không bị phạt chi phí $C_{\text{collision}}$.
- **Evidence**: `backend/handwriting/engine.py:eval_transition()` [L657-L705], `bridge_collision_cost()` [L546-L580].
- **Priority**: **P0**.

---

### `DAG-03`: Contextual Allographs are Greedily Overridden Before DAG
- **Problem**: Hàm `select_contextual_glyph()` quyết định cứng một biến thể duy nhất (formal initial hoặc word-final) trước khi chuyển dữ liệu cho DAG, thay vì đưa cả biến thể chuẩn và biến thể ngữ cảnh vào tập candidate của layer.
- **Impact**: Nếu một biến thể ngữ cảnh tạo ra tư thế nét đón/thoát bất lợi dẫn đến chi phí chuyển động $J$ cực lớn hoặc va chạm, DAG không có quyền fallback về biến thể chuẩn (base glyph).
- **Evidence**: `backend/handwriting/engine.py:text_to_strokes()` [L1296-L1302] gọi `select_contextual_glyph()` và chỉ đẩy 1 `raw_s` vào `char_info_list`.
- **Priority**: **P1**.

---

### `DAG-04`: Rigid Procedural Anchors Without Per-Glyph Anchor Metadata
- **Problem**: Tọa độ dấu được tính hoàn toàn bằng công thức thủ tục số học dựa trên `cx` và `y_shift` gán cứng trong `generate_accents()`, không có bảng anchor metadata đa điểm (top-anchor, bottom-anchor, horn-anchor) gắn liền với từng glyph variant.
- **Impact**: Không hỗ trợ được các font pack có giải phẫu chữ đặc thù hoặc các biến thể chữ nghiêng tự nhiên có trọng tâm thay đổi theo từng allograph.
- **Evidence**: `backend/handwriting/engine.py:generate_accents()` [L185-L300].
- **Priority**: **P1**.

---

### `DAG-05`: Delayed-Stroke Ordering is Static Word-End Append
- **Problem**: Mã nguồn chưa có bất kỳ thuật toán lập lịch thứ tự nét trễ nào. Tất cả nét dấu, dấu chấm chữ i/j, gạch ngang t/f/đ đều được gom vào danh sách `word_secondary_strokes` và vẽ tuần tự ở cuối từ.
- **Impact**: Máy vẽ plotter buộc phải quay lại vẽ toàn bộ dấu sau khi xong thân từ, không tối ưu được hành trình đầu bút giữa kịch bản "vẽ dấu ngay sau nguyên âm" và "vẽ dấu cuối từ".
- **Evidence**: `backend/handwriting/engine.py:text_to_strokes()` [L1327, L1385, L1403].
- **Priority**: **P0** (Đối với nhánh tối ưu hành trình plotter TV2/TV4).

---

### `DAG-06`: Monolithic Engine File with Embedded Inline Self-Check Suite
- **Problem**: File `backend/handwriting/engine.py` dài tới 3,884 dòng, trong đó từ dòng 1867 đến 3883 (>2,000 dòng) là hàm kiểm tra nội bộ `_run_self_check()` chứa hàng chục block test tích hợp chạy thẳng khi khởi động file.
- **Impact**: Khó bảo trì, tăng nguy cơ side-effects khi refactor; các test không được quản lý chuẩn qua pytest runner chung.
- **Evidence**: `backend/handwriting/engine.py:L1867-L3884`.
- **Priority**: **P2**.

---

### `DAG-07`: Fixed Heuristic $C_{\text{legibility}}$ Without Readability Metric Foundation
- **Problem**: Chi phí $C_{\text{legibility}}$ chỉ là các giá trị phạt tĩnh ($0.0, 0.02, 0.05$) định nghĩa trong `get_glyph_variants()`.
- **Impact**: Không lượng hóa được mức độ suy giảm tính dễ đọc khi chữ bị kéo dãn nét nối hoặc khi dấu bị xê dịch.
- **Evidence**: `backend/handwriting/engine.py:get_glyph_variants()` [L373, L404, L414, L417, L421].
- **Priority**: **P2**.

---

## H. Candidate Integration Points (Đề xuất cho Bước B)

> [!NOTE]  
> Đây là phân tích thiết kế kiến trúc phục vụ cho Bước B. Tuyệt đối **KHÔNG** thực hiện thay đổi code trong bước này.

Để đưa biểu diễn có nhận thức về dấu (Diacritic-Aware State) vào Trellis DAG, có hai phương án kiến trúc khả thi được đặt lên bàn cân:

### So sánh hai phương án tích hợp

| Tiêu chí | Phương án A: Mở rộng trực tiếp `GlyphVariant` (Compound Variant State) | Phương án B: Lớp tiền xử lý ứng viên tổ hợp trước DAG (Composition Candidate Layer) |
| :--- | :--- | :--- |
| **Bản chất kiến trúc** | Mở rộng class `GlyphVariant` thành Compound State: Một node trong DAG chứa cả `base_strokes` và `diacritic_strokes` (với các cấu hình vị trí dấu khác nhau). | Giữ nguyên `GlyphVariant` là nét thân chữ; tạo thêm cấu trúc `WordCompositionCandidate` bọc bên ngoài layer để sinh các cặp (Thân chữ, Cấu hình dấu). |
| **Vị trí tác động code** | `engine.py:GlyphVariant` [L329], `get_glyph_variants()` [L359], `eval_transition()` [L657], `text_to_strokes()` [L1320-L1396]. | `engine.py:select_contextual_glyph()` [L1092], tạo hàm mới `generate_diacritic_candidates()`, bổ sung tham số cho `optimize_word_dag()`. |
| **Độ phức tạp tính toán** | Số candidate mỗi layer dự kiến tăng từ $K \le 3$ lên $K' = K_{\text{base}} \times K_{\text{diacritic}} \approx 4-6$. Độ phức tạp lý thuyết chuyển từ $O(L \cdot K^2)$ sang $O(L \cdot K'^2)$. Việc tăng số candidate dự kiến vẫn khả thi với kích thước từ tiếng Việt thông thường (3–7 ký tự), nhưng latency thực tế chưa được đo đạc. Cần benchmark thực nghiệm trong Bước C trước khi kết luận ngưỡng thời gian (`[INFERENCE / ESTIMATE — chưa được benchmark thực nghiệm]`). | Số candidate của DAG chỉ tăng khi có dấu ($K' \approx 4-6$). Tách biệt rõ ràng giữa logic chọn glyph và logic định vị dấu. Cần benchmark độ trễ thực tế ở Bước C (`[INFERENCE / ESTIMATE]`). |
| **Độ tương thích ngược (Backward Compatibility)** | **Khả thi có kiểm soát**: API compatibility giữ mức CAO. Đối với input ASCII / không dấu, mục tiêu hồi quy là PRESERVE hành vi và đường nét hiện tại. Đối với input tiếng Việt có dấu, SVG geometry và quyết định chuyển tiếp chuyển động CÓ THỂ thay đổi có chủ đích (`NOT GUARANTEED` to be identical), vì đây chính là mục tiêu cốt lõi của Diacritic-Aware CA-VHC. | **Trung bình**: Cần thay đổi cấu trúc dữ liệu truyền vào `optimize_word_dag()` và sửa đổi hàm nhận kết quả ở renderer. |
| **Khả năng kiểm thử (Testability)** | Kiểm thử rất thuận lợi: Có thể viết unit test độc lập cho từng node `GlyphVariant` xem nó chứa những nét dấu nào và bounds ra sao. | Cần mock cả 2 tầng (tầng sinh tổ hợp và tầng giải DAG) khi viết unit test. |
| **Rủi ro hồi quy (Regression Risk)** | **Thấp đối với ASCII**: Nét dấu đi kèm với node, hàm `bridge_collision_cost()` chỉ cần kiểm tra thêm danh sách nét dấu có sẵn trong node. | **Trung bình**: Dễ xảy ra lệch pha (sync drift) giữa vị trí thân chữ đã tối ưu và vị trí dấu được gắn sau. |

### Đề xuất kỹ thuật cho Bước B

- **Candidate Recommendation from Audit**:
  Phương án A (Compound Variant State) là một hướng đi khả thi sơ bộ dựa trên cấu trúc mã nguồn hiện tại, giúp giảm thiểu thay đổi giao diện hàm `optimize_word_dag()`.
- **Final Architecture for Bước B: CHƯA KHÓA**:
  Kiến trúc chính thức cho Bước B chưa được chốt cứng. Cần thực hiện Design Review kỹ lưỡng trước khi bắt đầu implementation. Cụ thể, nhóm phát triển sẽ xem xét thêm một **Kiến trúc Hybrid tiềm năng**:
  - `GlyphVariant`: Tiếp tục giữ nguyên ngữ nghĩa cốt lõi là biến thể hình học của thân chữ gốc (base-glyph variant).
  - `CompositionState`: Đóng vai trò State Trellis ở cấp độ CA-VHC (tổ hợp thân chữ + dấu).
  - `DiacriticCandidate`: Biểu diễn cấu hình dấu độc lập (tọa độ anchor, bounding box, clearance zone).
  
Việc lựa chọn giữa Phương án A thuần túy và kiến trúc Hybrid sẽ được thống nhất sau buổi Design Review của Bước B.

---

## I. Existing Tests & Missing Tests

### 1. Bảng danh mục Tests hiện có liên quan đến Handwriting & DAG

| Test Suite / File | Test Name | Chức năng kiểm chứng thực tế | Nhãn bằng chứng |
| :--- | :--- | :--- | :--- |
| `backend/test_handwriting_validation.py` | `test_valid_handwriting_request` | Kiểm tra luồng API Gateway `/api/ai/generate`, trả về SVG hợp lệ và có `pen_lift_count > 0`. | `CONFIRMED BY CODE: test_handwriting_validation.py:L35` |
| `backend/test_handwriting_validation.py` | `test_seed_determinism` | Kiểm tra tính bất biến (determinism): Cùng text và seed luôn cho cùng độ dài nét và số lần nhấc bút. | `CONFIRMED BY CODE: test_handwriting_validation.py:L49` |
| `backend/test_handwriting_validation.py` | `test_valid_styles_all_succeed` | Kiểm tra 4 style (`hand_hocsinh`, `hand_nguoilon`, `hand_thuphap`, `hand_chukinhanh`) sinh SVG thành công. | `CONFIRMED BY CODE: test_handwriting_validation.py:L79` |
| `backend/test_handwriting_validation.py` | `test_valid_fonts_succeed` | Kiểm tra 5 font profile (`oly`, `omni_casual`, `thanhdam`, `thuphap`, `cursive`) render không lỗi. | `CONFIRMED BY CODE: test_handwriting_validation.py:L94` |
| `backend/test_handwriting_validation.py` | `test_formal_letter_type_compatibility` | Kiểm tra tính tương thích của `letter_type="formal"`: thành công với `oly`, bị từ chối với `omni_casual`. | `CONFIRMED BY CODE: test_handwriting_validation.py:L148` |
| `backend/handwriting/engine.py` | `_run_self_check()` (Block 4) | Kiểm tra Viterbi DP trên từ "viet": chọn đúng 4 biến thể, 3 chuyển tiếp, có ít nhất 1 nét nối. | `CONFIRMED BY CODE: engine.py:L1884-L1896` |
| `backend/handwriting/engine.py` | `_run_self_check()` (Block 5) | Kiểm tra invariant: `entry_pt` trùng điểm đầu nét chính 1, `exit_pt` trùng điểm cuối nét chính cuối cho toàn bộ a-z. | `CONFIRMED BY CODE: engine.py:L1898-L1914` |
| `backend/handwriting/engine.py` | `_run_self_check()` (Block 6) | Kiểm tra tích hợp cầu nối ligature trên từ nhiều nét ("minh", "nguyen"): bridge khớp chính xác với DP. | `CONFIRMED BY CODE: engine.py:L1915-L1978` |
| `backend/handwriting/engine.py` | `_run_self_check()` (Block 7) | Kiểm tra anisotropic tangent scaling: vector tiếp tuyến trong world coordinates phải được scale và normalize đúng. | `CONFIRMED BY CODE: engine.py:L1980-L2027` |
| `backend/handwriting/engine.py` | `_run_self_check()` (Block 8) | Kiểm tra tính toàn vẹn hình học của `build_ligature_bridge()`: không sinh NaN/Inf kể cả khi tangent = 0. | `CONFIRMED BY CODE: engine.py:L2028-L2044` |
| `backend/handwriting/engine.py` | `_run_self_check()` (Block 9) | Kiểm tra va chạm hình học: unit test `segments_intersect()`, regression check bugbot, tiếp xúc mút hợp lệ. | `CONFIRMED BY CODE: engine.py:L2045-L2073` |
| `backend/handwriting/engine.py` | `_run_self_check()` (Block Accent Audit) | Kiểm định bộ dấu tiếng Việt 72 nguyên âm thường (`audit_vietnamese_lowercase_accents()`) cho font pack. | `CONFIRMED BY CODE: engine.py:L1660-L1845` |

### 2. Khoảng trống kiểm thử còn thiếu (Missing Tests)

1. **Thiếu Unit Test độc lập cho `optimize_word_dag()` và `eval_transition()`**: Hiện các test giải thuật DAG chỉ nằm trong hàm script `_run_self_check()` của `engine.py`, không được thực thi tự động qua `pytest backend/test_handwriting_validation.py`.
2. **Thiếu Test va chạm giữa Cầu nối (Ligature Bridge) và Dấu tiếng Việt**: Chưa có ca kiểm thử nào kiểm tra tình huống cầu nối từ chữ cái phía trước đi xuyên qua dấu của chữ cái phía sau (hoặc ngược lại).
3. **Thiếu Test cho các tổ hợp dấu kép phức tạp trong ngữ cảnh từ**: Các tổ hợp như "nghiêng", "khoảnh", "thưởng", "truyền" chưa được kiểm tra về khoảng hở clearance giữa dấu của hai nguyên âm đứng liền nhau.
4. **Thiếu Performance Benchmark Test cho Viterbi DP**: Chưa có test đo lường thời gian chạy và bộ nhớ của `optimize_word_dag()` khi số lượng ký tự trong từ tăng lên hoặc khi mở rộng số candidate mỗi layer.
5. **Thiếu Test lập lịch thứ tự nét trễ (Delayed-Stroke Ordering)**: Do tính năng chưa được hiện thực trong mã nguồn.

---

## J. Files that would likely change in Bước C (Planning Only)

> [!IMPORTANT]  
> Danh sách dưới đây chỉ mang tính chất dự báo phạm vi cho Bước C (Implementation). Không thực hiện bất kỳ sửa đổi nào đối với các file này trong Bước A.

1. `backend/handwriting/engine.py`:
   - Mở rộng class `GlyphVariant` để tiếp nhận trường `diacritic_strokes` và `diacritic_tag` (hoặc tạo lớp `CompositionState`).
   - Cập nhật hàm `get_glyph_variants()` để nhận thông tin `accents` và sinh các candidate tổ hợp.
   - Cập nhật hàm `eval_transition()` và `bridge_collision_cost()` để đưa nét dấu vào tập kiểm tra va chạm runtime.
   - Cập nhật vòng lặp render trong `text_to_strokes()` để thu hoạch nét dấu trực tiếp từ kết quả Viterbi DAG.
2. `backend/handwriting/font_packs/geometry.py`:
   - Bổ sung helper trích xuất bounding box và clearance zone cho nét dấu phục vụ kiểm tra va chạm nhanh (broad-phase collision).
3. `backend/handwriting/font_packs/letter_variants.py`:
   - Định nghĩa các biến thể dấu đặc thù (diacritic variants: bẹt, dựng, lệch trái, lệch phải).
4. `backend/test_handwriting_validation.py`:
   - Tách các test DAG từ `_run_self_check()` thành các test case pytest chính thức.
   - Bổ sung test case hồi quy cho diacritic-aware Trellis DAG.

---

## K. Backward Compatibility Risks Matrix

| Thành phần có nguy cơ bị ảnh hưởng | Mức độ rủi ro | Phân tích nguyên nhân và Biện pháp kiểm soát rủi ro |
| :--- | :---: | :--- |
| **Seed Determinism** | **HIGH** | Nếu đưa dấu vào DAG, hàm mục tiêu $J$ sẽ thay đổi giá trị dẫn đến quyết định chọn biến thể và cầu nối có thể khác với phiên bản v1 trên cùng một seed ngẫu nhiên đối với từ có dấu. Cần giữ nguyên logic khởi tạo RNG và bảo toàn kết quả determinism đối với các từ thuần ASCII không có dấu. |
| **SVG Output & Visual Specimen** | **HIGH** | Đường nét SVG của các từ tiếng Việt có dấu CÓ THỂ thay đổi có chủ đích (behavioral change by design) do dấu được tối ưu vị trí và cầu nối tránh va chạm. Đối với văn bản thuần ASCII / không dấu, mục tiêu hồi quy là PRESERVE hoàn toàn hình học cũ. Cần cập nhật baseline trong `qa_specimens.py` và kiểm tra đối sánh trực quan. |
| **Existing Tests (`test_handwriting_validation.py`)** | **LOW** | Toàn bộ 34 test hiện tại chỉ kiểm tra HTTP status, mã lỗi validation, kiểu dữ liệu metrics (`pen_lift_count > 0`). Miễn là pipeline không crash và vẫn trả về SVG, các test này sẽ tiếp tục PASS 100%. |
| **API Contract (`/api/ai/generate`)** | **LOW** | Request payload và Response schema giữ nguyên $100\%$, không bổ sung trường bắt buộc mới. |
| **Font Packs (`omnidraw_legacy`, `omni_casual`)** | **LOW** | Dữ liệu hình học gốc của các nét chữ (`glyphs`, `widths`, `centers`) không bị thay đổi. |
| **Thời gian đáp ứng API (Latency)** | **LOW (Lý thuyết)** | Về mặt lý thuyết, việc tăng candidate mỗi layer từ $K \le 3$ lên $K' \approx 4-6$ giữ độ phức tạp ở mức $O(L \cdot K'^2)$, hoàn toàn khả thi với các từ tiếng Việt ngắn. Tuy nhiên, các con số thời gian thực thi (latency) cụ thể chưa được đo lường thực nghiệm (`[INFERENCE / ESTIMATE — chưa được benchmark thực nghiệm]`). Cần xây dựng benchmark suite chuyên biệt ở Bước C để kiểm chứng chính xác thời gian chạy trên từng từ và trên toàn trang. |

---

## L. Đánh giá Ranh giới Phân công: TV4 vs TV2

Dựa trên mã nguồn thực tế đối chiếu với phân công nghiên cứu:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        SHARED CORE RUNNER                              │
│  backend/handwriting/engine.py:                                        │
│  - optimize_word_dag() [Runner DP Viterbi]                             │
│  - eval_transition()   [Khung tích hợp hàm mục tiêu tổng J]            │
└──────────────────┬──────────────────────────────────┬──────────────────┘
                   │                                  │
                   ▼                                  ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│             TV4 DOMAIN               │  │          TV2 DOMAIN          │
│      Composition & Linguistics       │  │     Motion & Kinematics      │
├──────────────────────────────────────┤  ├──────────────────────────────┤
│ • Biểu diễn Glyph/State:             │  │ • Chi phí di chuyển đầu bút: │
│   - GlyphVariant, split_glyph_strokes│  │   - D_penup (khoảng cách)    │
│ • Font Packs & Hình học dấu:         │  │ • Chi phí nhấc bút:          │
│   - legacy, omni_casual, geometry    │  │   - N_lift, w2 penalty       │
│ • Xử lý Tiếng Việt:                  │  │ • Chi phí động học & góc:    │
│   - normalize_uy, group_nfd, accents │  │   - C_curvature (tiếp tuyến) │
│ • Ngữ cảnh & Dễ đọc:                 │  │ • Tối ưu hành trình nét trễ: │
│   - analyze_text_contexts            │  │   - delayed stroke kinematics│
│   - select_contextual_glyph          │  │ • Giới hạn gia tốc máy vẽ:   │
│   - C_legibility, Clearance checks   │  │   - physical feedrate limits │
│ • Render & Xuất bản vẽ:              │  │                              │
│   - apply_bio_variation, build_svg   │  │                              │
└──────────────────────────────────────┘  └──────────────────────────────┘
```

- **Tính toàn vẹn ranh giới trong mã nguồn hiện tại**: Trong code v1, TV4 đã hoàn thành phần khung cấu trúc ngôn ngữ và font chữ; TV2 đã đóng góp các công thức hình học vector cho $D_{\text{penup}}$, $N_{\text{lift}}$ và $C_{\text{curvature}}$. Điểm giao thoa tiếp theo trong Bước B/C là: **TV4 chịu trách nhiệm mở rộng không gian trạng thái Candidate chứa dấu và vùng an toàn clearance; TV2 chịu trách nhiệm công thức chi phí động học và thuật toán tối ưu thứ tự nét trễ.**

---

## Definition of Done (Xác nhận hoàn thành Audit)

| # | Câu hỏi thẩm định theo yêu cầu nhiệm vụ | Kết luận xác minh từ mã nguồn |
| :---: | :--- | :--- |
| **1** | Handwriting Mode call chain chính xác | **ĐÃ XÁC ĐỊNH**: `main.py:generate_ai_image` $\to$ `engine.py:generate_handwriting_svg` $\to$ `text_to_strokes` $\to$ `normalize_uy` $\to$ `group_nfd` $\to$ `select_contextual_glyph` $\to$ `optimize_word_dag` $\to$ `generate_accents` $\to$ `build_svg`. |
| **2** | `optimize_word_dag()` input/output | **ĐÃ XÁC ĐỊNH**: Input: `char_info_list` (chỉ base chars), `weights`, `force_lift`. Output: `{"variants": [...], "conns": [...]}`. Không trả về strokes hay cost metrics. |
| **3** | Trellis layer/node/edge hiện tại | **ĐÃ XÁC ĐỊNH**: Layer = vị trí ký tự trong từ; Node = `GlyphVariant` (1-3 biến thể); Edge = chuyển tiếp nhấc bút hoặc nối bridge. Không có Graph object độc lập. |
| **4** | State representation thật | **ĐÃ XÁC ĐỊNH**: Class `GlyphVariant` chứa tọa độ/tiếp tuyến vào-ra, flags nối nét, `cost_legibility` và `tag`. Không chứa dấu hay ngữ cảnh. |
| **5** | Candidate generation thật | **ĐÃ XÁC ĐỊNH**: **Hybrid (Kiểu C)**. Allograph ngữ cảnh (formal_initial, word_final) chọn cứng trước DAG; biến thể kết nối (std, mid_in, high_out, isolated) sinh trong DAG. |
| **6** | `eval_transition()` thật | **ĐÃ XÁC ĐỊNH**: $J = w_1 D_{\text{penup}} + w_2 N_{\text{lift}} + w_3 C_{\text{curvature}} + w_4 C_{\text{collision}} + w_5 C_{\text{legibility}}$. So sánh cost nối nét vs nhấc bút. |
| **7** | Viterbi recurrence hiện tại | **ĐÃ XÁC ĐỊNH**: $DP[i, j] = \min_p (DP[i-1, p] + \text{cost\_trans})$. Độ phức tạp $O(L \cdot K^2)$ với $K \le 3$. |
| **8** | NFD pipeline | **ĐÃ XÁC ĐỊNH**: `normalize_vietnamese_final_uy_tone()` $\to$ `group_nfd_graphemes()` phân rã chuẩn NFD thành `[base, mark1, mark2]`. |
| **9** | Diacritics vào trước hay sau DAG | **ĐÃ XÁC ĐỊNH**: **HOÀN TOÀN SAU DAG (POST-DAG)** thông qua `generate_accents()`. |
| **10** | Anchor/offset nằm ở đâu | **ĐÃ XÁC ĐỊNH**: Tâm $x$ lấy từ `font_pack["centers"]` và `dot_below_x_offsets`; Cao độ $y$ gán cứng thủ tục trong `generate_accents()` ($y_{\text{shift}} = -5.0$ cho chữ hoa). |
| **11** | Collision hiện có những lớp nào | **ĐÃ XÁC ĐỊNH**: Lớp A (Offline geometry auditor) = `IMPLEMENTED`; Lớp B (Runtime bridge vs primary strokes) = `IMPLEMENTED`; Lớp C (Runtime diacritic collision) = `NOT IMPLEMENTED`. |
| **12** | $C_{\text{legibility}}$ thực tế là gì | **ĐÃ XÁC ĐỊNH**: Heuristic phạt tĩnh: $0.0$ cho "std", $0.05$ cho "mid_in"/"high_out", $0.02$ cho "closed"/"isolated". |
| **13** | Delayed-stroke hiện có hay chưa | **ĐÃ XÁC ĐỊNH**: **NOT IMPLEMENTED**. Nét phụ chỉ được append tuần tự ở cuối mỗi từ. |
| **14** | Existing tests | **ĐÃ XÁC ĐỊNH**: 34 tests API trong `test_handwriting_validation.py` (PASS 100%) và bộ inline self-checks trong `engine.py` (PASS 100%). |
| **15** | Technical debt | **ĐÃ XÁC ĐỊNH**: 7 mã nợ kỹ thuật từ `DAG-01` đến `DAG-07` kèm bằng chứng dòng mã cụ thể. |
| **16** | Candidate insertion points cho Bước B | **ĐÃ XÁC ĐỊNH**: Đưa ra Candidate Recommendation (Phương án A), đồng thời xác nhận kiến trúc chính thức cho Bước B CHƯA KHÓA (để ngỏ hướng kiến trúc Hybrid). |
| **17** | Không có source file nào bị sửa | **ĐÃ XÁC ĐỊNH**: Không có bất kỳ dòng code nào bị thay đổi trong quá trình audit. |

---

```text
Source code modified: NONE

Audit report created/updated:
- docs/06_audit_trellis_dag_report.md

Audit status: COMPLETE

Unknowns remaining:
- Chưa có dữ liệu thực nghiệm về mức độ suy giảm thẩm mỹ/độ dễ đọc khi di chuyển vị trí dấu tiếng Việt lệch sang trái/phải quá 0.5mm trên máy vẽ plotter thực tế (cần phối hợp mẫu thực nghiệm cùng TV1 & TV2).
- Mức độ tương tác cơ học (chảy mực/rách giấy) khi đầu bút plotter vẽ dấu đè gần nét nối chữ chưa được đo đạc trên phần cứng CNC vật lý.
- Latency thực tế của Viterbi DP khi mở rộng số candidate mỗi layer lên 4–6 chưa có benchmark đo đạc cụ thể trên hệ thống phần cứng mục tiêu.

Recommended next step:
BƯỚC B — design diacritic-aware state representation
```
