from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]


class DatabaseSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    ECHO: bool
    POOL_SIZE: int
    MAX_OVERFLOW: int
    POOL_PRE_PING: bool
    POOL_RECYCLE: int
    AUTOFLUSH: bool
    EXPIRE_ON_COMMIT: bool

    ADMIN_CAN_CREATE: bool
    ADMIN_CAN_EDIT: bool
    ADMIN_CAN_DELETE: bool
    ADMIN_CAN_VIEW_DETAILS: bool

    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {
        "env_file": BASE_DIR / ".env",
        "env_file_encoding": "utf-8",
    }


class SchemaSettings(BaseSettings):
    pass


class Settings:
    db = DatabaseSettings()  # type: ignore
    schema = SchemaSettings()


settings = Settings()
