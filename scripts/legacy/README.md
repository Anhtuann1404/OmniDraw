# Công cụ cho contract/PR đã đóng

`generate_pr3_e1_dev_evidence.py` giữ logic tái lập PR3 E1; script gốc ở thư mục cha là wrapper tương thích. `ROOT` và command metadata đã cập nhật theo vị trí mới. Không chạy script này trong migration vì nó ghi đè evidence cũ; không dùng kết quả của nó cho mô hình nghiên cứu mới.

Bằng chứng đã lưu trong `docs/evidence/` và snapshot `docs/history/` giữ nguyên bytes/commit/phạm vi. PR đóng, code merge và nghiệm thu là các trạng thái khác nhau.
