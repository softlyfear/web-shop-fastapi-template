from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request) -> HTMLResponse:
    """Отображение домашней страницы."""
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
            "categories": [],
            "products": [],
        },
    )
