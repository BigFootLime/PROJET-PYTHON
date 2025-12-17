from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.base import Base


class UserRole(str, Enum):
    employee = "employee"
    manager = "manager"
    admin = "admin"

class UserPriority(str, Enum):
    standard = "standard"
    priority = "priority"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)

    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"), nullable=False)
    department: Mapped[str] = mapped_column(String(120), nullable=False)
    main_site: Mapped[str] = mapped_column(String(120), nullable=False)

    allowed_resource_types: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )

    priority: Mapped[UserPriority] = mapped_column(
        SAEnum(UserPriority, name="user_priority"), nullable=False, default=UserPriority.standard
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
