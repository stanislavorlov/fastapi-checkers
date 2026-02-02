from typing import List, Optional
from infrastructure.mongo_context import MongoContext
from domain.game.game import Game


class HistoryRepository:

    def __init__(self, db: MongoContext, game_repo):
        self.db = db
        self.game_repo = game_repo

    async def fetch_archived_games(self, player_id: str) -> List[Game]:
        from bson import ObjectId
        oid = ObjectId(player_id)
        
        # Query games where one of the players has the given player_id and game is finished
        cursor = self.db.games.find({
            "players.player_id": oid,
            "finished_at": {"$ne": None}
        }).sort("created_at", -1)
        
        games = []
        for doc in cursor:
            game = self.game_repo.map_to_domain(doc)
            if game:
                games.append(game)
        return games

    async def get_by_id(self, game_id: str) -> Optional[Game]:
        from bson import ObjectId
        doc = self.db.games.find_one({"_id": ObjectId(game_id)})
        return self.game_repo.map_to_domain(doc)