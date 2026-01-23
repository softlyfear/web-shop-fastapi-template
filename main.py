from contextlib import asynccontextmanager

import uvicorn
from alembic.config import Config
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from alembic import command
from app.admin.setup import setup_admin
from app.core import settings
from app.web import router as web_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.admin.SECRET_KEY)
setup_admin(app)


app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(web_router)


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run_migrations()
    uvicorn.run("main:app", reload=True)
