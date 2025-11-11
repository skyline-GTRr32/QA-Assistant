FROM python:3.11-slim

# Install system dependencies (including Playwright system deps)
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    gcc \
    make \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (for better caching)
# Note: Root directory is set to 'backend' in Railway, so paths are relative to backend/
COPY requirements.txt ./requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Install Playwright browsers with system dependencies
# Use --with-deps to install all required system libraries
RUN playwright install --with-deps chromium

# Verify Playwright installation
RUN python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(headless=True); browser.close(); p.stop(); print('Playwright Chromium verified!')"

# Copy backend code (all files from backend/ directory)
COPY . .

# Expose port
EXPOSE $PORT

# Start command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}", "--loop", "asyncio"]
