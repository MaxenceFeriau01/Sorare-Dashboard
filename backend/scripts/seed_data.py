"""
Script de seed pour insérer des données de test dans la base de données
Execute ce script pour avoir des joueurs de test dans ton dashboard

Usage:
    python seed_data.py
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.player import Player
from app.models.injury import Injury
from loguru import logger

# Configuration des logs
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


# Données de test réalistes
PLAYERS_DATA = [
    {
        "sorare_id": "kylian-mbappe",
        "first_name": "Kylian",
        "last_name": "Mbappé",
        "display_name": "Kylian Mbappé",
        "slug": "kylian-mbappe",
        "club_name": "Real Madrid",
        "club_slug": "real-madrid",
        "position": "Forward",
        "country": "France",
        "country_code": "FR",
        "age": 25,
        "birth_date": "1998-12-20",
        "average_score": 68.5,
        "total_games": 15,
        "season_games": 15,
        "last_game_score": 72.0,
        "is_active": True,
        "is_injured": False,
    },
    {
        "sorare_id": "erling-haaland",
        "first_name": "Erling",
        "last_name": "Haaland",
        "display_name": "Erling Haaland",
        "slug": "erling-haaland",
        "club_name": "Manchester City",
        "club_slug": "manchester-city",
        "position": "Forward",
        "country": "Norway",
        "country_code": "NO",
        "age": 24,
        "birth_date": "2000-07-21",
        "average_score": 71.2,
        "total_games": 14,
        "season_games": 14,
        "last_game_score": 85.0,
        "is_active": True,
        "is_injured": False,
    },
    {
        "sorare_id": "vinicius-junior",
        "first_name": "Vinícius",
        "last_name": "Júnior",
        "display_name": "Vinícius Jr.",
        "slug": "vinicius-junior",
        "club_name": "Real Madrid",
        "club_slug": "real-madrid",
        "position": "Forward",
        "country": "Brazil",
        "country_code": "BR",
        "age": 24,
        "birth_date": "2000-07-12",
        "average_score": 65.8,
        "total_games": 16,
        "season_games": 16,
        "last_game_score": 70.5,
        "is_active": True,
        "is_injured": True,
        "injury_status": "Blessure musculaire",
    },
    {
        "sorare_id": "kevin-de-bruyne",
        "first_name": "Kevin",
        "last_name": "De Bruyne",
        "display_name": "Kevin De Bruyne",
        "slug": "kevin-de-bruyne",
        "club_name": "Manchester City",
        "club_slug": "manchester-city",
        "position": "Midfielder",
        "country": "Belgium",
        "country_code": "BE",
        "age": 33,
        "birth_date": "1991-06-28",
        "average_score": 63.4,
        "total_games": 12,
        "season_games": 12,
        "last_game_score": 68.0,
        "is_active": True,
        "is_injured": False,
    },
    {
        "sorare_id": "jude-bellingham",
        "first_name": "Jude",
        "last_name": "Bellingham",
        "display_name": "Jude Bellingham",
        "slug": "jude-bellingham",
        "club_name": "Real Madrid",
        "club_slug": "real-madrid",
        "position": "Midfielder",
        "country": "England",
        "country_code": "GB",
        "age": 21,
        "birth_date": "2003-06-29",
        "average_score": 69.3,
        "total_games": 15,
        "season_games": 15,
        "last_game_score": 75.0,
        "is_active": True,
        "is_injured": False,
    },
    {
        "sorare_id": "rodri",
        "first_name": "Rodrigo",
        "last_name": "Hernández",
        "display_name": "Rodri",
        "slug": "rodri",
        "club_name": "Manchester City",
        "club_slug": "manchester-city",
        "position": "Midfielder",
        "country": "Spain",
        "country_code": "ES",
        "age": 28,
        "birth_date": "1996-06-22",
        "average_score": 66.7,
        "total_games": 0,
        "season_games": 0,
        "last_game_score": None,
        "is_active": False,
        "is_injured": True,
        "injury_status": "Rupture ligament croisé (grave)",
    },
    {
        "sorare_id": "virgil-van-dijk",
        "first_name": "Virgil",
        "last_name": "van Dijk",
        "display_name": "Virgil van Dijk",
        "slug": "virgil-van-dijk",
        "club_name": "Liverpool",
        "club_slug": "liverpool",
        "position": "Defender",
        "country": "Netherlands",
        "country_code": "NL",
        "age": 33,
        "birth_date": "1991-07-08",
        "average_score": 64.2,
        "total_games": 14,
        "season_games": 14,
        "last_game_score": 67.0,
        "is_active": True,
        "is_injured": False,
    },
    {
        "sorare_id": "ruben-dias",
        "first_name": "Rúben",
        "last_name": "Dias",
        "display_name": "Rúben Dias",
        "slug": "ruben-dias",
        "club_name": "Manchester City",
        "club_slug": "manchester-city",
        "position": "Defender",
        "country": "Portugal",
        "country_code": "PT",
        "age": 27,
        "birth_date": "1997-05-14",
        "average_score": 62.1,
        "total_games": 13,
        "season_games": 13,
        "last_game_score": 65.0,
        "is_active": True,
        "is_injured": False,
    },
    {
        "sorare_id": "thibaut-courtois",
        "first_name": "Thibaut",
        "last_name": "Courtois",
        "display_name": "Thibaut Courtois",
        "slug": "thibaut-courtois",
        "club_name": "Real Madrid",
        "club_slug": "real-madrid",
        "position": "Goalkeeper",
        "country": "Belgium",
        "country_code": "BE",
        "age": 32,
        "birth_date": "1992-05-11",
        "average_score": 58.9,
        "total_games": 10,
        "season_games": 10,
        "last_game_score": 60.5,
        "is_active": True,
        "is_injured": False,
    },
    {
        "sorare_id": "alisson-becker",
        "first_name": "Alisson",
        "last_name": "Becker",
        "display_name": "Alisson",
        "slug": "alisson-becker",
        "club_name": "Liverpool",
        "club_slug": "liverpool",
        "position": "Goalkeeper",
        "country": "Brazil",
        "country_code": "BR",
        "age": 32,
        "birth_date": "1992-10-02",
        "average_score": 61.3,
        "total_games": 12,
        "season_games": 12,
        "last_game_score": 63.0,
        "is_active": True,
        "is_injured": False,
    },
]

# Données de blessures de test
INJURIES_DATA = [
    {
        "player_slug": "vinicius-junior",
        "injury_type": "Muscle",
        "injury_description": "Blessure aux ischio-jambiers",
        "severity": "Moderate",
        "injury_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "expected_return_date": (datetime.now() + timedelta(days=10)).isoformat(),
        "is_active": True,
        "source": "L'Équipe",
        "source_url": "https://www.lequipe.fr",
    },
    {
        "player_slug": "rodri",
        "injury_type": "Ligament",
        "injury_description": "Rupture du ligament croisé antérieur",
        "severity": "Severe",
        "injury_date": (datetime.now() - timedelta(days=60)).isoformat(),
        "expected_return_date": (datetime.now() + timedelta(days=200)).isoformat(),
        "is_active": True,
        "source": "Manchester City Official",
        "source_url": "https://www.mancity.com",
    },
]


def seed_players(db: Session):
    """Insère les joueurs de test"""
    logger.info("🌱 Début du seed des joueurs...")
    
    created = 0
    updated = 0
    
    for player_data in PLAYERS_DATA:
        # Vérifier si le joueur existe déjà
        existing_player = db.query(Player).filter(
            Player.sorare_id == player_data["sorare_id"]
        ).first()
        
        if existing_player:
            # Mettre à jour
            for key, value in player_data.items():
                setattr(existing_player, key, value)
            updated += 1
            logger.debug(f"   ↻ Mis à jour: {player_data['display_name']}")
        else:
            # Créer
            new_player = Player(**player_data)
            db.add(new_player)
            created += 1
            logger.success(f"   ✓ Créé: {player_data['display_name']}")
    
    db.commit()
    
    logger.success(f"✅ Joueurs: {created} créés, {updated} mis à jour")
    return created, updated


def seed_injuries(db: Session):
    """Insère les blessures de test"""
    logger.info("🌱 Début du seed des blessures...")
    
    created = 0
    
    for injury_data in INJURIES_DATA:
        # Récupérer le joueur
        player = db.query(Player).filter(
            Player.slug == injury_data["player_slug"]
        ).first()
        
        if not player:
            logger.warning(f"   ⚠️  Joueur non trouvé: {injury_data['player_slug']}")
            continue
        
        # Vérifier si la blessure existe déjà
        existing_injury = db.query(Injury).filter(
            Injury.player_id == player.id,
            Injury.is_active == True
        ).first()
        
        if not existing_injury:
            injury_data_copy = injury_data.copy()
            del injury_data_copy["player_slug"]
            injury_data_copy["player_id"] = player.id
            
            new_injury = Injury(**injury_data_copy)
            db.add(new_injury)
            created += 1
            logger.success(f"   ✓ Blessure créée pour: {player.display_name}")
    
    db.commit()
    
    logger.success(f"✅ Blessures: {created} créées")
    return created


def clear_data(db: Session):
    """Supprime toutes les données (optionnel)"""
    logger.warning("🗑️  Suppression de toutes les données...")
    
    db.query(Injury).delete()
    db.query(Player).delete()
    db.commit()
    
    logger.success("✅ Toutes les données supprimées")


def main():
    """Fonction principale"""
    logger.info("=" * 60)
    logger.info("🌱 SEED DE LA BASE DE DONNÉES")
    logger.info("=" * 60)
    
    # Créer une session
    db = SessionLocal()
    
    try:
        # Option: Supprimer toutes les données existantes (décommente si besoin)
        # clear_data(db)
        
        # Insérer les joueurs
        players_created, players_updated = seed_players(db)
        
        # Insérer les blessures
        injuries_created = seed_injuries(db)
        
        logger.info("\n" + "=" * 60)
        logger.success("🎉 SEED TERMINÉ AVEC SUCCÈS!")
        logger.info("=" * 60)
        logger.info(f"📊 Résumé:")
        logger.info(f"   • Joueurs créés: {players_created}")
        logger.info(f"   • Joueurs mis à jour: {players_updated}")
        logger.info(f"   • Blessures créées: {injuries_created}")
        logger.info("=" * 60)
        
        logger.info("\n💡 Tu peux maintenant:")
        logger.info("   1. Actualiser ton frontend (http://localhost:3000)")
        logger.info("   2. Voir l'API (http://localhost:8000/docs)")
        logger.info("   3. Consulter les joueurs (http://localhost:8000/api/v1/players)")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du seed: {e}")
        logger.exception("Détails de l'erreur:")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()