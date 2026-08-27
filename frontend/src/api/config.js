// Cấu hình gốc cho toàn bộ API client.
// Đổi URL thật của backend bằng biến môi trường VITE_API_BASE_URL (file .env ở gốc project),
// không hardcode URL trong code — mỗi người trong nhóm chạy backend cục bộ ở cổng khác nhau
// vẫn dùng chung được code này.
//
// Ví dụ file .env:
//   VITE_API_BASE_URL=http://localhost:8000

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Bật MOCK_MODE = true khi backend (AI/thuật toán/phần cứng) chưa sẵn sàng —
// mọi hàm trong src/api/omnidraw.js sẽ trả về dữ liệu giả thay vì gọi mạng thật,
// giúp bạn code/tích hợp UI mà không cần chờ 3 bạn còn lại xong module.
// Tắt (false) khi đã có backend thật để test end-to-end.
export const MOCK_MODE = import.meta.env.VITE_MOCK_MODE !== "false";
