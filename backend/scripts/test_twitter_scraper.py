# Fichier: scripts/test_twitter_scraper.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# La ligne ci-dessus ajoute le répertoire 'backend' au PYTHONPATH
"""
Script de test pour valider le scraping Twitter/X.
Ce script charge manuellement le fichier .env avant l'exécution.
"""
from dotenv import load_dotenv
# 💥 CORRECTION ESSENTIELLE : Charger les variables d'environnement du .env
load_dotenv() 

from app.config import settings
from app.scrapers.twitter_scraper import TwitterSeleniumScraper
from loguru import logger
from time import sleep

# Configuration de Loguru pour s'assurer que les messages sont visibles
logger.add("test_twitter.log", rotation="10 MB") 


def test_scraper():
    """Fonction pour tester le scraper Twitter/X"""
    
    logger.info("--- Démarrage du Test Twitter Scraper ---")
    
    # 1. Vérification des identifiants dans les settings
    if not settings.TWITTER_EMAIL or not settings.TWITTER_PASSWORD:
        logger.error("❌ Les identifiants TWITTER_EMAIL ou TWITTER_PASSWORD sont vides dans les settings.")
        logger.error("Vérifiez le fichier .env ! Le test s'arrête.")
        return

    logger.info(f"✅ Identifiants chargés pour l'utilisateur: {settings.TWITTER_USERNAME}")
    
    scraper = None
    try:
        # 2. Instancier le Scraper
        scraper = TwitterSeleniumScraper(
            twitter_email=settings.TWITTER_EMAIL,
            twitter_password=settings.TWITTER_PASSWORD,
            twitter_username=settings.TWITTER_USERNAME
        )
        
        # 3. Exécuter la fonction de recherche (cela va déclencher l'init du driver et le login)
        logger.info("Tentative de recherche d'actualités pour 'Neymar'")
        results = scraper.search_player_news("Neymar")
        
        logger.info("--- Analyse des résultats de recherche ---")
        if results:
            logger.success(f"🎉 TEST RÉUSSI : {len(results)} tweets trouvés pour Neymar.")
            logger.debug(f"Premier tweet : {results[0]['content'][:100]}...")
        else:
            logger.warning("⚠️ TEST RÉUSSI (Connexion OK, mais) : Aucun tweet pertinent trouvé, ou la connexion au site a échoué après le login.")
            
    except Exception as e:
        logger.error(f"💣 TEST ÉCHOUÉ : Erreur inattendue durant l'exécution : {e}")
        
    finally:
        # 4. Fermer le navigateur
        if scraper:
            scraper.close()
        logger.info("--- Fin du Test Twitter Scraper ---")


if __name__ == "__main__":
    test_scraper()