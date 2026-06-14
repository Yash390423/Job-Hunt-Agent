"""Configuration validation for the job hunt assistant."""

import os
from pathlib import Path

from dotenv import load_dotenv

from utils.logger import logger


load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

def validate_config() -> bool:
    """
    Validate all required configuration variables.
    
    Returns:
        True if all required configs are valid, False otherwise
    
    Raises:
        ValueError: If critical configuration is missing
    """
    missing_keys = []
    
    # Required API keys
    required_keys = [
        'GEMINI_API_KEY',
        'ADZUNA_APP_ID',
        'ADZUNA_APP_KEY',
    ]
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        error_msg = f"Missing required environment variables: {', '.join(missing_keys)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("✅ All required configurations validated successfully")
    return True

def check_database_config() -> bool:
    """Check if database is configured (optional for MVP)."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.warning("DATABASE_URL not configured. Using the local SQLite fallback.")
        return False
    logger.info("✅ Database configuration found")
    return True

if __name__ == "__main__":
    try:
        validate_config()
        check_database_config()
        print("✅ Configuration is valid!")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
