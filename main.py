from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.admin.setup import setup_admin
from app.core import async_engine, settings
from app.models import Base
from app.web import router as web_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.admin.SECRET_KEY)
setup_admin(app)


app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(web_router)
