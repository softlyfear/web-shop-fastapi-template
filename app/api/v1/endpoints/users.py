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
    """Получить пользователя по username (только для авторизованных)."""
    user = await user_crud.get_user_by_username(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
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
    """Получить активных пользователей (только для администраторов)."""
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
    """Переключить статус активности пользователя (только для администраторов)."""
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
    """Изменить пароль текущего пользователя."""
    from app.core.security import AuthUtils

    if not AuthUtils.verify_password(
        password_data.current_password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный текущий пароль"
        )

    await user_crud.update_password(session, user, password_data.new_password)
    return {"message": "Пароль успешно изменен"}


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
    """Получить статистику пользователя."""
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к статистике другого пользователя",
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
    """Получить статистику текущего пользователя."""
    return await user_crud.get_user_statistics(session, user.id)
