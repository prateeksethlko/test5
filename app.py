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
        current_env = app.config.get('FLASK_ENV', 'default') # Access FLASK_ENV from app.config
        return f"Hello from Flask app in **{current_env}** environment! 🎉"

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

# --- Application Initialization for Gunicorn (Modified) ---
# When using an application factory, it's often more reliable to have Gunicorn
# directly call the factory function.
# We will no longer assign `app = create_app(...)` at the global scope directly.
# Instead, the Gunicorn startup command will be adjusted to call this function.

# The 'app' variable is still used here for local development,
# but in Azure, Gunicorn will use the specific startup command.
# For local debugging, we still need a global 'app' object if __name__ == '__main__' runs.
# However, for deployment, Gunicorn will directly use 'app:create_app()'.

# We'll define a variable that Gunicorn can "find" which is actually the result
# of calling create_app. This is a common pattern when the factory requires
# configuration at runtime.
# Here, 'application' is a common alternative name for the WSGI callable.
# We set this up to call create_app with the appropriate environment.
# Gunicorn can then be instructed to look for 'application'.
config_name_for_deploy = os.environ.get('FLASK_ENV', 'production')

try:
    application = create_app(config_name_for_deploy)
except Exception as e:
    logging.error(f"Failed to create application instance for deployment with config '{config_name_for_deploy}': {e}")
    raise # Re-raise to ensure deployment failure is properly reported

# --- Local Development Entry Point ---
# This block is primarily for running the Flask app locally using 'python app.py'.
# It uses the `application` object created above.
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # In local development, 'app' is often still used, but here we're using
    # the 'application' object created for Gunicorn's use.
    # If you prefer 'app' for local, you can add 'app = application' here.
    application.run(host='0.0.0.0', port=port, debug=True) # Changed to `debug=True` for local
