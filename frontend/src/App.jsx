import React, { useState, useEffect } from "react";
import CreateScreen from "./screens/CreateScreen";
import StudioScreen from "./screens/StudioScreen";
import PreviewScreen from "./screens/PreviewScreen";
import ConfirmScreen from "./screens/ConfirmScreen";
import PrintStatusScreen from "./screens/PrintStatusScreen";
import DoneScreen from "./screens/DoneScreen";
import Sidebar from "./components/Sidebar";
import { generateArt, startPrint, pausePrint, resumePrint, cancelPrint, getHistory, logExperimentData, deleteHistoryItem } from "./api/omnidraw";
import { usePrintStatusPolling } from "./hooks/usePrintStatusPolling";
import { MOCK_MODE } from "./api/config";

export default function App() {
  const [step, setStep] = useState("create"); 
  const [aiResult, setAiResult] = useState(null); 
  const [doneInfo, setDoneInfo] = useState(null); 
  const [historyItems, setHistoryItems] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [optimisticStatus, setOptimisticStatus] = useState(null); // Thêm state tối ưu giao diện
  const [createSessionKey, setCreateSessionKey] = useState(0);

  const { statusData } = usePrintStatusPolling(step === "printing" ? aiResult?.requestId : null);

  useEffect(() => {
    if (step === "printing" && statusData) {
      if (statusData.status === "done" || statusData.status === "error") {
        const payload = {
          request_id: aiResult?.requestId,
          timestamp: new Date().toISOString(),
          dataset_item_id: aiResult?.title,
          style: aiResult?.style,
          input_type: aiResult?.inputType,
          model_used: aiResult?.meta?.modelUsed,
          final_status: statusData.status,
          actual_draw_time_sec: statusData.actualDrawTimeSec || 0,
          error_code: statusData.error?.code || null
        };

        logExperimentData(payload).then(() => {
          // Refresh lịch sử sau khi backend đã lưu thành công
          getHistory().then((items) => setHistoryItems(items));
        }).catch(err => 
          console.warn("Lỗi ghi log CSV/DB:", err)
        );

        if (statusData.status === "done") {
          setDoneInfo({ actualDrawTimeSec: statusData.actualDrawTimeSec });
          setStep("done");
        }
      }
    }
  }, [step, statusData]);

  async function handleCreateSubmit({ mode = "art", inputType, style, font, letterType, seed, imageBase64, prompt, fileName, paperSize }) {
    setLoading(true);
    setErrorMsg(null);
    try {
      const result = await generateArt({ inputType, style, font, letterType, seed, imageBase64, prompt, paperSize, mode });
      let title = "Bản vẽ OmniDraw";
      if (mode === "letter") {
        title = fileName || (prompt ? (prompt.length > 32 ? prompt.slice(0, 32) + "..." : prompt) : "Thư tay");
      } else {
        title = inputType === "text" ? prompt : (fileName || "Bản vẽ upload");
      }
      setAiResult({ ...result, mode, style, font, letterType, seed, inputType, title, paperSize }); // lưu thêm paperSize để ConfirmScreen dùng
      setStep("preview");
    } catch (err) {
      setErrorMsg(err.message || "Có lỗi khi tạo tranh hoặc thư tay, thử lại nhé.");
    } finally {
      setLoading(false);
    }
  }

  async function handleStartPrint(options = {}) {
    if (!aiResult?.requestId) return;
    const chosenPaperSize = options?.paperSize || aiResult.paperSize || "a4";
    setLoading(true);
    setOptimisticStatus("printing"); // Cập nhật giao diện ngay lập tức
    try {
      await startPrint({ requestId: aiResult.requestId, paperSize: chosenPaperSize });
      setAiResult((prev) => (prev ? { ...prev, paperSize: chosenPaperSize } : prev));
      setStep("printing");
      
      // Log trạng thái queued
      await logExperimentData({
        request_id: aiResult.requestId,
        timestamp: new Date().toISOString(),
        dataset_item_id: aiResult.title,
        style: aiResult.style || "unknown",
        input_type: aiResult.inputType || "unknown",
        model_used: aiResult.meta?.modelUsed || "ai-core-v1-python",
        final_status: "queued", 
        actual_draw_time_sec: 0, 
        error_code: null
      });
    } catch (err) {
      setOptimisticStatus(null); // Hoàn tác nếu lỗi
      setErrorMsg(err.message || "Không thể bắt đầu vẽ, thử lại nhé.");
    } finally {
      setLoading(false);
    }
  }

  async function handlePause() {
    if (!aiResult?.requestId) return;
    setOptimisticStatus("paused"); // Cập nhật giao diện ngay lập tức
    try {
      await pausePrint(aiResult.requestId);
    } catch (err) {
      setOptimisticStatus(null); // Hoàn tác nếu lỗi
      setErrorMsg(err.message);
    }
  }

  async function handleResume() {
    if (!aiResult?.requestId) return;
    setOptimisticStatus("printing"); // Cập nhật giao diện ngay lập tức
    try {
      await resumePrint(aiResult.requestId);
    } catch (err) {
      setOptimisticStatus(null); // Hoàn tác nếu lỗi
      setErrorMsg(err.message);
    }
  }

  async function handleCancel() {
    if (aiResult?.requestId) {
      try {
        await cancelPrint(aiResult.requestId);
        await logExperimentData({
          request_id: aiResult.requestId,
          timestamp: new Date().toISOString(),
          style: aiResult.style || "unknown",
          model_used: aiResult.meta?.modelUsed || "ai-core-v1-python",
          final_status: "cancelled", 
          actual_draw_time_sec: 0, 
          error_code: null
        });
      } catch (err) {
        setErrorMsg(err.message);
      }
    }
    setStep("create");
    setAiResult(null);
    setDoneInfo(null);
    setOptimisticStatus(null); // Xóa trạng thái ảo khi hủy
  }

  function handleCreateNew() {
    setCreateSessionKey((key) => key + 1);
    setAiResult(null);
    setDoneInfo(null);
    setErrorMsg(null);
    setOptimisticStatus(null);
    setStep("create");
  }

  useEffect(() => {
    // Fetch lịch sử ngay khi app mount vì sidebar luôn hiển thị
    getHistory()
      .then((items) => setHistoryItems(items))
      .catch((err) => console.warn("Không tải được lịch sử:", err));
  }, []);

  // ── XỬ LÝ CLICK LỊCH SỬ ──
  function handleOpenHistoryItem(item) {
    const strokeCount = item.strokeCount || (item.svgMetrics?.pen_lift_count != null ? item.svgMetrics.pen_lift_count + 1 : undefined);
    const estimatedMinutes = item.estimatedMinutes || item.minutes || (item.svgMetrics?.total_path_length_mm != null ? Math.ceil(((item.svgMetrics.total_path_length_mm || 0) + (item.svgMetrics.pen_lift_distance_mm || 0)) / 40 / 60) : undefined);

    // Phục hồi lại dữ liệu tranh từ DB vào state aiResult
    setAiResult({
      requestId: item.id,
      title: item.title,
      style: item.style,
      inputType: item.inputType || "unknown", // fallback nếu cũ
      resultImageBase64: item.thumbnailUrl,    // API thumbnail trả về ảnh PNG gốc
      svgReady: true,                          // Ảnh cũ chắc chắn đã có SVG
      paperSize: item.paperSize || "a4",
      strokeCount: strokeCount,
      estimatedMinutes: estimatedMinutes,
      svgMetrics: item.svgMetrics || (strokeCount ? {
        pen_lift_count: strokeCount - 1,
        total_path_length_mm: (estimatedMinutes || 5) * 60 * 40 * 0.9,
        pen_lift_distance_mm: (estimatedMinutes || 5) * 60 * 40 * 0.1,
      } : undefined),
      meta: { modelUsed: item.modelUsed || (item.inputType === "image" ? "OpenCV Vectorizer" : "dall-e-3") }
    });
    // Phục hồi số phút vẽ (nếu có)
    if (item.actualDrawTimeSec || item.minutes || estimatedMinutes) {
      setDoneInfo({ actualDrawTimeSec: item.actualDrawTimeSec || ((item.minutes || estimatedMinutes) * 60) });
    }
    // Nhảy về màn Preview để có thể bấm vẽ lại
    setStep("preview");
  }

  async function handleDeleteHistory(item) {
    if (!window.confirm("Bạn có chắc muốn xoá bức tranh này khỏi lịch sử không?")) return;
    try {
      await deleteHistoryItem(item.id);
      // Tải lại lịch sử
      const items = await getHistory();
      setHistoryItems(items);
      // Nếu tranh đang mở là tranh bị xoá, quay về trang tạo tranh
      if (aiResult?.requestId === item.id) {
        setStep("create");
        setAiResult(null);
      }
    } catch (err) {
      console.warn("Lỗi xoá lịch sử:", err);
      alert("Không thể xoá lịch sử lúc này!");
    }
  }

  const strokeCount =
    aiResult?.strokeCount != null
      ? aiResult.strokeCount
      : (aiResult?.svgMetrics?.pen_lift_count != null
          ? aiResult.svgMetrics.pen_lift_count + 1
          : 248);

  const estimatedMinutes =
    aiResult?.estimatedMinutes != null
      ? aiResult.estimatedMinutes
      : (aiResult?.svgMetrics?.total_path_length_mm != null
          ? Math.max(1, Math.ceil(((aiResult.svgMetrics.total_path_length_mm || 0) + (aiResult.svgMetrics.pen_lift_distance_mm || 0)) / 40 / 60))
          : (aiResult?.minutes != null ? aiResult.minutes : 12));

  const strokesTotal = strokeCount;
  const strokesDone =
    statusData && statusData.progressPercent != null
      ? Math.floor((strokesTotal * statusData.progressPercent) / 100)
      : 0;

  const etaMinutes =
    statusData?.etaSec != null
      ? Math.ceil(statusData.etaSec / 60)
      : Math.ceil((estimatedMinutes * (100 - (statusData?.progressPercent || 0))) / 100);

  return (
    <div className="flex h-screen overflow-hidden bg-[#F5F3EA]">

      {/* ── Sidebar trái ── */}
      <Sidebar
        items={historyItems || []}
        activeItemId={aiResult?.requestId}
        onCreateNew={handleCreateNew}
        onOpenItem={handleOpenHistoryItem}
        onDeleteItem={handleDeleteHistory}
      />

      {/* ── Vùng chính: Create Screen hoặc White Paper Studio ── */}
      {step === "create" ? (
        <main className="flex-1 flex flex-col items-center justify-center pt-2 pb-8 px-6 gap-2.5 overflow-y-auto">
          {MOCK_MODE && (
            <div className="text-xs font-bold text-[#6B6B66] bg-white border-2 border-[#1A1A1A] rounded-full px-3 py-1">
              🧪 MOCK MODE — chưa nối backend thật (đổi VITE_MOCK_MODE=false trong .env khi sẵn sàng)
            </div>
          )}

          {errorMsg && (
            <div className="text-xs font-bold text-[#C0392B] bg-[#FBEAF0] border-2 border-[#C0392B] rounded-lg px-3 py-2 max-w-md text-center">
              {errorMsg}
            </div>
          )}

          <CreateScreen
            key={createSessionKey}
            onSubmit={handleCreateSubmit}
            loading={loading}
          />
        </main>
      ) : (
        <main className="flex-1 relative flex flex-col items-center justify-center overflow-hidden bg-[#ECE8DC] bg-grid-dots">
          {/* Status badge & error message floating at top-left */}
          <div className="absolute top-3 left-6 flex items-center gap-2 z-40">
            {MOCK_MODE && (
              <div className="text-[11px] font-bold text-[#6B6B66] bg-white/90 backdrop-blur border-2 border-[#1A1A1A] rounded-full px-3 py-0.5 shadow-sm">
                🧪 MOCK MODE
              </div>
            )}
            {errorMsg && (
              <div className="text-[11px] font-bold text-[#C0392B] bg-[#FBEAF0] border-2 border-[#C0392B] rounded-full px-3 py-0.5 shadow-sm">
                {errorMsg}
              </div>
            )}
          </div>

          <StudioScreen
            studioPhase={step === "printing" ? "printing" : (step === "done" ? "done" : "preview")}
            requestId={aiResult?.requestId}
            mode={aiResult?.mode || "art"}
            inputType={aiResult?.inputType || "text"}
            resultImageUrl={aiResult?.resultImageBase64}
            svgReady={aiResult?.svgReady || false}
            style={labelForStyle(aiResult?.style)}
            modelUsed={aiResult?.meta?.modelUsed}
            title={aiResult?.title || "Bản vẽ OmniDraw"}
            strokeCount={strokeCount}
            estimatedMinutes={estimatedMinutes}
            actualDrawTimeSec={doneInfo?.actualDrawTimeSec || statusData?.actualDrawTimeSec}
            paperSize={aiResult?.paperSize || "a4"}
            onPaperSizeChange={(newSize) =>
              setAiResult((prev) => (prev ? { ...prev, paperSize: newSize } : prev))
            }
            progressPercent={statusData?.progressPercent || 0}
            strokesDone={strokesDone}
            strokesTotal={strokesTotal}
            etaMinutes={etaMinutes}
            isPaused={(optimisticStatus || statusData?.status) === "paused"}
            onRetry={() => setStep("create")}
            onStartPrint={handleStartPrint}
            onPause={handlePause}
            onResume={handleResume}
            onCancel={handleCancel}
            onCreateNew={handleCreateNew}
            loading={loading}
          />
        </main>
      )}

      {/* ── Debug nav bar (dev only - top right) ── */}
      {MOCK_MODE && (
        <div className="fixed top-3 right-6 flex gap-1 bg-white/90 backdrop-blur border-2 border-[#1A1A1A] rounded-full p-1 shadow-md z-50">
          {[
            ["create", "create"],
            ["preview", "preview"],
            ["printing", "printing"],
            ["done", "done"],
          ].map(([key, label]) => (
            <button
              key={key}
              onClick={() => {
                if (!aiResult && key !== "create") {
                  setAiResult({
                    requestId: "mock-debug-specimen",
                    title: "Bản vẽ Demo OmniDraw",
                    style: "sketch",
                    inputType: "text",
                    mode: "art",
                    paperSize: "a4",
                    strokeCount: 248,
                    estimatedMinutes: 12,
                    meta: { modelUsed: "style-transfer-v1 (mock)", processingTimeMs: 1200 },
                  });
                }
                setStep(key);
              }}
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full transition-all ${
                step === key ? "bg-[#1A1A1A] text-white" : "text-[#1A1A1A] hover:bg-[#F5F3EA]"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      )}

    </div>
  );
}

function labelForStyle(id) {
  const map = {
    sketch: "Ký hoạ",
    line_art: "Line art",
    stipple: "Chấm bi",
    hatching: "Hatching",
    hand_hocsinh: "Chữ Học Sinh",
    hand_nguoilon: "Chữ Thảo Nghiêng",
    hand_thuphap: "Chữ Thư Pháp",
    hand_chukinhanh: "Chữ Ký Tên",
  };
  return map[id] || id || "Ký hoạ";
}