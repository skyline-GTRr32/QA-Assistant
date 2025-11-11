# backend/services/qa_agent_service_v2.py
"""
True AI Agent Architecture for QA Analysis

Multi-Agent System:
1. Planning Agent - Creates verification checklist from document
2. Extraction Agent - Extracts specs and compares with website
3. Verification Agent - Validates findings and removes false positives
"""

import os
import json
import re
from openai import OpenAI
import logging
from typing import Dict, List, Any, Optional
from .rag_service import RAGService

logging.basicConfig(level=logging.INFO)


class WebsiteAnalyzerAgent:
    """
    True AI Agent with multi-LLM architecture:
    - Agent 1: Planning (creates checklist)
    - Agent 2: Extraction & Comparison (finds issues)
    - Agent 3: Verification (validates findings)
    """
    
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini"  # Using OpenAI GPT-4o-mini
        
    def analyze_with_rag(self, scraped_data: dict, rag_service: RAGService, run_id: str) -> dict:
        """
        Main agent orchestration - runs 3 agent phases sequentially.
        """
        print("\n" + "="*70)
        print("🤖 Multi-Agent QA Analysis Starting...")
        print("="*70 + "\n")
        
        # Prepare analysis data from scraped website
        analysis_data = self._prepare_analysis_data(scraped_data)
        
        # ============================================
        # AGENT 1: PLANNING AGENT
        # ============================================
        print("\n[AGENT 1] Planning Agent: Creating verification checklist...")
        verification_checklist = self._planning_agent(rag_service, run_id, analysis_data)
        print(f"✓ Planning complete. Checklist has {len(verification_checklist)} items.\n")
        
        # ============================================
        # AGENT 2: EXTRACTION & COMPARISON AGENT
        # ============================================
        print("\n[AGENT 2] Extraction Agent: Comparing specs with website...")
        raw_findings = self._extraction_agent(
            rag_service, run_id, analysis_data, verification_checklist
        )
        print(f"✓ Extraction complete. Found {len(raw_findings)} potential issues.\n")
        
        # ============================================
        # AGENT 3: VERIFICATION AGENT
        # ============================================
        print("\n[AGENT 3] Verification Agent: Validating findings...")
        verified_report = self._verification_agent(
            rag_service, run_id, raw_findings, analysis_data
        )
        print(f"✓ Verification complete. Final report has {len(verified_report.get('all_issues', []))} verified issues.\n")
        
        # Format final report
        final_report = self._format_final_report(verified_report, scraped_data)
        final_report['url'] = scraped_data.get('url')
        
        return final_report
    
    # ============================================
    # AGENT 1: PLANNING AGENT
    # ============================================
    def _planning_agent(
        self, rag_service: RAGService, run_id: str, analysis_data: dict
    ) -> List[Dict[str, Any]]:
        """
        LLM Call 1: Creates a structured verification checklist.
        
        This agent:
        - Queries RAG to understand document structure
        - Identifies what components/specs exist
        - Creates prioritized checklist of what to verify
        """
        
        # Get document overview
        overview_queries = [
            "UI components buttons primary secondary styling",
            "color palette specifications hex codes",
            "typography font sizes responsive breakpoints",
            "layout grid flexbox sections",
            "content structure headings navigation"
        ]
        
        doc_overview = []
        for query in overview_queries:
            result = rag_service.query_collection(query, run_id, k=2)
            if result.get("context"):
                doc_overview.append(f"[{query}]\n{result['context']}\n")
        
        doc_context = "\n---\n".join(doc_overview)
        
        system_prompt = """You are a Planning Agent for QA analysis.

Your job: Analyze the design document and create a structured verification checklist.

Process:
1. Review the document context provided
2. Identify all UI components, colors, typography, layout specs mentioned
3. Create a prioritized checklist of what needs to be verified

Output format (JSON):
{
  "checklist": [
    {
      "category": "color|typography|layout|content",
      "component": "primary_button|secondary_button|heading_h1|...",
      "property": "background-color|font-size|display|...",
      "priority": "high|medium|low",
      "rag_query": "specific query to find this spec in document"
    }
  ]
}

Rules:
- Only include items explicitly mentioned in document
- Prioritize high-impact items (branding, accessibility)
- Be specific about what property to check
"""

        user_prompt = f"""DESIGN DOCUMENT CONTEXT:
{doc_context}

SCRAPED WEBSITE DATA SUMMARY:
- Colors found: {len(analysis_data.get('color_palette', []))} unique colors
- Typography: {len(analysis_data.get('typography', {}).get('font_families', []))} font families
- Layout: Grid={analysis_data.get('layout', {}).get('grid_usage')}, Flexbox={analysis_data.get('layout', {}).get('flexbox_usage')}
- Content: {sum(analysis_data.get('content', {}).get('headings', {}).values())} headings total

Create a verification checklist of what to compare.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            checklist = result.get("checklist", [])
            
            # Log checklist
            for i, item in enumerate(checklist, 1):
                print(f"  {i}. [{item.get('category')}] {item.get('component')}.{item.get('property')} (priority: {item.get('priority')})")
            
            return checklist
            
        except Exception as e:
            logging.error(f"Planning agent error: {e}")
            # Fallback to default checklist
            return self._default_checklist()
    
    def _default_checklist(self) -> List[Dict[str, Any]]:
        """Fallback checklist if planning agent fails."""
        return [
            {"category": "color", "component": "primary_button", "property": "background-color", "priority": "high", "rag_query": "primary button background color"},
            {"category": "color", "component": "secondary_button", "property": "background-color", "priority": "high", "rag_query": "secondary button background color border"},
            {"category": "typography", "component": "heading_h1", "property": "font-size", "priority": "high", "rag_query": "heading h1 font size responsive"},
        ]
    
    # ============================================
    # AGENT 2: EXTRACTION & COMPARISON AGENT
    # ============================================
    def _extraction_agent(
        self,
        rag_service: RAGService,
        run_id: str,
        analysis_data: dict,
        checklist: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        LLM Call 2: Extracts specs and compares with website.
        Processes items in batches to avoid context length issues.
        """
        
        system_prompt = """You are an Extraction & Comparison Agent for QA analysis.

Your job: For each checklist item, extract the spec from document and compare with website.

CRITICAL PROCESS FOR EACH ITEM:

Step 1: EXTRACT FROM DOCUMENT
- Read the doc_context carefully
- Find the EXACT specification for this component and property
- Quote the exact text from document
- Extract the exact value (e.g., "#2563eb", "white", "1.5rem", "600")

Step 2: SEARCH IN WEBSITE DATA
- Look in the scraped website data for this value
- For component-specific properties (buttons, cards, headings):
  * Check components.{component_name} object (e.g., components.primary_button, components.secondary_button)
  * Look for the property name (e.g., background-color, color, border, font-size, font-weight)
- For colors: Also search in color_palette.all_colors array
- For typography: Also search in typography.font_families, font_sizes, or line_heights
- For layout: Check layout.grid_usage or flexbox_usage
- For content: Check content.headings or image_count

EXAMPLE:
- If checking "primary_button.background-color":
  * Look in components.primary_button["background-color"] or components.primary_button["background"]
  * Also check if the value appears in color_palette.all_colors

Step 3: NORMALIZE AND COMPARE VALUES

COLOR NORMALIZATION (CRITICAL):
- Convert all colors to the same format for comparison
- Hex to RGB: #2563eb = rgb(37, 99, 235) = rgb(37,99,235) = rgb(37 99 235)
- Named colors: "white" = "#ffffff" = "rgb(255, 255, 255)" = "rgb(255 255 255)"
- CSS variables: Strip CSS variables like "/var(--tw-text-opacity)" - only compare the base color
- Gradients: "linear-gradient from #2563eb to #9333ea" = "linear-gradient(to right, rgb(37, 99, 235), rgb(147, 51, 234))" (same colors, different format)

EQUIVALENT VALUES (THESE ARE MATCHES):
- "#2563eb" = "rgb(37, 99, 235)" = "rgb(37,99,235)" = "rgb(37 99 235)" → MATCH
- "white" = "#ffffff" = "rgb(255, 255, 255)" = "rgb(255 255 255)" → MATCH
- "linear-gradient from #2563eb to #9333ea" = "linear-gradient(to right, rgb(37, 99, 235), rgb(147, 51, 234))" → MATCH (same colors)
- "700" = "bold" (for font-weight) → MATCH
- "600" = "semibold" (for font-weight) → MATCH

Step 4: COMPARE
- Normalize both expected and found values
- If normalized values are EQUIVALENT → status: "match" (DO NOT REPORT - it's compliant!)
- If normalized values are DIFFERENT → status: "mismatch" (REPORT with expected vs found)
- If doc_context has NO spec → Skip this item entirely (DO NOT REPORT)
- If spec exists but value not found in website data → status: "missing" (REPORT)

CRITICAL RULES:
1. NORMALIZE values before comparing (colors, font-weights, etc.)
2. ONLY report items with status "mismatch" or "missing"
3. DO NOT report items with status "match" (they're compliant, no issue)
4. DO NOT report items where doc_context has no spec (can't verify)
5. Always quote EXACT text from doc_context as doc_evidence
6. Always show EXACT value from website (or "not found")
7. When reporting, show both normalized comparison AND original values

Output format (JSON):
{
  "findings": [
    {
      "category": "color|typography|layout|content",
      "component": "primary_button",
      "property": "background-color",
      "doc_evidence": "exact quote from document showing the spec",
      "doc_page": "section or page reference",
      "expected_value": "exact value from doc (e.g., #2563eb)",
      "website_evidence": "where you searched (e.g., color_palette.all_colors)",
      "found_value": "exact value found in website (or 'not found')",
      "status": "mismatch|missing",
      "selector": "CSS selector if available",
      "impact": "high|medium|low"
    }
  ]
}

REMEMBER: Only include findings with status "mismatch" or "missing". Do NOT include "match" items.
"""

        # Provide structured, component-specific data for easy comparison
        summary_data = {
            "color_palette": {
                "all_colors": analysis_data.get("color_palette", []),  # Full list - colors are small
                "count": len(analysis_data.get("color_palette", []))
            },
            "typography": {
                "font_families": analysis_data.get("typography", {}).get("font_families", []),
                "font_sizes": list(analysis_data.get("typography", {}).get("font_sizes", [])),  # Full list
                "line_heights": list(analysis_data.get("typography", {}).get("line_heights", []))
            },
            "layout": {
                "grid_usage": analysis_data.get("layout", {}).get("grid_usage", False),
                "flexbox_usage": analysis_data.get("layout", {}).get("flexbox_usage", False),
                "media_queries": analysis_data.get("layout", {}).get("media_queries", [])[:5]  # Sample
            },
            "content": {
                "headings": analysis_data.get("content", {}).get("headings", {}),
                "image_count": analysis_data.get("content", {}).get("image_count", 0)
            },
            "components": analysis_data.get("components", {})  # NEW: Component-specific styles
        }
        
        # Process checklist in batches of 3-4 items to avoid context overflow
        batch_size = 3
        all_findings = []
        
        for i in range(0, len(checklist), batch_size):
            batch = checklist[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(checklist) + batch_size - 1) // batch_size
            
            print(f"  Processing batch {batch_num}/{total_batches} ({len(batch)} items)...")
            
            # Get RAG context for this batch only
            batch_context = []
            for item in batch:
                rag_query = item.get("rag_query", "")
                component = item.get("component", "")
                property_name = item.get("property", "")
                
                # Make more specific RAG queries
                specific_query = f"{component} {property_name} {rag_query}"
                rag_result = rag_service.query_collection(specific_query, run_id, k=3)  # Increased back to k=3
                doc_context = rag_result.get("context", "No specification found in document.")
                
                # If no context found, try broader query
                if not doc_context or doc_context == "No specification found in document.":
                    broader_result = rag_service.query_collection(rag_query, run_id, k=2)
                    doc_context = broader_result.get("context", "No specification found in document.")
                
                # Truncate doc_context if too long (max 800 chars per item - increased)
                if len(doc_context) > 800:
                    # Try to keep the most relevant part (look for the component name)
                    if component.lower() in doc_context.lower():
                        idx = doc_context.lower().find(component.lower())
                        start = max(0, idx - 200)
                        end = min(len(doc_context), idx + 600)
                        doc_context = doc_context[start:end]
                    else:
                        doc_context = doc_context[:800] + "..."
                
                batch_context.append({
                    "item": item,
                    "doc_context": doc_context,
                    "rag_query_used": specific_query
                })
            
            user_prompt = f"""VERIFICATION CHECKLIST BATCH ({len(batch)} items):
{json.dumps(batch, indent=2)}

DOCUMENT CONTEXTS (from RAG queries):
{json.dumps([{"item": c["item"], "doc_context": c["doc_context"], "query": c.get("rag_query_used", "")} for c in batch_context], indent=2)}

SCRAPED WEBSITE DATA:
{json.dumps(summary_data, indent=2)}

INSTRUCTIONS FOR EACH CHECKLIST ITEM:

1. READ the doc_context carefully - it contains the specification from the design document
2. EXTRACT the exact value mentioned in doc_context (e.g., "#2563eb", "white", "1.5rem", etc.)
3. SEARCH the scraped website data for the corresponding value:
   - For colors: Check color_palette.all_colors array
   - For typography: Check typography.font_families, font_sizes, line_heights
   - For layout: Check layout.grid_usage, flexbox_usage
   - For content: Check content.headings, image_count
4. COMPARE:
   - If exact match found → status: "match" (don't report, it's compliant)
   - If different value found → status: "mismatch" (report with expected vs found)
   - If no value found in website data → status: "missing" (report)
   - If no spec in doc_context → Skip this item entirely

IMPORTANT:
- Only report items with status "mismatch" or "missing"
- For "match" items, don't include them in findings (they're compliant)
- Always quote the exact text from doc_context as doc_evidence
- Always show the exact value you found (or didn't find) in website data

Return findings as JSON (only include mismatches and missing items).
"""

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                
                # Fix invalid Unicode escapes before parsing JSON
                import re
                # Fix invalid \u escapes (they should be \uXXXX where XXXX is exactly 4 hex digits)
                # Replace incomplete \u escapes (1-3 hex digits) with valid ones
                def fix_unicode_escape(match):
                    hex_digits = match.group(1)
                    # Pad to 4 digits with zeros
                    padded = hex_digits.zfill(4)
                    return f'\\u{padded}'
                
                # Fix incomplete Unicode escapes
                content = re.sub(r'\\u([0-9a-fA-F]{1,3})(?![0-9a-fA-F])', fix_unicode_escape, content)
                
                try:
                    result = json.loads(content)
                except json.JSONDecodeError as je:
                    # If JSON parsing fails, try to fix common issues
                    try:
                        # Remove invalid Unicode escapes by encoding/decoding
                        content_clean = content.encode('utf-8', errors='ignore').decode('utf-8')
                        # Try to extract JSON object manually (in case there's extra text)
                        start = content_clean.find('{')
                        end = content_clean.rfind('}') + 1
                        if start >= 0 and end > start:
                            content_clean = content_clean[start:end]
                        result = json.loads(content_clean)
                    except Exception as e2:
                        logging.error(f"Extraction agent batch {batch_num} JSON parse error: {je}")
                        logging.error(f"Second attempt also failed: {e2}")
                        logging.error(f"Response content (first 500 chars): {content[:500]}")
                        continue
                
                batch_findings = result.get("findings", [])
                all_findings.extend(batch_findings)
                
            except Exception as e:
                logging.error(f"Extraction agent batch {batch_num} error: {e}")
                import traceback
                logging.error(traceback.format_exc())
                continue
        
        # Log total findings
        matches = [f for f in all_findings if f.get("status") == "match"]
        mismatches = [f for f in all_findings if f.get("status") == "mismatch"]
        missing = [f for f in all_findings if f.get("status") == "missing"]
        
        print(f"  ✓ Matches: {len(matches)}")
        print(f"  ✗ Mismatches: {len(mismatches)}")
        print(f"  ? Missing: {len(missing)}")
        
        return all_findings
    
    # ============================================
    # AGENT 3: VERIFICATION AGENT
    # ============================================
    def _verification_agent(
        self,
        rag_service: RAGService,
        run_id: str,
        raw_findings: List[Dict[str, Any]],
        analysis_data: dict
    ) -> Dict[str, Any]:
        """
        LLM Call 3: Validates findings and removes false positives.
        
        This agent:
        - Reviews each finding
        - Verifies document evidence exists
        - Removes false positives
        - Categorizes issues properly
        """
        
        system_prompt = """You are a Verification Agent for QA analysis.

Your job: Validate findings and remove false positives.

CRITICAL VALIDATION RULES:
1. If finding has NO doc_evidence → REJECT (false positive)
2. If doc_evidence is vague/assumed → REJECT (not explicit)
3. If expected_value doesn't match doc_evidence → REJECT (agent made up value)
4. If comparison is wrong (e.g., comparing mobile to desktop) → REJECT
5. Only KEEP findings with:
   - Explicit document quote
   - Exact value comparison
   - Clear mismatch evidence

Process:
- Review each finding
- Validate document evidence exists and matches
- Remove false positives
- Categorize remaining issues properly

Output format (JSON):
{
  "verified_issues": [
    {
      "category": "color|typography|layout|content",
      "description": "clear description",
      "expected": "exact value from doc",
      "found": "exact value from website",
      "location": "CSS selector or element",
      "impact": "high|medium|low",
      "doc_page": "page/section reference",
      "doc_evidence": "exact quote",
      "selector": "CSS selector for screenshot"
    }
  ],
  "rejected_findings": [
    {
      "finding": "original finding",
      "reason": "why it was rejected"
    }
  ],
  "summary": {
    "total_findings": 0,
    "verified_issues": 0,
    "rejected": 0,
    "by_category": {"color": 0, "typography": 0, "layout": 0, "content": 0}
  }
}
"""

        user_prompt = f"""RAW FINDINGS TO VERIFY ({len(raw_findings)} items):
{json.dumps(raw_findings, indent=2)}

Validate each finding:
1. Check if doc_evidence is explicit and matches expected_value
2. Verify comparison is correct (not mobile vs desktop, etc.)
3. Remove any false positives
4. Keep only verified issues with clear evidence

Return verified report as JSON.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            verified = result.get("verified_issues", [])
            rejected = result.get("rejected_findings", [])
            
            print(f"  ✓ Verified issues: {len(verified)}")
            print(f"  ✗ Rejected false positives: {len(rejected)}")
            
            if rejected:
                print("\n  Rejected findings:")
                for r in rejected[:5]:  # Show first 5
                    print(f"    - {r.get('reason', 'No reason')}")
            
            return {
                "all_issues": verified,
                "rejected": rejected,
                "summary": result.get("summary", {})
            }
            
        except Exception as e:
            logging.error(f"Verification agent error: {e}")
            # Fallback: return raw findings as-is
            return {
                "all_issues": raw_findings,
                "rejected": [],
                "summary": {"total_findings": len(raw_findings), "verified_issues": len(raw_findings)}
            }
    
    # ============================================
    # HELPER METHODS
    # ============================================
    def _format_final_report(self, verified_report: Dict, scraped_data: dict) -> Dict:
        """Formats verified findings into final report structure."""
        
        issues = verified_report.get("all_issues", [])
        
        # Group by category
        by_category = {
            "color": [],
            "typography": [],
            "layout": [],
            "content": []
        }
        
        for issue in issues:
            cat = issue.get("category", "color")
            if cat in by_category:
                by_category[cat].append({
                    "description": issue.get("description", ""),
                    "selector": issue.get("selector"),
                    "expected": issue.get("expected", ""),
                    "found": issue.get("found", ""),
                    "location": issue.get("location", ""),
                    "impact": issue.get("impact", "Medium"),
                    "doc_page": issue.get("doc_page", ""),
                    "reason": issue.get("reason", "")
                })
        
        # Build final report structure
        report = {
            "color_analysis": {
                "status": "match" if len(by_category["color"]) == 0 else "mismatch",
                "details": f"Found {len(by_category['color'])} color-related issues." if by_category["color"] else "All color specifications match the document.",
                "issues": by_category["color"]
            },
            "typography_analysis": {
                "status": "match" if len(by_category["typography"]) == 0 else "mismatch",
                "details": f"Found {len(by_category['typography'])} typography-related issues." if by_category["typography"] else "All typography specifications match the document.",
                "issues": by_category["typography"]
            },
            "layout_analysis": {
                "status": "match" if len(by_category["layout"]) == 0 else "mismatch",
                "details": f"Found {len(by_category['layout'])} layout-related issues." if by_category["layout"] else "All layout specifications match the document.",
                "issues": by_category["layout"]
            },
            "content_analysis": {
                "status": "match" if len(by_category["content"]) == 0 else "mismatch",
                "details": f"Found {len(by_category['content'])} content-related issues." if by_category["content"] else "All content specifications match the document.",
                "issues": by_category["content"]
            },
            "overall_assessment": verified_report.get("summary", {}).get("overall", "Analysis complete."),
            "recommendations": []
        }
        
        # Add recommendations if issues found
        if issues:
            report["recommendations"] = [
                "Review and fix verified issues listed above",
                "Ensure all specifications match the design document exactly",
                "Re-run analysis after fixes to verify compliance"
            ]
        
        return report
    
    def _prepare_analysis_data(self, scraped_data: dict) -> dict:
        """Prepares structured analysis data from scraped website with component-specific extraction."""
        return {
            'color_palette': self._extract_colors(scraped_data),
            'typography': self._extract_typography(scraped_data),
            'layout': self._analyze_layout(scraped_data),
            'content': self._analyze_content(scraped_data),
            'components': self._extract_component_styles(scraped_data)  # NEW: Component-specific styles
        }
    
    def _extract_component_styles(self, data: dict) -> dict:
        """
        Extracts styles for specific components (buttons, cards, etc.) from scraped data.
        This makes it easier for the agent to find exact values.
        """
        components = {
            'primary_button': {},
            'secondary_button': {},
            'card': {},
            'heading_h1': {},
            'heading_h2': {},
            'heading_h3': {},
            'navigation': {},
            'hero_section': {},
            'footer': {}
        }
        
        # Extract from inline styles
        if 'styles' in data and 'inline' in data['styles']:
            for style in data['styles'].get('inline', []):
                selector = style.get('selector', '').lower()
                styles_text = style.get('styles', '')
                
                # Primary button
                if 'btn-primary' in selector or 'primary' in selector and 'button' in selector:
                    components['primary_button'].update(self._parse_style_string(styles_text))
                
                # Secondary button
                if 'btn-secondary' in selector or 'secondary' in selector and 'button' in selector:
                    components['secondary_button'].update(self._parse_style_string(styles_text))
                
                # Card
                if 'card' in selector:
                    components['card'].update(self._parse_style_string(styles_text))
                
                # Headings
                if selector.startswith('h1'):
                    components['heading_h1'].update(self._parse_style_string(styles_text))
                elif selector.startswith('h2'):
                    components['heading_h2'].update(self._parse_style_string(styles_text))
                elif selector.startswith('h3'):
                    components['heading_h3'].update(self._parse_style_string(styles_text))
                
                # Navigation
                if 'nav' in selector:
                    components['navigation'].update(self._parse_style_string(styles_text))
                
                # Footer
                if 'footer' in selector:
                    components['footer'].update(self._parse_style_string(styles_text))
        
        # Extract from computed styles
        if 'styles' in data and 'computed' in data['styles']:
            computed = data['styles']['computed']
            for selector, styles_dict in computed.items():
                selector_lower = selector.lower()
                
                if 'btn-primary' in selector_lower or ('primary' in selector_lower and 'button' in selector_lower):
                    components['primary_button'].update(styles_dict)
                elif 'btn-secondary' in selector_lower or ('secondary' in selector_lower and 'button' in selector_lower):
                    components['secondary_button'].update(styles_dict)
                elif 'card' in selector_lower:
                    components['card'].update(styles_dict)
                elif selector_lower.startswith('h1'):
                    components['heading_h1'].update(styles_dict)
                elif selector_lower.startswith('h2'):
                    components['heading_h2'].update(styles_dict)
                elif selector_lower.startswith('h3'):
                    components['heading_h3'].update(styles_dict)
                elif 'nav' in selector_lower:
                    components['navigation'].update(styles_dict)
                elif 'footer' in selector_lower:
                    components['footer'].update(styles_dict)
        
        # Extract from CSS rules
        if 'styles' in data and 'css_rules' in data['styles']:
            for rule in data['styles'].get('css_rules', []):
                selector = rule.get('selector', '').lower()
                css_text = rule.get('cssText', '')
                
                if 'btn-primary' in selector or '.primary' in selector and 'button' in selector:
                    components['primary_button'].update(self._parse_css_text(css_text))
                elif 'btn-secondary' in selector or '.secondary' in selector and 'button' in selector:
                    components['secondary_button'].update(self._parse_css_text(css_text))
                elif '.card' in selector or 'card' in selector:
                    components['card'].update(self._parse_css_text(css_text))
        
        return components
    
    def _parse_style_string(self, style_string: str) -> dict:
        """Parses inline style string into key-value pairs."""
        styles = {}
        if not style_string:
            return styles
        
        for prop in style_string.split(';'):
            prop = prop.strip()
            if ':' in prop:
                key, value = prop.split(':', 1)
                styles[key.strip()] = value.strip()
        return styles
    
    def _parse_css_text(self, css_text: str) -> dict:
        """Extracts key CSS properties from CSS rule text."""
        styles = {}
        if not css_text:
            return styles
        
        # Extract common properties
        patterns = {
            'background-color': r'background-color:\s*([^;]+)',
            'background': r'background:\s*([^;]+)',
            'color': r'color:\s*([^;]+)',
            'border': r'border:\s*([^;]+)',
            'border-color': r'border-color:\s*([^;]+)',
            'font-size': r'font-size:\s*([^;]+)',
            'font-weight': r'font-weight:\s*([^;]+)',
            'font-family': r'font-family:\s*([^;]+)',
            'display': r'display:\s*([^;]+)',
        }
        
        for prop, pattern in patterns.items():
            match = re.search(pattern, css_text, re.IGNORECASE)
            if match:
                styles[prop] = match.group(1).strip()
        
        return styles
    
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
    
    def generate_summary_report(self, comparison_report: dict) -> str:
        """Generates markdown summary from detailed report."""
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

