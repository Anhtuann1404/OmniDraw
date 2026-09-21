# OmniDraw — Roadmap

**Cập nhật lần cuối:** 21/09/2026
**Chu kỳ làm việc:** Sprint 2 tuần
**Deadline cuối cùng (nộp/bảo vệ):** *(điền ngày khi có lịch chính thức của đơn vị)*

> Đánh dấu trạng thái mỗi mục nhỏ: `⬜ Chưa bắt đầu` / `🟡 Đang làm` / `✅ Xong`
> Mỗi giai đoạn lớn chỉ được coi là xong khi TẤT CẢ mục nhỏ bên trong đã ✅.

---

## 1. Nguyên tắc tổ chức & Phân công 4 đường chạy (Module Ownership)

Hệ thống R&D của OmniDraw được tổ chức theo **4 đường chạy độc lập**, mỗi thành viên sở hữu trọn vẹn một module cốt lõi với ranh giới trách nhiệm, đầu vào, đầu ra và tiêu chí hoàn thành đo được (DoD). Mọi đường chạy đều hội tụ về việc giải quyết câu hỏi nghiên cứu trung tâm về **CA-VHC**.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        CÂU HỎI NGHIÊN CỨU TRUNG TÂM                     │
│    Context-Aware Vietnamese Handwriting Composition (CA-VHC) trên Máy Vẽ│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  TV1: AI DỮ LIỆU │       │  TV2: TỐI ƯU NÉT │       │  TV3: PHẦN CỨNG  │
│  & WRITER PROFILE│       │  & QUY HOẠCH ĐƯỜNG       │  & THỰC NGHIỆM   │
│  - Gemini API    │       │  - Nearest Neighb│       │  - pyaxidraw     │
│  - Dataset mẫu   │       │  - cKDTree/Or-opt│       │  - Simulator     │
│  - WriterProfile │       │  - Kinematic cost│       │  - Actual timing │
│  - Feature extract       │  - DAG Path Plan │       │  - Sai số quỹ đạo│
└────────┬─────────┘       └────────┬─────────┘       └────────┬─────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    ▼
                 ┌──────────────────────────────────────┐
                 │ TV4: PROJECT LEAD & HANDWRITING CORE │
                 │      NỀN TẢNG, TÍCH HỢP & EVAL       │
                 │  - Toàn bộ backend/handwriting/      │
                 │  - Font Pack, NFD, diacritics, rules │
                 │  - Frontend React & API Gateway      │
                 │  - Experiment runner & CSV logging   │
                 │  - Điều phối Báo cáo NCKH 5 chương   │
                 └──────────────────────────────────────┘
```

### Bảng tổng hợp phân công 4 đường chạy

| Đường chạy / Thành viên | Module sở hữu | Đầu ra chính (Deliverables) | Tiêu chí hoàn thành (DoD) | Ranh giới phạm vi (Boundary) |
| :--- | :--- | :--- | :--- | :--- |
| **TV4 — Project Lead & Handwriting / CA-VHC Composition Lead** | Toàn bộ `backend/handwriting/` (engine, font packs, Unicode NFD, diacritic anchors/offsets, contextual allographs, rules, Catmull–Rom smoothing, geometry auditor, QA specimens), Frontend React, API Gateway (`backend/main.py`), experiment runner & CSV logging, điều phối kiến trúc và tổng hợp Báo cáo NCKH 5 chương | • Quỹ đạo SVG centerline nét đơn tái lập bằng seed<br>• Handwriting Composition Core hoàn thiện (NFD, dấu tiếng Việt, allographs)<br>• Bộ test hình học (`qa_specimens.py`, polyline auditor) pass không finding suy biến<br>• Toàn bộ API request/response tuân thủ contract v1.4<br>• Dataset test chạy tự động, log CSV đầy đủ metrics | Đảm bảo tính toàn vẹn của handwriting subsystem; điều phối kỹ thuật chung; không trực tiếp làm firmware máy vẽ (TV3) hoặc module trích contour vẽ tranh / KD-tree (TV2) |
| **TV2 — Stroke Optimization & Path Planning Lead** | `backend/path_optimizer.py`, tối ưu thứ tự nét vẽ tranh (NN + Or-opt + `cKDTree` + Kinematic Turn Penalty), mô hình chi phí động học (pen-up distance minimization, kinematic cost), transition/path cost trong Trellis DAG (co-designed với TV4), 2 bộ đối sánh thực nghiệm (comparison sets) và ablation study chuyển động | • Thuật toán tối ưu đường vẽ tranh giảm thiểu nhấc bút và góc bẻ tiếp tuyến<br>• Hàm chi phí chuyển trạng thái ($D_{\text{penup}}$, $N_{\text{lift}}$, $C_{\text{curvature}}$) trong Trellis DAG<br>• Thiết lập và đo đạc thực nghiệm bộ đối sánh Art Mode và các baseline chuyển động trong CA-VHC | • Giảm rõ rệt quãng đường pen-up và thời gian chuyển động so với Naive/Greedy<br>• Thời gian tính toán $O(N \log N)$ qua KD-tree scale tốt với hàng nghìn nét<br>• Kết quả deterministic với cùng phiên bản code, cấu hình, seed và môi trường thực thi được hỗ trợ | Không sở hữu `backend/handwriting/`, không sở hữu font packs hay quy tắc ngữ cảnh chữ viết tay; tập trung vào tối ưu chuyển động và quy hoạch quỹ đạo |
| **TV1 — AI Data & Writer Profile Lead** | Chuẩn bị benchmark corpus, synthetic data fixtures (cho CA-VHC cung cấp cho TV4), data protocol, `WriterProfile` schema (versioned, P2), trích xuất đặc trưng chữ viết mẫu, tích hợp API sinh ảnh Gemini (chi tiết tại `08_handwriting_dataset_spec.md`) | • Benchmark corpus & fixture đầu vào cho experiment runner<br>• Schema `WriterProfile` chuẩn hóa (P2 preparation)<br>• Bộ trích xuất đặc trưng độc lập có unit test<br>• Tài liệu ánh xạ sang engine | • Schema validate thành công<br>• Trích xuất tin cậy tối thiểu 4 đặc trưng trên dữ liệu mẫu<br>• Dữ liệu corpus sẵn sàng cho runner | Không sở hữu experiment runner/logging (TV4); không sở hữu quy tắc chính tả/dấu hay thuật toán handwriting engine (TV4); không sửa trực tiếp `backend/handwriting/`; tích hợp thuần túy qua contract |
| **TV3 — Hardware, Calibration & Physical Validation Lead** | Hardware adapter & simulator, kết nối AxiDraw qua `pyaxidraw`, hiệu chuẩn tọa độ/tốc độ/gia tốc/bút, đo `actual_draw_time_sec`, camera inspector | • File SVG chuẩn vẽ thành công trên máy thật<br>• Bộ thông số hiệu chuẩn có version<br>• Log thời gian vẽ thực tế<br>• Simulator và máy thật dùng chung interface | • Máy vẽ vật lý thi công đúng nét, không lệch lề<br>• Sai số tọa độ trong ngưỡng cho phép<br>• Khi chưa có máy: simulator pass smoke test, ghi rõ "blocked by hardware" | Không gọi thời gian mô phỏng là số đo máy thật |

---

## 2. Quy tắc Ownership và Merge Code

- **Nguyên tắc Single-owner:** Mỗi module chỉ có một thành viên chịu trách nhiệm chính. Thành viên khác có thể đóng góp ý kiến hoặc phản biện nhưng không tự ý sửa đổi code hoặc contract ngoài phạm vi sở hữu.
- **Điều phối file dùng chung & Kiến trúc:** Các file dùng chung (`backend/main.py`, `docs/OmniDraw_API_Spec-4.md`, hệ thống tài liệu NCKH) do **TV4 (Project Lead)** điều phối merge sau khi có sự đồng thuận của owner mảng liên quan:
  - Thay đổi logic `backend/handwriting/` và `font_packs/`: Bắt buộc có review và duyệt từ **TV4** (Handwriting Composition Lead).
  - Thay đổi logic tối ưu đường vẽ `backend/path_optimizer.py` hoặc hàm chi phí chuyển động: Bắt buộc có review và duyệt từ **TV2** (Stroke Optimization Lead).
  - Thay đổi giải thuật Trellis DAG / Viterbi đồng thiết kế: Bắt buộc có sự thống nhất giữa **TV2** (phần path/transition cost) và **TV4** (phần glyph/state/diacritic context).
  - Thay đổi cấu trúc dữ liệu `WriterProfile`: Bắt buộc có review từ **TV1**.
  - Thay đổi phần cứng, adapter hoặc telemetry: Bắt buộc có review từ **TV3**.
  - Thay đổi schema API, logging hoặc UI contract: Bắt buộc có review từ **TV4**.
- **Nhịp tích hợp (Integration Cadence):** Chỉ tích hợp mã nguồn chính thức 1 lần mỗi tuần vào buổi họp kỹ thuật hoặc vào cuối mỗi sprint 2 tuần (trừ trường hợp hotfix lỗi nghiêm trọng làm tắc nghẽn toàn hệ thống).
- **Đóng băng Contract:** Tuyệt đối không thay đổi API contract giữa sprint nếu không phải lỗi blocker được toàn nhóm phê duyệt.

---

## 3. Definition of Done (DoD) chung

Một nhiệm vụ hoặc tính năng chỉ được đánh dấu hoàn thành (`✅ Xong` / `[x]`) khi đáp ứng đầy đủ các tiêu chí:

1. **Hiện diện thực tế:** Code nguồn, test hoặc tài liệu đầu ra thực sự tồn tại trong repository.
2. **Quy trình kiểm chứng rõ ràng:** Có lệnh chạy kiểm thử, script tái lập hoặc biên bản kiểm tra cụ thể.
3. **Kết quả kiểm chứng được ghi nhận:** Có log thực thi, kết quả test pass hoặc số liệu đo đạc được lưu lại.
4. **Không gây thoái lui (No Regression):** Bộ test hồi quy hiện tại và các test suite liên quan không bị ảnh hưởng.
5. **Đồng bộ hợp đồng:** Schema JSON, API Spec và tài liệu kỹ thuật được cập nhật đồng thời nếu hành vi dữ liệu thay đổi.
6. **Trung thực khoa học:** Không tuyên bố vượt quá bằng chứng thực nghiệm (không dùng các từ "100%", "hoàn toàn", "không giới hạn", "tối ưu nhất").
7. **Được xác nhận chéo:** Owner hoàn thành và reviewer tương ứng đã nghiệm thu.

> *Lưu ý:* Các trạng thái "đã thảo luận", "đã lên ý tưởng" hoặc "đang có kế hoạch" tuyệt đối không được đánh dấu hoàn thành.

---

## 4. Hệ thống Mức độ Ưu tiên (Priority Levels: P0 – P3)

Để tập trung nguồn lực bảo vệ thành công đề tài NCKH, toàn bộ các hạng mục công việc được phân cấp ưu tiên nghiêm ngặt:

### P0 — Bắt buộc để bảo vệ đề tài (Critical Path)
*Các hạng mục quyết định tính hợp lệ và đóng góp khoa học của đề tài. Mọi thành viên phải ưu tiên tuyệt đối.*
- Khóa Research Questions (RQ) và giả thuyết khoa học.
- Định nghĩa và toán học hóa hình thức hàm mục tiêu CA-VHC.
- Đưa dấu tiếng Việt theo quy tắc chính tả và vùng cấm va chạm trực tiếp vào bài toán Trellis DAG.
- Tối ưu hóa thứ tự nét trễ (Delayed-stroke ordering) cho dấu tiếng Việt.
- Thiết lập và đo đạc thực nghiệm 2 bộ baseline đối chứng (Art Mode: Naive, Greedy NN, cKDTree+Or-opt; CA-VHC: Static, Greedy Heuristic, Current Trellis DAG).
- Bộ thực nghiệm định lượng (Quantitative Benchmark) chữ viết tay và vẽ tranh.
- Nghiên cứu độ nhạy thành phần (Ablation Study) cho hàm chi phí $J$.
- Kiểm chứng thi công vật lý trên máy vẽ thật AxiDraw.
- Framework ghi log CSV chuẩn và bảo đảm tính tái lập kết quả deterministic qua seed.
- Xây dựng hoàn chỉnh Báo cáo NCKH 5 chương và slide bảo vệ.

### P1 — Hoàn thiện hệ thống nghiên cứu (Core Supporting)
*Các hạng mục giúp hệ thống hoàn chỉnh, chặt chẽ và phục vụ trực tiếp cho P0.*
- Mở rộng kho allographs có kiểm soát theo các cấp ngữ cảnh phổ biến.
- Bộ QA hình học mở rộng cho toàn bộ bảng chữ cái và tổ hợp dấu tiếng Việt phức tạp.
- Strict validation trên API Gateway (loại bỏ triệt để fallback ngầm đối với tham số `style` và `font`).
- Bố cục trang, tùy biến cỡ chữ và tự động ngắt dòng thông minh trên 1 trang A4.
- Camera inspector cơ bản hỗ trợ căn góc giấy.

### P2 — Mở rộng nếu tiến độ P0/P1 ổn định (Optional Extensions)
*Quy tắc thực hiện hạng mục P2 (Writer Profile & Telemetry):*
- **Được phép thực hiện song song trong Sprint 1–2 (P2 Preparation):** Nghiên cứu sơ bộ, thiết kế JSON schema `WriterProfile` (versioned), soạn protocol đạo đức và ẩn danh hóa, chuẩn bị synthetic fixtures, viết prototype feature extractor độc lập, và viết tài liệu ánh xạ tham số dự kiến. Các công việc chuẩn bị này chỉ được thực hiện khi không làm chậm tiến độ P0/P1.
- **Chỉ được thực hiện sau Gate 2 hoặc khi P0/P1 đã ổn định:** Tích hợp Writer Profile vào Handwriting Engine, triển khai Writer Profile MVP chạy end-to-end, thu thập dữ liệu người dùng thật, huấn luyện/fine-tune mô hình machine learning, few-shot personalization trên dữ liệu thật, telemetry phản hồi thời gian thực từ phần cứng, hoặc đánh giá/tuyên bố hiệu quả cá nhân hóa nét chữ.
- Xây dựng mô hình Writer Profile MVP (rule-based) [P2 — sau Gate 2].
- Thử nghiệm trích xuất đặc trưng chữ viết tay từ tập mẫu nhỏ (few-shot personalization) [P2 — sau Gate 2].
- Telemetry phản hồi trạng thái vẽ từ phần cứng theo thời gian thực [P2 — sau Gate 2].
- Đồng bộ hiệu ứng preview trên canvas theo tiến trình nét vẽ máy thật [P2 — sau Gate 2].

### P3 — Backlog nghiên cứu xa (Post-Defense Backlog)
*Tuyệt đối không thực hiện trước khi đóng băng tính năng (Feature Freeze).*
- Bộ chuyển đổi font viền đôi TTF/OTF sang centerline nét đơn.
- Bổ sung ồ ạt các font pack mới chưa qua kiểm thử hình học.
- Chữ hoa đầu đoạn phức tạp (Drop cap), tiêu đề cong, hoa văn viền trang trí.
- Mô hình sinh chữ viết tay bằng mạng nơ-ron học sâu quy mô lớn.
- Các tính năng trang trí giao diện không đóng góp vào bằng chứng nghiên cứu.

> **Nguyên tắc sắt:** Các hạng mục **P2** và **P3** tuyệt đối không được làm trễ hạn hoặc phân tán nguồn lực của các hạng mục **P0**.

---

## 5. Lộ trình theo các Cổng Quyết định (Decision Gates & Milestones)

Thay vì timeline tuyến tính đơn giản, tiến độ 12 tháng được giám sát qua các **Cổng quyết định (Decision Gates)**:

```text
[Sprint 1–2] ──Gate 1──▶ [Sprint 3–6] ──Gate 2──▶ [Sprint 7–10] ──Gate 3──▶ [Tháng 8–9] ──Gate 4──▶ [Tháng 10–12]
Khóa Nền tảng            Phát triển                Tích hợp Beta              Feature Freeze           Thực nghiệm
Nghiên cứu               Song song                 & Đánh giá                 & Ablation               & Bảo vệ
```

### Sprint 1–2 (Tháng 1–2) — Khóa nền nghiên cứu (Locking Research Foundation)
- **Mục tiêu:** Thống nhất toàn bộ cơ sở học thuật, công thức toán học và hợp đồng giao tiếp giữa 4 module.
- **Nội dung thực hiện:**
  - Chốt danh sách Research Questions (RQ1, RQ2, RQ3) và giả thuyết kiểm chứng.
  - Toán học hóa hàm mục tiêu $J$, chuẩn hóa ký hiệu toán học cho Trellis DAG và Viterbi DP.
  - Chốt input/output contract giữa 4 module qua API Spec v1.4.
  - Chốt benchmark corpus câu/từ chuẩn tiếng Việt và định nghĩa rõ ràng **2 bộ đối sánh độc lập (comparison sets)**:
    - *Bộ đối sánh Art Mode / Path Optimization (TV2 lead):* So sánh 3 phương pháp gồm (1) Original contour order / Naive, (2) Greedy Nearest Neighbor, và (3) Phương pháp tối ưu OmniDraw `cKDTree + Or-opt + Kinematic Turn Penalty`.
    - *Bộ đối sánh Handwriting CA-VHC (TV4 lead composition/runner, TV2 lead motion):* Đánh giá Phương pháp đề xuất (**Proposed CA-VHC** có diacritic constraints, delayed-stroke ordering và kinematic cost — là phương pháp nghiên cứu được đánh giá, không phải baseline thứ tư) đối chứng với **3 baseline**: (1) Static Glyph Renderer, (2) Greedy contextual/connection heuristic, và (3) Current Trellis DAG (chưa có ràng buộc dấu nâng cao).
  - Mỗi thành viên thiết lập backlog 2 tuần chi tiết kèm tiêu chí DoD tương ứng (TV1 thực hiện P2 Preparation cho Writer Profile mà không ảnh hưởng P0/P1).
- **Cổng hoàn thành (Gate 1):**
  - Không còn thuật ngữ nghiên cứu mơ hồ trong toàn bộ tài liệu dự án.
  - Mọi module có duy nhất một owner chịu trách nhiệm.
  - Mọi chỉ số kỳ vọng trong bài báo đều có công thức hoặc quy trình đo đạc xác định.

### Sprint 3–6 (Tháng 3–5) — Phát triển song song 4 đường chạy (Parallel Development)
- **Mục tiêu:** Triển khai các thành phần P0 và P1 cốt lõi theo ranh giới module độc lập.
- **Nội dung thực hiện:**
  - **TV4:** Hoàn thiện Handwriting Composition Core (đưa ràng buộc dấu tiếng Việt theo chính tả và vùng cấm va chạm phía handwriting vào DAG), triển khai strict validation (xóa fallback ngầm), hoàn thiện experiment runner và logging CSV.
  - **TV2:** Xây dựng phần tối ưu hóa quỹ đạo và transition cost cho Trellis DAG; chuẩn hóa bộ đối sánh Art Mode (Naive, Greedy NN, cKDTree+Or-opt) và các baseline chuyển động trong CA-VHC.
  - **TV1:** Hoàn thiện benchmark corpus/fixtures phục vụ P0; chỉ tiếp tục P2 Preparation cho Writer Profile nếu không ảnh hưởng tiến độ P0/P1.
  - **TV3:** Hoàn thiện hardware simulator, xây dựng calibration checklist và smoke test AxiDraw (nếu có máy).
- **Cổng hoàn thành (Gate 2):**
  - Có bản demo tích hợp end-to-end chạy tự động trên tập corpus mẫu với seed cố định.
  - Mỗi module phản hồi đúng cấu trúc JSON/SVG của contract, không crash với input lỗi.
  - Toàn bộ metrics cơ bản được ghi nhận tự động vào file log CSV, không cần tổng hợp thủ công.

### Sprint 7–10 (Tháng 6–7) — Tích hợp Beta & Kiểm định Phần cứng (Beta Integration)
- **Mục tiêu:** Tích hợp sâu các thành phần thuật toán với phần cứng máy vẽ và đánh giá mở rộng.
- **Nội dung thực hiện:**
  - Hoàn thiện thuật toán né tránh va chạm dấu phụ và tối ưu thứ tự nét trễ (delayed-stroke ordering).
  - Tích hợp Writer Profile MVP nếu dữ liệu mẫu đã sẵn sàng và chứng minh được tính khả thi.
  - Thu thập số đo thời gian thực tế `actual_draw_time_sec` trên máy vẽ vật lý.
  - Thử nghiệm bố cục và ngắt dòng thông minh trong phạm vi một trang giấy.
  - Chạy thử nghiệm benchmark sơ bộ, phát hiện và sửa toàn bộ lỗi lệch contract.
- **Cổng quyết định (Gate 3):**
  - *Quyết định Writer Profile:* Nếu Writer Profile chưa có dữ liệu mẫu thực tế hoặc chưa vượt qua baseline rule-based, lập tức chuyển về mục tiêu nghiên cứu tương lai, không làm chậm tiến độ P0.
  - *Quyết định Telemetry:* Nếu kết nối telemetry phản hồi thời gian thực chưa ổn định, chỉ giữ lại số đo thời gian thực tế `actual_draw_time_sec` và trạng thái job cơ bản.
  - *Nguyên tắc loại bỏ:* Không giữ bất kỳ tính năng nào chỉ vì "đã lỡ viết code" nếu nó không trực tiếp đóng góp vào các câu hỏi nghiên cứu của bài báo.

### Tháng 8–9 — Đóng băng tính năng & Chạy thực nghiệm toàn diện (Feature Freeze)
- **Mục tiêu:** Đóng băng toàn bộ mã nguồn, thực thi toàn bộ benchmark định lượng và kiểm thử hồi quy.
- **Quy tắc đóng băng:** Tuyệt đối không bổ sung tính năng mới, không sửa đổi cấu trúc dữ liệu hoặc thuật toán.
- **Nội dung thực hiện:**
  - Chạy trọn vẹn bộ thực nghiệm định lượng đối sánh CA-VHC với 3 baseline đối chứng và bộ đối sánh Art Mode trên toàn bộ corpus.
  - Thực hiện đầy đủ Ablation Study đánh giá độ nhạy tham số và bóc tách từng chi phí trong $J$.
  - Chạy regression test QA hình học trên toàn bộ ma trận font/style.
  - Kiểm chứng vẽ thực tế trên máy vẽ AxiDraw vật lý và đo sai số quỹ đạo.
  - Khóa phiên bản cố định (Tag release/commit hash): dataset corpus, seed, config và mã nguồn.

### Tháng 10–12 — Đánh giá người dùng, Viết báo cáo & Bảo vệ đề tài (Evaluation & Defense)
- **Mục tiêu:** Thu thập đánh giá định tính, hoàn tất báo cáo khoa học 5 chương và bảo vệ đề tài.
- **Nội dung thực hiện:**
  - Tổ chức khảo sát đánh giá người dùng (User Study) với 30–50 người theo protocol đạo đức khoa học.
  - Phân tích thống kê định lượng và định tính kết quả thực nghiệm.
  - Hoàn thiện bản thảo Báo cáo NCKH 5 chương chuẩn mực học thuật.
  - Thiết kế đồ thị đối sánh, biểu đồ ablation và quay video minh chứng quy trình thực thi máy vẽ.
  - Rà soát tính trung thực khoa học: kiểm tra từng phát biểu trong báo cáo đều có số liệu kiểm chứng.
  - Diễn tập thuyết trình, chuẩn bị slide và câu hỏi phản biện bảo vệ đề tài.

---

## 6. Chi tiết các giai đoạn triển khai (Giai đoạn 1 đến Giai đoạn 4)

### Giai đoạn 1 — Khảo sát & Nền tảng

**Trạng thái:** 🟡 Hoàn thành nền tảng phần mềm; phần cứng đang bị block | **Hạn giai đoạn:** *(phần mềm hoàn thành; phần cứng tiếp tục hoàn thiện khi có máy)*

#### 1.1 Khảo sát & chốt hướng AI
**Trạng thái:** ✅ | **Phụ trách:** TV1, TV2
- [x] So sánh 2-3 phương án model/API sinh ảnh (chi phí, tốc độ, chất lượng)
- [x] So sánh phương án CV cho căn giấy/nhận diện
- [x] Chốt lựa chọn cuối, ghi vào `01_tech-stack.md` (Dùng Gemini API developer tier để kiểm thử)

#### 1.2 Kiến trúc & chuẩn dữ liệu
**Trạng thái:** ✅ | **Phụ trách:** TV4 (lead)
- [x] Chốt sơ đồ luồng dữ liệu tổng thể (bao gồm cả Art Mode và Handwriting Mode)
- [x] Viết `OmniDraw_API_Spec-4.md` (schema JSON/SVG, mã lỗi chuẩn, metrics nghiên cứu)
- [x] Gửi tài liệu cho cả nhóm, xác nhận mọi người đã đọc & hiểu

#### 1.3 Phần cứng cơ bản
**Trạng thái:** ⬜ | **Phụ trách:** TV3 *(Blocked by hardware: chờ setup cáp & máy vẽ thực tế)*
- [ ] Lắp ráp máy AxiDraw, test vẽ tay bằng file SVG mẫu có sẵn
- [ ] Gắn thử camera, kiểm tra góc nhìn/độ phân giải đủ dùng
- [ ] Xác nhận kết nối máy tính ↔ máy vẽ ổn định (USB/Serial qua `pyaxidraw`)
- [x] Hoàn thiện khung mô phỏng phần mềm (`backend/main.py:mock_grbl`) để team phần mềm chạy thử

#### 1.4 Khung UI/UX (mock data)
**Trạng thái:** ✅ | **Phụ trách:** TV4
- [x] Thiết kế luồng màn hình chính (upload/nhập mô tả → preview → gửi vẽ → theo dõi tiến độ)
- [x] Dựng giao diện chạy được với dữ liệu giả
- [x] Dựng khung tích hợp rỗng (API client sẵn sàng kết nối backend)

---

### Giai đoạn 2 — Phát triển song song theo 4 đường chạy

**Trạng thái:** 🟡 Đang làm | **Hạn giai đoạn:** *(theo Sprint 3–6)*

#### 2.1 AI Core & Benchmark Dataset Preparation (Đường chạy TV1)
**Trạng thái:** 🟡 Đang làm | **Phụ trách:** TV1 | **Mức ưu tiên:** P0 / P1
- [x] Tích hợp model/API sinh ảnh từ text (`POST /api/ai/generate` với Google Gemini API), nhận kết quả đúng chuẩn [P1]
- [x] Test với bộ prompt mẫu, đánh giá latency và chất lượng đầu ra [P1]
- [x] Thiết kế & đặc tả kỹ thuật bộ phiếu thu thập chữ viết tay **OmniDraw Handwriting Collection Sheet Pack v1** gồm 4 trang: P01 (*Isolated Characters & Diacritics*), P02 (*Context & Ligatures*), P03 (*Sentence Flow & Pangram*), P04 (*Natural Paragraph*); trạng thái: **PILOT CANDIDATE** (chờ in/quét thực nghiệm, chưa phê duyệt thu thập chính thức; lưu trữ tại `docs/collection_sheets/P01..P04`) [P0] (TV1 phối hợp TV4)
- [ ] Xây dựng scan-validation pipeline tối thiểu (fiducial detection, deskew/rectification, scale check, deterministic auto-crop) và thực hiện in/quét bench test P01–P04 [P0] (TV1)
- [ ] Phân tích độ phủ ký tự & ngữ cảnh (coverage analysis) của P01–P04, chốt collection protocol & error-handling policy (Pending protocol decision) [P0] (TV1 phối hợp TV4)
- [ ] Triển khai thử nghiệm pilot giới hạn 3–5 người viết và đánh giá dữ liệu pilot [P0] (TV1)
- [ ] Thu thập dữ liệu chính thức ~40 writers với phân chia writer-disjoint split (28 Train, 6 Val, 6 Test - planned split, chưa thực thi) [P0] (TV1)
- [ ] Xây dựng benchmark corpus câu/từ chuẩn phục vụ thực nghiệm tự động hóa (tuân thủ quy chuẩn CA-VHC Dataset trong `08_handwriting_dataset_spec.md`) [P0]
- [ ] Chuẩn bị synthetic fixtures và dữ liệu đầu vào chuẩn cho experiment runner của TV4 [P0]

#### 2.2 AI Cá nhân hóa & Dữ liệu Writer Profile (Đường chạy TV1)
**Trạng thái:** 🟡 Chuẩn bị nghiên cứu / Chưa tích hợp | **Phụ trách:** TV1 | **Mức ưu tiên:** P2
*(Lưu ý: Writer Profile là hướng nghiên cứu mở rộng P2. Trong Sprint 1–2 chỉ thực hiện các bước chuẩn bị nhẹ (P2 Preparation): schema, protocol đạo đức/ẩn danh, fixture giả lập và prototype trích xuất đặc trưng độc lập theo đặc tả [`08_handwriting_dataset_spec.md`](08_handwriting_dataset_spec.md); chưa tích hợp vào engine, việc tích hợp chỉ xem xét sau Gate 2 hoặc khi P0/P1 ổn định; chưa coi là Writer Profile MVP hoàn thành, không huấn luyện mô hình lớn).*
- [ ] Thiết kế cấu trúc dữ liệu mẫu chữ viết tay và protocol ẩn danh hóa thông tin người dùng [P2]
- [ ] Định nghĩa JSON schema `WriterProfile` chuẩn hóa có version [P2]
- [ ] Xây dựng prototype trích xuất 4 đặc trưng cơ bản (slant, aspect ratio, spacing, baseline jitter) [P2]
- [ ] Xây dựng mô hình cá nhân hóa baseline rule-based và tài liệu ánh xạ sang tham số engine [P2]
- [ ] Nghiên cứu AI style transfer cho ảnh phác thảo khi có dữ liệu (tuỳ chọn) [P3]

#### 2.3 Thị giác máy tính & Căn chỉnh giấy (Đường chạy TV3)
**Trạng thái:** ⬜ Chưa bắt đầu | **Phụ trách:** TV3 | **Mức ưu tiên:** P1
- [ ] Nhận diện & đo góc nghiêng mép giấy tự động qua camera [P1]
- [ ] Truyền góc bù nắn thẳng vào pipeline kết xuất vector [P1]

#### 2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)
**Trạng thái:** 🟡 Đang làm | **Phụ trách:** TV4 & TV2 | **Mức ưu tiên:** P0 (lõi) / P1 / P2 / P3

##### A. Tối ưu đường vẽ tranh (Line-art Art Mode) — Đã xong
**Phụ trách:** TV2 (Stroke Optimization Lead)
- [x] Chuyển ảnh → vector line-art qua Canny Edge + FindContours
- [x] Tối ưu thứ tự nét vẽ tranh: giảm quãng đường pen-up qua `cKDTree` + Or-opt + Kinematic Turn Penalty
- [x] Xuất chuẩn SVG đường vẽ tranh kèm metrics hình học

##### B. Lõi giải thuật CA-VHC & Stroke Graph Optimizer — P0
**Phụ trách:** TV4 (Handwriting Lead) & TV2 (Optimization Lead) [Đồng thiết kế / Co-designed]
- [x] Cấu trúc Font Pack nét đơn độc lập (`font_packs/`: geometry, metrics, anchors — TV4 sở hữu)
- [x] Hoàn thiện 81 ký tự nét đơn custom trong gói Omni Casual v1 (TV4)
- [x] Thuật toán lõi Stroke Graph Optimizer: Quy hoạch động Viterbi DP trên Trellis DAG theo từng từ (`optimize_word_dag()`, `eval_transition()`) kết hợp state/context representation của TV4 và transition optimization của TV2
- [x] Xuất đường nét đơn mượt qua Catmull–Rom sang Cubic Bézier kết hợp auto-deskew (TV4)
- [x] Tái lập kết quả dựa trên seed số nguyên 32-bit không dấu (TV4)
- [ ] Mở rộng tối ưu hóa quỹ đạo nét ở cấp độ từ và dòng văn bản thay vì chỉ xử lý cục bộ [P0] (TV4 & TV2)

##### C. Bố trí dấu tiếng Việt & Thứ tự nét trễ — P0
**Phụ trách:** TV4 (chủ trì chính tả & mỏ neo dấu) + TV2 (phối hợp tối ưu nét trễ)
- [x] Xử lý chuẩn hóa Unicode NFD, tự động ghép dấu thanh và dấu phụ theo mỏ neo (anchors) và offset (TV4)
- [x] **BƯỚC A — Architecture Audit Trellis DAG / CA-VHC hiện tại (COMPLETE):** Audit toàn diện mã nguồn, bóc tách hạn chế ghép dấu post-DAG, phân rã NFD và rủi ro va chạm cầu nối runtime (`06_audit_trellis_dag_report.md`) [P0] (TV4)
- [x] **BƯỚC B — Diacritic-Aware State Architecture Design (APPROVED AND CLOSED):** Khóa thiết kế kiến trúc trạng thái lai `CompositionState = GlyphVariant × DiacriticCandidate` (`07_diacritic_aware_state_design.md`), phân tách $C_{\text{state}}$ và $J_{\text{transition}}$, loại bỏ double-count, Single Source of Truth `DiacriticConfig`, khống chế $K_{\text{raw}} \le 9$, 12 unit test strategies; trạng thái: Architecture draft: DONE / Internal technical cleanup: DONE / TV2 cross-review: COMPLETED / PASS [P0] (TV4 chủ trì phối hợp TV2)
- [ ] **BƯỚC C — Production Implementation (AUTHORIZED / NOT YET IMPLEMENTED — READY FOR STEP C: YES):** Software implementation authorized by TV4 after TV2 technical cross-review; chưa có CompositionState production implementation, chưa có diacritic-aware DAG production, chưa có delayed-stroke P0, chưa hoàn thành benchmark chính thức (không được hiểu AUTHORIZED là COMPLETED) [P0] (TV4 & TV2)
  - **Nhiệm vụ ưu tiên cao nhất của TV4:** `PR1 — Hoàn thiện CA-VHC Metrics & Experiment Infrastructure`: tích hợp internal evaluator vào experiment pipeline, mở rộng CSV cho các metric CA-VHC đã thực sự tồn tại, xây dựng automated experiment runner, giữ backward compatibility; chưa bắt đầu PR3 `CompositionState` trước khi PR1 có test và metric baseline ổn định.
  - **Nhiệm vụ song song của TV2:** `PR2 — Chuẩn hóa ba baseline adapters B1/B2/B3` độc lập và chuẩn bị giao diện transition-cost cho PR3.
- [ ] Nghiên cứu tối ưu hóa thứ tự nét trễ (`delayed-stroke ordering`): quyết định viết dấu ngay sau nguyên âm, sau khi viết xong thân từ, hay theo nhóm nét trễ để cân bằng giữa quãng đường di chuyển quay lại, số lần nhấc bút và độ dễ đọc [P0] (TV4 & TV2)
- [ ] Xử lý an toàn tổ hợp nhiều dấu tiếng Việt chồng tầng (dấu mũ + thanh, dấu móc + thanh) [P0] (TV4)

##### D. Contextual allographs có kiểm soát — P1
**Phụ trách:** TV4 (Handwriting Composition Lead)
- [x] Biến thể chữ hoa mở đầu trang trọng (`formal_initial`) cho K, T, C trên font pack legacy (TV4)
- [x] Biến thể hình học kết thúc từ (`word_final`) cho n, m trong Omni Casual (TV4)
- [ ] Mở rộng kho allographs theo các cấp ngữ cảnh: đầu đoạn, đầu câu, đầu từ, cuối từ, cuối câu, loại thư [P1] (TV4)
- [ ] Đánh giá định lượng chất lượng nối nét và mức độ phù hợp ngữ cảnh [P1] (TV4 phối hợp TV2)

##### E. AI cá nhân hóa nét chữ (Writer Profile) — P2 (TV1 chủ trì phối hợp TV4 & TV2 qua contract)
**Phụ trách:** TV1 (chủ trì) phối hợp TV4 & TV2
- [ ] Ánh xạ các đặc trưng từ Writer Profile (TV1) sang tham số biến đổi hình học trong Font Pack và Render Profile (TV4) [P2]
- [ ] Tích hợp thử nghiệm cá nhân hóa rule-based vào luồng sinh SVG (TV4 phối hợp TV2) [P2]

##### F. Bố cục trang, Cỡ chữ & Phân trang — P1 (TV4 phụ trách)
**Phụ trách:** TV4 (Handwriting Composition Lead)
*(Lưu ý: UI controls căn lề và giãn dòng đã có trên giao diện CreateScreen, nhưng backend layout engine thực tế, áp dụng lề vào tọa độ render, font size động và ngắt dòng thông minh xét ascender/descender/dấu tiếng Việt chưa hoàn thiện; không đánh dấu hoàn thành chỉ vì giao diện đã có control).*
- [ ] Hoàn thiện backend layout engine áp dụng cỡ chữ (`font_size_pt`), lề trang (`margins_mm`), căn lề (trái/giữa/phải) có hiệu lực thực tế trên 1 trang A4 [P1]
- [ ] Tự động ngắt dòng thông minh có xét đến chiều cao ascender, descender và dấu tiếng Việt [P1]
- [ ] Nghiên cứu phân trang đa trang (multi-page) xuất mảng file SVG (hiện tại từ chối tràn trang bằng `TEXT_OVERFLOW`) [P2]

##### G. Tính năng trình diễn & Mở rộng nét đơn (Demos & Embellishments) — P3 Backlog
**Phụ trách:** TV4 (Handwriting Composition Lead)
- [ ] Nét kéo dài lượn sóng dưới từ cuối câu (Terminal swash) [P3]
- [ ] Chữ hoa đầu đoạn trang trí nghệ thuật (Drop cap) [P3]
- [ ] Cụm từ nối liền khối (Logograms: "Kính gửi", "Thân gửi", "Cảm ơn") [P3]
- [ ] Tiêu đề uốn lượn vòm cong Bézier [P3]
- [ ] Đường phân đoạn hoa văn centerline [P3]

##### H. QA & Kiểm thử hình học — P0 / P1
**Phụ trách:** TV4 (Handwriting Composition Lead)
- [x] Công cụ kiểm thử trực quan ma trận font/style và đối chiếu biến thể thư tay (`backend/handwriting/qa_specimens.py`) [P1] (TV4)
- [x] Bộ kiểm tra polyline (`audit_font_pack_geometry()`, `_stroke_min_distance()`) phát hiện đoạn suy biến, nét đè lặp trong bộ ký tự hiện tại [P0] (TV4)
- [ ] Mở rộng kiểm thử hình học và QA trực quan cho toàn bộ bảng chữ cái, chữ hoa và tổ hợp dấu tiếng Việt phức tạp [P1] (TV4)

#### 2.5 Phần cứng — Firmware & Điều khiển chuyển động (Đường chạy TV3)
**Trạng thái:** ⬜ Chưa bắt đầu | **Phụ trách:** TV3 | **Mức ưu tiên:** P0
- [ ] Chuẩn hóa interface chung giữa hardware simulator và máy vẽ thật [P0]
- [ ] Điều khiển máy vẽ AxiDraw qua `pyaxidraw` thực thi đúng file SVG chuẩn [P0]
- [ ] Xử lý an toàn các lệnh tạm dừng (`pause`), tiếp tục (`resume`), hủy vẽ (`cancel`) [P1]
- [ ] Xây dựng quy trình và checklist hiệu chuẩn tọa độ, vận tốc, gia tốc và độ nảy ngòi bút [P0]

#### 2.6 Phần cứng — Đo đạc thực tế & Trạng thái (Đường chạy TV3)
**Trạng thái:** ⬜ Chưa bắt đầu | **Phụ trách:** TV3 | **Mức ưu tiên:** P0 / P2
- [ ] Thu thập số đo thời gian vẽ thực tế `actual_draw_time_sec` trên máy vẽ vật lý [P0]
- [ ] Báo cáo đo lường sai số quỹ đạo vật lý so với tọa độ SVG thiết kế [P0]
- [ ] Gửi trạng thái/tiến độ thi công về đúng chuẩn JSON ở mục 5 trong API Spec [P1]
- [ ] Phát hiện lỗi cơ bản (kẹt giấy, hết mực) và trả đúng mã lỗi chuẩn [P1]
- [ ] Telemetry phản hồi trạng thái đầu bút theo thời gian thực (hướng mở rộng) [P2]

#### 2.7 Giao diện, Strict Validation & Tích hợp (Đường chạy TV4)
**Trạng thái:** 🟡 Đang làm | **Phụ trách:** TV4 | **Mức ưu tiên:** P0 / P1
- [x] Hoàn thiện các màn hình giao diện hiện có (`CreateScreen`, `PreviewScreen`, `PrintStatusScreen`, `HistoryScreen`, `ConfirmScreen`, `DoneScreen`, `LoginScreen`) [P1]
- [x] Viết hàm gọi API theo chuẩn trong `frontend/src/api/omnidraw.js`, tích hợp Art Mode và Handwriting Mode [P0]
- [x] Strict Validation toàn diện trên API Gateway: loại bỏ triệt để silent fallback cho `style`, `font`, `letter_type`, `seed`, `target_paper_size_mm`; bảo đảm nguyên tắc validation-before-side-effect; 34/34 regression tests pass [P1] (TV4)
- [ ] Hoàn thiện màn hình cấu hình (`SettingsScreen`) hỗ trợ nhập thông số hiệu chuẩn máy vẽ [P1]
- [ ] Tích hợp cơ chế hiển thị lỗi chi tiết cho ký tự chưa hỗ trợ (`UNSUPPORTED_CHARACTER`) và tràn trang (`TEXT_OVERFLOW`) [P1]

#### 2.8 Checklist module & Đánh giá nội bộ
**Trạng thái:** 🟡 Đang làm | **Phụ trách:** Cả 4 người | **Mức ưu tiên:** P0
- [x] TV4 (Handwriting & API Gateway): Đã test sinh chữ viết tay chuẩn, xử lý lỗi contract, và truyền `request_id` xuyên suốt [P0]
- [x] TV2 (Tối ưu nét vẽ tranh): Đã test thuật toán tối ưu nét vẽ tranh, KD-tree, giảm quãng đường nhấc bút [P0]
- [x] TV1 (AI sinh ảnh): Đã test gọi API sinh ảnh text-to-image với prompt mẫu và xử lý lỗi phản hồi [P1]
- [ ] TV1 (Dữ liệu & Writer Profile): Kiểm thử schema `WriterProfile` và bộ trích xuất đặc trưng với fixture giả lập [P2]
- [ ] TV3 (Phần cứng & Firmware): Kiểm thử simulator qua smoke test; thực thi trên máy vẽ vật lý thật khi có thiết bị [P0]

---

### Giai đoạn 3 — Tích hợp hệ thống

**Trạng thái:** 🟡 Hoàn thành một phần sớm; tích hợp máy thật chưa bắt đầu | **Hạn giai đoạn:** *(theo Sprint 7–10; các mục 3.1 và 3.2 đã được tích hợp sớm ở mức phần mềm)*

#### 3.1 Tích hợp luồng AI & Sinh vector vào giao diện
**Trạng thái:** ✅ Hoàn thành | **Phụ trách:** TV1 + TV4 (TV4 lead tích hợp)
- [x] Thay mock data bằng gọi API backend thật cho luồng sinh ảnh AI từ text (`/api/ai/generate`) và chuyển ảnh thành SVG theo các style vector hóa hiện có (`path_optimizer.py`)
- [x] Xử lý lỗi/timeout hiển thị đúng trên giao diện

#### 3.2 Tích hợp CV & Tối ưu chữ viết tay vào giao diện
**Trạng thái:** ✅ Hoàn thành | **Phụ trách:** TV4 (lead) + TV2
- [x] Nối module CV/tối ưu đường vẽ tranh vào luồng thật sau bước AI sinh ảnh (TV2 + TV4)
- [x] Kiểm tra SVG xuất ra đúng khổ giấy, đúng chuẩn (TV4)
- [x] Nối module sinh chữ viết tay tiếng Việt nét đơn vào API Gateway `/api/ai/generate` và tích hợp hiển thị preview SVG (TV4)

#### 3.3 Tích hợp máy vẽ vật lý
**Trạng thái:** ⬜ Chưa bắt đầu | **Phụ trách:** TV3 + TV4 | **Mức ưu tiên:** P0
- [ ] Giao diện gửi lệnh vẽ thật xuống máy qua API Gateway, nhận trạng thái thật về
- [ ] Test các trường hợp lỗi thật (mất kết nối cáp, kẹt giấy...) xem hệ thống phản ứng đúng mã lỗi

#### 3.4 Test end-to-end toàn hệ thống
**Trạng thái:** ⬜ Chưa bắt đầu | **Phụ trách:** Cả nhóm (TV4 điều phối)
- [ ] Chạy thử toàn bộ luồng từ nhập văn bản/prompt đến lúc máy vẽ hoàn tất bức vẽ thật, tối thiểu 5 lần với input khác nhau
- [ ] Ghi lại lỗi phát sinh vào `04_progress-log.md`, phân công owner sửa theo đúng phân quyền module

---

### Giai đoạn 4 — Hoàn thiện, Benchmark Thực nghiệm & Báo cáo NCKH

**Trạng thái:** ⬜ Chưa bắt đầu | **Hạn giai đoạn:** *(Tháng 8–12)*

#### 4.1 Benchmark Thực nghiệm Định lượng & Ablation Study — P0
**Trạng thái:** ⬜ | **Phụ trách:** Cả nhóm (TV4 lead framework thực nghiệm/runner/logging & handwriting metrics, TV2 lead phân tích thuật toán chuyển động, TV3 lead đo máy)

##### A. Thực nghiệm Tối ưu đường vẽ tranh (Line-art Art Mode) — P1 (TV2 lead)
- [ ] Chạy bộ thực nghiệm định lượng so sánh **3 phương pháp đường vẽ tranh**:
  1. *Baseline 1 (Naive / Original Order):* Thứ tự contour nguyên bản trích từ ảnh, không tối ưu pen-up.
  2. *Baseline 2 (Greedy Nearest Neighbor):* Chọn nét kế tiếp gần nhất theo khoảng cách Euclid đơn thuần.
  3. *Phương pháp tối ưu OmniDraw:* Thuật toán `cKDTree + Or-opt + Kinematic Turn Penalty`.
- [ ] Hệ chỉ số đo đạc: tổng chiều dài nhấc bút ($mm$), số lần nhấc bút, thời gian tính toán ($ms$), và độ mượt góc đổi hướng.
- [ ] Đo lường độ chính xác nắn thẳng giấy tự động của module thị giác máy tính ($MAE$ góc nghiêng $\Delta\theta$).

##### B. Thực nghiệm Tối ưu chữ viết tay CA-VHC (Handwriting Mode) — P0 (TV4 lead composition & runner, TV2 lead motion metrics)
- [ ] Chạy bộ thực nghiệm đối sánh trên cùng tập corpus văn bản chuẩn với **3 phương pháp đối chứng (Baselines)**:
  1. *Baseline 1 (Static Glyph Renderer):* Bộ render glyph tĩnh (không có biến thể allographs ngữ cảnh, không nối nét động).
  2. *Baseline 2 (Greedy Heuristic):* Lựa chọn biến thể và quyết định nối nét theo thuật toán tham lam bước kế tiếp gần nhất (Greedy contextual/connection heuristic).
  3. *Baseline 3 (Current Trellis DAG):* Giải thuật Trellis DAG Viterbi DP hiện tại (chưa có ràng buộc dấu nâng cao).
- [ ] Đánh giá đối chứng với **Phương pháp đề xuất (Proposed CA-VHC)**: CA-VHC mở rộng tích hợp ràng buộc dấu tiếng Việt theo chính tả/âm tiết, thứ tự nét trễ (delayed-stroke ordering) và chi phí động học máy vẽ (đây là phương pháp nghiên cứu đề xuất của nhóm, không tính là baseline đối chứng thứ tư).
- [ ] Đo đạc và đối sánh hệ chỉ số: tổng chiều dài nét ($mm$), quãng đường nhấc bút ($mm$), số lần nhấc bút, thời gian tính toán giải thuật ($ms$), tỷ lệ va chạm hình học giữa dấu và nét chữ, độ liên tục tiếp tuyến $C^1$.
- [ ] Thực hiện **Ablation Study** đánh giá mức độ đóng góp của từng thành phần trong hàm mục tiêu $J$: bóc tách lần lượt contextual allograph cost, collision cost, curvature cost, legibility cost, diacritic constraints và kinematic cost.

##### C. Khảo sát Đánh giá Người dùng (User Evaluation Protocol) — P0 / P1
- [ ] Xây dựng protocol khảo sát người dùng có kiểm soát (User Study) với 30–50 người tham gia, tuân thủ tiêu chuẩn đạo đức nghiên cứu (thông tin ẩn danh, có sự đồng ý tham gia).
- [ ] Đánh giá định lượng theo thang đo Likert (1–5) về:
  - Độ tự nhiên của nét chữ viết tay nét đơn;
  - Độ dễ đọc (Legibility);
  - Mức độ phù hợp với loại văn bản/thư tín (Context appropriateness);
  - Tính đồng nhất phong cách người viết.

##### D. Thực nghiệm thi công vật lý trên máy AxiDraw — P0
- [ ] Đo đạc thời gian thi công thực tế `actual_draw_time_sec` trên máy vẽ thật đối chiếu với thời gian mô phỏng lý thuyết.
- [ ] Đo lường sai số quỹ đạo vật lý và kiểm tra độ bền cơ học của ngòi bút trên bề mặt giấy A4.

#### 4.2 Demo & Video minh họa — P1
**Trạng thái:** ⬜ | **Phụ trách:** TV4 (điều phối)
- [ ] Quay video minh hoạ toàn bộ quy trình từ nhập prompt/văn bản đến lúc máy vẽ hoàn tất bức thư nghệ thuật.
- [ ] Chuẩn bị kịch bản demo trực tiếp (chữ hoa mở đầu, nét nối tự nhiên, thi công máy vẽ mượt mà).

#### 4.3 Báo cáo khoa học (Chuẩn mực Báo cáo NCKH 5 chương) — P0
**Trạng thái:** ⬜ | **Phụ trách:** Mỗi người viết phần mình, TV4 tổng hợp & biên tập
- [ ] Xây dựng Báo cáo NCKH chuẩn cấu trúc 5 chương học thuật:
  - **Chương 1: Mở đầu** (Bối cảnh, tính cấp thiết, mục tiêu đề tài và 3 câu hỏi nghiên cứu RQ1, RQ2, RQ3).
  - **Chương 2: Tổng quan & Cơ sở lý thuyết** (Nghiên cứu liên quan về vector hóa ảnh, tối ưu hóa quỹ đạo nét và sinh chữ viết tay nét đơn cho máy vẽ).
  - **Chương 3: Phương pháp & Thiết kế Thuật toán CA-VHC** (Mô hình hóa Trellis DAG, hàm mục tiêu đa tiêu chí $J$, thuật toán Viterbi DP, quy tắc xử lý dấu tiếng Việt theo chính tả và âm tiết, thứ tự nét trễ).
  - **Chương 4: Thực nghiệm & Đánh giá kết quả** (Kết quả benchmark đối sánh CA-VHC với 3 baseline đối chứng, kết quả bộ đối sánh Art Mode, đồ thị Ablation Study, kết quả khảo sát người dùng Likert, số liệu thời gian vẽ thực tế trên AxiDraw).
  - **Chương 5: Kết luận & Hướng phát triển** (Tóm tắt đóng góp, hạn chế kỹ thuật, định hướng Writer Profile và phân trang đa trang).
- [ ] Bổ sung mô hình hóa toán học hình thức: Phương trình Bellman của Viterbi DP, biểu thức hàm phạt quán tính Kinematic Cost, phân tích độ phức tạp thuật toán Big-O.
- [ ] Biên tập thống nhất văn phong học thuật, kiểm tra đạo văn và chuẩn hóa trích dẫn tài liệu tham khảo theo IEEE/APA.

#### 4.4 Slide thuyết trình & Bảo vệ đề tài — P0
**Trạng thái:** ⬜ | **Phụ trách:** Cả nhóm
- [ ] Xây dựng slide trình bày cô đọng, nêu bật đóng góp thuật toán và kết quả thực nghiệm.
- [ ] Phân công thuyết trình theo đúng 4 mảng chuyên môn, diễn tập trả lời các câu hỏi phản biện từ hội đồng khoa học.