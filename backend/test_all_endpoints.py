"""
Script de test complet pour tous les endpoints API-Football
VERSION PRO - Avec accès saison 2025
"""
import httpx
import asyncio
from typing import Dict, Any

API_KEY = "b3337b4a41780ddee3261615c4d9fe4d"
BASE_URL = "https://v3.football.api-sports.io"

# IDs pour les tests
TEST_PLAYER_ID = 276  # Kylian Mbappé
TEST_TEAM_ID = 541    # Real Madrid
TEST_LEAGUE_ID = 140  # La Liga
TEST_SEASON = 2025    # Saison actuelle


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'


def print_test(title: str):
    print(f"\n{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 80}{Colors.END}")


def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_info(msg: str):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.END}")


async def make_request(endpoint: str, params: Dict = None) -> Dict[str, Any]:
    """Effectue une requête à l'API"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"x-apisports-key": API_KEY}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers, params=params or {})
        data = response.json()
        
        # Afficher les rate limits
        remaining = response.headers.get('x-ratelimit-requests-remaining', 'N/A')
        limit = response.headers.get('x-ratelimit-requests-limit', 'N/A')
        print_info(f"Rate Limit: {remaining}/{limit}")
        
        return data


async def test_status():
    """Test 1: Statut de l'API"""
    print_test("TEST 1: STATUT DE L'API")
    
    data = await make_request("/status")
    
    if data.get('errors'):
        print_error(f"Erreurs: {data['errors']}")
        return False
    
    response = data.get('response', {})
    account = response.get('account', {})
    subscription = response.get('subscription', {})
    requests = response.get('requests', {})
    
    print_success(f"Compte: {account.get('firstname')} {account.get('lastname')}")
    print_success(f"Plan: {subscription.get('plan')}")
    print_success(f"Requêtes: {requests.get('current')}/{requests.get('limit_day')}")
    
    return True


async def test_search_players():
    """Test 2: Recherche de joueurs"""
    print_test("TEST 2: RECHERCHE DE JOUEURS")
    
    print_info("Recherche: 'Mbappe'")
    data = await make_request("/players/profiles", {"search": "Mbappe"})
    
    if data.get('errors'):
        print_error(f"Erreurs: {data['errors']}")
        return False
    
    results = data.get('results', 0)
    print_success(f"{results} résultat(s) trouvé(s)")
    
    if data.get('response'):
        for i, item in enumerate(data['response'][:3], 1):
            player = item.get('player', item)
            print(f"  {i}. {player.get('name')} (ID: {player.get('id')}) - {player.get('age')} ans - {player.get('nationality')}")
    
    return True


async def test_player_details():
    """Test 3: Détails d'un joueur"""
    print_test(f"TEST 3: DÉTAILS DU JOUEUR (ID: {TEST_PLAYER_ID})")
    
    print_info(f"Récupération des stats pour la saison {TEST_SEASON}...")
    data = await make_request("/players", {"id": TEST_PLAYER_ID, "season": TEST_SEASON})
    
    if data.get('errors'):
        print_error(f"Erreurs: {data['errors']}")
        return False
    
    if not data.get('response'):
        print_error("Aucune donnée retournée")
        return False
    
    item = data['response'][0]
    player = item.get('player', {})
    statistics = item.get('statistics', [])
    
    print_success(f"Joueur: {player.get('name')}")
    print_success(f"Âge: {player.get('age')} ans")
    print_success(f"Nationalité: {player.get('nationality')}")
    print_success(f"Taille: {player.get('height')}")
    print_success(f"Poids: {player.get('weight')}")
    
    if statistics:
        stats = statistics[0]
        team = stats.get('team', {})
        games = stats.get('games', {})
        goals = stats.get('goals', {})
        
        print_success(f"\nÉquipe actuelle: {team.get('name')}")
        print_success(f"Position: {games.get('position')}")
        print_success(f"Matchs: {games.get('appearances')}")
        print_success(f"Buts: {goals.get('total')}")
        print_success(f"Assists: {goals.get('assists')}")
    
    return True


async def test_search_teams():
    """Test 4: Recherche d'équipes"""
    print_test("TEST 4: RECHERCHE D'ÉQUIPES")
    
    print_info("Recherche: 'Real Madrid'")
    data = await make_request("/teams", {"search": "Real Madrid"})
    
    if data.get('errors'):
        print_error(f"Erreurs: {data['errors']}")
        return False
    
    results = data.get('results', 0)
    print_success(f"{results} résultat(s) trouvé(s)")
    
    if data.get('response'):
        for i, item in enumerate(data['response'][:3], 1):
            team = item.get('team', {})
            venue = item.get('venue', {})
            print(f"  {i}. {team.get('name')} (ID: {team.get('id')}) - {team.get('country')} - Stade: {venue.get('name')}")
    
    return True


async def test_team_details():
    """Test 5: Détails d'une équipe"""
    print_test(f"TEST 5: DÉTAILS DE L'ÉQUIPE (ID: {TEST_TEAM_ID})")
    
    data = await make_request("/teams", {"id": TEST_TEAM_ID})
    
    if data.get('errors'):
        print_error(f"Erreurs: {data['errors']}")
        return False
    
    if not data.get('response'):
        print_error("Aucune donnée retournée")
        return False
    
    item = data['response'][0]
    team = item.get('team', {})
    venue = item.get('venue', {})
    
    print_success(f"Équipe: {team.get('name')}")
    print_success(f"Pays: {team.get('country')}")
    print_success(f"Fondée en: {team.get('founded')}")
    print_success(f"Stade: {venue.get('name')}")
    print_success(f"Ville: {venue.get('city')}")
    print_success(f"Capacité: {venue.get('capacity')} places")
    
    return True


async def test_upcoming_matches():
    """Test 6: Prochains matchs"""
    print_test(f"TEST 6: PROCHAINS MATCHS (Équipe ID: {TEST_TEAM_ID})")
    
    print_info("Récupération des 5 prochains matchs...")
    data = await make_request("/fixtures", {"team": TEST_TEAM_ID, "next": 5})
    
    if data.get('errors'):
        print_error(f"Erreurs: {data['errors']}")
        return False
    
    results = data.get('results', 0)
    print_success(f"{results} match(s) à venir")
    
    if data.get('response'):
        for i, fixture in enumerate(data['response'], 1):
            fixture_data = fixture.get('fixture', {})
            teams = fixture.get('teams', {})
            league = fixture.get('league', {})
            
            home = teams.get('home', {}).get('name')
            away = teams.get('away', {}).get('name')
            date = fixture_data.get('date', 'N/A')
            
            print(f"  {i}. {date[:10]} - {home} vs {away} ({league.get('name')})")
    
    return True


async def test_leagues():
    """Test 7: Liste des ligues"""
    print_test("TEST 7: LIGUES DISPONIBLES")
    
    print_info(f"Récupération des ligues pour la France (saison {TEST_SEASON})...")
    data = await make_request("/leagues", {"country": "France", "season": TEST_SEASON})
    
    if data.get('errors'):
        print_error(f"Erreurs: {data['errors']}")
        return False
    
    results = data.get('results', 0)
    print_success(f"{results} ligue(s) trouvée(s)")
    
    if data.get('response'):
        for i, item in enumerate(data['response'][:5], 1):
            league = item.get('league', {})
            print(f"  {i}. {league.get('name')} (ID: {league.get('id')}) - Type: {league.get('type')}")
    
    return True


async def test_injuries():
    """Test 8: Blessures"""
    print_test(f"TEST 8: BLESSURES (Équipe ID: {TEST_TEAM_ID})")
    
    print_info(f"Récupération des blessures de l'équipe (saison {TEST_SEASON})...")
    data = await make_request("/injuries", {"team": TEST_TEAM_ID, "season": TEST_SEASON})
    
    if data.get('errors'):
        print_error(f"Erreurs: {data['errors']}")
        return False
    
    results = data.get('results', 0)
    
    if results == 0:
        print_info("Aucune blessure en cours (c'est une bonne nouvelle !)")
    else:
        print_success(f"{results} joueur(s) blessé(s)")
        
        if data.get('response'):
            for i, injury in enumerate(data['response'][:5], 1):
                player = injury.get('player', {})
                fixture = injury.get('fixture', {})
                print(f"  {i}. {player.get('name')} - {player.get('reason')} (Type: {player.get('type')})")
    
    return True


async def main():
    """Lance tous les tests"""
    print(f"\n{Colors.GREEN}{'=' * 80}{Colors.END}")
    print(f"{Colors.GREEN}🧪 TEST COMPLET API-FOOTBALL{Colors.END}")
    print(f"{Colors.GREEN}API Key: {API_KEY[:20]}...{Colors.END}")
    print(f"{Colors.GREEN}{'=' * 80}{Colors.END}")
    
    tests = [
        ("Statut API", test_status),
        ("Recherche joueurs", test_search_players),
        ("Détails joueur", test_player_details),
        ("Recherche équipes", test_search_teams),
        ("Détails équipe", test_team_details),
        ("Prochains matchs", test_upcoming_matches),
        ("Ligues", test_leagues),
        ("Blessures", test_injuries),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Exception: {e}")
            results.append((name, False))
        
        # Petite pause entre chaque test
        await asyncio.sleep(1)
    
    # Résumé final
    print(f"\n{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BLUE}📊 RÉSUMÉ DES TESTS{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 80}{Colors.END}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if success else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{status} - {name}")
    
    print(f"\n{Colors.BLUE}Score: {passed}/{total} tests réussis{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}\n🎉 TOUS LES TESTS SONT PASSÉS ! 🎉{Colors.END}")
    else:
        print(f"{Colors.RED}\n⚠️ Certains tests ont échoué{Colors.END}")


if __name__ == "__main__":
    asyncio.run(main())