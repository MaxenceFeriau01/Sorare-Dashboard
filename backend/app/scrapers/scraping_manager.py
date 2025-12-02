"""
Manager principal pour orchestrer tous les scrapers.
Ce fichier orchestre la recherche pour tous les joueurs sur différentes sources,
gère l'analyse des risques de blessure et la sauvegarde en base de données.
"""
from typing import List, Dict
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

# Importations locales
from app.database import SessionLocal
from app.models.player import Player
from app.models.injury import Injury
from app.analysis.confidence_scorer import injury_analyzer
# Scrapers
from .lequipe_scraper import lequipe_scraper
from .twitter_scraper import TwitterSeleniumScraper
# Configuration
from app.config_with_twitter import settings


class ScrapingManager:
    """Manager qui orchestre tous les scrapers et maintient une session Twitter persistante."""
    
    def __init__(self):
        self.scrapers = [
            lequipe_scraper,
        ]
        self.twitter_scraper: Optional[TwitterSeleniumScraper] = None 
    
    # --- GESTION DE LA SESSION TWITTER ---
        
    def initialize_twitter_scraper(self):
        """Initialise le scraper Twitter et ouvre le navigateur une seule fois."""
        if self.twitter_scraper is None and settings.TWITTER_EMAIL and settings.TWITTER_PASSWORD:
            logger.info("🔧 Tentative d'initialisation du Twitter Scraper...")
            try:
                self.twitter_scraper = TwitterSeleniumScraper(
                    twitter_email=settings.TWITTER_EMAIL,
                    twitter_password=settings.TWITTER_PASSWORD,
                    twitter_username=settings.TWITTER_USERNAME,
                )
                # Le login sera effectué lors du premier appel à search_player_news
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'initialisation du Twitter Scraper : {e}")
                self.twitter_scraper = None
                
    def close_twitter_scraper(self):
        """Ferme explicitement le scraper Twitter, à appeler à la fin du programme principal."""
        if self.twitter_scraper:
            logger.info("🛑 Fermeture manuelle du Twitter Scraper.")
            self.twitter_scraper.close()
            self.twitter_scraper = None
            
    # --- PROCESSUS DE SCRAPING PRINCIPAL ---

    def scrape_all_players(self, db: Session = None) -> Dict:
        """
        Scrape les infos de tous les joueurs actifs en utilisant tous les scrapers disponibles.
        """
        if db is None:
            db = SessionLocal()
        
        logger.info("=" * 60)
        logger.info("🕷️  DÉBUT DU SCRAPING GLOBAL")
        logger.info("=" * 60)
        
        # 1. Préparation des données joueurs
        players = db.query(Player).filter(Player.is_active == True).all()
        logger.info(f"📊 {len(players)} joueurs à scraper")
        
        players_data = [
            {"id": p.id, "name": p.display_name, "display_name": p.display_name, "club_name": p.club_name}
            for p in players
        ]
        
        all_results = []
        
        # 2. Scraping Twitter (Session persistante)
        if self.twitter_scraper:
            try:
                logger.info(f"\n🔍 Scraping avec Twitter (Session persistante)...")
                twitter_results = []
                
                for player in players_data:
                    player_name = player['display_name']
                    logger.info(f"   -> Recherche pour {player_name}...")
                    # search_player_news gère l'ouverture et la connexion si besoin
                    player_results = self.twitter_scraper.search_player_news(player_name)
                    twitter_results.extend(player_results)
                
                all_results.extend(twitter_results)
                logger.success(f"✅ Twitter: {len(twitter_results)} résultats consolidés.")
                
                # 🛑 ATTENTION : PAS d'appel à self.twitter_scraper.close() ici !
                # Le scraper reste ouvert pour la prochaine exécution de la fonction si nécessaire.
                
            except Exception as e:
                logger.error(f"❌ Twitter a échoué pendant le scraping : {e}")
                # En cas d'échec catastrophique, on ferme
                self.close_twitter_scraper() 
        
        # 3. Autres scrapers
        for scraper in self.scrapers:
            logger.info(f"\n🔍 Scraping avec {scraper.name}...")
            try:
                # On suppose que les autres scrapers n'ont pas de problème de session
                results = scraper.scrape_players(players_data)
                all_results.extend(results)
                logger.success(f"✅ {scraper.name}: {len(results)} résultats.")
            except Exception as e:
                logger.error(f"❌ {scraper.name} a échoué : {e}")
        
        logger.info(f"\n📊 Total: {len(all_results)} résultats bruts collectés.")
        
        # 4. Analyse et Sauvegarde
        logger.info("\n🧠 Analyse des résultats...")
        injuries_detected = self._analyze_results(all_results, db)
        
        logger.info("\n💾 Sauvegarde et mise à jour des blessures...")
        added, updated = self._save_injuries(injuries_detected, db)
        
        # 5. Statistiques et Fin
        stats = {
            "total_results": len(all_results),
            "injuries_detected": len(injuries_detected),
            "injuries_added": added,
            "injuries_updated": updated,
            "scraped_at": datetime.now().isoformat(),
        }
        
        logger.info("\n" + "=" * 60)
        logger.success("✅ SCRAPING GLOBAL TERMINÉ")
        logger.info("=" * 60)
        logger.info(f"📊 Statistiques:")
        logger.info(f"   • Résultats scraped: {stats['total_results']}")
        logger.info(f"   • Blessures détectées: {stats['injuries_detected']}")
        logger.info(f"   • Blessures ajoutées: {stats['injuries_added']}")
        logger.info(f"   • Blessures mises à jour: {stats['injuries_updated']}")
        logger.info("=" * 60)
        
        if db:
            db.close()
        
        return stats
    
    # --- FONCTIONS D'ANALYSE ET DE SAUVEGARDE (Inchangées) ---
    
    def _analyze_results(self, results: List[Dict], db: Session) -> List[Dict]:
        """Analyse les résultats et attribue un score de confiance."""
        injuries_detected = []
        
        for result in results:
            player_name = result["player_name"]
            content = result["content"]
            source = result["source"]
            url = result["url"]
            
            # Utilise l'analyseur de confiance
            analysis = injury_analyzer.analyze_text(
                text=content,
                player_name=player_name,
                source=source,
                source_type="social", # Type mis à jour pour Twitter
            )
            
            # Seules les blessures avec une confiance suffisante sont conservées
            if analysis["is_injury"] and analysis["confidence"] >= 0.5:
                player = db.query(Player).filter(
                    Player.display_name.ilike(f"%{player_name}%")
                ).first()
                
                if player:
                    injuries_detected.append({
                        "player_id": player.id,
                        "player_name": player_name,
                        "injury_type": analysis["injury_type"],
                        "injury_description": result["title"],
                        "severity": analysis["severity"],
                        "confidence": analysis["confidence"],
                        "source": source,
                        "source_url": url,
                    })
                    
                    logger.success(
                        f"🚨 Blessure détectée: {player_name} "
                        f"(confiance: {analysis['confidence']*100:.0f}%)"
                    )
        
        return injuries_detected
    
    def _save_injuries(self, injuries: List[Dict], db: Session) -> tuple:
        """Sauvegarde les blessures en base de données ou met à jour les existantes."""
        added = 0
        updated = 0
        
        for injury_data in injuries:
            player_id = injury_data["player_id"]
            
            existing_injury = db.query(Injury).filter(
                Injury.player_id == player_id,
                Injury.is_active == True,
            ).first()
            
            if existing_injury:
                # Mise à jour si la confiance est élevée
                if injury_data["confidence"] > 0.7:
                    existing_injury.injury_description = injury_data["injury_description"]
                    existing_injury.severity = injury_data["severity"]
                    existing_injury.source = injury_data["source"]
                    updated += 1
                    logger.info(f"   ↻ Mise à jour: {injury_data['player_name']}")
            else:
                # Nouvelle blessure
                new_injury = Injury(
                    player_id=player_id,
                    injury_type=injury_data["injury_type"],
                    injury_description=injury_data["injury_description"],
                    severity=injury_data["severity"],
                    injury_date=datetime.now(),
                    is_active=True,
                    source=injury_data["source"],
                    source_url=injury_data["source_url"],
                )
                
                player = db.query(Player).filter(Player.id == player_id).first()
                if player:
                    player.is_injured = True
                    player.injury_status = injury_data["injury_description"]
                
                db.add(new_injury)
                added += 1
                logger.success(f"   ✓ Ajoutée: {injury_data['player_name']}")
        
        try:
            db.commit()
        except Exception as e:
            logger.error(f"Erreur lors du commit en base de données : {e}")
            db.rollback()
        
        return added, updated


# Instance globale du manager
scraping_manager = ScrapingManager()