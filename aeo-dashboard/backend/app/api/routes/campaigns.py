from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.campaign import Campaign, CampaignAsset, CampaignMetric
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignAssetCreate,
    CampaignAssetResponse,
    CampaignMetricResponse,
    CampaignTypeSummary,
)

router = APIRouter()


@router.get("/{client_id}", response_model=List[CampaignResponse])
async def list_campaigns(
    client_id: int,
    status: Optional[str] = None,
    campaign_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all campaigns for a client.

    Campaign types:
    - content_publish: Original content creation
    - guest_post: Guest posting on high-authority sites
    - press_release: Press release distribution
    - research_report: Original research/data
    - listicle: "Best X" style content
    - thought_leadership: Expert content
    """
    query = select(Campaign).where(Campaign.client_id == client_id)

    if status:
        query = query.where(Campaign.status == status)
    if campaign_type:
        query = query.where(Campaign.campaign_type == campaign_type)

    result = await db.execute(query.order_by(Campaign.created_at.desc()))
    campaigns = result.scalars().all()

    return campaigns


@router.post("/{client_id}", response_model=CampaignResponse)
async def create_campaign(
    client_id: int,
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new content marketing campaign.
    """
    campaign = Campaign(
        name=campaign_data.name,
        campaign_type=campaign_data.campaign_type,
        description=campaign_data.description,
        status="active",
        start_date=campaign_data.start_date or datetime.utcnow(),
        end_date=campaign_data.end_date,
        target_citations=campaign_data.target_citations,
        target_domains=campaign_data.target_domains,
        target_prompts=campaign_data.target_prompts,
        budget=campaign_data.budget,
        client_id=client_id,
    )

    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update campaign details.
    """
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)

    return campaign


@router.post("/{campaign_id}/assets", response_model=CampaignAssetResponse)
async def add_campaign_asset(
    campaign_id: int,
    asset_data: CampaignAssetCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Add an asset to a campaign.

    Asset types:
    - article: Blog post or article
    - guest_post: Guest article on external site
    - press_release: Press release
    - listicle: Listicle mentioning client
    - research_report: Original research
    """
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    asset = CampaignAsset(
        asset_type=asset_data.asset_type,
        title=asset_data.title,
        url=asset_data.url,
        hosting_domain=asset_data.hosting_domain,
        hosting_domain_authority=asset_data.hosting_domain_authority,
        client_position=asset_data.client_position,
        total_items=asset_data.total_items,
        status="pending",
        campaign_id=campaign_id,
    )

    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return asset


@router.get("/{campaign_id}/assets", response_model=List[CampaignAssetResponse])
async def list_campaign_assets(
    campaign_id: int,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all assets in a campaign.
    """
    query = select(CampaignAsset).where(CampaignAsset.campaign_id == campaign_id)

    if status:
        query = query.where(CampaignAsset.status == status)

    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/{asset_id}/status")
async def update_asset_status(
    asset_id: int,
    status: str = Query(..., regex="^(pending|live|indexed|cited)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Update asset status.

    Statuses: pending -> live -> indexed -> cited
    """
    result = await db.execute(
        select(CampaignAsset).where(CampaignAsset.id == asset_id)
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset.status = status
    if status == "live":
        asset.published_at = datetime.utcnow()
    elif status == "indexed":
        asset.indexed_at = datetime.utcnow()
    elif status == "cited":
        asset.first_citation_at = datetime.utcnow()

    await db.commit()

    return {"status": "updated", "new_status": status}


@router.get("/{client_id}/summary", response_model=List[CampaignTypeSummary])
async def get_campaign_summary(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get summary of campaigns by type.
    """
    result = await db.execute(
        select(Campaign).where(Campaign.client_id == client_id)
    )
    campaigns = result.scalars().all()

    # Group by type
    by_type = {}
    for c in campaigns:
        if c.campaign_type not in by_type:
            by_type[c.campaign_type] = {
                "total": 0,
                "active": 0,
                "assets": 0,
                "citations": 0,
            }
        by_type[c.campaign_type]["total"] += 1
        if c.status == "active":
            by_type[c.campaign_type]["active"] += 1

    # Get asset counts
    for campaign in campaigns:
        assets_result = await db.execute(
            select(CampaignAsset).where(CampaignAsset.campaign_id == campaign.id)
        )
        assets = assets_result.scalars().all()
        by_type[campaign.campaign_type]["assets"] += len(assets)
        by_type[campaign.campaign_type]["citations"] += sum(
            a.citation_count for a in assets
        )

    return [
        CampaignTypeSummary(
            campaign_type=ctype,
            total_campaigns=data["total"],
            active_campaigns=data["active"],
            total_assets=data["assets"],
            total_citations_gained=data["citations"],
            avg_time_to_citation_days=7.0,  # Would calculate from actual data
        )
        for ctype, data in by_type.items()
    ]


@router.get("/{campaign_id}/metrics", response_model=List[CampaignMetricResponse])
async def get_campaign_metrics(
    campaign_id: int,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """
    Get campaign performance metrics over time.
    """
    result = await db.execute(
        select(CampaignMetric)
        .where(CampaignMetric.campaign_id == campaign_id)
        .order_by(CampaignMetric.measured_at.desc())
        .limit(days)
    )

    return result.scalars().all()
