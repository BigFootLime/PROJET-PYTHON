from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no-show"


class BookingCreate(BaseModel):
    resource_id: int = Field(ge=1)
    user_id: int = Field(ge=1)
    start_at: datetime
    end_at: datetime

    title: str = Field(min_length=2, max_length=200)
    participants: int = Field(ge=1, le=500)
    notes: str = Field(default="", max_length=1000)


class BookingUpdate(BaseModel):
    start_at: datetime | None = None
    end_at: datetime | None = None
    title: str | None = Field(default=None, min_length=2, max_length=200)
    participants: int | None = Field(default=None, ge=1, le=500)
    notes: str | None = Field(default=None, max_length=1000)


class BookingResponse(BaseModel):
    id: int
    resource_id: int
    user_id: int
    start_at: datetime
    end_at: datetime
    status: BookingStatus
    title: str
    participants: int
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True
