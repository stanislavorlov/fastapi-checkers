from pymongo import MongoClient
from pymongo.server_api import ServerApi

client = MongoClient("mongodb+srv://stasorlov21:1ibAsmJf2SUq95Ba@cluster0.cchn0.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))

#db = client.checkers
db = client.get_database("checkers")
collection_name = db["games"]