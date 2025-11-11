"""
Proper Pipeline - Uses Your Analyzer Agent
Integrates scraper.py + analzye_agent.py properly

Workflow:
1. Scrape website → Store in temp directory
2. Call your WebsiteAnalyzerAgent
3. Clean up temp files, keep only AI report

Usage:
    python main_with_agent.py
"""

import asyncio
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import tempfile

# Import scraper
from scraper import EnhancedLandingPageScraper

# Import YOUR analyzer agent
from website_analyzer_agent import WebsiteAnalyzerAgent


class ProperPipeline:
    """Pipeline that properly uses your WebsiteAnalyzerAgent"""
    
    def __init__(self, groq_api_key: str, output_file: str = "website_analysis.json"):
        self.groq_api_key = groq_api_key
        self.output_file = output_file
        self.temp_dir = None
        
    async def analyze_website(self, url: str):
        """
        Complete pipeline using your agent
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Dictionary with analysis results
        """
        print("\n" + "="*80)
        print("🚀 WEBSITE ANALYSIS PIPELINE")
        print("   Using WebsiteAnalyzerAgent")
        print("="*80)
        print(f"📍 URL: {url}")
        print(f"💾 Report: {self.output_file}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        # Create temp directory for scraping
        self.temp_dir = tempfile.mkdtemp(prefix="website_scrape_")
        print(f"📁 Temp directory: {self.temp_dir}")
        
        try:
            # STEP 1: Scrape website to temp directory
            print("\n" + "="*80)
            print("STEP 1: SCRAPING WEBSITE")
            print("="*80)
            
            scraper = EnhancedLandingPageScraper(url=url, output_dir=self.temp_dir)
            scrape_result = await scraper.scrape()
            
            if not scrape_result['success']:
                print(f"❌ Scraping failed: {scrape_result.get('error')}")
                return {'success': False, 'error': scrape_result.get('error')}
            
            print(f"✅ Scraping complete!")
            print(f"   • Images: {scrape_result['images_downloaded']}")
            print(f"   • Output: {scrape_result['output_dir']}")
            
            # STEP 2: Analyze with YOUR agent
            print("\n" + "="*80)
            print("STEP 2: AI ANALYSIS (Using WebsiteAnalyzerAgent)")
            print("="*80)
            
            # Initialize YOUR analyzer agent
            analyzer = WebsiteAnalyzerAgent(groq_api_key=self.groq_api_key)
            
            # Call YOUR agent's analyze method
            analysis_report = analyzer.analyze_scraped_data(self.temp_dir)
            
            print(f"✅ Analysis complete!")
            
            # STEP 3: Save final report
            print("\n" + "="*80)
            print("STEP 3: SAVING FINAL REPORT")
            print("="*80)
            
            # Find the AI analysis file from temp directory
            import json
            analysis_files = list(Path(self.temp_dir).glob('ai_analysis_*.json'))
            
            if analysis_files:
                # Copy the AI report to final location
                latest_analysis = max(analysis_files, key=lambda x: x.stat().st_mtime)
                
                with open(latest_analysis, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Report saved: {self.output_file}")
            
            # Print summary
            self._print_summary(analysis_report)
            
            return {
                'success': True,
                'report_file': self.output_file,
                'analysis': analysis_report
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
        
        finally:
            # STEP 4: Cleanup temp files
            if self.temp_dir and os.path.exists(self.temp_dir):
                print("\n" + "="*80)
                print("STEP 4: CLEANING UP TEMP FILES")
                print("="*80)
                try:
                    shutil.rmtree(self.temp_dir)
                    print(f"✅ Temp files deleted: {self.temp_dir}")
                except Exception as e:
                    print(f"⚠️  Could not delete temp files: {e}")
    
    def _print_summary(self, report: dict):
        """Print beautiful summary"""
        print("\n" + "="*80)
        print("📊 FINAL SUMMARY")
        print("="*80)
        
        try:
            ai = report['ai_analysis']
            tech = report['technical_details']
            
            print("\n🎯 BRAND")
            print(f"  Name: {ai['brand_identity'].get('brand_name', 'N/A')}")
            print(f"  Description: {ai['brand_identity'].get('brand_description', 'N/A')[:60]}...")
            print(f"  Tone: {ai['brand_identity'].get('tone_of_voice', 'N/A')}")
            
            print("\n🎨 COLORS")
            print(f"  Primary: {ai['color_analysis'].get('primary_color', 'N/A')}")
            print(f"  Secondary: {', '.join(ai['color_analysis'].get('secondary_colors', [])[:3])}")
            print(f"  Mood: {ai['color_analysis'].get('mood', 'N/A')}")
            print(f"  Total Unique: {tech['colors']['total_unique_colors']}")
            
            print("\n✍️  TYPOGRAPHY")
            print(f"  Primary Font: {ai['typography_analysis'].get('primary_font', 'N/A')}")
            print(f"  Style: {ai['typography_analysis'].get('style', 'N/A')}")
            print(f"  Readability: {ai['typography_analysis'].get('readability', 'N/A')}")
            
            print("\n📝 CONTENT")
            print(f"  Type: {ai['content_analysis'].get('content_type', 'N/A')}")
            print(f"  Quality: {ai['content_analysis'].get('content_quality', 'N/A')}")
            
            print("\n⭐ QUALITY SCORES")
            assess = ai['overall_assessment']
            print(f"  Brand Consistency: {assess.get('brand_consistency_score', 0)}/10")
            print(f"  Design Quality: {assess.get('design_quality_score', 0)}/10")
            print(f"  Content Effectiveness: {assess.get('content_effectiveness_score', 0)}/10")
            
            print("\n💡 TOP RECOMMENDATIONS")
            for i, rec in enumerate(assess.get('recommendations', [])[:3], 1):
                print(f"  {i}. {rec}")
            
        except Exception as e:
            print(f"⚠️  Could not print summary: {e}")
        
        print("\n" + "="*80)
        print(f"✅ Analysis complete! Report: {self.output_file}")
        print("="*80 + "\n")


async def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("🌐 WEBSITE ANALYZER WITH PROPER AGENT INTEGRATION")
    print("   Scraper → WebsiteAnalyzerAgent → Final Report")
    print("="*80 + "\n")
    
    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        api_key = input("Enter Groq API key: ").strip()
        if not api_key:
            print("❌ API key required")
            sys.exit(1)
    else:
        print(f"✅ API key found: {api_key[:20]}...")
    
    # Get URL
    print("\n" + "-"*80)
    url = input("Enter website URL: ").strip()
    if not url:
        print("❌ URL required")
        sys.exit(1)
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"📝 Auto-corrected to: {url}")
    
    # Get output filename
    print("\n" + "-"*80)
    output_file = input("Report filename (default: website_analysis.json): ").strip()
    if not output_file:
        output_file = "website_analysis.json"
    
    # Confirm
    print("\n" + "="*80)
    print("CONFIGURATION:")
    print(f"  URL: {url}")
    print(f"  Report: {output_file}")
    print(f"  Pipeline: Scraper → Agent → Cleanup")
    print("="*80)
    
    confirm = input("\n▶️  Start analysis? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        sys.exit(0)
    
    # Run analysis
    try:
        pipeline = ProperPipeline(
            groq_api_key=api_key,
            output_file=output_file
        )
        
        result = await pipeline.analyze_website(url)
        
        if result['success']:
            print("\n🎉 SUCCESS!")
            print(f"📄 Report saved: {result['report_file']}")
            return 0
        else:
            print(f"\n❌ Failed: {result.get('error')}")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)