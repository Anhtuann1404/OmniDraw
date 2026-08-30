import { apiRequest, generateRequestId } from "./client";
import { MOCK_MODE } from "./config";

// ============================================================================
// CÁC HÀM ĐÃ CÓ TRONG OmniDraw_API_Spec.md — dùng thẳng khi backend sẵn sàng
// ============================================================================

/**
 * Mục 2 của API Spec — Giao diện → AI (sinh ảnh / style transfer)
 */
export async function generateArt({ inputType, imageBase64, prompt, style, experiment }) {
  const requestId = generateRequestId();

  if (MOCK_MODE) {
    await delay(1200);
    return {
      requestId,
      resultImageBase64: inputType === "image" ? imageBase64 : "https://via.placeholder.com/400x300.png?text=Mock+Text+Result", 
      meta: { modelUsed: "style-transfer-v1 (mock)", processingTimeMs: 1200 },
    };
  }

  const payload = {
    request_id: requestId,
    input_type: inputType,
    image_base64: inputType === "image" ? imageBase64 : null,
    prompt: inputType === "text" ? prompt : null,
    style,
    options: { target_paper_size_mm: [210, 297] },
    experiment: experiment
      ? { dataset_item_id: experiment.datasetItemId ?? null, method_tag: experiment.methodTag ?? null }
      : { dataset_item_id: null, method_tag: null },
  };

  const data = await apiRequest("/api/ai/generate", { method: "POST", body: payload });

  return {
    requestId: data.request_id,
    resultImageBase64: data.result_image_base64,
    meta: { modelUsed: data.meta?.model_used, processingTimeMs: data.meta?.processing_time_ms },
  };
}

/**
 * Mục 5 của API Spec — Máy vẽ → Giao diện (trạng thái/tiến độ)
 */
export async function getPrintStatus(requestId) {
  if (MOCK_MODE) {
    await delay(300);
    return mockProgressStatus(requestId);
  }

  const data = await apiRequest(`/api/print/status/${requestId}`, { method: "GET" });

  return {
    status: data.status,
    progressPercent: data.progress_percent,
    etaSec: data.estimated_time_remaining_sec,
    actualDrawTimeSec: data.actual_draw_time_sec ?? null,
    error: data.error,
  };
}

// ============================================================================
// ĐỀ XUẤT ENDPOINT MỚI
// ============================================================================

export async function startPrint({ requestId, paperSize = "a4" }) {
  if (MOCK_MODE) {
    await delay(400);
    return { requestId, status: "printing" };
  }
  const data = await apiRequest("/api/print/start", {
    method: "POST",
    body: { request_id: requestId, paper_size: paperSize },
  });
  return { requestId: data.request_id, status: data.status };
}

export async function pausePrint(requestId) {
  if (MOCK_MODE) {
    await delay(200);
    return { requestId, status: "paused" };
  }
  const data = await apiRequest("/api/print/pause", { method: "POST", body: { request_id: requestId } });
  return { requestId: data.request_id, status: data.status };
}

// BỔ SUNG: Hàm tiếp tục vẽ
export async function resumePrint(requestId) {
  if (MOCK_MODE) {
    await delay(200);
    return { requestId, status: "printing" };
  }
  const data = await apiRequest("/api/print/resume", { method: "POST", body: { request_id: requestId } });
  return { requestId: data.request_id, status: data.status };
}

export async function cancelPrint(requestId) {
  if (MOCK_MODE) {
    await delay(200);
    return { requestId, status: "cancelled" };
  }
  const data = await apiRequest("/api/print/cancel", { method: "POST", body: { request_id: requestId } });
  return { requestId: data.request_id, status: data.status };
}

export async function getHistory() {
  if (MOCK_MODE) {
    await delay(300);
    return [
      { id: "1", title: "Mèo ngủ", style: "Ký hoạ", timeAgo: "2 ngày trước", minutes: 12, thumbnailUrl: null },
      { id: "2", title: "Phong cảnh núi", style: "Line art", timeAgo: "5 ngày trước", minutes: 10, thumbnailUrl: null },
      { id: "3", title: "Chân dung", style: "Chấm bi", timeAgo: "1 tuần trước", minutes: 12, thumbnailUrl: null },
    ];
  }
  const data = await apiRequest("/api/history", { method: "GET" });
  return data.items.map((it) => ({
    id: it.id,
    title: it.title,
    style: it.style,
    timeAgo: it.time_ago,
    minutes: it.minutes,
    thumbnailUrl: it.thumbnail_url,
  }));
}

export async function logExperimentData(logPayload) {
  const data = await apiRequest("/api/log/experiment", { 
    method: "POST", 
    body: logPayload 
  });
  return data;
}

// ============================================================================
// Helpers nội bộ cho mock mode
// ============================================================================

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const mockStartTimes = new Map();

function mockProgressStatus(requestId) {
  if (!mockStartTimes.has(requestId)) mockStartTimes.set(requestId, Date.now());
  const elapsedSec = (Date.now() - mockStartTimes.get(requestId)) / 1000;
  const totalMockSec = 20; 
  const percent = Math.min(100, Math.round((elapsedSec / totalMockSec) * 100));

  if (percent >= 100) {
    return { status: "done", progressPercent: 100, etaSec: 0, actualDrawTimeSec: Math.round(totalMockSec), error: null };
  }
  return {
    status: "printing",
    progressPercent: percent,
    etaSec: Math.round(totalMockSec - elapsedSec),
    actualDrawTimeSec: null,
    error: null,
  };
}