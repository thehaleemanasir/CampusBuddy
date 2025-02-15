from flask import Blueprint, render_template
from app.services.auth_helpers import login_required  # Update based on where auth_helpers.py is stored

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
