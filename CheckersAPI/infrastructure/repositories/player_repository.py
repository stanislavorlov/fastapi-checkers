from domain.player.player import Player
from infrastructure.documents import PlayerSchema, PlayerType, RankSchema, StatsSchema
from infrastructure.mongo_context import MongoContext


class PlayerRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    def create(self, player: Player) -> str:
        player_document = PlayerSchema(
            type=PlayerType(player.type_.value),
            display_name=player.display_name,
            profile_id=player.profile_id,
        )

        result = self.db.players.insert_one(
            player_document
        )

        rank_document = RankSchema(
            player_id=result.inserted_id,
            rating=player.rank.rating,
            deviation=player.rank.deviation,
        )

        self.db.ranks.insert_one(rank_document)

        stats_document = StatsSchema(
            player_id=result.inserted_id,
            streak=player.stats.streak,
            wins=player.stats.wins,
            losses=player.stats.losses,
            draws=player.stats.draws,
            win_rate=player.stats.win_rate,
            games_played=player.stats.games_played,
        )

        self.db.stats.insert_one(stats_document)

        return str(result.inserted_id)