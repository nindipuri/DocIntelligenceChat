"""Environment configuration for the backend."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    max_context_pages: int = 5

    # Storage paths (relative to project root or absolute)
    storage_documents: Path = Path("storage/documents")
    storage_indexes: Path = Path("storage/indexes")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage_documents = Path(self.storage_documents)
        self.storage_indexes = Path(self.storage_indexes)


def get_settings() -> Settings:
    """Return application settings singleton."""
    return Settings()
