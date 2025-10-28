"""Configure flask app """

import os
import logging
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from flask_session import Session

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
    
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
    SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR', 'flask_session')
    SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'True').lower() == 'true'
    SESSION_USE_SIGNER = os.getenv('SESSION_USE_SIGNER', 'True').lower() == 'true'
    SESSION_KEY_PREFIX = os.getenv('SESSION_KEY_PREFIX', 'session:')
    SESSION_LIFETIME_MINUTES = int(os.getenv('SESSION_LIFETIME_MINUTES', '30'))
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=SESSION_LIFETIME_MINUTES)    
    SESSION_FILE_THRESHOLD = int(os.getenv('SESSION_FILE_THRESHOLD', '500'))
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
        
    @staticmethod
    def configure_app(app):
        """Initial Application Configuration"""

        app.config.from_object(Config) # pass Config to the application

        # Initialize Flask-Session
        session_dir = Path(Config.SESSION_FILE_DIR)
        session_dir.mkdir(exist_ok=True, mode=0o700)        
        Session(app)
                
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
        logger.info(f"Session directory: {session_dir.absolute()}")        
