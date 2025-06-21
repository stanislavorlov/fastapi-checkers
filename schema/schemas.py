def individual_game(game) -> dict:
    return {
        "id": str(game["_id"]),
        "name": game["name"],
        "started": game["started"]
    }

def list_games(games) -> list:
    return [individual_game(game) for game in games]