"""
Configuration settings for the IdeaManager application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'idea_manager')

# Application settings
DATA_ACCESS_TYPE = os.getenv('DATA_ACCESS_TYPE', 'sql')  # 'sql' or 'orm'
JSON_BACKUP_FILE = os.getenv('JSON_BACKUP_FILE', 'banco_ideas.json')

# Web interface settings
WEB_PORT = int(os.getenv('WEB_PORT', '7860'))
WEB_SHARE = os.getenv('WEB_SHARE', 'False').lower() == 'true'
