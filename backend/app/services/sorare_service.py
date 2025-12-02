"""
Service pour interagir avec l'API Sorare GraphQL
"""
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from typing import List, Dict, Optional
from loguru import logger
import bcrypt

from app.config import settings


class SorareService:
    """Service pour gérer les interactions avec l'API Sorare"""
    
    def __init__(self):
        self.api_url = settings.SORARE_API_URL
        self.email = settings.SORARE_EMAIL
        self.password = settings.SORARE_PASSWORD
        self.client = None
    
    def connect(self) -> bool:
        """
        Se connecte à l'API Sorare avec authentification
        """
        try:
            # Créer le transport HTTP
            transport = RequestsHTTPTransport(
                url=self.api_url,
                use_json=True,
                headers={
                    "Content-type": "application/json",
                },
                verify=True,
                retries=3,
            )
            
            # Créer le client GraphQL
            self.client = Client(
                transport=transport,
                fetch_schema_from_transport=False,
            )
            
            # Mutation pour se connecter
            login_mutation = gql("""
                mutation SignInMutation($input: signInInput!) {
                    signIn(input: $input) {
                        currentUser {
                            slug
                            id
                        }
                        errors {
                            message
                        }
                    }
                }
            """)
            
            logger.info(f"Tentative de connexion à Sorare avec {self.email}...")
            
            # Hasher le mot de passe avec bcrypt
            hashed_password = bcrypt.hashpw(
                self.password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Paramètres de connexion
            params = {
                "input": {
                    "email": self.email,
                    "password": hashed_password
                }
            }
            
            # Exécuter la mutation
            result = self.client.execute(login_mutation, variable_values=params)
            
            # Vérifier les erreurs
            errors = result.get("signIn", {}).get("errors")
            if errors:
                logger.error(f"Erreur de connexion Sorare: {errors}")
                return False
            
            # Vérifier la connexion
            current_user = result.get("signIn", {}).get("currentUser")
            if current_user:
                logger.success(f"✅ Connecté à Sorare en tant que {current_user['slug']}")
                return True
            
            logger.error("❌ Impossible de se connecter à Sorare")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la connexion à Sorare: {e}")
            return False
    
    def get_my_cards(self, limit: int = 50) -> List[Dict]:
        """
        Récupère les cartes de l'utilisateur connecté
        
        Args:
            limit: Nombre maximum de cartes à récupérer
            
        Returns:
            Liste des cartes avec les informations des joueurs
        """
        if not self.client:
            logger.warning("Non connecté à Sorare. Connexion en cours...")
            if not self.connect():
                return []
        
        try:
            # Query GraphQL pour récupérer les cartes
            cards_query = gql("""
                query GetMyCards($first: Int!) {
                    currentUser {
                        cards(first: $first) {
                            nodes {
                                slug
                                rarity
                                serialNumber
                                player {
                                    slug
                                    displayName
                                    firstName
                                    lastName
                                    age
                                    birthDate
                                    country {
                                        code
                                        name
                                    }
                                    position
                                    activeClub {
                                        name
                                        slug
                                    }
                                    avatarUrl
                                    status
                                }
                            }
                        }
                    }
                }
            """)
            
            # Exécuter la query
            result = self.client.execute(cards_query, variable_values={"first": limit})
            
            # Extraire les cartes
            cards = result.get("currentUser", {}).get("cards", {}).get("nodes", [])
            
            logger.info(f"✅ Récupéré {len(cards)} cartes depuis Sorare")
            
            return cards
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des cartes: {e}")
            return []
    
    def get_player_info(self, player_slug: str) -> Optional[Dict]:
        """
        Récupère les informations détaillées d'un joueur
        
        Args:
            player_slug: Le slug du joueur sur Sorare
            
        Returns:
            Dictionnaire avec les infos du joueur ou None
        """
        if not self.client:
            logger.warning("Non connecté à Sorare. Connexion en cours...")
            if not self.connect():
                return None
        
        try:
            # Query GraphQL pour un joueur spécifique
            player_query = gql("""
                query GetPlayer($slug: String!) {
                    player(slug: $slug) {
                        slug
                        displayName
                        firstName
                        lastName
                        age
                        birthDate
                        country {
                            code
                            name
                        }
                        position
                        activeClub {
                            name
                            slug
                        }
                        avatarUrl
                        status
                    }
                }
            """)
            
            # Exécuter la query
            result = self.client.execute(player_query, variable_values={"slug": player_slug})
            
            player = result.get("player")
            
            if player:
                logger.info(f"✅ Infos récupérées pour {player['displayName']}")
            
            return player
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération du joueur {player_slug}: {e}")
            return None
    
    def format_player_for_db(self, player_data: Dict) -> Dict:
        """
        Formate les données d'un joueur Sorare pour la base de données
        
        Args:
            player_data: Données brutes du joueur depuis l'API Sorare
            
        Returns:
            Dictionnaire formaté pour le modèle Player
        """
        club = player_data.get("activeClub") or {}
        country = player_data.get("country") or {}
        
        return {
            "sorare_id": player_data.get("slug"),
            "first_name": player_data.get("firstName"),
            "last_name": player_data.get("lastName"),
            "display_name": player_data.get("displayName"),
            "slug": player_data.get("slug"),
            "club_name": club.get("name"),
            "club_slug": club.get("slug"),
            "position": player_data.get("position"),
            "country": country.get("name"),
            "country_code": country.get("code"),
            "age": player_data.get("age"),
            "birth_date": player_data.get("birthDate"),
            "average_score": 0.0,
            "total_games": 0,
            "is_active": player_data.get("status") in ["ACTIVE", "PENDING"],
            "image_url": player_data.get("avatarUrl"),
            "card_sample_url": None,
        }


# Instance globale du service
sorare_service = SorareService()