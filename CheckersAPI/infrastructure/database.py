from pymongo import MongoClient
from pymongo.server_api import ServerApi
from infrastructure.config import DATABASE_URL, DATABASE_NAME

client = MongoClient(DATABASE_URL, server_api=ServerApi('1'))

db = client.get_database(DATABASE_NAME)
game_collection = db["games"]
history_collection = db["history"]
user_collection = db["users"]
player_collection = db["players"]
match_collection = db["matching_queue"]