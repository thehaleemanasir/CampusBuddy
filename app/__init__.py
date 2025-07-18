import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    # 🔐 Secret key for sessions
    app.secret_key = "your_secret_key_here"

    # ✅ Configure upload folder for PDFs
    app.config["UPLOAD_FOLDER"] = os.path.join("app", "static", "resources")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max file size

    # 🧩 Register Blueprints
    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    # (Register other blueprints like auth, home, canteen etc here)
    # from app.routes.auth_routes import auth_bp
    # app.register_blueprint(auth_bp)

    return app
