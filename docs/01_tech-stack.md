# Công nghệ và kiến trúc triển khai

**Cập nhật: 02/10/2026.** Hướng nghiên cứu đã được GVHD đồng ý theo thông báo của TV4; đây là kế hoạch, không phải kết quả nghiệm thu. [Kế hoạch kỹ thuật](30_research_development_plan.md), [contract solver](31_joint_solver_contract.md), [API nghiên cứu](32_research_api_and_artifact_contract.md) là nguồn triển khai.

## Công nghệ hiện hữu và phần cần phát triển

| Tầng | Hiện hữu | Hướng triển khai | Owner |
|---|---|---|---|
| Giao diện | React, preview SVG, history/print | Giữ Art Mode và thư tay; UI nghiên cứu chỉ sau gate backend | TV4 |
| Backend sản phẩm | Python/FastAPI, `/api/ai/generate`, print/history/log | Giữ tương thích API sản phẩm; không nhét solver option vào request cũ | TV4 tích hợp; TV3 print |
| Hình học | Glyph nét đơn, composition DAG/transition PR3 | World-mm, ứng viên trọn chữ và ownership/contacts; hình học render phải khớp hình học chấm | TV4 mô hình; TV1 dữ liệu |
| Bộ giải | DAG/preflight cũ | DP frontier/pending/endpoint, một mục tiêu; không coi mã cũ đã đáp ứng contract mới | TV4 |
| Kiểm chứng | Test/fixture PR3 cũ | Oracle vét cạn và kiểm hình học/cost độc lập, không nhập primitive solver | TV3 |
| Thực nghiệm | Runner B1/B2/B3/Proposed DEV và CSV 19 cột | Staged top-m, beam, manifest/JSONL mới, thống kê và độ nhạy | TV2 |
| Dữ liệu | Corpus TV1 và schema đã có | Split Holdout mới, custody/access log, corpus cũ chỉ bổ sung | TV1 |
| Thiết bị | HAL, driver/simulator | Máy vẽ phẳng hai trục khi sẵn sàng; cấu hình/nguồn đo ghi theo run | TV3 |

Không bắt buộc AxiDraw hoặc CoreXY. Dòng máy, cơ cấu truyền động và bộ điều khiển là ba lựa chọn riêng; concept A4 tiết kiệm chưa là thiết bị đã mua. Không thêm thư viện/driver hoặc chốt SKU chỉ qua tài liệu này.

## Nguyên tắc kỹ thuật

- Đơn vị mm; tọa độ hữu hạn; ID ổn định; dữ liệu ứng viên hữu hạn. Unicode normalization không tự phục hồi glyph thiếu.
- `J=L_down+rho*L_up+lambda*N_cycle`; thời gian mô hình, thời gian giải và số đo máy là ba đại lượng riêng.
- `c_min=0.20 mm` là ràng buộc cứng trên các cặp phải tách; ngoại lệ tiếp xúc phải khai báo.
- Tách module dữ liệu, feasibility/cost, DP, oracle, baseline và runner bằng contract. Oracle triển khai độc lập.
- API nghiên cứu triển khai offline trước. Mọi schema cần version, provenance, complete flags và lỗi resource limit rõ ràng.
- Chưa thêm Pareto/cắt tỉa mở rộng, Writer Profile, suy diễn thói quen nét hoặc mọi-font conversion vào acceptance kỳ này.

## Ownership

TV4 chịu trách nhiệm mô hình, truy hồi DP, SVG/trace và tích hợp. TV2 chủ trì cost/baseline/runner/phân tích; TV1 chủ trì dữ liệu và đồng chủ trì font; TV3 chủ trì oracle độc lập và thiết bị. Không sửa code của owner khác khi chưa có bàn giao cụ thể. Chi tiết reviewer/gate theo Docs 30.
