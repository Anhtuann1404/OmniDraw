# API nghiên cứu — slice gateway đã triển khai

**Ngày:** 02/10/2026. **Owner:** TV4. **Contract:** `joint-artifact-v1-draft`. **Trạng thái:** code lớp API có kiểm thử; review owner và các solver còn pending. Không tạo sign-off thuật toán/PR3 mới.

## 1. Có thể dùng gì hiện tại?

| HTTP | Chức năng thực tế | Thành công / lỗi |
|---|---|---|
| GET `/api/research/capabilities` | Schema version, method readiness và giới hạn server | 200; mặc định bốn method=false, certify_ready=false |
| POST `/api/research/validate` | Schema, hash, grapheme mapping, owners/IDs, precedence DAG và references | 200 STRUCTURALLY_VALID; geometric_validation=NOT_RUN; không đăng ký case |
| POST `/api/research/solve` | Resolve case từ server; validate request/budget; gọi adapter; kiểm output/provenance | 200 khi adapter trả kết quả hợp contract; 404 case không khả dụng, 503 method chưa đăng ký |
| POST `/api/research/certify` | Resolve case, fixed schedule/hash/domain, gọi certifier và kiểm bốn đỉnh/bounds | 200 khi output hợp contract; 503 khi thiếu certifier; không tự sinh optimum |

Tất cả payload nghiên cứu tách khỏi `/api/ai/generate`. API không gọi AI, tạo SVG, ghi log nghiên cứu chính thức hoặc khởi động máy. Run-manifest/JSONL, renderer sau independent check, importer font và bộ solve/chứng nhận thực tế là slice kế tiếp.

Không có public endpoint upload/register manifest hoặc case. Holdout trả unavailable khi lookup, bị từ chối khi submit validate; freeze_manifest_ref khác null cũng bị từ chối trong gateway này. Official runs dùng custody/offline protocol sau freeze, chưa được mở qua HTTP.

## 2. Schema đang dùng

Nguồn máy đọc được: OpenAPI `/docs` và `/openapi.json` của backend. Nguồn code: `backend/research/schemas.py`; contract nghiên cứu tại Docs 31/32. Extra fields bị từ chối. Float chỉ nhận JSON number hữu hạn, không bool/chuỗi; integer/boolean strict. Dung sai và tham số ở ví dụ không thành thông số nghiệm thu.

- Phiên bản cố định; c_min_mm=0.20. Point `[x,y]` world-mm; polyline ít nhất hai điểm. Zero-length cần khai báo allow_zero_length=true.
- Owner index liên tiếp từ 0, một grapheme NFD là base+combining marks; nối grapheme phải đúng text. IDs variant/stroke không chứa `/` hoặc `\` để qualified ID không mơ hồ.
- Body order chứa đủ thân đúng một lần; precedence chỉ giữa marks cùng variant và không chu trình. Pair references có thật, không trùng hoặc nối hai variant loại trừ nhau.
- Delay ưu tiên key `owner_index/candidate_id/stroke_id`, sau đó mark_type; thiếu k bị từ chối. Đây là kiểm cấu trúc; feasibility lịch/clearance vẫn do solver và checker độc lập.
- Solve method: joint_dp/independent_oracle không có baseline options; staged_top_m cần `{ranker,m,rank_at_theta0_ref}`; beam cần `{width}`. Không fallback âm thầm.
- API trần: request 1 MiB, manifest file 2 MiB; budget tối đa wall_time_ms=30000, max_states=200000, max_configurations=100000, memory_limit_mb=512. Đây là giới hạn vận hành gateway, không budget benchmark đăng ký trước. Thời gian/state/memory khi solve phải được adapter thực thi; chưa có hard-kill worker.

## 3. Tạo manifest phía server

Chỉ administrator/operator cung cấp đường dẫn qua `OMNIDRAW_RESEARCH_MANIFEST` khi backend khởi động. Request HTTP chỉ có case_ref, không được cung cấp đường dẫn hoặc thay cases. Manifest lỗi/hết giới hạn/hash sai/ID trùng làm cấu hình khởi động thất bại, không tự đọc file khác hay bỏ kiểm.

Envelope JSON gồm đúng `schema_version`, `manifest_sha256`, `cases`. TV1 tạo từng case bằng `ResearchCase.prepare(payload)` trong Python offline để chuẩn hóa kiểu và tính candidate hash; HTTP không chạy helper này và không sửa hash mismatch cho client. Manifest draft được đóng gói theo quy trình:

```python
from backend.research.schemas import ResearchCase, VERSION
from backend.research.service import manifest_hash

cases = [ResearchCase.prepare(payload) for payload in case_payloads]
digest = manifest_hash(cases)
for case in cases:
    case.manifest_sha256 = digest
packet = {
    "schema_version": VERSION,
    "manifest_sha256": digest,
    "cases": [case.model_dump(mode="json") for case in cases],
}
```

Payload tác giả cần manifest_sha256 64 hex ban đầu (có thể placeholder khi chuẩn bị offline); thay bằng digest trước xuất. `candidate_set_sha256` do helper tính; request validate từ client phải cung cấp đúng hash đã xuất.

Hash recipe draft: JSON UTF-8, ensure_ascii=false, sort_keys=true, separators=(",",":"), không NaN/Infinity, từ model_dump(mode="json") sau chuẩn hóa và default. Candidate hash phủ schema_version, normalization, normalized_text, candidates, contacts, separation_pairs, delay_policy, geometry_policy, boundary, reference_geometry. Manifest hash phủ `{schema_version,cases}` với từng case loại riêng manifest_sha256 để tránh tự tham chiếu. Đây là hash phạm vi nghiên cứu, không chỉ hash file font; recipe cần TV1/TV2 review trước freeze.

## 4. Gắn adapter và ownership

`ResearchService(cases, solvers={method: callable}, certifier=callable)` và `create_router(service)` là điểm tích hợp. Callable nhận bản sao sâu của ResearchCase và SolveRequest hoặc CertificateRequest, trả dict hay model tương ứng. Service trong app mặc định không đăng ký phương pháp; owner phải tích hợp adapter có review, không bật readiness bằng cấu hình phía client.

| Owner | Bàn giao cần làm |
|---|---|
| TV4 | Adapter DP joint đúng Docs 31, complete flags, schedule/cost, timeout/resource handling; certifier cố định lịch sau kiểm độc lập |
| TV2 | staged_top_m/beam và runner; provenance hashes/cost/stage timing; prefix incomplete không tuyên bố global top-m |
| TV1 | Manifest/glyph/anchors/license, qualified mark IDs và hash recipe; Holdout giữ riêng |
| TV3 | independent_oracle và checker distance/intersection/cost/clearance; nhận dữ liệu thô, không dùng logic solver |

SolveResult phải khớp run/case/method/candidate/manifest/seed và input/config hashes. Incumbent cần đủ motion coefficients khớp J, IDs/direction/coverage/boundary hợp cấu trúc. Exactness cần search_complete; staged exact cần enumeration/ranking complete và prefix scope. Beam trong gateway này chỉ FEASIBLE hoặc incomplete cho đến khi có cơ chế chứng nhận được review. Không tự đổi TIMEOUT thành OPTIMAL; validation NOT_RUN không thành PASS. PASS yêu cầu checker identity và independent_violations=0.

Certificate phải khớp schedule hash và đúng bốn góc miền, cùng scope. EXACT_MODELED cần bốn đỉnh exact có optimum/lower-bound evidence; conservative cần lower bounds hợp lệ. Certificate có bound yêu cầu independent validation PASS; gateway kiểm tính nhất quán dữ liệu, không chứng minh adapter đã giải đúng optimum hoặc primitive độc lập. Phần đó là gate nghiệm thu solver/checker.

## 5. Lỗi HTTP và giới hạn

422: schema/hash/options/budget/schedule lỗi; 413: payload quá lớn; 403: public Holdout hoặc official run bị khóa; 404: case không khả dụng (không lộ Holdout); 503: adapter chưa ready; 500: adapter sai contract/exception. Body lỗi gồm outcome, error.code/message, findings; không phải SolveResult thành công và không có optimum giả. Findings chỉ chứa location/type, không echo raw NaN/Infinity/input hoặc exception. Không trả stacktrace của adapter cho client.

Schema/registry chỉ bảo đảm cấu trúc và liên kết input-output. Chưa chứng minh collision-free, quyền license, phân bố corpus, độ độc lập oracle hoặc chất lượng tối ưu. Giới hạn singleton/cancellation/worker, official authentication/ACL và public deployment cần thiết kế thêm trước mở chức năng có dữ liệu Holdout hoặc solver dài.

## 6. Kiểm thử

`tests/test_research_api.py` dùng TestClient và adapter kiểm thử, không đóng vai bộ giải nghiên cứu/oracle độc lập. Kiểm invalid schema/hash/order/owner/NaN/options, payload/budget, Holdout/case-path, output/provenance, timeout, chứng nhận và main/OpenAPI integration. Chạy cùng `backend/test_handwriting_validation.py` để kiểm hồi quy API sản phẩm. Kết quả lần chạy được ghi trong progress log; không gọi các test này là sign-off nghiên cứu.
