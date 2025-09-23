# Web crawler for sitemap and web content ingestion (optional)

from typing import List, Dict, Optional
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path

class WebCrawler:
    """
    Simple web crawler for ingesting web content.
    Can crawl sitemaps or individual URLs.
    """
    
    def __init__(self, user_agent: str = "Vectorpenter/1.0"):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
    
    def crawl_sitemap(self, sitemap_url: str) -> List[Dict]:
        """
        Crawl a sitemap and extract URLs for content ingestion.
        """
        try:
            response = self.session.get(sitemap_url)
            response.raise_for_status()
            # TODO: Parse XML sitemap and extract URLs
            # This is a placeholder implementation
            return []
        except Exception as e:
            print(f"Error crawling sitemap {sitemap_url}: {e}")
            return []
    
    def fetch_page(self, url: str) -> Optional[Dict]:
        """
        Fetch a single web page and extract text content.
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Basic text extraction (could be enhanced with BeautifulSoup)
            content = response.text
            
            return {
                "url": url,
                "title": self._extract_title(content),
                "content": self._extract_text(content),
                "metadata": {
                    "source": "web",
                    "url": url,
                    "status_code": response.status_code
                }
            }
        except Exception as e:
            print(f"Error fetching page {url}: {e}")
            return None
    
    def _extract_title(self, html: str) -> str:
        """Extract title from HTML content."""
        # Simple title extraction
        import re
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _extract_text(self, html: str) -> str:
        """Extract text content from HTML."""
        # TODO: Implement proper HTML text extraction
        # This is a placeholder - would benefit from BeautifulSoup
        import re
        # Remove script and style elements
        html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL)
        # Remove HTML tags
        html = re.sub(r'<.*?>', '', html)
        # Clean up whitespace
        html = re.sub(r'\s+', ' ', html).strip()
        return html
