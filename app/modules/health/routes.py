from fastapi import APIRouter
from app.modules.health.service import get_health

"""Health check routes"""

router = APIRouter(prefix="/health", tags=["Health"])

"""Health check endpoint"""

@router.get("")
async def healthcheck():
    return await get_health()
