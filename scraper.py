"""
Enhanced Landing Page Scraper - PRODUCTION READY (Headless)
For use in web applications - no visible browser

FIXED:
- Runs headless (no browser window)
- Waits longer for images to load
- Uses currentSrc for actual image URLs
- Better error handling
"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import cssutils
import logging
from urllib.parse import urljoin, urlparse

# Suppress cssutils warnings
cssutils.log.setLevel(logging.CRITICAL)


class EnhancedLandingPageScraper:
    def __init__(self, url: str, output_dir: str = "scraped_output"):
        self.url = url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create images subdirectory
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.downloaded_images = {}
        
    async def scrape(self):
        """Main scraping method using Playwright"""
        print(f"🚀 Starting enhanced scrape of: {self.url}")
        
        async with async_playwright() as p:
            # Launch browser - HEADLESS for production
            browser = await p.chromium.launch(
                headless=True,  # ← HEADLESS MODE
                args=['--disable-blink-features=AutomationControlled']  # Avoid detection
            )
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()
            
            try:
                # Navigate to the page
                print("📡 Loading page...")
                await page.goto(self.url, wait_until='networkidle', timeout=60000)
                
                # CRITICAL: Wait for JavaScript to execute and images to load
                print("⏳ Waiting for dynamic content...")
                await page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(3)  # Initial wait
                
                # Scroll to trigger lazy loading
                print("📜 Scrolling to load lazy images...")
                await page.evaluate("""
                    async () => {
                        // Scroll to bottom
                        window.scrollTo(0, document.body.scrollHeight);
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        // Scroll back to top
                        window.scrollTo(0, 0);
                        await new Promise(resolve => setTimeout(resolve, 500));
                    }
                """)
                
                # Final wait for images to render
                await asyncio.sleep(2)
                
                # Extract HTML
                html_content = await page.content()
                print(f"✅ HTML extracted: {len(html_content)} characters")
                
                # Extract inline styles
                inline_styles = await self.extract_inline_styles(page)
                
                # Extract external CSS
                external_css = await self.extract_external_css(page)
                
                # Extract computed styles
                computed_styles = await self.extract_computed_styles(page)
                
                # Extract metadata
                metadata = await self.extract_metadata(page)
                
                # Download images
                await self.download_images(page, context)
                
                # Take screenshot
                screenshot_path = self.output_dir / f"screenshot_{self.timestamp}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                # Save all data
                await self.save_data(
                    html_content, 
                    inline_styles, 
                    external_css, 
                    computed_styles,
                    metadata
                )
                
                print("✨ Scraping completed successfully!")
                print(f"📁 Total images downloaded: {len(self.downloaded_images)}")
                
                return {
                    'success': True,
                    'images_downloaded': len(self.downloaded_images),
                    'output_dir': str(self.output_dir),
                    'images_dir': str(self.images_dir)
                }
                
            except Exception as e:
                print(f"❌ Error during scraping: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
            finally:
                await browser.close()
    
    async def download_images(self, page, context):
        """Download logos, favicons, and important images"""
        print("🖼️  Downloading images...")
        
        # Extract image URLs - IMPROVED to get actual rendered URLs
        image_data = await page.evaluate("""
            () => {
                const images = [];
                
                // Get all img tags with ACTUAL rendered src (important for Next.js)
                document.querySelectorAll('img').forEach(img => {
                    // currentSrc gives the actual loaded image URL
                    const actualSrc = img.currentSrc || img.src;
                    if (actualSrc && !actualSrc.startsWith('data:')) {
                        images.push({
                            type: 'img',
                            src: actualSrc,
                            alt: img.alt || '',
                            class: img.className || '',
                            id: img.id || '',
                            width: img.naturalWidth || 0,
                            height: img.naturalHeight || 0
                        });
                    }
                });
                
                // Get favicons
                document.querySelectorAll('link[rel*="icon"]').forEach(link => {
                    if (link.href && !link.href.startsWith('data:')) {
                        images.push({
                            type: 'favicon',
                            src: link.href,
                            alt: 'favicon',
                            rel: link.rel
                        });
                    }
                });
                
                // Get apple touch icons
                document.querySelectorAll('link[rel*="apple-touch-icon"]').forEach(link => {
                    if (link.href) {
                        images.push({
                            type: 'apple-icon',
                            src: link.href,
                            alt: 'apple-touch-icon',
                            rel: link.rel
                        });
                    }
                });
                
                // Get og:image
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    images.push({
                        type: 'og-image',
                        src: ogImage.content,
                        alt: 'og-image'
                    });
                }
                
                return images;
            }
        """)
        
        print(f"  Found {len(image_data)} images to download")
        
        # Download each image
        download_count = 0
        for idx, img_info in enumerate(image_data):
            success = await self.download_single_image(context, img_info, idx)
            if success:
                download_count += 1
        
        print(f"  ✓ Successfully downloaded {download_count}/{len(image_data)} images")
        
        # Save image manifest
        manifest_path = self.images_dir / f"image_manifest_{self.timestamp}.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.downloaded_images, f, indent=2)
        print(f"  ✓ Image manifest saved: {manifest_path}")
    
    async def download_single_image(self, context, img_info, idx):
        """Download a single image"""
        try:
            img_url = img_info['src']
            
            # Skip data URLs
            if img_url.startswith('data:'):
                return False
            
            # Make URL absolute
            full_url = urljoin(self.url, img_url)
            
            # Skip if already downloaded
            if full_url in self.downloaded_images:
                return False
            
            # Generate filename
            filename = self.get_safe_filename(img_info, idx)
            file_path = self.images_dir / filename
            
            # Create a new page for downloading
            page = await context.new_page()
            
            try:
                response = await page.goto(full_url, timeout=30000)
                
                if response and response.status == 200:
                    image_content = await response.body()
                    
                    # Save to file
                    with open(file_path, 'wb') as f:
                        f.write(image_content)
                    
                    # Track it
                    self.downloaded_images[full_url] = {
                        'filename': str(file_path),
                        'size': len(image_content),
                        'type': img_info.get('type', 'unknown')
                    }
                    
                    print(f"  ✓ {filename} ({len(image_content):,} bytes)")
                    return True
                else:
                    print(f"  ✗ HTTP {response.status}: {img_url[:50]}...")
                    return False
                    
            except Exception as e:
                print(f"  ✗ Failed: {str(e)[:40]}")
                return False
            finally:
                await page.close()
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:50]}")
            return False
    
    def get_safe_filename(self, img_info, idx):
        """Generate a safe filename for the image"""
        img_type = img_info.get('type', 'image')
        img_alt = img_info.get('alt', '').replace(' ', '_')
        img_url = img_info.get('src', '')
        
        # Get extension from URL
        parsed = urlparse(img_url)
        path = parsed.path
        
        if '.' in path:
            ext = path.split('.')[-1].split('?')[0][:4]
        else:
            ext = 'png'
        
        ext = re.sub(r'[^\w]', '', ext) or 'png'
        
        # Create filename based on type
        if img_type == 'favicon':
            filename = f"favicon_{idx}.{ext}"
        elif img_type == 'apple-icon':
            filename = f"apple_icon_{idx}.{ext}"
        elif img_type == 'og-image':
            filename = f"og_image_{idx}.{ext}"
        elif 'logo' in img_alt.lower() or 'logo' in img_info.get('class', '').lower():
            filename = f"logo_{idx}.{ext}"
        else:
            safe_alt = re.sub(r'[^\w\-_]', '_', img_alt)[:30]
            filename = f"{safe_alt or 'image'}_{idx}.{ext}"
        
        return filename
    
    async def extract_inline_styles(self, page):
        """Extract all inline styles from the page"""
        print("🎨 Extracting inline styles...")
        
        inline_styles = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('[style]');
                return Array.from(elements).map(el => ({
                    tag: el.tagName,
                    class: el.className,
                    id: el.id,
                    style: el.getAttribute('style')
                }));
            }
        """)
        
        return inline_styles
    
    async def extract_external_css(self, page):
        """Extract all external CSS files"""
        print("📄 Extracting external CSS...")
        
        css_links = await page.evaluate("""
            () => {
                const links = document.querySelectorAll('link[rel="stylesheet"]');
                return Array.from(links).map(link => link.href);
            }
        """)
        
        css_contents = {}
        for css_url in css_links:
            try:
                response = await page.goto(css_url, wait_until='networkidle', timeout=30000)
                if response and response.ok:
                    css_contents[css_url] = await response.text()
                    print(f"  ✓ Fetched CSS")
            except Exception as e:
                print(f"  ✗ CSS fetch failed")
        
        # Also extract style tags
        style_tags = await page.evaluate("""
            () => {
                const styles = document.querySelectorAll('style');
                return Array.from(styles).map(style => style.textContent);
            }
        """)
        
        return {
            'external_files': css_contents,
            'style_tags': style_tags
        }
    
    async def extract_computed_styles(self, page):
        """Extract computed styles for important elements"""
        print("🔍 Extracting computed styles...")
        
        computed_styles = await page.evaluate("""
            () => {
                const selectors = [
                    'body',
                    'header',
                    'nav',
                    'main',
                    'footer',
                    '.hero, [class*="hero"]',
                    '.container, [class*="container"]',
                    'h1, h2, h3',
                    'button, .button, .btn',
                    'a'
                ];
                
                const results = {};
                
                selectors.forEach(selector => {
                    const element = document.querySelector(selector);
                    if (element) {
                        const styles = window.getComputedStyle(element);
                        results[selector] = {
                            display: styles.display,
                            position: styles.position,
                            width: styles.width,
                            height: styles.height,
                            margin: styles.margin,
                            padding: styles.padding,
                            backgroundColor: styles.backgroundColor,
                            color: styles.color,
                            fontSize: styles.fontSize,
                            fontFamily: styles.fontFamily,
                            fontWeight: styles.fontWeight,
                            lineHeight: styles.lineHeight,
                            textAlign: styles.textAlign,
                            border: styles.border,
                            borderRadius: styles.borderRadius,
                            boxShadow: styles.boxShadow
                        };
                    }
                });
                
                return results;
            }
        """)
        
        return computed_styles
    
    async def extract_metadata(self, page):
        """Extract page metadata"""
        print("📊 Extracting metadata...")
        
        metadata = await page.evaluate("""
            () => {
                return {
                    title: document.title,
                    description: document.querySelector('meta[name="description"]')?.content || '',
                    keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                    ogTitle: document.querySelector('meta[property="og:title"]')?.content || '',
                    ogDescription: document.querySelector('meta[property="og:description"]')?.content || '',
                    ogImage: document.querySelector('meta[property="og:image"]')?.content || '',
                    viewport: document.querySelector('meta[name="viewport"]')?.content || '',
                    charset: document.characterSet,
                    language: document.documentElement.lang,
                    scripts: Array.from(document.querySelectorAll('script[src]')).map(s => s.src),
                    fonts: Array.from(document.querySelectorAll('link[rel*="font"]')).map(f => f.href)
                };
            }
        """)
        
        return metadata
    
    async def save_data(self, html, inline_styles, external_css, computed_styles, metadata):
        """Save all scraped data to files"""
        print("💾 Saving data...")
        
        # Save HTML
        html_path = self.output_dir / f"page_{self.timestamp}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✓ HTML saved")
        
        # Save inline styles
        inline_path = self.output_dir / f"inline_styles_{self.timestamp}.json"
        with open(inline_path, 'w', encoding='utf-8') as f:
            json.dump(inline_styles, f, indent=2)
        print(f"  ✓ Inline styles saved")
        
        # Save external CSS
        for css_url, css_content in external_css['external_files'].items():
            safe_filename = re.sub(r'[^\w\-_.]', '_', css_url.split('/')[-1])
            css_path = self.output_dir / f"css_{safe_filename}_{self.timestamp}.css"
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            print(f"  ✓ CSS saved")
        
        # Save style tags
        if external_css['style_tags']:
            style_tags_path = self.output_dir / f"style_tags_{self.timestamp}.css"
            with open(style_tags_path, 'w', encoding='utf-8') as f:
                f.write('\n\n/* ===== STYLE TAG ===== */\n\n'.join(external_css['style_tags']))
            print(f"  ✓ Style tags saved")
        
        # Save computed styles
        computed_path = self.output_dir / f"computed_styles_{self.timestamp}.json"
        with open(computed_path, 'w', encoding='utf-8') as f:
            json.dump(computed_styles, f, indent=2)
        print(f"  ✓ Computed styles saved")
        
        # Save metadata
        metadata_path = self.output_dir / f"metadata_{self.timestamp}.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f"  ✓ Metadata saved")
        
        # Create summary report
        summary = {
            'url': self.url,
            'scraped_at': datetime.now().isoformat(),
            'html_size': len(html),
            'inline_styles_count': len(inline_styles),
            'external_css_files': len(external_css['external_files']),
            'style_tags_count': len(external_css['style_tags']),
            'computed_styles_count': len(computed_styles),
            'images_downloaded': len(self.downloaded_images),
            'metadata': metadata
        }
        
        summary_path = self.output_dir / f"summary_{self.timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"  ✓ Summary saved")


async def main():
    """Example usage"""
    print("="*70)
    print("🌐 Enhanced Landing Page Scraper (HEADLESS - Production Ready)")
    print("="*70)
    print()
    
    # Get URL from user
    url = input("Enter the landing page URL to scrape: ").strip()
    
    if not url:
        url = "https://example.com"
        print(f"Using default URL: {url}")
    
    # Create scraper instance
    scraper = EnhancedLandingPageScraper(url)
    
    # Run the scraper
    result = await scraper.scrape()
    
    print("\n" + "="*70)
    if result['success']:
        print("🎉 All done! Check the 'scraped_output' folder for results.")
        print(f"📁 Images saved in: scraped_output/images/")
        print(f"📊 Total images: {result['images_downloaded']}")
    else:
        print(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
    print("="*70)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())