"""Order item API endpoints."""

from fastapi import HTTPException, status

from app.api.v1.router_factory import build_crud_router
from app.api.v1.utils import get_or_404
from app.core import SessionDep
from app.core.deps import CurrentUser
from app.crud import order_crud, order_item_crud
from app.schemas import OrderItemCreate, OrderItemRead, OrderItemUpdate

router = build_crud_router(
    crud=order_item_crud,
    create_schema=OrderItemCreate,
    update_schema=OrderItemUpdate,
    read_schema=OrderItemRead,
    resource_name="order_item",
)

router.get(
    "/order/{order_id}",
    name="Get items by order ID",
    response_model=list[OrderItemRead],
    status_code=status.HTTP_200_OK,
)


async def get_order_items(
    order_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get all order items."""
    order = await get_or_404(order_crud, session, order_id)

    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No access to this order"
        )

    return await order_item_crud.get_by_order_id(session, order_id)


@router.post(
    "/order/{order_id}/add",
    name="Add item to order",
    response_model=OrderItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_item_to_order(
    order_id: int,
    item_in: OrderItemCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Add item to order with stock validation."""
    order = await get_or_404(order_crud, session, order_id)

    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No access to this order"
        )

    try:
        return await order_item_crud.create_with_validation(session, item_in, order_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get(
    "/order/{order_id}/total",
    name="Calculate order total",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def calculate_order_total(
    order_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Calculate order total price."""
    order = await get_or_404(order_crud, session, order_id)

    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No access to this order"
        )

    total = await order_item_crud.calculate_order_total(session, order_id)
    return {"order_id": order_id, "total_price": total}
