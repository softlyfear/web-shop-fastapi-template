from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status

from app.core import SessionDep, templates
from app.core.security import AuthUtils
from app.crud import order_crud, user_crud
from app.models import OrderStatus

router = APIRouter()


def require_auth(request: Request) -> int:
    """Check authentication, return user_id or raise exception."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required",
        )
    return user_id


@router.get("/", response_class=HTMLResponse, name="account")
async def account_page(
    request: Request,
    session: SessionDep,
):
    """Main account page."""
    user_id = require_auth(request)

    # Get user
    user = await user_crud.get(session, user_id)
    if not user:
        # Clear only web user data, keep admin data
        request.session.pop("user_id", None)
        request.session.pop("username", None)
        request.session.pop("is_superuser", None)
        return RedirectResponse(
            url=request.url_for("login"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Get statistics
    stats = await user_crud.get_user_statistics(session, user_id)

    # Get recent orders
    recent_orders = await order_crud.get_by_user_id(session, user_id, limit=5)

    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={
            "request": request,
            "user": user,
            "stats": stats,
            "recent_orders": recent_orders,
        },
    )


@router.get("/orders", response_class=HTMLResponse, name="account_orders")
async def account_orders(
    request: Request,
    session: SessionDep,
    status_filter: str | None = None,
):
    """Order history page."""
    user_id = require_auth(request)

    # Get orders
    if status_filter:
        try:
            order_status = OrderStatus[status_filter]
            orders = await order_crud.get_user_orders_by_status(
                session, user_id, order_status, limit=50
            )
        except KeyError:
            orders = await order_crud.get_by_user_id(session, user_id, limit=50)
    else:
        orders = await order_crud.get_by_user_id(session, user_id, limit=50)

    return templates.TemplateResponse(
        request=request,
        name="account_orders.html",
        context={
            "request": request,
            "orders": orders,
            "status_filter": status_filter,
            "order_statuses": [s.value for s in OrderStatus],
        },
    )


@router.get(
    "/orders/{order_id}", response_class=HTMLResponse, name="account_order_detail"
)
async def account_order_detail(
    request: Request,
    session: SessionDep,
    order_id: int,
):
    """Order detail page."""
    user_id = require_auth(request)

    # Get order with items
    order = await order_crud.get_with_items(session, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Check access
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this order",
        )

    return templates.TemplateResponse(
        request=request,
        name="account_order_detail.html",
        context={
            "request": request,
            "order": order,
        },
    )


@router.post("/orders/{order_id}/cancel", name="account_order_cancel")
async def cancel_order(
    request: Request,
    session: SessionDep,
    order_id: int,
):
    """Cancel order (only for pending status)."""
    user_id = require_auth(request)

    # Get order
    order = await order_crud.get(session, order_id)

    if not order:
        request.session["flash_message"] = "Order not found"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_orders"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Check access
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this order",
        )

    # Check that order can be cancelled
    if order.status != OrderStatus.pending:
        request.session["flash_message"] = (
            f"Cannot cancel order with status '{order.status.value}'"
        )
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_order_detail", order_id=order_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Cancel order
    try:
        await order_crud.update_status(session, order, OrderStatus.cancelled)
        request.session["flash_message"] = "Order successfully cancelled"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Error cancelling order: {str(e)}"
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("account_order_detail", order_id=order_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/orders/{order_id}/edit", name="account_order_edit")
async def edit_order(
    request: Request,
    session: SessionDep,
    order_id: int,
    shipping_address: str = Form(..., min_length=10),
):
    """Change order shipping address (only for pending status)."""
    user_id = require_auth(request)

    # Get order
    order = await order_crud.get(session, order_id)

    if not order:
        request.session["flash_message"] = "Order not found"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_orders"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Check access
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this order",
        )

    # Check that order can be edited
    if order.status != OrderStatus.pending:
        request.session["flash_message"] = (
            f"Cannot edit order with status '{order.status.value}'"
        )
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_order_detail", order_id=order_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Update shipping address
    try:
        from app.schemas import OrderUpdate

        order_update = OrderUpdate(shipping_address=shipping_address)
        await order_crud.update(session, order, order_update)

        request.session["flash_message"] = "Shipping address successfully updated"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Error updating order: {str(e)}"
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("account_order_detail", order_id=order_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/profile", response_class=HTMLResponse, name="account_profile")
async def account_profile(
    request: Request,
    session: SessionDep,
):
    """Profile editing page."""
    user_id = require_auth(request)

    user = await user_crud.get(session, user_id)
    if not user:
        # Clear only web user data, keep admin data
        request.session.pop("user_id", None)
        request.session.pop("username", None)
        request.session.pop("is_superuser", None)
        return RedirectResponse(
            url=request.url_for("login"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        request=request,
        name="account_profile.html",
        context={
            "request": request,
            "user": user,
        },
    )


@router.post("/profile", name="account_profile_update")
async def account_profile_update(
    request: Request,
    session: SessionDep,
    email: str = Form(...),
    username: str = Form(..., min_length=3, max_length=20),
):
    """Update profile."""
    user_id = require_auth(request)

    user = await user_crud.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check username change
    if username != user.username:
        existing = await user_crud.get_user_by_username(session, username)
        if existing:
            request.session["flash_message"] = "Username already taken"
            request.session["flash_type"] = "error"
            return RedirectResponse(
                url=request.url_for("account_profile"),
                status_code=status.HTTP_303_SEE_OTHER,
            )

    # Check email change
    if email != user.email:
        existing = await user_crud.get_user_by_email(session, email)
        if existing:
            request.session["flash_message"] = "Email already registered"
            request.session["flash_type"] = "error"
            return RedirectResponse(
                url=request.url_for("account_profile"),
                status_code=status.HTTP_303_SEE_OTHER,
            )

    # Update data
    from app.schemas import UserUpdate

    user_update = UserUpdate(username=username, email=email)

    try:
        await user_crud.update(session, user, user_update)
        request.session["username"] = username  # Update session
        request.session["flash_message"] = "Profile updated"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Error: {str(e)}"
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("account_profile"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/password", response_class=HTMLResponse, name="account_password")
async def account_password_page(
    request: Request,
    session: SessionDep,
):
    """Password change page."""

    return templates.TemplateResponse(
        request=request,
        name="account_password.html",
        context={
            "request": request,
        },
    )


@router.post("/password", name="account_password_update")
async def account_password_update(
    request: Request,
    session: SessionDep,
    current_password: str = Form(...),
    new_password: str = Form(..., min_length=4),
    new_password_confirm: str = Form(...),
):
    """Update password."""
    user_id = require_auth(request)

    # Check new passwords match
    if new_password != new_password_confirm:
        request.session["flash_message"] = "New passwords do not match"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_password"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    user = await user_crud.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check current password
    if not AuthUtils.verify_password(current_password, user.hashed_password):
        request.session["flash_message"] = "Invalid current password"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_password"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Update password
    try:
        await user_crud.update_password(session, user, new_password)
        request.session["flash_message"] = "Password successfully changed"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Error: {str(e)}"
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("account_password"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
