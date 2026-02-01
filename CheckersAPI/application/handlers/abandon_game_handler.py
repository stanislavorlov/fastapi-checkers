import logging
from typing import Optional
from domain.game.game_mode import GameMode
from domain.player.player_type import PlayerType
from infrastructure.repositories.game_repository import GameRepository
from application.handlers.base_handler import RequestHandler
from application.requests.abandon_game import AbandonGameRequest

logger = logging.getLogger(__name__)

class AbandonGameHandler(RequestHandler[AbandonGameRequest, bool]):
    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository

    async def handle(self, request: AbandonGameRequest) -> bool:
        game_id = request.game_id
        player_id = request.player_id
        game = self.game_repository.fetch(game_id)
        if not game:
            logger.warning(f"Attempted to abandon non-existent game {game_id}")
            return False

        if game.finished_at:
            logger.info(f"Game {game_id} is already finished")
            return True

        # Check if the player is part of the game
        players_in_game = [str(p.id) for p in game.players.values()]
        if player_id not in players_in_game:
            logger.warning(f"Player {player_id} attempted to abandon game {game_id} they are not part of")
            return False

        # If it's a computer game, find the AI player and make it the winner
        if game.mode == GameMode.PVE:
            ai_player_id = None
            for p_side, p in game.players.items():
                if p.type_ == PlayerType.AI:
                    ai_player_id = str(p.id)
                    break
            
            if ai_player_id:
                game.finish_game(winner_id=ai_player_id, reason="Player abandoned the game")
                self.game_repository.save(game)
                logger.info(f"Game {game_id} marked as abandoned. AI winner: {ai_player_id}")
                return True

        # For online games, abandonment might need different logic (e.g. timeout or explicit surrender)
        # For now, we only implement the requirement for computer games.
        
        return False
