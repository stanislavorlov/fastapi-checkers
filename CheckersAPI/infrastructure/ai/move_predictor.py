import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import models
from domain.side import Side
from domain.pdn_move import PdnMove
from domain.legal_move import CapturedMove

class AiMovePredictor:
    _instance = None
    _model = None
    _vocab = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AiMovePredictor, cls).__new__(cls)
            cls._instance._load_resources()
        return cls._instance

    def _load_resources(self):
        base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'machine-learning')
        model_path = os.path.join(base_path, 'checkers_model.keras')
        vocab_path = os.path.join(base_path, 'move_vocab.json')
        
        if not os.path.exists(model_path) or not os.path.exists(vocab_path):
            # Try absolute path from project root if relative fails
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            model_path = os.path.join(project_root, 'machine-learning', 'checkers_model.keras')
            vocab_path = os.path.join(project_root, 'machine-learning', 'move_vocab.json')

        if not os.path.exists(model_path):
             raise FileNotFoundError(f"AI model not found at {model_path}")

        self._model = models.load_model(model_path)
        with open(vocab_path, 'r') as f:
            self._vocab = json.load(f)

    def predict(self, board, target_outcome=0):
        """
        board: domain.board.Board object
        target_outcome: 1 (White win), 0 (Draw), -1 (Black win). 
                       Defaulting to 0 (Draw) or you can pass intended result.
        """
        board_vec = self._get_board_vector(board)
        turn = -1 if board.turn == Side.Dark else 1
        
        board_input = np.array([board_vec])
        turn_input = np.array([[turn]])
        outcome_input = np.array([[target_outcome]])
        
        predictions = self._model.predict([board_input, turn_input, outcome_input], verbose=0)
        
        # Get moves in order of confidence
        sorted_indices = np.argsort(predictions[0])[::-1]
        
        legal_moves = board.get_legal_moves(board.turn)
        if not legal_moves:
            return None

        for idx in sorted_indices:
            move_str = self._vocab[idx]
            pdn_move = self._match_to_legal_move(board, move_str, legal_moves)
            if pdn_move:
                return pdn_move
        
        # Fallback: if no model move is legal, pick the first legal move
        first_legal = legal_moves[0]
        if isinstance(first_legal, CapturedMove):
            return PdnMove(f"{first_legal.from_}x{first_legal.to_}", [str(first_legal.jumped)])
        else:
            return PdnMove(f"{first_legal.from_}-{first_legal.to_}", [])

    def _get_board_vector(self, board):
        vector = []
        mapping = {
            'b': -1, 'B': -2,
            'r': 1,  'R': 2,
            None: 0
        }
        for sq in range(1, 33):
            piece_bit = board.get_piece(sq)
            vector.append(mapping.get(piece_bit, 0))
        return vector

    def _match_to_legal_move(self, board, move_str, legal_moves):
        sep = 'x' if 'x' in move_str else '-'
        try:
            squares = [int(p) for p in move_str.split(sep)]
        except:
            return None

        if len(squares) < 2:
            return None

        if sep == '-':
            match = next((m for m in legal_moves if m.from_ == squares[0] and m.to_ == squares[1]), None)
            if match and not isinstance(match, CapturedMove):
                return PdnMove(move_str, [])
            return None

        if sep == 'x':
            captured_sqs = []
            current_board = board.copy()
            temp_from = squares[0]
            
            for next_sq in squares[1:]:
                possible_moves = current_board.get_legal_moves(current_board.turn)
                match = next((m for m in possible_moves if m.from_ == temp_from and m.to_ == next_sq), None)
                
                if match and isinstance(match, CapturedMove):
                    captured_sqs.append(str(match.jumped))
                    # Simulate partial move
                    current_board.move_piece(match)
                    temp_from = next_sq
                else:
                    return None
            
            return PdnMove(move_str, captured_sqs)

        return None
