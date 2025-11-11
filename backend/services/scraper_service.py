# backend/services/scraper_service.py
import re
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Any
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from bs4 import BeautifulSoup
import cssutils
import time

# Disable CSS warnings from cssutils
cssutils.log.setLevel('ERROR')


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
            # Create a session with retry strategy
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Set headers to mimic a real browser
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            
            logging.info(f"Fetching {self.url}...")
            response = session.get(self.url, headers=headers, timeout=30, verify=True)
            response.raise_for_status()
            logging.info(f"Page fetched successfully, status: {response.status_code}")

            logging.info("Parsing HTML content...")
            soup = BeautifulSoup(response.text, "html.parser")
            logging.info(f"HTML content parsed, length: {len(str(soup))} characters")

            logging.info("Processing resources (making URLs absolute)...")
            self._process_resources(soup)

            logging.info("Extracting metadata...")
            metadata = self._extract_metadata(soup)

            logging.info("Extracting scripts...")
            scripts = self._extract_scripts(soup)

            logging.info("Extracting styles...")
            styles = self._extract_all_styles(soup, session)

            logging.info("Extracting assets...")
            assets = self._extract_assets(soup)

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

        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP request failed: {e}", exc_info=True)
            return {"success": False, "error": f"Failed to fetch page: {str(e)}"}
        except Exception as e:
            logging.error(f"Scraping failed: {e}", exc_info=True)
            return {"success": False, "error": f"Scraping failed: {str(e)}"}

    # --------------------------------------------------------------------------
    # Helper methods
    # --------------------------------------------------------------------------

    def _fetch_stylesheet(self, session: requests.Session, url: str) -> str:
        """Fetch a stylesheet and return its content."""
        try:
            if not url or url.startswith("data:"):
                return ""
            absolute_url = self._make_absolute(url)
            response = session.get(absolute_url, timeout=10, verify=True)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.warning(f"Failed to fetch stylesheet {url}: {e}")
            return ""

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

    def _extract_all_styles(self, soup: BeautifulSoup, session: requests.Session) -> Dict:
        """Extract all styles from the page."""
        # Extract inline styles from elements
        inline_styles = self._extract_inline_styles(soup)
        
        # Extract external stylesheets
        external_stylesheets = []
        for link in soup.find_all("link", rel="stylesheet"):
            href = link.get("href", "")
            if href:
                external_stylesheets.append({
                    "href": self._make_absolute(href),
                    "media": link.get("media", "all")
                })
        
        # Extract style tags
        style_tags = [str(tag) for tag in soup.find_all("style")]
        
        # Extract CSS rules from all stylesheets
        css_rules = []
        for link in soup.find_all("link", rel="stylesheet"):
            href = link.get("href", "")
            if href:
                css_content = self._fetch_stylesheet(session, href)
                if css_content:
                    css_rules.extend(self._parse_css_rules(css_content, href))
        
        # Also parse style tags
        for style_tag in soup.find_all("style"):
            css_content = style_tag.string or ""
            if css_content:
                css_rules.extend(self._parse_css_rules(css_content, "inline"))
        
        return {
            "inline": inline_styles,
            "external": external_stylesheets,
            "style_tags": style_tags,
            "computed": {},  # Cannot get computed styles without JavaScript
            "css_rules": css_rules,
        }

    def _extract_inline_styles(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract inline styles from elements."""
        inline_styles = []
        for element in soup.find_all(style=True):
            selector = element.name
            if element.get("id"):
                selector += f"#{element.get('id')}"
            if element.get("class"):
                classes = " ".join(element.get("class", []))
                selector += f".{classes.replace(' ', '.')}"
            
            inline_styles.append({
                "selector": selector,
                "styles": element.get("style", "")
            })
        return inline_styles

    def _parse_css_rules(self, css_content: str, source: str) -> List[Dict]:
        """Parse CSS rules from CSS content."""
        rules = []
        try:
            sheet = cssutils.parseString(css_content)
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    rules.append({
                        "selector": rule.selectorText,
                        "cssText": rule.cssText,
                        "href": source
                    })
        except Exception as e:
            logging.warning(f"Failed to parse CSS from {source}: {e}")
        return rules

    def _extract_assets(self, soup: BeautifulSoup) -> Dict:
        """Extract assets from the page."""
        return {
            "images": self._extract_assets_by_type(soup, "img", "src"),
            "background_images": self._extract_background_images(soup),
            "fonts": self._extract_fonts(soup),
        }

    def _extract_assets_by_type(self, soup: BeautifulSoup, tag: str, attr: str) -> List[Dict]:
        """Extract assets by tag type."""
        assets = []
        for element in soup.find_all(tag):
            src = element.get(attr, "")
            if src:
                assets.append({
                    "src": self._make_absolute(src),
                    "alt": element.get("alt", "")
                })
        return assets

    def _extract_background_images(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract background images from inline styles and CSS."""
        bg_images = []
        
        # Extract from inline styles
        for element in soup.find_all(style=True):
            style = element.get("style", "")
            urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', style)
            for url in urls:
                if url and not url.startswith("data:"):
                    bg_images.append({
                        "src": self._make_absolute(url),
                        "element": element.name or "",
                        "class": " ".join(element.get("class", [])),
                        "id": element.get("id", "")
                    })
        
        # Extract from style tags (basic regex matching)
        for style_tag in soup.find_all("style"):
            css_content = style_tag.string or ""
            urls = re.findall(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', css_content, re.IGNORECASE)
            for url in urls:
                if url and not url.startswith("data:"):
                    bg_images.append({
                        "src": self._make_absolute(url),
                        "element": "",
                        "class": "",
                        "id": ""
                    })
        
        return bg_images

    def _extract_fonts(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract font-face rules from CSS."""
        fonts = []
        
        # Extract from style tags
        for style_tag in soup.find_all("style"):
            css_content = style_tag.string or ""
            if css_content:
                try:
                    sheet = cssutils.parseString(css_content)
                    for rule in sheet:
                        if rule.type == rule.FONT_FACE_RULE:
                            fonts.append({
                                "cssText": rule.cssText,
                                "href": "inline",
                                "fontFamily": rule.style.getPropertyValue("font-family") or "",
                                "src": rule.style.getPropertyValue("src") or ""
                            })
                except Exception as e:
                    logging.warning(f"Failed to parse fonts from style tag: {e}")
        
        return fonts

    def _extract_scripts(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract script tags from the page."""
        scripts = []
        for script in soup.find_all("script"):
            scripts.append({
                "src": self._make_absolute(script.get("src", "")) if script.get("src") else "inline",
                "async": script.get("async") is not None,
                "defer": script.get("defer") is not None,
                "type": script.get("type", "text/javascript")
            })
        return scripts

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from the page."""
        title_tag = soup.find("title")
        title = title_tag.string if title_tag else ""
        
        description_meta = soup.find("meta", attrs={"name": "description"})
        description = description_meta.get("content", "") if description_meta else ""
        
        keywords_meta = soup.find("meta", attrs={"name": "keywords"})
        keywords = keywords_meta.get("content", "") if keywords_meta else ""
        
        viewport_meta = soup.find("meta", attrs={"name": "viewport"})
        viewport = viewport_meta.get("content", "") if viewport_meta else ""
        
        html_tag = soup.find("html")
        language = html_tag.get("lang", "") if html_tag else ""
        
        charset_meta = soup.find("meta", attrs={"charset": True})
        charset = charset_meta.get("charset", "") if charset_meta else ""
        if not charset:
            charset_meta = soup.find("meta", attrs={"http-equiv": "Content-Type"})
            if charset_meta:
                content = charset_meta.get("content", "")
                charset_match = re.search(r'charset=([^;]+)', content)
                charset = charset_match.group(1) if charset_match else ""
        
        return {
            "title": title,
            "description": description,
            "keywords": keywords,
            "viewport": viewport,
            "url": self.url,
            "language": language,
            "charset": charset
        }
