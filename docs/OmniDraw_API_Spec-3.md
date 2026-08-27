# OmniDraw — Tài liệu chuẩn giao tiếp giữa các mảng (API/Data Contract)

**Phiên bản:** v1.2 (bổ sung mục 5b — điều khiển máy vẽ start/pause/cancel, mục 5c — lấy lịch sử; kế thừa v1.1 — log CSV phục vụ nghiên cứu khoa học)
**Người giữ tài liệu (owner):** Thành viên phụ trách Giao diện & Tích hợp
**Mục đích:** Đây là "hợp đồng" bắt buộc giữa 4 mảng (AI, Xử lý ảnh/Thuật toán, Phần cứng, Giao diện). Mọi thay đổi định dạng phải được cập nhật vào file này TRƯỚC khi code, không tự ý đổi format một mình.

> Quy tắc chung: mỗi module chỉ cần quan tâm **input mình nhận** và **output mình phải trả**, không cần biết logic bên trong của module khác.

---

## 0. Sơ đồ luồng dữ liệu tổng quát

```
[Người dùng]
   │  (1) upload ảnh / nhập mô tả text
   ▼
[Giao diện] ──(2) ảnh đã chuẩn hoá──▶ [AI: sinh ảnh / style transfer]
                                            │
                                (3) ảnh kết quả (base64/URL)
                                            ▼
                              [Thuật toán: ảnh → SVG tối ưu]
                                            │
                                   (4) file SVG chuẩn
                                            ▼
                                    [Máy AxiDraw vẽ] ◀── (5b) start/pause/cancel
                                            │
                              (5) trạng thái/tiến độ (JSON)
                                            ▼
                                     [Giao diện hiển thị]
                                            │
                              (6) log số liệu (CSV) ghi song song
                                            ▼
                            [Kho dữ liệu thí nghiệm cho bài báo khoa học]

(5c) GET /api/history — giao diện gọi riêng khi vào màn Thư viện, không nằm trong luồng chính
```

Mỗi mũi tên số (1)-(6) tương ứng với một mục quy chuẩn bên dưới; (5b) và (5c) là các endpoint điều khiển/hỗ trợ đi kèm bước (5).

---

## 1. Chuẩn hoá ảnh đầu vào (Người dùng → Giao diện)

Chuẩn hoá **ngay tại tầng giao diện**, trước khi gửi đi bất kỳ đâu — không để các module khác tự xử lý theo cách riêng.

| Thuộc tính | Quy định |
|---|---|
| Định dạng file nhận | `.jpg`, `.jpeg`, `.png` only |
| Kích thước tối đa | 10 MB |
| Resize chuẩn hoá về | cạnh dài nhất = 1024px, giữ tỷ lệ khung hình |
| Màu | Chuyển sang RGB (loại bỏ alpha channel nếu có) |
| Trường hợp lỗi | Từ chối ngay tại giao diện, không gửi xuống các module khác |

**Nếu nhập bằng text (text-to-drawing):**
```json
{
  "input_type": "text",
  "prompt": "một chú mèo đang ngủ trên bậu cửa sổ",
  "style": "sketch"   // enum: "sketch" | "line_art" | "stipple" | "hatching"
}
```

---

## 2. Giao diện → AI (request sinh ảnh / style transfer)

**Endpoint gợi ý:** `POST /api/ai/generate`

**Request body:**
```json
{
  "request_id": "uuid-v4",
  "input_type": "image",              // "image" | "text"
  "image_base64": "data:image/jpeg;base64,...",  // bắt buộc nếu input_type = "image"
  "prompt": null,                      // bắt buộc nếu input_type = "text"
  "style": "sketch",                   // enum: xem mục 1
  "options": {
    "target_paper_size_mm": [210, 297] // A4 mặc định, để AI/thuật toán tính tỉ lệ
  },
  "experiment": {
    "dataset_item_id": "img_014",       // id ảnh/prompt trong bộ 30 ảnh + 15 prompt chuẩn, null nếu không phải chạy thí nghiệm
    "method_tag": "pipeline_v1"         // nhãn phương pháp đang test, dùng để so sánh baseline (vd: "canny", "xdog", "controlnet_lineart", "pipeline_v1")
  }
}
```

`request_id` **bắt buộc** — dùng xuyên suốt toàn bộ pipeline để lần theo 1 yêu cầu khi debug (xem mục 7).
`experiment` **tuỳ chọn** — chỉ điền khi đang chạy thí nghiệm chính thức cho bài báo (xem mục 6); để trống khi người dùng dùng app bình thường.

---

## 3. AI → Giao diện (kết quả sinh ảnh)

**Response từ AI service:**
```json
{
  "request_id": "uuid-v4",
  "status": "success",                 // "success" | "error"
  "result_image_base64": "data:image/png;base64,...",
  "meta": {
    "model_used": "style-transfer-v1",
    "processing_time_ms": 3200
  },
  "error": null
}
```

**Nếu lỗi:**
```json
{
  "request_id": "uuid-v4",
  "status": "error",
  "result_image_base64": null,
  "error": {
    "code": "AI_TIMEOUT",              // xem bảng mã lỗi chuẩn ở mục 8
    "message": "Model không phản hồi sau 30s"
  }
}
```

> **Quy ước ảnh:** luôn dùng `base64` (PNG) bọc trong JSON ở giai đoạn hiện tại của đề án — không dùng URL/file tạm, để tránh phát sinh thêm hạ tầng lưu trữ. Có thể nâng cấp sang URL nếu ảnh quá nặng làm chậm hệ thống về sau.

---

## 4. Thuật toán → Máy vẽ (SVG chuẩn)

Input của module thuật toán = `result_image_base64` từ mục 3.
Output bắt buộc = **file SVG** theo quy ước sau:

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     width="210mm" height="297mm"
     viewBox="0 0 210 297">
  <!-- Mỗi nét vẽ là 1 path riêng, không gộp nhiều nét vào 1 path -->
  <path d="M10,10 L50,50 ..." stroke="black" fill="none" stroke-width="0.3"/>
</svg>
```

**Quy tắc bắt buộc:**
- Đơn vị luôn là **mm**, khớp với `target_paper_size_mm` đã gửi ở mục 2.
- `fill="none"` bắt buộc — máy chỉ vẽ đường viền (stroke), không tô đặc.
- Không dùng `<text>`, `<image>`, `<use>` — chỉ `<path>`, `<line>`, `<polyline>` (các phần tử máy AxiDraw đọc trực tiếp được).
- Đặt tên file: `output_{request_id}.svg`

Lý do chọn SVG (không phải G-code/JSON tự chế): tận dụng được thư viện Python có sẵn của AxiDraw để đọc file và điều khiển máy trực tiếp, không cần viết layer chuyển đổi riêng.

> **Phục vụ đo đạc khoa học (RQ1, RQ2):** module thuật toán phải tự tính và đính kèm các chỉ số hình học ngay khi xuất SVG — xem trường `svg_metrics` ở mục 6 — thay vì để giao diện/máy vẽ tự suy ra sau.

---

## 5. Máy vẽ → Giao diện (trạng thái, tiến độ)

**Endpoint gợi ý:** `GET /api/print/status/{request_id}` (giao diện gọi định kỳ mỗi 1-2 giây — REST polling)

```json
{
  "request_id": "uuid-v4",
  "status": "printing",         // "queued" | "printing" | "paused" | "done" | "error" | "cancelled"
  "progress_percent": 42,
  "estimated_time_remaining_sec": 95,
  "error": null
}
```

**Khi hoàn thành:**
```json
{
  "request_id": "uuid-v4",
  "status": "done",
  "progress_percent": 100,
  "estimated_time_remaining_sec": 0,
  "actual_draw_time_sec": 712,    // thời gian vẽ thực tế đo được — bắt buộc khi status = "done", dùng cho log CSV ở mục 6
  "error": null
}
```

**Khi lỗi (kẹt giấy, hết mực...):**
```json
{
  "request_id": "uuid-v4",
  "status": "error",
  "progress_percent": 58,
  "error": {
    "code": "HARDWARE_PAPER_JAM",
    "message": "Phát hiện kẹt giấy tại toạ độ (120, 80)"
  }
}
```

> Khi hệ thống chạy ổn định và cần cập nhật mượt hơn (không giật khi polling), có thể nâng cấp endpoint này lên WebSocket — giữ nguyên cấu trúc JSON, chỉ đổi cách truyền.

---

## 5b. Điều khiển máy vẽ: bắt đầu / tạm dừng / huỷ (mới — v1.2)

**Bối cảnh:** giao diện đã dựng đủ 5 màn (bao gồm màn "Đang vẽ" với nút Tạm dừng/Huỷ), nhưng 3 endpoint dưới đây trước đó chưa có trong chuẩn chính thức. Bổ sung vào đây để backend (đặc biệt Phần cứng) code theo đúng, không đoán.

### Bắt đầu vẽ
Gọi khi người dùng bấm "Bắt đầu vẽ" ở màn Confirm — báo cho phần cứng thực thi file SVG đã có sẵn theo `request_id` (file đã được thuật toán xuất ra ở mục 4).

**Endpoint:** `POST /api/print/start`
```json
// Request
{ "request_id": "uuid-v4", "paper_size": "a4" }

// Response
{ "request_id": "uuid-v4", "status": "printing" }
```
Nếu máy chưa sẵn sàng/mất kết nối, trả lỗi theo cấu trúc chuẩn ở mục 8 với `code: "HARDWARE_NOT_CONNECTED"` (mã đã có sẵn, không cần thêm mã mới).

### Tạm dừng
Gọi khi bấm "Tạm dừng" ở màn Đang vẽ.

**Endpoint:** `POST /api/print/pause`
```json
// Request
{ "request_id": "uuid-v4" }

// Response
{ "request_id": "uuid-v4", "status": "paused" }
```

> **Giả định cần Phần cứng xác nhận lại:** mục này giả định máy AxiDraw hỗ trợ tạm dừng giữa chừng (dừng động cơ tạm thời, giữ nguyên vị trí bút, tiếp tục vẽ từ đúng chỗ dừng). Nếu máy/thư viện điều khiển thực tế **không** hỗ trợ tạm dừng an toàn (ví dụ dừng giữa chừng làm lệch toạ độ), báo lại để xoá hẳn endpoint này và bỏ nút "Tạm dừng" khỏi giao diện — không cố giữ một tính năng không làm được.

### Huỷ vẽ
Gọi khi bấm "Huỷ vẽ".

**Endpoint:** `POST /api/print/cancel`
```json
// Request
{ "request_id": "uuid-v4" }

// Response
{ "request_id": "uuid-v4", "status": "cancelled" }
```
Trạng thái `"cancelled"` đã được thêm vào enum `status` ở mục 5 phía trên.

---

## 5c. Lấy lịch sử tranh đã vẽ (mới — v1.2)

Phục vụ màn Thư viện (màn 5).

**Endpoint:** `GET /api/history`
```json
// Response
{
  "items": [
    {
      "id": "string",
      "title": "string",
      "style": "sketch",          // cùng enum style ở mục 1
      "time_ago": "2 ngày trước", // hoặc trả timestamp ISO 8601 để giao diện tự format, cần thống nhất thêm
      "minutes": 12,
      "thumbnail_url": "https://..."
    }
  ]
}
```

> **Cần thảo luận thêm khi có người phụ trách backend/database chính thức:**
> - `title` lấy từ đâu — người dùng tự đặt tên khi tạo tranh, hay hệ thống tự sinh (ví dụ theo `dataset_item_id`/`prompt` rút gọn)?
> - Dữ liệu lịch sử này lấy chung nguồn với log CSV ở mục 6, hay là một bảng riêng trong database ứng dụng (log CSV thiên về số liệu nghiên cứu, còn đây thiên về hiển thị cho người dùng cuối)?
> - `time_ago` nên trả dạng chuỗi đã format sẵn (như ví dụ) hay trả timestamp thô để giao diện tự tính — khuyến nghị trả timestamp ISO 8601 để tránh lệch múi giờ/ngôn ngữ giữa backend và giao diện.

---

## 6. Ghi log CSV phục vụ nghiên cứu khoa học (mới — v1.1)

**Bối cảnh:** theo nhận xét của giảng viên hướng dẫn, đề tài phải sinh ra được số liệu so sánh được cho bài báo khoa học (RQ1–RQ4), không chỉ chạy demo. Mục này định nghĩa cơ chế ghi log tự động để số liệu **tích luỹ tự nhiên trong quá trình phát triển**, không phải "chạy bù" cuối kỳ.

**Trách nhiệm:** TV4 xây dựng cơ chế ghi log ở tầng giao diện/backend (nơi tổng hợp đủ dữ liệu từ mọi module qua `request_id`). TV1/TV2/TV3 chỉ cần đảm bảo module của mình trả đủ các trường được yêu cầu ở mục 2-5 (đặc biệt là `experiment`, `svg_metrics`, `actual_draw_time_sec`).

**Thời điểm ghi:** ngay khi một `request_id` đạt trạng thái `status = "done"` hoặc `status = "error"` (ghi cả trường hợp lỗi — dữ liệu lỗi cũng có giá trị thống kê).

**File log:** `logs/experiment_log.csv`, mỗi dòng là 1 lần vẽ hoàn chỉnh (từ lúc tạo `request_id` đến lúc `done`/`error`).

**Cấu trúc cột bắt buộc:**

| Cột | Kiểu dữ liệu | Nguồn lấy | Ghi chú |
|---|---|---|---|
| `request_id` | string | mục 2 | khoá chính, dùng để đối chiếu lỗi |
| `timestamp` | ISO 8601 | giao diện tự sinh khi ghi log | |
| `dataset_item_id` | string / null | mục 2 (`experiment.dataset_item_id`) | null nếu không phải request thí nghiệm chính thức |
| `method_tag` | string / null | mục 2 (`experiment.method_tag`) | dùng để nhóm theo baseline khi phân tích (RQ1, RQ2, RQ3) |
| `input_type` | string | mục 2 | `"image"` \| `"text"` |
| `style` | string | mục 2 | phong cách vẽ đã chọn |
| `ai_processing_time_ms` | number | mục 3 (`meta.processing_time_ms`) | phục vụ chỉ số "thời gian tính toán" ở RQ1/RQ3 |
| `svg_metrics.total_path_length_mm` | number | thuật toán (mục 4) | tổng chiều dài nét — chỉ số chính RQ1 |
| `svg_metrics.pen_lift_distance_mm` | number | thuật toán (mục 4) | quãng đường nhấc bút — chỉ số chính RQ2 |
| `svg_metrics.pen_lift_count` | number | thuật toán (mục 4) | số lần nhấc bút — chỉ số RQ2 |
| `svg_metrics.optimize_time_ms` | number | thuật toán (mục 4) | thời gian tính toán tối ưu thứ tự nét — chỉ số RQ2 |
| `actual_draw_time_sec` | number | mục 5 (`actual_draw_time_sec`) | thời gian vẽ thực tế — chỉ số chính RQ1/RQ2 |
| `final_status` | string | mục 5 | `"done"` \| `"error"` |
| `error_code` | string / null | mục 5 (`error.code`) | null nếu thành công |

**Ví dụ 1 dòng log (CSV):**
```
request_id,timestamp,dataset_item_id,method_tag,input_type,style,ai_processing_time_ms,svg_metrics.total_path_length_mm,svg_metrics.pen_lift_distance_mm,svg_metrics.pen_lift_count,svg_metrics.optimize_time_ms,actual_draw_time_sec,final_status,error_code
a1b2c3d4,2026-08-26T10:15:32Z,img_014,pipeline_v1,image,sketch,3200,1840.5,320.2,18,145,712,done,
```

**Nguyên tắc bổ sung field mới:** nếu về sau cần đo thêm chỉ số nào (ví dụ phục vụ RQ4 — sai số căn giấy), thêm cột mới vào bảng trên và cập nhật mục 9 (lịch sử thay đổi tài liệu) — không tự thêm cột ngầm trong code.

---

## 7. Quy tắc dùng `request_id` để debug

- `request_id` được **giao diện sinh ra đầu tiên** (UUID v4) ngay khi người dùng bấm "Tạo tranh", và phải được **giữ nguyên xuyên suốt** qua mọi bước (AI → thuật toán → máy vẽ → trạng thái → log CSV).
- Mỗi module khi log lỗi/log hoạt động **bắt buộc ghi kèm `request_id`** — nhờ vậy khi có lỗi, chỉ cần lọc log theo 1 ID là thấy toàn bộ hành trình của yêu cầu đó qua từng mảng, biết ngay lỗi phát sinh ở đâu.
- Gợi ý: mỗi module tự ghi log hoạt động (không phải log thí nghiệm ở mục 6) ra file/console theo format:
  `[request_id] [tên module] [timestamp] message`

---

## 8. Bảng mã lỗi chuẩn (dùng chung cho tất cả module)

| Code | Ý nghĩa | Module phát sinh |
|---|---|---|
| `INPUT_INVALID_FORMAT` | Ảnh/text đầu vào sai định dạng | Giao diện |
| `AI_TIMEOUT` | Model AI không phản hồi kịp | AI |
| `AI_GENERATION_FAILED` | Model chạy nhưng lỗi nội bộ | AI |
| `VECTORIZE_FAILED` | Không chuyển được ảnh sang SVG | Thuật toán |
| `SVG_OUT_OF_BOUNDS` | Toạ độ vượt khổ giấy | Thuật toán |
| `HARDWARE_NOT_CONNECTED` | Máy không kết nối được | Phần cứng |
| `HARDWARE_PAPER_JAM` | Kẹt giấy | Phần cứng |
| `HARDWARE_OUT_OF_INK` | Hết mực/bút không xuống mực | Phần cứng |
| `UNKNOWN_ERROR` | Lỗi không xác định | Bất kỳ |

Mỗi lỗi trả về đều theo cùng cấu trúc `{ "code": "...", "message": "..." }` như ở mục 3 và 5 — không tự chế cấu trúc lỗi riêng.

---

## 9. Checklist trước khi tích hợp module vào hệ thống chung

- [ ] Module của tôi nhận đúng input theo mục tương ứng ở trên
- [ ] Module của tôi trả đúng output theo mục tương ứng (đúng tên field, đúng kiểu dữ liệu)
- [ ] Tôi có xử lý và trả lỗi đúng theo bảng mã ở mục 8 (không để crash không rõ nguyên nhân)
- [ ] Tôi có giữ và log `request_id` xuyên suốt
- [ ] Tôi có trả đủ các trường phục vụ log CSV ở mục 6 (nếu module của tôi thuộc AI/Thuật toán/Phần cứng)
- [ ] (Phần cứng) Đã xác nhận máy có hỗ trợ tạm dừng an toàn giữa chừng hay không (mục 5b) — nếu không, báo lại để bỏ endpoint `pause` và nút "Tạm dừng" khỏi giao diện
- [ ] Tôi đã test module của mình với ít nhất 1 input giả (mock) đúng chuẩn và 1 input lỗi

> Nếu cả 4 mảng đều tick đủ checklist này trước khi ráp lại, bước tích hợp sẽ chỉ còn là "cắm vào nhau", không phải sửa lỗi định dạng giữa chừng.

---

## 10. Thay đổi tài liệu

Mọi thay đổi định dạng dữ liệu phải được cập nhật vào file này và thông báo cho cả nhóm — không đổi ngầm trong code rồi để người khác tự phát hiện lúc tích hợp.

| Ngày | Người sửa | Nội dung thay đổi |
|---|---|---|
| _(điền)_ | | v1.1 — bổ sung mục 6 (log CSV cho bài báo khoa học), thêm trường `experiment` (mục 2), `svg_metrics` (mục 4), `actual_draw_time_sec` (mục 5) theo nhận xét giảng viên hướng dẫn |
| _(điền)_ | | v1.2 — bổ sung mục 5b (`POST /api/print/start`, `/pause`, `/cancel`) và mục 5c (`GET /api/history`), thêm `"cancelled"` vào enum `status` ở mục 5, thêm checklist xác nhận khả năng tạm dừng của phần cứng ở mục 9. Ba nội dung ở mục 5c (nguồn gốc `title`, quan hệ với log CSV, định dạng `time_ago`) vẫn cần chốt khi có người phụ trách backend/database chính thức |
