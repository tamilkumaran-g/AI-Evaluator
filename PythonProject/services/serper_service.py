"""
Serper API Service
------------------
Handles web searches using Serper API
Serper provides Google search results via API

How it works:
1. Takes a search query
2. Calls Serper API
3. Returns top search results with title, link, snippet
"""

import httpx
from typing import List, Dict, Any
from config import get_settings

settings = get_settings()

class SerperService:
    """
    Service for web searches using Serper API
    """
    
    def __init__(self):
        self.api_key = settings.serper_api_key
        self.base_url = "https://google.serper.dev/search"
    
    async def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a web search
        
        Args:
            query: Search query string
            num_results: Number of results to return (default: 10)
        
        Returns:
            List of search results with title, link, snippet
        """
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": num_results
        }
        
        try:
            print(f"🔍 Searching: {query}")
            
            async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
                response = await client.post(
                    self.base_url, 
                    json=payload, 
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract organic search results
                results = []
                if "organic" in data:
                    for item in data["organic"]:
                        results.append({
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "position": item.get("position", 0)
                        })
                
                print(f"✅ Found {len(results)} results")
                return results
                
        except Exception as e:
            print(f"❌ Serper search error: {str(e)}")
            return []
    
    async def search_competitors(self, idea_name: str, market: str) -> List[Dict[str, Any]]:
        """
        Search for competitors in the market
        
        Example query: "meal planning app competitors health wellness startups"
        """
        query = f"{idea_name} competitors {market} startups"
        return await self.search(query, num_results=10)
    
    async def search_market_size(self, market: str, region: str) -> List[Dict[str, Any]]:
        """
        Search for market size information
        
        Example query: "health wellness market size United States statistics"
        """
        query = f"{market} market size {region} statistics revenue"
        return await self.search(query, num_results=5)
    
    async def search_existing_solutions(self, problem: str, market: str) -> List[Dict[str, Any]]:
        """
        Search for existing solutions to the problem
        
        Example query: "healthy eating planning solutions health wellness apps"
        """
        query = f"{problem} solutions {market} apps platforms tools"
        return await self.search(query, num_results=10)
    
    async def search_founders_info(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search for founder and company information
        
        Example query: "MyFitnessPal founders CEO revenue funding"
        """
        query = f"{company_name} founders CEO revenue funding"
        return await self.search(query, num_results=5)