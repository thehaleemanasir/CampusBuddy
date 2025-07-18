import os
import logging
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("torch").setLevel(logging.ERROR)
from reminder_scheduler import start_reminder_scheduler

from flask import render_template, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from app import create_app
from app.models.User import User
from app.routes.academic_routes import academic_bp
from app.routes.auth_routes import auth_bp
from app.routes.calendar_routes import calendar_bp
from app.routes.canteen_routes import canteen_bp
from app.routes.home_routes import home_bp
from dotenv import load_dotenv

from app.routes.mental_health_routes import mental_health_bp
from app.routes.profile_routes import profile_bp
from app.routes.society_routes import society_bp
from app.routes.chatbot_routes import chatbot_bp
from database import db_connect, users_collection

from extensions import socketio



app = create_app()
login_manager = LoginManager()
login_manager.init_app(app)
## app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
socketio.init_app(app)

bcrypt = Bcrypt(app)


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Unauthorized'}), 401

from bson import ObjectId

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        return None
    return User(str(user_data["_id"]), user_data["email"], user_data["role"])

from flask_login import current_user

@app.route("/whoami")
def whoami():
    if current_user.is_authenticated:
        return f"Logged in as: {current_user.email}"
    return "Not logged in"


db = db_connect()

load_dotenv()

start_reminder_scheduler()

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise ValueError("SECRET_KEY is missing! Set it in the .env file.")

@app.route("/")
def landing_page():
    return render_template("landingPage.html")

@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403

# Register Blueprints
app.register_blueprint(mental_health_bp, url_prefix="/mental-health")
app.register_blueprint(home_bp, url_prefix="/") #homepage
#app.register_blueprint(admin_bp)
app.register_blueprint(society_bp, url_prefix="/society")
app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(canteen_bp, url_prefix="/canteen")
app.register_blueprint(academic_bp, url_prefix="/academic")
app.register_blueprint(calendar_bp)

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
