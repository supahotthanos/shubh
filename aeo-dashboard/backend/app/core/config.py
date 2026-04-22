from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AEO Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development | staging | production

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/aeo_dashboard"
    DATABASE_ECHO: bool = False
    # Sync URL is derived in alembic/env.py for migrations.

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL_SECONDS: int = 300

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # Demo credentials (seed script uses these)
    DEMO_ORG_SLUG: str = "demo"
    DEMO_ORG_NAME: str = "Demo Agency"
    DEMO_USER_EMAIL: str = "demo@aeo.local"
    DEMO_USER_PASSWORD: str = "demo1234"
    DEMO_USER_NAME: str = "Demo Admin"

    # Provider mode: mock | real | auto (auto picks real when key present, else mock)
    PROVIDER_MODE: str = "auto"

    # External API keys — when set, the auto factory switches to the real provider.
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    GOOGLE_AI_API_KEY: Optional[str] = None
    BRIGHTDATA_API_KEY: Optional[str] = None
    AHREFS_API_KEY: Optional[str] = None
    MOZ_API_KEY: Optional[str] = None
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

    # Celery
    CELERY_BROKER_URL: Optional[str] = None  # defaults to REDIS_URL
    CELERY_RESULT_BACKEND: Optional[str] = None  # defaults to REDIS_URL
    CELERY_TASK_ALWAYS_EAGER: bool = False  # True in tests

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    @property
    def sync_database_url(self) -> str:
        """Derive a sync URL from the async one for Alembic and scripts."""
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
