from pydantic_settings import BaseSettings, SettingsConfigDict
from .constants import MAX_FILE_SIZE, MAX_TOTAL_SIZE, ALLOWED_TYPES
import os

class Settings(BaseSettings):
    # Required settings
    GROQ_API_KEY: str
    REPLICATE_API_TOKEN: str
    HUGGINGFACE_API_TOKEN: str  # For Hugging Face Inference API

    # Optional settings with defaults
    MAX_FILE_SIZE: int = MAX_FILE_SIZE
    MAX_TOTAL_SIZE: int = MAX_TOTAL_SIZE
    ALLOWED_TYPES: list = ALLOWED_TYPES

    # Database settings
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "documents"

    # Embedding settings
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"  # Hugging Face embedding model

    # Retrieval settings
    VECTOR_SEARCH_K: int = 10
    HYBRID_RETRIEVER_WEIGHTS: list = [0.4, 0.6]

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # New cache settings with type annotations
    CACHE_DIR: str = "document_cache"
    CACHE_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields like VOYAGE_API_KEY that are not defined in Settings
    )

settings = Settings()