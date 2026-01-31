from fastapi import APIRouter, HTTPException, status

from app.core import SessionDep
from app.crud import category_crud
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    session: SessionDep,
):
    """Создать категорию."""
    return await category_crud.create_category(session, category_in)


@router.get(
    "/{category_id}", response_model=CategoryRead, status_code=status.HTTP_200_OK
)
async def get_category(session: SessionDep, category_id: int):
    """Получить категорию по ID."""
    category = await category_crud.get_category(session, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return category


@router.get("/", response_model=list[CategoryRead], status_code=status.HTTP_200_OK)
async def get_categories(
    session: SessionDep,
    offset: int = 0,
    limit: int = 20,
):
    return await category_crud.get_categories(session, offset, limit)


@router.patch(
    "/{category_id}", response_model=CategoryRead, status_code=status.HTTP_200_OK
)
async def update_category(
    session: SessionDep,
    category_id: int,
    category_in: CategoryUpdate,
):
    """Обновление категории."""
    category = await category_crud.get_category(session, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await category_crud.update_category(session, category, category_in)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    session: SessionDep,
    category_id: int,
):
    """Удалить категорию по ID."""
    category = await category_crud.get_category(session, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await category_crud.delete_category(session, category)
