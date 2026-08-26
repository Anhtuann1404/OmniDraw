# OmniDraw — React + Tailwind UI (5 màn hình)

Bộ component dựng theo đúng phong cách đã chốt với nhóm (comic/vẽ tay: nền be, panel viền đen dày,
bóng cứng đổ lệch, huy hiệu ngôi sao, wordmark "OmniDraw" font Kalam có gạch chân nét vẽ tay,
màu nhấn đỏ mực #C0392B).

## Chạy thử

```bash
npm install
npm run dev
```

Mở `http://localhost:5173` — có thanh nút nhỏ ở đáy màn hình để chuyển nhanh giữa 5 màn (chỉ phục vụ demo, xoá khi tích hợp thật).

## Cấu trúc

```
src/
  components/
    ComicPrimitives.jsx   ← các khối dùng chung: HardShadowBox, ComicButton, StarBadge,
                             StepBadge, Logo, HalftonePattern, ScreenShell
  screens/
    CreateScreen.jsx       ← Màn 1: Tạo tranh
    PreviewScreen.jsx      ← Màn 2: Xem trước kết quả AI
    ConfirmScreen.jsx      ← Màn 3: Xác nhận trước khi vẽ
    PrintStatusScreen.jsx  ← Màn 4: Theo dõi tiến độ vẽ (có mô phỏng "vẽ dần" theo %)
    HistoryScreen.jsx      ← Màn 5: Thư viện
  App.jsx                  ← nối 5 màn theo luồng demo
  index.css                ← import font Kalam + Tailwind directives
```

## Cách nối API thật (đọc kèm `OmniDraw_API_Spec.md`)

Mỗi màn nhận dữ liệu qua **props**, không tự gọi API bên trong — để dễ test độc lập và dễ thay
mock data bằng dữ liệu thật:

| Màn | Props chính cần đổ dữ liệu thật | Tương ứng mục nào trong API Spec |
|---|---|---|
| `CreateScreen` | `onSubmit({ inputType, style })` → gọi `POST /api/ai/generate` | Mục 2 |
| `PreviewScreen` | `resultImageUrl`, `style`, `modelUsed`, `processingTimeSec` | Mục 3 |
| `ConfirmScreen` | `svgPreviewUrl`, `strokeCount`, `estimatedMinutes` | Mục 4 (`svg_metrics`) |
| `PrintStatusScreen` | `progressPercent`, `strokesDone/Total`, `etaMinutes`, `machineStatus` | Mục 5 (polling `GET /api/print/status/{request_id}`) |
| `HistoryScreen` | `items: [{ id, title, style, timeAgo, thumbnailUrl }]` | — (endpoint danh sách tự định nghĩa thêm nếu cần) |

Gợi ý: thay các state demo trong `App.jsx` bằng `useEffect` + `fetch`/`axios` gọi đúng endpoint,
giữ nguyên `request_id` xuyên suốt như đã quy định trong API Spec mục 6-7.

## Icon

Dùng thư viện `lucide-react` (đã khai báo sẵn trong `package.json`) thay vì icon font, để nhẹ và
dễ tree-shake hơn khi build production.

## Ghi chú hiệu ứng "vẽ dần" ở màn 4

Hiện đang mô phỏng theo `progressPercent` (frontend-only, dùng `stroke-dashoffset`). Nếu sau này
phần cứng gửi thêm `current_path_index` thật, thay logic tính `pathDrawnOffset` trong
`PrintStatusScreen.jsx` bằng dữ liệu chính xác đó.
