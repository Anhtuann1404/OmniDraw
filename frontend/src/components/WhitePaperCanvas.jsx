import React, { useRef, useEffect } from "react";
import { Loader2, TriangleAlert } from "lucide-react";

const PAPER_DIMENSIONS = {
  a4: { label: "A4 (210 × 297mm)", width: "520px", height: "735px", marginMm: 15 },
  a3: { label: "A3 (297 × 420mm)", width: "580px", height: "820px", marginMm: 20 },
  a5: { label: "A5 (148 × 210mm)", width: "420px", height: "594px", marginMm: 10 },
};

/**
 * WhitePaperCanvas — Trang giấy trắng trung tâm của OmniDraw Studio
 */
export default function WhitePaperCanvas({
  paperSize = "a4",
  mode = "art",
  inputType = "text",
  svgText = null,
  svgLoading = false,
  svgError = null,
  resultImageUrl = null,
  viewMode = "svg", // "svg" | "image"
  studioPhase = "preview", // "preview" | "printing" | "done"
  progressPercent = 0,
  zoom = 85,
  onZoomChange,
  onResetZoom,
  title = "Bản vẽ OmniDraw",
  styleName = "Ký hoạ",
}) {
  const svgContainerRef = useRef(null);
  const isHandwriting = mode === "letter" || inputType === "handwriting";
  const paper = PAPER_DIMENSIONS[paperSize] || PAPER_DIMENSIONS.a4;

  // Cập nhật hiển thị nét vẽ dần dần theo progressPercent khi đang in
  useEffect(() => {
    if (!svgContainerRef.current || !svgText) return;
    const paths = svgContainerRef.current.querySelectorAll(
      "path, polyline, line, circle, ellipse, rect, polygon"
    );
    const total = paths.length;
    if (total === 0) return;

    if (studioPhase === "printing") {
      const drawnCount = Math.floor((progressPercent / 100) * total);
      paths.forEach((el, i) => {
        if (i < drawnCount) {
          el.style.stroke = "#1A1A1A";
          el.style.opacity = "1";
        } else {
          el.style.stroke = "#D4D0C4";
          el.style.opacity = "0.35";
        }
      });
    } else {
      // Khi ở preview hoặc done: hiện đầy đủ nét
      paths.forEach((el) => {
        el.style.stroke = "#1A1A1A";
        el.style.opacity = "1";
      });
    }
  }, [svgText, progressPercent, studioPhase]);

  return (
    <div className="relative flex-1 w-full h-full flex items-center justify-center overflow-hidden select-none">
      
      {/* ── BỘ ĐIỀU KHIỂN TRÊN CANVAS (GÓC TRÊN BÊN PHẢI) ── */}
      <div className="absolute top-4 right-5 flex items-center gap-2 z-20">
        {/* Khổ giấy Badge */}
        <div className="bg-white/95 backdrop-blur border-2 border-[#1A1A1A] px-3 py-1.5 rounded-full text-xs font-bold flex items-center gap-2 shadow-[2px_2px_0px_#1A1A1A]">
          <span className="text-[#7A7870]">KHỔ:</span>
          <span className="text-[#C0392B] font-extrabold">{paper.label}</span>
        </div>

        {/* Zoom Controls */}
        <div className="bg-white/95 backdrop-blur border-2 border-[#1A1A1A] px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1 shadow-[2px_2px_0px_#1A1A1A]">
          <button
            type="button"
            onClick={() => onZoomChange && onZoomChange(-10)}
            title="Thu nhỏ"
            className="w-6 h-6 rounded-full hover:bg-[#F5F3EA] flex items-center justify-center text-sm font-bold text-[#1A1A1A]"
          >
            -
          </button>
          <span className="w-10 text-center font-mono text-[11px] font-bold text-[#1A1A1A]">
            {zoom}%
          </span>
          <button
            type="button"
            onClick={() => onZoomChange && onZoomChange(10)}
            title="Phóng to"
            className="w-6 h-6 rounded-full hover:bg-[#F5F3EA] flex items-center justify-center text-sm font-bold text-[#1A1A1A]"
          >
            +
          </button>
          <div className="h-4 w-[1px] bg-[#D5D1C3] mx-0.5" />
          <button
            type="button"
            onClick={onResetZoom}
            title="Vừa màn hình"
            className="px-2 py-0.5 text-[10px] font-bold text-[#6B6B66] hover:text-[#1A1A1A]"
          >
            FIT
          </button>
        </div>
      </div>

      {/* ── TỜ GIẤY TRẮNG TRUNG TÂM (SCALE THEO ZOOM) ── */}
      <div
        className="transition-transform duration-150 ease-out origin-center"
        style={{ transform: `scale(${zoom / 100})` }}
      >
        <div
          id="omni-paper-sheet"
          style={{ width: paper.width, height: paper.height }}
          className={`bg-[#FEFDF9] rounded-sm relative overflow-hidden flex flex-col p-8 transition-all duration-300 shadow-[0_10px_30px_-5px_rgba(0,0,0,0.08),0_25px_50px_-12px_rgba(26,26,26,0.18),0_0_0_1px_rgba(26,26,26,0.08)]`}
        >
          {/* Header tờ giấy */}
          <div className="flex items-center justify-between text-[10px] font-mono text-[#8C887B] pb-2.5 border-b border-[#ECE8DC] select-none">
            <span className="flex items-center gap-1.5 font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-[#C0392B]" />
              OMNIDRAW VECTOR STUDIO
            </span>
            <span className="truncate max-w-[240px]">
              {isHandwriting ? "CA-VHC SINGLE-STROKE" : `${styleName.toUpperCase()} • NCKH`}
            </span>
          </div>

          {/* Vùng nội dung chính trên giấy */}
          <div className="flex-1 flex items-center justify-center relative my-2 overflow-hidden">
            
            {/* Nếu là thư tay: hiển thị nền dòng kẻ giấy tập vở tự nhiên */}
            {isHandwriting && (
              <div className="absolute inset-0 bg-[linear-gradient(to_bottom,transparent_27px,#E8E4D8_28px)] [background-size:100%_28px] pointer-events-none opacity-80" />
            )}

            {/* Tab 1: Ảnh gốc (chỉ hiển thị khi viewMode === "image" và có resultImageUrl) */}
            {viewMode === "image" && resultImageUrl && (
              <div className="w-full h-full flex items-center justify-center p-2 relative z-10">
                <img
                  src={resultImageUrl}
                  alt={title}
                  className="max-h-full max-w-full object-contain rounded-md drop-shadow-md"
                />
              </div>
            )}

            {/* Tab 2: Nét vẽ SVG */}
            {viewMode === "svg" && (
              <div className="w-full h-full flex items-center justify-center p-2 relative z-10">
                {svgLoading ? (
                  <div className="text-center">
                    <Loader2 size={36} className="mx-auto text-[#C0392B] animate-spin" />
                    <p className="text-xs font-bold text-[#6B6B66] mt-2">Đang tải bản nét vẽ...</p>
                  </div>
                ) : svgError ? (
                  <div className="text-center px-4">
                    <TriangleAlert size={36} className="mx-auto text-[#C0392B]" />
                    <p className="text-xs text-[#C0392B] font-bold mt-2">{svgError}</p>
                  </div>
                ) : svgText ? (
                  <>
                    <style>{`
                      #canvas-svg-container svg {
                        width: 100% !important;
                        height: 100% !important;
                        max-height: 100%;
                        display: block;
                        margin: 0 auto;
                      }
                    `}</style>
                    <div
                      ref={svgContainerRef}
                      id="canvas-svg-container"
                      className="w-full h-full flex items-center justify-center"
                      dangerouslySetInnerHTML={{ __html: svgText }}
                    />
                  </>
                ) : (
                  <div className="text-center text-[#8C887B]">
                    <p className="text-xs font-bold">Chưa có dữ liệu SVG</p>
                  </div>
                )}

                {/* Mô phỏng đầu bút máy vẽ khi đang in */}
                {studioPhase === "printing" && (
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none flex flex-col items-center">
                    <div className="relative w-4 h-4 flex items-center justify-center">
                      <span className="absolute w-full h-full rounded-full bg-[#C0392B] animate-ping opacity-75" />
                      <span className="relative w-2.5 h-2.5 rounded-full bg-[#C0392B] border border-white" />
                    </div>
                    <span className="text-[9px] font-mono font-bold text-[#C0392B] bg-white/90 px-1.5 py-0.5 rounded border border-[#C0392B]/40 shadow-sm mt-1">
                      PEN DOWN (40mm/s)
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer tờ giấy */}
          <div className="pt-2 border-t border-[#ECE8DC] flex items-center justify-between text-[9px] font-mono text-[#8C887B] select-none">
            <span className="truncate max-w-[200px]">ĐỀ TÀI: {title}</span>
            <span>TỶ LỆ 1:1 • THỰC NGHIỆM MÁY VẼ</span>
          </div>
        </div>
      </div>
    </div>
  );
}
