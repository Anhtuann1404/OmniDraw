import React, { useState, useEffect } from "react";
import { Download, PlusCircle, LibraryBig, PartyPopper, Loader2 } from "lucide-react";
import { ScreenShell, ComicButton, ScreenTitle, HardShadowBox, StarBadge } from "../components/ComicPrimitives";
import { getSvgContent } from "../api/omnidraw";

/**
 * Màn 4b — Hoàn thành
 * Props:
 *  - inputType?: "image" | "text"  ← phân nhánh hiển thị
 *  - requestId?: string            ← dùng để fetch SVG khi inputType==="image"
 *  - resultImageUrl?: string       ← hiển thị khi inputType==="text"
 *  - actualDrawTimeSec?: number
 *  - strokesTotal?: number
 *  - onCreateNew() / onViewHistory() / onDownload()?
 */
export default function DoneScreen({
  inputType = "text",
  requestId,
  resultImageUrl,
  actualDrawTimeSec,
  strokesTotal = 248,
  onCreateNew,
  onViewHistory,
  onDownload,
}) {
  const minutes = actualDrawTimeSec ? Math.round(actualDrawTimeSec / 60) : null;

  const [svgText, setSvgText] = useState(null);
  const [svgLoading, setSvgLoading] = useState(false);

  // Khi là luồng tải ảnh lên: fetch SVG để hiển thị tác phẩm hoàn chỉnh
  useEffect(() => {
    if (inputType !== "image" || !requestId) return;
    setSvgLoading(true);
    getSvgContent(requestId)
      .then((res) => setSvgText(res.svgText))
      .catch(() => setSvgText(null))
      .finally(() => setSvgLoading(false));
  }, [inputType, requestId]);

  return (
    <ScreenShell patternId="pattern-done">
      <div className="text-center mb-4">
        <PartyPopper size={26} className="inline-block text-[#C0392B]" />
        <p className="font-['Kalam'] text-xl font-bold text-[#1A1A1A] -rotate-1 inline-block ml-1.5">
          Tranh đã vẽ xong rồi!
        </p>
      </div>

      {/* ── Khung tranh hoàn chỉnh ── */}
      <div className="mb-5">
        <HardShadowBox shadowOffset={5}>
          <div className="h-72 flex items-center justify-center bg-[#FEFDF9] rounded-xl overflow-hidden">

            {/* Luồng Tải ảnh lên: hiển thị bản SVG nét vẽ */}
            {inputType === "image" && (
              svgLoading ? (
                <Loader2 size={36} className="animate-spin text-[#C0392B]" />
              ) : svgText ? (
                <>
                  <style>{`#svg-done svg { width: 100% !important; height: 100% !important; max-height: 288px; }`}</style>
                  <div
                    id="svg-done"
                    className="w-full h-full flex items-center justify-center p-2"
                    dangerouslySetInnerHTML={{ __html: svgText }}
                  />
                </>
              ) : (
                <div className="text-center">
                  <PartyPopper size={40} className="mx-auto text-[#C0392B]" />
                  <p className="text-sm text-[#6B6B66] font-medium mt-2">Tranh hoàn chỉnh</p>
                </div>
              )
            )}

            {/* Luồng AI sinh ảnh: hiển thị ảnh màu gốc AI tạo */}
            {inputType === "text" && (
              resultImageUrl ? (
                <img
                  src={resultImageUrl}
                  alt="Kết quả"
                  className="max-h-72 max-w-full object-contain rounded-lg"
                />
              ) : (
                <div className="text-center">
                  <PartyPopper size={40} className="mx-auto text-[#C0392B]" />
                  <p className="text-sm text-[#6B6B66] font-medium mt-2">Tranh hoàn chỉnh</p>
                </div>
              )
            )}

          </div>
        </HardShadowBox>
      </div>

      {/* ── Thống kê ── */}
      <div className="flex gap-2.5 mb-6">
        <StatBox label="SỐ NÉT VẼ" value={strokesTotal} />
        <StatBox label="THỜI GIAN VẼ" value={minutes ? `${minutes} phút` : "—"} />
      </div>

      {/* ── Nút hành động ── */}
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
