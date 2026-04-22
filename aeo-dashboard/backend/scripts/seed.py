"""Seed the database with realistic demo data — idempotent.

Run once the schema exists:
    cd backend && python -m scripts.seed
"""
from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.campaign import Campaign, CampaignAsset
from app.models.citation import Citation, CitationCheck, CitationPlatform
from app.models.client import Client, ClientDomain
from app.models.competitor import Competitor, CompetitorCitation
from app.models.content import ContentFreshness, TrackedContent
from app.models.keyword import Keyword, KeywordRanking, RRFScore
from app.models.prompt import Prompt, PromptCategory
from app.models.report import Report, ReportSchedule
from app.models.user import Organization, User

PLATFORMS = [
    ("chatgpt", "ChatGPT"),
    ("perplexity", "Perplexity"),
    ("claude", "Claude"),
    ("google_ai", "Google AI Overview"),
    ("gemini", "Gemini"),
]

CLIENT_SEEDS = [
    {
        "name": "Acme Corporation",
        "slug": "acme",
        "domain": "acme.example.com",
        "industry": "SaaS",
        "brand_names": ["Acme", "Acme Corp", "Acme.com"],
        "brand_keywords": ["workflow", "automation"],
    },
    {
        "name": "TechStart Inc",
        "slug": "techstart",
        "domain": "techstart.example.com",
        "industry": "Fintech",
        "brand_names": ["TechStart", "TechStart Inc"],
        "brand_keywords": ["api", "payments"],
    },
    {
        "name": "Global Solutions",
        "slug": "global-solutions",
        "domain": "globalsolutions.example.com",
        "industry": "Consulting",
        "brand_names": ["Global Solutions", "GlobalSol"],
        "brand_keywords": ["operations", "strategy"],
    },
]

SAMPLE_PROMPTS = [
    "What is the best crm software for small business?",
    "What are the top project management tools in 2025?",
    "Which email marketing platform should I use?",
    "How do I choose an analytics tool?",
    "What's the difference between semrush and ahrefs?",
    "What are some alternatives to mailchimp?",
    "Is HubSpot worth the money?",
    "Best no-code app builders for 2025?",
    "How much does a CRM typically cost?",
    "What is marketing automation?",
]

SAMPLE_URLS = [
    "https://example.com/guides/best-crm-software",
    "https://example.com/guides/project-management-2025",
    "https://example.com/reviews/email-platforms",
    "https://example.com/compare/semrush-vs-ahrefs",
    "https://example.com/guides/marketing-automation",
    "https://example.com/resources/seo-checklist",
]


async def _get_or_create(db, model, /, lookup: dict, defaults: dict | None = None):
    stmt = select(model)
    for key, value in lookup.items():
        stmt = stmt.where(getattr(model, key) == value)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing, False
    inst = model(**{**lookup, **(defaults or {})})
    db.add(inst)
    await db.flush()
    return inst, True


async def seed() -> None:
    rng = random.Random(42)
    async with async_session_factory() as db:
        # Organization + admin user
        org, _ = await _get_or_create(
            db,
            Organization,
            {"slug": settings.DEMO_ORG_SLUG},
            {"name": settings.DEMO_ORG_NAME, "is_active": True},
        )
        user, created_user = await _get_or_create(
            db,
            User,
            {"email": settings.DEMO_USER_EMAIL},
            {
                "full_name": settings.DEMO_USER_NAME,
                "role": "admin",
                "is_active": True,
                "is_superuser": True,
                "organization_id": org.id,
                "hashed_password": hash_password(settings.DEMO_USER_PASSWORD),
            },
        )
        if not created_user:
            user.hashed_password = hash_password(settings.DEMO_USER_PASSWORD)

        # Platforms
        platforms: dict[str, CitationPlatform] = {}
        for slug, name in PLATFORMS:
            plat, _ = await _get_or_create(
                db,
                CitationPlatform,
                {"slug": slug},
                {"name": name, "is_active": True},
            )
            platforms[slug] = plat

        # Default prompt categories
        for name in ("Product", "Pricing", "Reviews", "Comparison", "How-to"):
            await _get_or_create(
                db,
                PromptCategory,
                {"slug": name.lower()},
                {"name": name, "color": "#4f46e5"},
            )

        await db.commit()

        # Clients
        for seed_client in CLIENT_SEEDS:
            client, is_new = await _get_or_create(
                db,
                Client,
                {"slug": seed_client["slug"]},
                {
                    "name": seed_client["name"],
                    "organization_id": org.id,
                    "industry": seed_client["industry"],
                    "brand_names": seed_client["brand_names"],
                    "brand_keywords": seed_client["brand_keywords"],
                    "is_active": True,
                },
            )
            if is_new:
                db.add(
                    ClientDomain(
                        domain=seed_client["domain"],
                        is_primary=True,
                        is_verified=True,
                        gsc_property_url=f"https://{seed_client['domain']}",
                        gsc_connected=True,
                        client_id=client.id,
                    )
                )
                await db.flush()

            await _seed_client_data(db, client, platforms, rng)

        # Competitors
        for seed_client in CLIENT_SEEDS:
            client_q = await db.execute(
                select(Client).where(Client.slug == seed_client["slug"])
            )
            client = client_q.scalar_one()
            comps = [
                ("CompetitorOne", "competitor-one.example.com"),
                ("Rival Systems", "rival.example.com"),
                ("Primary Alt", "primaryalt.example.com"),
            ]
            for name, domain in comps:
                comp, is_new_comp = await _get_or_create(
                    db,
                    Competitor,
                    {"client_id": client.id, "domain": domain},
                    {
                        "name": name,
                        "brand_names": [name],
                        "total_citations": rng.randint(20, 120),
                        "citation_share": round(rng.uniform(5, 35), 1),
                        "avg_position": round(rng.uniform(1.2, 4.5), 1),
                        "harmonic_centrality_rank": rng.randint(1000, 500000),
                        "domain_rating": round(rng.uniform(40, 88), 1),
                        "is_active": True,
                    },
                )
                if is_new_comp:
                    for prompt in rng.sample(SAMPLE_PROMPTS, 5):
                        db.add(
                            CompetitorCitation(
                                competitor_id=comp.id,
                                prompt_text=prompt,
                                platform=rng.choice(list(platforms.keys())),
                                position=rng.randint(1, 5),
                                cited_url=f"https://{domain}/x",
                                mention_type=rng.choice(["linked", "unlinked"]),
                                client_also_cited=rng.random() < 0.3,
                                client_position=rng.choice([None, 2, 3, 4, 6]),
                                first_seen_at=datetime.utcnow()
                                - timedelta(days=rng.randint(1, 50)),
                                last_seen_at=datetime.utcnow(),
                                is_currently_visible=True,
                            )
                        )
        await db.commit()

        # One scheduled report on the first client
        first = (
            await db.execute(select(Client).where(Client.slug == CLIENT_SEEDS[0]["slug"]))
        ).scalar_one()
        existing_sched = (
            await db.execute(
                select(ReportSchedule).where(ReportSchedule.client_id == first.id)
            )
        ).scalar_one_or_none()
        if existing_sched is None:
            db.add(
                ReportSchedule(
                    frequency="weekly",
                    day_of_week=1,
                    hour=9,
                    recipients=[settings.DEMO_USER_EMAIL],
                    include_pdf=True,
                    is_active=True,
                    client_id=first.id,
                )
            )
            await db.commit()

    print(
        f"Seed complete. Login with {settings.DEMO_USER_EMAIL} / {settings.DEMO_USER_PASSWORD}"
    )


async def _seed_client_data(db, client: Client, platforms: dict, rng: random.Random) -> None:
    # Prompts
    existing_count = (
        await db.execute(
            select(Prompt.id).where(Prompt.client_id == client.id)
        )
    ).all()
    if not existing_count:
        for i, text in enumerate(SAMPLE_PROMPTS):
            db.add(
                Prompt(
                    text=text,
                    normalized_text=text.lower().strip(),
                    source="manual" if i > 3 else "gsc_import",
                    intent_type=rng.choice(
                        ["informational", "commercial", "transactional"]
                    ),
                    is_branded=False,
                    gsc_impressions=rng.randint(300, 25000),
                    gsc_clicks=rng.randint(5, 800),
                    gsc_avg_position=round(rng.uniform(1.5, 28.0), 2),
                    is_visible=rng.random() < 0.55,
                    visibility_score=round(rng.uniform(20, 98), 1),
                    last_checked_at=datetime.utcnow().isoformat(),
                    check_frequency_hours=24,
                    client_id=client.id,
                )
            )
        await db.flush()

    # Keywords + RRF
    keyword_terms = [
        "best crm software", "project management tools", "email marketing platform",
        "seo automation tool", "analytics dashboard", "customer support software",
        "marketing automation", "landing page builder", "video conferencing",
        "design software for teams",
    ]
    existing_kw = (
        await db.execute(select(Keyword).where(Keyword.client_id == client.id))
    ).scalars().all()
    kw_count = len(existing_kw)
    if kw_count < len(keyword_terms):
        for term in keyword_terms[kw_count:]:
            kw = Keyword(
                keyword=term,
                normalized_keyword=term.lower(),
                monthly_search_volume=rng.randint(500, 40000),
                keyword_difficulty=round(rng.uniform(20, 80), 1),
                cpc=round(rng.uniform(0.5, 15), 2),
                search_intent=rng.choice(["informational", "commercial"]),
                is_priority=rng.random() < 0.4,
                track_rankings=True,
                client_id=client.id,
            )
            db.add(kw)
            await db.flush()
            # RRF: 0-4 sub queries
            sub_queries = []
            ranks = []
            for _ in range(rng.randint(0, 4)):
                rank = rng.randint(1, 120)
                ranks.append(rank)
                sub_queries.append(
                    {
                        "query": f"{term} {rng.choice(['2025', 'for startups', 'free'])}",
                        "rank": rank,
                        "url": f"https://{client.slug}.com/guide",
                        "search_engine": "google",
                    }
                )
            raw = sum(1 / (60 + r) for r in ranks) if ranks else 0.0
            db.add(
                RRFScore(
                    keyword_id=kw.id,
                    sub_queries=sub_queries,
                    k_constant=60.0,
                    raw_score=raw,
                    normalized_score=min(1.0, raw / (len(ranks) * (1 / 61))) if ranks else 0,
                    meets_threshold=raw >= 0.02,
                    total_appearances=len(ranks),
                    avg_rank=(sum(ranks) / len(ranks)) if ranks else 0,
                    best_rank=min(ranks) if ranks else 0,
                    worst_rank=max(ranks) if ranks else 0,
                    appearances_needed=0 if raw >= 0.02 else 2,
                    target_rank_each=40,
                    calculated_at=datetime.utcnow(),
                )
            )
            for _ in range(rng.randint(1, 3)):
                db.add(
                    KeywordRanking(
                        search_engine="google",
                        position=rng.randint(1, 80),
                        url=f"https://{client.slug}.com/guide",
                        serp_features=[],
                        checked_at=datetime.utcnow(),
                        keyword_id=kw.id,
                    )
                )
        await db.flush()

    # Tracked content + freshness
    existing_content = (
        await db.execute(
            select(TrackedContent).where(TrackedContent.client_id == client.id)
        )
    ).scalars().all()
    if not existing_content:
        for url in SAMPLE_URLS:
            content = TrackedContent(
                url=url,
                title=url.rsplit("/", 1)[-1].replace("-", " ").title(),
                meta_description="Guide for the topic.",
                word_count=rng.randint(600, 2400),
                avg_chunk_size_tokens=rng.randint(280, 650),
                has_schema_markup=rng.random() < 0.7,
                schema_types=["Article"] if rng.random() < 0.7 else [],
                heading_structure={"h1": 1, "h2": rng.randint(2, 8)},
                has_paa_style_sections=rng.random() < 0.5,
                has_negation_content=rng.random() < 0.3,
                is_active=True,
                check_frequency_hours=168,
                client_id=client.id,
            )
            db.add(content)
            await db.flush()
            days = rng.randint(30, 720)
            score = max(0, 100 - days / 8)
            grade = _grade(score)
            db.add(
                ContentFreshness(
                    content_id=content.id,
                    last_modified_header=datetime.utcnow() - timedelta(days=days),
                    detected_update_date=datetime.utcnow() - timedelta(days=days),
                    content_hash=f"hash-{content.id}",
                    freshness_score=score,
                    freshness_grade=grade,
                    days_since_update=days,
                    gpt_impact_score=max(0, 100 - days / 4),
                    llama_impact_score=max(0, 100 - days / 2),
                    gemini_impact_score=max(0, 100 - days / 5),
                    refresh_priority=(
                        "critical"
                        if grade == "F"
                        else "high"
                        if grade == "D"
                        else "medium"
                        if grade == "C"
                        else "low"
                    ),
                    refresh_recommendation="Refresh with current examples."
                    if grade in ("D", "F")
                    else None,
                    estimated_position_loss=min(95, max(0, days - 180) // 3),
                    checked_at=datetime.utcnow(),
                )
            )
        await db.flush()

    # Campaigns
    existing_camp = (
        await db.execute(select(Campaign).where(Campaign.client_id == client.id))
    ).scalars().all()
    if not existing_camp:
        for name, ctype in (
            ("Q1 Thought Leadership", "thought_leadership"),
            ("Listicles Push", "listicle"),
            ("Product Launch PR", "press_release"),
        ):
            campaign = Campaign(
                name=name,
                campaign_type=ctype,
                description="Seeded campaign",
                status=rng.choice(["active", "active", "paused"]),
                start_date=datetime.utcnow() - timedelta(days=30),
                target_citations=rng.randint(20, 80),
                budget=rng.randint(2000, 25000),
                spent=rng.randint(0, 15000),
                client_id=client.id,
            )
            db.add(campaign)
            await db.flush()
            for _ in range(rng.randint(2, 5)):
                db.add(
                    CampaignAsset(
                        asset_type=ctype,
                        title=f"{name} — asset {rng.randint(1, 99)}",
                        url=f"https://external.example.com/{rng.randint(1, 9999)}",
                        hosting_domain="external.example.com",
                        hosting_domain_authority=round(rng.uniform(50, 90), 1),
                        status=rng.choice(["pending", "live", "indexed", "cited"]),
                        published_at=datetime.utcnow()
                        - timedelta(days=rng.randint(1, 25)),
                        citation_count=rng.randint(0, 6),
                        campaign_id=campaign.id,
                    )
                )
        await db.flush()

    # Citations + citation checks
    prompts = (
        await db.execute(select(Prompt).where(Prompt.client_id == client.id))
    ).scalars().all()
    existing_cit = (
        await db.execute(select(Citation.id).where(Citation.client_id == client.id))
    ).all()
    if not existing_cit:
        for prompt in prompts:
            for slug, platform in platforms.items():
                if rng.random() < 0.55:
                    pos = rng.randint(1, 5)
                    now = datetime.utcnow()
                    db.add(
                        Citation(
                            client_id=client.id,
                            prompt_id=prompt.id,
                            platform_id=platform.id,
                            cited_url=f"https://{client.slug}.com/guide",
                            cited_text=client.name,
                            mention_type=rng.choice(["linked", "unlinked", "brand_mention"]),
                            position=pos,
                            is_primary=pos == 1,
                            confidence_score=round(rng.uniform(0.7, 0.99), 2),
                            sentiment="neutral",
                            first_seen_at=now - timedelta(days=rng.randint(1, 60)),
                            last_seen_at=now,
                            is_currently_visible=True,
                        )
                    )
                for _ in range(rng.randint(2, 4)):
                    db.add(
                        CitationCheck(
                            prompt_id=prompt.id,
                            platform_id=platform.id,
                            was_cited=rng.random() < 0.55,
                            position=rng.randint(1, 5) if rng.random() < 0.7 else None,
                            response_text="[seeded response]",
                            response_hash=f"seed{rng.randint(1, 99999):05d}",
                            model_version=f"{slug}-mock",
                            temperature=0.7,
                            check_duration_ms=rng.randint(400, 1800),
                        )
                    )
        await db.commit()


def _grade(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


if __name__ == "__main__":
    asyncio.run(seed())
