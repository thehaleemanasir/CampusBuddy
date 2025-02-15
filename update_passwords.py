from database import users_collection
from flask_bcrypt import Bcrypt
from main import app

# ✅ Initialize Bcrypt
bcrypt = Bcrypt(app)

# ✅ Fetch all users
users = users_collection.find({})

# ✅ Update plaintext passwords to hashed ones
for user in users:
    if not user["password"].startswith("$2b$"):  # Detect unencrypted passwords
        hashed_password = bcrypt.generate_password_hash(user["password"]).decode("utf-8")
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"password": hashed_password}}
        )

print("✅ All plaintext passwords are now hashed!")
