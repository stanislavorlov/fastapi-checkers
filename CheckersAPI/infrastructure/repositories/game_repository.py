import json
from typing import Optional
from bson import ObjectId
import domain.player.player_type
from domain.game.game import Game
from domain.game.game_mode import GameMode
from domain.game.game_result import GameResult
from domain.history_entry import HistoryEntry
from domain.player.player import Player
from domain.player.display_name import DisplayName
from domain.player.rank import Rank
from domain.player.stats import PlayerStats
from domain.side import Side
from infrastructure import documents
from infrastructure.documents import GameSchema, GamePlayerSchema, PyObjectId
from infrastructure.mongo_context import MongoContext
from infrastructure.repositories.player_repository import PlayerRepository


class GameRepository:

    def __init__(self, db: MongoContext, player_repository: Optional[PlayerRepository] = None):
        self.db = db
        self.player_repository = player_repository

    def create(self, game: Game):
        players_schemas = []
        for side, player in game.players.items():
            # Map Side domain enum to PlayerColor schema enum
            color = documents.PlayerColor.BLACK if side == Side.Dark else documents.PlayerColor.WHITE
            
            players_schemas.append(GamePlayerSchema(
                player_id=ObjectId(player.id),
                color=color,
                snapshot={
                    "display_name": str(player.display_name.value) if player.display_name else "Unknown",
                    "type": player.type_.value
                }
            ))

        game_schema = GameSchema(
            created_at=game.created_at,
            started_at=game.started_at,
            mode=documents.GameMode(game.mode.value),
            players=players_schemas,
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

    def save(self, game: Game):
        update_data = {
            "finished_at": game.finished_at,
            "result": game.result
        }
        
        # If the game is finished, archive the history and clear the individual history documents
        if game.finished_at:
            archived_history = json.dumps([h.model_dump() for h in game.history])
            update_data["archived_history"] = archived_history
            
            # Delete from history collection
            self.db.history.delete_many({"game_id": ObjectId(game.id or game.id_)})

        self.db.games.update_one({"_id": ObjectId(game.id or game.id_)}, {"$set": update_data})

    def fetch(self, game_id: str) -> Optional[Game]:
        game_document = self.db.games.find_one({"_id": ObjectId(game_id)})
        
        if not game_document:
            return None
            
        cursor = self.db.history.find({"game_id": ObjectId(game_id)}).sort("sequence", 1)

        result_doc = game_document.get("result") or {}
        game_result = GameResult(
            winner=PyObjectId(result_doc.get("winner")) if result_doc.get("winner") else None,
            reason=result_doc.get("reason")
        )
        
        game_players: dict[Side, Player] = {}
        for p in game_document.get("players", []):
            side = Side.Dark if p["color"] == "black" else Side.Light
            player_id = str(p["player_id"])
            
            # If we have a repository, fetch the full player. 
            # Otherwise, use snapshot to recreate a basic player if needed (but prefer full lookup)
            if self.player_repository:
                player = self.player_repository.get_by_id(player_id)
                if player:
                    game_players[side] = player
                    continue
            
            # Fallback: create a basic player from snapshot if repository is missing or player not found
            # This ensures the game object is still functional even without repository ref

            snapshot = p.get("snapshot", {})
            game_players[side] = Player(
                _id=ObjectId(player_id),
                display_name=DisplayName(display_name=snapshot.get("display_name", "Unknown")),
                _type=domain.player.player_type.PlayerType(snapshot.get("type", "guest")),
                _rank=Rank.intermediate(),
                _stats=PlayerStats.create_empty()
            )

        game_history: list[HistoryEntry] = []
        archived_raw = game_document.get("archived_history")
        
        if archived_raw:
            history_data = json.loads(archived_raw)
            game_history = [HistoryEntry(**h) for h in history_data]
        else:
            for document in cursor:
                # Map 'pdn_string' from document or fallback to 'move'
                pdn = document.get('pdn_string') or document.get('move', '')
                
                # Explicitly create domain HistoryEntry with string player_id 
                # and only the fields the domain model expects.
                entry = HistoryEntry(
                    player_id=str(document["player_id"]),
                    pdn_string=pdn,
                    sequence=document["sequence"],
                    captures=document.get("captures", [])
                )
                game_history.append(entry)

        return Game(
            _id=game_document["_id"],
            created_at=game_document["created_at"],
            started_at=game_document["started_at"],
            finished_at=game_document["finished_at"],
            mode=GameMode(game_document["mode"]),
            result=game_result.to_dict(),
            players=game_players,
            history=game_history
        )
