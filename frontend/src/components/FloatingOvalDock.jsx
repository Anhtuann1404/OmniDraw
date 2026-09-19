import React from "react";
import {
  Play,
  Pause,
  RotateCcw,
  XCircle,
  Download,
  PlusCircle,
  PenTool,
  Image as ImageIcon,
  Check,
  Edit3,
  Loader2,
} from "lucide-react";

/**
 * FloatingOvalDock — Chiếc "Gối Oval" điều khiển đáy của OmniDraw Studio
 * Tự động biến đổi giao diện (morphing) theo 3 pha: Preview -> Printing -> Done.
 */
export default function FloatingOvalDock({
  studioPhase = "preview", // "preview" | "printing" | "done"
  mode = "art",
  inputType = "text",
  styleName = "Ký hoạ",
  modelUsed = "dall-e-3",
  strokeCount = 248,
  estimatedMinutes = 12,
  paperSize = "a4",
  onPaperSizeChange,
  viewMode = "svg", // "svg" | "image"
  onViewModeChange,
  onRetry,
  onStartPrint,
  progressPercent = 0,
  strokesDone = 0,
  strokesTotal = 248,
  etaMinutes = 0,
  isPaused = false,
  onPause,
  onResume,
  onCancel,
  actualDrawTimeSec = null,
  onDownloadSvg,
  onCreateNew,
  loading = false,
}) {
  const isHandwriting = mode === "letter" || inputType === "handwriting";

  // Định dạng thời gian thực tế hoàn thành
  const formatActualTime = (sec) => {
    if (!sec) return null;
    const m = Math.floor(sec / 60);
    const s = Math.round(sec % 60);
    if (m > 0 && s > 0) return `${m} phút ${s} giây`;
    if (m > 0) return `${m} phút`;
    return `${s} giây`;
  };

  return (
    <div className="absolute bottom-6 left-0 right-0 flex justify-center items-center pointer-events-none z-30 px-4">
      {/* ── KHUNG GỐI OVAL (OVAL CAPSULE) ── */}
      <div
        id="omni-floating-dock"
        className="pointer-events-auto bg-white/95 backdrop-blur-md border-[2.5px] border-[#1A1A1A] rounded-full py-2 px-4 flex items-center gap-3 transition-all duration-300 max-w-4xl shadow-[0_16px_36px_-6px_rgba(0,0,0,0.22),0_0_0_2.5px_#1A1A1A]"
      >
        {/* =========================================================
            PHA 1: PREVIEW & CẤU HÌNH (GỘP PREVIEW + CONFIRM)
           ========================================================= */}
        {studioPhase === "preview" && (
          <div className="flex items-center gap-3">
            {/* Cụm 1: Icon chế độ & Tóm tắt nét/thời gian */}
            <div className="flex items-center gap-2 pr-3 border-r-2 border-[#ECE8DC]">
              <div className="w-8 h-8 rounded-full bg-[#FEF9E7] border-2 border-[#1A1A1A] flex items-center justify-center text-sm font-bold shrink-0">
                {isHandwriting ? "✍️" : "🎨"}
              </div>
              <div className="leading-tight hidden sm:block">
                <div className="text-[10px] font-extrabold uppercase text-[#8C887B] truncate max-w-[140px]">
                  {isHandwriting ? "THƯ TAY NÉT ĐƠN" : styleName}
                </div>
                <div className="text-xs font-black text-[#1A1A1A] flex items-center gap-1.5">
                  <span>{strokeCount} nét</span>
                  <span className="text-[#D5D1C3]">•</span>
                  <span>~{estimatedMinutes} phút</span>
                </div>
              </div>
            </div>

            {/* Cụm 2: Tab chuyển đổi Nét vẽ SVG / Ảnh gốc (với Art text-to-image) */}
            {inputType === "text" && (
              <div className="flex items-center bg-[#F5F3EA] p-0.5 rounded-full border border-[#1A1A1A]/30">
                <button
                  type="button"
                  onClick={() => onViewModeChange && onViewModeChange("svg")}
                  className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 transition-all ${
                    viewMode === "svg"
                      ? "bg-[#1A1A1A] text-white shadow-sm"
                      : "text-[#6B6B66] hover:text-[#1A1A1A]"
                  }`}
                >
                  <PenTool size={12} />
                  <span>Nét SVG</span>
                </button>
                <button
                  type="button"
                  onClick={() => onViewModeChange && onViewModeChange("image")}
                  className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 transition-all ${
                    viewMode === "image"
                      ? "bg-[#1A1A1A] text-white shadow-sm"
                      : "text-[#6B6B66] hover:text-[#1A1A1A]"
                  }`}
                >
                  <ImageIcon size={12} />
                  <span>Ảnh Gốc</span>
                </button>
              </div>
            )}

            {/* Cụm 3: Menu chọn nhanh khổ giấy */}
            <div className="relative hidden md:block">
              <select
                value={paperSize}
                onChange={(e) => onPaperSizeChange && onPaperSizeChange(e.target.value)}
                className="appearance-none bg-[#FEFDF9] border-2 border-[#1A1A1A] rounded-full px-3 py-1.5 pr-6 text-xs font-bold text-[#1A1A1A] cursor-pointer focus:outline-none shadow-[1px_1px_0px_#1A1A1A]"
              >
                <option value="a4">Khổ A4 (210×297)</option>
                <option value="a3">Khổ A3 (297×420)</option>
                <option value="a5">Khổ A5 (148×210)</option>
              </select>
              <div className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-xs text-[#1A1A1A]">
                ▾
              </div>
            </div>

            <div className="h-6 w-[1.5px] bg-[#ECE8DC] mx-0.5" />

            {/* Cụm 4: Nút Chỉnh sửa & Nút BẮT ĐẦU VẼ NGAY */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onRetry}
                className="px-3 py-1.5 rounded-full border-2 border-[#1A1A1A] text-xs font-bold text-[#1A1A1A] hover:bg-[#F5F3EA] transition-all flex items-center gap-1.5 shadow-[1px_1px_0px_#1A1A1A] active:translate-x-[1px] active:translate-y-[1px]"
              >
                <Edit3 size={13} />
                <span>Chỉnh sửa</span>
              </button>

              <button
                type="button"
                onClick={onStartPrint}
                disabled={loading}
                className="px-4 py-1.5 rounded-full bg-[#C0392B] border-2 border-[#1A1A1A] text-xs font-black text-white hover:bg-[#A93226] transition-all flex items-center gap-2 shadow-[2px_2px_0px_#1A1A1A] active:translate-x-[1px] active:translate-y-[1px] disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    <span>ĐANG GỬI LỆNH...</span>
                  </>
                ) : (
                  <>
                    <Play size={14} fill="currentColor" />
                    <span>BẮT ĐẦU VẼ NGAY</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* =========================================================
            PHA 2: ĐANG VẼ (PRINTING / DRAWING)
           ========================================================= */}
        {studioPhase === "printing" && (
          <div className="flex items-center gap-4">
            {/* Đèn LED nhấp nháy & Trạng thái máy vẽ */}
            <div className="flex items-center gap-2.5 pr-3 border-r-2 border-[#ECE8DC]">
              <div className="relative w-3.5 h-3.5 flex items-center justify-center">
                <span
                  className={`absolute w-full h-full rounded-full ${
                    isPaused ? "bg-amber-500" : "bg-[#C0392B] animate-ping opacity-75"
                  }`}
                />
                <span
                  className={`relative w-2.5 h-2.5 rounded-full ${
                    isPaused ? "bg-amber-500" : "bg-[#C0392B]"
                  }`}
                />
              </div>
              <div className="leading-tight">
                <div className="text-xs font-black text-[#1A1A1A] flex items-center gap-1.5">
                  <span className={isPaused ? "text-amber-600" : "text-[#1A1A1A]"}>
                    {isPaused ? "TẠM DỪNG VẼ" : "ĐANG VẼ LÊN GIẤY"}
                  </span>
                  <span className="text-[11px] font-mono font-bold text-[#C0392B]">
                    {progressPercent}%
                  </span>
                </div>
                <div className="text-[10px] text-[#7A7870] font-medium flex items-center gap-2">
                  <span>
                    Nét: <strong className="text-[#1A1A1A]">{strokesDone} / {strokesTotal}</strong>
                  </span>
                  <span>•</span>
                  <span>
                    Còn lại: <strong className="text-[#1A1A1A]">~{etaMinutes} phút</strong>
                  </span>
                </div>
              </div>
            </div>

            {/* Thanh tiến độ mini bo tròn */}
            <div className="w-40 sm:w-56 bg-[#EDEBDF] h-3 rounded-full border border-[#1A1A1A] overflow-hidden p-0.5 relative">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  isPaused ? "bg-amber-500" : "bg-[#C0392B]"
                }`}
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            {/* Các nút điều khiển: Tạm dừng / Tiếp tục và Hủy */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={isPaused ? onResume : onPause}
                className="px-3 py-1.5 rounded-full border-2 border-[#1A1A1A] text-xs font-bold text-[#1A1A1A] bg-white hover:bg-[#F5F3EA] flex items-center gap-1.5 shadow-[1px_1px_0px_#1A1A1A] active:translate-x-[1px] active:translate-y-[1px]"
              >
                {isPaused ? (
                  <>
                    <Play size={13} fill="currentColor" />
                    <span>Tiếp tục</span>
                  </>
                ) : (
                  <>
                    <Pause size={13} fill="currentColor" />
                    <span>Tạm dừng</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={onCancel}
                className="px-2.5 py-1.5 rounded-full border-2 border-[#C0392B]/40 hover:border-[#C0392B] text-xs font-bold text-[#C0392B] hover:bg-[#FBEAF0] flex items-center gap-1 transition-all"
              >
                <XCircle size={13} />
                <span>Hủy</span>
              </button>
            </div>
          </div>
        )}

        {/* =========================================================
            PHA 3: HOÀN TẤT (DONE)
           ========================================================= */}
        {studioPhase === "done" && (
          <div className="flex items-center gap-4">
            {/* Huy hiệu tích xanh & Tóm tắt kết quả */}
            <div className="flex items-center gap-2.5 pr-3 border-r-2 border-[#ECE8DC]">
              <div className="w-8 h-8 rounded-full bg-emerald-100 border-2 border-emerald-600 flex items-center justify-center text-emerald-700 font-bold text-sm shadow-sm">
                <Check size={16} strokeWidth={3} />
              </div>
              <div className="leading-tight">
                <div className="text-xs font-black text-emerald-700 flex items-center gap-1">
                  TRANH ĐÃ VẼ XONG!
                </div>
                <div className="text-[10px] text-[#7A7870] font-medium">
                  {actualDrawTimeSec ? (
                    <>
                      Thời gian: <strong className="text-[#1A1A1A]">{formatActualTime(actualDrawTimeSec)}</strong> ({strokesTotal} nét)
                    </>
                  ) : (
                    <>Tổng số: <strong className="text-[#1A1A1A]">{strokesTotal} nét</strong></>
                  )}
                </div>
              </div>
            </div>

            {/* Nút hành động: Tải file SVG & Tạo bản mới */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onDownloadSvg}
                className="px-3.5 py-1.5 rounded-full border-2 border-[#1A1A1A] text-xs font-bold text-[#1A1A1A] bg-white hover:bg-[#F5F3EA] flex items-center gap-1.5 shadow-[1px_1px_0px_#1A1A1A] active:translate-x-[1px] active:translate-y-[1px]"
              >
                <Download size={13} />
                <span>Tải file SVG</span>
              </button>

              <button
                type="button"
                onClick={onCreateNew}
                className="px-4 py-1.5 rounded-full bg-[#1A1A1A] text-white text-xs font-black hover:bg-[#333333] flex items-center gap-1.5 shadow-[2px_2px_0px_#C0392B] active:translate-x-[1px] active:translate-y-[1px]"
              >
                <PlusCircle size={14} />
                <span>TẠO BẢN MỚI</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
