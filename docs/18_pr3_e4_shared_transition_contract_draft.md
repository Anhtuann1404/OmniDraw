# OmniDraw — Hợp đồng Giao diện Chuyển tiếp E4 cho PR3

**Trạng thái:** `APPROVED — SHARED TRANSITION CONTRACT LOCKED`

**Ngày ký duyệt:** 2026-09-24

**Owners phê duyệt:** TV4 (Handwriting & CA-VHC Composition Lead) và TV2 (Stroke Optimization & Path Planning Lead)

**Phạm vi:** Hợp đồng giao diện kỹ thuật nội bộ của CA-VHC PR3; không làm thay đổi public API, renderer hiện hành hoặc các baseline B1/B2/B3.

> [!IMPORTANT]
> Hợp đồng này chính thức khép lại Entry Gate E4. Quyết định kỹ thuật giữa TV2 và TV4 đã được chốt toàn diện; mã nguồn PR3 (`CompositionState` và Diacritic-Aware Trellis DAG) chính thức được phép bắt đầu theo Slice 0–6 của [`17_pr3_implementation_readiness.md`](17_pr3_implementation_readiness.md).

---

## 1. Bằng chứng nền và nguồn ưu tiên

- PR2 B1/B2/B3 đã merge qua PR #32 (commit `bcc1a7a`) với `backend/handwriting/baselines.py`, runner method tags, `tests/test_ca_vhc_baselines.py`. Toàn bộ test suite tự động đạt **136/136 passed**.
- `backend/handwriting/engine.py:eval_transition()` hiện nhận hai `GlyphVariant`, các điểm/tangent và nét chính ở world frame; trả `(total_cost, is_conn)`. Hàm cộng `weights[4] * w.cost_legibility` vào cả lựa chọn nối và nhấc bút. `optimize_word_dag()` cộng legibility của state đầu tại layer 0.
- [`07_diacritic_aware_state_design.md`](07_diacritic_aware_state_design.md) khóa công thức $C_{state} = C_{internal\_collision} + C_{legibility} + C_{placement}$ và $J_{transition} = \min(J_{conn}, J_{lift})$, tuyệt đối không double-count. [`09_pr3_acceptance_criteria.md`](09_pr3_acceptance_criteria.md) là nguồn chuẩn Entry/Exit Gate.
- Phiếu cross-review Chương 1–3 của cả 3 thành viên (TV1, TV2, TV3) đều đã được ký `PASS` và đóng `CLOSED`.

---

## 2. Đặc tả Hợp đồng Kỹ thuật E4 (Đã phê duyệt)

### 2.1. Cấu trúc dữ liệu và Chữ ký Callable

Bảo toàn nguyên trạng `eval_transition()` và `optimize_word_dag()` hiện hành trong `backend/handwriting/engine.py` phục vụ B3/default. Đối với PR3, toàn bộ kiểu dữ liệu và hàm đánh giá chuyển tiếp giữa hai `CompositionState` được định vị tại module mới `backend/handwriting/composition.py`:

```python
from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np

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
    is_valid: bool                                       # False nếu vi phạm hard constraint
    decision: str                                        # "CONNECT" | "LIFT" | "REJECT"
    total_cost: float                                    # min(J_conn, J_lift) hoặc +inf
    breakdown: TransitionCostBreakdown
    bridge_strokes: Optional[List[np.ndarray]] = None    # Polylines trong world frame (nếu CONNECT)
```

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
   - Mọi candidate hoặc transition có cost âm, NaN, hoặc Inf đều bị từ chối tường minh.
   - Nếu toàn bộ các cạnh đến một layer đều bị REJECT ($+\infty$), thuật toán Viterbi DP kích hoạt cơ chế fail-closed trả ngoại lệ `NoValidPathError` thay vì xuất SVG lỗi.

---

## 3. Nghị quyết Chính thức cho 7 Câu hỏi Giao diện

| STT | Câu hỏi giao diện | Quyết định đã khóa | Lý do kỹ thuật & Ranh giới |
| :---: | :--- | :--- | :--- |
| **Q1** | Symbol và module chính thức của PR3 transition? | Hàm `evaluate_composition_transition()` đặt trong module mới `backend/handwriting/composition.py`. | Giữ nguyên `eval_transition()` hiện hành trong `engine.py` để bảo đảm B3 adapter và 48/48 ASCII baseline fingerprints không bị ảnh hưởng. |
| **Q2** | `TransitionResult` lưu bridge geometry trực tiếp hay dựng lại? | Lưu trực tiếp `bridge_strokes: Optional[List[np.ndarray]]` trong `TransitionResult`. | Bảo đảm 100% nguyên tắc "hình học được đánh giá chính là hình học được vẽ", loại bỏ rủi ro sai lệch do tham số làm mịn khi renderer dựng lại. |
| **Q3** | Di chuyển `cost_legibility` như thế nào để tránh double-count? | Chuyển trọn vẹn vào $C_{state}(s)$. Bãi bỏ hoàn toàn số hạng $w_5 \cdot cost\_legibility$ trong `evaluate_composition_transition()`. | Tuân thủ nghiêm ngặt công thức toán học tại Docs 07 và Chương 3; B3 cũ vẫn giữ đường chạy riêng nên không bị lệch điểm. |
| **Q4** | Quy ước hệ tọa độ và chuẩn hóa tiếp tuyến? | Local là `glyph-local units`; World là `mm`. Điểm: $\mathbf{p}_w = \mathbf{p}_l \odot \mathbf{scale\_vec} + \mathbf{offset}$. Tiếp tuyến: $\mathbf{t}_w = \text{normalize}(\mathbf{t}_l \odot \mathbf{scale\_vec})$. | Hỗ trợ co giãn không đều X/Y (`scale_vec`), chuẩn hóa tiếp tuyến chính xác trong không gian giấy thực tế; bãi bỏ giả định scalar `scale` trong Docs 07. |
| **Q5** | Biểu diễn cạnh chuyển tiếp không hợp lệ? | Trả `TransitionResult(is_valid=False, total_cost=float('inf'), decision="REJECT")`. | Viterbi DP tự nhiên bỏ qua các cạnh có chi phí $+\infty$. Nếu không tìm thấy đường đi hợp lệ qua cả từ, fail-closed với `NoValidPathError`. |
| **Q6** | Cấu trúc dữ liệu Cost breakdown & Weights? | Khóa hai dataclass bất biến: `TransitionWeights(frozen=True)` và `TransitionCostBreakdown(frozen=True)`. | Tránh lỗi đột biến dữ liệu ngoài ý muốn (mutation) và hỗ trợ trích xuất metric phục vụ logging CSV 19 cột. |
| **Q7** | Đơn vị độ dịch ứng viên dấu `dx_candidates_mm`? | Áp dụng trực tiếp trong hệ tọa độ world (mm) sau khi thân chữ đã biến đổi. | Bảo đảm bước dịch kiểm tra khoảng hở an toàn ($0.3\,\text{mm}$, $0.5\,\text{mm}$) luôn bất biến theo kích thước vật lý của ngòi bút trên giấy, không bị co giãn theo font size. |

---

## 4. Phê duyệt & Ký duyệt Entry Gate E4

| Vai trò | Người xác nhận | Quyết định | Bằng chứng kiểm chứng |
| :--- | :--- | :---: | :--- |
| **TV2 — Stroke Optimization & Path Planning Lead** | Khải (TV2) | **APPROVED** | Đã xác nhận phân tách $J_{conn}$/$J_{lift}$, công thức $C_{curvature}$, ngưỡng góc $120^\circ$, và cấu trúc `TransitionWeights`/`TransitionCostBreakdown`. |
| **TV4 — Handwriting & CA-VHC Composition Lead** | Tuấn (TV4) | **APPROVED** | Đã xác nhận cấu trúc `CompositionState`, di chuyển legibility sang $C_{state}$, affine transform `scale_vec`, bảo toàn B3 parity và 136/136 unit tests. |

- **Entry Gate E4 Verdict:** **`PASS`**
- **Trạng thái PR3:** **`READY_TO_IMPLEMENT`**
- **Quyền bắt đầu Slice 0:** **CHÍNH THỨC ĐƯỢC CẤP PHÉP (AUTHORIZED)**

```text
===================================================================
ENTRY GATE E4: APPROVED AND CLOSED
PR3 SOFTWARE IMPLEMENTATION: AUTHORIZED (READY FOR SLICE 0)
===================================================================
```
