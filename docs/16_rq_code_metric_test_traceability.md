# Truy vết nghiên cứu → mã → metric → gate

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API nghiên cứu](32_research_api_and_artifact_contract.md) là nguồn triển khai.

Các đường dẫn dưới đây là điểm nối trong mã hiện hữu hoặc module cần xây; không tuyên bố đã triển khai tính năng mới.

| ID | Owner | Điểm nối / phần phải xây | Metric | Kiểm chứng/gate |
|---|---|---|---|---|
| N-RQ1 / MT1 | TV2 baseline/runner; TV4 solver/lập luận | `backend/handwriting/experiment_runner.py` là runner cũ; cần top-m/beam/artifacts mới | J, gap_m, m*, total runtime, complete/coverage; điều kiện bằng/có lợi | Prefix lồng, m=all khớp joint; budget đầy đủ, họ ví dụ tối thiểu và điều kiện tách được |
| N-RQ2 / MT2 | TV4 mô hình/DP; TV3 oracle; TV1 khảo sát | `backend/handwriting/composition.py` là tiền nhiệm; cần frontier/pending state | Feasibility, clearance/independent violations, infeasible rate, w/b/P/state cận và phân bố | TV3 oracle/primitive độc lập; DP khớp feasibility/optimum; ca dấu chồng/biên |
| N-RQ3 | TV2 phân tích; TV3 tham số; TV4 chứng nhận | Offline sensitivity/certificate cần xây | rho/lambda, regret bounds, w/b/P/states/time/memory | Fixed schedule/candidate scope, exact/lower-bound tại 4 đỉnh |
| N-RQ4 có điều kiện | TV1+TV4 | Candidate importer/anchor manifest; không coi font repair đã có | Base/mark coverage, independent violations (kỳ vọng 0), infeasible rate, manual comparison | License, selected fonts; không suy ra every-font |
| Tái lập | TV1 dữ liệu; TV2 runner; TV3 validation; TV4 tích hợp | Manifest/JSONL theo Docs 32 cần xây | Hashes, seed, code+dirty patch, artifact/capability version | Freeze trước Holdout; access log |
| Sản phẩm | TV4; TV3 print | `backend/main.py`, `backend/csv_logger.py`, HAL | SVG product metrics; print status; telemetry | Tương thích API cũ; không dùng CSV sản phẩm thay kết quả nghiên cứu |

## Gate chung

S0 review contract → S1 candidate fixtures → S2/S3 oracle-DP match → S4 baseline/runner → S5/S6 analysis → S7 freeze/open → S8 pilot. Phiếu E1/E4/PR3 cũ chỉ chứng minh checkpoint lịch sử. Lần cập nhật tài liệu không tạo sign-off hay test PASS mới.
