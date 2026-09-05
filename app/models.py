# ============================================================
#  app/models.py — Database Query Functions (Supabase PostgreSQL Version)
#
#  This file contains all functions that talk to the database.
#  Each function does ONE specific job (save, fetch, delete).
# ============================================================

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from flask import current_app

_tables_initialized = False


def get_db():
    """
    Opens a connection to the Supabase PostgreSQL database.
    Automatically initializes tables if they do not already exist.
    """
    global _tables_initialized
    db_url = current_app.config.get('DATABASE_URL') or os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL is not set. Please add DATABASE_URL in environment variables.")

    # Fix postgres:// URL scheme if provided by legacy tools
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # 4 second timeout prevents Vercel serverless function from timing out with 500/504
    conn = psycopg2.connect(db_url, connect_timeout=4)

    if not _tables_initialized:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE IF NOT EXISTS prompts (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        user_input TEXT NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        generated_prompt TEXT NOT NULL,
                        is_favorite INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
            _tables_initialized = True
        except Exception as e:
            conn.rollback()
            print(f"Warning: could not auto-create tables: {e}")

    return conn


def rows_to_dicts(rows):
    """
    Converts PostgreSQL Query Row objects to plain Python dicts.
    Also ensures the 'created_at' is a datetime object for template use.
    """
    result = []
    for row in rows:
        d = dict(row)
        if d.get('created_at') and isinstance(d['created_at'], str):
            try:
                date_str = d['created_at'].split('.')[0]
                d['created_at'] = datetime.strptime(
                    date_str, '%Y-%m-%d %H:%M:%S'
                )
            except (ValueError, TypeError):
                d['created_at'] = datetime.now()
        result.append(d)
    return result


# ============================================================
#  USER AUTHENTICATION FUNCTIONS
# ============================================================

def create_user(username, password_hash):
    """
    Inserts a new user into the users table.
    Returns the user id if successful, or None if username is taken or error.
    """
    try:
        db = get_db()
    except Exception as e:
        print(f"Database connection error in create_user: {e}")
        return None

    try:
        with db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                (username, password_hash)
            )
            row = cursor.fetchone()
            user_id = row['id'] if row else None
            db.commit()
        db.close()
        return user_id
    except psycopg2.IntegrityError:
        db.rollback()
        db.close()
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
        db.close()
        return None


def get_user_by_username(username):
    """
    Fetches a user from the users table by username.
    """
    db = None
    try:
        db = get_db()
        with db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            row = cursor.fetchone()
        db.close()
        if row:
            return dict(row)
        return None
    except Exception as e:
        if db:
            try:
                db.close()
            except Exception:
                pass
        raise e


def get_user_by_id(user_id):
    """
    Fetches a user from the users table by their ID.
    """
    try:
        db = get_db()
    except Exception as e:
        print(f"Database connection error in get_user_by_id: {e}")
        return None

    try:
        with db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
        db.close()
        if row:
            return dict(row)
        return None
    except Exception as e:
        print(f"Error in get_user_by_id: {e}")
        db.close()
        return None


# ============================================================
#  USER-SCOPED PROMPT FUNCTIONS
# ============================================================

def save_prompt(user_id, user_input, category, generated_prompt):
    """
    Inserts a new row into the prompts table associated with a user.
    """
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO prompts (user_id, user_input, category, generated_prompt) VALUES (%s, %s, %s, %s)",
                (user_id, user_input, category, generated_prompt)
            )
            db.commit()
        db.close()
    except Exception as e:
        print(f"Error saving prompt: {e}")


def get_all_prompts(user_id):
    """
    Fetches every saved prompt belonging to a specific user, newest first.
    """
    try:
        db = get_db()
        with db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM prompts WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
        db.close()
        return rows_to_dicts(rows)
    except Exception as e:
        print(f"Error getting all prompts: {e}")
        return []


def get_recent_prompts(user_id, limit=5):
    """
    Fetches the most recent N prompts for a specific user.
    """
    try:
        db = get_db()
        with db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM prompts WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
                (user_id, limit)
            )
            rows = cursor.fetchall()
        db.close()
        return rows_to_dicts(rows)
    except Exception as e:
        print(f"Error getting recent prompts: {e}")
        return []


def delete_prompt(prompt_id, user_id):
    """
    Deletes a single prompt row by its ID, ensuring it belongs to the user.
    """
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM prompts WHERE id = %s AND user_id = %s",
                (prompt_id, user_id)
            )
            db.commit()
        db.close()
    except Exception as e:
        print(f"Error deleting prompt: {e}")


def toggle_favorite(prompt_id, user_id):
    """
    Toggles the is_favorite column (0 -> 1, or 1 -> 0) for a prompt.
    Returns the new is_favorite status, or None if prompt not found/unauthorized.
    """
    try:
        db = get_db()
        with db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT is_favorite FROM prompts WHERE id = %s AND user_id = %s",
                (prompt_id, user_id)
            )
            row = cursor.fetchone()
            
            if not row:
                db.close()
                return None
                
            new_fav = 0 if row['is_favorite'] == 1 else 1
            
            cursor.execute(
                "UPDATE prompts SET is_favorite = %s WHERE id = %s AND user_id = %s",
                (new_fav, prompt_id, user_id)
            )
            db.commit()
        db.close()
        return new_fav
    except Exception as e:
        print(f"Error toggling favorite: {e}")
        return None

