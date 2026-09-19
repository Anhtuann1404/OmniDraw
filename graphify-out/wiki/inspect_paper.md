# inspect_paper

> 11 nodes · cohesion 0.20

## Key Concepts

- **inspect_paper()** (10 connections) — `backend/camera_inspector.py`
- **api_inspect_paper()** (4 connections) — `backend/main.py`
- **api_inspect_paper()** (4 connections) — `test/main.py`
- **_encode_jpeg()** (3 connections) — `backend/camera_inspector.py`
- **_normalize_paper_rect()** (3 connections) — `backend/camera_inspector.py`
- **_run_self_check()** (3 connections) — `backend/camera_inspector.py`
- **Chuyển ảnh OpenCV BGR thành chuỗi Base64 Data URL để UI render trực tiếp.** (1 connections) — `backend/camera_inspector.py`
- **Ponytail runnable check: assert synthetic paper detection precision.** (1 connections) — `backend/camera_inspector.py`
- **Chuẩn hóa góc nghiêng [-45, 45] độ và cạnh dài/cạnh ngắn.** (1 connections) — `backend/camera_inspector.py`
- **Kiểm tra tình trạng giấy từ frame ảnh hoặc webcam. # ponytail: dùng Otsu…** (1 connections) — `backend/camera_inspector.py`
- **Kiem tra tinh trang giay va goc lech qua camera thi giac (Closed-Loop Vision).** (1 connections) — `test/main.py`

## Relationships

- [custom_error](custom_error.md) (5 shared connections)
- [path_optimizer.py](path_optimizer.py.md) (4 shared connections)
- [test/main.py](test-main.py.md) (2 shared connections)

## Source Files

- `backend/camera_inspector.py`
- `backend/main.py`
- `test/main.py`

## Audit Trail

- EXTRACTED: 20 (91%)
- INFERRED: 2 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*