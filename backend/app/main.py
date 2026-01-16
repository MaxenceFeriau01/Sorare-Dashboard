"""
Point d'entrée principal de l'API FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger

from app.config import settings
from app.database import init_db
from app.api.routes import players, injuries, stats, sorare, football, football_integration, player_stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    (startup et shutdown)
    """
    # Startup
    logger.info("🚀 Démarrage de l'application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialiser la base de données
    try:
        init_db()
        logger.success("✅ Base de données initialisée")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la DB: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arrêt de l'application...")


# Créer l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API pour gérer ton dashboard Sorare personnel",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =================================
# ROUTES
# =================================

@app.get("/")
async def root():
    """Route racine - Health check"""
    return {
        "message": "Sorare Dashboard API",
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """Health check pour monitoring"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
    }


# Inclure les routers
app.include_router(
    players.router,
    prefix=f"{settings.API_V1_PREFIX}/players",
    tags=["Players"]
)

app.include_router(
    injuries.router,
    prefix=f"{settings.API_V1_PREFIX}/injuries",
    tags=["Injuries"]
)

app.include_router(
    stats.router,
    prefix=f"{settings.API_V1_PREFIX}/stats",
    tags=["Statistics"]
)

app.include_router(
    sorare.router,
    prefix=f"{settings.API_V1_PREFIX}/sorare",
    tags=["Sorare"]
)

app.include_router(
    football.router,
    prefix=f"{settings.API_V1_PREFIX}/football",
    tags=["football-api"]
)

app.include_router(
    football_integration.router,
    prefix=f"{settings.API_V1_PREFIX}/players",
    tags=["Football Integration"]
)

# ✅ NOUVEAU: Router pour les statistiques détaillées des joueurs
app.include_router(
    player_stats.router,
    prefix=f"{settings.API_V1_PREFIX}/player-stats",
    tags=["Player Statistics"]
)


# =================================
# EXCEPTION HANDLERS
# =================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire d'erreurs global"""
    logger.error(f"Erreur globale: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )