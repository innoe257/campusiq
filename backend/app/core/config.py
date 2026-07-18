from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "CampusIQ"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI-Powered Student Success Platform"
    
    # Database - Render provides DATABASE_URL
    DATABASE_URL: str = "postgresql+psycopg2://campusiq:campusiq_dev_password@localhost:5432/campusiq"
    
    # Redis - optional (disabled on Render free tier)
    REDIS_URL: str = ""
    
    # Ollama - optional (disabled on Render free tier, no GPU)
    OLLAMA_HOST: str = "http://localhost:11434"
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    
    # Security
    SECRET_KEY: str = "campusiq_dev_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "llama2"
    VECTOR_DIMENSION: int = 384
    
    # Render environment
    RENDER: bool = False
    FRONTEND_URL: str = ""
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
