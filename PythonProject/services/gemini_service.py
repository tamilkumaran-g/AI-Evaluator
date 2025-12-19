"""
Gemini AI Service
-----------------
Handles all AI analysis using Google Gemini API

Gemini is used for:
1. Processing raw user input into structured format
2. Analyzing competitors from web data
3. Generating comprehensive validation summary with SWOT, scores, recommendations
"""

import google.generativeai as genai
from typing import Dict, Any, List
import json
from config import get_settings
from models import IdeaInput, ProcessedInput, CompetitorInfo, ValidationSummary

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

class GeminiService:
    """
    Service for AI analysis using Google Gemini
    """
    
    def __init__(self):
        # Using Gemini 1.5 Flash for fast responses
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def process_user_input(self, user_input: IdeaInput) -> ProcessedInput:
        """
        STEP 1: Convert raw form input to clean, structured format
        
        What it does:
        - Takes messy user input
        - Cleans and organizes it
        - Returns structured data ready for analysis
        
        Args:
            user_input: Raw form data from frontend
        
        Returns:
            ProcessedInput: Clean, structured data
        """
        prompt = f"""
You are a startup analysis expert. Convert this user input into clean, structured format.

User Input:
- Idea Name: {user_input.idea_name}
- Problem: {user_input.problem}
- Why Problem Exists: {user_input.why_problem_exists}
- Target Audience: {user_input.target_audience}
- Solution: {user_input.solution}
- Key Features: {user_input.key_features}
- Uniqueness: {user_input.uniqueness}
- Market/Industry: {user_input.market}
- Revenue Model: {user_input.revenue_model}
- Expected Users: {user_input.expected_users}
- Region: {user_input.region}
- Extra Notes: {user_input.extra_notes}

Return ONLY a JSON object (no markdown, no explanation):
{{
  "idea_name": "clean concise name",
  "problem": "clearly stated problem",
  "solution": "proposed solution",
  "target_audience": "specific target audience",
  "uniqueness": "unique value proposition",
  "market": "market/industry",
  "revenue_model": "revenue model",
  "region": "geographic region",
  "additional_context": "synthesized context from all fields"
}}
"""
        
        response = await self._generate_content(prompt)
        return self._parse_json_response(response, ProcessedInput, user_input)
    
    async def analyze_competitors(
        self, 
        search_results: List[Dict[str, Any]], 
        scraped_data: List[Dict[str, Any]]
    ) -> List[CompetitorInfo]:
        """
        STEP 2: Analyze competitors from search and scraped data
        
        What it does:
        - Takes search results and scraped websites
        - Identifies actual competitors
        - Extracts: name, URL, description, founders, revenue, features
        
        Args:
            search_results: Results from Serper API
            scraped_data: Scraped website content from Firecrawl
        
        Returns:
            List of CompetitorInfo objects
        """
        prompt = f"""
Analyze this data and extract ONLY real competitor companies (not articles or blogs).

Search Results:
{json.dumps(search_results[:10], indent=2)}

Scraped Websites:
{json.dumps(scraped_data[:5], indent=2)}

Return ONLY a JSON array (no markdown, no explanation):
[
  {{
    "name": "Company Name",
    "url": "website url or empty string",
    "description": "what they do in 1-2 sentences",
    "founders": "founder names or Unknown",
    "revenue": "revenue info or Unknown",
    "region": "operating region or Unknown",
    "features": ["feature 1", "feature 2", "feature 3"]
  }}
]

Extract maximum 10 real competitors. If info is missing, use "Unknown".
"""
        
        response = await self._generate_content(prompt)
        return self._parse_competitor_response(response)
    
    async def generate_validation_summary(
        self, 
        processed_input: ProcessedInput,
        competitors: List[CompetitorInfo],
        market_data: List[Dict[str, Any]]
    ) -> ValidationSummary:
        """
        STEP 3: Generate comprehensive validation summary
        
        What it does:
        - Analyzes the idea against competitors and market
        - Generates SWOT analysis
        - Calculates feasibility and market readiness scores
        - Provides actionable recommendations
        
        Args:
            processed_input: Cleaned startup idea data
            competitors: List of identified competitors
            market_data: Market research from Serper
        
        Returns:
            ValidationSummary with complete analysis
        """
        prompt = f"""
You are a startup validation expert with 20 years experience. Analyze this idea thoroughly.

STARTUP IDEA:
{json.dumps(processed_input.model_dump(), indent=2)}

COMPETITORS:
{json.dumps([c.model_dump() for c in competitors], indent=2)}

MARKET DATA:
{json.dumps(market_data[:5], indent=2)}

Provide a detailed, honest analysis. Return ONLY a JSON object (no markdown):
{{
  "overview": "2-3 paragraph executive summary covering: the idea, market potential, competitive landscape",
  "feasibility_score": <integer 1-100, be realistic>,
  "market_readiness_score": <integer 1-100, be realistic>,
  "swot_analysis": {{
    "strengths": ["strength 1", "strength 2", "strength 3", "strength 4"],
    "weaknesses": ["weakness 1", "weakness 2", "weakness 3", "weakness 4"],
    "opportunities": ["opportunity 1", "opportunity 2", "opportunity 3", "opportunity 4"],
    "threats": ["threat 1", "threat 2", "threat 3", "threat 4"]
  }},
  "risk_analysis": ["risk 1 with impact", "risk 2 with impact", "risk 3 with impact", "risk 4 with impact", "risk 5 with impact"],
  "recommendations": ["actionable recommendation 1", "recommendation 2", "recommendation 3", "recommendation 4", "recommendation 5"],
  "competitive_advantage": "detailed paragraph on how to differentiate and win",
  "market_size_estimate": "estimated TAM/SAM/SOM with reasoning"
}}

Be thorough, specific, and actionable. Consider current market trends.
"""
        
        response = await self._generate_content(prompt)
        return self._parse_validation_response(response)
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    async def _generate_content(self, prompt: str) -> str:
        """
        Call Gemini API
        
        Args:
            prompt: The prompt to send to Gemini
        
        Returns:
            Generated text response
        """
        try:
            print("🤖 Calling Gemini AI...")
            response = self.model.generate_content(prompt)
            print("✅ Gemini response received")
            return response.text
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            return "{}"
    
    def _parse_json_response(self, response: str, model_class, fallback_data=None):
        """Parse JSON response and handle errors"""
        try:
            # Clean response (remove markdown code blocks if present)
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            
            data = json.loads(json_str)
            return model_class(**data)
        except Exception as e:
            print(f"⚠️ Error parsing response: {e}")
            # Return fallback
            if model_class == ProcessedInput and fallback_data:
                return ProcessedInput(
                    idea_name=fallback_data.idea_name,
                    problem=fallback_data.problem,
                    solution=fallback_data.solution,
                    target_audience=fallback_data.target_audience,
                    uniqueness=fallback_data.uniqueness,
                    market=fallback_data.market,
                    revenue_model=fallback_data.revenue_model,
                    region=fallback_data.region,
                    additional_context=f"{fallback_data.why_problem_exists} {fallback_data.key_features}"
                )
            return None
    
    def _parse_competitor_response(self, response: str) -> List[CompetitorInfo]:
        """Parse competitor JSON array"""
        try:
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            
            data = json.loads(json_str)
            return [CompetitorInfo(**comp) for comp in data]
        except Exception as e:
            print(f"⚠️ Error parsing competitors: {e}")
            return []
    
    def _parse_validation_response(self, response: str) -> ValidationSummary:
        """Parse validation summary"""
        try:
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            
            data = json.loads(json_str)
            return ValidationSummary(**data)
        except Exception as e:
            print(f"⚠️ Error parsing validation: {e}")
            # Return default
            return ValidationSummary(
                overview="Analysis could not be completed. Please try again.",
                feasibility_score=50,
                market_readiness_score=50,
                swot_analysis={
                    "strengths": ["Unable to analyze"],
                    "weaknesses": ["Unable to analyze"],
                    "opportunities": ["Unable to analyze"],
                    "threats": ["Unable to analyze"]
                },
                risk_analysis=["Unable to analyze risks"],
                recommendations=["Please try validation again"],
                competitive_advantage="Unable to analyze",
                market_size_estimate="Unable to estimate"
            )