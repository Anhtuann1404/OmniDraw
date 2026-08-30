import React from "react";
import { Clock, Route, Plug, PauseCircle, XCircle, PlayCircle } from "lucide-react";
import { ScreenShell, ComicButton, StepBadge, Logo, HardShadowBox } from "../components/ComicPrimitives";

export default function PrintStatusScreen({
  progressPercent = 58,
  strokesDone = 144,
  strokesTotal = 248,
  etaMinutes = 5,
  machineStatus = "ok",
  isPaused = false,
  onPause,
  onResume,
  onCancel,
}) {
  const pathDrawnOffset = Math.max(0, 240 - (240 * progressPercent) / 100);

  return (
    <ScreenShell patternId="pattern-print">
      <div className="flex items-start justify-between mb-5">
        <Logo subtitle="Đang vẽ..." size="text-[28px]" />
        <StepBadge step={4} />
      </div>

      <div className="mb-5">
        <HardShadowBox shadowOffset={5}>
          <div className="flex items-center justify-center bg-[#FEFDF9] rounded-xl p-3">
            <svg width="200" height="200" viewBox="0 0 220 220">
              <rect x="4" y="4" width="212" height="212" fill="none" stroke="#D8D5C8" strokeWidth="1" strokeDasharray="3,2" />
              <path d="M50,170 Q60,60 110,90 T170,40" fill="none" stroke="#E5E2D6" strokeWidth="2.2" />
              <path d="M55,185 Q95,150 145,175" fill="none" stroke="#E5E2D6" strokeWidth="2.2" />
              <circle cx="150" cy="70" r="18" fill="none" stroke="#E5E2D6" strokeWidth="2.2" />
              <path
                d="M50,170 Q60,60 110,90 T170,40"
                fill="none"
                stroke="#1A1A1A"
                strokeWidth="2.2"
                strokeDasharray="240"
                strokeDashoffset={pathDrawnOffset}
              />
              {progressPercent > 40 && (
                <path d="M55,185 Q95,150 145,175" fill="none" stroke="#1A1A1A" strokeWidth="2.2" />
              )}
              {progressPercent > 20 && (
                <circle cx="150" cy="70" r="18" fill="none" stroke="#C0392B" strokeWidth="2.4" strokeDasharray="113" strokeDashoffset={113 - (113 * progressPercent) / 100} />
              )}
              <circle cx="150" cy="70" r="3" fill="#C0392B" />
            </svg>
          </div>
        </HardShadowBox>
      </div>

      <div className="flex items-center gap-2.5 mb-5">
        <div className="flex-1 bg-[#EDEBDF] rounded-full h-4 border-2 border-[#1A1A1A] overflow-hidden">
          <div className="h-full bg-[#C0392B] transition-all" style={{ width: `${progressPercent}%` }} />
        </div>
        <span className="text-sm font-bold text-[#1A1A1A] min-w-[38px]">{progressPercent}%</span>
      </div>

      <div className="flex gap-2.5 mb-5">
        <StatBox icon={<Clock size={18} className="text-[#1A1A1A]" />} label="CÒN LẠI" value={`~ ${etaMinutes} phút`} />
        <StatBox icon={<Route size={18} className="text-[#1A1A1A]" />} label="NÉT ĐÃ VẼ" value={`${strokesDone} / ${strokesTotal}`} />
        {machineStatus === "ok" ? (
          <StatBox
            icon={<Plug size={18} className="text-[#2C7A3D]" />}
            label="MÁY VẼ"
            value="Hoạt động tốt"
            tone="success"
          />
        ) : (
          <StatBox
            icon={<Plug size={18} className="text-[#C0392B]" />}
            label="MÁY VẼ"
            value="Có sự cố"
            tone="error"
          />
        )}
      </div>

      <div className="flex items-center justify-between border-t-[3px] border-[#1A1A1A] pt-5">
        {isPaused ? (
          <ComicButton variant="primary" onClick={onResume}>
            <span className="flex items-center gap-1.5">
              <PlayCircle size={15} /> TIẾP TỤC
            </span>
          </ComicButton>
        ) : (
          <ComicButton variant="secondary" onClick={onPause}>
            <span className="flex items-center gap-1.5">
              <PauseCircle size={15} /> TẠM DỪNG
            </span>
          </ComicButton>
        )}
        <ComicButton variant="secondary" onClick={onCancel} className="!text-[#C0392B]">
          <span className="flex items-center gap-1.5">
            <XCircle size={15} /> HUỶ VẼ
          </span>
        </ComicButton>
      </div>
    </ScreenShell>
  );
}

function StatBox({ icon, label, value, tone = "neutral" }) {
  const toneClasses = {
    neutral: "bg-white border-[#1A1A1A] text-[#1A1A1A]",
    success: "bg-[#EAF3DE] border-[#2C7A3D] text-[#2C7A3D]",
    error: "bg-[#FBEAF0] border-[#C0392B] text-[#C0392B]",
  };
  return (
    <div className={`flex-1 text-center border-[2.5px] rounded-lg py-2.5 ${toneClasses[tone]}`}>
      <div className="flex justify-center">{icon}</div>
      <p className="text-[11px] font-bold mt-1">{label}</p>
      <p className="text-[13px] font-bold mt-0.5">{value}</p>
    </div>
  );
}