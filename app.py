import os
import logging
from flask import Flask

# Import the config dictionary from your config.py file
# Make sure your config.py file defines a dictionary named 'config'
from config import config

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app(config_name):
    """
    Application factory function.
    Creates and configures the Flask application instance based on the
    provided configuration name (e.g., 'production').
    """
    app = Flask(__name__)

    # Load configuration settings from the 'config' dictionary
    # defined in config.py. The specific configuration (e.g., ProductionConfig)
    # is selected based on config_name.
    app.config.from_object(config[config_name])

    # --- Register Blueprints, Extensions, and Routes Here ---
    #
    # This is where you would typically register your Flask extensions
    # (like SQLAlchemy, Flask-Login, etc.) and your application's blueprints
    # to modularize your code.

    # Example: If you had a 'main' blueprint in a file like 'your_app_folder/main/routes.py'
    # from .main import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    # Define a basic route for the root URL
    # This serves as a simple entry point to verify the app is running.
    @app.route('/')
    def hello_world():
        """
        A simple route that returns a greeting, indicating the current
        environment the Flask app is running in.
        """
        return f"Hello from Flask app in **{config_name}** environment!"

    # You can add more routes directly here or organize them into blueprints
    # Example of another route:
    # @app.route('/info')
    # def info():
    #     return "This is an info page."

    # You might also have error handlers here
    # @app.errorhandler(404)
    # def page_not_found(e):
    #     return "404 Not Found", 404

    return app

# --- Application Initialization ---
# This block attempts to create the Flask application.
# It uses the 'FLASK_ENV' environment variable to determine which
# configuration to load from 'config.py'. If not set, it defaults to 'production'.
try:
    # 'app' is the WSGI callable that Gunicorn will look for.
    # It's an instance of the Flask application.
    app = create_app(os.environ.get('FLASK_ENV', 'production'))
except Exception as e:
    # If the application fails to create, log the error and exit.
    # This is crucial for debugging startup issues in deployment environments.
    logging.error(f"Failed to create application: {e}")
    exit(1)

# --- Local Development Entry Point (Not used by Gunicorn in Azure) ---
# This block is primarily for running the Flask app locally using 'python app.py'.
# In Azure App Service, Gunicorn (with the 'app:app' command) directly calls
# the 'app' object instantiated above, so this block is not executed in that context.
if __name__ == '__main__':
    # Azure App Service sets a 'PORT' environment variable.
    # We use 5000 as a default for local development.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
