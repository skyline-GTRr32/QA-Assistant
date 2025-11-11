#!/bin/sh
# Startup script for Railway deployment
# Checks Playwright and starts the server with proper PORT handling

# Check Playwright browsers
python check_playwright.py

# Start uvicorn with PORT from environment (Railway sets this)
# Default to 8000 if PORT is not set
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --loop asyncio

