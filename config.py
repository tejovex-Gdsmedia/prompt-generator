# ============================================================
#  config.py — Flask Application Configuration (SQLite Version)
#
#  SQLite replaces MySQL completely.
#  No host, no username, no password needed.
#  The database is just a single file: promptgen.db
#  It is created automatically the first time you run the app.
# ============================================================

import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the same directory/root
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

class Config:

    # ----------------------------------------------------------
    # SECRET_KEY
    # Used by Flask to sign session cookies securely.
    # Change this in the .env file in production.
    # ----------------------------------------------------------
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'promptgen-secret-key-change-in-production')

    # ----------------------------------------------------------
    # DEBUG
    # True  → auto-reloads when you save a file (development)
    # False → use in production
    # ----------------------------------------------------------
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # ----------------------------------------------------------
    # SUPABASE POSTGRESQL DATABASE
    # Retrieve the database connection URL from environment variables.
    # ----------------------------------------------------------
    DATABASE_URL = os.environ.get('DATABASE_URL')

