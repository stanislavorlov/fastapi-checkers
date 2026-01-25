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

    def create(self, game: Game):
        game_mode_schema = documents.GameMode.PVE

        # Note: In a real implementation, player IDs would come from the game object
        player1 = GamePlayerSchema(
            snapshot={"display_name": "", "type": "account"},
            player_id=ObjectId(), # Placeholder
            color='white'
        )

        player2 = GamePlayerSchema(
            snapshot={"display_name": "", "type": "account"},
            player_id=ObjectId(), # Placeholder
            color='black'
        )

        game_schema = GameSchema(
            created_at=game.created_at,
            started_at=game.started_at,
            mode=game_mode_schema,
            players=[player1, player2],
        )

        result = self.db.games.insert_one(game_schema.model_dump(mode='python', by_alias=True))

        return result.inserted_id

    def append_history(self, game_id: str, history: HistoryEntry):
        history_document = documents.HistorySchema(
            game_id=ObjectId(game_id),
            player_id=ObjectId(history.player_id),
            pdn_string=history.pdn_string,
            captures=history.captures or [],
            sequence=history.sequence
        )
        self.db.history.insert_one(history_document.model_dump(mode='python', by_alias=True))

    def fetch(self, game_id: str) -> Optional[Game]:
        game_document = self.db.games.find_one({"_id": ObjectId(game_id)})
        
        if not game_document:
            return None
            
        cursor = self.db.history.find({"game_id": ObjectId(game_id)}).sort("sequence", 1)

        game_result = GameResult()
        game_players: dict[Side, Player] = {}
        game_history: list[HistoryEntry] = []

        for document in cursor:
            # We need to map 'pdn_string' back from the document if it exists
            # HistoryEntry expects 'pdn_string', but we might have 'move' in old records
            if 'pdn_string' not in document and 'move' in document:
                document['pdn_string'] = document.pop('move')
                
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