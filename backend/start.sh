#!/bin/sh
# Startup script for Railway deployment
# Starts the server with proper PORT handling

# Note: Playwright is only needed for screenshots, not for scraping
# If screenshots are needed, Playwright browsers should be installed
# For now, we skip the check to speed up startup

# Start uvicorn with PORT from environment (Railway sets this)
# Default to 8000 if PORT is not set
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --loop asyncio

