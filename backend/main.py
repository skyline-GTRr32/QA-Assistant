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
app = FastAPI(
    title="Website QA Agent API",
    description="AI-powered website quality assurance tool",
    version="1.0.0"
)
# CORS: Allow all origins for now (you can restrict to your Vercel domain later)
# Example: allow_origins=["https://qa-assistant-sigma.vercel.app", "https://your-domain.vercel.app"]
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Initialize all services with error handling
rag_service = None
qa_agent = None
scraper = None
screenshot_service = None
performance_service = None
pdf_service = None

try:
    print("Initializing services...")
    rag_service = RAGService()
    print("✓ RAG Service initialized")
except Exception as e:
    print(f"✗ Failed to initialize RAG Service: {e}")
    print("⚠ Application will start but RAG features will not work")

try:
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠ OPENAI_API_KEY not found, QA Agent will not work")
    else:
        qa_agent = WebsiteAnalyzerAgent(openai_key)
        print("✓ QA Agent initialized")
except Exception as e:
    print(f"✗ Failed to initialize QA Agent: {e}")

try:
    scraper = ScraperService()
    print("✓ Scraper Service initialized")
except Exception as e:
    print(f"✗ Failed to initialize Scraper Service: {e}")

try:
    screenshot_service = ScreenshotService()
    print("✓ Screenshot Service initialized")
except Exception as e:
    print(f"✗ Failed to initialize Screenshot Service: {e}")

try:
    performance_service = PerformanceService()
    print("✓ Performance Service initialized")
except Exception as e:
    print(f"✗ Failed to initialize Performance Service: {e}")

try:
    pdf_service = PDFService()
    print("✓ PDF Service initialized")
except Exception as e:
    print(f"✗ Failed to initialize PDF Service: {e}")

print("Service initialization complete!")

# Create directories
RUNS_DIR = Path("runs")
RUNS_DIR.mkdir(exist_ok=True)

@app.post("/api/analyze")
def analyze_full_website(url: str = Form(...), file: UploadFile = File(...)):
    # Check if required services are initialized
    if not rag_service:
        raise HTTPException(500, "RAG Service is not initialized. Check OPENAI_API_KEY environment variable.")
    if not qa_agent:
        raise HTTPException(500, "QA Agent is not initialized. Check OPENAI_API_KEY environment variable.")
    if not scraper:
        raise HTTPException(500, "Scraper Service is not initialized.")
    
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
        if performance_service:
            performance_data = performance_service.analyze(url)
        else:
            print("⚠ Performance service not available, using empty data")
            performance_data = {}

        # 4. AI Analysis using RAG context
        print(f"[{run_id}] AI is analyzing the website against the document...")
        report = qa_agent.analyze_with_rag(scraped_data, rag_service, run_id, run_dir)
        if "error" in report:
            raise HTTPException(500, f"AI analysis failed: {report['error']}")

        # 5. Take Screenshots of Issues
        print(f"[{run_id}] Taking screenshots of issues...")
        if screenshot_service:
            report_with_screenshots = screenshot_service.capture_issues(url, report, run_dir)
        else:
            print("⚠ Screenshot service not available, skipping screenshots")
            report_with_screenshots = report

        # 6. Generate Text Summary
        print(f"[{run_id}] Generating summary...")
        summary = qa_agent.generate_summary_report(report_with_screenshots)

        # 7. Generate Final PDF Report
        print(f"[{run_id}] Generating PDF report...")
        if not pdf_service:
            raise HTTPException(500, "PDF Service is not initialized.")
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

@app.get("/")
def root():
    return {
        "message": "Website QA Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "analyze": "/api/analyze (POST)",
            "docs": "/docs"
        }
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}