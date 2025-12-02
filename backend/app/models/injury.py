"""
Modèle de données pour les blessures des joueurs
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Injury(Base):
    """Modèle pour stocker les informations sur les blessures"""
    
    __tablename__ = "injuries"
    
    # ID
    id = Column(Integer, primary_key=True, index=True)
    
    # Relation avec le joueur
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    
    # Informations sur la blessure
    injury_type = Column(String(255))  # Ex: "Muscle", "Ligament", "Fracture"
    injury_description = Column(Text)
    severity = Column(String(50))  # Ex: "Minor", "Moderate", "Severe"
    
    # Dates
    injury_date = Column(DateTime(timezone=True))
    expected_return_date = Column(DateTime(timezone=True))
    actual_return_date = Column(DateTime(timezone=True))
    
    # Statut
    is_active = Column(Boolean, default=True)  # Si la blessure est toujours d'actualité
    
    # Source de l'information
    source = Column(String(255))  # Ex: "Twitter", "Official Club", "Transfermarkt"
    source_url = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    def __repr__(self):
        return f"<Injury {self.injury_type} - Player ID: {self.player_id}>"
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire"""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "injury_type": self.injury_type,
            "injury_description": self.injury_description,
            "severity": self.severity,
            "injury_date": self.injury_date.isoformat() if self.injury_date else None,
            "expected_return_date": self.expected_return_date.isoformat() if self.expected_return_date else None,
            "actual_return_date": self.actual_return_date.isoformat() if self.actual_return_date else None,
            "is_active": self.is_active,
            "source": self.source,
            "source_url": self.source_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }