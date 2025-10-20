"""Configure flask app """

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class."""

    # load env variables
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    APP_TITLE = os.getenv('APP_TITLE', 'Default App Title')
    
    LOG_DIRECTORY = os.getenv('LOG_DIRECTORY', 'logs')
    LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'ERROR').upper())
    LOG_FILE = os.getenv('LOG_FILE', 'default.log')
    
    API_HOST = os.getenv('API_HOST', 'https://127.0.0.1')
    API_AUTH = os.getenv('API_AUTH', '')
        
    @staticmethod
    def configure_app(app):
        """Initial Application Configuration"""

        app.config.from_object(Config) # pass Config to the application
                
        # set up logging
        log_dir = Path(Config.LOG_DIRECTORY)
        log_dir.mkdir(exist_ok=True)
        log_file_path = log_dir / Config.LOG_FILE
        logging.basicConfig(
            level=Config.LOG_LEVEL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path),
                logging.StreamHandler()
            ]
        )
                
        logger = logging.getLogger(__name__)
        logger.info("Application configuration initialized successfully")
