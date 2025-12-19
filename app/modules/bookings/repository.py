from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus


class BookingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, booking_id: int) -> Booking | None:
        res = await self.session.execute(select(Booking).where(Booking.id == booking_id))
        return res.scalar_one_or_none()

    async def list_for_user(self, user_id: int, limit: int, offset: int) -> list[Booking]:
        q = (
            select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.start_at.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(q)
        return list(res.scalars().all())

    async def has_conflict(
        self,
        *,
        resource_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_booking_id: int | None = None,
    ) -> bool:
        # Overlap rule: start < existing_end AND end > existing_start
        q = select(Booking.id).where(
            and_(
                Booking.resource_id == resource_id,
                Booking.status.in_([BookingStatus.pending, BookingStatus.confirmed]),
                Booking.start_at < end_at,
                Booking.end_at > start_at,
            )
        )
        if exclude_booking_id is not None:
            q = q.where(Booking.id != exclude_booking_id)

        res = await self.session.execute(q)
        return res.first() is not None

    async def create(self, booking: Booking) -> Booking:
        self.session.add(booking)
        await self.session.commit()
        await self.session.refresh(booking)
        return booking

    async def save(self, booking: Booking) -> Booking:
        await self.session.commit()
        await self.session.refresh(booking)
        return booking
