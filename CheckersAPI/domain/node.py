from typing import Optional, Dict, Tuple, List

from domain.board import Directions
from domain.color import Color
from domain.piece import Piece


class Node:
    def __init__(self, square: int):
        self._square = square
        self._piece : Optional['Piece'] = None
        self._neighbors: Dict[Directions, 'Node'] = {}

    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, piece):
        self._piece = piece

    @property
    def square(self):
        return self._square

    def add_neighbor(self, direction: Directions, neighbor: 'Node'):
        self._neighbors[direction] = neighbor

    def get_neighbor_squares(self) -> List[Tuple[Directions, 'Node']]:
        neighbors : List[Tuple[Directions, Node]] = []

        if not self._piece:
            return neighbors

        for direction in self._piece.get_move_directions():
            neighbors.append((direction, self._neighbors[direction]))

        return neighbors
