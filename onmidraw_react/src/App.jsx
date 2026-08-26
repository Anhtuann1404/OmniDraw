import React, { useState, useEffect } from "react";
import CreateScreen from "./screens/CreateScreen";
import PreviewScreen from "./screens/PreviewScreen";
import ConfirmScreen from "./screens/ConfirmScreen";
import PrintStatusScreen from "./screens/PrintStatusScreen";
import HistoryScreen from "./screens/HistoryScreen";

export default function App() {
  const [step, setStep] = useState("create");
  const [config, setConfig] = useState(null);
  
  // Các state để làm cho app "sống" lên
  const [isGenerating, setIsGenerating] = useState(false);
  const [printProgress, setPrintProgress] = useState(0);

  // 1. Giả lập luồng AI sinh ảnh (Mất 3 giây)
  const handleCreateSubmit = (cfg) => {
    setConfig(cfg);
    setIsGenerating(true); // Bật trạng thái đang load
    
    // Giả vờ gọi API tốn 3 giây
    setTimeout(() => {
      setIsGenerating(false);
      setStep("preview"); // Xong thì nhảy sang màn Preview
    }, 3000);
  };

  // 2. Giả lập luồng Máy AxiDraw đang vẽ (Tăng % mỗi giây)
  const handleStartPrinting = () => {
    setStep("printing");
    setPrintProgress(0); // Reset tiến độ về 0
    
    // Mỗi 500ms tăng tiến độ lên 5%
    const interval = setInterval(() => {
      setPrintProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          // Vẽ xong 100% thì tự động nhảy sang lịch sử
          setTimeout(() => setStep("history"), 1000); 
          return 100;
        }
        return prev + 5;
      });
    }, 500);
  };

  return (
    <div className="min-h-screen bg-[#F5F3EA] flex items-center justify-center p-6 relative">
      
      {/* Lớp phủ màn hình chờ khi AI đang sinh ảnh */}
      {isGenerating && (
        <div className="absolute inset-0 bg-black/40 z-50 flex flex-col items-center justify-center">
          <div className="bg-white p-6 rounded-xl border-4 border-[#1A1A1A] font-bold text-center animate-pulse">
            <p className="text-xl mb-2">🤖 AI ĐANG SÁNG TÁC...</p>
            <p className="text-sm text-gray-500">Vui lòng chờ khoảng 3 giây</p>
          </div>
        </div>
      )}

      {step === "create" && (
        <CreateScreen onSubmit={handleCreateSubmit} />
      )}

      {step === "preview" && (
        <PreviewScreen
          style={config?.style || "Ký hoạ"}
          // Lấy một cái ảnh ngẫu nhiên trên mạng làm ảnh giả lập
          resultImageUrl="https://picsum.photos/seed/omnidraw/400/300"
          processingTimeSec={3.2}
          onRetry={() => setStep("create")}
          onConfirm={() => setStep("confirm")}
        />
      )}

      {step === "confirm" && (
        <ConfirmScreen 
          onBack={() => setStep("preview")} 
          onStart={handleStartPrinting} 
        />
      )}

      {step === "printing" && (
        <PrintStatusScreen
          progressPercent={printProgress}
          strokesDone={Math.floor((printProgress / 100) * 248)}
          strokesTotal={248}
          etaMinutes={Math.ceil(5 - (printProgress / 100) * 5)} // Đếm ngược thời gian
          onPause={() => alert("Đã gửi lệnh tạm dừng xuống máy AxiDraw!")}
          onCancel={() => setStep("create")}
        />
      )}

      {step === "history" && (
        <HistoryScreen 
          onCreateNew={() => setStep("create")} 
        />
      )}
    </div>
  );
}