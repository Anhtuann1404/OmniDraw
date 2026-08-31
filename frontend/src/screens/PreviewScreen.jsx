import React, { useState, useEffect } from "react";
import { Image, RefreshCw, ArrowRight, PenTool, Loader2, TriangleAlert } from "lucide-react";
import { ScreenShell, ComicButton, StepBadge, Logo, HardShadowBox, StarBadge } from "../components/ComicPrimitives";
import { getSvgContent } from "../api/omnidraw";

/**
 * Màn 2 — Xem trước kết quả
 * Props:
 *  - requestId?: string
 *  - inputType?: "image" | "text"   ← phân nhánh hiển thị chính
 *  - resultImageUrl?: string         (chỉ dùng khi inputType === "text")
 *  - svgReady?: boolean
 *  - style, modelUsed, processingTimeSec
 *  - onRetry() / onConfirm()
 */
export default function PreviewScreen({
  requestId,
  inputType = "text",
  resultImageUrl,
  svgReady = false,
  style = "Ký hoạ",
  modelUsed = "dall-e-3",
  processingTimeSec = 3.2,
  onRetry,
  onConfirm,
}) {
  // Khi tải ảnh lên: mặc định sang tab SVG luôn
  const [activeTab, setActiveTab] = useState(inputType === "image" ? "svg" : "image");
  const [svgText, setSvgText] = useState(null);
  const [svgLoading, setSvgLoading] = useState(false);
  const [svgError, setSvgError] = useState(null);

  // Khi sang tab SVG hoặc inputType==="image" thì tự động fetch SVG
  useEffect(() => {
    if (activeTab !== "svg" || !requestId) return;
    if (svgText) return;

    setSvgLoading(true);
    setSvgError(null);

    getSvgContent(requestId)
      .then((res) => setSvgText(res.svgText))
      .catch((err) => setSvgError("Không tải được file SVG: " + (err.message || "")))
      .finally(() => setSvgLoading(false));
  }, [activeTab, requestId, svgText]);

  // Tiêu đề phụ thay đổi theo luồng
  const subtitle = inputType === "image" ? "Xem trước nét vẽ SVG" : "Xem trước kết quả AI";
  const displayModel = inputType === "image" ? "OpenCV Vectorizer" : (modelUsed || "dall-e-3");

  return (
    <ScreenShell patternId="pattern-preview">
      <div className="flex items-start justify-between mb-4">
        <Logo subtitle={subtitle} size="text-[28px]" />
        <StepBadge step={2} />
      </div>

      {/* ── Tab switcher: chỉ hiện khi AI sinh ảnh ── */}
      {inputType === "text" && (
        <div className="flex gap-2 mb-3">
          <TabButton
            active={activeTab === "image"}
            onClick={() => setActiveTab("image")}
            icon={<Image size={13} />}
            label="Ảnh AI"
          />
          <TabButton
            active={activeTab === "svg"}
            onClick={() => setActiveTab("svg")}
            icon={<PenTool size={13} />}
            label="Nét vẽ SVG"
            badge={svgReady ? "✓" : null}
          />
        </div>
      )}

      {/* ── Canvas ── */}
      <div className="relative mb-4">
        <HardShadowBox shadowOffset={5}>
          <div className="h-64 flex items-center justify-center bg-[#FEFDF9] rounded-xl overflow-hidden">

            {/* Tab Ảnh AI — chỉ render khi inputType==="text" và tab đang ở "image" */}
            {activeTab === "image" && inputType === "text" && (
              resultImageUrl ? (
                <img
                  src={resultImageUrl}
                  alt="Kết quả AI"
                  className="max-h-64 max-w-full object-contain rounded-lg"
                />
              ) : (
                <div className="text-center">
                  <Image size={42} className="mx-auto text-[#C0392B]" />
                  <p className="text-sm text-[#6B6B66] font-medium mt-2">
                    Ảnh kết quả AI (phong cách: {style})
                  </p>
                </div>
              )
            )}

            {/* Tab SVG — hiển thị với cả 2 luồng khi tab = "svg" */}
            {activeTab === "svg" && (
              svgLoading ? (
                <div className="text-center">
                  <Loader2 size={36} className="mx-auto text-[#C0392B] animate-spin" />
                  <p className="text-sm text-[#6B6B66] font-medium mt-2">Đang tải bản nét vẽ...</p>
                </div>
              ) : svgError ? (
                <div className="text-center px-4">
                  <TriangleAlert size={36} className="mx-auto text-[#C0392B]" />
                  <p className="text-xs text-[#C0392B] font-medium mt-2">{svgError}</p>
                </div>
              ) : svgText ? (
                <>
                  <style>{`#svg-preview-tab svg { width: 100% !important; height: 100% !important; max-height: 256px; }`}</style>
                  <div
                    id="svg-preview-tab"
                    className="w-full h-full flex items-center justify-center p-2"
                    dangerouslySetInnerHTML={{ __html: svgText }}
                  />
                </>
              ) : (
                <div className="text-center px-4">
                  <PenTool size={36} className="mx-auto text-[#6B6B66]" />
                  <p className="text-sm text-[#6B6B66] font-medium mt-2">
                    {svgReady ? "Bấm để tải bản nét vẽ..." : "Backend đang xử lý nét vẽ..."}
                  </p>
                  {!svgReady && (
                    <p className="text-xs text-[#6B6B66] mt-1">Thử lại sau vài giây</p>
                  )}
                </div>
              )
            )}

          </div>
        </HardShadowBox>
        <div className="absolute -top-2.5 -right-2.5">
          <StarBadge topLabel="XONG" bottomLabel="" size={56} />
        </div>
      </div>

      {/* ── Thống kê ── */}
      <div className="flex gap-2.5 mb-4">
        <StatBox label="STYLE" value={style} />
        <StatBox label="MODEL" value={displayModel} />
        {inputType === "text" && (
          <StatBox label="THỜI GIAN" value={`${processingTimeSec}s`} />
        )}
      </div>

      {/* ── Nút hành động ── */}
      <div className="flex items-center justify-between border-t-[3px] border-[#1A1A1A] pt-4">
        <ComicButton variant="secondary" onClick={onRetry}>
          <span className="flex items-center gap-1.5">
            <RefreshCw size={15} /> {inputType === "image" ? "TẢI ẢNH KHÁC" : "THỬ LẠI"}
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

function TabButton({ active, onClick, icon, label, badge }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold border-2 border-[#1A1A1A] transition-all ${
        active ? "bg-[#1A1A1A] text-white" : "bg-white text-[#1A1A1A] hover:bg-[#F0EEE5]"
      }`}
    >
      {icon}
      {label}
      {badge && (
        <span className="ml-0.5 bg-green-500 text-white rounded-full text-[9px] w-4 h-4 flex items-center justify-center font-bold">
          {badge}
        </span>
      )}
    </button>
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
