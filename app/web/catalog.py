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
    search: str | None = Query(None, description="Поиск по названию или описанию"),
    category_id: str | None = Query(None, description="Фильтр по категории"),
    min_price: str | None = Query(None, description="Минимальная цена"),
    max_price: str | None = Query(None, description="Максимальная цена"),
    sort: str = Query("newest", description="Сортировка"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(12, ge=1, le=50, description="Товаров на странице"),
):
    """
    Отображение страницы каталога товаров с фильтрацией и поиском.

    Поддерживает:
    - Поиск по названию/описанию
    - Фильтрацию по категории
    - Фильтрацию по цене
    - Сортировку
    - Пагинацию
    """
    # Преобразуем category_id из строки в int, игнорируя пустые значения
    category_id_int = None
    if category_id and category_id.strip():
        with suppress(ValueError):
            category_id_int = int(category_id)

    # Преобразуем цены из строк в float, игнорируя пустые значения
    min_price_float = None
    max_price_float = None
    if min_price and min_price.strip():
        with suppress(ValueError):
            min_price_float = float(min_price)
    if max_price and max_price.strip():
        with suppress(ValueError):
            max_price_float = float(max_price)

    # Получаем все категории для фильтра
    categories = await category_crud.get_categories_with_product_count(session)

    # Получаем выбранную категорию для отображения имени
    selected_category = None
    if category_id_int:
        selected_category = await category_crud.get(session, category_id_int)

    # Вычисляем offset для пагинации
    offset = (page - 1) * per_page

    # Получаем товары с фильтрами
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

    # Получаем общее количество товаров для пагинации (упрощенно)
    # В реальном приложении лучше сделать отдельный метод count
    all_products = await product_crud.search_products(
        session=session,
        search_query=search,
        category_id=category_id_int,
        min_price=min_price_float,
        max_price=max_price_float,
        only_active=True,
        limit=1000,  # Берем большое число для подсчета
    )
    total_products = len(all_products)
    total_pages = (total_products + per_page - 1) // per_page

    # Получаем информацию о пользователе
    user_id = request.session.get("user_id")
    username = request.session.get("username")

    # Количество товаров в корзине
    from app.utils.cart import CartManager

    cart = CartManager.get_cart(request)
    cart_count = sum(item.get("quantity", 0) for item in cart.values())

    # Опции сортировки для отображения в UI
    sort_options = [
        {"value": "newest", "label": "Новинки"},
        {"value": "oldest", "label": "Старые"},
        {"value": "price_asc", "label": "Цена: по возрастанию"},
        {"value": "price_desc", "label": "Цена: по убыванию"},
        {"value": "name_asc", "label": "Название: А-Я"},
        {"value": "name_desc", "label": "Название: Я-А"},
    ]

    return templates.TemplateResponse(
        request=request,
        name="catalog.html",  # Используем отдельный шаблон для каталога
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
    Каталог товаров определенной категории (по slug).
    Например: /catalog/category/hops
    """
    # Находим категорию по slug
    category = await category_crud.get_by_slug(session, slug)

    if not category:
        # Редирект на общий каталог если категория не найдена
        from fastapi.responses import RedirectResponse
        from starlette import status

        return RedirectResponse(
            url=request.url_for("catalog"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Редирект на основной каталог с фильтром по категории
    from fastapi.responses import RedirectResponse
    from starlette import status

    return RedirectResponse(
        url=f"/catalog/?category_id={category.id}&page={page}&per_page={per_page}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
