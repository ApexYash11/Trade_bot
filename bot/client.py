"""
Binance Futures Testnet API client wrapper.
"""

import os
from typing import Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv
from bot.logging_config import logger

# Load environment variables
load_dotenv()


class BinanceClient:
    """Wrapper for Binance Futures Testnet API."""
    
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
    
    def create_order(
        self,
        symbol: str,
        side: str,
        type_: str,
        quantity: float,
        price: Optional[float] = None
    ) -> dict:
        """
        Create an order on Binance Futures Testnet.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            type_: Order type (MARKET or LIMIT)
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            
        Returns:
            Order response dictionary
            
        Raises:
            BinanceAPIException: If Binance API returns an error
            Exception: For other network or parsing errors
        """
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
                params["timeInForce"] = "GTC"  # Good-Til-Cancelled
            
            logger.debug(f"Creating {type_} order with params: {params}")
            
            response = self.client.futures_create_order(**params)
            
            logger.debug(f"Order created successfully: {response}")
            
            return response
            
        except BinanceAPIException as e:
            error_msg = f"Binance API Error [{e.status_code}]: {e.message}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except BinanceRequestException as e:
            error_msg = f"Binance Request Error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error creating order: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_account_balance(self) -> dict:
        """
        Get account balance information.
        
        Returns:
            Account information dictionary
            
        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.futures_account()
            logger.debug(f"Account info retrieved")
            return response
        except Exception as e:
            error_msg = f"Error fetching account info: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
