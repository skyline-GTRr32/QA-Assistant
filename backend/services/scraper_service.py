# backend/services/scraper_service.py
import re
import sys
import asyncio
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Any
import logging

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ✅ CRITICAL FIX (Windows Only)
# Playwright requires the ProactorEventLoopPolicy to spawn subprocesses properly.
# This must be set BEFORE any Playwright operations.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class ScraperService:
    def scrape_website(self, url: str) -> Dict[str, Any]:
        try:
            scraper = WebsiteScraper(url)
            result = scraper.scrape()
            if result['success']:
                return {
                    'success': True,
                    'data': result['data']
                }
            else:
                raise Exception(result.get('error', 'Unknown scraping error'))
        except Exception as e:
            logging.error(f"An exception occurred in ScraperService: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


class WebsiteScraper:
    def __init__(self, url: str):
        self.url = url
        self.base_url = f"{urlparse(self.url).scheme}://{urlparse(self.url).netloc}"
        self.domain = urlparse(self.url).netloc

    def scrape(self) -> Dict:
        logging.info(f"Starting scrape for URL: {self.url}")
        try:
            logging.info("Initializing Playwright...")
            with sync_playwright() as p:
                logging.info("Playwright initialized successfully")

                try:
                    logging.info("Launching Chromium browser...")
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--disable-dev-shm-usage",
                            "--no-sandbox"
                        ]
                    )
                    logging.info("Browser launched successfully")
                except Exception as browser_error:
                    logging.error(f"Browser launch failed: {browser_error}", exc_info=True)
                    return {"success": False, "error": f"Browser launch failed: {str(browser_error)}"}

                try:
                    logging.info("Creating browser context...")
                    context = browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        user_agent=(
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        ),
                        java_script_enabled=True,
                        ignore_https_errors=True,
                    )
                    logging.info("Browser context created successfully")

                    logging.info("Creating new page...")
                    page = context.new_page()
                    page.set_default_timeout(120000)
                    logging.info("Page created successfully")

                    logging.info(f"Navigating to {self.url}...")
                    response = page.goto(self.url, wait_until="networkidle", timeout=120000)
                    logging.info(f"Navigation completed with status: {response.status if response else 'N/A'}")

                    if not response or not response.ok:
                        raise Exception(f"Failed to load page: Status {response.status if response else 'N/A'}")

                    logging.info("Preparing page (scrolling, waiting)...")
                    self._prepare_page(page)

                    logging.info("Extracting HTML content...")
                    html_content = page.content()
                    soup = BeautifulSoup(html_content, "html.parser")
                    logging.info(f"HTML content extracted, length: {len(str(soup))} characters")

                    logging.info("Processing resources (making URLs absolute)...")
                    self._process_resources(soup)

                    logging.info("Extracting metadata...")
                    metadata = self._extract_metadata(page)

                    logging.info("Extracting scripts...")
                    scripts = self._extract_scripts(page)

                    logging.info("Extracting styles...")
                    styles = self._extract_all_styles(page, soup)

                    logging.info("Extracting assets...")
                    assets = self._extract_assets(page, soup)

                    logging.info("Scraping completed successfully")
                    return {
                        "success": True,
                        "data": {
                            "html": str(soup),
                            "styles": styles,
                            "assets": assets,
                            "metadata": metadata,
                            "scripts": scripts,
                        },
                    }

                except Exception as page_error:
                    logging.error(f"Page operation failed: {page_error}", exc_info=True)
                    return {"success": False, "error": f"Page operation failed: {str(page_error)}"}

                finally:
                    logging.info("Closing browser...")
                    browser.close()
                    logging.info("Browser closed")

        except Exception as e:
            logging.error(f"Playwright initialization failed: {e}", exc_info=True)
            return {"success": False, "error": f"Playwright initialization failed: {str(e)}"}

    # --------------------------------------------------------------------------
    # Helper methods
    # --------------------------------------------------------------------------

    def _prepare_page(self, page):
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)

    def _process_resources(self, soup):
        for tag in soup.find_all(["a", "link", "img", "script", "source", "iframe"], href=True):
            tag["href"] = self._make_absolute(tag.get("href"))
            tag["src"] = self._make_absolute(tag.get("src"))
        for tag in soup.find_all(["img", "source"], srcset=True):
            new_srcset = ", ".join([
                f"{self._make_absolute(part.strip().split(' ')[0])} {part.strip().split(' ')[1]}"
                if " " in part else self._make_absolute(part.strip())
                for part in tag["srcset"].split(",")
            ])
            tag["srcset"] = new_srcset
        for tag in soup.find_all(style=True):
            new_style = re.sub(
                r"url\(['\"]?(.*?)['\"]?\)",
                lambda m: f'url("{self._make_absolute(m.group(1))}")',
                tag["style"],
            )
            tag["style"] = new_style

    def _make_absolute(self, url: str) -> str:
        if not url or url.startswith(("http", "data:", "blob:")):
            return url
        return urljoin(self.base_url, url)

    def _extract_all_styles(self, page, soup) -> Dict:
        return {
            "inline": self._extract_inline_styles(page),
            "external": page.evaluate(
                "() => Array.from(document.querySelectorAll('link[rel=\"stylesheet\"]')).map(link => ({ href: link.href, media: link.media }))"
            ),
            "style_tags": [str(tag) for tag in soup.find_all("style")],
            "computed": self._extract_computed_styles(page),
            "css_rules": self._extract_css_rules(page),
        }

    def _extract_inline_styles(self, page) -> List[Dict]:
        return page.evaluate(
            """() =>
                Array.from(document.querySelectorAll('[style]')).map(el => ({
                    selector:
                        el.tagName +
                        (el.id ? '#' + el.id : '') +
                        (el.className ? '.' + el.className.split(' ').join('.') : ''),
                    styles: el.getAttribute('style'),
                }))"""
        )

    def _extract_css_rules(self, page) -> List[Dict]:
        return page.evaluate(
            """() => {
                const rules = [];
                for (const sheet of document.styleSheets) {
                    try {
                        for (const rule of (sheet.cssRules || [])) {
                            if (rule.selectorText) {
                                rules.push({
                                    selector: rule.selectorText,
                                    cssText: rule.cssText,
                                    href: sheet.href || 'inline'
                                });
                            }
                        }
                    } catch (e) {}
                }
                return rules;
            }"""
        )

    def _extract_computed_styles(self, page) -> Dict:
        return page.evaluate(
            """() => {
                const styles = {};
                document.querySelectorAll('h1, h2, h3, p, a, button, input').forEach(el => {
                    const selector =
                        el.tagName +
                        (el.id ? '#' + el.id : '') +
                        (el.className ? '.' + el.className.split(' ').join('.') : '');
                    if (selector && !styles[selector]) {
                        const computed = window.getComputedStyle(el);
                        styles[selector] = Array.from(computed).reduce((acc, prop) => {
                            acc[prop] = computed.getPropertyValue(prop);
                            return acc;
                        }, {});
                    }
                });
                return styles;
            }"""
        )

    def _extract_assets(self, page, soup) -> Dict:
        return {
            "images": self._extract_assets_by_type(page, "img", "src"),
            "background_images": self._extract_background_images(page),
            "fonts": self._extract_fonts(page),
        }

    def _extract_assets_by_type(self, page, selector: str, attr: str) -> List[Dict]:
        return page.evaluate(
            """({ selector, attr }) =>
                Array.from(document.querySelectorAll(selector))
                    .filter(el => el[attr])
                    .map(el => ({
                        src: el[attr],
                        alt: el.alt || ''
                    }))""",
            {"selector": selector, "attr": attr},
        )

    def _extract_background_images(self, page) -> List[Dict]:
        return page.evaluate(
            """() => {
                const bgImages = [];
                document.querySelectorAll('*').forEach(el => {
                    const bgImage = window.getComputedStyle(el).backgroundImage;
                    if (bgImage && bgImage !== 'none') {
                        const urls = bgImage.match(/url\(["']?(.*?)["']?\)/g) || [];
                        urls.forEach(url => {
                            const cleanUrl = url.replace(/^url\(["']?|["']?\)$/g, '');
                            if (cleanUrl && !cleanUrl.startsWith('data:')) {
                                bgImages.push({
                                    src: cleanUrl,
                                    element: el.tagName.toLowerCase(),
                                    class: el.className || '',
                                    id: el.id || ''
                                });
                            }
                        });
                    }
                });
                return bgImages;
            }"""
        )

    def _extract_fonts(self, page) -> List[Dict]:
        return page.evaluate(
            """() => {
                const fonts = [];
                try {
                    for (const sheet of document.styleSheets) {
                        try {
                            for (const rule of (sheet.cssRules || [])) {
                                if (rule instanceof CSSFontFaceRule) {
                                    fonts.push({
                                        cssText: rule.cssText,
                                        href: sheet.href || 'inline',
                                        fontFamily: rule.style.fontFamily,
                                        src: rule.style.src
                                    });
                                }
                            }
                        } catch (e) {}
                    }
                } catch (e) {}
                return fonts;
            }"""
        )

    def _extract_scripts(self, page) -> List[Dict]:
        return page.evaluate(
            """() =>
                Array.from(document.scripts).map(script => ({
                    src: script.src || 'inline',
                    async: script.async,
                    defer: script.defer,
                    type: script.type || 'text/javascript'
                }))"""
        )

    def _extract_metadata(self, page) -> Dict:
        return page.evaluate(
            """() => ({
                title: document.title,
                description: document.querySelector('meta[name="description"]')?.content || '',
                keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                viewport: document.querySelector('meta[name="viewport"]')?.content || '',
                url: window.location.href,
                language: document.documentElement.lang,
                charset: document.characterSet
            })"""
        )
