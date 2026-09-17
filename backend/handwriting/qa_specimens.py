#!/usr/bin/env python3
"""
OmniDraw - Handwriting Visual QA Tool (qa_specimens.py)
======================================================
Công cụ QA trực quan để sinh và đối chiếu các bản vẽ chữ viết tay SVG
trước khi bổ sung hoặc tinh chỉnh thuật toán.

Cách dùng:
    backend/venv/bin/python backend/handwriting/qa_specimens.py [--out <path>] [--seed <int>]
"""

import argparse
import html
import os
import sys
import tempfile
import time
from pathlib import Path

# Đảm bảo đường dẫn import tương thích khi chạy trực tiếp script
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

for p in [str(PROJECT_ROOT), str(BACKEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.handwriting.engine import generate_handwriting_svg
except ImportError:
    from handwriting.engine import generate_handwriting_svg

# -----------------------------------------------------------------------------
# Cấu hình chuẩn cho QA Specimen
# -----------------------------------------------------------------------------

DEFAULT_SEED = 42
TARGET_PAPER_SIZE_MM = (210.0, 297.0)  # Khổ A4 tiêu chuẩn

# Mẫu nội dung chung cho toàn bộ ma trận 5 font × 4 style và đối chiếu chữ K:
# - Bắt đầu bằng "Kính gửi..." (kích hoạt chữ hoa mở đầu trang trọng K trong letter_type='formal')
# - Chứa chữ n/m ở giữa và cuối từ: bạn, nam, mộc, mạc, non, nước, tình cảm, chân thành
# - Khoảng cách từ tự nhiên và xuống dòng thủ công (\n)
# - Độ dài vừa vặn để render thành công 100% trên khổ A4 kể cả với các style có độ nghiêng lớn
SAMPLE_TEXT = (
    "Kính gửi bạn nam,\n"
    "Thư tay mộc mạc non nước tình cảm chân thành."
)

# Mẫu kiểm tra chữ hoa mở đầu trang trọng T (bắt đầu bằng "Thân gửi...")
SAMPLE_TEXT_T = (
    "Thân gửi bạn nam,\n"
    "Thư tay mộc mạc tình cảm chân thành."
)

# Mẫu kiểm tra chữ hoa mở đầu trang trọng C (bắt đầu bằng "Cảm ơn...")
SAMPLE_TEXT_C = (
    "Cảm ơn bạn nam,\n"
    "Thư tay mộc mạc tình cảm chân thành."
)

# Mẫu kiểm tra tính năng tự động ngắt dòng (Auto Word-Wrap) trên đoạn dài
WRAP_SAMPLE_TEXT = (
    "Mỗi dòng chữ nắn nót trên trang giấy trắng là nhịp cầu nối liền những tấm lòng thân thương, "
    "gửi gắm trọn vẹn niềm tin cùng bao ước vọng tốt đẹp nhất đến người nhận."
)

FONTS = ["oly", "omni_casual", "thanhdam", "thuphap", "cursive"]
STYLES = ["hand_hocsinh", "hand_nguoilon", "hand_thuphap", "hand_chukinhanh"]
LEGACY_FONTS = ["oly", "thanhdam", "thuphap", "cursive"]


def run_specimen(text, font, style, letter_type, seed, target_paper_size_mm):
    """
    Thực hiện render một cấu hình thư tay và ghi nhận kết quả hoặc lỗi.
    """
    t0 = time.perf_counter()
    try:
        svg_content, metrics, is_within_bounds = generate_handwriting_svg(
            text=text,
            font=font,
            style=style,
            target_paper_size_mm=target_paper_size_mm,
            seed=seed,
            letter_type=letter_type,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "success": True,
            "svg_content": svg_content,
            "metrics": metrics,
            "is_within_bounds": is_within_bounds,
            "error": None,
            "elapsed_ms": elapsed_ms,
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "success": False,
            "svg_content": None,
            "metrics": None,
            "is_within_bounds": False,
            "error": f"{type(exc).__name__}: {str(exc)}",
            "elapsed_ms": elapsed_ms,
        }


def render_card(item, show_contrast_badge=False, custom_note=None):
    """
    Render thẻ hiển thị kết quả một cấu hình mẫu SVG.
    """
    res = item["result"]
    font = item["font"]
    style = item["style"]
    letter_type = item["letter_type"]
    svg_filename = item["svg_filename"]
    seed = item.get("seed", DEFAULT_SEED)

    if res["success"]:
        in_bounds = res["is_within_bounds"]
        met = res["metrics"]
        status_badge = (
            '<span class="badge badge-success">✓ HỢP LỆ</span>'
            if in_bounds
            else '<span class="badge badge-warning">⚠ VƯỢT BOUNDS</span>'
        )

        metrics_html = f"""
            <div class="metrics-grid">
                <div class="metric-item">
                    <span class="m-label">Khổ giấy:</span>
                    <span class="m-val {'val-ok' if in_bounds else 'val-bad'}">{'Trong bounds' if in_bounds else 'Ngoài bounds'}</span>
                </div>
                <div class="metric-item">
                    <span class="m-label">Số nét (Strokes):</span>
                    <span class="m-val">{met.get('pen_lift_count', 0)}</span>
                </div>
                <div class="metric-item">
                    <span class="m-label">Chiều dài nét:</span>
                    <span class="m-val">{met.get('total_path_length_mm', 0):.1f} mm</span>
                </div>
                <div class="metric-item">
                    <span class="m-label">Nhấc bút:</span>
                    <span class="m-val">{met.get('pen_lift_distance_mm', 0):.1f} mm</span>
                </div>
            </div>
        """

        preview_html = f"""
            <div class="svg-viewport">
                <object data="{html.escape(svg_filename)}" type="image/svg+xml" class="svg-obj"></object>
            </div>
            <div class="card-footer">
                <a href="{html.escape(svg_filename)}" target="_blank" class="btn-inspect">🔍 Mở SVG kích thước thật</a>
                <span class="elapsed-tag">{res['elapsed_ms']:.1f}ms</span>
            </div>
        """
    else:
        status_badge = '<span class="badge badge-danger">✗ LỖI RENDER</span>'
        metrics_html = f"""
            <div class="error-box">
                <strong>Thông báo lỗi:</strong>
                <code>{html.escape(res['error'])}</code>
            </div>
        """
        preview_html = f"""
            <div class="svg-viewport viewport-error">
                <p class="error-text">Không thể tạo file SVG cho cấu hình này</p>
            </div>
            <div class="card-footer">
                <span class="elapsed-tag">Thất bại ({res['elapsed_ms']:.1f}ms)</span>
            </div>
        """

    type_badge = f'<span class="type-pill type-{letter_type}">{letter_type.upper()}</span>'
    contrast_tag = f'<span class="contrast-tag">{html.escape(custom_note)}</span>' if custom_note else (
        f'<span class="contrast-tag">Đối chiếu: {font}</span>' if show_contrast_badge else ''
    )

    return f"""
    <div class="specimen-card {'card-error' if not res['success'] else ''}">
        <div class="card-header">
            <div>
                <h3 class="card-title">{font} <span class="style-title">/ {style}</span></h3>
                <div class="card-tags">
                    {type_badge}
                    {contrast_tag}
                    <span class="seed-tag">seed={seed}</span>
                </div>
            </div>
            <div>{status_badge}</div>
        </div>
        {metrics_html}
        {preview_html}
    </div>
    """


def build_html_report(out_dir, seed, paper_size, general_results, formal_k_results, formal_tc_results, wrap_results):
    """
    Tạo file index.html trình bày các mẫu SVG độc lập, mở offline được.
    """
    all_results = general_results + formal_k_results + formal_tc_results + wrap_results
    total_configs = len(all_results)
    success_count = sum(1 for r in all_results if r["result"]["success"])
    fail_count = sum(1 for r in all_results if not r["result"]["success"])
    out_of_bounds_count = sum(
        1 for r in all_results if r["result"]["success"] and not r["result"]["is_within_bounds"]
    )

    general_cards_html = "\n".join(render_card(item) for item in general_results)
    formal_k_cards_html = "\n".join(render_card(item, show_contrast_badge=True, custom_note=f"Chữ K: {item['font']}") for item in formal_k_results)
    formal_tc_cards_html = "\n".join(render_card(item, show_contrast_badge=True, custom_note=item.get("custom_note")) for item in formal_tc_results)
    wrap_cards_html = "\n".join(render_card(item, custom_note="Đoạn dài tự wrap") for item in wrap_results)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniDraw - Handwriting Visual QA Report</title>
    <style>
        :root {{
            --bg-color: #F6F4EE;
            --panel-bg: #FFFFFF;
            --border-color: #1A1A1A;
            --text-main: #1A1A1A;
            --text-muted: #66645E;
            --accent-yellow: #FFEAA7;
            --accent-green: #2E7D32;
            --accent-red: #C0392B;
            --accent-amber: #D35400;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 24px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1440px;
            margin: 0 auto;
        }}
        header {{
            background: var(--panel-bg);
            border: 3px solid var(--border-color);
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 4px 4px 0px var(--border-color);
        }}
        h1 {{
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 8px;
        }}
        .subtitle {{
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 16px;
        }}
        .summary-stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-top: 16px;
        }}
        .stat-badge {{
            border: 2px solid var(--border-color);
            padding: 8px 14px;
            border-radius: 8px;
            background: #FAF8F2;
            font-size: 13px;
            font-weight: 700;
            box-shadow: 2px 2px 0px var(--border-color);
        }}
        .stat-success {{ background: #E8F5E9; color: var(--accent-green); }}
        .stat-fail {{ background: #FDEDEC; color: var(--accent-red); }}
        .stat-warn {{ background: #FEF9E7; color: var(--accent-amber); }}
        .note-box {{
            background: #FAF8F2;
            border: 2px dashed var(--border-color);
            border-radius: 8px;
            padding: 14px 18px;
            margin-top: 16px;
            font-size: 13px;
        }}
        .note-box strong {{ display: block; margin-bottom: 6px; }}
        .sample-text-content {{
            white-space: pre-line;
            font-family: inherit;
            color: #2D3748;
            margin-top: 4px;
        }}
        section {{
            margin-bottom: 36px;
        }}
        .section-header {{
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(440px, 1fr));
            gap: 20px;
        }}
        .specimen-card {{
            background: var(--panel-bg);
            border: 2.5px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 3px 3px 0px var(--border-color);
            display: flex;
            flex-direction: column;
        }}
        .card-error {{
            border-color: var(--accent-red);
        }}
        .card-header {{
            padding: 14px 16px;
            border-bottom: 2px solid var(--border-color);
            background: #FAF8F2;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .card-title {{
            font-size: 15px;
            font-weight: 800;
        }}
        .style-title {{
            color: var(--text-muted);
            font-weight: 600;
            font-size: 13px;
        }}
        .card-tags {{
            margin-top: 4px;
            display: flex;
            gap: 6px;
            align-items: center;
        }}
        .badge {{
            font-size: 11px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            border: 1.5px solid var(--border-color);
        }}
        .badge-success {{ background: #E8F5E9; color: var(--accent-green); }}
        .badge-warning {{ background: #FEF9E7; color: var(--accent-amber); }}
        .badge-danger {{ background: #FDEDEC; color: var(--accent-red); }}
        .type-pill {{
            font-size: 10px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}
        .type-general {{ background: var(--accent-yellow); color: #1A1A1A; }}
        .type-formal {{ background: #D6EAF8; color: #1B4F72; }}
        .contrast-tag, .seed-tag {{
            font-size: 10px;
            font-weight: 600;
            color: var(--text-muted);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 6px 12px;
            padding: 10px 16px;
            background: #FFFFFF;
            border-bottom: 1.5px solid #EAE8E0;
            font-size: 11.5px;
        }}
        .metric-item {{
            display: flex;
            justify-content: space-between;
        }}
        .m-label {{ color: var(--text-muted); font-weight: 600; }}
        .m-val {{ font-weight: 700; color: var(--text-main); }}
        .val-ok {{ color: var(--accent-green); }}
        .val-bad {{ color: var(--accent-red); }}
        .error-box {{
            padding: 12px 16px;
            background: #FDEDEC;
            color: var(--accent-red);
            font-size: 12px;
            border-bottom: 1.5px solid var(--accent-red);
        }}
        .error-box code {{
            display: block;
            margin-top: 4px;
            background: #FADBD8;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
            word-break: break-all;
        }}
        .svg-viewport {{
            flex: 1;
            min-height: 360px;
            max-height: 440px;
            background: #FFFFFF;
            background-image: 
                linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px);
            background-size: 20px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px;
            overflow: hidden;
        }}
        .viewport-error {{
            background: #FDFEFE;
        }}
        .error-text {{
            color: var(--text-muted);
            font-size: 12px;
            font-style: italic;
        }}
        .svg-obj {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            border: 1px solid #E2E0D8;
            border-radius: 6px;
            background: #FFFFFF;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .card-footer {{
            padding: 10px 16px;
            background: #FAF8F2;
            border-top: 1.5px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .btn-inspect {{
            text-decoration: none;
            color: var(--text-main);
            font-size: 11.5px;
            font-weight: 700;
            background: #FFFFFF;
            border: 1.5px solid var(--border-color);
            padding: 4px 10px;
            border-radius: 6px;
            box-shadow: 1.5px 1.5px 0px var(--border-color);
            transition: transform 0.1s;
        }}
        .btn-inspect:hover {{
            background: var(--accent-yellow);
            transform: translate(-1px, -1px);
        }}
        .elapsed-tag {{
            font-size: 11px;
            color: var(--text-muted);
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>OmniDraw Handwriting Visual QA Report</h1>
            <p class="subtitle">Báo cáo trực quan kiểm thử và soi nét chữ viết tay trước khi bổ sung thuật toán.</p>
            <div class="summary-stats">
                <span class="stat-badge">Tổng cấu hình: {total_configs}</span>
                <span class="stat-badge stat-success">✓ Thành công: {success_count}</span>
                <span class="stat-badge {'stat-fail' if fail_count > 0 else ''}">✗ Lỗi: {fail_count}</span>
                <span class="stat-badge {'stat-warn' if out_of_bounds_count > 0 else ''}">⚠ Vượt bounds: {out_of_bounds_count}</span>
                <span class="stat-badge">Seed: {seed}</span>
                <span class="stat-badge">Khổ giấy: A4 ({paper_size[0]} × {paper_size[1]} mm)</span>
            </div>
            <div class="note-box">
                <strong>Quy ước hình học chữ hoa mở đầu trang trọng (Formal Initial Glyphs):</strong>
                <p>Biến thể chữ hoa mở đầu trang trọng (K, T, C) trong OmniDraw chỉ kích hoạt ở chữ cái đầu tiên của toàn bộ văn bản (document-initial), không áp dụng ở đầu mỗi dòng kẻ đơn lẻ.</p>
                <div style="margin-top: 8px;">
                    <strong>Mẫu văn bản chung (Ma trận 5×4 & Chữ K):</strong>
                    <div class="sample-text-content">{html.escape(SAMPLE_TEXT)}</div>
                </div>
            </div>
        </header>

        <section>
            <div class="section-header">
                <h2 class="section-title">1. Đối chiếu chữ hoa mở đầu trang trọng (K, T, C)</h2>
                <span style="font-size: 12px; color: var(--text-muted);">So sánh General vs Formal trên các font Legacy</span>
            </div>
            <h3 style="font-size: 14px; font-weight: 700; margin-bottom: 12px; color: #2C3E50;">1.1. Chữ K mở đầu ("Kính gửi...") trên 4 font Legacy Pack</h3>
            <div class="cards-grid" style="margin-bottom: 24px;">
                {formal_k_cards_html}
            </div>

            <h3 style="font-size: 14px; font-weight: 700; margin-bottom: 12px; color: #2C3E50;">1.2. Chữ T ("Thân gửi...") và Chữ C ("Cảm ơn...") mở đầu trên font Tiểu Học (oly)</h3>
            <div class="cards-grid">
                {formal_tc_cards_html}
            </div>
        </section>

        <section>
            <div class="section-header">
                <h2 class="section-title">2. Ma trận toàn diện: 5 Fonts × 4 Styles (letter_type="general")</h2>
                <span style="font-size: 12px; color: var(--text-muted);">Khảo sát đầy đủ 20 cấu hình chung</span>
            </div>
            <div class="cards-grid">
                {general_cards_html}
            </div>
        </section>

        <section>
            <div class="section-header">
                <h2 class="section-title">3. Kiểm thử tự động ngắt dòng (Auto Word-Wrap)</h2>
                <span style="font-size: 12px; color: var(--text-muted);">Đoạn văn bản dài trên cấu hình mẫu phù hợp</span>
            </div>
            <div class="cards-grid">
                {wrap_cards_html}
            </div>
        </section>
    </div>
</body>
</html>
"""
    index_path = out_dir / "index.html"
    index_path.write_text(html_content, encoding="utf-8")
    return index_path


def main():
    parser = argparse.ArgumentParser(description="OmniDraw Handwriting Visual QA Tool")
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Thư mục xuất kết quả mới (từ chối nếu thư mục đã tồn tại trước đó)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Seed cố định cho tất cả các lần render (mặc định: {DEFAULT_SEED})",
    )
    args = parser.parse_args()

    # -------------------------------------------------------------------------
    # Xử lý thư mục output:
    # Với --out: Từ chối nếu thư mục đã tồn tại từ trước để bảo vệ dữ liệu người dùng.
    # Không truyền --out: Tự động tạo thư mục tạm mới bằng tempfile.mkdtemp.
    # -------------------------------------------------------------------------
    if args.out:
        out_dir = Path(args.out).resolve()
        if out_dir.exists():
            print(
                f"[LỖI AN TOÀN DỮ LIỆU] Thư mục output '{out_dir}' đã tồn tại từ trước.\n"
                f"Để tránh xóa hoặc ghi đè file của người dùng, công cụ từ chối thực hiện.\n"
                f"Vui lòng chỉ định một thư mục chưa tồn tại hoặc bỏ qua --out để tạo thư mục tạm mới.",
                file=sys.stderr,
            )
            sys.exit(2)
        out_dir.mkdir(parents=True, exist_ok=False)
    else:
        temp_dir_str = tempfile.mkdtemp(prefix="omnidraw-handwriting-qa-")
        out_dir = Path(temp_dir_str).resolve()

    print("=" * 70)
    print("OMNIDRAW HANDWRITING VISUAL QA SPECIMENS")
    print(f"Thư mục output: {out_dir}")
    print(f"Seed cố định : {args.seed}")
    print(f"Khổ giấy     : A4 {TARGET_PAPER_SIZE_MM} mm")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # Nhóm 1: Đối chiếu chữ K mở đầu ("Kính gửi...") cho 4 font Legacy Pack
    # -------------------------------------------------------------------------
    print("\n[1/4] Đang render Nhóm đối chiếu chữ K (General vs Formal trên 4 font Legacy)...")
    formal_k_results = []
    idx = 1
    for font in LEGACY_FONTS:
        for lt in ["general", "formal"]:
            style = "hand_hocsinh"
            svg_filename = f"contrast_K_{font}_{lt}_{style}.svg"
            svg_path = out_dir / svg_filename

            res = run_specimen(
                text=SAMPLE_TEXT,
                font=font,
                style=style,
                letter_type=lt,
                seed=args.seed,
                target_paper_size_mm=TARGET_PAPER_SIZE_MM,
            )

            if res["success"]:
                svg_path.write_text(res["svg_content"], encoding="utf-8")
                in_bounds_str = f"in_bounds={res['is_within_bounds']}"
                strokes_str = f"{res['metrics'].get('pen_lift_count', 0)} strokes"
                print(f"  [{idx:02d}/08] K | {font:12} | {lt:8} | {style:14} | SUCCESS | {in_bounds_str} | {strokes_str} | {res['elapsed_ms']:.1f}ms")
            else:
                print(f"  [{idx:02d}/08] K | {font:12} | {lt:8} | {style:14} | ERROR   | {res['error']}")

            formal_k_results.append({
                "font": font,
                "style": style,
                "letter_type": lt,
                "svg_filename": svg_filename,
                "result": res,
                "seed": args.seed,
            })
            idx += 1

    # -------------------------------------------------------------------------
    # Nhóm 2: Đối chiếu chữ T ("Thân gửi...") và C ("Cảm ơn...") trên font oly
    # -------------------------------------------------------------------------
    print("\n[2/4] Đang render Nhóm đối chiếu chữ T và C mở đầu (font oly)...")
    formal_tc_results = []
    tc_configs = [
        ("T", SAMPLE_TEXT_T, "Thân gửi..."),
        ("C", SAMPLE_TEXT_C, "Cảm ơn..."),
    ]
    idx = 1
    for char_key, text_sample, note in tc_configs:
        for lt in ["general", "formal"]:
            font = "oly"
            style = "hand_hocsinh"
            svg_filename = f"contrast_{char_key}_{font}_{lt}_{style}.svg"
            svg_path = out_dir / svg_filename

            res = run_specimen(
                text=text_sample,
                font=font,
                style=style,
                letter_type=lt,
                seed=args.seed,
                target_paper_size_mm=TARGET_PAPER_SIZE_MM,
            )

            if res["success"]:
                svg_path.write_text(res["svg_content"], encoding="utf-8")
                in_bounds_str = f"in_bounds={res['is_within_bounds']}"
                strokes_str = f"{res['metrics'].get('pen_lift_count', 0)} strokes"
                print(f"  [{idx:02d}/04] {char_key} | {font:12} | {lt:8} | {style:14} | SUCCESS | {in_bounds_str} | {strokes_str} | {res['elapsed_ms']:.1f}ms")
            else:
                print(f"  [{idx:02d}/04] {char_key} | {font:12} | {lt:8} | {style:14} | ERROR   | {res['error']}")

            formal_tc_results.append({
                "font": font,
                "style": style,
                "letter_type": lt,
                "svg_filename": svg_filename,
                "result": res,
                "seed": args.seed,
                "custom_note": f"Chữ {char_key} mở đầu ({note})",
            })
            idx += 1

    # -------------------------------------------------------------------------
    # Nhóm 3: Ma trận 5 Fonts × 4 Styles (letter_type="general")
    # -------------------------------------------------------------------------
    print("\n[3/4] Đang render Ma trận 5 Fonts × 4 Styles (letter_type='general')...")
    general_results = []
    matrix_idx = 1
    total_matrix = len(FONTS) * len(STYLES)

    for font in FONTS:
        for style in STYLES:
            lt = "general"
            svg_filename = f"matrix_{font}_{style}.svg"
            svg_path = out_dir / svg_filename

            res = run_specimen(
                text=SAMPLE_TEXT,
                font=font,
                style=style,
                letter_type=lt,
                seed=args.seed,
                target_paper_size_mm=TARGET_PAPER_SIZE_MM,
            )

            if res["success"]:
                svg_path.write_text(res["svg_content"], encoding="utf-8")
                in_bounds_str = f"in_bounds={res['is_within_bounds']}"
                strokes_str = f"{res['metrics'].get('pen_lift_count', 0)} strokes"
                print(f"  [{matrix_idx:02d}/{total_matrix:02d}] {font:12} | {style:16} | SUCCESS | {in_bounds_str} | {strokes_str} | {res['elapsed_ms']:.1f}ms")
            else:
                print(f"  [{matrix_idx:02d}/{total_matrix:02d}] {font:12} | {style:16} | ERROR   | {res['error']}")

            general_results.append({
                "font": font,
                "style": style,
                "letter_type": lt,
                "svg_filename": svg_filename,
                "result": res,
                "seed": args.seed,
            })
            matrix_idx += 1

    # -------------------------------------------------------------------------
    # Nhóm 4: Mẫu kiểm thử tự động ngắt dòng (Auto Word-Wrap Test)
    # -------------------------------------------------------------------------
    print("\n[4/4] Đang render Mẫu kiểm thử tự động ngắt dòng (Auto Word-Wrap)...")
    wrap_results = []
    wrap_font = "oly"
    wrap_style = "hand_hocsinh"
    wrap_lt = "general"
    wrap_svg_filename = f"wrap_test_{wrap_font}_{wrap_style}.svg"
    wrap_svg_path = out_dir / wrap_svg_filename

    wrap_res = run_specimen(
        text=WRAP_SAMPLE_TEXT,
        font=wrap_font,
        style=wrap_style,
        letter_type=wrap_lt,
        seed=args.seed,
        target_paper_size_mm=TARGET_PAPER_SIZE_MM,
    )

    if wrap_res["success"]:
        wrap_svg_path.write_text(wrap_res["svg_content"], encoding="utf-8")
        in_bounds_str = f"in_bounds={wrap_res['is_within_bounds']}"
        strokes_str = f"{wrap_res['metrics'].get('pen_lift_count', 0)} strokes"
        print(f"  [01/01] {wrap_font:12} | {wrap_style:16} | SUCCESS | {in_bounds_str} | {strokes_str} | {wrap_res['elapsed_ms']:.1f}ms")
    else:
        print(f"  [01/01] {wrap_font:12} | {wrap_style:16} | ERROR   | {wrap_res['error']}")

    wrap_results.append({
        "font": wrap_font,
        "style": wrap_style,
        "letter_type": wrap_lt,
        "svg_filename": wrap_svg_filename,
        "result": wrap_res,
        "seed": args.seed,
    })

    # Tạo file index.html báo cáo
    index_html_path = build_html_report(
        out_dir=out_dir,
        seed=args.seed,
        paper_size=TARGET_PAPER_SIZE_MM,
        general_results=general_results,
        formal_k_results=formal_k_results,
        formal_tc_results=formal_tc_results,
        wrap_results=wrap_results,
    )

    all_results = formal_k_results + formal_tc_results + general_results + wrap_results
    total_configs = len(all_results)
    success_count = sum(1 for r in all_results if r["result"]["success"])
    fail_count = sum(1 for r in all_results if not r["result"]["success"])
    out_of_bounds_count = sum(
        1 for r in all_results if r["result"]["success"] and not r["result"]["is_within_bounds"]
    )

    print("\n" + "=" * 70)
    print("TỔNG KẾT KIỂM THỬ THƯ TAY (QA SPECIMENS SUMMARY)")
    print(f"- Tổng số cấu hình đã chạy: {total_configs}")
    print(f"- Thành công                : {success_count}/{total_configs}")
    print(f"- Thất bại (Lỗi render)     : {fail_count}/{total_configs}")
    print(f"- Vượt khổ giấy (Out bounds): {out_of_bounds_count}/{total_configs}")
    print("-" * 70)
    print(f"HTML Report (mở bằng trình duyệt):")
    print(f"{index_html_path.resolve()}")
    print("=" * 70)

    # Trả về exit code khác 0 nếu có bất kỳ cấu hình nào bị lỗi render hoặc vượt bounds
    if fail_count > 0 or out_of_bounds_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
