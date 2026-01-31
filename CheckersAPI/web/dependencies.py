from fastapi import Depends
from application.handlers.create_player_handler import CreatePlayerHandler
from application.handlers.game_event_handler import GameEventHandler
from application.handlers.register_profile_handler import RegisterProfileHandler
from application.handlers.retrieve_token_handler import RetrieveTokenHandler
from application.handlers.resolve_guest_player_handler import ResolveGuestPlayerHandler
from infrastructure.event_parser import EventParser
from infrastructure.mongo_context import MongoContext
from infrastructure.repositories.game_repository import GameRepository
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.repositories.session_token_repository import SessionRepository
from infrastructure.repositories.matching_repository import MatchingRepository
from infrastructure.runtime import connection_manager as manager
from application.handlers.resolve_player_handler import ResolvePlayerHandler
from application.handlers.start_computer_game_handler import StartComputerGameHandler
from application.handlers.join_queue_handler import JoinQueueHandler
from application.handlers.abandon_game_handler import AbandonGameHandler

# created once at startup
mongo_context = MongoContext()

def get_mongo_context() -> MongoContext:
    return mongo_context

def get_event_parser():
    return EventParser()

def get_profile_repository(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)

    return profile_repository

def get_player_repository(
        db = Depends(get_mongo_context),
):
    player_repository = PlayerRepository(db)

    return player_repository

def get_game_repository(
        db = Depends(get_mongo_context),
        player_repository = Depends(get_player_repository),
):
    game_repository = GameRepository(db, player_repository)

    return game_repository

def get_session_repository(
        db = Depends(get_mongo_context),
):
    session_repository = SessionRepository(db)

    return session_repository

def get_matching_repository(
        db = Depends(get_mongo_context),
):
    return MatchingRepository(db)

def get_register_profile_handler(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)

    return RegisterProfileHandler(profile_repository)

def get_resolve_guest_player_handler(
        db = Depends(get_mongo_context),
):
    session_repository = SessionRepository(db)
    profile_repository = ProfileRepository(db)
    player_repository = PlayerRepository(db)
    create_player_handler = CreatePlayerHandler(profile_repository, player_repository)

    return ResolveGuestPlayerHandler(session_repository, create_player_handler)

def get_retrieve_token_handler(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)
    session_repository = SessionRepository(db)
    player_repository = PlayerRepository(db)
    create_player_handler = CreatePlayerHandler(profile_repository, player_repository)
    resolve_guest_player_handler = ResolveGuestPlayerHandler(session_repository, create_player_handler)

    return RetrieveTokenHandler(
        profile_repository,
        session_repository,
        player_repository,
        create_player_handler,
        resolve_guest_player_handler
    )

def get_game_event_handler(
        game_repository = Depends(get_game_repository),
):
    return GameEventHandler(game_repository, manager)

def get_create_player_handler(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)
    player_repository = PlayerRepository(db)

    return CreatePlayerHandler(profile_repository, player_repository)

def get_resolve_player_handler(
        player_handler = Depends(get_create_player_handler),
        resolve_guest_player_handler = Depends(get_resolve_guest_player_handler)
) -> ResolvePlayerHandler:
    return ResolvePlayerHandler(player_handler, resolve_guest_player_handler)

def get_start_computer_game_handler(
        game_repository = Depends(get_game_repository),
        player_repository = Depends(get_player_repository),
        game_event_handler = Depends(get_game_event_handler)
) -> StartComputerGameHandler:
    return StartComputerGameHandler(game_repository, player_repository, game_event_handler)

def get_join_queue_handler(
        matching_repository = Depends(get_matching_repository)
) -> JoinQueueHandler:
    return JoinQueueHandler(matching_repository)

def get_abandon_game_handler(
        game_repository = Depends(get_game_repository)
) -> AbandonGameHandler:
    return AbandonGameHandler(game_repository)