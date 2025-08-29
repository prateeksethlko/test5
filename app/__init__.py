import os
import logging
from flask import Flask, send_from_directory, jsonify
from config import config
from app.services.openai_service import OpenAIService
from app.services.chatbot_service import ChatbotService
from app.api.chat_routes import create_chat_routes

def create_app(config_name='default'):
    """Application factory pattern."""
    
    # IMPORTANT: Fix static folder path
    app = Flask(__name__, 
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'),
                static_url_path='')
    
    app.config.from_object(config[config_name])
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting application in {config_name} mode")
    logger.info(f"Static folder: {app.static_folder}")
    
    try:
        # Initialize services
        openai_service = OpenAIService(
            api_key=app.config['AZURE_OPENAI_API_KEY'],
            endpoint=app.config['AZURE_OPENAI_ENDPOINT'],
            deployment=app.config['AZURE_OPENAI_DEPLOYMENT'],
            api_version=app.config['AZURE_API_VERSION']
        )
        
        chatbot_service = ChatbotService(openai_service)
        
        # Register API routes
        app.register_blueprint(create_chat_routes(chatbot_service))
        
        # Static file routes
        @app.route('/')
        def index():
            try:
                return send_from_directory(app.static_folder, 'index.html')
            except FileNotFoundError:
                return """
                <html>
                    <head><title>Static File Missing</title></head>
                    <body>
                        <h1>⚠️ Static File Issue</h1>
                        <p>index.html not found in static folder: <code>{}</code></p>
                        <p><a href="/test">Test Page</a> | <a href="/health">Health Check</a></p>
                    </body>
                </html>
                """.format(app.static_folder), 404
        
        @app.route('/<path:filename>')
        def static_files(filename):
            try:
                return send_from_directory(app.static_folder, filename)
            except FileNotFoundError:
                return f"File '{filename}' not found", 404
        
        @app.route('/test')
        def test_page():
            return """
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1>✅ Flask is Working!</h1>
                    <p>Static folder: <code>{}</code></p>
                    <p><a href="/">Home</a> | <a href="/health">Health Check</a></p>
                </body>
            </html>
            """.format(app.static_folder)
        
        @app.route('/favicon.ico')
        def favicon():
            return '', 204
        
        @app.route('/health')
        def health_check():
            return jsonify({
                "status": "healthy", 
                "service": "informatica-access-chatbot",
                "static_folder": app.static_folder,
                "endpoints": [
                    "GET  /",
                    "GET  /health", 
                    "GET  /test",
                    "POST /api/chat"
                ]
            })
        
        logger.info("Application initialized successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
