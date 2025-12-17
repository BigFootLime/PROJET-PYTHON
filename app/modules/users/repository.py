from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_users(self, limit: int, offset: int) -> list[User]:
        q = select(User).order_by(User.id).limit(limit).offset(offset)
        res = await self.session.execute(q)
        return list(res.scalars().all())

    async def get_by_id(self, user_id: int) -> User | None:
        res = await self.session.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(user)
        return user

    async def save(self, user: User) -> User:
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(user)
        return user
