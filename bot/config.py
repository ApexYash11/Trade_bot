"""
Configuration constants for trading bot.
Centralized configuration to avoid hardcoded values across the project.
"""

import os

# API Configuration
BINANCE_TESTNET_BASE_URL = "https://testnet.binancefuture.com"
BINANCE_FUTURES_API_KEY = os.getenv("API_KEY")
BINANCE_FUTURES_API_SECRET = os.getenv("API_SECRET")

# Retry Configuration
MAX_RETRIES = 2  # Maximum retry attempts for network errors
RETRY_DELAY = 0.5  # Seconds to wait between retries

# Logging Configuration
LOG_FILE_PATH = "logs/bot.log"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 5

# Order Configuration
DEFAULT_TIME_IN_FORCE = "GTC"  # Good-Til-Cancelled

# Application Configuration
APP_NAME = "trading_bot"
APP_VERSION = "1.0.0"

# Exit Codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
