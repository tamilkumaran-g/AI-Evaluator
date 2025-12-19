from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any  # Added Dict, Any to fix NameError
from datetime import datetime

# ============================================
# INPUT MODELS (From Frontend Form)
# ============================================

class IdeaInput(BaseModel):
    idea_name: str
    problem: str
    why_problem_exists: str
    target_audience: str
    solution: str
    key_features: str
    uniqueness: str
    market: str
    revenue_model: str
    expected_users: str
    region: str
    extra_notes: Optional[str] = ""

# ============================================
# PROCESSED MODELS
# ============================================

class ProcessedInput(BaseModel):
    idea_name: str
    problem: str
    solution: str
    target_audience: str
    uniqueness: str
    market: str
    revenue_model: str
    region: str
    additional_context: str

# ============================================
# COMPETITOR ANALYSIS MODELS
# ============================================

class CompetitorInfo(BaseModel):
    name: str
    url: Optional[str] = ""
    description: str
    founders: Optional[str] = "Unknown"
    revenue: Optional[str] = "Unknown"
    region: Optional[str] = "Unknown"
    features: List[str] = []

# ============================================
# WEB RESEARCH MODELS
# ============================================

class WebResearchData(BaseModel):
    serper_results: List[Dict[str, Any]]     
    firecrawl_results: List[Dict[str, Any]]  
    competitors: List[CompetitorInfo]        
    market_insights: Dict[str, Any] = Field(default_factory=dict) # Added default

# ============================================
# VALIDATION SUMMARY MODELS
# ============================================

class ValidationSummary(BaseModel):
    overview: str
    feasibility_score: int
    market_readiness_score: int
    swot_analysis: Dict[str, List[str]] # More specific type hinting
    risk_analysis: List[str]
    recommendations: List[str]
    competitive_advantage: str
    
    # THE FIX: Default value prevents validation errors if Gemini misses this field
    market_size_estimate: str = Field(
        default="Market size estimation unavailable based on current data."
    )

# ============================================
# COMPLETE VALIDATION REPORT
# ============================================

class ValidationReport(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_input: IdeaInput
    processed_input: ProcessedInput
    web_research: WebResearchData
    final_summary: ValidationSummary
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }