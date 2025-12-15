"""
Schemas Pydantic pour la validation des données des joueurs
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlayerBase(BaseModel):
    """Schema de base pour un joueur"""
    sorare_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    slug: Optional[str] = None
    club_name: Optional[str] = None
    club_slug: Optional[str] = None
    position: Optional[str] = None
    league_name: Optional[str] = None  # 🆕
    league_id: Optional[int] = None    # 🆕
    league_country: Optional[str] = None  # 🆕
    country: Optional[str] = None
    country_code: Optional[str] = None
    age: Optional[int] = None
    birth_date: Optional[str] = None


class PlayerCreate(PlayerBase):
    """Schema pour créer un joueur"""
    pass


class PlayerUpdate(BaseModel):
    """Schema pour mettre à jour un joueur"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    club_name: Optional[str] = None
    position: Optional[str] = None
    league_name: Optional[str] = None  # 🆕
    league_id: Optional[int] = None    # 🆕
    league_country: Optional[str] = None  # 🆕
    average_score: Optional[float] = None
    total_games: Optional[int] = None
    season_games: Optional[int] = None
    is_active: Optional[bool] = None
    is_injured: Optional[bool] = None
    injury_status: Optional[str] = None


class PlayerResponse(PlayerBase):
    """Schema de réponse pour un joueur"""
    id: int
    average_score: float = 0.0
    total_games: int = 0
    season_games: int = 0
    last_game_score: Optional[float] = None
    is_active: bool = True
    is_injured: bool = False
    injury_status: Optional[str] = None
    image_url: Optional[str] = None
    card_sample_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_sorare_sync: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PlayerListResponse(BaseModel):
    """Schema pour une liste de joueurs"""
    total: int
    players: list[PlayerResponse]


class LeagueStats(BaseModel):
    """Schema pour les statistiques par ligue"""
    league_name: str
    league_country: Optional[str] = None
    player_count: int
    avg_score: float = 0.0
    injured_count: int = 0