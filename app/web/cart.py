from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status

from app.core import SessionDep, templates
from app.utils.cart import CartManager

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="cart")
async def view_cart(
    request: Request,
    session: SessionDep,
):
    """Отображение страницы корзины."""
    cart_details = await CartManager.get_cart_details(request, session)

    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={
            "request": request,
            "items": cart_details["items"],
            "total_price": cart_details["total_price"],
            "total_items": cart_details["total_items"],
        },
    )


@router.post("/add", name="cart_add")
async def add_to_cart(
    request: Request,
    session: SessionDep,
    product_id: int = Form(...),
    quantity: int = Form(1),
):
    """Добавить товар в корзину (из формы)."""
    try:
        await CartManager.add_to_cart(request, session, product_id, quantity)
        request.session["flash_message"] = "Товар добавлен в корзину"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = str(e)
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("cart"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/update", name="cart_update")
async def update_cart(
    request: Request,
    session: SessionDep,
    product_id: int = Form(...),
    quantity: int = Form(...),
):
    """Обновить количество товара в корзине."""
    try:
        await CartManager.update_cart_item(request, session, product_id, quantity)
        request.session["flash_message"] = "Корзина обновлена"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = str(e)
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("cart"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/remove/{product_id}", name="cart_remove")
async def remove_from_cart(
    request: Request,
    product_id: int,
):
    """Удалить товар из корзины."""
    try:
        await CartManager.remove_from_cart(request, product_id)
        request.session["flash_message"] = "Товар удален из корзины"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = str(e)
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("cart"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/clear", name="cart_clear")
async def clear_cart(request: Request):
    """Очистить всю корзину."""
    CartManager.clear_cart(request)
    request.session["flash_message"] = "Корзина очищена"
    request.session["flash_type"] = "success"

    return RedirectResponse(
        url=request.url_for("cart"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
