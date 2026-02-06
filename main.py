import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.admin.setup import setup_admin
from app.api import router_v1
from app.core import register_exception_handlers, settings
from app.web import router as web_router

app = FastAPI(title="FastApi AutoShop")
app.add_middleware(SessionMiddleware, secret_key=settings.admin.SECRET_KEY)
setup_admin(app)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web_router)
app.include_router(router_v1)

register_exception_handlers(app)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
