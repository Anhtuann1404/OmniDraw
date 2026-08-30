import React, { useState, useEffect } from "react";
import CreateScreen from "./screens/CreateScreen";
import PreviewScreen from "./screens/PreviewScreen";
import ConfirmScreen from "./screens/ConfirmScreen";
import PrintStatusScreen from "./screens/PrintStatusScreen";
import DoneScreen from "./screens/DoneScreen";
import Sidebar from "./components/Sidebar";
import { generateArt, startPrint, pausePrint, resumePrint, cancelPrint, getHistory, logExperimentData } from "./api/omnidraw";
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

  const { statusData } = usePrintStatusPolling(step === "printing" ? aiResult?.requestId : null);

  useEffect(() => {
    if (step === "printing" && statusData) {
      if (statusData.status === "done" || statusData.status === "error") {
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

  function handleCreateNewFromDone() {
    setAiResult(null);
    setDoneInfo(null);
    setStep("create");
    setOptimisticStatus(null);
  }

  useEffect(() => {
    // Fetch lịch sử ngay khi app mount vì sidebar luôn hiển thị
    getHistory()
      .then((items) => setHistoryItems(items))
      .catch((err) => console.warn("Không tải được lịch sử:", err));
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-[#F5F3EA]">

      {/* ── Sidebar trái ── */}
      <Sidebar
        items={historyItems || []}
        onCreateNew={handleCreateNewFromDone}
        onOpenItem={(item) => console.log("open", item)}
      />

      {/* ── Vùng chính — card căn giữa ── */}
      <main className="flex-1 flex flex-col items-center justify-center p-6 gap-3 overflow-y-auto">

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
            isPaused={(optimisticStatus || statusData.status) === "paused"}
            onPause={handlePause}
            onResume={handleResume}
            onCancel={handleCancel}
          />
        )}

        {step === "done" && (
          <DoneScreen
            resultImageUrl={aiResult?.resultImageBase64}
            actualDrawTimeSec={doneInfo?.actualDrawTimeSec}
            onCreateNew={handleCreateNewFromDone}
            onViewHistory={() => {}} // history giờ luôn ở sidebar
          />
        )}

        {/* ── Debug nav bar (dev only) ── */}
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 flex gap-2 bg-white border-2 border-[#1A1A1A] rounded-full px-3 py-2 shadow-lg">
          {[
            ["create", "create"],
            ["preview", "preview"],
            ["confirm", "confirm"],
            ["printing", "printing"],
            ["done", "done"],
          ].map(([key, label]) => (
            <button
              key={key}
              onClick={() => setStep(key)}
              className={`text-[10px] font-bold px-2 py-1 rounded-full ${
                step === key ? "bg-[#1A1A1A] text-white" : "text-[#1A1A1A]"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

      </main>
    </div>
  );
}

function labelForStyle(id) {
  const map = { sketch: "Ký hoạ", line_art: "Line art", stipple: "Chấm bi", hatching: "Hatching" };
  return map[id] || id || "Ký hoạ";
}