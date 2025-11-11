# backend/services/performance_service.py
import os
import requests
from typing import Dict

class PerformanceService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        self.api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def analyze(self, url: str) -> Dict:
        """
        Analyzes a URL using Google PageSpeed Insights API.
        """
        params = {
            'url': url,
            'key': self.api_key,
            'strategy': 'DESKTOP',  # Can also be 'MOBILE'
            'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES', 'SEO']
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract key metrics
            metrics = {
                'performance_score': data['lighthouseResult']['categories']['performance']['score'] * 100,
                'accessibility_score': data['lighthouseResult']['categories']['accessibility']['score'] * 100,
                'best_practices_score': data['lighthouseResult']['categories']['best-practices']['score'] * 100,
                'seo_score': data['lighthouseResult']['categories']['seo']['score'] * 100,
                'first_contentful_paint': data['lighthouseResult']['audits']['first-contentful-paint']['displayValue'],
                'largest_contentful_paint': data['lighthouseResult']['audits']['largest-contentful-paint']['displayValue'],
                'speed_index': data['lighthouseResult']['audits']['speed-index']['displayValue'],
            }
            return {"success": True, "metrics": metrics}
        except requests.exceptions.RequestException as e:
            print(f"Error calling PageSpeed Insights API: {e}")
            return {"success": False, "error": str(e)}