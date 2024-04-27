from typing import Any, Dict, Optional
import secrets

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    PROJECT_NAME: str = "ZhuchkaKeyboards"

    API_V1_STR: str = "/api"

    SECRET_KEY: str = secrets.token_urlsafe(32)

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(  # pyright: ignore
            scheme="postgresql+pg8000",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=values.get("POSTGRES_DB"),
        )

    USERS_OPEN_REGISTRATION: bool = False

    SMTP_TLS: bool = True
    SMTP_PORT: int
    SMTP_HOST: str
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    EMAILS_FROM_EMAIL: EmailStr
    EMAILS_FROM_NAME: str

    EMAIL_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "app/email-templates/build"
    EMAILS_ENABLED: bool = True


settings = Settings()  # pyright: ignore
