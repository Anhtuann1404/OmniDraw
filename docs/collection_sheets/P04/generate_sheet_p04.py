import os

def build_p04_svg():
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297" width="210mm" height="297mm">')
    
    # 1. White Paper Surface (A4 Portrait: 210 x 297 mm)
    lines.append('  <!-- Paper Surface -->')
    lines.append('  <rect x="0" y="0" width="210" height="297" fill="#ffffff"/>')
    
    # 2. Fiducial Markers: 5.0 x 5.0 mm at (12,12), (193,12), (12,280), (193,280)
    # Center coordinates: TL [14.50, 14.50], TR [195.50, 14.50], BL [14.50, 282.50], BR [195.50, 282.50]
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
    lines.append('    <text x="21.0" y="20.2" font-family="Helvetica, Arial, sans-serif" font-size="2.7" font-weight="bold" fill="#333333">P04 — Natural Paragraph Writing Collection Sheet</text>')
    lines.append('    <text x="21.0" y="23.8" font-family="Courier, monospace" font-size="1.9" fill="#555555">FORM VERSION: ODW-HW-P04-DEMO-v0.1 • PROTOCOL: DOC-SPEC-08-DATASET</text>')
    
    # Right-aligned header notices
    lines.append('    <text x="189.0" y="16.0" text-anchor="end" font-family="Courier, monospace" font-size="1.9" font-weight="bold" fill="#444444">RESEARCH USE ONLY</text>')
    lines.append('    <text x="189.0" y="19.8" text-anchor="end" font-family="Courier, monospace" font-size="1.9" fill="#666666">ANONYMIZED PROTOCOL • NO PII COLLECTED</text>')
    lines.append('    <text x="189.0" y="23.8" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#c93b2b">PILOT CANDIDATE — NOT APPROVED FOR FORMAL DATA COLLECTION</text>')
    
    # Thin divider
    lines.append('    <line x1="21.0" y1="25.5" x2="189.0" y2="25.5" stroke="#cccccc" stroke-width="0.25"/>')
    
    # Metadata Fields Box (No PII! Page is strictly P04)
    lines.append('    <rect x="13.0" y="27.0" width="184.0" height="6.5" fill="#f8f9fa" stroke="#cccccc" stroke-width="0.25" rx="0.6"/>')
    lines.append('    <text x="16.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Writer ID: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">W_________</tspan></text>')
    lines.append('    <text x="64.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Session: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">S______</tspan></text>')
    lines.append('    <text x="105.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Page: <tspan font-family="Courier, monospace" font-weight="bold" fill="#111111">P04</tspan></text>')
    lines.append('    <text x="145.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Date: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">_____ / _____ / 202___</tspan></text>')
    lines.append('  </g>')

    # 4. Instructions Box (y: 35.0 to 45.0 mm, height: 10.0 mm)
    lines.append('  <!-- Instructions -->')
    lines.append('  <g id="instructions">')
    lines.append('    <rect x="13.0" y="35.0" width="184.0" height="10.0" fill="#ffffff" stroke="#b0b0b0" stroke-width="0.28" rx="0.6"/>')
    lines.append('    <rect x="13.0" y="35.0" width="184.0" height="3.0" fill="#eceff1" stroke="#b0b0b0" stroke-width="0.28" rx="0.6"/>')
    lines.append('    <text x="16.0" y="37.2" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#111111">HƯỚNG DẪN VIẾT MẪU / WRITING INSTRUCTIONS</text>')
    lines.append('    <text x="194.0" y="37.2" text-anchor="end" font-family="Courier, monospace" font-size="1.6" fill="#555555">SPECIFICATION: 0.5MM BLACK GEL PEN</text>')
    
    # 2 columns of instructions (natural paragraph writing, no forced wrap, no fatigue pressure)
    lines.append('    <text x="16.0" y="40.3" font-family="Helvetica, Arial, sans-serif" font-size="1.7" fill="#333333">• Viết bằng nét chữ tự nhiên của bạn; không cố tình nắn nót đẹp hơn bình thường.</text>')
    lines.append('    <text x="16.0" y="43.2" font-family="Helvetica, Arial, sans-serif" font-size="1.7" fill="#333333">• Dùng bút gel đen 0.5 mm do nhóm cung cấp; chép lại toàn bộ đoạn văn bên dưới.</text>')
    lines.append('    <text x="106.0" y="40.3" font-family="Helvetica, Arial, sans-serif" font-size="1.7" fill="#333333">• Viết theo nhịp và kích cỡ tự nhiên; tự xuống dòng khi cần, không cố ép vào một dòng.</text>')
    lines.append('    <text x="106.0" y="43.2" font-family="Helvetica, Arial, sans-serif" font-size="1.7" fill="#333333">• Không cố nối nét, không cố giữ đều tuyệt đối, không tô lại nét; không ghi thông tin cá nhân.</text>')
    lines.append('  </g>')

    # 5. Natural Paragraph Block Specification
    # PARA_001
    paragraph_data = {
        "id": "PARA_001",
        "section": "A",
        "section_title": "SECTION A — CONTINUOUS PARAGRAPH",
        "prompt": "Mỗi dòng chữ nắn nót trên trang giấy trắng là nhịp cầu nối liền những tấm lòng thân thương, gửi gắm trọn vẹn niềm tin cùng bao ước vọng tốt đẹp nhất.",
        "context_tag": "NATURAL_PARAGRAPH",
        "research_note": "Paragraph-level spatial flow, long-range baseline stability, slant consistency, word/line spacing, natural wrap"
    }

    prompt_lines = [
        "Mỗi dòng chữ nắn nót trên trang giấy trắng là nhịp cầu nối liền",
        "những tấm lòng thân thương, gửi gắm trọn vẹn niềm tin cùng",
        "bao ước vọng tốt đẹp nhất."
    ]

    block_x = 13.0
    block_y = 48.0
    block_w = 184.0
    prompt_h = 30.0
    wz_h = 150.0
    block_h = prompt_h + wz_h  # 180.0 mm
    wz_y = block_y + prompt_h  # 78.0 mm
    line_slot_h = 30.0         # 5 lines * 30.0 = 150.0 mm

    def escape_xml(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    bbox_mm = [block_x, block_y, block_w, block_h]
    prompt_bbox_mm = [block_x, block_y, block_w, prompt_h]
    writing_bbox_mm = [block_x, wz_y, block_w, wz_h]

    line_bboxes = [
        [block_x, wz_y + i * line_slot_h, block_w, line_slot_h]
        for i in range(5)
    ]

    collected_metadata = {
        "sample_id": paragraph_data["id"],
        "prompt": paragraph_data["prompt"],
        "context_tag": paragraph_data["context_tag"],
        "word_count": len(paragraph_data["prompt"].split()),
        "unicode_codepoint_count": len(paragraph_data["prompt"]),
        "research_note": paragraph_data["research_note"],
        "bbox_mm": bbox_mm,
        "prompt_bbox_mm": prompt_bbox_mm,
        "writing_bbox_mm": writing_bbox_mm,
        "line_1_bbox_mm": line_bboxes[0],
        "line_2_bbox_mm": line_bboxes[1],
        "line_3_bbox_mm": line_bboxes[2],
        "line_4_bbox_mm": line_bboxes[3],
        "line_5_bbox_mm": line_bboxes[4],
        "line_baselines_y_mm": [wz_y + i * line_slot_h + 16.0 for i in range(5)]
    }

    lines.append('  <!-- Natural Paragraph Block PARA_001 -->')
    lines.append(f'  <g id="block_{paragraph_data["id"]}">')
    
    # Outer Block Frame
    lines.append(f'    <rect x="{block_x:.2f}" y="{block_y:.2f}" width="{block_w:.2f}" height="{block_h:.2f}" fill="#ffffff" stroke="#888888" stroke-width="0.3" rx="0.6"/>')
    
    # Prompt Region (Height: 30.0 mm, y: 48.0 to 78.0 mm)
    lines.append(f'    <rect x="{block_x:.2f}" y="{block_y:.2f}" width="{block_w:.2f}" height="{prompt_h:.2f}" fill="#f4f6f8" stroke="#888888" stroke-width="0.3" rx="0.6"/>')
    lines.append(f'    <line x1="{block_x:.2f}" y1="{wz_y:.2f}" x2="{block_x+block_w:.2f}" y2="{wz_y:.2f}" stroke="#777777" stroke-width="0.28"/>')
    
    # Prompt Top Meta Row
    lines.append(f'    <text x="{block_x+3.0:.2f}" y="{block_y+4.2:.2f}" font-family="Courier, monospace" font-size="2.2" font-weight="bold" fill="#222222">{paragraph_data["id"]}<tspan font-size="1.5" font-weight="normal" fill="#666666">  •  {paragraph_data["context_tag"]}</tspan></text>')
    lines.append(f'    <text x="{block_x+block_w-3.0:.2f}" y="{block_y+4.2:.2f}" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#333333">{paragraph_data["section_title"]}</text>')
    
    # Sub-divider in Prompt Region
    lines.append(f'    <line x1="{block_x+2.0:.2f}" y1="{block_y+5.8:.2f}" x2="{block_x+block_w-2.0:.2f}" y2="{block_y+5.8:.2f}" stroke="#d8d8d8" stroke-width="0.2"/>')
    
    # Prompt Label
    lines.append(f'    <text x="{block_x+3.0:.2f}" y="{block_y+9.8:.2f}" font-family="Helvetica, Arial, sans-serif" font-size="1.8" font-weight="bold" fill="#444444">Prompt (Đoạn văn mẫu chép tay):</text>')
    
    # 3-line machine printed prompt text (Times New Roman, regular / bold)
    lines.append(f'    <text x="{block_x+4.0:.2f}" y="{block_y+15.5:.2f}" font-family="Times New Roman, Georgia, serif" font-size="2.7" font-weight="bold" fill="#111111">"{escape_xml(prompt_lines[0])}</text>')
    lines.append(f'    <text x="{block_x+5.2:.2f}" y="{block_y+20.8:.2f}" font-family="Times New Roman, Georgia, serif" font-size="2.7" font-weight="bold" fill="#111111">{escape_xml(prompt_lines[1])}</text>')
    lines.append(f'    <text x="{block_x+5.2:.2f}" y="{block_y+26.1:.2f}" font-family="Times New Roman, Georgia, serif" font-size="2.7" font-weight="bold" fill="#111111">{escape_xml(prompt_lines[2])}"</text>')

    # Writing Zone: 5 Natural Writing Lines (y: 78.0 to 228.0 mm)
    # Each slot is 30.0 mm high.
    # Within slot:
    # ascender: slot_y + 7.0 mm
    # x-height: slot_y + 11.0 mm (ascender span = 4.0 mm)
    # baseline: slot_y + 16.0 mm (x-height span = 5.0 mm)
    # descender: slot_y + 20.0 mm (descender span = 4.0 mm)
    # clear gap to next line ascender = (slot_y + 30.0 + 7.0) - (slot_y + 20.0) = 17.0 mm
    # line pitch = 30.0 mm
    for i in range(5):
        slot_y = wz_y + i * line_slot_h
        asc_y = slot_y + 7.0
        xh_y  = slot_y + 11.0
        bs_y  = slot_y + 16.0
        dsc_y = slot_y + 20.0

        # Guidelines across width (x: 15.0 to 195.0 mm)
        lines.append(f'    <!-- Line {i+1} Guidelines (Baseline Y = {bs_y:.2f} mm) -->')
        lines.append(f'    <line x1="{block_x+2.0:.2f}" y1="{asc_y:.2f}" x2="{block_x+block_w-2.0:.2f}" y2="{asc_y:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        lines.append(f'    <line x1="{block_x+2.0:.2f}" y1="{xh_y:.2f}" x2="{block_x+block_w-2.0:.2f}" y2="{xh_y:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        lines.append(f'    <line x1="{block_x+2.0:.2f}" y1="{bs_y:.2f}" x2="{block_x+block_w-2.0:.2f}" y2="{bs_y:.2f}" stroke="#7e7e7e" stroke-width="0.28"/>')
        lines.append(f'    <line x1="{block_x+2.0:.2f}" y1="{dsc_y:.2f}" x2="{block_x+block_w-2.0:.2f}" y2="{dsc_y:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        
        # Edge registration ticks on baseline
        lines.append(f'    <line x1="{block_x:.2f}" y1="{bs_y:.2f}" x2="{block_x+1.2:.2f}" y2="{bs_y:.2f}" stroke="#555555" stroke-width="0.35"/>')
        lines.append(f'    <line x1="{block_x+block_w-1.2:.2f}" y1="{bs_y:.2f}" x2="{block_x+block_w:.2f}" y2="{bs_y:.2f}" stroke="#555555" stroke-width="0.35"/>')

    lines.append('  </g>')

    # 6. Calibration Area (y: 256.5 to 278.5 mm, height: 22.0 mm - Identical to P01/P02/P03)
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

    # 7. Footer - P04 Pilot Candidate wording
    lines.append('  <!-- Footer Section (between bottom fiducials) -->')
    lines.append('  <g id="footer">')
    lines.append('    <text x="22.0" y="282.5" font-family="Helvetica, Arial, sans-serif" font-size="1.8" fill="#333333"><tspan font-weight="bold">OmniDraw Research Dataset</tspan> • Form P04 Demo v0.1 (Pilot Candidate — Not Approved for Formal Data Collection)</text>')
    lines.append('    <text x="22.0" y="285.5" font-family="Courier, monospace" font-size="1.6" fill="#666666">SCAN TARGET: Flatbed 600 DPI • 24-bit RGB / 8-bit Grayscale • Lossless PNG • True Scale 1:1 • No Auto-Contrast</text>')
    lines.append('  </g>')

    lines.append('</svg>')
    return '\n'.join(lines), collected_metadata

if __name__ == '__main__':
    svg_content, metadata = build_p04_svg()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_svg = os.path.join(script_dir, 'collection_sheet_p04.svg')
    with open(target_svg, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {target_svg} ({len(svg_content)} bytes)")
    print(f"Sample ID: {metadata['sample_id']}")
    print(f"  Prompt: {metadata['prompt']}")
    print(f"  Words: {metadata['word_count']} • Unicode code points: {metadata['unicode_codepoint_count']}")
    print(f"  bbox_mm: {metadata['bbox_mm']}")
    print(f"  prompt_bbox_mm: {metadata['prompt_bbox_mm']}")
    print(f"  writing_bbox_mm: {metadata['writing_bbox_mm']}")
    for i in range(5):
        print(f"  line_{i+1}_bbox_mm: {metadata[f'line_{i+1}_bbox_mm']} (Baseline Y={metadata['line_baselines_y_mm'][i]} mm)")
