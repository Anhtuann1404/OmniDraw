import React from "react";

/**
 * OmniDraw design tokens (đã chốt với nhóm):
 * - Nền: #EDEBDF (be nhạt)
 * - Panel: trắng, viền đen 3px+, bo góc 12px
 * - Bóng cứng đổ lệch: offset 5-6px, không mờ (không dùng shadow blur mặc định của Tailwind)
 * - Màu nhấn: #C0392B (đỏ mực)
 * - Font tiêu đề: 'Kalam' (Google Fonts) — nhớ import trong index.html hoặc index.css:
 *     @import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&display=swap');
 */

// Khối "panel" viền đen có bóng cứng đổ lệch phía sau — dùng làm khung ngoài cho mọi màn hình
export function HardShadowBox({ children, className = "", shadowOffset = 6 }) {
  return (
    <div className={`relative ${className}`}>
      <div
        className="absolute bg-[#1A1A1A] rounded-xl"
        style={{ top: shadowOffset, left: shadowOffset, width: "100%", height: "100%" }}
      />
      <div className="relative bg-white border-[3.5px] border-[#1A1A1A] rounded-xl">
        {children}
      </div>
    </div>
  );
}

// Nút bấm có bóng cứng đổ lệch — variant: "primary" (đỏ) | "secondary" (trắng viền đen) | "dark" (đen)
export function ComicButton({ children, onClick, variant = "primary", className = "", type = "button" }) {
  const styles = {
    primary: "bg-[#C0392B] text-white border-[#1A1A1A]",
    secondary: "bg-white text-[#1A1A1A] border-[#1A1A1A]",
    dark: "bg-[#1A1A1A] text-[#FAFAF8] border-[#1A1A1A]",
  };
  return (
    <div className="relative inline-block">
      <div className="absolute top-1 left-1 w-full h-full bg-[#1A1A1A] rounded-lg" />
      <button
        type={type}
        onClick={onClick}
        className={`relative border-[2.5px] rounded-lg px-6 py-3 text-sm font-bold whitespace-nowrap transition-transform active:translate-x-[2px] active:translate-y-[2px] ${styles[variant]} ${className}`}
      >
        {children}
      </button>
    </div>
  );
}

// Badge tròn kiểu ngôi sao (huy hiệu "MỚI · AI"), dùng ở góc màn hình chính
export function StarBadge({ topLabel = "MỚI", bottomLabel = "AI", size = 70 }) {
  const cx = size / 2;
  return (
    <svg width={size} height={size} viewBox="0 0 70 70">
      <polygon
        points="35,2 42,17 60,13 51,28 68,35 51,42 60,57 42,53 35,68 28,53 10,57 19,42 2,35 19,28 10,13 28,17"
        fill="#C0392B"
        stroke="#1A1A1A"
        strokeWidth="2.5"
      />
      <text x={cx} y={cx - 3} textAnchor="middle" fontSize="8" fontWeight="700" fill="#FFFFFF">
        {topLabel}
      </text>
      <text x={cx} y={cx + 8} textAnchor="middle" fontSize="7" fontWeight="700" fill="#FFFFFF">
        {bottomLabel}
      </text>
    </svg>
  );
}

// Badge trạng thái bước (vd "BƯỚC 2/4")
export function StepBadge({ step, total = 4 }) {
  return (
    <span className="text-[11px] font-bold text-white bg-[#1A1A1A] px-3 py-1.5 rounded-full whitespace-nowrap">
      BƯỚC {step}/{total}
    </span>
  );
}

// Wordmark "OmniDraw" + gạch chân dạng nét vẽ tay — dùng làm tiêu đề chuẩn xuyên suốt UI
export function Logo({ subtitle, size = "text-3xl" }) {
  return (
    <div>
      <p className={`font-['Kalam'] ${size} font-bold text-[#1A1A1A] -rotate-2 inline-block m-0`}>
        OmniDraw
      </p>
      <svg width="140" height="10" className="block mt-0.5">
        <path d="M5,5 Q40,0 70,5 T135,5" fill="none" stroke="#C0392B" strokeWidth="2.5" strokeLinecap="round" />
      </svg>
      {subtitle && <p className="text-xs text-[#6B6B66] font-semibold mt-1.5">{subtitle}</p>}
    </div>
  );
}

// Hoạ tiết chấm bi trang trí góc màn hình
export function HalftonePattern({ id, color = "#1A1A1A", position = "top-right", opacity = 0.5, size = 150 }) {
  const posClasses = {
    "top-right": "-top-9 -right-9",
    "bottom-left": "-bottom-8 -left-8",
  };
  return (
    <svg
      width={size}
      height={size}
      className={`absolute ${posClasses[position]} pointer-events-none z-0`}
      style={{ opacity }}
    >
      <defs>
        <pattern id={id} width="9" height="9" patternUnits="userSpaceOnUse">
          <circle cx="2" cy="2" r="1.6" fill={color} />
        </pattern>
      </defs>
      <circle cx={size / 2} cy={size / 2} r={size / 2} fill={`url(#${id})`} />
    </svg>
  );
}

// Khung ngoài dùng chung cho cả 5 màn hình (nền be + panel trắng + hoạ tiết)
// LƯU Ý: width cố định (không dùng max-w + shrink-to-fit) để nội dung bên trong
// (chữ dài/đậm ở các ô lựa chọn, v.v.) không bao giờ làm khung tự phình/co lại.
export function ScreenShell({ children, patternId }) {
  return (
    <div className="bg-[#EDEBDF] rounded-2xl border-[3.5px] border-[#1A1A1A] p-6 relative overflow-hidden w-[480px] shrink-0">
      <HalftonePattern id={patternId} position="top-right" />
      <HardShadowBox className="relative z-10">
        <div className="p-6">{children}</div>
      </HardShadowBox>
    </div>
  );
}
