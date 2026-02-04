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
    USERNAME: str
    PASSWORD: str
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
    access_token_expire_minutes: int = 3


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()  # type: ignore
    admin: AdminSettings = AdminSettings()  # type: ignore
    auth_jwt: AuthJWTSettings = AuthJWTSettings()


settings = Settings()

print(settings.auth_jwt)
