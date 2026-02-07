import asyncio
import logging
import json
from application.matchmaking import Matchmaker, QueueEntry
from infrastructure.repositories.matching_repository import MatchingRepository
from infrastructure.repositories.game_repository import GameRepository
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.connnection_manager import ConnectionManager
from domain.game.game import Game

logger = logging.getLogger(__name__)

class MatchmakingManager:
    def __init__(
        self,
        matching_repository: MatchingRepository,
        game_repository: GameRepository,
        player_repository: PlayerRepository,
        connection_manager: ConnectionManager
    ):
        self.matching_repository = matching_repository
        self.game_repository = game_repository
        self.player_repository = player_repository
        self.connection_manager = connection_manager
        self.matchmaker = Matchmaker()

    async def run_tick(self):
        try:
            # 1. Fetch waiting players from DB
            waiting_items = self.matching_repository.get_waiting_players()
            if not waiting_items:
                return

            # 2. Sync with in-memory matchmaker
            # Clear in-memory queue first to ensure consistency with DB
            self.matchmaker.queue.clear()
            for item in waiting_items:
                entry = QueueEntry(
                    player_id=str(item.player_id),
                    rating=item.rating_estimate,
                    rd=item.rd,
                    region=item.region,
                    join_ts=item.timestamp.timestamp()
                )
                self.matchmaker.enqueue(entry)

            # 3. Find pairs
            pairs = self.matchmaker.tick()
            if not pairs:
                return

            logger.info(f"Matchmaking found {len(pairs)} pairs")

            for p1_entry, p2_entry in pairs:
                await self._handle_match(p1_entry.player_id, p2_entry.player_id)

        except Exception as e:
            logger.error(f"Error in matchmaking tick: {e}", exc_info=True)

    async def _handle_match(self, p1_id: str, p2_id: str):
        try:
            # 1. Load players from domain
            player1 = self.player_repository.get_by_id(p1_id)
            player2 = self.player_repository.get_by_id(p2_id)

            if not player1 or not player2:
                logger.warning(f"Could not load players for match: {p1_id}, {p2_id}")
                return

            # 2. Create game
            new_game = Game.create_pvp(player1, player2)
            game_id = self.game_repository.create(new_game)
            game_id_str = str(game_id)

            # 3. Update DB queue status
            self.matching_repository.mark_as_matched(p1_id, p2_id)

            # 4. Notify players via WebSockets
            notification = json.dumps({
                "type": "match_found",
                "game_id": game_id_str
            })

            await self.connection_manager.send_to_player(p1_id, notification)
            await self.connection_manager.send_to_player(p2_id, notification)

            logger.info(f"Match found and game created: {game_id_str} for players {p1_id} and {p2_id}")

        except Exception as e:
            logger.error(f"Error handling match: {e}", exc_info=True)
