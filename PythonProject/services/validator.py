"""
Main Validation Service
------------------------
Orchestrates the complete validation workflow

WORKFLOW:
1. Process user input (Gemini)
2. Search for competitors (Serper)
3. Search for existing solutions (Serper)
4. Search for market data (Serper)
5. Scrape competitor websites (Firecrawl)
6. Analyze competitors (Gemini)
7. Generate validation summary (Gemini)
8. Return complete report
"""

from typing import Dict, Any
from models import IdeaInput, ValidationReport, WebResearchData
from services.gemini_service import GeminiService
from services.serper_service import SerperService
from services.firecrawl_service import FirecrawlService

class ValidationService:
    """
    Main service that coordinates all validation steps
    """
    
    def __init__(self):
        # Initialize all service dependencies
        self.gemini = GeminiService()
        self.serper = SerperService()
        self.firecrawl = FirecrawlService()
    
    async def validate_idea(self, user_input: IdeaInput) -> ValidationReport:
        """
        Complete validation workflow
        
        This is the main function that runs everything!
        
        Args:
            user_input: Raw form data from user
        
        Returns:
            ValidationReport: Complete validation report
        """
        
        print("\n" + "="*60)
        print("🚀 STARTING VALIDATION WORKFLOW")
        print("="*60 + "\n")
        
        # ========================================
        # STEP 1: Process User Input with AI
        # ========================================
        print("📝 STEP 1: Processing user input with Gemini AI...")
        processed_input = await self.gemini.process_user_input(user_input)
        print(f"   ✅ Processed idea: {processed_input.idea_name}\n")
        
        # ========================================
        # STEP 2: Web Research Phase
        # ========================================
        print("🔍 STEP 2: Conducting web research...")
        
        # 2a. Search for competitors
        print("   → Searching for competitors...")
        competitor_results = await self.serper.search_competitors(
            user_input.idea_name,
            user_input.market
        )
        print(f"   ✅ Found {len(competitor_results)} competitor results")
        
        # 2b. Search for existing solutions
        print("   → Searching for existing solutions...")
        solution_results = await self.serper.search_existing_solutions(
            user_input.problem,
            user_input.market
        )
        print(f"   ✅ Found {len(solution_results)} solution results")
        
        # 2c. Search for market size and data
        print("   → Searching for market data...")
        market_results = await self.serper.search_market_size(
            user_input.market,
            user_input.region
        )
        print(f"   ✅ Found {len(market_results)} market insights\n")
        
        # Combine all search results
        all_serper_results = competitor_results + solution_results + market_results
        
        # ========================================
        # STEP 3: Scrape Competitor Websites
        # ========================================
        print("🌐 STEP 3: Scraping competitor websites...")
        
        # Extract URLs from search results (top 5)
        competitor_urls = [
            r["link"] for r in competitor_results[:5] 
            if r.get("link") and r["link"].startswith("http")
        ]
        
        if competitor_urls:
            print(f"   → Scraping {len(competitor_urls)} websites...")
            firecrawl_results = await self.firecrawl.scrape_multiple(competitor_urls)
            successful_scrapes = len([r for r in firecrawl_results if r.get("success")])
            print(f"   ✅ Successfully scraped {successful_scrapes}/{len(competitor_urls)} sites\n")
        else:
            print("   ⚠️ No competitor URLs found to scrape\n")
            firecrawl_results = []
        
        # ========================================
        # STEP 4: Analyze Competitors with AI
        # ========================================
        print("🤖 STEP 4: Analyzing competitors with Gemini AI...")
        competitors = await self.gemini.analyze_competitors(
            all_serper_results,
            firecrawl_results
        )
        print(f"   ✅ Identified {len(competitors)} competitors\n")
        
        # ========================================
        # STEP 5: Generate Validation Summary
        # ========================================
        print("📊 STEP 5: Generating validation summary with Gemini AI...")
        validation_summary = await self.gemini.generate_validation_summary(
            processed_input,
            competitors,
            market_results
        )
        print(f"   ✅ Feasibility Score: {validation_summary.feasibility_score}/100")
        print(f"   ✅ Market Readiness: {validation_summary.market_readiness_score}/100\n")
        
        # ========================================
        # STEP 6: Package Everything Together
        # ========================================
        print("📦 STEP 6: Packaging final report...")
        
        # Create web research data object
        web_research = WebResearchData(
            serper_results=all_serper_results,
            firecrawl_results=firecrawl_results,
            competitors=competitors,
            market_insights={
                "total_searches": len(all_serper_results),
                "competitor_count": len(competitors),
                "websites_scraped": len([r for r in firecrawl_results if r.get("success")]),
                "market_data_sources": len(market_results)
            }
        )
        
        # Create final validation report
        validation_report = ValidationReport(
            user_input=user_input,
            processed_input=processed_input,
            web_research=web_research,
            final_summary=validation_summary
        )
        
        print("   ✅ Report ready!\n")
        print("="*60)
        print("✨ VALIDATION COMPLETE!")
        print("="*60 + "\n")
        
        return validation_report