import re
from flask import Blueprint, request, render_template, redirect, flash, session, url_for
from flask_bcrypt import check_password_hash
from flask_login import login_user

from app.models.User import User
from database import users_collection, bcrypt, canteen_staff_collection

auth_bp = Blueprint('auth', __name__, template_folder='templates')

# Updated Regex for Student Email Validation
STUDENT_EMAIL_REGEX = r"^K00[a-zA-Z0-9._%+-]+@student\.tus\.ie$"
STAFF_EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@tus\.ie$"



def is_valid_password(password):
    """Check if password meets complexity requirements."""
    return (
        len(password) >= 6 and
        any(char.isupper() for char in password) and
        any(char in "!@#$%^&*()-_=+[{]};:'\",<.>/?`~" for char in password)  # Special character check
    )
import re

def is_valid_password(password):
    """Check if password meets complexity requirements."""
    return (
        len(password) >= 6 and
        any(char.isupper() for char in password) and
        any(char in "!@#$%^&*()-_=+[{]};:'\",<.>/?`~" for char in password)  # Special character check
    )

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email").strip()
        password = request.form.get("password")

        # Prevent registration of canteen staff manually
        if email.endswith("@canteen.tus.ie"):
            flash("Canteen staff cannot self-register. Please contact the admin.", "danger")
            return redirect(url_for("auth.login"))

        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Email is already registered. Please log in.", "danger")
            return redirect(url_for("auth.login"))

        # Hash the password using Flask-Bcrypt before storing
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": "student"
        })

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password")

        user_data = users_collection.find_one({"email": email})

        if not user_data:
            flash("Invalid email or password!", "danger")
            return redirect(url_for("auth.login"))

        # Validate hashed password using Flask-Bcrypt
        if check_password_hash(user_data["password"], password):
            session["user_id"] = str(user_data["_id"])  # Store user in session
            session["email"] = user_data["email"]
            session["role"] = user_data["role"]

            flash("Login successful!", "success")

            # Redirect based on role
            if session["role"] in ["canteen_staff", "canteen_admin"]:
                return redirect(url_for("canteen.canteen_staff"))
            return redirect(url_for("home.homepage"))

        flash("Invalid email or password!", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")



@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Check if email exists
        user = users_collection.find_one({"email": email})
        if not user:
            flash("No account found with this email.", "danger")
            return redirect(url_for("auth.reset_password"))

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("auth.reset_password"))

        # Hash the new password and update it in the database
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})

        flash("Password reset successful! Please log in with your new password.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home.homepage"))

