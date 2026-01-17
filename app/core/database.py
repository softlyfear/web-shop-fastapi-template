from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings


class DatabaseEngine:
    async_engine = create_async_engine(
        url=settings.db.ASYNC_DATABASE_URL,
        echo=True,
        pool_size=5,
        max_overflow=10,
    )

    sync_engine = create_engine(url=settings.db.SYNC_DATABASE_URL, echo=False)
