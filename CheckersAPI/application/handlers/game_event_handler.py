import json
from domain.board.board import Board
from domain.history_entry import HistoryEntry
from domain.pdn_move import PdnMove
from infrastructure.connnection_manager import ConnectionManager
from infrastructure.repositories.game_repository import GameRepository


class GameEventHandler:

    def __init__(self, game_repository: GameRepository, manager: ConnectionManager):
        self.manager = manager
        self.game_repository = game_repository

    async def handle(self, game_id: str, player_id: str, pdn_move: PdnMove):
        print('Event handler called -> handle')

        game = await self.game_repository.fetch(game_id)

        print(f'Found history {game.history}')

        board = Board.from_history(game.history)

        if board.apply_move(pdn_move):
            history = HistoryEntry(
                player_id=player_id,
                move=pdn_move.as_string,
                captures=pdn_move.captured_squares,
                sequence=len(game.history),
            )

            await self.game_repository.append_history(game_id, history)

            response = pdn_move.to_dict()
            response['player_id'] = player_id

            await self.manager.broadcast(game_id, json.dumps(response))