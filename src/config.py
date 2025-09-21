"""
Configuration management for iRacing Telemetry Coach
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    TELEMETRY_WATCH_FOLDER = os.getenv('TELEMETRY_WATCH_FOLDER', str(BASE_DIR))
    TELEMETRY_ARCHIVE_FOLDER = os.getenv('TELEMETRY_ARCHIVE_FOLDER', str(BASE_DIR / 'processed'))
    CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', str(BASE_DIR / 'data' / 'chroma_db'))

    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # Pi Toolbox
    PI_TOOLBOX_PATH = os.getenv('PI_TOOLBOX_PATH', '')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'telemetry_coach.log'))

    # File Processing
    SUPPORTED_EXTENSIONS = ['.ibt']
    FILE_COMPLETION_WAIT_TIME = 5  # seconds to wait after file creation

    # Database
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    COLLECTION_NAME = 'iracing_telemetry'

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.BASE_DIR / 'data',
            cls.BASE_DIR / 'logs',
            cls.TELEMETRY_ARCHIVE_FOLDER,
            cls.CHROMA_DB_PATH
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        errors = []

        if not Path(cls.TELEMETRY_WATCH_FOLDER).exists():
            errors.append(f"Telemetry watch folder does not exist: {cls.TELEMETRY_WATCH_FOLDER}")

        if cls.PI_TOOLBOX_PATH and not Path(cls.PI_TOOLBOX_PATH).exists():
            errors.append(f"Pi Toolbox path does not exist: {cls.PI_TOOLBOX_PATH}")

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not set")

        return errors