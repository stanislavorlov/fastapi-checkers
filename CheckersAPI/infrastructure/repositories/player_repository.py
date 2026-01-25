import logging
from datetime import datetime, timezone
from bson import ObjectId
from domain.player.display_name import DisplayName
from domain.player.player import Player
from domain.player.rank import Rank
from domain.player.stats import PlayerStats
from infrastructure.documents import PlayerSchema, PlayerType, RankSchema, StatsSchema
from infrastructure.mongo_context import MongoContext

logger = logging.getLogger(__name__)

class PlayerRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    def create(self, player: Player) -> str:
        player_document = PlayerSchema(
            id=player.id,
            type=PlayerType(player.type_.value),
            display_name=player.display_name.value,
            profile_id=player.profile_id,
        )

        self.db.players.insert_one(
            player_document.model_dump(mode='python', by_alias=True)
        )

        rank_document = RankSchema(
            player_id=player.id,
            rating=player.rank.rating,
            deviation=player.rank.deviation,
        )

        self.db.ranks.insert_one(rank_document.model_dump(mode='python', by_alias=True))

        stats_document = StatsSchema(
            player_id=player.id,
            streak=player.stats.streak,
            wins=player.stats.wins,
            losses=player.stats.losses,
            draws=player.stats.draws,
            win_rate=player.stats.win_rate,
            games_played=player.stats.games_played,
        )

        self.db.stats.insert_one(stats_document.model_dump(mode='python', by_alias=True))

        return str(player.id)

    def get_by_id(self, player_id: str) -> Player:
        logger.debug(f'looking up player by id: {player_id}')
        result = self.db.players.find_one({"_id": ObjectId(player_id)})
        
        if result is None:
            return None
            
        rank = self.db.ranks.find_one({"player_id": result["_id"]})
        stats = self.db.stats.find_one({"player_id": result["_id"]})

        return Player(
            _id=result["_id"],
            _type=PlayerType(result["type"]),
            display_name=DisplayName(display_name=result["display_name"]),
            profile_id=result.get("profile_id"),
            _rank=Rank(
                rating=rank['rating'] if rank else 0,
                deviation=rank['deviation'] if rank else 0,
                last_update=rank['last_update'] if rank and 'last_update' in rank else datetime.now(timezone.utc),
            ),
            _stats=PlayerStats(
                games_played=stats['games_played'] if stats else 0,
                wins=stats['wins'] if stats else 0,
                losses=stats['losses'] if stats else 0,
                draws=stats['draws'] if stats else 0,
                win_rate=stats['win_rate'] if stats else 0,
                streak=stats['streak'] if stats else 0,
            ),
        )

    def get_by_profile_id(self, profile_id: str | ObjectId) -> Player | None:
        logger.debug(f'looking up player by profile_id: {profile_id}')
        
        oid = ObjectId(profile_id) if isinstance(profile_id, str) else profile_id
        result = self.db.players.find_one({"profile_id": oid})
        
        if result is None:
            return None
            
        rank = self.db.ranks.find_one({"player_id": result["_id"]})
        stats = self.db.stats.find_one({"player_id": result["_id"]})

        return Player(
            id=result["_id"],
            _type=PlayerType(result["type"]),
            display_name=DisplayName(display_name=result["display_name"]),
            profile_id=result.get("profile_id"),
            _rank=Rank(
                rating=rank['rating'] if rank else 0,
                deviation=rank['deviation'] if rank else 0,
                last_update=rank['last_update'] if rank and 'last_update' in rank else datetime.now(timezone.utc),
            ),
            _stats=PlayerStats(
                games_played=stats['games_played'] if stats else 0,
                wins=stats['wins'] if stats else 0,
                losses=stats['losses'] if stats else 0,
                draws=stats['draws'] if stats else 0,
                win_rate=stats['win_rate'] if stats else 0,
                streak=stats['streak'] if stats else 0,
            ),
        )