"""
Routes API pour les statistiques du dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.player import Player
from app.models.injury import Injury
from app.models.update import Update

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Récupère toutes les statistiques pour le dashboard principal
    """
    
    # Stats générales des joueurs
    total_players = db.query(Player).count()
    active_players = db.query(Player).filter(Player.is_active == True).count()
    injured_players = db.query(Player).filter(Player.is_injured == True).count()
    
    # Score moyen de l'équipe
    avg_team_score = db.query(func.avg(Player.average_score)).scalar() or 0.0
    
    # Joueurs par position
    players_by_position = db.query(
        Player.position,
        func.count(Player.id).label('count')
    ).filter(
        Player.position.isnot(None)
    ).group_by(
        Player.position
    ).all()
    
    position_distribution = {pos: count for pos, count in players_by_position}
    
    # Top 5 joueurs par score moyen
    top_players = db.query(Player).filter(
        Player.average_score > 0
    ).order_by(
        desc(Player.average_score)
    ).limit(5).all()
    
    top_players_data = [
        {
            "id": p.id,
            "name": p.display_name,
            "club": p.club_name,
            "position": p.position,
            "score": p.average_score,
            "games": p.total_games
        }
        for p in top_players
    ]
    
    # Blessures actives
    active_injuries_count = db.query(Injury).filter(Injury.is_active == True).count()
    
    # Dernière mise à jour
    last_update = db.query(Update).order_by(desc(Update.created_at)).first()
    last_update_info = None
    if last_update:
        last_update_info = {
            "type": last_update.update_type,
            "status": last_update.status,
            "date": last_update.created_at.isoformat(),
            "items_processed": last_update.items_processed
        }
    
    return {
        "overview": {
            "total_players": total_players,
            "active_players": active_players,
            "injured_players": injured_players,
            "avg_team_score": round(avg_team_score, 2),
            "active_injuries_count": active_injuries_count
        },
        "position_distribution": position_distribution,
        "top_players": top_players_data,
        "last_update": last_update_info
    }