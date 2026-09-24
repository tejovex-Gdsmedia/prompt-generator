# ============================================================
#  app/models.py — Database Query Functions (Supabase PostgreSQL)
# ============================================================

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from flask import current_app

# Fallback connection string for Supabase PostgreSQL
FALLBACK_DATABASE_URL = "postgresql://postgres:PromptGen2024Secure@db.wrpcdshtlbqrbguffwnn.supabase.co:5432/postgres?sslmode=require"


def get_db():
    """
    Opens a connection to the Supabase PostgreSQL database.
    Ensures SSL mode is enabled for production and returns (conn, cursor).
    Optimized for Vercel serverless cold starts.
    """
    database_url = os.environ.get('DATABASE_URL', '')
    if not database_url and current_app:
        try:
            database_url = current_app.config.get('DATABASE_URL', '')
        except Exception:
            pass

    if not database_url:
        print("[DB INFO] DATABASE_URL not set in environment or config. Using fallback Supabase URL.")
        database_url = FALLBACK_DATABASE_URL

    # Fix postgres:// URL scheme if provided by legacy tools
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Supabase requires SSL in production
    if 'sslmode' not in database_url:
        separator = '&' if '?' in database_url else '?'
        database_url += f'{separator}sslmode=require'

    print(f"[DB INFO] Connecting to database (URL prefix): {database_url[:50]}...")

    try:
        # Connect without restrictive timeout to survive Vercel cold starts
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cursor
    except Exception as e:
        print(f"[DB ERROR] Database connection failed: {e}")
        raise e


def rows_to_dicts(rows):
    """
    Converts PostgreSQL Query Row objects to plain Python dicts.
    Ensures 'created_at' is a datetime object for template rendering.
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

def create_user(username, email, password_hash):
    """
    Inserts a new user into the users table with username and email.
    Returns the user id if successful, or None if taken/error.
    """
    try:
        conn, cursor = get_db()
    except Exception as e:
        print(f"[DB ERROR] Connection failed in create_user: {e}")
        return None

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (username, email, password_hash)
        )
        row = cursor.fetchone()
        user_id = row['id'] if row else None
        conn.commit()
        return user_id
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print(f"[DB ERROR] Integrity error in create_user: {e}")
        return None
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Error creating user: {e}")
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def get_user_by_username(username):
    """
    Fetches a user from the users table by username.
    Returns dict with id, username, email, password_hash or None.
    """
    try:
        conn, cursor = get_db()
    except Exception as e:
        print(f"[DB ERROR] Connection failed in get_user_by_username: {e}")
        return None

    try:
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = %s",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        print(f"[DB ERROR] Error in get_user_by_username: {e}")
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def get_user_by_email(email):
    """
    Fetches a user from the users table by email.
    Returns dict with id, username, email or None.
    """
    try:
        conn, cursor = get_db()
    except Exception as e:
        print(f"[DB ERROR] Connection failed in get_user_by_email: {e}")
        return None

    try:
        cursor.execute(
            "SELECT id, username, email FROM users WHERE email = %s",
            (email,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        print(f"[DB ERROR] Error in get_user_by_email: {e}")
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def get_user_by_id(user_id):
    """
    Fetches a user from the users table by their ID.
    """
    try:
        conn, cursor = get_db()
    except Exception as e:
        print(f"[DB ERROR] Connection failed in get_user_by_id: {e}")
        return None

    try:
        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        print(f"[DB ERROR] Error in get_user_by_id: {e}")
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


# ============================================================
#  USER-SCOPED PROMPT FUNCTIONS
# ============================================================

def save_prompt(user_id, user_input, category, generated_prompt):
    """
    Inserts a new row into the prompts table associated with a user.
    """
    try:
        conn, cursor = get_db()
    except Exception as e:
        print(f"[DB ERROR] Connection failed in save_prompt: {e}")
        return None

    try:
        cursor.execute(
            "INSERT INTO prompts (user_id, user_input, category, generated_prompt) VALUES (%s, %s, %s, %s)",
            (user_id, user_input, category, generated_prompt)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Error saving prompt: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def get_all_prompts(user_id):
    """
    Fetches every saved prompt belonging to a specific user, newest first.
    """
    try:
        conn, cursor = get_db()
    except Exception as e:
        print(f"[DB ERROR] Connection failed in get_all_prompts: {e}")
        return []

    try:
        cursor.execute(
            "SELECT * FROM prompts WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        return rows_to_dicts(rows)
    except Exception as e:
        print(f"[DB ERROR] Error getting all prompts: {e}")
        return []
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def get_recent_prompts(user_id, limit=5):
    """
    Fetches the most recent N prompts for a specific user.
    """
    try:
        conn, cursor = get_db()
    except Exception as e:
        print(f"[DB ERROR] Connection failed in get_recent_prompts: {e}")
        return []

    try:
        cursor.execute(
            "SELECT * FROM prompts WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        return rows_to_dicts(rows)
    except Exception as e:
        print(f"[DB ERROR] Error getting recent prompts: {e}")
        return []
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def delete_prompt(prompt_id, user_id):
    """
    Deletes a single prompt row by its ID, ensuring it belongs to the user.
    """
    try:
        conn, cursor = get_db()
    except Exception as e:
        print(f"[DB ERROR] Connection failed in delete_prompt: {e}")
        return

    try:
        cursor.execute(
            "DELETE FROM prompts WHERE id = %s AND user_id = %s",
            (prompt_id, user_id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Error deleting prompt: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def toggle_favorite(prompt_id, user_id):
    """
    Toggles the is_favorite column (0 -> 1, or 1 -> 0) for a prompt.
    Returns the new is_favorite status, or None if prompt not found/unauthorized.
    """
    try:
        conn, cursor = get_db()
    except Exception as e:
        print(f"[DB ERROR] Connection failed in toggle_favorite: {e}")
        return None

    try:
        cursor.execute(
            "SELECT is_favorite FROM prompts WHERE id = %s AND user_id = %s",
            (prompt_id, user_id)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
            
        new_fav = 0 if row['is_favorite'] == 1 else 1
        
        cursor.execute(
            "UPDATE prompts SET is_favorite = %s WHERE id = %s AND user_id = %s",
            (new_fav, prompt_id, user_id)
        )
        conn.commit()
        return new_fav
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Error toggling favorite: {e}")
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
