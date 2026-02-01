from fastapi import Depends

from application.requests.update_profile import UpdateProfileRequest
from application.handlers.update_profile_handler import UpdateProfileHandler
from application.handlers.create_player_handler import CreatePlayerHandler
from application.handlers.register_profile_handler import RegisterProfileHandler
from application.handlers.retrieve_token_handler import RetrieveTokenHandler
from application.handlers.resolve_guest_player_handler import ResolveGuestPlayerHandler
from infrastructure.event_parser import EventParser
from infrastructure.mongo_context import MongoContext
from infrastructure.repositories.game_repository import GameRepository
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.repositories.matching_repository import MatchingRepository
from infrastructure.runtime import connection_manager as manager
from application.handlers.resolve_player_handler import ResolvePlayerHandler
from application.handlers.start_computer_game_handler import StartComputerGameHandler
from application.handlers.join_queue_handler import JoinQueueHandler
from application.handlers.abandon_game_handler import AbandonGameHandler
from application.handlers.websocket.dispatcher import WebSocketDispatcher
from application.handlers.websocket.move_handler import MoveHandler
from application.mediator import Mediator
from application.requests.create_player import CreatePlayerRequest
from application.requests.retrieve_token import RetrieveToken, RetrieveGuestToken, RetrieveProfileToken
from application.requests.register_profile import RegisterProfileRequest
from application.requests.resolve_guest_player import ResolveGuestPlayerRequest
from application.requests.resolve_player import ResolvePlayerRequest
from application.requests.start_computer_game import StartComputerGameRequest
from application.requests.join_queue import JoinQueueRequest
from application.requests.abandon_game import AbandonGameRequest
from application.requests.move import MoveRequest

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
    profile_repository = ProfileRepository(db)
    player_repository = PlayerRepository(db)
    create_player_handler = CreatePlayerHandler(profile_repository, player_repository)

    return ResolveGuestPlayerHandler(player_repository, create_player_handler)

def get_retrieve_token_handler(
        db = Depends(get_mongo_context),
):
    profile_repository = ProfileRepository(db)
    player_repository = PlayerRepository(db)
    create_player_handler = CreatePlayerHandler(profile_repository, player_repository)
    resolve_guest_player_handler = ResolveGuestPlayerHandler(player_repository, create_player_handler)

    return RetrieveTokenHandler(
        profile_repository,
        player_repository,
        create_player_handler,
        resolve_guest_player_handler
    )

def get_move_handler(
        game_repository = Depends(get_game_repository),
        event_parser = Depends(get_event_parser)
) -> MoveHandler:
    return MoveHandler(game_repository, manager, event_parser)

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
        move_handler = Depends(get_move_handler)
) -> StartComputerGameHandler:
    return StartComputerGameHandler(game_repository, player_repository, move_handler)

def get_join_queue_handler(
        matching_repository = Depends(get_matching_repository)
) -> JoinQueueHandler:
    return JoinQueueHandler(matching_repository)

def get_abandon_game_handler(
        game_repository = Depends(get_game_repository)
) -> AbandonGameHandler:
    return AbandonGameHandler(game_repository)

def get_update_profile_handler(
        db = Depends(get_mongo_context),
        player_repository: PlayerRepository = Depends(get_player_repository)
) -> UpdateProfileHandler:
    profile_repository = ProfileRepository(db)
    return UpdateProfileHandler(profile_repository, player_repository)

def get_mediator(
    create_player_handler = Depends(get_create_player_handler),
    register_profile_handler = Depends(get_register_profile_handler),
    retrieve_token_handler = Depends(get_retrieve_token_handler),
    resolve_guest_player_handler = Depends(get_resolve_guest_player_handler),
    resolve_player_handler = Depends(get_resolve_player_handler),
    start_computer_game_handler = Depends(get_start_computer_game_handler),
    join_queue_handler = Depends(get_join_queue_handler),
    abandon_game_handler = Depends(get_abandon_game_handler),
    move_handler = Depends(get_move_handler),
    update_profile_handler = Depends(get_update_profile_handler)
) -> Mediator:
    mediator = Mediator()
    mediator.register(CreatePlayerRequest, create_player_handler)
    mediator.register(RegisterProfileRequest, register_profile_handler)
    mediator.register(RetrieveToken, retrieve_token_handler)
    mediator.register(RetrieveGuestToken, retrieve_token_handler)
    mediator.register(RetrieveProfileToken, retrieve_token_handler)
    mediator.register(ResolveGuestPlayerRequest, resolve_guest_player_handler)
    mediator.register(ResolvePlayerRequest, resolve_player_handler)
    mediator.register(StartComputerGameRequest, start_computer_game_handler)
    mediator.register(JoinQueueRequest, join_queue_handler)
    mediator.register(AbandonGameRequest, abandon_game_handler)
    mediator.register(MoveRequest, move_handler)
    mediator.register(UpdateProfileRequest, update_profile_handler)
    return mediator

def get_websocket_dispatcher(
        mediator = Depends(get_mediator)
) -> WebSocketDispatcher:
    dispatcher = WebSocketDispatcher(mediator)
    return dispatcher