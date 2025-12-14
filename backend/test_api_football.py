"""
Script de test simple pour vérifier l'API-Football
"""
import httpx
import asyncio

API_KEY = "b3337b4a41780ddee3261615c4d9fe4d"
BASE_URL = "https://v3.football.api-sports.io"

async def test_status():
    """Test 1: Vérifier le statut de l'API"""
    print("=" * 60)
    print("TEST 1: Vérification du statut de l'API")
    print("=" * 60)
    
    url = f"{BASE_URL}/status"
    headers = {"x-apisports-key": API_KEY}
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Rate Limit Headers:")
        print(f"  - Remaining: {response.headers.get('x-ratelimit-requests-remaining', 'N/A')}")
        print(f"  - Limit: {response.headers.get('x-ratelimit-requests-limit', 'N/A')}")
        
        data = response.json()
        print(f"\nResponse:")
        print(data)
        
        if data.get('errors'):
            print(f"\n❌ ERREUR: {data['errors']}")
            return False
        else:
            print(f"\n✅ SUCCÈS!")
            return True

async def test_search():
    """Test 2: Rechercher un joueur"""
    print("\n" + "=" * 60)
    print("TEST 2: Recherche d'un joueur")
    print("=" * 60)
    
    url = f"{BASE_URL}/players/profiles"
    headers = {"x-apisports-key": API_KEY}
    params = {"search": "Mbappe"}
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        
        print(f"Status Code: {response.status_code}")
        print(f"Rate Limit Headers:")
        print(f"  - Remaining: {response.headers.get('x-ratelimit-requests-remaining', 'N/A')}")
        print(f"  - Limit: {response.headers.get('x-ratelimit-requests-limit', 'N/A')}")
        
        data = response.json()
        
        if data.get('errors'):
            print(f"\n❌ ERREUR: {data['errors']}")
            return False
        else:
            print(f"\n✅ SUCCÈS! {data.get('results', 0)} résultat(s)")
            
            # Afficher le premier résultat
            if data.get('response'):
                first = data['response'][0]
                player = first.get('player', first)
                print(f"\nPremier résultat:")
                print(f"  - ID: {player.get('id')}")
                print(f"  - Nom: {player.get('name')}")
                print(f"  - Âge: {player.get('age')}")
                print(f"  - Nationalité: {player.get('nationality')}")
            return True

async def main():
    """Lancer tous les tests"""
    print("\n🔑 TEST API-FOOTBALL")
    print(f"API Key: {API_KEY}")
    print()
    
    # Test 1: Status
    status_ok = await test_status()
    
    if status_ok:
        # Test 2: Recherche
        await test_search()
    else:
        print("\n⚠️ Le test de status a échoué, impossible de continuer")

if __name__ == "__main__":
    asyncio.run(main())