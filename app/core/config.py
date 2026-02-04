from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]
CERTS_DIR = BASE_DIR / "app" / "core" / "certs"


class DatabaseSettings(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    NAME: str

    ECHO: bool
    POOL_SIZE: int
    MAX_OVERFLOW: int
    POOL_PRE_PING: bool
    POOL_RECYCLE: int
    AUTOFLUSH: bool
    EXPIRE_ON_COMMIT: bool

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.USER}:{self.PASSWORD}"
            f"@{self.HOST}:{self.PORT}/{self.NAME}"
        )

    model_config = {
        "env_prefix": "DB_",
        "env_file": BASE_DIR / ".env",
        "extra": "ignore",
    }


class AdminSettings(BaseSettings):
    SECRET_KEY: str

    CAN_CREATE: bool
    CAN_EDIT: bool
    CAN_DELETE: bool
    CAN_VIEW_DETAILS: bool

    model_config = {
        "env_prefix": "ADMIN_",
        "env_file": BASE_DIR / ".env",
        "extra": "ignore",
    }


class AuthJWTSettings(BaseSettings):
    private_key_path: Path = CERTS_DIR / "jwt-private.pem"
    public_key_path: Path = CERTS_DIR / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    @property
    def private_key(self) -> str:
        if not hasattr(self, "_private_key"):
            self._private_key = self.private_key_path.read_text()
        return self._private_key

    @property
    def public_key(self) -> str:
        if not hasattr(self, "_public_key"):
            self._public_key = self.public_key_path.read_text()
        return self._public_key

    model_config = {
        "env_prefix": "AUTHJWT_",
        "env_file": BASE_DIR / ".env",
        "extra": "ignore",
    }


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()  # type: ignore
    admin: AdminSettings = AdminSettings()  # type: ignore
    auth_jwt: AuthJWTSettings = AuthJWTSettings()


settings = Settings()
