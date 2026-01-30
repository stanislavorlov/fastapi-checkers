from typing import Dict, List, Optional
import numpy as np
from application.neural_network import NeuralNetwork
from domain.board.board import Board
from domain.side import Side
from domain.legal_move import LegalMove, CapturedMove

class MCTSNode:
    """
    Represents a node in the Monte Carlo Tree Search tree.
    """

    def __init__(self, board: Board, parent=None, parent_action: LegalMove = None):
        self.board = board
        self.parent: Optional[MCTSNode] = parent
        self.parent_action = parent_action
        self.children: Dict[LegalMove, MCTSNode] = {}
        self.visits = 0
        self.value_sum = 0
        self.policy_prior = 0.0

        # List of legal moves that haven't been expanded as children yet
        self.unexplored_moves: Optional[List[LegalMove]] = None

    def is_leaf(self) -> bool:
        return not self.children

    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    def get_uct_score(self, c_puct: float) -> float:
        """
        Calculate UCT score for node selection.
        """
        if self.visits == 0:
            # high value to encourage initial exploration
            q_value = 0
            exploration_term = c_puct * self.policy_prior * (np.sqrt(self.parent.visits) / (1 + self.visits))
        else:
            q_value = self.value_sum / self.visits
            exploration_term = c_puct * self.policy_prior * (np.sqrt(self.parent.visits) / (1 + self.visits))

        return q_value + exploration_term

class SimulationResult:
    def __init__(self, policy: Dict[LegalMove, float], best_move: Optional[LegalMove]):
        self.policy = policy
        self.best_move = best_move

class MCTS:
    """
    Implements the Monte Carlo Tree Search algorithm guided by a Neural Network.
    """

    def __init__(self, neural_network: NeuralNetwork, c_puct: float = 1.4):
        self.nn = neural_network
        self.c_puct = c_puct

    def run(self, root_board: Board, num_simulations: int) -> SimulationResult:
        root = MCTSNode(root_board.copy())

        # Initial expansion of the root
        self._expand_and_evaluate(root)

        for _ in range(num_simulations):
            node = root
            path = [node]

            # 1. Selection
            while not node.is_leaf() and not node.is_game_over():
                node = self._select_child(node)
                path.append(node)

            # 2. Expansion and Evaluation
            value = 0
            if not node.is_game_over():
                value = self._expand_and_evaluate(node)
            else:
                # Terminal node evaluation
                winner = node.board.get_winner()
                if winner == Side.Dark:
                    value = 1.0 # Black wins
                elif winner == Side.Light:
                    value = -1.0 # Red wins
                else:
                    value = 0.0 # Draw
                
                # Invert if it's current player's turn (value should be from perspective of current player)
                if node.board.turn == Side.Light:
                    value = -value

            # 3. Backpropagation
            self._backpropagate(path, value)

        # 4. Extract Results
        return self._create_result(root)

    def _select_child(self, node: MCTSNode) -> MCTSNode:
        best_score = float('-inf')
        best_child = None

        for child in node.children.values():
            score = child.get_uct_score(self.c_puct)
            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def _expand_and_evaluate(self, node: MCTSNode) -> float:
        """
        Expands the node by creating children for all legal moves and evaluates the state.
        Returns the value estimate from the neural network.
        """
        # Get policy and value from NN
        policy_probs, value = self.nn.predict(node.board)
        
        legal_moves = node.board.get_legal_moves(node.board.turn)
        
        # Calculate priors for legal moves
        priors = []
        for move in legal_moves:
            # Convert move to PDN string for lookup
            move_str = f"{move.from_}x{move.to_}" if isinstance(move, CapturedMove) else f"{move.from_}-{move.to_}"
            idx = self.nn.get_move_idx(move_str)
            prob = policy_probs[idx] if idx is not None else 0.01 # Small bias for moves not in vocab
            priors.append(prob)
        
        # Normalize priors among legal moves
        sum_priors = sum(priors)
        if sum_priors > 0:
            priors = [p / sum_priors for p in priors]
        else:
            priors = [1.0 / len(legal_moves)] * len(legal_moves)

        # Create child nodes
        for i, move in enumerate(legal_moves):
            next_board = node.board.copy()
            next_board.move_piece(move)
            child = MCTSNode(next_board, parent=node, parent_action=move)
            child.policy_prior = priors[i]
            node.children[move] = child

        return value

    @staticmethod
    def _backpropagate(path: List[MCTSNode], value: float):
        """
        Updates node statistics along the selection path.
        """
        # The value is from the perspective of the leaf node's player.
        # As we go up, each node's value is the negative of its child's value.
        for node in reversed(path):
            node.visits += 1
            node.value_sum += value
            value = -value # switch perspective for parent

    @staticmethod
    def _create_result(root: MCTSNode) -> SimulationResult:
        if not root.children:
            return SimulationResult({}, None)

        # Choose the move with the most visits (most robust)
        move_visits = {move: child.visits for move, child in root.children.items()}
        total_visits = sum(move_visits.values())
        
        policy = {move: visits / total_visits for move, visits in move_visits.items()}
        best_move = max(move_visits, key=move_visits.get)

        return SimulationResult(policy, best_move)