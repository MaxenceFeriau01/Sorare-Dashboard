"""
Routes API pour la gestion des joueurs avec support des ligues
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, Integer
from typing import Optional, List
from collections import defaultdict
from datetime import datetime
from loguru import logger
from app.models.injury import Injury

from app.database import get_db
from app.models.player import Player
from app.models.football_api_data import FootballAPIData
from app.services.football_api_service import football_api_service
from app.schemas.player import (
    PlayerResponse, 
    PlayerListResponse, 
    PlayerCreate, 
    PlayerUpdate,
    LeagueStats
)

router = APIRouter()


@router.get("/", response_model=PlayerListResponse)
def get_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    position: Optional[str] = None,
    club: Optional[str] = None,
    league: Optional[str] = None,
    is_injured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des joueurs avec filtres optionnels
    
    Nouveaux filtres:
    - league: Filtre par nom de ligue (ex: "Premier League", "Ligue 1")
    """
    query = db.query(Player)
    
    # Appliquer les filtres
    if position:
        query = query.filter(Player.position == position)
    if club:
        query = query.filter(Player.club_name.ilike(f"%{club}%"))
    if league:
        query = query.filter(Player.league_name == league)
    if is_injured is not None:
        query = query.filter(Player.is_injured == is_injured)
    
    # Compter le total
    total = query.count()
    
    # Récupérer les joueurs avec pagination
    players = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "players": players
    }


@router.get("/leagues", response_model=List[LeagueStats])
def get_leagues_stats(db: Session = Depends(get_db)):
    """
    Récupère la liste de toutes les ligues avec leurs statistiques
    
    Retourne pour chaque ligue:
    - Nom de la ligue
    - Pays
    - Nombre de joueurs
    - Score moyen
    - Nombre de blessés
    """
    # Récupérer toutes les ligues distinctes
    leagues = db.query(
        Player.league_name,
        Player.league_country,
        func.count(Player.id).label('player_count'),
        func.avg(Player.average_score).label('avg_score'),
        func.sum(func.cast(Player.is_injured, Integer)).label('injured_count')
    ).filter(
        Player.league_name.isnot(None)
    ).group_by(
        Player.league_name,
        Player.league_country
    ).order_by(
        func.count(Player.id).desc()
    ).all()
    
    # Formater les résultats
    result = []
    for league in leagues:
        result.append(LeagueStats(
            league_name=league.league_name,
            league_country=league.league_country,
            player_count=league.player_count,
            avg_score=round(float(league.avg_score or 0), 2),
            injured_count=league.injured_count or 0
        ))
    
    return result


@router.get("/leagues/list")
def get_available_leagues(db: Session = Depends(get_db)):
    """
    Récupère la liste simple des noms de ligues disponibles
    
    Utile pour les filtres dropdown dans le frontend
    """
    leagues = db.query(
        distinct(Player.league_name)
    ).filter(
        Player.league_name.isnot(None)
    ).order_by(
        Player.league_name
    ).all()
    
    return {
        "success": True,
        "leagues": [league[0] for league in leagues]
    }


@router.get("/upcoming-matches")
async def get_upcoming_matches(db: Session = Depends(get_db)):
    """
    Récupère les prochains matchs groupés par équipe
    
    Retourne uniquement les matchs où tu as au moins un joueur dans l'une des deux équipes
    """
    logger.info("📅 Récupération des prochains matchs")
    
    # 1. Récupérer tous les joueurs actifs avec leurs équipes
    players_with_teams = db.query(Player, FootballAPIData).join(
        FootballAPIData,
        Player.id == FootballAPIData.player_id
    ).filter(
        Player.is_active == True,
        FootballAPIData.current_team_id.isnot(None)
    ).all()
    
    if not players_with_teams:
        logger.info("Aucun joueur avec équipe trouvé")
        return {"matches": []}
    
    # 2. Grouper les joueurs par équipe
    teams_dict = defaultdict(list)
    team_info = {}
    
    for player, football_data in players_with_teams:
        team_id = football_data.current_team_id
        teams_dict[team_id].append(player)
        
        if team_id not in team_info:
            team_info[team_id] = {
                "name": football_data.current_team_name,
                "logo": football_data.current_team_logo
            }
    
    logger.info(f"📊 {len(teams_dict)} équipes distinctes trouvées")
    
    # 3. Récupérer les prochains matchs pour chaque équipe
    all_matches = []
    seen_fixtures = set()
    
    for team_id in teams_dict.keys():
        try:
            result = await football_api_service.get_upcoming_matches(team_id, next=3)
            
            if result.get('success') and result.get('data'):
                for fixture in result['data']:
                    fixture_id = fixture.get('fixture', {}).get('id')
                    
                    # Éviter les doublons
                    if fixture_id in seen_fixtures:
                        continue
                    
                    seen_fixtures.add(fixture_id)
                    
                    fixture_data = fixture.get('fixture', {})
                    teams = fixture.get('teams', {})
                    league = fixture.get('league', {})
                    
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    home_team_id = home_team.get('id')
                    away_team_id = away_team.get('id')
                    
                    # Vérifier si on a des joueurs dans au moins une des équipes
                    home_players = teams_dict.get(home_team_id, [])
                    away_players = teams_dict.get(away_team_id, [])
                    
                    if not home_players and not away_players:
                        continue
                    
                    all_matches.append({
                        "id": fixture_id,
                        "date": fixture_data.get('date'),
                        "timestamp": fixture_data.get('timestamp'),
                        "home_team": home_team.get('name'),
                        "away_team": away_team.get('name'),
                        "home_logo": home_team.get('logo'),
                        "away_logo": away_team.get('logo'),
                        "league": league.get('name'),
                        "venue": fixture_data.get('venue', {}).get('name'),
                        "home_players": [
                            {
                                "id": p.id,
                                "display_name": p.display_name,
                                "club_name": p.club_name,
                                "position": p.position,
                                "average_score": p.average_score,
                                "total_games": p.total_games,
                                "is_injured": p.is_injured,
                                "image_url": p.image_url
                            }
                            for p in home_players
                        ],
                        "away_players": [
                            {
                                "id": p.id,
                                "display_name": p.display_name,
                                "club_name": p.club_name,
                                "position": p.position,
                                "average_score": p.average_score,
                                "total_games": p.total_games,
                                "is_injured": p.is_injured,
                                "image_url": p.image_url
                            }
                            for p in away_players
                        ]
                    })
        
        except Exception as e:
            logger.error(f"Erreur récupération matchs équipe {team_id}: {e}")
            continue
    
    # 4. Trier par date (plus proches en premier)
    all_matches.sort(key=lambda x: x['timestamp'])
    
    # 5. Limiter à 10 matchs max
    all_matches = all_matches[:10]
    
    logger.success(f"✅ {len(all_matches)} matchs trouvés")
    
    return {"matches": all_matches}


@router.get("/upcoming-matches-with-results")
async def get_upcoming_matches_with_results(db: Session = Depends(get_db)):
    """
    Récupère les prochains matchs avec les derniers résultats H2H
    """
    logger.info("📅 Récupération des prochains matchs avec résultats")
    
    # 1. Récupérer tous les joueurs actifs avec leurs équipes
    players_with_teams = db.query(Player, FootballAPIData).join(
        FootballAPIData,
        Player.id == FootballAPIData.player_id
    ).filter(
        Player.is_active == True,
        FootballAPIData.current_team_id.isnot(None)
    ).all()
    
    if not players_with_teams:
        return {"matches": []}
    
    # 2. Grouper les joueurs par équipe
    teams_dict = defaultdict(list)
    
    for player, football_data in players_with_teams:
        team_id = football_data.current_team_id
        teams_dict[team_id].append(player)
    
    logger.info(f"📊 {len(teams_dict)} équipes distinctes trouvées")
    
    # 3. Récupérer les prochains matchs
    all_matches = []
    seen_fixtures = set()
    
    for team_id in teams_dict.keys():
        try:
            # Prochains matchs
            upcoming_result = await football_api_service.get_upcoming_matches(team_id, next=3)
            
            if upcoming_result.get('success') and upcoming_result.get('data'):
                for fixture in upcoming_result['data']:
                    fixture_id = fixture.get('fixture', {}).get('id')
                    
                    if fixture_id in seen_fixtures:
                        continue
                    
                    seen_fixtures.add(fixture_id)
                    
                    fixture_data = fixture.get('fixture', {})
                    teams = fixture.get('teams', {})
                    league = fixture.get('league', {})
                    
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    home_team_id = home_team.get('id')
                    away_team_id = away_team.get('id')
                    
                    # Vérifier si on a des joueurs
                    player_count = len(teams_dict.get(home_team_id, [])) + len(teams_dict.get(away_team_id, []))
                    
                    if player_count == 0:
                        continue
                    
                    # 🆕 Récupérer le dernier match entre ces deux équipes
                    last_result = None
                    try:
                        h2h_result = await football_api_service.get_head_to_head(home_team_id, away_team_id, last=1)
                        
                        if h2h_result.get('success') and h2h_result.get('data'):
                            last_match = h2h_result['data'][0]
                            last_fixture = last_match.get('fixture', {})
                            last_goals = last_match.get('goals', {})
                            
                            # Vérifier que c'est bien un match terminé
                            if last_fixture.get('status', {}).get('short') == 'FT':
                                last_result = {
                                    "home_score": last_goals.get('home', 0),
                                    "away_score": last_goals.get('away', 0),
                                    "date": last_fixture.get('date')
                                }
                    except Exception as e:
                        logger.warning(f"Impossible de récupérer H2H pour {home_team_id} vs {away_team_id}: {e}")
                    
                    all_matches.append({
                        "id": fixture_id,
                        "date": fixture_data.get('date'),
                        "timestamp": fixture_data.get('timestamp'),
                        "home_team": home_team.get('name'),
                        "away_team": away_team.get('name'),
                        "home_logo": home_team.get('logo'),
                        "away_logo": away_team.get('logo'),
                        "league": league.get('name'),
                        "venue": fixture_data.get('venue', {}).get('name'),
                        "player_count": player_count,
                        "last_result": last_result
                    })
        
        except Exception as e:
            logger.error(f"Erreur récupération matchs équipe {team_id}: {e}")
            continue
    
    # 4. Trier par date
    all_matches.sort(key=lambda x: x['timestamp'])
    
    # 5. Limiter à 10 matchs
    all_matches = all_matches[:10]
    
    logger.success(f"✅ {len(all_matches)} matchs trouvés avec résultats")
    
    return {"matches": all_matches}


@router.get("/match/{match_id}/details")
async def get_match_details(match_id: int, db: Session = Depends(get_db)):
    """
    Récupère les détails complets d'un match avec tous les joueurs
    """
    logger.info(f"🔍 Récupération détails match ID: {match_id}")
    
    # 1. Récupérer les infos du match depuis l'API
    try:
        fixture_result = await football_api_service.get_fixture_by_id(match_id)
        
        if not fixture_result.get('success') or not fixture_result.get('data'):
            raise HTTPException(status_code=404, detail="Match non trouvé")
        
        fixture = fixture_result['data'][0]
        fixture_data = fixture.get('fixture', {})
        teams = fixture.get('teams', {})
        league = fixture.get('league', {})
        
        home_team = teams.get('home', {})
        away_team = teams.get('away', {})
        home_team_id = home_team.get('id')
        away_team_id = away_team.get('id')
        
        # 2. Récupérer les joueurs de ces équipes
        home_players = db.query(Player).join(
            FootballAPIData,
            Player.id == FootballAPIData.player_id
        ).filter(
            Player.is_active == True,
            FootballAPIData.current_team_id == home_team_id
        ).all()
        
        away_players = db.query(Player).join(
            FootballAPIData,
            Player.id == FootballAPIData.player_id
        ).filter(
            Player.is_active == True,
            FootballAPIData.current_team_id == away_team_id
        ).all()
        
        # 3. Récupérer le dernier résultat
        last_result = None
        try:
            h2h_result = await football_api_service.get_head_to_head(home_team_id, away_team_id, last=1)
            
            if h2h_result.get('success') and h2h_result.get('data'):
                last_match = h2h_result['data'][0]
                last_fixture = last_match.get('fixture', {})
                last_goals = last_match.get('goals', {})
                
                if last_fixture.get('status', {}).get('short') == 'FT':
                    last_result = {
                        "home_score": last_goals.get('home', 0),
                        "away_score": last_goals.get('away', 0),
                        "date": last_fixture.get('date')
                    }
        except Exception as e:
            logger.warning(f"Impossible de récupérer H2H: {e}")
        
        # 4. Formater la réponse
        return {
            "id": match_id,
            "date": fixture_data.get('date'),
            "home_team": home_team.get('name'),
            "away_team": away_team.get('name'),
            "home_logo": home_team.get('logo'),
            "away_logo": away_team.get('logo'),
            "league": league.get('name'),
            "venue": fixture_data.get('venue', {}).get('name'),
            "home_players": [
                {
                    "id": p.id,
                    "display_name": p.display_name,
                    "club_name": p.club_name,
                    "position": p.position,
                    "average_score": p.average_score,
                    "total_games": p.total_games,
                    "is_injured": p.is_injured,
                    "image_url": p.image_url
                }
                for p in home_players
            ],
            "away_players": [
                {
                    "id": p.id,
                    "display_name": p.display_name,
                    "club_name": p.club_name,
                    "position": p.position,
                    "average_score": p.average_score,
                    "total_games": p.total_games,
                    "is_injured": p.is_injured,
                    "image_url": p.image_url
                }
                for p in away_players
            ],
            "last_result": last_result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération détails match: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(
    player_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère un joueur spécifique par son ID
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    
    if not player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    return player


@router.post("/", response_model=PlayerResponse, status_code=201)
def create_player(
    player: PlayerCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau joueur
    """
    # Vérifier si le joueur existe déjà
    existing = db.query(Player).filter(Player.sorare_id == player.sorare_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ce joueur existe déjà")
    
    # Créer le joueur
    db_player = Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    
    return db_player


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un joueur existant
    """
    db_player = db.query(Player).filter(Player.id == player_id).first()
    
    if not db_player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    # Mettre à jour les champs fournis
    update_data = player_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_player, field, value)
    
    db.commit()
    db.refresh(db_player)
    
    return db_player


@router.delete("/{player_id}")
def delete_player(
    player_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime un joueur et toutes ses données associées
    """
    # 1. Récupérer le joueur
    db_player = db.query(Player).filter(Player.id == player_id).first()
    
    if not db_player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    player_name = db_player.display_name
    
    # 2. Supprimer les données FootballAPIData liées
    db.query(FootballAPIData).filter(
        FootballAPIData.player_id == player_id
    ).delete()
    
    # 3. Supprimer les blessures liées
    db.query(Injury).filter(
        Injury.player_id == player_id
    ).delete()
    
    # 4. Supprimer les prédictions de match liées (si la table existe)
    try:
        from app.models.match_prediction import MatchPrediction
        db.query(MatchPrediction).filter(
            MatchPrediction.player_id == player_id
        ).delete()
    except:
        pass  # La table n'existe peut-être pas encore
    
    # 5. Supprimer le joueur
    db.delete(db_player)
    
    # 6. Commit
    db.commit()
    
    logger.success(f"✅ Joueur {player_name} (ID: {player_id}) supprimé avec toutes ses données")
    
    return {"message": f"Joueur {player_name} supprimé avec succès"}