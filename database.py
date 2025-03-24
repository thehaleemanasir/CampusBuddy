from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import config  # Import from root-level config.py

import os

bcrypt = Bcrypt()

def db_connect():
    client = MongoClient(config.MONGO_URI)
    return client['campus_buddy']

db = db_connect()

societies_collection = db['societies']
campuses_collection = db['campuses']
joined_collection = db['joined_societies']
chat_history_collection = db['chats_history']
users_collection = db["users"]
mental_health_collection = db["mental_health"]
canteen_menu_collection = db["canteen_menu"]
canteen_staff_collection = db["canteen_staff"]  # New collection for staff
canteen_facilities_collection = db["canteen_facilities"]
faq_collection = db["faq_collection"]
events_collection = db['events']
