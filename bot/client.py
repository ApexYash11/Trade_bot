"""
Binance Futures Testnet API client wrapper.
Handles API communication with retry logic and request tracking.
"""

import os
import time
import uuid
from typing import Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv
from bot.logging_config import logger
from bot import config

# Load environment variables
load_dotenv()


class BinanceClient:
    """
    Wrapper for Binance Futures Testnet API.
    
    Provides:
    - Connection management with testnet configuration
    - Retry logic for network errors
    - Request ID tracking for debugging
    - Comprehensive exception handling
    """
    
    def __init__(self):
        """Initialize Binance Futures client with testnet configuration."""
        api_key = os.getenv("API_KEY")
        api_secret = os.getenv("API_SECRET")
        
        if not api_key or not api_secret:
            raise ValueError(
                "API_KEY and API_SECRET must be set in .env file. "
                "See README.md for setup instructions."
            )
        
        # Initialize Client for testnet
        self.client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True  # Use testnet
        )
        
        logger.debug("Binance Futures Testnet client initialized")
    
    def _generate_request_id(self) -> str:
        """
        Generate a unique request ID for tracking.
        
        Returns:
            Short UUID string (first 8 characters)
        """
        return str(uuid.uuid4())[:8]
    
    def create_order(
        self,
        symbol: str,
        side: str,
        type_: str,
        quantity: float,
        price: Optional[float] = None,
        request_id: Optional[str] = None
    ) -> dict:
        """
        Create an order on Binance Futures Testnet with retry logic.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            type_: Order type (MARKET or LIMIT)
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            request_id: Optional tracking ID (auto-generated if not provided)
            
        Returns:
            Order response dictionary
            
        Raises:
            ValueError: If input validation fails (not retried)
            Exception: If order placement fails after max retries
        """
        if not request_id:
            request_id = self._generate_request_id()
        
        req_tag = f"[req_id={request_id}]"
        
        try:
            params = {
                "symbol": symbol,
                "side": side,
                "type": type_,
                "quantity": quantity
            }
            
            # Add price for LIMIT orders
            if type_ == "LIMIT" and price:
                params["price"] = price
                params["timeInForce"] = config.DEFAULT_TIME_IN_FORCE
            
            logger.debug(f"{req_tag} Creating {type_} order - Symbol: {symbol}, Qty: {quantity}")
            
            # Attempt with retry logic
            response = self._retry_api_call(params, request_id, req_tag)
            
            logger.debug(f"{req_tag} Order created successfully - Order ID: {response.get('orderId')}")
            
            return response
            
        except BinanceAPIException as e:
            error_msg = f"{req_tag} Binance API Error [{e.status_code}]: {e.message}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except BinanceRequestException as e:
            error_msg = f"{req_tag} Binance Request Error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"{req_tag} Error creating order: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _retry_api_call(self, params: dict, request_id: str, req_tag: str) -> dict:
        """
        Attempt API call with retry logic for network errors.
        
        Only retries on network/connection errors, NOT on API validation errors.
        
        Args:
            params: Order parameters
            request_id: Request tracking ID
            req_tag: Formatted request tag for logging
            
        Returns:
            API response dictionary
            
        Raises:
            Exception: If all retries exhausted
        """
        last_exception = None
        
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                if attempt > 1:
                    logger.info(f"{req_tag} Retry attempt {attempt}/{config.MAX_RETRIES}")
                    time.sleep(config.RETRY_DELAY)
                
                response = self.client.futures_create_order(**params)
                return response
                
            except BinanceRequestException as e:
                # Network error - retry eligible
                last_exception = e
                if attempt < config.MAX_RETRIES:
                    logger.warning(f"{req_tag} Network error (attempt {attempt}): {str(e)}. Retrying...")
                    continue
                else:
                    raise
            except BinanceAPIException as e:
                # API error - do NOT retry
                raise
            except Exception as e:
                # Unknown error - do NOT retry
                raise
        
        # All retries exhausted
        raise last_exception if last_exception else Exception("Unknown error")
    
    def get_account_balance(self) -> dict:
        """
        Get account balance information.
        
        Returns:
            Account information dictionary
            
        Raises:
            Exception: If API call fails
        """
        request_id = self._generate_request_id()
        req_tag = f"[req_id={request_id}]"
        
        try:
            logger.debug(f"{req_tag} Fetching account information")
            response = self.client.futures_account()
            logger.debug(f"{req_tag} Account info retrieved")
            return response
        except Exception as e:
            error_msg = f"{req_tag} Error fetching account info: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
