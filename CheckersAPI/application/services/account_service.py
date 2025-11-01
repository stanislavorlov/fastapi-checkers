# from domain.accounts.account import Account
# from domain.accounts.account_factory import AccountFactory
# from domain.player.rank import Rank
# from web.models import CreateAccountDto


# class AccountService:
#
#     @staticmethod
#     def register_account(create_user: CreateAccountDto):
        # full_name = FullName(create_user.first_name, create_user.last_name)
        # domain_rank = Rank.from_level(create_user.level)
        # domain_player = Account.create(domain_rank, str(full_name), Region.global_())
        #
        # domain_user = Account.create(full_name, create_user.country, create_user.email, create_user.password)

        # domain_account = AccountFactory.create(create_user)
        # domain_rank = Rank.from_level(create_user.level)

        # with client.start_session() as session:
        #     with session.start_transaction():
        #         # Maybe declare a mapper with methods to_schema, to_domain
        #         player_rank_schema = RankSchema.model_validate(domain_rank.__dict__)
        #         rank_inserted = ranks_collection.insert_one(dict(player_rank_schema))
        #
        #         player_stats_schema = StatsSchema.model_validate(domain_player.player_stats.__dict__)
        #         stats_inserted = stats_collection.insert_one(dict(player_stats_schema))
        #
        #         player_schema = pm.domain_to_schema(
        #             domain_player,
        #             str(rank_inserted.inserted_id),
        #             str(stats_inserted.inserted_id))
        #         player_insert_result = player_collection.insert_one(player_schema.model_dump())
        #
        #         user_schema = um.domain_to_schema(domain_user, str(player_insert_result.inserted_id))
        #         user_collection.insert_one(user_schema.model_dump())