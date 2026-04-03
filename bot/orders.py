"""
Order placement logic for trading bot.
"""

import time
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
        
        # Validate that orderId is present in response
        order_id_raw = response.get("orderId")
        if not order_id_raw:
            logger.error("Order placement response missing orderId")
            raise Exception("Order placement failed: missing orderId in response")
        
        order_id = int(order_id_raw)
        
        # Brief delay to allow order execution on server
        time.sleep(0.5)
        
        # Fetch actual filled data with retry
        filled_order = response
        for retry in range(3):
            try:
                filled_order = self.client.get_order(
                    symbol=validated["symbol"],
                    order_id=order_id
                )
                logger.debug(f"Successfully fetched filled order details on attempt {retry + 1}")
                break
            except Exception as e:
                if retry < 2:
                    logger.debug(f"Attempt {retry + 1} to fetch order details failed: {str(e)}. Retrying...")
                    time.sleep(0.3)
                else:
                    logger.warning(f"Could not fetch filled order details after 3 attempts: {str(e)}. Using initial response.")
        
        # Parse and structure response with actual filled data
        # Use safe float conversion: if value is None, use 0.0
        result = {
            "success": True,
            "order_id": filled_order.get("orderId"),
            "symbol": filled_order.get("symbol"),
            "side": filled_order.get("side"),
            "type": filled_order.get("type"),
            "status": filled_order.get("status"),
            "quantity": float(filled_order.get("origQty") or 0),
            "executed_qty": float(filled_order.get("executedQty") or 0),
            "average_price": float(filled_order.get("avgPrice") or 0),
            "price": float(filled_order.get("price") or 0),
            "raw_response": filled_order
        }
        
        logger.info(f"Order placed successfully - ID: {result['order_id']}, Status: {result['status']}, Filled: {result['executed_qty']} @ {result['average_price']}")
        
        return result
