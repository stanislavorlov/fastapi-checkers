import logging
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from domain.player.display_name import DisplayName
from domain.player.player import Player
from domain.player.rank import Rank
from domain.player.stats import PlayerStats
from domain.sessions.player_session import PlayerSession
from domain.sessions.region import Region
from infrastructure.documents import PlayerSchema, PlayerType, RankSchema, StatsSchema, SessionSchema
from infrastructure.mongo_context import MongoContext

logger = logging.getLogger(__name__)

class PlayerRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    def create(self, player: Player) -> str:
        # 1. Store Sessions in separate collection
        for s in player.sessions:
            session_doc = SessionSchema(
                player_id=player.id,
                token=s.token,
                host=s.host,
                agent=s.agent,
                region=s.region.code,
                timezone="UTC",
                expires_at=s.expires_at,
                created_at=s.created_at
            )
            self.db.sessions.insert_one(
                session_doc.model_dump(mode='python', by_alias=True)
            )

        # 2. Store Player
        player_document = PlayerSchema(
            _id=player.id,
            type=PlayerType(player.type_.value),
            display_name=player.display_name.value,
            profile_id=player.profile_id,
            created_at=player.created_at
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

    def save(self, player: Player) -> None:
        """Saves player state and ensures its sessions are in the standalone collection."""
        # 1. Update/Upsert sessions in separate collection
        for s in player.sessions:
            session_doc = SessionSchema(
                player_id=player.id,
                token=s.token,
                host=s.host,
                agent=s.agent,
                region=s.region.code,
                timezone="UTC",
                expires_at=s.expires_at,
                created_at=s.created_at
            )
            # Use token as unique identifier for upserting
            update_doc = session_doc.model_dump(mode='python', by_alias=True)
            update_doc.pop('_id', None)  # Ensure _id is not in the replacement doc

            self.db.sessions.replace_one(
                {"token": s.token},
                update_doc,
                upsert=True
            )

        # 2. Update Player
        player_document = PlayerSchema(
            _id=player.id,
            type=PlayerType(player.type_.value),
            display_name=player.display_name.value,
            profile_id=player.profile_id,
            created_at=player.created_at
        )

        update_doc = player_document.model_dump(mode='python', by_alias=True)
        update_doc.pop('_id', None)  # Ensure _id is not in the replacement doc

        self.db.players.replace_one(
            {"_id": player.id},
            update_doc
        )

    def _map_to_domain(self, doc: dict) -> Player:
        if not doc:
            return None
            
        rank = self.db.ranks.find_one({"player_id": doc["_id"]})
        stats = self.db.stats.find_one({"player_id": doc["_id"]})

        # Fetch sessions from STANDALONE collection
        session_docs = self.db.sessions.find({"player_id": doc["_id"]})
        sessions = []
        for s in session_docs:
            sessions.append(PlayerSession(
                player_id=doc["_id"],
                created_at=s.get("created_at") or datetime.now(timezone.utc),
                expires_at=s.get("expires_at") or datetime.now(timezone.utc),
                token=s["token"],
                host=s["host"],
                agent=s["agent"],
                region=Region(code=s["region"]),
                tz_offset=timedelta(0) # Default to UTC
            ))

        return Player(
            _id=doc["_id"],
            _type=PlayerType(doc["type"]),
            display_name=DisplayName(display_name=doc["display_name"]),
            profile_id=doc.get("profile_id"),
            sessions=sessions,
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
            created_at=doc.get("created_at") or datetime.now(timezone.utc)
        )

    def get_by_id(self, player_id: str | ObjectId) -> Player:
        oid = ObjectId(player_id) if isinstance(player_id, str) else player_id
        result = self.db.players.find_one({"_id": oid})
        return self._map_to_domain(result)

    def get_by_profile_id(self, profile_id: str | ObjectId) -> Player | None:
        oid = ObjectId(profile_id) if isinstance(profile_id, str) else profile_id
        result = self.db.players.find_one({"profile_id": oid})
        return self._map_to_domain(result)

    def find_recent_guest_session(self, host: str, agent: str, limit_hours: int = 24) -> str | None:
        """
        Finds a session for a given host and agent within the last limit_hours.
        Returns the player_id if found, else None.
        Querying the standalone sessions collection.
        """
        threshold = datetime.now(timezone.utc) - timedelta(hours=limit_hours)

        query = {
            "host": host,
            "agent": agent,
            "created_at": {"$gte": threshold}
        }

        # Find the NEWEST session for this host/agent
        newest_session = self.db.sessions.find_one(query, sort=[("created_at", -1)])
        
        if newest_session:
            return str(newest_session["player_id"])
                        
        return None

    def find_session_by_player_and_client(self, player_id: str | ObjectId, host: str, agent: str) -> str | None:
        """
        Finds an existing session token for a specific player and client device using the standalone collection.
        """
        oid = ObjectId(player_id) if isinstance(player_id, str) else player_id
        
        query = {
            "player_id": oid,
            "host": host,
            "agent": agent
        }
        
        # Return the newest one
        newest_session = self.db.sessions.find_one(query, sort=[("created_at", -1)])
        
        if newest_session:
            return newest_session["token"]
            
        return None