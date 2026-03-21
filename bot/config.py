"""Configuration loading from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot token (required for Telegram mode, not needed for --test)
    bot_token: str = ""

    # LMS Backend API
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API (for Task 3 intent routing)
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"


# Global settings instance
settings = BotSettings()
