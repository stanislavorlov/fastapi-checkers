from domain.kernel.value_object import ValueObject

class PlayerStats(ValueObject):
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    streak: int
    @staticmethod
    def create_empty() -> 'PlayerStats':
        return PlayerStats(
            games_played=0,
            wins=0,
            losses=0,
            draws=0,
            win_rate=0.0,
            streak=0
        )