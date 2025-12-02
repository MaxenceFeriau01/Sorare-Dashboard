"""
Manager principal pour orchestrer tous les scrapers
"""
from typing import List, Dict
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.player import Player
from app.models.injury import Injury
from app.analysis.confidence_scorer import injury_analyzer
from .lequipe_scraper import lequipe_scraper
from .twitter_scraper import TwitterSeleniumScraper
from app.config_with_twitter import settings


class ScrapingManager:
    """Manager qui orchestre tous les scrapers"""
    
    def __init__(self):
        self.scrapers = [
            lequipe_scraper,
            # Twitter sera initialisé avec credentials
        ]
    
    def scrape_all_players(self, db: Session = None) -> Dict:
        """Scrape les infos de tous les joueurs"""
        if db is None:
            db = SessionLocal()
        
        logger.info("=" * 60)
        logger.info("🕷️  DÉBUT DU SCRAPING")
        logger.info("=" * 60)
        
        players = db.query(Player).filter(Player.is_active == True).all()
        logger.info(f"📊 {len(players)} joueurs à scraper")
        
        players_data = [
            {
                "id": p.id,
                "name": p.display_name,
                "display_name": p.display_name,
                "club_name": p.club_name,
            }
            for p in players
        ]
        
        all_results = []
        
        # Twitter scraper (si configuré)
        if settings.TWITTER_EMAIL and settings.TWITTER_PASSWORD:
            try:
                logger.info(f"\n🔍 Scraping with Twitter...")
                twitter_scraper = TwitterSeleniumScraper(
                    twitter_email=settings.TWITTER_EMAIL,
                    twitter_password=settings.TWITTER_PASSWORD,
                    twitter_username=settings.TWITTER_USERNAME,
                )
                results = twitter_scraper.scrape_players(players_data)
                all_results.extend(results)
                logger.success(f"✅ Twitter: {len(results)} résultats")
                twitter_scraper.close()
            except Exception as e:
                logger.error(f"❌ Twitter failed: {e}")
        
        # Autres scrapers
        for scraper in self.scrapers:
            logger.info(f"\n🔍 Scraping with {scraper.name}...")
            try:
                results = scraper.scrape_players(players_data)
                all_results.extend(results)
                logger.success(f"✅ {scraper.name}: {len(results)} résultats")
            except Exception as e:
                logger.error(f"❌ {scraper.name} failed: {e}")
        
        logger.info(f"\n📊 Total: {len(all_results)} résultats")
        
        # Analyser
        logger.info("\n🧠 Analyse des résultats...")
        injuries_detected = self._analyze_results(all_results, db)
        
        # Sauvegarder
        logger.info("\n💾 Sauvegarde des blessures...")
        added, updated = self._save_injuries(injuries_detected, db)
        
        stats = {
            "total_results": len(all_results),
            "injuries_detected": len(injuries_detected),
            "injuries_added": added,
            "injuries_updated": updated,
            "scraped_at": datetime.now().isoformat(),
        }
        
        logger.info("\n" + "=" * 60)
        logger.success("✅ SCRAPING TERMINÉ")
        logger.info("=" * 60)
        logger.info(f"📊 Statistiques:")
        logger.info(f"   • Résultats scraped: {stats['total_results']}")
        logger.info(f"   • Blessures détectées: {stats['injuries_detected']}")
        logger.info(f"   • Blessures ajoutées: {stats['injuries_added']}")
        logger.info(f"   • Blessures mises à jour: {stats['injuries_updated']}")
        logger.info("=" * 60)
        
        if db:
            db.close()
        
        return stats
    
    def _analyze_results(self, results: List[Dict], db: Session) -> List[Dict]:
        """Analyse les résultats"""
        injuries_detected = []
        
        for result in results:
            player_name = result["player_name"]
            content = result["content"]
            source = result["source"]
            url = result["url"]
            
            analysis = injury_analyzer.analyze_text(
                text=content,
                player_name=player_name,
                source=source,
                source_type="website",
            )
            
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
        """Sauvegarde les blessures"""
        added = 0
        updated = 0
        
        for injury_data in injuries:
            player_id = injury_data["player_id"]
            
            existing_injury = db.query(Injury).filter(
                Injury.player_id == player_id,
                Injury.is_active == True,
            ).first()
            
            if existing_injury:
                if injury_data["confidence"] > 0.7:
                    existing_injury.injury_description = injury_data["injury_description"]
                    existing_injury.severity = injury_data["severity"]
                    existing_injury.source = injury_data["source"]
                    updated += 1
                    logger.info(f"   ↻ Mise à jour: {injury_data['player_name']}")
            else:
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
                logger.success(f"   ✓ Ajoutée: {injury_data['player_name']}")
        
        try:
            db.commit()
        except Exception as e:
            logger.error(f"Error: {e}")
            db.rollback()
        
        return added, updated


scraping_manager = ScrapingManager()