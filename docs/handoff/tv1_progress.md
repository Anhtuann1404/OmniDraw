# Tiến độ và bàn giao TV1 — Candidate Dataset, Diacritics & Custody

Cập nhật: 03/10/2026. Owner: TV1 (Nguyễn Hoàng Thắng). Nhánh làm việc: `codex/tv1-research-candidates-20261002`.

---

### Mẫu bàn giao theo `docs/handoff/pending_decisions.md`

```text
Owner / ID quyết định liên quan:
  TV1 (Nguyễn Hoàng Thắng) / Q02, Q03, Q05, Q13 (đồng thời theo dõi Q01, Q06, Q10, Q16)

Commit nền chia sẻ đã fetch / commit bàn giao:
  Nền chia sẻ đã fetch: 5b0f328 (origin/codex/tv4-pr3-slices) -> merge review cb38f64 tại commit ff23687
  Commit bàn giao: HEAD trên nhánh codex/tv1-research-candidates-20261002

Contract/artifact version / policy IDs:
  Contract: joint-contract-v1-draft (Docs 31)
  Artifact: joint-artifact-v1-draft (Docs 32)
  Geometry policy: tv4-dev-polyline-v1, tv4-dev-float-v1, tv4-dev-all-pairs-v1
  Contact policy: tv4-dev-exact-endpoint-v1
  Cost policy: tv4-dev-dyadic-primitive-cost-v1
  Floor: c_min_mm = 0.20 mm (không vi phạm, không trừ tolerance)

Case/manifest/candidate/config hashes và split (DEV/synthetic):
  Split: dev
  Manifest hash: 4c62fa2e7a4bdfd297e9d959062f450900bcd5a52ef1150cdbaecfec0b047993
  Evidence file: docs/evidence/tv1_dev_cases_evidence.json
  Files:
    - dataset/research/dev/tv1_dev_manifest.json
    - tests/research/fixtures/tv1_candidates_dev.json
  Cases & Candidate Set SHA-256:
    1. tv1-dev-stacked-diacritic-01 ("ấb", NFD: "ấb")
       -> candidate_set_sha256: c82721ba2bc0b188ae8d88e45e4c9edc33f84ee8654144b3e9fddcb04f587e8f
    2. tv1-dev-mark-below-02 ("ệc", NFD: "ệc")
       -> candidate_set_sha256: 914921136540b63316992152eb8b7d3f83b040f92fc635f296b985a4bfb1b134
    3. tv1-dev-distant-interaction-03 ("óto", NFD: "óto")
       -> candidate_set_sha256: fb4310c99665ffbcb2f11f7113993fed6d54b72a14295bde78051c2776a46495
    4. tv1-dev-distant-interaction-04 ("óto", NFD: "óto" với flourished variants)
       -> candidate_set_sha256: ab52b46eca6cb14c152a37d0e21a76399780f7503f984eb75a9d5a4574d8d9a4

Đã làm / chưa làm / phạm vi claim:
  Đã làm (xử lý toàn diện F1–F7 theo phiếu review cb38f64 và rereview c970a18 của TV4):
    1. [F1 - CLOSED] Khắc phục triệt để sai lệch J: Xác minh nguồn gốc số cũ (13.06, 17.51, 17.84) là từ prototype chưa cộng chi phí chuyển nét lambda * N_cycle. Tái chạy nghiệm thu chuẩn và trích xuất artifact docs/evidence/tv1_dev_cases_evidence.json chứa đúng float precision và exact rational ratios khớp 100% kết quả TV4 (TV4 xác nhận F1 CLOSED).
    2. [F2 - CLOSED] Minh bạch xuất xứ ứng viên DEV: Làm rõ toàn bộ glyph DEV là bộ tham số tổng hợp do TV1 tự tạo (hand-authored parametric polylines, CC-BY-4.0), sử dụng hàm authoring_digest; đặt reference_geometry: null tránh ngộ nhận là trích xuất từ font Open Sans thực tế khi chưa qua Font Pilot (Q16) (TV4 xác nhận F2 CLOSED).
    3. [F3 - CLOSED] Thiết kế ca kiểm thử ranh giới trễ k=2 so với k=1: Xây dựng test_tv1_delay_k_two_body_boundary probe lịch body0 -> t_stem -> t_crossbar -> body2 -> tone0 (hoãn vẽ dấu sau 2 thân chữ hoàn tất), kiểm chứng strictly PASS tại k=2 nhưng FAIL tại k=1 và k=0 với ngoại lệ deadline (TV4 xác nhận F3 CLOSED).
    4. [F4 - CLOSED] Xây dựng ca tương tác xa thực thụ (Case 04): Bổ sung tv1-dev-distant-interaction-04 với biến thể nét uốn lượn (swash/flourish) giữa owner 0 và owner 2 có clearance 0.10 mm < c_min = 0.20 mm, tạo cạnh đồ thị future_neighbors = {0: [2], 2: [0]}, kích hoạt cơ chế giữ frontier và prune cặp xung đột trong DP. Đồng thời chuẩn hóa phạm vi claim của Case 03 là fixture đa thân hoãn dấu (delayed-mark) (TV4 xác nhận F4 CLOSED).
    5. [F5 - CLOSED] Kiểm chuẩn tiếp xúc hình học và chuyển tiếp CONNECT: Tách biệt rõ ràng claim "tiếp xúc hình học hợp lệ" khỏi "lịch chuyển tiếp CONNECT". Viết test_tv1_contact_and_connect_traversal kiểm chứng cả ca dương tính CONNECT (delta_up_mm = 0, delta_cycles = 0) và các ca âm tính khi thiếu whitelist hoặc lệch endpoint (TV4 xác nhận F5 CLOSED).
    6. [F6 - RESOLVED] Đo đạc và định nghĩa chất lượng Q03 chặt chẽ: Phân định rạch ròi giữa chiều cao thân chuẩn x-height h_x (áp dụng cho nguyên âm) và body bbox height h_bbox (áp dụng cho phụ âm/ascender như 'b', 't'); giới hạn nhãn ĐẠT ở khoảng hở thẳng đứng dương Delta_y_mark; ghi nhận NOT_EVALUATED cho góc nét Delta_theta do chưa có font tham chiếu và chính sách hồi quy tự động. Xác định chính xác các biến thể o-swash (+163.33%) và o2-flourish (+45.00%) KHÔNG ĐẠT tiêu chuẩn Delta_AR <= 10% và sẽ bị bộ lọc typography loại bỏ trước khóa tập G; trong DEV chúng được gán nhãn ngoại lệ DEV_ONLY_INTERACTION_PROBE_EXEMPT để phục vụ thử nghiệm frontier DP của TV4. Giữ toàn bộ bounds ở mức PROPOSED / PENDING.
    7. [F7 - RESOLVED] Chuẩn hóa metadata và provenance bằng chứng số học: Cập nhật docs/evidence/tv1_dev_cases_evidence.json gắn chính xác source_input_commit c970a18a706b983fc8fda3659aa7c16e836b3c72 chứa đúng 4 ca manifest canonical hash 4c62fa2e..., ghi nhận đầy đủ môi trường, lệnh tái lập và budget.
    8. Bộ test tests/research/test_tv1_candidates.py đạt 13/13 PASS; toàn bộ suite tests/research đạt 190/190 PASS.
  Chưa làm:
    - Chưa mở tập HOLDOUT (chờ gate Q14 freeze).
    - Chưa nạp font bên thứ ba hoặc đo H_geom (chờ Font Pilot Q16).
    - Chưa chạy trên máy vẽ thật (chờ phần cứng TV3).
  Phạm vi claim:
    - Các ca DEV của TV1 là baseline hình học và fixture phục vụ kiểm thử solver/DP; không tuyên bố là bộ font hoàn chỉnh hay dataset chữ viết tay chính thức của đề tài.

Lệnh tái lập / môi trường / budget và stage timing:
  Lệnh tái lập:
    python dataset/research/dev/candidate_builder.py
    python -m pytest tests/research/test_tv1_candidates.py -v
    python -m pytest tests/research -q
  Môi trường: Windows 11, Python 3.13.14.
  Budget: wall_time_ms=10000, max_states=100000, max_configurations=10000, memory_limit_mb=64.
  Timing: test_tv1_candidates (13 tests) 0.54s, toàn bộ tests/research (190 tests) 7.05s.

Kết quả: feasibility, J, scope, complete flags; error/timeout/infeasible:
  - tv1-dev-stacked-diacritic-01: OPTIMAL, search_complete=True, scope=full_candidate_set,
    L_down=15.338315569973318, L_up=8.816578365470374, N_cycle=4, J_mm=27.746604752708503,
    exact_ratio="999676790600755641/36028797018963968"
  - tv1-dev-mark-below-02: OPTIMAL, search_complete=True, scope=full_candidate_set,
    L_down=12.23421246039155, L_up=12.84899559237939, N_cycle=4, J_mm=26.658710256581244,
    exact_ratio="240120315155434627/9007199254740992"
  - tv1-dev-distant-interaction-03: OPTIMAL, search_complete=True, scope=full_candidate_set,
    L_down=16.337541126091548, L_up=15.269925772104335, N_cycle=5, J_mm=33.972504012143716,
    exact_ratio="305997112819866239/9007199254740992"
  - tv1-dev-distant-interaction-04: OPTIMAL, search_complete=True, scope=full_candidate_set,
    L_down=12.892953165265947, L_up=10.050778301982978, N_cycle=4, J_mm=25.918342316257434,
    exact_ratio="233451673595115887/9007199254740992"
  - Không có timeout, không infeasible, không lỗi bộ nhớ. Cả 2 mode no-forget và safe-forget đạt cùng exact internal objective trên mọi ca.

Checker/oracle identity và bằng chứng độc lập (hoặc NOT_RUN):
  - TV4 DEV Checker: check_selected_geometry đạt status: "PASS" trên cả 4 ca.
  - Oracle TV3 độc lập: NOT_RUN (chờ phân công và chuyển giao custody chính thức).

Bất đồng/counterexample, kết luận hiện tại và giới hạn:
  - no-forget và safe-forget đồng thuận hoàn toàn trên cả 4 ca DEV.
  - Trên ca 04, đồ thị future_neighbors = {0: [2], 2: [0]} hoạt động đúng: DP đã loại trừ cặp không tương thích (o-swash, o2-flourish) và tìm ra nghiệm tối ưu hợp lệ.

Đề xuất cần review / reviewer cần xác nhận:
  - Toàn văn đề xuất cập nhật tại: docs/handoff/tv1_proposals_q03_q05_q13.md
  - Bảng đo đạc thực nghiệm các ứng viên DEV chứng minh tuân thủ các ngưỡng đề xuất.
  - Giữ toàn bộ tham số ở trạng thái PROPOSED / PENDING.

Gate vẫn PENDING / bước tiếp theo:
  - Toàn bộ 16 quyết định Q01–Q16 vẫn PENDING (trong đó Q03, Q05, Q13 tiếp tục chờ thẩm duyệt đa phương).
  - Bước tiếp theo: Bàn giao commit, artifact bằng chứng và bảng xử lý F1–F7 cho TV4 re-review; chờ TV3 nhận oracle (Q01), TV2 triển khai runner (Q06/Q11).
```

---

## Bảng tổng hợp trạng thái phản biện TV4 (F1 – F7)

| Finding | Nội dung phản biện TV4 | Trạng thái | Biện pháp xử lý của TV1 | Tệp liên quan & Bằng chứng |
| :--- | :--- | :---: | :--- | :--- |
| **F1** (P1) | $J$ trong handoff không khớp commit/theta bàn giao (13.06/17.51/17.84 mm). | **CLOSED** | Tái tính toán chính xác trên cả 4 ca, xuất file bằng chứng số học chuẩn `docs/evidence/tv1_dev_cases_evidence.json`, cập nhật handoff đúng float precision và exact rational ratios (TV4 đã đối chiếu khớp 100%). | `docs/evidence/tv1_dev_cases_evidence.json`<br>`docs/handoff/tv1_progress.md` |
| **F2** (P2) | Hash nguồn/reference là hash của tên; chưa chứng minh nguồn font. | **CLOSED** | Minh bạch toàn bộ glyph DEV là bộ tham số nhân tạo do TV1 tự tạo (hand-authored polylines, CC-BY-4.0); đặt `reference_geometry: None` và `authoring_digest` để tránh trích dẫn font giả định khi chưa qua Font Pilot (Q16). | `dataset/research/dev/candidate_builder.py`<br>`dataset/research/dev/tv1_dev_manifest.json` |
| **F3** (P2) | Test $k=2$ chưa phân biệt được với $k=1$ do chỉ hoãn qua một thân chữ cái. | **CLOSED** | Xây dựng test probe `body0 -> t_stem -> t_crossbar -> body2 -> tone0` hoãn dấu sau 2 thân chữ: strictly PASS tại $k=2$, FAIL tại $k=1$ và $k=0$ với ngoại lệ deadline. | `tests/research/test_tv1_candidates.py` (`test_tv1_delay_k_two_body_boundary`) |
| **F4** (P2) | Fixture "distant interaction" có đồ thị tương tác rỗng, không kích hoạt frontier DP. | **CLOSED** | Chuẩn hóa Case 03 thành fixture đa thân hoãn dấu; bổ sung Case 04 (`tv1-dev-distant-interaction-04`) với các biến thể va chạm clearance ($0.10\,\text{mm} < 0.20\,\text{mm}$), tạo cạnh `{0: [2], 2: [0]}` và prune cặp không khả thi. | `dataset/research/dev/candidate_builder.py`<br>`tests/research/test_tv1_candidates.py` (`test_tv1_distant_interaction_frontier_and_solve`) |
| **F5** (P2) | Traversal stem -> crossbar không thể thực hiện CONNECT; test chỉ kiểm contact count. | **CLOSED** | Tách bạch claim tiếp xúc hình học khỏi chuyển tiếp CONNECT; bổ sung test kiểm chứng chuyển tiếp CONNECT dương tính (delta_up = 0) và âm tính (thiếu whitelist / endpoint lệch). | `tests/research/test_tv1_candidates.py` (`test_tv1_contact_and_connect_traversal`) |
| **F6** (P2) | Bảng đo chưa chứng minh tuân thủ toàn bộ bounds Q03; o-swash/o2-flourish vượt ngưỡng 10% $\Delta\text{AR}$; nhầm x-height cho ascender; chưa đo góc nét $\Delta\theta$. | **RESOLVED** | Phân định $x$-height $h_x$ và body bbox height $h_{\text{bbox}}$; giới hạn nhãn ĐẠT ở clearance dọc; đánh dấu `NOT_EVAL` cho góc nét; xác định chính xác `o-swash` (+163.33%) và `o2-flourish` (+45.00%) vượt ngưỡng $\Delta\text{AR} \le 10\%$, gán nhãn ngoại lệ `DEV_ONLY_INTERACTION_PROBE_EXEMPT` với ngữ nghĩa bị loại trước khóa $\mathcal{G}$ nếu áp bộ lọc chất lượng. Giữ bounds PROPOSED/PENDING. | `docs/handoff/tv1_proposals_q03_q05_q13.md`<br>`docs/handoff/tv1_progress.md` |
| **F7** (P2) | Evidence ghi `head_commit=ff23687` (chứa manifest 3 ca cũ), không chỉ rõ commit snapshot đã chạy. | **RESOLVED** | Cập nhật `docs/evidence/tv1_dev_cases_evidence.json` ghi nhận rõ `source_input_commit: c970a18a706b983fc8fda3659aa7c16e836b3c72`, `manifest_canonical_sha256: 4c62fa2e...`, đầy đủ lệnh và môi trường chạy nghiệm thu. | `docs/evidence/tv1_dev_cases_evidence.json`<br>`docs/handoff/tv1_progress.md` |
