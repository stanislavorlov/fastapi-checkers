from fastapi import Depends
from application.handlers.create_player_handler import CreatePlayerHandler
from application.handlers.game_event_handler import GameEventHandler
from application.handlers.register_profile_handler import RegisterProfileHandler
from application.handlers.retrieve_token_handler import RetrieveTokenHandler
from infrastructure.event_parser import EventParser
from infrastructure.mongo_context import MongoContext
from infrastructure.repositories.game_repository import GameRepository
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.repositories.session_token_repository import SessionRepository
from infrastructure.runtime import connection_manager as manager

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

def get_game_repository(
        db = Depends(get_mongo_context),
):
    game_repository = GameRepository(db)

    return game_repository

def get_session_repository(
        db = Depends(get_mongo_context),
):
    session_repository = SessionRepository(db)

    return session_repository

def get_register_profile_handler(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)

    return RegisterProfileHandler(profile_repository)

def get_retrieve_token_handler(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)
    session_repository = SessionRepository(db)

    return RetrieveTokenHandler(profile_repository, session_repository)

def get_guest_token_handler(
        db = Depends(get_mongo_context),
):
    pass

def get_game_event_handler(
        db = Depends(get_mongo_context),
):
    game_repository = GameRepository(db)

    return GameEventHandler(game_repository, manager)

def get_create_player_handler(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)
    player_repository = PlayerRepository(db)

    return CreatePlayerHandler(profile_repository, player_repository)