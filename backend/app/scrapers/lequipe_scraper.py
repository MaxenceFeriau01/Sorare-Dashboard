"""
Scraper pour L'Équipe
Recherche d'articles sur les blessures
"""
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
from urllib.parse import quote_plus

from .base_scraper import BaseScraper


class LEquipeScraper(BaseScraper):
    """
    Scraper pour le site L'Équipe
    """
    
    def __init__(self):
        super().__init__(name="L'Équipe")
        self.base_url = "https://www.lequipe.fr"
        self.search_url = f"{self.base_url}/recherche"
    
    def search_player_news(self, player_name: str, player_club: str = None) -> List[Dict]:
        """
        Recherche des articles sur un joueur
        """
        logger.info(f"[L'Équipe] Searching for: {player_name}")
        
        results = []
        
        # Construire la query de recherche
        search_terms = f"{player_name} blessure"
        encoded_search = quote_plus(search_terms)
        
        # URL de recherche
        search_url = f"{self.search_url}?q={encoded_search}"
        
        # Récupérer la page de résultats
        html = self._fetch_page(search_url)
        if not html:
            return results
        
        soup = self._parse_html(html)
        if not soup:
            return results
        
        # Parser les résultats de recherche
        # Note: Le sélecteur peut changer, il faut l'adapter
        articles = soup.select('article.SearchResult')
        
        for article in articles[:5]:  # Limiter à 5 résultats
            try:
                # Extraire le titre
                title_elem = article.select_one('h2.SearchResult__title a')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                article_url = title_elem.get('href', '')
                
                if not article_url.startswith('http'):
                    article_url = self.base_url + article_url
                
                # Extraire le résumé
                summary_elem = article.select_one('.SearchResult__description')
                summary = summary_elem.get_text(strip=True) if summary_elem else ""
                
                # Extraire la date
                date_elem = article.select_one('time')
                date_str = date_elem.get('datetime', '') if date_elem else None
                article_date = None
                
                if date_str:
                    try:
                        article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        pass
                
                # Récupérer le contenu complet de l'article (optionnel)
                full_content = self._fetch_article_content(article_url)
                
                # Créer le résultat
                results.append(self._normalize_result(
                    player_name=player_name,
                    title=title,
                    content=full_content or summary,
                    url=article_url,
                    date=article_date,
                    source="L'Équipe",
                ))
                
            except Exception as e:
                logger.error(f"[L'Équipe] Error parsing article: {e}")
                continue
        
        logger.info(f"[L'Équipe] Found {len(results)} articles for {player_name}")
        
        return results
    
    def get_injury_updates(self) -> List[Dict]:
        """
        Récupère les derniers articles sur les blessures
        """
        logger.info("[L'Équipe] Getting injury updates")
        
        results = []
        
        # URL de la rubrique blessures (si elle existe)
        injury_url = f"{self.base_url}/Football/blessures"
        
        html = self._fetch_page(injury_url)
        if not html:
            # Sinon, faire une recherche générale
            return self._search_general_injuries()
        
        soup = self._parse_html(html)
        if not soup:
            return results
        
        # Parser les articles de blessures
        articles = soup.select('article')[:10]  # Top 10
        
        for article in articles:
            try:
                title_elem = article.select_one('h2 a, h3 a')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                
                if not url.startswith('http'):
                    url = self.base_url + url
                
                # Extraire un joueur du titre (basique)
                # TODO: Améliorer la détection du nom
                player_name = self._extract_player_name(title)
                
                if player_name:
                    content = self._fetch_article_content(url) or title
                    
                    results.append(self._normalize_result(
                        player_name=player_name,
                        title=title,
                        content=content,
                        url=url,
                        source="L'Équipe",
                    ))
            
            except Exception as e:
                logger.error(f"[L'Équipe] Error parsing injury article: {e}")
                continue
        
        return results
    
    def _fetch_article_content(self, url: str) -> Optional[str]:
        """
        Récupère le contenu complet d'un article
        """
        html = self._fetch_page(url)
        if not html:
            return None
        
        soup = self._parse_html(html)
        if not soup:
            return None
        
        # Sélecteurs possibles pour le contenu
        content_selectors = [
            'article .article__body',
            'article .Article__content',
            '.article-content',
            'article p',
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Extraire tout le texte
                paragraphs = content_elem.find_all('p')
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
                return content
        
        return None
    
    def _search_general_injuries(self) -> List[Dict]:
        """
        Recherche générale sur les blessures
        """
        search_terms = "blessure football"
        encoded_search = quote_plus(search_terms)
        search_url = f"{self.search_url}?q={encoded_search}"
        
        results = []
        
        html = self._fetch_page(search_url)
        if not html:
            return results
        
        soup = self._parse_html(html)
        if not soup:
            return results
        
        articles = soup.select('article.SearchResult')[:10]
        
        for article in articles:
            # Similaire à search_player_news
            # (code omis pour éviter la duplication)
            pass
        
        return results
    
    def _extract_player_name(self, text: str) -> Optional[str]:
        """
        Tente d'extraire un nom de joueur d'un titre
        Méthode basique, à améliorer avec NLP
        """
        # TODO: Implémenter une vraie détection de noms
        # Pour l'instant, on retourne None
        return None


# Instance globale
lequipe_scraper = LEquipeScraper()