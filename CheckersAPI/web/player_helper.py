from datetime import datetime
from infrastructure.documents import PlayerStatsSchema, PlayerRankSchema


def detect_region(country: str):
    match country:
        case "UA":
            return "EU"
        case "UK":
            return "UK"
        case _:
            return "Global"

# def initial_rank(level: str) -> PlayerRankSchema:
#     match level:
#         case "beginner":
#             return PlayerRankSchema(rating=400, deviation=0, last_update=datetime.now())
#         case "intermediate":
#             return PlayerRankSchema(rating=800, deviation=0, last_update=datetime.now())
#         case "advanced":
#             return PlayerRankSchema(rating=1200, deviation=0, last_update=datetime.now())
#
#     return PlayerRankSchema(rating=800, deviation=0, last_update=datetime.now())

def initial_stats():
    return PlayerStatsSchema(
            games_played=0,
            wins=0,
            losses=0,
            draws=0,
            win_rate=0.0,
            streak=0
        )