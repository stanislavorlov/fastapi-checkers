from typing import List
from domain.kernel.domain_event import DomainEvent


class Entity:

    def __init__(self):
        self._events: List[DomainEvent] = []

    @property
    def events(self) -> List[DomainEvent]:
        return self._events

    def raise_event(self, event: DomainEvent):
        self._events.append(event)

    def raise_events(self, events: List[DomainEvent]):
        for event in events:
            self.raise_event(event)