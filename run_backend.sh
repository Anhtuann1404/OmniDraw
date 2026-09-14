#!/bin/bash
# OmniDraw - Khởi động máy chủ Backend tự động
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

echo "=========================================="
echo "  🚀 Khởi động OmniDraw Backend..."
echo "=========================================="

if [ -f "$BACKEND_DIR/venv/bin/uvicorn" ]; then
    echo "✔ Đang sử dụng môi trường ảo: backend/venv"
    "$BACKEND_DIR/venv/bin/uvicorn" main:app --app-dir "$BACKEND_DIR" --reload --port 8000
elif [ -f "$BACKEND_DIR/venv/bin/python" ]; then
    echo "✔ Đang sử dụng python trong venv: backend/venv"
    "$BACKEND_DIR/venv/bin/python" "$BACKEND_DIR/main.py"
else
    echo "⚠ Chưa phát hiện venv, đang chạy bằng python3 hệ thống..."
    python3 "$BACKEND_DIR/main.py"
fi
