from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "contractguard-api"
    LOG_LEVEL: str = "INFO"
    
    # Auth
    AUTH_MODE: str = "jwt"  # jwt, static, none
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "RS256"
    JWT_ISSUER: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://contractguard:password@localhost:5432/contractguard"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # NATS
    NATS_URL: str = "nats://localhost:4222"
    
    # Vector DB (pgvector)
    VECTOR_DIMENSIONS: int = 1536
    
    # LLM
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4-turbo-preview"
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET: str = "contractguard-contracts"
    
    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318"
    
    # Build metadata
    GIT_COMMIT: str = "dev"
    BUILD_TIME: str = "unknown"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
