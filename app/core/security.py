"""Authentication and security utilities."""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

from app.core import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

http_bearer = HTTPBearer()


class AuthUtils:
    """JWT and password utilities."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(password, hashed)

    @staticmethod
    def encode_jwt(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key,
        algorithm: str = settings.auth_jwt.algorithm,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
    ):
        """Encode JWT token with expiration."""
        to_encode = payload.copy()
        now = datetime.now(UTC)
        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes=expire_minutes)
        to_encode.update(
            exp=expire,
            iat=now,
        )
        encoded = jwt.encode(
            to_encode,
            private_key,
            algorithm,
        )
        return encoded

    @staticmethod
    def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key,
        algorithm: str = settings.auth_jwt.algorithm,
    ):
        """Decode and verify JWT token."""
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=[algorithm],
        )
        return decoded

    @staticmethod
    def create_access_token(user_id: int, username: str) -> str:
        """Create access JWT token for user."""
        payload = {
            "sub": str(user_id),
            "username": username,
            "type": "access",
        }
        return AuthUtils.encode_jwt(
            payload=payload,
            expire_minutes=settings.auth_jwt.access_token_expire_minutes,
        )

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create refresh JWT token for user."""
        payload = {
            "sub": str(user_id),
            "type": "refresh",
        }
        return AuthUtils.encode_jwt(
            payload=payload,
            expire_timedelta=timedelta(
                days=settings.auth_jwt.refresh_token_expire_days
            ),
        )

    @staticmethod
    def validate_token_type(payload: dict, expected_type: str) -> None:
        """Validate JWT token type matches expected."""
        token_type = payload.get("type")
        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. "
                f"Expected '{expected_type}', got '{token_type}'",
            )
