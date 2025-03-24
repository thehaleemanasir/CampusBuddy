import os

from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin

from app.routes.academic_routes import academic_bp
from app.routes.auth_routes import auth_bp
from app.routes.canteen_routes import canteen_bp
from app.routes.events_routes import events_bp
##from app.routes.events_routes import events_bp
from app.routes.home_routes import home_bp
from dotenv import load_dotenv

from app.routes.profile_routes import profile_bp
from app.routes.society_routes import society_bp
from app.routes.chatbot_routes import chatbot_bp
from app.routes.mental_health_routes import mental_health_bp
from database import db_connect, users_collection
import config


app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# ✅ Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)


# Database Connection
db = db_connect()

# Load environment variables from .env
load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise ValueError("SECRET_KEY is missing! Set it in the .env file.")

@app.route("/")
def landing_page():
    return render_template("landingPage.html")

# Register Blueprints
app.register_blueprint(home_bp, url_prefix="/") #homepage
app.register_blueprint(society_bp, url_prefix="/society") #socoertu
app.register_blueprint(chatbot_bp, url_prefix="/chatbot") #chatbot
app.register_blueprint(auth_bp, url_prefix="/auth")  # Authentication (Login, Register)
app.register_blueprint(profile_bp, url_prefix="/profile")

app.register_blueprint(mental_health_bp, url_prefix="/mental_health")
app.register_blueprint(canteen_bp, url_prefix="/canteen")
app.register_blueprint(academic_bp, url_prefix="/academic")

app.register_blueprint(events_bp)  # No url_prefix needed


if __name__ == "__main__":
    app.run(debug=True)
