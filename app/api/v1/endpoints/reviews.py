"""Review API endpoints."""

from fastapi import HTTPException, status

from app.api.v1.router_factory import build_crud_router
from app.core import SessionDep
from app.core.deps import ActiveUser, CurrentUser
from app.crud import review_crud
from app.schemas import ReviewCreate, ReviewRead, ReviewUpdate

router = build_crud_router(
    crud=review_crud,
    create_schema=ReviewCreate,
    update_schema=ReviewUpdate,
    read_schema=ReviewRead,
    resource_name="review",
)


@router.get(
    "/product/{product_id}",
    name="Get reviews by product ID",
    response_model=list[ReviewRead],
    status_code=status.HTTP_200_OK,
)
async def get_product_reviews(
    product_id: int,
    session: SessionDep,
    offset: int = 0,
    limit: int = 25,
):
    """Get all reviews for product."""
    return await review_crud.get_by_product_id(session, product_id, offset, limit)


@router.get(
    "/user/{user_id}",
    name="Get reviews by user ID",
    response_model=list[ReviewRead],
    status_code=status.HTTP_200_OK,
)
async def get_user_reviews(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    offset: int = 0,
    limit: int = 25,
):
    """Get all user reviews."""
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to another user's reviews",
        )
    return await review_crud.get_by_user_id(session, user_id, offset, limit)


@router.get(
    "/my/reviews",
    name="Get current user's reviews",
    response_model=list[ReviewRead],
    status_code=status.HTTP_200_OK,
)
async def get_my_reviews(
    session: SessionDep,
    user: ActiveUser,
    offset: int = 0,
    limit: int = 25,
):
    """Get current user reviews."""
    return await review_crud.get_by_user_id(session, user.id, offset, limit)


@router.get(
    "/product/{product_id}/user/{user_id}",
    name="Get user's review for product",
    response_model=ReviewRead | None,
    status_code=status.HTTP_200_OK,
)
async def get_user_product_review(
    product_id: int,
    user_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Check if user has reviewed product."""
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to another user's reviews",
        )
    return await review_crud.get_user_review_for_product(session, user_id, product_id)


@router.post(
    "/create-validated",
    name="Create review with validation",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_review_validated(
    review_in: ReviewCreate,
    session: SessionDep,
    user: ActiveUser,
):
    """Create review with duplicate check."""
    if review_in.user_id != user.id and not user.is_superuser:
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
    "/product/{product_id}/rating",
    name="Get average rating for product",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_product_rating(
    product_id: int,
    session: SessionDep,
):
    """Get product average rating."""
    avg_rating = await review_crud.get_average_rating(session, product_id)
    return {
        "product_id": product_id,
        "average_rating": avg_rating,
    }


@router.get(
    "/product/{product_id}/rating-stats",
    name="Get rating statistics for product",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_product_rating_stats(
    product_id: int,
    session: SessionDep,
):
    """Get detailed product rating statistics."""
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
