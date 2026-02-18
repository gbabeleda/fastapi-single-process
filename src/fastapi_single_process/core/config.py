"""
Application configuration using Pydantic settings.

Settings are loaded from environment variables with .env file support.
The settings instance is cached as a singleton via @cache decorator.

Usage:
    from fastapi_single_process.core.config import settings

    print(settings.PROJECT_NAME)
"""

from functools import cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Values are loaded from environment variables, with .env file as fallback.

    Local development:
        Create .env file in project root with overrides

    Production:
        Set as actual environment variables (no .env file)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore unknown environment variables
    )

    # Project metadata
    PROJECT_NAME: str = "Single Process FastAPI"
    VERSION: str = "0.1.0"

    # API configuration
    API_V1_PREFIX: str = "/api/v1"

    # Application Environment
    APP_ENVIRONMENT: Literal["local", "docker", "production"] = "local"

    # Database configuration
    APPLICATION_DATABASE_URL: str
    DB_ECHO_SQL: bool = False  # Set to True to log all SQL queries
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600  # Recycle connections after 3600 seconds (1 hour)
    DB_POOL_PRE_PING: bool = False

    # Forward reference
    # The quotes delay evaluation until after the class is defined
    @model_validator(mode="after")
    def adjust_db_url(self) -> "Settings":
        """
        Adjust database URL for host machine execution.

        The APPLICATION_DATABASE_URL uses Docker service networking by default
        (postgres:5432), which only resolves inside Docker containers. When
        running Python code on the host machine, we need to replace the service
        name with localhost and use the externally mapped port.

        Adjustments by environment:
            local:      postgres:5432 → localhost:5445 (host machine access)
            docker:     postgres:5432 (no change, uses container networking)
            production: postgres:5432 (no change, uses production DNS)

        The port mapping is defined in docker-compose.yaml:
            ports:
              - "5445:5432"  # host_port:container_port

        Examples:
            APP_ENVIRONMENT=local:
                Input:  postgresql+asyncpg://dev:dev@postgres:5432/mydb
                Output: postgresql+asyncpg://dev:dev@localhost:5445/mydb

            APP_ENVIRONMENT=docker:
                Input:  postgresql+asyncpg://dev:dev@postgres:5432/mydb
                Output: postgresql+asyncpg://dev:dev@postgres:5432/mydb (unchanged)
        """
        if self.APP_ENVIRONMENT == "local":
            self.APPLICATION_DATABASE_URL = self.APPLICATION_DATABASE_URL.replace(
                "postgres:5432", "localhost:5445"
            )
        return self


@cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton pattern)."""
    return Settings()


# Global settings instance
settings = get_settings()
