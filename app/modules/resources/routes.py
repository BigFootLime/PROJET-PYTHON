from fastapi import APIRouter, Depends, Query

from app.core.db import AsyncSessionLocal
from app.core.security import CurrentUser, get_current_user
from app.modules.resources.models import ResourceStatus, ResourceType
from app.modules.resources.schemas import ResourceCreate, ResourceResponse, ResourceUpdate
from app.modules.resources.service import ResourceService

router = APIRouter(prefix="/resources", tags=["Resources"])


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("", response_model=list[ResourceResponse])
async def list_resources(
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    type: ResourceType | None = Query(default=None),
    site: str | None = Query(default=None),
    status: ResourceStatus | None = Query(default=None),
    min_capacity: int | None = Query(default=None, ge=1, le=500),
    feature: str | None = Query(default=None),
    sort: str = Query(default="name", pattern="^(name|capacity|type)$"),
):
    return await ResourceService(session).list_resources(
        current,
        limit=limit,
        offset=offset,
        type_=type,
        site=site,
        status=status,
        min_capacity=min_capacity,
        feature=feature.strip().lower() if feature else None,
        sort=sort,
    )


@router.post("", response_model=ResourceResponse, status_code=201)
async def create_resource(
    payload: ResourceCreate,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await ResourceService(session).create_resource(current, payload)


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await ResourceService(session).get_resource(current, resource_id)


@router.patch("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    payload: ResourceUpdate,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await ResourceService(session).update_resource(current, resource_id, payload)


@router.delete("/{resource_id}", response_model=ResourceResponse)
async def delete_resource(
    resource_id: int,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await ResourceService(session).soft_delete(current, resource_id)
