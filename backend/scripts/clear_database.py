"""
Script pour vider complètement la base de données
ATTENTION: Supprime toutes les données !

Usage:
    python clear_database.py
"""
import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.player import Player
from app.models.injury import Injury
from app.models.update import Update
from loguru import logger

# Configuration des logs
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


def clear_database(db: Session):
    """Supprime toutes les données de la base"""
    
    logger.warning("=" * 60)
    logger.warning("⚠️  SUPPRESSION DE TOUTES LES DONNÉES")
    logger.warning("=" * 60)
    
    # Compter les données avant suppression
    injuries_count = db.query(Injury).count()
    players_count = db.query(Player).count()
    updates_count = db.query(Update).count()
    
    logger.info(f"📊 Données à supprimer:")
    logger.info(f"   • {injuries_count} blessures")
    logger.info(f"   • {players_count} joueurs")
    logger.info(f"   • {updates_count} mises à jour")
    
    # Demander confirmation
    response = input("\n❓ Es-tu sûr de vouloir tout supprimer ? (oui/non): ")
    
    if response.lower() not in ["oui", "yes", "y", "o"]:
        logger.info("❌ Suppression annulée")
        return
    
    logger.warning("\n🗑️  Suppression en cours...")
    
    try:
        # Supprimer dans l'ordre (à cause des foreign keys)
        db.query(Injury).delete()
        logger.success(f"   ✓ {injuries_count} blessures supprimées")
        
        db.query(Update).delete()
        logger.success(f"   ✓ {updates_count} mises à jour supprimées")
        
        db.query(Player).delete()
        logger.success(f"   ✓ {players_count} joueurs supprimés")
        
        db.commit()
        
        logger.success("\n✅ Base de données vidée avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression: {e}")
        db.rollback()
        raise


def main():
    """Fonction principale"""
    db = SessionLocal()
    
    try:
        clear_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()