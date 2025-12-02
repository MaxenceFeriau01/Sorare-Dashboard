"""
Configuration de l'application avec credentials Twitter
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Application
    APP_NAME: str = "Sorare Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sorare_db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend Next.js
        "http://localhost:8000",  # Backend
    ]
    
    # Sorare API
    SORARE_API_URL: str = "https://api.sorare.com/graphql"
    SORARE_EMAIL: str = ""
    SORARE_PASSWORD: str = ""
    
    # Twitter/X Credentials (pour le scraping avec Selenium)
    TWITTER_EMAIL: str = ""           # Ton email Twitter
    TWITTER_PASSWORD: str = ""        # Ton mot de passe Twitter
    TWITTER_USERNAME: str = ""        # Ton @username (parfois demandé)
    
    # Scraping Settings
    SCRAPING_ENABLED: bool = True
    SCRAPING_INTERVAL_MINUTES: int = 60  # Scraping toutes les heures
    SCRAPING_RATE_LIMIT_SECONDS: int = 2  # Délai entre requêtes
    
    # Celery (pour les tâches automatiques)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()