from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    SERVICE_NAME: str = "contractguard-api"
    LOG_LEVEL: str = "INFO"
    AUTH_MODE: str = "jwt"
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "RS256"
    JWT_ISSUER: Optional[str] = None
    DATABASE_URL: str = "postgresql://contractguard:password@localhost:5432/contractguard"
    REDIS_URL: str = "redis://localhost:6379/0"
    NATS_URL: str = "nats://localhost:4222"
    VECTOR_DIMENSIONS: int = 1536
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4-turbo-preview"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET: str = "contractguard-contracts"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318"
    GIT_COMMIT: str = "dev"
    BUILD_TIME: str = "unknown"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
