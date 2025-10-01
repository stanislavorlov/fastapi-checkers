class EventType:
    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def move():
        return EventType('move')

    @staticmethod
    def select():
        return EventType('select')

    @staticmethod
    def unselect():
        return EventType('unselect')

    @staticmethod
    def capture():
        return EventType('capture')

    @staticmethod
    def promote():
        return EventType('promote')

    @staticmethod
    def turned():
        return EventType('turned')

    @staticmethod
    def parse(message_text: str):
        match message_text:
            case 'move':
                return EventType.move()
            case 'select':
                return EventType.select()
            case 'unselect':
                return EventType.unselect()
            case 'capture':
                return EventType.capture()
            case 'promote':
                return EventType.promote()
            case 'turned':
                return EventType.turned()
            case _:
                return None

    def value(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

class GameEvent:
    def __init__(self, player_id: str, type_: EventType, square: str):
        self.player_id = player_id
        self.type = type_
        self.square = square

class GameEvents:
    def __init__(self, prev: GameEvent, cur: GameEvent):
        self.prev = prev
        self.cur = cur