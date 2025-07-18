

from flask import Blueprint, render_template

from app.routes.decorators import roles_required

mental_health_bp = Blueprint("mental_health", __name__)

@mental_health_bp.route("/mental-health")
@roles_required('student', 'staff')
def student_mental_health_page():
    return render_template("mental_health.html")
