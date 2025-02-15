from database import users_collection, bcrypt

users_collection.insert_one({
    "email": "canteen_admin@canteen.tus.ie",
    "password": bcrypt.generate_password_hash("password123").decode("utf-8"),
    "role": "canteen_admin"
})
print("✅ Canteen Admin User Created!")
