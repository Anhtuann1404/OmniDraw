# Tiến độ và bàn giao TV1 — Candidate Dataset, Diacritics & Custody

Cập nhật: 03/10/2026. Owner: TV1 (Nguyễn Hoàng Thắng). Nhánh làm việc: `codex/tv1-research-candidates-20261002`.

---

### Mẫu bàn giao theo `docs/handoff/pending_decisions.md`

```text
Owner / ID quyết định liên quan:
  TV1 (Nguyễn Hoàng Thắng) / Q02, Q03, Q05, Q13 (đồng thời theo dõi Q01, Q06, Q10, Q16)

Commit nền chia sẻ đã fetch / commit bàn giao:
  Nền chia sẻ đã fetch: 5b0f328 (origin/codex/tv4-pr3-slices, là descendant của commit code 510f4e1)
  Commit bàn giao: HEAD trên nhánh codex/tv1-research-candidates-20261002

Contract/artifact version / policy IDs:
  Contract: joint-contract-v1-draft (Docs 31)
  Artifact: joint-artifact-v1-draft (Docs 32)
  Geometry policy: tv4-dev-polyline-v1, tv4-dev-float-v1, tv4-dev-all-pairs-v1
  Contact policy: tv4-dev-exact-endpoint-v1
  Floor: c_min_mm = 0.20 mm (không vi phạm, không trừ tolerance)

Case/manifest/candidate/config hashes và split (DEV/synthetic):
  Split: dev
  Manifest hash: c69090b7ceb1f7c70e7859836f82860111a19aecd7ff0800fbb7be8f7d8bbb81
  Files:
    - dataset/research/dev/tv1_dev_manifest.json
    - tests/research/fixtures/tv1_candidates_dev.json
  Cases & Candidate Set SHA-256:
    1. tv1-dev-stacked-diacritic-01 ("ấb", NFD: "ấb")
       -> candidate_set_sha256: 770ef1b33065854ce2a5646c68900572216911a7106a51681a67122ed10aa405
    2. tv1-dev-mark-below-02 ("ệc", NFD: "ệc")
       -> candidate_set_sha256: 0cefecccfbd17216ae7df5f6cbaa5a0561f59050ab5fc2b6a78866d985689067
    3. tv1-dev-distant-interaction-03 ("óto", NFD: "óto")
       -> candidate_set_sha256: aeb0e79d202f4fcccadb2e7b5d37c46df34a6f8af0f9cc2d22df373a5d33e039

Đã làm / chưa làm / phạm vi claim:
  Đã làm:
    1. Kiểm tra Git worktree sạch sẽ, bảo toàn nhánh cũ feature/tv1-data-corpus (commit 0cd03a9), mở worktree mới tại ../OmniDraw-tv1-research trên nhánh codex/tv1-research-candidates-20261002 từ origin/codex/tv4-pr3-slices.
    2. Đọc và đối chiếu toàn bộ 9 tài liệu quy định (Docs README, 03, 30, 31, 32, handoff README, pending_decisions, backend/research README, tests/research README).
    3. Rà soát fixtures DEV tự tạo của TV4: Xác nhận chúng là synthetic toy cases phục vụ kiểm thử solver recurrence/arithmetic của TV4, TV1 KHÔNG duyệt chúng là font/dataset chính thức.
    4. Lập trình module dataset/research/dev/candidate_builder.py xây dựng bộ ứng viên tiếng Việt chuẩn NFD, world-mm, có thứ tự nét thân (body_order) và quan hệ ưu tiên dấu (mark_precedence).
    5. Thiết kế đầy đủ các ca thử nghiệm thực tế:
       - Dấu chồng (stacked marks): 'ấb' với mũ (circumflex) và sắc (acute), bảo đảm thứ tự vẽ mũ trước sắc.
       - Dấu dưới (mark below): 'ệc' với mũ trên và dấu nặng dưới chân chữ (y < 0 mm).
       - Tương tác xa & trễ k: 'óto' với dấu sắc có deadline k=2, cho phép hoãn vẽ dấu sau 2 thân chữ kế tiếp.
       - Nét đảo chiều: reversible=True cho các nét đối xứng/ngang và reversible=False cho nét cong.
       - Điểm tiếp xúc (contact): Khai báo đúng điểm mút endpoint trùng khớp [3.0, 3.5] trên chữ 't' với bán kính disk 0.25 mm.
    6. Tạo bộ test tests/research/test_tv1_candidates.py đạt 8/8 PASS, kiểm tra tương thích toàn diện với compile_geometry và solve_joint (cả no-forget và safe-forget).
    7. Chạy toàn bộ test suite nghiên cứu tests/research đạt 185/185 PASS và hồi quy handwriting validation đạt 34/34 PASS.
    8. Soạn thảo đề xuất quality bounds (Q03), bảng trễ k (Q05), và quy chế custody HOLDOUT niêm phong ngoài Git (Q13).
  Chưa làm:
    - Chưa mở tập HOLDOUT (chờ gate Q14).
    - Chưa mở rộng toàn bộ bảng âm vị tiếng Việt hoặc nạp font bên thứ ba (chờ kết quả S0/S1).
    - Chưa chạy trên máy vẽ thật (chờ phần cứng TV3).
  Phạm vi claim:
    - Khẳng định các ca DEV do TV1 tạo đạt 100% hợp lệ về mặt cấu trúc dữ liệu, hình học và thuật toán solver hiện tại trên DEV; không tuyên bố đã hoàn tất toàn bộ corpus tiếng Việt hay nghiệm thu font pilot.

Lệnh tái lập / môi trường / budget và stage timing:
  Lệnh tái lập:
    python dataset/research/dev/candidate_builder.py
    python -m pytest tests/research/test_tv1_candidates.py -v
    python -m pytest tests/research
    python -m pytest backend/test_handwriting_validation.py
  Môi trường: Windows 11, Python 3.13.14.
  Budget: wall_time_ms=10000, max_states=100000, max_configurations=10000, memory_limit_mb=64.
  Timing: test_tv1_candidates 0.53s, toàn bộ tests/research (185 tests) 15.27s.

Kết quả: feasibility, J, scope, complete flags; error/timeout/infeasible:
  - tv1-dev-stacked-diacritic-01: OPTIMAL, search_complete=True, scope=full_candidate_set, J_mm=13.06 mm, circumflex index < acute index (PASS precedence).
  - tv1-dev-mark-below-02: OPTIMAL, search_complete=True, scope=full_candidate_set, J_mm=17.51 mm, cả 2 dấu của 'e' hoàn tất trước khi vẽ 'c' (PASS k=0).
  - tv1-dev-distant-interaction-03: OPTIMAL, search_complete=True, scope=full_candidate_set, J_mm=17.84 mm, search_complete=True (PASS k=2 và contact endpoint).
  - Không có timeout, không infeasible, không lỗi bộ nhớ.

Checker/oracle identity và bằng chứng độc lập (hoặc NOT_RUN):
  - TV4 DEV Checker: check_selected_geometry đạt status: "PASS" trên cả 3 ca.
  - Oracle TV3 độc lập: NOT_RUN (chờ bàn giao S2 từ TV3).

Bất đồng/counterexample, kết luận hiện tại và giới hạn:
  - no-forget và safe-forget cho ra cùng kết quả tối ưu trên cả 3 ca của TV1.
  - Lưu ý về Contact Policy: Quy định tv4-dev-exact-endpoint-v1 bắt buộc vị trí tiếp xúc phải là một endpoint của CẢ HAI nét. TV1 đã chuẩn hóa chữ 't' để nét thân và thanh ngang gặp nhau tại đúng điểm đầu mút [3.0, 3.5], loại bỏ lỗi vị trí nằm giữa đoạn thẳng.

Đề xuất cần review / reviewer cần xác nhận:
  - Đề xuất Q03 (Quality Bounds trên DEV):
    + Khoảng hở: c_min = 0.20 mm cứng.
    + Giới hạn dịch dấu: Delta_y_mark in [0.15, 0.45] * x_height.
    + Giới hạn góc nghiêng: Delta_theta <= 5 độ.
    + Tỷ lệ khung chữ: Delta_AR <= 10%.
  - Đề xuất Q05 (Bảng k theo loại dấu):
    + Dấu cấu tạo (mũ, móc): k = 0 mặc định (hoặc k = 1 nếu có ligatures).
    + Dấu thanh (sắc, huyền, hỏi, ngã, nặng): k in {0, 1, 2}.
    + Mark precedence: Dấu cấu tạo PHẢI đi trước dấu thanh khi đi cùng một chữ cái.
  - Đề xuất Q13 (Custody & HOLDOUT Protocol):
    + Toàn bộ 20 từ DEV và 20 từ Holdout của Benchmark Corpus CA-VHC v1.0 cũ được phân loại thành "supplemental".
    + Tập HOLDOUT mới cho bài toán đồng tối ưu sẽ được niêm phong hoàn toàn ngoài Git dưới dạng manifest_sha256 được ký duyệt bởi 2 thành viên (TV1 + TV2/TV3), chỉ mở sau khi freeze code và tham số (Gate Q14).

Gate vẫn PENDING / bước tiếp theo:
  - Toàn bộ 16 quyết định Q01–Q16 vẫn PENDING.
  - Bước tiếp theo: Bàn giao kết quả slice S1 cho TV4, chờ TV3 xác nhận nhận oracle (Q01), TV2 triển khai baseline/runner (Q06/Q11).
```
