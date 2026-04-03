"""
Order placement logic for trading bot.
"""

from typing import Union, Optional
from bot.client import BinanceClient
from bot.validators import validate_all_inputs
from bot.logging_config import logger


class OrderManager:
    """Manages order placement and processing."""
    
    def __init__(self):
        """Initialize order manager with Binance client."""
        self.client = BinanceClient()
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Union[str, float, int],
        price: Union[str, float, int, None] = None
    ) -> dict:
        """
        Place an order on Binance Futures Testnet.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            order_type: Order type (MARKET or LIMIT)
            quantity: Order quantity
            price: Order price (required for LIMIT, optional for MARKET)
            
        Returns:
            Dictionary with order details and status
            
        Raises:
            ValueError: If input validation fails
            Exception: If order placement fails
        """
        # Validate all inputs
        try:
            validated = validate_all_inputs(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValueError(str(e))
        
        # Log order request
        log_msg = (
            f"Placing order - Symbol: {validated['symbol']}, "
            f"Side: {validated['side']}, "
            f"Type: {validated['order_type']}, "
            f"Qty: {validated['quantity']}"
        )
        if validated['price'] > 0:
            log_msg += f", Price: {validated['price']}"
        logger.info(log_msg)
        
        # Create order via client
        try:
            response = self.client.create_order(
                symbol=validated["symbol"],
                side=validated["side"],
                type_=validated["order_type"],
                quantity=validated["quantity"],
                price=validated["price"] if validated["price"] > 0 else None
            )
        except Exception as e:
            logger.error(f"Order placement failed: {str(e)}")
            raise Exception(str(e))
        
        # Parse and structure response
        result = {
            "success": True,
            "order_id": response.get("orderId"),
            "symbol": response.get("symbol"),
            "side": response.get("side"),
            "type": response.get("type"),
            "status": response.get("status"),
            "quantity": float(response.get("origQty", 0)),
            "executed_qty": float(response.get("executedQty", 0)),
            "average_price": float(response.get("avgPrice", 0)),
            "price": float(response.get("price", 0)),
            "raw_response": response
        }
        
        logger.info(f"Order placed successfully - ID: {result['order_id']}, Status: {result['status']}")
        
        return result
