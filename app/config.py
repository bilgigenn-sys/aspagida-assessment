from pydantic_settings import BaseSettings
from pydantic import EmailStr, field_validator
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "BilgiGEN Assessment"
    SECRET_KEY: str = "change_this_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    ADMIN_EMAIL: EmailStr = "admin@bilgigen.com.tr"
    ADMIN_PASSWORD: str = "ChangeMe123!"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True

    REPORT_SEND_TO: EmailStr = "webmaster@bilgigen.com.tr"

    class Config:
        env_file = ".env"

settings = Settings()
