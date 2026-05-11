from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    GROQ_API_KEY: str
    PHOENIX_API_KEY: str
    PHOENIX_COLLECTOR_ENDPOINT: str
    VITE_API_BASE_URL: str
    QDRANT_URL: str = "http://localhost:6333"
    MEMGRAPH_URI: str = "bolt://localhost:7687"
    MEMGRAPH_USER: str = "memgraph"
    MEMGRAPH_PASSWORD: str = "password"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields like VOYAGE_API_KEY that are not defined in Settings
    )

settings = Settings()