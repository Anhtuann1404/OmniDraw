import React, { useState } from "react";
import { Mail, Lock, User, LogIn, UserPlus, Loader2 } from "lucide-react";
import { ScreenShell, ComicButton, Logo, StarBadge } from "../components/ComicPrimitives";
import { login, register } from "../api/auth";

/**
 * Màn Đăng nhập / Đăng ký — cửa ngõ trước khi vào Trang tạo tranh.
 * Chuẩn bị cho hướng đa người dùng sau này; hiện dùng src/api/auth.js
 * (các hàm được đánh dấu [ĐỀ XUẤT], chưa có trong API Spec chính thức).
 *
 * Props:
 *  - onLoginSuccess({ token, user }) : gọi khi đăng nhập/đăng ký thành công
 */
export default function LoginScreen({ onLoginSuccess }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);
    try {
      const result =
        mode === "login" ? await login({ email, password }) : await register({ name, email, password });
      onLoginSuccess?.(result);
    } catch (err) {
      setErrorMsg(err.message || "Có lỗi xảy ra, thử lại nhé.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScreenShell patternId="pattern-login">
      <div className="flex items-start justify-between mb-6">
        <Logo subtitle={mode === "login" ? "Đăng nhập" : "Tạo tài khoản"} size="text-3xl" />
      </div>

      <form onSubmit={handleSubmit}>
        {mode === "register" && (
          <Field icon={User} label="Tên hiển thị">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nguyễn Văn A"
              className="w-full bg-transparent text-sm font-medium focus:outline-none"
              required
            />
          </Field>
        )}

        <Field icon={Mail} label="Email">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="ban@vidu.com"
            className="w-full bg-transparent text-sm font-medium focus:outline-none"
            required
          />
        </Field>

        <Field icon={Lock} label="Mật khẩu">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full bg-transparent text-sm font-medium focus:outline-none"
            required
          />
        </Field>

        {errorMsg && (
          <p className="text-xs font-bold text-[#C0392B] bg-[#FBEAF0] border-2 border-[#C0392B] rounded-lg px-3 py-2 mb-4 text-center">
            {errorMsg}
          </p>
        )}

        <div className="flex items-center justify-between border-t-[3px] border-[#1A1A1A] pt-5">
          <button
            type="button"
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setErrorMsg(null);
            }}
            className="text-xs font-bold text-[#1A1A1A] underline underline-offset-2"
          >
            {mode === "login" ? "Chưa có tài khoản? Đăng ký" : "Đã có tài khoản? Đăng nhập"}
          </button>

          <ComicButton
            variant="primary"
            type="submit"
            className={loading ? "opacity-70 pointer-events-none" : ""}
          >
            <span className="flex items-center gap-1.5">
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> ĐANG XỬ LÝ...
                </>
              ) : mode === "login" ? (
                <>
                  <LogIn size={16} /> ĐĂNG NHẬP
                </>
              ) : (
                <>
                  <UserPlus size={16} /> ĐĂNG KÝ
                </>
              )}
            </span>
          </ComicButton>
        </div>
      </form>
    </ScreenShell>
  );
}

function Field({ icon: Icon, label, children }) {
  return (
    <div className="mb-4">
      <p className="text-[11px] font-bold text-[#1A1A1A] uppercase mb-1.5">{label}</p>
      <div className="flex items-center gap-2.5 border-[2.5px] border-[#1A1A1A] rounded-lg px-3.5 py-3 bg-[#FEFDF9]">
        <Icon size={17} className="text-[#6B6B66] shrink-0" />
        {children}
      </div>
    </div>
  );
}
