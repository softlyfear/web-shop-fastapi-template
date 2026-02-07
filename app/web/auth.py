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
    """Display login page."""
    # If user is already authorized, redirect to account
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
    """Process login."""
    # Find user
    user = await user_crud.get_user_by_username(session, username)

    # Check user and password
    if not user or not AuthUtils.verify_password(password, user.hashed_password):
        request.session["flash_message"] = "Invalid username or password"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("login"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Check user is active
    if not user.is_active:
        request.session["flash_message"] = "Account deactivated"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("login"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Save user in session
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["is_superuser"] = user.is_superuser

    request.session["flash_message"] = f"Welcome, {user.username}!"
    request.session["flash_type"] = "success"

    # Redirect to account or home
    return RedirectResponse(
        url=request.url_for("account"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/register", response_class=HTMLResponse, name="register")
async def get_register(request: Request) -> HTMLResponse:
    """Display registration page."""
    # If user is already authorized, redirect
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
    """Process registration."""
    # Check password match
    if password != password_confirm:
        request.session["flash_message"] = "Passwords do not match"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("register"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Check if username exists
    existing_user = await user_crud.get_user_by_username(session, username)
    if existing_user:
        request.session["flash_message"] = "Username already taken"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("register"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Check if email exists
    existing_email = await user_crud.get_user_by_email(session, email)
    if existing_email:
        request.session["flash_message"] = "Email already registered"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("register"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Create user
    try:
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
        )
        user = await user_crud.create(session, user_data)

        # Automatic login after registration
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["is_superuser"] = user.is_superuser

        request.session["flash_message"] = "Registration successful! Welcome!"
        request.session["flash_type"] = "success"

        return RedirectResponse(
            url=request.url_for("account"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        request.session["flash_message"] = f"Registration error: {str(e)}"
        request.session["flash_type"] = "error"
        return RedirectResponse(
            url=request.url_for("register"),
            status_code=status.HTTP_303_SEE_OTHER,
        )


@router.get("/logout", name="logout")
async def logout(request: Request):
    """Logout."""
    # Clear only web user data, keep admin data
    request.session.pop("user_id", None)
    request.session.pop("username", None)
    request.session.pop("is_superuser", None)
    request.session.pop("cart", None)

    request.session["flash_message"] = "You have been logged out"
    request.session["flash_type"] = "success"

    return RedirectResponse(
        url=request.url_for("home"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
