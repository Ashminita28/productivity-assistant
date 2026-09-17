import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Load and expose environment settings for the application"""
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "DEVELOPMENT")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Productivity Assistant API")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    
    
    SMART_LLM_PROVIDER: str = os.getenv("SMART_LLM_PROVIDER", "gemini")
    SMART_LLM_MODEL: str = os.getenv("SMART_LLM_MODEL", "gemini-3.5-pro")
    
    FAST_LLM_PROVIDER: str = os.getenv("FAST_LLM_PROVIDER", "ollama")
    FAST_LLM_MODEL: str = os.getenv("FAST_LLM_MODEL", "llama3.2:1b")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
