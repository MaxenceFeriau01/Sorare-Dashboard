"""
Configuration principale de l'application
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Application
    APP_NAME: str = "Sorare Dashboard API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_SECRET_KEY: str = "change_this_secret_key_in_production"
    API_ALGORITHM: str = "HS256"
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Database
    POSTGRES_USER: str = "sorare"
    POSTGRES_PASSWORD: str = "sorare_super_secret_password_2024"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sorare_db"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construit l'URL de la base de données"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    @property
    def REDIS_URL(self) -> str:
        """Construit l'URL de Redis"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # Celery
    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.REDIS_URL
    
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL
    
    # Sorare API
    SORARE_EMAIL: str = "maxence.epdsae@gmail.com"
    SORARE_PASSWORD: str = "Delory59170"
    SORARE_API_URL: str = "https://api.sorare.com/graphql"
    
    # Scraping
    SCRAPING_DELAY_MIN: int = 5
    SCRAPING_DELAY_MAX: int = 15
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Twitter/X (optionnel)
    TWITTER_BEARER_TOKEN: str = ""
    
    # Cron intervals (en minutes)
    UPDATE_PLAYERS_INTERVAL: int = 60
    UPDATE_INJURIES_INTERVAL: int = 30
    UPDATE_TWITTER_INTERVAL: int = 15
    
    # Timezone
    TIMEZONE: str = "Europe/Paris"
    
    # Logs
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True


# Instance globale des settings
settings = Settings()