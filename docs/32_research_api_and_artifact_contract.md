# Giao diện nghiên cứu và artifact contract

**Version:** `joint-artifact-v1-draft`, 02/10/2026. **Owner:** TV4 API/schema; TV2 runner/result; TV1 manifest; TV3 oracle/hardware.

**Status:** IMPLEMENTED_GATEWAY / DEV_DP_IMPLEMENTED / REVIEW_PENDING, 02/10/2026. Lớp API/schema/manifest/adapter đã có trong `backend/research/` và gắn vào `backend/main.py`. Có GET `/api/research/capabilities`, POST `/validate`, `/solve`, `/certify`. Chưa có adapter joint/baseline/oracle/certifier được đăng ký mặc định; solve/certify trả 503 cho case khả dụng khi thiếu implementation. Đây không là nghiệm thu thuật toán hay chứng nhận. Không gửi payload này vào `/api/ai/generate`. Hướng dẫn dùng và bàn giao: [Docs 34](support/34_research_api_gateway_implementation.md).

## 1. Kiến trúc và giao diện dự kiến

`manifest + glyph candidates -> solve request -> DP/oracle/top-m/beam -> schedule + metrics + provenance -> independent validation -> SVG/export`.

| Interface nội bộ dự kiến | Input → output | Owner | HTTP nếu triển khai sau |
|---|---|---|---|
| validate_case | ResearchCase → structural status/errors | TV4 schema; TV1 IDs; TV3 independent checker | POST /api/research/validate (đã có gateway) |
| solve_case | SolveRequest → SolveResult | TV4 joint; TV3 oracle; TV2 baselines | POST /api/research/solve |
| run_manifest | locked manifest → per-case JSONL + summary | TV2 | CLI/offline ưu tiên; không cần UI mở Holdout |
| certify_schedule | fixed schedule + domain → vertex evidence | TV4 + TV2 | POST /api/research/certify |
| font_pilot | licensed selected font → candidates/QC report | TV1 + TV4 | Offline trước; chưa có public TTF upload |

MVP gateway gọi adapter đồng bộ qua threadpool FastAPI. API giới hạn kích thước request và từ chối budget vượt trần; adapter phải thực thi giới hạn thời gian/state/memory bên trong solver. Gateway chưa là worker có thể cưỡng bức dừng tiến trình. Nếu chuyển job dài sang HTTP, phải đặc tả job_id, queued/running/completed/cancelled, polling/cancellation và artifact ACL riêng trước code; không dùng status printing của HAL cho solver job. API sản phẩm giữ sinh SVG/print/history như trước, không trigger physical draw từ solve/certify.

## 2. ResearchCase — schema thiết kế

| Field | Kiểu / ràng buộc | Nghĩa |
|---|---|---|
| schema_version | literal joint-artifact-v1-draft | Phiên bản contract, sau review mới freeze v1 |
| case_id, dataset_version, manifest_sha256 | string không rỗng | ID/hash thực; ví dụ không là hash đã đăng ký |
| split | dev / holdout / supplemental / synthetic | 20 từ cũ chỉ supplemental, không đổi tên để tạo Holdout mới |
| normalized_text, normalization | string; NFD | Giữ original_text/hash nguồn theo manifest khi có |
| candidates | array các chữ/ứng viên | ID ổn định; coordinates world-mm hữu hạn; nét có stroke_id, body/mark, owner_index, reversible, polyline_mm; body_order; mark precedence |
| contacts | array cặp ID + endpoint/location + tolerance policy | Whitelist cụ thể, không global allow_overlap |
| delay_policy | mark_id/type → nonnegative integer k | Đơn vị thân chữ theo Docs 31 |
| geometry_policy | c_min_mm=0.20, flatten/contact/numeric tolerance IDs | Dung sai/exception khóa trước freeze |
| boundary | p0_mm, p_end_mm, pen states UP, convention_id | N_cycle theo các maximal pen-down runs |
| reference_geometry | glyph/default anchors + source hash, mapping policy | H_geom độc lập optimum/Holdout |
| candidate_set_sha256 | string | Geometry sau style và finite choices, cùng cho mọi method |

Không nhận NaN/Infinity, bool thay number/integer, duplicate IDs, owner ngoài range, cycle precedence, empty polyline không có quy ước, coordinates thiếu, k âm, missing license cho public font pilot. Strict validation phải độc lập và diễn ra trước artifact/log side effect; semantic constraints cần checker, không chỉ JSON Schema.

### Schema lồng nhau và indexing (draft cần S0 review)

- `candidates`: array có một entry cho mỗi chữ, theo `owner_index` liên tiếp từ 0. Một chữ là đơn vị base+combining marks theo mapping grapheme đã khóa, không phải mỗi code point NFD; dấu kết hợp không tạo body mới. Entry có `owner_index`, `grapheme`, `variants` không rỗng. Mỗi variant có `candidate_id`, `source_hash`, `strokes`, `body_order` và `mark_precedence`.
- `strokes`: array `{stroke_id, role, owner_index, reversible, polyline_mm}`. role là body/mark (bridge chỉ khi khai báo thành nét trước solve); polyline_mm là array ít nhất hai điểm `[x_mm,y_mm]` hữu hạn, zero-length cần policy rõ. stroke_id độc nhất trong variant; cặp `(owner_index,candidate_id,stroke_id)` định danh nét toàn cục. Lịch chọn một variant/owner, không trộn thân của variant này với dấu của variant khác.
- `body_order`: array stroke IDs role body, chứa đủ body strokes đúng một lần. `mark_precedence`: array cặp `[before_id,after_id]` trong variant, không chu trình; delay_policy resolve mọi mark đã chọn qua ID/type cụ thể, quy tắc ưu tiên ID trước type. Thiếu k là lỗi, không tự lấy default 0.
- `contacts` và `separation_pairs` dùng hai định danh nét đầy đủ, kèm vùng tiếp xúc/ngoại lệ và policy ID khi cần. separation_pairs được suy bảo thủ từ chính sách kiểm tra đã version hoặc khai báo đầy đủ và được independent checker xác nhận; không cho client bỏ cặp nguy hiểm để có optimum giả. Same-stroke intersection và contact giữa phần thân có chủ ý có policy riêng.
- Boundary có p0_mm/p_end_mm mỗi giá trị hai tọa độ, initial_pen/final_pen cùng UP. `normalization` là NFD trong draft nhưng giữ text gốc/hash, grapheme mapping và policy phân rã Đ/đ/dấu riêng; NFD không tự cung cấp ánh xạ glyph.
- `case_ref` resolve đúng một ResearchCase trong manifest có hash, không nhận ID mơ hồ. Hash artifact thật là 64 ký tự hex SHA-256; schema_version, source/font ID và numeric policy phải khớp manifest.
- Đổi biểu diễn curve/flatten hoặc representation làm thay đổi candidate hash. H_geom yêu cầu correspondence/reference khóa; missing coverage được báo, không tự fill geometry theo nghiệm thắng.

## 3. SolveRequest

```json
{
  "schema_version": "joint-artifact-v1-draft",
  "run_id": "dev-example-001",
  "case_ref": "dev-case-001",
  "method": "joint_dp",
  "theta": {"rho": 1.0, "lambda_mm": 2.0},
  "baseline": null,
  "budget": {"wall_time_ms": 10000, "max_states": 100000, "max_configurations": 10000, "memory_limit_mb": 512},
  "seed": 42,
  "freeze_manifest_ref": null
}
```

Số ở ví dụ chỉ minh họa format, không phải điểm vận hành/budget đã duyệt. method dự kiến joint_dp / independent_oracle / staged_top_m / beam. staged_top_m bắt buộc ranker H_ref/H_geom, positive integer m và rank_at_theta0_ref; beam bắt buộc positive width. Trường không phù hợp method bị từ chối, không silent fallback. rho>0, lambda>=0, budget positive finite; seed integer không bool. Không đổi candidate set theo method. Official holdout chỉ chạy manifest có freeze hash và quyền mở/log hợp lệ; không nhận text Holdout tùy ý từ UI.

## 4. SolveResult và trạng thái

| Field | Quy tắc |
|---|---|
| run_id, case_id, method, candidate_set_sha256, contract_version | Định danh đủ để ghép kết quả |
| outcome | OPTIMAL / FEASIBLE / INFEASIBLE / NO_FEASIBLE_IN_PREFIX / TIMEOUT / RESOURCE_LIMIT / INVALID_INPUT / INTERNAL_ERROR |
| scope | full_candidate_set / declared_prefix / explored_subset |
| enumeration_complete, ranking_complete, search_complete | Đã duyệt hết G / đã chứng minh đúng prefix yêu cầu / đã giải exact trong scope; ba Boolean độc lập |
| schedule | null hoặc chọn candidate IDs + ordered actions với stroke_id, orientation, CONNECT/LIFT; boundary actions xác định |
| metrics | L_down_mm, L_up_mm, N_cycle, J_mm, T_hat_sec nếu có v_down; thời gian stage/total, peak states/memory, w/f/b, independent violations |
| bounds | lower_bound_J_mm/upper_bound_J_mm nullable; provenance và scope từng bound |
| provenance | git commit + dirty patch hash, input/manifest/config/candidate hashes, seed, runtime versions, measured/DEV/assumed timing source |
| validation | NOT_RUN / PASS / FAIL; checker_id/version, findings |
| error | null hoặc code/message; không chứa thông tin bí mật |

OPTIMAL chỉ khi có chứng minh search complete/exact trong scope khai báo; với joint full-set không bắt buộc enumerate hết Cartesian nếu DP chứng minh bao phủ nó. Prefix OPTIMAL không đồng nghĩa full-set optimal. INFEASIBLE chỉ khi đã chứng minh trong scope; với top-m prefix dùng NO_FEASIBLE_IN_PREFIX, và khi enumeration chưa đầy đủ không kết luận G vô nghiệm. Beam có nghiệm trả FEASIBLE trừ khi có chứng nhận độc lập.

TIMEOUT/RESOURCE_LIMIT có thể kèm incumbent khả thi; không thay outcome bằng OPTIMAL, không gán chi phí 0 hoặc kết luận equivalence. J không có thì null, không Infinity hay chuỗi "nan". Validation FAIL cấm export/print như nghiệm đã kiểm; NOT_RUN không là PASS.

Trường gap_m trong aggregate chỉ tính khi giá trị cần so là exact, ranking đầy đủ đúng G, cùng hash/policy/theta và mẫu số >0. Kết quả incomplete ở nhóm riêng. Tie sequence so khi cùng tie_policy_id; nếu khác chỉ đối chiếu feasibility/cost và validity mỗi lịch.

Aggregate cần chênh lệch tuyệt đối, mean/max gap, nhóm dấu, coverage/missing reasons, runtime median/p95, warmup/repeat counts và môi trường. `m_star` là m nhỏ nhất đạt biên đã khóa chỉ khi có chứng cứ cho mọi m nhỏ hơn (hoặc tìm kiếm đơn điệu exact có chứng cứ); nếu chỉ chạy một lưới m, báo `smallest_tested_m` thay vì giả định minimum toàn miền. Kết luận tương đương thực dụng trên tập khóa yêu cầu max gap không vượt epsilon và đủ kết quả bắt buộc; suy luận thống kê nếu có phải đăng ký trước và kiểm khoảng tin cậy trong biên. Ca không đủ coverage không được làm denominator biến mất mà không báo.

## 5. CertificateResult

Input: một schedule cố định đã hợp lệ, cùng finite feasible-set hash, rectangular domain, numerical policy. Output: bốn theta vertices, J_pi, optimum/lower-bound evidence từng đỉnh, certificate_status EXACT_MODELED / CONSERVATIVE_BOUND / NOT_CERTIFIED, max_regret_upper_mm, scope và tolerance. Vertex timeout hoặc chỉ heuristic optimum không tạo EXACT_MODELED. Không gọi bound theo mô hình là thời gian thực hay bảo đảm máy thật.

## 6. Logging và quyền dữ liệu

- Log nghiên cứu mới ưu tiên JSONL có schema/version, mỗi case-method-theta-m một record; summary dẫn hash records. Giữ kết quả lỗi/timeout/infeasible và stage costs. Nếu xuất CSV, có companion provenance JSON; mỗi version file riêng.
- CSV sản phẩm hiện tại `backend/csv_logger.py`: 15 cột. Runner legacy `backend/handwriting/experiment_runner.py`: 19 cột. CSV hardware schema riêng do TV3. Không gộp/chuyển tên metric để trông tương thích; không thêm cột vào file đã có header khác.
- Solver timing bắt đầu trước sinh/xếp hạng/solve; báo riêng stage times. Peak memory, machine/software versions, warmup/repeats/aggregation khóa trong protocol.
- Holdout mới không nằm trong git/public output. TV1 custody; runner của TV2 chỉ đọc sau freeze/open gate; log access có hai người đối chiếu. Mã/budget/c_min/theta0/epsilon không đổi sau mở.
- public package chỉ gồm dữ liệu/font có quyền công bố; provenance thiếu quyền chứa manifest mô tả và hướng dẫn tái lập, không tự export font nguồn.

## 7. Tích hợp sản phẩm và hardware

Renderer adapter chỉ xuất geometry/schedule đã kiểm, không gọi apply_bio_variation sau solve. Trace/fingerprint phải khớp SVG trong dung sai. Việc style hiện có biến đổi hình học thuộc candidate generation trước solve; không coi tham số style preset là học thói quen người.

`POST /api/ai/generate` hiện hữu không nhận method/theta/top_m như contract mới. Thí điểm font chưa có importer/upload API đã nghiệm thu. HAL nhận SVG như trước; driver/config phụ thuộc máy thực chọn, không cố định AxiDraw/CoreXY. Physical status/timing/capability do TV3; simulator/fake không thành số đo thật. `pause_supported` và HTTP 400 lỗi unsupported phải recheck đúng nhánh/commit; không sửa HAL bằng cập nhật docs.

## 8. Gate để API có hiệu lực

TV4 schema/HTTP + TV2 runner + TV1 manifest + TV3 independent check review; có fixtures đủ valid/invalid/empty/reverse/connect/deadline/tie/infeasible/timeout; có commit triển khai và tests. Hiện gate lớp transport đã có kiểm thử; gate solver, oracle độc lập, geometric validation và freeze/official runs chưa hoàn tất. Frontend đọc capabilities, không gọi phương pháp chưa ready hoặc diễn giải STRUCTURALLY_VALID thành hình học khả thi/đã ký.

## Vận hành gateway và bàn giao adapter

Routes đã có: GET `/api/research/capabilities`, POST `/api/research/validate`, `/api/research/solve`, `/api/research/certify`. Mặc định solver/certifier chưa đăng ký; capabilities là nguồn readiness. Không dùng adapter kiểm thử như một bộ giải thực.

Manifest DEV/synthetic đăng ký phía server qua `OMNIDRAW_RESEARCH_MANIFEST`; không có public case registration hoặc mở Holdout qua HTTP. `ResearchCase.prepare` hỗ trợ hash offline; HTTP không tự sửa hash. Guide hỗ trợ Docs 34 mô tả thao tác, không thay schema/code trong `backend/research/`.

`enumeration_complete` chỉ duyệt hết G; `ranking_complete` chứng minh prefix yêu cầu theo ranker/tie; `search_complete` chứng minh inner solve trong scope. Prefix exact cần hai điều kiện cuối, không cần duyệt hết G nếu k-best có chứng nhận. Gateway kiểm tính nhất quán khai báo, không tự chứng minh ranking hoặc optimum. Adapter lưu evidence trong artifact offline để reviewer tái lập.

API giới hạn 30s, 200k states, 100k configurations, 512MB; đây không là budget nghiệm thu nghiên cứu. Adapter phải thực thi budget nội bộ. Ghi cả ranking và solve timing, hash/scope/complete flags và checker identity; không đổi TIMEOUT thành OPTIMAL. Certificate giữ hash của phương án hoàn chỉnh, bốn đỉnh đúng miền và kiểm độc lập; không chứng nhận thời gian máy thật.

Kiểm thử mục tiêu hiện có: 42 gateway + 34 handwriting regression = 76 PASS, adapter chỉ kiểm transport. Solver/baseline/oracle/certifier và review owner còn PENDING. Chi tiết lần chạy trong nhật ký tiến độ.

## Checkpoint offline DEV sau gateway

TV4 có `joint_dp.py` no-forget/safe-forget, `geometry.py`, replay/trace, single-case `dev_solve.py`, renderer SVG DEV và diagnostic `vertex_analysis.py`. Xem [research README](../backend/research/README.md) cho policy/budget/giới hạn và lệnh tái lập. Đây chưa là adapter được đăng ký vào API; capabilities mặc định không đổi, validate HTTP vẫn structural-only, solve/certify chưa ready.

DEV JSON chứa SolveResult cùng config và trace; config_sha256 là hash config CLI thực, không phải SolveRequest HTTP nên không đưa packet này trực tiếp vào adapter. Provenance ghi source commit và dirty digest của diff tracked cùng hashes untracked không ignored. SVG metadata giữ candidate/schedule hashes, independent NOT_RUN và quality PENDING. Diagnostic bốn đỉnh luôn NOT_CERTIFIED dù các search DEV complete. Không tự nâng independent_violations/PASS hoặc mở freeze/HOLDOUT từ các artifact này. Tests gateway đã chuyển đến `tests/research/test_api.py`; map đường dẫn cũ ở [tests README](../tests/research/README.md).
