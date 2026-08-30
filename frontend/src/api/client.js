import { API_BASE_URL } from "./config";

/**
 * ApiError — lỗi chuẩn hoá theo bảng mã lỗi ở OmniDraw_API_Spec.md mục 8.
 * Luôn có .code (một trong các mã đã định nghĩa) và .message (mô tả cho người dùng/log).
 */
export class ApiError extends Error {
  constructor(code, message) {
    super(message || code);
    this.name = "ApiError";
    this.code = code || "UNKNOWN_ERROR";
  }
}

/**
 * Wrapper fetch dùng chung cho mọi lời gọi API thật.
 * - Tự thêm base URL
 * - Tự parse JSON
 * - Tự ném ApiError với đúng "code" mà backend trả về (theo mục 8 API Spec),
 *   để nơi gọi (UI) luôn xử lý lỗi theo cùng 1 kiểu, không phải đoán hình dạng lỗi mỗi lần.
 */
export async function apiRequest(path, { method = "GET", body, signal } = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
      signal,
    });
  } catch (networkErr) {
    // Lỗi mạng (server sập, không có mạng...) — không có trong bảng mã lỗi gốc,
    // dùng UNKNOWN_ERROR nhưng giữ message thật để debug dễ hơn.
    throw new ApiError("UNKNOWN_ERROR", `Không thể kết nối tới server: ${networkErr.message}`);
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    // Response không phải JSON hợp lệ
  }

  if (!response.ok) {
    const code = data?.error?.code || "UNKNOWN_ERROR";
    const message = data?.error?.message || `Yêu cầu thất bại (HTTP ${response.status})`;
    throw new ApiError(code, message);
  }

  // Một số endpoint (theo API Spec) trả status: "error" trong body dù HTTP 200 —
  // xử lý luôn ở đây để nơi gọi không phải tự kiểm tra 2 lớp.
  if (data?.status === "error" && data?.error) {
    throw new ApiError(data.error.code, data.error.message);
  }

  return data;
}

// Tạo request_id kiểu UUID v4 — theo quy định mục 7 của API Spec: giao diện sinh request_id
// đầu tiên, giữ nguyên xuyên suốt toàn bộ pipeline.
export function generateRequestId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  // fallback đơn giản cho môi trường không có crypto.randomUUID
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
