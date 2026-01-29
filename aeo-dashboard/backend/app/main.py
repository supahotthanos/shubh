from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import (
    clients,
    prompts,
    citations,
    keywords,
    content,
    campaigns,
    competitors,
    reports,
    dashboard,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AEO/GEO Dashboard API - AI Citation Tracking and Optimization",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router, prefix=f"{settings.API_PREFIX}/dashboard", tags=["Dashboard"])
app.include_router(clients.router, prefix=f"{settings.API_PREFIX}/clients", tags=["Clients"])
app.include_router(prompts.router, prefix=f"{settings.API_PREFIX}/prompts", tags=["Prompts"])
app.include_router(citations.router, prefix=f"{settings.API_PREFIX}/citations", tags=["Citations"])
app.include_router(keywords.router, prefix=f"{settings.API_PREFIX}/keywords", tags=["Keywords & RRF"])
app.include_router(content.router, prefix=f"{settings.API_PREFIX}/content", tags=["Content & Freshness"])
app.include_router(campaigns.router, prefix=f"{settings.API_PREFIX}/campaigns", tags=["Campaigns"])
app.include_router(competitors.router, prefix=f"{settings.API_PREFIX}/competitors", tags=["Competitors"])
app.include_router(reports.router, prefix=f"{settings.API_PREFIX}/reports", tags=["Reports"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
