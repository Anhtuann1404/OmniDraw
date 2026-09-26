# OmniDraw — Hợp đồng Giao diện Chuyển tiếp E4 cho PR3

**Trạng thái:** `TV2_CHANGES_REQUIRED — E4 REOPENED FOR CORRECTION`

**Ngày TV2 review:** 2026-09-25

**Owners:** TV4 (Handwriting & CA-VHC Composition Lead) và TV2 (Stroke Optimization & Path Planning Lead)

**Phạm vi:** Hợp đồng giao diện kỹ thuật nội bộ của CA-VHC PR3; không làm thay đổi public API, renderer hiện hành hoặc các baseline B1/B2/B3.

> [!IMPORTANT]
> TV2 đã review lại contract trên commit tích hợp `7d1c1d3b7388ce3ff76dd823c19bd8607f994d19` và xác nhận `PASS_WITH_CHANGES`. E4 chưa được đóng lại cho đến khi TV4 xử lý các điều kiện bắt buộc ở Mục 3.1 và TV2 recheck. Review này không tự khôi phục phần triển khai PR3 đã bị revert.

---

## 1. Bằng chứng nền và nguồn ưu tiên

- PR2 B1/B2/B3 đã merge qua PR #32 (commit `bcc1a7a`) với `backend/handwriting/baselines.py`, runner method tags, `tests/test_ca_vhc_baselines.py`. Toàn bộ test suite tự động đạt **136/136 passed**.
- `backend/handwriting/engine.py:eval_transition()` hiện nhận hai `GlyphVariant`, các điểm/tangent và nét chính ở world frame; trả `(total_cost, is_conn)`. Hàm cộng `weights[4] * w.cost_legibility` vào cả lựa chọn nối và nhấc bút. `optimize_word_dag()` cộng legibility của state đầu tại layer 0.
- [`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md) khóa công thức $C_{state} = C_{internal\_collision} + C_{legibility} + C_{placement}$ và $J_{transition} = \min(J_{conn}, J_{lift})$, tuyệt đối không double-count. [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md) là nguồn chuẩn Entry/Exit Gate.
- Phiếu cross-review Chương 1–3 của cả 3 thành viên (TV1, TV2, TV3) đều đã được ký `PASS` và đóng `CLOSED`.

---

## 2. Đặc tả Hợp đồng Kỹ thuật E4 (đang sửa theo TV2 review)

### 2.1. Cấu trúc dữ liệu và Chữ ký Callable

Bảo toàn nguyên trạng `eval_transition()` và `optimize_word_dag()` hiện hành trong `backend/handwriting/engine.py` phục vụ B3/default. Đối với PR3, toàn bộ kiểu dữ liệu và hàm đánh giá chuyển tiếp giữa hai `CompositionState` được định vị tại module mới `backend/handwriting/composition.py`:

```python
from dataclasses import dataclass
from typing import Literal, Optional, Tuple
import numpy as np

CONTRACT_VERSION = "e4-v1"

@dataclass(frozen=True)
class TransitionWeights:
    """Trọng số động học cho hàm chi phí chuyển tiếp J_transition."""
    w_penup: float = 0.5            # w1: Quãng đường di chuyển không vẽ
    w_lift: float = 4.0             # w2: Chi phí phạt nhấc bút
    w_curvature: float = 2.0        # w3: Chi phí phạt đổi hướng tiếp tuyến
    w_bridge_collision: float = 15.0 # w4: Chi phí phạt va chạm bridge–diacritic / bridge–glyph

@dataclass(frozen=True)
class TransitionCostBreakdown:
    """Bóc tách chi tiết các thành phần chi phí chuyển tiếp."""
    d_penup_mm: float
    n_lift: int
    c_curvature: float
    c_bridge_collision: float
    total_cost: float

@dataclass(frozen=True)
class TransitionResult:
    """Kết quả đánh giá chuyển tiếp giữa 2 CompositionState."""
    contract_version: str                                # luôn bằng CONTRACT_VERSION
    is_valid: bool                                       # False nếu vi phạm hard constraint
    decision: Literal["CONNECT", "LIFT", "REJECT"]
    total_cost: float                                    # min(J_conn, J_lift) hoặc +inf
    breakdown: Optional[TransitionCostBreakdown]         # None khi decision == "REJECT"
    reject_reason: Optional[str] = None                  # bắt buộc khi decision == "REJECT"
    bridge_strokes: Optional[Tuple[np.ndarray, ...]] = None
```

`bridge_strokes` chứa defensive copies trong world frame; mỗi array phải được đánh dấu read-only trước khi đóng gói. `frozen=True` chỉ khóa phép gán field, không tự làm `np.ndarray` bất biến. `TransitionWeights` và `TransitionCostBreakdown` chỉ chứa scalar hữu hạn, không âm và được validate tại boundary.

Invariant của `TransitionResult`:

- Với `decision` là `CONNECT` hoặc `LIFT`: `is_valid=True`, `total_cost` hữu hạn/không âm, `breakdown` bắt buộc khác `None`, mọi scalar trong breakdown hữu hạn/không âm và `reject_reason=None`.
- Với `decision="REJECT"`: `is_valid=False`, `total_cost=+inf`, `breakdown=None`, `bridge_strokes=None` và `reject_reason` bắt buộc là mã không rỗng. Không tạo breakdown giả chứa `+inf`.
- NaN/Inf phát sinh do lỗi tính toán không tạo `TransitionResult`; evaluator raise `TransitionEvaluationError`.

Chữ ký hàm chuyển tiếp chính thức:

```python
def evaluate_composition_transition(
    prev_state: CompositionState,
    curr_state: CompositionState,
    prev_world: GlyphWorldGeometry,
    curr_world: GlyphWorldGeometry,
    transition_weights: TransitionWeights,
    diacritic_config: DiacriticConfig,
) -> TransitionResult:
    """
    Đánh giá chi phí chuyển tiếp J_transition(prev, curr) giữa hai node CompositionState.
    - Nhánh LIFT: J_lift = w1 * D_penup + w2 * N_lift.
    - Nhánh CONNECT: J_conn = w3 * C_curvature + w4 * C_bridge_collision.
    - Cắt tỉa cứng (Hard reject): Gán J_conn = +inf nếu vi phạm hard clearance hoặc giao cắt dấu.
    - Kết quả: Chọn min(J_conn, J_lift); nếu cả hai không hợp lệ -> REJECT (+inf).
    - NaN/Inf do lỗi tính toán không được chuyển thành REJECT; raise TransitionEvaluationError.
    """
```

### 2.2. Quy ước Hệ Tọa độ và Biến đổi Hình học

1. **Hệ tọa độ Cục bộ (Glyph-local units):**
   - Tọa độ nét chữ và mỏ neo trong Font Pack là đơn vị glyph-local.
   - `DiacriticCandidate.strokes_local` và `bounds_local` nằm hoàn toàn trong hệ tọa độ cục bộ này.
2. **Hệ tọa độ Thực tế (World coordinates in mm):**
   - Đơn vị tọa độ world là **milimét (mm)** trên mặt giấy thực tế.
   - Một phép biến đổi affine duy nhất theo từng ký tự:
     $$\mathbf{p}_{world} = \mathbf{p}_{local} \odot \mathbf{scale\_vec} + \mathbf{offset}$$
   - Biến đổi tiếp tuyến (tangent):
     $$\mathbf{t}_{world} = \frac{\mathbf{t}_{local} \odot \mathbf{scale\_vec}}{\|\mathbf{t}_{local} \odot \mathbf{scale\_vec}\|}$$
   - Nếu vector sau transform có norm bằng 0 hoặc chứa NaN/Inf, geometry bị xem là malformed và transition evaluator phải fail closed bằng `TransitionEvaluationError`; không thay bằng tangent mặc định.
3. **Độ dịch Ứng viên Dấu (`dx_candidates_mm`, `dy_candidates_mm`):**
   - Nhằm bảo đảm tính bất biến vật lý (khoảng hở $0.3\,\text{mm}$ hay $0.5\,\text{mm}$ luôn chính xác trên giấy bất kể cỡ chữ), độ dịch ứng viên được áp dụng trực tiếp trong hệ tọa độ world:
     $$\mathbf{p}_{diacritic\_world} = (\mathbf{p}_{diacritic\_local} \odot \mathbf{scale\_vec}) + \mathbf{offset} + [\Delta x_{mm}, \Delta y_{mm}]$$
4. **Kiểm tra va chạm Bridge:**
   - Dựng đường nối `candidate_br` trong world frame từ `p_exit_world`, `v_exit_world`, `p_entry_world`, `v_entry_world`.
   - Kiểm tra va chạm với cả 4 tập nét ở world frame: thân chữ trước, cụm dấu trước, thân chữ sau, và cụm dấu sau.
   - Kết quả polyline của bridge được lưu trực tiếp vào `TransitionResult.bridge_strokes` để renderer tái sử dụng chính xác, triệt tiêu sai lệch giữa bước giải DP và bước xuất SVG.

### 2.3. Bóc tách Chi phí & Nguyên tắc Chống Tính Trùng (Zero Double-Count)

1. **Chi phí Trạng thái $C_{state}(s)$ (TV4 sở hữu):**
   $$C_{state}(s) = C_{internal\_collision}(s) + w_{legibility} \cdot \text{cost\_legibility}(s) + C_{placement}(s)$$
   - Chỉ tính toán trên nội tại của một `CompositionState` (va chạm thân–dấu nội tại, legibility của biến thể glyph, và mức phạt lệch vị trí canonical của dấu).
   - Ký tự không dấu có $C_{internal\_collision} = 0$, $C_{placement} = 0$.
2. **Chi phí Chuyển tiếp $J_{transition}(s', s)$ (TV2/TV4 đồng thiết kế):**
   $$J_{transition}(s', s) = \min\bigl(J_{conn}(s', s), J_{lift}(s', s)\bigr)$$
   - Nhánh `LIFT`: $J_{lift} = w_1 D_{penup} + w_2 N_{lift}$ (trong đó $N_{lift} = 1$).
   - Nhánh `CONNECT`: $J_{conn} = w_3 C_{curvature} + w_4 C_{bridge\_collision}$ (nếu vi phạm hard collision thì $J_{conn} = +\infty$).
   - **Xóa bỏ `cost_legibility` khỏi $J_{transition}$:** Khác với `eval_transition()` cũ cộng `w5 * w.cost_legibility`, PR3 chuyển hoàn toàn legibility sang $C_{state}$. $J_{transition}$ chỉ thuần túy đo đạc chi phí chuyển động giữa hai ký tự.
3. **Cơ chế Cắt tỉa Cứng (Fail-closed Hard Pruning):**
   - Hard constraint đã biết được biểu diễn bằng `decision="REJECT"`, `is_valid=False`, `total_cost=+inf`, `breakdown=None`, `bridge_strokes=None` và `reject_reason` có mã ổn định. Đây là trường hợp duy nhất `+inf` được phép xuất hiện trong `TransitionResult`.
   - Cost âm, NaN/Inf do phép tính, geometry sai shape và tangent suy biến là lỗi đánh giá; raise `TransitionEvaluationError` và giữ cause, không giả thành một cạnh `REJECT` bình thường.
   - Nếu toàn bộ các cạnh đến một layer đều bị REJECT ($+\infty$), thuật toán Viterbi DP kích hoạt cơ chế fail-closed trả ngoại lệ `NoValidPathError` thay vì xuất SVG lỗi.

### 2.4. Điều kiện ký E4 và nghiệm thu code PR3

E4 chỉ khóa **interface, semantics, đơn vị, ownership và test plan**. Đóng E4 không yêu cầu code PR3 hoặc toàn bộ test nghiệm thu implementation đã tồn tại/chạy PASS. Sau khi E4 được hai owner ký lại, PR3 mới được phép triển khai theo slice.

Các test B3/ASCII parity, no-double-count, immutable bridge geometry, anisotropic transform, invalid geometry và `NoValidPathError` là **PR3 implementation/exit criteria**. Test contract phải kiểm tra thêm: `CONNECT`/`LIFT` luôn có breakdown hữu hạn; `REJECT` luôn có `breakdown=None`, `bridge_strokes=None` và `total_cost=+inf`; lỗi tính toán phải raise thay vì bị đổi thành `REJECT`. Trước khi đóng E4, TV2 và TV4 chỉ cần duyệt tên test, assertion bắt buộc và owner; kết quả thực thi chỉ được ghi khi code tương ứng tồn tại.

---

## 3. Nghị quyết Chính thức cho 7 Câu hỏi Giao diện

| STT | Câu hỏi giao diện | Quyết định đã khóa | Lý do kỹ thuật & Ranh giới |
| :---: | :--- | :--- | :--- |
| **Q1** | Symbol và module chính thức của PR3 transition? | Hàm `evaluate_composition_transition()` đặt trong module mới `backend/handwriting/composition.py`. | Giữ nguyên `eval_transition()` hiện hành trong `engine.py`; E4 khóa test plan bảo toàn B3/ASCII, còn kết quả test thuộc nghiệm thu implementation PR3. |
| **Q2** | `TransitionResult` lưu bridge geometry trực tiếp hay dựng lại? | Lưu defensive copies dưới dạng `bridge_strokes: Optional[Tuple[np.ndarray, ...]]`; arrays được đặt read-only trước khi trả kết quả. | Bảo đảm hình học được đánh giá chính là hình học được vẽ và không bị mutation sau khi DP chấm cost. |
| **Q3** | Di chuyển `cost_legibility` như thế nào để tránh double-count? | Chuyển trọn vẹn vào $C_{state}(s)$. Bãi bỏ hoàn toàn số hạng $w_5 \cdot cost\_legibility$ trong `evaluate_composition_transition()`. | Tuân thủ nghiêm ngặt công thức toán học tại Docs 07 và Chương 3; B3 cũ vẫn giữ đường chạy riêng nên không bị lệch điểm. |
| **Q4** | Quy ước hệ tọa độ và chuẩn hóa tiếp tuyến? | Local là `glyph-local units`; World là `mm`. Điểm: $\mathbf{p}_w = \mathbf{p}_l \odot \mathbf{scale\_vec} + \mathbf{offset}$. Tiếp tuyến: $\mathbf{t}_w = \text{normalize}(\mathbf{t}_l \odot \mathbf{scale\_vec})$. | Hỗ trợ co giãn không đều X/Y; tangent zero-norm hoặc không hữu hạn gây `TransitionEvaluationError`, không dùng fallback vector. |
| **Q5** | Biểu diễn cạnh chuyển tiếp không hợp lệ? | Hard constraint: `REJECT` + `is_valid=False` + `total_cost=+inf` + `breakdown=None` + `bridge_strokes=None` + `reject_reason`. Lỗi tính toán: raise `TransitionEvaluationError`. | Breakdown chỉ tồn tại cho `CONNECT`/`LIFT` và chỉ chứa scalar hữu hạn; Viterbi bỏ cạnh `REJECT`; nếu không còn đường đi hợp lệ thì runner raise `NoValidPathError` và renderer/API chuyển thành lỗi có cấu trúc. |
| **Q6** | Cấu trúc dữ liệu Cost breakdown & Weights? | Dùng frozen dataclass scalar, khóa `CONTRACT_VERSION="e4-v1"`, tên/đơn vị/thứ tự breakdown và defaults `0.5/4.0/2.0/15.0`. | Defaults là tham số kỹ thuật ban đầu, không phải kết quả thực nghiệm; mọi trọng số phải hữu hạn và không âm. |
| **Q7** | Đơn vị độ dịch ứng viên dấu `dx_candidates_mm`? | Áp dụng trực tiếp trong hệ tọa độ world (mm) sau khi thân chữ đã biến đổi. | Bảo đảm bước dịch kiểm tra khoảng hở an toàn ($0.3\,\text{mm}$, $0.5\,\text{mm}$) luôn bất biến theo kích thước vật lý của ngòi bút trên giấy, không bị co giãn theo font size. |

### 3.1. Phản hồi chính thức của TV2

| Câu hỏi | Ý kiến TV2 | Điều kiện bắt buộc trước khi E4 đóng lại |
| :---: | :--- | :--- |
| **Q1 — Interface PR3** | Đồng ý dùng `backend/handwriting/composition.py::evaluate_composition_transition()` và giữ nguyên `engine.eval_transition()` cho B3/default. | E4 khóa test plan B3/ASCII parity; test phải PASS tại PR3 exit gate, không phải điều kiện phải có implementation trước E4. |
| **Q2 — Bridge geometry** | Đồng ý lưu geometry bridge đã được đánh giá để renderer dùng lại, không dựng lại lần hai. | Contract đã đổi sang tuple của defensive copy/read-only arrays; PR3 phải có mutation test tại exit gate. |
| **Q3 — `cost_legibility`** | Đồng ý chuyển toàn bộ legibility của PR3 vào `C_state`; `J_transition` mới không cộng lại khoản này. | Giữ đường B3 cũ riêng và có test no-double-count cho state đầu, state tiếp theo, nhánh `CONNECT` và nhánh `LIFT`. |
| **Q4 — Tọa độ** | Đồng ý local là glyph units, world là mm; điểm dùng `scale_vec`/`offset`, tangent transform theo `scale_vec` rồi normalize. | Contract đã khóa `TransitionEvaluationError` cho tangent zero-norm/không hữu hạn; anisotropic test thuộc PR3 exit gate. |
| **Q5 — Cạnh không hợp lệ** | Đồng ý dùng `REJECT/+inf/breakdown=None/reject_reason` cho hard constraint; lỗi tính toán raise `TransitionEvaluationError`; hết đường đi raise `NoValidPathError` tại runner. | Renderer/API phải chuyển lỗi runner thành lỗi có cấu trúc; implementation test phải phân biệt invariant của `CONNECT`/`LIFT`, `REJECT` và computational error tại PR3 exit gate. |
| **Q6 — Cost/config** | Đồng ý dùng frozen dataclass scalar; defaults `0.5/4.0/2.0/15.0` chỉ là tham số kỹ thuật ban đầu. | Contract đã thêm `CONTRACT_VERSION="e4-v1"`, validation finite/non-negative và ranh giới immutability. |

TV2 đồng ý Q7 theo quyết định hiện tại: độ dịch mang đơn vị mm được áp dụng đúng một lần trong world frame, kèm test scale X/Y không đều.

---

## 4. Phê duyệt & Ký duyệt Entry Gate E4

| Vai trò | Người xác nhận | Quyết định | Bằng chứng kiểm chứng |
| :--- | :--- | :---: | :--- |
| **TV2 — Stroke Optimization & Path Planning Lead** | Khải (TV2) | **CHANGES_REQUIRED** | `PASS_WITH_CHANGES`; đã trả lời Q1–Q7. Các điều kiện về immutability, zero-tangent, sentinel/error semantics, contract version và ranh giới test plan đã được đưa vào bản contract này; chờ TV4 recheck và hai owner đồng thuận trước khi đóng E4. |
| **TV4 — Handwriting & CA-VHC Composition Lead** | Tuấn (TV4) | **PENDING_RECHECK** | `APPROVED` ngày 2026-09-24 chỉ áp dụng cho bản E4 cũ đã bị mở lại; đó là bản ghi lịch sử, không phải chữ ký cho contract hiện hành. TV4 chưa ký lại bản có các correction mới. |

- **TV2 verdict:** **`PASS_WITH_CHANGES`**
- **TV2_APPROVAL:** **`CHANGES_REQUIRED`**
- **TV2 reviewer:** **Khải (TV2)**
- **Ngày xác nhận:** **2026-09-25**
- **Commit đã review:** **`7d1c1d3b7388ce3ff76dd823c19bd8607f994d19`**
- **Entry Gate E4 Verdict:** **`REOPENED — WAITING_TV4_CHANGES_AND_TV2_RECHECK`**
- **Trạng thái PR3 trên nhánh tích hợp:** **`IMPLEMENTATION_REVERTED`**

```text
===================================================================
ENTRY GATE E4: REOPENED — CHANGES REQUIRED
PR3 SOFTWARE IMPLEMENTATION: NOT RE-AUTHORIZED BY THIS REVIEW
===================================================================
```
