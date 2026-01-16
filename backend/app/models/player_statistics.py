"""
Modèle pour les statistiques détaillées des joueurs
"""
from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from datetime import datetime
from app.database import Base  # ✅ Import correct (absolu, pas relatif)

class PlayerStatistics(Base):
    """Statistiques détaillées d'un joueur pour une saison donnée"""
    __tablename__ = "player_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations du joueur
    player_id = Column(Integer, index=True, nullable=False)
    player_name = Column(String, nullable=False)
    player_firstname = Column(String)
    player_lastname = Column(String)
    player_age = Column(Integer)
    player_birth_date = Column(Date)
    player_birth_place = Column(String)
    player_birth_country = Column(String)
    player_nationality = Column(String)
    player_height = Column(String)
    player_weight = Column(String)
    player_injured = Column(Boolean, default=False)
    player_photo = Column(String)
    
    # Informations de l'équipe
    team_id = Column(Integer, index=True)
    team_name = Column(String)
    team_logo = Column(String)
    
    # Informations de la ligue
    league_id = Column(Integer, index=True)
    league_name = Column(String)
    league_country = Column(String)
    league_logo = Column(String)
    league_flag = Column(String)
    season = Column(Integer, index=True)
    
    # Statistiques de jeu
    games_appearences = Column(Integer, default=0)
    games_lineups = Column(Integer, default=0)
    games_minutes = Column(Integer, default=0)
    games_number = Column(Integer)  # Numéro de maillot
    games_position = Column(String)
    games_rating = Column(Float)
    games_captain = Column(Boolean, default=False)
    
    # Statistiques de remplacement
    substitutes_in = Column(Integer, default=0)
    substitutes_out = Column(Integer, default=0)
    substitutes_bench = Column(Integer, default=0)
    
    # Statistiques de tir
    shots_total = Column(Integer, default=0)
    shots_on = Column(Integer, default=0)
    
    # Statistiques de but
    goals_total = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    goals_assists = Column(Integer, default=0)
    goals_saves = Column(Integer, default=0)
    
    # Statistiques de passe
    passes_total = Column(Integer, default=0)
    passes_key = Column(Integer, default=0)
    passes_accuracy = Column(Integer, default=0)
    
    # Statistiques de tacle
    tackles_total = Column(Integer, default=0)
    tackles_blocks = Column(Integer, default=0)
    tackles_interceptions = Column(Integer, default=0)
    
    # Statistiques de duel
    duels_total = Column(Integer, default=0)
    duels_won = Column(Integer, default=0)
    
    # Statistiques de dribble
    dribbles_attempts = Column(Integer, default=0)
    dribbles_success = Column(Integer, default=0)
    dribbles_past = Column(Integer, default=0)
    
    # Statistiques de faute
    fouls_drawn = Column(Integer, default=0)
    fouls_committed = Column(Integer, default=0)
    
    # Statistiques de carton
    cards_yellow = Column(Integer, default=0)
    cards_yellowred = Column(Integer, default=0)
    cards_red = Column(Integer, default=0)
    
    # Statistiques de pénalty
    penalty_won = Column(Integer, default=0)
    penalty_committed = Column(Integer, default=0)
    penalty_scored = Column(Integer, default=0)
    penalty_missed = Column(Integer, default=0)
    penalty_saved = Column(Integer, default=0)
    
    # Métadonnées
    last_updated = Column(Date, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PlayerStatistics {self.player_name} - {self.team_name} - {self.season}>"
    
    def to_dict(self):
        """Convertit les statistiques en dictionnaire"""
        return {
            "id": self.id,
            "player": {
                "id": self.player_id,
                "name": self.player_name,
                "firstname": self.player_firstname,
                "lastname": self.player_lastname,
                "age": self.player_age,
                "birth": {
                    "date": self.player_birth_date.isoformat() if self.player_birth_date else None,
                    "place": self.player_birth_place,
                    "country": self.player_birth_country
                },
                "nationality": self.player_nationality,
                "height": self.player_height,
                "weight": self.player_weight,
                "injured": self.player_injured,
                "photo": self.player_photo
            },
            "team": {
                "id": self.team_id,
                "name": self.team_name,
                "logo": self.team_logo
            },
            "league": {
                "id": self.league_id,
                "name": self.league_name,
                "country": self.league_country,
                "logo": self.league_logo,
                "flag": self.league_flag,
                "season": self.season
            },
            "statistics": {
                "games": {
                    "appearences": self.games_appearences,
                    "lineups": self.games_lineups,
                    "minutes": self.games_minutes,
                    "number": self.games_number,
                    "position": self.games_position,
                    "rating": self.games_rating,
                    "captain": self.games_captain
                },
                "substitutes": {
                    "in": self.substitutes_in,
                    "out": self.substitutes_out,
                    "bench": self.substitutes_bench
                },
                "shots": {
                    "total": self.shots_total,
                    "on": self.shots_on
                },
                "goals": {
                    "total": self.goals_total,
                    "conceded": self.goals_conceded,
                    "assists": self.goals_assists,
                    "saves": self.goals_saves
                },
                "passes": {
                    "total": self.passes_total,
                    "key": self.passes_key,
                    "accuracy": self.passes_accuracy
                },
                "tackles": {
                    "total": self.tackles_total,
                    "blocks": self.tackles_blocks,
                    "interceptions": self.tackles_interceptions
                },
                "duels": {
                    "total": self.duels_total,
                    "won": self.duels_won
                },
                "dribbles": {
                    "attempts": self.dribbles_attempts,
                    "success": self.dribbles_success,
                    "past": self.dribbles_past
                },
                "fouls": {
                    "drawn": self.fouls_drawn,
                    "committed": self.fouls_committed
                },
                "cards": {
                    "yellow": self.cards_yellow,
                    "yellowred": self.cards_yellowred,
                    "red": self.cards_red
                },
                "penalty": {
                    "won": self.penalty_won,
                    "committed": self.penalty_committed,
                    "scored": self.penalty_scored,
                    "missed": self.penalty_missed,
                    "saved": self.penalty_saved
                }
            },
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }