from typing import List, Mapping
from pymongo.synchronous.cursor import Cursor
from infrastructure.documents import Game, History, Player
from web.models import ReadGameDto, HistoryDto


def individual_game(game : Game, history_cursor: Cursor[Mapping[str, History]]) -> ReadGameDto:
    return ReadGameDto(
        name=game['name'],
        started=game['started'],
        mode=game['mode'],
        game_id=str(game['_id']),
        light_player=game['light_player'],
        dark_player=game['dark_player'],
        history=list_histories(history_cursor)
    )

def single_player(player: Player) -> dict:
    return {
        "player_id": player['player_id'],
        "username": player['username'],
        "first_name": player['first_name'],
        "last_name": player['last_name'],
        "country": player['country'],
    }

def list_games(games : List[Game]) -> list[ReadGameDto]:
    return [individual_game(game, []) for game in games]

def individual_history(history: History) -> HistoryDto:
    return HistoryDto(
        player_id=history.player_id,
        move=history['move'],
        sequence=history['sequence'],
        captures=history['captures'],
    )

def list_histories(histories : List[History]) -> list[HistoryDto]:
    history_dtos : list[HistoryDto] = []
    for history in histories:
        history_dtos.append(individual_history(history))

    return history_dtos