from fastapi import APIRouter, Depends, Query
from app.core.db import AsyncSessionLocal
from app.core.security import CurrentUser, get_current_user
from app.modules.users.schemas import (
    UserCreate,
    UserPermissionsResponse,
    UserPermissionsUpdate,
    UserResponse,
    UserUpdate,
)
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("", response_model=list[UserResponse])
async def list_users(
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return await UserService(session).list_users(current, limit, offset)

@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreate,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await UserService(session).create_user(current, payload)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await UserService(session).get_user(current, user_id)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await UserService(session).update_user(current, user_id, payload)

@router.get("/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_permissions(
    user_id: int,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    u = await UserService(session).get_user(current, user_id)
    return UserPermissionsResponse(
        user_id=u.id,
        role=u.role,
        allowed_resource_types=u.allowed_resource_types,
        priority=u.priority,
        is_active=u.is_active,
    )

@router.patch("/{user_id}/permissions", response_model=UserResponse)
async def update_permissions(
    user_id: int,
    payload: UserPermissionsUpdate,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await UserService(session).update_permissions(current, user_id, payload)

@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await UserService(session).deactivate(current, user_id)

@router.post("/{user_id}/reactivate", response_model=UserResponse)
async def reactivate_user(
    user_id: int,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await UserService(session).reactivate(current, user_id)
