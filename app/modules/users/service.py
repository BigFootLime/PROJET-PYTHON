from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser
from app.modules.users.models import User, UserPriority, UserRole
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserPermissionsUpdate, UserUpdate

def _integrity_error_to_http() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error_code": "DUPLICATE_CONSTRAINT",
            "message": "Username or email already exists.",
        },
    )

def _not_found(user_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": "USER_NOT_FOUND", "message": f"User {user_id} not found."},
    )

def _forbidden() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error_code": "INSUFFICIENT_PERMISSIONS", "message": "Forbidden."},
    )

class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def list_users(self, current: CurrentUser, limit: int, offset: int) -> list[User]:
        if current.role not in {"admin", "manager"}:
            raise _forbidden()
        return await self.repo.list_users(limit=limit, offset=offset)

    async def get_user(self, current: CurrentUser, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise _not_found(user_id)

        # admin/manager can view anyone, employee can view self
        if current.role == "employee" and current.user_id != user_id:
            raise _forbidden()

        return user

    async def create_user(self, current: CurrentUser, payload: UserCreate) -> User:
        if current.role != "admin":
            raise _forbidden()

        user = User(
            username=payload.username,
            email=str(payload.email),
            full_name=payload.full_name,
            role=UserRole(payload.role.value),
            department=payload.department,
            main_site=payload.main_site,
            allowed_resource_types=payload.allowed_resource_types,
            priority=UserPriority(payload.priority.value),
            is_active=payload.is_active,
        )

        try:
            return await self.repo.create(user)
        except IntegrityError:
            raise _integrity_error_to_http()

    async def update_user(self, current: CurrentUser, user_id: int, payload: UserUpdate) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise _not_found(user_id)

        # admin can edit anyone; employee can edit self but only profile fields (here: same payload)
        if current.role == "employee" and current.user_id != user_id:
            raise _forbidden()

        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.department is not None:
            user.department = payload.department
        if payload.main_site is not None:
            user.main_site = payload.main_site

        try:
            return await self.repo.save(user)
        except IntegrityError:
            raise _integrity_error_to_http()

    async def update_permissions(
        self, current: CurrentUser, user_id: int, payload: UserPermissionsUpdate
    ) -> User:
        if current.role != "admin":
            raise _forbidden()

        user = await self.repo.get_by_id(user_id)
        if not user:
            raise _not_found(user_id)

        if payload.role is not None:
            user.role = UserRole(payload.role.value)
        if payload.allowed_resource_types is not None:
            user.allowed_resource_types = payload.allowed_resource_types
        if payload.priority is not None:
            user.priority = UserPriority(payload.priority.value)
        if payload.is_active is not None:
            user.is_active = payload.is_active

        try:
            return await self.repo.save(user)
        except IntegrityError:
            raise _integrity_error_to_http()

    async def deactivate(self, current: CurrentUser, user_id: int) -> User:
        if current.role != "admin":
            raise _forbidden()
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise _not_found(user_id)
        user.is_active = False
        return await self.repo.save(user)

    async def reactivate(self, current: CurrentUser, user_id: int) -> User:
        if current.role != "admin":
            raise _forbidden()
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise _not_found(user_id)
        user.is_active = True
        return await self.repo.save(user)
