from datetime import datetime, timezone
from app.core.db import db_ping

"""Health check service"""



async def get_health() -> dict:

    """Get health status of the service."""
    db_ok = await db_ping()
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "project-reservation",
        "db": "up" if db_ok else "down",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
