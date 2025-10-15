from dataclasses import dataclass
from domain.kernel.entity import Entity
from domain.players.rank import Rank
from domain.players.region import Region
from domain.players.stats import PlayerStats
from domain.users.full_name import FullName, FirstName, LastName


@dataclass
class Player(Entity):
    player_rank: Rank
    player_stats: PlayerStats
    nickname: str
    region: Region
    is_anonymous: bool

    @staticmethod
    def create(rank: Rank, nickname: str, region: Region) -> 'Player':
        return Player(
            player_rank=rank,
            nickname=nickname,
            region=region,
            player_stats=PlayerStats.create_empty(),
            is_anonymous=False,
        )

    @staticmethod
    def create_anonymous(rank: Rank) -> 'Player':
        return Player(
            player_rank=rank,
            nickname=FullName(FirstName.create(), LastName.create()),
            region=Region.global_(),
            player_stats=PlayerStats.create_empty(),
            is_anonymous=True,
        )