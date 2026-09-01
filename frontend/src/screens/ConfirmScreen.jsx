import React, { useState, useEffect } from "react";
import { ArrowLeft, PlayCircle, Loader2 } from "lucide-react";
import { ScreenShell, ComicButton, ScreenTitle, HardShadowBox } from "../components/ComicPrimitives";
import { getSvgContent } from "../api/omnidraw";

const PAPER_SIZES = [
  { id: "a4", label: "A4 (210×297mm)" },
  { id: "a3", label: "A3 (297×420mm)" },
  { id: "a5", label: "A5 (148×210mm)" },
];

/**
 * Màn 3 — Xác nhận trước khi vẽ
 * Props:
 *  - requestId?: string       (để fetch SVG thật)
 *  - strokeCount, estimatedMinutes
 *  - onBack() / onStart({ paperSize })
 */
export default function ConfirmScreen({
  requestId,
  strokeCount = 248,
  estimatedMinutes = 12,
  paperSize = "a4",
  onBack,
  onStart,
}) {
  const [svgText, setSvgText] = useState(null);
  const [svgLoading, setSvgLoading] = useState(false);

  // Fetch SVG khi màn Confirm mount
  useEffect(() => {
    if (!requestId) return;
    setSvgLoading(true);
    getSvgContent(requestId)
      .then((res) => setSvgText(res.svgText))
      .catch(() => setSvgText(null))
      .finally(() => setSvgLoading(false));
  }, [requestId]);

  return (
    <ScreenShell patternId="pattern-confirm">
      <div className="mb-5">
        <HardShadowBox shadowOffset={5}>
          <div className="h-80 flex items-center justify-center bg-[#FEFDF9] rounded-xl relative overflow-hidden">
            {svgLoading ? (
              <Loader2 size={32} className="animate-spin text-[#C0392B]" />
            ) : svgText ? (
              <>
                <style>{`#svg-confirm svg { width: 100% !important; height: 100% !important; max-height: 300px; }`}</style>
                <div
                  id="svg-confirm"
                  className="w-full h-full flex items-center justify-center p-2"
                  dangerouslySetInnerHTML={{ __html: svgText }}
                />
              </>
            ) : (
              /* Placeholder khi chưa có SVG */
              <svg width="90" height="130" viewBox="0 0 100 140">
                <rect x="2" y="2" width="96" height="136" fill="none" stroke="#C0392B" strokeWidth="1.5" strokeDasharray="3,2" />
                <path d="M20,100 Q30,40 50,60 T80,30" fill="none" stroke="#1A1A1A" strokeWidth="1.8" />
                <path d="M25,110 Q45,90 65,105" fill="none" stroke="#1A1A1A" strokeWidth="1.8" />
              </svg>
            )}
            <p className="absolute bottom-3.5 text-xs text-[#6B6B66] font-medium">
              {svgText ? "Bản nét vẽ SVG thật" : "Xem trước đường vẽ (SVG)"}
            </p>
          </div>
        </HardShadowBox>
      </div>

      <div className="flex gap-2.5 mb-5">
        <div className="flex-1 text-center border-[2.5px] border-[#1A1A1A] rounded-lg p-2.5 bg-white">
          <p className="text-[11px] text-[#6B6B66] font-bold">KHỔ GIẤY</p>
          <p className="text-base text-[#1A1A1A] font-bold mt-0.5">
            {PAPER_SIZES.find(p => p.id === paperSize)?.label.split(" ")[0] || paperSize.toUpperCase()}
          </p>
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
        <ComicButton variant="primary" onClick={() => onStart?.()}>
          <span className="flex items-center gap-1.5">
            <PlayCircle size={16} /> BẮT ĐẦU VẼ
          </span>
        </ComicButton>
      </div>
    </ScreenShell>
  );
}
