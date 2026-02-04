from fastapi import HTTPException, Query, status

from app.api.v1.router_factory import build_crud_router
from app.api.v1.utils import get_or_404
from app.core import SessionDep
from app.core.deps import CurrentUser, SuperUser
from app.crud import product_crud, review_crud
from app.schemas import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ReviewCreate,
    ReviewRead,
)

# Базовые CRUD роуты
router = build_crud_router(
    crud=product_crud,
    create_schema=ProductCreate,
    update_schema=ProductUpdate,
    read_schema=ProductRead,
    resource_name="product",
)


# Переопределяем GET / для поддержки фильтров
@router.get(
    "/",
    name="Get products with filters",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK,
)
async def get_products_with_filters(
    session: SessionDep,
    search: str | None = Query(None, description="Поиск по названию или описанию"),
    category_id: int | None = Query(None, description="Фильтр по категории"),
    min_price: float | None = Query(None, ge=0, description="Минимальная цена"),
    max_price: float | None = Query(None, ge=0, description="Максимальная цена"),
    only_active: bool = Query(True, description="Только активные товары"),
    sort: str = Query(
        "newest",
        description="Сортировка: price_asc, price_desc, "
        "newest, oldest, name_asc, name_desc",
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """
    Получить список товаров с фильтрацией, поиском и сортировкой.

    Параметры:
    - search: поиск по названию или описанию
    - category_id: фильтр по ID категории
    - min_price: минимальная цена
    - max_price: максимальная цена
    - only_active: показывать только активные товары
    - sort: сортировка (price_asc, price_desc, newest, oldest, name_asc, name_desc)
    - offset: смещение для пагинации
    - limit: количество результатов (макс 100)
    """
    return await product_crud.search_products(
        session=session,
        search_query=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        only_active=only_active,
        sort_by=sort,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/slug/{slug}",
    name="Get product by slug",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
)
async def get_product_by_slug(
    slug: str,
    session: SessionDep,
):
    """Получить продукт по slug."""
    product = await product_crud.get_by_slug(session, slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Продукт не найден"
        )
    return product


@router.get(
    "/category/{category_id}/products",
    name="Get products by category",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: int,
    session: SessionDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    only_active: bool = Query(True),
):
    """Получить продукты категории."""
    return await product_crud.get_by_category(
        session, category_id, offset, limit, only_active
    )


@router.get(
    "/active/",
    name="Get active products",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK,
)
async def get_active_products(
    session: SessionDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """Получить только активные продукты."""
    return await product_crud.get_active_products(session, offset, limit)


@router.get(
    "/low-stock/",
    name="Get low stock products",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK,
)
async def get_low_stock_products(
    session: SessionDep,
    admin: SuperUser,
    threshold: int = Query(10, ge=0, description="Порог остатка"),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """Получить продукты с низким остатком (для администраторов)."""
    return await product_crud.get_low_stock_products(session, threshold, offset, limit)


@router.patch(
    "/{product_id}/stock",
    name="Update product stock",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
)
async def update_product_stock(
    product_id: int,
    session: SessionDep,
    admin: SuperUser,
    quantity_change: int = Query(
        ..., description="Изменение количества (+ добавить, - уменьшить)"
    ),
):
    """Обновить остаток товара (только для администраторов)."""
    try:
        return await product_crud.update_stock(session, product_id, quantity_change)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


# Эндпоинты для отзывов в контексте продукта (требование ТЗ)


@router.get(
    "/{product_id}/reviews/",
    name="Get product reviews",
    response_model=list[ReviewRead],
    status_code=status.HTTP_200_OK,
)
async def get_product_reviews(
    product_id: int,
    session: SessionDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """Получить отзывы продукта (требование ТЗ: GET /api/v1/products/{id}/reviews/)."""
    # Проверяем существование продукта
    await get_or_404(product_crud, session, product_id)

    return await review_crud.get_by_product_id(session, product_id, offset, limit)


@router.post(
    "/{product_id}/reviews/",
    name="Create product review",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_review(
    product_id: int,
    review_in: ReviewCreate,
    session: SessionDep,
    user: CurrentUser,
):
    """
    Добавить отзыв на продукт (требование ТЗ: POST /api/v1/products/{id}/reviews/).
    Требуется JWT авторизация.
    """
    # Проверяем существование продукта
    await get_or_404(product_crud, session, product_id)

    # Проверяем что product_id совпадает
    if review_in.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product ID в URL и в теле запроса не совпадают",
        )

    # Проверяем что пользователь создает отзыв от своего имени
    if review_in.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно создавать отзывы только от своего имени",
        )

    try:
        return await review_crud.create_with_validation(session, review_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get(
    "/{product_id}/reviews/rating",
    name="Get product rating statistics",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_product_rating_stats(
    product_id: int,
    session: SessionDep,
):
    """Получить статистику оценок продукта."""
    # Проверяем существование продукта
    await get_or_404(product_crud, session, product_id)

    avg_rating = await review_crud.get_average_rating(session, product_id)
    rating_counts = await review_crud.get_rating_counts(session, product_id)

    total_reviews = sum(rating_counts.values())

    return {
        "product_id": product_id,
        "average_rating": avg_rating,
        "total_reviews": total_reviews,
        "rating_distribution": {
            "5_stars": rating_counts.get(5, 0),
            "4_stars": rating_counts.get(4, 0),
            "3_stars": rating_counts.get(3, 0),
            "2_stars": rating_counts.get(2, 0),
            "1_star": rating_counts.get(1, 0),
        },
    }
