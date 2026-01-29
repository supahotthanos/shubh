from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.client import Client, ClientDomain
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientSummary,
    ClientDomainCreate,
)
from app.schemas.base import PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ClientSummary])
async def list_clients(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all clients with pagination.
    """
    # Build query
    query = select(Client)

    if search:
        query = query.where(Client.name.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.where(Client.is_active == is_active)

    # Get total count
    total_query = select(Client.id)
    if search:
        total_query = total_query.where(Client.name.ilike(f"%{search}%"))
    if is_active is not None:
        total_query = total_query.where(Client.is_active == is_active)

    # Execute queries
    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )
    clients = result.scalars().all()

    total_result = await db.execute(total_query)
    total = len(total_result.all())

    # Convert to response model
    items = [
        ClientSummary(
            id=c.id,
            name=c.name,
            slug=c.slug,
            industry=c.industry,
            is_active=c.is_active,
            total_citations=0,  # Would aggregate from citations table
            total_prompts=0,  # Would aggregate from prompts table
            citation_stability_score=0.0,
        )
        for c in clients
    ]

    return PaginatedResponse.create(items, total, page, page_size)


@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new client.
    """
    # Generate slug from name
    slug = client_data.name.lower().replace(" ", "-")

    client = Client(
        name=client_data.name,
        slug=slug,
        description=client_data.description,
        industry=client_data.industry,
        logo_url=client_data.logo_url,
        brand_names=client_data.brand_names,
        brand_keywords=client_data.brand_keywords,
        organization_id=1,  # Would come from auth context
    )

    db.add(client)
    await db.commit()
    await db.refresh(client)

    # Add domains
    for domain_data in client_data.domains:
        domain = ClientDomain(
            domain=domain_data.domain,
            is_primary=domain_data.is_primary,
            gsc_property_url=domain_data.gsc_property_url,
            client_id=client.id,
        )
        db.add(domain)

    await db.commit()
    await db.refresh(client)

    return client


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get client by ID.
    """
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update client.
    """
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Update fields
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    await db.commit()
    await db.refresh(client)

    return client


@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete client (soft delete by setting is_active=False).
    """
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client.is_active = False
    await db.commit()

    return {"message": "Client deactivated successfully"}


@router.post("/{client_id}/domains", response_model=ClientResponse)
async def add_domain(
    client_id: int,
    domain_data: ClientDomainCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a domain to client.
    """
    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    domain = ClientDomain(
        domain=domain_data.domain,
        is_primary=domain_data.is_primary,
        gsc_property_url=domain_data.gsc_property_url,
        client_id=client_id,
    )

    db.add(domain)
    await db.commit()
    await db.refresh(client)

    return client
