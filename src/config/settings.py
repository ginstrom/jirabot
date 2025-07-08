"""Configuration settings for the jirabot application."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Jira Configuration
    jira_url: str = Field(..., description="Jira instance URL")
    jira_username: str = Field(..., description="Jira username/email")
    jira_api_token: str = Field(..., description="Jira API token")

    # Application Configuration
    log_level: str = Field("INFO", description="Logging level")
    debug: bool = Field(False, description="Debug mode")
    environment: str = Field("development", description="Environment")

    # Output Configuration
    output_dir: str = Field("output", description="Output directory for files")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


# Global settings instance - will be initialized when first accessed
_settings: Optional[Settings] = None


def settings() -> Settings:
    """Get or create application settings."""
    global _settings
    if _settings is None:
        _settings = get_settings()
    return _settings
