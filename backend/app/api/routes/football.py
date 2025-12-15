"""
Routes API pour l'intégration API-Football
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger
from datetime import datetime

from app.services.football_api_service import football_api_service
from app.database import get_db
from app.models.player import Player
from app.models.football_api_data import FootballAPIData
from app.models.injury import Injury

router = APIRouter()


# ============================================
# STATUS & INFOS
# ============================================

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


# ============================================
# RECHERCHE JOUEURS
# ============================================

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


# ============================================
# ÉQUIPES
# ============================================

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


# ============================================
# MATCHS
# ============================================

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


# ============================================
# LIGUES
# ============================================

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


# ============================================
# BLESSURES
# ============================================

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


# ============================================
# 🆕 PRÉDICTIONS
# ============================================

@router.get("/player/{player_id}/next-match-prediction")
async def get_player_next_match_with_prediction(
    player_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère le prochain match d'un joueur avec prédictions
    
    Retourne:
    - Infos du prochain match
    - Prédictions (gagnant, score, etc.)
    - Score de jouabilité (0-10)
    - Conseils pour Sorare
    """
    # Récupérer les données API-Football du joueur
    football_data = db.query(FootballAPIData).filter(
        FootballAPIData.player_id == player_id
    ).first()
    
    if not football_data or not football_data.football_api_id:
        raise HTTPException(
            status_code=404,
            detail="Données API-Football non trouvées pour ce joueur"
        )
    
    if not football_data.current_team_id:
        raise HTTPException(
            status_code=404,
            detail="Équipe actuelle non trouvée pour ce joueur"
        )
    
    # Récupérer le prochain match avec prédictions
    result = await football_api_service.get_player_next_match_prediction(
        football_data.football_api_id,
        football_data.current_team_id
    )
    
    if not result.get('success'):
        raise HTTPException(
            status_code=404,
            detail=result.get('message', 'Aucun prochain match trouvé')
        )
    
    return result


@router.get("/dashboard-predictions")
async def get_dashboard_predictions(
    db: Session = Depends(get_db)
):
    """
    Récupère les prédictions pour tous les joueurs du dashboard
    
    Retourne une liste avec:
    - Joueur
    - Prochain match
    - Prédictions
    - Score de jouabilité
    """
    # Récupérer tous les joueurs actifs avec données API-Football
    players_with_data = db.query(Player, FootballAPIData).join(
        FootballAPIData,
        Player.id == FootballAPIData.player_id
    ).filter(
        Player.is_active == True,
        FootballAPIData.current_team_id.isnot(None)
    ).limit(20).all()  # Limiter à 20 pour ne pas dépasser le rate limit
    
    predictions_list = []
    
    for player, football_data in players_with_data:
        try:
            # Récupérer le prochain match avec prédictions
            result = await football_api_service.get_player_next_match_prediction(
                football_data.football_api_id,
                football_data.current_team_id
            )
            
            if result.get('success'):
                predictions_list.append({
                    'player': {
                        'id': player.id,
                        'name': player.display_name,
                        'position': player.position,
                        'club': player.club_name,
                        'image': player.image_url
                    },
                    'match': result.get('match'),
                    'prediction': result.get('prediction'),
                    'playability_score': result.get('playability_score'),
                    'has_prediction': result.get('has_prediction', False)
                })
        except Exception as e:
            logger.error(f"Erreur prédiction pour {player.display_name}: {e}")
            continue
    
    # Trier par score de jouabilité (décroissant)
    predictions_list.sort(
        key=lambda x: x.get('playability_score', {}).get('score', 0),
        reverse=True
    )

    
    return {
        'success': True,
        'count': len(predictions_list),
        'predictions': predictions_list
    }

@router.get("/team/{team_id}/squad")
async def get_team_squad(team_id: int, db: Session = Depends(get_db)):
    """
    ✅ VERSION CORRIGÉE - Récupère l'effectif complet d'une équipe
    """
    logger.info(f"📋 Récupération de l'effectif de l'équipe ID: {team_id}")
    
    # Récupérer l'effectif depuis l'API-Football
    result = await football_api_service.get_team_squad(team_id)
    
    if not result.get('success'):
        raise HTTPException(status_code=404, detail="Effectif non trouvé")
    
    data = result.get('data', [])
    if not data:
        raise HTTPException(status_code=404, detail="Aucune donnée retournée")
    
    # ✅ CORRECTION: L'API retourne [{ "team": {...}, "players": [...] }]
    squad_data = data[0]
    team_info = squad_data.get('team', {})
    players_list = squad_data.get('players', [])
    
    logger.info(f"✅ {len(players_list)} joueurs trouvés")
    
    # Formater les joueurs pour le frontend
    formatted_players = []
    player_ids = []
    
    for player in players_list:
        player_id = player.get('id')
        if player_id:
            player_ids.append(player_id)
            
        formatted_players.append({
            "id": player_id,
            "name": player.get('name'),
            "firstname": player.get('firstname'),
            "lastname": player.get('lastname'),
            "age": player.get('age'),
            "number": player.get('number'),
            "position": player.get('position'),
            "photo": player.get('photo'),
            "nationality": player.get('nationality')
        })
    
    # Vérifier quels joueurs sont déjà importés
    existing_players = db.query(FootballAPIData).filter(
        FootballAPIData.football_api_id.in_(player_ids)
    ).all() if player_ids else []
    
    existing_ids = {fp.football_api_id: fp.player_id for fp in existing_players}
    
    # Enrichir avec le statut d'import
    for player in formatted_players:
        player_api_id = player['id']
        player['is_imported'] = player_api_id in existing_ids
        player['dashboard_player_id'] = existing_ids.get(player_api_id)
    
    return {
        "success": True,
        "team": {
            "id": team_info.get('id'),
            "name": team_info.get('name'),
            "logo": team_info.get('logo')
        },
        "players": formatted_players,
        "count": len(formatted_players),
        "imported_count": len(existing_ids)
    }


@router.post("/team/{team_id}/import-player/{player_id}")
async def import_player_from_team(
    team_id: int,
    player_id: int,
    db: Session = Depends(get_db)
):
    """
    Importe un joueur depuis l'effectif d'une équipe
    
    Crée automatiquement un sorare_id basé sur le nom du joueur
    
    Exemple: POST /team/541/import-player/276
    """
    logger.info(f"📥 Import joueur {player_id} depuis équipe {team_id}")
    
    # Récupérer les données du joueur depuis l'API
    player_result = await football_api_service.get_player_by_id(player_id, 2025)
    
    if not player_result.get('success') or not player_result.get('data'):
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    player_data = player_result['data'][0]
    player_info = player_data.get('player', {})
    
    # Vérifier si le joueur existe déjà
    existing = db.query(FootballAPIData).filter(
        FootballAPIData.football_api_id == player_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ce joueur est déjà importé (ID: {existing.player_id})"
        )
    
    # Générer un sorare_id automatique
    # Format: prenom-nom-apiid (ex: kylian-mbappe-276)
    firstname = player_info.get('firstname', '').lower().replace(' ', '-')
    lastname = player_info.get('lastname', '').lower().replace(' ', '-')
    sorare_id = f"{firstname}-{lastname}-{player_id}"
    
    # Utiliser la route d'import existante
    from app.api.routes.football_integration import import_player_from_football_api
    from app.schemas.football_api import ImportPlayerRequest
    
    import_request = ImportPlayerRequest(
        football_api_id=player_id,
        sorare_id=sorare_id,
        display_name=player_info.get('name'),
        position=None  # Sera rempli automatiquement
    )
    
    result = await import_player_from_football_api(import_request, db)
    
    return {
        "success": True,
        "message": f"Joueur {player_info.get('name')} importé avec succès",
        "player": result
    }

# ✅ À AJOUTER dans backend/app/api/routes/football.py

@router.post("/sync-injuries")
async def sync_injuries(db: Session = Depends(get_db)):
    """
    ✅ VERSION OPTIMISÉE - Synchronise les blessures avec validation
    
    OPTIMISATIONS:
    - Limite à 10 joueurs max
    - Déduplication des blessures
    - Logs clairs
    """
    logger.info("🔄 Synchronisation des blessures avec validation")
    
    # ✅ LIMITER À 10 JOUEURS pour éviter le timeout
    players_with_teams = db.query(Player, FootballAPIData).join(
        FootballAPIData,
        Player.id == FootballAPIData.player_id
    ).filter(
        Player.is_active == True,
        FootballAPIData.football_api_id.isnot(None),
        FootballAPIData.current_team_id.isnot(None)
    ).limit(10).all()  # ✅ MAX 10 JOUEURS
    
    logger.info(f"📊 {len(players_with_teams)} joueur(s) à vérifier (max 10)")
    
    total_checked = 0
    injuries_found = 0
    injuries_cleared = 0
    errors = []
    
    for player, football_data in players_with_teams:
        try:
            logger.info(f"🔍 [{total_checked + 1}/{len(players_with_teams)}] Vérification: {player.display_name}")
            
            # Appeler la fonction smart avec validation
            result = await football_api_service.get_player_injuries_smart(
                player_id=football_data.football_api_id,
                team_id=football_data.current_team_id,
                season=2025
            )
            
            if not result.get('success'):
                logger.warning(f"⚠️ Impossible de vérifier {player.display_name}")
                continue
            
            validated_injuries = result.get('data', [])
            total_checked += 1
            
            if validated_injuries:
                # ✅ PRENDRE SEULEMENT LA PREMIÈRE BLESSURE (pas de duplicatas)
                injury_info = validated_injuries[0].get('player', {})
                
                player.is_injured = True
                player.injury_status = injury_info.get('reason', 'Injury')
                
                # Créer/mettre à jour dans la table injuries
                existing_injury = db.query(Injury).filter(
                    Injury.player_id == player.id,
                    Injury.is_active == True
                ).first()
                
                if not existing_injury:
                    new_injury = Injury(
                        player_id=player.id,
                        injury_type=injury_info.get('type', 'Unknown'),
                        injury_description=injury_info.get('reason', ''),
                        severity='Moderate',
                        is_active=True,
                        injury_date=datetime.now()
                    )
                    db.add(new_injury)
                    injuries_found += 1
                    logger.success(f"✅ Blessure confirmée: {player.display_name}")
                else:
                    existing_injury.updated_at = datetime.now()
                    logger.info(f"🔄 Blessure mise à jour: {player.display_name}")
            
            else:
                # Pas de blessure ou invalidée
                if player.is_injured:
                    player.is_injured = False
                    player.injury_status = None
                    
                    # Désactiver les blessures actives
                    active_injuries = db.query(Injury).filter(
                        Injury.player_id == player.id,
                        Injury.is_active == True
                    ).all()
                    
                    for injury in active_injuries:
                        injury.is_active = False
                        injury.recovery_date = datetime.now()
                    
                    injuries_cleared += 1
                    logger.success(f"✅ Blessure invalidée: {player.display_name}")
            
            db.commit()
            
        except Exception as e:
            error_msg = f"{player.display_name}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"❌ Erreur pour {player.display_name}: {e}")
            db.rollback()
            continue
    
    logger.success(f"🎯 SYNCHRONISATION TERMINÉE: {total_checked} vérifiés, {injuries_found} confirmées, {injuries_cleared} invalidées")
    
    return {
        "success": True,
        "message": "Synchronisation terminée",
        "stats": {
            "total_checked": total_checked,
            "injuries_found": injuries_found,
            "injuries_cleared": injuries_cleared,
            "errors": len(errors)
        },
        "errors": errors[:5] if errors else []  # Max 5 erreurs dans la réponse
    }