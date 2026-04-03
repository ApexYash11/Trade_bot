"""
Configuration constants for trading bot.
Centralized configuration to avoid hardcoded values across the project.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
BINANCE_TESTNET_BASE_URL = "https://testnet.binancefuture.com"
BINANCE_FUTURES_API_KEY = os.getenv("API_KEY")
BINANCE_FUTURES_API_SECRET = os.getenv("API_SECRET")

# Validate API credentials are present
missing_vars = []
if not BINANCE_FUTURES_API_KEY:
    missing_vars.append("API_KEY")
if not BINANCE_FUTURES_API_SECRET:
    missing_vars.append("API_SECRET")

if missing_vars:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(missing_vars)}. "
        "Please set API_KEY and API_SECRET in .env file. "
        "See README.md for setup instructions."
    )

# Retry Configuration
MAX_RETRIES = 2  # Maximum retry attempts for network errors
RETRY_DELAY = 0.5  # Seconds to wait between retries

# Logging Configuration
# Compute absolute path to logs directory relative to this config module
_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CONFIG_DIR)
LOG_FILE_PATH = os.path.join(_PROJECT_ROOT, "logs", "bot.log")
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
