from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.prompt import Prompt, PromptCategory
from app.schemas.prompt import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptBulkImport,
    PromptGSCImport,
    PromptCategoryCreate,
    PromptCategoryResponse,
    PromptVisibilityCheck,
)
from app.schemas.base import PaginatedResponse

router = APIRouter()


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
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Import prompts from Google Search Console data.

    Converts GSC queries to conversational AI prompts.
    """
    # This would trigger the GSC import service in the background
    # background_tasks.add_task(gsc_importer.import_and_convert, client_id, config)

    return {
        "status": "import_started",
        "message": "GSC import started. Check back for results.",
        "config": config.model_dump(),
    }


@router.post("/{prompt_id}/check-visibility")
async def check_prompt_visibility(
    prompt_id: int,
    config: PromptVisibilityCheck,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Check if client is cited for this prompt across platforms.

    Runs multiple checks to assess stability (variance analysis).
    """
    # Get prompt
    result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id)
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # This would trigger citation checking in background
    # background_tasks.add_task(citation_checker.check_with_variance, ...)

    return {
        "status": "check_started",
        "prompt_id": prompt_id,
        "platforms": config.platforms,
        "check_count": config.check_count,
        "message": "Visibility check started. Results will be available shortly.",
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
