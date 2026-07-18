from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "CampusIQ"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI-Powered Student Success Platform"
    
    DATABASE_URL: str = "postgresql+psycopg2://campusiq:campusiq_dev_password@localhost:5432/campusiq"
    REDIS_URL: str = "redis://localhost:6379/0"
    OLLAMA_HOST: str = "http://localhost:11434"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    
    SECRET_KEY: str = "campusiq_dev_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "llama2"
    VECTOR_DIMENSION: int = 384
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
