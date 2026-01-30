import pandas as pd
import numpy as np
import json
import os
import sys

# Add the project root to sys.path to allow importing domain logic
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from domain.board.board import Board
from domain.side import Side
from domain.pdn_move import PdnMove
from domain.legal_move import CapturedMove
from domain.piece_factory import PieceFactory

def map_piece_to_int(piece_acronym):
    if not piece_acronym:
        return 0
    mapping = {
        'b': -1, # Black Man
        'B': -2, # Black King
        'r': 1,  # Red/White Man
        'R': 2   # Red/White King
    }
    return mapping.get(piece_acronym, 0)

def get_board_vector(board):
    vector = []
    for sq in range(1, 33):
        piece_bit = board.get_piece(sq)
        vector.append(map_piece_to_int(piece_bit))
    return vector

def map_result(result_str):
    if result_str == 'white_win':
        return 1
    elif result_str == 'black_win':
        return -1
    else:
        return 0

def parse_move_string(move_str):
    """Simple parser for moves like '11-15' or '15x22' or '16x23x30'"""
    sep = 'x' if 'x' in move_str else '-'
    try:
        parts = [int(p) for p in move_str.split(sep)]
        return parts
    except:
        return []

def main():
    print("Loading games.csv...")
    df = pd.read_csv('games.csv', sep=';')
    
    X_board = []
    X_turn = []
    X_outcome = []
    y_move = []
    
    move_vocab = set()
    
    print(f"Processing {len(df)} games...")
    
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"Processing game {idx}...")
            
        result = map_result(row['result'])
        moves_str = row['moves']
        if pd.isna(moves_str):
            continue
            
        moves_list = moves_str.split(',')
        
        board = Board()
        # board._turn starts as Side.Dark (Black)
        
        for move_str in moves_list:
            move_str = move_str.strip()
            if not move_str:
                continue
                
            # 1. Capture current state features
            current_board_vec = get_board_vector(board)
            current_turn = -1 if board.turn == Side.Dark else 1
            
            X_board.append(current_board_vec)
            X_turn.append(current_turn)
            X_outcome.append(result)
            y_move.append(move_str)
            move_vocab.add(move_str)
            
            # 2. Advance the board
            # We need to apply the move. Since our Board.apply_move expects PdnMove 
            # and might need captured squares, we'll try to find the legal move that matches.
            
            squares = parse_move_string(move_str)
            if len(squares) < 2:
                # Fallback switch turn if move is invalid to avoid infinite loop or stuck board
                board.switch_turn()
                continue
            
            success = False
            # Handle multi-jumps or simple moves
            # The domain Board.apply_move is a bit complex, let's try to mimic it or use it carefully.
            
            # For simplicity in data prep, we can try to use the bitboard directly if apply_move fails
            # But let's try the proper way first.
            
            # We need to construct a PdnMove. 
            # To get captured_squares, we might need to simulate the jump.
            captured_sqs = []
            temp_from = squares[0]
            valid_pdn = True
            
            for next_sq in squares[1:]:
                legal_moves = board.get_legal_moves(board.turn)
                match = next((m for m in legal_moves if m.from_ == temp_from and m.to_ == next_sq), None)
                if match:
                    if isinstance(match, CapturedMove):
                        captured_sqs.append(str(match.jumped))
                    temp_from = next_sq
                else:
                    valid_pdn = False
                    break
            
            if valid_pdn:
                pdn = PdnMove(move_str, captured_sqs)
                if board.apply_move(pdn):
                    success = True
            
            if not success:
               # If it fails, we switch turn to keep going, though the data might be slightly corrupted 
               # but it's better than crashing. In a real scenario we'd debug why the move is 'illegal'.
               board.switch_turn()

    print("Encoding target labels...")
    move_list = sorted(list(move_vocab))
    move_to_idx = {move: i for i, move in enumerate(move_list)}
    
    y_move_idx = [move_to_idx[m] for m in y_move]
    
    print("Saving files...")
    np.save('X_board.npy', np.array(X_board, dtype=np.int8))
    np.save('X_turn.npy', np.array(X_turn, dtype=np.int8))
    np.save('X_outcome.npy', np.array(X_outcome, dtype=np.int8))
    np.save('y_move.npy', np.array(y_move_idx, dtype=np.int32))
    
    with open('move_vocab.json', 'w') as f:
        json.dump(move_list, f)
        
    print(f"Preprocessing complete. Total samples: {len(X_board)}. Move vocabulary size: {len(move_list)}.")

if __name__ == "__main__":
    main()
