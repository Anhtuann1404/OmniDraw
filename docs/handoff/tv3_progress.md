# Nhật ký tiến độ và bàn giao của TV3 — Oracle Độc Lập và Kiểm Chứng

## 1. Xác nhận nhận nhiệm vụ Oracle độc lập & Trạng thái Gate Q01

- **Owner:** TV3 (Kiểm chứng độc lập hình học/lịch trình & Thẩm định phần cứng).
- **Trạng thái Gate Q01:** **CLOSED_STEP_VERIFIED** (Nhận việc đã được xác minh và đóng riêng bước này. Nghiệm thu oracle và các gate khác vẫn **PENDING**; chưa merge hoặc dùng làm ground truth nghiệm thu DP).
- **Xác nhận phân công:** TV3 thực hiện nhiệm vụ xây dựng bộ kiểm chứng oracle và các primitive hình học độc lập theo phân công của trưởng nhóm tại [Docs 30](../30_research_development_plan.md) §2 và [Docs 31](../31_joint_solver_contract.md) §3, §7.
- **Không chờ máy:** Xác nhận TV3 triển khai oracle phần mềm trên nhánh nghiên cứu độc lập, không chờ thiết bị AxiDraw vật lý.
- **Ranh giới độc lập:** Mã nguồn oracle độc lập được viết hoàn toàn mới từ đặc tả toán học trong Docs 31/32, đặt tại `backend/research/independent_oracle/`. **Tuyệt đối không import** `geometry.py`, `joint_dp.py`, `schedule_checker.py`, hoặc bất kỳ bảng cache feasibility / cost helper nào của TV4 / TV2.
- **Tách biệt phần cứng:** Công việc phần cứng vẫn duy trì độc lập tại working tree `D:\UED\NCKH\OmniDraw` (nhánh `feature/hardware`), giữ nguyên trạng thái `PENDING_TV3_CALIBRATION`. Không sử dụng số liệu simulator/fake làm số đo vật lý, không chạy lệnh vẽ vật lý để giải toán hoặc chứng nhận. HOLDOUT niêm phong vẫn đóng.

---

## 2. Báo cáo bàn giao theo mẫu chuẩn Docs 30 / 31 / 32 / Pending Decisions

```text
Owner / ID quyết định liên quan:
  TV3 (Oracle độc lập, Kiểm chứng hình học, Phần cứng) / Q01 (Nhận việc: ĐÃ ĐÓNG RIÊNG), Q02 (Lịch & J), Q04 (Contact & clearance), Q08 (Sai số số học), Q10 (Nghiệm thu DP đối chiếu oracle - PENDING).

Commit nền chia sẻ đã fetch / commit bàn giao:
  - Base commit TV4: 510f4e108d29d5597cb7e82ed3dd53d2ba5c806a (ancestor của shared HEAD)
  - Remote shared branch HEAD đã fetch: origin/codex/tv4-pr3-slices (9659946)
  - Nhánh làm việc TV3: codex/tv3-research-oracle-20261002 (worktree: D:\UED\NCKH\OmniDraw-tv3-research)
  - Commit trước: d84c241
  - Commit bàn giao cập nhật: (commit mới sửa 5 điểm review)

Contract/artifact version / policy IDs:
  - Contract version: joint-contract-v1-draft (Docs 31)
  - Artifact version: joint-artifact-v1-draft (Docs 32)
  - Geometry policy ID: tv4-dev-polyline-v1, tv4-dev-all-pairs-v1, tv4-dev-exact-endpoint-v1, tv4-dev-float-v1
  - Cost policy ID: tv4-dev-dyadic-primitive-cost-v1 (Docs 36 / Numeric Audit 20261002)
  - Tie policy ID: tv4-dev-dyadic-lex-actions-v2

Case/manifest/candidate/config hashes và split (DEV/synthetic):
  - Split: dev và synthetic (HOLDOUT niêm phong đóng hoàn toàn, kiểm tra split="holdout" lập tức reject ValueError)
  - Manifest fixtures đã kiểm thử:
    * tests/research/fixtures/solver_dev_cases.json (manifest_sha256: 921b2a37f4266cf62f6b03b9f2715ad3191becf45ad826080344e4baf96cfd9c)
    * tests/research/fixtures/method_gap_example.json (manifest_sha256: 28a1c97a82bcf23668e16eaecce03534b12e3e5bc3566191fbca2a04eb0868f0)
    * tests/research/fixtures/numeric_rounding_cases.json (manifest_sha256: 5eec56c7035f29d2b27a3c3aa41bf4d283cb73872bb5848bb37e1634fbca4912)

Đã làm / Sửa theo review TV4:
  1. Chi phí (Probe polyline nhiều đoạn):
     - Thay thế tích lũy float thô bằng math.fsum cho độ dài polyline và các tích lũy L_down, L_up.
     - delta chi phí từng bước tích lũy dưới dạng Fraction chính xác theo tv4-dev-dyadic-primitive-cost-v1.
     - Đã kiểm thử so khớp exact fraction với ScheduleReplay trên polyline 4 đoạn: trùng khớp tuyệt đối Fraction và binary64.
  2. Budget (max_states và memory limit):
     - Kiểm tra trần budget tại TỪNG state được khám phá (không kiểm thưa theo chu kỳ 500).
     - Với max_states=1: search dừng ngay tại state vượt ngưỡng, trả outcome="RESOURCE_LIMIT", search_complete=False (không báo nhầm OPTIMAL).
     - Tích hợp tracemalloc để theo dõi bộ nhớ thực tế và kích hoạt RESOURCE_LIMIT nếu vượt memory_limit_mb. Ghi nhận peak_memory_mb vào Metrics.
  3. Contract & Policies:
     - Bổ sung validate_contract_and_policies: lập tức từ chối ValueError với split="holdout", policy hình học ngoài danh mục DEV, c_min != 0.20 mm, contact policy không được hỗ trợ, hoặc vị trí contact không khớp đúng endpoint của nét.
  4. Provenance:
     - Thay thế commit nền tĩnh bằng git_snapshot() động lấy đúng commit HEAD chứa mã oracle và mã hóa dirty_patch_sha256 nếu có thay đổi chưa commit.
  5. Bounds (Cận bao ngoài):
     - Triển khai cost_interval(J_exact) tính cận bao ngoài binary64 [lo, hi] (dùng math.nextafter), đảm bảo lo <= J_exact <= hi.
     - Khi search bị gián đoạn (search_complete=False), lower_bound_J_mm được đặt là None, upper_bound_J_mm giữ giá trị incumbent nếu có.

Kiểm thử & Kết quả:
  - tests/research/test_independent_oracle_primitives.py: 22/22 tests PASS.
  - tests/research/test_independent_oracle_enumerator.py: 16/16 tests PASS (bổ sung test polyline nhiều đoạn, max_states=1, memory, holdout, policy invalid).
  - Toàn bộ suite tests/research: 215/215 tests PASS.

Checker/oracle identity và bằng chứng độc lập (hoặc NOT_RUN):
  - Oracle Identity: TV3 Independent Exhaustive Oracle (`tv3-oracle-dev-v1`).
  - Validation status trong SolveResult: giữ nguyên NOT_RUN trước khi checker độc lập thực hiện audit.

Bất đồng/counterexample, kết luận hiện tại và giới hạn:
  - Các điểm bất đồng số học và budget chỉ ra bởi TV4 đã được sửa và chứng minh bằng unit tests.
  - Bốn đỉnh DEV luôn NOT_CERTIFIED. Không tự nâng cấp thành nghiệm thu DP hay ground truth cho Holdout.

Gate vẫn PENDING / bước tiếp theo:
  - Q01: ĐÃ ĐÓNG RIÊNG bước nhận việc.
  - Q02, Q04, Q08, Q10: Tiếp tục PENDING chờ review chéo mã nguồn và kiểm chứng độc lập.
  - Chưa merge vào nhánh chính/develop và chưa mở HOLDOUT.
```
