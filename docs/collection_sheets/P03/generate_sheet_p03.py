import os

def build_p03_svg():
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
    lines.append('    <text x="21.0" y="20.2" font-family="Helvetica, Arial, sans-serif" font-size="2.7" font-weight="bold" fill="#333333">P03 — Sentence Flow &amp; Pangram Collection Sheet</text>')
    lines.append('    <text x="21.0" y="23.8" font-family="Courier, monospace" font-size="1.9" fill="#555555">FORM VERSION: ODW-HW-P03-DEMO-v0.1 • PROTOCOL: DOC-SPEC-08-DATASET</text>')
    
    # Right-aligned header notices
    lines.append('    <text x="189.0" y="16.0" text-anchor="end" font-family="Courier, monospace" font-size="1.9" font-weight="bold" fill="#444444">RESEARCH USE ONLY</text>')
    lines.append('    <text x="189.0" y="19.8" text-anchor="end" font-family="Courier, monospace" font-size="1.9" fill="#666666">ANONYMIZED PROTOCOL • NO PII COLLECTED</text>')
    lines.append('    <text x="189.0" y="23.8" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#c93b2b">PILOT CANDIDATE — NOT APPROVED FOR FORMAL DATA COLLECTION</text>')
    
    # Thin divider
    lines.append('    <line x1="21.0" y1="25.5" x2="189.0" y2="25.5" stroke="#cccccc" stroke-width="0.25"/>')
    
    # Metadata Fields Box (No PII! Page is strictly P03)
    lines.append('    <rect x="13.0" y="27.0" width="184.0" height="6.5" fill="#f8f9fa" stroke="#cccccc" stroke-width="0.25" rx="0.6"/>')
    lines.append('    <text x="16.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Writer ID: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">W_________</tspan></text>')
    lines.append('    <text x="64.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Session: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">S______</tspan></text>')
    lines.append('    <text x="105.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Page: <tspan font-family="Courier, monospace" font-weight="bold" fill="#111111">P03</tspan></text>')
    lines.append('    <text x="145.0" y="31.5" font-family="Helvetica, Arial, sans-serif" font-size="2.2" font-weight="bold" fill="#222222">Date: <tspan font-family="Courier, monospace" font-weight="normal" fill="#555555">_____ / _____ / 202___</tspan></text>')
    lines.append('  </g>')

    # 4. Instructions Box (y: 35.0 to 45.0 mm, height: 10.0 mm)
    lines.append('  <!-- Instructions -->')
    lines.append('  <g id="instructions">')
    lines.append('    <rect x="13.0" y="35.0" width="184.0" height="10.0" fill="#ffffff" stroke="#b0b0b0" stroke-width="0.28" rx="0.6"/>')
    lines.append('    <rect x="13.0" y="35.0" width="184.0" height="3.0" fill="#eceff1" stroke="#b0b0b0" stroke-width="0.28" rx="0.6"/>')
    lines.append('    <text x="16.0" y="37.2" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#111111">HƯỚNG DẪN VIẾT MẪU / WRITING INSTRUCTIONS</text>')
    lines.append('    <text x="194.0" y="37.2" text-anchor="end" font-family="Courier, monospace" font-size="1.6" fill="#555555">SPECIFICATION: 0.5MM BLACK GEL PEN</text>')
    
    # 2 columns of instructions (reflecting natural flow, no forced ligatures, natural wrap allowed)
    lines.append('    <text x="16.0" y="40.3" font-family="Helvetica, Arial, sans-serif" font-size="1.7" fill="#333333">• Viết bằng nét chữ tự nhiên; không cố tình nắn nót đẹp hơn bình thường.</text>')
    lines.append('    <text x="16.0" y="43.2" font-family="Helvetica, Arial, sans-serif" font-size="1.7" fill="#333333">• Dùng bút gel đen 0.5 mm do nhóm cung cấp (hoặc tương thích); viết lại đầy đủ câu.</text>')
    lines.append('    <text x="106.0" y="40.3" font-family="Helvetica, Arial, sans-serif" font-size="1.7" fill="#333333">• Viết theo nhịp tự nhiên; khi hết dòng 1, tự nhiên xuống dòng 2 (natural wrap).</text>')
    lines.append('    <text x="106.0" y="43.2" font-family="Helvetica, Arial, sans-serif" font-size="1.7" fill="#333333">• Không cố nối nét, không cố giữ khoảng cách đều, không tô lại nét; không ghi thông tin cá nhân.</text>')
    lines.append('  </g>')

    # 5. Sentence Prompts Specification
    sentences = [
        {
            "id": "SENT_001",
            "section": "A",
            "section_title": "SECTION A — SENTENCE 01",
            "prompt": "Do bạch kim rất quý nên qua thời gian phong thổ vẫn giữ màu sáng rực rỡ.",
            "context_tag": "SENTENCE_FLOW / PANGRAM_SET",
            "research_note": "Continuous sentence flow, word spacing, diacritic placement, baseline stability"
        },
        {
            "id": "SENT_002",
            "section": "B",
            "section_title": "SECTION B — SENTENCE 02",
            "prompt": "Cậu bé xinh đẹp này phóng vèo qua dãy phố cổ mù sương.",
            "context_tag": "SENTENCE_FLOW / PANGRAM_SET",
            "research_note": "Mixed character shapes, spacing, ascender/descender behavior, sentence rhythm"
        },
        {
            "id": "SENT_003",
            "section": "C",
            "section_title": "SECTION C — SENTENCE 03",
            "prompt": "Hoàng tử nhảy múa cùng các cô gái vùng biển xanh biếc.",
            "context_tag": "SENTENCE_FLOW / PANGRAM_SET",
            "research_note": "Continuous writing, multi-word spacing, diacritic-rich flow, line stability"
        }
    ]

    lines.append('  <!-- Sentence Flow Blocks (3 Blocks: SENT_001, SENT_002, SENT_003) -->')
    lines.append('  <g id="sentence_blocks">')

    current_y = 48.0
    block_w = 184.0
    block_h = 58.0
    prompt_h = 12.0
    writing_h = block_h - prompt_h  # 46.0 mm
    block_gap = 8.0
    start_x = 13.0

    collected_metadata = []

    def escape_xml(s):
        return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    for s_idx, sent in enumerate(sentences):
        by = current_y
        sid = sent["id"]
        prompt = sent["prompt"]
        tag = sent["context_tag"]
        sec_title = sent["section_title"]
        sec_code = sent["section"]
        res_note = sent["research_note"]

        bbox_mm = [round(start_x, 2), round(by, 2), round(block_w, 2), round(block_h, 2)]
        prompt_bbox_mm = [round(start_x, 2), round(by, 2), round(block_w, 2), round(prompt_h, 2)]
        writing_bbox_mm = [round(start_x, 2), round(by + prompt_h, 2), round(block_w, 2), round(writing_h, 2)]
        
        # Line 1 and Line 2 bounding boxes (geometric guides)
        # Line 1: wz_y + 0.0 to wz_y + 23.0 mm
        # Line 2: wz_y + 23.0 to wz_y + 46.0 mm
        wz_y = by + prompt_h
        line_1_bbox_mm = [round(start_x, 2), round(wz_y, 2), round(block_w, 2), round(23.0, 2)]
        line_2_bbox_mm = [round(start_x, 2), round(wz_y + 23.0, 2), round(block_w, 2), round(23.0, 2)]

        collected_metadata.append({
            "sample_id": sid,
            "prompt": prompt,
            "context_tag": tag,
            "section": sec_code,
            "research_note": res_note,
            "bbox_mm": bbox_mm,
            "prompt_bbox_mm": prompt_bbox_mm,
            "writing_bbox_mm": writing_bbox_mm,
            "line_1_bbox_mm": line_1_bbox_mm,
            "line_2_bbox_mm": line_2_bbox_mm
        })

        lines.append(f'    <!-- Sentence Block {sid} -->')
        lines.append(f'    <g id="block_{sid}">')
        # Outer Block Frame
        lines.append(f'      <rect x="{start_x:.2f}" y="{by:.2f}" width="{block_w:.2f}" height="{block_h:.2f}" fill="#ffffff" stroke="#888888" stroke-width="0.3" rx="0.6"/>')
        
        # Prompt Header Region (Height: 12.0 mm)
        lines.append(f'      <rect x="{start_x:.2f}" y="{by:.2f}" width="{block_w:.2f}" height="{prompt_h:.2f}" fill="#f4f6f8" stroke="#888888" stroke-width="0.3" rx="0.6"/>')
        lines.append(f'      <line x1="{start_x:.2f}" y1="{by+prompt_h:.2f}" x2="{start_x+block_w:.2f}" y2="{by+prompt_h:.2f}" stroke="#777777" stroke-width="0.28"/>')
        
        # Prompt Header Top Row: Sample ID, Tag, Section Banner (neutral grayscale)
        lines.append(f'      <text x="{start_x+3.0:.2f}" y="{by+4.2:.2f}" font-family="Courier, monospace" font-size="2.2" font-weight="bold" fill="#222222">{escape_xml(sid)}<tspan font-size="1.5" font-weight="normal" fill="#666666">  •  {escape_xml(tag)}</tspan></text>')
        lines.append(f'      <text x="{start_x+block_w-3.0:.2f}" y="{by+4.2:.2f}" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="1.9" font-weight="bold" fill="#333333">{escape_xml(sec_title)}</text>')
        
        # Sub-divider within Prompt Header
        lines.append(f'      <line x1="{start_x+2.0:.2f}" y1="{by+5.6:.2f}" x2="{start_x+block_w-2.0:.2f}" y2="{by+5.6:.2f}" stroke="#d8d8d8" stroke-width="0.2"/>')
        
        # Prompt Text Line
        lines.append(f'      <text x="{start_x+3.0:.2f}" y="{by+9.8:.2f}" font-family="Helvetica, Arial, sans-serif" font-size="1.7" font-weight="bold" fill="#555555">Prompt:</text>')
        lines.append(f'      <text x="{start_x+17.0:.2f}" y="{by+9.9:.2f}" font-family="Times New Roman, Georgia, serif" font-size="2.7" font-weight="bold" fill="#111111">"{escape_xml(prompt)}"</text>')
        
        # Writing Zone (Height: 46.0 mm, from wz_y to wz_y + 46.0 mm)
        # Line 1 Guidelines:
        # Ascender: wz_y + 4.5 mm
        # x-height: wz_y + 8.5 mm (ascender span = 4.0 mm)
        # Baseline: wz_y + 13.5 mm (x-height span = 5.0 mm)
        # Descender: wz_y + 17.5 mm (descender span = 4.0 mm)
        l1_asc = wz_y + 4.5
        l1_xh  = wz_y + 8.5
        l1_bs  = wz_y + 13.5
        l1_dsc = wz_y + 17.5

        lines.append(f'      <line x1="{start_x+2.0:.2f}" y1="{l1_asc:.2f}" x2="{start_x+block_w-2.0:.2f}" y2="{l1_asc:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        lines.append(f'      <line x1="{start_x+2.0:.2f}" y1="{l1_xh:.2f}" x2="{start_x+block_w-2.0:.2f}" y2="{l1_xh:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        lines.append(f'      <line x1="{start_x+2.0:.2f}" y1="{l1_bs:.2f}" x2="{start_x+block_w-2.0:.2f}" y2="{l1_bs:.2f}" stroke="#7e7e7e" stroke-width="0.28"/>')
        lines.append(f'      <line x1="{start_x+2.0:.2f}" y1="{l1_dsc:.2f}" x2="{start_x+block_w-2.0:.2f}" y2="{l1_dsc:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        # Line 1 edge registration ticks
        lines.append(f'      <line x1="{start_x:.2f}" y1="{l1_bs:.2f}" x2="{start_x+1.2:.2f}" y2="{l1_bs:.2f}" stroke="#555555" stroke-width="0.35"/>')
        lines.append(f'      <line x1="{start_x+block_w-1.2:.2f}" y1="{l1_bs:.2f}" x2="{start_x+block_w:.2f}" y2="{l1_bs:.2f}" stroke="#555555" stroke-width="0.35"/>')

        # Line 2 Guidelines:
        # Ascender: wz_y + 27.5 mm (inter-line clear gap = 10.0 mm from l1_dsc)
        # x-height: wz_y + 31.5 mm (ascender span = 4.0 mm)
        # Baseline: wz_y + 36.5 mm (x-height span = 5.0 mm)
        # Descender: wz_y + 40.5 mm (descender span = 4.0 mm)
        l2_asc = wz_y + 27.5
        l2_xh  = wz_y + 31.5
        l2_bs  = wz_y + 36.5
        l2_dsc = wz_y + 40.5

        lines.append(f'      <line x1="{start_x+2.0:.2f}" y1="{l2_asc:.2f}" x2="{start_x+block_w-2.0:.2f}" y2="{l2_asc:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        lines.append(f'      <line x1="{start_x+2.0:.2f}" y1="{l2_xh:.2f}" x2="{start_x+block_w-2.0:.2f}" y2="{l2_xh:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        lines.append(f'      <line x1="{start_x+2.0:.2f}" y1="{l2_bs:.2f}" x2="{start_x+block_w-2.0:.2f}" y2="{l2_bs:.2f}" stroke="#7e7e7e" stroke-width="0.28"/>')
        lines.append(f'      <line x1="{start_x+2.0:.2f}" y1="{l2_dsc:.2f}" x2="{start_x+block_w-2.0:.2f}" y2="{l2_dsc:.2f}" stroke="#d0d0d0" stroke-width="0.18" stroke-dasharray="1.2, 1.2"/>')
        # Line 2 edge registration ticks
        lines.append(f'      <line x1="{start_x:.2f}" y1="{l2_bs:.2f}" x2="{start_x+1.2:.2f}" y2="{l2_bs:.2f}" stroke="#555555" stroke-width="0.35"/>')
        lines.append(f'      <line x1="{start_x+block_w-1.2:.2f}" y1="{l2_bs:.2f}" x2="{start_x+block_w:.2f}" y2="{l2_bs:.2f}" stroke="#555555" stroke-width="0.35"/>')

        lines.append('    </g>')

        current_y += block_h
        if s_idx < len(sentences) - 1:
            current_y += block_gap

    lines.append('  </g>')

    # 6. Calibration Area (y: 256.5 to 278.5 mm, height: 22.0 mm - Identical to P01/P02)
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

    # 7. Footer - P03 Pilot Candidate wording
    lines.append('  <!-- Footer Section (between bottom fiducials) -->')
    lines.append('  <g id="footer">')
    lines.append('    <text x="22.0" y="282.5" font-family="Helvetica, Arial, sans-serif" font-size="1.8" fill="#333333"><tspan font-weight="bold">OmniDraw Research Dataset</tspan> • Form P03 Demo v0.1 (Pilot Candidate — Not Approved for Formal Data Collection)</text>')
    lines.append('    <text x="22.0" y="285.5" font-family="Courier, monospace" font-size="1.6" fill="#666666">SCAN TARGET: Flatbed 600 DPI • 24-bit RGB / 8-bit Grayscale • Lossless PNG • True Scale 1:1 • No Auto-Contrast</text>')
    lines.append('  </g>')

    lines.append('</svg>')
    return '\n'.join(lines), collected_metadata

if __name__ == '__main__':
    svg_content, metadata = build_p03_svg()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_svg = os.path.join(script_dir, 'collection_sheet_p03.svg')
    with open(target_svg, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {target_svg} ({len(svg_content)} bytes)")
    print(f"Total sentences collected: {len(metadata)}")
    for item in metadata:
        print(f"  {item['sample_id']}: bbox={item['bbox_mm']}, prompt_bbox={item['prompt_bbox_mm']}, writing_bbox={item['writing_bbox_mm']}")
