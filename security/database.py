from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import config

bcrypt = Bcrypt()

def db_connect():
    client = MongoClient(config.MONGO_URI)
    return client['campus_buddy']

db = db_connect()

societies_collection = db['societies']
campuses_collection = db['campuses']
chat_history_collection = db['chats_history']
users_collection = db["users"]
canteen_menu_collection = db["canteen_menu"]
canteen_staff_collection = db["canteen_staff"]
canteen_facilities_collection = db["canteen_facilities"]
faq_collection = db["faq_collection"]
calendar_events_collection = db['calendar_events']