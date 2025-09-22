from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    # Application Info
    APP_NAME: str = "Railway Intelligent Decision Support System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Database Configuration
    # Default to SQLite for ease of local development; can be overridden via env
    DATABASE_URL: str = "sqlite:///./ridss.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security Configuration
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173"
    ]
    
    # External API Configuration
    TMS_API_URL: str = "https://api.tms.indianrailways.gov.in"
    SIGNALING_API_URL: str = "https://api.signaling.indianrailways.gov.in"
    TIMETABLE_API_URL: str = "https://api.timetable.indianrailways.gov.in"
    RAILWAY_API_KEY: str = "your-railway-api-key"
    
    # AI/ML Configuration
    MODEL_PATH: str = "./models/"
    OPTIMIZATION_TIMEOUT: int = 30
    MAX_TRAINS_PER_OPTIMIZATION: int = 100
    AI_MODEL_VERSION: str = "v1.0"
    
    # Performance Settings
    MAX_WORKERS: int = 4
    CACHE_TTL: int = 300
    WEBSOCKET_TIMEOUT: int = 60
    
    # Monitoring Configuration
    PROMETHEUS_PORT: int = 9090
    GRAFANA_URL: str = "http://localhost:3001"
    ENABLE_METRICS: bool = True
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    # File Storage
    UPLOAD_PATH: str = "./uploads/"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USER: str = "alerts@ridss.indianrailways.gov.in"
    EMAIL_PASSWORD: str = "your-email-password"

# Create settings instance
settings = Settings()

# Ensure required directories exist
Path(settings.MODEL_PATH).mkdir(parents=True, exist_ok=True)
Path(settings.UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
