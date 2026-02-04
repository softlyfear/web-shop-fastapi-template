from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status

from app.core import SessionDep, templates
from app.core.security import AuthUtils
from app.crud import user_crud
from app.schemas import UserCreate

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="login")
async def get_login(request: Request) -> HTMLResponse:
    """Отображение страницы входа в систему."""
    # Если пользователь уже авторизован, редирект в личный кабинет
    if request.session.get("user_id"):
        return RedirectResponse(
            url=request.url_for("account"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
        },
    )


@router.post("/", name="login_process")
async def login_process(
    request: Request,
    session: SessionDep,
    username: str = Form(...),
    password: str = Form(...),
):
    """Обработка входа в систему."""
    # Находим пользователя
    user = await user_crud.get_user_by_username(session, username)

    # Проверяем пользователя и пароль
    if not user or not AuthUtils.verify_password(password, user.hashed_password):
        request.session["flash_message"] = "Неверное имя пользователя или пароль"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("login"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Проверяем активность пользователя
    if not user.is_active:
        request.session["flash_message"] = "Аккаунт деактивирован"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("login"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Сохраняем пользователя в сессии
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["is_superuser"] = user.is_superuser

    request.session["flash_message"] = f"Добро пожаловать, {user.username}!"
    request.session["flash_type"] = "success"

    # Редирект в личный кабинет или на главную
    return RedirectResponse(
        url=request.url_for("account"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/register", response_class=HTMLResponse, name="register")
async def get_register(request: Request) -> HTMLResponse:
    """Отображение страницы регистрации."""
    # Если пользователь уже авторизован, редирект
    if request.session.get("user_id"):
        return RedirectResponse(
            url=request.url_for("account"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request,
        },
    )


@router.post("/register", name="register_process")
async def register_process(
    request: Request,
    session: SessionDep,
    username: str = Form(..., min_length=3, max_length=20),
    email: str = Form(...),
    password: str = Form(..., min_length=4),
    password_confirm: str = Form(...),
):
    """Обработка регистрации."""
    # Проверка совпадения паролей
    if password != password_confirm:
        request.session["flash_message"] = "Пароли не совпадают"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("register"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Проверка существования username
    existing_user = await user_crud.get_user_by_username(session, username)
    if existing_user:
        request.session["flash_message"] = "Имя пользователя уже занято"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("register"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Проверка существования email
    existing_email = await user_crud.get_user_by_email(session, email)
    if existing_email:
        request.session["flash_message"] = "Email уже зарегистрирован"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("register"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Создаем пользователя
    try:
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
        )
        user = await user_crud.create(session, user_data)

        # Автоматический вход после регистрации
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["is_superuser"] = user.is_superuser

        request.session["flash_message"] = "Регистрация успешна! Добро пожаловать!"
        request.session["flash_type"] = "success"

        return RedirectResponse(
            url=request.url_for("account"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        request.session["flash_message"] = f"Ошибка при регистрации: {str(e)}"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("register"),
            status_code=status.HTTP_303_SEE_OTHER,
        )


@router.get("/logout", name="logout")
async def logout(request: Request):
    """Выход из системы."""
    request.session.clear()
    request.session["flash_message"] = "Вы вышли из системы"
    request.session["flash_type"] = "success"

    return RedirectResponse(
        url=request.url_for("home"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
