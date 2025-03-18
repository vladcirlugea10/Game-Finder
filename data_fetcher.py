import os
import json
import time
import requests

KB_FILENAME = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
CACHE_DURATION = 3600  # 1 hour

IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
IGDB_ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")

def fetch_from_igdb():
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": IGDB_CLIENT_ID,
        "Authorization": f"Bearer {IGDB_ACCESS_TOKEN}"
    }
    
    # categories with their coresponding IGDB genre IDs.
    categories = {
        "action": 4,
        "adventure": 31,
        "strategy": 15,
        "rpg": 12,
        "simulation": 8
    }
    
    desired_count = 20
    genres_map = fetch_genres_mapping()
    platforms_map = fetch_platforms_mapping()
    all_games = []

    for category, genre_id in categories.items():
        category_games = []
        offset = 0
        while len(category_games) < desired_count:
            query = (
                f"fields name, genres, platforms, rating, cover.url; "
                f"where genres = ({genre_id}); "
                f"limit {desired_count} offset {offset};"
            )
            response = requests.post(url, headers=headers, data=query)
            if response.status_code != 200:
                print(f"Error fetching {category} games: {response.status_code}, {response.text}")
                break

            fetched_games = response.json()
            if not fetched_games:
                break

            category_games.extend(fetched_games)
            offset += desired_count

        category_games = category_games[:desired_count]
        for game in category_games:
            processed_game = {
                "name": game.get("name", "Unknown Game"),
                "description": "No description available.",
                "genre": [genres_map.get(g, "Unknown") for g in game.get("genres", [])],
                "platforms": [platforms_map.get(p, "Unknown") for p in game.get("platforms", [])],
                "rating": round(game.get("rating", 0), 1),
                "image_url": "https:" + game.get("cover", {}).get("url", "//via.placeholder.com/200"),
                "price": fetch_price_from_cheapshark(game.get("name", ""))
            }
            all_games.append(processed_game)
    
    save_to_cache(all_games)
    return all_games

def fetch_genres_mapping():
    url = "https://api.igdb.com/v4/genres"
    headers = {
        "Client-ID": IGDB_CLIENT_ID,
        "Authorization": f"Bearer {IGDB_ACCESS_TOKEN}"
    }
    query = "fields id, name; limit 50;"
    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 200:
        return {g["id"]: g["name"] for g in response.json()}
    return {}

def fetch_platforms_mapping():
    """Fetches platform ID-to-name mapping from IGDB."""
    url = "https://api.igdb.com/v4/platforms"
    headers = {
        "Client-ID": IGDB_CLIENT_ID,
        "Authorization": f"Bearer {IGDB_ACCESS_TOKEN}"
    }
    query = "fields id, name; limit 50;"
    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 200:
        return {p["id"]: p["name"] for p in response.json()}
    return {}

def fetch_price_from_cheapshark(game_name):
    try:
        params = {"title": game_name, "limit": 1}
        response = requests.get("https://www.cheapshark.com/api/1.0/games", params=params)
        response.raise_for_status()
        data = response.json()
        if data and isinstance(data, list):
            return float(data[0].get("cheapest", 0))
    except Exception as e:
        print(f"Error fetching price for {game_name}: {e}")
    return 0.0

def save_to_cache(games):
    data = {"games": games}
    try:
        with open(KB_FILENAME, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error writing to cache:", e)

def fetch_game_data(force_update=False):
    if not force_update and os.path.exists(KB_FILENAME):
        last_modified = os.path.getmtime(KB_FILENAME)
        if time.time() - last_modified < CACHE_DURATION:
            with open(KB_FILENAME, "r", encoding="utf-8") as f:
                return json.load(f).get("games", [])

    return fetch_from_igdb()
