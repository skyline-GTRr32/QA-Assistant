# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from pathlib import Path
import uuid
from dotenv import load_dotenv

# Import all services
from services.rag_service import RAGService
# Use new multi-agent system (v2) - true AI agent with 3 LLM calls
from services.qa_agent_service_simple import WebsiteAnalyzerAgent
from services.scraper_service import ScraperService
from services.screenshot_service import ScreenshotService
from services.performance_service import PerformanceService
from services.pdf_service import PDFService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Website QA Agent API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Initialize all services
rag_service = RAGService()
# Use OPENAI_API_KEY for OpenAI GPT models
qa_agent = WebsiteAnalyzerAgent(os.getenv("OPENAI_API_KEY"))
scraper = ScraperService()
screenshot_service = ScreenshotService()
performance_service = PerformanceService()
pdf_service = PDFService()

# Create directories
RUNS_DIR = Path("runs")
RUNS_DIR.mkdir(exist_ok=True)

@app.post("/api/analyze")
def analyze_full_website(url: str = Form(...), file: UploadFile = File(...)):
    run_id = str(uuid.uuid4())
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir()
    temp_file_path = run_dir / file.filename

    try:
        # 1. Process Document with RAG
        print(f"[{run_id}] Processing document...")
        with open(temp_file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        if not rag_service.process_and_index_file(temp_file_path, run_id):
            raise HTTPException(500, "Failed to process and index the document. It might be empty or corrupted.")

        # 2. Scrape Website
        print(f"[{run_id}] Scraping {url}...")
        scrape_result = scraper.scrape_website(url)
        if not scrape_result.get("success"):
            raise HTTPException(500, f"Scraping failed: {scrape_result.get('error')}")
        scraped_data = scrape_result["data"]
        
        # --- FIX: ADD THE URL TO THE SCRAPED DATA ---
        # This ensures the URL is available for the report generation.
        scraped_data["url"] = url

        # 3. Get Performance Metrics
        print(f"[{run_id}] Analyzing performance...")
        performance_data = performance_service.analyze(url)

        # 4. AI Analysis using RAG context
        print(f"[{run_id}] AI is analyzing the website against the document...")
        report = qa_agent.analyze_with_rag(scraped_data, rag_service, run_id, run_dir)
        if "error" in report:
            raise HTTPException(500, f"AI analysis failed: {report['error']}")

        # 5. Take Screenshots of Issues
        print(f"[{run_id}] Taking screenshots of issues...")
        report_with_screenshots = screenshot_service.capture_issues(url, report, run_dir)

        # 6. Generate Text Summary
        print(f"[{run_id}] Generating summary...")
        summary = qa_agent.generate_summary_report(report_with_screenshots)

        # 7. Generate Final PDF Report
        print(f"[{run_id}] Generating PDF report...")
        pdf_path = pdf_service.generate_report(report_with_screenshots, summary, performance_data, run_dir)
        
        print(f"[{run_id}] Analysis complete! PDF report at: {pdf_path}")
        return FileResponse(path=pdf_path, media_type='application/pdf', filename=f"QA_Report_{run_id}.pdf")

    except Exception as e:
        print(f"[{run_id}] An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print(f"[{run_id}] Cleaning up resources...")
        if temp_file_path.exists():
            temp_file_path.unlink()
        rag_service.cleanup_collection(run_id)

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}