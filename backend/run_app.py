import sys
import os
from dotenv import load_dotenv
from loguru import logger
from getpass import getpass 
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# =========================================================================
# 1. INITIALISATION ET IMPORTS
# =========================================================================

# Charger les variables d'environnement depuis le fichier .env
load_dotenv() 

# Ajouter le répertoire parent au chemin pour les imports locaux
sys.path.append('.') 

# Importation du Scraper Twitter
try:
    from app.scrapers.twitter_scraper import TwitterSeleniumScraper 
except ImportError:
    logger.error("Impossible d'importer TwitterSeleniumScraper. Vérifiez le chemin : app/scrapers/twitter_scraper.py")
    sys.exit(1)

# Importation de l'Analyseur de Blessures
try:
    from app.analysis.confidence_scorer import InjuryAnalyzer 
    injury_analyzer = InjuryAnalyzer()
except ImportError:
    logger.error("Impossible d'importer InjuryAnalyzer. Vérifiez le fichier app/analysis/confidence_scorer.py.")
    sys.exit(1)

# Configuration de Loguru
logger.add(sys.stderr, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")

# Instance du scraper (sera initialisée dans la fonction principale)
global_scraper: Optional[TwitterSeleniumScraper] = None 


# =========================================================================
# 2. FONCTIONS DE GESTION ET D'ANALYSE (Inchangées)
# =========================================================================

# Les fonctions get_user_credentials, get_next_opponent, analyze_player_risk, 
# et generate_report restent IDENTIQUES car elles sont de la logique métier.

def get_user_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Charge les identifiants de connexion Twitter depuis le fichier .env."""
    email = os.getenv("TWITTER_EMAIL")
    password = os.getenv("TWITTER_PASSWORD")
    
    if email and password:
        logger.info("✅ Identifiants Twitter chargés automatiquement depuis .env.")
        return email, password
    else:
        logger.warning("Identifiants Twitter (TWITTER_EMAIL ou TWITTER_PASSWORD) non trouvés.")
        print("=" * 50)
        print(" 🔒 Connexion à Twitter (X) - SAISIE MANUELLE ")
        print("=" * 50)
        email = input("Email ou Nom d'utilisateur Twitter : ")
        password = getpass("Mot de passe Twitter : ") 
        return email, password

def get_next_opponent(player_name: str) -> str:
    """Détermine le prochain adversaire du joueur (simulée)."""
    player_name_lower = player_name.lower()
    
    if "rodri" in player_name_lower or "manchester city" in player_name_lower:
        opponent = "Fulham (à l'extérieur)"
        date = "Mardi 2 décembre 2025"
        return f"{opponent} - {date}"
    elif "mbappe" in player_name_lower or "paris" in player_name_lower:
        return "Olympique de Marseille (au Parc)"
    else:
        return "Adversaire Inconnu"


def analyze_player_risk(player_name: str, raw_results: List[Dict]) -> Tuple[int, str, List[Dict]]:
    """Analyse les résultats bruts pour calculer un pourcentage de disponibilité."""
    logger.info("Démarrage de l'analyse des risques...")
    
    analyzed_results = []
    
    # 1. Analyser chaque résultat brut en utilisant la méthode correcte : analyze_text
    for item in raw_results:
        try:
            analysis = injury_analyzer.analyze_text(
                text=item.get('content', ''),
                player_name=player_name,
                source=item.get('author', 'unknown'), 
                source_type="twitter"
            )
            item.update(analysis)
            analyzed_results.append(item)
        except Exception as e:
            logger.warning(f"Erreur lors de l'analyse d'un tweet : {e}")
            analyzed_results.append(item) 

    # 2. Déterminer la disponibilité globale
    if not analyzed_results:
        return 100, "✅ Très Probable : Aucune information de blessure pertinente n'a été trouvée.", []

    # Trouver la disponibilité la plus faible rapportée par l'analyseur
    min_availability = min(item.get('availability_percentage', 100) for item in analyzed_results)
    
    confidence_percent = min_availability
    
    # 3. Déterminer la recommandation
    if confidence_percent >= 90:
        recommendation = "✅ Très Probable : Aucune source fiable ne signale de blessure récente."
    elif confidence_percent >= 70:
        recommendation = "🟡 Probable : Quelques mentions de risque, mais aucune confirmation majeure."
    elif confidence_percent >= 40:
        recommendation = "⚠️ Incertain : Plusieurs sources discutent d'une blessure. Risque de forfait."
    else:
        max_confidence = max(item.get('confidence', 0.0) for item in analyzed_results)
        if max_confidence >= 0.8:
            recommendation = "❌ Forfait Confirmé : Le risque est maximal et l'information est fiable."
        else:
            recommendation = "❌ Très Incertain / Forfait : Le risque est élevé. Évitez de l'aligner."

    return confidence_percent, recommendation, analyzed_results


def generate_report(player_name: str, next_opponent: str, raw_results: List[Dict]):
    """Génère et affiche un rapport d'analyse structuré en français."""
    
    confidence_percent, recommendation, analyzed_results = analyze_player_risk(player_name, raw_results)
    
    print("\n" + "=" * 80)
    print(f"       📝 RAPPORT D'ANALYSE DE RISQUE DE BLESSURE POUR {player_name.upper()} 📝")
    print("=" * 80)
    
    # --- Infos Match ---
    print(f"## ⚽ Prochain Match : {next_opponent}")
    print("-" * 40)
    
    # --- Résumé du Risque ---
    print("\n## 📊 Résumé du Risque et Probabilité (Analyse IA)")
    print("-" * 40)
    print(f"**Probabilité de jouer le prochain match :** **{confidence_percent}%**")
    print(f"**Recommandation :** {recommendation}")
    print("-" * 40)
    
    # --- Sources et Éléments Pertinents ---
    print("\n## 📰 Sources Récentes Pertinentes (Confiance Blessure > 30%)")
    
    relevant_results = [item for item in analyzed_results if item.get('confidence', 0.0) >= 0.3]
    
    def sort_key(item):
        return item.get('confidence', 0.0)

    sorted_results = sorted(relevant_results, key=sort_key, reverse=True)

    if not sorted_results:
        print("> Aucune information de blessure pertinente n'a été trouvée (score < 30%).")
        if analyzed_results:
             print(f"> {len(analyzed_results)} tweets ont été analysés (Recherche Blessure + Composition).")
        return

    # Afficher les 5 résultats les plus pertinents
    for i, item in enumerate(sorted_results[:5]):
        date_obj = item.get('date', datetime.now())
        date_str = date_obj.strftime('%d %b à %H:%M') if isinstance(date_obj, datetime) else str(date_obj)
        
        print(f"\n### {i+1}. {item.get('title', 'Source Inconnue')}")
        print(f"**Auteur :** @{item.get('author', 'N/A')}")
        print(f"**Date :** {date_str}")
        print(f"**Confiance Blessure :** {item.get('confidence', 0.0) * 100:.1f}% ({item.get('interpretation', 'N/A')})")
        print(f"**Détails :** {item.get('severity', 'N/A')} - {item.get('injury_type', 'Général')}")
        print(f"**Contenu :** {item['content'][:150]}...")
        print(f"**Lien :** {item['url']}")
        print("---")
        
    print("\n" + "=" * 80)
    logger.info(f"Rapport pour {player_name} terminé. Probabilité de jeu estimée à {confidence_percent}%.")


# =========================================================================
# 3. FONCTION PRINCIPALE (MODIFIÉE)
# =========================================================================

def run_interactive_report():
    """
    Fonction principale interactive.
    Initialise le scraper une fois, puis entre dans une boucle de recherche.
    """
    global global_scraper
    
    email, password = get_user_credentials()
    
    if not email or not password:
        logger.error("Identifiants Twitter manquants. Fin du programme.")
        return

    try:
        # 1. 🔑 INITIALISATION UNIQUE DU SCRAPER (Ouverture du navigateur)
        logger.info("Ouverture du navigateur Chrome...")
        global_scraper = TwitterSeleniumScraper(
            twitter_email=email, 
            twitter_password=password
        )

        # 2. DÉMARRAGE DE LA BOUCLE INTERACTIVE
        while True:
            print("-" * 50)
            player_name = input("✍️ Entrez le nom complet du joueur à rechercher (ou 'quitter') : ")
            
            if player_name.strip().lower() in ('q', 'quit', 'quitter'):
                logger.info("Demande d'arrêt. Fin de la session de recherche.")
                break
                
            if not player_name.strip():
                continue
                
            # --- DÉBUT DU TRAITEMENT D'UN JOUEUR ---
            try:
                # 1. Obtenir l'adversaire
                next_opponent = get_next_opponent(player_name)
                logger.info(f"Prochain adversaire déterminé : {next_opponent}")
                
                # 2. Exécuter le Scraping (le scraper réutilise la session ouverte)
                raw_results = global_scraper.search_player_news(
                    player_name=player_name, 
                    max_tweets_per_query=30
                )
                
                # 3. Afficher le Compte Rendu
                if raw_results:
                    generate_report(player_name, next_opponent, raw_results)
                else:
                    logger.warning(
                        f"Aucune information récente trouvée pour {player_name} après l'exécution des deux requêtes."
                    )
            
            except Exception as e:
                logger.error(f"Une erreur est survenue lors du traitement de {player_name} : {e}")
                
            # --- FIN DU TRAITEMENT D'UN JOUEUR ---
            
    except Exception as e:
        logger.error(f"Une erreur inattendue est survenue lors de l'initialisation ou de l'exécution : {e}")
        
    finally:
        # 3. 🔑 FERMETURE UNIQUE DU SCRAPER (Fermeture du navigateur à la fin du programme)
        if global_scraper:
            global_scraper.close()
            logger.info("Navigateur fermé.")


if __name__ == "__main__":
    # La fonction run_injury_report est remplacée par la boucle interactive
    run_interactive_report()