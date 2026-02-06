"""Cart API endpoints."""

from fastapi import APIRouter, Request, status

from app.core import SessionDep
from app.schemas import CartItemAdd, CartItemUpdate, CartResponse
from app.utils.cart import CartManager

router = APIRouter()


@router.get(
    "/",
    name="Get cart",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
async def get_cart(
    request: Request,
    session: SessionDep,
):
    """Get cart contents."""
    cart_details = await CartManager.get_cart_details(request, session)
    return CartResponse(**cart_details)


@router.post(
    "/",
    name="Add item to cart",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def add_to_cart(
    item: CartItemAdd,
    request: Request,
    session: SessionDep,
):
    """Add item to cart."""
    await CartManager.add_to_cart(
        request,
        session,
        item.product_id,
        item.quantity,
    )
    return {"message": "Item added to cart"}


@router.patch(
    "/",
    name="Update cart item",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def update_cart_item(
    item: CartItemUpdate,
    request: Request,
    session: SessionDep,
):
    """Update cart item quantity."""
    await CartManager.update_cart_item(
        request,
        session,
        item.product_id,
        item.quantity,
    )
    return {"message": "Cart updated"}


@router.delete(
    "/{product_id}",
    name="Remove item from cart",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_from_cart(
    product_id: int,
    request: Request,
    session: SessionDep,
):
    """Remove item from cart."""
    await CartManager.remove_from_cart(request, product_id)


@router.delete(
    "/",
    name="Clear cart",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def clear_cart(request: Request):
    """Clear entire cart."""
    CartManager.clear_cart(request)
