"""
Modèle pour stocker les prédictions de matchs en base de données
Pour éviter d'appeler l'API-Football à chaque chargement du dashboard
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class MatchPrediction(Base):
    """
    Stocke les prédictions pour les prochains matchs des joueurs
    Permet d'éviter d'appeler l'API-Football constamment
    """
    __tablename__ = "match_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relations
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    player = relationship("Player", back_populates="match_predictions")
    
    # Informations du match
    fixture_id = Column(Integer, nullable=False)
    match_date = Column(DateTime, nullable=False, index=True)
    opponent = Column(String(200))
    is_home = Column(Boolean, default=False)
    venue = Column(String(200))
    competition = Column(String(200))
    
    # Prédictions
    playability_score = Column(Float)
    playability_advice = Column(String(500))
    playability_color = Column(String(50))
    playability_reasons = Column(JSON)
    
    # Prédictions détaillées (stockées en JSON)
    prediction_data = Column(JSON)
    
    # Métadonnées
    is_active = Column(Boolean, default=True, index=True)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<MatchPrediction(player_id={self.player_id}, fixture={self.fixture_id}, date={self.match_date})>"