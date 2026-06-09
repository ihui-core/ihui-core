from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    ANTHROPIC_API_KEY: str
    IA_PROVIDER: str = "ollama"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    RESEND_API_KEY: str = ""
    UPLOAD_DIR: str = "uploads"
    BASE_URL: str = "http://localhost:3001"

    class Config:
        env_file = str(BASE_DIR / ".env")

settings = Settings()