from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserRole(str, Enum):
    employee = "employee"
    manager = "manager"
    admin = "admin"

class UserPriority(str, Enum):
    standard = "standard"
    priority = "priority"

ALLOWED_RESOURCE_TYPES = {"room", "equipment", "vehicle"}

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    role: UserRole
    department: str = Field(min_length=2, max_length=120)
    main_site: str = Field(min_length=2, max_length=120)
    allowed_resource_types: list[str] = Field(default_factory=list)
    priority: UserPriority = UserPriority.standard
    is_active: bool = True

    @field_validator("allowed_resource_types")
    @classmethod
    def validate_allowed_types(cls, v: list[str]) -> list[str]:
        normalized = [x.strip().lower() for x in v]
        unknown = [x for x in normalized if x not in ALLOWED_RESOURCE_TYPES]
        if unknown:
            raise ValueError(f"Invalid resource types: {unknown}")
        return normalized

class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    department: str | None = Field(default=None, min_length=2, max_length=120)
    main_site: str | None = Field(default=None, min_length=2, max_length=120)

class UserPermissionsUpdate(BaseModel):
    role: UserRole | None = None
    allowed_resource_types: list[str] | None = None
    priority: UserPriority | None = None
    is_active: bool | None = None

    @field_validator("allowed_resource_types")
    @classmethod
    def validate_allowed_types(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        normalized = [x.strip().lower() for x in v]
        unknown = [x for x in normalized if x not in ALLOWED_RESOURCE_TYPES]
        if unknown:
            raise ValueError(f"Invalid resource types: {unknown}")
        return normalized

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    department: str
    main_site: str
    allowed_resource_types: list[str]
    priority: UserPriority
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserPermissionsResponse(BaseModel):
    user_id: int
    role: UserRole
    allowed_resource_types: list[str]
    priority: UserPriority
    is_active: bool
