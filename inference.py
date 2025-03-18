def recommend_games(games_data, user_preferences):
    recommended = []
    for game in games_data:
        if game_matches_preferences(game, user_preferences):
            recommended.append(game)
    return recommended

def game_matches_preferences(game, prefs):
    # check genre
    if prefs.get("genre"):
        if not any(g.lower() == prefs["genre"] for g in game.get("genre", [])):
            return False

    # check platform
    if prefs.get("platform"):
        if not any(prefs["platform"].lower() in p.lower() for p in game.get("platforms", [])):
            return False

    # check price
    try:
        price = float(game.get("price", 0))
    except (ValueError, TypeError):
        price = 0
    if price > prefs.get("price_max", 0):
        return False

    return True
