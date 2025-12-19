"""
Configuration Management
------------------------
Loads environment variables and provides centralized config
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    gemini_api_key: str
    serper_api_key: str
    firecrawl_api_key: str
    
    # Server Configuration
    port: int = 8000
    host: str = "127.0.0.1"
    
    # API Timeouts
    api_timeout: int = 60
    
    # Search Configuration
    max_search_results: int = 10
    max_scrape_urls: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
