import { apiRequest } from "./client";
import { MOCK_MODE } from "./config";

// ============================================================================
// ĐỀ XUẤT — XÁC THỰC NGƯỜI DÙNG (chưa có trong OmniDraw_API_Spec.md)
// Toàn bộ đề tài hiện tại vẫn xoay quanh 1 người dùng (đúng phạm vi đã chốt
// trong tài liệu định hướng). Đây là bước chuẩn bị cho hướng đa người dùng
// sau này — cần cả nhóm bàn và chính thức thêm vào API Spec (mục "Xác thực")
// trước khi backend code theo, giống các endpoint print/start-pause-cancel
// trước đó.
// ============================================================================

const TOKEN_STORAGE_KEY = "omnidraw_auth_token";

/**
 * [ĐỀ XUẤT] Đăng nhập.
 * Endpoint gợi ý: POST /api/auth/login
 * @returns {Promise<{token: string, user: {id: string, name: string, email: string}}>}
 */
export async function login({ email, password }) {
  if (MOCK_MODE) {
    await delay(600);
    if (!email || !password) {
      throw new AuthError("AUTH_INVALID_INPUT", "Nhập đủ email và mật khẩu nhé.");
    }
    const fakeUser = { id: "mock-user-1", name: email.split("@")[0], email };
    const fakeToken = "mock-token-" + Date.now();
    persistToken(fakeToken);
    return { token: fakeToken, user: fakeUser };
  }

  const data = await apiRequest("/api/auth/login", { method: "POST", body: { email, password } });
  persistToken(data.token);
  return { token: data.token, user: data.user };
}

/**
 * [ĐỀ XUẤT] Đăng ký tài khoản mới.
 * Endpoint gợi ý: POST /api/auth/register
 */
export async function register({ name, email, password }) {
  if (MOCK_MODE) {
    await delay(600);
    if (!name || !email || !password) {
      throw new AuthError("AUTH_INVALID_INPUT", "Điền đủ thông tin nhé.");
    }
    const fakeUser = { id: "mock-user-new", name, email };
    const fakeToken = "mock-token-" + Date.now();
    persistToken(fakeToken);
    return { token: fakeToken, user: fakeUser };
  }

  const data = await apiRequest("/api/auth/register", { method: "POST", body: { name, email, password } });
  persistToken(data.token);
  return { token: data.token, user: data.user };
}

/** Đăng xuất — chỉ xoá token phía client, không cần gọi mạng ở bản MVP này. */
export function logout() {
  clearToken();
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

function persistToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export class AuthError extends Error {
  constructor(code, message) {
    super(message);
    this.name = "AuthError";
    this.code = code;
  }
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
