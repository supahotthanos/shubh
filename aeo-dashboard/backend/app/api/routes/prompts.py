from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.models.client import Client, ClientDomain
from app.models.prompt import Prompt, PromptCategory
from app.schemas.base import PaginatedResponse
from app.schemas.prompt import (
    PromptBulkImport,
    PromptCategoryCreate,
    PromptCategoryResponse,
    PromptCreate,
    PromptGSCImport,
    PromptResponse,
    PromptUpdate,
    PromptVisibilityCheck,
)
from app.services.citation_orchestrator import run_prompt_check
from app.services.gsc_importer import GSCImporterService

router = APIRouter()
_gsc_importer = GSCImporterService()


@router.get("/{client_id}", response_model=PaginatedResponse[PromptResponse])
async def list_prompts(
    client_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    category_id: Optional[int] = None,
    is_visible: Optional[bool] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all tracked prompts for a client.
    """
    query = select(Prompt).where(Prompt.client_id == client_id)

    if category_id:
        query = query.where(Prompt.category_id == category_id)
    if is_visible is not None:
        query = query.where(Prompt.is_visible == is_visible)
    if source:
        query = query.where(Prompt.source == source)

    # Get total
    total_result = await db.execute(query)
    total = len(total_result.all())

    # Get paginated results
    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    prompts = result.scalars().all()

    return PaginatedResponse.create(prompts, total, page, page_size)


@router.post("/{client_id}", response_model=PromptResponse)
async def create_prompt(
    client_id: int,
    prompt_data: PromptCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new prompt to track.
    """
    prompt = Prompt(
        text=prompt_data.text,
        normalized_text=prompt_data.text.lower().strip(),
        category_id=prompt_data.category_id,
        intent_type=prompt_data.intent_type,
        is_branded=prompt_data.is_branded,
        check_frequency_hours=prompt_data.check_frequency_hours,
        source="manual",
        client_id=client_id,
    )

    db.add(prompt)
    await db.commit()
    await db.refresh(prompt)

    return prompt


@router.post("/{client_id}/bulk", response_model=dict)
async def import_prompts_bulk(
    client_id: int,
    import_data: PromptBulkImport,
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk import prompts.
    """
    added = 0
    skipped = 0

    for text in import_data.prompts:
        # Check for duplicates
        existing = await db.execute(
            select(Prompt).where(
                Prompt.client_id == client_id,
                Prompt.normalized_text == text.lower().strip(),
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        prompt = Prompt(
            text=text,
            normalized_text=text.lower().strip(),
            category_id=import_data.category_id,
            source=import_data.source,
            client_id=client_id,
        )
        db.add(prompt)
        added += 1

    await db.commit()

    return {
        "added": added,
        "skipped": skipped,
        "total_processed": len(import_data.prompts),
    }


@router.post("/{client_id}/import-gsc")
async def import_from_gsc(
    client_id: int,
    config: PromptGSCImport,
    db: AsyncSession = Depends(get_db),
):
    """Pull GSC queries, convert to prompts, cluster, prioritize, and persist."""
    client_result = await db.execute(select(Client).where(Client.id == client_id))
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    domain_result = await db.execute(
        select(ClientDomain).where(ClientDomain.client_id == client_id)
    )
    domains = domain_result.scalars().all()
    primary = next(
        (d for d in domains if d.is_primary), domains[0] if domains else None
    )
    property_url = (primary.gsc_property_url if primary else None) or (
        f"https://{primary.domain}" if primary else f"https://{client.slug}.com"
    )

    queries = await _gsc_importer.fetch_queries(
        property_url=property_url,
        days_back=config.days_back,
        min_impressions=config.min_impressions,
        min_clicks=config.min_clicks,
        max_position=config.max_position,
    )
    converted = _gsc_importer.convert_to_prompts(queries, brand_names=client.brand_names or [])
    clusters = _gsc_importer.cluster_prompts(converted)
    prioritized = _gsc_importer.prioritize_prompts(converted)

    added = 0
    skipped = 0
    for conv in converted:
        existing = await db.execute(
            select(Prompt).where(
                Prompt.client_id == client_id,
                Prompt.normalized_text == conv.conversational_prompt.lower().strip(),
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue
        db.add(
            Prompt(
                text=conv.conversational_prompt,
                normalized_text=conv.conversational_prompt.lower().strip(),
                source="gsc_import",
                intent_type=conv.intent_type,
                is_branded=conv.is_branded,
                gsc_impressions=conv.gsc_metrics.impressions,
                gsc_clicks=conv.gsc_metrics.clicks,
                gsc_avg_position=conv.gsc_metrics.position,
                client_id=client_id,
            )
        )
        added += 1
    await db.commit()

    return {
        "status": "done",
        "imported_prompts": added,
        "skipped_duplicates": skipped,
        "clusters": len(clusters),
        "summary": _gsc_importer.generate_stakeholder_summary(prioritized),
    }


@router.post("/{prompt_id}/check-visibility")
async def check_prompt_visibility(
    prompt_id: int,
    config: PromptVisibilityCheck,
    db: AsyncSession = Depends(get_db),
):
    """Run live visibility check across platforms and persist results."""
    result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    outcomes = await run_prompt_check(
        db,
        prompt,
        platforms=config.platforms,
        check_count=max(1, min(5, config.check_count)),
    )
    summary = {}
    for platform, results in outcomes.items():
        cited = sum(1 for r in results if r.was_cited)
        positions = [r.position for r in results if r.position]
        summary[platform] = {
            "checks": len(results),
            "citation_rate": round(cited / len(results), 2) if results else 0,
            "avg_position": (sum(positions) / len(positions)) if positions else None,
        }
    return {
        "status": "complete",
        "prompt_id": prompt_id,
        "is_visible": prompt.is_visible,
        "visibility_score": prompt.visibility_score,
        "per_platform": summary,
    }


@router.get("/{client_id}/visibility-summary")
async def get_visibility_summary(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get prompt visibility summary.

    Categories:
    - already_visible: Prompts where client is cited
    - high_potential: Strong GSC performance, not yet visible in AI
    - at_risk: Recently lost visibility
    """
    # Get all prompts with visibility data
    result = await db.execute(
        select(Prompt).where(Prompt.client_id == client_id)
    )
    prompts = result.scalars().all()

    already_visible = [p for p in prompts if p.is_visible]
    not_visible = [p for p in prompts if not p.is_visible]

    # Identify high potential (has good GSC metrics but not visible)
    high_potential = [
        p for p in not_visible
        if p.gsc_impressions and p.gsc_impressions > 1000
        and p.gsc_avg_position and p.gsc_avg_position < 20
    ]

    return {
        "total_prompts": len(prompts),
        "already_visible": {
            "count": len(already_visible),
            "prompts": [
                {"id": p.id, "text": p.text, "visibility_score": p.visibility_score}
                for p in already_visible[:10]
            ],
        },
        "high_potential": {
            "count": len(high_potential),
            "prompts": [
                {
                    "id": p.id,
                    "text": p.text,
                    "gsc_impressions": p.gsc_impressions,
                    "gsc_position": p.gsc_avg_position,
                }
                for p in high_potential[:10]
            ],
        },
        "not_visible": {
            "count": len(not_visible) - len(high_potential),
        },
    }


# Category endpoints
@router.get("/categories/", response_model=List[PromptCategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """
    List all prompt categories.
    """
    result = await db.execute(select(PromptCategory))
    return result.scalars().all()


@router.post("/categories/", response_model=PromptCategoryResponse)
async def create_category(
    category_data: PromptCategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new prompt category.
    """
    category = PromptCategory(
        name=category_data.name,
        slug=category_data.name.lower().replace(" ", "-"),
        description=category_data.description,
        color=category_data.color,
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category
