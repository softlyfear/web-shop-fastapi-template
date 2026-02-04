from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette import status

from app.core import SessionDep, templates
from app.crud import product_crud, review_crud
from app.models import Product
from app.schemas import ReviewCreate

router = APIRouter()


@router.get("/{slug}", response_class=HTMLResponse, name="product_detail")
async def product_detail(
    slug: str,
    request: Request,
    session: SessionDep,
):
    """Отображение детальной страницы товара."""
    stmt = (
        select(Product)
        .where(Product.slug == slug)
        .options(selectinload(Product.category))
    )
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )

    reviews = await review_crud.get_by_product_id(session, product.id, limit=10)

    avg_rating = await review_crud.get_average_rating(session, product.id)
    rating_counts = await review_crud.get_rating_counts(session, product.id)

    total_reviews = sum(rating_counts.values())

    user_id = request.session.get("user_id")
    user_review = None
    can_review = False

    if user_id:
        user_review = await review_crud.get_user_review_for_product(
            session, user_id, product.id
        )
        # TODO: Проверить, покупал ли пользователь этот товар
        # can_review = await has_purchased_product(session, user_id, product.id)
        can_review = not user_review  # Упрощенная версия

    return templates.TemplateResponse(
        request=request,
        name="product-detail.html",
        context={
            "request": request,
            "product": product,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "rating_counts": rating_counts,
            "total_reviews": total_reviews,
            "user_review": user_review,
            "can_review": can_review,
        },
    )


@router.post("/{slug}/review", name="product_add_review")
async def add_review(
    slug: str,
    request: Request,
    session: SessionDep,
    rating: int = Form(..., ge=1, le=5),
    comment: str | None = Form(None),
):
    """Добавить отзыв на товар."""
    user_id = request.session.get("user_id")
    if not user_id:
        request.session["flash_message"] = "Необходимо войти для добавления отзыва"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("login"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    product = await product_crud.get_by_slug(session, slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )

    review_data = ReviewCreate(
        product_id=product.id,
        user_id=user_id,
        rating=rating,
        comment=comment,
    )

    try:
        await review_crud.create_with_validation(session, review_data)
        request.session["flash_message"] = "Отзыв успешно добавлен"
        request.session["flash_type"] = "success"
    except ValueError as e:
        request.session["flash_message"] = str(e)
        request.session["flash_type"] = "error"
    except Exception as e:
        request.session["flash_message"] = f"Ошибка при добавлении отзыва: {str(e)}"
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("product_detail", slug=slug),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{slug}/add-to-cart", name="product_add_to_cart")
async def add_product_to_cart(
    slug: str,
    request: Request,
    session: SessionDep,
    quantity: int = Form(1, ge=1),
):
    """Добавить товар в корзину со страницы товара."""
    from app.utils.cart import CartManager

    product = await product_crud.get_by_slug(session, slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )

    try:
        await CartManager.add_to_cart(request, session, product.id, quantity)
        request.session["flash_message"] = f"Товар '{product.name}' добавлен в корзину"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = str(e)
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("product_detail", slug=slug),
        status_code=status.HTTP_303_SEE_OTHER,
    )
