"""
Routes API pour la gestion des blessures
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.injury import Injury
from app.models.player import Player
from app.schemas.injury import InjuryResponse, InjuryListResponse, InjuryCreate, InjuryUpdate

router = APIRouter()


@router.get("/", response_model=InjuryListResponse)
def get_injuries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    player_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des blessures avec filtres optionnels
    """
    query = db.query(Injury)
    
    # Appliquer les filtres
    if player_id:
        query = query.filter(Injury.player_id == player_id)
    if is_active is not None:
        query = query.filter(Injury.is_active == is_active)
    
    # Trier par date de création (plus récentes d'abord)
    query = query.order_by(Injury.created_at.desc())
    
    # Compter le total
    total = query.count()
    
    # Récupérer les blessures avec pagination
    injuries = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "injuries": injuries
    }


@router.get("/{injury_id}", response_model=InjuryResponse)
def get_injury(
    injury_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère une blessure spécifique par son ID
    """
    injury = db.query(Injury).filter(Injury.id == injury_id).first()
    
    if not injury:
        raise HTTPException(status_code=404, detail="Blessure non trouvée")
    
    return injury


@router.post("/", response_model=InjuryResponse, status_code=201)
def create_injury(
    injury: InjuryCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle blessure
    """
    # Vérifier que le joueur existe
    player = db.query(Player).filter(Player.id == injury.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    # Créer la blessure
    db_injury = Injury(**injury.model_dump())
    db.add(db_injury)
    
    # Mettre à jour le statut du joueur
    player.is_injured = True
    if injury.injury_description:
        player.injury_status = injury.injury_description
    
    db.commit()
    db.refresh(db_injury)
    
    return db_injury


@router.put("/{injury_id}", response_model=InjuryResponse)
def update_injury(
    injury_id: int,
    injury_update: InjuryUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une blessure existante
    """
    db_injury = db.query(Injury).filter(Injury.id == injury_id).first()
    
    if not db_injury:
        raise HTTPException(status_code=404, detail="Blessure non trouvée")
    
    # Mettre à jour les champs fournis
    update_data = injury_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_injury, field, value)
    
    # Si la blessure devient inactive, mettre à jour le joueur
    if update_data.get("is_active") == False:
        player = db.query(Player).filter(Player.id == db_injury.player_id).first()
        if player:
            # Vérifier s'il a d'autres blessures actives
            other_injuries = db.query(Injury).filter(
                Injury.player_id == player.id,
                Injury.id != injury_id,
                Injury.is_active == True
            ).count()
            
            if other_injuries == 0:
                player.is_injured = False
                player.injury_status = None
    
    db.commit()
    db.refresh(db_injury)
    
    return db_injury


@router.delete("/{injury_id}", status_code=204)
def delete_injury(
    injury_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime une blessure
    """
    db_injury = db.query(Injury).filter(Injury.id == injury_id).first()
    
    if not db_injury:
        raise HTTPException(status_code=404, detail="Blessure non trouvée")
    
    player_id = db_injury.player_id
    
    db.delete(db_injury)
    db.commit()
    
    # Vérifier si le joueur a d'autres blessures actives
    player = db.query(Player).filter(Player.id == player_id).first()
    if player:
        active_injuries = db.query(Injury).filter(
            Injury.player_id == player_id,
            Injury.is_active == True
        ).count()
        
        if active_injuries == 0:
            player.is_injured = False
            player.injury_status = None
            db.commit()
    
    return None