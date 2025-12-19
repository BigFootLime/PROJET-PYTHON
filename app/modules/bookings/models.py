from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no-show"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, name="booking_status"),
        nullable=False,
        default=BookingStatus.pending,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    participants: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[str] = mapped_column(String(1000), nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships are optional for the TP, but handy later
    resource = relationship("Resource")
    user = relationship("User")
