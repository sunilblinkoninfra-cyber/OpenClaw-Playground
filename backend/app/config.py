from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Openclaw Provisioning Engine"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@db:5432/openclaw"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Supabase
    SUPABASE_URL: str = "https://placeholder.supabase.co"
    SUPABASE_KEY: str = "placeholder-key"
    
    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_placeholder"
    STRIPE_WEBHOOK_SECRET: str = "whsec_placeholder"
    
    # Docker Registry
    DOCKER_REGISTRY: str = "docker.io"
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Provisioning
    CONTAINER_MEMORY_MB: int = 2048
    CONTAINER_CPU_SHARES: int = 1024
    CONTAINER_PORT: int = 8080
    TRIAL_DURATION_HOURS: int = 24
    
    # API
    API_PREFIX: str = "/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
