"""
Modèle de données pour les informations API-Football liées aux joueurs
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class FootballAPIData(Base):
    """Stocke les données de l'API-Football pour chaque joueur"""
    
    __tablename__ = "football_api_data"
    
    # ID
    id = Column(Integer, primary_key=True, index=True)
    
    # Relation avec le joueur Sorare
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, unique=True, index=True)
    
    # ID API-Football
    football_api_id = Column(Integer, nullable=False, index=True)
    
    # Informations de base
    name = Column(String(200))
    firstname = Column(String(100))
    lastname = Column(String(100))
    age = Column(Integer)
    nationality = Column(String(100))
    height = Column(String(20))
    weight = Column(String(20))
    photo = Column(Text)
    
    # Équipe actuelle
    current_team_id = Column(Integer)
    current_team_name = Column(String(200))
    current_team_logo = Column(Text)
    
    # Statistiques saison en cours
    current_season = Column(Integer, default=2025)
    season_appearances = Column(Integer, default=0)
    season_goals = Column(Integer, default=0)
    season_assists = Column(Integer, default=0)
    season_minutes_played = Column(Integer, default=0)
    season_yellow_cards = Column(Integer, default=0)
    season_red_cards = Column(Integer, default=0)
    season_rating = Column(Float)
    
    # Statut blessure
    is_injured = Column(Boolean, default=False)
    injury_type = Column(String(255))
    injury_reason = Column(Text)
    injury_date = Column(DateTime(timezone=True))
    
    # Prochains matchs (JSON array)
    upcoming_matches = Column(JSON)  # [{date, opponent, competition, home/away}]
    
    # Toutes les stats détaillées (JSON pour flexibilité)
    detailed_stats = Column(JSON)  # Toutes les stats par compétition
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_api_sync = Column(DateTime(timezone=True))  # Dernière synchro avec l'API
    
    def __repr__(self):
        return f"<FootballAPIData Player#{self.player_id} - API#{self.football_api_id}>"
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire"""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "football_api_id": self.football_api_id,
            "name": self.name,
            "age": self.age,
            "nationality": self.nationality,
            "height": self.height,
            "weight": self.weight,
            "photo": self.photo,
            "current_team": {
                "id": self.current_team_id,
                "name": self.current_team_name,
                "logo": self.current_team_logo
            },
            "season_stats": {
                "season": self.current_season,
                "appearances": self.season_appearances,
                "goals": self.season_goals,
                "assists": self.season_assists,
                "minutes": self.season_minutes_played,
                "yellow_cards": self.season_yellow_cards,
                "red_cards": self.season_red_cards,
                "rating": self.season_rating
            },
            "injury_status": {
                "is_injured": self.is_injured,
                "type": self.injury_type,
                "reason": self.injury_reason,
                "date": self.injury_date.isoformat() if self.injury_date else None
            },
            "upcoming_matches": self.upcoming_matches or [],
            "detailed_stats": self.detailed_stats or {},
            "last_api_sync": self.last_api_sync.isoformat() if self.last_api_sync else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }