import json
from domain.board_factory import BoardFactory
from domain.pdn_move import PdnMove
from infrastructure.database import history_collection
from infrastructure.documents import History
from infrastructure.connnection_manager import ConnectionManager


class EventHandler:
    def __init__(self, game_id: str, manager: ConnectionManager):
        self.game_id = game_id
        self.manager = manager

    async def handle(self, player_id: str, pdn_move: PdnMove):
        print('Event handler called -> handle')

        histories = list(history_collection.find({'game_id': self.game_id}).sort('sequence', 1))

        print(f'Found history {histories}')

        board = BoardFactory.create(histories)

        if board.apply_move(pdn_move):
            history = History(
                game_id=self.game_id,
                player_id=player_id,
                move=pdn_move.as_string,
                captures=pdn_move.captured_squares,
                sequence=len(histories),
            )
            print(f'Saving history {dict(history)}')
            #history_collection.insert_one(dict(history))

            response = pdn_move.to_dict()
            print(response)
            response['player_id'] = player_id
            print(response)

            await self.manager.broadcast(self.game_id, json.dumps(response))