import logging
from typing import Dict, Type, Any

logger = logging.getLogger(__name__)

class Mediator:
    def __init__(self):
        self._handlers: Dict[Type, Any] = {}

    def register(self, request_type: Type, handler: Any):
        self._handlers[request_type] = handler

    async def send(self, request: Any) -> Any:
        request_type = type(request)
        handler = self._handlers.get(request_type)
        if handler:
            if hasattr(handler, 'handle'):
                if hasattr(handler.handle, '__call__'):
                    import inspect
                    if inspect.iscoroutinefunction(handler.handle):
                        return await handler.handle(request)
                    else:
                        return handler.handle(request)
                return None
            else:
                logger.error(f"Handler for {request_type.__name__} does not have a 'handle' method")
                raise Exception(f"Handler for {request_type.__name__} does not have a 'handle' method")
        else:
            logger.warning(f"No handler registered for request type: {request_type.__name__}")
            raise Exception(f"No handler registered for request type: {request_type.__name__}")
