"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, status
from jwt import InvalidTokenError

from app.core import AuthUtils
from app.core.auth import authenticate_user, create_token_pair, register_user
from app.core.deps import ActiveUser, SessionDep
from app.crud import user_crud
from app.schemas import (
    LoginRequest,
    RefreshRequest,
    TokenInfo,
    TokenPair,
    UserCreate,
    UserInfo,
)

router = APIRouter()


@router.post("/login", response_model=TokenPair)
async def login(
    session: SessionDep,
    credentials: LoginRequest,
):
    """User login - returns token pair."""
    user = await authenticate_user(session, credentials.username, credentials.password)
    tokens = create_token_pair(user)
    return tokens


@router.post("/register", response_model=TokenPair)
async def register(
    session: SessionDep,
    user_data: UserCreate,
):
    """Register new user."""
    user = await register_user(session, user_data)
    tokens = create_token_pair(user)
    return tokens


@router.post("/refresh", response_model=TokenInfo)
async def refresh(
    session: SessionDep,
    data: RefreshRequest,
):
    """Refresh access token."""
    # Decode refresh token
    try:
        payload = AuthUtils.decode_jwt(data.refresh_token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {exc}",
        ) from exc

    AuthUtils.validate_token_type(payload, "refresh")
    user_id = int(payload.get("sub"))
    user = await user_crud.get(session, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )

    access_token = AuthUtils.create_access_token(
        user_id=user.id,
        username=user.username,
    )

    return TokenInfo(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserInfo)
async def get_me(
    user: ActiveUser,
):
    """Get current user info."""
    return UserInfo(
        username=user.username,
        email=user.email,
        logged_in_at=None,
    )
