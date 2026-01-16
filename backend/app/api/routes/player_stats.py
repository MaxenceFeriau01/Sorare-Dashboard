"""
Routes API pour les statistiques des joueurs
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.player_stats_service import PlayerStatsService
from app.models.player_statistics import PlayerStatistics
from app.config import settings

router = APIRouter()

# Récupération de la clé API depuis les settings
API_FOOTBALL_KEY = settings.API_FOOTBALL_KEY if hasattr(settings, 'API_FOOTBALL_KEY') else None


# Schémas Pydantic pour la validation
class PlayerStatsQuery(BaseModel):
    """Paramètres de requête pour récupérer les statistiques"""
    player_id: Optional[int] = Field(None, description="ID du joueur")
    team_id: Optional[int] = Field(None, description="ID de l'équipe")
    league_id: Optional[int] = Field(None, description="ID de la ligue")
    season: Optional[int] = Field(None, description="Saison (YYYY)")
    search: Optional[str] = Field(None, min_length=4, description="Nom du joueur (min 4 caractères)")
    page: int = Field(1, ge=1, description="Numéro de page")
    force_refresh: bool = Field(False, description="Forcer le rafraîchissement depuis l'API")


class PlayerStatsResponse(BaseModel):
    """Réponse contenant les statistiques d'un joueur"""
    cached: bool
    results: int
    paging: Optional[dict] = None
    response: List[dict]


@router.get("/fetch", response_model=PlayerStatsResponse)
async def fetch_player_statistics(
    player_id: Optional[int] = Query(None, description="ID du joueur"),
    team_id: Optional[int] = Query(None, description="ID de l'équipe"),
    league_id: Optional[int] = Query(None, description="ID de la ligue"),
    season: Optional[int] = Query(None, description="Saison (YYYY)"),
    search: Optional[str] = Query(None, min_length=4, description="Nom du joueur (min 4 caractères)"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    force_refresh: bool = Query(False, description="Forcer le rafraîchissement depuis l'API"),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques des joueurs depuis l'API-Football
    
    - **player_id**: ID du joueur spécifique
    - **team_id**: ID de l'équipe
    - **league_id**: ID de la ligue
    - **season**: Saison au format YYYY (nécessite league_id, team_id ou player_id)
    - **search**: Rechercher un joueur par nom (nécessite league_id ou team_id)
    - **page**: Numéro de page pour la pagination (20 résultats par page)
    - **force_refresh**: Force le rafraîchissement depuis l'API (ignorer le cache)
    
    **Note**: Pour rechercher des statistiques de saison, vous devez fournir au moins
    un ID de ligue, d'équipe ou de joueur avec la saison.
    """
    if not API_FOOTBALL_KEY:
        raise HTTPException(status_code=500, detail="Clé API-Football non configurée")
    
    try:
        service = PlayerStatsService(API_FOOTBALL_KEY)
        result = service.fetch_player_statistics(
            db=db,
            player_id=player_id,
            team_id=team_id,
            league_id=league_id,
            season=season,
            search=search,
            page=page,
            force_refresh=force_refresh
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")


@router.get("/team/{team_id}")
async def get_team_statistics(
    team_id: int,
    season: int = Query(..., description="Saison (YYYY)"),
    league_id: Optional[int] = Query(None, description="ID de la ligue"),
    db: Session = Depends(get_db)
):
    """
    Récupère toutes les statistiques des joueurs d'une équipe pour une saison donnée
    """
    if not API_FOOTBALL_KEY:
        raise HTTPException(status_code=500, detail="Clé API-Football non configurée")
    
    try:
        service = PlayerStatsService(API_FOOTBALL_KEY)
        stats = service.get_player_stats_by_team(db, team_id, season, league_id)
        return {
            "results": len(stats),
            "response": [stat.to_dict() for stat in stats]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/search")
async def search_players(
    search: str = Query(..., min_length=3, description="Terme de recherche"),
    league_id: Optional[int] = Query(None, description="Filtrer par ligue"),
    season: Optional[int] = Query(None, description="Filtrer par saison"),
    db: Session = Depends(get_db)
):
    """
    Recherche des joueurs par nom dans la base de données locale
    """
    if not API_FOOTBALL_KEY:
        raise HTTPException(status_code=500, detail="Clé API-Football non configurée")
    
    try:
        service = PlayerStatsService(API_FOOTBALL_KEY)
        stats = service.search_players(db, search, league_id, season)
        return {
            "results": len(stats),
            "response": [stat.to_dict() for stat in stats]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/player/{player_id}")
async def get_player_statistics(
    player_id: int,
    season: Optional[int] = Query(None, description="Filtrer par saison"),
    db: Session = Depends(get_db)
):
    """
    Récupère toutes les statistiques d'un joueur spécifique
    """
    try:
        query = db.query(PlayerStatistics).filter(PlayerStatistics.player_id == player_id)
        
        if season:
            query = query.filter(PlayerStatistics.season == season)
        
        stats = query.all()
        
        if not stats:
            raise HTTPException(status_code=404, detail="Aucune statistique trouvée pour ce joueur")
        
        return {
            "results": len(stats),
            "response": [stat.to_dict() for stat in stats]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.delete("/cache/player/{player_id}")
async def clear_player_cache(
    player_id: int,
    season: Optional[int] = Query(None, description="Supprimer uniquement pour cette saison"),
    db: Session = Depends(get_db)
):
    """
    Supprime les statistiques en cache pour un joueur
    """
    try:
        query = db.query(PlayerStatistics).filter(PlayerStatistics.player_id == player_id)
        
        if season:
            query = query.filter(PlayerStatistics.season == season)
        
        deleted_count = query.delete()
        db.commit()
        
        return {
            "message": f"{deleted_count} statistique(s) supprimée(s) du cache",
            "player_id": player_id,
            "season": season
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/leagues")
async def get_available_leagues(db: Session = Depends(get_db)):
    """
    Récupère la liste des ligues disponibles dans la base de données
    """
    try:
        leagues = db.query(
            PlayerStatistics.league_id,
            PlayerStatistics.league_name,
            PlayerStatistics.league_country,
            PlayerStatistics.league_logo,
            PlayerStatistics.season
        ).distinct().order_by(
            PlayerStatistics.league_name,
            PlayerStatistics.season.desc()
        ).all()
        
        leagues_dict = {}
        for league in leagues:
            league_key = f"{league.league_id}"
            if league_key not in leagues_dict:
                leagues_dict[league_key] = {
                    "id": league.league_id,
                    "name": league.league_name,
                    "country": league.league_country,
                    "logo": league.league_logo,
                    "seasons": []
                }
            if league.season not in leagues_dict[league_key]["seasons"]:
                leagues_dict[league_key]["seasons"].append(league.season)
        
        return {
            "results": len(leagues_dict),
            "response": list(leagues_dict.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/positions")
async def get_player_positions(
    league_id: Optional[int] = Query(None, description="Filtrer par ligue"),
    season: Optional[int] = Query(None, description="Filtrer par saison"),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des positions disponibles avec le nombre de joueurs
    """
    try:
        query = db.query(
            PlayerStatistics.games_position,
            db.func.count(PlayerStatistics.id).label("count")
        ).filter(PlayerStatistics.games_position.isnot(None))
        
        if league_id:
            query = query.filter(PlayerStatistics.league_id == league_id)
        if season:
            query = query.filter(PlayerStatistics.season == season)
        
        positions = query.group_by(PlayerStatistics.games_position).all()
        
        return {
            "results": len(positions),
            "response": [
                {"position": pos[0], "count": pos[1]}
                for pos in positions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")