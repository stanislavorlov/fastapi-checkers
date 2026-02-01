import logging
from datetime import datetime, timezone
from domain.player.player import Player
from domain.player.player_type import PlayerType as DomainPlayerType
from domain.player.display_name import DisplayName
from domain.player.rank import Rank
from domain.player.stats import PlayerStats
from domain.game.game import Game
from domain.game.game_mode import GameMode
from domain.side import Side
from infrastructure.repositories.game_repository import GameRepository
from infrastructure.repositories.player_repository import PlayerRepository
from application.handlers.websocket.move_handler import MoveHandler
from infrastructure.documents import PyObjectId

from application.handlers.base_handler import RequestHandler
from application.requests.start_computer_game import StartComputerGameRequest

logger = logging.getLogger(__name__)

class StartComputerGameHandler(RequestHandler[StartComputerGameRequest, str]):
    def __init__(
        self,
        game_repository: GameRepository,
        player_repository: PlayerRepository,
        move_handler: MoveHandler
    ):
        self.game_repository = game_repository
        self.player_repository = player_repository
        self.move_handler = move_handler

    async def handle(self, request: StartComputerGameRequest) -> str:
        player_id = request.player_id
        single_side = request.single_side
        player = self.player_repository.get_by_id(player_id)
        
        # Create AI bot player object
        ai_bot = Player(
            display_name=DisplayName(display_name="AI Bot"),
            _type=DomainPlayerType.AI,
            _rank=Rank.intermediate(),
            _stats=PlayerStats.create_empty()
        )
        
        player_side = Side.Light if single_side == "red" else Side.Dark
        ai_side = Side.Dark if player_side == Side.Light else Side.Light

        new_game = Game(
            created_at=datetime.now(timezone.utc),
            mode=GameMode.PVE,
            players={
                Side.Light : ai_bot if ai_side == Side.Light else player,
                Side.Dark : ai_bot if ai_side == Side.Dark else player
            },
            history=[],
            result={}
        )

        new_game.start()
        
        game_id = self.game_repository.create(new_game)
        
        # Set the ID on the domain object so trigger_ai_move can use it
        new_game.id = PyObjectId(game_id)
        
        # Trigger AI move immediately on creation
        await self.move_handler.trigger_ai_move(new_game)
        
        return str(game_id)
