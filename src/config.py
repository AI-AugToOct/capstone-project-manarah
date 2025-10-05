"""Configuration management for Manarah backend."""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI API
    openai_api_key: str
    
    # Application Settings
    api_port: int = 8000
    log_level: str = "INFO"
    max_upload_size_mb: int = 500
    frame_extraction_fps: int = 15
    
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


# Global settings instance
settings = Settings()

# Ensure data directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.content_dir.mkdir(parents=True, exist_ok=True)
settings.analysis_dir.mkdir(parents=True, exist_ok=True)
settings.decisions_dir.mkdir(parents=True, exist_ok=True)
settings.audit_dir.mkdir(parents=True, exist_ok=True)
