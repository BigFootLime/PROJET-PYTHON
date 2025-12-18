from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser
from app.modules.resources.models import Resource, ResourceStatus, ResourceType
from app.modules.resources.repository import ResourceRepository
from app.modules.resources.schemas import FEATURES_BY_TYPE, ResourceCreate, ResourceUpdate


def _forbidden() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error_code": "INSUFFICIENT_PERMISSIONS", "message": "Forbidden."},
    )


def _not_found(resource_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": "RESOURCE_NOT_FOUND", "message": f"Resource {resource_id} not found."},
    )


def _conflict_name_site() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error_code": "RESOURCE_NAME_ALREADY_USED",
            "message": "A resource with the same name already exists on this site.",
        },
    )


def _bad_request(msg: str, code: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error_code": code, "message": msg})


class ResourceService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ResourceRepository(session)

    async def list_resources(self, current: CurrentUser, **kwargs) -> list[Resource]:
        # Listing is readable by everyone (subject expects visibility)
        return await self.repo.list_resources(**kwargs)

    async def get_resource(self, current: CurrentUser, resource_id: int) -> Resource:
        resource = await self.repo.get_by_id(resource_id)
        if not resource:
            raise _not_found(resource_id)
        return resource

    async def create_resource(self, current: CurrentUser, payload: ResourceCreate) -> Resource:
        # Admin only for creation (subject)
        if current.role != "admin":
            raise _forbidden()

        # Capacity required for rooms
        if payload.type == ResourceType.room and payload.capacity_max is None:
            raise _bad_request("capacity_max is required for rooms.", "ROOM_CAPACITY_REQUIRED")

        # Features must match the type predefined set
        allowed = FEATURES_BY_TYPE[payload.type]
        unknown = [f for f in payload.features if f not in allowed]
        if unknown:
            raise _bad_request(f"Invalid features for {payload.type}: {unknown}", "INVALID_FEATURES")

        resource = Resource(
            name=payload.name,
            type=payload.type,
            capacity_max=payload.capacity_max,
            description=payload.description,
            features=payload.features,
            site=payload.site,
            building=payload.building,
            floor=payload.floor,
            room_number=payload.room_number,
            status=payload.status,
            open_time=payload.open_time,
            close_time=payload.close_time,
            image_url=str(payload.image_url) if payload.image_url else None,
            hourly_rate_internal=payload.hourly_rate_internal,
        )

        try:
            return await self.repo.create(resource)
        except IntegrityError:
            raise _conflict_name_site()

    async def update_resource(self, current: CurrentUser, resource_id: int, payload: ResourceUpdate) -> Resource:
        # Admin/manager can update (subject)
        if current.role not in {"admin", "manager"}:
            raise _forbidden()

        resource = await self.repo.get_by_id(resource_id)
        if not resource:
            raise _not_found(resource_id)

        # Apply patch
        for field, value in payload.model_dump(exclude_unset=True).items():
            if field == "image_url":
                setattr(resource, field, str(value) if value else None)
            else:
                setattr(resource, field, value)

        # Keep room rule consistent after patch
        if resource.type == ResourceType.room and resource.capacity_max is None:
            raise _bad_request("capacity_max is required for rooms.", "ROOM_CAPACITY_REQUIRED")

        # Validate features if provided
        if payload.features is not None:
            allowed = FEATURES_BY_TYPE[resource.type]
            unknown = [f for f in resource.features if f not in allowed]
            if unknown:
                raise _bad_request(f"Invalid features for {resource.type}: {unknown}", "INVALID_FEATURES")

        try:
            return await self.repo.save(resource)
        except IntegrityError:
            raise _conflict_name_site()

    async def soft_delete(self, current: CurrentUser, resource_id: int) -> Resource:
        # Admin only deletion (recommended logical delete)
        if current.role != "admin":
            raise _forbidden()

        resource = await self.repo.get_by_id(resource_id)
        if not resource:
            raise _not_found(resource_id)

        resource.is_deleted = True
        return await self.repo.save(resource)
