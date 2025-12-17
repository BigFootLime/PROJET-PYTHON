from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

"""Database connection and utilities."""

def build_db_url() -> str:
    pwd = quote_plus(settings.db_password)  # encode le + etc.
    return (
        f"postgresql+asyncpg://{settings.db_user}:{pwd}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )

engine: AsyncEngine = create_async_engine(
    build_db_url(),
    echo=(settings.env == "dev"),
    pool_pre_ping=True,
)

"""Asynchronous session maker for database interactions"""

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

"""Ping the database to check connectivity."""
async def db_ping() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.exec_driver_sql("SELECT 1;")
        return True
    except Exception:
        return False
