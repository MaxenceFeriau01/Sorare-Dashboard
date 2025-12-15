"""
Routes API pour la gestion des joueurs avec support des ligues
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, Integer
from typing import Optional, List

from app.database import get_db
from app.models.player import Player
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
    league: Optional[str] = None,  # 🆕 Filtre par ligue
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
    if league:  # 🆕
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
        Player.league_name.isnot(None)  # Exclure les joueurs sans ligue
    ).group_by(
        Player.league_name,
        Player.league_country
    ).order_by(
        func.count(Player.id).desc()  # Trier par nombre de joueurs
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
    Supprime un joueur
    """
    db_player = db.query(Player).filter(Player.id == player_id).first()
    
    if not db_player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    db.delete(db_player)
    db.commit()
    
    return {"message": f"Joueur {db_player.display_name} supprimé avec succès"}