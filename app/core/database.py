# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core import settings

async_engine = create_async_engine(
    url=settings.db.ASYNC_DATABASE_URL,
    echo=settings.db.ECHO,
    pool_size=settings.db.POOL_SIZE,
    max_overflow=settings.db.MAX_OVERFLOW,
    pool_pre_ping=settings.db.POOL_PRE_PING,
    pool_recycle=settings.db.POOL_RECYCLE,
)

sync_engine = create_engine(
    url=settings.db.SYNC_DATABASE_URL,
    echo=settings.db.ECHO,
    pool_size=settings.db.POOL_SIZE,
    max_overflow=settings.db.MAX_OVERFLOW,
    pool_pre_ping=settings.db.POOL_PRE_PING,
    pool_recycle=settings.db.POOL_RECYCLE,
)

async_factory = async_sessionmaker(
    bind=async_engine,
    autoflush=settings.db.AUTOFLUSH,
    expire_on_commit=settings.db.EXPIRE_ON_COMMIT,
)

sync_factory = sessionmaker(
    bind=sync_engine,
    autoflush=settings.db.AUTOFLUSH,
    expire_on_commit=settings.db.EXPIRE_ON_COMMIT,
)
