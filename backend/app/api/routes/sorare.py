"""
Routes API pour la synchronisation avec Sorare
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

from app.database import get_db
from app.models.player import Player
from app.services.sorare_service import sorare_service

router = APIRouter()


@router.post("/sync")
def sync_players_from_sorare(db: Session = Depends(get_db)):
    """
    Synchronise les joueurs depuis ton compte Sorare
    
    - Se connecte à ton compte Sorare
    - Récupère toutes tes cartes
    - Ajoute ou met à jour les joueurs dans la base de données
    """
    try:
        # Connexion à Sorare
        logger.info("🔌 Connexion à Sorare...")
        if not sorare_service.connect():
            raise HTTPException(
                status_code=500,
                detail="Impossible de se connecter à Sorare. Vérifie tes identifiants dans le .env"
            )
        
        # Récupérer les cartes
        logger.info("📥 Récupération de tes cartes Sorare...")
        cards = sorare_service.get_my_cards(limit=100)
        
        if not cards:
            return {
                "message": "Aucune carte trouvée sur ton compte Sorare",
                "players_added": 0,
                "players_updated": 0,
                "total_cards": 0
            }
        
        players_added = 0
        players_updated = 0
        players_processed = set()  # Pour éviter les doublons
        
        # Traiter chaque carte
        for card in cards:
            player_data = card.get("player")
            if not player_data:
                continue
            
            player_slug = player_data.get("slug")
            
            # Éviter de traiter le même joueur plusieurs fois
            if player_slug in players_processed:
                continue
            
            players_processed.add(player_slug)
            
            # Formater les données pour la DB
            player_dict = sorare_service.format_player_for_db(player_data)
            
            # Vérifier si le joueur existe déjà
            existing_player = db.query(Player).filter(
                Player.sorare_id == player_slug
            ).first()
            
            if existing_player:
                # Mettre à jour le joueur existant
                for key, value in player_dict.items():
                    setattr(existing_player, key, value)
                existing_player.last_sorare_sync = datetime.now()
                players_updated += 1
                logger.info(f"🔄 Mise à jour: {player_dict['display_name']}")
            else:
                # Créer un nouveau joueur
                new_player = Player(**player_dict)
                new_player.last_sorare_sync = datetime.now()
                db.add(new_player)
                players_added += 1
                logger.info(f"✨ Nouveau: {player_dict['display_name']}")
        
        # Sauvegarder dans la DB
        db.commit()
        
        logger.success(f"✅ Synchronisation terminée: {players_added} ajoutés, {players_updated} mis à jour")
        
        return {
            "message": "Synchronisation réussie",
            "total_cards": len(cards),
            "unique_players": len(players_processed),
            "players_added": players_added,
            "players_updated": players_updated
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la synchronisation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la synchronisation: {str(e)}"
        )


@router.get("/test-connection")
def test_sorare_connection():
    """
    Test la connexion à Sorare
    
    Utile pour vérifier que tes identifiants sont corrects
    """
    try:
        logger.info("🔌 Test de connexion à Sorare...")
        
        if sorare_service.connect():
            return {
                "status": "success",
                "message": "✅ Connexion à Sorare réussie !",
                "email": sorare_service.email
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="❌ Échec de connexion. Vérifie tes identifiants SORARE_EMAIL et SORARE_PASSWORD dans le .env"
            )
    
    except Exception as e:
        logger.error(f"❌ Erreur lors du test de connexion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/player/{player_slug}")
def get_sorare_player_info(player_slug: str):
    """
    Récupère les infos d'un joueur spécifique depuis Sorare
    
    Utile pour tester ou récupérer un joueur en particulier
    """
    try:
        # Connexion à Sorare
        if not sorare_service.connect():
            raise HTTPException(
                status_code=500,
                detail="Impossible de se connecter à Sorare"
            )
        
        # Récupérer les infos du joueur
        player_info = sorare_service.get_player_info(player_slug)
        
        if not player_info:
            raise HTTPException(
                status_code=404,
                detail=f"Joueur {player_slug} non trouvé sur Sorare"
            )
        
        return player_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur: {str(e)}"
        )