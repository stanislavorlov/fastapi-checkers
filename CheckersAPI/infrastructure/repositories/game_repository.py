from typing import Optional
from bson import ObjectId
from domain.game.game import Game
from domain.game.game_mode import GameMode
from domain.game.game_result import GameResult
from domain.history_entry import HistoryEntry
from domain.player.player import Player
from domain.side import Side
from infrastructure import documents
from infrastructure.documents import GameSchema, GamePlayerSchema
from infrastructure.mongo_context import MongoContext


class GameRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    async def create(self, game: Game):
        game_mode_schema = documents.GameMode.PVE

        player1 = GamePlayerSchema(
            snapshot={"display_name": "", "type": "account"},
            player_id='',
            color=''
        )

        player2 = GamePlayerSchema(
            snapshot={"display_name": "", "type": "account"},
            player_id='',
            color=''
        )

        game_schema = GameSchema(
            created_at=game.created_at,
            started_at=game.started_at,
            mode=game_mode_schema,
            players=[player1, player2],
        )

        result = await self.db.games.insert_one(game_schema.model_dump(by_alias=True))

        return result.inserted_id

    async def append_history(self, game_id: str, history: HistoryEntry):
        await self.db.history.insert_one({
            "game_id": game_id,
            "player_id": history.player_id,
            "move": history.move,
            "captures": history.captures,
            "sequence": history.sequence,
        })

    async def fetch(self, game_id: str) -> Optional[Game]:
        game_document = await self.db.games.find_one({"_id": ObjectId(game_id)})
        cursor = self.db.history.find({"game_id": ObjectId(game_id)}).sort("sequence", 1)

        game_result = GameResult()
        game_players: dict[Side, Player] = {}
        game_history: list[HistoryEntry] = []

        async for document in cursor:
            entry = HistoryEntry(**document)
            game_history.append(entry)

        return Game(
            _id=game_document["_id"],
            created_at=game_document["created_at"],
            started_at=game_document["started_at"],
            finished_at=game_document["finished_at"],
            mode=GameMode(game_document["mode"]),
            result=game_result,
            players=game_players,
            history=game_history
        )