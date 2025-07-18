from flask import Blueprint, render_template, session, redirect, url_for, flash, request

from app.routes.decorators import roles_required
from database import users_collection, bcrypt
from flask_bcrypt import Bcrypt

from bson import ObjectId


bcrypt = Bcrypt()

profile_bp = Blueprint("profile", __name__)



@profile_bp.route("/")
@roles_required('student', 'staff')
def view_profile():
    user_id = session.get("user_id")

    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        flash("Invalid user session. Please log in again.", "danger")
        return redirect(url_for("auth.login"))

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("home.homepage"))

    return render_template("profile.html", user=user)

@profile_bp.route("/change_password", methods=["POST"])
@roles_required('student', 'staff')
def change_password():
    user_id = session.get("user_id")

    if not user_id:
        flash("Unauthorized access. Please log in again.", "danger")
        return redirect(url_for("auth.login"))

    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        flash("User not found. Please log in again.", "danger")
        return redirect(url_for("auth.login"))

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("profile.view_profile"))

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not bcrypt.check_password_hash(user["password"], current_password):
        flash("Current password is incorrect!", "danger")
        return redirect(url_for("profile.view_profile"))

    if new_password != confirm_password:
        flash("New passwords do not match!", "danger")
        return redirect(url_for("profile.view_profile"))

    hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"password": hashed_password}})

    flash("Password updated successfully!", "success")
    return redirect(url_for("profile.view_profile"))