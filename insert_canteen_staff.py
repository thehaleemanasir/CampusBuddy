from database import canteen_staff_collection, bcrypt

staff_data = {
    "email": "canteen_admin@canteen.tus.ie",
    "password": bcrypt.generate_password_hash("password123").decode("utf-8"),
    "role": "canteen_admin"
}

canteen_staff_collection.insert_one(staff_data)
print("✅ Canteen Staff User Inserted!")
