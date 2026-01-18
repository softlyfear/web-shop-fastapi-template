from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin

from app.core.database import DatabaseEngine
from app.models import UserAdmin
from app.web.router import router as web_router

app = FastAPI()
admin = Admin(app, DatabaseEngine.async_engine)
admin.add_view(UserAdmin)


app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(web_router)
