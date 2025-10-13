from pymongo import MongoClient
from pymongo.server_api import ServerApi
from infrastructure.config import DATABASE_URL, DATABASE_NAME

client = MongoClient(DATABASE_URL, server_api=ServerApi('1'))

db = client.get_database(DATABASE_NAME)
user_collection = db["users"]
users_session_collection = db["user_sessions"]
ranks_collection = db["ranks"]
stats_collection = db["stats"]
player_collection = db["players"]
match_collection = db["matching_queue"]
game_collection = db["games"]
history_collection = db["history"]
