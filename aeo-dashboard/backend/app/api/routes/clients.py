from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.citation import Citation
from app.models.client import Client, ClientDomain
from app.models.prompt import Prompt
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.client import (
    ClientCreate,
    ClientDomainCreate,
    ClientResponse,
    ClientSummary,
    ClientUpdate,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ClientSummary])
async def list_clients(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base = select(Client)
    if not user.is_superuser:
        base = base.where(Client.organization_id == user.organization_id)
    if search:
        base = base.where(Client.name.ilike(f"%{search}%"))
    if is_active is not None:
        base = base.where(Client.is_active == is_active)

    total = (
        await db.execute(select(func.count()).select_from(base.subquery()))
    ).scalar() or 0
    result = await db.execute(
        base.order_by(Client.name).offset((page - 1) * page_size).limit(page_size)
    )
    clients = result.scalars().all()

    items: List[ClientSummary] = []
    for client in clients:
        total_cites = (
            await db.execute(
                select(func.count(Citation.id)).where(Citation.client_id == client.id)
            )
        ).scalar() or 0
        total_prompts = (
            await db.execute(
                select(func.count(Prompt.id)).where(Prompt.client_id == client.id)
            )
        ).scalar() or 0
        items.append(
            ClientSummary(
                id=client.id,
                name=client.name,
                slug=client.slug,
                industry=client.industry,
                is_active=client.is_active,
                total_citations=total_cites,
                total_prompts=total_prompts,
                citation_stability_score=0.0,
            )
        )
    return PaginatedResponse.create(items, total, page, page_size)


@router.post("/", response_model=ClientResponse)
async def create_client(
    data: ClientCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    slug = data.name.lower().replace(" ", "-")
    client = Client(
        name=data.name,
        slug=slug,
        description=data.description,
        industry=data.industry,
        logo_url=data.logo_url,
        brand_names=data.brand_names,
        brand_keywords=data.brand_keywords,
        organization_id=user.organization_id,
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)

    for d in data.domains:
        db.add(
            ClientDomain(
                domain=d.domain,
                is_primary=d.is_primary,
                gsc_property_url=d.gsc_property_url,
                client_id=client.id,
            )
        )
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not user.is_superuser and client.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Client belongs to another organization")
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not user.is_superuser and client.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Client belongs to another organization")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    await db.commit()
    await db.refresh(client)
    return client


@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not user.is_superuser and client.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Client belongs to another organization")
    client.is_active = False
    await db.commit()
    return {"message": "Client deactivated successfully"}


@router.post("/{client_id}/domains", response_model=ClientResponse)
async def add_domain(
    client_id: int,
    data: ClientDomainCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not user.is_superuser and client.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Client belongs to another organization")
    db.add(
        ClientDomain(
            domain=data.domain,
            is_primary=data.is_primary,
            gsc_property_url=data.gsc_property_url,
            client_id=client_id,
        )
    )
    await db.commit()
    await db.refresh(client)
    return client
