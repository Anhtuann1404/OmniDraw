# Graph Report - OmniDraw  (2026-09-20)

## Corpus Check
- 65 files · ~126,392 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: .stl 6, (none) 3, .css 1)

## Summary
- 953 nodes · 1651 edges · 89 communities (61 shown, 28 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 185 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dcccb89e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- App.jsx
- engine.py
- segments_intersect
- BÁO CÁO AUDIT KIẾN TRÚC: TRELLIS DAG / CA-VHC HIỆN TẠI (BƯỚC A)
- package.json
- api_generator.py
- APIResponse
- build_svg
- extract_strokes
- handwriting/__init__.py
- extract_strokes_stipple
- process
- TraceStroke
- OmniDraw — Đặc Tả Nghiên Cứu & Thiết Kế Kỹ Thuật Lõi CA-VHC
- path_optimizer.py
- 5. Kế Hoạch Benchmark Định Lượng
- test_seed_determinism
- generate_accents
- OmniDraw — Tài liệu chuẩn giao tiếp giữa các mảng (API/Data Contract)
- test_ca_vhc_metrics.py
- GlyphVariant
- _run_self_check
- test_handwriting_validation.py
- compute_diacritic_clearance
- 1. Ba Câu Hỏi Nghiên Cứu & Giả Thuyết Khoa Học
- 8. Kiến trúc Hàm Chi Phí Mới (Cost Architecture)
- test_font_omitted_defaults_to_oly
- generate_handwriting_svg
- What You Must Do When Invoked
- _text_to_strokes_impl
- 3. Thiết kế Thực thể `DiacriticCandidate`
- 6. Quy trình Sinh Ứng viên Trạng thái & Kiểm soát Cắt tỉa (Pruning)
- test_invalid_style_rejected_without_silent_fallback
- OmniDraw — CA-VHC Diacritic-Aware State Architecture
- 9. Phương trình Truy hồi Viterbi DP Mới
- OmniDraw — Đặc tả Kỹ thuật Dataset Chữ viết tay (Handwriting Dataset Specification)
- find_unsupported_characters
- test_target_paper_size_omitted_defaults_to_a4
- metrics_evaluator.py
- resolve_font
- main.py
- run.sh
- run_backend.sh
- 3. Định Nghĩa Chính Xác Ba Baseline Đối Chứng
- nearest_neighbor_order
- 13. Hợp đồng Tương thích Ngược (Backward Compatibility Contract)
- optimize_word_dag
- 2. Backlog chi tiết Sprint 1–2 (Kế hoạch hành động 2 tuần tới)
- test_curvature_cost_formula
- graphify reference: extra exports and benchmark
- _stroke_min_distance
- test_empty_handwriting_text_rejected
- test_art_mode_invalid_style_rejected_without_side_effects
- users_yingjunn_study_nckh_2026_2027_omnidraw_test_handwriting_py
- _auto_isolate_background
- 5. Thiết kế Thực thể `CompositionState` & Cơ chế Chuyển đổi Tọa độ
- Giai đoạn 2 — Phát triển song song theo 4 đường chạy
- 2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)
- test_formal_letter_type_compatibility
- test_invalid_target_paper_size
- test_direct_engine_style_strict_validation
- graphify reference: query, path, explain
- OmniDraw — Roadmap
- 5. Lộ trình theo các Cổng Quyết định (Decision Gates & Milestones)
- OmniDraw — React + Tailwind UI (5 màn hình)
- OmniDraw — Danh sách 15 Prompt Test (Chuẩn Xứ Lý AxiDraw v2.0)
- test_valid_handwriting_request
- test_invalid_input_type_rejected
- test_invalid_requests_do_not_trigger_cleanup_or_side_effects
- Giai đoạn 1 — Khảo sát & Nền tảng
- Giai đoạn 3 — Tích hợp hệ thống
- 4.1 Benchmark Thực nghiệm Định lượng & Ablation Study — P0
- 6. Chi tiết các giai đoạn triển khai (Giai đoạn 1 đến Giai đoạn 4)
- handwriting
- handwriting_font_packs
- handwriting_font_packs_geometry
- handwriting_font_packs_legacy
- handwriting_font_packs_omni_casual
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rules/graphify.md
- extraction-spec.md
- workflows/graphify.md
- test_art_mode_invalid_input_graceful

## God Nodes (most connected - your core abstractions)
1. `optimize_word_dag()` - 24 edges
2. `_run_self_check()` - 24 edges
3. `generate_accents()` - 22 edges
4. `GlyphVariant` - 22 edges
5. `eval_transition()` - 22 edges
6. `_text_to_strokes_impl()` - 20 edges
7. `App()` - 20 edges
8. `bridge_collision_cost()` - 19 edges
9. `process()` - 19 edges
10. `OmniDraw — CA-VHC Diacritic-Aware State Architecture` - 19 edges

## Surprising Connections (you probably didn't know these)
- `10.1 Trách nhiệm của Renderer trong Bước C` --references--> `generate_accents()`  [INFERRED]
  docs/07_diacritic_aware_state_design.md → backend/handwriting/engine.py
- `7. Chiến lược Mỏ neo P0 (Anchor Strategy)` --references--> `generate_accents()`  [INFERRED]
  docs/07_diacritic_aware_state_design.md → backend/handwriting/engine.py
- `4. Nhật ký tiến độ theo ngày (Progress Log by Date)` --references--> `GlyphVariant`  [INFERRED]
  docs/03_current-task.md → backend/handwriting/engine.py
- `3. Bản đồ Anchor và Offset` --references--> `GlyphVariant`  [INFERRED]
  docs/06_audit_trellis_dag_report.md → backend/handwriting/engine.py
- `3.1. Baseline 1: Static Glyphs Renderer (B1)` --references--> `build_ligature_bridge()`  [INFERRED]
  docs/05_ca_vhc_research_spec.md → backend/handwriting/engine.py

## Import Cycles
- None detected.

## Communities (89 total, 28 thin omitted)

### Community 0 - "App.jsx"
Cohesion: 0.05
Nodes (69): 2.7 Giao diện, Strict Validation & Tích hợp (Đường chạy TV4), Cách nối API thật (đọc kèm `OmniDraw_API_Spec.md`), Đã nối sẵn API client (mock mode), AuthError, clearToken(), delay(), login(), logout() (+61 more)

### Community 1 - "engine.py"
Cohesion: 0.17
Nodes (20): can_ligature(), OmniDraw - Module Viết Thư Tay Tự Động (Bio-Inspired Vietnamese Handwriting…, Fallback tương thích ngược., backend_handwriting_font_packs, bz(), make_arch(), make_ascender_loop(), make_descender_loop() (+12 more)

### Community 2 - "segments_intersect"
Cohesion: 0.10
Nodes (19): point_on_segment(), Kiểm tra điểm p có nằm trên đoạn thẳng [a, b] trong hệ tọa độ 2D (khi p, a, b…, Kiểm tra giao nhau giữa 2 đoạn thẳng [p1, p2] và [q1, q2] bền vững: - Sử dụng…, segments_intersect(), 2.2. Ánh Xạ Sang Tọa Độ Thế Giới & Quy Đổi Kích Thước Chữ, 2.3. Quyết Định Chuyển Trạng Thái: Nối Nét hay Nhấc Bút, 2.4. Hàm Mục Tiêu $J$ & Chi Phí Chuyển Tiếp, 2.5. Bảng Chi Tiết Thành Phần Hàm Mục Tiêu $J$ (+11 more)

### Community 3 - "BÁO CÁO AUDIT KIẾN TRÚC: TRELLIS DAG / CA-VHC HIỆN TẠI (BƯỚC A)"
Cohesion: 0.15
Nodes (13): audit_vietnamese_lowercase_accents(), Kiểm định bộ dấu tiếng Việt viết thường cho một Font Pack. Kiểm tra 12 họ…, 1. Bảng danh mục Tests hiện có liên quan đến Handwriting & DAG, 1. Luồng xử lý dấu từ Unicode đến SVG Render, 1. Sơ đồ luồng thực thi (End-to-End Call Chain), 3. Bản đồ Anchor và Offset, B. Current Call Graph, BÁO CÁO AUDIT KIẾN TRÚC: TRELLIS DAG / CA-VHC HIỆN TẠI (BƯỚC A) (+5 more)

### Community 4 - "package.json"
Cohesion: 0.08
Nodes (24): dependencies, lucide-react, react, react-dom, devDependencies, autoprefixer, postcss, tailwindcss (+16 more)

### Community 5 - "api_generator.py"
Cohesion: 0.12
Nodes (22): ExperimentLog, load_prompts_from_docx(), log_to_csv(), main(), process_all_prompts(), PromptData, Đọc file DOCX, trích xuất 15 prompt, OmniDraw — AI Core API Generator Phần mềm: Gọi API sinh ảnh cho 15 prompt thử… (+14 more)

### Community 6 - "APIResponse"
Cohesion: 0.11
Nodes (19): APIResponse, call_openai_image_api(), Gọi OpenAI Image API (DALL-E 3), generate_ai_image(), Art Mode text-to-drawing với style='sketch' không bị handwriting validation…, Art Mode text-to-drawing với style='line_art' không bị handwriting validation…, Art Mode khi style là None hoặc thiếu không bị crash ngoài kiểm soát (tự động…, Art Mode khi style omitted hoặc None phải tự động resolve thành 'sketch' và… (+11 more)

### Community 7 - "build_svg"
Cohesion: 0.18
Nodes (15): build_svg(), _catmull_rom_cubic_segments(), get_render_bounds_px(), polyline_to_path_d(), px_to_mm(), Quy doi pixel -> mm. Neu co truyen paper_size_mm, CLAMP ket qua ve dung trong…, Xoay toa do 2D quanh tam 'center' mot goc angle_deg (do). Dung de tu dong bu…, Trả về các segment Cubic Bézier (p1, c1, c2, p2) dùng đúng công thức hiện tại… (+7 more)

### Community 8 - "extract_strokes"
Cohesion: 0.20
Nodes (10): extract_strokes(), extract_strokes_hatching(), extract_strokes_line_art(), [NANG CAP TOAN DIEN v2] Style sketch (Ky hoa chi danh bong): Tao cam giac chan…, Ham dung chung: resize an toan + chuyen grayscale, tra ve (gray, (w,h))., [NANG CAP] Style line_art: 1. Dung Bilateral Filter thay vi Gaussian: Giup lam…, [NANG CAP] Style hatching: quet cac duong thang song song theo 3 huong de tao…, _resize_and_gray() (+2 more)

### Community 9 - "handwriting/__init__.py"
Cohesion: 0.14
Nodes (16): backend_handwriting, backend_handwriting_engine, OmniDraw - Handwriting Engine Compatibility Shim…, Nội dung thư tay không thể đặt trọn vẹn trong một trang., Nội dung chứa ký tự chưa có glyph trong Font Pack đang chọn., Loại văn bản / thư (letter_type) không được hỗ trợ hoặc không tương thích font…, Xác thực letter_type và kiểm tra tính tương thích với font_pack_id. -…, resolve_letter_type() (+8 more)

### Community 10 - "extract_strokes_stipple"
Cohesion: 0.12
Nodes (21): _extract_stipple_contours(), _extract_stipple_dots_poisson(), extract_strokes_stipple(), Lop 1: Trich xuat cac duong contour vector lien tuc (Continuous Line Contours)…, Lop 2: Trich xuat cac hat sac do (Tone & Shading Dots) bang phuong phap…, [HYBRID TWO-LAYER STIPPLING] Ket hop giua vector contours sac net va halftone…, cv2, _create_synthetic_portrait() (+13 more)

### Community 11 - "process"
Cohesion: 0.18
Nodes (10): chain_strokes(), decode_image(), log_msg(), make_error(), process(), Ham xu ly chinh cua module Thuat toan, khop input/output muc 1-3-4-6 cua API…, Noi cac stroke co diem dau/cuoi gan nhau (trong ban kinh snap_dist) thanh 1 net…, Log dung format chuan muc 7: [request_id] [ten module] [timestamp] message (+2 more)

### Community 12 - "TraceStroke"
Cohesion: 0.21
Nodes (7): StructuredRenderResult, Any, Cấu trúc dữ liệu đại diện cho một nét vẽ kèm thông tin ngữ cảnh CA-VHC. Hỗ trợ…, TraceStroke, NamedTuple, Kiểm tra hợp đồng dữ liệu của TraceStroke và StructuredRenderResult., test_trace_stroke_and_render_result_contract()

### Community 13 - "OmniDraw — Đặc Tả Nghiên Cứu & Thiết Kế Kỹ Thuật Lõi CA-VHC"
Cohesion: 0.25
Nodes (7): 6. Ma Trận Truy Vết Khoa Học (Traceability Matrix), 7. Kế Hoạch Triển Khai Tiếp Theo (Chia 5 PR Nhỏ), Kết Luận & Hành Động Tiếp Theo, OmniDraw — Đặc Tả Nghiên Cứu & Thiết Kế Kỹ Thuật Lõi CA-VHC, PR2: Chuẩn Hóa và Khóa Ba Baseline Đối Chứng (B1, B2, B3), PR4: Delayed-Stroke Ordering Optimizer, PR5: Benchmark Runner, Automated Reporting & Ablation Study

### Community 14 - "path_optimizer.py"
Cohesion: 0.20
Nodes (13): compute_svg_metrics(), dist(), _edge_cost(), or_opt_improve(), polyline_length(), OmniDraw - Module Thuat toan: Anh -> SVG toi uu duong ve…, Tinh cac chi so bat buoc cho log CSV khoa hoc (muc 6): - total_path_length_mm :…, 2-Opt dao nguoc doan de go cac duong nhac but cat cheo nhau (crossing edges). #… (+5 more)

### Community 15 - "5. Kế Hoạch Benchmark Định Lượng"
Cohesion: 0.29
Nodes (7): 5.1. Hai Tập Ngữ Liệu: Development Corpus & Holdout Corpus, 5.2. Môi Trường Thực Nghiệm & Giao Thức Đo Đạc (Benchmark Protocol), 5.3. Bảy Chỉ Số Đo Đạc Tối Thiểu (Minimum Metrics Set), 5.4. Quy Định Lưu Trữ Dữ Liệu Benchmark, 5.5. Bảng Tiêu Chí Đánh Giá Thống Nhất (Acceptance Thresholds), 5. Kế Hoạch Benchmark Định Lượng, Giao thức đo đạc:

### Community 16 - "test_seed_determinism"
Cohesion: 0.40
Nodes (5): Cùng text và cùng seed phải cho metrics giống nhau hoàn toàn., test_seed_determinism(), 14.1 Danh mục Kiểm thử Đơn vị & Hồi quy (Unit & Regression Tests), 14.2 Bộ Đo đạc Thực nghiệm Đối chuẩn (Benchmark & Ablation Study — Pha sau), 14. Chiến lược Kiểm thử cho Bước C (Test Strategy for Step C)

### Community 17 - "generate_accents"
Cohesion: 0.22
Nodes (11): generate_accents(), Sinh các nét dấu Tiếng Việt (Single-stroke Accents) căn chỉnh tự động: - Bố trí…, 2. Phân loại hai nhóm dấu tiếng Việt trong mã nguồn, `DAG-01`: Diacritics are Attached Exclusively Post-DAG (Hậu kỳ tách rời), `DAG-02`: Zero Runtime Diacritic Collision Checking in Transition Evaluation, `DAG-04`: Rigid Procedural Anchors Without Per-Glyph Anchor Metadata, `DAG-05`: Delayed-Stroke Ordering is Static Word-End Append, `DAG-06`: Monolithic Engine File with Embedded Inline Self-Check Suite (+3 more)

### Community 18 - "OmniDraw — Tài liệu chuẩn giao tiếp giữa các mảng (API/Data Contract)"
Cohesion: 0.06
Nodes (32): 0. Sơ đồ luồng dữ liệu tổng quát, 10. Thay đổi tài liệu, 1. Chuẩn hoá ảnh đầu vào (Người dùng → Giao diện), 2b. Giao diện → Backend (request tạo thư tay nét đơn — mới v1.4), 3. AI → Giao diện (kết quả sinh ảnh), 3b. Backend → Giao diện (kết quả sinh thư tay — mới v1.4), 4. Thuật toán → Máy vẽ (SVG chuẩn), 5. Máy vẽ → Giao diện (trạng thái, tiến độ) (+24 more)

### Community 19 - "test_ca_vhc_metrics.py"
Cohesion: 0.19
Nodes (12): Hàm nội bộ dành cho nghiên cứu CA-VHC: Trích xuất strokes kèm Structured Render…, text_to_strokes_structured(), math, Unit tests for PR1: CA-VHC Metrics, Structured Render Trace, and Benchmark…, So sánh đầu ra của text_to_strokes() và text_to_strokes_structured().strokes…, Kiểm tra trên tập từ mẫu tiếng Việt với font cursive, cả 4 loại nhãn nét…, Xử lý an toàn các trường hợp biên: chuỗi rỗng, 1 ký tự, nhiều dấu liên tiếp., Kịch bản không va chạm: chữ chuẩn không có cầu nối cắt qua dấu. (+4 more)

### Community 20 - "GlyphVariant"
Cohesion: 0.18
Nodes (10): GlyphVariant, Biến thể hình học (Alloglyph Node) trong đồ thị DAG., TV4 — Project Lead & Handwriting / CA-VHC Composition Lead, Log, OmniDraw — Progress & Decisions Log, 16. Bảng Kiểm Tra Tiêu Chí Hoàn Thành Bước B (Definition of Done Checklist), 2.1 Nguyên tắc bất biến đối với `GlyphVariant`, 2.2 Kiến trúc Lai được lựa chọn chính thức (+2 more)

### Community 21 - "_run_self_check"
Cohesion: 0.17
Nodes (9): get_glyph_variants(), Kiểm tra tự động module viết thư tay với các kiểu nét đã đăng ký., Tách nét chính (primary_strokes) và nét phụ (secondary_strokes) của glyph: - i,…, Sinh 1-3 biến thể hình học cho ký tự trên đồ thị DAG: - std: Nét chuẩn…, _run_self_check(), split_glyph_strokes(), 2.1. Không Gian Trạng Thái Tại Vị Trí Ký Tự, `DAG-07`: Fixed Heuristic $C_{\text{legibility}}$ Without Readability Metric Foundation (+1 more)

### Community 22 - "test_handwriting_validation.py"
Cohesion: 0.06
Nodes (31): Font không nằm trong RENDER_PROFILES phải trả lỗi UNSUPPORTED_FONT., letter_type không nằm trong LETTER_TYPES phải trả lỗi UNSUPPORTED_LETTER_TYPE., Seed phải là số nguyên không âm trong khoảng [0, 4294967295], không chấp nhận…, Truyền key 'font' nhưng value là null hoặc sai kiểu dữ liệu phải trả lỗi…, Nếu không truyền letter_type trong options, hệ thống dùng default 'general' và…, Truyền key 'letter_type' nhưng value là null hoặc sai kiểu dữ liệu phải trả lỗi…, Thiếu trường 'style' trong request handwriting phải trả structured error…, style = null hoặc sai datatype trong request handwriting phải trả structured… (+23 more)

### Community 23 - "compute_diacritic_clearance"
Cohesion: 0.13
Nodes (18): compute_diacritic_clearance(), count_bridge_diacritic_collisions(), point_to_segment_distance(), Tính khoảng cách Euclide ngắn nhất từ điểm p đến đoạn thẳng nối từ a đến b. Xử…, Kiểm tra va chạm giao cắt hình học giữa hai đoạn thẳng [p1, p2] và [q1, q2].…, Tính khoảng cách Euclide ngắn nhất giữa hai đoạn thẳng [p1, p2] và [q1, q2].…, Đếm số cặp (bridge_stroke, diacritic_stroke) có ít nhất một giao cắt hoặc chạm…, Tính khoảng cách Euclide ngắn nhất giữa bất kỳ đoạn thẳng nào của bridge_stroke… (+10 more)

### Community 24 - "1. Ba Câu Hỏi Nghiên Cứu & Giả Thuyết Khoa Học"
Cohesion: 0.40
Nodes (5): 1.1. RQ1: Nối Nét, Quãng Đường Pen-up và Số Lần Nhấc Bút, 1.2. RQ2: Tránh Va Chạm Giữa Dấu Tiếng Việt, Thân Chữ và Nét Nối, 1.3. RQ3: Hiệu Năng Tính Toán & Tính Khả Thi Thi Công Trên Máy Vẽ, 1. Ba Câu Hỏi Nghiên Cứu & Giả Thuyết Khoa Học, Nguyên tắc phân loại đánh giá kết quả (Evaluation Priority Rule)

### Community 25 - "8. Kiến trúc Hàm Chi Phí Mới (Cost Architecture)"
Cohesion: 0.40
Nodes (5): 8.1.1 Phân biệt Hình thức: Geometry Metric (Đơn vị vật lý mm) vs. Cost Metric (Vô hướng chuẩn hóa), 8.1 State Cost $C_{\text{state}}(s)$ — Lãnh địa TV4, 8.2 Transition Cost $J_{\text{transition}}(s_{\text{prev}}, s_{\text{curr}})$ — Shared TV2 & TV4, 8.3 Cải tiến then chốt trong $C_{\text{bridge\_collision}}$ (Transition Bridge Collision), 8. Kiến trúc Hàm Chi Phí Mới (Cost Architecture)

### Community 27 - "generate_handwriting_svg"
Cohesion: 0.09
Nodes (27): argparse, _encode_jpeg(), inspect_paper(), _normalize_paper_rect(), OmniDraw - Module Thị giác Máy tính: Giám sát Giấy & Camera (Closed-Loop…, Chuyển ảnh OpenCV BGR thành chuỗi Base64 Data URL để UI render trực tiếp., Ponytail runnable check: assert synthetic paper detection precision., Chuẩn hóa góc nghiêng [-45, 45] độ và cạnh dài/cạnh ngắn. (+19 more)

### Community 28 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 29 - "_text_to_strokes_impl"
Cohesion: 0.15
Nodes (22): analyze_text_contexts(), apply_bio_variation(), build_ligature_bridge(), group_nfd_graphemes(), normalize_vietnamese_final_uy_tone(), Context Analyzer v1 (CA-VHC): Phân tích ngữ cảnh vị trí của từng grapheme không…, Chọn nét hình học, độ rộng và tâm của glyph theo ngữ cảnh tài liệu, ngữ cảnh từ…, Áp dụng các lớp biến dạng sinh học (Bio-mimetic Variation): 1. Slant affine… (+14 more)

### Community 30 - "3. Thiết kế Thực thể `DiacriticCandidate`"
Cohesion: 0.50
Nodes (4): 3.1 Cấu trúc dữ liệu ý niệm (Conceptual Schema), 3.2 Ý nghĩa chi tiết của từng trường dữ liệu & Quy ước Hệ Tọa độ, 3.3 Phân định Dấu Cấu trúc (Vowel-forming Marks) và Dấu Thanh (Tone Marks), 3. Thiết kế Thực thể `DiacriticCandidate`

### Community 31 - "6. Quy trình Sinh Ứng viên Trạng thái & Kiểm soát Cắt tỉa (Pruning)"
Cohesion: 0.50
Nodes (4): 6.1 Phân tích Không gian Trạng thái Tự nhiên (Raw Candidates Upper Bound), 6.2 Chính sách Xử lý Fallback (Fallback Policy & Failure Path), 6.3 Thuật toán sinh ứng viên (Pseudocode), 6. Quy trình Sinh Ứng viên Trạng thái & Kiểm soát Cắt tỉa (Pruning)

### Community 33 - "OmniDraw — CA-VHC Diacritic-Aware State Architecture"
Cohesion: 0.18
Nodes (10): 10.1 Trách nhiệm của Renderer trong Bước C, 10. Tái cấu trúc Luồng Render (Renderer Architecture), 11. Phân định Phạm vi: Delayed-Stroke Ordering là Nhiệm vụ Độc lập, 12. Ma trận Trách nhiệm Module (Ownership Matrix), 15. Bản Thiết kế Metrics Nghiên cứu Nội bộ (Research Metrics Schema), 17. Trạng thái Phê duyệt & Sẵn sàng cho Bước C (Implementation Readiness), 4. Thiết lập Tham số Cấu hình Duy nhất (Single Source of Truth), 7. Chiến lược Mỏ neo P0 (Anchor Strategy) (+2 more)

### Community 34 - "9. Phương trình Truy hồi Viterbi DP Mới"
Cohesion: 0.50
Nodes (4): 9.1 Khởi tạo (Base Case - Layer 0), 9.2 Bước truy hồi (Inductive Step - Layer $i$, với $1 \le i < L$), 9.3 Kết thúc và Truy vết (Termination & Backtracking), 9. Phương trình Truy hồi Viterbi DP Mới

### Community 35 - "OmniDraw — Đặc tả Kỹ thuật Dataset Chữ viết tay (Handwriting Dataset Specification)"
Cohesion: 0.08
Nodes (23): 10. Bảo mật, đạo đức và tuân thủ (Privacy, Consent & Ethics), 11.1. Khuyến nghị công cụ DVC (Data Version Control), 11. Quản trị phiên bản dữ liệu (Dataset Versioning Protocol), 1.1. Tách biệt hai loại Dataset độc lập, 1.2. Mối quan hệ và Nguyên tắc "Shared Raw Input", 1. Mục đích và phạm vi (Purpose & Scope), 2. Phân công trách nhiệm (Dataset Ownership), 3.1. Các bước thực hiện chi tiết (+15 more)

### Community 38 - "metrics_evaluator.py"
Cohesion: 0.16
Nodes (18): compute_curvature_cost_from_stroke(), compute_stroke_fingerprint(), compute_total_curvature_cost(), evaluate_ca_vhc_metrics(), _extract_points(), polyline_length(), OmniDraw CA-VHC Metrics Evaluator & Structured Render Trace. Provides: -…, Tính chi phí độ cong xấp xỉ từ các điểm polyline của một bridge stroke. (+10 more)

### Community 39 - "resolve_font"
Cohesion: 0.22
Nodes (9): load_benchmark_fonts(), Any, OmniDraw CA-VHC Benchmark Fixtures & Corpus Definitions. Defined per…, Tải 2 font pack chuẩn dùng cho nghiên cứu CA-VHC: 'oly' và 'omni_casual'. Trả…, Phân giải font_id thành (font_pack, render_profile). Không fallback ngầm cho…, resolve_font(), Kiểm tra tính rời nhau (disjoint) của BENCHMARK_DEV_CORPUS_20 và…, test_corpus_disjointness_and_counts() (+1 more)

### Community 40 - "main.py"
Cohesion: 0.06
Nodes (59): asyncio, delete_history_item(), format_time_ago(), get_all_history(), init_db(), parse_svg_info(), Tính toán nhanh số nét vẽ, chiều dài và thời gian ước tính từ file SVG nếu…, save_history_record() (+51 more)

### Community 45 - "3. Định Nghĩa Chính Xác Ba Baseline Đối Chứng"
Cohesion: 0.67
Nodes (3): 3.1. Baseline 1: Static Glyphs Renderer (B1), 3.2. Baseline 2: Greedy Heuristic (B2), 3. Định Nghĩa Chính Xác Ba Baseline Đối Chứng

### Community 46 - "nearest_neighbor_order"
Cohesion: 0.25
Nodes (8): compute_pixel_to_mm_transform(), kinematic_cost(), nearest_neighbor_order(), Chiêu 3: Khoang cach Euclid + phat goc quay quan tinh dong hoc: dist + lambda *…, Sap xep ban dau bang Nearest Neighbor ket hop phat quan tinh dong hoc (Chiêu 1…, Tinh he so quy doi pixel -> mm theo kieu "contain" (giu ty le, can giua trong…, 6. Anh den khong gay loi hoac vuot bounds., test_stipple_black_image_in_bounds()

### Community 47 - "13. Hợp đồng Tương thích Ngược (Backward Compatibility Contract)"
Cohesion: 0.67
Nodes (3): 13.1 Đối với Văn bản ASCII / Không dấu (Strict Regression Target), 13.2 Đối với Văn bản Tiếng Việt có dấu (Intentional Geometric Evolution), 13. Hợp đồng Tương thích Ngược (Backward Compatibility Contract)

### Community 48 - "optimize_word_dag"
Cohesion: 0.16
Nodes (21): bridge_collision_cost(), eval_transition(), optimize_word_dag(), Sampled-polyline / segment-distance heuristic: Tính chi phí va chạm hình học…, Tính chi phí chuyển trạng thái giữa 2 node theo hàm mục tiêu: J = w1*D_penup +…, Quy hoạch động Viterbi DP trên đồ thị có hướng (DAG), độ phức tạp O(n * k^2).…, 3.3. Baseline 3: Current Trellis DAG (B3 — Hiện Trạng Chưa Có Ràng Buộc Dấu), 4.2. Cơ Chế Đưa Dấu Vào Trellis DAG (Không Bùng Nổ Trạng Thái) (+13 more)

### Community 49 - "2. Backlog chi tiết Sprint 1–2 (Kế hoạch hành động 2 tuần tới)"
Cohesion: 0.20
Nodes (9): 1. Trạng thái hiện tại theo 4 đường chạy (Current Sprint Status), 2. Backlog chi tiết Sprint 1–2 (Kế hoạch hành động 2 tuần tới), 3. Tiêu chí Hoàn thành (Definition of Done) cho từng Task, 4. Nhật ký tiến độ theo ngày (Progress Log by Date), OmniDraw — Current Task & Sprint Backlog, Quy định phối hợp toàn nhóm trong Sprint, TV1 — AI Data & Writer Profile Lead, TV2 — Stroke Optimization & Path Planning Lead (+1 more)

### Community 50 - "test_curvature_cost_formula"
Cohesion: 0.33
Nodes (6): compute_curvature_cost_from_vectors(), compute_turning_cost(), Tính chi phí bẻ một góc tiếp tuyến: 1.0 - cos(theta). - 0 deg -> 0.0 - 90 deg…, Tính chi phí góc bẻ tiếp tuyến cho một cầu nối theo đúng định nghĩa đặc tả: u_d…, Curvature cost tính đúng theo công thức với các góc đã biết: - 0 độ -> cost 0 -…, test_curvature_cost_formula()

### Community 51 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 52 - "_stroke_min_distance"
Cohesion: 0.09
Nodes (26): audit_font_pack_geometry(), point_to_segment_distance(), Kiểm tra hình học glyph dành cho máy vẽ plotter (Geometry Auditor): Phát hiện…, Tính khoảng cách tối thiểu giữa hai stroke (polyline) trong cùng hệ tọa độ…, Tính khoảng cách Euclide ngắn nhất từ điểm p đến đoạn thẳng nối từ a đến b., _stroke_min_distance(), 1. AI Data & Writer Profile (TV1 — AI Data & Writer Profile Lead), 2. Tối ưu đường vẽ & Quy hoạch quỹ đạo (TV2 — Stroke Optimization & Path Planning Lead) (+18 more)

### Community 56 - "_auto_isolate_background"
Cohesion: 0.50
Nodes (4): _auto_isolate_background(), _is_background_already_white(), Kiem tra 2 goc tren va vien tren cua anh da la nen trang/sang hay chua., Tu dong phat hien va tach chu the khoi phong nen ngoai canh (sa mac, phong, cay…

### Community 57 - "5. Thiết kế Thực thể `CompositionState` & Cơ chế Chuyển đổi Tọa độ"
Cohesion: 0.67
Nodes (3): 5.1 Cấu trúc dữ liệu ý niệm (Conceptual Schema), 5.2 Cơ chế Chuyển đổi Tọa độ Cục bộ $\rightarrow$ Tọa độ Thế giới (Transform Helper), 5. Thiết kế Thực thể `CompositionState` & Cơ chế Chuyển đổi Tọa độ

### Community 58 - "Giai đoạn 2 — Phát triển song song theo 4 đường chạy"
Cohesion: 0.29
Nodes (7): 2.1 AI Core & Benchmark Dataset Preparation (Đường chạy TV1), 2.2 AI Cá nhân hóa & Dữ liệu Writer Profile (Đường chạy TV1), 2.3 Thị giác máy tính & Căn chỉnh giấy (Đường chạy TV3), 2.5 Phần cứng — Firmware & Điều khiển chuyển động (Đường chạy TV3), 2.6 Phần cứng — Đo đạc thực tế & Trạng thái (Đường chạy TV3), 2.8 Checklist module & Đánh giá nội bộ, Giai đoạn 2 — Phát triển song song theo 4 đường chạy

### Community 59 - "2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)"
Cohesion: 0.25
Nodes (8): 2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2), A. Tối ưu đường vẽ tranh (Line-art Art Mode) — Đã xong, B. Lõi giải thuật CA-VHC & Stroke Graph Optimizer — P0, C. Bố trí dấu tiếng Việt & Thứ tự nét trễ — P0, D. Contextual allographs có kiểm soát — P1, E. AI cá nhân hóa nét chữ (Writer Profile) — P2 (TV1 chủ trì phối hợp TV4 & TV2 qua contract), F. Bố cục trang, Cỡ chữ & Phân trang — P1 (TV4 phụ trách), G. Tính năng trình diễn & Mở rộng nét đơn (Demos & Embellishments) — P3 Backlog

### Community 63 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 64 - "OmniDraw — Roadmap"
Cohesion: 0.18
Nodes (10): 1. Nguyên tắc tổ chức & Phân công 4 đường chạy (Module Ownership), 2. Quy tắc Ownership và Merge Code, 3. Definition of Done (DoD) chung, 4. Hệ thống Mức độ Ưu tiên (Priority Levels: P0 – P3), Bảng tổng hợp phân công 4 đường chạy, OmniDraw — Roadmap, P0 — Bắt buộc để bảo vệ đề tài (Critical Path), P1 — Hoàn thiện hệ thống nghiên cứu (Core Supporting) (+2 more)

### Community 65 - "5. Lộ trình theo các Cổng Quyết định (Decision Gates & Milestones)"
Cohesion: 0.33
Nodes (6): 5. Lộ trình theo các Cổng Quyết định (Decision Gates & Milestones), Sprint 1–2 (Tháng 1–2) — Khóa nền nghiên cứu (Locking Research Foundation), Sprint 3–6 (Tháng 3–5) — Phát triển song song 4 đường chạy (Parallel Development), Sprint 7–10 (Tháng 6–7) — Tích hợp Beta & Kiểm định Phần cứng (Beta Integration), Tháng 10–12 — Đánh giá người dùng, Viết báo cáo & Bảo vệ đề tài (Evaluation & Defense), Tháng 8–9 — Đóng băng tính năng & Chạy thực nghiệm toàn diện (Feature Freeze)

### Community 66 - "OmniDraw — React + Tailwind UI (5 màn hình)"
Cohesion: 0.33
Nodes (5): Chạy thử, Cấu trúc, Ghi chú hiệu ứng "vẽ dần" ở màn 4, Icon, OmniDraw — React + Tailwind UI (5 màn hình)

### Community 67 - "OmniDraw — Danh sách 15 Prompt Test (Chuẩn Xứ Lý AxiDraw v2.0)"
Cohesion: 0.33
Nodes (5): Bảng Phân Bố Style, OmniDraw — Danh sách 15 Prompt Test (Chuẩn Xứ Lý AxiDraw v2.0), Phần 1: Prompt Đơn Giản (Động vật nhỏ, dễ thương), Phần 2: Prompt Có Bối Cảnh (Chủ thể + Không gian), Phần 3: Prompt Chi Tiết, Phức Tạp, Trừu Tượng

### Community 71 - "Giai đoạn 1 — Khảo sát & Nền tảng"
Cohesion: 0.40
Nodes (5): 1.1 Khảo sát & chốt hướng AI, 1.2 Kiến trúc & chuẩn dữ liệu, 1.3 Phần cứng cơ bản, 1.4 Khung UI/UX (mock data), Giai đoạn 1 — Khảo sát & Nền tảng

### Community 72 - "Giai đoạn 3 — Tích hợp hệ thống"
Cohesion: 0.40
Nodes (5): 3.1 Tích hợp luồng AI & Sinh vector vào giao diện, 3.2 Tích hợp CV & Tối ưu chữ viết tay vào giao diện, 3.3 Tích hợp máy vẽ vật lý, 3.4 Test end-to-end toàn hệ thống, Giai đoạn 3 — Tích hợp hệ thống

### Community 73 - "4.1 Benchmark Thực nghiệm Định lượng & Ablation Study — P0"
Cohesion: 0.40
Nodes (5): 4.1 Benchmark Thực nghiệm Định lượng & Ablation Study — P0, A. Thực nghiệm Tối ưu đường vẽ tranh (Line-art Art Mode) — P1 (TV2 lead), B. Thực nghiệm Tối ưu chữ viết tay CA-VHC (Handwriting Mode) — P0 (TV4 lead composition & runner, TV2 lead motion metrics), C. Khảo sát Đánh giá Người dùng (User Evaluation Protocol) — P0 / P1, D. Thực nghiệm thi công vật lý trên máy AxiDraw — P0

### Community 74 - "6. Chi tiết các giai đoạn triển khai (Giai đoạn 1 đến Giai đoạn 4)"
Cohesion: 0.40
Nodes (5): 4.2 Demo & Video minh họa — P1, 4.3 Báo cáo khoa học (Chuẩn mực Báo cáo NCKH 5 chương) — P0, 4.4 Slide thuyết trình & Bảo vệ đề tài — P0, 6. Chi tiết các giai đoạn triển khai (Giai đoạn 1 đến Giai đoạn 4), Giai đoạn 4 — Hoàn thiện, Benchmark Thực nghiệm & Báo cáo NCKH

### Community 81 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 82 - "graphify reference: commit hook and native AGENTS.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 83 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **228 isolated node(s):** `run.sh script`, `name`, `private`, `version`, `type` (+223 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 497 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Giai đoạn 2 — Phát triển song song theo 4 đường chạy` connect `Giai đoạn 2 — Phát triển song song theo 4 đường chạy` to `App.jsx`, `6. Chi tiết các giai đoạn triển khai (Giai đoạn 1 đến Giai đoạn 4)`, `2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)`?**
  _High betweenness centrality (0.286) - this node is a cross-community bridge._
- **Why does `2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)` connect `2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)` to `Giai đoạn 2 — Phát triển song song theo 4 đường chạy`, `_stroke_min_distance`?**
  _High betweenness centrality (0.283) - this node is a cross-community bridge._
- **Why does `2.7 Giao diện, Strict Validation & Tích hợp (Đường chạy TV4)` connect `App.jsx` to `Giai đoạn 2 — Phát triển song song theo 4 đường chạy`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `optimize_word_dag()` (e.g. with `A. Đã triển khai (Implemented)` and `Phân rã hai lõi kỹ thuật của CA-VHC`) actually correct?**
  _`optimize_word_dag()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `_run_self_check()` (e.g. with `_spy_bridge_tracked()` and `_spy_eval()`) actually correct?**
  _`_run_self_check()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `generate_accents()` (e.g. with `TV4 — Project Lead & Handwriting / CA-VHC Composition Lead` and `Log`) actually correct?**
  _`generate_accents()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `GlyphVariant` (e.g. with `4. Nhật ký tiến độ theo ngày (Progress Log by Date)` and `TV4 — Project Lead & Handwriting / CA-VHC Composition Lead`) actually correct?**
  _`GlyphVariant` has 18 INFERRED edges - model-reasoned connections that need verification._