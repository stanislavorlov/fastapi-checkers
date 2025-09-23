from typing import List
from domain.kernel.domain_event import DomainEvent


class Entity:

    def __init__(self):
        self._events: List[DomainEvent] = []

    def flush_events(self) -> List[DomainEvent]:
        copy = self._events.copy()

        self._events = []

        return copy

    def raise_event(self, event: DomainEvent):
        self._events.append(event)

    def raise_events(self, events: List[DomainEvent]):
        for event in events:
            self.raise_event(event)