"""Configuration management for YOLOX API"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_title: str = "YOLOX Object Detection API"
    api_description: str = "Stateless and scalable YOLOX inference API for commercial use"
    api_version: str = "1.0.0"

    # Model Configuration
    model_name: str = "yolox-s"
    model_path: str = "./models/yolox_s.pth"
    confidence_threshold: float = 0.3
    nms_threshold: float = 0.45
    input_size: int = 640

    # Performance Settings
    max_batch_size: int = 8
    device: str = "cuda"  # cuda or cpu

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
