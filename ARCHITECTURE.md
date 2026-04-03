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

---

## 🎯 Objective

Create a **production-quality Python CLI trading bot** that interacts with **Binance Futures Testnet (USDT-M)**.

### Goals:
- Place MARKET and LIMIT orders on Binance Testnet
- Support BUY and SELL operations
- Provide user-friendly CLI experience (both interactive and command-line)
- Validate all user inputs before sending to API
- Log all requests, responses, and errors
- Handle errors gracefully with clear messages
- No real funds at risk (testnet environment)

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
│  - API call handling                    │
│  - Exception handling                   │
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
trading_bot/
│
├── bot/                          # Main package
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # CLI interface (CRITICAL FILE)
│   ├── client.py                # Binance API wrapper
│   ├── orders.py                # Order business logic
│   ├── validators.py            # Input validation functions
│   └── logging_config.py        # Logging setup
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
├── README.md                     # User guide
├── ARCHITECTURE.md              # This file
└── .git/                         # Git repository
```

---

## 📦 Component Details

### 1. **cli.py** (Entry Point)
**Purpose:** Simple entry point that delegates to `bot.cli.main()`

```python
from bot.cli import main

if __name__ == '__main__':
    main()
```

**Why separate?** Allows running with `python cli.py` from project root

---

### 2. **bot/cli.py** (CLI Interface - CRITICAL)
**Purpose:** Handle all user interaction and command parsing

**Key Functions:**
- `create_parser()` — Creates argparse ArgumentParser with subcommands
- `get_interactive_inputs()` — Prompts user for inputs when no args provided
- `format_order_summary()` — Pretty-print order details
- `format_order_response()` — Display API response
- `format_error_message()` — Display errors with ❌ emoji
- `main()` — Main CLI entry point

**Responsibilities:**
- Parse command-line arguments
- Determine if interactive or direct mode
- Call validators (via OrderManager)
- Call order placement (via OrderManager)
- Format and display responses
- Handle exceptions and show user-friendly errors

**Example Flow:**
```
User runs: python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
                    ↓
Parser extracts arguments
                    ↓
Display ORDER SUMMARY
                    ↓
Call OrderManager.place_order()
                    ↓
Display RESPONSE (formatted table)
                    ↓
Print ✅ success or ❌ error
```

---

### 3. **bot/validators.py** (Input Validation)
**Purpose:** Validate all user inputs before API calls

**Functions:**
- `validate_symbol(symbol: str) → str`
  - Check format: must be string, non-empty
  - **Current limitation:** Only accepts symbols ending with "USDT" (e.g., BTCUSDT, ETHUSDT)
  - Returns uppercase symbol
  - **Note:** Hardcoded to USDT for testnet scope. To support multiple quote currencies (BUSD, USDC, etc.):
    1. Add `ACCEPTED_QUOTE_CURRENCIES = ["USDT", "BUSD", "USDC"]` to `config.py`
    2. Update `validate_symbol()` to check against `config.ACCEPTED_QUOTE_CURRENCIES`
    3. Optionally validate symbols against Binance API's trading pairs endpoint for live pair validation

- `validate_side(side: str) → str`
  - Must be "BUY" or "SELL"
  - Returns uppercase side

- `validate_order_type(order_type: str) → str`
  - Must be "MARKET" or "LIMIT"
  - Returns uppercase type

- `validate_quantity(quantity: float|str|int) → float`
  - Must be positive number
  - Returns as float

- `validate_price(price: float|str|None, order_type: str) → float`
  - If LIMIT order: price is REQUIRED
  - If MARKET order: price ignored
  - Must be positive number
  - Returns as float (0.0 for MARKET)

- `validate_all_inputs(...) → dict`
  - Calls all validators
  - Returns dictionary with validated inputs
  - Single entry point for validation

**Error Messages (User-Friendly):**
```
"Symbol must end with USDT (e.g., BTCUSDT)"
"Side must be BUY or SELL"
"Order type must be MARKET or LIMIT"
"Quantity must be positive"
"Price is required for LIMIT orders"
"Price must be positive"
```

---

### 4. **bot/orders.py** (Business Logic)
**Purpose:** Orchestrate order placement process

**Class:** `OrderManager`

**Methods:**
- `__init__()` — Initialize BinanceClient
- `place_order(symbol, side, order_type, quantity, price=None) → dict`

**Workflow:**
```
1. Validate inputs (call validators.validate_all_inputs())
2. Log order request with parameters
3. Call client.create_order()
4. Parse response into structured dict
5. Log success/error
6. Return result to CLI
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
    "raw_response": {...}  # Full API response
}
```

---

### 5. **bot/client.py** (Binance API Wrapper)
**Purpose:** Handle all Binance API communication

**Class:** `BinanceClient`

**Configuration:**
- API credentials from `.env` (API_KEY, API_SECRET)
- Testnet: `testnet=True`
- Uses `binance.client.Client` from python-binance library

**Methods:**
- `__init__()` — Initialize and connect to Binance Testnet
- `create_order(symbol, side, type_, quantity, price=None) → dict`
  - Builds request parameters
  - Calls `client.futures_create_order()`
  - Catches `BinanceAPIException` and `BinanceRequestException`
  - Logs all requests and responses
  - Returns raw response from Binance

- `get_account_balance() → dict` — Get account info (bonus feature)

**Exception Handling:**
```python
try:
    response = self.client.futures_create_order(**params)
except BinanceAPIException as e:
    # API returned error (e.g., insufficient balance, invalid order)
except BinanceRequestException as e:
    # Network/connection error
except Exception as e:
    # Unknown error
```

---

### 6. **bot/logging_config.py** (Logging Setup)
**Purpose:** Configure centralized logging

**Features:**
- Rotating file handler: 5MB per file, 5 backups
- Console handler: Shows errors only
- Log file: `logs/bot.log`
- Format: `timestamp - logger_name - level - message`

**Example Log Entry:**
```
2026-04-03 15:59:21 - trading_bot - INFO - Placing order - Symbol: BTCUSDT, Side: BUY, Type: MARKET, Qty: 0.01
2026-04-03 15:59:21 - trading_bot - DEBUG - Creating MARKET order with params: {'symbol': 'BTCUSDT', ...}
2026-04-03 15:59:22 - trading_bot - DEBUG - Order created successfully: {'orderId': 13020106208, ...}
2026-04-03 15:59:22 - trading_bot - INFO - Order placed successfully - ID: 13020106208, Status: NEW
```

**Log Levels:**
- `DEBUG` — Request/response details
- `INFO` — Order placement attempts and results
- `ERROR` — Validation errors, API errors, exceptions

---

### 7. **.env** (Configuration)
**Purpose:** Store sensitive API credentials

```
API_KEY=your_binance_testnet_api_key
API_SECRET=your_binance_testnet_api_secret
```

**Security:**
- Added to `.gitignore` — never committed to git
- Loaded via `python-dotenv`
- Checked at startup in `BinanceClient.__init__()`

---

### 8. **requirements.txt** (Dependencies)
```
python-binance>=1.0.17,<2.0.0    # Binance API wrapper (fixed major version)
python-dotenv>=1.0.0,<2.0.0      # Environment variable management
```

**Dependency Management:**
- Uses version pinning to prevent breaking changes
- Recommended: Create a `requirements.lock` file for production deployments
  ```bash
  pip freeze > requirements.lock
  ```
- Lock file ensures reproducible installs across all environments
- To upgrade: `pip install -U -r requirements.txt && pip freeze > requirements.lock`

### Complete Order Placement Flow

```
START
  │
  ├─→ python cli.py place-order [OPTIONS]
  │
  ├─→ [Arguments provided?]
  │   ├─ YES → Parse from command line
  │   │   └─→ JumpTO: Validation
  │   │
  │   └─ NO → Interactive mode
  │       ├─ Prompt for symbol
  │       ├─ Prompt for side
  │       ├─ Prompt for order type
  │       ├─ Prompt for quantity
  │       ├─ If LIMIT: Prompt for price
  │       └─→ JumpTO: Validation
  │
  ├─→ VALIDATION:
  │   ├─ Validate symbol
  │   ├─ Validate side
  │   ├─ Validate order type
  │   ├─ Validate quantity
  │   ├─ Validate price (if needed)
  │   │
  │   ├─ [All valid?]
  │   │   ├─ NO → ERROR: Show message → END
  │   │   │
  │   │   └─ YES → Display ORDER SUMMARY
  │   └─→ JumpTO: API Call
  │
  ├─→ API CALL:
  │   ├─ Check .env for API_KEY/SECRET
  │   ├─ Connect to Binance Testnet
  │   ├─ Build request parameters
  │   ├─ Log request
  │   ├─ Send futures_create_order() to Binance
  │   │
  │   ├─ [API Success?]
  │   │   ├─ NO → Catch exception
  │   │   │    ├─ Log error
  │   │   │    ├─ Show ERROR message
  │   │   │    └─ END
  │   │   │
  │   │   └─ YES → Parse response
  │   └─→ JumpTO: Display Response
  │
  ├─→ DISPLAY RESPONSE:
  │   ├─ Format response as table
  │   ├─ Show Order ID, Status, Qty, Price
  │   ├─ Print ✅ success indicator
  │   ├─ Log success
  │   └─→ JumpTO: End
  │
  └─→ END (Exit with code 0 or 1)
```

---

## 📊 Data Flow

### Step-by-Step Data Journey

#### **1. User Input (Interactive)**
```
User Input
    └─→ Raw string (e.g., "btcusdt", "buy", "market", "0.01", "65000")
```

#### **2. CLI Processing**
```
Interactive/CLI Args
    └─→ Dictionary: {
        'symbol': 'btcusdt',
        'side': 'buy',
        'type': 'market',
        'qty': '0.01',
        'price': '65000'
    }
```

#### **3. Validation Layer**
```
Raw Input Dict
    └─→ validators.validate_all_inputs()
        └─→ Validated Dict: {
            'symbol': 'BTCUSDT',        # upper, checked ends with USDT
            'side': 'BUY',              # upper, checked in [BUY, SELL]
            'order_type': 'MARKET',     # upper, checked in [MARKET, LIMIT]
            'quantity': 0.01,           # float, checked > 0
            'price': 0.0                # float or 0 for MARKET
        }
```

#### **4. Order Manager**
```
Validated Dict
    └─→ OrderManager.place_order()
        ├─→ Log request
        ├─→ Call BinanceClient.create_order()
        └─→ Parse Binance response
            └─→ Result Dict: {
                'success': True,
                'order_id': 13020106208,
                'symbol': 'BTCUSDT',
                'status': 'NEW',
                'quantity': 0.01,
                'executed_qty': 0.0,
                'average_price': 0.0,
                'raw_response': {...}
            }
```

#### **5. Binance API**
```
Request to https://testnet.binancefuture.com/fapi/v1/order
    ├─ Parameters: BTCUSDT, BUY, MARKET, 0.01
    ├─ Headers: API-Key, signature
    └─→ Response JSON: {
        orderId: 13020106208,
        status: NEW,
        executedQty: 0.0,
        avgPrice: 0.0,
        ... (20+ fields)
    }
```

#### **6. CLI Display**
```
Result Dict
    └─→ format_order_response()
        └─→ Display: ✅ Order placed successfully
            Order ID: 13020106208
            Status: NEW
            ...
```

---

## ⚠️ Error Handling

### Error Handling Strategy

| Layer | Error Type | Handled In | Action | Result |
|-------|-----------|-----------|--------|--------|
| **Bootstrap** | Missing .env file | `bot/config.py` (load time) | Validate API_KEY/API_SECRET present; raise RuntimeError | Fail fast with "Missing required environment variables: API_KEY, API_SECRET" |
| **CLI** | Missing arguments | `bot/cli.py` (parse_args) | Check all([args.symbol, args.side, ...]) | Show help or raise ValueError |
| **CLI** | Missing subcommand | `bot/cli.py` (main) | Check args.command | Show help and exit 0 |
| **Validators** | Invalid symbol | `bot/validators.py.validate_symbol()` | Symbol must end with USDT | Raise ValueError("Symbol must end with USDT...") |
| **Validators** | Invalid side (not BUY/SELL) | `bot/validators.py.validate_side()` | Check against ["BUY", "SELL"] | Raise ValueError("Side must be BUY or SELL") |
| **Validators** | Invalid order type | `bot/validators.py.validate_order_type()` | Check against ["MARKET", "LIMIT"] | Raise ValueError("Order type must be MARKET or LIMIT") |
| **Validators** | Invalid quantity | `bot/validators.py.validate_quantity()` | Must be positive float | Raise ValueError("Quantity must be positive") |
| **Validators** | Missing price for LIMIT | `bot/validators.py.validate_price()` | LIMIT orders require price | Raise ValueError("Price is required for LIMIT orders") |
| **OrderManager** | Validation fails | `bot/orders.py.place_order()` (try/except) | Catch ValueError from validators | Log error; re-raise to CLI |
| **Client** | Authentication fails | `bot/client.py.create_order()` (try/except) | Catch BinanceAPIException [401] | Log "[req_id=X] Binance API Error [401]: ..."; raise Exception |
| **Client** | Rate limiting | `bot/client.py._retry_api_call()` | Catch BinanceAPIException [429]; implement backoff | Retry up to MAX_RETRIES times with RETRY_DELAY between attempts; log warning |
| **Client** | Network timeout | `bot/client.py._retry_api_call()` | Catch BinanceRequestException (network error) | Retry up to MAX_RETRIES times; log warning; eventually raise to caller |
| **Client** | API validation error | `bot/client.py.create_order()` | Catch BinanceAPIException [400] | Log error; DO NOT retry (API error, not network) |
| **CLI** | Order placement fails | `bot/cli.py.main()` (try/except) | Catch Exception from OrderManager | Print format_error_message(str(e)); exit 1 |

### Error Flow Example

**Scenario 1: Missing price for LIMIT order**
```
User enters: python cli.py place-order --symbol BTCUSDT --side BUY --type LIMIT --qty 0.01
    ↓
cli.py calls validators.validate_all_inputs()
    ↓
validate_price(price=None, order_type="LIMIT") raises ValueError("Price is required for LIMIT orders")
    ↓
OrderManager catches ValueError
    ↓
cli.py catches Exception from place_order()
    ↓
Format: "❌ Order failed: Price is required for LIMIT orders"
    ↓
Exit with code 1
```

**Scenario 2: Network timeout (with retry)**
```
User places order: python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
    ↓
client.py._retry_api_call() calls futures_create_order()
    ↓
BinanceRequestException (connection timeout)
    ↓
Attempt 1/2 fails; log warning; sleep 0.5s
    ↓
Attempt 2/2 fails; raise exception
    ↓
cli.py catches and prints: "❌ Order failed: Binance Request Error: [error details]"
    ↓
Exit with code 1
```

**Scenario 3: Authentication fails (no retry)**
```
User places order with invalid API key
    ↓
client.py.create_order() calls futures_create_order()
    ↓
BinanceAPIException [401] "API-key format invalid"
    ↓
cli.py catches: "❌ Order failed: Binance API Error [401]: API-key format invalid"
    ↓
Exit with code 1
(No retry attempted - API error, not network error)
```

---

## ✨ Key Features

### 1. **Dual Interface**
- **Interactive Mode**: Prompts user for each field
- **CLI Mode**: Direct arguments for automation

### 2. **Input Validation**
- Client-side validation before API calls
- Clear, actionable error messages
- Type checking and range checking

### 3. **Professional Logging**
- All requests logged with timestamps and request IDs
- All responses captured
- Rotating file logs with size limits
- Separate DEBUG and ERROR levels

### 4. **Error Resilience**
- Graceful handling of network errors
- API error capture and translation
- User-friendly error messages
- No crashes, always exit cleanly

### 5. **Formatted Output**
- Clean ASCII tables
- Color indicators (✅/❌)
- Organized information display

### 6. **Security**
- API credentials in `.env` (not in code/git)
- No plaintext secrets in logs
- Testnet isolation (no real funds at risk)

---

## 🚀 Execution Examples

### Example 1: Interactive Mode
```bash
$ python cli.py place-order

========================================
            PLACE ORDER
========================================
Enter symbol (e.g., BTCUSDT): BTCUSDT
Enter side (BUY/SELL): BUY
Enter order type (MARKET/LIMIT): MARKET
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
Executed Qty    : 0.0
Average Price   : 0.0

✅ Order placed successfully
```

### Example 2: CLI Mode (MARKET)
```bash
$ python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --qty 0.01

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
...

✅ Order placed successfully
```

### Example 3: CLI Mode (LIMIT)
```bash
$ python cli.py place-order --symbol ETHUSDT --side SELL --type LIMIT --qty 1 --price 2500

===================================
          ORDER SUMMARY
===================================
Symbol     : ETHUSDT
Side       : SELL
Type       : LIMIT
Quantity   : 1
Price      : 2500

===================================
            RESPONSE
===================================
Order ID        : 13020106209
Status          : NEW
...

✅ Order placed successfully
```

### Example 4: Validation Error
```bash
$ python cli.py place-order --symbol BTCUSDT --side BUY --type LIMIT --qty 0.01

===================================
          ORDER SUMMARY
===================================
Symbol     : BTCUSDT
Side       : BUY
Type       : LIMIT
Quantity   : 0.01
Price      : None

❌ Order failed: Price is required for LIMIT orders
```

---

## 📝 Summary

### What The Bot Does:
1. **Accepts user input** via CLI (interactive or arguments)
2. **Validates inputs** against business rules
3. **Connects to Binance Testnet** using credentials from `.env`
4. **Places orders** (MARKET or LIMIT, BUY or SELL)
5. **Logs everything** to `logs/bot.log`
6. **Displays formatted results** with success/error indicators

### Why It's Production-Quality:
- ✅ Modular architecture (layers of responsibility)
- ✅ Input validation at CLI level
- ✅ Comprehensive error handling
- ✅ Detailed logging for debugging
- ✅ User-friendly error messages
- ✅ Type hints for clarity
- ✅ No hardcoded values
- ✅ Testnet isolation for safety
- ✅ Professional code structure
- ✅ .gitignore protection for secrets

---

## 🔗 Related Files
- [README.md](README.md) — User guide and examples
- [.env](.env) — API credentials template
- [requirements.txt](requirements.txt) — Dependencies
- [.gitignore](.gitignore) — Git configuration
