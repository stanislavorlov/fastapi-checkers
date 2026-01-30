from application.monte_carlo_tree import MCTS
from application.neural_network import NeuralNetwork
from application.tansor_helper import TensorHelper
from domain.board.board import Board
from domain.side import Side


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
            board_state_nn = TensorHelper.board_to_8_8_3_tensor(board)
            game_history.append((board_state_nn, simulation_result.policy, simulation_result.best_move))

            board.move_piece(simulation_result.best_move)

        game_winner = board.get_winner()
        game_result = 0
        if game_winner == Side.Dark:
            game_result = 1
        elif game_winner == Side.Light:
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