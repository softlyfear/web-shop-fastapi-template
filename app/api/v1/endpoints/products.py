"""Product API endpoints."""

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

# Base CRUD routes
router = build_crud_router(
    crud=product_crud,
    create_schema=ProductCreate,
    update_schema=ProductUpdate,
    read_schema=ProductRead,
    resource_name="product",
)


# Override GET / for filter support
@router.get(
    "/",
    name="Get products with filters",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK,
)
async def get_products_with_filters(
    session: SessionDep,
    search: str | None = Query(None, description="Search by name or description"),
    category_id: int | None = Query(None, description="Filter by category"),
    min_price: float | None = Query(None, ge=0, description="Minimum price"),
    max_price: float | None = Query(None, ge=0, description="Maximum price"),
    only_active: bool = Query(True, description="Only active products"),
    sort: str = Query(
        "newest",
        description="Sort: price_asc, price_desc, newest, oldest, name_asc, name_desc",
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """Get product list with filtering, search, and sorting.

    Parameters:
    - search: search by name or description
    - category_id: filter by category ID
    - min_price: minimum price
    - max_price: maximum price
    - only_active: show only active products
    - sort: sorting (price_asc, price_desc, newest, oldest, name_asc, name_desc)
    - offset: pagination offset
    - limit: results limit (max 100)
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
    """Get product by slug."""
    product = await product_crud.get_by_slug(session, slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
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
    """Get products by category."""
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
    """Get only active products."""
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
    threshold: int = Query(10, ge=0, description="Stock threshold"),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """Get low stock products (admins only)."""
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
    quantity_change: int = Query(..., description="Quantity change (+ add, - reduce)"),
):
    """Update product stock (admins only)."""
    try:
        return await product_crud.update_stock(session, product_id, quantity_change)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


# Product review endpoints


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
    """Get product reviews."""
    # Check product exists
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
    """Add product review (JWT required)."""
    # Check product exists
    await get_or_404(product_crud, session, product_id)

    # Check product_id matches
    if review_in.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product ID in URL and body do not match",
        )

    # Check user creates review on their behalf
    if review_in.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create reviews on your own behalf",
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
    """Get product rating statistics."""
    # Check product exists
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
