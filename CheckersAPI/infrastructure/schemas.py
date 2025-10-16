from typing import List, Mapping
from pymongo.synchronous.cursor import Cursor
from infrastructure.documents import GameSchema, HistorySchema, UserSchema
from web.models import ReadGameDto, HistoryDto, PlayerUserDto


def individual_game(game : GameSchema, history_cursor: Cursor[Mapping[str, HistorySchema]]) -> ReadGameDto:
    return ReadGameDto(
        name=game['name'],
        started=game['started'],
        mode=game['mode'],
        game_id=str(game['_id']),
        light_player=game['light_player'],
        dark_player=game['dark_player'],
        history=list_histories(history_cursor)
    )

def single_user(player: UserSchema) -> PlayerUserDto:
    return PlayerUserDto(
        player_id=player['player_id'],
        email=player['email'],
        first_name=player.get('first_name') or '',
        last_name=player.get('last_name') or '',
        country=player.get('country') or '',
        anonymous=False
    )

def guest_user(guest_id) -> PlayerUserDto:
    return PlayerUserDto(
        player_id=guest_id,
        email='',
        first_name='Guest',
        last_name='Guest',
        country='',
        anonymous=True
    )

def list_games(games : List[GameSchema]) -> list[ReadGameDto]:
    return [individual_game(game, []) for game in games]

def individual_history(history: HistorySchema) -> HistoryDto:
    return HistoryDto(
        player_id=history.player_id,
        move=history['move'],
        sequence=history['sequence'],
        captures=history['captures'],
    )

def list_histories(histories : List[HistorySchema]) -> list[HistoryDto]:
    history_dtos : list[HistoryDto] = []
    for history in histories:
        history_dtos.append(individual_history(history))

    return history_dtos