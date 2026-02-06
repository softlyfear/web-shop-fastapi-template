"""Core application components."""

from app.core.config import settings
from app.core.database import async_engine, async_session, get_async_session
from app.core.deps import SessionDep
from app.core.handlers import register_exception_handlers
from app.core.security import AuthUtils
from app.core.templates import templates

__all__ = [
    "settings",
    "templates",
    "async_engine",
    "async_session",
    "get_async_session",
    "SessionDep",
    "register_exception_handlers",
    "AuthUtils",
]
