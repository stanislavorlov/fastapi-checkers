from dataclasses import dataclass

@dataclass
class PlayerStats:
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    streak: int

    def __init__(self, games_played, wins, losses, draws, win_rate, streak):
        self.games_played = games_played
        self.wins = wins
        self.losses = losses
        self.draws = draws
        self.win_rate = win_rate
        self.streak = streak

    @staticmethod
    def create_empty() -> 'PlayerStats':
        return PlayerStats(0, 0, 0, 0, 0, 0)