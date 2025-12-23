# config.py
"""
Configuration module for The Voyager Flask application.
Loads environment variables from .env file and provides a Config class
for Flask app configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# override=True ensures .env values take precedence over system environment variables
load_dotenv(override=True)


class Config:
    """
    Flask application configuration class.
    All sensitive values are loaded from environment variables.
    """
    
    # Flask Secret Key
    # Used for session signing and CSRF token generation
    # Should be a long random string in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set")
    
    # OpenAI API Configuration
    # API key for gpt-5-nano model access
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable must be set")
    
    # MySQL Database Connection Settings
    # Hostname where MySQL server is running
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    
    # Name of the database to connect to
    DB_NAME = os.environ.get('DB_NAME', 'voyager_db')
    
    # MySQL username for authentication
    DB_USER = os.environ.get('DB_USER', 'voyager_user')
    
    # MySQL password for authentication
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    if not DB_PASSWORD:
        raise ValueError("DB_PASSWORD environment variable must be set")
    
    # Flask Session Configuration
    # Set to True in production with HTTPS, False for local development
    SESSION_COOKIE_SECURE = False
    
    # Ensure session cookies are only sent via HTTP (not JavaScript)
    SESSION_COOKIE_HTTPONLY = True
    
    # SameSite attribute for CSRF protection
    SESSION_COOKIE_SAMESITE = 'Lax'