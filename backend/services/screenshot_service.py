
import os
import re # Import the regular expression module
from pathlib import Path
from typing import List, Dict
from playwright.sync_api import sync_playwright

class ScreenshotService:
    def capture_issues(self, url: str, report: Dict, run_dir: Path) -> Dict:
        """
        Takes screenshots of specific issues identified in the analysis report.
        It cleans CSS selectors to handle pseudo-states like :hover before capturing.

        Args:
            url: The website URL to take screenshots from.
            report: The analysis report from the WebsiteAnalyzerAgent.
            run_dir: The directory to save screenshots into.

        Returns:
            The updated report with screenshot paths added to the issues.
        """
        screenshots_dir = run_dir / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        issues_to_screenshot = []
        for category in report.values():
            if isinstance(category, dict) and "issues" in category and category["issues"]:
                for issue in category["issues"]:
                    if issue and issue.get("selector"):
                        issues_to_screenshot.append(issue)

        if not issues_to_screenshot:
            print("No issues with selectors found to screenshot.")
            return report

        print(f"Found {len(issues_to_screenshot)} issues to screenshot. Starting browser...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
                
                for i, issue in enumerate(issues_to_screenshot):
                    original_selector = issue.get("selector")
                    screenshot_filename = f"issue_{i+1}.png"
                    screenshot_path = screenshots_dir / screenshot_filename
                    
                    # --- FIX IMPLEMENTED HERE ---
                    # Clean the selector by removing pseudo-classes that Playwright cannot handle directly.
                    # This prevents timeouts on selectors like '.button:hover'.
                    clean_selector = re.sub(r':hover|:focus|:active|::before|::after', '', original_selector).strip()
                    
                    # Skip invalid selectors early
                    if not clean_selector or clean_selector.lower() in ["not available", "n/a", "null", "none", ""]:
                        print(f"  ✗ Selector '{original_selector}' is invalid, skipping screenshot.")
                        issue["screenshot_error"] = f"Invalid selector: {original_selector}"
                        continue
                    
                    # Fix selector format - add . for classes, # for IDs if missing
                    if clean_selector and not clean_selector.startswith(('.', '#', '[', 'body', 'html', '/')):
                        # If it looks like a class name (contains dash or is alphanumeric), add .
                        if '-' in clean_selector or clean_selector.replace('-', '').isalnum():
                            clean_selector = f'.{clean_selector}'

                    try:
                        element = page.locator(clean_selector).first
                        element.wait_for(state="visible", timeout=5000)
                        
                        element.scroll_into_view_if_needed()
                        element.evaluate("el => el.style.boxShadow = '0 0 0 3px red'") # More visible highlight
                        element.screenshot(path=str(screenshot_path))
                        element.evaluate("el => el.style.boxShadow = ''")
                        
                        issue["screenshot"] = f"screenshots/{screenshot_filename}"
                        print(f"  ✓ Screenshot saved for selector: '{original_selector}' (captured as '{clean_selector}')")
                    except Exception as e:
                        error_message = str(e).split('\n')[0] # Get a concise error message
                        issue["screenshot_error"] = f"Could not capture element: {error_message}"
                        print(f"  ✗ Failed to screenshot selector '{original_selector}': {error_message}")

            except Exception as e:
                print(f"An error occurred during screenshot process: {e}")
            finally:
                browser.close()
                
        return report