import json
import logging
from domain.board.board import Board
from domain.game.game import Game
from domain.history_entry import HistoryEntry
from domain.player.player_type import PlayerType
from domain.side import Side
from domain.game.game_mode import GameMode
from application.alpha_zero_predictor import AlphaZeroPredictor
from application.handlers.base_handler import RequestHandler
from application.requests.move import MoveRequest
from infrastructure.connnection_manager import ConnectionManager
from infrastructure.event_parser import EventParser
from infrastructure.repositories.game_repository import GameRepository

logger = logging.getLogger(__name__)

class MoveHandler(RequestHandler[MoveRequest, None]):
    def __init__(
        self, 
        game_repository: GameRepository, 
        manager: ConnectionManager, 
        parser: EventParser
    ):
        self.game_repository = game_repository
        self.manager = manager
        self.parser = parser

    async def handle(self, request: MoveRequest):
        game_id = request.game_id
        player_id = request.player_id
        data = request.data
        
        logger.info(f'Move handler called for game {game_id} by player {player_id}')

        player, pdn_move = self.parser.parse(data)
        
        game = self.game_repository.fetch(game_id)
        if not game:
            logger.error(f"Game {game_id} not found")
            return

        board = Board.from_history(game.history)

        logger.debug(f"Applying move: {pdn_move.as_string}")

        if board.apply_move(pdn_move):
            history = HistoryEntry(
                player_id=player, # Using player from parsed data (JSON)
                pdn_string=pdn_move.as_string,
                captures=pdn_move.captured_squares,
                sequence=len(game.history),
            )

            self.game_repository.append_history(game_id, history)
            game.history.append(history)

            response = pdn_move.to_dict()
            response['player_id'] = player
            response['player_color'] = Side.Dark.value if str(game.players[Side.Dark].id) == player else Side.Light.value

            await self.manager.broadcast(game_id, json.dumps(response))

            if board.is_game_over():
                winner_side = board.get_winner()
                winner_player = game.players.get(winner_side) if winner_side else None
                game.finish_game(str(winner_player.id) if winner_player else None, "Game over")
                self.game_repository.save(game)
                
                over_response = {
                    "type": "game_over",
                    "winner_id": str(winner_player.id) if winner_player else None,
                    "winner_side": winner_side.value if winner_side else None,
                    "reason": "Game over"
                }
                await self.manager.broadcast(game_id, json.dumps(over_response))
                return

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
            
        board = Board.from_history(game.history)
        if board.is_game_over():
            logger.error(f"Game has ended")
            return

        ai_side = board.turn
        ai_player = game.players.get(ai_side)

        logger.debug(f"Player {ai_player.display_name}. Board turn {board.turn}")

        if ai_player and ai_player.type_ == PlayerType.AI:
            logger.info(f"AI's turn ({ai_side}). Predicting move with AlphaZero (MCTS)...")
            
            predictor = AlphaZeroPredictor()
            ai_pdn = predictor.predict(board, num_simulations=100) # Balanced simulation count
            
            if ai_pdn:
                logger.info(f"AI predicted move: {ai_pdn.as_string}")
                if board.apply_move(ai_pdn):
                    logger.debug("applying predicted move")
                    ai_history = HistoryEntry(
                        player_id=str(ai_player.id),
                        pdn_string=ai_pdn.as_string,
                        captures=ai_pdn.captured_squares,
                        sequence=len(game.history),
                    )
                    self.game_repository.append_history(game.id, ai_history)
                    game.history.append(ai_history)
                    
                    ai_response = ai_pdn.to_dict()
                    ai_response['player_id'] = str(ai_player.id)
                    ai_response['player_color'] = ai_side.value
                    await self.manager.broadcast(game.id, json.dumps(ai_response))

                    if board.is_game_over():
                        winner_side = board.get_winner()
                        winner_player = game.players.get(winner_side) if winner_side else None
                        game.finish_game(str(winner_player.id) if winner_player else None, "Game over")
                        self.game_repository.save(game)

                        over_response = {
                            "type": "game_over",
                            "winner_id": str(winner_player.id) if winner_player else None,
                            "winner_side": winner_side.value if winner_side else None,
                            "reason": "Game over"
                        }
                        await self.manager.broadcast(game.id, json.dumps(over_response))
                else:
                    logger.error("AI predicted an illegal move!")
            else:
                logger.warning("AI could not predict a valid move.")
