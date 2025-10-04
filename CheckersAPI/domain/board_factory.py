from domain.board import Board
from domain.board_history import BoardHistory
from domain.history_entry import HistoryEntry
from infrastructure.documents import History


class BoardFactory:

    @staticmethod
    def create(histories: list[History]) -> Board:
        history_entries: list[HistoryEntry] = []
        for history in histories:
            history_entries.append(HistoryEntry(
                player_id=history['player_id'],
                move=history['move'],
                sequence=history['sequence'],
                captures=history['captures'],
            ))

        board_history = BoardHistory(history_entries)

        return Board().from_history(board_history)