# Kế hoạch kỹ thuật theo hướng nghiên cứu đã thống nhất

**Cập nhật:** 02/10/2026. **Owner:** TV4. **Trạng thái:** kế hoạch triển khai, chưa phải bằng chứng nghiệm thu.

Ngày 02/10/2026, TV4 thông báo GVHD đã đồng ý hướng nghiên cứu. Xác nhận này áp dụng cho hướng đề tài; không tự xác nhận epsilon_eq, số mẫu, tham số máy, API mới hoặc kết quả thực nghiệm. Đề cương nguồn: [Google Docs](https://docs.google.com/document/d/1iyEXfAvh8kaw7xXrF6vM6z6nSn2qfhkG0xmg62eto1Y/edit), bản đồng bộ tại [Docs 29](29_research_proposal_consolidated.md).

## 1. Phạm vi và nguồn đặc tả

- Lõi: đồng tối ưu hình học chữ/dấu tiếng Việt và lịch thực hiện nét; đối chứng phân tầng top-m; kiểm chứng độc lập; điều kiện có lợi/bằng nhau; độ nhạy hai tham số chuyển động.
- Một thí điểm có điều kiện: font thiết kế, TV1–TV4 đồng chủ trì. Không tự sửa mọi font, không khôi phục chữ cơ sở thiếu.
- Kiểm chứng máy vẽ phẳng hai trục khi thiết bị sẵn sàng. Chưa chốt dòng máy/cơ cấu; phương án A4 tiết kiệm là concept, không phải cấu hình đã mua/hiệu chuẩn.
- Writer Profile, Pareto, cắt tỉa mở rộng, hiệu chuẩn chủ động, nhiều màu và phân trang nâng cao ngoài cam kết kỳ này. Art Mode và thư tay giữ là chức năng sản phẩm; không lấy số liệu của chúng thay cho nghiên cứu chữ/dấu.
- [Docs 31](31_joint_solver_contract.md) là đặc tả dùng chung DP–oracle–baseline; [Docs 32](32_research_api_and_artifact_contract.md) là giao diện nghiên cứu dự kiến. API sản phẩm hiện hữu vẫn tại [API Spec](OmniDraw_API_Spec-4.md).

## 2. Ownership theo sản phẩm

| Owner | Chủ trì | Bàn giao | Reviewer |
|---|---|---|---|
| TV4 / CN | Mô hình chữ/dấu, hàm mục tiêu, trạng thái/truy hồi, DP, tích hợp, báo cáo phương pháp | Đặc tả, bộ giải, backpointer/trace, renderer adapter, lập luận và giới hạn | TV2 mô hình; TV3 oracle; TV1 dữ liệu |
| TV2 | Toàn văn tài liệu, đối chứng H_ref/H_geom/beam, mô hình chi phí, runner và phân tích | Bảng Balas có trang, baseline độc lập, manifest chạy, số liệu và biểu đồ | TV4 phương pháp; TV3 QA |
| TV1 | Ngữ liệu, split mới, custody Holdout, khảo sát âm tiết/w/b; đồng chủ trì font | Manifest/hash/access log, corpus có nhóm dấu, tham chiếu font và quyền sử dụng | TV2 protocol; TV3 đối chiếu khi mở |
| TV3 | Oracle và primitive hình học độc lập; đo máy, driver/HAL | Vét cạn ca nhỏ, ca kiểm tay, báo cáo bất đồng, nguồn/biên tham số máy | TV2 hình học/chi phí; TV4 tích hợp |

TV3 cần xác nhận khả năng nhận oracle trong tuần đầu tháng 1. Nếu chuyển oracle cho TV1, TV2 nhận custody/log Holdout trước bàn giao; người viết oracle không giữ/mở Holdout một mình. TV4 là tác giả DP nên không tự viết oracle rồi gọi đó là kiểm chứng độc lập. Font lùi nếu oracle còn tồn đọng. Sign-off cũ chỉ có hiệu lực cho đúng commit/phạm vi đã ký.

## 3. Snapshot triển khai được kiểm tra

Checkout ngày 02/10/2026: `codex/tv4-pr3-slices`, HEAD `c1b4696`, có thay đổi chưa commit. Không suy ra đây là trạng thái mới nhất của mọi nhánh remote.

| Thành phần | Bằng chứng hiện có | Việc của hướng mới |
|---|---|---|
| React + FastAPI, sinh SVG, API print/history/log | Có mã hiện hữu | Giữ tương thích; không tự thêm option nghiên cứu vào API hiện tại |
| `backend/handwriting/composition.py` | `CompositionState`, `optimize_composition_dag` | Tái sử dụng có kiểm chứng; chưa chứng minh đủ state cho pending/frontier mới |
| `backend/handwriting/experiment_runner.py` | Runner B1/B2/B3/Proposed, Proposed DEV-only, CSV 19 cột | Runner mới top-m/beam, complete/incomplete và provenance riêng do TV2 |
| `backend/csv_logger.py` | Log sản phẩm 15 cột | Không đổi header để nhét kết quả nghiên cứu mới |
| `backend/hardware_adapter.py` | HAL/driver/simulator và CSV riêng | TV3 chọn driver theo thiết bị; giữ số đo và mô phỏng riêng |
| HTTP pause/resume ở `backend/main.py` | Nhánh lỗi đi qua `custom_error` | Recheck việc bảo lưu capability/status theo nhánh TV3; chưa tuyên bố checkpoint này đáp ứng toàn contract |
| Solver joint, oracle độc lập, top-m, chứng nhận | Có preflight khám phá ở Docs 25 | Chưa nghiệm thu hướng mới; preflight dùng primitive chung không thay oracle độc lập |

Không có số test mới hoặc verdict PASS được tạo bởi lần cập nhật tài liệu này.

### Cập nhật triển khai API sau snapshot docs

Gateway/schema/manifest đã có trong `backend/research/`, main đã include router; chi tiết Docs 34. Đây là một phần S0/S1, chưa hoàn tất S2–S7. Default methods/certifier đều chưa ready; 38 tests gateway và 34 regression API handwriting PASS. Không dùng test adapter làm số liệu, solver hoặc sign-off owner.

## 4. Các slice để triển khai

| Slice | Owner | Đầu ra | Gate và phụ thuộc |
|---|---|---|---|
| S0 — Khóa bài toán | TV4 + TV2 + TV1 + TV3 | Docs 31, candidate IDs, contact exceptions, timing/tie/budget manifest | Review từng người; chưa mở Holdout |
| S1 — Dữ liệu vào và fixtures | TV1 + TV4 | Glyph/mark ownership, fixed world-mm geometry, independent test cases | Geometry sau style phải trùng geometry chấm; test reverse/connect/deadline |
| S2 — Oracle độc lập | TV3 | Enumerator + independent distance/intersection/cost checker | Kiểm tay 0,19/0,20/0,21 mm, suy biến, đồng hạng, vô nghiệm |
| S3 — DP một mục tiêu | TV4 | Frontier/pending/pen state, recurrence, backpointer | So khả thi và optimum với S2; không đòi cùng lịch khi tie khác |
| S4 — Đối chứng và runner | TV2 | H_ref/H_geom, top-m đầy đủ, beam, logging | m=toàn bộ bằng joint; ranking incomplete không gọi top-m toàn cục |
| S5 — Lập luận và cấu trúc | TV4 + TV2; TV1 dữ liệu | Ví dụ có lợi, điều kiện đủ bằng nhau, cận state, w/b | Glyph tham số hóa trước; không gọi công cụ chuẩn là thuật toán mới |
| S6 — Độ nhạy và bốn đỉnh | TV4 + TV2 | Lưới rho/lambda, regret cho lịch cố định | Tập khả thi cố định; oracle exact hoặc lower bound hợp lệ; heuristic không thay optimum |
| S7 — Freeze và đánh giá | TV1 custody; TV2 runner; TV3 QA; TV4 tích hợp | Freeze manifest, Holdout mới, per-case results, gói tái lập | Qua S2–S6 trong phạm vi khóa; ghi timeout/infeasible/coverage |
| S8 — Font và máy | TV1 + TV4 font; TV3 máy | Pilot chọn lọc, giấy phép, manual reference, physical logs | Sau gate lõi; có thể hoãn để bảo vệ báo cáo |

Các ký hiệu S0–S8 là kế hoạch mới, không đổi tên PR1–PR5/E1/E4 cũ thành bằng chứng mới. Đóng PR3 cũ trên đúng commit là việc tích hợp nền, không thay gate S7.

## 5. Một tiến độ duy nhất: 8 tháng

Tháng tương đối từ ngày bắt đầu thực hiện được phê duyệt, chưa tự gán lịch cụ thể chỉ từ lời đồng ý hướng.

| Tháng | Công việc | Owner | Gate |
|---|---|---|---|
| 1 | S0; xác nhận oracle; đọc hai bài Balas toàn văn; đề xuất epsilon_eq và cỡ mẫu; đăng ký ranking/tie/budget; chuẩn bị số đo hoặc nguồn tham số | TV4 đặc tả; TV2 tài liệu/biên; TV1 split; TV3 oracle/đo | Không giả nhận đã đọc toàn văn hoặc đã khóa biên |
| 2 | S1–S4 trên DEV; oracle độc lập; tách Holdout mới; ví dụ tham số hóa; đo sơ bộ nếu có máy | TV4 DP; TV3 oracle; TV2 baseline/runner; TV1 dữ liệu | Không mở Holdout, không Pareto |
| 3 | S5–S6 và đối chiếu; cuối tháng khóa code/data/candidates/tie/c_min/theta0/epsilon/budgets | Cả nhóm theo ownership | DP–oracle khớp trong tolerance; chưa đạt thì lùi mở dữ liệu |
| 4 | Mở Holdout mới có hai người đối chiếu; chạy bản đã khóa, báo failure/coverage | TV1 custody; TV2 chạy; TV3 QA; TV4 nguyên nhân | Không điều chỉnh theo Holdout |
| 5 | Phân tích lợi ích/bằng nhau/chưa đủ bằng chứng; thiết kế font có license/reference | TV2 kết quả; TV4 cơ chế; TV1+TV4 font | Chỉ pilot khi lõi đã tái lập |
| 6 | Pilot font; máy nếu sẵn sàng; viết chương kết quả | TV1+TV4 font; TV3 máy; TV2 thống kê | Không lấy mô phỏng làm số đo máy |
| 7 | Hoàn tất thử nghiệm; báo cáo, giới hạn, bản thảo bài báo | Cả nhóm, TV4 tổng hợp | Không cam kết bài báo được nhận |
| 8 | QA số liệu/trích dẫn, gói tái lập, hồ sơ/slides/bàn giao | Cả nhóm | Licenses quyết định phần dữ liệu có thể công bố |

## 6. Cắt phạm vi và quyết định còn mở

- Khi trượt cuối tháng 3: giảm khảo sát w/b rộng và họ ví dụ lớn; giữ ví dụ tối thiểu và gate độc lập. Không mở Holdout hoặc làm font để thay thế lỗi solver.
- Pareto, cắt tỉa mở rộng, Writer Profile và hiệu chuẩn chủ động không được khởi động để cứu số liệu lõi.
- Nếu lõi còn trễ tháng 6: lùi font, dành tháng 7–8 cho báo cáo/gói tái lập.
- Phải chốt trong tháng 1–3: số mẫu mới, epsilon_eq có căn cứ, rho0/lambda0 và miền quét, k từng loại dấu, dung sai số học/contact, budget, method IDs và nguồn tham số. Giá trị chưa chọn là PENDING, không tự biến ví dụ thành cấu hình nghiệm thu.
- Nếu máy chưa có: protocol DEV và dải có nguồn phù hợp với phương án máy dự kiến; công khai giả định. Không dùng thông số AxiDraw như số đo của máy A4 khác.

## 7. Tài liệu, ownership và migration

Chỉ đổi đặc tả/phân công trên docs trong lượt này; không sửa code TV2/HAL/cơ khí. Tài liệu đang dùng được đồng bộ; báo cáo, phiếu review, corpus cũ và bằng chứng giữ như lịch sử có nhãn. Bản nội dung trước khi thay được giữ trong `history/20261002/`; không xóa kết quả không thuận lợi hoặc nâng sign-off.

Đề cương Google Docs là nguồn hướng nghiên cứu; Docs 29 là bản đối chiếu local. Đổi contract phải sửa Docs 31/32, RQ traceability và runner manifest trước code. API mới chỉ thành implemented khi có code, kiểm thử và review trên commit cụ thể.
