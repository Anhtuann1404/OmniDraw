# Graph Report - OmniDraw  (2026-09-20)

## Corpus Check
- 60 files · ~111,635 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: .stl 6, (none) 3, .css 1)

## Summary
- 787 nodes · 1355 edges · 81 communities (49 shown, 32 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 140 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1fe88a38`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- App.jsx
- bz
- database.py
- generate_accents
- package.json
- api_generator.py
- APIResponse
- build_svg
- compute_svg_metrics
- handwriting/__init__.py
- test_invalid_letter_type_rejected
- process
- generate_ai_image
- path_optimizer.py
- dist
- test_seed_boundary_and_type_validation
- test_letter_type_omitted_defaults_to_general
- nearest_neighbor_order
- OmniDraw — Tài liệu chuẩn giao tiếp giữa các mảng (API/Data Contract)
- test_invalid_target_paper_size
- test_direct_engine_style_strict_validation
- test_explicit_letter_type_null_or_invalid_type_rejected
- test_handwriting_validation.py
- GlyphVariant
- ComicPrimitives.jsx
- test_explicit_font_null_or_invalid_type_rejected
- test_font_omitted_defaults_to_oly
- inspect_paper
- What You Must Do When Invoked
- text_to_strokes
- test_target_paper_size_valid_explicit
- test_art_mode_image_upload_regression
- test_invalid_style_rejected_without_silent_fallback
- OmniDraw — CA-VHC Diacritic-Aware State Architecture
- test_art_mode_image_all_valid_styles_downstream_verification
- OmniDraw — Đặc tả Kỹ thuật Dataset Chữ viết tay (Handwriting Dataset Specification)
- test_style_null_or_invalid_type_structured_error
- test_target_paper_size_omitted_defaults_to_a4
- test_art_mode_empty_payload_rejected_without_side_effects
- get
- main.py
- run.sh
- run_backend.sh
- bridge_collision_cost
- _clear_cached_svg_for_request
- test_formal_letter_type_compatibility
- eval_transition
- 2. Backlog chi tiết Sprint 1–2 (Kế hoạch hành động 2 tuần tới)
- BÁO CÁO AUDIT KIẾN TRÚC: TRELLIS DAG / CA-VHC HIỆN TẠI (BƯỚC A)
- graphify reference: extra exports and benchmark
- Chi tiết trạng thái giải thuật CA-VHC
- test_empty_handwriting_text_rejected
- test_art_mode_invalid_style_rejected_without_side_effects
- users_yingjunn_study_nckh_2026_2027_omnidraw_test_handwriting_py
- test_valid_fonts_succeed
- Giai đoạn 2 — Phát triển song song theo 4 đường chạy
- 2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)
- graphify reference: query, path, explain
- OmniDraw — Roadmap
- 5. Lộ trình theo các Cổng Quyết định (Decision Gates & Milestones)
- OmniDraw — React + Tailwind UI (5 màn hình)
- OmniDraw — Danh sách 15 Prompt Test (Chuẩn Xứ Lý AxiDraw v2.0)
- Giai đoạn 1 — Khảo sát & Nền tảng
- Giai đoạn 3 — Tích hợp hệ thống
- 4.1 Benchmark Thực nghiệm Định lượng & Ablation Study — P0
- 6. Chi tiết các giai đoạn triển khai (Giai đoạn 1 đến Giai đoạn 4)
- 4. Hệ thống Mức độ Ưu tiên (Priority Levels: P0 – P3)
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rules/graphify.md
- extraction-spec.md
- workflows/graphify.md
- engine.py
- test_valid_handwriting_request
- test_art_mode_invalid_input_graceful
- test_valid_styles_all_succeed

## God Nodes (most connected - your core abstractions)
1. `text_to_strokes()` - 27 edges
2. `_run_self_check()` - 24 edges
3. `generate_accents()` - 21 edges
4. `GlyphVariant` - 21 edges
5. `App()` - 20 edges
6. `process()` - 19 edges
7. `OmniDraw — CA-VHC Diacritic-Aware State Architecture` - 19 edges
8. `eval_transition()` - 18 edges
9. `optimize_word_dag()` - 18 edges
10. `OmniDraw — Tài liệu chuẩn giao tiếp giữa các mảng (API/Data Contract)` - 18 edges

## Surprising Connections (you probably didn't know these)
- `10.1 Trách nhiệm của Renderer trong Bước C` --references--> `generate_accents()`  [INFERRED]
  docs/07_diacritic_aware_state_design.md → backend/handwriting/engine.py
- `7. Chiến lược Mỏ neo P0 (Anchor Strategy)` --references--> `generate_accents()`  [INFERRED]
  docs/07_diacritic_aware_state_design.md → backend/handwriting/engine.py
- `4. Nhật ký tiến độ theo ngày (Progress Log by Date)` --references--> `GlyphVariant`  [INFERRED]
  docs/03_current-task.md → backend/handwriting/engine.py
- ``DAG-02`: Zero Runtime Diacritic Collision Checking in Transition Evaluation` --references--> `bridge_collision_cost()`  [INFERRED]
  docs/06_audit_trellis_dag_report.md → backend/handwriting/engine.py
- `TV2 — Stroke Optimization & Path Planning Lead` --references--> `eval_transition()`  [INFERRED]
  docs/03_current-task.md → backend/handwriting/engine.py

## Import Cycles
- None detected.

## Communities (81 total, 32 thin omitted)

### Community 0 - "App.jsx"
Cohesion: 0.10
Nodes (39): Đã nối sẵn API client (mock mode), AuthError, clearToken(), delay(), login(), logout(), persistToken(), register() (+31 more)

### Community 1 - "bz"
Cohesion: 0.22
Nodes (14): bz(), make_arch(), make_ascender_loop(), make_descender_loop(), make_hook_stem(), make_oval(), Sinh nét móc vòm cong tròn tự nhiên chuẩn hình học đối xứng: Hai cung Bézier…, Sinh hình tròn/elip khép kín hoàn hảo bằng 4 cung Bézier chuẩn hình học: Hệ số… (+6 more)

### Community 2 - "database.py"
Cohesion: 0.19
Nodes (12): format_time_ago(), get_all_history(), init_db(), parse_svg_info(), Tính toán nhanh số nét vẽ, chiều dài và thời gian ước tính từ file SVG nếu…, get_history(), lifespan(), datetime (+4 more)

### Community 3 - "generate_accents"
Cohesion: 0.18
Nodes (13): generate_accents(), Sinh các nét dấu Tiếng Việt (Single-stroke Accents) căn chỉnh tự động: - Bố trí…, 2. Phân loại hai nhóm dấu tiếng Việt trong mã nguồn, `DAG-01`: Diacritics are Attached Exclusively Post-DAG (Hậu kỳ tách rời), `DAG-02`: Zero Runtime Diacritic Collision Checking in Transition Evaluation, `DAG-03`: Contextual Allographs are Greedily Overridden Before DAG, `DAG-04`: Rigid Procedural Anchors Without Per-Glyph Anchor Metadata, `DAG-05`: Delayed-Stroke Ordering is Static Word-End Append (+5 more)

### Community 4 - "package.json"
Cohesion: 0.08
Nodes (24): dependencies, lucide-react, react, react-dom, devDependencies, autoprefixer, postcss, tailwindcss (+16 more)

### Community 5 - "api_generator.py"
Cohesion: 0.12
Nodes (22): ExperimentLog, load_prompts_from_docx(), log_to_csv(), main(), process_all_prompts(), PromptData, Đọc file DOCX, trích xuất 15 prompt, OmniDraw — AI Core API Generator Phần mềm: Gọi API sinh ảnh cho 15 prompt thử… (+14 more)

### Community 6 - "APIResponse"
Cohesion: 0.13
Nodes (15): APIResponse, Art Mode text-to-drawing với style='sketch' không bị handwriting validation…, Art Mode text-to-drawing với style='line_art' không bị handwriting validation…, Art Mode khi style là None hoặc thiếu không bị crash ngoài kiểm soát (tự động…, Art Mode khi style omitted hoặc None phải tự động resolve thành 'sketch' và…, Text-to-Drawing với 4 style chuẩn (sketch, line_art, stipple, hatching) phải…, Art Mode cũng phải validate nghiêm ngặt target_paper_size_mm trước khi gọi…, Request hợp lệ phải gọi _clear_cached_svg_for_request đúng 1 lần trước khi… (+7 more)

### Community 7 - "build_svg"
Cohesion: 0.15
Nodes (17): build_svg(), _catmull_rom_cubic_segments(), compute_pixel_to_mm_transform(), get_render_bounds_px(), polyline_to_path_d(), px_to_mm(), Ponytail runnable check: assert NN + 2-Opt + Or-Opt reduces travel distance., Tinh he so quy doi pixel -> mm theo kieu "contain" (giu ty le, can giua trong… (+9 more)

### Community 8 - "compute_svg_metrics"
Cohesion: 0.14
Nodes (13): compute_svg_metrics(), extract_strokes(), extract_strokes_hatching(), extract_strokes_line_art(), extract_strokes_stipple(), polyline_length(), Tinh cac chi so bat buoc cho log CSV khoa hoc (muc 6): - total_path_length_mm :…, [NANG CAP TOAN DIEN v2] Style sketch (Ky hoa chi danh bong): Tao cam giac chan… (+5 more)

### Community 9 - "handwriting/__init__.py"
Cohesion: 0.08
Nodes (27): backend_handwriting, backend_handwriting_engine, OmniDraw - Handwriting Engine Compatibility Shim…, Nội dung thư tay không thể đặt trọn vẹn trong một trang., Nội dung chứa ký tự chưa có glyph trong Font Pack đang chọn., Loại văn bản / thư (letter_type) không được hỗ trợ hoặc không tương thích font…, Xác thực letter_type và kiểm tra tính tương thích với font_pack_id. -…, resolve_letter_type() (+19 more)

### Community 11 - "process"
Cohesion: 0.18
Nodes (10): chain_strokes(), decode_image(), log_msg(), make_error(), process(), Ham xu ly chinh cua module Thuat toan, khop input/output muc 1-3-4-6 cua API…, Noi cac stroke co diem dau/cuoi gan nhau (trong ban kinh snap_dist) thanh 1 net…, Log dung format chuan muc 7: [request_id] [ten module] [timestamp] message (+2 more)

### Community 12 - "generate_ai_image"
Cohesion: 0.22
Nodes (11): Any, call_openai_image_api(), Gọi OpenAI Image API (DALL-E 3), generate_ai_image(), Resolve and validate style for Art Mode (input_type in {'text', 'image'}).…, Validates target_paper_size_mm in options. Contract: - omitted: default A4…, Validates skew_angle_deg in options., resolve_art_style() (+3 more)

### Community 13 - "path_optimizer.py"
Cohesion: 0.29
Nodes (8): argparse, OmniDraw - Module Thị giác Máy tính: Giám sát Giấy & Camera (Closed-Loop…, OmniDraw - Module Thuat toan: Anh -> SVG toi uu duong ve…, base64, cv2, json, math, scipy_spatial

### Community 14 - "dist"
Cohesion: 0.25
Nodes (8): dist(), _edge_cost(), or_opt_improve(), 2-Opt dao nguoc doan de go cac duong nhac but cat cheo nhau (crossing edges). #…, Tong quang duong nhac but (khong tinh quang duong ve net), don vi = don vi cua…, Cai tien thu tu bang Or-opt dua tren danh sach hang xom KHONG GIAN (KD-tree),…, total_travel_distance(), two_opt_improve()

### Community 17 - "nearest_neighbor_order"
Cohesion: 0.50
Nodes (4): kinematic_cost(), nearest_neighbor_order(), Chiêu 3: Khoang cach Euclid + phat goc quay quan tinh dong hoc: dist + lambda *…, Sap xep ban dau bang Nearest Neighbor ket hop phat quan tinh dong hoc (Chiêu 1…

### Community 18 - "OmniDraw — Tài liệu chuẩn giao tiếp giữa các mảng (API/Data Contract)"
Cohesion: 0.06
Nodes (32): 0. Sơ đồ luồng dữ liệu tổng quát, 10. Thay đổi tài liệu, 1. Chuẩn hoá ảnh đầu vào (Người dùng → Giao diện), 2b. Giao diện → Backend (request tạo thư tay nét đơn — mới v1.4), 3. AI → Giao diện (kết quả sinh ảnh), 3b. Backend → Giao diện (kết quả sinh thư tay — mới v1.4), 4. Thuật toán → Máy vẽ (SVG chuẩn), 5. Máy vẽ → Giao diện (trạng thái, tiến độ) (+24 more)

### Community 22 - "test_handwriting_validation.py"
Cohesion: 0.17
Nodes (11): Font không nằm trong RENDER_PROFILES phải trả lỗi UNSUPPORTED_FONT., Thiếu trường 'style' trong request handwriting phải trả structured error…, Bất kỳ input_type nào ngoài ('handwriting', 'letter', 'text', 'image') đều phải…, Tất cả các request bị từ chối ở tầng validation tuyệt đối không được gọi…, test_invalid_font_rejected(), test_invalid_input_type_rejected(), test_invalid_requests_do_not_trigger_cleanup_or_side_effects(), test_missing_style_structured_error() (+3 more)

### Community 23 - "GlyphVariant"
Cohesion: 0.20
Nodes (11): GlyphVariant, Biến thể hình học (Alloglyph Node) trong đồ thị DAG., Log, OmniDraw — Progress & Decisions Log, 1. Luồng xử lý dấu từ Unicode đến SVG Render, 3. Bản đồ Anchor và Offset, E. Vietnamese Diacritic Pipeline, 2.1 Nguyên tắc bất biến đối với `GlyphVariant` (+3 more)

### Community 24 - "ComicPrimitives.jsx"
Cohesion: 0.09
Nodes (30): 2.7 Giao diện, Strict Validation & Tích hợp (Đường chạy TV4), Cách nối API thật (đọc kèm `OmniDraw_API_Spec.md`), getSvgContent(), ComicButton(), HardShadowBox(), Logo(), ScreenShell(), ScreenTitle() (+22 more)

### Community 27 - "inspect_paper"
Cohesion: 0.25
Nodes (8): _encode_jpeg(), inspect_paper(), _normalize_paper_rect(), Chuyển ảnh OpenCV BGR thành chuỗi Base64 Data URL để UI render trực tiếp., Ponytail runnable check: assert synthetic paper detection precision., Chuẩn hóa góc nghiêng [-45, 45] độ và cạnh dài/cạnh ngắn., Kiểm tra tình trạng giấy từ frame ảnh hoặc webcam. # ponytail: dùng Otsu…, _run_self_check()

### Community 28 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 29 - "text_to_strokes"
Cohesion: 0.13
Nodes (24): analyze_text_contexts(), apply_bio_variation(), build_ligature_bridge(), generate_handwriting_svg(), group_nfd_graphemes(), normalize_vietnamese_final_uy_tone(), Context Analyzer v1 (CA-VHC): Phân tích ngữ cảnh vị trí của từng grapheme không…, Chọn nét hình học, độ rộng và tâm của glyph theo ngữ cảnh tài liệu, ngữ cảnh từ… (+16 more)

### Community 33 - "OmniDraw — CA-VHC Diacritic-Aware State Architecture"
Cohesion: 0.06
Nodes (35): Cùng text và cùng seed phải cho metrics giống nhau hoàn toàn., test_seed_determinism(), 10.1 Trách nhiệm của Renderer trong Bước C, 10. Tái cấu trúc Luồng Render (Renderer Architecture), 11. Phân định Phạm vi: Delayed-Stroke Ordering là Nhiệm vụ Độc lập, 13.1 Đối với Văn bản ASCII / Không dấu (Strict Regression Target), 13.2 Đối với Văn bản Tiếng Việt có dấu (Intentional Geometric Evolution), 13. Hợp đồng Tương thích Ngược (Backward Compatibility Contract) (+27 more)

### Community 35 - "OmniDraw — Đặc tả Kỹ thuật Dataset Chữ viết tay (Handwriting Dataset Specification)"
Cohesion: 0.08
Nodes (24): 10. Bảo mật, đạo đức và tuân thủ (Privacy, Consent & Ethics), 11.1. Khuyến nghị công cụ DVC (Data Version Control), 11. Quản trị phiên bản dữ liệu (Dataset Versioning Protocol), 12. Bảng trạng thái thực tế hệ thống (Implementation Status Matrix), 1.1. Tách biệt hai loại Dataset độc lập, 1.2. Mối quan hệ và Nguyên tắc "Shared Raw Input", 1. Mục đích và phạm vi (Purpose & Scope), 2. Phân công trách nhiệm (Dataset Ownership) (+16 more)

### Community 39 - "get"
Cohesion: 0.29
Nodes (7): api_inspect_paper(), get_svg_content(), get_thumbnail(), Kiem tra tinh trang giay va goc lech qua camera thi giac (Closed-Loop Vision)., Trả nội dung SVG thật để giao diện render hiệu ứng 'vẽ dần theo %'., root(), get

### Community 40 - "main.py"
Cohesion: 0.15
Nodes (26): asyncio, save_history_record(), cancel_print(), custom_error(), GenerateRequest, get_status(), log_experiment(), login_admin() (+18 more)

### Community 45 - "bridge_collision_cost"
Cohesion: 0.23
Nodes (12): audit_font_pack_geometry(), bridge_collision_cost(), point_to_segment_distance(), Kiểm tra hình học glyph dành cho máy vẽ plotter (Geometry Auditor): Phát hiện…, Tính khoảng cách tối thiểu giữa hai stroke (polyline) trong cùng hệ tọa độ…, Tính khoảng cách Euclide ngắn nhất từ điểm p đến đoạn thẳng nối từ a đến b., Sampled-polyline / segment-distance heuristic: Tính chi phí va chạm hình học…, _stroke_min_distance() (+4 more)

### Community 46 - "_clear_cached_svg_for_request"
Cohesion: 0.33
Nodes (6): delete_history_item(), _clear_cached_svg_for_request(), delete_history(), Xóa file SVG và cache metrics của một request_id nếu bị retry hoặc gặp lỗi., delete, 8. Bảng mã lỗi chuẩn (dùng chung cho tất cả module)

### Community 48 - "eval_transition"
Cohesion: 0.13
Nodes (22): eval_transition(), get_glyph_variants(), optimize_word_dag(), Tách nét chính (primary_strokes) và nét phụ (secondary_strokes) của glyph: - i,…, Sinh 1-3 biến thể hình học cho ký tự trên đồ thị DAG: - std: Nét chuẩn…, Tính chi phí chuyển trạng thái giữa 2 node theo hàm mục tiêu: J = w1*D_penup +…, Quy hoạch động Viterbi DP trên đồ thị có hướng (DAG), độ phức tạp O(n * k^2).…, split_glyph_strokes() (+14 more)

### Community 49 - "2. Backlog chi tiết Sprint 1–2 (Kế hoạch hành động 2 tuần tới)"
Cohesion: 0.20
Nodes (9): 1. Trạng thái hiện tại theo 4 đường chạy (Current Sprint Status), 2. Backlog chi tiết Sprint 1–2 (Kế hoạch hành động 2 tuần tới), 3. Tiêu chí Hoàn thành (Definition of Done) cho từng Task, 4. Nhật ký tiến độ theo ngày (Progress Log by Date), OmniDraw — Current Task & Sprint Backlog, Quy định phối hợp toàn nhóm trong Sprint, TV1 — AI Data & Writer Profile Lead, TV2 — Stroke Optimization & Path Planning Lead (+1 more)

### Community 50 - "BÁO CÁO AUDIT KIẾN TRÚC: TRELLIS DAG / CA-VHC HIỆN TẠI (BƯỚC A)"
Cohesion: 0.20
Nodes (10): audit_vietnamese_lowercase_accents(), Kiểm định bộ dấu tiếng Việt viết thường cho một Font Pack. Kiểm tra 12 họ…, 1. Bảng danh mục Tests hiện có liên quan đến Handwriting & DAG, 1. Sơ đồ luồng thực thi (End-to-End Call Chain), B. Current Call Graph, BÁO CÁO AUDIT KIẾN TRÚC: TRELLIS DAG / CA-VHC HIỆN TẠI (BƯỚC A), F. Current vs Target Gap, I. Existing Tests & Missing Tests (+2 more)

### Community 51 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 52 - "Chi tiết trạng thái giải thuật CA-VHC"
Cohesion: 0.12
Nodes (16): 1. AI Data & Writer Profile (TV1 — AI Data & Writer Profile Lead), 2. Tối ưu đường vẽ & Quy hoạch quỹ đạo (TV2 — Stroke Optimization & Path Planning Lead), 3. Phần cứng, Hiệu chuẩn & Thực nghiệm Vật lý (TV3 — Hardware, Calibration & Physical Validation Lead), 4. Nền tảng, Tích hợp & Quản trị Hệ thống (TV4 — Project Lead & Handwriting / CA-VHC Composition Lead), 5. Khung giải thuật Context-Aware Vietnamese Handwriting Composition (CA-VHC), B. Đang phát triển (In Progress), C. Định hướng nghiên cứu (Research Directions), Chi tiết trạng thái giải thuật CA-VHC (+8 more)

### Community 58 - "Giai đoạn 2 — Phát triển song song theo 4 đường chạy"
Cohesion: 0.29
Nodes (7): 2.1 AI Core & Benchmark Dataset Preparation (Đường chạy TV1), 2.2 AI Cá nhân hóa & Dữ liệu Writer Profile (Đường chạy TV1), 2.3 Thị giác máy tính & Căn chỉnh giấy (Đường chạy TV3), 2.5 Phần cứng — Firmware & Điều khiển chuyển động (Đường chạy TV3), 2.6 Phần cứng — Đo đạc thực tế & Trạng thái (Đường chạy TV3), 2.8 Checklist module & Đánh giá nội bộ, Giai đoạn 2 — Phát triển song song theo 4 đường chạy

### Community 59 - "2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)"
Cohesion: 0.29
Nodes (7): 2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2), A. Tối ưu đường vẽ tranh (Line-art Art Mode) — Đã xong, C. Bố trí dấu tiếng Việt & Thứ tự nét trễ — P0, D. Contextual allographs có kiểm soát — P1, E. AI cá nhân hóa nét chữ (Writer Profile) — P2 (TV1 chủ trì phối hợp TV4 & TV2 qua contract), F. Bố cục trang, Cỡ chữ & Phân trang — P1 (TV4 phụ trách), G. Tính năng trình diễn & Mở rộng nét đơn (Demos & Embellishments) — P3 Backlog

### Community 63 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 64 - "OmniDraw — Roadmap"
Cohesion: 0.33
Nodes (5): 1. Nguyên tắc tổ chức & Phân công 4 đường chạy (Module Ownership), 2. Quy tắc Ownership và Merge Code, 3. Definition of Done (DoD) chung, Bảng tổng hợp phân công 4 đường chạy, OmniDraw — Roadmap

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

### Community 75 - "4. Hệ thống Mức độ Ưu tiên (Priority Levels: P0 – P3)"
Cohesion: 0.40
Nodes (5): 4. Hệ thống Mức độ Ưu tiên (Priority Levels: P0 – P3), P0 — Bắt buộc để bảo vệ đề tài (Critical Path), P1 — Hoàn thiện hệ thống nghiên cứu (Core Supporting), P2 — Mở rộng nếu tiến độ P0/P1 ổn định (Optional Extensions), P3 — Backlog nghiên cứu xa (Post-Defense Backlog)

### Community 81 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 82 - "graphify reference: commit hook and native AGENTS.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 83 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 92 - "engine.py"
Cohesion: 0.14
Nodes (12): can_ligature(), find_unsupported_characters(), point_on_segment(), OmniDraw - Module Viết Thư Tay Tự Động (Bio-Inspired Vietnamese Handwriting…, Kiểm tra nội dung văn bản sau chuẩn hóa NFD và trả về danh sách các ký tự chưa…, Kiểm tra điểm p có nằm trên đoạn thẳng [a, b] trong hệ tọa độ 2D (khi p, a, b…, Kiểm tra giao nhau giữa 2 đoạn thẳng [p1, p2] và [q1, q2] bền vững: - Sử dụng…, Fallback tương thích ngược. (+4 more)

## Knowledge Gaps
- **205 isolated node(s):** `run.sh script`, `name`, `private`, `version`, `type` (+200 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 411 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Giai đoạn 2 — Phát triển song song theo 4 đường chạy` connect `Giai đoạn 2 — Phát triển song song theo 4 đường chạy` to `ComicPrimitives.jsx`, `6. Chi tiết các giai đoạn triển khai (Giai đoạn 1 đến Giai đoạn 4)`, `2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)`?**
  _High betweenness centrality (0.327) - this node is a cross-community bridge._
- **Why does `2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)` connect `2.4 Khung giải thuật CA-VHC & Tối ưu đường nét (Đường chạy TV4 & TV2)` to `eval_transition`, `Giai đoạn 2 — Phát triển song song theo 4 đường chạy`, `bridge_collision_cost`?**
  _High betweenness centrality (0.318) - this node is a cross-community bridge._
- **Why does `2.7 Giao diện, Strict Validation & Tích hợp (Đường chạy TV4)` connect `ComicPrimitives.jsx` to `App.jsx`, `Giai đoạn 2 — Phát triển song song theo 4 đường chạy`?**
  _High betweenness centrality (0.251) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `text_to_strokes()` (e.g. with `2. Bảng đặc tả từng bước trong Call Chain` and `Definition of Done (Xác nhận hoàn thành Audit)`) actually correct?**
  _`text_to_strokes()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `_run_self_check()` (e.g. with `_spy_bridge_tracked()` and `_spy_eval()`) actually correct?**
  _`_run_self_check()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `generate_accents()` (e.g. with `TV4 — Project Lead & Handwriting / CA-VHC Composition Lead` and `Log`) actually correct?**
  _`generate_accents()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `GlyphVariant` (e.g. with `4. Nhật ký tiến độ theo ngày (Progress Log by Date)` and `TV4 — Project Lead & Handwriting / CA-VHC Composition Lead`) actually correct?**
  _`GlyphVariant` has 17 INFERRED edges - model-reasoned connections that need verification._