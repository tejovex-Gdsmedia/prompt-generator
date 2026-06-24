# ============================================================
#  app/models.py — Database Query Functions (Supabase PostgreSQL Version)
#
#  This file contains all functions that talk to the database.
#  Each function does ONE specific job (save, fetch, delete).
#
#  Key differences from SQLite version:
#  - Uses psycopg2 to connect to Supabase PostgreSQL database
#  - Uses %s as placeholder instead of ?
#  - Uses psycopg2.extras.RealDictCursor for dictionary-like rows
#  - Leverages postgresql RETURNING id for last insert IDs
# ============================================================

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from flask import current_app


def get_db():
    """
    Opens a connection to the Supabase PostgreSQL database.
    """
    conn = psycopg2.connect(current_app.config['DATABASE_URL'])
    return conn


def rows_to_dicts(rows):
    """
    Converts PostgreSQL Query Row objects to plain Python dicts.
    Also ensures the 'created_at' is a datetime object for template use.
    """
    result = []
    for row in rows:
        d = dict(row)
        # PostgreSQL TIMESTAMP yields native Python datetime objects
        # We ensure it's converted or handled correctly
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
    Returns the user id if successful, or None if username is taken.
    """
    db = get_db()
    try:
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
            (username, password_hash)
        )
        user_id = cursor.fetchone()['id']
        db.commit()
        db.close()
        return user_id
    except psycopg2.IntegrityError:
        # Username already exists
        db.rollback()
        db.close()
        return None
    except Exception:
        db.rollback()
        db.close()
        return None


def get_user_by_username(username):
    """
    Fetches a user from the users table by username.
    """
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT * FROM users WHERE username = %s",
        (username,)
    )
    row = cursor.fetchone()
    db.close()
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id):
    """
    Fetches a user from the users table by their ID.
    """
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,)
    )
    row = cursor.fetchone()
    db.close()
    if row:
        return dict(row)
    return None


# ============================================================
#  USER-SCOPED PROMPT FUNCTIONS
# ============================================================

def save_prompt(user_id, user_input, category, generated_prompt):
    """
    Inserts a new row into the prompts table associated with a user.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO prompts (user_id, user_input, category, generated_prompt) VALUES (%s, %s, %s, %s)",
        (user_id, user_input, category, generated_prompt)
    )
    db.commit()
    db.close()


def get_all_prompts(user_id):
    """
    Fetches every saved prompt belonging to a specific user, newest first.
    """
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT * FROM prompts WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    db.close()
    return rows_to_dicts(rows)


def get_recent_prompts(user_id, limit=5):
    """
    Fetches the most recent N prompts for a specific user.
    """
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT * FROM prompts WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    db.close()
    return rows_to_dicts(rows)


def delete_prompt(prompt_id, user_id):
    """
    Deletes a single prompt row by its ID, ensuring it belongs to the user.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM prompts WHERE id = %s AND user_id = %s",
        (prompt_id, user_id)
    )
    db.commit()
    db.close()


def toggle_favorite(prompt_id, user_id):
    """
    Toggles the is_favorite column (0 -> 1, or 1 -> 0) for a prompt.
    Returns the new is_favorite status, or None if prompt not found/unauthorized.
    """
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT is_favorite FROM prompts WHERE id = %s AND user_id = %s",
        (prompt_id, user_id)
    )
    row = cursor.fetchone()
    
    if not row:
        db.close()
        return None
        
    # Toggle logic: 1 if it was 0, 0 if it was 1
    new_fav = 0 if row['is_favorite'] == 1 else 1
    
    cursor.execute(
        "UPDATE prompts SET is_favorite = %s WHERE id = %s AND user_id = %s",
        (new_fav, prompt_id, user_id)
    )
    db.commit()
    db.close()
    return new_fav
