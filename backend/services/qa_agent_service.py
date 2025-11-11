# backend/services/qa_agent_service.py
import os
import json
import re
from groq import Groq
import logging
from .rag_service import RAGService # Import RAGService

logging.basicConfig(level=logging.INFO)

class WebsiteAnalyzerAgent:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        
    def analyze_with_rag(self, scraped_data: dict, rag_service: RAGService, run_id: str) -> dict:
        """
        Analyzes scraped data using RAG to get context from the design doc.
        """
        print("\n" + "="*70)
        print("🤖 AI-Powered Website Analysis Starting (with RAG)...")
        print("="*70 + "\n")

        # Make comprehensive, targeted RAG queries for each component type
        queries = [
            "primary button btn-primary styling background border color",
            "secondary button btn-secondary styling background border color",
            "color palette primary colors blue purple hex codes",
            "typography font sizes responsive breakpoints rem px",
            "layout grid flexbox sections components",
            "content headings h1 h2 h3 count structure"
        ]
        
        all_contexts = []
        for query in queries:
            rag_result = rag_service.query_collection(query, run_id, k=3)
            context = rag_result.get("context", "")
            if context:
                all_contexts.append(f"[Query: {query}]\n{context}\n")
        
        design_context = "\n---\n".join(all_contexts) if all_contexts else "No relevant design documentation found."

        analysis_data = self._prepare_analysis_data(scraped_data)
        
        report = self._generate_comparison_report(analysis_data, design_context)
        report['url'] = scraped_data.get('url') # Add URL to the report
        
        return report

    def _prepare_analysis_data(self, scraped_data: dict) -> dict:
        return {
            'color_palette': self._extract_colors(scraped_data),
            'typography': self._extract_typography(scraped_data),
            'layout': self._analyze_layout(scraped_data),
            'content': self._analyze_content(scraped_data)
        }

    def _extract_colors(self, data: dict) -> list[str]:
        colors = set()
        if 'styles' in data and 'inline' in data['styles']:
            for style in data['styles']['inline']:
                if 'styles' in style:
                    color_matches = re.findall(
                        r'(?:color|background-color|border-color|background):\s*(#[0-9a-fA-F]{3,6}|rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)|rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*|hsl\(\s*\d+\s*,\s*[\d.]+%\s*,\s*[\d.]+%\s*\))',
                        style['styles']
                    )
                    colors.update(color_matches)
        return list(colors)

    def _extract_typography(self, data: dict) -> dict:
        typography = {'font_families': set(), 'font_sizes': set(), 'line_heights': set()}
        if 'styles' in data and 'inline' in data['styles']:
            for style in data['styles']['inline']:
                if 'styles' in style:
                    font_matches = re.findall(r'font-family:\s*([^;]+)', style['styles'])
                    for match in font_matches:
                        fonts = [f.strip(" '\"") for f in match.split(',')]
                        typography['font_families'].update(fonts)
                    size_matches = re.findall(r'font-size:\s*([^;]+)', style['styles'])
                    typography['font_sizes'].update(size_matches)
                    line_height_matches = re.findall(r'line-height:\s*([^;]+)', style['styles'])
                    typography['line_heights'].update(line_height_matches)
        return {k: list(v) for k, v in typography.items()}

    def _analyze_layout(self, data: dict) -> dict:
        layout = {'media_queries': [], 'grid_usage': False, 'flexbox_usage': False}
        if 'styles' in data and 'css_rules' in data['styles']:
            for rule in data['styles']['css_rules']:
                if 'media' in rule and rule['media']:
                    layout['media_queries'].append(rule['media'])
                if 'cssText' in rule:
                    if 'display: grid' in rule['cssText']: layout['grid_usage'] = True
                    if 'display: flex' in rule['cssText']: layout['flexbox_usage'] = True
        return layout

    def _analyze_content(self, data: dict) -> dict:
        content = {'headings': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}, 'image_count': 0, 'form_count': 0, 'word_count': 0}
        if 'html' in data:
            html = data['html'].lower()
            for h in content['headings'].keys():
                content['headings'][h] = html.count(f'<{h}')
            content['image_count'] = html.count('<img')
            content['form_count'] = html.count('<form')
            text = re.sub(r'<[^>]+>', ' ', html)
            content['word_count'] = len(text.split())
        return content

    def _generate_comparison_report(self, analysis_data: dict, design_context: str) -> dict:
        """Generate a comparison report using Groq LLM with a strict QA system prompt and the provided context."""
        system_prompt = """🚨 CRITICAL ANALYSIS RULES (READ FIRST) 🚨

BEFORE REPORTING ANY ISSUE:
1) Use RAG to find the EXACT specification in the document
2) Quote the EXACT text from document with page number
3) Compare ONLY the exact value mentioned in document
4) For responsive specs, identify the correct breakpoint
5) If specification is NOT explicitly in document, DO NOT report it as mismatch

STEP-BY-STEP COMPARISON PROCESS:
Step 1: EXTRACT from Document (using RAG)
- Query: "primary blue color specification"
- Find: "#2563eb (blue-600) - Primary blue for text and elements" (page 1)
- Expected value: #2563eb (NOT #3b82f6)

Step 2: EXTRACT from Website (from scraped CSS)
- Search scraped CSS for: color, background-color, border-color
- Find: "color: #2563eb" in button styles
- Found value: #2563eb

Step 3: COMPARE
- Expected: #2563eb
- Found: #2563eb
- Result: ✅ MATCH

Step 4: REPORT
- Only report if MISMATCH
- If MATCH, add to verified list

RESPONSIVE VALUES (Font Sizes, Layouts):
- Document specifies values per breakpoint:
  "Mobile (base): 1.5rem"
  "Large (1024px+): 3rem"
- Check scraped CSS at CORRECT breakpoint:
  - Mobile check: @media (max-width: 1023px) → expect 1.5rem
  - Desktop check: @media (min-width: 1024px) → expect 3rem
- NEVER compare mobile spec to desktop implementation!

VAGUE SPECIFICATIONS:
If document says "use grid layout", you must:
- Find WHICH section should use grid
- Find expected grid configuration (columns, gaps)
- Quote exact text: "Features section: 1→2→3→4→5 columns at breakpoints" (page X)
- Check scraped CSS for that specific section
- Report: "Features section (#features) should use CSS Grid with 3 columns on large screens (Doc page 10), but found Flexbox"

MISSING SPECIFICATIONS:
If RAG returns no results for a query:
- DO NOT report it as an issue
- DO NOT invent expected values
- Skip that check entirely

VERIFICATION PROCESS (FOR EVERY COMPARISON, SHOW YOUR WORK):
1) Show your RAG query
2) Show the exact doc evidence with page number
3) Show the exact website evidence from scraped CSS/HTML
4) Show the comparison result (match|mismatch)

# QA ANALYST SYSTEM PROMPT

You are an expert QA analyst with 10+ years of experience comparing live websites to design documentation. Your job is to provide accurate, actionable quality assurance reports.

## CORE IDENTITY
- Role: Senior QA Analyst specializing in web design compliance
- Expertise: Color theory, typography, responsive design, CSS, HTML5, accessibility
- Goal: Identify REAL discrepancies between documentation and implementation
- Output: Professional, precise, actionable QA reports

## CRITICAL RULES (NEVER BREAK THESE)
Rule 1: BE DECISIVE
- Use ONLY two status values: "match" or "mismatch"
- If 99% matches but 1% doesn't → Status: "mismatch"
- If 100% matches → Status: "match"

Rule 2: BE SPECIFIC
- Always cite EXACT values (hex codes, pixel sizes, rem units)
- Always cite page numbers from the documentation
- Always cite CSS selectors or HTML element locations

Rule 3: BE HONEST
- If something matches perfectly → say "match" and move on
- Don't invent issues

Rule 4: NO HEDGING LANGUAGE
- BANNED: "may be", "might be", "could be", "possibly", "seems to", "appears to", "looks like", "mostly", "generally", "usually", "typically", "approximately", "roughly", "around", "some", "various", "certain"
- REQUIRED: "matches exactly", "does not match", "found", "verified", "confirmed", "expected [value], found [value]", "compliant", "non-compliant"

Rule 5: EVIDENCE-BASED ANALYSIS
- Every claim must be backed by scraped data (computed styles or HTML)
- Compare actual CSS values, not visuals
- Verify measurements in exact units (px, rem, %, vh/vw)

Rule 6: PRIORITIZE ISSUES
- HIGH: Breaks UX, violates branding, accessibility failure
- MEDIUM: Noticeable inconsistency, minor usability impact
- LOW: Minor deviation, negligible user impact

Rule 7: ACTIONABLE REPORTING — Each issue must include:
1) What's wrong (specific element)
2) What was expected (exact quote from documentation with page number)
3) What was found (exact CSS/HTML from scraped data)
4) Where it is (CSS selector or section ID)
5) Impact (High/Medium/Low)
6) Screenshot is taken only if issue exists (we will handle screenshots using returned selectors)

## OUTPUT CONTRACT (STRICT)
You MUST return a single valid JSON object with the following exact schema. Do not include any extra keys or commentary. All category.status values must be either "match" or "mismatch".
{
  "verification_process": [
    {
      "rag_query": "string",
      "doc_evidence": "string",
      "doc_page": "string",
      "website_evidence": "string",
      "comparison": "match|mismatch"
    }
  ],
  "color_analysis": {
    "status": "match|mismatch",
    "details": "string",
    "issues": [
      {
        "description": "string",
        "selector": "string|null",
        "expected": "string",
        "found": "string",
        "location": "string",
        "impact": "High|Medium|Low",
        "doc_page": "string",
        "reason": "string"
      }
    ]
  },
  "typography_analysis": {
    "status": "match|mismatch",
    "details": "string",
    "issues": [
      {
        "description": "string",
        "selector": "string|null",
        "expected": "string",
        "found": "string",
        "location": "string",
        "impact": "High|Medium|Low",
        "doc_page": "string",
        "reason": "string"
      }
    ]
  },
  "layout_analysis": {
    "status": "match|mismatch",
    "details": "string",
    "issues": [
      {
        "description": "string",
        "selector": "string|null",
        "expected": "string",
        "found": "string",
        "location": "string",
        "impact": "High|Medium|Low",
        "doc_page": "string",
        "reason": "string"
      }
    ]
  },
  "content_analysis": {
    "status": "match|mismatch",
    "details": "string",
    "issues": [
      {
        "description": "string",
        "selector": "string|null",
        "expected": "string",
        "found": "string",
        "location": "string",
        "impact": "High|Medium|Low",
        "doc_page": "string",
        "reason": "string"
      }
    ]
  },
  "overall_assessment": "string",
  "recommendations": ["string"]
}
"""

        # Build the user content that provides the dynamic inputs for the analysis
        user_content = f"""
DESIGN DOCUMENTATION CONTEXT (RAG):
        {design_context}

SCRAPED WEBSITE ANALYSIS DATA:
        {json.dumps(analysis_data, indent=2)}

TASK:
1) Extract ALL specifications from the documentation context (with exact quotes and page numbers).
2) Compare against the scraped website data (computed CSS/HTML).
3) Apply the CRITICAL RULES strictly (statuses only "match" or "mismatch").
4) Include a 'verification_process' array that shows your RAG query, doc evidence (with page), website evidence, and the comparison result for each check performed.
5) Return a single JSON object that strictly matches the OUTPUT CONTRACT schema above.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.1,
                max_tokens=3500,
                response_format={"type": "json_object"}
            )
            report = json.loads(response.choices[0].message.content)
            return report
        except Exception as e:
            logging.error(f"Error generating comparison report: {str(e)}")
            return {"error": str(e)}

    def generate_summary_report(self, comparison_report: dict) -> str:
        try:
            prompt = f"""
            Convert the following detailed comparison report into a clear, concise summary report in markdown format.
            Focus on key findings, major issues, and top recommendations.

            COMPARISON REPORT:
            {json.dumps(comparison_report, indent=2)}
            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical writer creating clear, concise reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error generating summary report: {str(e)}")
            return f"Error generating summary: {str(e)}"