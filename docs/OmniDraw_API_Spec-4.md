# OmniDraw — Tài liệu chuẩn giao tiếp giữa các mảng (API/Data Contract)

**Phiên bản:** v1.4 (bổ sung contract cho chế độ thư tay nét đơn `input_type="handwriting"`, làm rõ cấu trúc `svg_metrics` nghiên cứu và chuẩn hóa bảng mã lỗi; kế thừa v1.3 — mục 5d lấy SVG thật; kế thừa v1.2 — điều khiển máy vẽ và lịch sử; kế thừa v1.1 — log CSV nghiên cứu)
**Người giữ tài liệu (owner):** Thành viên phụ trách Giao diện & Tích hợp
**Mục đích:** Đây là "hợp đồng" bắt buộc giữa 4 mảng (AI, Xử lý ảnh/Thuật toán, Phần cứng, Giao diện). Mọi thay đổi định dạng phải được cập nhật vào file này TRƯỚC khi code, không tự ý đổi format một mình.

> Quy tắc chung: mỗi module chỉ cần quan tâm **input mình nhận** và **output mình phải trả**, không cần biết logic bên trong của module khác.

---



## 0. Sơ đồ luồng dữ liệu tổng quát

### Luồng 1: Vẽ tranh nghệ thuật / Vector hóa ảnh (Art Mode)

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
```

### Luồng 2: Viết thư tay nét đơn thích ứng ngữ cảnh (Handwriting Mode — mới v1.4)

```
[Người dùng nhập văn bản tiếng Việt / tải file .docx, .txt]
   │
   ▼
[Giao diện] ──(2b) POST /api/ai/generate (input_type="handwriting")──▶ [Handwriting Engine]
                                                                           │
                                                              (NFD + Font Pack + Contextual Variants)
                                                                           │
                                                                           ▼
                                                              [Stroke Graph Optimizer]
                                                              (Viterbi DP trên Trellis DAG)
                                                                           │
                                                                           ▼
                                                              (4b) file SVG centerline + svg_metrics
                                                                           │
                                                                           ▼
                                                              [Giao diện Preview / Máy AxiDraw vẽ]
```

> **Lưu ý:** Chế độ viết thư tay (`handwriting`) hoạt động trực tiếp trong Handwriting Engine của backend, kết xuất trực tiếp ra SVG centerline và không bắt buộc cũng như không gọi mô hình AI sinh ảnh bitmap.

(5c) `GET /api/history` — giao diện gọi riêng khi vào màn Thư viện, không nằm trong luồng chính.
(5d) `GET /api/print/svg/{request_id}` — giao diện gọi từ màn Xác nhận trở đi để lấy nội dung SVG thật, dùng vẽ hiệu ứng "hé lộ nét theo %" trên canvas — dùng chung cho cả tranh và thư tay.

---



## 1. Chuẩn hoá ảnh đầu vào (Người dùng → Giao diện)

Chuẩn hoá **ngay tại tầng giao diện**, trước khi gửi đi bất kỳ đâu — không để các module khác tự xử lý theo cách riêng.


| Thuộc tính          | Quy định                                                    |
| ------------------- | ----------------------------------------------------------- |
| Định dạng file nhận | `.jpg`, `.jpeg`, `.png` only                                |
| Kích thước tối đa   | 10 MB                                                       |
| Resize chuẩn hoá về | cạnh dài nhất = 1024px, giữ tỷ lệ khung hình                |
| Màu                 | Chuyển sang RGB (loại bỏ alpha channel nếu có)              |
| Trường hợp lỗi      | Từ chối ngay tại giao diện, không gửi xuống các module khác |


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



## 2b. Giao diện → Backend (request tạo thư tay nét đơn — mới v1.4)

**Endpoint:** `POST /api/ai/generate`

> Đây là endpoint dùng chung cho toàn bộ quá trình sinh nội dung. Khi `input_type = "handwriting"`, backend sẽ tự động chuyển hướng request vào Handwriting Engine chuyên trách và không gọi mô hình AI sinh ảnh bitmap.

**Request body:**

```json
{
  "request_id": "uuid-v4",
  "input_type": "handwriting",
  "image_base64": null,
  "prompt": "Kính gửi bạn nam,\nThư tay mộc mạc non nước tình cảm chân thành.",
  "style": "hand_hocsinh",
  "options": {
    "target_paper_size_mm": [210, 297],
    "auto_deskew": true,
    "font": "oly",
    "letter_type": "general",
    "seed": 42
  },
  "experiment": {
    "dataset_item_id": "letter_001",
    "method_tag": "cavhc_current"
  }
}
```

**Chi tiết các trường quy định:**

| Trường | Kiểu dữ liệu | Bắt buộc | Mô tả & Ràng buộc giá trị |
| :--- | :--- | :--- | :--- |
| `request_id` | string | Có | UUID v4 dùng xuyên suốt toàn bộ pipeline để định danh và đối chiếu. |
| `input_type` | string | Có | Bắt buộc là `"handwriting"`. *(Lưu ý: backend còn hỗ trợ `"letter"` như một alias tương thích ngược; contract chính thức chuẩn hóa là `"handwriting"`).* |
| `prompt` | string / null | Có* | Nội dung văn bản Unicode tiếng Việt cần viết tay (hỗ trợ ký tự xuống dòng `\n`). Bắt buộc nếu `image_base64` là null. Nếu để trống sẽ trả lỗi `EMPTY_TEXT`. |
| `image_base64` | string / null | Không | Chuỗi base64 của file tài liệu (`.docx` hoặc `.txt`). Nếu được truyền, backend sẽ tự động giải mã và trích xuất nội dung văn bản. |
| `style` | string | Có | Enum phong cách nét viết tay hỗ trợ trong backend (`STYLE_CONFIGS`):<br>• `"hand_hocsinh"`: Chữ Học Sinh (nét đứng, nắn nót, góc nghiêng slant = 0.0)<br>• `"hand_nguoilon"`: Chữ Thảo Nghiêng (tự nhiên, mềm mại, slant = 0.20 ~ 11°)<br>• `"hand_thuphap"`: Chữ Thư Pháp (phóng khoáng, bổng trầm, slant = 0.15)<br>• `"hand_chukinhanh"`: Chữ Ký Tên (nghiêng mạnh, bay bướm, slant = 0.32 ~ 18°)<br>*(Chú thích triển khai: 4 giá trị trên là enum contract chính thức. Hiện tại backend còn fallback về `"hand_hocsinh"` đối với style không tìm thấy trong `STYLE_CONFIGS`. Đây là khoảng lệch triển khai (implementation gap) cần sửa: backend tương lai phải validate nghiêm và trả lỗi có cấu trúc, không fallback âm thầm. Tài liệu không tự thêm mã lỗi chưa tồn tại vào bảng mã lỗi binding).* |
| `options.font` | string | Không | Enum font chữ nét đơn hỗ trợ trong backend (`RENDER_PROFILES`):<br>• `"oly"`: Tiểu Học Nét Đều (pack `omnidraw_legacy`, mặc định)<br>• `"omni_casual"`: Omni Casual (pack `omni_casual`, thân thiện tự nhiên)<br>• `"thanhdam"`: Bút Máy Thanh Đậm (pack `omnidraw_legacy`, nhân đôi nét sổ)<br>• `"thuphap"`: Thư Pháp Thủy Mặc (pack `omnidraw_legacy`, móc vát đuôi)<br>• `"cursive"`: Chữ Thảo Cursive (pack `omnidraw_legacy`, nối nét liền mạch)<br>*(Lưu ý: Không hỗ trợ tải lên file TTF/OTF. Font không hợp lệ phải trả lỗi `UNSUPPORTED_FONT`, không tự ý fallback ngầm).* |
| `options.letter_type` | string | Không | Enum phân loại văn bản (`LETTER_TYPES`):<br>• `"general"`: Thư thường ngày (hỗ trợ cho mọi font pack, mặc định)<br>• `"formal"`: Văn bản trang trọng (kích hoạt chữ hoa mở đầu trang trọng K, T, C; chỉ hỗ trợ font pack legacy: `oly`, `thanhdam`, `thuphap`, `cursive`; nếu dùng với `omni_casual` sẽ trả lỗi `UNSUPPORTED_LETTER_TYPE`). |
| `options.seed` | number / null | Không | Số nguyên 32-bit không dấu trong khoảng `0` đến `4294967295` (`0 <= seed <= 0xFFFFFFFF`). Dùng để tái lập chính xác nét chữ giữa các lần render khi kiểm thử và so sánh nghiệm. Nếu không truyền, hệ thống sẽ sinh ngẫu nhiên. |
| `options.target_paper_size_mm` | [number, number] | Không | Kích thước khổ giấy đích theo trục [width, height] tính bằng mm. Mặc định `[210, 297]` (A4). |
| `options.auto_deskew` | boolean | Không | Mặc định `false`. Nếu `true`, tự động áp dụng góc bù nắn thẳng giấy khi kết xuất. |
| `experiment` | object / null | Không | Chứa `dataset_item_id` và `method_tag` phục vụ đối chuẩn thực nghiệm NCKH. |

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



## 3b. Backend → Giao diện (kết quả sinh thư tay — mới v1.4)

**Response thành công (`status = "success"`):**

```json
{
  "request_id": "uuid-v4",
  "status": "success",
  "result_image_base64": null,
  "meta": {
    "model_used": "Bio-mimetic (oly / hand_hocsinh)",
    "processing_time_ms": 14.5,
    "seed": 42,
    "letter_type": "general"
  },
  "svg_ready": true,
  "svg_metrics": {
    "total_path_length_mm": 150.186,
    "pen_lift_distance_mm": 72.982,
    "pen_lift_count": 22,
    "optimize_time_ms": 0.0,
    "skew_angle_deg": 0.0
  },
  "error": null
}
```

**Mô tả các trường:**

- `result_image_base64`: Luôn là `null` trong chế độ handwriting (không sinh ảnh bitmap).
- `meta.model_used`: Chuỗi định danh mô hình dạng `Bio-mimetic ({font} / {style})`.
- `meta.processing_time_ms`: Thời gian xử lý thực tế trên backend của request thư tay tính bằng millisecond (đo qua `perf_counter`).
- `meta.seed`: Hạt giống ngẫu nhiên được sử dụng.
- `meta.letter_type`: Loại thư được áp dụng.
- `svg_ready`: `true` xác nhận file SVG đã được ghi thành công trên máy chủ.
- `svg_metrics`: Tập chỉ số hình học trích xuất từ các nét vẽ (chi tiết tại mục 6).
- `error`: `null` khi thành công.

> **Lưu trữ và tải SVG:** File SVG hoàn chỉnh được lưu tại `backend/svg_output/output_{request_id}.svg`. Giao diện gọi endpoint `GET /api/print/svg/{request_id}` (mục 5d) để nhận chuỗi SVG thô hiển thị trên canvas hoặc nạp xuống máy vẽ.

**Nếu xảy ra lỗi (`status = "error"`):**

```json
{
  "request_id": "uuid-v4",
  "status": "error",
  "result_image_base64": null,
  "error": {
    "code": "UNSUPPORTED_CHARACTER",
    "message": "Phát hiện ký tự chưa được hỗ trợ glyph: {'œ'}",
    "characters": ["œ"]
  }
}
```
*(Nếu là lỗi `UNSUPPORTED_CHARACTER`, response trả kèm mảng `characters` chứa các ký tự vi phạm).*

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
  "actual_draw_time_sec": 712,    // thời gian chạy của tiến trình mô phỏng (simulation) dựa trên path_length / 40 mm/s; chỉ được gọi là thời gian thi công thực tế khi có máy vẽ vật lý và nguồn đo phần cứng — bắt buộc khi status = "done", dùng cho log CSV ở mục 6
  "error": null
}
```

> *(Lưu ý về `actual_draw_time_sec`: Ở giai đoạn hiện tại khi chưa kết nối máy vẽ vật lý, giá trị này phản ánh thời gian chạy của tiến trình mô phỏng phần mềm (simulation) tính theo quy ước tốc độ ngòi $40\text{ mm/s}$. Chỉ được gọi là thời gian thi công thực tế khi hệ thống kết nối máy vẽ thật và nhận số đo từ phần cứng).*


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
>
> - `title` lấy từ đâu — người dùng tự đặt tên khi tạo tranh, hay hệ thống tự sinh (ví dụ theo `dataset_item_id`/`prompt` rút gọn)?
> - Dữ liệu lịch sử này lấy chung nguồn với log CSV ở mục 6, hay là một bảng riêng trong database ứng dụng (log CSV thiên về số liệu nghiên cứu, còn đây thiên về hiển thị cho người dùng cuối)?
> - `time_ago` nên trả dạng chuỗi đã format sẵn (như ví dụ) hay trả timestamp thô để giao diện tự tính — khuyến nghị trả timestamp ISO 8601 để tránh lệch múi giờ/ngôn ngữ giữa backend và giao diện.

---



## 5d. Lấy nội dung SVG thật để hiển thị (mới — v1.3)

**Bối cảnh:** giao diện cần vẽ hiệu ứng "vẽ dần theo tiến độ thật" trên canvas lớn (từ màn Xác nhận cho tới lúc vẽ xong) — muốn vậy phải có nội dung SVG thật do thuật toán xuất ra (mục 4), không phải hình minh hoạ giả. Trước bản v1.3, không có cách nào để giao diện lấy lại được nội dung file này.

**Endpoint:** `GET /api/print/svg/{request_id}`

```json
// Response (200)
{
  "request_id": "uuid-v4",
  "svg_content": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"210mm\" height=\"297mm\" viewBox=\"0 0 210 297\"><path d=\"M10,10 L50,50 ...\" stroke=\"black\" fill=\"none\" stroke-width=\"0.3\"/></svg>"
}
```

**Quy tắc:**

- Gọi được ngay từ màn Xác nhận (mục 4 đã có file SVG rồi, không cần đợi tới lúc bấm "Bắt đầu vẽ").
- `svg_content` là toàn bộ nội dung file `output_{request_id}.svg` dạng text thô (không phải base64) — đúng chuẩn SVG đã quy định ở mục 4 (chỉ `<path>`, `<line>`, `<polyline>`, đơn vị mm).
- Nếu chưa có file SVG ứng với `request_id` (ví dụ thuật toán chưa xử lý xong), trả lỗi theo cấu trúc chuẩn mục 8 với mã `VECTORIZE_FAILED` hoặc mã phù hợp, HTTP 404.
- Giao diện dùng `svg_content` này để tự vẽ hiệu ứng "hé lộ nét theo %" bằng `stroke-dasharray`/`stroke-dashoffset` kết hợp `getTotalLength()` của trình duyệt trên từng phần tử — chính xác hơn hẳn cách ước lượng toạ độ giả trước đây, vì dựa trên đúng hình dạng nét thật.

> **Cân nhắc hiệu năng:** nếu SVG có rất nhiều nét (ảnh mật độ chi tiết cao, xem nhóm ảnh 021-030 trong bộ dữ liệu chuẩn), `svg_content` có thể khá nặng. Nếu sau này thấy chậm, có thể cân nhắc nén (gzip) ở tầng HTTP thay vì đổi cấu trúc response.

---



## 6. Ghi log CSV phục vụ nghiên cứu khoa học (mới — v1.1, chuẩn hóa v1.4)

**Bối cảnh:** theo nhận xét của giảng viên hướng dẫn, đề tài phải sinh ra được số liệu so sánh được cho bài báo khoa học (RQ1–RQ4), không chỉ chạy demo. Mục này định nghĩa cơ chế ghi log tự động để số liệu **tích luỹ tự nhiên trong quá trình phát triển**, không phải "chạy bù" cuối kỳ.

**Trách nhiệm:** TV4 xây dựng cơ chế ghi log ở tầng giao diện/backend (nơi tổng hợp đủ dữ liệu từ mọi module qua `request_id`). TV1/TV2/TV3 chỉ cần đảm bảo module của mình trả đủ các trường được yêu cầu ở mục 2-5 (đặc biệt là `experiment`, `svg_metrics`, `actual_draw_time_sec`).

**Thời điểm ghi:** ngay khi một `request_id` đạt trạng thái `status = "done"` hoặc `status = "error"` (ghi cả trường hợp lỗi — dữ liệu lỗi cũng có giá trị thống kê).

**File log:** `logs/experiment_log.csv`, mỗi dòng là 1 lần vẽ hoàn chỉnh (từ lúc tạo `request_id` đến lúc `done`/`error`).

### Phân định nhóm chỉ số (Metrics) nghiên cứu

#### Nhóm 1: Metrics hình học & tính toán (Geometric & Computational Metrics)
- `svg_metrics.total_path_length_mm`: Tổng chiều dài nét vẽ tiếp xúc mặt giấy ($mm$) — chỉ số chính RQ1.
- `svg_metrics.pen_lift_distance_mm`: Tổng quãng đường đầu bút di chuyển trên không khi nhấc bút ($mm$) — chỉ số chính RQ2.
- `svg_metrics.pen_lift_count`: Số lần nhấc đầu bút di chuyển giữa các stroke rời rạc — chỉ số chính RQ2.
- `svg_metrics.optimize_time_ms`: Thời gian tính toán thuật toán tối ưu thứ tự nét ($ms$) — chỉ số chính RQ2. *(Lưu ý: Đối với chế độ handwriting, do duy trì thứ tự nét tự nhiên theo từng từ nên `optimize_time_ms = 0.0`).*
- `svg_metrics.skew_angle_deg`: Góc nắn bù nghiêng giấy đã áp dụng (độ) — chỉ số RQ4.
- `ai_processing_time_ms`: Tổng thời gian xử lý thực tế trên backend của request ($ms$, trích xuất từ `meta.processing_time_ms`) — phục vụ chỉ số thời gian tính toán ở RQ1/RQ3.

#### Nhóm 2: Metrics phần cứng (Hardware Execution Metrics)
- `actual_draw_time_sec`: Thời gian vẽ thực tế đo được trên máy vẽ vật lý ($s$).
- **Lưu ý trung thực khoa học:** Chỉ được ghi nhận là thời gian vẽ thực tế khi có máy vẽ vật lý kết nối và nguồn đo thời gian thực từ phần cứng. Hiện tại khi chưa cắm máy vẽ thật, giá trị này trong backend print là thời gian mô phỏng phần mềm (`mock_grbl` / ước tính thời gian chạy theo tốc độ ngòi $40\text{ mm/s}$); tuyệt đối không đánh đồng thời gian mô phỏng với thời gian thi công thực tế trên máy thật.

#### Dự kiến cho thực nghiệm CA-VHC (Non-binding / Chưa triển khai trong contract hiện tại)
Các chỉ số dưới đây đang trong giai đoạn thiết kế thực nghiệm, không bắt buộc trong contract API hiện hành:
- Tỷ lệ va chạm dấu tiếng Việt (Diacritic collision rate).
- Tỷ lệ nhận dạng ký tự/từ đọc đúng (Character/Word Recognition Rate).
- Độ dài pen-up trung bình trên mỗi ký tự.
- Độ liên tục tiếp tuyến nét nối (C1 continuity metric).
- Điểm đánh giá mức độ tự nhiên từ khảo sát người dùng mù (Handwriting Turing Test).

### Cấu trúc cột log CSV bắt buộc

| Cột | Kiểu dữ liệu | Nguồn lấy | Ghi chú |
| :--- | :--- | :--- | :--- |
| `request_id` | string | mục 2 / 2b | Khóa chính, dùng để đối chiếu lỗi |
| `timestamp` | ISO 8601 | giao diện | Thời điểm ghi log |
| `dataset_item_id` | string / null | mục 2 / 2b (`experiment.dataset_item_id`) | null nếu không phải request thí nghiệm chính thức |
| `method_tag` | string / null | mục 2 / 2b (`experiment.method_tag`) | Dùng để nhóm theo baseline khi phân tích (RQ1, RQ2, RQ3) |
| `input_type` | string | mục 2 / 2b | `"image"`, `"text"`, hoặc `"handwriting"` |
| `style` | string | mục 2 / 2b | Phong cách vẽ hoặc phong cách chữ đã chọn |
| `ai_processing_time_ms` | number | mục 3 / 3b (`meta.processing_time_ms`) | Thời gian xử lý backend thực tế (ms) |
| `svg_metrics.total_path_length_mm` | number | thuật toán / engine | Tổng chiều dài nét (mm) |
| `svg_metrics.pen_lift_distance_mm` | number | thuật toán / engine | Quãng đường nhấc bút (mm) |
| `svg_metrics.pen_lift_count` | number | thuật toán / engine | Số lần nhấc bút |
| `svg_metrics.optimize_time_ms` | number | thuật toán / engine | Thời gian tối ưu thứ tự nét (ms) |
| `actual_draw_time_sec` | number / null | mục 5 (`actual_draw_time_sec`) | Thời gian vẽ thực tế (hoặc mô phỏng nếu chưa có máy) |
| `final_status` | string | mục 5 | `"done"` \| `"error"` |
| `error_code` | string / null | mục 5 (`error.code`) | null nếu thành công |

**Ví dụ 1 dòng log (CSV):**

```
request_id,timestamp,dataset_item_id,method_tag,input_type,style,ai_processing_time_ms,svg_metrics.total_path_length_mm,svg_metrics.pen_lift_distance_mm,svg_metrics.pen_lift_count,svg_metrics.optimize_time_ms,actual_draw_time_sec,final_status,error_code
a1b2c3d4,2026-08-26T10:15:32Z,img_014,pipeline_v1,image,sketch,3200,1840.5,320.2,18,145,712,done,
hw5e6f7g,2026-09-17T08:20:15Z,letter_001,cavhc_current,handwriting,hand_hocsinh,14.5,150.2,73.0,22,0.0,35,done,
```

---



## 7. Quy tắc dùng `request_id` để debug

- `request_id` được **giao diện khởi tạo ở bước đầu** (UUID v4) ngay khi người dùng bấm "Tạo tranh" hoặc "Viết thư", và phải được **giữ nguyên xuyên suốt** qua mọi bước (AI/Engine → thuật toán → máy vẽ → trạng thái → log CSV).
- Mỗi module khi log lỗi/log hoạt động **bắt buộc ghi kèm** `request_id` — nhờ vậy khi có lỗi, chỉ cần lọc log theo 1 ID là thấy toàn bộ hành trình của yêu cầu đó qua từng mảng, biết ngay lỗi phát sinh ở đâu.
- Gợi ý: mỗi module tự ghi log hoạt động (không phải log thí nghiệm ở mục 6) ra file/console theo format:
`[request_id] [tên module] [timestamp] message`

---



## 8. Bảng mã lỗi chuẩn (dùng chung cho tất cả module)

| Code | Ý nghĩa | Module phát sinh |
| :--- | :--- | :--- |
| `INPUT_INVALID_FORMAT` | Ảnh/text đầu vào sai định dạng hoặc thiếu thông tin bắt buộc | Giao diện / API Gateway |
| `EMPTY_TEXT` | Nội dung thư tay rỗng (cả prompt và file tải lên đều không có nội dung) | Handwriting Engine |
| `UNSUPPORTED_FONT` | Font chữ chỉ định không nằm trong danh sách hỗ trợ của hệ thống | Handwriting Engine |
| `INVALID_SEED` | Seed không phải số nguyên 32-bit hợp lệ trong khoảng `0..4294967295` | Handwriting Engine |
| `UNSUPPORTED_LETTER_TYPE` | Loại thư (`letter_type`) không hợp lệ hoặc không tương thích font pack | Handwriting Engine |
| `UNSUPPORTED_CHARACTER` | Văn bản chứa ký tự chưa được định nghĩa glyph nét đơn (kèm mảng `characters`) | Handwriting Engine |
| `TEXT_OVERFLOW` | Văn bản quá dài vượt ngoài giới hạn khổ giấy thiết lập sau khi ngắt dòng | Handwriting Engine |
| `SVG_OUT_OF_BOUNDS` | Nét vẽ vượt ra ngoài khổ giấy sau khi nắn nghiêng kết xuất | Thuật toán / Handwriting Engine |
| `AI_TIMEOUT` | Model AI sinh ảnh không phản hồi sau thời gian quy định | AI Core |
| `AI_GENERATION_FAILED` | Model AI sinh ảnh gặp lỗi nội bộ | AI Core |
| `VECTORIZE_FAILED` | Không chuyển đổi được ảnh raster sang định dạng vector SVG | Thuật toán vector |
| `HARDWARE_NOT_CONNECTED` | Máy vẽ chưa kết nối hoặc mất kết nối phần cứng | Phần cứng / Print API |
| `JOB_ALREADY_EXISTS` | Bản vẽ này đang trong hàng đợi hoặc đang thực thi | Phần cứng / Print API |
| `JOB_NOT_FOUND` | Không tìm thấy mã yêu cầu trong hàng đợi in | Phần cứng / Print API |
| `INVALID_STATE` | Trạng thái không hợp lệ khi gửi lệnh điều khiển (ví dụ pause khi không in) | Phần cứng / Print API |
| `HARDWARE_PAPER_JAM` | Phát hiện kẹt giấy trên máy vẽ | Phần cứng |
| `HARDWARE_OUT_OF_INK` | Hết mực hoặc bút không xuống mực | Phần cứng |
| `SVG_READ_ERROR` | Không thể đọc hoặc không tìm thấy file SVG của request_id | Backend / File IO |
| `UNKNOWN_ERROR` | Lỗi ngoại lệ chưa được phân loại | Bất kỳ |

Mỗi lỗi trả về đều theo cùng cấu trúc `{ "code": "...", "message": "..." }` (riêng `UNSUPPORTED_CHARACTER` có thêm trường `characters: [...]`) — không tự chế cấu trúc lỗi riêng.

---



## 9. Checklist trước khi tích hợp module vào hệ thống chung

### Checklist chung (Mọi module)
- [ ] Module của tôi nhận đúng input theo mục tương ứng ở trên
- [ ] Module của tôi trả đúng output theo mục tương ứng (đúng tên field, đúng kiểu dữ liệu)
- [ ] Tôi có xử lý và trả lỗi đúng theo bảng mã ở mục 8 (không để crash không rõ nguyên nhân)
- [ ] Tôi có giữ và log `request_id` xuyên suốt
- [ ] Tôi có trả đủ các trường phục vụ log CSV ở mục 6 (nếu module của tôi thuộc AI/Thuật toán/Phần cứng)
- [ ] (Phần cứng) Đã xác nhận máy có hỗ trợ tạm dừng an toàn giữa chừng hay không (mục 5b) — nếu không, báo lại để bỏ endpoint `pause` và nút "Tạm dừng" khỏi giao diện
- [ ] (Thuật toán) File SVG đã lưu lại theo đúng tên `output_{request_id}.svg` và đọc lại được qua `GET /api/print/svg/{request_id}` (mục 5d) — không chỉ gửi thẳng cho máy vẽ rồi xoá
- [ ] Tôi đã test module của mình với ít nhất 1 input giả (mock) đúng chuẩn và 1 input lỗi

### Checklist riêng cho Module Viết Thư Tay (Handwriting Mode — mới v1.4)
- [ ] Chuỗi văn bản tiếng Việt Unicode được xử lý chuẩn hóa NFD, các cụm âm ghép dấu được đặt mỏ neo và tính offset chính xác.
- [ ] Kiểm tra và validate nghiêm ngặt các tham số `font`, `style`, `letter_type`, `seed` (không fallback ngầm khi tham số sai lệch; ghi nhận hiện tại backend còn khoảng lệch triển khai: tự fallback `style` về `hand_hocsinh` thay vì báo lỗi — cần khắc phục).
- [ ] Đảm bảo tính tất định: cùng input text + cùng seed cho ra kết quả hình học và tọa độ nét tái lập nhất quán.
- [ ] Xử lý và trả lỗi có cấu trúc khi gặp ký tự chưa hỗ trợ (`UNSUPPORTED_CHARACTER`) hoặc tràn trang (`TEXT_OVERFLOW`), không tự ý đổi ký tự lạ thành `?`.
- [ ] SVG xuất xưởng tuân thủ chuẩn nét đơn centerline `<path>` với `fill="none"`, chỉ chứa geometry máy vẽ hỗ trợ.
- [ ] File SVG được lưu đúng quy ước `output_{request_id}.svg` và metrics nghiên cứu được gắn đúng `request_id` tương ứng.

---

## Phụ lục: Định hướng mở rộng hợp đồng dữ liệu (Future / Non-binding Extensions)

> [!NOTE]
> **Quy định ràng buộc:** Toàn bộ các định nghĩa dữ liệu dưới đây thuộc nhóm **Định hướng nghiên cứu mở rộng (chưa triển khai trong mã nguồn hiện hành)**.
> - Các trường, cấu trúc và tên gọi dưới đây **KHÔNG có hiệu lực contract binding** cho phiên bản v1.4 hiện tại.
> - Client và backend **không** được đưa các trường này vào validation bắt buộc của API v1.4.
> - Tên trường, kiểu dữ liệu và cấu trúc có thể thay đổi khi nhóm tiến hành triển khai thực tế.
> - **Hiện trạng xử lý văn bản dài:** Backend hiện tại xử lý trên 1 trang duy nhất và từ chối văn bản vượt quá giới hạn khổ giấy bằng mã lỗi `TEXT_OVERFLOW`.

### A. Cá nhân hóa nét chữ & Hồ sơ người viết (Writer Profile / Personalization)
- **Mục đích:** Hỗ trợ tạo chữ viết tay nét đơn mang đặc trưng phong cách của người viết cụ thể dựa trên tập mẫu trích xuất đặc trưng (few-shot personalization).
- **Request mở rộng dự kiến (`options` trong `POST /api/ai/generate`):**
```json
{
  "options": {
    "writer_profile_id": "profile_user_001_v1",
    "writer_profile": {
      "slant_mean_deg": 12.5,
      "baseline_jitter_sigma": 0.35,
      "letter_spacing_scale": 1.05,
      "ligature_probability": 0.85
    }
  }
}
```

### B. Tùy biến Bố cục, Căn lề & Cỡ chữ (Layout & Typography)
- **Mục đích:** Cho phép người dùng tùy biến hình thức bức thư phù hợp với các loại giấy và ngữ cảnh trình bày khác nhau.
- **Request mở rộng dự kiến (`options` trong `POST /api/ai/generate`):**
```json
{
  "options": {
    "font_size_pt": 14.0,
    "margins_mm": [20.0, 20.0, 20.0, 20.0],
    "line_spacing_ratio": 1.5,
    "text_alignment": "left"
  }
}
```

### C. Phân trang đa trang (Multi-page Output)
- **Mục đích:** Tự động chia tách văn bản dài thành nhiều trang vẽ SVG nối tiếp khi vượt quá dung lượng 1 trang A4.
- **Hành vi hiện tại:** Trả mã lỗi `TEXT_OVERFLOW` khi văn bản tràn trang.
- **Response mở rộng dự kiến:**
```json
{
  "request_id": "uuid-v4",
  "status": "success",
  "pagination": {
    "page_count": 2,
    "current_page": 1,
    "overflow_policy": "multi_page"
  },
  "pages": [
    {
      "page_index": 1,
      "svg_url": "/api/print/svg/uuid-v4_p1",
      "svg_metrics": {
        "total_path_length_mm": 1820.5,
        "pen_lift_count": 82
      }
    },
    {
      "page_index": 2,
      "svg_url": "/api/print/svg/uuid-v4_p2",
      "svg_metrics": {
        "total_path_length_mm": 940.2,
        "pen_lift_count": 41
      }
    }
  ]
}
```

### D. Telemetry phản hồi phần cứng thời gian thực (Hardware Telemetry)
- **Mục đích:** Phản hồi tiến độ thi công thực tế từ máy vẽ vật lý đến từng nét vẽ SVG, thay thế cho mô phỏng phần mềm hiện tại.
- **Hành vi hiện tại:** `GET /api/print/status` trả về `actual_draw_time_sec` và `progress_percent` dựa trên tính toán mô phỏng từ backend ở vận tốc giả định 40 mm/s.
- **Response mở rộng dự kiến (`GET /api/print/status`):**
```json
{
  "request_id": "uuid-v4",
  "status": "drawing",
  "telemetry": {
    "current_stroke_index": 142,
    "total_strokes": 520,
    "pen_state": "DOWN",
    "realtime_velocity_mm_s": 38.5,
    "head_position_xy_mm": [105.2, 148.0],
    "buffer_underrun_count": 0
  }
}
```

---

## 10. Thay đổi tài liệu

Mọi thay đổi định dạng dữ liệu phải được cập nhật vào file này và thông báo cho cả nhóm — không đổi ngầm trong code rồi để người khác tự phát hiện lúc tích hợp.

| Ngày | Người sửa | Nội dung thay đổi |
| :--- | :--- | :--- |
| *26/8* | Tuấn | v1.1 — bổ sung mục 6 (log CSV cho bài báo khoa học), thêm trường `experiment` (mục 2), `svg_metrics` (mục 4), `actual_draw_time_sec` (mục 5) theo nhận xét giảng viên hướng dẫn |
| *28/8* | Tminh | v1.2 — bổ sung mục 5b (`POST /api/print/start`, `/pause`, `/cancel`) và mục 5c (`GET /api/history`), thêm `"cancelled"` vào enum `status` ở mục 5, thêm checklist xác nhận khả năng tạm dừng của phần cứng ở mục 9. Ba nội dung ở mục 5c (nguồn gốc `title`, quan hệ với log CSV, định dạng `time_ago`) vẫn cần chốt khi có người phụ trách backend/database chính thức |
| *29/8* | Tuấn | v1.3 — bổ sung mục 5d (`GET /api/print/svg/{request_id}`) để giao diện lấy nội dung SVG thật, phục vụ canvas hiển thị hiệu ứng "vẽ dần theo %" từ màn Xác nhận trở đi; thêm checklist yêu cầu Thuật toán lưu lại file SVG đọc được qua endpoint này |
| *17/9* | Tuấn | v1.4 — bổ sung contract cho chế độ thư tay nét đơn (mục 2b: `input_type="handwriting"`, mục 3b: response thư tay), phân định rõ ràng metrics hình học tính toán và thời gian phần cứng thực tế, chuẩn hóa bảng mã lỗi đầy đủ từ backend, bổ sung checklist handwriting và phụ lục định hướng mở rộng non-binding (Writer Profile, Layout, Multi-page, Telemetry) |
