# Bảng quyết định và gate còn PENDING

Cập nhật 02/10/2026, nền đã kiểm `bf68d0bb69d3efe2852a7d315a87d6778fb0b77f`, nhánh chia sẻ `codex/tv4-pr3-slices`. Trưởng nhóm xác nhận giữ phân công TV1–TV4 như cũ. Đây là bảng điều phối theo nguồn hiện hành, không là contract thứ hai hoặc phiếu nghiệm thu.

Nguồn chính: [Docs 30 — kế hoạch/ownership](../30_research_development_plan.md), [Docs 31 — mô hình](../31_joint_solver_contract.md), [Docs 32 — artifacts](../32_research_api_and_artifact_contract.md). [Current-task](../03_current-task.md) ghi trạng thái triển khai. Review S0 TV2 target `8dcfe66` là REVIEWED_WITH_OPEN_GATES; 332 tests PASS tại code `bf68d0b` là kiểm thử nội bộ/hồi quy, chưa là nghiệm thu độc lập. PR3 đã đóng; code publish, code merge và nghiệm thu cần bằng chứng riêng.

## Phân công giữ nguyên

| Thành viên | Trách nhiệm theo phân công hiện tại |
|---|---|
| TV1 | Dữ liệu, ứng viên/reference/quality, split và custody HOLDOUT; đồng chủ trì font với TV4 |
| TV2 | Baseline H_ref/H_geom/top-m/beam, chi phí, runner, protocol/phân tích và đối chiếu tài liệu |
| TV3 | Oracle và primitive độc lập; phần cứng, đo máy và nguồn tham số vật lý |
| TV4 | Mô hình, DP, trace, tích hợp và tổng hợp tài liệu; đồng chủ trì font với TV1 |

Phân công đã được trưởng nhóm giữ nguyên, nhưng bảng không xác nhận từng TV đã nhận hoặc hoàn tất việc. TV3 ghi xác nhận nhận oracle trong log của mình; không tự chuyển oracle sang TV1. TV4 không tự ký độc lập cho DP của mình. Các phương án chuyển người trong tài liệu kế hoạch chỉ là dự phòng, chưa kích hoạt.

## Danh sách để review và chốt

Mọi hàng dưới đây hiện **PENDING**. “Chủ trì → reviewer” lấy theo ownership của Docs 30; các phối hợp liên quan được ghi cụ thể. Reviewer kiểm bằng chứng, trưởng nhóm tổng hợp quyết định có người xác nhận/commit/phạm vi. Tên người trong bảng chưa là chữ ký của họ. Ưu tiên là thứ tự xử lý theo phụ thuộc, không tự đặt ngày nghiệm thu.

| ID / ưu tiên | Việc cần chốt hoặc kiểm chứng | Chủ trì → reviewer / phối hợp | Bằng chứng cần có để đóng hàng | Nguồn |
|---|---|---|---|---|
| Q01 / CLOSED_ACKNOWLEDGEMENT_ONLY | TV3 xác nhận nhận oracle và phạm vi độc lập | TV3 → TV2; TV4 bàn giao schema/fixtures | Log nhận việc; kế hoạch primitive/enumerator tự viết từ đặc tả; ghi rõ không import checker/cache feasibility TV4. Không cần chờ máy | Docs 30 §2, S2; Docs 31 §3/7 |
| Q02 / làm ngay | Review draft contract về lịch và J | TV4 mô hình, TV2 chi phí → review chéo; TV3 oracle, TV1 dữ liệu | Review đúng commit/version về BODY/MARK/END, k/deadline, reverse, CONNECT/LIFT, boundary/N_cycle; ca kiểm tay và danh sách bất đồng đã giải. Đây là review quy tắc, không chọn lại công thức từ ví dụ | Docs 31 §1–5; Docs 32 §8 |
| Q03 / trước so sánh | Reference/mapping và gate chất lượng chung | TV1 + TV4 → TV2 protocol; TV3 đối chiếu geometry | IDs/grapheme/owner, correspondence/anchor/x-height/license; bounds dịch dấu/slant/scale/topology/H_geom đề xuất trên DEV; manifest/hash trước–sau lọc và lý do, cùng cho mọi method | Docs 31 §3.1; Docs 32 §2 |
| Q04 / trước so sánh | Contact/near-contact và flatten/numeric policy | TV4 đặc tả + TV3 primitive → TV2 hình học/chi phí; TV1 glyph | Policy version/hash; vùng ngoại lệ hữu hạn; ca degenerate/collinear/self-intersection và .19/.20/.21 mm; sai số flatten/contact/cost có căn cứ. Nếu khác endpoint phải chốt snap trước hash hoặc connector khai báo/đo/kiểm. Không hạ floor .20 mm bằng tolerance | Docs 31 §2/3; review S0 TV2 |
| Q05 / trước freeze | k theo loại/ID dấu và mark precedence | TV4 → TV2 mô hình; TV1 dữ liệu, TV3 đối chiếu | Bảng k nguyên không âm, nguồn/lý do chọn trên DEV và ca deadline/precedence; đơn vị là số thân kế tiếp hoàn tất. k ví dụ không là tham số đã duyệt | Docs 31 §2/5; Docs 32 §2 |
| Q06 / trước so sánh | Ranker, tie và scope prefix | TV2 → TV4 phương pháp; TV3 QA; TV1 reference | H_ref/H_geom, stable config-ID tie và reference schedule khai báo; giữ cấu hình reference invalid trong G; prefix evidence/coverage. Exhaustive DEV hoặc chứng minh k-best; khai báo tie schedule/numeric riêng, không suy cùng lịch nếu tie khác | Docs 31 §6; Docs 32 §4 |
| Q07 / trước freeze | Điểm theta0 và miền rho/lambda | TV3 nguồn/đo; TV2 protocol → TV4 phương pháp | Nguồn v_down/v_up/tau hoặc giả định DEV công khai; đơn vị/quy đổi, rho0/lambda0, miền chữ nhật và lý do. Tách measured/assumed/DEV; không lấy số máy khác làm số đo máy đang chọn | Docs 30 §6; Docs 31 §4/8 |
| Q08 / trước freeze | epsilon_eq và tolerance đối chiếu | TV2 → TV4 phương pháp; TV3 numeric QA | Biên tương đương có căn cứ và review; tolerance so DP–oracle và sai số số học phân biệt với epsilon_eq; quyết định trước HOLDOUT. Tolerance debug CLI không tự thành epsilon_eq | Docs 30 §5/6; Docs 31 §8 |
| Q09 / trước freeze | Phạm vi exact, budget và completion | TV2 protocol; TV4 DP; TV3 oracle QA | Phạm vi n/q/k/số nét/w; budget wall-time/states/configurations/memory; stage/total timing, allocation/RSS đúng nghĩa, warmup/repeat/environment. Kết quả DEV và ngưỡng completion đề xuất; giữ timeout/infeasible/missing trong denominator. Trần API không là budget nghiệm thu | Docs 30 §5/6; Docs 32 §4/6 |
| Q10 / sau fixtures | Nghiệm thu DP trong phạm vi đã khai báo | TV4 → TV3 oracle; TV2 mô hình/chi phí, TV1 dữ liệu | No-forget/safe-forget khớp feasibility/value; oracle độc lập và kiểm tay khớp trong tolerance được review; trace/candidate hashes và counterexamples được xử lý. Chỉ so sequence nếu cùng tie. Ghi commit/scope/checker thực | Docs 30 S2/S3; Docs 31 §5/7 |
| Q11 / sau inner interface | Nghiệm thu baseline/runner và điều kiện tính gap | TV2 → TV4 phương pháp; TV3 QA | Ca DEV G nhỏ, m đầy đủ: prefix nested, J không tăng và m=toàn bộ khớp joint/oracle; scope/flags/bounds đúng khi ranking/inner incomplete. JSONL/hash/timing có đủ failures; gap chỉ với exact/feasible/certified-prefix/cùng hash/theta/J_m>0 | Docs 30 S4; Docs 31 §6/8; Docs 32 §4/6 |
| Q12 / trước freeze | Protocol lambda và cutoff để giảm trọng tâm | TV2 → TV4 phương pháp; TV1 fixtures | Quét rho/lambda đăng ký trên DEV; phân biệt multi-N khả thi, multi-N không bị trội và đổi optimum thực; incomplete là UNKNOWN. Cutoff phải có evidence/review, không sửa HOLDOUT để tạo switching | Docs 31 §4.1; Docs 30 S6 |
| Q13 / trước mở HOLDOUT | Cỡ mẫu, split mới và custody/access protocol | TV1 → TV2 protocol; TV3 đối chiếu | Đề xuất mẫu/nhóm dấu/tiêu chí loại và căn cứ; provenance mới chưa dùng tinh chỉnh; manifest niêm phong ngoài Git, access log và quy trình hai người. Corpus cũ chỉ supplemental; không mở dữ liệu ở bước lập bảng | Docs 30 S7; Docs 32 §6 |
| Q14 / gate mở HOLDOUT | Freeze và review/sign-off chung | TV4 tổng hợp; TV1/TV2/TV3 review đúng phần | Hash code/data/candidates/reference/policies/tie/theta0/domain/k/c_min/epsilon/budgets/protocol; evidence Q02–Q13 phù hợp phạm vi, owner xác nhận và quyền mở/log hợp lệ. Gate chưa đạt thì lùi mở, không tự ký thay | Docs 30 S0/S7, §5/6; Docs 32 §8 |
| Q15 / sau gate lõi | Certificate và tích hợp/export | TV4 + TV2 → TV3 independent check; TV1 manifest | Giữ phương án hoàn chỉnh cố định, đối thủ full feasible set tại bốn đỉnh; exact optimum hoặc lower bound hợp lệ, scope/error evidence; renderer khớp geometry/trace. Diagnostic NOT_CERTIFIED hoặc test adapter không thay certificate/solver ready | Docs 31 §8; Docs 32 §5/7/8 |
| Q16 / có điều kiện | Font pilot, máy và bằng chứng tài liệu | TV1 + TV4 font; TV3 máy; TV2 nguồn → review theo Docs 30 | Font chọn lọc có license/reference/protocol sau gate lõi; logs đo máy đúng thiết bị. TV2 bổ sung toàn văn/trang Balas/RTSP/PCGTSP và mapping/giới hạn trước viện dẫn. Các việc có thể song song phần chuẩn bị, chưa là kết quả đã kiểm | Docs 30 S5/S8, §5/6; review S0 TV2 |

Q16 gom các đầu ra bổ sung để theo dõi, không buộc mua máy hoặc có máy mới được viết oracle. Bảng chưa đặt giá trị số, người duyệt thay thế hoặc lịch mở dữ liệu. Nguồn toàn văn chưa đọc vẫn PENDING; không thực hiện nghiên cứu tài liệu mới trong slice điều phối này.

## Buổi đối chiếu đầu tiên của trưởng nhóm

1. Xem log Q01: TV3 đã nhận oracle chưa; nếu chưa, yêu cầu TV3 xác nhận theo phân công hiện tại, không tự đổi người.
2. Thu review Q02–Q06: chỗ nào contract chưa rõ, kèm ca DEV nhỏ và đề xuất; mỗi bất đồng có một ID và owner xử lý.
3. Xem Q10–Q11: mỗi bên ghi commit/version/hash đã chạy. Cùng input/geometry/policy/theta mới đối chiếu feasibility và J; scope/incomplete khác nhau phải tách riêng.
4. Chốt việc chuẩn bị Q07–Q09/Q12–Q13 trên DEV. Khi có bằng chứng mới thì cập nhật nguồn Docs 30/31/32 trước, rồi ghi quyết định ở bảng; giữ HOLDOUT đóng đến Q14.

## Mẫu bàn giao dùng chung

Mỗi TV ghi trong `docs/handoff/tv1_progress.md`, `tv2_progress.md` hoặc `tv3_progress.md` của mình; TV4 tổng hợp current-task/progress-log. File log của owner chỉ tạo khi có bàn giao thực, không tạo record nhận việc thay họ.

```text
Owner / ID quyết định liên quan:
Commit nền chia sẻ đã fetch / commit bàn giao:
Contract/artifact version / policy IDs:
Case/manifest/candidate/config hashes và split (DEV/synthetic):
Đã làm / chưa làm / phạm vi claim:
Lệnh tái lập / môi trường / budget và stage timing:
Kết quả: feasibility, J, scope, complete flags; error/timeout/infeasible:
Checker/oracle identity và bằng chứng độc lập (hoặc NOT_RUN):
Bất đồng/counterexample, kết luận hiện tại và giới hạn:
Đề xuất cần review / reviewer cần xác nhận:
Gate vẫn PENDING / bước tiếp theo:
```

## Quy tắc cập nhật quyết định

Mỗi Q-ID có record khi có evidence, gồm trạng thái PENDING/PROPOSED/REVIEWED_WITH_OPEN_GATES/APPROVED, giá trị/phạm vi đề xuất, commit/artifact/lệnh, người review/xác nhận thực, ngày và phụ thuộc chưa đóng. APPROVED chỉ ghi khi có xác nhận trong scope; trạng thái workflow này không tự thay validation PASS hay certificate status của Docs 32. Tại thời điểm tạo bảng chưa có record; xem các cập nhật có provenance bên dưới.

Nếu cùng sửa docs gây conflict: owner giữ log riêng; TV4 nhập kết quả tổng hợp, đối chiếu nguồn hiện hành và evidence từng bên, không dùng blanket ours/theirs. Giữ lịch sử verdict theo commit/scope. Cách đồng bộ nhánh trong [handoff README](README.md).

Bằng chứng chuẩn bị TV4 mới: [Docs 36](../support/36_joint_method_and_dp_argument.md) và test_method_example.py/fixture synthetic liên quan Q02/Q04/Q05/Q06/Q10/Q11. Có bản lập luận và phép tính tay để review, chưa có xác nhận reviewer hay independent PASS; toàn bộ Q-ID vẫn PENDING.

Chuẩn bị Q04/Q06/Q08/Q09/Q10/Q11: [numeric audit](../reviews/tv4_numeric_audit_20261002.md) có counterexample và DEV fix cost-policy/tie. Enclosure chỉ primitive arithmetic, không sai số geometry hoặc sign-off; các Q-ID vẫn PENDING.

Review thực tại commit TV1 1f583e9 ngày 03/10/2026: [phiếu TV4](../reviews/tv4_tv1_candidates_review_20261003.md) và [evidence](../evidence/tv1_review_1f583e9_20261003.json). Q03/Q05/Q13 có đề xuất/fixtures, chưa đóng; CHANGES_REQUESTED cho J/provenance/coverage. Không coi review AI APPROVED là sign-off hoặc oracle độc lập.

Review tiếp tại c970a18: [phiếu TV4](../reviews/tv4_tv1_candidates_rereview_c970a18_20261003.md), F1–F5 closed DEV; F6 partial/F7 evidence provenance còn mở. CHANGES_REQUESTED; Q03/Q05/Q13 và toàn bộ gate vẫn PENDING, chưa merge hoặc independent PASS.

## Q01 — CLOSED_ACKNOWLEDGEMENT_ONLY, 03/10/2026

Owner TV3 đã ghi nhận việc oracle không chờ máy trong docs/handoff/tv3_progress.md tại d84c24177a3afe69bbbf9add526614755d275091 (origin/codex/tv3-research-oracle-20261002). TV4 đã xác minh log/import boundaries; bước điều phối nhận việc hoàn tất. Không là human sign-off/oracle nghiệm thu: [review O1–O5](../reviews/tv4_tv3_oracle_review_d84c241_20261003.md) CHANGES_REQUESTED. Q02/Q04/Q08/Q10 và các gate khác PENDING. Không ghi TV2 đã ký thay người.

TV1 tại ce3f92d: [recheck cuối](../reviews/tv4_tv1_final_recheck_ce3f92d_20261003.md), F1–F7 CLOSED_DEV_HANDOFF. Q03/Q05/Q13/Q16 và chất lượng vẫn PENDING; Q01 chỉ nhận việcTV3 đã hoàn tất, không oracle nghiệmthu. Chưa mergeTV1.
