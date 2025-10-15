from domain.players.player import Player
from infrastructure.documents import PlayerSchema


def domain_to_schema(player: Player, rank_id: str, stats_id: str) -> PlayerSchema:
    return PlayerSchema.model_validate({
        **player.__dict__,
        "rank_id": rank_id,
        "stats_id": stats_id,
        "region": player.region.name,
    })