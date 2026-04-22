# AEO/GEO Dashboard

Answer-Engine / Generative-Engine Optimization platform for tracking and optimizing AI citations across ChatGPT, Perplexity, Claude, Google AI Overviews, Gemini, Grok, and Bing Copilot.

## Features (all 8 modules wired end-to-end)

1. **AI Citation Tracking Center** — citations table, filter chips, platform breakdown, live stability scoring.
2. **RRF Score Calculator** — Reciprocal Rank Fusion (k=60, τ=0.020), quick-reference table, simulator, per-keyword recommendations.
3. **Authority Signals** — Common Crawl HC/PageRank, Ahrefs DR, Moz DA, Wikipedia citation check, platform-dilution warnings.
4. **Content Freshness** — A–F grades, model-specific cadence (GPT / LLaMA / Gemini / Qwen), re-analyze on demand.
5. **GSC → AI Prompt Intelligence** — Google Search Console import with intent detection, clustering, and conversational rewriting.
6. **Campaigns** — 7 campaign types (listicle, guest post, PR, research report, thought leadership, community, publish) with asset lifecycle (pending → live → indexed → cited).
7. **Competitive Intelligence** — share-of-voice donut, citations-by-competitor bar chart, citation overlap, authority comparison.
8. **Client Reporting** — on-demand + scheduled weekly/monthly reports, PDF (WeasyPrint) and CSV export, Slides outline.

## Architecture

**Backend**: FastAPI + SQLAlchemy 2.0 async + PostgreSQL 15 + Alembic + Celery + Redis.

**Frontend**: Next.js 14 (App Router) + Tailwind + Recharts + TanStack Query + Zustand + Sonner (toasts).

External integrations (OpenAI, Anthropic, Perplexity, Google Gemini, GSC, Ahrefs, Moz, Wikipedia) are behind a **provider pattern**: the app always uses deterministic **mock providers** until you set the matching `*_API_KEY` env var, at which point the factory swaps in the real implementation. This means the whole app is usable end-to-end without any external accounts.

## Quick start

Everything runs via Docker Compose:

```bash
docker compose up
```

This will bring up Postgres, Redis, the FastAPI backend (with Alembic migrations + seed on first boot), Celery worker + beat, and the Next.js frontend.

Then:
- Open `http://localhost:3000/login`
- Log in with `demo@aeo.local` / `demo1234`
- Click through each sidebar route — every page shows real, seeded data.

Swagger UI lives at `http://localhost:8000/docs`.

## Local (non-Docker) setup

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # edit if needed
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
# separate shells for workers
celery -A app.core.celery_app worker --loglevel=info
celery -A app.core.celery_app beat --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Make targets

```bash
make bootstrap   # Postgres + Redis via docker compose
make migrate     # alembic upgrade head
make seed        # populate demo data
make dev         # full stack
make test        # backend pytest
make lint        # frontend next lint
```

## Tests

```bash
cd backend && pytest -q
```

Covers: RRF math, freshness scoring, password/JWT round-trips, mock provider determinism.

## Configuration

All settings are environment variables (see `backend/.env.example`). The important ones:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Postgres (async) URL |
| `REDIS_URL` | Celery broker + cache |
| `SECRET_KEY` | JWT signing key (change in prod) |
| `PROVIDER_MODE` | `mock` / `real` / `auto` (default: auto — uses real when the matching key is set) |
| `OPENAI_API_KEY` | Enables real OpenAI citation checking |
| `ANTHROPIC_API_KEY` | Enables real Claude citation checking |
| `PERPLEXITY_API_KEY` | Enables real Perplexity citation checking |
| `GOOGLE_AI_API_KEY` | Enables real Gemini citation checking |
| `GSC_CREDENTIALS_PATH` | Service-account JSON for real GSC |
| `AHREFS_API_KEY` / `MOZ_API_KEY` | Real domain-authority signals |

## Project layout

```
aeo-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routes + deps
│   │   ├── core/           # config, db, security, celery, cache
│   │   ├── models/         # SQLAlchemy models (12 tables)
│   │   ├── providers/      # base + mock/* + real/*
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # RRF, freshness, citation orchestrator, GSC, authority, reports
│   │   ├── tasks/          # Celery tasks
│   │   └── templates/      # Jinja template for PDF reports
│   ├── alembic/            # migrations
│   ├── scripts/seed.py     # idempotent demo data
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js App Router pages (login + 9 authed pages)
│   │   ├── components/ui/  # Table, Modal, FilterBar, Sidebar, AppShell, …
│   │   ├── components/charts/
│   │   ├── components/modules/
│   │   ├── hooks/          # One TanStack Query hook file per module
│   │   ├── lib/api.ts      # Axios client with JWT interceptor
│   │   ├── stores/         # Zustand auth + active-client stores
│   │   └── types/
│   └── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Demo credentials

```
Email:    demo@aeo.local
Password: demo1234
```

3 demo clients are seeded (Acme Corporation, TechStart Inc, Global Solutions) with prompts, keywords, RRF scores, tracked content + freshness, 3 competitors each, and a scheduled weekly report.

## License

Proprietary.
