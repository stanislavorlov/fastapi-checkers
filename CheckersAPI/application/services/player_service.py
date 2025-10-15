from domain.players.player import Player
from domain.players.rank import Rank
from domain.players.region import Region
from domain.users.full_name import FullName
from domain.users.user import User
from infrastructure.database import client, user_collection, ranks_collection, player_collection, stats_collection
from infrastructure.documents import PlayerStatsSchema, PlayerRankSchema
from infrastructure.mappers import user_mapper as um, player_mapper as pm
from web.models import CreateUserDto


class PlayerService:

    @staticmethod
    def register_user(create_user: CreateUserDto):
        full_name = FullName(create_user.first_name, create_user.last_name)
        domain_rank = Rank.from_level(create_user.level)
        domain_player = Player.create(domain_rank, str(full_name), Region.global_())

        domain_user = User.create(full_name, create_user.country, create_user.email, create_user.password, domain_player)

        with client.start_session() as session:
            with session.start_transaction():
                # Maybe declare a mapper with methods to_schema, to_domain
                player_rank_schema = PlayerRankSchema.model_validate(domain_rank.__dict__)
                rank_inserted = ranks_collection.insert_one(dict(player_rank_schema))

                player_stats_schema = PlayerStatsSchema.model_validate(domain_player.player_stats.__dict__)
                stats_inserted = stats_collection.insert_one(dict(player_stats_schema))

                player_schema = pm.domain_to_schema(
                    domain_player,
                    str(rank_inserted.inserted_id),
                    str(stats_inserted.inserted_id))
                player_insert_result = player_collection.insert_one(player_schema.model_dump())

                user_schema = um.domain_to_schema(domain_user, str(player_insert_result.inserted_id))
                user_collection.insert_one(user_schema.model_dump())