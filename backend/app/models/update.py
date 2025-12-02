"""
Modèle de données pour tracker les mises à jour automatiques
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base


class Update(Base):
    """Modèle pour stocker l'historique des mises à jour"""
    
    __tablename__ = "updates"
    
    # ID
    id = Column(Integer, primary_key=True, index=True)
    
    # Type de mise à jour
    update_type = Column(String(100), index=True)  # Ex: "players", "injuries", "twitter", "scraping"
    
    # Statut
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    
    # Résultats
    items_processed = Column(Integer, default=0)
    items_updated = Column(Integer, default=0)
    items_created = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    
    # Détails
    message = Column(Text)
    error_message = Column(Text)
    details = Column(JSON)  # Pour stocker des infos supplémentaires
    
    # Durée
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Source
    source = Column(String(255))  # Ex: "celery_task", "manual", "api_call"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Update {self.update_type} - {self.status}>"
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire"""
        return {
            "id": self.id,
            "update_type": self.update_type,
            "status": self.status,
            "items_processed": self.items_processed,
            "items_updated": self.items_updated,
            "items_created": self.items_created,
            "items_failed": self.items_failed,
            "message": self.message,
            "error_message": self.error_message,
            "details": self.details,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }