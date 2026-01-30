import os
import json
import numpy as np
from tensorflow.keras import models
from domain.side import Side

class NeuralNetwork:
    """
    A wrapper around the Keras model for AlphaZero integration.
    """

    def __init__(self):
        self._load_resources()
        print("Neural Network initialized with Keras model.")

    def _load_resources(self):
        # Paths relative to the project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        model_path = os.path.join(project_root, 'machine-learning', 'checkers_model.keras')
        vocab_path = os.path.join(project_root, 'machine-learning', 'move_vocab.json')
        
        if not os.path.exists(model_path):
             raise FileNotFoundError(f"AI model not found at {model_path}")

        self._model = models.load_model(model_path)
        with open(vocab_path, 'r') as f:
            self._vocab = json.load(f)
        
        self.output_size = len(self._vocab)

    def predict(self, board):
        """
        board: domain.board.Board object
        Returns:
            policy_probs: np.array of probabilities for each move in the vocabulary.
            value: scalar value in [-1, 1] representing board evaluation.
        """
        # 1. Prepare Inputs
        board_vec = self._get_board_vector(board)
        turn = -1 if board.turn == Side.Dark else 1
        
        # We assume target outcome 0 (Draw) for the move prediction part
        target_outcome = 0
        
        board_input = np.array([board_vec])
        turn_input = np.array([[turn]])
        outcome_input = np.array([[target_outcome]])
        
        # 2. Get Policy from Keras model
        # The current model only outputs policy probabilities
        predictions = self._model.predict([board_input, turn_input, outcome_input], verbose=0)
        policy_probs = predictions[0]
        
        # 3. Heuristic Value (since model doesn't output value head yet)
        # Value should be from the perspective of the current player (who is about to move)
        value = self._get_heuristic_value(board)
        
        return policy_probs, value

    @staticmethod
    def _get_board_vector(board):
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

    @staticmethod
    def _get_heuristic_value(board):
        """
        Calculates a simple piece-count based value in range [-1, 1].
        """
        score = 0
        mapping = {
            'b': -1, 'B': -1.5,
            'r': 1,  'R': 1.5,
            None: 0
        }
        for sq in range(1, 33):
            piece_bit = board.get_piece(sq)
            score += mapping.get(piece_bit, 0)
        
        # Normalize to ~[-1, 1]
        # Max score is 12 pieces * 1.5 = 18
        normalized_score = score / 18.0
        
        # perspective adjustment
        # if it's Black's turn, a negative score is good
        if board.turn == Side.Dark:
            return -normalized_score
        else:
            return normalized_score

    def get_move_idx(self, move_str):
        """Helper to find vocab index for a move string."""
        try:
            return self._vocab.index(move_str)
        except ValueError:
            return None

    def get_move_str(self, idx):
        """Helper to find move string for a vocab index."""
        return self._vocab[idx]