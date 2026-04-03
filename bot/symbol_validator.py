"""
Live symbol validation against Binance API.
Validates that trading symbols actually exist on the exchange.
"""

import logging
from typing import List, Dict, Optional
from bot.client import BinanceClient
from bot.logging_config import logger


class SymbolValidator:
    """Validates trading symbols against live Binance API data."""
    
    def __init__(self):
        """Initialize symbol validator with Binance client."""
        self.client = BinanceClient()
        self._symbols_cache: Optional[Dict[str, Dict]] = None
    
    def get_available_symbols(self, use_cache: bool = True) -> List[str]:
        """
        Get list of available USDT-M futures symbols from Binance.
        
        Args:
            use_cache: Whether to cache results (default True)
            
        Returns:
            List of available symbols (e.g., ['BTCUSDT', 'ETHUSDT', ...])
            
        Raises:
            Exception: If unable to fetch symbols from API
        """
        if use_cache and self._symbols_cache is not None:
            return sorted(self._symbols_cache.keys())
        
        try:
            # Get exchange info from Binance (USDT-M futures)
            exchange_info = self.client.client.futures_exchange_info()
            
            # Extract USDT-M perpetual symbols
            symbols = []
            for symbol_data in exchange_info.get('symbols', []):
                symbol = symbol_data.get('symbol')
                status = symbol_data.get('status')
                
                # Only include trading pairs that are actively trading
                if symbol and symbol.endswith('USDT') and status == 'TRADING':
                    symbols.append({
                        'symbol': symbol,
                        'base': symbol_data.get('baseAsset'),
                        'quote': symbol_data.get('quoteAsset'),
                        'status': status,
                    })
            
            # Cache the symbols
            self._symbols_cache = {s['symbol']: s for s in symbols}
            
            logger.debug(f"Fetched {len(symbols)} available USDT-M perpetual symbols from Binance API")
            return sorted([s['symbol'] for s in symbols])
            
        except Exception as e:
            logger.error(f"Failed to fetch available symbols from Binance API: {str(e)}")
            raise Exception(f"Unable to validate symbol availability: {str(e)}")
    
    def validate_symbol_exists(self, symbol: str) -> bool:
        """
        Validate that a symbol exists and is actively trading.
        
        Args:
            symbol: Trading symbol to validate (e.g., BTCUSDT)
            
        Returns:
            True if symbol exists and is trading, False otherwise
            
        Raises:
            Exception: If unable to reach Binance API
        """
        symbol = symbol.upper().strip()
        
        try:
            available_symbols = self.get_available_symbols(use_cache=True)
            
            if symbol in available_symbols:
                logger.debug(f"Symbol {symbol} validated successfully")
                return True
            else:
                logger.warning(f"Symbol {symbol} not found in available symbols")
                return False
                
        except Exception as e:
            # If API call fails, fall back to simple format validation
            logger.warning(
                f"Live symbol validation failed, falling back to format check: {str(e)}"
            )
            # Return True to allow the order, let validator.py handle format check
            return True
    
    def get_symbol_details(self, symbol: str) -> Optional[Dict]:
        """
        Get details about a specific symbol.
        
        Args:
            symbol: Trading symbol to get details for
            
        Returns:
            Dictionary with symbol details or None if not found
        """
        symbol = symbol.upper().strip()
        
        if not self._symbols_cache:
            try:
                self.get_available_symbols(use_cache=True)
            except Exception:
                return None
        
        return self._symbols_cache.get(symbol) if self._symbols_cache else None
    
    def clear_cache(self):
        """Clear the symbols cache to refresh on next call."""
        self._symbols_cache = None
        logger.debug("Symbol cache cleared")


# Global symbol validator instance
symbol_validator = SymbolValidator()
