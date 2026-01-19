from sqladmin.authentication import AuthenticationBackend

from app.core import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if username == settings.admin.USERNAME and password == settings.admin.PASSWORD:
            request.session.update({"token": "admin"})
            return True
        return False

    async def logout(self, request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request) -> bool:
        token = request.session.get("token")
        if token == "admin":
            return True
        return False
