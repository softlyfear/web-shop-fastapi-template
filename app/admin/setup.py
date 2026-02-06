"""Admin panel setup and configuration."""

import io

from fastapi import FastAPI
from sqladmin import Admin
from starlette.datastructures import FormData, UploadFile

from app.admin import ALL_ADMIN_VIEWS, AdminAuth
from app.admin.views import UPLOAD_DIR
from app.core import async_engine, settings
from app.models import Product


class AdminWithUploads(Admin):
    async def _handle_form_data(self, request, obj=None) -> FormData:
        form = await request.form()
        form_data: list[tuple[str, str | UploadFile]] = []
        for key, value in form.multi_items():
            if not isinstance(value, UploadFile):
                form_data.append((key, value))
                continue

            should_clear = form.get(key + "_checkbox")
            empty_upload = len(await value.read(1)) != 1
            await value.seek(0)

            if should_clear:
                form_data.append((key, UploadFile(io.BytesIO(b""))))
                continue

            if empty_upload and obj and getattr(obj, key):
                f = getattr(obj, key)
                if isinstance(obj, Product) and key == "image" and isinstance(f, str):
                    f = UPLOAD_DIR / f
                if hasattr(f, "name") and hasattr(f, "open"):
                    form_data.append(
                        (key, UploadFile(filename=f.name, file=f.open("rb")))
                    )
                else:
                    form_data.append((key, value))
                continue

            form_data.append((key, value))
        return FormData(form_data)


def setup_admin(app: FastAPI):
    """Initialize admin panel with views."""
    admin = AdminWithUploads(
        app,
        async_engine,
        authentication_backend=AdminAuth(secret_key=settings.admin.SECRET_KEY),
    )

    for view in ALL_ADMIN_VIEWS:
        admin.add_view(view)

    return admin
