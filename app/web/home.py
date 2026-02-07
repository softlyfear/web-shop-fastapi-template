from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core import SessionDep, templates
from app.crud import category_crud, product_crud

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="home")
async def home(
    request: Request,
    session: SessionDep,
) -> HTMLResponse:
    """
    Display home page.
    Show categories and new/popular products.
    """
    # Get all categories with product count
    categories_with_counts = await category_crud.get_categories_with_product_count(
        session
    )

    # Get last 8 active products (new arrivals)
    featured_products = await product_crud.search_products(
        session=session,
        only_active=True,
        sort_by="newest",
        limit=8,
    )

    # Get popular products (can add logic based on order count)
    # For now, just get random active products
    popular_products = await product_crud.get_active_products(
        session=session,
        limit=4,
    )

    # Get current user information from session
    user_id = request.session.get("user_id")
    username = request.session.get("username")

    # Get number of items in cart
    from app.utils.cart import CartManager

    cart = CartManager.get_cart(request)
    cart_count = sum(item.get("quantity", 0) for item in cart.values())

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
            "categories": categories_with_counts,
            "featured_products": featured_products,
            "popular_products": popular_products,
            "user_id": user_id,
            "username": username,
            "cart_count": cart_count,
        },
    )
