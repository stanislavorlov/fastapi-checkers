import numpy as np
import json
import tensorflow as tf
from tensorflow.keras import models

import os

def load_model_and_vocab():
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, 'checkers_model.keras')
    vocab_path = os.path.join(base_path, 'move_vocab.json')
    
    model = models.load_model(model_path)
    with open(vocab_path, 'r') as f:
        move_vocab = json.load(f)
    return model, move_vocab

def predict_next_move(model, move_vocab, board_vec, turn, target_outcome):
    """
    board_vec: list of 32 integers (-2 to 2)
    turn: -1 (Black) or 1 (White)
    target_outcome: -1 (Black win), 0 (Draw), 1 (White win)
    """
    board_input = np.array([board_vec])
    turn_input = np.array([[turn]])
    outcome_input = np.array([[target_outcome]])
    
    predictions = model.predict([board_input, turn_input, outcome_input], verbose=0)
    move_idx = np.argmax(predictions[0])
    return move_vocab[move_idx], predictions[0][move_idx]

def get_starting_board():
    # Black pieces: -1 at 1..12
    # White pieces: 1 at 21..32
    board = [0] * 32
    for i in range(12): board[i] = -1
    for i in range(20, 32): board[i] = 1
    return board

def main():
    model, vocab = load_model_and_vocab()
    
    board = get_starting_board()
    turn = -1 # Black starts
    
    print("Standard Starting Position (Black to move)")
    
    outcomes = {
        -1: "Black Win Goal",
        0: "Draw Goal",
        1: "White Win Goal"
    }
    
    for outcome_val, label in outcomes.items():
        move, prob = predict_next_move(model, vocab, board, turn, outcome_val)
        print(f"Target: {label:15s} -> Predicted Move: {move:10s} (Confidence: {prob:.4f})")

if __name__ == "__main__":
    main()
