# ============================================================
#  app/__init__.py — Application Factory (SQLite Version)
#
#  This file creates and configures the Flask application.
#
#  Key difference from MySQL version:
#  - No Flask-MySQLdb extension needed
#  - We use Python's built-in `sqlite3` module
#  - The database TABLE is created automatically on first run
#    via init_db() — no need to run schema.sql manually
# ============================================================

from flask import Flask
from config import Config


def create_app():
    """
    App factory function.
    Creates, configures, and returns the Flask application.
    """

    # Create the Flask app
    app = Flask(__name__)

    # Load configuration from config.py
    app.config.from_object(Config)

    # Register routes from routes.py
    from app.routes import main
    app.register_blueprint(main)

    return app

