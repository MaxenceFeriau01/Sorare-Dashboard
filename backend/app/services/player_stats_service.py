"""
Service pour gérer les statistiques des joueurs via l'API-Football
"""
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.player_statistics import PlayerStatistics  # ✅ IMPORT, pas définition
import logging

logger = logging.getLogger(__name__)

class PlayerStatsService:
    """Service pour récupérer et gérer les statistiques des joueurs"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": api_key
        }
    
    def fetch_player_statistics(
        self,
        db: Session,
        player_id: Optional[int] = None,
        team_id: Optional[int] = None,
        league_id: Optional[int] = None,
        season: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Récupère les statistiques des joueurs depuis l'API
        
        Args:
            db: Session de base de données
            player_id: ID du joueur
            team_id: ID de l'équipe
            league_id: ID de la ligue
            season: Saison (format YYYY)
            search: Nom du joueur à rechercher (minimum 4 caractères)
            page: Numéro de page pour la pagination
            force_refresh: Force le refresh depuis l'API
            
        Returns:
            Dict contenant les statistiques et métadonnées
        """
        
        # Validation des paramètres
        if search and len(search) < 4:
            raise ValueError("Le nom du joueur doit contenir au moins 4 caractères")
        
        if season and (not league_id and not team_id and not player_id):
            raise ValueError("La saison nécessite un ID de ligue, d'équipe ou de joueur")
        
        if search and not (league_id or team_id):
            raise ValueError("La recherche nécessite un ID de ligue ou d'équipe")
        
        # Construction des paramètres de requête
        params = {"page": page}
        if player_id:
            params["id"] = player_id
        if team_id:
            params["team"] = team_id
        if league_id:
            params["league"] = league_id
        if season:
            params["season"] = season
        if search:
            params["search"] = search
        
        # Vérifier si on a déjà les données en cache (sauf si force_refresh)
        if not force_refresh and player_id and season:
            cached_stats = self._get_cached_stats(db, player_id, season, team_id, league_id)
            if cached_stats:
                logger.info(f"Utilisation du cache pour le joueur {player_id}")
                return {
                    "cached": True,
                    "results": len(cached_stats),
                    "response": [stat.to_dict() for stat in cached_stats]
                }
        
        # Appel à l'API
        try:
            logger.info(f"Appel API pour les statistiques: {params}")
            response = requests.get(
                f"{self.base_url}/players",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("errors"):
                logger.error(f"Erreur API: {data['errors']}")
                raise Exception(f"Erreur API: {data['errors']}")
            
            # Sauvegarde des statistiques en base de données
            if data.get("response"):
                self._save_statistics(db, data["response"])
            
            return {
                "cached": False,
                "results": data.get("results", 0),
                "paging": data.get("paging", {}),
                "response": data.get("response", [])
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'appel API: {e}")
            raise Exception(f"Erreur lors de la récupération des statistiques: {e}")
    
    def _get_cached_stats(
        self,
        db: Session,
        player_id: int,
        season: int,
        team_id: Optional[int] = None,
        league_id: Optional[int] = None
    ) -> List[PlayerStatistics]:
        """Récupère les statistiques en cache depuis la base de données"""
        query = db.query(PlayerStatistics).filter(
            PlayerStatistics.player_id == player_id,
            PlayerStatistics.season == season
        )
        
        if team_id:
            query = query.filter(PlayerStatistics.team_id == team_id)
        if league_id:
            query = query.filter(PlayerStatistics.league_id == league_id)
        
        # Vérifier que les données ne sont pas trop anciennes (moins de 7 jours)
        from datetime import timedelta
        week_ago = datetime.utcnow().date() - timedelta(days=7)
        query = query.filter(PlayerStatistics.last_updated >= week_ago)
        
        return query.all()
    
    def _save_statistics(self, db: Session, players_data: List[Dict]) -> None:
        """Sauvegarde les statistiques en base de données"""
        for player_data in players_data:
            player_info = player_data.get("player", {})
            
            # Pour chaque statistique (un joueur peut avoir plusieurs stats s'il a joué dans plusieurs équipes)
            for stat in player_data.get("statistics", []):
                team_info = stat.get("team", {})
                league_info = stat.get("league", {})
                
                # Vérifier si la statistique existe déjà
                existing_stat = db.query(PlayerStatistics).filter(
                    PlayerStatistics.player_id == player_info.get("id"),
                    PlayerStatistics.team_id == team_info.get("id"),
                    PlayerStatistics.league_id == league_info.get("id"),
                    PlayerStatistics.season == league_info.get("season")
                ).first()
                
                if existing_stat:
                    # Mise à jour
                    self._update_player_stat(existing_stat, player_info, stat)
                    logger.info(f"Mise à jour des stats pour {player_info.get('name')}")
                else:
                    # Création
                    new_stat = self._create_player_stat(player_info, stat)
                    db.add(new_stat)
                    logger.info(f"Création des stats pour {player_info.get('name')}")
        
        db.commit()
    
    def _create_player_stat(self, player_info: Dict, stat: Dict) -> PlayerStatistics:
        """Crée une nouvelle entrée de statistiques"""
        team_info = stat.get("team", {})
        league_info = stat.get("league", {})
        games = stat.get("games", {})
        substitutes = stat.get("substitutes", {})
        shots = stat.get("shots", {})
        goals = stat.get("goals", {})
        passes = stat.get("passes", {})
        tackles = stat.get("tackles", {})
        duels = stat.get("duels", {})
        dribbles = stat.get("dribbles", {})
        fouls = stat.get("fouls", {})
        cards = stat.get("cards", {})
        penalty = stat.get("penalty", {})
        
        birth_info = player_info.get("birth", {})
        birth_date = None
        if birth_info.get("date"):
            try:
                birth_date = datetime.strptime(birth_info.get("date"), "%Y-%m-%d").date()
            except:
                pass
        
        return PlayerStatistics(
            # Informations du joueur
            player_id=player_info.get("id"),
            player_name=player_info.get("name"),
            player_firstname=player_info.get("firstname"),
            player_lastname=player_info.get("lastname"),
            player_age=player_info.get("age"),
            player_birth_date=birth_date,
            player_birth_place=birth_info.get("place"),
            player_birth_country=birth_info.get("country"),
            player_nationality=player_info.get("nationality"),
            player_height=player_info.get("height"),
            player_weight=player_info.get("weight"),
            player_injured=player_info.get("injured", False),
            player_photo=player_info.get("photo"),
            
            # Informations de l'équipe
            team_id=team_info.get("id"),
            team_name=team_info.get("name"),
            team_logo=team_info.get("logo"),
            
            # Informations de la ligue
            league_id=league_info.get("id"),
            league_name=league_info.get("name"),
            league_country=league_info.get("country"),
            league_logo=league_info.get("logo"),
            league_flag=league_info.get("flag"),
            season=league_info.get("season"),
            
            # Statistiques
            games_appearences=games.get("appearences", 0),
            games_lineups=games.get("lineups", 0),
            games_minutes=games.get("minutes", 0),
            games_number=games.get("number"),
            games_position=games.get("position"),
            games_rating=float(games.get("rating")) if games.get("rating") else None,
            games_captain=games.get("captain", False),
            
            substitutes_in=substitutes.get("in", 0),
            substitutes_out=substitutes.get("out", 0),
            substitutes_bench=substitutes.get("bench", 0),
            
            shots_total=shots.get("total", 0),
            shots_on=shots.get("on", 0),
            
            goals_total=goals.get("total", 0),
            goals_conceded=goals.get("conceded", 0),
            goals_assists=goals.get("assists", 0),
            goals_saves=goals.get("saves", 0),
            
            passes_total=passes.get("total", 0),
            passes_key=passes.get("key", 0),
            passes_accuracy=passes.get("accuracy", 0),
            
            tackles_total=tackles.get("total", 0),
            tackles_blocks=tackles.get("blocks", 0),
            tackles_interceptions=tackles.get("interceptions", 0),
            
            duels_total=duels.get("total", 0),
            duels_won=duels.get("won", 0),
            
            dribbles_attempts=dribbles.get("attempts", 0),
            dribbles_success=dribbles.get("success", 0),
            dribbles_past=dribbles.get("past", 0),
            
            fouls_drawn=fouls.get("drawn", 0),
            fouls_committed=fouls.get("committed", 0),
            
            cards_yellow=cards.get("yellow", 0),
            cards_yellowred=cards.get("yellowred", 0),
            cards_red=cards.get("red", 0),
            
            penalty_won=penalty.get("won", 0),
            penalty_committed=penalty.get("commited", 0),  # Note: typo dans l'API
            penalty_scored=penalty.get("scored", 0),
            penalty_missed=penalty.get("missed", 0),
            penalty_saved=penalty.get("saved", 0),
            
            last_updated=datetime.utcnow().date()
        )
    
    def _update_player_stat(self, existing_stat: PlayerStatistics, player_info: Dict, stat: Dict) -> None:
        """Met à jour une entrée de statistiques existante"""
        games = stat.get("games", {})
        substitutes = stat.get("substitutes", {})
        shots = stat.get("shots", {})
        goals = stat.get("goals", {})
        passes = stat.get("passes", {})
        tackles = stat.get("tackles", {})
        duels = stat.get("duels", {})
        dribbles = stat.get("dribbles", {})
        fouls = stat.get("fouls", {})
        cards = stat.get("cards", {})
        penalty = stat.get("penalty", {})
        
        # Mise à jour des statistiques
        existing_stat.games_appearences = games.get("appearences", 0)
        existing_stat.games_lineups = games.get("lineups", 0)
        existing_stat.games_minutes = games.get("minutes", 0)
        existing_stat.games_rating = float(games.get("rating")) if games.get("rating") else None
        
        existing_stat.goals_total = goals.get("total", 0)
        existing_stat.goals_assists = goals.get("assists", 0)
        existing_stat.shots_total = shots.get("total", 0)
        existing_stat.passes_accuracy = passes.get("accuracy", 0)
        existing_stat.cards_yellow = cards.get("yellow", 0)
        existing_stat.cards_red = cards.get("red", 0)
        
        existing_stat.last_updated = datetime.utcnow().date()
    
    def get_player_stats_by_team(
        self,
        db: Session,
        team_id: int,
        season: int,
        league_id: Optional[int] = None
    ) -> List[PlayerStatistics]:
        """Récupère toutes les statistiques des joueurs d'une équipe"""
        query = db.query(PlayerStatistics).filter(
            PlayerStatistics.team_id == team_id,
            PlayerStatistics.season == season
        )
        
        if league_id:
            query = query.filter(PlayerStatistics.league_id == league_id)
        
        return query.order_by(PlayerStatistics.games_appearences.desc()).all()
    
    def search_players(
        self,
        db: Session,
        search_term: str,
        league_id: Optional[int] = None,
        season: Optional[int] = None
    ) -> List[PlayerStatistics]:
        """Recherche des joueurs par nom"""
        query = db.query(PlayerStatistics).filter(
            PlayerStatistics.player_name.ilike(f"%{search_term}%")
        )
        
        if league_id:
            query = query.filter(PlayerStatistics.league_id == league_id)
        if season:
            query = query.filter(PlayerStatistics.season == season)
        
        return query.limit(50).all()