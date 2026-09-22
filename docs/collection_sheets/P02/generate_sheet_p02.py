import os

def build_p02_svg():
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297" width="210mm" height="297mm">')
    
    # 1. White Paper Surface (A4 Portrait: 210 x 297 mm)
    lines.append('  <!-- Paper Surface -->')
    lines.append('  <rect x="0" y="0" width="210" height="297" fill="#ffffff"/>')
    
    # 2. Fiducial Markers: 5.0 x 5.0 mm at (12,12), (193,12), (12,280), (193,280)
    # Exact center span: horizontal 181.0 mm, vertical 268.0 mm (identical to P01)
    lines.append('  <!-- 4 Corner Fiducial Markers (5.0 x 5.0 mm) -->')
    lines.append('  <g id="fiducials">')
    lines.append('    <rect id="fiducial_tl" x="12.0" y="12.0" width="5.0" height="5.0" fill="#000000"/>')
    lines.append('    <rect id="fiducial_tr" x="193.0" y="12.0" width="5.0" height="5.0" fill="#000000"/>')
    lines.append('    <rect id="fiducial_bl" x="12.0" y="280.0" width="5.0" height="5.0" fill="#000000"/>')
    lines.append('    <rect id="fiducial_br" x="193.0" y="280.0" width="5.0" height="5.0" fill="#000000"/>')
    lines.append('  </g>')

    # 3. Header Section (y: 12.5 to 25.5 mm)
    lines.append('  <!-- Header -->')
    lines.append('  <g id="header">')
    lines.append('    <text x="21.0" y="16.0" font-family="Helvetica, Arial, sans-serif" font-size="4.0" font-weight="bold" fill="#111111" letter-spacing="0.2">OMNIDRAW RESEARCH DATASET</text>')
    lines.append('    <text x="21.0" y="20.2" font-family="Helvetica, Arial, sans-serif" font-size="2.7" font-weight="bold" fill="#333333">P02 — Context &amp; Ligature Collection Sheet</text>')
    lines.append('    <text x="21.0" y="23.8" font-family="Courier, monospace" font-size="1.9" fill="#555555">FORM VERSION: ODW-HW-P02-DEMO-v0.1 • PROTOCOL: DOC-SPEC-08-DATASET</text>')
    
    # Right-aligned header notices
    lines.append('    <text x="189.0" y="16.0" text-anchor="end" font-family="Courier, monospace" font-size="1.9" font-weight="bold" fill="#444444">RESEARCH USE ONLY</text>')
    lines.append('    <text x="189.0" y="19.8" text-anchor="end" font-family="Courier, monospace" font-size="1.9" fill="#666666">ANONYMIZED PROTOCOL • NO PII COLLECTED</text>')
    lines.append('    <text x="189.0" y="23.8" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#c93b2b">PILOT CANDIDATE — NOT APPROVED FOR FORMAL DATA COLLECTION</text>')
    
    # Thin divider
    lines.append('    <line x1="21.0" y1="25.5" x2="189.0" y2="25.5" stroke="#cccccc" stroke-width="0.25"/>')
    
    # Metadata Fields Box (No PII! Page is strictly P02)
    lines.append('    <rect x="13.0" y="27.0" width="184.0" height="6.5" fill="#f8f9fa" stroke="#cccccc" stroke-width="0.25" rx="0.6"/>')
    lines.append('    <text x="16.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Writer ID: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">W_________</tspan></text>')
    lines.append('    <text x="64.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Session: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">S______</tspan></text>')
    lines.append('    <text x="105.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Page: <tspan font-family="Courier, monospace" font-weight="bold" fill="#111111">P02</tspan></text>')
    lines.append('    <text x="145.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Date: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">_____ / _____ / 202___</tspan></text>')
    lines.append('  </g>')

    # 4. Instructions Box (y: 35.0 to 44.5 mm, height: 9.5 mm)
    lines.append('  <!-- Instructions -->')
    lines.append('  <g id="instructions">')
    lines.append('    <rect x="13.0" y="35.0" width="184.0" height="9.5" fill="#ffffff" stroke="#b0b0b0" stroke-width="0.28" rx="0.6"/>')
    lines.append('    <rect x="13.0" y="35.0" width="184.0" height="3.0" fill="#eceff1" stroke="#b0b0b0" stroke-width="0.28" rx="0.6"/>')
    lines.append('    <text x="16.0" y="37.2" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#111111">HƯỚNG DẪN VIẾT MẪU / WRITING INSTRUCTIONS</text>')
    lines.append('    <text x="194.0" y="37.2" text-anchor="end" font-family="Courier, monospace" font-size="1.6" fill="#555555">SPECIFICATION: 0.5MM BLACK GEL PEN</text>')
    
    # 2 columns of instructions
    lines.append('    <text x="16.0" y="40.5" font-family="Helvetica, Arial, sans-serif" font-size="1.75" fill="#333333">• Viết bằng nét chữ tự nhiên; tuyệt đối KHÔNG cố tình nắn nót đẹp hơn bình thường.</text>')
    lines.append('    <text x="16.0" y="43.2" font-family="Helvetica, Arial, sans-serif" font-size="1.75" fill="#333333">• Dùng bút gel đen 0.5 mm do nhóm cung cấp (hoặc tương thích); không dùng bút khác.</text>')
    lines.append('    <text x="106.0" y="40.5" font-family="Helvetica, Arial, sans-serif" font-size="1.75" fill="#333333">• Viết đúng từ/cụm từ yêu cầu, liền mạch tự nhiên trong vùng kẻ; KHÔNG chạm dải nhãn.</text>')
    lines.append('    <text x="106.0" y="43.2" font-family="Helvetica, Arial, sans-serif" font-size="1.75" fill="#333333">• Không viết đè, không tô lại nét lỗi, không dùng bút xóa; không ký tên hay ghi thông tin cá nhân.</text>')
    lines.append('  </g>')

    # 5. Writing Sections and Rows Specification
    # Section A: 4 rows (Initial)
    # Section B: 6 rows (Medial & Ligature Challenge with 2 trial pairs)
    # Section C: 6 rows (Final Variants)
    sections_spec = [
        {
            "code": "A",
            "title": "SECTION A — WORD INITIAL / PHRASE INITIAL",
            "tagline": "ENTRY STROKE • INITIAL ALLOGRAPHS • WORD SPACING",
            "rows": [
                {"id": "CTX_INIT_001", "prompt": "Kính gửi", "tag": "WORD_INITIAL", "note": "Phrase Initial"},
                {"id": "CTX_INIT_002", "prompt": "Thân gửi", "tag": "WORD_INITIAL", "note": "Phrase Initial"},
                {"id": "CTX_INIT_003", "prompt": "Cảm ơn", "tag": "WORD_INITIAL", "note": "Diacritic & Spacing"},
                {"id": "CTX_INIT_004", "prompt": "Chào mừng", "tag": "WORD_INITIAL", "note": "Dấu huyền trên a trong 'Chào'; ư mang dấu huyền trong 'mừng'"}
            ]
        },
        {
            "code": "B",
            "title": "SECTION B — WORD MEDIAL & LIGATURE CHALLENGE",
            "tagline": "MEDIAL CONNECTORS • DIACRITIC INTERACTION • INTRA-WRITER VARIATION",
            "rows": [
                {"id": "CTX_MED_001",   "prompt": "thuyền",  "tag": "WORD_MEDIAL / LIGATURE", "note": "Cụm u-y-ê, dấu huyền trên ê; ligature/diacritic challenge"},
                {"id": "CTX_MED_002",   "prompt": "nghiêng", "tag": "WORD_MEDIAL / LIGATURE", "note": "Cụm i-ê, thanh ngang; ligature/spacing challenge"},
                {"id": "CTX_MED_003_A", "prompt": "trường",  "tag": "LIGATURE CHALLENGE",     "note": "Trial A — Bridge Risk"},
                {"id": "CTX_MED_003_B", "prompt": "trường",  "tag": "LIGATURE CHALLENGE",     "note": "Trial B — Repeat Trial"},
                {"id": "CTX_MED_004_A", "prompt": "nguyễn",  "tag": "LIGATURE CHALLENGE",     "note": "Trial A — Double Diacritic"},
                {"id": "CTX_MED_004_B", "prompt": "nguyễn",  "tag": "LIGATURE CHALLENGE",     "note": "Trial B — Repeat Trial"}
            ]
        },
        {
            "code": "C",
            "title": "SECTION C — WORD FINAL VARIANTS",
            "tagline": "TERMINAL ALLOGRAPHS • EXIT STROKES • BOUNDARY SPACING",
            "rows": [
                {"id": "CTX_FINAL_001", "prompt": "bạn",  "tag": "WORD_FINAL", "note": "Descender / Dot Below"},
                {"id": "CTX_FINAL_002", "prompt": "nam",  "tag": "WORD_FINAL", "note": "Terminal Bilabial Nasal"},
                {"id": "CTX_FINAL_003", "prompt": "nhìn", "tag": "WORD_FINAL", "note": "Double Dot / Tone Accent"},
                {"id": "CTX_FINAL_004", "prompt": "tình", "tag": "WORD_FINAL", "note": "Nét kết thúc h / terminal exit stroke; dấu huyền trên i"},
                {"id": "CTX_FINAL_005", "prompt": "mộc",  "tag": "WORD_FINAL", "note": "Circumflex & Dot Below"},
                {"id": "CTX_FINAL_006", "prompt": "hoa",  "tag": "WORD_FINAL", "note": "Open Vowel Exit Stroke"}
            ]
        }
    ]

    lines.append('  <!-- Contextual Writing Rows (16 Rows across 3 Sections) -->')
    lines.append('  <g id="writing_sections">')

    current_y = 46.0
    sec_header_h = 3.5
    gap_after_sec = 0.8
    row_w = 184.0
    row_h = 11.6
    label_h = 3.5
    row_gap = 0.5
    sec_gap = 1.8
    start_x = 13.0

    collected_metadata = []

    def escape_xml(s):
        return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    for s_idx, sec in enumerate(sections_spec):
        # Section Header Banner
        sy = current_y
        lines.append(f'    <!-- Section {sec["code"]} Banner -->')
        lines.append(f'    <g id="sec_banner_{sec["code"]}">')
        lines.append(f'      <rect x="{start_x:.2f}" y="{sy:.2f}" width="{row_w:.2f}" height="{sec_header_h:.2f}" fill="#eeeeee" stroke="#aaaaaa" stroke-width="0.25" rx="0.5"/>')
        lines.append(f'      <text x="{start_x+2.5:.2f}" y="{sy+2.4:.2f}" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#222222">{escape_xml(sec["title"])}</text>')
        lines.append(f'      <text x="{start_x+row_w-2.5:.2f}" y="{sy+2.4:.2f}" text-anchor="end" font-family="Courier, monospace" font-size="1.4" fill="#666666">{escape_xml(sec["tagline"])}</text>')
        lines.append('    </g>')
        
        current_y += sec_header_h + gap_after_sec

        for r_idx, row_item in enumerate(sec["rows"]):
            ry = current_y
            sample_id = row_item["id"]
            prompt = row_item["prompt"]
            tag = row_item["tag"]
            note = row_item["note"]

            bbox_mm = [round(start_x, 2), round(ry, 2), round(row_w, 2), round(row_h, 2)]
            writing_bbox_mm = [round(start_x, 2), round(ry + label_h, 2), round(row_w, 2), round(row_h - label_h, 2)]
            
            collected_metadata.append({
                "sample_id": sample_id,
                "prompt": prompt,
                "context_tag": tag,
                "section": sec["code"],
                "row_in_sec": r_idx + 1,
                "note": note,
                "bbox_mm": bbox_mm,
                "writing_bbox_mm": writing_bbox_mm
            })

            lines.append(f'    <!-- Row {sample_id} -->')
            lines.append(f'    <g id="row_{sample_id}">')
            # Outer Row Box
            lines.append(f'      <rect x="{start_x:.2f}" y="{ry:.2f}" width="{row_w:.2f}" height="{row_h:.2f}" fill="#ffffff" stroke="#888888" stroke-width="0.28" rx="0.5"/>')
            
            # Label Strip (Height: 3.5 mm)
            lines.append(f'      <rect x="{start_x:.2f}" y="{ry:.2f}" width="{row_w:.2f}" height="{label_h:.2f}" fill="#f4f6f8" stroke="#888888" stroke-width="0.28" rx="0.5"/>')
            lines.append(f'      <line x1="{start_x:.2f}" y1="{ry+label_h:.2f}" x2="{start_x+row_w:.2f}" y2="{ry+label_h:.2f}" stroke="#777777" stroke-width="0.25"/>')
            
            # Left: Sample ID & Context Tag
            lines.append(f'      <text x="{start_x+2.0:.2f}" y="{ry+2.5:.2f}" font-family="Courier, monospace" font-size="1.8" font-weight="bold" fill="#222222">{escape_xml(sample_id)}<tspan font-family="Helvetica, Arial, sans-serif" font-size="1.4" font-weight="normal" fill="#666666">  •  {escape_xml(tag)}</tspan></text>')
            
            # Right: Target Prompt
            lines.append(f'      <text x="{start_x+row_w-35.0:.2f}" y="{ry+2.5:.2f}" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="1.6" fill="#555555">Prompt:</text>')
            lines.append(f'      <text x="{start_x+row_w-2.0:.2f}" y="{ry+2.6:.2f}" text-anchor="end" font-family="Times New Roman, Georgia, serif" font-size="3.2" font-weight="bold" fill="#000000">{escape_xml(prompt)}</text>')
            
            # Writing Zone Guidelines
            # Local coordinates from ry:
            # ry + 4.7 mm: Ascender line (dashed)
            # ry + 6.9 mm: x-height line (dashed)
            # ry + 9.8 mm: Baseline (solid)
            # ry + 11.0 mm: Descender line (dashed)
            y_asc = ry + 4.7
            y_xh  = ry + 6.9
            y_bs  = ry + 9.8
            y_dsc = ry + 11.0

            lines.append(f'      <line x1="{start_x+1.5:.2f}" y1="{y_asc:.2f}" x2="{start_x+row_w-1.5:.2f}" y2="{y_asc:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
            lines.append(f'      <line x1="{start_x+1.5:.2f}" y1="{y_xh:.2f}" x2="{start_x+row_w-1.5:.2f}" y2="{y_xh:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
            lines.append(f'      <line x1="{start_x+1.5:.2f}" y1="{y_bs:.2f}" x2="{start_x+row_w-1.5:.2f}" y2="{y_bs:.2f}" stroke="#7e7e7e" stroke-width="0.26"/>')
            lines.append(f'      <line x1="{start_x+1.5:.2f}" y1="{y_dsc:.2f}" x2="{start_x+row_w-1.5:.2f}" y2="{y_dsc:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
            
            # Baseline edge ticks for scan registration
            lines.append(f'      <line x1="{start_x:.2f}" y1="{y_bs:.2f}" x2="{start_x+1.2:.2f}" y2="{y_bs:.2f}" stroke="#555555" stroke-width="0.35"/>')
            lines.append(f'      <line x1="{start_x+row_w-1.2:.2f}" y1="{y_bs:.2f}" x2="{start_x+row_w:.2f}" y2="{y_bs:.2f}" stroke="#555555" stroke-width="0.35"/>')
            lines.append('    </g>')

            current_y += row_h
            if r_idx < len(sec["rows"]) - 1:
                current_y += row_gap

        if s_idx < len(sections_spec) - 1:
            current_y += sec_gap

    lines.append('  </g>')

    # 6. Calibration Area (y: 256.5 to 278.5 mm, height: 22.0 mm - Identical to P01)
    lines.append('  <!-- Calibration Scale & Aspect Ratio Verification Area -->')
    lines.append('  <g id="calibration_area">')
    lines.append('    <rect x="13.0" y="256.5" width="184.0" height="22.0" fill="#fafafa" stroke="#b0b0b0" stroke-width="0.25" rx="0.8"/>')
    
    # Left Section: 50mm Ruler
    r_x = 22.0
    r_y = 270.0
    lines.append('    <!-- 50mm Precision Ruler -->')
    lines.append('    <text x="22.0" y="260.5" font-family="Helvetica, Arial, sans-serif" font-size="2.0" font-weight="bold" fill="#222222">OPTICAL SCAN CALIBRATION RULER (50.0 mm TRUE SCALE CHECK)</text>')
    lines.append(f'    <line x1="{r_x}" y1="{r_y}" x2="{r_x+50.0}" y2="{r_y}" stroke="#000000" stroke-width="0.35"/>')
    
    # Major ticks (every 10mm: 0, 10, 20, 30, 40, 50)
    for mm in range(0, 51, 10):
        tx = r_x + mm
        lines.append(f'    <line x1="{tx}" y1="{r_y-3.2}" x2="{tx}" y2="{r_y}" stroke="#000000" stroke-width="0.3"/>')
        lines.append(f'    <text x="{tx}" y="{r_y-4.0}" text-anchor="middle" font-family="Courier, monospace" font-size="1.8" font-weight="bold" fill="#111111">{mm}</text>')
    
    # Medium ticks (every 5mm)
    for mm in range(5, 50, 10):
        tx = r_x + mm
        lines.append(f'    <line x1="{tx}" y1="{r_y-2.0}" x2="{tx}" y2="{r_y}" stroke="#444444" stroke-width="0.22"/>')
        
    # Minor ticks (every 1mm)
    for mm in range(1, 50):
        if mm % 5 != 0:
            tx = r_x + mm
            lines.append(f'    <line x1="{tx}" y1="{r_y-1.0}" x2="{tx}" y2="{r_y}" stroke="#777777" stroke-width="0.14"/>')
            
    lines.append('    <text x="22.0" y="274.2" font-family="Helvetica, Arial, sans-serif" font-size="1.5" fill="#555555">Pilot check: 50.0 ± 0.2 mm span • PILOT ENGINEERING THRESHOLD — TO BE VALIDATED</text>')

    # Right Section: 20x20mm Calibration Square
    sq_x = 125.0
    sq_y = 257.5
    lines.append('    <!-- 20.0 x 20.0 mm Calibration Square -->')
    lines.append(f'    <rect x="{sq_x}" y="{sq_y}" width="20.0" height="20.0" fill="#ffffff" stroke="#000000" stroke-width="0.35"/>')
    # Inner crosshairs
    lines.append(f'    <line x1="{sq_x+10.0}" y1="{sq_y+7.0}" x2="{sq_x+10.0}" y2="{sq_y+13.0}" stroke="#888888" stroke-width="0.2"/>')
    lines.append(f'    <line x1="{sq_x+7.0}" y1="{sq_y+10.0}" x2="{sq_x+13.0}" y2="{sq_y+10.0}" stroke="#888888" stroke-width="0.2"/>')
    lines.append(f'    <text x="{sq_x+10.0}" y="{sq_y+11.5}" text-anchor="middle" font-family="Courier, monospace" font-size="1.5" fill="#444444">20×20</text>')
    
    # Text next to square
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+4.2}" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#111111">CALIBRATION SQUARE</text>')
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+7.8}" font-family="Helvetica, Arial, sans-serif" font-size="1.6" fill="#333333">Width = Height = 20.0 mm</text>')
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+11.2}" font-family="Helvetica, Arial, sans-serif" font-size="1.6" fill="#333333">Aspect Ratio: 1.000 ± 0.005</text>')
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+14.2}" font-family="Courier, monospace" font-size="1.35" font-weight="bold" fill="#777777">PILOT ENG THRESHOLD — TO BE VALIDATED</text>')
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+17.5}" font-family="Helvetica, Arial, sans-serif" font-size="1.5" fill="#555555">Supports checking X/Y scale consistency</text>')
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+20.0}" font-family="Helvetica, Arial, sans-serif" font-size="1.5" fill="#555555">and scan distortion.</text>')
    lines.append('  </g>')

    # 7. Footer - P02 Pilot Candidate wording
    lines.append('  <!-- Footer Section (between bottom fiducials) -->')
    lines.append('  <g id="footer">')
    lines.append('    <text x="22.0" y="282.5" font-family="Helvetica, Arial, sans-serif" font-size="1.8" fill="#333333"><tspan font-weight="bold">OmniDraw Research Dataset</tspan> • Form P02 Demo v0.1 (Pilot Candidate — Not Approved for Formal Data Collection)</text>')
    lines.append('    <text x="22.0" y="285.5" font-family="Courier, monospace" font-size="1.6" fill="#666666">SCAN TARGET: Flatbed 600 DPI • 24-bit RGB / 8-bit Grayscale • Lossless PNG • True Scale 1:1 • No Auto-Contrast</text>')
    lines.append('  </g>')

    lines.append('</svg>')
    return '\n'.join(lines), collected_metadata

if __name__ == '__main__':
    svg_content, metadata = build_p02_svg()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_svg = os.path.join(script_dir, 'collection_sheet_p02.svg')
    with open(target_svg, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {target_svg} ({len(svg_content)} bytes)")
    print(f"Total rows collected: {len(metadata)}")
    for item in metadata:
        print(f"  {item['sample_id']}: bbox={item['bbox_mm']}, writing_bbox={item['writing_bbox_mm']}")
