#!/usr/bin/env python3
"""
OmniDraw — AI Core API Generator
Phần mềm: Gọi API sinh ảnh cho 15 prompt thử nghiệm
Phù hợp với: OmniDraw_API_Spec.md (v1.1) và 01_tech-stack.md

Luồng:
  1. Đọc TV1_15_prompts.docx → trích xuất 15 prompt
  2. Gửi từng prompt → API OpenAI Image (DALL-E 3)
  3. Lưu ảnh + metadata → backend/data/
  4. Ghi log CSV (request_id, processing_time, style, etc.)
"""

import os
import sys
import csv
import uuid
import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

import requests
from docx import Document
from openai import OpenAI, APITimeoutError
from logs.csv_logger import log_experiment_csv  # Thay đổi 1: Import hàm ghi CSV

# ============================================================================
# CONFIG
# ============================================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Thay đổi 2: Dùng biến môi trường, giữ nguyên đường dẫn cũ làm mặc định
DOCX_PATH = BASE_DIR / "TV1_15_prompts.docx"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-demo-key")
OPENAI_MODEL = "dall-e-3"
IMAGE_SIZE = "1024x1024"
IMAGE_QUALITY = "standard"
TIMEOUT_SEC = 60

LOG_CSV_PATH = LOGS_DIR / "experiment_log.csv"
ACTIVITY_LOG_PATH = LOGS_DIR / "api_generator.log"

# ============================================================================
# LOGGING
# ============================================================================

# Cấu hình lại bảng mã để hỗ trợ in emoji trên Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(ACTIVITY_LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class PromptData:
    dataset_item_id: str
    style: str
    prompt_text: str
    prompt_vi: str


@dataclass
class APIResponse:
    request_id: str
    status: str
    result_image_base64: str = None
    model_used: str = None
    processing_time_ms: int = 0
    error_code: str = None
    error_message: str = None


@dataclass
class ExperimentLog:
    request_id: str
    timestamp: str
    dataset_item_id: str
    method_tag: str
    input_type: str
    style: str
    ai_processing_time_ms: int
    final_status: str
    error_code: str = None


# ============================================================================
# STEP 1: ĐỌC DOCX
# ============================================================================

def load_prompts_from_docx(docx_path: Path) -> List[PromptData]:
    """Đọc file DOCX, trích xuất 15 prompt"""
    logger.info(f"📖 Đang đọc file: {docx_path}")

    if not docx_path.exists():
        logger.error(f"❌ File không tồn tại: {docx_path}")
        raise FileNotFoundError(f"File {docx_path} không tồn tại")

    doc = Document(docx_path)
    prompts: List[PromptData] = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()

        if not text.startswith("prompt_"):
            continue

        try:
            # Đã sửa lỗi tìm dấu ngoặc vuông thay vì ']:'
            bracket_idx = text.find("]")
            if bracket_idx == -1:
                logger.warning(f"⚠️  Bỏ qua dòng: {text[:50]}...")
                continue

            header = text[:bracket_idx]
            prompt_id, style_part = header.split("[")
            prompt_id = prompt_id.strip()
            style = style_part.strip()

            # Đã sửa lỗi cắt chuỗi sau dấu ']'
            prompt_text = text[bracket_idx + 1:].strip()

            neo_marker = "black and white line art"
            if neo_marker in prompt_text:
                prompt_text = prompt_text[:prompt_text.index(neo_marker)].strip()

            prompts.append(PromptData(
                dataset_item_id=prompt_id,
                style=style,
                prompt_text=prompt_text,
                prompt_vi=prompt_text
            ))
            logger.info(f"✓ Trích xuất: {prompt_id} [{style}]")

        except Exception as e:
            logger.warning(f"⚠️  Lỗi parse: {str(e)}")
            continue

    # Thay đổi 3: Đã lùi lề ra ngoài vòng for
    logger.info(f"✅ Trích xuất {len(prompts)} prompt thành công")
    return prompts


# ============================================================================
# STEP 2: GỌI API
# ============================================================================

def call_openai_image_api(
        prompt: str,
        request_id: str,
        style: str,
        timeout: int = TIMEOUT_SEC
) -> APIResponse:
    """Gọi OpenAI Image API (DALL-E 3)"""
    logger.info(f"[{request_id}] 🎨 Gọi OpenAI API: {prompt[:60]}...")

    start_time = datetime.now()
    response = APIResponse(request_id=request_id, status="error")

    # Thay đổi 4: Gắn style vào prompt trước khi gửi đi
    final_prompt = f"{prompt}, {style} style" if style else prompt

    try:
        api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
        client = OpenAI(api_key=api_key, timeout=timeout)

        image_response = client.images.generate(
            model=OPENAI_MODEL,
            prompt=final_prompt,  # Sử dụng biến đã gắn style
            size=IMAGE_SIZE,
            quality=IMAGE_QUALITY,
            n=1,
            response_format="url"
        )

        image_url = image_response.data[0].url
        logger.info(f"[{request_id}] ✓ API trả URL")

        img_response = requests.get(image_url, timeout=10)
        img_response.raise_for_status()

        image_base64 = base64.b64encode(img_response.content).decode("utf-8")

        processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        response = APIResponse(
            request_id=request_id,
            status="success",
            result_image_base64=image_base64,
            model_used=OPENAI_MODEL,
            processing_time_ms=processing_time_ms
        )
        logger.info(f"[{request_id}] ✅ Thành công ({processing_time_ms}ms)")

    except APITimeoutError as e:
        logger.error(f"[{request_id}] ⏱️  TIMEOUT: {str(e)}")
        response.error_code = "AI_TIMEOUT"
        response.error_message = f"Model không phản hồi (>{timeout}s)"
        response.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    except requests.Timeout as e:
        logger.error(f"[{request_id}] ⏱️  Download timeout")
        response.error_code = "DOWNLOAD_TIMEOUT"
        response.error_message = "Timeout khi download ảnh"
        response.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    except Exception as e:
        logger.error(f"[{request_id}] ❌ Lỗi: {str(e)}")
        response.error_code = "AI_GENERATION_FAILED"
        response.error_message = f"Lỗi API: {str(e)}"
        response.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    return response


# ============================================================================
# STEP 3: LƯU ẢNH
# ============================================================================

def save_image_and_metadata(
        response: APIResponse,
        prompt_data: PromptData,
        data_dir: Path = DATA_DIR
) -> Tuple[bool, Path]:
    """Lưu ảnh base64 và metadata"""
    if response.status != "success" or not response.result_image_base64:
        return (False, Path())

    try:
        image_filename = f"output_{response.request_id}.png"
        image_path = data_dir / image_filename

        image_bytes = base64.b64decode(response.result_image_base64)
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"[{response.request_id}] 💾 Lưu ảnh: {image_path}")

        metadata = {
            "request_id": response.request_id,
            "dataset_item_id": prompt_data.dataset_item_id,
            "style": prompt_data.style,
            "prompt": prompt_data.prompt_text,
            "model": response.model_used,
            "processing_time_ms": response.processing_time_ms
        }

        metadata_path = data_dir / f"metadata_{response.request_id}.txt"
        with open(metadata_path, "w", encoding="utf-8") as f:
            for k, v in metadata.items():
                f.write(f"{k}: {v}\n")

        return (True, image_path)

    except Exception as e:
        logger.error(f"[{response.request_id}] ❌ Lỗi lưu: {str(e)}")
        return (False, Path())


# ============================================================================
# STEP 4: GHI LOG CSV
# ============================================================================

def log_to_csv(
        response: APIResponse,
        prompt_data: PromptData,
        csv_path: Path = LOG_CSV_PATH
) -> bool:
    """Ghi log CSV theo mục 6 (OmniDraw_API_Spec.md)"""
    try:
        log_entry = ExperimentLog(
            request_id=response.request_id,
            timestamp=datetime.now().isoformat() + "Z",
            dataset_item_id=prompt_data.dataset_item_id,
            method_tag="text_to_drawing_baseline",
            input_type="text",
            style=prompt_data.style,
            ai_processing_time_ms=response.processing_time_ms,
            final_status=response.status,
            error_code=response.error_code
        )

        # Thay đổi 5: Comment lại code cũ, gọi hàm chung (giữ nguyên độ dài code)
        # is_new_file = not csv_path.exists()
        #
        # with open(csv_path, "a", newline="", encoding="utf-8") as f:
        #     writer = csv.DictWriter(f, fieldnames=asdict(log_entry).keys())
        #
        #     if is_new_file:
        #         writer.writeheader()
        #
        #     writer.writerow(asdict(log_entry))

        log_experiment_csv(asdict(log_entry), str(csv_path))

        logger.info(f"[{response.request_id}] 📊 Ghi log CSV")
        return True

    except Exception as e:
        logger.error(f"[{response.request_id}] ❌ Lỗi ghi CSV: {str(e)}")
        return False


# ============================================================================
# STEP 5: MAIN
# ============================================================================

def process_all_prompts(
        prompts: List[PromptData],
        api_call_fn=call_openai_image_api,
        dry_run: bool = False
) -> Dict[str, int]:
    """Xử lý tất cả 15 prompt"""
    stats = {"success": 0, "failed": 0, "timeout": 0, "total": len(prompts)}

    logger.info("=" * 70)
    logger.info(f"🚀 BẮT ĐẦU XỬ LÝ {len(prompts)} PROMPT")
    logger.info("=" * 70)

    for idx, prompt_data in enumerate(prompts, 1):
        req_id = str(uuid.uuid4())
        logger.info(f"\n[{idx}/{len(prompts)}] Xử lý {prompt_data.dataset_item_id}...")

        if dry_run:
            logger.info(f"[DRY_RUN] Bỏ qua gọi API")
            response = APIResponse(
                request_id=req_id,
                status="success",
                processing_time_ms=1000,
                model_used="mock-model"
            )
        else:
            response = api_call_fn(
                prompt=prompt_data.prompt_text,
                request_id=req_id,
                style=prompt_data.style
            )

        if response.status == "success":
            save_image_and_metadata(response, prompt_data)
            stats["success"] += 1
        else:
            if response.error_code == "AI_TIMEOUT":
                stats["timeout"] += 1
            else:
                stats["failed"] += 1

        log_to_csv(response, prompt_data)

    logger.info("\n" + "=" * 70)
    logger.info(f"✅ HOÀN THÀNH: {stats['success']}/{stats['total']} thành công")
    logger.info(f"   ⏱️  Timeout: {stats['timeout']}")
    logger.info(f"   ❌ Failed: {stats['failed']}")
    logger.info(f"📊 Log CSV: {LOG_CSV_PATH}")
    logger.info("=" * 70 + "\n")

    return stats


def main():
    """Main entry point"""
    try:
        prompts = load_prompts_from_docx(DOCX_PATH)

        if not prompts:
            logger.error("❌ Không tìm thấy prompt!")
            sys.exit(1)

        # Đã đặt dry_run=True để chạy giả lập
        stats = process_all_prompts(prompts, dry_run=True)

        sys.exit(0 if stats["success"] > 0 else 1)

    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()