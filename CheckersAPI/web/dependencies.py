from fastapi import Depends
from application.handlers.game_event_handler import GameEventHandler
from application.handlers.register_profile_handler import RegisterProfileHandler
from application.handlers.retrieve_token_handler import RetrieveTokenHandler
from infrastructure.event_parser import EventParser
from infrastructure.mongo_context import MongoContext
from infrastructure.repositories.game_repository import GameRepository
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.runtime import connection_manager as manager

# created once at startup
mongo_context = MongoContext()

def get_mongo_context() -> MongoContext:
    return mongo_context

def get_register_profile_handler(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)

    return RegisterProfileHandler(profile_repository)

def get_retrieve_token_handler(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)

    return RetrieveTokenHandler(profile_repository)

def get_event_parser():
    return EventParser()

def get_game_event_handler(
        db = Depends(get_mongo_context),
):
    game_repository = GameRepository(db)

    return GameEventHandler(game_repository, manager)

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