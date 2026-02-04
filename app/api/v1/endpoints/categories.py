from fastapi import HTTPException, status

from app.api.v1.router_factory import build_crud_router
from app.core import SessionDep
from app.crud import category_crud
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate

# Базовые CRUD роуты
router = build_crud_router(
    crud=category_crud,
    create_schema=CategoryCreate,
    update_schema=CategoryUpdate,
    read_schema=CategoryRead,
    resource_name="category",
)


@router.get(
    "/slug/{slug}",
    name="Get category by slug",
    response_model=CategoryRead,
    status_code=status.HTTP_200_OK,
)
async def get_category_by_slug(
    slug: str,
    session: SessionDep,
):
    """Получить категорию по slug."""
    category = await category_crud.get_by_slug(session, slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
        )
    return category


@router.get(
    "/{category_id}/with-products",
    name="Get category with products",
    response_model=CategoryRead,
    status_code=status.HTTP_200_OK,
)
async def get_category_with_products(
    category_id: int,
    session: SessionDep,
):
    """Получить категорию со всеми продуктами (eager loading)."""
    category = await category_crud.get_with_products(session, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
        )
    return category


@router.get(
    "/stats/product-counts",
    name="Get categories with product counts",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
)
async def get_categories_with_product_counts(
    session: SessionDep,
):
    """Получить категории с количеством активных продуктов."""
    return await category_crud.get_categories_with_product_count(session)
