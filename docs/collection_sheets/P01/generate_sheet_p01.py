import os

def build_svg():
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297" width="210mm" height="297mm">')
    
    # 1. White Paper Surface (A4 Portrait: 210 x 297 mm)
    lines.append('  <!-- Paper Surface -->')
    lines.append('  <rect x="0" y="0" width="210" height="297" fill="#ffffff"/>')
    
    # 2. Fiducial Markers: 5.0 x 5.0 mm at (12,12), (193,12), (12,280), (193,280)
    # Exact center span: horizontal 181.0 mm, vertical 268.0 mm
    lines.append('  <!-- 4 Corner Fiducial Markers (5.0 x 5.0 mm) -->')
    lines.append('  <g id="fiducials">')
    lines.append('    <rect id="fiducial_tl" x="12.0" y="12.0" width="5.0" height="5.0" fill="#000000"/>')
    lines.append('    <rect id="fiducial_tr" x="193.0" y="12.0" width="5.0" height="5.0" fill="#000000"/>')
    lines.append('    <rect id="fiducial_bl" x="12.0" y="280.0" width="5.0" height="5.0" fill="#000000"/>')
    lines.append('    <rect id="fiducial_br" x="193.0" y="280.0" width="5.0" height="5.0" fill="#000000"/>')
    lines.append('  </g>')

    # 3. Header Section (y: 13 to 36 mm)
    lines.append('  <!-- Header -->')
    lines.append('  <g id="header">')
    lines.append('    <text x="21.0" y="16.5" font-family="Helvetica, Arial, sans-serif" font-size="4.2" font-weight="bold" fill="#111111" letter-spacing="0.2">OMNIDRAW RESEARCH DATASET</text>')
    lines.append('    <text x="21.0" y="21.0" font-family="Helvetica, Arial, sans-serif" font-size="2.8" font-weight="bold" fill="#333333">P01 — Character &amp; Diacritic Collection Sheet</text>')
    lines.append('    <text x="21.0" y="24.8" font-family="Courier, monospace" font-size="2.0" fill="#555555">FORM VERSION: ODW-HW-P01-DEMO-v0.2 • PROTOCOL: DOC-SPEC-08-DATASET</text>')
    
    # Right-aligned header notices: updated to RESEARCH USE ONLY and PILOT CANDIDATE
    lines.append('    <text x="189.0" y="16.5" text-anchor="end" font-family="Courier, monospace" font-size="1.9" font-weight="bold" fill="#444444">RESEARCH USE ONLY</text>')
    lines.append('    <text x="189.0" y="20.5" text-anchor="end" font-family="Courier, monospace" font-size="1.9" fill="#666666">ANONYMIZED PROTOCOL • NO PII COLLECTED</text>')
    lines.append('    <text x="189.0" y="24.5" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#c93b2b">PILOT CANDIDATE — NOT APPROVED FOR FORMAL DATA COLLECTION</text>')
    
    # Thin divider
    lines.append('    <line x1="21.0" y1="26.8" x2="189.0" y2="26.8" stroke="#cccccc" stroke-width="0.25"/>')
    
    # Metadata Fields Box (No PII! Page is strictly P01)
    lines.append('    <rect x="13.0" y="28.5" width="184.0" height="7.5" fill="#f8f9fa" stroke="#cccccc" stroke-width="0.25" rx="0.6"/>')
    lines.append('    <text x="16.0" y="33.5" font-family="Helvetica, Arial, sans-serif" font-size="2.3" font-weight="bold" fill="#222222">Writer ID: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">W_________</tspan></text>')
    lines.append('    <text x="64.0" y="33.5" font-family="Helvetica, Arial, sans-serif" font-size="2.3" font-weight="bold" fill="#222222">Session: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">S______</tspan></text>')
    lines.append('    <text x="105.0" y="33.5" font-family="Helvetica, Arial, sans-serif" font-size="2.3" font-weight="bold" fill="#222222">Page: <tspan font-family="Courier, monospace" font-weight="bold" fill="#111111">P01</tspan></text>')
    lines.append('    <text x="145.0" y="33.5" font-family="Helvetica, Arial, sans-serif" font-size="2.3" font-weight="bold" fill="#222222">Date: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">_____ / _____ / 202___</tspan></text>')
    lines.append('  </g>')

    # 4. Instructions Box (y: 38.0 to 51.5 mm, height: 13.5 mm)
    lines.append('  <!-- Instructions -->')
    lines.append('  <g id="instructions">')
    lines.append('    <rect x="13.0" y="38.0" width="184.0" height="13.5" fill="#ffffff" stroke="#b0b0b0" stroke-width="0.3" rx="0.8"/>')
    lines.append('    <rect x="13.0" y="38.0" width="184.0" height="3.6" fill="#eceff1" stroke="#b0b0b0" stroke-width="0.3" rx="0.8"/>')
    lines.append('    <text x="16.0" y="40.7" font-family="Helvetica, Arial, sans-serif" font-size="2.1" font-weight="bold" fill="#111111">HƯỚNG DẪN VIẾT MẪU / WRITING INSTRUCTIONS</text>')
    lines.append('    <text x="194.0" y="40.7" text-anchor="end" font-family="Courier, monospace" font-size="1.8" fill="#555555">SPECIFICATION: 0.5MM BLACK GEL PEN</text>')
    
    # 2 columns of instructions
    lines.append('    <text x="16.0" y="44.5" font-family="Helvetica, Arial, sans-serif" font-size="1.9" fill="#333333">• Viết bằng nét chữ tự nhiên của bạn; tuyệt đối KHÔNG cố tình nắn nót đẹp hơn bình thường.</text>')
    lines.append('    <text x="16.0" y="48.2" font-family="Helvetica, Arial, sans-serif" font-size="1.9" fill="#333333">• Dùng bút gel đen 0.5 mm do nhóm cung cấp (hoặc tương thích); không dùng bút xanh, dạ hoặc chì.</text>')
    lines.append('    <text x="106.0" y="44.5" font-family="Helvetica, Arial, sans-serif" font-size="1.9" fill="#333333">• Viết đúng ký tự Target yêu cầu; chỉ viết trong vùng 4 đường kẻ; KHÔNG chạm vào dải nhãn trên.</text>')
    lines.append('    <text x="106.0" y="48.2" font-family="Helvetica, Arial, sans-serif" font-size="1.9" fill="#333333">• Không viết đè, không tô lại nét lỗi, không dùng bút xóa; không ký tên hay viết thông tin cá nhân.</text>')
    lines.append('  </g>')

    # 5. Character Grid: 4 columns x 6 rows = 24 cells
    cells_data = [
        # Row 1: Base Characters
        {"id": "BASE_001", "target": "a", "label_extra": ""},
        {"id": "BASE_002", "target": "e", "label_extra": ""},
        {"id": "BASE_003", "target": "o", "label_extra": ""},
        {"id": "BASE_004", "target": "u", "label_extra": ""},
        # Row 2: Structural Diacritics
        {"id": "STR_001",  "target": "ă", "label_extra": ""},
        {"id": "STR_002",  "target": "â", "label_extra": ""},
        {"id": "STR_003",  "target": "ê", "label_extra": ""},
        {"id": "STR_004",  "target": "ơ", "label_extra": ""},
        # Row 3: Tone Diacritics
        {"id": "TONE_001", "target": "á", "label_extra": ""},
        {"id": "TONE_002", "target": "à", "label_extra": ""},
        {"id": "TONE_003", "target": "ả", "label_extra": ""},
        {"id": "TONE_004", "target": "ạ", "label_extra": ""},
        # Row 4: Secondary Stroke & Ligatures
        {"id": "SEC_001",  "target": "đ", "label_extra": ""},
        {"id": "STR_005",  "target": "ư", "label_extra": ""},
        {"id": "BASE_005", "target": "n", "label_extra": ""},
        {"id": "BASE_006", "target": "m", "label_extra": ""},
        # Row 5: Two-level Complex Diacritics
        {"id": "CMP_001",  "target": "ắ", "label_extra": ""},
        {"id": "CMP_002",  "target": "ấ", "label_extra": ""},
        {"id": "CMP_003",  "target": "ố", "label_extra": ""},
        {"id": "CMP_004",  "target": "ở", "label_extra": ""},
        # Row 6: Repetition Trials (Intra-writer variation)
        {"id": "REP_001",  "target": "ế", "label_extra": "(Trial A)"},
        {"id": "REP_002",  "target": "ế", "label_extra": "(Trial B)"},
        {"id": "REP_003",  "target": "ử", "label_extra": "(Trial A)"},
        {"id": "REP_004",  "target": "ử", "label_extra": "(Trial B)"}
    ]

    lines.append('  <!-- 24 Character Writing Cells -->')
    lines.append('  <g id="character_grid">')
    
    col_w = 43.5
    col_gap = 3.333333
    row_h = 31.0
    row_gap = 3.0
    start_x = 13.0
    start_y = 53.5

    for idx, c in enumerate(cells_data):
        row = idx // 4
        col = idx % 4
        cx = start_x + col * (col_w + col_gap)
        cy = start_y + row * (row_h + row_gap)
        
        # Cell border
        lines.append(f'    <!-- Cell {c["id"]} -->')
        lines.append(f'    <g id="cell_{c["id"]}">')
        lines.append(f'      <rect x="{cx:.2f}" y="{cy:.2f}" width="{col_w:.2f}" height="{row_h:.2f}" fill="#ffffff" stroke="#888888" stroke-width="0.3" rx="0.5"/>')
        
        # Upper label strip (Height: 6.5 mm)
        lines.append(f'      <rect x="{cx:.2f}" y="{cy:.2f}" width="{col_w:.2f}" height="6.5" fill="#f4f6f8" stroke="#888888" stroke-width="0.3" rx="0.5"/>')
        lines.append(f'      <line x1="{cx:.2f}" y1="{cy+6.5:.2f}" x2="{cx+col_w:.2f}" y2="{cy+6.5:.2f}" stroke="#777777" stroke-width="0.3"/>')
        
        # Label Strip Text
        extra_str = f" {c['label_extra']}" if c['label_extra'] else ""
        lines.append(f'      <text x="{cx+1.8:.2f}" y="{cy+4.5:.2f}" font-family="Courier, monospace" font-size="2.0" font-weight="bold" fill="#222222">{c["id"]}<tspan font-family="Helvetica, Arial, sans-serif" font-size="1.6" font-weight="normal" fill="#666666">{extra_str}</tspan></text>')
        lines.append(f'      <text x="{cx+34.5:.2f}" y="{cy+4.5:.2f}" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="2.0" fill="#555555">Target:</text>')
        lines.append(f'      <text x="{cx+39.5:.2f}" y="{cy+5.2:.2f}" text-anchor="middle" font-family="Times New Roman, Georgia, serif" font-size="4.2" font-weight="bold" fill="#000000">{c["target"]}</text>')
        
        # Guide lines
        y_asc = cy + 10.5
        y_xh  = cy + 16.5
        y_bs  = cy + 22.5
        y_dsc = cy + 27.5

        lines.append(f'      <line x1="{cx+1.5:.2f}" y1="{y_asc:.2f}" x2="{cx+col_w-1.5:.2f}" y2="{y_asc:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        lines.append(f'      <line x1="{cx+1.5:.2f}" y1="{y_xh:.2f}" x2="{cx+col_w-1.5:.2f}" y2="{y_xh:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        lines.append(f'      <line x1="{cx+1.5:.2f}" y1="{y_bs:.2f}" x2="{cx+col_w-1.5:.2f}" y2="{y_bs:.2f}" stroke="#7e7e7e" stroke-width="0.28"/>')
        lines.append(f'      <line x1="{cx+1.5:.2f}" y1="{y_dsc:.2f}" x2="{cx+col_w-1.5:.2f}" y2="{y_dsc:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        
        lines.append(f'      <line x1="{cx:.2f}" y1="{y_bs:.2f}" x2="{cx+1.0:.2f}" y2="{y_bs:.2f}" stroke="#555555" stroke-width="0.35"/>')
        lines.append(f'      <line x1="{cx+col_w-1.0:.2f}" y1="{y_bs:.2f}" x2="{cx+col_w:.2f}" y2="{y_bs:.2f}" stroke="#555555" stroke-width="0.35"/>')
        lines.append(f'    </g>')
    lines.append('  </g>')

    # 6. Calibration Area (y: 256.5 to 278.5 mm, height: 22.0 mm)
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
            
    lines.append('    <text x="22.0" y="274.2" font-family="Helvetica, Arial, sans-serif" font-size="1.6" fill="#555555">Measure with physical vernier caliper / ruler: 0 to 50 mm span must equal exactly 50.0 mm.</text>')

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
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+4.8}" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#111111">CALIBRATION SQUARE</text>')
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+8.5}" font-family="Helvetica, Arial, sans-serif" font-size="1.6" fill="#333333">Width = Height = 20.0 mm</text>')
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+12.0}" font-family="Helvetica, Arial, sans-serif" font-size="1.6" fill="#333333">Aspect Ratio: 1.000 ± 0.005</text>')
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+15.5}" font-family="Helvetica, Arial, sans-serif" font-size="1.6" fill="#555555">Supports checking X/Y scale consistency</text>')
    lines.append(f'    <text x="{sq_x+22.5}" y="{sq_y+18.5}" font-family="Helvetica, Arial, sans-serif" font-size="1.6" fill="#555555">and scan distortion.</text>')
    lines.append('  </g>')

    # 7. Footer - Pilot Candidate wording
    lines.append('  <!-- Footer Section (between bottom fiducials) -->')
    lines.append('  <g id="footer">')
    lines.append('    <text x="22.0" y="282.5" font-family="Helvetica, Arial, sans-serif" font-size="1.8" fill="#333333"><tspan font-weight="bold">OmniDraw Research Dataset</tspan> • Form P01 Demo v0.2 (Pilot Candidate — Not Approved for Formal Data Collection)</text>')
    lines.append('    <text x="22.0" y="285.5" font-family="Courier, monospace" font-size="1.6" fill="#666666">SCAN TARGET: Flatbed 600 DPI • 24-bit RGB / 8-bit Grayscale • Lossless PNG • True Scale 1:1 • No Auto-Contrast</text>')
    lines.append('  </g>')

    lines.append('</svg>')
    return '\n'.join(lines)

if __name__ == '__main__':
    svg_content = build_svg()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_svg = os.path.join(script_dir, 'collection_sheet_p01.svg')
    with open(target_svg, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {target_svg} ({len(svg_content)} bytes)")
