from __future__ import annotations

from datetime import time
from enum import Enum

from sqlalchemy import Boolean, Enum as SAEnum, Integer, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class ResourceType(str, Enum):
    room = "room"
    equipment = "equipment"
    vehicle = "vehicle"


class ResourceStatus(str, Enum):
    active = "active"
    maintenance = "maintenance"
    out_of_service = "out_of_service"


class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = (UniqueConstraint("name", "site", name="uq_resources_name_site"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[ResourceType] = mapped_column(SAEnum(ResourceType, name="resource_type"), nullable=False)


    capacity_max: Mapped[int | None] = mapped_column(Integer, nullable=True)

    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    features: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)

    site: Mapped[str] = mapped_column(String(120), nullable=False)
    building: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    floor: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    room_number: Mapped[str] = mapped_column(String(50), nullable=False, default="")

    status: Mapped[ResourceStatus] = mapped_column(
        SAEnum(ResourceStatus, name="resource_status"),
        nullable=False,
        default=ResourceStatus.active,
    )

    open_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    close_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    hourly_rate_internal: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
