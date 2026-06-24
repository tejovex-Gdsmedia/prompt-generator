# ============================================================
#  run.py — Application Entry Point
#
#  This is the file you run to start the Flask development server.
#  Command: python run.py
#
#  It imports create_app() from the app package, which builds
#  and configures the Flask application, then starts the server.
# ============================================================

from app import create_app

# Create the Flask application using the factory function
app = create_app()

if __name__ == '__main__':
    # Start the development server
    # debug=True is set in config.py — it auto-reloads on file changes
    app.run()
