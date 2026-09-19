# OmniDraw — CA-VHC Diacritic-Aware State Architecture
## BƯỚC B — Design Specification

**Tài liệu:** `docs/07_diacritic_aware_state_design.md`  
**Dự án:** OmniDraw — Single-Stroke Vector Centerline Engine  
**Module:** CA-VHC (Context-Aware Vietnamese Handwriting Composition)  
**Tác giả:** Nguyễn Tài Anh Tuấn (TV4 — Handwriting Lead & Project Lead) phối hợp cùng TV2 (Stroke Optimization & Path Planning Lead)  
**Thời điểm cập nhật:** 20/09/2026 (Technical Cleanup & Consistency Correction)  
**Chế độ tài liệu:** ARCHITECTURE DESIGN DRAFT SPECIFICATION (Chưa sửa mã nguồn)  
**Trạng thái phê duyệt:** DESIGN DRAFT COMPLETED — PENDING CROSS-REVIEW (Chờ review chéo từ TV2 trước khi sang Bước C)  
**Trạng thái kiểm thử nền tảng:** 34/34 API regression tests PASS  

---

## 1. Bối cảnh, Động lực & Kết quả từ Bước A (Audit Grounding)

Trong **BƯỚC A — Architecture Audit Trellis DAG / CA-VHC** (chi tiết tại [`docs/06_audit_trellis_dag_report.md`](file:///Users/yingjunn_/Study_/Nckh_2026-2027/OmniDraw/docs/06_audit_trellis_dag_report.md)), cấu trúc hiện tại của hệ thống đã được xác lập minh bạch dựa trên mã nguồn thực tế:

1. **Không gian trạng thái hiện tại:** Trellis DAG trong `backend/handwriting/engine.py:optimize_word_dag()` hoạt động ở cấp độ từ (word-level) dựa trên thuật toán Quy hoạch động Viterbi. Mỗi nút (node) trong đồ thị là một đối tượng `GlyphVariant`, biểu diễn các biến thể kết nối tiếp tuyến của **riêng biệt thân chữ cái gốc (base character)** (gồm các nhãn `std`, `mid_in`, `high_out`, `closed`, `isolated`).
2. **Dấu tiếng Việt bị tách rời khỏi DAG (Post-DAG Procedural Attachment):** Chuỗi ký tự đầu vào được phân rã qua Unicode NFD (`group_nfd_graphemes()`), nhưng các dấu thanh và dấu phụ (`accents`) hoàn toàn không tham gia vào không gian trạng thái của Trellis DAG. Chỉ sau khi Viterbi DP hoàn tất và chuỗi thân chữ đã được cố định, hàm `generate_accents()` mới được gọi ở pha hậu kỳ (`text_to_strokes()`) để tính toán tọa độ nét dấu theo quy tắc mỏ neo cứng (procedural anchors dựa trên tâm `cx`).
3. **Hậu quả kỹ thuật & Rủi ro hình học:**
   - **Xung đột cầu nối runtime (Runtime Bridge Collision):** Hàm `build_ligature_bridge()` và `bridge_collision_cost()` chỉ kiểm tra giao cắt giữa cầu nối Bézier với nét thân chữ của ký tự liền kề (`prev_strokes` và `curr_strokes`). Engine hoàn toàn "mù" đối với vị trí dấu tiếng Việt lân cận. Khi xuất hiện nét nối cao (`high_out`) hoặc nét nối dài, cầu nối có thể vắt ngang qua dấu thanh (sắc, huyền, hỏi, ngã) của nguyên âm đứng trước hoặc đứng sau.
   - **Mất khả năng tối ưu hóa thích ứng ngữ cảnh (Lack of Contextual Adaptation):** Vị trí dấu không thể dịch chuyển linh hoạt để né tránh các nét chữ hoa vươn cao (`ascender`) hoặc nét uốn nghệ thuật (`flourish`).
   - **Khoảng cách lý thuyết vs thực tế:** Các tài liệu định hướng (`docs/01_tech-stack.md`, `docs/02_roadmap.md`) ghi nhận CA-VHC tích hợp ràng buộc dấu tiếng Việt, trong khi mã nguồn hiện hành mới dừng ở mức ghép dấu tĩnh hậu kỳ.

**Mục tiêu của BƯỚC B:** Khóa thiết kế kiến trúc không gian trạng thái mới (**Diacritic-Aware State Representation**) cho CA-VHC, giải quyết triệt để vấn đề va chạm dấu mà vẫn bảo toàn nguyên tắc phân tách trách nhiệm (Separation of Concerns), kiểm soát bùng nổ tổ hợp, xác lập mục tiêu bảo toàn hồi quy cho ký tự không dấu (ASCII), và thiết lập chiến lược kiểm thử vững chắc trước khi triển khai mã nguồn ở Bước C.

---

## 2. Nguyên tắc Thiết kế Cốt lõi: Kiến trúc Lai (Hybrid Architecture)

### 2.1 Nguyên tắc bất biến đối với `GlyphVariant`
> **IRON RULE:** `GlyphVariant` giữ nguyên ngữ nghĩa là **biến thể hình học của THÂN CHỮ GỐC (Base Character Geometry)**.  
> Tuyệt đối **KHÔNG** nhồi nhét dấu tiếng Việt, trạng thái lập lịch nét trễ hay toàn bộ dữ liệu ngữ cảnh vào `GlyphVariant` để biến nó thành đối tượng "thần thánh" (God Object).

Cấu trúc hiện tại của `GlyphVariant` (`engine.py:L329-L343`) biểu diễn xuất sắc các đặc tính tiếp tuyến của thân chữ cái:
- Điểm vào/ra: `entry_pt`, `exit_pt`
- Vector tiếp tuyến: `v_entry`, `v_exit`
- Cờ cho phép nối nét: `can_in`, `can_out`
- Nét chính: `strokes`
- Chi phí ưu tiên: `cost_legibility`
- Nhãn biến thể: `tag`

Ngữ nghĩa này được giữ nguyên vẹn trong toàn bộ thiết kế mới.

### 2.2 Kiến trúc Lai được lựa chọn chính thức
Thay vì mở rộng trực tiếp `GlyphVariant` thành một cấu trúc phức hợp cồng kềnh, hệ thống áp dụng mô hình kiến trúc lai (Hybrid Composition Architecture):

```text
       ┌──────────────────────┐
       │     GlyphVariant     │  (Thân chữ gốc: std, mid_in, high_out, closed, isolated)
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │   CompositionState   │ ◄── [Node chính thức của Trellis DAG]
       └──────────▲───────────┘
                  │
       ┌──────────┴───────────┐
       │  DiacriticCandidate  │  (Cấu hình dấu: marks, placement, clearance zone, offsets)
       └──────────────────────┘
```

### 2.3 Lý giải khoa học và kỹ thuật
1. **Phân tách mối quan tâm (Separation of Concerns):** Biến thể hình học thân chữ (đặc tính tiếp tuyến, góc vào/ra) thuộc về quy luật kết nối chữ viết tay. Vị trí dấu thanh (cấu trúc chính tả, độ cao tầng, né va chạm) thuộc về quy tắc cấu tạo âm tiết tiếng Việt. Tách rời hai khái niệm này giúp mã nguồn sáng rõ và chuẩn mực học thuật.
2. **Giảm thiểu độ ghép nối (Low Coupling):** Dữ liệu hình học trong các gói font (`font_packs/`) không bị ràng buộc trực tiếp vào giải thuật bố trí dấu.
3. **Tính khả kiểm độc lập (Unit Testability):** Có thể viết unit test kiểm tra riêng bộ sinh dấu (`DiacriticCandidate`), kiểm tra riêng bộ tính va chạm nội tại, và kiểm tra riêng Trellis DAG mà không làm bẩn fixtures.
4. **Khả năng mở rộng biến thể Allographs:** Dễ dàng bổ sung các biến thể thân chữ mới (như chữ hoa mở đầu trang trọng `formal_initial`, chữ thường kết thúc từ `word_final`) mà không phải tái cấu trúc lại bảng dấu.
5. **Khả năng mở rộng Cá nhân hóa nét chữ (Writer Profile P2):** Khi TV1 phát triển module trích xuất đặc trưng phong cách người viết (độ nghiêng `slant_deg`, độ dao động `baseline_jitter_sigma`), các toán tử biến dạng hình học có thể tác động độc lập lên `GlyphVariant` hoặc `DiacriticCandidate` trước khi đóng gói thành `CompositionState`.
6. **Mục tiêu bảo toàn hồi quy cho ký tự không dấu (ASCII / no-diacritic regression target):** Ký tự không có dấu chỉ cần gán `diacritic_candidate = None`. Không gian trạng thái và thuật toán DAG kỳ vọng suy biến tự nhiên về bài toán gốc (behavior-equivalent target), bảo toàn cấu trúc chuyển trạng thái mà không phát sinh chi phí thừa.
7. **Tương thích phân công trách nhiệm (Ownership Alignment):** TV4 sở hữu `DiacriticCandidate` và `CompositionState` (cấu trúc chữ và hình học dấu); TV2 sở hữu các thành phần động học $J_{\text{transition}}$ (quãng đường, góc bẻ tiếp tuyến, năng lượng nhấc bút).

---

## 3. Thiết kế Thực thể `DiacriticCandidate`

`DiacriticCandidate` đại diện cho một phương án bố trí cụ thể của hệ thống dấu trên nguyên âm cơ sở.

### 3.1 Cấu trúc dữ liệu ý niệm (Conceptual Schema)

```python
from dataclasses import dataclass
from typing import Tuple, Optional, Any
import numpy as np

@dataclass(frozen=True)
class DiacriticCandidate:
    """
    Biểu diễn một cấu hình ứng viên của dấu tiếng Việt cho ký tự cơ sở.
    Bất biến (immutable) để bảo đảm an toàn dữ liệu trong Viterbi DP.
    
    QUY ƯỚC HỆ TỌA ĐỘ BẮT BUỘC:
    - strokes_local được biểu diễn trong HỆ TỌA ĐỘ CỤC BỘ (LOCAL GLYPH/COMPOSITION FRAME)
      so với gốc tọa độ của ký tự cơ sở, đã áp dụng độ lệch (dx, dy).
    - CHƯA áp dụng tọa độ thế giới (chưa cộng page offset, line origin, word origin).
    - Biến đổi sang tọa độ thế giới (world/paper coordinates) chỉ diễn ra khi render SVG
      hoặc khi kiểm tra va chạm cầu nối runtime (bridge collision).
    """
    marks: Tuple[str, ...]                    # Danh sách Unicode combining marks NFD
    placement_tag: str                        # Nhãn vị trí: 'canonical', 'safe_left', 'safe_right'
    strokes_local: Tuple[np.ndarray, ...]     # Danh sách polyline nét dấu ở TỌA ĐỘ CỤC BỘ (local mm)
    anchor_x: float                           # Tọa độ mỏ neo X cục bộ cơ sở (local mm)
    anchor_y: float                           # Tọa độ mỏ neo Y cục bộ cơ sở (local mm)
    dx: float                                 # Khoảng dịch ngang cục bộ so với vị trí chuẩn tắc (mm)
    dy: float                                 # Khoảng dịch dọc cục bộ so với vị trí chuẩn tắc (mm)
    bounds_local: Tuple[float, float, float, float] # Hộp bao cục bộ AABB: (xmin, ymin, xmax, ymax)
    clearance_zone_local: Tuple[np.ndarray, ...]    # Vùng bao an toàn cục bộ (polygon/dilated hull)
    placement_penalty: float                  # Chi phí phạt do lệch khỏi vị trí chuẩn tắc (>= 0.0)
```

### 3.2 Ý nghĩa chi tiết của từng trường dữ liệu & Quy ước Hệ Tọa độ

| Trường | Kiểu dữ liệu | Ý nghĩa kỹ thuật & Quy ước Tọa độ |
| :--- | :--- | :--- |
| `marks` | `Tuple[str, ...]` | Bộ các ký tự combining mark chuẩn Unicode NFD cấu thành dấu. Ví dụ: `('\u0301',)` (dấu sắc), `('\u0302', '\u0301')` (mũ + sắc cho 'ế', 'ố'), `('\u031b', '\u0309')` (móc + hỏi cho 'ở', 'ử'). |
| `placement_tag` | `str` | Định danh phân loại ứng viên P0: <br>• `canonical`: Vị trí chuẩn tắc theo thiết kế font.<br>• `safe_left`: Dấu được dịch sang trái một khoảng an toàn $\Delta x < 0$ nhằm né cầu nối cao từ phía sau vươn tới.<br>• `safe_right`: Dấu được dịch sang phải $\Delta x > 0$ khi phía trái bị che khuất bởi nét vươn cao của ký tự đứng trước.<br>*(Lưu ý: `compact` được định vị là ứng viên thử nghiệm tùy chọn ở P1, không nằm trong bộ ứng viên mặc định của P0).* |
| `strokes_local` | `Tuple[np.ndarray, ...]` | Mảng các polyline vector $(N, 2)$ trong **hệ tọa độ cục bộ (local frame)** của ký tự, đã được cộng vector độ lệch $(\Delta x, \Delta y)$ so với mỏ neo chuẩn. Tuyệt đối chưa chứa tọa độ trang/dòng. |
| `anchor_x`, `anchor_y`| `float` | Tọa độ mỏ neo gốc cục bộ xác định từ tâm `cx` và đỉnh chữ cái cơ sở trước khi dịch chuyển. |
| `dx`, `dy` | `float` | Vector chuyển dịch tương đối so với mỏ neo gốc. Với `canonical`, $dx = 0.0, dy = 0.0$. |
| `bounds_local` | `Tuple[float, 4]` | Hộp bao hình học AABB cục bộ `(xmin, ymin, xmax, ymax)` của toàn bộ nét dấu, dùng cho sàng lọc thô (Broad-phase test) trong không gian local. |
| `clearance_zone_local` | `Tuple[np.ndarray, ...]` | Đa giác vùng cấm cục bộ mở rộng quanh nét dấu với bán kính an toàn $\delta_{\text{clearance}}$. |
| `placement_penalty`| `float` | Giá trị phạt chuẩn hóa không âm $C_{\text{placement}} \ge 0$, phản ánh mức độ suy giảm thẩm mỹ khi dịch chuyển dấu ra khỏi tâm lý tưởng. |

### 3.3 Phân định Dấu Cấu trúc (Vowel-forming Marks) và Dấu Thanh (Tone Marks)
Cấu trúc chính tả chữ viết tiếng Việt theo chuẩn Unicode NFD phân tách rạch ròi giữa hai tầng dấu:
- **Dấu cấu trúc tạo nguyên âm (Vowel-forming Orthographic Marks):** Gồm dấu mũ (circumflex `\u0302`: â, ê, ô), dấu trăng/mũ ngược (breve `\u0306`: ă), và dấu móc (horn `\u031b`: ơ, ư).
- **Dấu thanh (Tone Marks):** Gồm sắc (`\u0301`), huyền (`\u0300`), hỏi (`\u0309`), ngã (`\u0303`), và nặng (`\u0323`).

**Quy tắc phân rã Unicode NFD và biểu diễn trong `DiacriticCandidate`:**
Mọi nguyên âm có dấu phức hợp trong tiếng Việt được phân rã theo thứ tự chuẩn mực:
$$\text{Grapheme NFD} = \text{Base Character} + \text{Structural Mark (nếu có)} + \text{Tone Mark (nếu có)}$$

*Ví dụ chuẩn xác về chuỗi NFD:*
- `ế` $\rightarrow$ `'e'` (`\u0065`) + `'\u0302'` (circumflex) + `'\u0301'` (acute)
- `ố` $\rightarrow$ `'o'` (`\u006f`) + `'\u0302'` (circumflex) + `'\u0301'` (acute)
- `ở` $\rightarrow$ `'o'` (`\u006f`) + `'\u031b'` (horn) + `'\u0309'` (hook above)
- `ử` $\rightarrow$ `'u'` (`\u0075`) + `'\u031b'` (horn) + `'\u0309'` (hook above)
- `ấ` $\rightarrow$ `'a'` (`\u0061`) + `'\u0302'` (circumflex) + `'\u0301'` (acute)
- `ắ` $\rightarrow$ `'a'` (`\u0061`) + `'\u0306'` (breve) + `'\u0301'` (acute)
- `ợ` $\rightarrow$ `'o'` (`\u006f`) + `'\u031b'` (horn) + `'\u0323'` (dot below)

*Quy cách hình học:*
- Dấu cấu trúc đóng vai trò mỏ neo tầng 1 (Tier 1 anchor).
- Dấu thanh được xếp ở tầng 2 (Tier 2 anchor) nằm phía trên hoặc chếch về phía bên phải dấu cấu trúc theo quy chuẩn chính tả truyền thống.
- `DiacriticCandidate` biểu diễn toàn bộ cụm dấu hoàn chỉnh này dưới dạng các nét thành phần riêng biệt trong `strokes_local`.
- **CẤM:** Tuyệt đối không gộp (flatten) cụm dấu thành một nét liền duy nhất nếu việc này làm mất khả năng kiểm tra va chạm nội tại giữa dấu thanh và dấu cấu trúc.

---

## 4. Thiết lập Tham số Cấu hình Duy nhất (Single Source of Truth)

> **IMPORTANT — CẢNH BÁO KHOA HỌC & TẬP TRUNG CẤU HÌNH:**  
> Đề tài hiện **chưa có dữ liệu thực nghiệm đối chuẩn** để chứng minh một giá trị offset hay ngưỡng va chạm cụ thể là tối ưu toàn cục.  
> Toàn bộ các giá trị tham số hình học được quản lý tập trung trong một cấu trúc duy nhất: `DiacriticConfig`. Tuyệt đối không hard-code các số literal rải rác trong mã nguồn. Các giá trị dưới đây là **tham số kỹ thuật mặc định ban đầu (Engineering Defaults / Initial Config)**, phục vụ kiểm thử chức năng trước khi tối ưu hóa qua Ablation Study.

```python
from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class DiacriticConfig:
    """
    Nguồn cấu hình duy nhất (Single Source of Truth) cho hệ thống dấu CA-VHC.
    Toàn bộ giải thuật sinh ứng viên và hàm tính chi phí đều đọc từ cấu trúc này.
    """
    # Ngưỡng dung sai va chạm hình học (Geometry Metric, đơn vị mm):
    # Nếu khoảng cách xuyên thấu penetration_depth_mm <= tolerance_mm thì coi như chưa chạm
    internal_collision_tolerance_mm: float = 0.05
    
    # Khoảng cách an toàn tối thiểu mong muốn giữa dấu và các nét liền kề (Geometry Metric, đơn vị mm):
    clearance_threshold_mm: float = 0.20
    
    # Ngưỡng chi phí va chạm nội tại tối đa cho phép trước khi cắt tỉa ứng viên (Cost Metric, vô hướng không thứ nguyên):
    max_internal_collision_cost: float = 0.50
    
    # Danh sách độ dịch ngang cục bộ cho các ứng viên P0 (mm)
    dx_candidates_mm: Dict[str, float] = field(default_factory=lambda: {
        "canonical": 0.0,
        "safe_left": -0.45,
        "safe_right": +0.45,
    })
    
    # Danh sách độ dịch dọc cục bộ cho các ứng viên P0 (mm)
    dy_candidates_mm: Dict[str, float] = field(default_factory=lambda: {
        "canonical": 0.0,
    })
    
    # Độ lệch dịch chuyển tối đa cho phép để chuẩn hóa placement penalty (mm)
    max_placement_shift_mm: float = 1.0
```

---

## 5. Thiết kế Thực thể `CompositionState` & Cơ chế Chuyển đổi Tọa độ

`CompositionState` là nút (node) chính thức cấu thành không gian trạng thái của Trellis DAG đa tầng.

### 5.1 Cấu trúc dữ liệu ý niệm (Conceptual Schema)

```python
@dataclass(frozen=True)
class CompositionState:
    """
    Node logic chính thức của Trellis DAG tại vị trí ký tự i.
    Bất biến (frozen=True) để bảo đảm an toàn dữ liệu và tái lập thực nghiệm.
    """
    base_variant: GlyphVariant                        # Biến thể hình học thân chữ cái gốc
    diacritic_candidate: Optional[DiacriticCandidate] # Ứng viên cấu hình dấu (None nếu không dấu)
    base_char: str                                    # Ký tự gốc (VD: 'e', 'a', 'o', 'd')
    accents: Tuple[str, ...]                          # Bộ combining marks nguyên bản từ NFD
    context: Dict[str, Any]                           # Ngữ cảnh ký tự (vị trí từ, câu, loại văn bản)
    state_tag: str                                    # Nhãn kết hợp (VD: 'std_canonical', 'high_out_safe_left')
    internal_collision_cost: float                    # Chi phí tự va chạm nội tại C_internal_collision (>= 0.0)
    legibility_cost: float                            # Chi phí thẩm mỹ thân chữ kế thừa từ base_variant (>= 0.0)
    metadata: Dict[str, Any]                          # Thông tin phục vụ debug, tracking và phân tích
```

### 5.2 Cơ chế Chuyển đổi Tọa độ Cục bộ $\rightarrow$ Tọa độ Thế giới (Transform Helper)
Để bảo đảm tính nhất quán tuyệt đối về tọa độ, việc chuyển đổi từ không gian cục bộ (Local) sang không gian thế giới trên giấy (World/Paper) được thực hiện qua hàm tiện ích ý niệm:

```python
def transform_state_to_world(
    state: CompositionState,
    word_origin_x: float,
    baseline_y: float,
    scale: float = 1.0
) -> Tuple[Tuple[np.ndarray, ...], Tuple[np.ndarray, ...]]:
    """
    Chuyển đổi toàn bộ nét của CompositionState từ tọa độ cục bộ sang tọa độ trang giấy (World).
    Trả về: (world_base_strokes, world_diacritic_strokes)
    """
    # 1. Biến đổi nét thân chữ
    world_base = tuple(
        stroke * scale + np.array([word_origin_x, baseline_y])
        for stroke in state.base_variant.strokes
    )
    
    # 2. Biến đổi nét dấu (nếu có)
    world_diacritic = ()
    if state.diacritic_candidate is not None:
        world_diacritic = tuple(
            stroke * scale + np.array([word_origin_x, baseline_y])
            for stroke in state.diacritic_candidate.strokes_local
        )
        
    return world_base, world_diacritic
```

---

## 6. Quy trình Sinh Ứng viên Trạng thái & Kiểm soát Cắt tỉa (Pruning)

### 6.1 Phân tích Không gian Trạng thái Tự nhiên (Raw Candidates Upper Bound)
Trong thiết kế P0:
- Số biến thể thân chữ tối đa của ký tự gốc: $K_{\text{base}} \le 3$ (gồm `std`, `mid_in` hoặc `high_out`, `closed` hoặc `isolated`).
- Số ứng viên dấu tối đa của ký tự có dấu: $K_{\text{diacritic}} \le 3$ (gồm `canonical`, `safe_left`, `safe_right`).
- **Giới hạn cận trên thô tự nhiên (Natural Raw Bound):**
  $$K_{\text{raw}} \le K_{\text{base}} \times K_{\text{diacritic}} \le 3 \times 3 = 9$$

> **CRITICAL RULE — NGUYÊN TẮC CẮT TỈA P0:**  
> Ở giai đoạn P0, tuyệt đối **KHÔNG áp dụng cắt tỉa heuristic top-6 mù quáng** hoặc Beam Search sớm khi chưa chạy thực nghiệm đối chuẩn.  
> P0 **CHỈ CẮT TỈA CÁC ỨNG VIÊN BẤT HỢP LỆ CỨNG (Hard Invalid Candidates)**:
> 1. **Va chạm nội tại vượt ngưỡng cắt tỉa cứng:** Chi phí va chạm nội tại $C_{\text{internal\_collision}} > \text{config.max\_internal\_collision\_cost}$ (hoặc độ sâu xuyên thấu hình học $\text{penetration\_depth\_mm} > \text{config.internal\_collision\_tolerance\_mm}$).
> 2. **Vi phạm biên hình học cứng của dòng kẻ / trang giấy:** Dấu vượt trần dòng chữ (`bounds_local[3] > line_top_bound_local`) hoặc thủng đáy/vượt lề giấy.
> 3. **Hình học suy biến hoặc dữ liệu hỏng:** Chứa tọa độ NaN/Inf, polyline rỗng (`len == 0`), hoặc geometry malformed.
> 4. **Tổ hợp combining marks không hợp lệ:** Kết hợp dấu vi phạm cấu trúc chính tả tiếng Việt.
> 
> **IRON INVARIANT — HARD CONSTRAINTS MUST NOT BE BYPASSED BY FALLBACK:**  
> Một candidate đã bị loại bởi Hard Invalid Constraint **TUYỆT ĐỐI KHÔNG ĐƯỢC HỒI SINH** bằng bất kỳ cơ chế fallback nào.

> **THEORETICAL COMPLEXITY ANALYSIS — NOT A PERFORMANCE BENCHMARK:**  
> Với $K_{\text{raw}} \le 9$, số transition tối đa giữa hai layer liên tiếp là $9 \times 9 = 81$. Đây là kích thước không gian trạng thái tương đối nhỏ về mặt lý thuyết đồ thị Trellis DAG.  
> Tuy nhiên, **latency thực tế** của thuật toán Viterbi DP sau khi bổ sung:  
> - Tính toán hình học va chạm (collision geometry),  
> - Chuyển đổi hệ tọa độ cục bộ $\leftrightarrow$ thế giới (coordinate transforms),  
> - Sinh ứng viên dấu tiếng Việt (diacritic candidate generation)  
> 
> **chưa được đo đạc bằng thực nghiệm đối chuẩn**.  
> Do đó, tài liệu thiết kế Bước B **tuyệt đối không đưa ra kết luận về thời gian xử lý cụ thể** (như `<1ms/từ`, tức thời / instant, đảm bảo thời gian thực / real-time guaranteed, hay độ trễ không đáng kể / negligible latency). Thời gian thực thi thực tế (Viterbi solve latency) bắt buộc phải được đo lường và khảo sát thực nghiệm cụ thể ở Bước C/D trên tập văn bản benchmark.

### 6.2 Chính sách Xử lý Fallback (Fallback Policy & Failure Path)

Để bảo toàn tính toàn vẹn của các ràng buộc hình học cứng, quy trình sinh trạng thái phân định rạch ròi 2 trường hợp:

1. **CASE A — Có ứng viên hợp lệ (`valid_states != []`):**  
   Trả về danh sách `valid_states` bình thường để đưa vào bước truy hồi Viterbi DP.
2. **CASE B — Không còn bất kỳ ứng viên hợp lệ nào (`valid_states == []`):**  
   **TUYỆT ĐỐI KHÔNG** tự ý "hồi sinh" ứng viên `canonical` (hoặc bất kỳ candidate nào) nếu nó đã bị loại vì vi phạm Hard Invalid Constraint (ví dụ: đè nét nghiêm trọng, tọa độ NaN, vượt trần dòng). Việc hồi sinh này sẽ phá vỡ hoàn toàn ý nghĩa của các ràng buộc cứng.  
   Thay vào đó, thiết kế khóa một **đường dẫn thất bại tường minh (Explicit Failure Path)** ở cấp độ kiến trúc: kích hoạt ngoại lệ có cấu trúc `NoValidCompositionState` hoặc trả về `CompositionBuildResult(states=[], status="NO_VALID_STATE")`.

> **GRACEFUL FALLBACK POLICY (CHỈ DÀNH CHO SOFT PREFERENCE FAILURE):**  
> Cơ chế nới lỏng/fallback (nếu áp dụng) **CHỈ ĐƯỢC PHÉP ÁP DỤNG ĐỐI VỚI SOFT PREFERENCE FAILURE**, hoàn toàn không áp dụng cho Hard Invalid.  
> *Ví dụ:* Một ứng viên `canonical` có chi phí phạt vị trí cao ($C_{\text{placement}}$ lớn) hoặc độ dễ đọc thấp ($C_{\text{legibility}}$ cao), nhưng hoàn toàn thỏa mãn mọi ràng buộc hình học (không xuyên thấu, không NaN, không vượt biên) $\rightarrow$ Vẫn được giữ lại làm một state hợp lệ trong đồ thị để Viterbi cân nhắc đánh đổi (trade-off) toàn cục. Ngược lại, nếu va chạm vượt ngưỡng cắt tỉa cứng $\rightarrow$ bị loại vĩnh viễn, không được fallback.

### 6.3 Thuật toán sinh ứng viên (Pseudocode)

```python
def build_composition_states(
    char_info: Dict[str, Any],
    font_pack: Dict[str, Any],
    config: DiacriticConfig
) -> List[CompositionState]:
    """
    Sinh tập ứng viên CompositionState cho một ký tự tại vị trí xác định.
    Độ phức tạp lý thuyết: O(K_base * K_diacritic) với K_base <= 3, K_diacritic <= 3 (tối đa 9 states thô).
    """
    base_char = char_info["base_char"]
    accents = char_info.get("accents", ())
    context = char_info.get("context", {})
    
    # 1. Lấy danh sách biến thể thân chữ cơ bản
    base_variants: List[GlyphVariant] = get_glyph_variants(
        base_char=base_char,
        raw_strokes=char_info["raw_strokes"],
        context=context
    )
    
    # 2. Xử lý ký tự không dấu (ASCII / no-diacritic)
    if not accents:
        return [
            CompositionState(
                base_variant=bv,
                diacritic_candidate=None,
                base_char=base_char,
                accents=(),
                context=context,
                state_tag=bv.tag,
                internal_collision_cost=0.0,
                legibility_cost=bv.cost_legibility,  # Không cộng placement penalty
                metadata={"index": char_info.get("index", 0)}
            )
            for bv in base_variants
        ]
    
    # 3. Sinh danh sách ứng viên cấu hình dấu
    diacritic_candidates: List[DiacriticCandidate] = generate_diacritic_candidates(
        base_char=base_char,
        accents=accents,
        char_info=char_info,
        font_pack=font_pack,
        config=config
    )
    
    # 4. Tổ hợp tích Descartes và Cắt tỉa bất hợp lệ cứng (Hard Invalid Pruning)
    valid_states: List[CompositionState] = []
    for bv in base_variants:
        for dc in diacritic_candidates:
            # Cắt tỉa cứng 0: Dữ liệu hình học rỗng hoặc chứa giá trị suy biến NaN/Inf
            if not dc.strokes_local or any(np.isnan(s).any() or np.isinf(s).any() for s in dc.strokes_local):
                continue
                
            # Tính toán va chạm nội tại giữa nét dấu và nét thân chữ cục bộ
            # (tolerance_mm là geometry metric dùng phát hiện độ sâu xuyên thấu)
            internal_cost = compute_internal_collision_cost(
                base_strokes_local=bv.strokes,
                diacritic_strokes_local=dc.strokes_local,
                tolerance_mm=config.internal_collision_tolerance_mm
            )
            
            # Cắt tỉa cứng 1: Loại bỏ nếu chi phí va chạm nội tại vượt ngưỡng trần cứng
            if internal_cost > config.max_internal_collision_cost:
                continue
                
            # Cắt tỉa cứng 2: Loại bỏ nếu dấu vượt biên trần dòng chữ hoặc lề trang
            if dc.bounds_local[3] > char_info.get("line_top_bound_local", float("inf")):
                continue
                
            # Tạo CompositionState hợp lệ
            # LƯU Ý BẢO TOÀN: legibility_cost chỉ phản ánh chất lượng thân chữ
            # placement_penalty được lưu trữ độc lập trong dc để tính ở C_state, TRÁNH DOUBLE-COUNT
            state_tag = f"{bv.tag}_{dc.placement_tag}"
            
            valid_states.append(CompositionState(
                base_variant=bv,
                diacritic_candidate=dc,
                base_char=base_char,
                accents=accents,
                context=context,
                state_tag=state_tag,
                internal_collision_cost=internal_cost,
                legibility_cost=bv.cost_legibility,  # Độc lập hoàn toàn với placement penalty
                metadata={"bv_tag": bv.tag, "dc_tag": dc.placement_tag}
            ))
            
    # 5. Xử lý kết quả theo Invariant: Hard constraints MUST NOT be bypassed by fallback.
    # CASE A: Có ít nhất 1 state hợp lệ -> trả về danh sách
    if valid_states:
        return valid_states

    # CASE B: valid_states rỗng do toàn bộ ứng viên vi phạm hard constraints
    # -> Kích hoạt Failure Path tường minh, TUYỆT ĐỐI KHÔNG hồi sinh canonical candidate
    raise NoValidCompositionState(
        f"Không tìm thấy CompositionState hợp lệ cho ký tự '{base_char}' với dấu {accents}. "
        "Toàn bộ ứng viên đã bị loại bỏ bởi Hard Invalid Constraints."
    )
```

---

## 7. Chiến lược Mỏ neo P0 (Anchor Strategy)

Nhằm đảm bảo tính khả thi kỹ thuật và không mở rộng phạm vi không cần thiết:
1. **Không tái cấu trúc toàn bộ Font Pack ở P0:** P0 không yêu cầu số hóa lại toàn bộ tọa độ vector hay bổ sung hệ thống mỏ neo đa điểm phức tạp (`top_anchor`, `bottom_anchor`, `horn_anchor`) cho từng ký tự vào file font. Việc thiết kế hệ thống mỏ neo chi tiết theo từng glyph được định vị là nhiệm vụ mở rộng của **P1**.
2. **Tái sử dụng Geometry hiện tại làm Canonical Source:**
   - Tận dụng bảng tọa độ tâm `font_pack["centers"]` và bảng bù trục `dot_below_x_offsets` hiện có.
   - Thuật toán `generate_accents()` hiện tại của engine được tái sử dụng như một **bộ sinh tọa độ chuẩn mực (Canonical Geometry Provider)**.
3. **Cơ chế dịch chuyển vector cục bộ:**
   - Tọa độ nét dấu canonical: $P_{\text{canonical}} = \text{generate\_canonical\_geometry}(\text{base\_char}, \text{accents}, \dots)$
   - Tọa độ ứng viên lệch:
     $$P_{\text{candidate}}(x, y) = P_{\text{canonical}}(x + \Delta x, y + \Delta y)$$
   - Nhờ đó, việc tích hợp cấu trúc mới ở Bước C hoàn toàn không đòi hỏi sửa đổi các file `font_packs/legacy.py` hay `font_packs/omni_casual.py`.

---

## 8. Kiến trúc Hàm Chi Phí Mới (Cost Architecture)

Để chuẩn hóa thuật ngữ và tránh nhầm lẫn giữa các loại va chạm, hệ thống phân tách rõ rệt 2 nhóm chi phí:

```text
                           HÀM MỤC TIÊU TỔNG THỂ: J_total
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
   State Cost: C_state(s)                                   Transition Cost: J_transition(prev, curr)
   (Lãnh địa TV4 — Ngôn ngữ & Dấu)                           (Lãnh địa TV2 & TV4 Shared — Động học & Nối nét)
        │                                                                 │
        ├── w_4a * C_internal_collision                                   ├── w_1 * D_penup (Quãng đường không tải)
        ├── w_5  * C_legibility                                           ├── w_2 * N_lift (Số lần nhấc bút)
        └── w_6  * C_placement (Phạt lệch tâm chuẩn)                       ├── w_3 * C_curvature (Góc bẻ tiếp tuyến)
                                                                          └── w_4 * C_bridge_collision
                                                                                    (Cầu nối vs Thân & DẤU)
```

### 8.1 State Cost $C_{\text{state}}(s)$ — Lãnh địa TV4
Chi phí nội tại của một node `CompositionState` $s$, độc lập với trạng thái đứng trước nó:

$$C_{\text{state}}(s) = w_{4a} \cdot C_{\text{internal\_collision}}(s) + w_5 \cdot C_{\text{legibility}}(s) + w_6 \cdot C_{\text{placement}}(s)$$

Trong đó các thành phần được định nghĩa rạch ròi, **triệt tiêu hoàn toàn nguy cơ tính trùng (Double-Counting)**:
1. **$C_{\text{internal\_collision}}(s)$:** Đo lường xung đột hình học nội tại giữa các nét thành phần trong cùng một ký tự ở tọa độ cục bộ:
   - Giao cắt hoặc khoảng cách vi phạm giữa nét dấu và nét thân chữ (`diacritic ↔ base_variant`).
   - Giao cắt giữa dấu cấu trúc và dấu thanh (`structural_mark ↔ tone_mark`).
   - Giao cắt giữa dấu và nét phụ của chữ cái (ví dụ: dấu của chữ 'đ' với gạch ngang thân chữ).
2. **$C_{\text{legibility}}(s)$:** Chi phí độ dễ đọc và mức độ tự nhiên của riêng thân chữ cái, lấy trực tiếp từ `s.base_variant.cost_legibility` (không cộng thêm chi phí của dấu).
3. **$C_{\text{placement}}(s)$:** Chi phí phạt độ lệch vị trí chuẩn tắc của dấu, lấy trực tiếp từ `s.diacritic_candidate.placement_penalty` (nếu `diacritic_candidate is None` thì bằng 0):
   $$C_{\text{placement}}(s) = \frac{\sqrt{\Delta x^2 + \Delta y^2}}{\text{config.max\_placement\_shift\_mm}}$$

### 8.1.1 Phân biệt Hình thức: Geometry Metric (Đơn vị vật lý mm) vs. Cost Metric (Vô hướng chuẩn hóa)

Để triệt tiêu lỗi trộn lẫn hoặc so sánh sai đơn vị giữa kích thước vật lý ($\text{mm}$) và hàm chi phí ($J, C$), hệ thống chuẩn hóa hai tầng khái niệm độc lập:

1. **Geometry Metric (Chỉ số hình học — Có đơn vị vật lý $\text{mm}$ hoặc số đếm):**
   - $\text{min\_clearance\_mm}$: Khoảng cách hở Euclide nhỏ nhất giữa hai polyline ($\text{mm}$).
   - $\text{penetration\_depth\_mm}$: Độ sâu xuyên thấu/chồng lấn giữa hai nét khi khoảng cách nhỏ hơn ngưỡng dung sai $\text{tolerance\_mm}$ ($\text{mm}$).
   - $\text{intersection\_count}$: Số điểm giao cắt hình học giữa các đoạn thẳng (số nguyên $\ge 0$).
2. **Cost Metric (Chỉ số chi phí — Vô hướng chuẩn hóa, không thứ nguyên / dimensionless):**
   - $C_{\text{internal\_collision}}$: Chi phí phạt va chạm nội tại vô hướng, được ánh xạ từ các geometry metric qua hàm cost mapping:
     $$\text{Geometry (Polylines)} \xrightarrow{\text{phân tích hình học}} \text{Collision Metrics (mm, count)} \xrightarrow{\text{cost mapping}} C_{\text{internal\_collision}} \in [0.0, 1.0]$$
   - $C_{\text{placement}}$, $C_{\text{legibility}}$: Các giá trị phạt vô hướng không âm ($\ge 0.0$).

> **CRITICAL RULE — KHÔNG SO SÁNH TRỘN ĐƠN VỊ:**  
> Tuyệt đối không so sánh trực tiếp hoặc viết biểu thức lẫn lộn như:  
> `C_internal_collision < internal_collision_tolerance_mm` (SAI — so sánh chi phí vô hướng với milimét).  
> - Khi kiểm tra hình học (Geometry check), bắt buộc dùng metric hình học với ngưỡng hình học:  
>   $\text{min\_clearance\_mm} \ge \text{config.clearance\_threshold\_mm}$  
>   hoặc $\text{penetration\_depth\_mm} \le \text{config.internal\_collision\_tolerance\_mm}$.  
> - Khi kiểm tra chi phí (Cost check), bắt buộc dùng cost metric với ngưỡng chi phí vô hướng:  
>   $C_{\text{internal\_collision}} \le \text{config.max\_internal\_collision\_cost}$.

### 8.2 Transition Cost $J_{\text{transition}}(s_{\text{prev}}, s_{\text{curr}})$ — Shared TV2 & TV4
Chi phí chuyển trạng thái giữa node đứng trước $s_{\text{prev}}$ và node hiện tại $s_{\text{curr}}$:

$$J_{\text{transition}}(s_{\text{prev}}, s_{\text{curr}}) = w_1 \cdot D_{\text{penup}} + w_2 \cdot N_{\text{lift}} + w_3 \cdot C_{\text{curvature}} + w_4 \cdot C_{\text{bridge\_collision}}$$

Trong đó các thành phần chuyển động vật lý do TV2 phụ trách chuẩn hóa:
- $D_{\text{penup}}$: Quãng đường di chuyển đầu bút khi nhấc bút từ điểm thoát của $s_{\text{prev}}$ sang điểm đón của $s_{\text{curr}}$ (mm).
- $N_{\text{lift}}$: Chi phí phạt mỗi lần nhấc/hạ bút.
- $C_{\text{curvature}}$: Độ lệch tiếp tuyến $1 - \cos\theta$ giữa vector thoát và vector đón.

### 8.3 Cải tiến then chốt trong $C_{\text{bridge\_collision}}$ (Transition Bridge Collision)
Khi Viterbi thử nghiệm phương án nối nét (`is_conn == True`), cầu nối Bézier $\mathcal{B}$ (trong hệ tọa độ thế giới) được kiểm tra va chạm với **4 tập hợp nét thế giới**:

$$C_{\text{bridge\_collision}} = \text{cost}\Big(\mathcal{B}_{\text{world}} \longleftrightarrow \mathcal{S}_{\text{check\_world}}\Big)$$

với:
$$\mathcal{S}_{\text{check\_world}} = \mathcal{S}_{\text{prev\_world}}^{\text{base}} \cup \mathcal{S}_{\text{curr\_world}}^{\text{base}} \cup \mathcal{S}_{\text{prev\_world}}^{\text{diacritic}} \cup \mathcal{S}_{\text{curr\_world}}^{\text{diacritic}}$$

**Cơ chế giải quyết xung đột của Viterbi DP:**
Nếu trạng thái $s_{\text{prev}}$ hoặc $s_{\text{curr}}$ đang chọn một ứng viên dấu có vị trí bị cầu nối cắt qua, $C_{\text{bridge\_collision}}$ sẽ tăng vọt (phạt nặng). Thuật toán Viterbi DP sẽ tự động đưa ra một trong hai quyết định tối ưu:
1. **Phương án A (Né dấu):** Giữ nguyên nối nét liền mạch, nhưng chuyển sang chọn một `DiacriticCandidate` an toàn hơn (ví dụ: `safe_left` hoặc `safe_right`) để dấu né khỏi quỹ đạo cầu nối.
2. **Phương án B (Nhấc bút):** Nếu dịch dấu vẫn không an toàn hoặc gây phạt thẩm mỹ lớn, Viterbi sẽ quyết định **nhấc bút (pen-up)** giữa hai chữ cái thay vì ép nối nét gượng gạo.

---

## 9. Phương trình Truy hồi Viterbi DP Mới

Do không gian trạng thái mỗi layer được biểu diễn bằng `CompositionState` thay vì `GlyphVariant`, thuật toán Viterbi DP giữ nguyên tính chất thanh lịch và tối ưu toàn cục:

### 9.1 Khởi tạo (Base Case - Layer 0)
Tại vị trí ký tự đầu tiên của từ ($i = 0$):

$$DP[0, j] = C_{\text{state}}(s[0, j]), \quad \forall j \in \{0, \dots, K'_0 - 1\}$$

### 9.2 Bước truy hồi (Inductive Step - Layer $i$, với $1 \le i < L$)
Với mỗi trạng thái $j$ tại layer $i$:

$$DP[i, j] = C_{\text{state}}(s[i, j]) + \min_{0 \le p < K'_{i-1}} \Big( DP[i-1, p] + J_{\text{transition}}(s[i-1, p], s[i, j]) \Big)$$

Lưu vết chỉ số tối ưu phục vụ hồi quy:
$$\text{Backpointer}[i, j] = \arg\min_{0 \le p < K'_{i-1}} \Big( DP[i-1, p] + J_{\text{transition}}(s[i-1, p], s[i, j]) \Big)$$

### 9.3 Kết thúc và Truy vết (Termination & Backtracking)
Tại ký tự cuối cùng của từ ($i = L - 1$):
$$j^* = \arg\min_{0 \le j < K'_{L-1}} DP[L-1, j]$$

Truy ngược từ $L-1$ về $0$ thông qua ma trận `Backpointer` để thu được chuỗi trạng thái tối ưu:
$$\mathcal{S}^* = \big( s_0^*, s_1^*, \dots, s_{L-1}^* \big)$$

---

## 10. Tái cấu trúc Luồng Render (Renderer Architecture)

Kiến trúc mới giải quyết dứt điểm mâu thuẫn giữa quy hoạch động và kết xuất đồ họa:

```text
HIỆN TẠI (Post-DAG Procedural Attachment):
Trellis DAG ──► Chosen GlyphVariant ──► Post-DAG generate_accents() ──► SVG Path
                     (Chỉ có thân chữ)        (Tự tính vị trí tĩnh)

KIẾN TRÚC MỚI (Diacritic-Integrated Composition):
Trellis DAG ──► Chosen CompositionState ──► transform_state_to_world() ──► SVG Path
                ├── base_variant (Thân chữ)
                └── diacritic_candidate (Dấu đã tối ưu né va chạm)
```

### 10.1 Trách nhiệm của Renderer trong Bước C
1. **Không tự ý tính lại vị trí dấu:** Renderer chỉ nhận đầu vào là chuỗi `CompositionState` tối ưu từ Viterbi DP.
2. **Trích xuất nét trực tiếp qua Transform Helper:**
   - Nét thân chữ được lấy từ `state.base_variant.strokes`.
   - Cầu nối ligature (nếu cờ kết nối bật) được lấy từ kết quả chuyển trạng thái.
   - Nét dấu được lấy trực tiếp từ `state.diacritic_candidate.strokes_local`.
   - Tất cả được biến đổi sang tọa độ thế giới thông qua `transform_state_to_world()`.
3. **Tái cấu trúc hàm `generate_accents()`:**
   - Hàm `generate_accents()` hiện tại **KHÔNG BỊ XÓA BỎ**.
   - Trong Bước C, hàm này sẽ được refactor thành hàm nội bộ phục vụ tầng sinh ứng viên (`generate_canonical_diacritic_geometry()`) để cung cấp hình học gốc cho `build_composition_states()`.

---

## 11. Phân định Phạm vi: Delayed-Stroke Ordering là Nhiệm vụ Độc lập

> **IMPORTANT — NGUYÊN TẮC PHÂN BIỆT BÀI TOÁN "WHERE" VÀ "WHEN":**  
> - **Bài toán "WHERE" (Không gian):** Bố trí dấu ở đâu trong không gian 2D để né va chạm với cầu nối và nét chữ lân cận mà vẫn bảo đảm chính tả, tỷ lệ thẩm mỹ. $\rightarrow$ **ĐÂY LÀ PHẠM VI TRỌNG TÂM CỦA BƯỚC B & BƯỚC C.**  
> - **Bài toán "WHEN" (Thời gian):** Bút vẽ dấu vào thời điểm nào trong chu trình chuyển động của máy vẽ (vẽ ngay sau khi viết xong nguyên âm, hay viết xong toàn bộ thân từ rồi mới quay lại đánh dấu toàn từ). $\rightarrow$ **ĐÂY LÀ BÀI TOÁN LẬP LỊCH NÉT TRỄ (Delayed-Stroke Scheduling).**

**Quyết định thiết kế cho Bước B/C v1:**
1. Bước B và Bước C đầu tiên **chỉ tập trung hoàn thiện bài toán "WHERE"** (tích hợp dấu vào không gian trạng thái DAG và né va chạm hình học).
2. Bài toán "WHEN" (Delayed-Stroke Ordering) được tách riêng thành một mốc nghiên cứu độc lập tiếp nối (**P0-follow-up** do TV2 chủ trì phần tối ưu chuyển động động học phối hợp cùng TV4).
3. `CompositionState` v1 sẽ **không chứa** các trường phức tạp về lập lịch nét trễ ngoài metadata tối thiểu (`stroke_order_hint`), tránh gây phình to phạm vi và bảo đảm tiến độ kiểm thử chắc chắn.

---

## 12. Ma trận Trách nhiệm Module (Ownership Matrix)

Ranh giới kỹ thuật giữa các thành viên được phân định rõ ràng để bảo đảm tính kỷ luật của dự án:

| Thành phần kỹ thuật | Thành viên sở hữu chính | Thành viên phối hợp / Review | Ghi chú ranh giới |
| :--- | :--- | :--- | :--- |
| `DiacriticCandidate` Schema | **TV4** | TV1 | TV4 toàn quyền quyết định cấu trúc mỏ neo và mã NFD. |
| `CompositionState` Schema | **TV4** | TV2 | Nút đồ thị trung tâm của bài toán CA-VHC. |
| Pipeline sinh ứng viên dấu | **TV4** | TV1 | Xử lý cấu trúc chính tả tiếng Việt và mỏ neo. |
| Chi phí tự va chạm nội tại $C_{\text{internal\_collision}}$ | **TV4** | TV2 | Kiểm tra giao cắt hình học giữa dấu và thân chữ. |
| Chi phí thẩm mỹ $C_{\text{placement}}$, $C_{\text{legibility}}$ | **TV4** | TV1 | Đánh giá độ tự nhiên và mức phạt lệch tâm. |
| Chi phí chuyển động ($D_{\text{penup}}, N_{\text{lift}}, C_{\text{curvature}}$) | **TV2** | TV4 | Mô hình hóa động học ngòi bút và chuyển động vật lý máy vẽ. |
| Chi phí cầu nối né dấu $C_{\text{bridge\_collision}}$ | **TV4 & TV2 (Shared)** | Cả nhóm | Mở rộng kiểm tra va chạm cầu nối Bézier với nét dấu. |
| Thuật toán Viterbi DP Runner | **TV4 & TV2 (Shared)** | Cả nhóm | Truy hồi đồ thị Trellis DAG và tối ưu hóa toàn cục. |
| Trích xuất Render SVG từ State | **TV4** | TV2 | Chuyển đổi trạng thái tối ưu thành SVG polylines. |
| Tối ưu thứ tự nét trễ (Delayed-Stroke) | **TV2** | TV4 | Bài toán tối ưu hóa đường đi ngòi bút (P0-follow-up). |

*Quy tắc cộng tác:* Mọi thay đổi đối với interface chung (`eval_transition()`, chữ ký hàm `optimize_word_dag()`) trong Bước C bắt buộc phải được review và chấp thuận chéo giữa TV4 và TV2.

---

## 13. Hợp đồng Tương thích Ngược (Backward Compatibility Contract)

### 13.1 Đối với Văn bản ASCII / Không dấu (Strict Regression Target)
- **Mục tiêu bảo toàn hành vi:** Mọi câu văn, từ ngữ không chứa dấu tiếng Việt khi chạy qua engine mới kỳ vọng cho ra hành vi tương đương về mặt logic kết nối so với engine cũ (Behavior-equivalent target).
- **Tiêu chuẩn nghiệm thu hồi quy:**
  1. Tập ứng viên sinh ra có kích thước tương đương: $K' = K_{\text{base}}$.
  2. Mọi quyết định nối nét (`conns[i] == True/False`) tại các vị trí tương ứng không bị sai lệch ngoài ý muốn.
  3. Tính tất định (Determinism): Cùng một chuỗi ký tự với cùng một giá trị `seed` số nguyên 32-bit phải sinh ra chuỗi biến thể và quỹ đạo nhất quán.
  4. Tuyệt đối không thay đổi mã lỗi Strict Validation (`INPUT_INVALID_FORMAT`, `UNSUPPORTED_FONT`, `INVALID_SEED`...).

### 13.2 Đối với Văn bản Tiếng Việt có dấu (Intentional Geometric Evolution)
- **Đặc tính đầu ra:** Tọa độ nét dấu trong file SVG đầu ra **được phép thay đổi có chủ đích (MAY change by design)** so với engine cũ, bởi vì dấu giờ đây đã được dịch chuyển thông minh để né va chạm thay vì bị ghim cứng ở tọa độ tĩnh.
- **Bảo toàn bắt buộc:**
  1. Bảo toàn đúng bản sắc chữ viết Unicode (không làm mất dấu, không gán nhầm dấu).
  2. Không làm vỡ giới hạn khổ giấy vật lý (`paper_size_mm`).
  3. Tuân thủ định dạng thẻ SVG chuẩn `<path d="..." fill="none"/>`.

---

## 14. Chiến lược Kiểm thử cho Bước C (Test Strategy for Step C)

Kế hoạch kiểm thử được phân tách rạch ròi giữa **Kiểm thử Đơn vị / Hồi quy (Unit & Regression Tests)** bắt buộc cho Bước C và **Bộ Thực nghiệm Đối chuẩn (Benchmark & Ablation Study)** cho giai đoạn sau:

### 14.1 Danh mục Kiểm thử Đơn vị & Hồi quy (Unit & Regression Tests)
Đây là các ca kiểm thử tự động bắt buộc phải đạt 100% pass trước khi nghiệm thu code Bước C:

| STT | Tên ca kiểm thử (Test Case) | Mục tiêu kiểm chứng | Kỳ vọng đầu ra |
| :---: | :--- | :--- | :--- |
| **1** | `test_composition_state_without_accent` | Kiểm tra ký tự không dấu (chữ cái Latinh thường/hoa). | Sinh đúng $K_{\text{base}}$ trạng thái; mọi trạng thái đều có `diacritic_candidate is None`. |
| **2** | `test_acute_accent_candidate_generation` | Kiểm tra nguyên âm mang dấu thanh đơn (á, é, ó). | Sinh đầy đủ 3 ứng viên `canonical`, `safe_left`, `safe_right` với độ lệch $dx$ đọc từ config. |
| **3a**| `test_circumflex_acute_geometry_clearance`| Kiểm tra hình học nguyên âm đôi phức hợp (ế, ố) theo đơn vị mm (Geometry Metric). | Sinh cấu trúc 2 tầng (mũ + sắc) chính xác; khoảng cách an toàn $\text{min\_clearance\_mm} \ge \text{config.clearance\_threshold\_mm}$ (hoặc độ sâu xuyên thấu $\text{penetration\_depth\_mm} \le \text{config.internal\_collision\_tolerance\_mm}$). |
| **3b**| `test_circumflex_acute_internal_collision_cost`| Kiểm tra chi phí phạt va chạm nội tại vô hướng của tổ hợp mũ + sắc (Cost Metric). | Chi phí phạt không âm và thỏa mãn ngưỡng trần cho phép: $C_{\text{internal\_collision}} \le \text{config.max\_internal\_collision\_cost}$. |
| **4** | `test_horn_tone_candidate_generation` | Kiểm tra nguyên âm có móc (ở, ứ). | Đặt dấu thanh lệch chuẩn bên cạnh dấu móc theo đúng thẩm mỹ chữ Việt. |
| **5** | `test_dot_below_candidate_generation` | Kiểm tra dấu nặng (ạ, ệ, ọ). | Chỉ sinh 1 ứng viên canonical duy nhất nằm dưới baseline; $dx = 0, dy = 0$. |
| **6** | `test_bridge_vs_diacritic_collision` | Dựng trường hợp giả lập nét nối đè lên dấu. | Hàm $C_{\text{bridge\_collision}}$ phát hiện giao cắt và trả về chi phí phạt cao. |
| **7** | `test_internal_diacritic_base_collision` | Giả lập dấu bị đặt đè lên đỉnh thân chữ. | Phát hiện vi phạm khoảng cách hở ($\text{penetration\_depth\_mm} > \text{config.internal\_collision\_tolerance\_mm}$) và tính chi phí phạt nội tại $C_{\text{internal\_collision}} > 0$. |
| **8** | `test_candidate_pruning` | Kiểm tra cơ chế cắt tỉa cứng khi candidate vi phạm hard constraints. | Ứng viên vượt ngưỡng $C_{\text{internal\_collision}} > \text{config.max\_internal\_collision\_cost}$ bị loại bỏ chính xác; tuyệt đối không bị hồi sinh bởi fallback. |
| **9** | `test_viterbi_selects_lower_collision_state` | So sánh 2 phương án: canonical (bị cầu nối cắt) vs safe_left (an toàn). | Viterbi DP tự động chọn trạng thái `safe_left` có tổng chi phí $J$ thấp hơn. |
| **10**| `test_ascii_regression_equivalence` | Chạy bộ từ tiếng Anh mẫu ("OmniDraw", "plotter", "vector"). | Các quyết định nối nét tương đương với engine trước khi nâng cấp. |
| **11**| `test_seed_determinism` | Chạy cùng 1 câu tiếng Việt với `seed=42` qua 5 lần lặp. | Toàn bộ danh sách trạng thái và tọa độ SVG hoàn toàn trùng khớp 100%. |
| **12**| `test_complex_vietnamese_words` | Kiểm thử trên tập fixture từ ngữ phức tạp: *"tiếng"*, *"thưởng"*, *"truyền"*, *"khoảnh"*, *"nghiêng"*. | Thuật toán chạy thành công, 0 lỗi crash. *(Lưu ý: Đây là fixture kiểm thử kỹ thuật ban đầu, chưa đại diện toàn bộ kho từ vựng tiếng Việt).* |

### 14.2 Bộ Đo đạc Thực nghiệm Đối chuẩn (Benchmark & Ablation Study — Pha sau)
Các tuyên bố định lượng về hiệu năng sẽ được chứng minh qua benchmark độc lập (không thuộc phạm vi unit test):
- **Tỷ lệ giảm va chạm dấu (Collision Rate Reduction):** Đo đạc trên corpus văn bản chuẩn đối sánh với baseline static renderer.
- **Độ mượt động học và quãng đường pen-up:** Đo đạc qua CSV logging phối hợp cùng TV2.
- **Thời gian thực thi giải thuật (Viterbi solve latency):** Khảo sát phân bố thời gian (ms) trên 100+ câu văn tiếng Việt.

---

## 15. Bản Thiết kế Metrics Nghiên cứu Nội bộ (Research Metrics Schema)

Để phục vụ công tác đo đạc thực nghiệm, viết báo cáo NCKH Chương 4 và phục vụ runner thực nghiệm của TV4, tài liệu thiết kế xác lập schema telemetry nội bộ (**Non-binding research telemetry — Tuyệt đối không thay đổi API contract công khai**):

```python
# Schema đo đạc thực nghiệm nội bộ (Non-binding research telemetry)
RESEARCH_METRICS_SCHEMA = {
    "diacritic_collision_count": int,       # Tổng số trường hợp nét cầu nối cắt qua nét dấu trong từ
    "diacritic_collision_rate": float,      # Tỷ lệ phần trăm ký tự có dấu gặp va chạm hình học
    "min_diacritic_clearance_mm": float,    # Khoảng cách hở nhỏ nhất ghi nhận được giữa dấu và nét liền kề (mm)
    "composition_candidate_count": int,     # Tổng số CompositionState được sinh ra trước khi prune
    "viterbi_state_count": int,             # Số lượng CompositionState tham gia đồ thị Viterbi sau khi prune
    "viterbi_solve_time_ms": float,         # Thời gian giải quy hoạch động Trellis DAG (ms)
    "mean_placement_shift_mm": float,       # Khoảng cách dịch chuyển trung bình của dấu so với vị trí chuẩn (mm)
}
```

Các chỉ số này sẽ được ghi nhận vào file CSV thực nghiệm (`append_experiment_log`) phục vụ phân tích câu hỏi nghiên cứu RQ1 và RQ2.

---

## 16. Bảng Kiểm Tra Tiêu Chí Hoàn Thành Bước B (Definition of Done Checklist)

Bản đặc tả thiết kế Bước B này được nghiệm thu hoàn thành dựa trên việc trả lời đầy đủ và dứt khoát 18 câu hỏi kỹ thuật cốt lõi:

- [x] **1. `GlyphVariant` giữ vai trò gì?** $\rightarrow$ Giữ nguyên bản chất là biến thể hình học của thân chữ cái gốc (base-glyph), kiểm soát các đặc tính tiếp tuyến vào/ra.
- [x] **2. `DiacriticCandidate` chứa gì?** $\rightarrow$ Chứa danh sách combining marks NFD, nhãn vị trí (`placement_tag`), tọa độ nét dấu cục bộ (`strokes_local`), mỏ neo, độ lệch $(dx, dy)$, hộp bao `bounds_local`, vùng cấm `clearance_zone_local` và chi phí phạt vị trí.
- [x] **3. `CompositionState` chứa gì?** $\rightarrow$ Chứa cặp `(base_variant, diacritic_candidate)`, ký tự gốc, mảng accents, metadata ngữ cảnh, nhãn kết hợp, chi phí tự va chạm $C_{\text{internal\_collision}}$ và chi phí thẩm mỹ thân chữ $C_{\text{legibility}}$.
- [x] **4. Candidate generation hoạt động ra sao?** $\rightarrow$ Chạy qua pipeline 4 bước: bóc tách NFD $\rightarrow$ sinh biến thể thân $\rightarrow$ sinh ứng viên dấu $\rightarrow$ tích Descartes có kiểm soát $\rightarrow$ cắt tỉa bất hợp lệ cứng.
- [x] **5. Structural và Tone marks được biểu diễn thế nào?** $\rightarrow$ Dấu cấu trúc là mỏ neo tầng 1, dấu thanh là mỏ neo tầng 2; giữ nguyên dạng các polyline độc lập trong `DiacriticCandidate`, không làm phẳng thành khối liền.
- [x] **6. Anchor source lấy từ đâu trong P0?** $\rightarrow$ Tái sử dụng bảng `centers`, `dot_below_x_offsets` và thuật toán `generate_accents()` hiện tại làm Canonical Geometry Source; ứng viên lệch được sinh qua phép tịnh tiến vector.
- [x] **7. Candidate được prune ra sao?** $\rightarrow$ Chỉ cắt tỉa các ứng viên bất hợp lệ cứng (chi phí tự va chạm nội tại vượt ngưỡng trần config hoặc vi phạm biên an toàn dòng kẻ); không dùng beam pruning ở P0.
- [x] **8. State cost gồm những gì?** $\rightarrow$ $C_{\text{state}} = w_{4a} C_{\text{internal\_collision}} + w_5 C_{\text{legibility}} + w_6 C_{\text{placement}}$, không double-count.
- [x] **9. Transition cost gồm những gì?** $\rightarrow$ $J_{\text{transition}} = w_1 D_{\text{penup}} + w_2 N_{\text{lift}} + w_3 C_{\text{curvature}} + w_4 C_{\text{bridge\_collision}}$.
- [x] **10. Bridge collision kiểm tra dấu thế nào?** $\rightarrow$ Cầu nối Bézier trong hệ tọa độ thế giới được kiểm tra đồng thời với nét thân chữ và nét dấu của cả ký tự đứng trước lẫn ký tự đứng sau.
- [x] **11. Viterbi recurrence mới là gì?** $\rightarrow$ $DP[i, j] = C_{\text{state}}(s[i, j]) + \min_p (DP[i-1, p] + J_{\text{transition}}(s[i-1, p], s[i, j]))$.
- [x] **12. Renderer lấy nét dấu từ đâu?** $\rightarrow$ Trích xuất trực tiếp từ `state.diacritic_candidate.strokes_local` đã được Viterbi chọn tối ưu và biến đổi sang tọa độ thế giới qua `transform_state_to_world()`.
- [x] **13. ASCII regression target là gì?** $\rightarrow$ Kỳ vọng bảo toàn hành vi tương đương về mặt logic kết nối, cùng seed cho ra kết quả nhất quán, không đổi API contract.
- [x] **14. Vietnamese SVG change policy là gì?** $\rightarrow$ Tọa độ nét dấu được phép thay đổi có chủ đích để né va chạm, nhưng bắt buộc bảo toàn bản sắc chữ viết Unicode, kích thước khổ giấy và tính tất định seed.
- [x] **15. Delayed stroke nằm ngoài scope nào?** $\rightarrow$ Nằm ngoài scope Bước B/C v1 (bài toán "WHEN" được tách riêng cho TV2 tối ưu động học ở mốc tiếp theo; Bước B/C v1 tập trung hoàn thiện bài toán "WHERE").
- [x] **16. TV4 và TV2 ownership đã rõ chưa?** $\rightarrow$ Đã phân định rạch ròi qua Ma trận Trách nhiệm Mục 12 (TV4: State & Dấu; TV2: Motion & Transition; Shared: Objective $J$ & Viterbi runner).
- [x] **17. Tests Bước C đã được định nghĩa chưa?** $\rightarrow$ Đã định nghĩa danh mục các ca kiểm thử tự động cụ thể tại Mục 14.1 (phân tách rạch ròi giữa mm-based geometry metric và scalar cost metric).
- [x] **18. Metrics nghiên cứu đã có schema design chưa?** $\rightarrow$ Đã thiết kế schema đo đạc nội bộ gồm 7 trường chỉ số non-binding tại Mục 15.

---

## 17. Trạng thái Phê duyệt & Sẵn sàng cho Bước C (Implementation Readiness)

- **Trạng thái hiện tại:** `DESIGN DRAFT COMPLETED — PENDING TV2/TV4 CROSS-REVIEW`.
- **Điều kiện tiên quyết để sang Bước C (Entry Criteria for Step C):**
  1. TV2 hoàn thành phiên rà soát chéo (cross-review) đối với giao diện `eval_transition()` và các thành phần chi phí động học trong $J_{\text{transition}}$.
  2. TV4 và TV2 ký duyệt thống nhất phương trình Bellman Viterbi DP và các tham số mặc định trong `DiacriticConfig`.
- **Quyết định chuyển bước:**  
  > **READY FOR STEP C:** **NO (PENDING CROSS-REVIEW)**.  
  > Sau khi hoàn tất phiên họp review chéo kỹ thuật giữa TV4 và TV2, trạng thái sẽ được cập nhật thành `✅ BƯỚC B COMPLETE — Ready for Step C`.
