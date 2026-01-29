from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.keyword import Keyword, RRFScore
from app.schemas.keyword import (
    KeywordCreate,
    KeywordUpdate,
    KeywordResponse,
    RRFScoreResponse,
    RRFCalculation,
    RRFQuickReference,
    RRFRecommendation,
)
from app.services.rrf_calculator import RRFCalculatorService, SubQueryRank

router = APIRouter()
rrf_service = RRFCalculatorService()


@router.get("/{client_id}", response_model=List[KeywordResponse])
async def list_keywords(
    client_id: int,
    priority_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    """
    List all tracked keywords for a client.
    """
    query = select(Keyword).where(Keyword.client_id == client_id)

    if priority_only:
        query = query.where(Keyword.is_priority == True)

    result = await db.execute(query)
    keywords = result.scalars().all()

    return keywords


@router.post("/{client_id}", response_model=KeywordResponse)
async def add_keyword(
    client_id: int,
    keyword_data: KeywordCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new keyword to track.
    """
    keyword = Keyword(
        keyword=keyword_data.keyword,
        normalized_keyword=keyword_data.keyword.lower().strip(),
        monthly_search_volume=keyword_data.monthly_search_volume,
        keyword_difficulty=keyword_data.keyword_difficulty,
        cpc=keyword_data.cpc,
        search_intent=keyword_data.search_intent,
        is_priority=keyword_data.is_priority,
        client_id=client_id,
    )

    db.add(keyword)
    await db.commit()
    await db.refresh(keyword)

    return keyword


@router.post("/{client_id}/bulk")
async def add_keywords_bulk(
    client_id: int,
    keywords: List[str],
    db: AsyncSession = Depends(get_db),
):
    """
    Add multiple keywords at once.
    """
    added = []
    for kw in keywords:
        keyword = Keyword(
            keyword=kw,
            normalized_keyword=kw.lower().strip(),
            client_id=client_id,
        )
        db.add(keyword)
        added.append(kw)

    await db.commit()

    return {"added": len(added), "keywords": added}


@router.get("/{client_id}/rrf-scores", response_model=List[RRFScoreResponse])
async def get_rrf_scores(
    client_id: int,
    below_threshold_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    """
    Get RRF scores for all tracked keywords.
    """
    query = select(RRFScore).join(Keyword).where(Keyword.client_id == client_id)

    if below_threshold_only:
        query = query.where(RRFScore.meets_threshold == False)

    result = await db.execute(query.order_by(RRFScore.raw_score.desc()))
    scores = result.scalars().all()

    return scores


@router.post("/calculate-rrf", response_model=RRFScoreResponse)
async def calculate_rrf_score(
    data: RRFCalculation,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate RRF score for a keyword based on sub-query rankings.

    The RRF formula: RRF(d) = Σ 1/(k + r(d))
    where k = 60 and r(d) is the rank position.

    Target threshold: 0.020 for likely citation inclusion.
    """
    # Convert input to SubQueryRank objects
    sub_queries = [
        SubQueryRank(
            query=sq["query"],
            rank=sq["rank"],
            url=sq["url"],
            search_engine=sq.get("search_engine", "google"),
        )
        for sq in data.sub_queries
    ]

    # Calculate RRF score
    result = rrf_service.calculate_from_sub_queries(sub_queries)

    # Get keyword for storage
    keyword_result = await db.execute(
        select(Keyword).where(Keyword.id == data.keyword_id)
    )
    keyword = keyword_result.scalar_one_or_none()

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    # Store result
    rrf_record = RRFScore(
        keyword_id=data.keyword_id,
        sub_queries=[sq.__dict__ for sq in sub_queries],
        k_constant=rrf_service.k,
        raw_score=result.raw_score,
        normalized_score=result.normalized_score,
        meets_threshold=result.meets_threshold,
        total_appearances=result.total_appearances,
        avg_rank=result.avg_rank,
        best_rank=result.best_rank,
        worst_rank=result.worst_rank,
        appearances_needed=result.appearances_needed,
        target_rank_each=result.target_rank_each,
        calculated_at=datetime.utcnow(),
    )

    db.add(rrf_record)
    await db.commit()
    await db.refresh(rrf_record)

    return RRFScoreResponse(
        id=rrf_record.id,
        keyword_id=rrf_record.keyword_id,
        keyword_text=keyword.keyword,
        sub_queries=rrf_record.sub_queries,
        k_constant=rrf_record.k_constant,
        raw_score=rrf_record.raw_score,
        normalized_score=rrf_record.normalized_score,
        meets_threshold=rrf_record.meets_threshold,
        total_appearances=rrf_record.total_appearances,
        avg_rank=rrf_record.avg_rank,
        best_rank=rrf_record.best_rank,
        worst_rank=rrf_record.worst_rank,
        appearances_needed=rrf_record.appearances_needed,
        target_rank_each=rrf_record.target_rank_each,
        calculated_at=rrf_record.calculated_at,
    )


@router.get("/rrf-quick-reference", response_model=List[RRFQuickReference])
async def get_rrf_quick_reference():
    """
    Get RRF quick reference table.

    Shows guaranteed scores for different appearance/rank combinations:
    | Appearances | Max Rank Each | Guaranteed Score |
    |------------|---------------|------------------|
    | 2×         | ≤ 40          | 0.0200 ✓        |
    | 3×         | ≤ 90          | 0.0200 ✓        |
    | 4×         | ≤ 140         | 0.0200 ✓        |
    """
    table = rrf_service.get_quick_reference_table()

    return [
        RRFQuickReference(
            appearances=row["appearances"],
            max_rank_each=row["max_rank_each"],
            guaranteed_score=row["guaranteed_score"],
            meets_threshold=row["meets_threshold"],
        )
        for row in table
    ]


@router.get("/{client_id}/rrf-recommendations", response_model=List[RRFRecommendation])
async def get_rrf_recommendations(
    client_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Get prioritized RRF improvement recommendations.
    """
    # Get keywords with their latest RRF scores
    query = (
        select(Keyword, RRFScore)
        .outerjoin(RRFScore, Keyword.id == RRFScore.keyword_id)
        .where(Keyword.client_id == client_id)
        .where(Keyword.track_rankings == True)
    )

    result = await db.execute(query)
    rows = result.all()

    recommendations = []
    for keyword, rrf_score in rows:
        if rrf_score and rrf_score.meets_threshold:
            continue  # Skip keywords already meeting threshold

        current_score = rrf_score.raw_score if rrf_score else 0.0

        # Generate recommendation
        if current_score == 0:
            rec = RRFRecommendation(
                keyword=keyword.keyword,
                current_score=0.0,
                target_score=0.020,
                gap=0.020,
                recommendation="No rankings found. Create comprehensive content targeting this topic.",
                priority="high",
                action_items=[
                    "Create pillar content for this topic",
                    "Target 2+ sub-queries at rank 40 or better",
                    "Build supporting content for related queries",
                ],
            )
        else:
            appearances_needed = rrf_score.appearances_needed if rrf_score else 2
            target_rank = rrf_score.target_rank_each if rrf_score else 40

            rec = RRFRecommendation(
                keyword=keyword.keyword,
                current_score=current_score,
                target_score=0.020,
                gap=0.020 - current_score,
                recommendation=f"Need {appearances_needed} more appearances at rank {target_rank} or better.",
                priority="medium" if current_score > 0.010 else "high",
                action_items=[
                    f"Target {appearances_needed} additional related queries",
                    f"Improve existing rankings to reach top {target_rank}",
                    "Consider content updates for freshness boost",
                ],
            )

        recommendations.append(rec)

    # Sort by gap (highest priority first)
    recommendations.sort(key=lambda r: r.gap, reverse=True)

    return recommendations[:limit]


@router.post("/{keyword_id}/simulate-improvement")
async def simulate_rrf_improvement(
    keyword_id: int,
    new_rank: int = Query(..., ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Simulate adding one more appearance at a given rank.

    Useful for planning which rankings to target.
    """
    # Get current RRF score
    result = await db.execute(
        select(RRFScore)
        .where(RRFScore.keyword_id == keyword_id)
        .order_by(RRFScore.calculated_at.desc())
        .limit(1)
    )
    current_rrf = result.scalar_one_or_none()

    if not current_rrf:
        current_score = 0.0
    else:
        current_score = current_rrf.raw_score

    # Calculate new contribution
    new_contribution = 1.0 / (60 + new_rank)
    new_score = current_score + new_contribution
    would_meet = new_score >= 0.020

    return {
        "current_score": current_score,
        "new_rank": new_rank,
        "new_contribution": new_contribution,
        "projected_score": new_score,
        "would_meet_threshold": would_meet,
        "threshold": 0.020,
        "message": (
            f"Adding rank #{new_rank} would bring score to {new_score:.4f} "
            f"({'meeting' if would_meet else 'still below'} threshold)"
        ),
    }
