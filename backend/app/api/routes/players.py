"""
Routes API pour la gestion des joueurs
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.player import Player
from app.schemas.player import PlayerResponse, PlayerListResponse, PlayerCreate, PlayerUpdate

router = APIRouter()


@router.get("/", response_model=PlayerListResponse)
def get_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    position: Optional[str] = None,
    club: Optional[str] = None,
    is_injured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des joueurs avec filtres optionnels
    """
    query = db.query(Player)
    
    # Appliquer les filtres
    if position:
        query = query.filter(Player.position == position)
    if club:
        query = query.filter(Player.club_name.ilike(f"%{club}%"))
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


@router.delete("/{player_id}", status_code=204)
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
    
    return None