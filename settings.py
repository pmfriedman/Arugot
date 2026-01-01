from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    runtime_root: str = Field(default="")
    log_level: str = Field(default="INFO")

    obsidian_vault_dir: str = Field(default="")

    fireflies_api_key: str = Field(default="")

    # Scheduler settings
    scheduler_check_interval: int = Field(default=30)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
