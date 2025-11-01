# --- MCTS Node ---
import random
from typing import Dict
import numpy as np

from application.tansor_helper import TensorHelper
from domain.board.board import Board
from domain.side import Side
from domain.move import Move
from neural_network import NeuralNetwork

class MCTSNode:
    """
    Represents a node in the Monte Carlo Tree Search tree.
    """

    def __init__(self, board : Board, parent=None, parent_action : Move=None):
        self.board = board
        self.parent : MCTSNode = parent
        self.parent_action = parent_action
        self.children : Dict[Move, MCTSNode] = {}
        self.visits = 0
        self.value_sum = 0
        self.policy_prior = None

        # The MCTSNode itself uses the Board's get_legal_moves, which is now cached.
        # This list will be populated on demand and then used.
        self.unexplored_moves : list[Move] = None

    def is_leaf(self):
        return not self.children and not self.unexplored_moves

    def is_game_over(self):
        return self.board.is_game_over()

    def get_uct_score(self, c_puct):
        if self.visits == 0:
            return float('inf')

        q_value = self.value_sum / self.visits

        if self.parent:
            exploration_term = c_puct * self.policy_prior * (np.sqrt(self.parent.visits) / (1 + self.visits))
        else:
            exploration_term = 0

        return q_value + exploration_term

class SimulationResult:

    def __init__(self, policy: dict[Move, float], best_move: Move):
        self.policy = policy
        self.best_move = best_move

# --- Monte Carlo Tree Search (MCTS) ---
class MCTS:
    """
    Implements the Monte Carlo Tree Search algorithm.
    """

    def __init__(self, neural_network : NeuralNetwork, c_puct=1.0):
        self.nn = neural_network
        self.c_puct = c_puct

    def run(self, root_board : Board, num_simulations):
        root = MCTSNode(root_board)

        for _ in range(num_simulations):
            node = root
            path = [node]

            # 1. Selection: Traverse the tree to a leaf node
            while not node.is_leaf() and not node.is_game_over():
                best_child = None
                best_uct_score = float('-inf')

                if node.unexplored_moves is None:
                    # This call now benefits from the Board's internal cache
                    node.unexplored_moves = node.board.get_legal_moves(node.board.turn)
                    random.shuffle(node.unexplored_moves)

                if node.unexplored_moves:
                    move_to_expand = node.unexplored_moves.pop()

                    next_board = node.board.copy()
                    next_board.move_piece(move_to_expand)
                    best_child : MCTSNode = MCTSNode(next_board, parent=node, parent_action=move_to_expand)
                    node.children[move_to_expand] = best_child

                    #board_state_nn = next_board.get_state_representation()
                    board_state_nn = TensorHelper.board_to_8_8_3_tensor(next_board)
                    policy_probs, value = self.nn.predict(board_state_nn)
                    best_child.policy_prior = 1.0 / (
                                len(node.unexplored_moves) + 1) if node.unexplored_moves else 1.0  # Placeholder

                    node = best_child
                    path.append(node)
                    break

                else:
                    for move, child in node.children.items():
                        uct_score = child.get_uct_score(self.c_puct)
                        if uct_score > best_uct_score:
                            best_uct_score = uct_score
                            best_child = child

                    if best_child is None:
                        break
                    node = best_child
                    path.append(node)

            # 2. Expansion
            if node.is_leaf() and not node.is_game_over():
                #board_state_nn = node.board.get_state_representation()
                board_state_nn = TensorHelper.board_to_8_8_3_tensor(node.board)
                policy_probs, value = self.nn.predict(board_state_nn)
            elif node.is_game_over():
                winner = node.board.get_winner()
                if winner == Side.Dark:
                    value = 1.0
                elif winner == Side.Light:
                    value = -1.0
                else:
                    value = 0.0
            else:
                value = 0.0

            # 3. Backpropagation
            for node_on_path in reversed(path):
                node_on_path.visits += 1
                if node_on_path.board.turn == Side.Dark:
                    node_on_path.value_sum += value
                else:
                    node_on_path.value_sum -= value

        # 4. Get final policy
        move_visits = {move: child.visits for move, child in root.children.items()}
        total_visits = sum(move_visits.values())
        if total_visits == 0:
            return SimulationResult({}, None)

        final_policy = {move: count / total_visits for move, count in move_visits.items()}
        best_move = max(final_policy, key=final_policy.get) if final_policy else None

        return SimulationResult(final_policy, best_move)