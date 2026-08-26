import React from "react";
import { Image, RefreshCw, ArrowRight } from "lucide-react";
import { ScreenShell, ComicButton, StepBadge, Logo, HardShadowBox, StarBadge } from "../components/ComicPrimitives";

/**
 * Màn 2 — Xem trước kết quả AI
 * Props:
 *  - resultImageUrl?: string  (nếu có ảnh thật, hiển thị thay placeholder)
 *  - style, modelUsed, processingTimeSec
 *  - onRetry() : bấm "Thử style khác"
 *  - onConfirm() : bấm "Xác nhận"
 */
export default function PreviewScreen({
  resultImageUrl,
  style = "Ký hoạ",
  modelUsed = "style-transfer-v1",
  processingTimeSec = 3.2,
  onRetry,
  onConfirm,
}) {
  return (
    <ScreenShell patternId="pattern-preview">
      <div className="flex items-start justify-between mb-5">
        <Logo subtitle="Xem trước kết quả AI" size="text-[28px]" />
        <StepBadge step={2} />
      </div>

      <div className="relative mb-5">
        <HardShadowBox shadowOffset={5}>
          <div className="h-64 flex items-center justify-center bg-[#FEFDF9] rounded-xl">
            {resultImageUrl ? (
              <img src={resultImageUrl} alt="Kết quả AI" className="max-h-64 max-w-full object-contain rounded-lg" />
            ) : (
              <div className="text-center">
                <Image size={42} className="mx-auto text-[#C0392B]" />
                <p className="text-sm text-[#6B6B66] font-medium mt-2">Ảnh kết quả AI (phong cách: {style})</p>
              </div>
            )}
          </div>
        </HardShadowBox>
        <div className="absolute -top-2.5 -right-2.5">
          <StarBadge topLabel="XONG" bottomLabel="" size={56} />
        </div>
      </div>

      <div className="flex gap-2.5 mb-5">
        <StatBox label="STYLE" value={style} />
        <StatBox label="MODEL" value={modelUsed} />
        <StatBox label="THỜI GIAN" value={`${processingTimeSec}s`} />
      </div>

      <div className="flex items-center justify-between border-t-[3px] border-[#1A1A1A] pt-5">
        <ComicButton variant="secondary" onClick={onRetry}>
          <span className="flex items-center gap-1.5">
            <RefreshCw size={15} /> THỬ STYLE KHÁC
          </span>
        </ComicButton>
        <ComicButton variant="primary" onClick={onConfirm}>
          <span className="flex items-center gap-1.5">
            XÁC NHẬN <ArrowRight size={16} />
          </span>
        </ComicButton>
      </div>
    </ScreenShell>
  );
}

function StatBox({ label, value }) {
  return (
    <div className="flex-1 text-center border-[2.5px] border-[#1A1A1A] rounded-lg py-2 bg-white">
      <p className="text-[11px] text-[#6B6B66] font-bold">{label}</p>
      <p className="text-[13px] text-[#1A1A1A] font-bold mt-0.5 truncate">{value}</p>
    </div>
  );
}
