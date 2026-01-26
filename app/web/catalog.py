from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core import templates

router = APIRouter()


@router.get("/catalogs/", response_class=HTMLResponse)
async def get_catalogs(request: Request) -> HTMLResponse:
    """Отображение страницы каталога товаров."""
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
            "categories": [],
            "products": [],
            "current_user": None,
        },
    )
