import copy
import random
import numpy as np
import functools  # For memoization

from application.board_helper import board_to_8_8_3_tensor
from application.monte_carlo_tree import MCTS
from application.neural_network import NeuralNetwork
from domain.board import Board
from domain.color import Color
from domain.move import Move


# --- Self-Play Training Loop (Conceptual) ---
def self_play_training(num_games : int, num_simulations_per_move : int, neural_network : NeuralNetwork):
    """
    Conceptual self-play training loop for AlphaZero.
    """
    training_data = []

    for game_idx in range(num_games):
        print(f"\n--- Starting Self-Play Game {game_idx + 1} ---")
        board = Board()
        game_history = []

        while not board.is_game_over():
            mcts = MCTS(neural_network)
            #mcts_policy, best_move = mcts.run(board.copy(), num_simulations_per_move)
            simulation_result = mcts.run(board, num_simulations_per_move)

            if not simulation_result.best_move:
                print("No legal moves found during MCTS. Breaking game.")
                break

            # board_state_nn = board.get_state_representation()
            board_state_nn = board_to_8_8_3_tensor(board)
            game_history.append((board_state_nn, simulation_result.policy, simulation_result.best_move))

            board.move_piece(simulation_result.best_move)

        game_winner = board.get_winner()
        game_result = 0
        if game_winner == Color.Black:
            game_result = 1
        elif game_winner == Color.Red:
            game_result = -1

        for board_state_nn, mcts_policy_dict, move_made in game_history:
            training_data.append({
                'board_state': board_state_nn,
                'mcts_policy': mcts_policy_dict,
                'game_result': game_result
            })

        print(f"Game {game_idx + 1} finished. Winner: {game_winner}")

        if training_data:
            print(f"Training Neural Network with {len(training_data)} samples...")
            print("Neural Network training step completed (conceptual).")

    print("\n--- Self-Play Training Complete ---")
    return training_data


# --- Main Execution (Conceptual) ---
if __name__ == "__main__":
    board_input_shape = (8, 8, 3)
    action_space_size = 64 * 4

    checkers_nn = NeuralNetwork(board_input_shape, action_space_size)

    trained_data = self_play_training(num_games=2, num_simulations_per_move=10, neural_network=checkers_nn)

    print("\n--- Demonstration of AI playing after (conceptual) training ---")
    game_board = Board()
    #print("Initial Board:")
    #game_board.display()

    while not game_board.is_game_over():
        if game_board.turn == Color.Red:
            print("\nRed's Turn (Human Player - Random Move)")
            red_moves = game_board.get_legal_moves(Color.Red)
            if red_moves:
                chosen_move : Move = random.choice(red_moves)
                print(f"Red chooses move: {chosen_move}")
                game_board.move_piece(chosen_move)
            else:
                print("Red has no legal moves. Game Over.")
                break
        else:  # Black's Turn (AlphaZero AI)
            print("\nBlack's Turn (AlphaZero AI)")
            mcts_agent = MCTS(checkers_nn)
            result = mcts_agent.run(game_board.copy(), num_simulations=50)

            ai_best_move = result.best_move

            if ai_best_move:
                print(f"AI (Black) makes move: {ai_best_move}")
                game_board.move_piece(ai_best_move)
            else:
                print("AI (Black) has no legal moves. Game Over.")
                break

        game_board.display()

    winner = game_board.get_winner()
    if winner == Color.Red:
        print("\nGame Over! Red Wins!")
    elif winner == Color.Black:
        print("\nGame Over! Black Wins!")
    else:
        print("\nGame Over! It's a Draw (no more moves for current player).")