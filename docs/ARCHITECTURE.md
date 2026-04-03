# Trading Bot - Complete Architecture & Workflow Documentation

## 📋 Table of Contents
1. [Objective](#objective)
2. [Architecture Overview](#architecture-overview)
3. [Project Structure](#project-structure)
4. [Component Details](#component-details)
5. [Workflow Diagram](#workflow-diagram)
6. [Data Flow](#data-flow)
7. [Error Handling](#error-handling)
8. [Key Features](#key-features)
9. [Optional Enhancements](#optional-enhancements)

---

## 🎯 Objective

Create a **production-quality Python CLI trading bot** that interacts with **Binance Futures Testnet (USDT-M)**.

### Goals:
- Place MARKET and LIMIT orders on Binance Testnet
- Support BUY and SELL operations
- Provide user-friendly CLI experience (both interactive and command-line)
- Validate all user inputs before sending to API
- Log all requests, responses, and errors securely
- Handle errors gracefully with clear messages
- No real funds at risk (testnet environment)
- Production-grade code quality and security

---

## 🏗️ Architecture Overview

The trading bot follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│         CLI Layer (cli.py)              │
│  - Parse arguments (argparse)           │
│  - Interactive prompts                  │
│  - Format & display output              │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     Validation Layer (validators.py)    │
│  - Symbol validation                    │
│  - Side (BUY/SELL) validation           │
│  - Order type validation                │
│  - Quantity & Price validation          │
│  - Live symbol validation (optional)    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    Business Logic (orders.py)           │
│  - OrderManager class                   │
│  - Orchestrate validation + client      │
│  - Parse API response                   │
│  - Logging integration                  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     API Client Layer (client.py)        │
│  - BinanceClient wrapper                │
│  - Testnet connection                   │
│  - Retry logic (exponential backoff)    │
│  - Request ID tracking                  │
│  - Exception handling                   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   Logging & Utilities                   │
│  - logging_config.py - Setup            │
│  - logging_filter.py - Redaction        │
│  - symbol_validator.py - Live check     │
│  - config.py - Centralized config       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   Binance Futures Testnet API           │
│  https://testnet.binancefuture.com      │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Trade_bot/
│
├── bot/                          # Main package
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # CLI interface (CRITICAL FILE)
│   ├── client.py                # Binance API wrapper
│   ├── orders.py                # Order business logic
│   ├── validators.py            # Input validation functions
│   ├── config.py                # Centralized configuration
│   ├── logging_config.py        # Logging setup
│   ├── logging_filter.py        # Secret redaction (NEW)
│   └── symbol_validator.py      # Live symbol validation (NEW)
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # Technical architecture
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── TESTING.md               # Testing procedures
│   ├── PERFORMANCE.md           # Performance tuning
│   ├── ENHANCEMENTS.md          # Optional features
│   └── CONTRIBUTING.md          # Contributing guide
│
├── logs/                         # Log directory
│   └── bot.log                  # Main log file (auto-created)
│
├── v-env/                        # Virtual environment
│   └── (Python packages)
│
├── cli.py                        # Entry point
├── .env                          # API credentials (NOT in git)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── requirements.lock             # Exact versions (reproducible installs)
├── README.md                     # User guide
├── ARCHITECTURE.md              # Architecture reference
└── .git/                         # Git repository
```

---

## 📦 Component Details

### 1. **bot/config.py** (Centralized Configuration)
**Purpose:** Single source of truth for all constants and configuration values

**Features:**
- Loads environment variables from `.env` via `python-dotenv`
- Validates API credentials at startup
- Centralizes all magic constants
- Configurable logging parameters
- Retry and timeout settings

**Key Configuration:**
```python
BINANCE_TESTNET_BASE_URL = "https://testnet.binancefuture.com"
MAX_RETRIES = 2  # Network error retries
RETRY_DELAY = 0.5  # Seconds between retries
LOG_FILE_PATH = "logs/bot.log"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5MB per file
LOG_BACKUP_COUNT = 5  # Keep 5 backup files
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
```

---

### 2. **bot/logging_config.py** (Logging Setup)
**Purpose:** Configure centralized, secure logging

**Features:**
- Rotating file handler (5MB per file, 5 backups)
- Console handler for errors only
- Integration with Redis (optional)
- Automatic secret redaction via `RedactingFilter`

**Example Log Entry:**
```
2026-04-03 15:59:21 - trading_bot - INFO - Placing order - Symbol: BTCUSDT, Side: BUY, Type: MARKET, Qty: 0.01
2026-04-03 15:59:21 - trading_bot - DEBUG - [req_id=f19b9435] Creating MARKET order...
2026-04-03 15:59:22 - trading_bot - INFO - [req_id=f19b9435] Order placed successfully - ID: 13020106208
```

---

### 3. **bot/logging_filter.py** (Secret Redaction - NEW)
**Purpose:** Prevent sensitive information in logs

**Features:**
- Redacts API keys and secrets
- Redacts Bearer tokens
- Redacts passwords
- Pattern matching for common credentials formats
- Applies to both file and console handlers

**Redaction Examples:**
```
Before:  "Error: API_KEY=HoGELJ0YkEKWExPQWtS8yOngTI5sEHOcdXIlCfdwwZvEfowu2k4FSp0VqLHQ9kpU"
After:   "Error: API_KEY=***REDACTED***"

Before:  "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
After:   "Bearer ***REDACTED***"
```

---

### 4. **bot/symbol_validator.py** (Live Symbol Validation - NEW)
**Purpose:** Validate trading symbols against live Binance API

**Features:**
- Fetches available USDT-M perpetual symbols from Binance
- Caches results to avoid repeated API calls
- Falls back gracefully if API unavailable
- Provides symbol details (base asset, quote asset, status)

**Usage:**
```python
from bot.symbol_validator import symbol_validator

# Get all available symbols
symbols = symbol_validator.get_available_symbols()

# Validate one symbol
if symbol_validator.validate_symbol_exists('BTCUSDT'):
    print("BTCUSDT is trading")
else:
    print("BTCUSDT not found or not trading")

# Get details
details = symbol_validator.get_symbol_details('ETHUSDT')
# Returns: {'symbol': 'ETHUSDT', 'base': 'ETH', 'quote': 'USDT', 'status': 'TRADING'}
```

---

### 5. **bot/cli.py** (CLI Interface - CRITICAL)
**Purpose:** Handle all user interaction and command parsing

**Key Functions:**
- `create_parser()` — Creates argparse ArgumentParser
- `get_interactive_inputs()` — Prompts user when no args provided
- `format_order_summary()` — Pretty-print order details
- `format_order_response()` — Display API response
- `format_error_message()` — Display errors  
- `main()` — Main entry point

**Responsibilities:**
- Parse command-line arguments
- Determine interactive or direct mode
- Call validators and order placement
- Format and display responses
- Handle exceptions gracefully

---

### 6. **bot/validators.py** (Input Validation)
**Purpose:** Validate all user inputs before API calls

**Functions:**
- `validate_symbol(symbol, live_validation=False)` — Format and optional live check
- `validate_side(side)` — BUY or SELL
- `validate_order_type(order_type)` — MARKET or LIMIT
- `validate_quantity(quantity)` — Positive number
- `validate_price(price, order_type)` — Price validation
- `validate_all_inputs(...)` — Orchestrates all validators

**Live Validation Mode:**
```python
# Validate with live API check (slower but ensures symbol exists)
validate_symbol("btcusdt", live_validation=True)

# Validate format only (fast, default behavior)
validate_symbol("btcusdt", live_validation=False)
```

---

### 7. **bot/orders.py** (Business Logic)
**Purpose:** Orchestrate order placement workflow

**Workflow:**
```
1. Validate inputs
2. Log request with parameters
3. Call client.create_order()
4. Parse response
5. Log result
6. Return to CLI
```

**Example Response:**
```python
{
    "success": True,
    "order_id": 13020106208,
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "status": "NEW",
    "quantity": 0.01,
    "executed_qty": 0.0,
    "average_price": 0.0,
    "price": 0.0,
    "raw_response": {...}
}
```

---

### 8. **bot/client.py** (Binance API Wrapper)
**Purpose:** Handle all Binance API communication

**Features:**
- Retry logic with exponential backoff (network errors only)
- Request ID tracking `[req_id=xxxxx]` in logs
- Distinction between API errors (no retry) and network errors (with retry)
- Exception categorization and logging

**Retry Strategy:**
- MAX_RETRIES = 2 (2 attempts total)
- RETRY_DELAY = 0.5 seconds between attempts
- Only retries on `BinanceRequestException` (network issues)
- Does NOT retry on `BinanceAPIException` (validation errors)

---

## 🔄 Complete Order Placement Flow

```
┌─────────────────────────────────────────┐
│            START: User Input            │
│   python cli.py place-order [OPTIONS]   │
└────────────────┬────────────────────────┘
                 │
                 ▼
     ┌──────────────────────────────────┐
     │  Arguments provided?              │
     └────┬──────────────────────────┬───┘
          │                          │
         YES                         NO
          │                          │
          ▼                          ▼
   ┌─────────────────┐      ┌──────────────────┐
   │ Parse from CLI  │      │ Interactive Mode │
   └────────┬────────┘      │ - Prompt symbol  │
            │               │ - Prompt side    │
            │               │ - Prompt type    │
            │               │ - Prompt qty     │
            │               │ - Prompt price   │
            │               └────────┬─────────┘
            └───────────┬────────────┘
                        ▼
            ┌──────────────────────────┐
            │    DISPLAY SUMMARY       │
            │ Show order parameters    │
            └────────┬─────────────────┘
                     ▼
            ┌──────────────────────────┐
            │  VALIDATE INPUTS         │
            │  - Symbol format         │
            │  - Side is BUY/SELL      │
            │  - Type is MARKET/LIMIT  │
            │  - Qty positive          │
            │  - Price valid (if LIMIT)│
            └────┬──────────────────┬──┘
                 │                  │
              VALID              INVALID
                 │                  │
                 │                  ▼
                 │          ┌──────────────────┐
                 │          │ ERROR MESSAGE    │
                 │          │ Exit code: 1     │
                 │          └──────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │   CONNECT TO BINANCE     │
        │  - Load API credentials  │
        │  - Validate auth         │
        │  - Connect to testnet    │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │   CALL BINANCE API       │
        │  - Build params          │
        │  - Add request ID        │
        │  - Log request           │
        │  - futures_create_order()│
        └────┬──────────────────┬──┘
             │                  │
          SUCCESS            FAILURE
             │                  │
             │         ┌────────┴────────┐
             │         │                 │
             │    NETWORK ERROR      API ERROR
             │         │                 │
             │         ▼                 ▼
             │    Retry?           [No Retry]
             │         │                 │
             │     YES/NO             Log &
             │         │              Report
             │         ▼                 │
             │    Retried?               │
             │         │                 │
             │     YES/NO                │
             │         │                 │
             └─────────┼─────────────────┘
                       ▼
            ┌──────────────────────────┐
            │  PARSE RESPONSE          │
            │  - Extract order ID      │
            │  - Extract status        │
            │  - Format to dict        │
            └────────┬─────────────────┘
                     ▼
            ┌──────────────────────────┐
            │  DISPLAY SUCCESS         │
            │  Show response table     │
            │  Exit code: 0            │
            └──────────────────────────┘
```

---

## ⚠️ Error Handling

### Comprehensive Error Matrix

| Layer | Error Type | Handler | Action | User Message |
|-------|-----------|---------|--------|--------------|
| Bootstrap | Missing .env | config.py | RuntimeError | "Missing required environment variables: API_KEY, API_SECRET" |
| Bootstrap | Invalid API key format | client.py | BinanceAPIException [400] | "Binance API Error [400]: Invalid API key format" |
| CLI | Missing command | cli.py | argparse | Show help; exit 0 |
| CLI | Missing required args | cli.py | ValueError | "Missing required arguments. Use --help for usage" |
| Validator | Invalid symbol | validators.py | ValueError | "Symbol must end with USDT (e.g., BTCUSDT)" |
| Validator | Invalid side | validators.py | ValueError | "Side must be BUY or SELL" |
| Validator | Invalid order type | validators.py | ValueError | "Order type must be MARKET or LIMIT" |
| Validator | Invalid quantity | validators.py | ValueError | "Quantity must be positive" |
| Validator | Missing LIMIT price | validators.py | ValueError | "Price is required for LIMIT orders" |
| API | Authentication error | client.py | BinanceAPIException [401] | "Binance API Error [401]: ..." (no retry) |
| API | Rate limiting | client.py | BinanceAPIException [429] | "Rate limited by Binance; please retry later" (with retry) |
| API | Network timeout | client.py | BinanceRequestException | "Network error; retrying..." (with retry, max 2 attempts) |
| API | Invalid order params | client.py | BinanceAPIException [400] | "Binance API Error [400]: ..." (no retry) |
| API | Insufficient balance | client.py | BinanceAPIException [400] | Shows Binance's error message |
| Network | Connection refused | client.py | BinanceRequestException | Retry up to 2 times; then display error |

---

## ✨ Key Features

### 1. **Production-Grade Security**
- API credentials in `.env` (not in code)
- Automatic secret redaction in logs
- No hardcoded values
- Input validation prevents injection attacks

### 2. **Dual Interface**
- Interactive mode (guided prompts)
- CLI mode (automation-friendly)
- Both paths normalize inputs consistently

### 3. **Professional Logging**
- Rotating file handler (5MB per file)
- Request ID tracking `[req_id=xxxxx]`
- Separate DEBUG and ERROR levels
- Automatic secret redaction

### 4. **Error Resilience**
- Network error retry logic (exponential backoff)
- Distinction between temporary and permanent errors
- Graceful fallbacks
- Clear error messages to users

### 5. **Maintainability**
- Centralized configuration
- Modular architecture (layers of responsibility)
- Type hints throughout
- Comprehensive documentation

### 6. **Reproducible Deployments**
- `requirements.lock` for exact versions
- Version pinning in `requirements.txt`
- Consistent behavior across environments

---

## 🔧 Optional Enhancements

The bot comes with optional enhancements that can be enabled:

### 1. **Secret Redaction** ✅ IMPLEMENTED
- Implemented in `bot/logging_filter.py`
- Automatically masks API keys and secrets
- Integrated into `logging_config.py`
- Configurable patterns for custom sensitivity

### 2. **Live Symbol Validation** ✅ IMPLEMENTED
- Implemented in `bot/symbol_validator.py`
- Validates symbols against live Binance API
- Optional per-validation (format check by default)
- Graceful fallback if API unavailable

### 3. **Reproducible Installs** ✅ IMPLEMENTED
- `requirements.lock` file created
- Use with: `pip install -r requirements.lock`
- Ensures identical versions across all machines

---

## 🚀 Execution Examples

### Example 1: Interactive Mode
```bash
$ python cli.py place-order
Enter symbol (e.g., BTCUSDT): btcusdt
Enter side (BUY/SELL): buy
Enter order type (MARKET/LIMIT): market
Enter quantity: 0.01

===================================
          ORDER SUMMARY
===================================
Symbol     : BTCUSDT
Side       : BUY
Type       : MARKET
Quantity   : 0.01

===================================
            RESPONSE
===================================
Order ID        : 13020106208
Status          : NEW

✅ Order placed successfully
```

### Example 2: CLI Mode
```bash
$ python cli.py place-order --symbol ETHUSDT --side SELL --type LIMIT --qty 1 --price 2500
```

### Example 3: With Live Symbol Validation
```python
# In validators.py, enable live validation:
validate_symbol("BTCUSDT", live_validation=True)
# Validates against Binance API for true availability
```

---

## 📝 Summary

### What Makes It Production-Quality:
- ✅ Modular layered architecture
- ✅ Comprehensive error handling
- ✅ Security: Secret redaction, no hardcoded values
- ✅ Logging: Request tracking, rotation, severity levels
- ✅ Performance: Retry logic, connection pooling ready
- ✅ Maintainability: Centralized config, type hints
- ✅ Testing: Testnet isolation, reproducibility
- ✅ Documentation: Architecture, deployment, testing guides
- ✅ Automation: Exit codes, structured output
- ✅ Resilience: Graceful degradation, meaningful errors

---

**See Also:** [README.md](../README.md) · [DEPLOYMENT.md](DEPLOYMENT.md) · [TESTING.md](TESTING.md) · [ENHANCEMENTS.md](ENHANCEMENTS.md)
