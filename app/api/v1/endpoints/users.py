from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core import SessionDep
from app.crud import user_crud
from app.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    session: SessionDep,
    user_in: UserCreate,
):
    """Создать нового пользователя."""
    try:
        return await user_crud.create_user(session, user_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Такой username или email уже существует",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пароль не соответствует требованиям",
        )


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user(
    session: SessionDep,
    user_id: int,
):
    """Получить пользователя по ID."""
    user = await user_crud.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.get("/", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_users(
    session: SessionDep,
    offset: int = 0,
    limit: int = 20,
):
    """Получить всех пользователей."""
    return await user_crud.get_users(session, offset, limit)


@router.patch("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(
    session: SessionDep,
    user_id: int,
    user_in: UserUpdate,
):
    """Обновить пользователя по ID."""
    user = await user_crud.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await user_crud.update_user(session, user, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    session: SessionDep,
    user_id: int,
):
    """Удалить пользователя по ID."""
    user = await user_crud.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await user_crud.delete_user(session, user)
