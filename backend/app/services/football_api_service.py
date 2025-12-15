"""
Service pour interagir avec l'API-Football
✅ VERSION OPTIMISÉE AVEC VALIDATION PAR MATCHS RÉCENTS
"""
import httpx
from typing import Dict, List, Optional
from loguru import logger
from datetime import datetime, timedelta

class FootballAPIService:
    """Service d'intégration avec API-Football v3"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": api_key
        }
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Effectue une requête vers l'API-Football
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"📡 API-Football: {endpoint} {params or ''}")
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('errors'):
                    logger.error(f"❌ API Error: {data['errors']}")
                    return {'success': False, 'error': data['errors']}
                
                logger.info(f"✅ Résultats: {data.get('results', 0)}")
                return {
                    'success': True,
                    'results': data.get('results', 0),
                    'data': data.get('response', [])
                }
                
        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP Error: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ============================================
    # 🏥 BLESSURES - VALIDATION PAR MATCHS RÉCENTS
    # ============================================
    
    def _check_player_in_lineups(self, lineups: List[Dict], player_id: int, player_name: str) -> Optional[str]:
        """
        Vérifie si un joueur est présent dans les compositions d'un match
        
        Returns:
            - "starter" si dans le XI de départ
            - "substitute" si sur le banc
            - None si absent
        """
        for team_lineup in lineups:
            # Vérifier dans le XI de départ
            start_xi = team_lineup.get('startXI', [])
            for player_data in start_xi:
                player_info = player_data.get('player', {})
                if player_info.get('id') == player_id or player_info.get('name', '').lower() == player_name.lower():
                    return "starter"
            
            # Vérifier dans les remplaçants
            substitutes = team_lineup.get('substitutes', [])
            for player_data in substitutes:
                player_info = player_data.get('player', {})
                if player_info.get('id') == player_id or player_info.get('name', '').lower() == player_name.lower():
                    return "substitute"
        
        return None
    
    async def validate_injury_with_recent_matches(
        self,
        player_id: int,
        player_name: str,
        team_id: int,
        suspected_injury: bool
    ) -> Dict:
        """
        ✅ Valide une blessure en vérifiant si le joueur a joué récemment
        
        Logique:
        - Si le joueur a joué dans les 2 derniers matchs → Pas blessé
        - Si le joueur n'a pas joué depuis 2+ matchs → Blessure confirmée
        """
        logger.info(f"🔍 Validation blessure pour {player_name} (ID: {player_id})")
        
        try:
            # 1. Récupérer les 3 derniers matchs de l'équipe
            last_matches_result = await self._make_request("/fixtures", {
                "team": team_id,
                "last": 3,
                "status": "FT"  # Seulement les matchs terminés
            })
            
            if not last_matches_result.get('success'):
                logger.warning(f"⚠️ Impossible de récupérer les derniers matchs")
                return {
                    "is_actually_injured": suspected_injury,
                    "validation_method": "no_validation_possible",
                    "last_played": None,
                    "matches_checked": 0
                }
            
            matches = last_matches_result.get('data', [])
            if not matches:
                logger.warning(f"⚠️ Aucun match récent trouvé")
                return {
                    "is_actually_injured": suspected_injury,
                    "validation_method": "no_recent_matches",
                    "last_played": None,
                    "matches_checked": 0
                }
            
            logger.info(f"📊 {len(matches)} match(s) récent(s) trouvé(s)")
            
            # 2. Vérifier si le joueur a joué
            played_in_matches = []
            
            for match in matches[:3]:
                fixture_id = match.get('fixture', {}).get('id')
                fixture_date = match.get('fixture', {}).get('date')
                
                if not fixture_id:
                    continue
                
                # Récupérer les compositions
                lineups_result = await self._make_request("/fixtures/lineups", {
                    "fixture": fixture_id
                })
                
                if not lineups_result.get('success'):
                    logger.warning(f"⚠️ Compositions non disponibles pour le match {fixture_id}")
                    continue
                
                lineups = lineups_result.get('data', [])
                player_played = self._check_player_in_lineups(lineups, player_id, player_name)
                
                if player_played:
                    played_in_matches.append({
                        "fixture_id": fixture_id,
                        "date": fixture_date,
                        "role": player_played
                    })
                    logger.info(f"✅ {player_name} a joué le {fixture_date} ({player_played})")
            
            # 3. Analyser les résultats
            matches_checked = len(matches)
            
            if len(played_in_matches) >= 2:
                # Joué 2-3 fois → PAS BLESSÉ
                logger.success(f"✅ {player_name} a joué {len(played_in_matches)} fois récemment → DISPONIBLE")
                return {
                    "is_actually_injured": False,
                    "validation_method": "played_recently",
                    "last_played": played_in_matches[0]["date"],
                    "matches_checked": matches_checked,
                    "matches_played": len(played_in_matches)
                }
            
            elif len(played_in_matches) == 1:
                # Joué 1 fois → INCERTAIN
                logger.warning(f"⚠️ {player_name} n'a joué qu'1 fois sur {matches_checked} → INCERTAIN")
                return {
                    "is_actually_injured": suspected_injury,
                    "validation_method": "uncertain_limited_playtime",
                    "last_played": played_in_matches[0]["date"],
                    "matches_checked": matches_checked,
                    "matches_played": 1
                }
            
            else:
                # Jamais joué → BLESSURE CONFIRMÉE
                logger.error(f"❌ {player_name} absent des {matches_checked} derniers matchs → BLESSÉ")
                return {
                    "is_actually_injured": True,
                    "validation_method": "not_played_recently",
                    "last_played": None,
                    "matches_checked": matches_checked,
                    "matches_played": 0
                }
        
        except Exception as e:
            logger.error(f"❌ Erreur validation: {e}")
            return {
                "is_actually_injured": suspected_injury,
                "validation_method": "validation_error",
                "last_played": None,
                "matches_checked": 0,
                "error": str(e)
            }
    
    async def get_player_injuries_smart(
        self,
        player_id: Optional[int] = None,
        team_id: Optional[int] = None,
        season: int = 2025
    ) -> Dict:
        """
        ✅ VERSION OPTIMISÉE - Récupère les blessures ET valide avec matchs récents
        
        OPTIMISATIONS:
        - Déduplication des joueurs blessés
        - Validation une seule fois par joueur
        - Logs clairs
        """
        logger.info(f"🏥 Récupération INTELLIGENTE des blessures (saison {season})")
        
        # 1. Récupérer les blessures brutes
        raw_result = await self.get_player_injuries(player_id, team_id, season)
        
        if not raw_result.get('success'):
            return raw_result
        
        raw_injuries = raw_result.get('data', [])
        logger.info(f"📋 {len(raw_injuries)} absence(s) détectée(s) par l'API")
        
        # 2. Filtrer les vraies blessures médicales
        medical_injuries = []
        
        for injury_data in raw_injuries:
            player_info = injury_data.get('player', {})
            injury_type = player_info.get('type', '').lower()
            injury_reason = player_info.get('reason', '').lower()
            
            # Filtrer les non-blessures
            non_medical_keywords = [
                'suspension', 'suspended', 'red card', 'yellow cards',
                'rest', 'rested', 'rotation', 'tactical',
                'not in squad', 'coach decision', 'personal reasons',
                'disciplinary', 'ban', 'banned'
            ]
            
            is_non_medical = any(keyword in injury_type or keyword in injury_reason 
                                for keyword in non_medical_keywords)
            
            if not is_non_medical:
                medical_injuries.append(injury_data)
        
        logger.info(f"🏥 {len(medical_injuries)} blessure(s) médicale(s) après filtrage")
        
        # ✅ 3. DÉDUPLICATION - Grouper par joueur
        injuries_by_player = {}
        for injury_data in medical_injuries:
            player_info = injury_data.get('player', {})
            api_player_id = player_info.get('id')
            
            if api_player_id not in injuries_by_player:
                injuries_by_player[api_player_id] = {
                    'player_info': player_info,
                    'injury_data': injury_data,
                    'count': 1
                }
            else:
                injuries_by_player[api_player_id]['count'] += 1
        
        logger.info(f"👥 {len(injuries_by_player)} joueur(s) unique(s) blessé(s)")
        
        # 4. VALIDATION avec les matchs récents (UNE SEULE FOIS PAR JOUEUR)
        validated_injuries = []
        
        for api_player_id, player_data in injuries_by_player.items():
            player_info = player_data['player_info']
            injury_data = player_data['injury_data']
            player_name = player_info.get('name')
            duplicate_count = player_data['count']
            
            if duplicate_count > 1:
                logger.info(f"ℹ️ {player_name}: {duplicate_count} entrées (on ne vérifie qu'une fois)")
            
            # Déterminer le team_id
            fixture_team = injury_data.get('team', {})
            validation_team_id = team_id or fixture_team.get('id')
            
            if not validation_team_id:
                logger.warning(f"⚠️ Pas de team_id pour {player_name}, on garde la blessure")
                validated_injuries.append({
                    **injury_data,
                    'validation_status': 'no_team_id',
                    'is_validated': False
                })
                continue
            
            # ✅ VALIDATION PAR MATCHS (une seule fois)
            validation_result = await self.validate_injury_with_recent_matches(
                player_id=api_player_id,
                player_name=player_name,
                team_id=validation_team_id,
                suspected_injury=True
            )
            
            # Décision finale
            is_actually_injured = validation_result.get('is_actually_injured')
            validation_method = validation_result.get('validation_method')
            
            if is_actually_injured:
                # Blessure confirmée
                validated_injuries.append({
                    **injury_data,
                    'validation_status': validation_method,
                    'is_validated': True,
                    'last_played': validation_result.get('last_played'),
                    'matches_checked': validation_result.get('matches_checked')
                })
                logger.success(f"✅ BLESSURE CONFIRMÉE: {player_name} ({validation_method})")
            else:
                # Blessure invalidée (a joué récemment)
                logger.warning(f"❌ BLESSURE INVALIDÉE: {player_name} a joué récemment")
                # On ne l'ajoute PAS à validated_injuries
        
        logger.success(f"🎯 RÉSULTAT FINAL: {len(validated_injuries)} blessure(s) validée(s)")
        
        return {
            'success': True,
            'results': len(validated_injuries),
            'data': validated_injuries,
            'raw_count': len(raw_injuries),
            'medical_count': len(medical_injuries),
            'unique_players': len(injuries_by_player),
            'validated_count': len(validated_injuries)
        }
    
    async def get_player_injuries(
        self, 
        player_id: Optional[int] = None, 
        team_id: Optional[int] = None, 
        season: int = 2025
    ) -> Dict:
        """Méthode basique pour récupérer les blessures"""
        params = {"season": season}
        
        if player_id:
            params["player"] = player_id
        if team_id:
            params["team"] = team_id
        
        logger.info(f"🏥 Récupération blessures brutes")
        return await self._make_request("/injuries", params)
    
    # ============================================
    # 🔮 PRÉDICTIONS
    # ============================================
    
    async def get_fixture_prediction(self, fixture_id: int) -> dict:
        """Récupère les prédictions pour un match"""
        logger.info(f"🔮 Prédictions pour le match {fixture_id}")
        
        params = {'fixture': fixture_id}
        result = await self._make_request('/predictions', params)
        
        if result.get('success') and result.get('data'):
            prediction_data = result['data'][0]
            predictions = prediction_data.get('predictions', {})
            teams = prediction_data.get('teams', {})
            comparison = prediction_data.get('comparison', {})
            
            return {
                'success': True,
                'fixture_id': fixture_id,
                'predictions': {
                    'winner': predictions.get('winner', {}),
                    'win_or_draw': predictions.get('win_or_draw'),
                    'under_over': predictions.get('under_over'),
                    'goals_home': predictions.get('goals', {}).get('home'),
                    'goals_away': predictions.get('goals', {}).get('away'),
                    'advice': predictions.get('advice'),
                    'percent': predictions.get('percent', {})
                },
                'teams': {
                    'home': teams.get('home', {}),
                    'away': teams.get('away', {})
                },
                'comparison': comparison,
                'league': prediction_data.get('league', {})
            }
        
        return {'success': False, 'data': None}
    
    def _calculate_playability_score(self, prediction: dict, team_id: int) -> dict:
        """Calcule le score de jouabilité (0-10)"""
        score = 5.0
        reasons = []
        
        predictions = prediction.get('predictions') or {}
        teams = prediction.get('teams') or {}
        
        home_team = teams.get('home') or {}
        away_team = teams.get('away') or {}
        is_home = home_team.get('id') == team_id
        team_type = 'home' if is_home else 'away'
        
        # Vérifier que winner a un ID
        winner = predictions.get('winner') or {}
        winner_id = winner.get('id') if isinstance(winner, dict) else None
        winner_comment = winner.get('comment', '') if isinstance(winner, dict) else ''
        
        # 1. Chance de victoire
        if winner_id == team_id:
            try:
                if '%' in str(winner_comment):
                    win_chance = float(str(winner_comment).replace('%', ''))
                    if win_chance >= 70:
                        score += 2.5
                        reasons.append(f"✅ Très forte chance de victoire ({win_chance}%)")
                    elif win_chance >= 50:
                        score += 1.5
                        reasons.append(f"👍 Bonne chance de victoire ({win_chance}%)")
                    else:
                        score += 0.5
                        reasons.append(f"⚠️ Chance modérée ({win_chance}%)")
                else:
                    score += 1.5
                    reasons.append("✅ Équipe favorite")
            except (ValueError, TypeError, AttributeError):
                score += 1.0
                reasons.append("✅ Équipe favorite")
                
        elif winner_id and winner_id != team_id:
            score -= 1
            reasons.append("⚠️ Pas favorite")
        else:
            reasons.append("ℹ️ Pas de prédictions")
        
        # 2. Buts attendus
        goals_prediction = predictions.get(f'goals_{team_type}')
        if goals_prediction:
            if '+2.5' in str(goals_prediction):
                score += 1.5
                reasons.append("⚽ Beaucoup de buts attendus")
            elif '+1.5' in str(goals_prediction):
                score += 1
                reasons.append("⚽ Quelques buts attendus")
        
        # 3. Under/Over
        under_over = predictions.get('under_over')
        if under_over and '+2.5' in str(under_over):
            score += 0.5
            reasons.append("🔥 Match spectaculaire")
        
        # 4. Win or Draw
        win_or_draw = predictions.get('win_or_draw')
        if win_or_draw:
            score += 0.5
            reasons.append("🛡️ Pas de risque de défaite")
        
        # 5. Advice
        advice_text = predictions.get('advice')
        if advice_text and team_type in str(advice_text).lower():
            score += 0.5
            reasons.append("💡 Recommandé par l'API")
        
        # Limiter entre 0 et 10
        score = max(0, min(10, score))
        
        # Conseil final
        if score >= 8:
            advice = "🌟 EXCELLENT - À jouer absolument !"
            color = "green"
        elif score >= 6.5:
            advice = "✅ BON - Recommandé pour la lineup"
            color = "blue"
        elif score >= 4.5:
            advice = "⚠️ MOYEN - Risqué mais jouable"
            color = "orange"
        else:
            advice = "❌ FAIBLE - Éviter si possible"
            color = "red"
        
        return {
            'score': round(score, 1),
            'advice': advice,
            'color': color,
            'reasons': reasons
        }
    
    async def get_player_next_match_prediction(self, player_id: int, team_id: int) -> dict:
        """Récupère le prochain match avec prédictions"""
        logger.info(f"📅 Prochain match avec prédictions pour joueur {player_id}")
        
        # 1. Prochain match
        matches_result = await self.get_upcoming_matches(team_id, next=1)
        
        if not matches_result.get('success') or not matches_result.get('data'):
            return {'success': False, 'message': 'Aucun prochain match'}
        
        next_match = matches_result['data'][0]
        fixture_id = next_match.get('fixture', {}).get('id')
        
        if not fixture_id:
            return {'success': False, 'message': 'ID du match non trouvé'}
        
        # 2. Prédictions
        prediction = await self.get_fixture_prediction(fixture_id)
        
        if not prediction.get('success'):
            return {
                'success': True,
                'has_prediction': False,
                'match': next_match,
                'prediction': None,
                'playability_score': {
                    'score': 5.0,
                    'advice': 'ℹ️ Pas de prédictions disponibles',
                    'color': 'gray',
                    'reasons': ['Aucune prédiction disponible']
                }
            }
        
        # 3. Score de jouabilité
        playability_score = self._calculate_playability_score(prediction, team_id)
        
        return {
            'success': True,
            'has_prediction': True,
            'match': next_match,
            'prediction': prediction,
            'playability_score': playability_score
        }
    
    # ============================================
    # AUTRES MÉTHODES
    # ============================================
    
    async def search_players(self, query: str, page: int = 1) -> Dict:
        """Recherche des joueurs par nom"""
        params = {"search": query, "page": page}
        return await self._make_request("/players", params)
    
    async def get_player_by_id(self, player_id: int, season: int = 2025) -> Dict:
        """Récupère un joueur par son ID"""
        params = {"id": player_id, "season": season}
        return await self._make_request("/players", params)
    
    async def search_teams(self, query: str, country: Optional[str] = None) -> Dict:
        """Recherche des équipes"""
        params = {"search": query}
        if country:
            params["country"] = country
        return await self._make_request("/teams", params)
    
    async def get_team_info(self, team_id: int) -> Dict:
        """Récupère les infos d'une équipe"""
        params = {"id": team_id}
        return await self._make_request("/teams", params)
    
    async def get_team_squad(self, team_id: int) -> Dict:
        """Récupère l'effectif d'une équipe"""
        params = {"team": team_id}
        return await self._make_request("/players/squads", params)
    
    async def get_upcoming_matches(self, team_id: int, next: int = 5) -> Dict:
        """Récupère les prochains matchs"""
        params = {"team": team_id, "next": next}
        return await self._make_request("/fixtures", params)
    
    async def get_leagues(self, country: Optional[str] = None, season: int = 2025) -> Dict:
        """Récupère les ligues"""
        params = {"season": season}
        if country:
            params["country"] = country
        return await self._make_request("/leagues", params)
    
    async def check_api_status(self) -> Dict:
        """Vérifie le statut de l'API"""
        return await self._make_request("/status")
    
    def format_player_for_database(self, api_player: Dict) -> Dict:
        """Formate les données pour la base"""
        player = api_player.get('player', {})
        statistics = api_player.get('statistics', [])
        
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
        """Normalise les positions"""
        position_map = {
            "Goalkeeper": "Goalkeeper",
            "Defender": "Defender",
            "Midfielder": "Midfielder",
            "Attacker": "Forward"
        }
        return position_map.get(position, "Midfielder")


# ============================================
# INITIALISATION
# ============================================

try:
    from app.config import settings
    football_api_service = FootballAPIService(settings.FOOTBALL_API_KEY)
    logger.info("✅ FootballAPIService initialisé avec succès")
except Exception as e:
    logger.error(f"❌ Erreur initialisation: {e}")
    football_api_service = None