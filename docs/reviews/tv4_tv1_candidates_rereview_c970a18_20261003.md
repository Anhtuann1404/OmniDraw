# TV4 review lại TV1 — c970a18, 03/10/2026

**Verdict: CHANGES_REQUESTED cho claim Q03 và provenance evidence. F1–F5 CLOSED trong phạm vi DEV; F6 PARTIALLY_RESOLVED.** Không merge TV1, không nghiệm thu font/quality/DP/oracle, không đóng Q01–Q16 hoặc mở HOLDOUT. Phiếu cũ tại 1f583e9 giữ nguyên lịch sử.

Target `c970a18a706b983fc8fda3659aa7c16e836b3c72`, remote đã fetch; cb38f64 là ancestor. Diff so nhánh TV4 cb38f64 chỉ có 7 file TV1 (builder, hai manifest, tests, hai handoff, evidence); không sửa engine/TV2/hardware. Review trên git archive riêng `/private/tmp/omnidraw-tv1-review-c970a18`, không checkout/reset dirty work.

## Đối chiếu F1–F6

| Finding | Kết quả | Bằng chứng/giới hạn |
|---|---|---|
| F1 | CLOSED về số học | Cả 4 ca × 2 modes khớp tuyệt đối L_down/L_up/N_cycle/J/candidate IDs/exact ratio với evidence. Metadata commit còn F7 bên dưới. |
| F2 | CLOSED về xuất xứ DEV | Synthetic self-authored polylines, CC-BY-4.0 declaration, authoring_digest, reference_geometry=null. Digest là metadata tác giả; candidate hash khóa geometry. Không là hash font hoặc reference thật, Q03/Q16 PENDING. |
| F3 | CLOSED | Probe sau body owner 1 và owner 2: k2 PASS, k1/k0 từ chối đúng deadline. |
| F4 | CLOSED | Case03 được mô tả delayed multi-body; giữ case_id cũ để tương thích. Case04 có graph {0:[2],1:[],2:[0]}, incompatible swash/flourish; cả modes chọn compact/standard/compact, J=25.918342316257434. Chưa thay oracle độc lập. |
| F5 | CLOSED | Test CONNECT dương có delta_up=0/delta_cycles=0/N_cycle=1; thiếu whitelist/lệch endpoint bị từ chối. Case03 chỉ kiểm declared contact, không claim traversal CONNECT. |
| F6 | PARTIALLY_RESOLVED | Có định nghĩa clearance dấu trên/dưới/chồng và bảng kích thước khớp coordinates. Claim tuân thủ toàn bộ quality bounds chưa có đủ căn cứ; xem dưới. |

## F6 — P2: Bảng đo chưa chứng minh tuân thủ toàn bộ bounds Q03

Nguồn [proposal tại target, dòng 70–99](https://github.com/Anhtuann1404/OmniDraw/blob/c970a18a706b983fc8fda3659aa7c16e836b3c72/docs/handoff/tv1_proposals_q03_q05_q13.md#L70), [claim progress dòng 49](https://github.com/Anhtuann1404/OmniDraw/blob/c970a18a706b983fc8fda3659aa7c16e836b3c72/docs/handoff/tv1_progress.md#L49).

Proposal đặt ΔAR≤10% nhưng case04 o-swash có AR=3.95/1.8 so compact=1.5/1.8: biến thiên **163.33%**; o2-flourish so o2-compact: **45%**. Bảng vẫn gán ĐẠT cho flourish, progress claim toàn bộ ứng viên tuân thủ bounds. Nếu flourish thuộc class riêng/toy chỉ kiểm interaction, phải khai báo class, baseline AR0 và scope exemption cụ thể; không áp ngầm quality exemption. Bảng chưa có theta_candidate/nominal/Δtheta hoặc quy tắc xác định nét/trục chính ổn định; “hồi quy hoặc đoạn chính” chưa là measurement policy tái lập. hx=height toàn body hợp các nguyên âm DEV, nhưng b/t có ascender trong bảng cần nhãn body bbox height thay vì x-height nếu không có baseline/meanline thật.

Yêu cầu TV1: giới hạn nhãn ĐẠT ở metric clearance đã đo; ghi NOT_EVALUATED cho góc/quality tổng thể, hoặc bổ sung policy và measurements/AR0 theo class. Ghi rõ variant nào loại trước khóa G nếu áp bounds10%; nếu giữ toy fixture vượt bounds, gắn exception DEV_ONLY ngoài quality evaluation. Không đổi numeric thresholds để làm đẹp kết quả, không tự freeze Q03. Chưa có reference thật nên reference-relative quality vẫn PENDING.

## F7 — P2: Evidence không tái lập từ head_commit khai báo

Nguồn [evidence dòng 3](https://github.com/Anhtuann1404/OmniDraw/blob/c970a18a706b983fc8fda3659aa7c16e836b3c72/docs/evidence/tv1_dev_cases_evidence.json#L3). `head_commit=ff236872dcc7bfb35763c5ac227fb39e672c05b0`, nhưng `git show ff23687:dataset/research/dev/tv1_dev_manifest.json` vẫn cho **3 ca, manifest c69090b7…**, khác evidence 4 ca/4c62fa2e…. Số học khớp target c970a18 nhưng metadata không chỉ ra input đã chạy.

Yêu cầu TV1: tạo follow-up evidence trên clean snapshot c970a18, ghi source/input commit đầy đủ + lệnh + môi trường; evidence được commit sau target, không tự yêu cầu file chứa hash của chính commit nó. Hoặc khai báo parent + dirty/input content digest chính xác nếu chạy trên working tree. Giữ source/input commit và review-target rõ ràng, không thay hash bằng HEAD mà không chạy lại.

## Kiểm chứng TV4

- Manifest canonical SHA-256 **4c62fa2e7a4bdfd297e9d959062f450900bcd5a52ef1150cdbaecfec0b047993**; export vào temporary path khớp bytes cả dataset và fixture. Đây là canonical manifest hash, không SHA256 raw JSON bytes.
- `PYTHONPATH=backend <repo>/backend/venv/bin/python3 -m pytest tests/research/test_tv1_candidates.py -q`: **13 PASS, .10s**.
- Cùng interpreter/PYTHONPATH, `pytest tests/research backend/test_handwriting_validation.py -q`: **224 PASS, 2.64s** (190 research + 34 handwriting), Python3.14; một AnyIO deprecation warning có sẵn. Không cộng hai batches. Không chạy lại batch acceptance 79/~421s TV1 báo; chỉ ghi reported.
- [Evidence TV4](../evidence/tv1_review_c970a18_20261003.json) lưu 8 runs xác minh exact equality, builder và graph; không gọi TV4 checker là independent oracle. TV3 NOT_RUN.

Bước tiếp theo: TV1 sửa F6/F7 trong phạm vi owner rồi bàn giao commit + evidence mới; TV2/TV3 có thể dùng bốn ca như synthetic DEV inputs tại target đã pin. Chưa coi quality/reference được duyệt. Merge tích hợp do TV4 xử lý sau recheck; tránh cùng sửa docs tổng hợp, giữ log TV1 riêng và resolve conflict theo nội dung/evidence, không blanket ours/theirs. PR3 giữ đóng.
