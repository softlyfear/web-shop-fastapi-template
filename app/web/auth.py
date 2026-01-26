from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core import templates

router = APIRouter()


@router.get("/login/", response_class=HTMLResponse, name="login")
async def get_login(request: Request) -> HTMLResponse:
    """Отображение страницы входа в систему."""
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "current_user": None,
            "error": None,
        },
    )
