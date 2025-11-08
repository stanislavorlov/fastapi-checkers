from bson import ObjectId
from domain.player.display_name import DisplayName
from domain.player.player import Player
from domain.player.rank import Rank
from domain.player.stats import PlayerStats
from infrastructure.documents import PlayerSchema, PlayerType, RankSchema, StatsSchema
from infrastructure.mongo_context import MongoContext


class PlayerRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    def create(self, player: Player) -> str:
        player_document = PlayerSchema(
            type=PlayerType(player.type_.value),
            display_name=player.display_name.value,
            profile_id=player.profile_id,
        )

        result = self.db.players.insert_one(
            player_document.model_dump()
        )

        rank_document = RankSchema(
            player_id=result.inserted_id,
            rating=player.rank.rating,
            deviation=player.rank.deviation,
        )

        self.db.ranks.insert_one(rank_document.model_dump())

        stats_document = StatsSchema(
            player_id=result.inserted_id,
            streak=player.stats.streak,
            wins=player.stats.wins,
            losses=player.stats.losses,
            draws=player.stats.draws,
            win_rate=player.stats.win_rate,
            games_played=player.stats.games_played,
        )

        self.db.stats.insert_one(stats_document.model_dump())

        return str(result.inserted_id)

    def get_by_profile_id(self, profile_id: str) -> Player:
        print('looking up player by profile_id: {}'.format(profile_id))
        result = self.db.players.find_one({"profile_id": ObjectId(profile_id)})
        rank = self.db.ranks.find_one({"player_id": result["_id"]})
        stats = self.db.stats.find_one({"player_id": result["_id"]})

        return Player(
            _type=PlayerType.ACCOUNT,
            display_name=DisplayName(display_name=result["display_name"]),
            profile_id=result["profile_id"],
            _rank=Rank(
                rating=rank['rating'],
                deviation=rank['deviation'],
                last_update=rank['last_update'],
            ),
            _stats=PlayerStats(
                games_played=stats['games_played'],
                wins=stats['wins'],
                losses=stats['losses'],
                draws=stats['draws'],
                win_rate=stats['win_rate'],
                streak=stats['streak'],
            ),
        )