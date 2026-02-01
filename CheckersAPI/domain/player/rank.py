from datetime import datetime
from domain.kernel.value_object import ValueObject


class Rank(ValueObject):
    rating: int
    deviation: int
    last_update: datetime

    @staticmethod
    def beginner():
        return Rank(rating=400, deviation=0, last_update=datetime.now())

    @staticmethod
    def intermediate():
        return Rank(rating=800, deviation=0, last_update=datetime.now())

    @staticmethod
    def advanced():
        return Rank(rating=1200, deviation=0, last_update=datetime.now())

    @staticmethod
    def from_level(user_level: str) -> 'Rank':
        match user_level:
            case 'beginner':
                return Rank.beginner()
            case 'intermediate':
                return Rank.intermediate()
            case 'advanced':
                return Rank.advanced()

        return Rank.intermediate()