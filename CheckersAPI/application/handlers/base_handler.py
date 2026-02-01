from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TRequest = TypeVar('TRequest')
TResponse = TypeVar('TResponse')

class RequestHandler(ABC, Generic[TRequest, TResponse]):
    @abstractmethod
    async def handle(self, request: TRequest) -> TResponse:
        pass
