from domain.king import King
from domain.man import Man
from domain.piece import Piece
from domain.side import Side


class PieceFactory:

    @staticmethod
    def get_piece(acronym: str) -> Piece:
        pieces = [Man(Side.Dark), Man(Side.Light), King(Side.Dark), King(Side.Light)]
        piece = next((p for p in pieces if p.acronym == acronym), None)

        return piece