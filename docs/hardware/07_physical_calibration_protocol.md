# Giao thức Kiểm chuẩn & Thực nghiệm Vật lý Máy vẽ (Physical Calibration Protocol)

**Vai trò chủ trì:** TV3 — Hardware, Calibration & Physical Validation Lead  
**Mục tiêu học thuật:** Phục vụ câu hỏi nghiên cứu **RQ3** (Physical Feasibility & Diacritic Clearance) và nghiệm thu phần cứng  
**Mã tài liệu:** `docs/hardware/07_physical_calibration_protocol.md`  
**Phiên bản:** v1.0 (2026-09-24)  
**Trạng thái:** ACTIVE BASELINE PROTOCOL / READY FOR HARDWARE BENCH  

---

## 1. Mục đích & Phạm vi

Tài liệu này quy chuẩn hóa quy trình thực nghiệm, phương pháp đo đạc và điều kiện nghiệm thu thực tế trên máy vẽ vật lý (AxiDraw / OmniDraw Plotter V1) nhằm giải quyết câu hỏi nghiên cứu **RQ3**:
> *"Việc áp dụng giải thuật CA-VHC có đảm bảo khả năng thi công vật lý trên máy vẽ hay không; khoảng hở hình học bao nhiêu là đủ để ngăn ngừa dính nét do loang mực (`ink bleed`), và thời gian mô phỏng sai lệch bao nhiêu phần trăm so với thời gian vẽ thực tế (`actual_draw_time_sec`)?"*

Giao thức này là cơ sở duy nhất để chuyển trạng thái từ `PENDING_TV3_CALIBRATION` sang `PASS_TV3_CALIBRATION` trong toàn bộ tài liệu nghiên cứu (Docs 10, Chương 1 và Chương 3).

---

## 2. Chuẩn hóa Vật tư & Thiết bị Thực nghiệm

Để đảm bảo tính tái lập (reproducibility) của các phép đo vật lý, mọi lượt chạy thực nghiệm phải tuân thủ nghiêm ngặt danh mục vật tư sau:

| Hạng mục | Quy chuẩn kỹ thuật | Mục đích / Ràng buộc |
| :--- | :--- | :--- |
| **Giấy vẽ tiêu chuẩn** | Giấy in A4 Double A định lượng $80\,\text{g/m}^2$, bề mặt láng mịn, độ ẩm bảo quản $50 \pm 10\%$ | Đảm bảo độ thấm hút mực đồng đều, khống chế hiện tượng mao dẫn giấy. |
| **Bút vẽ tiêu chuẩn** | Bút bi mực gel Pentel EnerGel $0.5\,\text{mm}$ (màu đen) hoặc Pilot G2 $0.5\,\text{mm}$ | Ngòi bi lăn chuẩn, lưu lượng mực ổn định; đường kính bi $0.5\,\text{mm}$. |
| **Góc gá đặt bút** | $90.0^\circ \pm 1.0^\circ$ so với mặt phẳng giấy (thẳng đứng) | Triệt tiêu sai số phi đối xứng khi di chuyển theo các hướng X/Y. |
| **Lực tì ngòi bút (Pen Pressure)** | $50 - 80\,\text{gf}$ ($\approx 0.49 - 0.78\,\text{N}$) | Duy trì độ đậm nét mà không làm cào xước mặt giấy hay kẹt bi. |
| **Thiết bị đo quang học** | Máy quét phẳng (Flatbed Scanner) quang học độ phân giải thực $600\,\text{DPI}$ (True scale 1:1, Lossless PNG) | Đo đạc độ rộng nét mực khô và khoảng hở thực tế qua điểm ảnh ($1\text{ px} \approx 0.0423\,\text{mm}$). |
| **Thiết bị đo cơ khí** | Thước kẹp điện tử Mitutoyo độ phân giải $0.01\,\text{mm}$ | Kiểm chứng kích thước hành trình cơ khí thô. |

---

## 3. Cấu trúc Tiêu bản Kiểm chuẩn RQ3 (`rq3_clearance_calibration_specimen.svg`)

Tiêu bản kiểm chuẩn được thiết kế trên khổ A4 ngang ($297 \times 210\,\text{mm}$) bao gồm 4 khối kiểm tra độc lập:

### 3.1. Khối A: Thang kiểm tra khoảng hở nét & loang mực (Clearance Test Ladder)
- **Cấu trúc:** 7 cặp đường song song và cặp bridge-dấu tượng trưng với khoảng hở CAD danh định ($d_{CAD}$):
  $$d_{CAD} \in \{0.10\,\text{mm}, 0.20\,\text{mm}, 0.30\,\text{mm}, 0.40\,\text{mm}, 0.50\,\text{mm}, 0.60\,\text{mm}, 0.70\,\text{mm}\}$$
- **Mục tiêu:** 
  1. Xác định bề rộng nét mực thực tế ($w_{ink}$) trên giấy.
  2. Xác định khoảng hở thực nghiệm $d_{actual} = d_{CAD} - w_{ink}$.
  3. Tìm ngưỡng chuyển tiếp mà tại đó mực dính liền thành một mảng ($d_{actual} \le 0$).

### 3.2. Khối B: Kiểm tra rung giật góc cua nhọn (Kinematic Turn & Acute Angle Test)
- **Cấu trúc:** Các đường zig-zag tạo góc bẻ hướng tiếp tuyến:
  $$\theta_{turn} \in \{60^\circ, 90^\circ, 120^\circ, 150^\circ\}$$
- **Mục tiêu:** 
  1. Đánh giá độ nảy ngòi bút và hiện tượng văng mực tại góc cua gắt.
  2. Đo độ méo dạng góc hình học do gia tốc và quán tính đầu bút.
  3. Kiểm chứng thực nghiệm cho giả thuyết H3.2 (`acute_turn_count_120deg`).

### 3.3. Khối C: Tần suất nâng hạ bút trục Z (Rapid Pen-Lift Actuation Test)
- **Cấu trúc:** Dãy nét đứt tuần hoàn chu kỳ $2\,\text{mm}$ nét vẽ / $2\,\text{mm}$ nhấc bút ở các dải tốc độ $v \in \{20, 40, 60\}\,\text{mm/s}$.
- **Mục tiêu:**
  1. Kiểm tra độ trễ thực tế của servo trục Z ($t_{down}, t_{up}$).
  2. Phát hiện hiện tượng vệt đuôi chuột (pen drag) do nhấc bút không kịp hoặc đọng mực do hạ bút chậm.

### 3.4. Khối D: Thước chuẩn định cỡ quang học (Dimensional Calibration Bar)
- **Cấu trúc:** Thước kiểm chuẩn dài chính xác $50.00\,\text{mm}$ theo trục X và Y, kèm ô vuông $20.00 \times 20.00\,\text{mm}$.
- **Mục tiêu:** Hiệu chỉnh tỷ lệ co giãn quang học khi scan trước khi đo đạc độ rộng nét.

---

## 4. Quy trình Thực hiện Thực nghiệm từng bước

```text
[BƯỚC 1: Chuẩn bị máy & Cân bằng bàn vẽ]
      │
      ▼
[BƯỚC 2: Cố định giấy & Cài đặt lực ngòi]
      │
      ▼
[BƯỚC 3: Chạy CLI Benchmark tự động (--benchmark-rq3)]
      │
      ▼
[BƯỚC 4: Để khô mực 15 phút & Quét phẳng 600 DPI]
      │
      ▼
[BƯỚC 5: Phân tích trích xuất dữ liệu qua Scan Validator]
      │
      ▼
[BƯỚC 6: Tổng hợp CSV Telemetry & Đối chiếu Simulator]
```

### Bước 1: Chuẩn bị máy & Cân bằng bàn vẽ
1. Đặt máy vẽ trên mặt bàn đá hoặc gỗ phẳng vững chắc, không rung động.
2. Dùng thước nivô (thủy bình) kiểm tra độ phẳng mặt bàn vẽ theo 2 trục X và Y.
3. Cắm nguồn $12\text{V}/2\text{A}$ và cáp USB vào máy tính điều khiển.

### Bước 2: Cố định giấy & Cài đặt lực ngòi
1. Dán phẳng 4 góc tờ giấy Double A A4 vào mặt bàn vẽ bằng băng dính giấy (washi tape), không làm căng phồng giấy.
2. Gá bút Pentel EnerGel $0.5\,\text{mm}$ vào ngàm kẹp, điều chỉnh lò xo/đối trọng đạt lực tì $60 \pm 10\,\text{gf}$.
3. Cho máy về gốc tọa độ máy (Home: $X=0, Y=0$) và kiểm tra hành trình nâng hạ bút tự do.

### Bước 3: Chạy CLI Benchmark tự động
1. Thực hiện lệnh benchmark tự động:
   ```bash
   python backend/hardware_adapter.py --benchmark-rq3 --mode physical
   ```
2. Hệ thống sẽ tự động gửi tiêu bản `tests/fixtures/rq3_clearance_calibration_specimen.svg` sang driver phần cứng, bấm giờ độ phân giải microsecond, thu thập telemetry và lưu kết quả vào `logs/hardware_metrics.csv`.

### Bước 4: Để khô mực & Quét phẳng
1. Sau khi máy vẽ hoàn tất, giữ nguyên bản vẽ trên bàn phẳng ít nhất 15 phút ở nhiệt độ phòng ($25^\circ\text{C}$) để mực gel đóng rắn hoàn toàn, tránh lem bẩn khi quét.
2. Đặt bản vẽ lên máy quét phẳng 600 DPI, quét chế độ Grayscale hoặc 24-bit True Color, định dạng PNG lossless (không nén suy hao).

### Bước 5: Phân tích trích xuất dữ liệu
1. Đưa file ảnh quét vào pipeline phân tích đo lường:
   - Dùng thước chuẩn $50.00\,\text{mm}$ để tính độ phân giải thực tế ($PPM = \text{pixels per mm}$).
   - Đo bề rộng nét vẽ thực tế $w_{ink}$ trung bình qua profile phân bố cường độ xám FWHM (Full Width at Half Maximum).
   - Đo khoảng cách rìa-đến-rìa (edge-to-edge distance) của từng bậc khoảng hở $0.10 \to 0.70\,\text{mm}$.

---

## 5. Tiêu chuẩn Nghiệm thu Đóng Gate (`PASS_TV3_CALIBRATION`)

Để đóng chính thức `PENDING_TV3_CALIBRATION`, các tiêu chí sau bắt buộc phải đạt trên ít nhất 3 lượt vẽ lặp lại độc lập:

1. **An toàn va chạm nét mực (Ink Separation Threshold):**
   - Bậc $0.50\,\text{mm}$ danh định trên CAD phải có khoảng hở thực tế đo được sau khi mực khô:
     $$d_{actual} \ge 0.15\,\text{mm} > 0$$
     (Tuyệt đối không bị dính liền nét hoặc tạo cầu nối mực do mao dẫn).
   - Bậc $0.20\,\text{mm}$ danh định được xác định là ranh giới kỹ thuật tối thiểu (biên độ dung sai tiếp giáp).

2. **Độ lệch thời gian thi công (Draw Time Prediction Accuracy):**
   - Sai số tương đối giữa thời gian mô phỏng ($T_{sim}$) và thời gian thực tế ($T_{actual}$):
     $$\epsilon_{time} = \frac{|T_{actual} - T_{sim}|}{T_{actual}} \le 15.0\%$$
   - Khi sai số $\le 15\%$, mô hình động học của Simulator được coi là hợp thức để dùng làm tham chiếu ước tính.

3. **Chất lượng góc cua & rung động:**
   - Không xuất hiện hiện tượng văng giọt mực hoặc mất nét tại góc cua $120^\circ$ và $150^\circ$.
   - Độ vọt lố (overshoot) cơ học tại đỉnh góc cua $< 0.15\,\text{mm}$.
