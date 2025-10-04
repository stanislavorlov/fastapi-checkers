from typing import List
from domain.history_entry import HistoryEntry


class BoardHistory:

    def __init__(self, items: List[HistoryEntry]):
        super().__init__()
        self.items = items

    def append(self, history_dto: HistoryEntry):
        self.items.append(history_dto)
        self.items = sorted(self.items, key=lambda x: x.sequence)

    def __iter__(self):
        return iter(self.items)

    @staticmethod
    def empty():
        return BoardHistory([])

    def last(self):
        return self.items[-1]