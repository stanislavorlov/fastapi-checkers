from typing import List, Mapping
from pymongo.synchronous.cursor import Cursor
from infrastructure.documents import Game, History
from web.game_dto import ReadGameDto
from web.history_dto import HistoryDto


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

def list_games(games : List[Game]) -> list[ReadGameDto]:
    return [individual_game(game, []) for game in games]

def individual_history(history: History) -> HistoryDto:
    return HistoryDto(
        player_id=history.player_id,
        event_type=history['event_type'],
        from_=int(history['from_']),
        to=int(history['to']),
        sequence=history['sequence'],
    )

def list_histories(histories : List[History]) -> list[HistoryDto]:
    history_dtos : list[HistoryDto] = []
    for history in histories:
        history_dtos.append(individual_history(history))

    return history_dtos