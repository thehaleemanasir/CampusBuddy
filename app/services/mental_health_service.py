from database import mental_health_collection
from bson import ObjectId

# ✅ Fetch all mental health resources
def get_all_mental_health_data():
    return list(mental_health_collection.find({}, {"_id": 0}))

# ✅ Fetch a single mental health resource by ID
def get_mental_health_resource(resource_id):
    return mental_health_collection.find_one({"_id": ObjectId(resource_id)}, {"_id": 0})

# ✅ Add a new mental health resource
def add_mental_health_resource(data):
    return mental_health_collection.insert_one(data).inserted_id

# ✅ Update an existing mental health resource
def update_mental_health_resource(resource_id, data):
    return mental_health_collection.update_one({"_id": ObjectId(resource_id)}, {"$set": data}).matched_count

# ✅ Delete a mental health resource
def delete_mental_health_resource(resource_id):
    return mental_health_collection.delete_one({"_id": ObjectId(resource_id)}).deleted_count
