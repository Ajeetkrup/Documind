from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    NVIDIA_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields like VOYAGE_API_KEY that are not defined in Settings
    )

settings = Settings()