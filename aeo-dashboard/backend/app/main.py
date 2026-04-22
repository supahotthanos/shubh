from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.deps import get_current_user
from app.api.routes import (
    auth,
    authority,
    campaigns,
    citations,
    clients,
    competitors,
    content,
    dashboard,
    keywords,
    prompts,
    reports,
)
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # `init_db` is idempotent; useful for fresh dev envs but production should
    # use Alembic. See `alembic upgrade head`.
    try:
        await init_db()
    except Exception:
        # Alembic has already created the schema — don't block startup.
        pass
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AEO/GEO Dashboard API — AI Citation Tracking and Optimization",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth is unauthenticated.
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Auth"])

# Every other route requires a valid JWT.
_auth = [Depends(get_current_user)]
app.include_router(dashboard.router, prefix=f"{settings.API_PREFIX}/dashboard", tags=["Dashboard"], dependencies=_auth)
app.include_router(clients.router, prefix=f"{settings.API_PREFIX}/clients", tags=["Clients"], dependencies=_auth)
app.include_router(prompts.router, prefix=f"{settings.API_PREFIX}/prompts", tags=["Prompts"], dependencies=_auth)
app.include_router(citations.router, prefix=f"{settings.API_PREFIX}/citations", tags=["Citations"], dependencies=_auth)
app.include_router(keywords.router, prefix=f"{settings.API_PREFIX}/keywords", tags=["Keywords & RRF"], dependencies=_auth)
app.include_router(content.router, prefix=f"{settings.API_PREFIX}/content", tags=["Content & Freshness"], dependencies=_auth)
app.include_router(campaigns.router, prefix=f"{settings.API_PREFIX}/campaigns", tags=["Campaigns"], dependencies=_auth)
app.include_router(competitors.router, prefix=f"{settings.API_PREFIX}/competitors", tags=["Competitors"], dependencies=_auth)
app.include_router(authority.router, prefix=f"{settings.API_PREFIX}/authority", tags=["Authority"], dependencies=_auth)
app.include_router(reports.router, prefix=f"{settings.API_PREFIX}/reports", tags=["Reports"], dependencies=_auth)


@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
