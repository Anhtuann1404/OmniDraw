import React, { useState, useEffect, useRef } from "react";
import { Clock, Plug, PauseCircle, XCircle, PlayCircle, Loader2 } from "lucide-react";
import { ScreenShell, ComicButton, StepBadge, Logo, HardShadowBox } from "../components/ComicPrimitives";
import { getSvgContent } from "../api/omnidraw";

/**
 * Màn 4 — Đang vẽ
 * Nếu có requestId, fetch SVG thật và hiển thị với animation clipPath theo progressPercent.
 */
export default function PrintStatusScreen({
  requestId,
  progressPercent = 58,
  etaMinutes = 5,
  machineStatus = "ok",
  isPaused = false,
  onPause,
  onResume,
  onCancel,
}) {
  const [svgText, setSvgText] = useState(null);
  const [svgLoading, setSvgLoading] = useState(false);
  const svgContainerRef = useRef(null);

  // Fetch SVG thật khi màn này được mount
  useEffect(() => {
    if (!requestId) return;
    setSvgLoading(true);
    getSvgContent(requestId)
      .then((res) => setSvgText(res.svgText))
      .catch(() => setSvgText(null))
      .finally(() => setSvgLoading(false));
  }, [requestId]);

  // Tô màu dần các path SVG theo progressPercent
  useEffect(() => {
    if (!svgContainerRef.current || !svgText) return;
    const paths = svgContainerRef.current.querySelectorAll("path, polyline, line, circle, ellipse, rect");
    const total = paths.length;
    if (total === 0) return;
    const drawnCount = Math.floor((progressPercent / 100) * total);
    paths.forEach((el, i) => {
      if (i < drawnCount) {
        el.style.stroke = "#1A1A1A";
        el.style.opacity = "1";
      } else {
        el.style.stroke = "#E5E2D6";
        el.style.opacity = "0.4";
      }
    });
  }, [svgText, progressPercent]);

  return (
    <ScreenShell patternId="pattern-print">
      <div className="flex items-start justify-between mb-5">
        <Logo subtitle={isPaused ? "Tạm dừng..." : "Đang vẽ..."} size="text-[28px]" />
        <StepBadge step={4} />
      </div>

      {/* Canvas vẽ */}
      <div className="mb-4">
        <HardShadowBox shadowOffset={5}>
          <div className="flex items-center justify-center bg-[#FEFDF9] rounded-xl overflow-hidden" style={{ height: "200px" }}>
            {svgLoading ? (
              <Loader2 size={32} className="animate-spin text-[#C0392B]" />
            ) : svgText ? (
              <>
                <style>{`#svg-printing svg { width: 100% !important; height: 100% !important; max-height: 196px; }`}</style>
                <div
                  ref={svgContainerRef}
                  id="svg-printing"
                  className="w-full h-full flex items-center justify-center p-2"
                  dangerouslySetInnerHTML={{ __html: svgText }}
                />
              </>
            ) : (
              /* Fallback animation SVG tĩnh */
              <svg width="200" height="200" viewBox="0 0 220 220">
                <rect x="4" y="4" width="212" height="212" fill="none" stroke="#D8D5C8" strokeWidth="1" strokeDasharray="3,2" />
                <path d="M50,170 Q60,60 110,90 T170,40" fill="none" stroke="#E5E2D6" strokeWidth="2.2" />
                <path d="M55,185 Q95,150 145,175" fill="none" stroke="#E5E2D6" strokeWidth="2.2" />
                <circle cx="150" cy="70" r="18" fill="none" stroke="#E5E2D6" strokeWidth="2.2" />
                <path
                  d="M50,170 Q60,60 110,90 T170,40"
                  fill="none" stroke="#1A1A1A" strokeWidth="2.2"
                  strokeDasharray="240"
                  strokeDashoffset={Math.max(0, 240 - (240 * progressPercent) / 100)}
                />
                {progressPercent > 40 && (
                  <path d="M55,185 Q95,150 145,175" fill="none" stroke="#1A1A1A" strokeWidth="2.2" />
                )}
                {progressPercent > 20 && (
                  <circle cx="150" cy="70" r="18" fill="none" stroke="#C0392B" strokeWidth="2.4"
                    strokeDasharray="113" strokeDashoffset={113 - (113 * progressPercent) / 100} />
                )}
                <circle cx="150" cy="70" r="3" fill="#C0392B" />
              </svg>
            )}
          </div>
        </HardShadowBox>
      </div>

      {/* Thanh tiến độ */}
      <div className="flex items-center gap-2.5 mb-5">
        <div className="flex-1 bg-[#EDEBDF] rounded-full h-4 border-2 border-[#1A1A1A] overflow-hidden">
          <div className="h-full bg-[#C0392B] transition-all duration-500" style={{ width: `${progressPercent}%` }} />
        </div>
        <span className="text-sm font-bold text-[#1A1A1A] min-w-[38px]">{progressPercent}%</span>
      </div>

      {/* Thống kê */}
      <div className="flex gap-2.5 mb-5">
        <StatBox icon={<Clock size={18} />} label="CÒN LẠI" value={`~ ${etaMinutes} phút`} />
        <StatBox
          icon={<Plug size={18} className={machineStatus === "ok" ? "text-[#2C7A3D]" : "text-[#C0392B]"} />}
          label="MÁY VẼ"
          value={machineStatus === "ok" ? "Hoạt động tốt" : "Có sự cố"}
          tone={machineStatus === "ok" ? "success" : "error"}
        />
      </div>

      {/* Nút điều khiển */}
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