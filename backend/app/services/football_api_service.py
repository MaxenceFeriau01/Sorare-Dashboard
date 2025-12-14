"""
Service pour interagir avec l'API-Football (API-Sports)
Documentation: https://www.api-football.com/documentation-v3
"""
import httpx
import unicodedata
from typing import Optional, List, Dict, Any
from loguru import logger
from app.config import settings


def remove_accents(text: str) -> str:
    """
    Enlève les accents d'une chaîne de caractères
    L'API-Football n'accepte pas les accents dans les recherches
    
    Args:
        text: Texte avec accents
        
    Returns:
        Texte sans accents
    """
    # Normaliser en NFD (décompose les caractères accentués)
    nfd = unicodedata.normalize('NFD', text)
    # Filtrer les marques diacritiques (accents)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    return without_accents


class FootballAPIService:
    """Service pour l'API-Football"""
    
    def __init__(self):
        self.base_url = "https://v3.football.api-sports.io"
        
        # Récupérer l'API Key depuis les settings
        self.api_key = settings.FOOTBALL_API_KEY
        
        # 🔍 LOG POUR DÉBUGGER
        if self.api_key:
            logger.info(f"🔑 API-Football: API Key chargée ({self.api_key[:10]}...{self.api_key[-4:]})")
        else:
            logger.error("❌ API-Football: API Key manquante dans settings.FOOTBALL_API_KEY !")
        
        # Vérifier que l'API Key n'est pas la valeur par défaut
        if self.api_key == "your_api_key_here" or not self.api_key or len(self.api_key) < 20:
            logger.error(f"⚠️ API Key invalide: '{self.api_key}' - Vérifie le fichier .env")
        
        self.headers = {
            "x-apisports-key": self.api_key
        }
        self.timeout = 30.0
        
        logger.info(f"✅ Service API-Football initialisé - Base URL: {self.base_url}")
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Effectue une requête GET à l'API-Football
        
        Args:
            endpoint: L'endpoint à appeler (ex: /players)
            params: Paramètres de la requête
            
        Returns:
            Dict contenant la réponse de l'API
        """
        url = f"{self.base_url}{endpoint}"
        
        # 🔍 LOG DE LA REQUÊTE
        logger.info(f"📡 Requête API-Football: {url}")
        logger.debug(f"   Params: {params}")
        logger.debug(f"   Headers: x-apisports-key={self.api_key[:10]}...{self.api_key[-4:]}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params or {}
                )
                
                # Log des rate limits
                remaining = response.headers.get('x-ratelimit-requests-remaining', 'N/A')
                limit = response.headers.get('x-ratelimit-requests-limit', 'N/A')
                logger.info(f"📊 API-Football Rate Limit: {remaining}/{limit} requêtes restantes")
                
                # Log du status code
                logger.info(f"📥 Status Code: {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                # 🔍 LOG DE LA RÉPONSE
                logger.debug(f"   Response Keys: {list(data.keys())}")
                
                # Vérifier les erreurs de l'API
                if data.get('errors'):
                    logger.error(f"❌ Erreurs API-Football: {data['errors']}")
                    return {
                        "success": False,
                        "errors": data['errors'],
                        "results": []
                    }
                
                results_count = data.get('results', 0)
                logger.success(f"✅ Requête réussie: {results_count} résultat(s)")
                
                return {
                    "success": True,
                    "results": results_count,
                    "data": data.get('response', [])
                }
                
        except httpx.HTTPError as e:
            logger.error(f"❌ Erreur HTTP lors de la requête à l'API-Football: {e}")
            logger.error(f"   URL: {url}")
            logger.error(f"   Status: {getattr(e, 'response', None)}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
        except Exception as e:
            logger.error(f"❌ Erreur inattendue avec l'API-Football: {e}")
            logger.exception("Stack trace:")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def search_players(self, query: str, page: int = 1) -> Dict:
        """
        Recherche des joueurs par nom (utilise /players/profiles)
        
        Args:
            query: Nom du joueur à rechercher (min 3 caractères)
            page: Numéro de page (défaut: 1, 250 résultats par page)
            
        Returns:
            Dict avec la liste des joueurs trouvés
        """
        if len(query) < 3:
            return {
                "success": False,
                "error": "La recherche doit contenir au moins 3 caractères",
                "results": []
            }
        
        # 🔧 Enlever les accents (l'API ne les accepte pas)
        clean_query = remove_accents(query)
        
        if clean_query != query:
            logger.info(f"🔄 Requête nettoyée: '{query}' → '{clean_query}'")
        
        params = {
            "search": clean_query,
            "page": page
        }
        
        logger.info(f"🔍 Recherche de joueurs (profiles): {clean_query} (page {page})")
        return await self._make_request("/players/profiles", params)
    
    async def get_player_by_id(self, player_id: int, season: int = 2025) -> Dict:
        """
        Récupère les détails complets d'un joueur
        
        Args:
            player_id: ID du joueur sur API-Football
            season: Saison pour les statistiques (défaut: 2025)
            
        Returns:
            Dict avec les infos du joueur
        """
        params = {
            "id": player_id,
            "season": season
        }
        
        logger.info(f"📊 Récupération joueur ID: {player_id} (saison {season})")
        return await self._make_request("/players", params)
    
    async def get_player_statistics(self, player_id: int, season: int = 2025) -> Dict:
        """
        Récupère les statistiques d'un joueur pour une saison
        ATTENTION: Nécessite aussi league ou team
        
        Args:
            player_id: ID du joueur
            season: Année de la saison (défaut: 2025)
            
        Returns:
            Dict avec les stats du joueur
        """
        params = {
            "id": player_id,
            "season": season
        }
        
        logger.info(f"📊 Récupération stats joueur ID: {player_id} (saison {season})")
        return await self._make_request("/players", params)
    
    async def search_players_with_stats(self, query: str, league: int, season: int = 2025) -> Dict:
        """
        Recherche des joueurs avec leurs statistiques
        Nécessite league + season
        
        Args:
            query: Nom du joueur (min 4 caractères)
            league: ID de la ligue (OBLIGATOIRE)
            season: Année de la saison (défaut: 2025)
            
        Returns:
            Dict avec la liste des joueurs et leurs stats
        """
        if len(query) < 4:
            return {
                "success": False,
                "error": "La recherche doit contenir au moins 4 caractères",
                "results": []
            }
        
        # 🔧 Enlever les accents
        clean_query = remove_accents(query)
        
        if clean_query != query:
            logger.info(f"🔄 Requête nettoyée: '{query}' → '{clean_query}'")
        
        params = {
            "search": clean_query,
            "league": league,
            "season": season
        }
        
        logger.info(f"🔍 Recherche joueurs avec stats: {clean_query} (ligue {league}, saison {season})")
        return await self._make_request("/players", params)
    
    async def get_team_info(self, team_id: int) -> Dict:
        """
        Récupère les informations d'une équipe
        
        Args:
            team_id: ID de l'équipe
            
        Returns:
            Dict avec les infos de l'équipe
        """
        params = {"id": team_id}
        
        logger.info(f"Récupération de l'équipe ID: {team_id}")
        return await self._make_request("/teams", params)
    
    async def search_teams(self, query: str, country: Optional[str] = None) -> Dict:
        """
        Recherche des équipes par nom
        
        Args:
            query: Nom de l'équipe (min 3 caractères)
            country: Pays de l'équipe (optionnel)
            
        Returns:
            Dict avec la liste des équipes trouvées
        """
        if len(query) < 3:
            return {
                "success": False,
                "error": "La recherche doit contenir au moins 3 caractères",
                "results": []
            }
        
        params = {"search": query}
        if country:
            params["country"] = country
        
        logger.info(f"Recherche d'équipes: {query}")
        return await self._make_request("/teams", params)
    
    async def get_upcoming_matches(self, team_id: int, next: int = 10) -> Dict:
        """
        Récupère les prochains matchs d'une équipe
        
        Args:
            team_id: ID de l'équipe
            next: Nombre de matchs à récupérer (défaut: 10)
            
        Returns:
            Dict avec la liste des matchs à venir
        """
        params = {
            "team": team_id,
            "next": next
        }
        
        logger.info(f"Récupération des {next} prochains matchs de l'équipe {team_id}")
        return await self._make_request("/fixtures", params)
    
    async def get_leagues(self, country: Optional[str] = None, season: int = 2025) -> Dict:
        """
        Récupère la liste des ligues disponibles
        
        Args:
            country: Pays (optionnel)
            season: Saison (défaut: 2025)
            
        Returns:
            Dict avec la liste des ligues
        """
        params = {"season": season}
        if country:
            params["country"] = country
        
        logger.info(f"Récupération des ligues pour {season}")
        return await self._make_request("/leagues", params)
    
    async def get_player_injuries(self, player_id: Optional[int] = None, team_id: Optional[int] = None, season: int = 2025) -> Dict:
        """
        Récupère les blessures des joueurs
        IMPORTANT: Le paramètre season est OBLIGATOIRE
        
        Args:
            player_id: ID du joueur (optionnel)
            team_id: ID de l'équipe (optionnel)
            season: Année de la saison (OBLIGATOIRE, défaut: 2025)
            
        Returns:
            Dict avec la liste des blessures
        """
        params = {"season": season}
        
        if player_id:
            params["player"] = player_id
        if team_id:
            params["team"] = team_id
        
        logger.info(f"🏥 Récupération blessures (joueur: {player_id}, équipe: {team_id}, saison: {season})")
        return await self._make_request("/injuries", params)
    
    async def check_api_status(self) -> Dict:
        """
        Vérifie le statut de l'API et la consommation
        Cette requête ne compte pas dans le quota quotidien
        
        Returns:
            Dict avec le statut de l'API et les infos du compte
        """
        logger.info("Vérification du statut de l'API-Football")
        return await self._make_request("/status")
    
    def format_player_for_database(self, api_player: Dict) -> Dict:
        """
        Formate les données d'un joueur de l'API vers le format de la base de données
        
        Args:
            api_player: Données brutes de l'API
            
        Returns:
            Dict formaté pour la création en base de données
        """
        player = api_player.get('player', {})
        statistics = api_player.get('statistics', [])
        
        # Prendre les stats de l'équipe principale (première dans la liste)
        main_stats = statistics[0] if statistics else {}
        team = main_stats.get('team', {})
        games = main_stats.get('games', {})
        goals = main_stats.get('goals', {})
        
        return {
            "api_football_id": player.get('id'),
            "first_name": player.get('firstname', ''),
            "last_name": player.get('lastname', ''),
            "display_name": player.get('name', ''),
            "club_name": team.get('name', ''),
            "position": self._normalize_position(games.get('position', '')),
            "country": player.get('nationality', ''),
            "age": player.get('age'),
            "birth_date": player.get('birth', {}).get('date'),
            "height": player.get('height'),
            "weight": player.get('weight'),
            "photo_url": player.get('photo'),
            "total_games": games.get('appearances', 0),
            "season_games": games.get('appearances', 0),
            "total_goals": goals.get('total', 0),
            "is_active": True,
            "is_injured": False
        }
    
    def _normalize_position(self, position: str) -> str:
        """
        Normalise les positions de l'API vers le format de la base
        
        Args:
            position: Position de l'API (Goalkeeper, Defender, Midfielder, Attacker)
            
        Returns:
            Position normalisée
        """
        position_map = {
            "Goalkeeper": "Goalkeeper",
            "Defender": "Defender",
            "Midfielder": "Midfielder",
            "Attacker": "Forward"
        }
        return position_map.get(position, "Midfielder")


# Instance globale du service
football_api_service = FootballAPIService()