from fastapi import FastAPI
from sqladmin import Admin

from app.admin import ALL_ADMIN_VIEWS, AdminAuth
from app.core import async_engine, settings


def setup_admin(app: FastAPI):
    admin = Admin(
        app,
        async_engine,
        authentication_backend=AdminAuth(secret_key=settings.admin.SECRET_KEY),
    )

    for view in ALL_ADMIN_VIEWS:
        admin.add_view(view)

    return admin
