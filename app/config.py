"""Application configuration."""

from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_version: str = Field(default="v1", description="API version")
    debug: bool = Field(default=False, description="Debug mode")
    reload: bool = Field(default=False, description="Auto-reload on changes")

    # Database
    database_url: PostgresDsn = Field(
        description="PostgreSQL database URL",
        examples=["postgresql://user:pass@localhost:5432/dbname"],
    )

    # Security
    secret_key: str = Field(
        description="Secret key for JWT token generation",
        min_length=32,
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )

    # External APIs
    weather_api_base_url: str = Field(
        default="https://api.weather.example.com",
        description="Base URL for external weather API",
    )
    weather_api_key: str = Field(
        default="", description="API key for weather service"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json/text)")

    # Application
    app_name: str = Field(default="Roop Marine Operations", description="Application name")
    app_description: str = Field(
        default="Marine Operations Feasibility Service for roop",
        description="Application description",
    )

    @validator("database_url", pre=True)
    def validate_database_url(cls, v: Any) -> str:
        """Validate database URL format."""
        if isinstance(v, str):
            return v
        return str(v)

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return str(self.database_url).replace("postgresql://", "postgresql://", 1)

    @property
    def database_url_async(self) -> str:
        """Get async database URL for SQLAlchemy."""
        return str(self.database_url).replace("postgresql://", "postgresql+asyncpg://", 1)


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()