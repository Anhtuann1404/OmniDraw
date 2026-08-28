import React from "react";
import { Download, PlusCircle, LibraryBig, PartyPopper } from "lucide-react";
import { ScreenShell, ComicButton, Logo, HardShadowBox, StarBadge } from "../components/ComicPrimitives";

/**
 * Màn 4b — Hoàn thành (hiện ra khi PrintStatusScreen báo status = "done")
 * Props:
 *  - resultImageUrl?: string
 *  - actualDrawTimeSec?: number
 *  - strokesTotal?: number
 *  - onCreateNew() : quay lại màn Tạo tranh
 *  - onViewHistory() : sang màn Thư viện
 *  - onDownload()?: tuỳ chọn, tải ảnh/SVG về máy
 */
export default function DoneScreen({
  resultImageUrl,
  actualDrawTimeSec,
  strokesTotal = 248,
  onCreateNew,
  onViewHistory,
  onDownload,
}) {
  const minutes = actualDrawTimeSec ? Math.round(actualDrawTimeSec / 60) : null;

  return (
    <ScreenShell patternId="pattern-done">
      <div className="flex items-start justify-between mb-5">
        <Logo subtitle="Hoàn thành!" size="text-[28px]" />
        <StarBadge topLabel="XONG" bottomLabel="" size={64} />
      </div>

      <div className="text-center mb-4">
        <PartyPopper size={26} className="inline-block text-[#C0392B]" />
        <p className="font-['Kalam'] text-xl font-bold text-[#1A1A1A] -rotate-1 inline-block ml-1.5">
          Tranh đã vẽ xong rồi!
        </p>
      </div>

      <div className="mb-5">
        <HardShadowBox shadowOffset={5}>
          <div className="h-56 flex items-center justify-center bg-[#FEFDF9] rounded-xl">
            {resultImageUrl ? (
              <img src={resultImageUrl} alt="Kết quả" className="max-h-56 max-w-full object-contain rounded-lg" />
            ) : (
              <div className="text-center">
                <PartyPopper size={40} className="mx-auto text-[#C0392B]" />
                <p className="text-sm text-[#6B6B66] font-medium mt-2">Tranh hoàn chỉnh</p>
              </div>
            )}
          </div>
        </HardShadowBox>
      </div>

      <div className="flex gap-2.5 mb-6">
        <StatBox label="SỐ NÉT VẼ" value={strokesTotal} />
        <StatBox label="THỜI GIAN VẼ" value={minutes ? `${minutes} phút` : "—"} />
      </div>

      <div className="flex items-center justify-between border-t-[3px] border-[#1A1A1A] pt-5 gap-2.5">
        <ComicButton variant="secondary" onClick={onViewHistory} className="!px-4">
          <span className="flex items-center gap-1.5">
            <LibraryBig size={15} /> XEM THƯ VIỆN
          </span>
        </ComicButton>
        {onDownload && (
          <ComicButton variant="secondary" onClick={onDownload} className="!px-4">
            <span className="flex items-center gap-1.5">
              <Download size={15} /> TẢI VỀ
            </span>
          </ComicButton>
        )}
        <ComicButton variant="primary" onClick={onCreateNew}>
          <span className="flex items-center gap-1.5">
            <PlusCircle size={16} /> VẼ TRANH MỚI
          </span>
        </ComicButton>
      </div>
    </ScreenShell>
  );
}

function StatBox({ label, value }) {
  return (
    <div className="flex-1 text-center border-[2.5px] border-[#1A1A1A] rounded-lg py-2.5 bg-white">
      <p className="text-[11px] text-[#6B6B66] font-bold">{label}</p>
      <p className="text-base text-[#1A1A1A] font-bold mt-0.5">{value}</p>
    </div>
  );
}
