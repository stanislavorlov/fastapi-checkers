from application.monte_carlo_tree import MCTS
from application.neural_network import NeuralNetwork
from domain.board.board import Board
from domain.pdn_move import PdnMove
from domain.legal_move import LegalMove, CapturedMove
from domain.side import Side
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
        current_board = board.copy()
        segments = []
        captured_sqs = []
        is_capture = False
        
        original_side = board.turn
        
        while True:
            mcts = MCTS(self._nn)
            result = mcts.run(current_board, num_simulations)
            if not result.best_move:
                break
            
            move = result.best_move
            if not segments:
                segments.append(move.from_)
            segments.append(move.to_)
            
            if isinstance(move, CapturedMove):
                is_capture = True
                captured_sqs.append(str(move.jumped))
            
            current_board.move_piece(move)
            
            # Stop if turn switched, game over, or no more segments found
            if current_board.turn != original_side or current_board.is_game_over():
                break
        
        if len(segments) < 2:
            return None
            
        sep = "x" if is_capture else "-"
        pdn_str = sep.join(map(str, segments))
        return PdnMove(pdn_str, captured_sqs)
