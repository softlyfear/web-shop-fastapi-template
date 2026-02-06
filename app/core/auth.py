"""User authentication and registration logic."""

from fastapi import Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core import AuthUtils, SessionDep
from app.crud import user_crud
from app.models import User
from app.schemas import TokenPair, UserCreate


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> User:
    """Authenticate user by username and password."""
    user = await user_crud.get_user_by_username(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not AuthUtils.verify_password(
        password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )
    return user


async def register_user(
    session: AsyncSession,
    user_data: UserCreate,
) -> User:
    """Register new user with unique username and email."""
    existing_user = await user_crud.get_user_by_username(session, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )

    existing_email = await user_crud.get_user_by_email(session, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await user_crud.create(session, user_data)
    return user


async def validate_auth_user_form(
    session: SessionDep,
    username: str = Form(),
    password: str = Form(),
) -> User:
    """Validate user credentials from form data."""
    return await authenticate_user(session, username, password)


def create_token_pair(user: User) -> TokenPair:
    """Create access and refresh tokens for user."""
    access_token = AuthUtils.create_access_token(
        user_id=user.id, username=user.username
    )
    refresh_token = AuthUtils.create_refresh_token(user_id=user.id)

    return TokenPair(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )
