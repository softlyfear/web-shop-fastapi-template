"""FastAPI dependency injection utilities."""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core import get_async_session
from app.core.security import AuthUtils, http_bearer
from app.crud import user_crud
from app.models import User

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),  # noqa: B008
) -> dict:
    """Extract and validate JWT token payload."""
    token = credentials.credentials
    try:
        payload = AuthUtils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {exc}",
        ) from exc

    AuthUtils.validate_token_type(payload, "access")
    return payload


async def get_current_user(
    session: SessionDep,
    payload: dict = Depends(get_current_token_payload),  # noqa: B008
) -> User:
    """Get current user from JWT payload."""
    user_id: int = int(payload.get("sub"))
    user = await user_crud.get(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return user


async def get_active_user(user: User = Depends(get_current_user)):  # noqa: B008
    """Get current active user."""
    if user.is_active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is not active",
    )


async def get_superuser(user: User = Depends(get_active_user)) -> User:  # noqa: B008
    """Get current superuser."""
    if not user.is_superuser:
        raise HTTPException(403, "Insufficient permissions")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_active_user)]
SuperUser = Annotated[User, Depends(get_superuser)]
