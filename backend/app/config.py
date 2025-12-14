"""
Configuration de l'application avec credentials Twitter
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
    VERSION: str = "1.0.0"
    
    # ✅ Variables résolvant les erreurs précédentes (ENVIRONMENT, DEBUG)
    ENVIRONMENT: str = "dev"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"             # 💥 AJOUTÉ : LOG_LEVEL
    TIMEZONE: str = "Europe/Paris"      # 💥 AJOUTÉ : TIMEZONE
    
    API_V1_PREFIX: str = "/api/v1"
    
    # ========================================
    # 2. BASE DE DONNÉES (POSTGRES)
    # ========================================
    # La DATABASE_URL est la variable de connexion complète
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sorare_db"
    
    # 💥 AJOUTÉ : Variables détaillées de la DB (pour un meilleur paramétrage)
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
    REDIS_URL: str = "redis://localhost:6379/0" # 💥 AJOUTÉ : REDIS_URL
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # 💥 AJOUTÉ : Intervalles Celery
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
    
    # 💥 AJOUTÉ : Variables Frontend
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"
    NEXT_PUBLIC_APP_NAME: str = "Sorare Dashboard"
    
    # ========================================
    # 5. JWT & API SECURITY
    # ========================================
    # 💥 AJOUTÉ : Variables de Sécurité (Clés secrètes)
    API_SECRET_KEY: str = "change_this_to_a_random_secret_key_min_32_chars"
    API_ALGORITHM: str = "HS256"
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ========================================
    # 6. SORARE API
    # ========================================
    SORARE_API_URL: str = "https://api.sorare.com/graphql"
    SORARE_EMAIL: str = ""
    SORARE_PASSWORD: str = ""

    # API-Football
    FOOTBALL_API_KEY: str = "b3337b4a41780ddee3261615c4d9fe4d"
    
    # ========================================
    # 7. TWITTER/X CREDENTIALS
    # ========================================
    TWITTER_EMAIL: str = ""
    TWITTER_PASSWORD: str = ""
    TWITTER_USERNAME: str = ""
    TWITTER_BEARER_TOKEN: str = "" # 💥 AJOUTÉ : TWITTER_BEARER_TOKEN
    
    # ========================================
    # 8. SCRAPING SETTINGS
    # ========================================
    SCRAPING_ENABLED: bool = True
    SCRAPING_INTERVAL_MINUTES: int = 60
    SCRAPING_RATE_LIMIT_SECONDS: int = 2
    
    # 💥 AJOUTÉ : Variables détaillées de Scraping
    SCRAPING_DELAY_MIN: int = 5
    SCRAPING_DELAY_MAX: int = 15
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # NOTE : Si les erreurs persistent (improbable), vous pouvez ajouter :
        # extra = 'ignore' 
        # MAIS il est préférable d'avoir toutes les variables déclarées comme ci-dessus.


settings = Settings()