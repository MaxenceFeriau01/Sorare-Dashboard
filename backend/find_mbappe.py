"""
Script pour trouver le bon ID de Kylian Mbappé
"""
import httpx
import asyncio

API_KEY = "b3337b4a41780ddee3261615c4d9fe4d"
BASE_URL = "https://v3.football.api-sports.io"

async def search_mbappe():
    """Cherche tous les Mbappé"""
    url = f"{BASE_URL}/players/profiles"
    headers = {"x-apisports-key": API_KEY}
    params = {"search": "Mbappe"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        
        print("=" * 80)
        print("🔍 TOUS LES MBAPPÉ TROUVÉS")
        print("=" * 80)
        
        for item in data.get('response', []):
            player = item.get('player', item)
            print(f"\nID: {player.get('id')}")
            print(f"Nom: {player.get('name')}")
            print(f"Prénom: {player.get('firstname')}")
            print(f"Nom de famille: {player.get('lastname')}")
            print(f"Âge: {player.get('age')}")
            print(f"Nationalité: {player.get('nationality')}")
            print(f"Photo: {player.get('photo')}")
            print("-" * 80)


async def check_player_injuries(player_id: int, season: int = 2025):
    """Vérifie si un joueur est blessé"""
    url = f"{BASE_URL}/injuries"
    headers = {"x-apisports-key": API_KEY}
    params = {"player": player_id, "season": season}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        
        injuries = data.get('response', [])
        
        if injuries:
            print(f"\n🏥 BLESSURES:")
            for injury in injuries[:3]:  # Afficher les 3 dernières
                player_info = injury.get('player', {})
                fixture = injury.get('fixture', {})
                
                print(f"   ⚠️ Type: {player_info.get('type')}")
                print(f"   📋 Raison: {player_info.get('reason')}")
                print(f"   📅 Match: {fixture.get('date', 'N/A')}")
        else:
            print(f"\n✅ AUCUNE BLESSURE EN COURS")


async def check_player_team(player_id: int, season: int = 2025):
    """Vérifie l'équipe actuelle d'un joueur"""
    url = f"{BASE_URL}/players"
    headers = {"x-apisports-key": API_KEY}
    params = {"id": player_id, "season": season}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        
        print(f"\n{'=' * 80}")
        print(f"📊 DÉTAILS JOUEUR ID: {player_id} (SAISON {season})")
        print(f"{'=' * 80}")
        
        if data.get('response'):
            item = data['response'][0]
            player = item.get('player', {})
            statistics = item.get('statistics', [])
            
            print(f"Nom: {player.get('name')}")
            print(f"Âge: {player.get('age')} ans")
            print(f"Nationalité: {player.get('nationality')}")
            
            # Vérifier si blessé dans le profil
            if player.get('injured'):
                print(f"⚠️ STATUT: BLESSÉ")
            else:
                print(f"✅ STATUT: DISPONIBLE")
            
            if statistics:
                for stat in statistics:
                    team = stat.get('team', {})
                    league = stat.get('league', {})
                    games = stat.get('games', {})
                    goals = stat.get('goals', {})
                    
                    print(f"\n🏆 Équipe: {team.get('name')}")
                    print(f"   Ligue: {league.get('name')}")
                    print(f"   Position: {games.get('position')}")
                    print(f"   Matchs: {games.get('appearances')}")
                    print(f"   Buts: {goals.get('total')}")
                    print(f"   Assists: {goals.get('assists')}")
            else:
                print("\n⚠️ Aucune statistique pour 2025")
            
            # Vérifier les blessures via l'endpoint dédié
            await check_player_injuries(player_id, season)
        else:
            print("❌ Aucune donnée trouvée")


async def main():
    print("\n" + "=" * 80)
    print("🔎 RECHERCHE DU VRAI KYLIAN MBAPPÉ")
    print("=" * 80)
    
    # 1. Lister tous les Mbappé
    await search_mbappe()
    
    # 2. Vérifier les IDs suspects
    suspect_ids = [276, 278, 200174, 386287]
    
    print("\n" + "=" * 80)
    print("🔍 VÉRIFICATION DES ÉQUIPES ACTUELLES")
    print("=" * 80)
    
    for player_id in suspect_ids:
        await check_player_team(player_id, 2025)
        await asyncio.sleep(0.5)  # Pause entre les requêtes
    
    print("\n" + "=" * 80)
    print("✅ ANALYSE TERMINÉE")
    print("=" * 80)
    print("\nℹ️  Le vrai Kylian Mbappé du Real Madrid devrait apparaître ci-dessus")
    print("ℹ️  Cherche celui avec 'Real Madrid' comme équipe actuelle")


if __name__ == "__main__":
    asyncio.run(main())