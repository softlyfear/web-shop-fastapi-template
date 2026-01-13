from sqlalchemy.ext.asyncio import create_async_engine

from config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
)
