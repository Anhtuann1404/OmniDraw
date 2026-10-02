# OmniDraw

Nguồn ngữ cảnh hiện hành: [docs/README.md](docs/README.md), rồi [current-task](docs/03_current-task.md), [kế hoạch](docs/30_research_development_plan.md), [contract solver](docs/31_joint_solver_contract.md) và [API/artifacts](docs/32_research_api_and_artifact_contract.md).

## Bản đồ mã và ownership

| Vùng | Vai trò | Trạng thái / owner |
|---|---|---|
| [backend/handwriting/](backend/handwriting/README.md) | Luồng sản phẩm chữ/SVG, composition/baselines/runner hiện hữu | Giữ tương thích; các kết quả PR cũ chỉ có hiệu lực trong phạm vi cũ |
| [backend/research/](backend/research/README.md) | Gateway và joint solver theo Docs 31/32 | TV4 core/API; DEV no-forget/safe-forget đã có; chưa nghiệm thu độc lập |
| `backend/main.py`, `frontend/` | API/UI sản phẩm | Research routes tách riêng; không tự kích hoạt drawing |
| `backend/hardware_adapter.py`, `cad/`, `docs/hardware/` | HAL và cơ khí | TV3; không thay đổi trong slice TV4 |
| [tests/research/](tests/research/README.md) | Tests/fixtures contract nghiên cứu mới | TV4 DEV; không thay oracle TV3 |
| `tests/test_pr3_*.py`, `tests/test_ca_vhc_*.py` | Hồi quy sản phẩm/contract cũ | Vẫn chạy để kiểm tương thích; không là kết quả nghiên cứu mới |
| [scripts/](scripts/README.md) | Công cụ theo mục đích | Script PR3 chuyển vào legacy, giữ entry tương thích |
| `dataset/`, `docs/evidence/` | Dữ liệu/bằng chứng đúng nguồn và phạm vi | Không đổi corpus cũ thành HOLDOUT mới |
| `output/research_dev/` | JSON/trace/SVG tự sinh từ DEV CLI | Git-ignore riêng vùng này; không bỏ qua toàn bộ output đang có |

PR3 đã đóng theo xác nhận trưởng nhóm. PR đóng, code đã merge và kết quả đã nghiệm thu là ba trạng thái riêng, cần commit/phạm vi và bằng chứng tương ứng. Tên nhánh `codex/tv4-pr3-slices` không mở lại PR3.

## Hướng nghiên cứu mới

Ứng viên world-mm đã khóa → schema/hash → kiểm geometry và graph tương tác → joint DP BODY/MARK/END → replay/trace → đối chiếu oracle độc lập → đối chứng top-m/beam → freeze → HOLDOUT.

TV2 chủ trì baseline/cost review/runner; TV1 chủ trì ứng viên/split/custody; TV3 chủ trì oracle/primitive độc lập và hardware. Những phần này còn PENDING cho contract mới; không tạo module rỗng rồi gọi là đã hoàn tất.

Lệnh kiểm hiện hành và lệnh DEV xem [backend/research/README.md](backend/research/README.md). Code nghiên cứu không import solver/bridge/cost sản phẩm. HOLDOUT, quality gate, numeric/contact policy freeze và sign-off không được tự nâng trạng thái từ test PASS.
