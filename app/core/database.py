from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
)


async_session = async_sessionmaker(async_engine)
