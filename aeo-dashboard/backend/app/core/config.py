from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AEO Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/aeo_dashboard"
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    BRIGHTDATA_API_KEY: Optional[str] = None
    AHREFS_API_KEY: Optional[str] = None
    SEMRUSH_API_KEY: Optional[str] = None

    # Google APIs
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GSC_CREDENTIALS_PATH: Optional[str] = None

    # Scraping Configuration
    SCRAPE_CONCURRENCY: int = 5
    SCRAPE_RATE_LIMIT: int = 10  # requests per minute
    SCRAPE_RETRY_ATTEMPTS: int = 3

    # RRF Configuration
    RRF_K_CONSTANT: float = 60.0
    RRF_THRESHOLD: float = 0.020

    # Freshness Scoring
    FRESHNESS_DECAY_DAYS: int = 180  # 6 months

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
