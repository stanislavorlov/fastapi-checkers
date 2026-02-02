from typing import List
from domain.game.game import Game
from domain.side import Side
from infrastructure.documents import HistorySchema
from web.models import ReadGameDto, HistoryDto, PlayerUserDto


def individual_game(game: Game) -> ReadGameDto:
    # Use side assignment from domain dictionary
    light_player = game.players.get(Side.Light)
    dark_player = game.players.get(Side.Dark)
    
    return ReadGameDto(
        game_id=str(game.id),
        name="Checkers Game", # Or get from domain if added
        started=game.started_at or game.created_at, # Fallback to created_at
        mode=game.mode.value,
        light_player=str(light_player.id) if light_player else "",
        dark_player=str(dark_player.id) if dark_player else "",
        history=list_histories(game.history),
        finished_at=game.finished_at,
        result=game.result
    )

def list_games(games: List[Game]) -> List[ReadGameDto]:
    game_dtos : list[ReadGameDto] = []
    for game in games:
        game_dtos.append(individual_game(game))

    return game_dtos

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