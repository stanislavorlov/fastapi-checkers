from application.monte_carlo_tree import MCTS
from application.neural_network import NeuralNetwork
from domain.board.board import Board
from domain.pdn_move import PdnMove
from domain.legal_move import CapturedMove
import logging

logger = logging.getLogger(__name__)

class AlphaZeroPredictor:
    """
    High-level predictor that uses MCTS and a Neural Network.
    """
    _instance = None
    _nn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlphaZeroPredictor, cls).__new__(cls)
            cls._instance._nn = NeuralNetwork()
        return cls._instance

    def predict(self, board: Board, num_simulations: int = 400) -> PdnMove:
        """
        Runs MCTS to find the best move.
        """
        mcts = MCTS(self._nn)
        result = mcts.run(board, num_simulations)
        
        if not result.best_move:
            return None
            
        move = result.best_move
        
        # Convert LegalMove back to PdnMove
        if isinstance(move, CapturedMove):
            # For simplicity, we assume single jump here for now as MCTS works segment-by-segment
            # However, if it's a multi-jump, AI will make it in multiple turns if not handled.
            # But the Board.move_piece handles turn switching, so AI will continue jumping if it's the same turn.
            return PdnMove(f"{move.from_}x{move.to_}", [str(move.jumped)])
        else:
            return PdnMove(f"{move.from_}-{move.to_}", [])
