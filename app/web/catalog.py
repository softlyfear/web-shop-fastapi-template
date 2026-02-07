from contextlib import suppress

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from app.core import SessionDep, templates
from app.crud import category_crud, product_crud

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="catalog")
async def get_catalog(
    request: Request,
    session: SessionDep,
    search: str | None = Query(None, description="Search by name or description"),
    category_id: str | None = Query(None, description="Filter by category"),
    min_price: str | None = Query(None, description="Minimum price"),
    max_price: str | None = Query(None, description="Maximum price"),
    sort: str = Query("newest", description="Sort by"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(12, ge=1, le=50, description="Items per page"),
):
    """
    Display product catalog page with filtering and search.

    Supports:
    - Search by name/description
    - Filter by category
    - Filter by price
    - Sorting
    - Pagination
    """
    # Convert category_id from string to int, ignoring empty values
    category_id_int = None
    if category_id and category_id.strip():
        with suppress(ValueError):
            category_id_int = int(category_id)

    # Convert prices from strings to float, ignoring empty values
    min_price_float = None
    max_price_float = None
    if min_price and min_price.strip():
        with suppress(ValueError):
            min_price_float = float(min_price)
    if max_price and max_price.strip():
        with suppress(ValueError):
            max_price_float = float(max_price)

    # Get all categories for filter
    categories = await category_crud.get_categories_with_product_count(session)

    # Get selected category to display name
    selected_category = None
    if category_id_int:
        selected_category = await category_crud.get(session, category_id_int)

    # Calculate offset for pagination
    offset = (page - 1) * per_page

    # Get products with filters
    products = await product_crud.search_products(
        session=session,
        search_query=search,
        category_id=category_id_int,
        min_price=min_price_float,
        max_price=max_price_float,
        only_active=True,
        sort_by=sort,
        offset=offset,
        limit=per_page,
    )

    # Get total product count for pagination (simplified)
    # In a real application, better to create a separate count method
    all_products = await product_crud.search_products(
        session=session,
        search_query=search,
        category_id=category_id_int,
        min_price=min_price_float,
        max_price=max_price_float,
        only_active=True,
        limit=1000,  # Get large number for counting
    )
    total_products = len(all_products)
    total_pages = (total_products + per_page - 1) // per_page

    # Get user information
    user_id = request.session.get("user_id")
    username = request.session.get("username")

    # Number of items in cart
    from app.utils.cart import CartManager

    cart = CartManager.get_cart(request)
    cart_count = sum(item.get("quantity", 0) for item in cart.values())

    # Sort options for UI display
    sort_options = [
        {"value": "newest", "label": "Newest"},
        {"value": "oldest", "label": "Oldest"},
        {"value": "price_asc", "label": "Price: Low to High"},
        {"value": "price_desc", "label": "Price: High to Low"},
        {"value": "name_asc", "label": "Name: A-Z"},
        {"value": "name_desc", "label": "Name: Z-A"},
    ]

    return templates.TemplateResponse(
        request=request,
        name="catalog.html",  # Use separate template for catalog
        context={
            "request": request,
            "products": products,
            "categories": categories,
            "selected_category": selected_category,
            "search": search,
            "category_id": category_id_int,
            "min_price": min_price,
            "max_price": max_price,
            "sort": sort,
            "sort_options": sort_options,
            "page": page,
            "per_page": per_page,
            "total_products": total_products,
            "total_pages": total_pages,
            "user_id": user_id,
            "username": username,
            "cart_count": cart_count,
        },
    )


@router.get("/category/{slug}", response_class=HTMLResponse, name="catalog_by_category")
async def get_catalog_by_category_slug(
    slug: str,
    request: Request,
    session: SessionDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
):
    """
    Product catalog for specific category (by slug).
    Example: /catalog/category/hops
    """
    # Find category by slug
    category = await category_crud.get_by_slug(session, slug)

    if not category:
        # Redirect to general catalog if category not found
        from fastapi.responses import RedirectResponse
        from starlette import status

        return RedirectResponse(
            url=request.url_for("catalog"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Redirect to main catalog with category filter
    from fastapi.responses import RedirectResponse
    from starlette import status

    return RedirectResponse(
        url=f"/catalog/?category_id={category.id}&page={page}&per_page={per_page}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
