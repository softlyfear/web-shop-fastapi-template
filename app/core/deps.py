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
    token = credentials.credentials
    try:
        payload = AuthUtils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка недопустимого токена: {exc}",
        ) from exc

    AuthUtils.validate_token_type(payload, "access")
    return payload


async def get_current_user(
    session: SessionDep,
    payload: dict = Depends(get_current_token_payload),  # noqa: B008
) -> User:
    user_id: int = int(payload.get("sub"))
    user = await user_crud.get(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильное имя пользователя или пароль",
        )
    return user


async def get_active_user(user: User = Depends(get_current_user)):  # noqa: B008
    if user.is_active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Пользователь не активен",
    )


async def get_superuser(user: User = Depends(get_active_user)) -> User:  # noqa: B008
    if not user.is_superuser:
        raise HTTPException(403, "Недостаточно разрешений")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_active_user)]
SuperUser = Annotated[User, Depends(get_superuser)]
