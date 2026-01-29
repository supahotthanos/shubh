from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.competitor import Competitor, CompetitorCitation
from app.services.authority_tracker import AuthorityTrackerService

router = APIRouter()
authority_service = AuthorityTrackerService()


@router.get("/{client_id}", response_model=List[dict])
async def list_competitors(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    List all tracked competitors for a client.
    """
    result = await db.execute(
        select(Competitor).where(
            Competitor.client_id == client_id,
            Competitor.is_active == True,
        )
    )
    competitors = result.scalars().all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "domain": c.domain,
            "total_citations": c.total_citations,
            "citation_share": c.citation_share,
            "avg_position": c.avg_position,
            "harmonic_centrality_rank": c.harmonic_centrality_rank,
            "domain_rating": c.domain_rating,
        }
        for c in competitors
    ]


@router.post("/{client_id}")
async def add_competitor(
    client_id: int,
    name: str,
    domain: str,
    brand_names: List[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a competitor to track.
    """
    competitor = Competitor(
        name=name,
        domain=domain,
        brand_names=brand_names or [name],
        client_id=client_id,
    )

    db.add(competitor)
    await db.commit()
    await db.refresh(competitor)

    return {"id": competitor.id, "name": competitor.name, "domain": competitor.domain}


@router.get("/{client_id}/comparison")
async def get_competitive_comparison(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive competitive comparison.

    Compares:
    - Total citations
    - Share of voice
    - Authority metrics (HC rank, DR)
    - Citation overlap
    """
    # Get competitors
    result = await db.execute(
        select(Competitor).where(
            Competitor.client_id == client_id,
            Competitor.is_active == True,
        )
    )
    competitors = result.scalars().all()

    # Build comparison data
    comparison = []
    total_citations = sum(c.total_citations for c in competitors)

    for c in competitors:
        share = (c.total_citations / total_citations * 100) if total_citations > 0 else 0
        comparison.append({
            "name": c.name,
            "domain": c.domain,
            "is_client": False,
            "total_citations": c.total_citations,
            "share_of_voice": round(share, 1),
            "avg_position": c.avg_position or 0,
            "hc_rank": c.harmonic_centrality_rank,
            "domain_rating": c.domain_rating,
        })

    # Sort by citations (client would be added separately)
    comparison.sort(key=lambda x: x["total_citations"], reverse=True)

    # Add rankings
    for i, c in enumerate(comparison):
        c["rank"] = i + 1

    return {
        "competitors": comparison,
        "total_tracked": len(competitors),
        "analysis": {
            "leader": comparison[0]["name"] if comparison else None,
            "avg_citations": total_citations / len(competitors) if competitors else 0,
        },
    }


@router.get("/{client_id}/citation-overlap")
async def get_citation_overlap(
    client_id: int,
    competitor_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze citation overlap with competitors.

    Shows prompts where both client and competitor are cited.
    """
    query = select(CompetitorCitation).join(Competitor).where(
        Competitor.client_id == client_id
    )

    if competitor_id:
        query = query.where(CompetitorCitation.competitor_id == competitor_id)

    result = await db.execute(query)
    citations = result.scalars().all()

    # Analyze overlap
    overlap_prompts = [c for c in citations if c.client_also_cited]
    competitor_only = [c for c in citations if not c.client_also_cited]

    return {
        "total_competitor_citations": len(citations),
        "overlap_count": len(overlap_prompts),
        "competitor_only_count": len(competitor_only),
        "overlap_prompts": [
            {
                "prompt": c.prompt_text,
                "competitor_position": c.position,
                "client_position": c.client_position,
                "winning": c.client_position < c.position if c.client_position else False,
            }
            for c in overlap_prompts[:20]
        ],
        "opportunities": [
            {
                "prompt": c.prompt_text,
                "competitor_position": c.position,
                "platform": c.platform,
            }
            for c in competitor_only[:20]
        ],
    }


@router.get("/{client_id}/authority-comparison")
async def get_authority_comparison(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Compare authority metrics across competitors.
    """
    result = await db.execute(
        select(Competitor).where(
            Competitor.client_id == client_id,
            Competitor.is_active == True,
        )
    )
    competitors = result.scalars().all()

    # Would integrate with authority tracker service
    comparison = [
        {
            "name": c.name,
            "domain": c.domain,
            "hc_rank": c.harmonic_centrality_rank,
            "domain_rating": c.domain_rating,
        }
        for c in competitors
    ]

    # Sort by HC rank (lower is better)
    comparison.sort(key=lambda x: x["hc_rank"] or float("inf"))

    return {
        "rankings": comparison,
        "insights": [
            "Authority metrics help predict citation likelihood",
            "Higher HC rank correlates with more AI citations",
        ],
    }


@router.post("/{competitor_id}/analyze")
async def analyze_competitor(
    competitor_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Run full analysis on a competitor.

    Includes:
    - Authority metrics refresh
    - Recent content detection
    - Citation pattern analysis
    """
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()

    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    # Analyze authority
    authority = await authority_service.analyze_domain(competitor.domain)

    # Update competitor record
    competitor.harmonic_centrality_rank = authority.harmonic_centrality_rank
    competitor.domain_rating = authority.domain_rating
    competitor.last_analyzed_at = datetime.utcnow()

    await db.commit()

    return {
        "competitor": competitor.name,
        "domain": competitor.domain,
        "authority_metrics": {
            "hc_rank": authority.harmonic_centrality_rank,
            "pagerank": authority.pagerank_score,
            "domain_rating": authority.domain_rating,
            "referring_domains": authority.referring_domains,
            "has_wikipedia": authority.has_wikipedia_citation,
        },
        "warnings": {
            "authority_dilution": authority.authority_dilution_warning,
            "dilution_reason": authority.dilution_explanation,
        },
        "analyzed_at": datetime.utcnow().isoformat(),
    }
