"""
Routes d'intégration API-Football
✅ CORRECTIONS APPLIQUÉES:
1. Utilisation de la méthode get_player_injuries_smart()
2. Gestion correcte du statut is_injured
3. Distinction entre "Missing Fixture" et "Questionable"
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

from app.database import get_db
from app.models.player import Player
from app.models.football_api_data import FootballAPIData
from app.schemas.football_api import (
    ImportPlayerRequest,
    SyncPlayerResponse,
    PlayerCompleteResponse,
    FootballAPIDataResponse
)
from app.services.football_api_service import football_api_service

router = APIRouter()


@router.post("/import", response_model=PlayerCompleteResponse, status_code=201)
async def import_player_from_football_api(
    request: ImportPlayerRequest,
    db: Session = Depends(get_db)
):
    """
    Importe un joueur depuis l'API-Football et le stocke en base
    """
    logger.info(f"📥 Import joueur API-Football ID: {request.football_api_id}")
    
    # 1. Vérifier si le joueur existe déjà
    existing_player = db.query(Player).filter(Player.sorare_id == request.sorare_id).first()
    
    if existing_player:
        logger.info(f"✅ Joueur existant trouvé: {existing_player.display_name}")
        player = existing_player
    else:
        player = Player(
            sorare_id=request.sorare_id,
            display_name=request.display_name,
            position=request.position,
            is_active=True
        )
        db.add(player)
        db.commit()
        db.refresh(player)
        logger.info(f"✅ Nouveau joueur créé: {player.display_name}")
    
    # 2. Récupérer les données de l'API-Football
    api_result = await football_api_service.get_player_by_id(request.football_api_id, 2025)
    
    if not api_result.get('success') or not api_result.get('data'):
        raise HTTPException(status_code=404, detail="Joueur non trouvé sur l'API-Football")
    
    player_data = api_result['data'][0]
    api_player = player_data.get('player', {})
    statistics = player_data.get('statistics', [])
    
    # 3. Mettre à jour le joueur
    player.first_name = api_player.get('firstname')
    player.last_name = api_player.get('lastname')
    player.display_name = api_player.get('name', player.display_name)
    player.age = api_player.get('age')
    player.birth_date = str(api_player.get('birth', {}).get('date', ''))
    player.country = api_player.get('nationality')
    player.image_url = api_player.get('photo')
    
    if statistics:
        main_stats = statistics[0]
        team = main_stats.get('team', {})
        games = main_stats.get('games', {})
        
        player.club_name = team.get('name')
        if not player.position and games.get('position'):
            player.position = games.get('position')
    
    # 4. Créer ou mettre à jour football_api_data
    football_data = db.query(FootballAPIData).filter(
        FootballAPIData.player_id == player.id
    ).first()
    
    if not football_data:
        football_data = FootballAPIData(player_id=player.id)
        db.add(football_data)
    
    football_data.football_api_id = request.football_api_id
    football_data.name = api_player.get('name')
    football_data.firstname = api_player.get('firstname')
    football_data.lastname = api_player.get('lastname')
    football_data.age = api_player.get('age')
    football_data.nationality = api_player.get('nationality')
    football_data.height = api_player.get('height')
    football_data.weight = api_player.get('weight')
    football_data.photo = api_player.get('photo')
    
    if statistics:
        main_stats = statistics[0]
        team = main_stats.get('team', {})
        games = main_stats.get('games', {})
        goals = main_stats.get('goals', {})
        cards = main_stats.get('cards', {})
        
        football_data.current_team_id = team.get('id')
        football_data.current_team_name = team.get('name')
        football_data.current_team_logo = team.get('logo')
        football_data.season_appearances = games.get('appearances') or 0
        football_data.season_goals = goals.get('total') or 0
        football_data.season_assists = goals.get('assists') or 0
        football_data.season_minutes_played = games.get('minutes') or 0
        football_data.season_yellow_cards = cards.get('yellow') or 0
        football_data.season_red_cards = cards.get('red') or 0
        football_data.season_rating = float(games.get('rating') or 0) if games.get('rating') else None
        football_data.detailed_stats = statistics
    
    # 5. Récupérer les prochains matchs
    if football_data.current_team_id:
        matches_result = await football_api_service.get_upcoming_matches(
            football_data.current_team_id, 
            next=5
        )
        
        if matches_result.get('success'):
            upcoming = []
            for fixture in matches_result.get('data', []):
                fixture_data = fixture.get('fixture', {})
                teams = fixture.get('teams', {})
                league = fixture.get('league', {})
                
                home_team = teams.get('home', {})
                away_team = teams.get('away', {})
                is_home = home_team.get('id') == football_data.current_team_id
                opponent = away_team.get('name') if is_home else home_team.get('name')
                
                upcoming.append({
                    "date": fixture_data.get('date'),
                    "opponent": opponent,
                    "competition": league.get('name'),
                    "is_home": is_home,
                    "venue": fixture_data.get('venue', {}).get('name')
                })
            
            football_data.upcoming_matches = upcoming
    
    # 6. ✅ NOUVELLE LOGIQUE: Vérifier les blessures intelligemment
    football_data.is_injured = False
    football_data.injury_type = None
    football_data.injury_reason = None
    player.is_injured = False
    player.injury_status = None
    
    # Initialiser à "disponible" par défaut lors de l'import
    # La synchronisation mettra à jour le statut réel
    
    football_data.last_api_sync = datetime.utcnow()
    db.commit()
    db.refresh(player)
    db.refresh(football_data)
    
    logger.info(f"✅ Import terminé: {player.display_name} (ID: {player.id})")
    
    # Retourner le joueur complet
    football_data_dict = football_data.to_dict()
    football_data_dict.pop('detailed_stats', None)
    
    return PlayerCompleteResponse(
        id=player.id,
        sorare_id=player.sorare_id,
        display_name=player.display_name,
        first_name=player.first_name,
        last_name=player.last_name,
        club_name=player.club_name,
        position=player.position,
        country=player.country,
        age=player.age,
        average_score=player.average_score,
        total_games=player.total_games,
        is_injured=player.is_injured,
        football_data=FootballAPIDataResponse(**football_data_dict) if football_data_dict else None
    )


@router.post("/{player_id}/sync", response_model=SyncPlayerResponse)
async def sync_player_with_football_api(
    player_id: int,
    db: Session = Depends(get_db)
):
    """
    ✅ SYNCHRONISATION CORRIGÉE avec logique intelligente des blessures
    
    Synchronise un joueur existant avec l'API-Football
    Met à jour : stats, matchs, et statut de blessure
    """
    logger.info(f"🔄 Synchronisation joueur ID: {player_id}")
    
    # 1. Récupérer le joueur
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    football_data = db.query(FootballAPIData).filter(
        FootballAPIData.player_id == player_id
    ).first()
    
    if not football_data:
        raise HTTPException(
            status_code=404,
            detail="Aucune donnée API-Football. Utilisez /import d'abord."
        )
    
    stats_updated = False
    injuries_updated = False
    matches_updated = False
    
    try:
        # 2. Mettre à jour les stats
        api_result = await football_api_service.get_player_by_id(
            football_data.football_api_id,
            2025
        )
        
        if api_result.get('success') and api_result.get('data'):
            player_data = api_result['data'][0]
            statistics = player_data.get('statistics', [])
            
            if statistics:
                main_stats = statistics[0]
                games = main_stats.get('games', {})
                goals = main_stats.get('goals', {})
                cards = main_stats.get('cards', {})
                
                football_data.season_appearances = games.get('appearances') or 0
                football_data.season_goals = goals.get('total') or 0
                football_data.season_assists = goals.get('assists') or 0
                football_data.season_minutes_played = games.get('minutes') or 0
                football_data.season_yellow_cards = cards.get('yellow') or 0
                football_data.season_red_cards = cards.get('red') or 0
                football_data.season_rating = float(games.get('rating') or 0) if games.get('rating') else None
                football_data.detailed_stats = statistics
                
                stats_updated = True
        
        # 3. Mettre à jour les prochains matchs
        if football_data.current_team_id:
            matches_result = await football_api_service.get_upcoming_matches(
                football_data.current_team_id,
                next=5
            )
            
            if matches_result.get('success'):
                upcoming = []
                for fixture in matches_result.get('data', []):
                    fixture_data = fixture.get('fixture', {})
                    teams = fixture.get('teams', {})
                    league = fixture.get('league', {})
                    
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    is_home = home_team.get('id') == football_data.current_team_id
                    opponent = away_team.get('name') if is_home else home_team.get('name')
                    
                    upcoming.append({
                        "date": fixture_data.get('date'),
                        "opponent": opponent,
                        "competition": league.get('name'),
                        "is_home": is_home,
                        "venue": fixture_data.get('venue', {}).get('name')
                    })
                
                football_data.upcoming_matches = upcoming
                matches_updated = True
        
        # 4. ✅ NOUVELLE LOGIQUE INTELLIGENTE: Vérifier les blessures
        if football_data.current_team_id:
            injury_check = await football_api_service.get_player_injuries_smart(
                player_id=football_data.football_api_id,
                team_id=football_data.current_team_id,
                season=2025
            )
            
            old_injured_status = football_data.is_injured
            
            # Mettre à jour selon la nouvelle logique
            football_data.is_injured = injury_check.get('is_injured', False)
            player.is_injured = injury_check.get('is_injured', False)
            
            if injury_check.get('is_injured'):
                # Vraiment blessé
                injury_info = injury_check.get('injury_info', {})
                football_data.injury_type = injury_info.get('type')
                football_data.injury_reason = injury_info.get('reason')
                player.injury_status = injury_info.get('reason')
                logger.warning(f"❌ {player.display_name} confirmé BLESSÉ: {injury_info.get('reason')}")
            else:
                # Pas blessé ou incertain
                football_data.injury_type = None
                football_data.injury_reason = None
                player.injury_status = None
                logger.info(f"✅ {player.display_name} DISPONIBLE")
            
            injuries_updated = (old_injured_status != football_data.is_injured)
        
        # 5. Mettre à jour le timestamp
        football_data.last_api_sync = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Synchronisation terminée pour {player.display_name}")
        
        return SyncPlayerResponse(
            success=True,
            player_id=player_id,
            message=f"Synchronisation réussie pour {player.display_name}",
            synced_at=datetime.utcnow(),
            stats_updated=stats_updated,
            injuries_updated=injuries_updated,
            matches_updated=matches_updated
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la synchronisation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/{player_id}/complete", response_model=PlayerCompleteResponse)
def get_complete_player_data(
    player_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère TOUTES les données d'un joueur
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    football_data = db.query(FootballAPIData).filter(
        FootballAPIData.player_id == player_id
    ).first()
    
    football_data_response = None
    if football_data:
        football_data_dict = football_data.to_dict()
        football_data_dict.pop('detailed_stats', None)
        football_data_response = FootballAPIDataResponse(**football_data_dict)
    
    return PlayerCompleteResponse(
        id=player.id,
        sorare_id=player.sorare_id,
        display_name=player.display_name,
        first_name=player.first_name,
        last_name=player.last_name,
        club_name=player.club_name,
        position=player.position,
        country=player.country,
        age=player.age,
        average_score=player.average_score,
        total_games=player.total_games,
        is_injured=player.is_injured,
        football_data=football_data_response
    )