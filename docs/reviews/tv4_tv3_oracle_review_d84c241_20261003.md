# TV4 review TV3 oracle d84c241 — 03/10/2026

**Verdict implementation: CHANGES_REQUESTED. Q01 nhận việc: CLOSED_ACKNOWLEDGEMENT_ONLY.** TV3 đã nhận oracle không chờ máy, giữ ownership/hardware riêng và chỉ import schema + stdlib + modules oracle trong package. Đây là xác minh kỹ thuật log nhận việc, không human sign-off, independent PASS toàn solver hoặc nghiệm thu Q02/Q04/Q08/Q10. Không dùng d84c241 làm ground truth nghiệm thu cho DP/top-m trước sửa và recheck.

Target `d84c24177a3afe69bbbf9add526614755d275091`, branch origin/codex/tv3-research-oracle-20261002, base9659946. Đã fetch đúng nhánh; thông báo trước về thiếu log chỉ áp dụng remote lúc kiểm trước đó, nay superseded. Diff7files chỉ oracle/tests/log owner; không hardware. Review git archive `/private/tmp/omnidraw-tv3-review-d84c241`, bảo toàn dirty TV4, không merge/chỉnh owner code.

## O1 — P1: Không thực hiện đúng cost policy đã khai báo

[enumerator.py L89](https://github.com/Anhtuann1404/OmniDraw/blob/d84c24177a3afe69bbbf9add526614755d275091/backend/research/independent_oracle/enumerator.py#L89): calculate_stroke_length dùng total+=point_distance/hypot; policy tv4-dev-dyadic-primitive-cost-v1 khóa stroke primitive fsum của math.dist trên segments. Fraction không sửa rounding đã xảy ra trước Fraction.

Probe một owner/one variant, polyline `[(i*.3,(i%3)*.17) for i in range(12)]`, theta(.5,2), input đầy đủ trong evidence: cả OPTIMAL, oracle ratio **16842350292829887/2251799813685248**, DP **16842350292829889/2251799813685248**. Length oracle4.118844429781222 vs primitive fsum4.118844429781223. Đây là lỗi contract về exact primitive semantics, không tolerance được duyệt. Tự viết accumulator đúng policy, không import helper TV4; nếu dùng primitive khác phải ID/proposal riêng và thống nhất trước đối soát. Test exact ratios/true ties/multisegment, không chỉ math.isclose (rel_tol1e-9 trên lambda2^53 che khác biệt rất lớn). Tests hiện không chứng minh “khớp tuyệt đối100%” tổng quát.

## O2 — P1: Budget không bao toàn bộ enumerate/search/memory

[enumerator.py L220](https://github.com/Anhtuann1404/OmniDraw/blob/d84c24177a3afe69bbbf9add526614755d275091/backend/research/independent_oracle/enumerator.py#L220): materialize toàn Cartesian configs trước try/budget; memory_limit_mb không được dùng; primitive loops không guard. Search chỉ check mỗi500states L298 và không check cuối trước OPTIMAL. Probe max_states1 trên stacked trả RESOURCE_LIMIT sau500states, đã giữ incumbent vượt ngân sách; config chỉ1 với search<500 có thể trả OPTIMAL ngoài max_states. Chưa khóa/enforce scope n/q/k/actions nhỏ mà log mô tả. Cần streaming configs, guard trước cấp phát/chuyển state/geometry và cuối, memory scope đo được, incomplete flags/incumbent đúng nghĩa, registered scope hoặc rejection rõ; tests tiny budget cả có/không incumbent và không vượt completion claim.

## O3 — P1: Không kiểm split/policy/contact contract trước solve

[enumerator.py L169](https://github.com/Anhtuann1404/OmniDraw/blob/d84c24177a3afe69bbbf9add526614755d275091/backend/research/independent_oracle/enumerator.py#L169), geometry L97: accepts case split=holdout và unknown numeric policy rồi trả OPTIMAL/search_complete. Probe HOLDOUT chỉ là relabel synthetic input, không đọc dữ liệu niêm phong thực. Contact location không shared endpoint chỉ trả INFEASIBLE ở probe thay vì lỗi unsupported/invalid contact; nếu dùng radius đủ lớn có thể miễn clearance không đúng policy. Cần whitelist geometry/contact/flatten/separation/numeric policy IDs độc lập, exact endpoint/radius validity, split dev/synthetic guard trước enumerate; không âm thầm giải input khác contract. Không tự freeze tolerance/near-contact. Các kiểm tra schema hiện không thay policy validation của implementation.

## O4 — P2: Provenance trỏ commit không chứa oracle

[adapter.py L36](https://github.com/Anhtuann1404/OmniDraw/blob/d84c24177a3afe69bbbf9add526614755d275091/backend/research/independent_oracle/adapter.py#L36) hardcode git_commit9659946, dirty_patch=null. Commit9659946 không có package oracle. Cần source snapshot thực + dirty content digest nếu có, version/config hash ràng policy/implementation; phát evidence vào commit sau source commit, không self hash giả. Progress chưa điền commit bàn giao có thể ghi source ở follow-up. NOT_RUN được giữ đúng, chưa sửa thành PASS.

## O5 — P2: Bounds dùng displayed float thay enclosure exact cost

[adapter.py L71](https://github.com/Anhtuann1404/OmniDraw/blob/d84c24177a3afe69bbbf9add526614755d275091/backend/research/independent_oracle/adapter.py#L71) đặt lower=upper=J_float; với exact Fraction không biểu diễn được float, một phía cận sai. Dùng outward enclosure tự viết theo cost policy; incomplete chỉ upper incumbent, không lower từ incumbent. Guard overflow/conversion finite; không gọi enclosure primitive arithmetic là bound sai số Euclid thật. Test Fraction so bounds exact, subnormal/large/overflow.

## Xác minh và giới hạn

`PYTHONPATH=backend <repo>/backend/venv/bin/python3 -m pytest tests/research -q` tại archive → **209 PASS,1.56s**,1AnyIO warning,Python3.14. 32 oracle tests nằm trong batch209; không cộng batches. BaseTV4 không chứa13 testsTV1 nên209=177+32, không có nghĩa regres190TV1 branch đã chạy. Imports AST/source package chỉ stdlib/schema/local, harness ngoài package importTV4 hợp ranh giới. Không chứng minh lịch sử tác giả chỉ từ imports. Đối soát fixture hand/method/numeric trong suite đạt phạm vi assertions hiện có, không thay O1–O5. Không chạy HOLDOUT/máy hoặc nghiệm thu hardware; hardware PENDING_TV3_CALIBRATION theo owner báo, không kiểm lại máy.

[Evidence probes](../evidence/tv3_review_d84c241_20261003.json) chứa case/budget/theta/raw results tái lập: gọi solve_oracle và solve_joint từ harness ngoài package. Inputs đã prepare hash lại; metadata adapter chứng minh commit9659946/bounds display. Phiếu TV4 là technical review, human approval vẫn cần người có thẩm quyền.

TV3 sửa O1–O5, chạy regressions và hand probes từ raw data, xuất source/evidence hashes/lệnh/complete flags; bàn giao commit mới. TV2 review scope và dùng oracle chỉ exploratory tới recheck. TV4 chưa thêm default adapter hoặc merge. PR3 giữ đóng, mọi gate ngoài Q01 nhận việc còn PENDING.
