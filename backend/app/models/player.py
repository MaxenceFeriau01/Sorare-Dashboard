"""
Modèle de données pour les joueurs Sorare
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base


class Player(Base):
    """Modèle pour stocker les joueurs Sorare"""
    
    __tablename__ = "players"
    
    # ID
    id = Column(Integer, primary_key=True, index=True)
    sorare_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Informations de base
    first_name = Column(String(100))
    last_name = Column(String(100))
    display_name = Column(String(200))
    slug = Column(String(255), unique=True, index=True)
    
    # Club & Position
    club_name = Column(String(200))
    club_slug = Column(String(255))
    position = Column(String(50))  # Goalkeeper, Defender, Midfielder, Forward
    
    # Nationalité
    country = Column(String(100))
    country_code = Column(String(10))
    
    # Âge & Date de naissance
    age = Column(Integer)
    birth_date = Column(String(50))
    
    # Stats Sorare
    average_score = Column(Float, default=0.0)
    total_games = Column(Integer, default=0)
    season_games = Column(Integer, default=0)
    last_game_score = Column(Float)
    
    # État du joueur
    is_active = Column(Boolean, default=True)
    is_injured = Column(Boolean, default=False)
    injury_status = Column(String(255))
    
    # Métadonnées
    image_url = Column(Text)
    card_sample_url = Column(Text)
    
    # Données additionnelles (JSON pour flexibilité)
    extra_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_sorare_sync = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Player {self.display_name} ({self.club_name})>"
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire"""
        return {
            "id": self.id,
            "sorare_id": self.sorare_id,
            "display_name": self.display_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "slug": self.slug,
            "club_name": self.club_name,
            "position": self.position,
            "country": self.country,
            "age": self.age,
            "average_score": self.average_score,
            "total_games": self.total_games,
            "is_active": self.is_active,
            "is_injured": self.is_injured,
            "injury_status": self.injury_status,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }