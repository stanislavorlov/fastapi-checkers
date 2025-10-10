from infrastructure.documents import PlayerStats


def detect_region(country: str):
    match country:
        case "UA":
            return "EU"
        case "UK":
            return "UK"
        case _:
            return "Global"

def initial_rank(level: str) -> int:
    match level:
        case "beginner":
            return 400
        case "intermediate":
            return 800
        case "advanced":
            return 1200

    return 800

def initial_stats():
    return PlayerStats(
            games_played=0,
            wins=0,
            losses=0,
            draws=0,
            win_rate=0.0,
            streak=0
        )