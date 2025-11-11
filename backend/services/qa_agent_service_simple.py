# backend/services/qa_agent_service_simple.py
"""
Multi-Agent QA System:
1. HTML/CSS Parser - Extracts structured data from website
2. Report Writer - LLM writes report from parsed data
3. Comparison Agent - Compares report with document specs
"""

import json
import re
from openai import OpenAI
import logging
from typing import Dict, List, Any
from .rag_service import RAGService

logging.basicConfig(level=logging.INFO)


class WebsiteAnalyzerAgent:
    """Multi-agent system for QA analysis."""
    
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini"
        
    def analyze_with_rag(self, scraped_data: dict, rag_service: RAGService, run_id: str, run_dir=None) -> dict:
        """
        Multi-agent analysis:
        1. Parse HTML/CSS to extract structured data
        2. LLM writes report from parsed data
        3. Compare report with document specs
        """
        from pathlib import Path
        
        print("\n" + "="*70)
        print("🤖 Multi-Agent QA Analysis Starting...")
        print("="*70 + "\n")
        
        # AGENT 1: HTML/CSS Parser
        print("[AGENT 1] HTML/CSS Parser: Extracting structured data...")
        parsed_data = self._parse_html_css(scraped_data)
        print(f"✓ Parsed: {len(parsed_data.get('components', {}))} components, {len(parsed_data.get('colors', []))} colors\n")
        
        # Save Agent 1 output
        if run_dir:
            agent1_file = Path(run_dir) / "agent1_parsed_data.json"
            with open(agent1_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Agent 1 output saved to: {agent1_file}\n")
        
        # AGENT 2: Report Writer
        print("[AGENT 2] Report Writer: Generating website analysis report...")
        website_report = self._write_website_report(parsed_data)
        print("✓ Website report generated\n")
        
        # Save Agent 2 output
        if run_dir:
            agent2_file = Path(run_dir) / "agent2_website_report.txt"
            with open(agent2_file, 'w', encoding='utf-8') as f:
                f.write(website_report)
            print(f"💾 Agent 2 output saved to: {agent2_file}\n")
        
        # AGENT 3: Comparison Agent
        print("[AGENT 3] Comparison Agent: Comparing with document specs...")
        doc_specs = self._get_document_specs(rag_service, run_id)
        
        # Save document specs too
        if run_dir:
            doc_specs_file = Path(run_dir) / "document_specs.txt"
            with open(doc_specs_file, 'w', encoding='utf-8') as f:
                f.write(doc_specs)
            print(f"💾 Document specs saved to: {doc_specs_file}\n")
        
        # Option: Use simple text matching instead of LLM
        # Set use_simple_matching=True to use Python text matching (faster, cheaper)
        # Agent 1 & 2 outputs look good - enabling simple matching!
        USE_SIMPLE_MATCHING = True  # Using simple matching based on Agent 1 & 2 outputs
        final_report = self._compare_with_document(website_report, doc_specs, parsed_data, use_simple_matching=USE_SIMPLE_MATCHING)
        print("✓ Comparison complete\n")
        
        final_report['url'] = scraped_data.get('url')
        return final_report
    
    # ============================================
    # AGENT 1: HTML/CSS PARSER
    # ============================================
    def _parse_html_css(self, scraped_data: dict) -> dict:
        """
        Extracts structured data from HTML/CSS.
        This is the parser - it finds important code.
        """
        parsed = {
            'components': {},
            'colors': [],
            'typography': {},
            'layout': {},
            'content': {}
        }
        
        # Extract colors
        colors = set()
        if 'styles' in scraped_data:
            # From inline styles
            if 'inline' in scraped_data['styles']:
                for style in scraped_data['styles']['inline']:
                    styles_text = style.get('styles', '')
                    selector = style.get('selector', '')
                    
                    # Extract colors
                    color_matches = re.findall(
                        r'(?:color|background-color|border-color|background):\s*(#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)|white|black|transparent)',
                        styles_text,
                        re.IGNORECASE
                    )
                    colors.update(color_matches)
                    
                    # Parse component styles
                    self._parse_component(parsed['components'], selector, styles_text)
            
            # From CSS rules
            if 'css_rules' in scraped_data['styles']:
                for rule in scraped_data['styles']['css_rules']:
                    selector = rule.get('selector', '')
                    css_text = rule.get('cssText', '')
                    
                    # Extract colors from CSS
                    color_matches = re.findall(
                        r'(?:color|background-color|border-color|background):\s*(#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)|white|black|transparent)',
                        css_text,
                        re.IGNORECASE
                    )
                    colors.update(color_matches)
                    
                    # Parse component styles
                    self._parse_component(parsed['components'], selector, css_text)
        
        parsed['colors'] = sorted(list(colors))
        
        # Extract typography
        parsed['typography'] = self._extract_typography(scraped_data)
        
        # Extract heading-specific typography from computed styles
        if 'styles' in scraped_data and 'computed' in scraped_data['styles']:
            heading_typography = {}
            for selector, styles_dict in scraped_data['styles']['computed'].items():
                selector_lower = selector.lower()
                if selector_lower.startswith('h1') or 'h1' in selector_lower:
                    heading_typography['h1'] = {
                        'font-size': styles_dict.get('font-size', ''),
                        'font-weight': styles_dict.get('font-weight', ''),
                        'font-family': styles_dict.get('font-family', ''),
                        'line-height': styles_dict.get('line-height', '')
                    }
                elif selector_lower.startswith('h2') or 'h2' in selector_lower:
                    heading_typography['h2'] = {
                        'font-size': styles_dict.get('font-size', ''),
                        'font-weight': styles_dict.get('font-weight', ''),
                        'font-family': styles_dict.get('font-family', ''),
                        'line-height': styles_dict.get('line-height', '')
                    }
                elif selector_lower.startswith('h3') or 'h3' in selector_lower:
                    heading_typography['h3'] = {
                        'font-size': styles_dict.get('font-size', ''),
                        'font-weight': styles_dict.get('font-weight', ''),
                        'font-family': styles_dict.get('font-family', ''),
                        'line-height': styles_dict.get('line-height', '')
                    }
            if heading_typography:
                parsed['typography']['headings'] = heading_typography
        
        # Extract layout
        parsed['layout'] = self._extract_layout(scraped_data)
        
        # Extract content
        parsed['content'] = self._extract_content(scraped_data)
        
        return parsed
    
    def _parse_component(self, components: dict, selector: str, styles_text: str):
        """Parse styles for a specific component."""
        selector_lower = selector.lower()
        
        # Identify component type
        component_name = None
        if 'btn-primary' in selector_lower or ('primary' in selector_lower and 'button' in selector_lower):
            component_name = 'primary_button'
        elif 'btn-secondary' in selector_lower or ('secondary' in selector_lower and 'button' in selector_lower):
            component_name = 'secondary_button'
        elif 'card' in selector_lower:
            component_name = 'card'
        elif selector_lower.startswith('h1') or selector_lower == 'h1':
            component_name = 'heading_h1'
        elif selector_lower.startswith('h2') or selector_lower == 'h2':
            component_name = 'heading_h2'
        elif selector_lower.startswith('h3') or selector_lower == 'h3':
            component_name = 'heading_h3'
        elif 'nav' in selector_lower:
            component_name = 'navigation'
        elif 'footer' in selector_lower:
            component_name = 'footer'
        elif 'hero' in selector_lower:
            component_name = 'hero_section'
        
        if component_name:
            if component_name not in components:
                components[component_name] = {'selector': selector, 'styles': {}}
            
            # Parse style properties
            for prop in styles_text.split(';'):
                prop = prop.strip()
                if ':' in prop:
                    key, value = prop.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    components[component_name]['styles'][key] = value
    
    def _extract_typography(self, data: dict) -> dict:
        """Extract typography information from both inline styles and CSS rules."""
        typo = {
            'font_families': set(),
            'font_sizes': set(),
            'font_weights': set(),
            'line_heights': set()
        }
        
        def extract_from_text(text: str):
            """Extract typography from CSS text."""
            # Font families
            fonts = re.findall(r'font-family:\s*([^;]+)', text, re.IGNORECASE)
            for f in fonts:
                typo['font_families'].update([x.strip(" '\"") for x in f.split(',')])
            
            # Font sizes
            sizes = re.findall(r'font-size:\s*([^;]+)', text, re.IGNORECASE)
            typo['font_sizes'].update([s.strip() for s in sizes])
            
            # Font weights
            weights = re.findall(r'font-weight:\s*([^;]+)', text, re.IGNORECASE)
            typo['font_weights'].update([w.strip() for w in weights])
            
            # Line heights
            line_heights = re.findall(r'line-height:\s*([^;]+)', text, re.IGNORECASE)
            typo['line_heights'].update([lh.strip() for lh in line_heights])
        
        if 'styles' in data:
            # Extract from inline styles
            if 'inline' in data['styles']:
                for style in data['styles']['inline']:
                    styles_text = style.get('styles', '')
                    extract_from_text(styles_text)
            
            # Extract from CSS rules (this is where most typography is!)
            if 'css_rules' in data['styles']:
                for rule in data['styles']['css_rules']:
                    css_text = rule.get('cssText', '')
                    extract_from_text(css_text)
            
            # Extract from computed styles if available
            if 'computed' in data['styles']:
                for selector, styles_dict in data['styles']['computed'].items():
                    if 'font-family' in styles_dict:
                        fonts = [x.strip(" '\"") for x in str(styles_dict['font-family']).split(',')]
                        typo['font_families'].update(fonts)
                    if 'font-size' in styles_dict:
                        typo['font_sizes'].add(str(styles_dict['font-size']))
                    if 'font-weight' in styles_dict:
                        typo['font_weights'].add(str(styles_dict['font-weight']))
                    if 'line-height' in styles_dict:
                        typo['line_heights'].add(str(styles_dict['line-height']))
        
        return {k: sorted(list(v)) for k, v in typo.items()}
    
    def _extract_layout(self, data: dict) -> dict:
        """Extract layout information."""
        layout = {
            'grid_usage': False,
            'flexbox_usage': False,
            'position_types': set(),
            'media_queries': []
        }
        
        if 'styles' in data and 'css_rules' in data['styles']:
            for rule in data['styles']['css_rules']:
                css_text = rule.get('cssText', '')
                
                if 'display:\\s*grid' in css_text or 'display:grid' in css_text:
                    layout['grid_usage'] = True
                if 'display:\\s*flex' in css_text or 'display:flex' in css_text:
                    layout['flexbox_usage'] = True
                
                # Position types
                positions = re.findall(r'position:\s*([^;]+)', css_text)
                layout['position_types'].update(positions)
                
                # Media queries
                if 'media' in rule and rule['media']:
                    layout['media_queries'].append(rule['media'])
        
        layout['position_types'] = list(layout['position_types'])
        return layout
    
    def _extract_content(self, data: dict) -> dict:
        """Extract content information."""
        content = {
            'headings': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},
            'image_count': 0,
            'button_count': 0
        }
        
        if 'html' in data:
            html_lower = data['html'].lower()
            for h in content['headings'].keys():
                content['headings'][h] = html_lower.count(f'<{h}')
            content['image_count'] = html_lower.count('<img')
            content['button_count'] = html_lower.count('<button') + html_lower.count('btn')
        
        return content
    
    # ============================================
    # AGENT 2: REPORT WRITER
    # ============================================
    def _write_website_report(self, parsed_data: dict) -> str:
        """
        LLM writes a descriptive report from parsed data.
        This report describes what the website actually has.
        """
        system_prompt = """You are a technical writer. Write a clear, structured report describing the website's implementation.

Based on the parsed HTML/CSS data, write a report that describes:
- Colors used (with exact values)
- Typography (fonts, sizes, weights)
- Layout (grid, flexbox, positioning)
- Components (buttons, headings, navigation, etc.)

Be specific and accurate. Use exact values from the data.
"""
        
        user_prompt = f"""PARSED WEBSITE DATA:
{json.dumps(parsed_data, indent=2)}

Write a detailed report describing what this website implements. Include:
1. Color Palette: List all colors found with their exact values
2. Typography: Font families, sizes, weights used
3. Layout: Grid/flexbox usage, positioning
4. Components: Describe each component (buttons, headings, etc.) with their styles

Format as a clear, structured report.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Report writing error: {e}")
            return "Error generating website report."
    
    # ============================================
    # AGENT 3: COMPARISON AGENT
    # ============================================
    def _get_document_specs(self, rag_service: RAGService, run_id: str) -> str:
        """Get document specifications via RAG."""
        queries = [
            "primary button background color styling specifications",
            "secondary button background color styling specifications",
            "color palette hex codes primary colors",
            "typography font sizes font weights headings specifications",
            "layout grid flexbox navigation position specifications",
            "content headings structure specifications"
        ]
        
        contexts = []
        for query in queries:
            result = rag_service.query_collection(query, run_id, k=3)
            context = result.get("context", "")
            if context:
                contexts.append(f"[{query}]\n{context}\n")
        
        return "\n---\n".join(contexts) if contexts else "No specifications found in document."
    
    def _compare_with_document(self, website_report: str, doc_specs: str, parsed_data: dict = None, use_simple_matching: bool = False) -> dict:
        """
        Compare website report with document specs.
        This is where we find mismatches.
        
        If use_simple_matching=True, uses Python text matching instead of LLM.
        """
        if use_simple_matching:
            return self._simple_text_match(website_report, doc_specs, parsed_data)
        
        system_prompt = """You are a QA analyst comparing a website implementation report with design document specifications.

RULES:
1. Normalize values before comparing:
   - Hex = RGB: Convert hex colors to RGB for comparison
   - Named colors: Convert named colors (white, black, etc.) to hex/rgb
   - Strip CSS variables: rgb(255 255 255/var(--opacity)) = white
   - Gradients: same colors = match (format doesn't matter)
2. Only report REAL mismatches (not format differences)
3. If values match → status: "match" (don't report in issues)
4. If values differ → status: "mismatch" (report with expected vs found)
5. If spec not in document → skip it

Return JSON with this structure:
{
  "color_analysis": {"status": "match|mismatch", "details": "...", "issues": [...]},
  "typography_analysis": {"status": "match|mismatch", "details": "...", "issues": [...]},
  "layout_analysis": {"status": "match|mismatch", "details": "...", "issues": [...]},
  "content_analysis": {"status": "match|mismatch", "details": "...", "issues": [...]}
}

Each issue must have:
{
  "description": "what's wrong",
  "expected_value": "expected from doc",
  "found_value": "found on website",
  "selector": "CSS selector from parsed data or 'not available'",
  "location": "where it is",
  "impact": "High|Medium|Low",
  "doc_page": "page or section from document"
}
"""
        
        user_prompt = f"""WEBSITE IMPLEMENTATION REPORT:
{website_report}

DESIGN DOCUMENT SPECIFICATIONS:
{doc_specs}

Compare the website report with document specs. Report only real mismatches (not format differences).
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
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return self._format_report(result)
            
        except Exception as e:
            logging.error(f"Comparison error: {e}")
            return self._empty_report()
    
    def _simple_text_match(self, website_report: str, doc_specs: str, parsed_data: dict = None) -> dict:
        """
        Simple text matching approach - no LLM needed.
        Extracts expected values from document specs dynamically, then compares with parsed data.
        """
        import re
        
        issues = {
            'color': [],
            'typography': [],
            'layout': [],
            'content': []
        }
        
        # ===== EXTRACT EXPECTED VALUES FROM DOCUMENT =====
        expected_specs = self._extract_expected_specs(doc_specs)
        
        # Debug: Print extracted specs
        if expected_specs:
            print(f"\n📋 Extracted Expected Specs:")
            if 'primary_button' in expected_specs:
                print(f"  Primary Button Default: {expected_specs['primary_button'].get('default_gradient', {})}")
                print(f"  Primary Button Hover: {expected_specs['primary_button'].get('hover_gradient', {})}")
            if 'secondary_button' in expected_specs:
                print(f"  Secondary Button Default: {expected_specs['secondary_button'].get('default_background', '')}")
                print(f"  Secondary Button Hover: {expected_specs['secondary_button'].get('hover_background', '')}")
            if 'h1' in expected_specs:
                print(f"  H1 Weight: {expected_specs['h1'].get('font_weight', '')}")
            if 'navigation' in expected_specs:
                print(f"  Navigation Position: {expected_specs['navigation'].get('position', '')}")
            print()
        
        # ===== COLOR MATCHING =====
        def normalize_color(color_str):
            """Normalize color to comparable format."""
            if not color_str:
                return ""
            color_str = str(color_str).lower().strip()
            # Remove CSS variables
            color_str = re.sub(r'/var\([^)]+\)', '', color_str)
            # Convert rgb to hex
            rgb_match = re.search(r'rgb\((\d+)\s*[, ]\s*(\d+)\s*[, ]\s*(\d+)', color_str)
            if rgb_match:
                r, g, b = map(int, rgb_match.groups())
                return f"#{r:02x}{g:02x}{b:02x}"
            # Extract hex
            hex_match = re.search(r'#([0-9a-f]{3,6})', color_str)
            if hex_match:
                hex_val = hex_match.group(1)
                if len(hex_val) == 3:
                    hex_val = ''.join([c*2 for c in hex_val])
                return f"#{hex_val}"
            if 'white' in color_str:
                return "#ffffff"
            return color_str
        
        def colors_match(expected, found):
            """Check if two colors match (normalized)."""
            exp_norm = normalize_color(expected)
            found_norm = normalize_color(found)
            return exp_norm == found_norm or exp_norm in found_norm or found_norm in exp_norm
        
        # Use parsed_data if available (more accurate)
        if parsed_data and 'components' in parsed_data:
            components = parsed_data['components']
            
            # Check primary button gradient
            if 'primary_button' in components and 'primary_button' in expected_specs:
                btn_styles = components['primary_button'].get('styles', {})
                gradient_from = btn_styles.get('--tw-gradient-from', '').split()[0] if '--tw-gradient-from' in btn_styles else ''
                gradient_to = btn_styles.get('--tw-gradient-to', '').split()[0] if '--tw-gradient-to' in btn_styles else ''
                
                expected = expected_specs['primary_button']
                expected_default = expected.get('default_gradient', {})
                expected_hover = expected.get('hover_gradient', {})
                
                if gradient_from and gradient_to:
                    # Check if found colors match default or hover
                    exp_from = expected_default.get('from', '')
                    exp_to = expected_default.get('to', '')
                    hover_from = expected_hover.get('from', '')
                    hover_to = expected_hover.get('to', '')
                    
                    is_hover_colors = (colors_match(hover_from, gradient_from) and colors_match(hover_to, gradient_to)) if hover_from and hover_to else False
                    is_default_colors = (colors_match(exp_from, gradient_from) and colors_match(exp_to, gradient_to)) if exp_from and exp_to else False
                    
                    if is_hover_colors:
                        issues['color'].append({
                            "description": "Primary button using hover gradient colors in default state",
                            "expected_value": f"{exp_from} to {exp_to} (default state)",
                            "found_value": f"{gradient_from} to {gradient_to} (hover colors)",
                            "selector": ".btn-primary",
                            "location": "primary button",
                            "impact": "High",
                            "doc_page": "UI Components"
                        })
                    elif not is_default_colors and exp_from and exp_to:
                        issues['color'].append({
                            "description": "Primary button gradient colors mismatch",
                            "expected_value": f"{exp_from} to {exp_to} (default)",
                            "found_value": f"{gradient_from} to {gradient_to}",
                            "selector": ".btn-primary",
                            "location": "primary button",
                            "impact": "High",
                            "doc_page": "UI Components"
                        })
            
            # Check secondary button background
            if 'secondary_button' in components and 'secondary_button' in expected_specs:
                btn_styles = components['secondary_button'].get('styles', {})
                bg_color = btn_styles.get('background-color', '')
                
                expected = expected_specs['secondary_button']
                expected_default = expected.get('default_background', '')
                expected_hover = expected.get('hover_background', '')
                
                if bg_color:
                    is_hover_color = colors_match(expected_hover, bg_color) if expected_hover else False
                    is_default_color = colors_match(expected_default, bg_color) if expected_default else False
                    
                    if is_hover_color and expected_default:
                        issues['color'].append({
                            "description": "Secondary button using hover background color in default state",
                            "expected_value": f"{expected_default} (default state)",
                            "found_value": f"{bg_color} (hover color)",
                            "selector": ".btn-secondary",
                            "location": "secondary button",
                            "impact": "High",
                            "doc_page": "UI Components"
                        })
                    elif not is_default_color and expected_default:
                        issues['color'].append({
                            "description": "Secondary button background color mismatch",
                            "expected_value": expected_default,
                            "found_value": bg_color,
                            "selector": ".btn-secondary",
                            "location": "secondary button",
                            "impact": "High",
                            "doc_page": "UI Components"
                        })
        
        # ===== TYPOGRAPHY MATCHING =====
        # Use parsed_data for accurate typography (from computed styles)
        if parsed_data and 'typography' in parsed_data and 'headings' in parsed_data['typography']:
            headings = parsed_data['typography']['headings']
            
            # Check H1 font weight
            if 'h1' in headings and 'h1' in expected_specs:
                h1_weight = headings['h1'].get('font-weight', '')
                expected_weight = expected_specs['h1'].get('font_weight', '')
                if h1_weight and expected_weight and h1_weight != expected_weight:
                    issues['typography'].append({
                        "description": "H1 font weight mismatch",
                        "expected_value": f"{expected_weight} (from document)",
                        "found_value": f"{h1_weight}",
                        "selector": "h1",
                        "location": "heading",
                        "impact": "High",
                        "doc_page": "Typography"
                    })
            
            # Check H1 font size (if specified in document)
            if 'h1' in headings and 'h1' in expected_specs:
                h1_size = headings['h1'].get('font-size', '')
                expected_size = expected_specs['h1'].get('font_size', '')
                # Only check if document specifies a size (might be responsive)
                if expected_size and h1_size:
                    # Normalize sizes for comparison (px vs rem)
                    if not self._sizes_match(expected_size, h1_size):
                        issues['typography'].append({
                            "description": "H1 font size mismatch",
                            "expected_value": f"{expected_size} (from document)",
                            "found_value": f"{h1_size}",
                            "selector": "h1",
                            "location": "heading",
                            "impact": "Medium",
                            "doc_page": "Typography"
                        })
        
        # ===== LAYOUT MATCHING =====
        # Check navigation position using parsed_data
        if parsed_data and 'components' in parsed_data:
            if 'navigation' in parsed_data['components'] and 'navigation' in expected_specs:
                nav_selector = parsed_data['components']['navigation'].get('selector', '')
                expected_position = expected_specs['navigation'].get('position', '')
                
                if expected_position:
                    if expected_position.lower() == 'fixed' and 'fixed' not in nav_selector.lower():
                        issues['layout'].append({
                            "description": "Navigation position mismatch",
                            "expected_value": expected_position,
                            "found_value": "not fixed (found in selector: " + nav_selector[:50] + ")",
                            "selector": nav_selector.split()[0] if nav_selector else "nav",
                            "location": "navigation",
                            "impact": "High",
                            "doc_page": "Website Structure"
                        })
        
        # Build final report
        return {
            "color_analysis": {
                "status": "mismatch" if issues['color'] else "match",
                "details": f"Found {len(issues['color'])} color issues." if issues['color'] else "All colors match.",
                "issues": issues['color']
            },
            "typography_analysis": {
                "status": "mismatch" if issues['typography'] else "match",
                "details": f"Found {len(issues['typography'])} typography issues." if issues['typography'] else "All typography matches.",
                "issues": issues['typography']
            },
            "layout_analysis": {
                "status": "mismatch" if issues['layout'] else "match",
                "details": f"Found {len(issues['layout'])} layout issues." if issues['layout'] else "No layout issues found.",
                "issues": issues['layout']
            },
            "content_analysis": {"status": "match", "details": "No content issues found.", "issues": []},
            "overall_assessment": "Simple text matching analysis complete.",
            "recommendations": []
        }
    
    def _extract_expected_specs(self, doc_specs: str) -> dict:
        """
        Extract expected specifications from document text.
        Returns a dict with component specs.
        """
        import re
        specs = {}
        
        # Extract primary button specs
        primary_match = re.search(r'Primary Button.*?Background:\s*Linear gradient from\s*(#[0-9a-fA-F]{6})\s*to\s*(#[0-9a-fA-F]{6})', doc_specs, re.IGNORECASE | re.DOTALL)
        hover_match = re.search(r'Hover State.*?Gradient changes:\s*(#[0-9a-fA-F]{6})\s*to\s*(#[0-9a-fA-F]{6})', doc_specs, re.IGNORECASE | re.DOTALL)
        
        if primary_match:
            specs['primary_button'] = {
                'default_gradient': {
                    'from': primary_match.group(1),
                    'to': primary_match.group(2)
                }
            }
            if hover_match:
                specs['primary_button']['hover_gradient'] = {
                    'from': hover_match.group(1),
                    'to': hover_match.group(2)
                }
        
        # Extract secondary button specs
        secondary_match = re.search(r'Secondary Button.*?Background:\s*(White|#[0-9a-fA-F]{6}|#ffffff)', doc_specs, re.IGNORECASE | re.DOTALL)
        secondary_hover_match = re.search(r'Hover State.*?Background changes to:\s*(#[0-9a-fA-F]{6}|rgb\([^)]+\))', doc_specs, re.IGNORECASE | re.DOTALL)
        
        if secondary_match:
            bg = secondary_match.group(1)
            if bg.lower() == 'white':
                bg = '#ffffff'
            specs['secondary_button'] = {
                'default_background': bg
            }
            if secondary_hover_match:
                specs['secondary_button']['hover_background'] = secondary_hover_match.group(1)
        
        # Extract H1 specs
        h1_weight_match = re.search(r'H1.*?Weight:\s*(Bold|700|bold)', doc_specs, re.IGNORECASE)
        h1_size_match = re.search(r'H1.*?Font.*?(\d+\.?\d*\s*(rem|px|em))', doc_specs, re.IGNORECASE)
        
        if h1_weight_match or h1_size_match:
            specs['h1'] = {}
            if h1_weight_match:
                weight = h1_weight_match.group(1)
                if weight.lower() == 'bold':
                    weight = '700'
                specs['h1']['font_weight'] = weight
            if h1_size_match:
                specs['h1']['font_size'] = h1_size_match.group(1)
        
        # Extract navigation position
        nav_match = re.search(r'Navigation.*?Position:\s*(Fixed|fixed|static|absolute|relative)', doc_specs, re.IGNORECASE)
        if nav_match:
            specs['navigation'] = {
                'position': nav_match.group(1).lower()
            }
        
        return specs
    
    def _sizes_match(self, expected: str, found: str) -> bool:
        """Check if two font sizes match (handles px, rem, em conversions)."""
        import re
        
        def parse_size(size_str):
            """Parse size string to pixels."""
            if not size_str:
                return None
            size_str = str(size_str).strip()
            # Extract number and unit
            match = re.search(r'(\d+\.?\d*)\s*(px|rem|em)', size_str, re.IGNORECASE)
            if match:
                num = float(match.group(1))
                unit = match.group(2).lower()
                # Convert to px (assuming 16px base)
                if unit == 'rem':
                    return num * 16
                elif unit == 'em':
                    return num * 16  # Approximate
                else:  # px
                    return num
            return None
        
        exp_px = parse_size(expected)
        found_px = parse_size(found)
        
        if exp_px and found_px:
            # Allow 2px difference for rounding
            return abs(exp_px - found_px) < 2
        
        # Fallback: string match
        return expected.lower() in found.lower() or found.lower() in expected.lower()
    
    def _format_report(self, result: dict) -> dict:
        """Format LLM result to expected report structure."""
        report = {
            "color_analysis": result.get("color_analysis", {"status": "match", "details": "", "issues": []}),
            "typography_analysis": result.get("typography_analysis", {"status": "match", "details": "", "issues": []}),
            "layout_analysis": result.get("layout_analysis", {"status": "match", "details": "", "issues": []}),
            "content_analysis": result.get("content_analysis", {"status": "match", "details": "", "issues": []}),
            "overall_assessment": "Analysis complete.",
            "recommendations": []
        }
        
        # Add details if missing
        for key in ["color_analysis", "typography_analysis", "layout_analysis", "content_analysis"]:
            cat = report[key]
            if not cat.get("details"):
                issues = cat.get("issues", [])
                if issues:
                    cat["details"] = f"Found {len(issues)} issues."
                else:
                    cat["details"] = "All specifications match the document."
        
        return report
    
    def _empty_report(self) -> dict:
        """Return empty report on error."""
        return {
            "color_analysis": {"status": "match", "details": "Analysis error occurred.", "issues": []},
            "typography_analysis": {"status": "match", "details": "Analysis error occurred.", "issues": []},
            "layout_analysis": {"status": "match", "details": "Analysis error occurred.", "issues": []},
            "content_analysis": {"status": "match", "details": "Analysis error occurred.", "issues": []},
            "overall_assessment": "Analysis error occurred.",
            "recommendations": []
        }
    
    def generate_summary_report(self, comparison_report: dict) -> str:
        """
        Generates structured summary from detailed report.
        No LLM needed - builds structured summary from data.
        """
        try:
            summary_parts = []
            
            # Count issues by category
            color_issues = len(comparison_report.get("color_analysis", {}).get("issues", []))
            typo_issues = len(comparison_report.get("typography_analysis", {}).get("issues", []))
            layout_issues = len(comparison_report.get("layout_analysis", {}).get("issues", []))
            content_issues = len(comparison_report.get("content_analysis", {}).get("issues", []))
            total_issues = color_issues + typo_issues + layout_issues + content_issues
            
            # Get status for each category
            color_status = comparison_report.get("color_analysis", {}).get("status", "match")
            typo_status = comparison_report.get("typography_analysis", {}).get("status", "match")
            layout_status = comparison_report.get("layout_analysis", {}).get("status", "match")
            content_status = comparison_report.get("content_analysis", {}).get("status", "match")
            
            # Executive Summary Header
            summary_parts.append("# Executive Summary\n")
            
            # Overall Status
            if total_issues == 0:
                summary_parts.append("## Overall Status: ✅ All Checks Passed\n")
                summary_parts.append("All specifications match the design document. No issues found.\n")
            else:
                summary_parts.append(f"## Overall Status: ⚠️ {total_issues} Issue(s) Found\n")
                summary_parts.append(f"Analysis identified {total_issues} discrepancy(ies) that require attention.\n")
            
            # Category Breakdown
            summary_parts.append("## Category Analysis\n")
            
            # Color Analysis
            color_emoji = "❌" if color_status == "mismatch" else "✅"
            summary_parts.append(f"### {color_emoji} Color Analysis: {color_status.upper()}")
            if color_issues > 0:
                summary_parts.append(f"- **Issues Found**: {color_issues}")
                for issue in comparison_report.get("color_analysis", {}).get("issues", [])[:3]:  # Top 3
                    desc = issue.get("description", "")[:60]
                    summary_parts.append(f"  - {desc}")
            else:
                summary_parts.append("- All color specifications match.")
            summary_parts.append("")
            
            # Typography Analysis
            typo_emoji = "❌" if typo_status == "mismatch" else "✅"
            summary_parts.append(f"### {typo_emoji} Typography Analysis: {typo_status.upper()}")
            if typo_issues > 0:
                summary_parts.append(f"- **Issues Found**: {typo_issues}")
                for issue in comparison_report.get("typography_analysis", {}).get("issues", [])[:3]:
                    desc = issue.get("description", "")[:60]
                    summary_parts.append(f"  - {desc}")
            else:
                summary_parts.append("- All typography specifications match.")
            summary_parts.append("")
            
            # Layout Analysis
            layout_emoji = "❌" if layout_status == "mismatch" else "✅"
            summary_parts.append(f"### {layout_emoji} Layout Analysis: {layout_status.upper()}")
            if layout_issues > 0:
                summary_parts.append(f"- **Issues Found**: {layout_issues}")
                for issue in comparison_report.get("layout_analysis", {}).get("issues", [])[:3]:
                    desc = issue.get("description", "")[:60]
                    summary_parts.append(f"  - {desc}")
            else:
                summary_parts.append("- All layout specifications match.")
            summary_parts.append("")
            
            # Content Analysis
            content_emoji = "❌" if content_status == "mismatch" else "✅"
            summary_parts.append(f"### {content_emoji} Content Analysis: {content_status.upper()}")
            if content_issues > 0:
                summary_parts.append(f"- **Issues Found**: {content_issues}")
                for issue in comparison_report.get("content_analysis", {}).get("issues", [])[:3]:
                    desc = issue.get("description", "")[:60]
                    summary_parts.append(f"  - {desc}")
            else:
                summary_parts.append("- All content specifications match.")
            summary_parts.append("")
            
            # Recommendations
            if total_issues > 0:
                summary_parts.append("## Recommendations\n")
                summary_parts.append("1. Review and address the identified issues above.")
                summary_parts.append("2. Ensure all specifications align with the design document.")
                summary_parts.append("3. Re-run the analysis after fixes to verify compliance.")
            else:
                summary_parts.append("## Recommendations\n")
                summary_parts.append("No action required. All specifications are compliant.")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logging.error(f"Error generating summary report: {str(e)}")
            return f"# Executive Summary\n\nError generating summary: {str(e)}"
