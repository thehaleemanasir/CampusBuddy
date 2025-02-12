from pymongo import MongoClient
import config

def db_connect():
    client = MongoClient(config.MONGO_URI)
    return client['campus_buddy']

db = db_connect()

societies_collection = db['societies']
campuses_collection = db['campuses']
joined_collection = db['joined_societies']
chat_history_collection = db['chats_history']
