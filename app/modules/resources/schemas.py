from __future__ import annotations

from datetime import time
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ResourceType(str, Enum):
    room = "room"
    equipment = "equipment"
    vehicle = "vehicle"


class ResourceStatus(str, Enum):
    active = "active"
    maintenance = "maintenance"
    out_of_service = "out_of_service"



FEATURES_BY_TYPE: dict[ResourceType, set[str]] = {
    ResourceType.room: {"projector", "whiteboard", "tv", "conference_phone"},
    ResourceType.equipment: {"laptop", "camera", "microphone"},
    ResourceType.vehicle: {"electric", "van", "gps"},
}


class ResourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    type: ResourceType

    capacity_max: int | None = Field(default=None, ge=1, le=500)

    description: str = Field(default="", max_length=1000)
    features: list[str] = Field(default_factory=list)

    site: str = Field(min_length=2, max_length=120)
    building: str = Field(default="", max_length=120)
    floor: str = Field(default="", max_length=50)
    room_number: str = Field(default="", max_length=50)

    status: ResourceStatus = ResourceStatus.active

    open_time: time | None = None
    close_time: time | None = None

    image_url: HttpUrl | None = None
    hourly_rate_internal: int | None = Field(default=None, ge=0)

    @field_validator("features")
    @classmethod
    def normalize_features(cls, v: list[str]) -> list[str]:
        return [x.strip().lower() for x in v if x.strip()]


class ResourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    capacity_max: int | None = Field(default=None, ge=1, le=500)
    description: str | None = Field(default=None, max_length=1000)
    features: list[str] | None = None

    site: str | None = Field(default=None, min_length=2, max_length=120)
    building: str | None = Field(default=None, max_length=120)
    floor: str | None = Field(default=None, max_length=50)
    room_number: str | None = Field(default=None, max_length=50)

    status: ResourceStatus | None = None

    open_time: time | None = None
    close_time: time | None = None

    image_url: HttpUrl | None = None
    hourly_rate_internal: int | None = Field(default=None, ge=0)

    @field_validator("features")
    @classmethod
    def normalize_features(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        return [x.strip().lower() for x in v if x.strip()]


class ResourceResponse(BaseModel):
    id: int
    name: str
    type: ResourceType
    capacity_max: int | None
    description: str
    features: list[str]
    site: str
    building: str
    floor: str
    room_number: str
    status: ResourceStatus
    open_time: time | None
    close_time: time | None
    image_url: str | None
    hourly_rate_internal: int | None

    class Config:
        from_attributes = True
