import React, { useState, useEffect, useRef } from "react";
import { Clock, Plug, PauseCircle, XCircle, PlayCircle, Loader2, Pencil } from "lucide-react";
import { ScreenShell, ComicButton, ScreenTitle, HardShadowBox } from "../components/ComicPrimitives";
import { getSvgContent } from "../api/omnidraw";

/**
 * Màn 4 — Đang vẽ
 * Nếu có requestId, fetch SVG thật và hiển thị với animation clipPath theo progressPercent.
 */
export default function PrintStatusScreen({
  requestId,
  progressPercent = 58,
  etaMinutes = 5,
  machineStatus = "ok",
  isPaused = false,
  onPause,
  onResume,
  onCancel,
}) {
  const [svgText, setSvgText] = useState(null);
  const [svgLoading, setSvgLoading] = useState(false);
  const svgContainerRef = useRef(null);
  const wrapperRef = useRef(null);
  const pencilRef = useRef(null);
  const pathDataRef = useRef(null);
  const visualPercentRef = useRef(0);
  const animationRef = useRef(null);

  // Fetch SVG thật khi màn này được mount
  useEffect(() => {
    if (!requestId) return;
    setSvgLoading(true);
    getSvgContent(requestId)
      .then((res) => setSvgText(res.svgText))
      .catch(() => setSvgText(null))
      .finally(() => setSvgLoading(false));
  }, [requestId]);

  const updateDrawingState = (percent) => {
    if (!pathDataRef.current) return;
    const { paths, totalLength } = pathDataRef.current;
    if (totalLength === 0) return;

    const targetLen = (percent / 100) * totalLength;
    let activeIndex = -1;
    let lengthInActive = 0;

    for (let i = 0; i < paths.length; i++) {
      const p = paths[i];
      if (p.accumulated + p.len >= targetLen) {
        activeIndex = i;
        lengthInActive = targetLen - p.accumulated;
        break;
      }
    }

    if (activeIndex === -1 && paths.length > 0) {
      activeIndex = paths.length - 1;
      lengthInActive = paths[paths.length - 1].len;
    }

    paths.forEach((p, i) => {
      if (i < activeIndex) {
        p.el.style.stroke = "#1A1A1A";
        p.el.style.opacity = "1";
        p.el.style.strokeDasharray = "none";
        p.el.style.strokeDashoffset = "0";
      } else if (i === activeIndex) {
        p.el.style.stroke = "#1A1A1A";
        p.el.style.opacity = "1";
        p.el.style.strokeDasharray = `${p.len}`;
        p.el.style.strokeDashoffset = `${Math.max(0, p.len - lengthInActive)}`;
      } else {
        p.el.style.stroke = "#E5E2D6";
        p.el.style.opacity = "0.4";
        p.el.style.strokeDasharray = "none";
        p.el.style.strokeDashoffset = "0";
      }
    });

    if (activeIndex !== -1 && pencilRef.current && wrapperRef.current) {
      const activePath = paths[activeIndex].el;
      if (activePath.getPointAtLength) {
        try {
          const pt = activePath.getPointAtLength(lengthInActive);
          const CTM = activePath.getScreenCTM();
          if (CTM) {
            const screenPt = pt.matrixTransform(CTM);
            const containerRect = wrapperRef.current.getBoundingClientRect();
            // Điều chỉnh tọa độ để mũi ngòi bút chì chỉ đúng vào đường vẽ
            const x = screenPt.x - containerRect.left - 2; 
            const y = screenPt.y - containerRect.top - 21; 
            pencilRef.current.style.transform = `translate(${x}px, ${y}px)`;
            pencilRef.current.style.opacity = "1";
          }
        } catch (e) {}
      }
    } else if (pencilRef.current) {
      pencilRef.current.style.opacity = "0";
    }
  };

  // Khởi tạo dữ liệu path khi có svgText
  useEffect(() => {
    if (!svgContainerRef.current || !svgText) return;
    const svgEl = svgContainerRef.current.querySelector("svg");
    if (!svgEl) return;
    
    // Đợi SVG render xong
    const timer = setTimeout(() => {
      const paths = svgEl.querySelectorAll("path, polyline, line, circle, ellipse, rect");
      let totalLength = 0;
      const data = [];
      paths.forEach(el => {
        let len = 0;
        if (el.getTotalLength) {
          try {
            len = el.getTotalLength();
          } catch(e) {}
        }
        data.push({ el, len, accumulated: totalLength });
        totalLength += len;

        el.style.stroke = "#E5E2D6";
        el.style.opacity = "0.4";
        el.style.strokeDasharray = "none";
        el.style.strokeDashoffset = "0";
      });
      pathDataRef.current = { paths: data, totalLength, svgEl };
      visualPercentRef.current = 0;
      updateDrawingState(0);
    }, 100);
    return () => clearTimeout(timer);
  }, [svgText]);

  // Vòng lặp animation mượt mà
  useEffect(() => {
    if (!svgText || !pathDataRef.current) return;
    
    let lastTime = performance.now();
    const animate = (time) => {
      const dt = time - lastTime;
      lastTime = time;
      
      const target = progressPercent;
      let current = visualPercentRef.current;
      
      if (current !== target) {
        const diff = Math.abs(target - current);
        let speed = 40; // Tốc độ mặc định (rất nhanh) dùng khi mới load trang để bắt kịp %
        
        if (diff <= 5) {
          // Sử dụng làm mượt hàm mũ (exponential decay smoothing)
          // Tốc độ luôn tỷ lệ thuận với khoảng cách còn lại. Bút sẽ trượt chậm dần đều
          // khi tiến gần target, do đó không bao giờ có hiện tượng chạy vọt tới rồi đứng im.
          speed = Math.max(0.02, diff * 0.4); 
        }
        
        if (target > current) {
          current = Math.min(target, current + (speed * dt / 1000));
        } else {
          current = Math.max(target, current - (speed * dt / 1000));
        }
        visualPercentRef.current = current;
        updateDrawingState(current);
      }
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animationRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationRef.current);
  }, [progressPercent, svgText]);

  return (
    <ScreenShell patternId="pattern-print">
      {/* Canvas vẽ */}
      <div className="mb-4">
        <HardShadowBox shadowOffset={5}>
          <div ref={wrapperRef} className="h-72 flex items-center justify-center bg-[#FEFDF9] rounded-xl overflow-hidden relative">
            {svgLoading ? (
              <Loader2 size={32} className="animate-spin text-[#C0392B]" />
            ) : svgText ? (
              <>
                <style>{`#svg-printing svg { width: 100% !important; height: 100% !important; max-height: 280px; }`}</style>
                <div
                  ref={svgContainerRef}
                  id="svg-printing"
                  className="w-full h-full flex items-center justify-center p-2"
                  dangerouslySetInnerHTML={{ __html: svgText }}
                />
                <div 
                  ref={pencilRef} 
                  className="absolute top-0 left-0 text-[#1A1A1A] pointer-events-none z-10"
                  style={{ opacity: 0, transform: 'translate(0px, 0px)', transition: 'opacity 0.2s' }}
                >
                  <Pencil size={24} className="drop-shadow-md text-[#C0392B] fill-white" />
                </div>
              </>
            ) : (
              /* Fallback animation SVG tĩnh */
              <svg width="200" height="200" viewBox="0 0 220 220">
                <rect x="4" y="4" width="212" height="212" fill="none" stroke="#D8D5C8" strokeWidth="1" strokeDasharray="3,2" />
                <path d="M50,170 Q60,60 110,90 T170,40" fill="none" stroke="#E5E2D6" strokeWidth="2.2" />
                <path d="M55,185 Q95,150 145,175" fill="none" stroke="#E5E2D6" strokeWidth="2.2" />
                <circle cx="150" cy="70" r="18" fill="none" stroke="#E5E2D6" strokeWidth="2.2" />
                <path
                  d="M50,170 Q60,60 110,90 T170,40"
                  fill="none" stroke="#1A1A1A" strokeWidth="2.2"
                  strokeDasharray="240"
                  strokeDashoffset={Math.max(0, 240 - (240 * progressPercent) / 100)}
                />
                {progressPercent > 40 && (
                  <path d="M55,185 Q95,150 145,175" fill="none" stroke="#1A1A1A" strokeWidth="2.2" />
                )}
                {progressPercent > 20 && (
                  <circle cx="150" cy="70" r="18" fill="none" stroke="#C0392B" strokeWidth="2.4"
                    strokeDasharray="113" strokeDashoffset={113 - (113 * progressPercent) / 100} />
                )}
                <circle cx="150" cy="70" r="3" fill="#C0392B" />
              </svg>
            )}
          </div>
        </HardShadowBox>
      </div>

      {/* Thanh tiến độ */}
      <div className="flex items-center gap-2.5 mb-5">
        <div className="flex-1 bg-[#EDEBDF] rounded-full h-4 border-2 border-[#1A1A1A] overflow-hidden">
          <div className="h-full bg-[#C0392B] transition-all duration-500" style={{ width: `${progressPercent}%` }} />
        </div>
        <span className="text-sm font-bold text-[#1A1A1A] min-w-[38px]">{progressPercent}%</span>
      </div>

      {/* Thống kê */}
      <div className="flex gap-2.5 mb-5">
        <StatBox icon={<Clock size={18} />} label="CÒN LẠI" value={`~ ${etaMinutes} phút`} />
        <StatBox
          icon={<Plug size={18} className={machineStatus === "ok" ? "text-[#2C7A3D]" : "text-[#C0392B]"} />}
          label="MÁY VẼ"
          value={machineStatus === "ok" ? "Hoạt động tốt" : "Có sự cố"}
          tone={machineStatus === "ok" ? "success" : "error"}
        />
      </div>

      {/* Nút điều khiển */}
      <div className="flex items-center justify-between border-t-[3px] border-[#1A1A1A] pt-5">
        {isPaused ? (
          <ComicButton variant="primary" onClick={onResume}>
            <span className="flex items-center gap-1.5">
              <PlayCircle size={15} /> TIẾP TỤC
            </span>
          </ComicButton>
        ) : (
          <ComicButton variant="secondary" onClick={onPause}>
            <span className="flex items-center gap-1.5">
              <PauseCircle size={15} /> TẠM DỪNG
            </span>
          </ComicButton>
        )}
        <ComicButton variant="secondary" onClick={onCancel} className="!text-[#C0392B]">
          <span className="flex items-center gap-1.5">
            <XCircle size={15} /> HUỶ VẼ
          </span>
        </ComicButton>
      </div>
    </ScreenShell>
  );
}

function StatBox({ icon, label, value, tone = "neutral" }) {
  const toneClasses = {
    neutral: "bg-white border-[#1A1A1A] text-[#1A1A1A]",
    success: "bg-[#EAF3DE] border-[#2C7A3D] text-[#2C7A3D]",
    error: "bg-[#FBEAF0] border-[#C0392B] text-[#C0392B]",
  };
  return (
    <div className={`flex-1 text-center border-[2.5px] rounded-lg py-2.5 ${toneClasses[tone]}`}>
      <div className="flex justify-center">{icon}</div>
      <p className="text-[11px] font-bold mt-1">{label}</p>
      <p className="text-[13px] font-bold mt-0.5">{value}</p>
    </div>
  );
}