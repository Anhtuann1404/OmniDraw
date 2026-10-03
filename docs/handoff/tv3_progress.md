# Nhật ký tiến độ và bàn giao của TV3 — Oracle Độc Lập và Kiểm Chứng

## 1. Xác nhận nhận nhiệm vụ Oracle độc lập (Q01)

- **Owner:** TV3 (Kiểm chứng độc lập hình học/lịch trình & Thẩm định phần cứng).
- **Trạng thái:** **ACCEPTED / IMPLEMENTED_SLICE_1_AND_2**.
- **Xác nhận phân công:** TV3 chính thức nhận nhiệm vụ xây dựng bộ kiểm chứng oracle và các primitive hình học độc lập theo phân công của trưởng nhóm tại [Docs 30](../30_research_development_plan.md) §2 và [Docs 31](../31_joint_solver_contract.md) §3, §7.
- **Không chờ máy:** Xác nhận TV3 triển khai oracle phần mềm ngay trên nhánh nghiên cứu độc lập, không chờ thiết bị AxiDraw vật lý.
- **Ranh giới độc lập:** Mã nguồn oracle độc lập được viết hoàn toàn mới từ đặc tả toán học trong Docs 31/32, đặt tại `backend/research/independent_oracle/`. **Tuyệt đối không import** `geometry.py`, `joint_dp.py`, `schedule_checker.py`, hoặc bất kỳ bảng cache feasibility / cost helper nào của TV4 / TV2.
- **Tách biệt phần cứng:** Công việc phần cứng vẫn duy trì độc lập tại working tree `D:\UED\NCKH\OmniDraw` (nhánh `feature/hardware`), giữ nguyên trạng thái `PENDING_TV3_CALIBRATION`. Không sử dụng số liệu simulator/fake làm số đo vật lý, không chạy lệnh vẽ vật lý để giải toán hoặc chứng nhận. HOLDOUT niêm phong vẫn đóng.

---

## 2. Báo cáo bàn giao theo mẫu chuẩn Docs 30 / 31 / 32 / Pending Decisions

```text
Owner / ID quyết định liên quan:
  TV3 (Oracle độc lập, Kiểm chứng hình học, Phần cứng) / Q01 (Nhận oracle), Q02 (Lịch & J), Q04 (Contact & clearance), Q08 (Sai số số học), Q10 (Nghiệm thu DP đối chiếu oracle).

Commit nền chia sẻ đã fetch / commit bàn giao:
  - Base commit TV4: 510f4e108d29d5597cb7e82ed3dd53d2ba5c806a (ancestor của shared HEAD)
  - Remote shared branch HEAD đã fetch: origin/codex/tv4-pr3-slices (9659946)
  - Nhánh làm việc TV3: codex/tv3-research-oracle-20261002 (worktree: D:\UED\NCKH\OmniDraw-tv3-research)
  - Commit bàn giao: (Sẽ commit sau khi hoàn tất kiểm tra và ghi nhật ký)

Contract/artifact version / policy IDs:
  - Contract version: joint-contract-v1-draft (Docs 31)
  - Artifact version: joint-artifact-v1-draft (Docs 32)
  - Geometry policy ID: tv4-dev-polyline-v1, tv4-dev-all-pairs-v1, tv4-dev-exact-endpoint-v1, tv4-dev-float-v1
  - Cost policy ID: tv4-dev-dyadic-primitive-cost-v1 (Docs 36 / Numeric Audit 20261002)
  - Tie policy ID: tv4-dev-dyadic-lex-actions-v2

Case/manifest/candidate/config hashes và split (DEV/synthetic):
  - Split: dev và synthetic (HOLDOUT niêm phong đóng hoàn toàn)
  - Manifest fixtures đã kiểm thử:
    * tests/research/fixtures/solver_dev_cases.json (manifest_sha256: 921b2a37f4266cf62f6b03b9f2715ad3191becf45ad826080344e4baf96cfd9c)
    * tests/research/fixtures/method_gap_example.json (manifest_sha256: 28a1c97a82bcf23668e16eaecce03534b12e3e5bc3566191fbca2a04eb0868f0)
    * tests/research/fixtures/numeric_rounding_cases.json (manifest_sha256: 5eec56c7035f29d2b27a3c3aa41bf4d283cb73872bb5848bb37e1634fbca4912)

Đã làm / chưa làm / phạm vi claim:
  - ĐÃ LÀM:
    1. Thiết lập worktree độc lập `OmniDraw-tv3-research` tại `codex/tv3-research-oracle-20261002`.
    2. Triển khai gói primitive hình học độc lập `backend/research/independent_oracle/primitives.py`:
       * Khoảng cách điểm-đoạn, đoạn-đoạn với kiểm tra overflow/NaN/Inf.
       * Giao cắt đoạn thẳng, xử lý điểm suy biến (degenerate point) và đoạn thẳng cộng tuyến (collinear overlap/disjoint).
       * Tự cắt (self-intersection) của polyline theo quy tắc Docs 31 (cho phép đỉnh chung kế tiếp, cấm gập ngược 180 độ).
       * Vùng tiếp xúc hữu hạn (contact disk clipping): cắt bỏ phần polyline nằm trong đĩa B(location, radius), đo khoảng cách ngoài đĩa.
       * Kiểm tay ngưỡng c_min = 0.20 mm: 0.19 mm (INFEASIBLE), 0.20 mm (FEASIBLE boundary), 0.21 mm (FEASIBLE).
    3. Triển khai bộ vét cạn độc lập `backend/research/independent_oracle/enumerator.py`:
       * Vét cạn toàn bộ cấu hình tích Descartes của các variants.
       * Kiểm tra tính khả thi hình học (tự cắt + khoảng cách all-pairs có ngoại lệ đĩa tiếp xúc).
       * Sinh lịch hợp lệ: thân trái sang phải, thứ tự thân nội bộ theo variant, dấu sau thân sở hữu, tiền định (precedence) giữa các dấu, deadline k(j) tính theo số thân kế tiếp hoàn tất.
       * Đảo chiều nét khi reversible=true.
       * Chuyển tiếp LIFT và CONNECT (CONNECT chỉ khi cùng tọa độ endpoint và có khai báo tiếp xúc hợp lệ).
       * Biên UP đầu/cuối: p0 -> nét đầu, nét cuối -> p_end; tính travel rỗng.
       * N_cycle bằng số đoạn vẽ liên tục tối đa (maximal pen-down runs).
       * Tính toán chi phí chính xác bằng Fraction: J = L_down + rho * L_up + lambda * N_cycle.
    4. Triển khai adapter chuẩn Docs 32 `backend/research/independent_oracle/adapter.py`:
       * solve_oracle_adapter trả về SolveResult chuẩn với đầy đủ outcome, scope=full_candidate_set, enumeration_complete=True, search_complete=True, bounds, metrics, provenance, validation=NOT_RUN.
    5. Xây dựng bộ kiểm thử độc lập:
       * `tests/research/test_independent_oracle_primitives.py` (22 tests PASS).
       * `tests/research/test_independent_oracle_enumerator.py` (10 tests PASS).
       * Toàn bộ test suite nghiên cứu `tests/research` đạt 209/209 tests PASS.
  - CHƯA LÀM / GIỚI HẠN CLAIM:
    * Chưa nghiệm thu toàn diện (human sign-off) cho toàn bộ phương pháp;
    * Bốn đỉnh DEV vẫn giữ chẩn đoán NOT_CERTIFIED;
    * Giới hạn phạm vi oracle: dành cho các ca nhỏ DEV (n <= 3, q <= 2, k <= 1, <= 6 actions) để làm ground truth đối chiếu cho DP; không khẳng định bộ vét cạn chạy được trên văn bản dài thời gian thực.
    * HOLDOUT niêm phong vẫn đóng.

Lệnh tái lập / môi trường / budget và stage timing:
  - Môi trường: Windows 11, Python 3.14.2, pytest 9.1.1.
  - Lệnh chạy primitive tests:
      $env:PYTHONPATH="backend"; python -m pytest tests/research/test_independent_oracle_primitives.py -v
  - Lệnh chạy enumerator & cross-validation tests:
      $env:PYTHONPATH="backend"; python -m pytest tests/research/test_independent_oracle_enumerator.py -v
  - Lệnh chạy toàn bộ suite nghiên cứu:
      $env:PYTHONPATH="backend"; python -m pytest tests/research -q
  - Kết quả timing: 32 tests oracle chạy trong ~0.51s; toàn bộ 209 tests chạy trong 4.88s.

Kết quả: feasibility, J, scope, complete flags; error/timeout/infeasible:
  - Empty case: OPTIMAL, L_down=0, L_up=dist(p0, p_end), N_cycle=0, J=rho*L_up.
  - Clearance 0.19 mm: INFEASIBLE, schedule=None.
  - Clearance 0.20 mm / 0.21 mm: FEASIBLE.
  - solver_dev_cases (stacked-3, empty): Đối chiếu với TV4 DP solver cho kết quả TRÙNG KHỚP TUYỆT ĐỐI về feasibility, optimal J, L_down, L_up, N_cycle.
  - method_gap_example: Trùng khớp nhân chứng Docs 36: chọn ứng viên 'a-delayed' với lịch thực hiện dấu trễ ('a-delayed', True), J đạt tối ưu toàn cục.
  - numeric_rounding_cases: Xử lý chính xác stress-test độ chính xác cao lambda=2^53.

Checker/oracle identity và bằng chứng độc lập (hoặc NOT_RUN):
  - Oracle Identity: TV3 Independent Exhaustive Oracle (`tv3-oracle-dev-v1`).
  - Validation status trong SolveResult: giữ nguyên NOT_RUN trước khi checker độc lập thực hiện audit.

Bất đồng/counterexample, kết luận hiện tại và giới hạn:
  - Không phát hiện bất đồng (disagreement) giữa Oracle TV3 và TV4 Joint DP trên các ca kiểm thử solver_dev_cases, method_gap_example, và numeric_rounding_cases.
  - Các phép tính tay biên 0.19 / 0.20 / 0.21 mm và tiếp xúc đĩa 0.25 mm hoàn toàn khớp đặc tả hình học.

Đề xuất cần review / reviewer cần xác nhận:
  - TV4 review đối chiếu logic hình học và giải thuật vét cạn trong `backend/research/independent_oracle/`.
  - TV2 sử dụng kết quả oracle TV3 làm ground-truth đối chứng khi đánh giá chất lượng prefix top-m và beam search.
  - Đóng gate Q01 trong bảng quyết định PENDING.

Gate vẫn PENDING / bước tiếp theo:
  - Q01: Đề xuất đóng APPROVED sau khi TV4 và TV2 đối soát biên bản này.
  - Q02, Q04, Q08, Q10: Tiến tới đối soát toàn diện trước khi freeze DEV.
  - Bước tiếp theo của TV3: Tiếp tục bổ sung các fixture kiểm thử ca biên khó (stress tests với tương tác xa, tie-breaking đa tầng) và duy trì sự sẵn sàng của quy trình hiệu chuẩn phần cứng khi có thiết bị.
```
