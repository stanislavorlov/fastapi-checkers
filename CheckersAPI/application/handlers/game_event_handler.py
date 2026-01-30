import json
import logging
from domain.board.board import Board
from domain.game.game import Game
from domain.history_entry import HistoryEntry
from domain.pdn_move import PdnMove
from domain.player.player_type import PlayerType
from infrastructure.connnection_manager import ConnectionManager
from infrastructure.repositories.game_repository import GameRepository
from domain.game.game_mode import GameMode
from domain.side import Side
from infrastructure.ai.move_predictor import AiMovePredictor

logger = logging.getLogger(__name__)

class GameEventHandler:

    def __init__(self, game_repository: GameRepository, manager: ConnectionManager):
        self.manager = manager
        self.game_repository = game_repository

    async def handle(self, game_id: str, player_id: str, pdn_move: PdnMove):
        logger.info(f'Event handler called -> handle for game {game_id}')

        game = self.game_repository.fetch(game_id)
        if not game:
            logger.error(f"Game {game_id} not found")
            return

        logger.debug(f'Found history {game.history}')

        board = Board.from_history(game.history)

        board.display_squares()

        logger.debug(f"Applying move: {pdn_move.as_string}")

        if board.apply_move(pdn_move):
            history = HistoryEntry(
                player_id=player_id,
                pdn_string=pdn_move.as_string,
                captures=pdn_move.captured_squares,
                sequence=len(game.history),
            )

            self.game_repository.append_history(game_id, history)
            game.history.append(history)

            response = pdn_move.to_dict()
            response['player_id'] = player_id

            await self.manager.broadcast(game_id, json.dumps(response))

            # Trigger AI move if it's a PVE game and it's AI's turn
            await self.trigger_ai_move(game)

    async def trigger_ai_move(self, game: Game):
        logger.debug(f'Trigger AI move for game {game.id}')

        if not game:
            logger.error(f"Game not found")
            return

        if game.mode != GameMode.PVE:
            logger.error(f"Game does not have PVE mode")
            return

        logger.debug(f"Board history {game.history}")

        board = Board.from_history(game.history)
        if board.is_game_over():
            logger.error(f"Game has ended")
            return

        ai_side = board.turn
        ai_player = game.players.get(ai_side)

        logger.debug(ai_player)

        logger.debug(f"Player {ai_player.display_name}. Board turn {board.turn}")

        if ai_player and ai_player.type_ == PlayerType.AI:
            logger.info(f"AI's turn ({ai_side}). Predicting move...")
            
            predictor = AiMovePredictor()
            ai_pdn = predictor.predict(board)
            
            if ai_pdn:
                logger.info(f"AI predicted move: {ai_pdn.as_string}")
                board.display_squares()
                if board.apply_move(ai_pdn):
                    logger.debug("applying predicted move")
                    ai_history = HistoryEntry(
                        player_id=str(ai_player.id),
                        pdn_string=ai_pdn.as_string,
                        captures=ai_pdn.captured_squares,
                        sequence=len(game.history), # sequence is 0-based index in domain HistoryEntry
                    )
                    self.game_repository.append_history(game.id, ai_history)
                    game.history.append(ai_history)
                    
                    ai_response = ai_pdn.to_dict()
                    ai_response['player_id'] = str(ai_player.id)
                    await self.manager.broadcast(game.id, json.dumps(ai_response))
                else:
                    logger.error("AI predicted an illegal move!")
            else:
                logger.warning("AI could not predict a valid move.")