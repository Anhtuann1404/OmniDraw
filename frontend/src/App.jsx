import React, { useState, useEffect } from "react";
import CreateScreen from "./screens/CreateScreen";
import PreviewScreen from "./screens/PreviewScreen";
import ConfirmScreen from "./screens/ConfirmScreen";
import PrintStatusScreen from "./screens/PrintStatusScreen";
import DoneScreen from "./screens/DoneScreen";
import HistoryScreen from "./screens/HistoryScreen";
import { generateArt, startPrint, pausePrint, cancelPrint, getHistory, logExperimentData } from "./api/omnidraw";
import { usePrintStatusPolling } from "./hooks/usePrintStatusPolling";
import { MOCK_MODE } from "./api/config";


/**
 * App — nối 5 màn theo đúng luồng, gọi API thật qua src/api/omnidraw.js.
 */
export default function App() {
  const [step, setStep] = useState("create"); // "create" | "preview" | "confirm" | "printing" | "done" | "history"
  const [aiResult, setAiResult] = useState(null); // { requestId, resultImageBase64, meta, style }
  const [doneInfo, setDoneInfo] = useState(null); // { actualDrawTimeSec }
  const [historyItems, setHistoryItems] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const { statusData } = usePrintStatusPolling(step === "printing" ? aiResult?.requestId : null);

  // KẾT HỢP: Khi máy vẽ xong (hoặc lỗi) -> Tự động ghi log -> Chuyển sang màn DoneScreen
  useEffect(() => {
    if (step === "printing" && statusData) {
      if (statusData.status === "done" || statusData.status === "error") {
        
        // 1. Bắn API ghi log tự động
        const payload = {
          request_id: aiResult?.requestId,
          timestamp: new Date().toISOString(),
          style: aiResult?.style,
          model_used: aiResult?.meta?.modelUsed,
          final_status: statusData.status,
          actual_draw_time_sec: statusData.actualDrawTimeSec || 0,
          error_code: statusData.error?.code || null
        };

        logExperimentData(payload).catch(err => 
          console.warn("Lỗi ghi log CSV:", err)
        );

        // 2. Chuyển UI sang màn hoàn thành nếu vẽ thành công
        if (statusData.status === "done") {
          setDoneInfo({ actualDrawTimeSec: statusData.actualDrawTimeSec });
          setStep("done");
        }
      }
    }
  }, [step, statusData]);

  async function handleCreateSubmit({ inputType, style, imageBase64, prompt }) {
    setLoading(true);
    setErrorMsg(null);
    try {
      const result = await generateArt({ inputType, style, imageBase64, prompt });
      setAiResult({ ...result, style });
      setStep("preview");
    } catch (err) {
      setErrorMsg(err.message || "Có lỗi khi tạo tranh, thử lại nhé.");
    } finally {
      setLoading(false);
    }
  }

  async function handleStartPrint({ paperSize }) {
    setLoading(true);
    setErrorMsg(null);
    try {
      await startPrint({ requestId: aiResult.requestId, paperSize });
      setStep("printing");
    } catch (err) {
      setErrorMsg(err.message || "Không thể bắt đầu vẽ, thử lại nhé.");
    } finally {
      setLoading(false);
    }
  }

  async function handlePause() {
    if (!aiResult?.requestId) return;
    try {
      await pausePrint(aiResult.requestId);
    } catch (err) {
      setErrorMsg(err.message);
    }
  }

  async function handleCancel() {
    if (aiResult?.requestId) {
      try {
        // 1. Dừng máy vẽ
        await cancelPrint(aiResult.requestId);

        // 2. ÉP GHI LOG HUỶ (Phần cực kỳ quan trọng để CSV nhận dữ liệu)
        await logExperimentData({
          request_id: aiResult.requestId,
          timestamp: new Date().toISOString(),
          style: aiResult.style || "unknown",
          model_used: aiResult.meta?.modelUsed || "ai-core-v1-python",
          final_status: "cancelled", 
          actual_draw_time_sec: 0, 
          error_code: null
        });
        console.log("✅ Đã ghi log trạng thái cancelled thành công!");

      } catch (err) {
        setErrorMsg(err.message);
      }
    }
    
    // 3. Sau khi ghi xong mới chuyển màn hình
    setStep("create");
    setAiResult(null);
    setDoneInfo(null);
  }

  function handleCreateNewFromDone() {
    setAiResult(null);
    setDoneInfo(null);
    setStep("create");
  }

  async function openHistory() {
    setStep("history");
    if (!historyItems) {
      try {
        const items = await getHistory();
        setHistoryItems(items);
      } catch (err) {
        setErrorMsg(err.message);
      }
    }
  }

  return (
    <div className="min-h-screen bg-[#F5F3EA] flex flex-col items-center justify-center p-6 gap-3">
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

      {step === "create" && <CreateScreen onSubmit={handleCreateSubmit} loading={loading} />}

      {step === "preview" && aiResult && (
        <PreviewScreen
          resultImageUrl={aiResult.resultImageBase64}
          style={labelForStyle(aiResult.style)}
          modelUsed={aiResult.meta?.modelUsed}
          processingTimeSec={aiResult.meta?.processingTimeMs ? aiResult.meta.processingTimeMs / 1000 : undefined}
          onRetry={() => setStep("create")}
          onConfirm={() => setStep("confirm")}
        />
      )}

      {step === "confirm" && <ConfirmScreen onBack={() => setStep("preview")} onStart={handleStartPrint} />}

      {step === "printing" && statusData && statusData.status !== "done" && (
        <PrintStatusScreen
          progressPercent={statusData.progressPercent}
          etaMinutes={Math.ceil((statusData.etaSec || 0) / 60)}
          machineStatus={statusData.status === "error" ? "error" : "ok"}
          onPause={handlePause}
          onCancel={handleCancel}
        />
      )}

      {step === "done" && (
        <DoneScreen
          resultImageUrl={aiResult?.resultImageBase64}
          actualDrawTimeSec={doneInfo?.actualDrawTimeSec}
          onCreateNew={handleCreateNewFromDone}
          onViewHistory={openHistory}
        />
      )}

      {step === "history" && (
        <HistoryScreen items={historyItems || []} onCreateNew={() => setStep("create")} onOpenItem={(item) => console.log("open", item)} />
      )}

      {/* Thanh điều hướng nhanh phục vụ demo/test — xoá khi tích hợp thật xong hoàn toàn */}
      <div className="fixed bottom-4 left-1/2 -translate-x-1/2 flex gap-2 bg-white border-2 border-[#1A1A1A] rounded-full px-3 py-2 shadow-lg">
        {[
          ["create", "create"],
          ["preview", "preview"],
          ["confirm", "confirm"],
          ["printing", "printing"],
          ["done", "done"],
          ["history", "history"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => (key === "history" ? openHistory() : setStep(key))}
            className={`text-[10px] font-bold px-2 py-1 rounded-full ${
              step === key ? "bg-[#1A1A1A] text-white" : "text-[#1A1A1A]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}

function labelForStyle(id) {
  const map = { sketch: "Ký hoạ", line_art: "Line art", stipple: "Chấm bi", hatching: "Hatching" };
  return map[id] || id || "Ký hoạ";
}