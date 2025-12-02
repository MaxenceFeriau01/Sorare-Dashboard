"""
Configuration de l'application avec credentials Twitter
(Inclut tous les champs nécessaires pour Pydantic v2)
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # ========================================
    # 1. APPLICATION & ENVIRONNEMENT
    # ========================================
    APP_NAME: str = "Sorare Dashboard API"
    APP_VERSION: str = "1.0.0"
    
    # ✅ AJOUTÉ pour résoudre les erreurs 'Extra inputs'
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "dev"
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "Europe/Paris"
    
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1" # Manquant dans votre snippet original
    
    # ========================================
    # 2. BASE DE DONNÉES (POSTGRES)
    # ========================================
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sorare_db"
    
    # ✅ AJOUTÉ pour résoudre les erreurs 'Extra inputs'
    POSTGRES_USER: str = "sorare"
    POSTGRES_PASSWORD: str = "sorare_super_secret_password_2024"
    POSTGRES_DB: str = "sorare_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # ========================================
    # 3. REDIS & CELERY
    # ========================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0" # ✅ AJOUTÉ
    
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # ✅ AJOUTÉ pour les intervalles Celery
    UPDATE_PLAYERS_INTERVAL: int = 60
    UPDATE_INJURIES_INTERVAL: int = 30
    UPDATE_TWITTER_INTERVAL: int = 15
    
    # ========================================
    # 4. CORS & FRONTEND
    # ========================================
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # ✅ AJOUTÉ pour le Frontend
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"
    NEXT_PUBLIC_APP_NAME: str = "Sorare Dashboard"
    
    # ========================================
    # 5. JWT & API SECURITY
    # ========================================
    # ✅ AJOUTÉ pour la sécurité (utilisé dans app.main/auth)
    API_SECRET_KEY: str = "change_this_to_a_random_secret_key_min_32_chars"
    API_ALGORITHM: str = "HS256"
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ========================================
    # 6. SORARE API
    # ========================================
    SORARE_API_URL: str = "https://api.sorare.com/graphql"
    SORARE_EMAIL: str = ""
    SORARE_PASSWORD: str = ""
    
    # ========================================
    # 7. TWITTER/X CREDENTIALS
    # ========================================
    TWITTER_EMAIL: str = ""
    TWITTER_PASSWORD: str = ""
    TWITTER_USERNAME: str = ""
    TWITTER_BEARER_TOKEN: str = "" # ✅ AJOUTÉ
    
    # ========================================
    # 8. SCRAPING SETTINGS
    # ========================================
    SCRAPING_ENABLED: bool = True
    SCRAPING_INTERVAL_MINUTES: int = 60
    SCRAPING_RATE_LIMIT_SECONDS: int = 2
    
    # ✅ AJOUTÉ pour le scraping (utilisé par twitter_scraper.py)
    SCRAPING_DELAY_MIN: int = 5
    SCRAPING_DELAY_MAX: int = 15
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # 💥 Si l'erreur 'Extra inputs are not permitted' persiste:
        # Pydantic est trop stricte. Forcer l'acceptation (ou l'ignorance) des champs supplémentaires.
        extra = 'allow'
        # Si vous êtes en Pydantic v1, vous pourriez avoir besoin de:
        # @classmethod
        # def customise_sources(cls, settings_cls, init_settings, env_settings, file_secret_settings):
        #     return (
        #         env_settings,
        #         init_settings,
        #         file_secret_settings,
        #     )


settings = Settings()