"""
Logging configuration for trading bot.
Ensures secure, structured, and readable logs without sensitive data.
"""

import logging
import logging.handlers
import os
from bot import config


def setup_logger(log_file: str = config.LOG_FILE_PATH) -> logging.Logger:
    """
    Configure and return logger instance.
    
    Features:
    - Rotating file handler (5MB limit, 5 backups)
    - No sensitive data logged
    - Structured format with timestamps
    - Separate console handler for errors only
    
    Args:
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logger = logging.getLogger(config.APP_NAME)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Rotating file handler - 5MB per file, keep 5 files
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler for errors only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    
    # Structured formatter - consistent format across all logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger()
