"""
Firecrawl API Service
----------------------
Handles website scraping using Firecrawl API
Firecrawl can scrape websites and extract clean content

How it works:
1. Takes a website URL
2. Calls Firecrawl API
3. Returns clean markdown content, title, description
"""

import httpx
from typing import Dict, Any, List
from config import get_settings

settings = get_settings()

class FirecrawlService:
    """
    Service for scraping websites using Firecrawl API
    """
    
    def __init__(self):
        self.api_key = settings.firecrawl_api_key
        self.base_url = "https://api.firecrawl.dev/v0"
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single website URL
        
        Args:
            url: Website URL to scrape
        
        Returns:
            Dictionary containing:
            - url: Original URL
            - title: Page title
            - description: Meta description
            - content: Main content (markdown format)
            - success: Whether scraping succeeded
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url,
            "formats": ["markdown", "html"],
            "onlyMainContent": True  # Extract only main content, ignore headers/footers
        }
        
        try:
            print(f"🌐 Scraping: {url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/scrape",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract relevant data
                result = {
                    "url": url,
                    "title": data.get("data", {}).get("metadata", {}).get("title", ""),
                    "description": data.get("data", {}).get("metadata", {}).get("description", ""),
                    "content": data.get("data", {}).get("markdown", "")[:5000],  # Limit to 5000 chars
                    "success": True
                }
                
                print(f"✅ Scraped successfully")
                return result
                
        except Exception as e:
            print(f"❌ Firecrawl error for {url}: {str(e)}")
            return {
                "url": url,
                "title": "",
                "description": "",
                "content": "",
                "success": False,
                "error": str(e)
            }
    
    async def scrape_multiple(self, urls: List[str], max_urls: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs
        
        Args:
            urls: List of URLs to scrape
            max_urls: Maximum number of URLs to scrape (default: 5)
        
        Returns:
            List of scrape results
        """
        results = []
        
        # Limit to max_urls to avoid timeout and rate limits
        for url in urls[:max_urls]:
            result = await self.scrape_url(url)
            results.append(result)
        
        successful = len([r for r in results if r.get("success")])
        print(f"📊 Scraped {successful}/{len(results)} websites successfully")
        
        return results
    
    async def extract_competitor_info(self, url: str) -> Dict[str, Any]:
        """
        Extract specific competitor information from website
        
        Args:
            url: Competitor website URL
        
        Returns:
            Extracted information about the competitor
        """
        scraped_data = await self.scrape_url(url)
        
        if not scraped_data.get("success"):
            return {
                "url": url,
                "extracted": False,
                "error": scraped_data.get("error", "Unknown error")
            }
        
        return {
            "url": url,
            "title": scraped_data.get("title", ""),
            "description": scraped_data.get("description", ""),
            "content_preview": scraped_data.get("content", "")[:1000],  # First 1000 chars
            "extracted": True
        }