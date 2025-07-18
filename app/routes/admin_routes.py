from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from functools import wraps

from app.routes.decorators import roles_required
from database import users_collection, chat_history_collection
from bson import ObjectId

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        role = session.get("role")
        if role != "admin":
            flash("Admin access required.")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route("/")
@roles_required('admin')
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/admin/users")
@roles_required('admin')
def manage_users():
    users = list(users_collection.find())
    return render_template("admin/manage_users.html", users=users)

@roles_required('admin')
@admin_bp.route("/admin/users/toggle/<user_id>")
def toggle_user(user_id):
    from bson import ObjectId
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        new_status = not user.get("active", False)
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"active": new_status}}
        )
        flash(f"User {'activated' if new_status else 'deactivated'} successfully.", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('admin.manage_users'))


@admin_bp.route("/admin/users/promote/<user_id>", methods=["POST"])
@roles_required('admin')
def promote_user(user_id):
    new_role = request.form.get("role")
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role}})
    flash("User promoted to " + new_role, "success")
    return redirect(url_for("admin.manage_users"))

@admin_bp.route("/chatbot-logs")
@roles_required('admin')
def chatbot_logs():
    logs = list(chat_history_collection.find().sort("timestamp", -1))
    return render_template("admin/admin_chatbot_logs.html", logs=logs)
@admin_bp.route("/update-response/<log_id>", methods=["POST"])
@roles_required('admin')
def update_chatbot_response(log_id):
    new_response = request.form.get("updated_response")
    if new_response:
        chat_history_collection.update_one(
            {"_id": ObjectId(log_id)},
            {
                "$set": {
                    "response": new_response,
                    "edited": True
                }
            }
        )

        flash("Response updated!", "success")
    return redirect(url_for("admin.chatbot_logs"))

@admin_bp.route("/chatbot-logs/delete/<log_id>")
@roles_required('admin')
def delete_chatbot_log(log_id):
    from bson import ObjectId
    chat_history_collection.delete_one({"_id": ObjectId(log_id)})
    flash("Chat log deleted successfully.", "success")
    return redirect(url_for("admin.chatbot_logs"))
