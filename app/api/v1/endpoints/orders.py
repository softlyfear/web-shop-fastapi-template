"""Order API endpoints."""

from fastapi import HTTPException, Query, status

from app.api.v1.router_factory import build_crud_router
from app.api.v1.utils import get_or_404
from app.core import SessionDep
from app.core.deps import CurrentUser, SuperUser
from app.crud import order_crud
from app.models import OrderStatus
from app.schemas import OrderCreate, OrderItemCreate, OrderRead, OrderUpdate

# Base CRUD routes
router = build_crud_router(
    crud=order_crud,
    create_schema=OrderCreate,
    update_schema=OrderUpdate,
    read_schema=OrderRead,
    resource_name="order",
)


# Override GET / for current user orders
@router.get(
    "/",
    name="Get my orders",
    response_model=list[OrderRead],
    status_code=status.HTTP_200_OK,
)
async def get_my_orders(
    session: SessionDep,
    user: CurrentUser,
    status_filter: str | None = Query(None, description="Filter by order status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """Get current user orders (from JWT token)."""
    if status_filter:
        try:
            order_status = OrderStatus[status_filter]
            return await order_crud.get_user_orders_by_status(
                session, user.id, order_status, offset, limit
            )
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Available: {[s.value for s in OrderStatus]}",
            ) from None

    return await order_crud.get_by_user_id(session, user.id, offset, limit)


@router.get(
    "/user/{user_id}",
    name="Get orders by user ID",
    response_model=list[OrderRead],
    status_code=status.HTTP_200_OK,
)
async def get_user_orders(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """Get all user orders (own or admin)."""
    # Check: user can only see their own orders
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to another user's orders",
        ) from None
    return await order_crud.get_by_user_id(session, user_id, offset, limit)


@router.get(
    "/status/{status_value}",
    name="Get orders by status",
    response_model=list[OrderRead],
    status_code=status.HTTP_200_OK,
)
async def get_orders_by_status(
    status_value: str,
    session: SessionDep,
    admin: SuperUser,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """Get orders by status (admins only)."""
    try:
        order_status = OrderStatus[status_value]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Available: {[s.value for s in OrderStatus]}",
        ) from None

    return await order_crud.get_by_status(session, order_status, offset, limit)


@router.get(
    "/{order_id}/with-items",
    name="Get order with all items",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
)
async def get_order_with_items(
    order_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get order with all items (eager loading)."""
    order = await order_crud.get_with_items(session, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Access check
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No access to this order"
        )

    return order


@router.patch(
    "/{order_id}/status",
    name="Update order status",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
)
async def update_order_status(
    order_id: int,
    new_status: str = Query(..., description="New order status"),
    session: SessionDep = ...,
    current_user: CurrentUser = ...,
):
    """Update order status.

    - User can cancel own order only (status 'cancelled')
    - Admin can change any status
    """
    order = await get_or_404(order_crud, session, order_id)

    # Parse status
    try:
        status_enum = OrderStatus[new_status]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Available: {[s.value for s in OrderStatus]}",
        ) from None

    # Permission check
    if status_enum == OrderStatus.cancelled:
        # User can cancel own order
        if order.user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to this order",
            )
    else:
        # Other status changes only for admins
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change status",
            )

    return await order_crud.update_status(session, order, status_enum)


@router.post(
    "/create-with-items",
    name="Create order with items",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_with_items(
    order_in: OrderCreate,
    items_in: list[OrderItemCreate],
    session: SessionDep,
    user: CurrentUser,
):
    """Create order with all items atomically (alternative to checkout)."""
    # Ensure order is created for current user
    if order_in.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create orders for yourself",
        )

    if not items_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item",
        )

    # Convert items to format for create_order_with_items
    cart_items = [
        {
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": float(item.price) if item.price else 0,
        }
        for item in items_in
    ]

    try:
        return await order_crud.create_order_with_items(
            session=session,
            user_id=order_in.user_id,
            shipping_address=order_in.shipping_address,
            cart_items=cart_items,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
