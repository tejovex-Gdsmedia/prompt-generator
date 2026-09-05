# ============================================================
#  app/routes.py — URL Routes (Version 2)
#
#  This file maps URLs to Python functions.
#  Updates include user auth, scope checking, and favorite endpoints.
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import (
    save_prompt, get_all_prompts, delete_prompt, get_recent_prompts,
    create_user, get_user_by_username, get_user_by_id, toggle_favorite
)
from app.prompt_builder import build_prompt

# Create a Blueprint named 'main'
main = Blueprint('main', __name__)


# ============================================================
#  ROUTE 1: Home Page — GET / POST
# ============================================================
@main.route('/', methods=['GET', 'POST'])
def index():
    """
    GET  → Show the prompt generator form
    POST → Read form data, build prompt, save if logged in, show result
    """
    generated_prompt = None
    user_input = ''
    selected_category = ''
    
    # Check if user is logged in
    user_id = session.get('user_id')

    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        selected_category = request.form.get('category', 'General')

        if user_input:
            # Build the prompt
            generated_prompt = build_prompt(user_input, selected_category)

            # Save only if user is logged in
            if user_id:
                save_prompt(user_id, user_input, selected_category, generated_prompt)
            else:
                flash('Prompt generated! Log in or Register to save your prompts permanently.', 'warning')
        else:
            flash('Please enter a goal or task before generating.', 'warning')

    # Fetch recent history if logged in
    recent = get_recent_prompts(user_id, 5) if user_id else []

    return render_template(
        'index.html',
        generated_prompt=generated_prompt,
        user_input=user_input,
        selected_category=selected_category,
        recent=recent
    )


# ============================================================
#  ROUTE 2: Register — GET / POST
# ============================================================
@main.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles new user signups.
    """
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('All fields are required.', 'warning')
            return render_template('register.html')

        # Check if user exists
        try:
            existing_user = get_user_by_username(username)
        except Exception as e:
            flash('Database connection failed. Please check your Supabase DATABASE_URL configuration in Vercel.', 'danger')
            return render_template('register.html')

        if existing_user:
            flash('Username is already taken. Choose another one.', 'warning')
            return render_template('register.html')

        # Create user
        hashed_password = generate_password_hash(password)
        new_user_id = create_user(username, hashed_password)
        
        if new_user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Could not create account. Please check your database settings.', 'danger')

    return render_template('register.html')


# ============================================================
#  ROUTE 3: Login — GET / POST
# ============================================================
@main.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login sessions.
    """
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('All fields are required.', 'warning')
            return render_template('login.html')

        try:
            user = get_user_by_username(username)
        except Exception as e:
            flash('Database connection failed. Please check your Supabase DATABASE_URL configuration in Vercel.', 'danger')
            return render_template('login.html')

        if user and check_password_hash(user['password_hash'], password):
            # Save user identity in Flask session
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('main.index'))
            
        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


# ============================================================
#  ROUTE 4: Logout
# ============================================================
@main.route('/logout')
def logout():
    """
    Clears session variables.
    """
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


# ============================================================
#  ROUTE 5: History Page — GET
# ============================================================
@main.route('/history')
def history():
    """
    Fetches saved prompts for the logged-in user.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your prompt history.', 'warning')
        return redirect(url_for('main.login'))

    all_prompts = get_all_prompts(user_id)
    return render_template('history.html', prompts=all_prompts)


# ============================================================
#  ROUTE 6: Delete Prompt — POST
# ============================================================
@main.route('/delete/<int:prompt_id>', methods=['POST'])
def delete(prompt_id):
    """
    Deletes a user's prompt by ID.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to delete prompts.', 'warning')
        return redirect(url_for('main.login'))

    delete_prompt(prompt_id, user_id)
    flash('Prompt deleted successfully.', 'success')
    return redirect(url_for('main.history'))


# ============================================================
#  ROUTE 7: Toggle Favorite — POST (AJAX API)
# ============================================================
@main.route('/favorite/<int:prompt_id>', methods=['POST'])
def favorite(prompt_id):
    """
    Endpoint for toggling favorite status of a prompt.
    Returns JSON.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required.'}), 401

    new_status = toggle_favorite(prompt_id, user_id)
    if new_status is None:
        return jsonify({'error': 'Prompt not found or unauthorized.'}), 404

    return jsonify({
        'success': True,
        'is_favorite': new_status
    })
