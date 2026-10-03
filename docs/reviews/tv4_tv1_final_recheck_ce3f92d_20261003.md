# TV4 final recheck TV1 — ce3f92d, 03/10/2026

**Verdict: REVIEWED_DEV_HANDOFF_WITH_OPEN_GATES. F1–F7 CLOSED trong phạm vi bàn giao synthetic DEV.** Không human sign-off/quality/font/solver/oracle acceptance, không đóng Q03/Q05/Q13/Q16, không mở HOLDOUT. TV1 có thể tiếp tục kế hoạch dữ liệu/font/reference theo ownership; không làm lại F1–F7 đã đóng.

Target `ce3f92dafa156bf6dbf605c7026bbdd6c0f3b448`, remote codex/tv1-research-candidates-20261002 đã fetch. 138b647 là ancestor; từ c970a18 code/backend/tests/dataset không đổi; sửa proposal/log/evidence và merge reviewdocs. Kiểm git archive riêng `/private/tmp/omnidraw-tv1-review-ce3f92d`, dirty work TV4 bảo toàn, chưa merge nhánh TV1 vào TV4/main/develop.

## Disposition

| Finding | Recheck |
|---|---|
| F1–F5 | CLOSED từ c970a18; inputs/code giữ nguyên, regressions và 8runs xác minh lại. |
| F6 | CLOSED về claim/định nghĩa DEV: hx nguyên âm và h_bbox ascender tách riêng; angle NOT_EVALUATED; ARswash+163.33%/flourish+45% VƯỢT10%, DEV_ONLY_INTERACTION_PROBE_EXEMPT mô tả rõ chỉ toyinteraction, nếu áp typography filter sẽ loại trước khóaG. Overall Q03 PENDING, không nới bounds. |
| F7 | CLOSED: source_input_commit/target_review_commit c970a18 thật chứa4ca/hash4c62fa2e…; environment/manifestpath/command/budget có metadata, source khác commit chứa evidence hợp lệ. TV4 tái sinh và chạy lại khớp; không coi đây là xác minh trực tiếp môi trường Windows owner. |

## Bằng chứng tái lập

- Canonical manifest SHA256 `4c62fa2e7a4bdfd297e9d959062f450900bcd5a52ef1150cdbaecfec0b047993`; builder temporary export bytes bằng dataset/fixture, input ởsource c970a18 không đổi.
- `PYTHONPATH=backend <repo>/backend/venv/bin/python3 -m pytest tests/research backend/test_handwriting_validation.py -q` tại archive: **224 PASS (190research +34handwriting),2.89s**,Python3.14,1AnyIO deprecation warning. 13testsTV1 nằm trong190; không cộng batches. Các timing13/.88s/190/31.98s/47/13.92s owner báo không là timing TV4.
- Harness TV4 dùng load_manifest/export builder/solve_joint no-forget vàsafe-forget,theta(.5,2),budget10000ms/100000states/10000configs/64MB. Cả8runs khớp tuyệt đối coefficient floats,J,candidate IDs,exact ratios và graph; xem [evidence recheck](../evidence/tv1_review_ce3f92d_20261003.json). Không dùng oracleTV3 đang có O1–O5 để nghiệm thu.

## Ghi chú không chặn đóng findings

Bảng pending_decisions đã kế thừa Q01 CLOSED_ACKNOWLEDGEMENT_ONLY đúng từ138b647. Log riêng tv1_progress còn câu tất cả16gatesPENDING/chờTV3 nhận oracle là tóm tắt cũ; lần cập nhật log tiếp theo TV1 nên ghi Q01 nhận việc hoàn tất, oracle implementation CHANGES_REQUESTED/Q10PENDING. Các records cũ giữ lịch sử scope.

AR0=0 của t stem thẳng: biểu thức biến thiên tương đối0/0 không định nghĩa. Dòng baseline chỉ là nhãn kiểm so với chính nó, không dùng để claim quality tổng thể; khi triển khai filter chính thức cần policy NA/classmetric cho glyph width0. Ngưỡng đangPROPOSED vàqualityPENDING, không chặn toy DEV dùng kiểm solver.

Lệnh evidence pytest hiện tái lập tests nhưng không xuất file evidence; exact ratios được TV4 kiểm riêng ở harness. Khi làm runner/pilot cần script xuất evidence có version thay copy manual. Không yêu cầu đổi dataset hay tựthêm fields schema trong slice này.

TV4 dọn prompt khỏi task sửaF1–F7; phiếu cũ giữ verdict theo commit. Merge tích hợp là bước riêng; bộ DEV này không thành dataset/font quality đãnghiệmthu hoặc representative sample. PR3giữđóng, ownershipgiữnguyên, oracleTV3chưanghiệmthu/HOLDOUTđóng.
