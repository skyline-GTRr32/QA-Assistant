#!/bin/sh
# Startup script for Railway deployment
# Start uvicorn server with PORT from environment (Railway sets this)
PORT="${PORT:-8000}"
exec python -m uvicorn main:app --host 0.0.0.0 --port "$PORT" --loop asyncio

