# Website QA Analysis Tool

AI-powered website quality assurance tool that compares live websites against design documentation.

## Architecture

- **Frontend**: Next.js 14 (App Router) + TypeScript + Chakra UI
- **Backend**: FastAPI + Python
- **AI**: OpenAI GPT-4o-mini + RAG (ChromaDB + Sentence Transformers)
- **Scraping**: Playwright (headless browser)

## Features

- 🔍 Automated website scraping and analysis
- 📄 Document processing with RAG
- 🤖 Multi-agent AI analysis system
- 📊 Performance metrics (PageSpeed Insights)
- 📸 Screenshot capture for issues
- 📑 Professional PDF reports

## Project Structure

```
.
├── backend/          # FastAPI backend
│   ├── services/    # Core services
│   ├── main.py      # FastAPI app
│   └── requirements.txt
├── frontend/        # Next.js frontend
│   ├── app/         # App router pages
│   ├── src/         # Components and services
│   └── package.json
└── README.md
```

## Setup

### Backend

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
```

2. Set environment variables:
```bash
OPENAI_API_KEY=your_key_here
```

3. Run:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set environment variables:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run:
```bash
npm run dev
```

## Deployment

### Backend (Railway)

1. Connect GitHub repo to Railway
2. Set environment variables in Railway dashboard
3. Add build command: `pip install -r requirements.txt && playwright install chromium`
4. Deploy!

### Frontend (Vercel)

1. Connect GitHub repo to Vercel
2. Set `NEXT_PUBLIC_API_URL` to Railway backend URL
3. Deploy!

## License

MIT

