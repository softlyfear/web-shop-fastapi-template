from fastapi import FastAPI
from sqladmin import Admin

from app.admin import ALL_ADMIN_VIEWS
from app.core import async_engine


def setup_admin(app: FastAPI):
    admin = Admin(app, async_engine)

    for view in ALL_ADMIN_VIEWS:
        admin.add_view(view)

    return admin
