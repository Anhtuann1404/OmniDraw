# _run_self_check

> 15 nodes · cohesion 0.18

## Key Concepts

- **_run_self_check()** (13 connections) — `backend/path_optimizer.py`
- **build_svg()** (12 connections) — `backend/path_optimizer.py`
- **_catmull_rom_cubic_segments()** (6 connections) — `backend/path_optimizer.py`
- **get_render_bounds_px()** (5 connections) — `backend/path_optimizer.py`
- **polyline_to_path_d()** (5 connections) — `backend/path_optimizer.py`
- **rotate_points_2d()** (4 connections) — `backend/path_optimizer.py`
- **px_to_mm()** (3 connections) — `backend/path_optimizer.py`
- **validate_within_bounds()** (2 connections) — `backend/path_optimizer.py`
- **Ponytail runnable check: assert NN + 2-Opt + Or-Opt reduces travel distance.** (1 connections) — `backend/path_optimizer.py`
- **Quy doi pixel -> mm. Neu co truyen paper_size_mm, CLAMP ket qua ve dung trong…** (1 connections) — `backend/path_optimizer.py`
- **Xoay toa do 2D quanh tam 'center' mot goc angle_deg (do). Dung de tu dong bu…** (1 connections) — `backend/path_optimizer.py`
- **Trả về các segment Cubic Bézier (p1, c1, c2, p2) dùng đúng công thức hiện tại…** (1 connections) — `backend/path_optimizer.py`
- **Lay bounds thuc te se render theo pixel: - Bounds ban dau bao gom rectangle anh…** (1 connections) — `backend/path_optimizer.py`
- **Chuyen doi danh sach toa do mm thanh SVG path data. Neu smooth=True va so diem…** (1 connections) — `backend/path_optimizer.py`
- **Xuat SVG dung chuan muc 4 API Spec: - xmlns, width/height dang "{w}mm"/"{h}mm",…** (1 connections) — `backend/path_optimizer.py`

## Relationships

- [path_optimizer.py](path_optimizer.py.md) (8 shared connections)
- [process](process.md) (3 shared connections)
- [or_opt_improve](or_opt_improve.md) (3 shared connections)
- [engine.py](engine.py.md) (2 shared connections)
- [nearest_neighbor_order](nearest_neighbor_order.md) (2 shared connections)
- [custom_error](custom_error.md) (1 shared connections)

## Source Files

- `backend/path_optimizer.py`

## Audit Trail

- EXTRACTED: 38 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*