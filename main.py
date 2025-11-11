"""
Main Integration Script
Combines Landing Page Scraper + AI Analysis Agent

Workflow:
1. Scrape website (HTML, CSS, images)
2. Pass scraped data to AI analyzer
3. Generate comprehensive branding report

Usage:
    python main.py
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Import our modules
from scraper import EnhancedLandingPageScraper
from website_analyzer_agent import WebsiteAnalyzerAgent


class WebsiteAnalysisPipeline:
    """Complete pipeline: Scrape → Analyze → Report"""
    
    def __init__(self, groq_api_key: str, output_dir: str = "scraped_output"):
        self.groq_api_key = groq_api_key
        self.output_dir = output_dir
        
    async def run_full_analysis(self, url: str):
        """
        Run complete analysis pipeline
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Dictionary with scraping and analysis results
        """
        print("\n" + "="*80)
        print("🚀 WEBSITE ANALYSIS PIPELINE")
        print("="*80)
        print(f"📍 Target URL: {url}")
        print(f"📁 Output Directory: {self.output_dir}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        # STEP 1: Scrape the website
        print("="*80)
        print("STEP 1: SCRAPING WEBSITE")
        print("="*80)
        
        try:
            scraper = EnhancedLandingPageScraper(url=url, output_dir=self.output_dir)
            scrape_result = await scraper.scrape()
            
            if not scrape_result['success']:
                print(f"\n❌ Scraping failed: {scrape_result.get('error', 'Unknown error')}")
                return {
                    'success': False,
                    'step': 'scraping',
                    'error': scrape_result.get('error', 'Unknown error')
                }
            
            print(f"\n✅ Scraping completed successfully!")
            print(f"   • Images downloaded: {scrape_result['images_downloaded']}")
            print(f"   • Output directory: {scrape_result['output_dir']}")
            
        except Exception as e:
            print(f"\n❌ Scraping error: {e}")
            return {
                'success': False,
                'step': 'scraping',
                'error': str(e)
            }
        
        # Small pause between steps
        await asyncio.sleep(2)
        
        # STEP 2: AI Analysis
        print("\n" + "="*80)
        print("STEP 2: AI-POWERED ANALYSIS")
        print("="*80)
        
        try:
            analyzer = WebsiteAnalyzerAgent(groq_api_key=self.groq_api_key)
            analysis_report = analyzer.analyze_scraped_data(self.output_dir)
            
            print(f"\n✅ AI Analysis completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Analysis error: {e}")
            return {
                'success': False,
                'step': 'analysis',
                'error': str(e),
                'scrape_result': scrape_result
            }
        
        # STEP 3: Final Summary
        print("\n" + "="*80)
        print("📊 PIPELINE COMPLETE - FINAL SUMMARY")
        print("="*80)
        
        final_result = {
            'success': True,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'scraping': {
                'images_downloaded': scrape_result['images_downloaded'],
                'output_dir': scrape_result['output_dir'],
                'images_dir': scrape_result['images_dir']
            },
            'analysis': {
                'brand_name': analysis_report['ai_analysis']['brand_identity'].get('brand_name', 'N/A'),
                'primary_color': analysis_report['ai_analysis']['color_analysis'].get('primary_color', 'N/A'),
                'primary_font': analysis_report['ai_analysis']['typography_analysis'].get('primary_font', 'N/A'),
                'design_score': analysis_report['ai_analysis']['overall_assessment'].get('design_quality_score', 0),
                'brand_score': analysis_report['ai_analysis']['overall_assessment'].get('brand_consistency_score', 0)
            },
            'output_files': {
                'scraped_data': scrape_result['output_dir'],
                'ai_report': str(Path(self.output_dir) / f"ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            }
        }
        
        # Print beautiful summary
        self._print_final_summary(final_result)
        
        return final_result
    
    def _print_final_summary(self, result: dict):
        """Print a beautiful final summary"""
        print(f"\n✅ WEBSITE: {result['url']}")
        print(f"⏰ COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "-"*80)
        
        print("\n📊 SCRAPING RESULTS:")
        print(f"   • Images Downloaded: {result['scraping']['images_downloaded']}")
        print(f"   • Output Directory: {result['scraping']['output_dir']}")
        
        print("\n🎯 BRAND ANALYSIS:")
        print(f"   • Brand Name: {result['analysis']['brand_name']}")
        print(f"   • Primary Color: {result['analysis']['primary_color']}")
        print(f"   • Primary Font: {result['analysis']['primary_font']}")
        
        print("\n⭐ QUALITY SCORES:")
        print(f"   • Brand Consistency: {result['analysis']['brand_score']}/10")
        print(f"   • Design Quality: {result['analysis']['design_score']}/10")
        
        print("\n📁 OUTPUT FILES:")
        print(f"   • Scraped Data: {result['output_files']['scraped_data']}")
        print(f"   • AI Report: {result['output_files']['ai_report']}")
        
        print("\n" + "="*80)
        print("🎉 ANALYSIS PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")


async def main():
    """Main execution function with user input"""
    
    # Print header
    print("\n" + "="*80)
    print("🌐 COMPLETE WEBSITE ANALYSIS SYSTEM")
    print("   Scraper + AI Analyzer Powered by Groq")
    print("="*80 + "\n")
    
    # Step 1: Get Groq API Key
    groq_api_key = os.getenv('GROQ_API_KEY')
    
    if not groq_api_key:
        print("⚠️  GROQ_API_KEY not found in environment variables")
        groq_api_key = input("Enter your Groq API key: ").strip()
        
        if not groq_api_key:
            print("\n❌ Error: Groq API key is required to run AI analysis")
            print("💡 Get your free API key at: https://console.groq.com/keys")
            sys.exit(1)
    else:
        print("✅ Groq API key found in environment")
    
    # Step 2: Get website URL
    print("\n" + "-"*80)
    url = input("Enter the website URL to analyze: ").strip()
    
    if not url:
        print("⚠️  No URL provided. Using example: https://example.com")
        url = "https://example.com"
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"📝 Auto-corrected URL to: {url}")
    
    # Step 3: Get output directory (optional)
    print("\n" + "-"*80)
    output_dir = input("Enter output directory (press Enter for default 'scraped_output'): ").strip()
    
    if not output_dir:
        output_dir = "scraped_output"
    
    print(f"📁 Using output directory: {output_dir}")
    
    # Step 4: Confirm and run
    print("\n" + "="*80)
    print("CONFIGURATION:")
    print(f"  URL: {url}")
    print(f"  Output: {output_dir}")
    print(f"  API: Groq (configured)")
    print("="*80)
    
    confirm = input("\n▶️  Start analysis? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("\n❌ Analysis cancelled by user")
        sys.exit(0)
    
    # Step 5: Run the pipeline
    try:
        pipeline = WebsiteAnalysisPipeline(
            groq_api_key=groq_api_key,
            output_dir=output_dir
        )
        
        result = await pipeline.run_full_analysis(url)
        
        if result['success']:
            print("\n🎊 SUCCESS! All analysis files have been saved.")
            print(f"📂 Check the '{output_dir}' directory for:")
            print("   • Scraped HTML, CSS, and images")
            print("   • AI analysis report (JSON)")
            print("   • Full website screenshot")
            return 0
        else:
            print(f"\n❌ Pipeline failed at step: {result.get('step', 'unknown')}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user (Ctrl+C)")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)