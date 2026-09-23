# OmniDraw — Master Review Disposition Chương 1–3

```text
INTEGRATION_OWNER: TV4
REVIEW_TARGET_COMMIT: 7ae43e6994506928cb6be8bd61e936b4f5e3857e
DISPOSITION_STATUS: FINDINGS_RECONCILED_AWAITING_VERSION_BINDING_AND_SCOPED_RECHECK
RQ_FREEZE_RECOMMENDATION: PENDING
```

Đọc [`README.md`](README.md) trước khi cập nhật. File này là sổ xử lý finding; không thay thế chữ ký độc lập của TV1–TV3.

**Nguồn TV2:** phiếu hiện ghi `WORKFLOW_STATUS: CLOSED`, `HUMAN_VERDICT: PASS` và TV2-R01–R06 `VERIFIED_CLOSED` sau khi recheck commit `e26af4fd2559c2e28672fff1a11865bf427683a8` ngày 2026-09-23. Phiếu vẫn để `REVIEW_TARGET_COMMIT` là commit review gốc `5e9c857e42021f8a48d45b1fdaefcfdb87e82ff3`, khác checkpoint gói v0.2 `7ae43e6994506928cb6be8bd61e936b4f5e3857e`. TV2 cần tự chỉnh metadata của phiếu để trường này khớp checkpoint, giữ commit gốc và commit recheck ở các trường riêng; TV4 không sửa chữ ký hoặc verdict của reviewer.

**Thay đổi sau checkpoint:** commit `e26af4f` sửa Docs 10, 13, 14 và 15, trong đó có các mục thuộc phạm vi phiếu TV1/TV3. TV1 đã PASS scoped recheck trên `031d198` trong phiếu tại commit `e4f0dfd`; TV3 vẫn cần xác nhận lại đúng phần bị ảnh hưởng trước khi TV4 đề xuất `RQ FREEZE: APPROVED`. Đây là recheck tài liệu, không phải mở lại corpus freeze hay hardware gate.

- TV1 đã recheck các thay đổi trong Docs 10 (trạng thái PR2/E4 và công thức H1.2), Docs 14 §1.9, Docs 15 §§3.1/3.7/3.8 trên `031d198`; không mở lại corpus freeze.
- TV3 recheck các thay đổi trong Docs 10 liên quan RQ3, Docs 14 §1.9 và Docs 15 §§3.1/3.7/3.8; xác nhận chúng không biến simulation hay ngưỡng clearance thành claim máy thật.

## 1. Tổng hợp verdict

| Reviewer | Workflow status | Human verdict | Commit đã review | Finding mở | Ngày xác nhận |
| :--- | :--- | :--- | :--- | ---: | :--- |
| TV1 | `CLOSED`; scoped recheck đã hoàn tất | `PASS` trên `031d198` | Checkpoint `7ae43e6994506928cb6be8bd61e936b4f5e3857e`; recheck `031d1983f07895306a0cf31b72300ad4d9e5ee50` (phiếu tại `e4f0dfd`) | 0; TV1-R01–R03 tiếp tục đóng | 23/09/2026 |
| TV2 | `CLOSED`; còn lệch metadata `REVIEW_TARGET_COMMIT` | `PASS` sau recheck | Gốc `5e9c857e42021f8a48d45b1fdaefcfdb87e82ff3`; checkpoint `7ae43e6`; recheck `e26af4f` | 0; TV2-R01–R06 đã đóng | 23/09/2026 |
| TV3 | `CLOSED` trên checkpoint; scoped recheck sau `e26af4f` còn chờ | `PASS` trên `7ae43e6` | `7ae43e6994506928cb6be8bd61e936b4f5e3857e` | 0 finding gốc; recheck phần thay đổi còn chờ | 23/09/2026 |

## 2. Master finding log

| Finding ID | Reviewer | Severity | File:mục | Tóm tắt | Disposition | Owner | Bằng chứng sửa/giải trình | Recheck |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TV1-R01 | TV1 | MINOR | Docs 10 §4.4; 14 §§1.5.3, 1.9 | Phân biệt dữ liệu thu thập người viết và corpus benchmark kỹ thuật | `ACCEPTED` | TV1 (review); TV4 (duy trì wording) | Phiếu TV1 xác nhận hai nguồn dữ liệu được tách; không diễn giải dữ liệu P2 dự kiến như đã thu thập | `VERIFIED_CLOSED` tại `7ae43e6`, recheck `031d198` |
| TV1-R02 | TV1 | MINOR | Docs 10 §4.4; 15 §3.7.3 | DEV/Holdout phải rời nhau, runner không mở Holdout mặc định | `ACCEPTED` | TV1 | Phiếu TV1 ghi DEV/Holdout disjoint và Holdout chỉ chạy bằng cờ tường minh; corpus freeze được lưu riêng | `VERIFIED_CLOSED` tại `7ae43e6`, recheck `031d198` |
| TV1-R03 | TV1 | MINOR | Docs 13 §2.2; 14 §1.5.3; 15 §3.8 | Writer Profile P2 không được trình bày như CA-VHC P0 đã học thói quen | `ACCEPTED` | TV4 (docs); TV1 (review) | Phiếu TV1 xác nhận ranh giới P0/P2 trong tài liệu được giữ rõ | `VERIFIED_CLOSED` tại `7ae43e6`, recheck `031d198` |
| TV2-R01 | TV2 | MAJOR | Docs 07 §8.2; 10 §3.5; 15 §3.5.2 | Tổng cost chưa tách nhánh connect/lift | `ACCEPTED` | TV4 | Đã ghi $J_{transition}=\min(J_{conn},J_{lift})$, chỉ áp dụng hạng tử theo nhánh và giữ B3 hiện hành riêng; E4 là gate kỹ thuật độc lập | `VERIFIED_CLOSED` tại `e26af4f` |
| TV2-R02 | TV2 | MAJOR | Docs 10 §4.3; 15 §3.7.2 | Thiếu `acute_turn_count_120deg` trong bảng metric dù H3.2 yêu cầu | `ACCEPTED` | TV4 (docs); TV2 (metric trước PR5) | Đã thêm hàng metric với trạng thái chưa triển khai/diagnostic; không tuyên bố đã đo | `VERIFIED_CLOSED` tại `e26af4f`; code metric chờ PR5 |
| TV2-R03 | TV2 | MINOR | Docs 13 §2.4; 15 §3.8 | $O(NK^2)$ chỉ đếm cạnh, chưa tính collision geometry | `ACCEPTED` | TV4 | Đã phân biệt DP edge count với cận $O(NK^2L_{geom})$, $L_{geom}=O(L_{bridge}L_{glyph})$ cho kiểm tra đơn giản; cache và candidate generation tính riêng | `VERIFIED_CLOSED` tại `e26af4f` |
| TV2-R04 | TV2 | MINOR | Docs 14 §1.4.1; 15 §3.3.1 | B2 có thể bị hiểu nhầm là tự chọn vị trí dấu | `ACCEPTED` | TV4 | Đã ghi B1/B2/B3 gắn dấu hậu xử lý bằng anchor tĩnh; B2 chỉ tham lam trên `GlyphVariant` | `VERIFIED_CLOSED` tại `e26af4f` |
| TV2-R05 | TV2 | MINOR | Docs 05 §1.1; 10 §§3.1, 4.4 | H1.2 chưa rõ tỷ lệ giảm trên corpus | `ACCEPTED` | TV4 | Đã khóa công thức tỷ lệ trên tổng `pen_lift_count` của cùng corpus; mẫu số 0 là `NOT_APPLICABLE`, không dùng median từng từ | `VERIFIED_CLOSED` tại `e26af4f` |
| TV2-R06 | TV2 | MINOR | Docs 05 PR2; 10 status; 14 §1.9; 15 §§3.1.3, 3.7.4 | Cần tách E3 đã PASS khỏi E4 còn chờ | `ACCEPTED` | TV4 | Docs 15 đã tách E3/E4 trước đợt này; đã đồng bộ thêm Docs 05/10/14, không coi review học thuật là E4 sign-off | `VERIFIED_CLOSED` tại `e26af4f` |
| TV3-R01 | TV3 | MINOR | Docs 10 §3.3; 14 §1.4.3 | Không đồng nhất thời gian mô phỏng với `actual_draw_time_sec` máy thật | `ACCEPTED` | TV3 (review); TV4 (duy trì wording) | Phiếu TV3 xác nhận simulator chỉ ước tính; physical feasibility vẫn `PENDING_TV3_CALIBRATION` | `VERIFIED_CLOSED` tại `7ae43e6` |
| TV3-R02 | TV3 | MINOR | Docs 15 §§3.7.4, 3.8 | Phân biệt technical minimum 0.20 mm và provisional target 0.50 mm | `ACCEPTED` | TV3 (review); TV4 (duy trì wording) | Phiếu TV3 xác nhận không diễn giải ngưỡng hình học thành an toàn cơ khí khi chưa hiệu chuẩn | `VERIFIED_CLOSED` tại `7ae43e6` |

Disposition hợp lệ:

- `ACCEPTED`: sẽ/đã sửa; phải có owner và bằng chứng thay đổi.
- `REJECTED_WITH_REASON`: không sửa; phải giải thích dựa trên nguồn chuẩn hoặc code/evidence.
- `DEFERRED_WITH_OWNER`: ngoài gate hiện tại; phải có owner, mốc/gate tiếp theo và không được trình bày như đã hoàn tất.

Không xóa finding sau khi xử lý. Giữ nguyên ID để tạo audit trail.

## 3. Checklist đóng gói

- [ ] `REVIEW_TARGET_COMMIT` giống nhau trong README, ba phiếu và file này.
- [x] Đã nhận đủ human verdict của TV1, TV2 và TV3; TV1 đã scoped recheck trên `031d198`, hiệu lực chung vẫn phụ thuộc scoped recheck TV3 và version binding TV2.
- [x] Mọi finding TV1-R01–R03, TV2-R01–R06 và TV3-R01–R02 được chép vào master log và có disposition.
- [x] Không còn finding `CRITICAL` hoặc `MAJOR` ở trạng thái mở trong các phiếu hiện tại.
- [x] Không có finding `DEFERRED_WITH_OWNER` trong vòng này; điều kiện owner/gate không phát sinh.
- [ ] Reviewer đã recheck thay đổi liên quan và đóng finding.
- [ ] Docs 02/03/05/07/08/09/10–15 không còn mâu thuẫn trạng thái.
- [x] Không biến review tài liệu thành bằng chứng PR2/PR3, corpus freeze, formal experiment hoặc hardware validation; các gate này có bằng chứng và trạng thái riêng.
- [ ] TV4 chỉ chuyển `RQ_FREEZE_RECOMMENDATION` khỏi `PENDING` sau khi các điều kiện trên đạt.

## 4. Kết luận tích hợp

- Thay đổi đã thực hiện: TV1-R01–R03 đã được TV1 scoped recheck và giữ `VERIFIED_CLOSED` tại `031d198`; TV3-R01–R02 vẫn theo phiếu PASS tại checkpoint `7ae43e6`; TV2-R01–R06 đã được TV2 recheck và đóng tại `e26af4f`. Code metric của TV2-R02 vẫn là dependency trước PR5, không được ghi là kết quả đo.
- Finding bị bác bỏ và lý do: không có.
- Finding hoãn và gate tiếp theo: không có finding tài liệu bị hoãn; phần code metric H3.2 thuộc PR5 và E4 vẫn là gate kỹ thuật riêng.
- Rủi ro còn lại: metadata `REVIEW_TARGET_COMMIT` trong phiếu TV2 khác checkpoint v0.2; TV3 cần scoped recheck phần tài liệu bị `e26af4f` sửa sau checkpoint; E4, PR3 và formal benchmark chưa đóng.
- `RQ_FREEZE_RECOMMENDATION`: `PENDING`
- TV4 xác nhận: `PENDING`
- Ngày: `PENDING`
