"""
Website Branding & Design Analyzer Agent
Powered by Groq API

Analyzes scraped HTML/CSS data to extract:
- Brand identity and messaging
- Color palette with hex codes
- Typography and font families
- Content structure and tone
- Design patterns and UI elements
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from groq import Groq
import cssutils
from collections import Counter
import logging

# Suppress cssutils warnings
cssutils.log.setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.INFO)


class WebsiteAnalyzerAgent:
    def __init__(self, groq_api_key: str):
        """Initialize the analyzer with Groq API key"""
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.1-8b-instant"  # Best model for analysis
        
    def analyze_scraped_data(self, scraped_dir: str) -> Dict:
        """
        Main analysis method that processes scraped website data
        
        Args:
            scraped_dir: Path to the directory containing scraped files
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        print("\n" + "="*70)
        print("🤖 AI-Powered Website Analysis Starting...")
        print("="*70 + "\n")
        
        scraped_path = Path(scraped_dir)
        
        if not scraped_path.exists():
            raise ValueError(f"Directory not found: {scraped_dir}")
        
        # Load all scraped data
        print("📂 Loading scraped data...")
        data = self._load_scraped_files(scraped_path)
        
        # Extract colors
        print("🎨 Extracting color palette...")
        colors = self._extract_colors(data)
        
        # Extract fonts
        print("✍️  Extracting typography...")
        fonts = self._extract_fonts(data)
        
        # Analyze with AI
        print("🧠 Analyzing with AI (Groq)...")
        analysis = self._analyze_with_ai(data, colors, fonts)
        
        # Generate final report
        print("📊 Generating comprehensive report...")
        report = self._generate_report(analysis, colors, fonts, data)
        
        # Save report
        report_path = scraped_path / f"ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Analysis complete! Report saved: {report_path}")
        
        # Print summary
        self._print_summary(report)
        
        return report
    
    def _load_scraped_files(self, scraped_path: Path) -> Dict:
        """Load all scraped files from the directory"""
        data = {
            'html': '',
            'inline_styles': [],
            'external_css': [],
            'style_tags': [],
            'computed_styles': {},
            'metadata': {},
            'image_manifest': {}
        }
        
        # Find the most recent files
        files = list(scraped_path.glob('*'))
        
        # Load HTML
        html_files = list(scraped_path.glob('page_*.html'))
        if html_files:
            latest_html = max(html_files, key=lambda x: x.stat().st_mtime)
            with open(latest_html, 'r', encoding='utf-8') as f:
                data['html'] = f.read()
            print(f"  ✓ Loaded HTML: {len(data['html'])} chars")
        
        # Load inline styles
        inline_files = list(scraped_path.glob('inline_styles_*.json'))
        if inline_files:
            latest_inline = max(inline_files, key=lambda x: x.stat().st_mtime)
            with open(latest_inline, 'r', encoding='utf-8') as f:
                data['inline_styles'] = json.load(f)
            print(f"  ✓ Loaded inline styles: {len(data['inline_styles'])} elements")
        
        # Load external CSS
        css_files = list(scraped_path.glob('css_*.css'))
        for css_file in css_files:
            with open(css_file, 'r', encoding='utf-8') as f:
                data['external_css'].append(f.read())
        if css_files:
            print(f"  ✓ Loaded external CSS: {len(css_files)} files")
        
        # Load style tags
        style_files = list(scraped_path.glob('style_tags_*.css'))
        if style_files:
            latest_style = max(style_files, key=lambda x: x.stat().st_mtime)
            with open(latest_style, 'r', encoding='utf-8') as f:
                data['style_tags'] = [f.read()]
            print(f"  ✓ Loaded style tags")
        
        # Load computed styles
        computed_files = list(scraped_path.glob('computed_styles_*.json'))
        if computed_files:
            latest_computed = max(computed_files, key=lambda x: x.stat().st_mtime)
            with open(latest_computed, 'r', encoding='utf-8') as f:
                data['computed_styles'] = json.load(f)
            print(f"  ✓ Loaded computed styles")
        
        # Load metadata
        metadata_files = list(scraped_path.glob('metadata_*.json'))
        if metadata_files:
            latest_metadata = max(metadata_files, key=lambda x: x.stat().st_mtime)
            with open(latest_metadata, 'r', encoding='utf-8') as f:
                data['metadata'] = json.load(f)
            print(f"  ✓ Loaded metadata")
        
        # Load image manifest
        manifest_files = list(scraped_path.glob('images/image_manifest_*.json'))
        if manifest_files:
            latest_manifest = max(manifest_files, key=lambda x: x.stat().st_mtime)
            with open(latest_manifest, 'r', encoding='utf-8') as f:
                data['image_manifest'] = json.load(f)
            print(f"  ✓ Loaded image manifest: {len(data['image_manifest'])} images")
        
        return data
    
    def _extract_colors(self, data: Dict) -> Dict:
        """Extract all colors from CSS and HTML"""
        colors = {
            'hex': [],
            'rgb': [],
            'rgba': [],
            'named': []
        }
        
        # Regex patterns
        hex_pattern = r'#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b'
        rgb_pattern = r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)'
        rgba_pattern = r'rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)'
        
        # Collect all CSS text
        all_css = ' '.join(data['external_css'] + data['style_tags'])
        
        # Add inline styles
        for style in data['inline_styles']:
            all_css += ' ' + style.get('style', '')
        
        # Add computed styles
        for selector, styles in data['computed_styles'].items():
            for prop, value in styles.items():
                all_css += ' ' + str(value)
        
        # Extract colors
        colors['hex'] = list(set(re.findall(hex_pattern, all_css)))
        colors['rgb'] = list(set(re.findall(rgb_pattern, all_css)))
        colors['rgba'] = list(set(re.findall(rgba_pattern, all_css)))
        
        # Get most common colors
        all_colors = colors['hex'] + colors['rgb'] + colors['rgba']
        color_counter = Counter(all_colors)
        
        return {
            'all_colors': colors,
            'most_common': color_counter.most_common(10),
            'total_unique': len(set(all_colors))
        }
    
    def _extract_fonts(self, data: Dict) -> Dict:
        """Extract font families and typography info"""
        fonts = {
            'families': [],
            'sizes': [],
            'weights': []
        }
        
        # From computed styles
        for selector, styles in data['computed_styles'].items():
            if 'fontFamily' in styles:
                fonts['families'].append(styles['fontFamily'])
            if 'fontSize' in styles:
                fonts['sizes'].append(styles['fontSize'])
            if 'fontWeight' in styles:
                fonts['weights'].append(styles['fontWeight'])
        
        # From metadata (Google Fonts, etc.)
        if 'fonts' in data['metadata']:
            for font_url in data['metadata']['fonts']:
                fonts['families'].append(font_url)
        
        # Count occurrences
        family_counter = Counter(fonts['families'])
        size_counter = Counter(fonts['sizes'])
        weight_counter = Counter(fonts['weights'])
        
        return {
            'primary_fonts': family_counter.most_common(5),
            'font_sizes': size_counter.most_common(10),
            'font_weights': weight_counter.most_common(5),
            'total_unique_fonts': len(set(fonts['families']))
        }
    
    def _analyze_with_ai(self, data: Dict, colors: Dict, fonts: Dict) -> Dict:
        """Use Groq AI to analyze the website content and design"""
        
        # Prepare a focused HTML snippet (first 8000 chars for text content)
        html_snippet = data['html'][:8000]
        
        # Remove scripts and styles from HTML for cleaner analysis
        html_text = re.sub(r'<script[^>]*>.*?</script>', '', html_snippet, flags=re.DOTALL)
        html_text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL)
        html_text = re.sub(r'<[^>]+>', ' ', html_text)
        html_text = re.sub(r'\s+', ' ', html_text).strip()[:4000]
        
        # Create analysis prompt
        prompt = f"""
You are an expert web design and branding analyst. Analyze this website data and provide a comprehensive report.

**WEBSITE METADATA:**
Title: {data['metadata'].get('title', 'N/A')}
Description: {data['metadata'].get('description', 'N/A')}
OG Title: {data['metadata'].get('ogTitle', 'N/A')}

**COLOR PALETTE (Top 10 colors found):**
{', '.join([str(c[0]) for c in colors['most_common']])}

**TYPOGRAPHY:**
Primary Fonts: {', '.join([str(f[0]) for f in fonts['primary_fonts']])}

**WEBSITE TEXT CONTENT (Sample):**
{html_text}

**COMPUTED STYLES:**
{json.dumps(data['computed_styles'], indent=2)[:1500]}

---

Please provide a detailed analysis in the following JSON format:

{{
  "brand_identity": {{
    "brand_name": "extracted brand name",
    "brand_description": "what the brand does",
    "tone_of_voice": "professional/casual/modern/etc",
    "target_audience": "who this is for",
    "key_messages": ["main message 1", "main message 2"]
  }},
  "color_analysis": {{
    "primary_color": "#hexcode",
    "secondary_colors": ["#hex1", "#hex2"],
    "color_scheme_type": "monochromatic/complementary/analogous/etc",
    "mood": "calm/energetic/professional/etc",
    "insights": "detailed color psychology insights"
  }},
  "typography_analysis": {{
    "primary_font": "font name",
    "font_pairing": "description of how fonts work together",
    "readability": "excellent/good/needs improvement",
    "style": "modern/classic/elegant/etc",
    "insights": "typography insights"
  }},
  "content_analysis": {{
    "main_headline": "the main headline",
    "content_type": "landing page/portfolio/ecommerce/etc",
    "key_sections": ["section 1", "section 2"],
    "call_to_actions": ["CTA 1", "CTA 2"],
    "content_quality": "compelling/average/needs work",
    "insights": "content strategy insights"
  }},
  "design_patterns": {{
    "layout_style": "grid/single-column/multi-column/etc",
    "design_system": "modern/minimalist/maximalist/etc",
    "ui_components": ["buttons", "cards", "etc"],
    "responsive_indicators": "mobile-first/desktop-first/hybrid",
    "notable_features": ["feature 1", "feature 2"]
  }},
  "overall_assessment": {{
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "brand_consistency_score": 8.5,
    "design_quality_score": 9.0,
    "content_effectiveness_score": 7.5
  }}
}}

Respond ONLY with valid JSON. No markdown, no explanations, just the JSON object.
"""

        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert web design and branding analyst. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parse response
            ai_response = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            ai_response = re.sub(r'```json\s*', '', ai_response)
            ai_response = re.sub(r'```\s*', '', ai_response)
            
            analysis = json.loads(ai_response)
            
            print("  ✓ AI analysis completed")
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"  ⚠️  Warning: Could not parse AI response as JSON: {e}")
            print(f"  Raw response: {ai_response[:200]}...")
            return self._get_fallback_analysis()
        except Exception as e:
            print(f"  ⚠️  Warning: AI analysis failed: {e}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self) -> Dict:
        """Return a basic structure if AI analysis fails"""
        return {
            "brand_identity": {
                "brand_name": "Unknown",
                "brand_description": "Analysis incomplete",
                "tone_of_voice": "Unknown",
                "target_audience": "Unknown",
                "key_messages": []
            },
            "color_analysis": {
                "primary_color": "Unknown",
                "secondary_colors": [],
                "color_scheme_type": "Unknown",
                "mood": "Unknown",
                "insights": "AI analysis was unsuccessful"
            },
            "typography_analysis": {
                "primary_font": "Unknown",
                "font_pairing": "Unknown",
                "readability": "Unknown",
                "style": "Unknown",
                "insights": "AI analysis was unsuccessful"
            },
            "content_analysis": {
                "main_headline": "Unknown",
                "content_type": "Unknown",
                "key_sections": [],
                "call_to_actions": [],
                "content_quality": "Unknown",
                "insights": "AI analysis was unsuccessful"
            },
            "design_patterns": {
                "layout_style": "Unknown",
                "design_system": "Unknown",
                "ui_components": [],
                "responsive_indicators": "Unknown",
                "notable_features": []
            },
            "overall_assessment": {
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "brand_consistency_score": 0,
                "design_quality_score": 0,
                "content_effectiveness_score": 0
            }
        }
    
    def _generate_report(self, analysis: Dict, colors: Dict, fonts: Dict, data: Dict) -> Dict:
        """Generate comprehensive final report"""
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "website_url": "See scraped metadata",
            "metadata": data['metadata'],
            "ai_analysis": analysis,
            "technical_details": {
                "colors": {
                    "total_unique_colors": colors['total_unique'],
                    "top_10_colors": [c[0] for c in colors['most_common']],
                    "color_usage_frequency": colors['most_common']
                },
                "typography": {
                    "total_unique_fonts": fonts['total_unique_fonts'],
                    "primary_fonts": [f[0] for f in fonts['primary_fonts']],
                    "font_sizes_used": [s[0] for s in fonts['font_sizes']],
                    "font_weights_used": [w[0] for w in fonts['font_weights']]
                },
                "images": {
                    "total_images": len(data['image_manifest']),
                    "image_types": self._categorize_images(data['image_manifest'])
                },
                "html_stats": {
                    "total_html_size": len(data['html']),
                    "inline_styled_elements": len(data['inline_styles']),
                    "external_css_files": len(data['external_css'])
                }
            }
        }
    
    def _categorize_images(self, image_manifest: Dict) -> Dict:
        """Categorize images by type"""
        categories = {
            'favicon': 0,
            'logo': 0,
            'og-image': 0,
            'apple-icon': 0,
            'other': 0
        }
        
        for img_url, img_data in image_manifest.items():
            img_type = img_data.get('type', 'other')
            if img_type in categories:
                categories[img_type] += 1
            else:
                categories['other'] += 1
        
        return categories
    
    def _print_summary(self, report: Dict):
        """Print a beautiful summary of the analysis"""
        print("\n" + "="*70)
        print("📊 WEBSITE ANALYSIS SUMMARY")
        print("="*70)
        
        ai = report['ai_analysis']
        tech = report['technical_details']
        
        # Brand Identity
        print("\n🎯 BRAND IDENTITY")
        print("-" * 70)
        brand = ai['brand_identity']
        print(f"  Brand Name: {brand.get('brand_name', 'N/A')}")
        print(f"  Description: {brand.get('brand_description', 'N/A')}")
        print(f"  Tone: {brand.get('tone_of_voice', 'N/A')}")
        print(f"  Target Audience: {brand.get('target_audience', 'N/A')}")
        
        # Color Analysis
        print("\n🎨 COLOR PALETTE")
        print("-" * 70)
        color = ai['color_analysis']
        print(f"  Primary Color: {color.get('primary_color', 'N/A')}")
        print(f"  Secondary Colors: {', '.join(color.get('secondary_colors', []))}")
        print(f"  Scheme Type: {color.get('color_scheme_type', 'N/A')}")
        print(f"  Mood: {color.get('mood', 'N/A')}")
        print(f"  Total Unique Colors: {tech['colors']['total_unique_colors']}")
        
        # Typography
        print("\n✍️  TYPOGRAPHY")
        print("-" * 70)
        typo = ai['typography_analysis']
        print(f"  Primary Font: {typo.get('primary_font', 'N/A')}")
        print(f"  Style: {typo.get('style', 'N/A')}")
        print(f"  Readability: {typo.get('readability', 'N/A')}")
        print(f"  Total Unique Fonts: {tech['typography']['total_unique_fonts']}")
        
        # Content
        print("\n📝 CONTENT ANALYSIS")
        print("-" * 70)
        content = ai['content_analysis']
        print(f"  Main Headline: {content.get('main_headline', 'N/A')}")
        print(f"  Content Type: {content.get('content_type', 'N/A')}")
        print(f"  Quality: {content.get('content_quality', 'N/A')}")
        
        # Design Patterns
        print("\n🎨 DESIGN PATTERNS")
        print("-" * 70)
        design = ai['design_patterns']
        print(f"  Layout: {design.get('layout_style', 'N/A')}")
        print(f"  Design System: {design.get('design_system', 'N/A')}")
        print(f"  Responsive: {design.get('responsive_indicators', 'N/A')}")
        
        # Overall Assessment
        print("\n⭐ OVERALL SCORES")
        print("-" * 70)
        assessment = ai['overall_assessment']
        print(f"  Brand Consistency: {assessment.get('brand_consistency_score', 0)}/10")
        print(f"  Design Quality: {assessment.get('design_quality_score', 0)}/10")
        print(f"  Content Effectiveness: {assessment.get('content_effectiveness_score', 0)}/10")
        
        # Recommendations
        print("\n💡 TOP RECOMMENDATIONS")
        print("-" * 70)
        for i, rec in enumerate(assessment.get('recommendations', [])[:3], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*70)


def main():
    """Main execution function"""
    print("="*70)
    print("🤖 Website Branding & Design Analyzer")
    print("Powered by Groq AI")
    print("="*70)
    print()
    
    # Get Groq API key
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("⚠️  GROQ_API_KEY not found in environment variables")
        api_key = input("Enter your Groq API key: ").strip()
        
        if not api_key:
            print("❌ API key is required. Exiting...")
            return
    
    # Get scraped directory
    scraped_dir = input("Enter the path to scraped_output directory (default: ./scraped_output): ").strip()
    
    if not scraped_dir:
        scraped_dir = "./scraped_output"
    
    try:
        # Create analyzer
        analyzer = WebsiteAnalyzerAgent(groq_api_key=api_key)
        
        # Run analysis
        report = analyzer.analyze_scraped_data(scraped_dir)
        
        print("\n🎉 Analysis complete! Check the JSON report for full details.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()