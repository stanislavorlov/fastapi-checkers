import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

DATABASE_URL=os.getenv('DATABASE_URL')
DATABASE_NAME=os.getenv('DATABASE_NAME')

client = MongoClient(DATABASE_URL, server_api=ServerApi('1'))

#db = client.checkers
db = client.get_database(DATABASE_NAME)
game_collection = db["games"]
history_collection = db["history"]
player_collection = db["players"]