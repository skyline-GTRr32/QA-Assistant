#!/usr/bin/env python3
"""Check and install Playwright browsers if needed (for Railway deployment)"""
import os
import subprocess
import sys

def check_playwright():
    """Check if Playwright browsers are installed, install if missing"""
    try:
        from playwright.sync_api import sync_playwright
        
        # Set browser path if not set
        if not os.environ.get('PLAYWRIGHT_BROWSERS_PATH'):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/app/.playwright'
        
        # Try to launch browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        print("✓ Playwright browsers are installed and working")
        return True
    except Exception as e:
        print(f"⚠ Playwright browsers not found: {e}")
        print("Installing Playwright browsers...")
        try:
            subprocess.run(
                ["playwright", "install", "chromium"],
                check=True,
                capture_output=True
            )
            print("✓ Playwright browsers installed successfully")
            return True
        except subprocess.CalledProcessError as install_error:
            print(f"✗ Failed to install Playwright browsers: {install_error}")
            return False

if __name__ == "__main__":
    success = check_playwright()
    sys.exit(0 if success else 1)

