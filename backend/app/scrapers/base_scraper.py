"""
Classe de base pour tous les scrapers
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import requests
from bs4 import BeautifulSoup
import time


class BaseScraper(ABC):
    """
    Classe abstraite de base pour tous les scrapers
    """
    
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.rate_limit_delay = 2  # Secondes entre chaque requête
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Applique un rate limiting pour ne pas surcharger les sites"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            logger.debug(f"Rate limiting: waiting {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Récupère le contenu HTML d'une page
        
        Args:
            url: L'URL à récupérer
            timeout: Timeout en secondes
            
        Returns:
            Le contenu HTML ou None en cas d'erreur
        """
        self._rate_limit()
        
        try:
            logger.debug(f"[{self.name}] Fetching: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"[{self.name}] Error fetching {url}: {e}")
            return None
    
    def _parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        Parse le HTML avec BeautifulSoup
        
        Args:
            html: Le contenu HTML
            
        Returns:
            Objet BeautifulSoup ou None
        """
        if not html:
            return None
        
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"[{self.name}] Error parsing HTML: {e}")
            return None
    
    @abstractmethod
    def search_player_news(self, player_name: str, player_club: str = None) -> List[Dict]:
        """
        Recherche des actualités sur un joueur
        
        Args:
            player_name: Nom du joueur
            player_club: Club du joueur (optionnel)
            
        Returns:
            Liste de dictionnaires contenant les infos trouvées
        """
        pass
    
    @abstractmethod
    def get_injury_updates(self) -> List[Dict]:
        """
        Récupère les dernières mises à jour de blessures
        
        Returns:
            Liste de dictionnaires avec les infos de blessures
        """
        pass
    
    def _normalize_result(
        self,
        player_name: str,
        title: str,
        content: str,
        url: str,
        date: Optional[datetime] = None,
        source: str = None,
    ) -> Dict:
        """
        Normalise un résultat dans un format standard
        
        Args:
            player_name: Nom du joueur
            title: Titre de l'article
            content: Contenu de l'article
            url: URL de l'article
            date: Date de publication
            source: Source de l'info
            
        Returns:
            Dict normalisé
        """
        return {
            "player_name": player_name,
            "title": title,
            "content": content,
            "url": url,
            "date": date or datetime.now(),
            "source": source or self.name,
            "scraper": self.name,
            "scraped_at": datetime.now(),
        }
    
    def scrape_players(self, players: List[Dict]) -> List[Dict]:
        """
        Scrape des infos pour une liste de joueurs
        
        Args:
            players: Liste de dicts avec au moins {name, club}
            
        Returns:
            Liste de résultats normalisés
        """
        results = []
        
        logger.info(f"[{self.name}] Scraping {len(players)} players...")
        
        for player in players:
            player_name = player.get("display_name") or player.get("name")
            player_club = player.get("club_name")
            
            try:
                player_results = self.search_player_news(player_name, player_club)
                results.extend(player_results)
                
                logger.debug(
                    f"[{self.name}] Found {len(player_results)} results for {player_name}"
                )
            except Exception as e:
                logger.error(
                    f"[{self.name}] Error scraping {player_name}: {e}"
                )
                continue
        
        logger.success(
            f"[{self.name}] Scraping completed: {len(results)} total results"
        )
        
        return results