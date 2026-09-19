import React, { useState, useEffect, useCallback } from "react";
import WhitePaperCanvas from "../components/WhitePaperCanvas";
import FloatingOvalDock from "../components/FloatingOvalDock";
import { getSvgContent } from "../api/omnidraw";

/**
 * StudioScreen — Không gian làm việc chính (White Paper Studio) của OmniDraw
 * Tích hợp toàn diện các trạng thái sau bước tạo tranh (Preview, Drawing, Done).
 */
export default function StudioScreen({
  studioPhase = "preview", // "preview" | "printing" | "done"
  requestId,
  mode = "art",
  inputType = "text",
  resultImageUrl,
  svgReady = false,
  style = "Ký hoạ",
  modelUsed = "dall-e-3",
  title = "Bản vẽ OmniDraw",
  strokeCount = 248,
  estimatedMinutes = 12,
  actualDrawTimeSec = null,
  paperSize = "a4",
  onPaperSizeChange,
  progressPercent = 0,
  strokesDone = 0,
  strokesTotal = 248,
  etaMinutes = 0,
  isPaused = false,
  onRetry,
  onStartPrint,
  onPause,
  onResume,
  onCancel,
  onCreateNew,
  loading = false,
}) {
  const isHandwriting = mode === "letter" || inputType === "handwriting";
  const [zoom, setZoom] = useState(85);
  const [viewMode, setViewMode] = useState(inputType === "image" || isHandwriting ? "svg" : "svg");
  const [svgText, setSvgText] = useState(null);
  const [svgLoading, setSvgLoading] = useState(false);
  const [svgError, setSvgError] = useState(null);
  const [currentPaperSize, setCurrentPaperSize] = useState(paperSize);

  // Đồng bộ paperSize từ props
  useEffect(() => {
    if (paperSize) setCurrentPaperSize(paperSize);
  }, [paperSize]);

  // Reset tab & SVG khi đổi requestId
  useEffect(() => {
    setSvgText(null);
    setSvgError(null);
    setViewMode("svg");
  }, [requestId]);

  // Tải nội dung SVG từ API backend hoặc mock
  useEffect(() => {
    if (!requestId) return;
    let isCancelled = false;

    setSvgLoading(true);
    setSvgError(null);

    getSvgContent(requestId)
      .then((res) => {
        if (!isCancelled) {
          setSvgText(res.svgText);
        }
      })
      .catch((err) => {
        if (!isCancelled) {
          setSvgError("Không tải được file SVG: " + (err.message || ""));
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setSvgLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [requestId]);

  // Xử lý đổi khổ giấy
  const handlePaperSizeChange = (newSize) => {
    setCurrentPaperSize(newSize);
    if (onPaperSizeChange) {
      onPaperSizeChange(newSize);
    }
  };

  // Zoom handlers
  const handleZoomChange = useCallback((delta) => {
    setZoom((prev) => Math.max(50, Math.min(150, prev + delta)));
  }, []);

  const handleResetZoom = useCallback(() => {
    setZoom(85);
  }, []);

  // Tải file SVG trực tiếp về máy tính
  const handleDownloadSvg = useCallback(() => {
    if (!svgText) {
      alert("Chưa có dữ liệu SVG để tải về.");
      return;
    }
    const blob = new Blob([svgText], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const safeTitle = (title || "omnidraw_vector").replace(/[^a-zA-Z0-9_-]/g, "_");
    link.href = url;
    link.download = `${safeTitle}_${currentPaperSize}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [svgText, title, currentPaperSize]);

  // Gửi lệnh in kèm khổ giấy hiện tại
  const handleStartPrintWithPaper = useCallback(() => {
    if (onStartPrint) {
      onStartPrint({ paperSize: currentPaperSize });
    }
  }, [onStartPrint, currentPaperSize]);

  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center overflow-hidden">
      {/* ── 1. TRANG GIẤY TRẮNG TRUNG TÂM (CANVAS) ── */}
      <WhitePaperCanvas
        paperSize={currentPaperSize}
        mode={mode}
        inputType={inputType}
        svgText={svgText}
        svgLoading={svgLoading}
        svgError={svgError}
        resultImageUrl={resultImageUrl}
        viewMode={viewMode}
        studioPhase={studioPhase}
        progressPercent={progressPercent}
        zoom={zoom}
        onZoomChange={handleZoomChange}
        onResetZoom={handleResetZoom}
        title={title}
        styleName={style}
      />

      {/* ── 2. CHIẾC GỐI OVAL ĐIỀU KHIỂN ĐÁY (DOCK) ── */}
      <FloatingOvalDock
        studioPhase={studioPhase}
        mode={mode}
        inputType={inputType}
        styleName={style}
        modelUsed={modelUsed}
        strokeCount={strokeCount}
        estimatedMinutes={estimatedMinutes}
        paperSize={currentPaperSize}
        onPaperSizeChange={handlePaperSizeChange}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        onRetry={onRetry}
        onStartPrint={handleStartPrintWithPaper}
        progressPercent={progressPercent}
        strokesDone={strokesDone}
        strokesTotal={strokesTotal}
        etaMinutes={etaMinutes}
        isPaused={isPaused}
        onPause={onPause}
        onResume={onResume}
        onCancel={onCancel}
        actualDrawTimeSec={actualDrawTimeSec}
        onDownloadSvg={handleDownloadSvg}
        onCreateNew={onCreateNew}
        loading={loading}
      />
    </div>
  );
}
