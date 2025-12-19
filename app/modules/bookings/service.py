from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.bookings.repository import BookingRepository
from app.modules.bookings.schemas import BookingCreate, BookingUpdate
from app.modules.resources.models import ResourceStatus
from app.modules.resources.repository import ResourceRepository
from app.modules.users.repository import UserRepository
from app.utils.time_slots import minutes_between, now_utc, round_to_step, to_utc


def _not_found(kind: str, id_: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error_code": f"{kind.upper()}_NOT_FOUND", "message": f"{kind} {id_} not found."},
    )


def _forbidden() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error_code": "INSUFFICIENT_PERMISSIONS", "message": "Forbidden."},
    )


def _bad_request(code: str, msg: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error_code": code, "message": msg})


def _conflict(msg: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"error_code": "BOOKING_CONFLICT", "message": msg},
    )


class BookingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.bookings = BookingRepository(session)
        self.resources = ResourceRepository(session)
        self.users = UserRepository(session)

    async def create_booking(self, current: CurrentUser, payload: BookingCreate) -> Booking:
        user = await self.users.get_by_id(payload.user_id)
        if not user:
            raise _not_found("user", payload.user_id)
        if not user.is_active:
            raise _bad_request("USER_DISABLED", "This user account is disabled.")

        # Employee can only create for self (simple rule)
        if current.role == "employee" and current.user_id != payload.user_id:
            raise _forbidden()

        resource = await self.resources.get_by_id(payload.resource_id)
        if not resource:
            raise _not_found("resource", payload.resource_id)
        if resource.status in {ResourceStatus.maintenance, ResourceStatus.out_of_service}:
            raise _bad_request("RESOURCE_NOT_BOOKABLE", "Resource is not available for booking.")

        start_at = round_to_step(payload.start_at, 15)
        end_at = round_to_step(payload.end_at, 15)

        if end_at <= start_at:
            raise _bad_request("INVALID_TIME_SLOT", "end_at must be after start_at.")

        minutes = minutes_between(start_at, end_at)
        if minutes < 30:
            raise _bad_request("DURATION_TOO_SHORT", "Minimum duration is 30 minutes.")
        if minutes > 8 * 60:
            raise _bad_request("DURATION_TOO_LONG", "Maximum duration is 8 hours.")

        # No booking in the past (except admin)
        if current.role != "admin" and start_at < now_utc():
            raise _bad_request("PAST_BOOKING_NOT_ALLOWED", "Booking in the past is not allowed.")

        # Check user permission for resource type
        if resource.type.value not in user.allowed_resource_types and current.role != "admin":
            raise _forbidden()

        # Capacity rule for rooms
        if resource.type.value == "room" and resource.capacity_max is not None:
            if payload.participants > resource.capacity_max:
                raise _bad_request("CAPACITY_EXCEEDED", "Participants exceed room capacity.")

        # Conflict detection
        if await self.bookings.has_conflict(resource_id=resource.id, start_at=start_at, end_at=end_at):
            raise _conflict("This resource is already booked for this time slot.")

        status_init = BookingStatus.confirmed if current.role in {"admin", "manager"} else BookingStatus.pending

        booking = Booking(
            resource_id=resource.id,
            user_id=user.id,
            start_at=to_utc(start_at),
            end_at=to_utc(end_at),
            status=status_init,
            title=payload.title,
            participants=payload.participants,
            notes=payload.notes,
            created_at=datetime.now(timezone.utc),
        )
        return await self.bookings.create(booking)

    async def update_booking(self, current: CurrentUser, booking_id: int, payload: BookingUpdate) -> Booking:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise _not_found("booking", booking_id)

        # Creator can update, admin can update
        if current.role != "admin" and current.user_id != booking.user_id:
            raise _forbidden()

        data = payload.model_dump(exclude_unset=True)

        start_at = booking.start_at
        end_at = booking.end_at

        if "start_at" in data:
            start_at = round_to_step(data["start_at"], 15)
        if "end_at" in data:
            end_at = round_to_step(data["end_at"], 15)

        if end_at <= start_at:
            raise _bad_request("INVALID_TIME_SLOT", "end_at must be after start_at.")

        minutes = minutes_between(start_at, end_at)
        if minutes < 30:
            raise _bad_request("DURATION_TOO_SHORT", "Minimum duration is 30 minutes.")
        if minutes > 8 * 60:
            raise _bad_request("DURATION_TOO_LONG", "Maximum duration is 8 hours.")

        if current.role != "admin" and start_at < now_utc():
            raise _bad_request("PAST_BOOKING_NOT_ALLOWED", "Booking in the past is not allowed.")

        # Re-check conflicts if slot changed
        if ("start_at" in data) or ("end_at" in data):
            if await self.bookings.has_conflict(
                resource_id=booking.resource_id,
                start_at=start_at,
                end_at=end_at,
                exclude_booking_id=booking.id,
            ):
                raise _conflict("This resource is already booked for this time slot.")
            booking.start_at = to_utc(start_at)
            booking.end_at = to_utc(end_at)

        if "title" in data:
            booking.title = data["title"]
        if "participants" in data:
            booking.participants = data["participants"]
        if "notes" in data:
            booking.notes = data["notes"]

        return await self.bookings.save(booking)

    async def cancel_booking(self, current: CurrentUser, booking_id: int) -> Booking:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise _not_found("booking", booking_id)

        if current.role != "admin" and current.user_id != booking.user_id:
            raise _forbidden()

        booking.status = BookingStatus.cancelled
        return await self.bookings.save(booking)
