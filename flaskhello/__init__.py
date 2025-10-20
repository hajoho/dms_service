"""Initialize flask app"""

import logging
from flask import Flask
from .config import Config
from .routes import main
    
def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize configuration
    Config.configure_app(app)
    
    # Register blueprints
    app.register_blueprint(main)
    
    # Configure logging for the app
    logger = logging.getLogger(__name__)
    logger.info("Flask application created successfully")
    
    return app
