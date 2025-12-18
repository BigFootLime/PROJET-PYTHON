from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.resources.models import Resource, ResourceStatus, ResourceType


class ResourceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, resource_id: int) -> Resource | None:
        res = await self.session.execute(
            select(Resource).where(and_(Resource.id == resource_id, Resource.is_deleted.is_(False)))
        )
        return res.scalar_one_or_none()

    async def list_resources(
        self,
        *,
        limit: int,
        offset: int,
        type_: ResourceType | None,
        site: str | None,
        status: ResourceStatus | None,
        min_capacity: int | None,
        feature: str | None,
        sort: str,
    ) -> list[Resource]:
        q = select(Resource).where(Resource.is_deleted.is_(False))

        if type_ is not None:
            q = q.where(Resource.type == type_)
        if site is not None:
            q = q.where(Resource.site.ilike(site))
        if status is not None:
            q = q.where(Resource.status == status)
        if min_capacity is not None:
            q = q.where(Resource.capacity_max >= min_capacity)
        if feature is not None:
            q = q.where(Resource.features.contains([feature]))

        if sort == "name":
            q = q.order_by(Resource.name.asc())
        elif sort == "capacity":
            q = q.order_by(Resource.capacity_max.asc().nulls_last())
        elif sort == "type":
            q = q.order_by(Resource.type.asc())

        q = q.limit(limit).offset(offset)
        res = await self.session.execute(q)
        return list(res.scalars().all())

    async def create(self, resource: Resource) -> Resource:
        self.session.add(resource)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(resource)
        return resource

    async def save(self, resource: Resource) -> Resource:
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(resource)
        return resource
