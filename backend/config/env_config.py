import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Load and expose environment settings for the application"""
    ENVIRONMENT: str = "DEVELOPMENT"
    PROJECT_NAME: str = "Productivity Assistant API"
    LOG_DIR: str = "logs"
    
    LLM_API_KEY: str = "your-api-key-here"
    DATABASE_URL: str = "sqlite:///./tasks.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
