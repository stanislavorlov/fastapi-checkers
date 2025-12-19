import pytest
from bson import ObjectId
from infrastructure.documents import HistorySchema, GameSchema, GamePlayerSchema, GameMode, PlayerColor
from infrastructure.mappers import individual_history

def test_history_schema_validation():
    game_id = ObjectId()
    data = {
        "game_id": game_id,
        "player_id": "player1",
        "move": "11-15",
        "captures": [],
        "sequence": 1
    }
    schema = HistorySchema(**data)
    assert schema.game_id == game_id
    assert schema.player_id == "player1"
    assert schema.move == "11-15"

def test_individual_history_mapper():
    game_id = ObjectId()
    schema = HistorySchema(
        game_id=game_id,
        player_id="player1",
        move="11-15",
        captures=[],
        sequence=1
    )
    dto = individual_history(schema)
    assert dto.player_id == "player1"
    assert dto.move == "11-15"
    assert dto.sequence == 1

def test_game_schema_defaults():
    player1 = GamePlayerSchema(
        player_id=ObjectId(),
        color=PlayerColor.WHITE
    )
    player2 = GamePlayerSchema(
        player_id=ObjectId(),
        color=PlayerColor.BLACK
    )
    
    schema = GameSchema(
        mode=GameMode.PVP,
        players=[player1, player2]
    )
    
    assert isinstance(schema.id, ObjectId)
    assert schema.created_at is not None
    assert schema.result is None
