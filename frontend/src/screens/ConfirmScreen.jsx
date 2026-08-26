import React, { useState } from "react";
import { ArrowLeft, PlayCircle } from "lucide-react";
import { ScreenShell, ComicButton, StepBadge, Logo, HardShadowBox } from "../components/ComicPrimitives";

const PAPER_SIZES = [
  { id: "a4", label: "A4 (210×297mm)" },
  { id: "a5", label: "A5 (148×210mm)" },
];

/**
 * Màn 3 — Xác nhận trước khi vẽ
 * Props:
 *  - svgPreviewUrl?: string (nếu có SVG thật để render)
 *  - strokeCount, estimatedMinutes
 *  - onBack() / onStart({ paperSize })
 */
export default function ConfirmScreen({
  svgPreviewUrl,
  strokeCount = 248,
  estimatedMinutes = 12,
  onBack,
  onStart,
}) {
  const [paperSize, setPaperSize] = useState("a4");

  return (
    <ScreenShell patternId="pattern-confirm">
      <div className="flex items-start justify-between mb-5">
        <Logo subtitle="Xác nhận trước khi vẽ" size="text-[28px]" />
        <StepBadge step={3} />
      </div>

      <div className="mb-5">
        <HardShadowBox shadowOffset={5}>
          <div className="h-52 flex items-center justify-center bg-[#FEFDF9] rounded-xl relative">
            {svgPreviewUrl ? (
              <img src={svgPreviewUrl} alt="Xem trước SVG" className="max-h-48 max-w-full object-contain" />
            ) : (
              <svg width="90" height="130" viewBox="0 0 100 140">
                <rect x="2" y="2" width="96" height="136" fill="none" stroke="#C0392B" strokeWidth="1.5" strokeDasharray="3,2" />
                <path d="M20,100 Q30,40 50,60 T80,30" fill="none" stroke="#1A1A1A" strokeWidth="1.8" />
                <path d="M25,110 Q45,90 65,105" fill="none" stroke="#1A1A1A" strokeWidth="1.8" />
              </svg>
            )}
            <p className="absolute bottom-3.5 text-xs text-[#6B6B66] font-medium">Xem trước đường vẽ (SVG)</p>
          </div>
        </HardShadowBox>
      </div>

      <div className="flex gap-2.5 mb-5">
        <div className="flex-1 border-[2.5px] border-[#1A1A1A] rounded-lg p-2.5 bg-white">
          <p className="text-[11px] text-[#6B6B66] font-bold mb-1">KHỔ GIẤY</p>
          <select
            value={paperSize}
            onChange={(e) => setPaperSize(e.target.value)}
            className="w-full border border-[#1A1A1A] font-bold text-[13px] p-1 bg-white focus:outline-none"
          >
            {PAPER_SIZES.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1 text-center border-[2.5px] border-[#1A1A1A] rounded-lg p-2.5 bg-white">
          <p className="text-[11px] text-[#6B6B66] font-bold">SỐ NÉT VẼ</p>
          <p className="text-base text-[#1A1A1A] font-bold mt-0.5">{strokeCount}</p>
        </div>
        <div className="flex-1 text-center border-[2.5px] border-[#1A1A1A] rounded-lg p-2.5 bg-[#FBEAF0]">
          <p className="text-[11px] text-[#721C24] font-bold">ƯỚC TÍNH</p>
          <p className="text-base text-[#C0392B] font-bold mt-0.5">~ {estimatedMinutes} phút</p>
        </div>
      </div>

      <div className="flex items-center justify-between border-t-[3px] border-[#1A1A1A] pt-5">
        <ComicButton variant="secondary" onClick={onBack}>
          <span className="flex items-center gap-1.5">
            <ArrowLeft size={15} /> QUAY LẠI
          </span>
        </ComicButton>
        <ComicButton variant="primary" onClick={() => onStart?.({ paperSize })}>
          <span className="flex items-center gap-1.5">
            <PlayCircle size={16} /> BẮT ĐẦU VẼ
          </span>
        </ComicButton>
      </div>
    </ScreenShell>
  );
}
