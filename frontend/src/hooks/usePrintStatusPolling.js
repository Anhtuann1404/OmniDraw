import { useEffect, useRef, useState } from "react";
import { getPrintStatus } from "../api/omnidraw";

/**
 * Hook polling trạng thái vẽ theo đúng cơ chế REST polling đã chốt ở API Spec mục 5.
 * Tự động gọi getPrintStatus mỗi `intervalMs`, dừng khi status = "done" | "error" | "cancelled",
 * hoặc khi component unmount / requestId đổi.
 *
 * @param {string|null} requestId - null thì không polling
 * @param {number} intervalMs - mặc định 1500ms (trong khoảng 1-2s theo khuyến nghị API Spec)
 */
export function usePrintStatusPolling(requestId, intervalMs = 1500) {
  const [statusData, setStatusData] = useState(null);
  const [pollError, setPollError] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    setStatusData(null);
    setPollError(null);
    if (!requestId) return;

    let cancelled = false;

    async function poll() {
      try {
        const data = await getPrintStatus(requestId);
        if (cancelled) return;
        setStatusData(data);

        // Dừng polling khi đã kết thúc — không cần gọi thêm request thừa
        const finished = ["done", "error", "cancelled"].includes(data.status);
        if (!finished) {
          timerRef.current = setTimeout(poll, intervalMs);
        }
      } catch (err) {
        if (cancelled) return;
        setPollError(err);
        // Vẫn thử lại theo chu kỳ khi lỗi mạng tạm thời, không dừng hẳn polling
        timerRef.current = setTimeout(poll, intervalMs);
      }
    }

    poll();

    return () => {
      cancelled = true;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [requestId, intervalMs]);

  return { statusData, pollError };
}
