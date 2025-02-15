from flask import Blueprint, render_template, request, jsonify
from app.services.mental_health_service import (
    get_all_mental_health_data,
    get_mental_health_resource,
    add_mental_health_resource,
    update_mental_health_resource,
    delete_mental_health_resource
)

mental_health_bp = Blueprint('mental_health', __name__, template_folder='templates')


# ✅ Fetch all mental health resources
@mental_health_bp.route('/mental-health', methods=['GET'])
def mental_health_page():
    mental_health_data = get_all_mental_health_data()

    if not mental_health_data:
        return "❌ No mental health data found in MongoDB", 500

    return render_template('mental_health.html', mental_health_data=mental_health_data)


# ✅ Fetch a single resource
@mental_health_bp.route('/mental-health/<resource_id>', methods=['GET'])
def get_mental_health(resource_id):
    resource = get_mental_health_resource(resource_id)
    if not resource:
        return jsonify({"error": "Resource not found"}), 404
    return jsonify(resource), 200

# ✅ Add a new resource
@mental_health_bp.route('/add-mental-health', methods=['POST'])
def add_mental_health():
    data = request.json
    if not data or "title" not in data or "category" not in data:
        return jsonify({"error": "Invalid data"}), 400

    resource_id = add_mental_health_resource(data)
    return jsonify({"message": "Resource added", "id": str(resource_id)}), 201

# ✅ Update an existing resource
@mental_health_bp.route('/update-mental-health/<resource_id>', methods=['PUT'])
def update_mental_health(resource_id):
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    updated = update_mental_health_resource(resource_id, data)
    if updated == 0:
        return jsonify({"error": "Resource not found"}), 404

    return jsonify({"message": "Resource updated successfully"}), 200

# ✅ Delete a resource
@mental_health_bp.route('/delete-mental-health/<resource_id>', methods=['DELETE'])
def delete_mental_health(resource_id):
    deleted = delete_mental_health_resource(resource_id)
    if deleted == 0:
        return jsonify({"error": "Resource not found"}), 404

    return jsonify({"message": "Resource deleted successfully"}), 200
