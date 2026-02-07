from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status

from app.core import SessionDep, templates
from app.crud import order_crud
from app.utils.cart import CartManager

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="checkout")
async def checkout_page(
    request: Request,
    session: SessionDep,
):
    """Display checkout page."""
    cart_details = await CartManager.get_cart_details(request, session)

    if not cart_details["items"]:
        request.session["flash_message"] = "Cart is empty"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("cart"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    user_id = request.session.get("user_id")
    if not user_id:
        request.session["flash_message"] = "Login required to checkout"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("login"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "request": request,
            "items": cart_details["items"],
            "total_price": cart_details["total_price"],
            "total_items": cart_details["total_items"],
        },
    )


@router.post("/", name="checkout_process")
async def process_checkout(
    request: Request,
    session: SessionDep,
    shipping_address: str = Form(..., min_length=10),
    payment_method: str = Form(default="cash"),
):
    """Process checkout."""
    # Check authentication
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required",
        )

    cart = CartManager.get_cart(request)

    if not cart:
        request.session["flash_message"] = "Cart is empty"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("cart"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    cart_items = [
        {
            "product_id": int(product_id),
            "quantity": item_data["quantity"],
            "price": item_data["price"],
        }
        for product_id, item_data in cart.items()
    ]

    try:
        order = await order_crud.create_order_with_items(
            session=session,
            user_id=user_id,
            shipping_address=shipping_address,
            cart_items=cart_items,
        )

        CartManager.clear_cart(request)

        # TODO: Send email notification (item 8)
        # await send_order_confirmation_email(order)

        request.session["flash_message"] = f"Order #{order.id} successfully created"
        request.session["flash_type"] = "success"

        return RedirectResponse(
            url=f"/account/orders/{order.id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except ValueError as e:
        request.session["flash_message"] = str(e)
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("checkout"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        request.session["flash_message"] = f"Error creating order: {str(e)}"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("checkout"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
