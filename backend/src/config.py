"""Configuration management for Manarah backend."""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import field_validator
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000

    # OpenAI API
    openai_api_key: str
    openai_model_vision: str = "gpt-4o"
    openai_model_audio: str = "whisper-1"
    openai_model_reasoner: str = "gpt-4"

    # Application Settings
    api_port: int = 8000
    log_level: str = "INFO"
    max_upload_size_mb: int = 500
    frame_extraction_fps: int = 15

    # CORS Settings (comma-separated string)
    allowed_origins: str = "http://localhost:5173,http://localhost:4173,http://127.0.0.1:5173,http://127.0.0.1:4173"
    
    # Thresholds
    auto_remove_threshold: float = 0.85
    review_threshold: float = 0.60
    warning_threshold: float = 0.40
    
    # Data Paths
    data_dir: Path = Path("./data")
    content_dir: Path = Path("./data/content")
    analysis_dir: Path = Path("./data/analysis")
    decisions_dir: Path = Path("./data/decisions")
    audit_dir: Path = Path("./data/audit")
    
    # API Settings
    max_retries: int = 3
    retry_delay: float = 1.0

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_origins_list(self) -> List[str]:
        """Parse allowed_origins string into list."""
        if isinstance(self.allowed_origins, str):
            return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]
        return self.allowed_origins if self.allowed_origins else []


# Global settings instance
settings = Settings()

# Ensure data directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.content_dir.mkdir(parents=True, exist_ok=True)
settings.analysis_dir.mkdir(parents=True, exist_ok=True)
settings.decisions_dir.mkdir(parents=True, exist_ok=True)
settings.audit_dir.mkdir(parents=True, exist_ok=True)
