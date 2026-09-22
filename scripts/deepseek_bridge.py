#!/usr/bin/env python3
"""
DeepSeek Bridge - Autonomous Dual-Agent Bridge for Antigravity & DeepSeek
------------------------------------------------------------------------
Provides programmatic, token-optimized bridge between Antigravity (Executor)
and DeepSeek (Architect / Independent Reviewer).

Features:
- Budget Circuit Breaker: Enforces strict MAX_BUDGET_USD ceiling.
- Prompt Cache Optimization: Leverages DeepSeek 90% prompt cache discount.
- Diff-Only Review: Sends minimal git diff instead of full codebase.
- Error & Balance Detection: Catches HTTP 402 Insufficient Balance gracefully.
- Usage Tracker: Persists cumulative token and USD usage in .deepseek_usage.json.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from openai import OpenAI, APIStatusError, RateLimitError, APIConnectionError
except ImportError:
    print("Error: openai library is required. Run 'pip install openai' in your venv.")
    sys.exit(1)

# Base directory resolution
REPO_DIR = Path(__file__).resolve().parent.parent
USAGE_FILE = REPO_DIR / ".deepseek_usage.json"
ENV_FILE = REPO_DIR / "backend" / ".env"

# Pricing Table (USD per 1M tokens) - DeepSeek V3 & R1
PRICING = {
    "deepseek-chat": {
        "cache_miss": 0.14 / 1_000_000,
        "cache_hit": 0.014 / 1_000_000,
        "output": 0.28 / 1_000_000,
    },
    "deepseek-reasoner": {
        "cache_miss": 0.55 / 1_000_000,
        "cache_hit": 0.14 / 1_000_000,
        "output": 2.19 / 1_000_000,
    },
}

DEFAULT_MAX_BUDGET_USD = 1.95


def load_api_key() -> str:
    """Loads DEEPSEEK_API_KEY from environment or backend/.env."""
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key

    if ENV_FILE.exists():
        if load_dotenv:
            load_dotenv(ENV_FILE)
            key = os.getenv("DEEPSEEK_API_KEY", "").strip()
            if key:
                return key
        else:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DEEPSEEK_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip("\"'")
                        if val:
                            return val

    print("⚠️ Lỗi: Không tìm thấy DEEPSEEK_API_KEY trong môi trường hoặc trong backend/.env.")
    print(f"Vui lòng thêm DEEPSEEK_API_KEY=sk-... vào {ENV_FILE}")
    sys.exit(1)


def get_usage_data() -> Dict[str, Any]:
    """Retrieves accumulated usage statistics."""
    if USAGE_FILE.exists():
        try:
            with open(USAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "total_requests": 0,
        "total_tokens": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_cost_usd": 0.0,
        "history": [],
    }


def record_usage(model: str, usage: Any, prompt_summary: str = "") -> float:
    """Calculates request cost and updates persistent usage log."""
    data = get_usage_data()
    model_pricing = PRICING.get(model, PRICING["deepseek-chat"])

    prompt_tokens = getattr(usage, "prompt_tokens", 0)
    cache_hit_tokens = getattr(usage, "prompt_cache_hit_tokens", 0) or 0
    cache_miss_tokens = max(0, prompt_tokens - cache_hit_tokens)
    completion_tokens = getattr(usage, "completion_tokens", 0)
    total_tokens = getattr(usage, "total_tokens", prompt_tokens + completion_tokens)

    cost = (
        (cache_miss_tokens * model_pricing["cache_miss"])
        + (cache_hit_tokens * model_pricing["cache_hit"])
        + (completion_tokens * model_pricing["output"])
    )

    data["total_requests"] += 1
    data["total_tokens"] += total_tokens
    data["total_prompt_tokens"] += prompt_tokens
    data["total_completion_tokens"] += completion_tokens
    data["total_cost_usd"] += cost

    # Keep last 50 transactions in history
    data["history"].append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": model,
        "prompt_summary": prompt_summary[:100],
        "prompt_tokens": prompt_tokens,
        "cache_hit_tokens": cache_hit_tokens,
        "completion_tokens": completion_tokens,
        "cost_usd": cost,
    })
    data["history"] = data["history"][-50:]

    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return cost


def check_budget_limit(max_budget: float = DEFAULT_MAX_BUDGET_USD) -> None:
    """Verifies that accumulated spending is within budget."""
    data = get_usage_data()
    curr_cost = data.get("total_cost_usd", 0.0)
    if curr_cost >= max_budget:
        print(f"\n🛑 CIRCUIT BREAKER TRIGGERED: Ngân sách đã chạm ${curr_cost:.4f} USD (Giới hạn: ${max_budget:.2f} USD).")
        print("Tự động ngắt gọi DeepSeek API để bảo vệ số dư tài khoản của bạn.")
        sys.exit(2)


def call_deepseek(
    messages: list,
    model: str = "deepseek-chat",
    temperature: float = 0.3,
    max_tokens: int = 4096,
    max_retries: int = 3,
    max_budget: float = DEFAULT_MAX_BUDGET_USD,
) -> Optional[str]:
    """Executes call to DeepSeek with retries, budget tracking, and error handling."""
    check_budget_limit(max_budget)
    key = load_api_key()
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            usage = response.usage
            summary = messages[-1]["content"][:60] if messages else ""
            step_cost = record_usage(model, usage, summary)
            content = response.choices[0].message.content

            usage_data = get_usage_data()
            print(
                f"[DeepSeek] ✅ Success | Tokens: {usage.total_tokens} "
                f"(Hit: {getattr(usage, 'prompt_cache_hit_tokens', 0) or 0}) | "
                f"Cost: ${step_cost:.5f} | Total: ${usage_data['total_cost_usd']:.4f}"
            )
            return content

        except APIStatusError as e:
            if e.status_code == 402 or "insufficient" in str(e).lower():
                print("\n" + "=" * 60)
                print("⚠️ THÔNG BÁO: TÀI KHOẢN DEEPSEEK CẦN NẠP TIỀN (HTTP 402)")
                print("Số dư tài khoản DeepSeek hiện tại là 0 USD.")
                print("Vui lòng truy cập để nạp số dư (khoảng 2 USD):")
                print("👉 https://platform.deepseek.com/top_up")
                print("Sau khi nạp, key sẽ tự động hoạt động ngay lập tức!")
                print("=" * 60 + "\n")
                sys.exit(402)
            elif e.status_code == 429:
                wait_time = 2 ** attempt
                print(f"[DeepSeek] ⚠️ Rate limit (429). Thử lại lần {attempt}/{max_retries} sau {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[DeepSeek] ⚠️ HTTP {e.status_code}: {e.message}")
                if attempt == max_retries:
                    raise
                time.sleep(2)

        except (RateLimitError, APIConnectionError) as e:
            wait_time = 2 ** attempt
            print(f"[DeepSeek] ⚠️ Network / Rate limit: {e}. Thử lại sau {wait_time}s...")
            time.sleep(wait_time)

        except Exception as e:
            print(f"[DeepSeek] ⚠️ Lỗi không xác định: {type(e).__name__} - {e}")
            if attempt == max_retries:
                raise
            time.sleep(2)

    return None


def cmd_status() -> None:
    """Checks API connectivity and reporting balance status."""
    print("🔍 Đang kiểm tra kết nối API DeepSeek...")
    key = load_api_key()
    masked = key[:6] + "..." + key[-4:] if len(key) > 10 else "***"
    print(f"API Key: {masked}")

    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        print("✅ KẾT NỐI THÀNH CÔNG: DeepSeek API sẵn sàng hoạt động!")
        print(f"Phản hồi: {response.choices[0].message.content.strip()}")
        usage_data = get_usage_data()
        print(f"Tổng chi phí đã ghi nhận trên máy: ${usage_data['total_cost_usd']:.4f} USD")
    except APIStatusError as e:
        if e.status_code == 402 or "insufficient" in str(e).lower():
            print("\n⚠️ KẾT NỐI API THÀNH CÔNG NHƯNG SỐ DƯ = $0 USD (Error 402 Insufficient Balance).")
            print("API Key hoàn toàn chuẩn xác và kết nối tốt tới máy chủ DeepSeek.")
            print("Bạn chỉ cần vào https://platform.deepseek.com/top_up để nạp 2$ là chạy được ngay!")
        else:
            print(f"❌ Lỗi HTTP {e.status_code}: {e.message}")
    except Exception as e:
        print(f"❌ Lỗi kết nối: {type(e).__name__} - {e}")


def cmd_plan(task_description: str, context: Optional[str] = None, model: str = "deepseek-chat") -> None:
    """Collaborative Planning: DeepSeek acts as Tech Lead / Architect."""
    system_prompt = (
        "Bạn là Tech Lead & Software Architect chuyên nghiệp. "
        "Nhiệm vụ của bạn là nhận đề bài từ Antigravity (Lead Developer), phân tích bài toán, "
        "đưa ra Kế hoạch Thiết kế Kiến trúc (Architectural Plan), Phân bổ file cần sửa/tạo mới, "
        "và Tiêu chuẩn nghiệm thu (Acceptance Criteria / Test Plan). "
        "Hãy suy luận mạch lạc, súc tích, chặt chẽ và bám sát thực tế của dự án."
    )

    user_content = f"### ĐỀ BÀI TASK:\n{task_description}\n"
    if context:
        user_content += f"\n### BỐI CẢNH DỰ ÁN / TÀI LIỆU KÈM THEO:\n{context}\n"

    print(f"📋 Đang gửi yêu cầu lập kế hoạch sang DeepSeek ({model})...")
    plan = call_deepseek(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        model=model,
        temperature=0.2,
    )
    if plan:
        print("\n" + "=" * 60)
        print("🏛️ KẾ HOẠCH TỪ DEEPSEEK (TECH LEAD / ARCHITECT)")
        print("=" * 60)
        print(plan)
        print("=" * 60 + "\n")


def cmd_review(task_description: str, diff_text: Optional[str] = None, test_log: Optional[str] = None, model: str = "deepseek-chat") -> None:
    """Diff-Only Review: DeepSeek reviews code changes and test outputs."""
    if not diff_text:
        # Automatically grab git diff if none provided
        try:
            diff_proc = subprocess.run(["git", "diff"], cwd=REPO_DIR, capture_output=True, text=True)
            diff_text = diff_proc.stdout.strip()
            if not diff_text:
                stat_proc = subprocess.run(["git", "diff", "--stat", "HEAD~1"], cwd=REPO_DIR, capture_output=True, text=True)
                diff_text = "(Không có uncommitted diff. Stat commit gần nhất):\n" + stat_proc.stdout.strip()
        except Exception as e:
            diff_text = f"Không thể lấy git diff tự động: {e}"

    system_prompt = (
        "Bạn là Independent Senior Code Reviewer / Socratic Verifier. "
        "Antigravity (Developer) vừa thực hiện xong task và gửi bạn git diff cùng kết quả kiểm thử. "
        "Nhiệm vụ của bạn: "
        "1. Soi lỗi logic, edge cases, bảo mật, sai lệch yêu cầu, hoặc hồi quy (regressions). "
        "2. Đánh giá xem kết quả kiểm thử đã đầy đủ chưa. "
        "3. Đưa ra KẾT LUẬN CUỐI CÙNG rõ ràng: "
        "   - Nếu đạt: Bắt buộc kết thúc bằng dòng chữ: 'VERDICT: APPROVED' "
        "   - Nếu có lỗi/cần sửa: Bắt buộc kết thúc bằng dòng chữ: 'VERDICT: REVISE' kèm danh sách điểm cần sửa cụ thể."
    )

    user_content = f"### TASK ĐÃ THỰC HIỆN:\n{task_description}\n\n### GIT DIFF THAY ĐỔI:\n```diff\n{diff_text[:12000]}\n```\n"
    if test_log:
        user_content += f"\n### LOG KIỂM THỬ THỰC TẾ:\n```text\n{test_log[:4000]}\n```\n"

    print(f"🕵️ Đang gửi git diff ({len(diff_text)} bytes) sang DeepSeek để review chéo...")
    review = call_deepseek(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        model=model,
        temperature=0.1,
    )
    if review:
        print("\n" + "=" * 60)
        print("🔍 ĐÁNH GIÁ TỪ DEEPSEEK CODE REVIEWER")
        print("=" * 60)
        print(review)
        print("=" * 60 + "\n")


def cmd_budget(reset: bool = False) -> None:
    """Displays or resets accumulated usage statistics."""
    if reset:
        if USAGE_FILE.exists():
            USAGE_FILE.unlink()
        print("🧹 Đã làm mới nhật ký ngân sách DeepSeek!")
        return

    data = get_usage_data()
    print("\n" + "=" * 50)
    print("📊 BÁO CÁO SỬ DỤNG API DEEPSEEK TRÊN MÁY BẠN")
    print("=" * 50)
    print(f"- Số request đã gọi      : {data.get('total_requests', 0):,}")
    print(f"- Tổng token đã dùng     : {data.get('total_tokens', 0):,} tokens")
    print(f"  + Prompt tokens        : {data.get('total_prompt_tokens', 0):,}")
    print(f"  + Completion tokens    : {data.get('total_completion_tokens', 0):,}")
    print(f"- Tổng chi phí ước tính  : ${data.get('total_cost_usd', 0.0):.5f} USD")
    print(f"- Giới hạn an toàn đặt ra: ${DEFAULT_MAX_BUDGET_USD:.2f} USD")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Antigravity <-> DeepSeek Dual-Agent Bridge")
    subparsers = parser.add_subparsers(dest="subcommand", help="Lệnh cần thực hiện")

    # status
    subparsers.add_parser("status", help="Kiểm tra kết nối và trạng thái số dư API")

    # budget
    budget_parser = subparsers.add_parser("budget", help="Xem báo cáo chi phí và token đã dùng")
    budget_parser.add_argument("--reset", action="store_true", help="Xóa lịch sử và đặt lại ngân sách")

    # plan
    plan_parser = subparsers.add_parser("plan", help="Yêu cầu DeepSeek lập kế hoạch kiến trúc")
    plan_parser.add_argument("task", type=str, help="Mô tả đề bài / tính năng cần làm")
    plan_parser.add_argument("--context", type=str, default="", help="Bối cảnh / file mô tả kèm theo")
    plan_parser.add_argument("--reasoner", action="store_true", help="Dùng DeepSeek-R1 (Suy luận sâu)")

    # review
    review_parser = subparsers.add_parser("review", help="Gửi git diff và log test sang DeepSeek review chéo")
    review_parser.add_argument("task", type=str, help="Mô tả task đã hoàn thành")
    review_parser.add_argument("--diff", type=str, default="", help="Chuỗi git diff (mặc định tự lấy từ repo)")
    review_parser.add_argument("--test-log", type=str, default="", help="Đoạn trích kết quả chạy test")
    review_parser.add_argument("--reasoner", action="store_true", help="Dùng DeepSeek-R1 để review")

    # ask
    ask_parser = subparsers.add_parser("ask", help="Hỏi đáp trực tiếp với DeepSeek")
    ask_parser.add_argument("prompt", type=str, help="Nội dung cần hỏi")
    ask_parser.add_argument("--reasoner", action="store_true", help="Dùng DeepSeek-R1")

    args = parser.parse_args()

    if args.subcommand == "status":
        cmd_status()
    elif args.subcommand == "budget":
        cmd_budget(reset=args.reset)
    elif args.subcommand == "plan":
        model = "deepseek-reasoner" if args.reasoner else "deepseek-chat"
        cmd_plan(args.task, context=args.context, model=model)
    elif args.subcommand == "review":
        model = "deepseek-reasoner" if args.reasoner else "deepseek-chat"
        cmd_review(args.task, diff_text=args.diff, test_log=args.test_log, model=model)
    elif args.subcommand == "ask":
        model = "deepseek-reasoner" if args.reasoner else "deepseek-chat"
        res = call_deepseek(
            messages=[{"role": "user", "content": args.prompt}],
            model=model,
        )
        if res:
            print("\n" + res + "\n")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
