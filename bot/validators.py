"""
Input validation for trading bot.
"""

from typing import Union


def validate_symbol(symbol: str) -> str:
    """
    Validate trading symbol format.
    
    Args:
        symbol: Trading symbol (e.g., BTCUSDT)
        
    Returns:
        Valid symbol
        
    Raises:
        ValueError: If symbol is invalid
    """
    if not isinstance(symbol, str):
        raise ValueError("Symbol must be a string")
    
    symbol = symbol.strip().upper()
    
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    
    if not symbol.endswith("USDT"):
        raise ValueError("Symbol must end with USDT (e.g., BTCUSDT)")
    
    if len(symbol) < 5:
        raise ValueError("Symbol format invalid (e.g., BTCUSDT)")
    
    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.
    
    Args:
        side: Order side (BUY or SELL)
        
    Returns:
        Valid side
        
    Raises:
        ValueError: If side is invalid
    """
    if not isinstance(side, str):
        raise ValueError("Side must be a string")
    
    side = side.strip().upper()
    
    if side not in ["BUY", "SELL"]:
        raise ValueError("Side must be BUY or SELL")
    
    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.
    
    Args:
        order_type: Order type (MARKET or LIMIT)
        
    Returns:
        Valid order type
        
    Raises:
        ValueError: If order type is invalid
    """
    if not isinstance(order_type, str):
        raise ValueError("Order type must be a string")
    
    order_type = order_type.strip().upper()
    
    if order_type not in ["MARKET", "LIMIT"]:
        raise ValueError("Order type must be MARKET or LIMIT")
    
    return order_type


def validate_quantity(quantity: Union[str, float, int]) -> float:
    """
    Validate order quantity.
    
    Args:
        quantity: Order quantity
        
    Returns:
        Valid quantity as float
        
    Raises:
        ValueError: If quantity is invalid
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError("Quantity must be a valid number")
    
    if qty <= 0:
        raise ValueError("Quantity must be positive")
    
    return qty


def validate_price(price: Union[str, float, int, None], order_type: str) -> float:
    """
    Validate order price.
    
    Args:
        price: Order price (required for LIMIT orders)
        order_type: Order type (MARKET or LIMIT)
        
    Returns:
        Valid price as float
        
    Raises:
        ValueError: If price is invalid or missing for LIMIT orders
    """
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders")
        
        try:
            px = float(price)
        except (ValueError, TypeError):
            raise ValueError("Price must be a valid number")
        
        if px <= 0:
            raise ValueError("Price must be positive")
        
        return px
    
    # MARKET orders don't require price
    return 0.0


def validate_all_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Union[str, float, int],
    price: Union[str, float, int, None] = None
) -> dict:
    """
    Validate all order inputs.
    
    Args:
        symbol: Trading symbol
        side: Order side (BUY or SELL)
        order_type: Order type (MARKET or LIMIT)
        quantity: Order quantity
        price: Order price (optional for MARKET, required for LIMIT)
        
    Returns:
        Dictionary with validated inputs
        
    Raises:
        ValueError: If any input is invalid
    """
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, validate_order_type(order_type))
    }
