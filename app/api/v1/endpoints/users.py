"""User API endpoints."""

from fastapi import HTTPException, status

from app.api.v1.router_factory import build_crud_router
from app.api.v1.utils import get_or_404
from app.core import SessionDep
from app.core.deps import ActiveUser, CurrentUser, SuperUser
from app.crud import user_crud
from app.schemas import UserCreate, UserRead, UserUpdate
from app.schemas.auth import PasswordUpdate

router = build_crud_router(
    crud=user_crud,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    read_schema=UserRead,
    resource_name="user",
)


@router.get(
    "/username/{username}",
    name="Get user by username",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_username(
    username: str,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get user by username (authenticated only)."""
    user = await user_crud.get_user_by_username(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get(
    "/active/",
    name="Get active users",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
)
async def get_active_users(
    session: SessionDep,
    admin: SuperUser,
    offset: int = 0,
    limit: int = 25,
):
    """Get active users (admins only)."""
    return await user_crud.get_active_users(session, offset, limit)


@router.patch(
    "/{user_id}/toggle-active",
    name="Toggle user active status",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def toggle_user_active_status(
    user_id: int,
    session: SessionDep,
    admin: SuperUser,
):
    """Toggle user active status (admins only)."""
    user = await get_or_404(user_crud, session, user_id)
    return await user_crud.toggle_active_status(session, user)


@router.post(
    "/me/change-password",
    name="Change current user password",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def change_my_password(
    password_data: PasswordUpdate,
    session: SessionDep,
    user: ActiveUser,
):
    """Change current user password."""
    from app.core.security import AuthUtils

    if not AuthUtils.verify_password(
        password_data.current_password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password"
        )

    await user_crud.update_password(session, user, password_data.new_password)
    return {"message": "Password successfully changed"}


@router.get(
    "/{user_id}/statistics",
    name="Get user statistics",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_user_statistics(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get user statistics."""
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to another user's statistics",
        )

    return await user_crud.get_user_statistics(session, user_id)


@router.get(
    "/me/statistics",
    name="Get current user statistics",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_my_statistics(
    session: SessionDep,
    user: ActiveUser,
):
    """Get current user statistics."""
    return await user_crud.get_user_statistics(session, user.id)
