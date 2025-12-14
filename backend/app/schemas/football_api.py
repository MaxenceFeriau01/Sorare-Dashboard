"""
Schemas Pydantic pour les données API-Football
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class UpcomingMatch(BaseModel):
    """Schema pour un match à venir"""
    date: str
    opponent: str
    competition: str
    is_home: bool
    venue: Optional[str] = None


class SeasonStats(BaseModel):
    """Schema pour les stats de la saison"""
    season: int
    appearances: int = 0
    goals: int = 0
    assists: int = 0
    minutes: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    rating: Optional[float] = None


class InjuryStatus(BaseModel):
    """Schema pour le statut de blessure"""
    is_injured: bool = False
    type: Optional[str] = None
    reason: Optional[str] = None
    date: Optional[datetime] = None


class CurrentTeam(BaseModel):
    """Schema pour l'équipe actuelle"""
    id: int
    name: str
    logo: Optional[str] = None


class FootballAPIDataResponse(BaseModel):
    """Schema de réponse pour les données API-Football"""
    id: int
    player_id: int
    football_api_id: int
    name: str
    age: Optional[int] = None
    nationality: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    photo: Optional[str] = None
    current_team: Optional[CurrentTeam] = None
    season_stats: SeasonStats
    injury_status: InjuryStatus
    upcoming_matches: List[UpcomingMatch] = []
    detailed_stats: Dict[str, Any] = {}
    last_api_sync: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PlayerCompleteResponse(BaseModel):
    """Schema pour un joueur avec TOUTES ses données"""
    # Données Sorare (base)
    id: int
    sorare_id: str
    display_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    club_name: Optional[str] = None
    position: Optional[str] = None
    country: Optional[str] = None
    age: Optional[int] = None
    average_score: float = 0.0
    total_games: int = 0
    is_injured: bool = False
    
    # Données API-Football (enrichies)
    football_data: Optional[FootballAPIDataResponse] = None
    
    class Config:
        from_attributes = True


class ImportPlayerRequest(BaseModel):
    """Schema pour importer un joueur depuis l'API-Football"""
    football_api_id: int
    sorare_id: str  # ID Sorare du joueur à créer/lier
    display_name: str
    position: Optional[str] = None


class SyncPlayerResponse(BaseModel):
    """Schema de réponse pour la synchronisation"""
    success: bool
    player_id: int
    message: str
    synced_at: datetime
    stats_updated: bool
    injuries_updated: bool
    matches_updated: bool