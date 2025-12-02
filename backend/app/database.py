"""
Configuration de la base de données SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Créer l'engine de la base de données
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Vérifie la connexion avant de l'utiliser
    pool_size=10,  # Nombre de connexions dans le pool
    max_overflow=20,  # Connexions supplémentaires en cas de besoin
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """
    Dependency pour obtenir une session de base de données
    Usage dans FastAPI:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialise la base de données (crée les tables)
    À appeler au démarrage de l'application
    """
    Base.metadata.create_all(bind=engine)