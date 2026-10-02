# Công cụ repo theo mục đích

| Entry | Vai trò | Nguồn/trạng thái |
|---|---|---|
| `python -m backend.research.dev_solve` | Debug một ca theo contract mới; JSON/trace/SVG DEV | TV4, xem [research README](../backend/research/README.md); không là runner TV2 |
| `legacy/generate_pr3_e1_dev_evidence.py` | Tái lập bằng chứng PR3 E1 cũ | PR3 đã đóng; không chạy khi dọn repo, không nâng sign-off |
| `generate_pr3_e1_dev_evidence.py` | Entry tương thích gọi script legacy | Giữ lệnh cũ; không chứa solver hoặc logic nghiên cứu mới |
| `research_parametric_preflight.py` | Prototype khám phá DEV/synthetic trước contract hiện hành | File có sẵn chưa commit được giữ nguyên; không import từ research core, không là oracle độc lập/runner chính thức |
| `deepseek_bridge.py` | Cầu nối công cụ AI có tính phí | Không chạy hoặc sửa trong lượt TV4; chỉ theo yêu cầu duo tường minh |

Không chuyển/xóa prototype có sẵn, file hardware hoặc output của owner khác chỉ vì chưa nằm đúng thư mục mong muốn. Git dirty trước lượt đã được lưu hash để đối chiếu bảo toàn; dọn vùng TV4 bằng đường dẫn rõ và cập nhật references.
