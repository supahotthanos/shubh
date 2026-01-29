from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.content import TrackedContent, ContentFreshness
from app.schemas.content import (
    TrackedContentCreate,
    TrackedContentUpdate,
    TrackedContentResponse,
    FreshnessResponse,
    FreshnessTarget,
    ContentOptimizationRecommendation,
    ChunkAnalysis,
)
from app.services.freshness_analyzer import FreshnessAnalyzerService

router = APIRouter()
freshness_service = FreshnessAnalyzerService()


@router.get("/{client_id}", response_model=List[TrackedContentResponse])
async def list_tracked_content(
    client_id: int,
    freshness_grade: Optional[str] = None,
    needs_refresh: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    """
    List all tracked content for a client.
    """
    query = select(TrackedContent).where(TrackedContent.client_id == client_id)

    if needs_refresh:
        query = query.where(TrackedContent.is_active == True)

    result = await db.execute(query)
    content_list = result.scalars().all()

    # Filter by freshness grade if specified
    if freshness_grade:
        content_list = [c for c in content_list if c.freshness_records and
                       c.freshness_records[-1].freshness_grade == freshness_grade]

    return content_list


@router.post("/{client_id}", response_model=TrackedContentResponse)
async def add_tracked_content(
    client_id: int,
    content_data: TrackedContentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new URL to track for freshness and optimization.
    """
    content = TrackedContent(
        url=content_data.url,
        check_frequency_hours=content_data.check_frequency_hours,
        client_id=client_id,
    )

    db.add(content)
    await db.commit()
    await db.refresh(content)

    # Schedule initial analysis
    # background_tasks.add_task(analyze_content, content.id)

    return content


@router.post("/{content_id}/analyze")
async def analyze_content_freshness(
    content_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze content freshness and structure.
    """
    result = await db.execute(
        select(TrackedContent).where(TrackedContent.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Run freshness analysis
    analysis = await freshness_service.analyze_url(content.url)

    # Store freshness record
    freshness = ContentFreshness(
        content_id=content_id,
        last_modified_header=analysis.last_modified,
        detected_publish_date=analysis.publish_date,
        detected_update_date=analysis.update_date,
        content_hash=analysis.content_hash,
        freshness_score=analysis.freshness_score,
        freshness_grade=analysis.freshness_grade.value,
        days_since_update=analysis.days_since_update,
        gpt_impact_score=None,  # Would map from impact string
        llama_impact_score=None,
        gemini_impact_score=None,
        refresh_priority=analysis.refresh_priority,
        refresh_recommendation=analysis.recommendations[0] if analysis.recommendations else None,
        estimated_position_loss=analysis.estimated_position_loss,
    )

    db.add(freshness)
    await db.commit()

    return {
        "url": content.url,
        "freshness_score": analysis.freshness_score,
        "freshness_grade": analysis.freshness_grade.value,
        "days_since_update": analysis.days_since_update,
        "gpt_impact": analysis.gpt_impact,
        "llama_impact": analysis.llama_impact,
        "gemini_impact": analysis.gemini_impact,
        "estimated_position_loss": analysis.estimated_position_loss,
        "refresh_priority": analysis.refresh_priority,
        "recommendations": analysis.recommendations,
    }


@router.get("/{client_id}/freshness-summary")
async def get_freshness_summary(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get content freshness summary with grade distribution.
    """
    result = await db.execute(
        select(TrackedContent).where(
            TrackedContent.client_id == client_id,
            TrackedContent.is_active == True,
        )
    )
    content_list = result.scalars().all()

    # Calculate grade distribution
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    total_score = 0
    needs_refresh = []

    for content in content_list:
        if content.freshness_records:
            latest = content.freshness_records[-1]
            grade = latest.freshness_grade
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
            total_score += latest.freshness_score

            if grade in ("D", "F"):
                needs_refresh.append({
                    "url": content.url,
                    "title": content.title,
                    "grade": grade,
                    "days_old": latest.days_since_update,
                    "position_loss": latest.estimated_position_loss,
                    "priority": latest.refresh_priority,
                })

    total_content = len(content_list)
    avg_score = total_score / total_content if total_content > 0 else 0

    # Determine overall grade
    if avg_score >= 80:
        overall_grade = "A"
    elif avg_score >= 60:
        overall_grade = "B"
    elif avg_score >= 40:
        overall_grade = "C"
    elif avg_score >= 20:
        overall_grade = "D"
    else:
        overall_grade = "F"

    return {
        "overall_grade": overall_grade,
        "avg_score": avg_score,
        "total_pages": total_content,
        "grade_distribution": grade_counts,
        "needs_refresh_count": len(needs_refresh),
        "needs_refresh": sorted(needs_refresh, key=lambda x: x["priority"] == "critical", reverse=True)[:10],
    }


@router.get("/freshness-targets", response_model=List[FreshnessTarget])
async def get_freshness_targets():
    """
    Get recommended update frequencies by model family.
    """
    targets = freshness_service.get_model_freshness_targets()

    return [
        FreshnessTarget(
            model_family=t["model_family"],
            recommended_update_frequency_months=t["recommended_update_months"],
            current_age_months=0,  # Would be content-specific
            is_fresh=True,
            impact_description=t["notes"],
        )
        for t in targets
    ]


@router.get("/{content_id}/optimization-recommendations", response_model=ContentOptimizationRecommendation)
async def get_content_optimization(
    content_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI-specific optimization recommendations for content.

    Recommendations based on:
    - Chunk size optimization (~500 tokens per section)
    - Negation-aware content ("what it is" AND "what it isn't")
    - PAA-style answer blocks
    - Schema markup implementation
    """
    result = await db.execute(
        select(TrackedContent).where(TrackedContent.id == content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    recommendations = []

    # Chunk size recommendation
    if content.avg_chunk_size_tokens:
        if content.avg_chunk_size_tokens > 600:
            recommendations.append({
                "type": "chunk_size",
                "priority": "high",
                "title": "Reduce section sizes",
                "description": f"Average chunk size is {content.avg_chunk_size_tokens} tokens. Target ~500 tokens for optimal LLM retrieval.",
                "action": "Break long sections into smaller, focused subsections.",
            })
        elif content.avg_chunk_size_tokens < 300:
            recommendations.append({
                "type": "chunk_size",
                "priority": "medium",
                "title": "Expand thin sections",
                "description": f"Average chunk size is {content.avg_chunk_size_tokens} tokens. Sections may lack sufficient detail.",
                "action": "Add more comprehensive information to thin sections.",
            })

    # Schema markup
    if not content.has_schema_markup:
        recommendations.append({
            "type": "schema",
            "priority": "high",
            "title": "Add Schema Markup",
            "description": "No structured data detected. Schema helps AI understand content context.",
            "action": "Implement Article, FAQ, or HowTo schema as appropriate.",
        })

    # PAA-style content
    if not content.has_paa_style_sections:
        recommendations.append({
            "type": "paa_format",
            "priority": "medium",
            "title": "Add Q&A Sections",
            "description": "PAA-style question/answer format improves citation likelihood.",
            "action": "Add FAQ section with common questions and concise answers.",
        })

    # Negation content
    if not content.has_negation_content:
        recommendations.append({
            "type": "negation",
            "priority": "medium",
            "title": "Add Negation Content",
            "description": "Including 'what it isn't' helps with semantic relevance scoring.",
            "action": "Add sections clarifying what the topic is NOT or common misconceptions.",
        })

    return ContentOptimizationRecommendation(
        url=content.url,
        title=content.title,
        recommendations=recommendations,
        priority_score=sum(10 if r["priority"] == "high" else 5 for r in recommendations),
        estimated_impact="high" if len(recommendations) > 2 else "medium",
    )
