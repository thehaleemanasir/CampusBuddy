from flask import Blueprint, render_template
from database import mental_health_collection

mental_health_bp = Blueprint("mental_health", __name__)

@mental_health_bp.route('/mental-health')
def mental_health_page():
    data = list(mental_health_collection.find({}, {"_id": 0}))
    return render_template('mental_health.html', support=data)
