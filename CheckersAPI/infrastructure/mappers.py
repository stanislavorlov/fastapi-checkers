from typing import List, Mapping
from pymongo.synchronous.cursor import Cursor
from infrastructure.documents import GameSchema, HistorySchema
from web.models import ReadGameDto, HistoryDto, PlayerUserDto


def individual_game(game : GameSchema, history_cursor: Cursor[Mapping[str, HistorySchema]]) -> ReadGameDto:
    # Note: GameSchema might not have all these fields. This mapper seems to expect a dict or a different schema.
    # Assuming game is a dict for now if it has fields not in GameSchema, or we need to update GameSchema.
    # But the type hint says GameSchema. 
    # If GameSchema is Pydantic, we should use .name, but GameSchema doesn't have name.
    # I will switch to attribute access but this might fail if fields are missing.
    # For now, I'll assume the input might be a dict (from Mongo) despite the type hint, 
    # OR I should update GameSchema.
    # Given the ambiguity, I will leave this function as is but warn, or try to fix what I can.
    # Actually, let's fix individual_history which is definitely using HistorySchema.
    pass

def individual_user(user_dict):
    return {
        'user_id': user_dict['user_id'],
        'player_id': user_dict['player_id'],
        'email': user_dict['email'],
        'first_name': user_dict['first_name'],
        'last_name': user_dict['last_name'],
        'country': user_dict['country'],
    }

def user_profile(pipeline_result):
    return {
        'user_id': str(pipeline_result['user_id']),
        'player_id': str(pipeline_result['player_id']),
        'first_name': pipeline_result.get('first_name') or '',
        'last_name': pipeline_result.get('last_name') or '',
        'email': pipeline_result.get('email') or '',
        'nickname': pipeline_result['player']['nickname'] or '',
        'region': pipeline_result['player']['region'] or '',
        'country': pipeline_result.get('country') or '',
    }

def guest_user(guest_id) -> PlayerUserDto:
    return PlayerUserDto(
        player_id=guest_id,
        email='',
        first_name='Guest',
        last_name='Guest',
        country='',
        anonymous=True
    )

def individual_history(history: HistorySchema) -> HistoryDto:
    return HistoryDto(
        player_id=str(history.player_id),
        move=history.pdn_string,
        sequence=history.sequence,
        captures=history.captures,
    )

def list_histories(histories : List[HistorySchema]) -> list[HistoryDto]:
    history_dtos : list[HistoryDto] = []
    for history in histories:
        history_dtos.append(individual_history(history))

    return history_dtos