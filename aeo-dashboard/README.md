# AEO/GEO Dashboard

A comprehensive Answer Engine Optimization (AEO) and Generative Engine Optimization (GEO) dashboard for tracking and optimizing AI citations across platforms like ChatGPT, Perplexity, Claude, Google AI Overviews, and more.

## Features

### Module 1: AI Citation Tracking Center
- Real-time citation monitoring across 5+ LLM platforms
- Citation position tracking (1st mention vs. buried)
- Linked vs. Unlinked mention differentiation
- Historical citation trend charts (30/60/90 day views)
- Alert system for citation drops or gains

### Module 2: RRF Score Calculator & Visibility Predictor
Based on ChatGPT's k≈60 RRF (Reciprocal Rank Fusion) system:
- RRF Score calculation: Σ(1/(60 + rank))
- Target threshold: τ = 0.020
- Quick reference table for optimization planning
- Recommendations engine for improving visibility

### Module 3: Authority Signals Tracker
- Common Crawl WebGraph Metrics (Harmonic Centrality, PageRank)
- Public Suffix List (PSL) Analysis
- Trust Score Components (Wikipedia, Reddit, Press mentions)
- Authority dilution warnings for platform content

### Module 4: Recency & Freshness Optimization
Based on ChatGPT's freshness scoring profile:
- Content freshness tracking with A-F grades
- Model-specific update frequency recommendations
- Estimated position loss calculations
- Refresh priority rankings

### Module 5: GSC-to-AI Prompt Intelligence
- Import GSC ranking queries
- Convert keywords to conversational prompts
- Semantic clustering
- Visibility validation

### Module 6: Campaign Management
Track content marketing efforts:
- Listicle campaigns
- Guest posts
- Press releases
- Research reports

### Module 7: Competitive Intelligence
- Share of voice comparison
- Citation overlap analysis
- Authority metric comparisons
- Competitor activity monitoring

### Module 8: Client Reporting
- Automated weekly/monthly reports
- PDF and CSV export
- Google Slides integration
- Scheduled report delivery

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLAlchemy 2.0
- **Task Queue**: Celery with Redis
- **Caching**: Redis

### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State Management**: Zustand
- **Data Fetching**: TanStack Query

## Project Structure

```
aeo-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # API endpoints
│   │   ├── core/             # Configuration & database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities & API client
│   │   ├── hooks/            # Custom hooks
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start the development server
npm run dev
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Concepts

### RRF (Reciprocal Rank Fusion)
The RRF algorithm combines rankings from multiple sub-queries:
- Formula: RRF(d) = Σ 1/(k + r(d))
- k = 60 (constant)
- Threshold = 0.020 for likely citation inclusion

### Quick Reference
| Appearances | Max Rank Each | Guaranteed Score |
|------------|---------------|------------------|
| 2×         | ≤ 40          | 0.0200 ✓        |
| 3×         | ≤ 90          | 0.0200 ✓        |
| 4×         | ≤ 140         | 0.0200 ✓        |

### Freshness Scoring
| Model Family | Recommended Update Frequency |
|--------------|------------------------------|
| GPT-based    | Every 6-12 months           |
| LLaMA-based  | Every 3-6 months            |
| Qwen-based   | Annually                     |

## License

Proprietary - All rights reserved.
