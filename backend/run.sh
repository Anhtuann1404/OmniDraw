#!/bin/bash
# OmniDraw - Chạy backend từ thư mục backend
cd "$(dirname "$0")"
if [ -f "venv/bin/uvicorn" ]; then
    venv/bin/uvicorn main:app --reload --port 8000
elif [ -f "venv/bin/python" ]; then
    venv/bin/python main.py
else
    python3 main.py
fi
