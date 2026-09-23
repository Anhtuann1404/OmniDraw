# OmniDraw — Master Review Disposition Chương 1–3

```text
INTEGRATION_OWNER: TV4
REVIEW_TARGET_COMMIT: 7ae43e6994506928cb6be8bd61e936b4f5e3857e
DISPOSITION_STATUS: TV2_DRAFT_ADDRESSED_AWAITING_RECHECK
RQ_FREEZE_RECOMMENDATION: PENDING
```

Đọc [`README.md`](README.md) trước khi cập nhật. File này là sổ xử lý finding; không thay thế chữ ký độc lập của TV1–TV3.

**Nguồn TV2:** phiếu do TV2 gửi ngày 2026-09-23 ghi `AI_DRAFT_VERDICT: PASS_WITH_CHANGES`, `HUMAN_VERDICT: PENDING` và review commit `5e9c857e42021f8a48d45b1fdaefcfdb87e82ff3`, khác checkpoint v0.2 `7ae43e6994506928cb6be8bd61e936b4f5e3857e`. Sáu finding dưới đây được tiếp nhận để TV4 xử lý, **chưa phải verdict hợp lệ của gói v0.2**. TV2 cần recheck bản tài liệu mới, đồng bộ phiếu thuộc repository và tự xác nhận verdict; không thay `REVIEW_TARGET_COMMIT` của cả gói chỉ để khớp phiếu cũ.

## 1. Tổng hợp verdict

| Reviewer | Workflow status | Human verdict | Commit đã review | Finding mở | Ngày xác nhận |
| :--- | :--- | :--- | :--- | ---: | :--- |
| TV1 | `NOT_STARTED` | `PENDING` | `7ae43e6994506928cb6be8bd61e936b4f5e3857e` | PENDING | PENDING |
| TV2 | `BLOCKED` — draft đã được TV4 xử lý, chờ recheck/version binding | `PENDING` | `5e9c857e42021f8a48d45b1fdaefcfdb87e82ff3` (khác target v0.2) | 6 chờ TV2 recheck | PENDING |
| TV3 | `NOT_STARTED` | `PENDING` | `7ae43e6994506928cb6be8bd61e936b4f5e3857e` | PENDING | PENDING |

## 2. Master finding log

| Finding ID | Reviewer | Severity | File:mục | Tóm tắt | Disposition | Owner | Bằng chứng sửa/giải trình | Recheck |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TV2-R01 | TV2 | MAJOR | Docs 07 §8.2; 10 §3.5; 15 §3.5.2 | Tổng cost chưa tách nhánh connect/lift | `ACCEPTED` | TV4 | Đã ghi $J_{transition}=\min(J_{conn},J_{lift})$, chỉ áp dụng hạng tử theo nhánh và giữ B3 hiện hành riêng; E4 là gate kỹ thuật độc lập | `PENDING_TV2_RECHECK` |
| TV2-R02 | TV2 | MAJOR | Docs 10 §4.3; 15 §3.7.2 | Thiếu `acute_turn_count_120deg` trong bảng metric dù H3.2 yêu cầu | `ACCEPTED` | TV4 (docs); TV2 (metric trước PR5) | Đã thêm hàng metric với trạng thái chưa triển khai/diagnostic; không tuyên bố đã đo | `PENDING_TV2_RECHECK`; code metric chờ PR5 |
| TV2-R03 | TV2 | MINOR | Docs 13 §2.4; 15 §3.8 | $O(NK^2)$ chỉ đếm cạnh, chưa tính collision geometry | `ACCEPTED` | TV4 | Đã phân biệt DP edge count với cận $O(NK^2L_{geom})$, $L_{geom}=O(L_{bridge}L_{glyph})$ cho kiểm tra đơn giản; cache và candidate generation tính riêng | `PENDING_TV2_RECHECK` |
| TV2-R04 | TV2 | MINOR | Docs 14 §1.4.1; 15 §3.3.1 | B2 có thể bị hiểu nhầm là tự chọn vị trí dấu | `ACCEPTED` | TV4 | Đã ghi B1/B2/B3 gắn dấu hậu xử lý bằng anchor tĩnh; B2 chỉ tham lam trên `GlyphVariant` | `PENDING_TV2_RECHECK` |
| TV2-R05 | TV2 | MINOR | Docs 05 §1.1; 10 §§3.1, 4.4 | H1.2 chưa rõ tỷ lệ giảm trên corpus | `ACCEPTED` | TV4 | Đã khóa công thức tỷ lệ trên tổng `pen_lift_count` của cùng corpus; mẫu số 0 là `NOT_APPLICABLE`, không dùng median từng từ | `PENDING_TV2_RECHECK` |
| TV2-R06 | TV2 | MINOR | Docs 05 PR2; 10 status; 14 §1.9; 15 §§3.1.3, 3.7.4 | Cần tách E3 đã PASS khỏi E4 còn chờ | `ACCEPTED` | TV4 | Docs 15 đã tách E3/E4 trước đợt này; đã đồng bộ thêm Docs 05/10/14, không coi review học thuật là E4 sign-off | `PENDING_TV2_RECHECK` |

Disposition hợp lệ:

- `ACCEPTED`: sẽ/đã sửa; phải có owner và bằng chứng thay đổi.
- `REJECTED_WITH_REASON`: không sửa; phải giải thích dựa trên nguồn chuẩn hoặc code/evidence.
- `DEFERRED_WITH_OWNER`: ngoài gate hiện tại; phải có owner, mốc/gate tiếp theo và không được trình bày như đã hoàn tất.

Không xóa finding sau khi xử lý. Giữ nguyên ID để tạo audit trail.

## 3. Checklist đóng gói

- [ ] `REVIEW_TARGET_COMMIT` giống nhau trong README, ba phiếu và file này.
- [ ] Đã nhận đủ human verdict của TV1, TV2 và TV3.
- [ ] Mọi finding được chép vào master log và có disposition.
- [ ] Không còn finding `CRITICAL` hoặc `MAJOR` ở trạng thái mở.
- [ ] Finding `DEFERRED_WITH_OWNER` có owner và gate cụ thể.
- [ ] Reviewer đã recheck thay đổi liên quan và đóng finding.
- [ ] Docs 02/03/05/07/08/09/10–15 không còn mâu thuẫn trạng thái.
- [ ] Không biến review tài liệu thành bằng chứng PR2/PR3, corpus freeze, formal experiment hoặc hardware validation.
- [ ] TV4 chỉ chuyển `RQ_FREEZE_RECOMMENDATION` khỏi `PENDING` sau khi các điều kiện trên đạt.

## 4. Kết luận tích hợp

- Thay đổi đã thực hiện: `TV2-R01`–`TV2-R06` đã được TV4 xử lý ở mức tài liệu; chưa được reviewer kiểm tra lại. Code metric của `TV2-R02` vẫn là dependency trước PR5, không được ghi là kết quả đo.
- Finding bị bác bỏ và lý do: không có trong sáu finding TV2 đã tiếp nhận.
- Finding hoãn và gate tiếp theo: không có finding tài liệu bị hoãn; phần code metric H3.2 thuộc PR5 và E4 vẫn là gate kỹ thuật riêng.
- Rủi ro còn lại: phiếu TV2 nguồn chưa có human verdict và dùng commit khác checkpoint v0.2; TV1/TV3 vẫn chờ; E4, PR3 và formal benchmark chưa đóng.
- `RQ_FREEZE_RECOMMENDATION`: `PENDING`
- TV4 xác nhận: `PENDING`
- Ngày: `PENDING`
