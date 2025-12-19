from fastapi import APIRouter, Depends, Query

from app.core.db import AsyncSessionLocal
from app.core.security import CurrentUser, get_current_user
from app.modules.bookings.schemas import BookingCreate, BookingResponse, BookingUpdate
from app.modules.bookings.service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(
    payload: BookingCreate,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await BookingService(session).create_booking(current, payload)


@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    payload: BookingUpdate,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await BookingService(session).update_booking(current, booking_id, payload)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    current: CurrentUser = Depends(get_current_user),
    session=Depends(get_session),
):
    return await BookingService(session).cancel_booking(current, booking_id)
