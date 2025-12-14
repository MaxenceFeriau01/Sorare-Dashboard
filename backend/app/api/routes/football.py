"""
Routes API pour l'intégration API-Football
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from loguru import logger

from app.services.football_api_service import football_api_service

router = APIRouter()


@router.get("/status")
async def check_api_status():
    """
    Vérifie le statut de l'API-Football et la consommation
    Cette route ne compte pas dans le quota quotidien
    """
    result = await football_api_service.check_api_status()
    
    if not result.get('success'):
        raise HTTPException(
            status_code=500,
            detail="Impossible de vérifier le statut de l'API-Football"
        )
    
    return result.get('data', {})


@router.get("/search-players")
async def search_players(
    query: str = Query(..., min_length=3, description="Nom du joueur à rechercher"),
    page: int = Query(1, ge=1, description="Numéro de page (250 résultats par page)")
):
    """
    Recherche des joueurs par nom (profil simple sans stats)
    
    Exemples:
    - /search-players?query=Mbappé
    - /search-players?query=Ronaldo&page=2
    """
    logger.info(f"🔍 Recherche de joueurs: {query}")
    
    result = await football_api_service.search_players(query, page)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=400,
            detail=result.get('error', 'Erreur lors de la recherche')
        )
    
    # Formater les résultats pour le frontend
    players = []
    for item in result.get('data', []):
        # /players/profiles retourne directement les infos du joueur
        player = item.get('player', {}) if 'player' in item else item
        
        players.append({
            "id": player.get('id'),
            "name": player.get('name'),
            "firstname": player.get('firstname'),
            "lastname": player.get('lastname'),
            "age": player.get('age'),
            "nationality": player.get('nationality'),
            "photo": player.get('photo'),
            "height": player.get('height'),
            "weight": player.get('weight'),
            "birth": player.get('birth'),
            "injured": player.get('injured')
        })
    
    return {
        "success": True,
        "count": len(players),
        "players": players
    }


@router.get("/player/{player_id}")
async def get_player_details(
    player_id: int,
    season: int = Query(2025, description="Année de la saison")
):
    """
    Récupère les détails complets d'un joueur
    
    Exemple: /player/276?season=2025
    """
    logger.info(f"📊 Récupération du joueur ID: {player_id}")
    
    result = await football_api_service.get_player_by_id(player_id, season)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=404,
            detail="Joueur non trouvé"
        )
    
    data = result.get('data', [])
    if not data:
        raise HTTPException(
            status_code=404,
            detail="Joueur non trouvé"
        )
    
    player_data = data[0]
    
    # Formater pour la base de données
    formatted = football_api_service.format_player_for_database(player_data)
    
    return {
        "success": True,
        "player": player_data,
        "formatted_for_db": formatted
    }


@router.get("/search-teams")
async def search_teams(
    query: str = Query(..., min_length=3, description="Nom de l'équipe"),
    country: Optional[str] = Query(None, description="Pays de l'équipe")
):
    """
    Recherche des équipes par nom
    
    Exemples:
    - /search-teams?query=Real Madrid
    - /search-teams?query=PSG&country=France
    """
    logger.info(f"🔍 Recherche d'équipes: {query}")
    
    result = await football_api_service.search_teams(query, country)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=400,
            detail=result.get('error', 'Erreur lors de la recherche')
        )
    
    # Formater les résultats
    teams = []
    for item in result.get('data', []):
        team = item.get('team', {})
        venue = item.get('venue', {})
        
        teams.append({
            "id": team.get('id'),
            "name": team.get('name'),
            "code": team.get('code'),
            "country": team.get('country'),
            "founded": team.get('founded'),
            "logo": team.get('logo'),
            "venue": {
                "name": venue.get('name'),
                "city": venue.get('city'),
                "capacity": venue.get('capacity')
            }
        })
    
    return {
        "success": True,
        "count": len(teams),
        "teams": teams
    }


@router.get("/team/{team_id}")
async def get_team_info(team_id: int):
    """
    Récupère les informations d'une équipe
    
    Exemple: /team/541
    """
    logger.info(f"📊 Récupération de l'équipe ID: {team_id}")
    
    result = await football_api_service.get_team_info(team_id)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=404,
            detail="Équipe non trouvée"
        )
    
    data = result.get('data', [])
    if not data:
        raise HTTPException(
            status_code=404,
            detail="Équipe non trouvée"
        )
    
    return {
        "success": True,
        "team": data[0]
    }


@router.get("/matches/upcoming/{team_id}")
async def get_upcoming_matches(
    team_id: int,
    next: int = Query(10, ge=1, le=50, description="Nombre de matchs à récupérer")
):
    """
    Récupère les prochains matchs d'une équipe
    
    Exemple: /matches/upcoming/541?next=5
    """
    logger.info(f"📅 Récupération des {next} prochains matchs de l'équipe {team_id}")
    
    result = await football_api_service.get_upcoming_matches(team_id, next)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=400,
            detail="Impossible de récupérer les matchs"
        )
    
    # Formater les matchs
    matches = []
    for fixture in result.get('data', []):
        fixture_data = fixture.get('fixture', {})
        teams = fixture.get('teams', {})
        league = fixture.get('league', {})
        
        matches.append({
            "id": fixture_data.get('id'),
            "date": fixture_data.get('date'),
            "timestamp": fixture_data.get('timestamp'),
            "venue": fixture_data.get('venue', {}).get('name'),
            "status": fixture_data.get('status', {}).get('long'),
            "league": {
                "id": league.get('id'),
                "name": league.get('name'),
                "country": league.get('country'),
                "logo": league.get('logo')
            },
            "home_team": {
                "id": teams.get('home', {}).get('id'),
                "name": teams.get('home', {}).get('name'),
                "logo": teams.get('home', {}).get('logo')
            },
            "away_team": {
                "id": teams.get('away', {}).get('id'),
                "name": teams.get('away', {}).get('name'),
                "logo": teams.get('away', {}).get('logo')
            }
        })
    
    return {
        "success": True,
        "count": len(matches),
        "matches": matches
    }


@router.get("/leagues")
async def get_leagues(
    country: Optional[str] = Query(None, description="Pays"),
    season: int = Query(2025, description="Année de la saison")
):
    """
    Récupère la liste des ligues disponibles
    
    Exemples:
    - /leagues?season=2025
    - /leagues?country=France&season=2025
    """
    logger.info(f"📋 Récupération des ligues pour {season}")
    
    result = await football_api_service.get_leagues(country, season)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=400,
            detail="Impossible de récupérer les ligues"
        )
    
    # Formater les ligues
    leagues = []
    for item in result.get('data', []):
        league = item.get('league', {})
        country_data = item.get('country', {})
        
        leagues.append({
            "id": league.get('id'),
            "name": league.get('name'),
            "type": league.get('type'),
            "logo": league.get('logo'),
            "country": {
                "name": country_data.get('name'),
                "code": country_data.get('code'),
                "flag": country_data.get('flag')
            }
        })
    
    return {
        "success": True,
        "count": len(leagues),
        "leagues": leagues
    }


@router.get("/injuries")
async def get_injuries(
    player_id: Optional[int] = Query(None, description="ID du joueur"),
    team_id: Optional[int] = Query(None, description="ID de l'équipe"),
    season: int = Query(2025, description="Année de la saison (OBLIGATOIRE)")
):
    """
    Récupère les blessures des joueurs
    IMPORTANT: Le paramètre season est OBLIGATOIRE
    
    Exemples:
    - /injuries?player_id=276&season=2025
    - /injuries?team_id=541&season=2025
    """
    logger.info(f"🏥 Récupération des blessures (saison {season})")
    
    result = await football_api_service.get_player_injuries(player_id, team_id, season)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=400,
            detail="Impossible de récupérer les blessures"
        )
    
    return {
        "success": True,
        "count": result.get('results', 0),
        "injuries": result.get('data', [])
    }