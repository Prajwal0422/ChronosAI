from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    app_name: str = "AI Timetable Generator"
    debug: bool = False
    api_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/timetable_db",
        validation_alias="DATABASE_URL",
    )

    jwt_secret_key: str = Field(default="", validation_alias="JWT_SECRET_KEY")

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if not v:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is required. "
                "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    max_login_attempts: int = 5
    account_lockout_minutes: int = 30

    cors_origins: list[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True

    upload_dir: str = "uploads"
    max_upload_size_mb: int = 50

    ai_generation_timeout_seconds: int = 300
    ai_max_solutions: int = 10
    ai_population_size: int = 100
    ai_generations: int = 50

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
