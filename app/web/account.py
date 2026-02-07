from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status

from app.core import SessionDep, templates
from app.core.security import AuthUtils
from app.crud import order_crud, user_crud
from app.models import OrderStatus

router = APIRouter()


def require_auth(request: Request) -> int:
    """Проверка авторизации, возвращает user_id или редирект."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходимо войти в систему",
        )
    return user_id


@router.get("/", response_class=HTMLResponse, name="account")
async def account_page(
    request: Request,
    session: SessionDep,
):
    """Главная страница личного кабинета."""
    user_id = require_auth(request)

    # Получаем пользователя
    user = await user_crud.get(session, user_id)
    if not user:
        # Очищаем только данные веб-пользователя, сохраняя админские
        request.session.pop("user_id", None)
        request.session.pop("username", None)
        request.session.pop("is_superuser", None)
        return RedirectResponse(
            url=request.url_for("login"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Получаем статистику
    stats = await user_crud.get_user_statistics(session, user_id)

    # Получаем последние заказы
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
    """Страница истории заказов."""
    user_id = require_auth(request)

    # Получаем заказы
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
    """Детальная информация о заказе."""
    user_id = require_auth(request)

    # Получаем заказ с items
    order = await order_crud.get_with_items(session, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден",
        )

    # Проверяем доступ
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому заказу",
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
    """Отменить заказ (только для статуса pending)."""
    user_id = require_auth(request)

    # Получаем заказ
    order = await order_crud.get(session, order_id)

    if not order:
        request.session["flash_message"] = "Заказ не найден"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_orders"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Проверяем доступ
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому заказу",
        )

    # Проверяем, что заказ можно отменить
    if order.status != OrderStatus.pending:
        request.session["flash_message"] = (
            f"Невозможно отменить заказ со статусом '{order.status.value}'"
        )
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_order_detail", order_id=order_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Отменяем заказ
    try:
        await order_crud.update_status(session, order, OrderStatus.cancelled)
        request.session["flash_message"] = "Заказ успешно отменен"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Ошибка при отмене заказа: {str(e)}"
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
    """Изменить адрес доставки заказа (только для статуса pending)."""
    user_id = require_auth(request)

    # Получаем заказ
    order = await order_crud.get(session, order_id)

    if not order:
        request.session["flash_message"] = "Заказ не найден"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_orders"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Проверяем доступ
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому заказу",
        )

    # Проверяем, что заказ можно редактировать
    if order.status != OrderStatus.pending:
        request.session["flash_message"] = (
            f"Невозможно редактировать заказ со статусом '{order.status.value}'"
        )
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_order_detail", order_id=order_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Обновляем адрес доставки
    try:
        from app.schemas import OrderUpdate

        order_update = OrderUpdate(shipping_address=shipping_address)
        await order_crud.update(session, order, order_update)

        request.session["flash_message"] = "Адрес доставки успешно обновлен"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Ошибка при обновлении заказа: {str(e)}"
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
    """Страница редактирования профиля."""
    user_id = require_auth(request)

    user = await user_crud.get(session, user_id)
    if not user:
        # Очищаем только данные веб-пользователя, сохраняя админские
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
    """Обновление профиля."""
    user_id = require_auth(request)

    user = await user_crud.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем изменение username
    if username != user.username:
        existing = await user_crud.get_user_by_username(session, username)
        if existing:
            request.session["flash_message"] = "Имя пользователя уже занято"
            request.session["flash_type"] = "error"
            return RedirectResponse(
                url=request.url_for("account_profile"),
                status_code=status.HTTP_303_SEE_OTHER,
            )

    # Проверяем изменение email
    if email != user.email:
        existing = await user_crud.get_user_by_email(session, email)
        if existing:
            request.session["flash_message"] = "Email уже зарегистрирован"
            request.session["flash_type"] = "error"
            return RedirectResponse(
                url=request.url_for("account_profile"),
                status_code=status.HTTP_303_SEE_OTHER,
            )

    # Обновляем данные
    from app.schemas import UserUpdate

    user_update = UserUpdate(username=username, email=email)

    try:
        await user_crud.update(session, user, user_update)
        request.session["username"] = username  # Обновляем сессию
        request.session["flash_message"] = "Профиль обновлен"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Ошибка: {str(e)}"
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
    """Страница смены пароля."""

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
    """Обновление пароля."""
    user_id = require_auth(request)

    # Проверяем совпадение новых паролей
    if new_password != new_password_confirm:
        request.session["flash_message"] = "Новые пароли не совпадают"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_password"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    user = await user_crud.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем текущий пароль
    if not AuthUtils.verify_password(current_password, user.hashed_password):
        request.session["flash_message"] = "Неверный текущий пароль"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("account_password"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Обновляем пароль
    try:
        await user_crud.update_password(session, user, new_password)
        request.session["flash_message"] = "Пароль успешно изменен"
        request.session["flash_type"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Ошибка: {str(e)}"
        request.session["flash_type"] = "error"

    return RedirectResponse(
        url=request.url_for("account_password"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
