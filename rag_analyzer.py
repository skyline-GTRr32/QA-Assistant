"""
RAG-Enhanced Website Analyzer
Compares scraped website against brand guide documents

Workflow:
1. User uploads brand guide (.md/.txt)
2. Agent scrapes website
3. Agent loads brand guide into RAG
4. Agent compares website vs brand guide
5. Generates compliance report

Usage:
    python rag_analyzer.py
"""

import asyncio
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# RAG imports
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Our imports
from scraper import EnhancedLandingPageScraper
from groq import Groq


class RAGWebsiteAnalyzer:
    """Analyzes website and compares against brand guide using RAG"""
    
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"
        
        # Initialize ChromaDB for RAG
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create collection for brand guide
        self.collection = self.chroma_client.create_collection(
            name="brand_guide",
            metadata={"description": "Brand guidelines and design rules"}
        )
        
        print("✅ RAG system initialized")
    
    def load_brand_guide(self, file_path: str):
        """
        Load brand guide document into RAG system
        
        Args:
            file_path: Path to .md or .txt brand guide
        """
        print("\n" + "="*80)
        print("📚 LOADING BRAND GUIDE INTO RAG")
        print("="*80)
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Brand guide not found: {file_path}")
        
        # Read the brand guide
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 File: {file_path.name}")
        print(f"📏 Size: {len(content)} characters")
        
        # Split into chunks (by sections or paragraphs)
        chunks = self._split_into_chunks(content)
        print(f"📦 Chunks: {len(chunks)}")
        
        # Store in ChromaDB
        for i, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                ids=[f"chunk_{i}"],
                metadatas=[{
                    "source": file_path.name,
                    "chunk_index": i,
                    "type": self._detect_section_type(chunk)
                }]
            )
        
        print(f"✅ Brand guide loaded into RAG system!")
        print("="*80 + "\n")
        
        return {
            'file': file_path.name,
            'chunks': len(chunks),
            'total_chars': len(content)
        }
    
    def _split_into_chunks(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into semantic chunks"""
        
        # First try to split by headers (markdown style)
        sections = re.split(r'\n#{1,6}\s+', text)
        
        chunks = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # If section is too long, split by paragraphs
            if len(section) > chunk_size:
                paragraphs = section.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        # If still too long, split by sentences
                        if len(para) > chunk_size:
                            sentences = para.split('. ')
                            current_chunk = ""
                            for sent in sentences:
                                if len(current_chunk) + len(sent) < chunk_size:
                                    current_chunk += sent + ". "
                                else:
                                    if current_chunk:
                                        chunks.append(current_chunk.strip())
                                    current_chunk = sent + ". "
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                        else:
                            chunks.append(para)
            else:
                chunks.append(section)
        
        return chunks
    
    def _detect_section_type(self, text: str) -> str:
        """Detect what type of guideline this chunk contains"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['color', 'palette', 'hex', '#']):
            return 'colors'
        elif any(word in text_lower for word in ['font', 'typography', 'typeface']):
            return 'typography'
        elif any(word in text_lower for word in ['logo', 'brand mark', 'icon']):
            return 'logo'
        elif any(word in text_lower for word in ['tone', 'voice', 'messaging']):
            return 'messaging'
        elif any(word in text_lower for word in ['spacing', 'layout', 'grid']):
            return 'layout'
        else:
            return 'general'
    
    async def analyze_with_brand_guide(self, url: str, output_file: str = "compliance_report.json"):
        """
        Analyze website and compare against brand guide
        
        Args:
            url: Website URL
            output_file: Output report filename
            
        Returns:
            Compliance report
        """
        print("\n" + "="*80)
        print("🚀 RAG-ENHANCED WEBSITE ANALYSIS")
        print("="*80)
        print(f"📍 URL: {url}")
        print(f"💾 Report: {output_file}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="website_scrape_")
        
        try:
            # STEP 1: Scrape website
            print("="*80)
            print("STEP 1: SCRAPING WEBSITE")
            print("="*80)
            
            scraper = EnhancedLandingPageScraper(url=url, output_dir=temp_dir)
            scrape_result = await scraper.scrape()
            
            if not scrape_result['success']:
                return {'success': False, 'error': scrape_result.get('error')}
            
            print(f"✅ Scraping complete!")
            
            # STEP 2: Extract website data
            print("\n" + "="*80)
            print("STEP 2: EXTRACTING WEBSITE DATA")
            print("="*80)
            
            website_data = self._extract_website_data(temp_dir)
            print(f"✅ Extracted: Colors, Fonts, Content")
            
            # STEP 3: Compare with brand guide using RAG
            print("\n" + "="*80)
            print("STEP 3: COMPARING WITH BRAND GUIDE (RAG)")
            print("="*80)
            
            comparison = await self._compare_with_brand_guide(website_data)
            print(f"✅ Comparison complete!")
            
            # STEP 4: Generate compliance report
            print("\n" + "="*80)
            print("STEP 4: GENERATING COMPLIANCE REPORT")
            print("="*80)
            
            report = self._generate_compliance_report(url, website_data, comparison)
            
            # Save report
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Report saved: {output_file}")
            
            # Print summary
            self._print_compliance_summary(report)
            
            return {
                'success': True,
                'report_file': output_file,
                'compliance_score': report['compliance_summary']['overall_score']
            }
            
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"\n✅ Temp files cleaned up")
    
    def _extract_website_data(self, temp_dir: str) -> Dict:
        """Extract key data from scraped website"""
        
        temp_path = Path(temp_dir)
        data = {
            'colors': [],
            'fonts': [],
            'content': '',
            'metadata': {}
        }
        
        # Load metadata
        metadata_files = list(temp_path.glob('metadata_*.json'))
        if metadata_files:
            with open(metadata_files[0], 'r', encoding='utf-8') as f:
                data['metadata'] = json.load(f)
        
        # Load computed styles for colors and fonts
        computed_files = list(temp_path.glob('computed_styles_*.json'))
        if computed_files:
            with open(computed_files[0], 'r', encoding='utf-8') as f:
                computed = json.load(f)
                
                for selector, styles in computed.items():
                    # Colors
                    if 'color' in styles:
                        data['colors'].append(styles['color'])
                    if 'backgroundColor' in styles:
                        data['colors'].append(styles['backgroundColor'])
                    
                    # Fonts
                    if 'fontFamily' in styles:
                        data['fonts'].append(styles['fontFamily'])
        
        # Load CSS for more colors
        css_files = list(temp_path.glob('css_*.css')) + list(temp_path.glob('style_tags_*.css'))
        all_css = ""
        for css_file in css_files:
            with open(css_file, 'r', encoding='utf-8') as f:
                all_css += f.read()
        
        # Extract hex colors from CSS
        hex_colors = re.findall(r'#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b', all_css)
        data['colors'].extend(hex_colors)
        
        # Remove duplicates
        data['colors'] = list(set(data['colors']))
        data['fonts'] = list(set(data['fonts']))
        
        # Load HTML for content
        html_files = list(temp_path.glob('page_*.html'))
        if html_files:
            with open(html_files[0], 'r', encoding='utf-8') as f:
                html = f.read()
                # Clean HTML
                text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
                text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
                text = re.sub(r'<[^>]+>', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                data['content'] = text[:3000]  # First 3000 chars
        
        return data
    
    async def _compare_with_brand_guide(self, website_data: Dict) -> Dict:
        """Compare website data with brand guide using RAG"""
        
        comparison = {
            'colors': {'status': 'unknown', 'details': '', 'matches': [], 'violations': []},
            'typography': {'status': 'unknown', 'details': '', 'matches': [], 'violations': []},
            'messaging': {'status': 'unknown', 'details': '', 'matches': [], 'violations': []},
            'overall': {'status': 'unknown', 'details': ''}
        }
        
        # Query 1: Colors
        print("🎨 Checking colors...")
        colors_query = f"What are the approved brand colors? Website uses: {', '.join(website_data['colors'][:10])}"
        colors_context = self._query_brand_guide(colors_query, category='colors')
        colors_analysis = await self._analyze_with_ai(
            f"Brand Guide Colors: {colors_context}\n\nWebsite Colors: {website_data['colors'][:15]}\n\nAre the website colors compliant with the brand guide?",
            "colors"
        )
        comparison['colors'] = colors_analysis
        
        # Query 2: Typography
        print("✍️  Checking typography...")
        fonts_query = f"What are the approved brand fonts? Website uses: {', '.join(website_data['fonts'][:5])}"
        fonts_context = self._query_brand_guide(fonts_query, category='typography')
        fonts_analysis = await self._analyze_with_ai(
            f"Brand Guide Fonts: {fonts_context}\n\nWebsite Fonts: {website_data['fonts']}\n\nAre the website fonts compliant with the brand guide?",
            "typography"
        )
        comparison['typography'] = fonts_analysis
        
        # Query 3: Messaging/Tone
        print("💬 Checking messaging...")
        messaging_query = f"What is the brand tone and messaging style?"
        messaging_context = self._query_brand_guide(messaging_query, category='messaging')
        content_sample = website_data['content'][:800]
        messaging_analysis = await self._analyze_with_ai(
            f"Brand Guide Messaging: {messaging_context}\n\nWebsite Content Sample: {content_sample}\n\nDoes the website messaging match the brand guide?",
            "messaging"
        )
        comparison['messaging'] = messaging_analysis
        
        # Overall assessment
        print("📊 Overall assessment...")
        overall_analysis = await self._analyze_with_ai(
            f"Summarize the overall brand compliance based on:\nColors: {comparison['colors']['status']}\nTypography: {comparison['typography']['status']}\nMessaging: {comparison['messaging']['status']}",
            "overall"
        )
        comparison['overall'] = overall_analysis
        
        return comparison
    
    def _query_brand_guide(self, query: str, category: str = None, n_results: int = 3) -> str:
        """Query RAG system for relevant brand guide info"""
        
        where_filter = None
        if category:
            where_filter = {"type": category}
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            if results['documents'] and results['documents'][0]:
                return "\n\n".join(results['documents'][0])
            else:
                return "No relevant brand guidelines found."
        except Exception as e:
            print(f"⚠️  RAG query error: {e}")
            return "Error querying brand guide."
    
    async def _analyze_with_ai(self, context: str, category: str) -> Dict:
        """Use Groq to analyze compliance"""
        
        prompt = f"""You are a brand compliance expert. Analyze the following:

{context}

Respond ONLY with valid JSON in this format:
{{
  "status": "compliant/partial/non-compliant",
  "details": "detailed explanation",
  "matches": ["what matches the brand guide"],
  "violations": ["what violates the brand guide"],
  "score": 0-100,
  "recommendations": ["specific recommendations"]
}}

Respond with ONLY valid JSON, no markdown, no explanation."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a brand compliance analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Clean response
            ai_response = re.sub(r'```json\s*', '', ai_response)
            ai_response = re.sub(r'```\s*', '', ai_response)
            
            result = json.loads(ai_response)
            return result
            
        except Exception as e:
            print(f"⚠️  AI analysis error ({category}): {e}")
            return {
                "status": "error",
                "details": f"Analysis failed: {str(e)}",
                "matches": [],
                "violations": [],
                "score": 0,
                "recommendations": []
            }
    
    def _generate_compliance_report(self, url: str, website_data: Dict, comparison: Dict) -> Dict:
        """Generate final compliance report"""
        
        # Calculate overall score
        scores = []
        for category in ['colors', 'typography', 'messaging']:
            if 'score' in comparison[category]:
                scores.append(comparison[category]['score'])
        
        overall_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "website_url": url,
            "compliance_summary": {
                "overall_score": round(overall_score, 1),
                "status": "compliant" if overall_score >= 80 else "partial" if overall_score >= 50 else "non-compliant",
                "colors_score": comparison['colors'].get('score', 0),
                "typography_score": comparison['typography'].get('score', 0),
                "messaging_score": comparison['messaging'].get('score', 0)
            },
            "detailed_analysis": {
                "colors": comparison['colors'],
                "typography": comparison['typography'],
                "messaging": comparison['messaging'],
                "overall": comparison['overall']
            },
            "website_data": {
                "colors_found": website_data['colors'][:20],
                "fonts_found": website_data['fonts'],
                "metadata": website_data['metadata']
            },
            "all_recommendations": self._collect_recommendations(comparison)
        }
    
    def _collect_recommendations(self, comparison: Dict) -> List[str]:
        """Collect all recommendations from comparison"""
        all_recs = []
        for category in ['colors', 'typography', 'messaging']:
            if 'recommendations' in comparison[category]:
                all_recs.extend(comparison[category]['recommendations'])
        return all_recs
    
    def _print_compliance_summary(self, report: Dict):
        """Print beautiful compliance summary"""
        print("\n" + "="*80)
        print("📊 BRAND COMPLIANCE REPORT")
        print("="*80)
        
        summary = report['compliance_summary']
        
        # Overall Score
        score = summary['overall_score']
        status = summary['status']
        
        status_emoji = "✅" if status == "compliant" else "⚠️" if status == "partial" else "❌"
        
        print(f"\n{status_emoji} OVERALL COMPLIANCE: {score}/100 ({status.upper()})")
        print("="*80)
        
        # Category Scores
        print("\n📊 CATEGORY SCORES:")
        print(f"  🎨 Colors: {summary['colors_score']}/100")
        print(f"  ✍️  Typography: {summary['typography_score']}/100")
        print(f"  💬 Messaging: {summary['messaging_score']}/100")
        
        # Details
        details = report['detailed_analysis']
        
        print("\n🎨 COLORS")
        print(f"  Status: {details['colors']['status']}")
        print(f"  Details: {details['colors']['details'][:150]}...")
        
        print("\n✍️  TYPOGRAPHY")
        print(f"  Status: {details['typography']['status']}")
        print(f"  Details: {details['typography']['details'][:150]}...")
        
        print("\n💬 MESSAGING")
        print(f"  Status: {details['messaging']['status']}")
        print(f"  Details: {details['messaging']['details'][:150]}...")
        
        # Top Recommendations
        print("\n💡 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(report['all_recommendations'][:5], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*80 + "\n")


async def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("🎯 RAG-ENHANCED WEBSITE BRAND COMPLIANCE ANALYZER")
    print("   Compare Website vs Brand Guide Documents")
    print("="*80 + "\n")
    
    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        api_key = input("Enter Groq API key: ").strip()
        if not api_key:
            print("❌ API key required")
            sys.exit(1)
    
    # Initialize RAG analyzer
    analyzer = RAGWebsiteAnalyzer(groq_api_key=api_key)
    
    # Get brand guide file
    print("\n" + "-"*80)
    brand_guide_path = input("Enter brand guide file path (.md or .txt): ").strip()
    
    if not brand_guide_path or not os.path.exists(brand_guide_path):
        print("❌ Brand guide file not found")
        sys.exit(1)
    
    # Load brand guide into RAG
    try:
        analyzer.load_brand_guide(brand_guide_path)
    except Exception as e:
        print(f"❌ Failed to load brand guide: {e}")
        sys.exit(1)
    
    # Get website URL
    print("\n" + "-"*80)
    url = input("Enter website URL to analyze: ").strip()
    if not url:
        print("❌ URL required")
        sys.exit(1)
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Get output filename
    print("\n" + "-"*80)
    output_file = input("Report filename (default: compliance_report.json): ").strip()
    if not output_file:
        output_file = "compliance_report.json"
    
    # Confirm
    print("\n" + "="*80)
    print("CONFIGURATION:")
    print(f"  Brand Guide: {brand_guide_path}")
    print(f"  Website: {url}")
    print(f"  Report: {output_file}")
    print(f"  Mode: RAG-Enhanced Compliance Check")
    print("="*80)
    
    confirm = input("\n▶️  Start analysis? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        sys.exit(0)
    
    # Run analysis
    try:
        result = await analyzer.analyze_with_brand_guide(url, output_file)
        
        if result['success']:
            print(f"\n🎉 SUCCESS!")
            print(f"📄 Compliance Report: {result['report_file']}")
            print(f"📊 Overall Score: {result['compliance_score']}/100")
            return 0
        else:
            print(f"\n❌ Failed: {result.get('error')}")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)