from pymongo import MongoClient
from pymongo.server_api import ServerApi
from infrastructure.config import DATABASE_URL, DATABASE_NAME

class MongoContext:
    def __init__(self, url: str = DATABASE_URL, db_name: str = DATABASE_NAME):
        self.client = MongoClient(url, server_api=ServerApi("1"))
        self.db = self.client[db_name]

    @property
    def sessions(self):
        return self.db["sessions"]

    @property
    def ranks(self):
        return self.db["ranks"]

    @property
    def stats(self):
        return self.db["stats"]

    @property
    def matching_queue(self):
        return self.db["matching_queue"]

    @property
    def games(self):
        return self.db["games"]

    @property
    def history(self):
        return self.db["history"]

    @property
    def profiles(self):
        return self.db["profiles"]

    @property
    def players(self):
        return self.db["players"]

# client = MongoClient(DATABASE_URL, server_api=ServerApi('1'))
#
# db = client.get_database(DATABASE_NAME)
# account_collection = db["accounts"]
# account_sessions_collection = db["accounts_sessions"]
# ranks_collection = db["ranks"]
# stats_collection = db["stats"]
# match_collection = db["matching_queue"]
# game_collection = db["games"]
# history_collection = db["history"]
# profile_collection = db["profiles"]