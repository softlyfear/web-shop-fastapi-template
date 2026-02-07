"""Admin panel authentication backend."""

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.database import get_async_session
from app.core.security import AuthUtils
from app.crud import user_crud


class AdminAuth(AuthenticationBackend):
    """Admin authentication backend."""

    async def login(self, request: Request) -> bool:
        """Login for superusers from database."""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        async for session in get_async_session():
            user = await user_crud.get_user_by_username(session, username)
            if not user:
                return False

            if not AuthUtils.verify_password(password, user.hashed_password):
                return False

            if not user.is_superuser:
                return False

            if not user.is_active:
                return False

            token = AuthUtils.create_access_token(
                user_id=user.id, username=user.username
            )
            request.session.update(
                {
                    "admin_token": token,
                    "admin_user_id": user.id,
                    "admin_username": user.username,
                }
            )
            return True

        return False

    async def logout(self, request: Request) -> bool:
        """Выход - очистка только admin данных из session."""
        request.session.pop("admin_token", None)
        request.session.pop("admin_user_id", None)
        request.session.pop("admin_username", None)
        return True

    async def authenticate(self, request: Request) -> bool:
        """Validate on each admin request."""
        token = request.session.get("admin_token")

        if not token:
            return False

        try:
            payload = AuthUtils.decode_jwt(token)
            AuthUtils.validate_token_type(payload, "access")
            user_id = int(payload.get("sub"))
            async for session in get_async_session():
                user = await user_crud.get(session, user_id)
                if user and user.is_active and user.is_superuser:
                    return True

            return False

        except Exception:
            # Очищаем только admin-ключи из сессии
            request.session.pop("admin_token", None)
            request.session.pop("admin_user_id", None)
            request.session.pop("admin_username", None)
            return False
