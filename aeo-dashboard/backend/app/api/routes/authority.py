"""Authority signals endpoints (Common Crawl HC, Ahrefs, Moz, Wikipedia)."""
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_for_user
from app.core.database import get_db
from app.models.authority import AuthoritySignal
from app.models.client import Client, ClientDomain
from app.services.authority_tracker import AuthorityTrackerService

router = APIRouter()
_service = AuthorityTrackerService()


@router.get("/{client_id}/overview")
async def get_authority_overview(
    client_id: int,
    client: Client = Depends(get_client_for_user),
    db: AsyncSession = Depends(get_db),
):
    domains_q = await db.execute(
        select(ClientDomain).where(ClientDomain.client_id == client.id)
    )
    domains = domains_q.scalars().all()
    if not domains:
        raise HTTPException(status_code=404, detail="Client has no domains")

    results = []
    for domain in domains:
        analysis = await _service.analyze_domain(domain.domain)
        # Upsert into persisted signal
        sig_q = await db.execute(
            select(AuthoritySignal).where(AuthoritySignal.domain == domain.domain)
        )
        sig = sig_q.scalar_one_or_none()
        if sig is None:
            sig = AuthoritySignal(domain=domain.domain)
            db.add(sig)
        sig.harmonic_centrality_rank = analysis.harmonic_centrality_rank
        sig.harmonic_centrality_score = analysis.harmonic_centrality_score
        sig.pagerank_rank = analysis.pagerank_rank
        sig.pagerank_score = analysis.pagerank_score
        sig.domain_rating = analysis.domain_rating
        sig.domain_authority = analysis.domain_authority
        sig.referring_domains = analysis.referring_domains
        sig.total_backlinks = analysis.total_backlinks
        sig.has_wikipedia_citation = analysis.has_wikipedia_citation
        sig.wikipedia_citation_url = analysis.wikipedia_url
        sig.authority_dilution_warning = analysis.authority_dilution_warning
        sig.dilution_explanation = analysis.dilution_explanation
        sig.is_subdomain = analysis.is_subdomain
        sig.root_domain = analysis.root_domain
        sig.measured_at = datetime.utcnow()
        await db.commit()
        recs = _service.get_authority_improvement_recommendations(analysis)
        results.append(
            {
                "domain": domain.domain,
                "is_primary": domain.is_primary,
                "metrics": {
                    "hc_rank": analysis.harmonic_centrality_rank,
                    "hc_score": analysis.harmonic_centrality_score,
                    "pagerank_rank": analysis.pagerank_rank,
                    "pagerank_score": analysis.pagerank_score,
                    "domain_rating": analysis.domain_rating,
                    "domain_authority": analysis.domain_authority,
                    "referring_domains": analysis.referring_domains,
                    "total_backlinks": analysis.total_backlinks,
                    "has_wikipedia_citation": analysis.has_wikipedia_citation,
                    "wikipedia_url": analysis.wikipedia_url,
                },
                "warnings": {
                    "authority_dilution": analysis.authority_dilution_warning,
                    "explanation": analysis.dilution_explanation,
                },
                "recommendations": recs,
            }
        )
    return {"domains": results}


@router.get("/{client_id}/history")
async def get_authority_history(
    client_id: int,
    client: Client = Depends(get_client_for_user),
    db: AsyncSession = Depends(get_db),
):
    domains_q = await db.execute(
        select(ClientDomain.domain).where(ClientDomain.client_id == client.id)
    )
    domains = [d for (d,) in domains_q.all()]
    sig_q = await db.execute(
        select(AuthoritySignal)
        .where(AuthoritySignal.domain.in_(domains))
        .order_by(AuthoritySignal.measured_at.desc())
    )
    return [
        {
            "domain": s.domain,
            "measured_at": s.measured_at,
            "hc_rank": s.harmonic_centrality_rank,
            "domain_rating": s.domain_rating,
            "domain_authority": s.domain_authority,
            "referring_domains": s.referring_domains,
        }
        for s in sig_q.scalars().all()
    ]
