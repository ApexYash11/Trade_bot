"""
Unit tests for input validators.
Tests validation logic for symbols, sides, order types, quantities, and prices.
"""

import pytest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price
)


class TestValidateSymbol:
    """Test symbol validation."""
    
    def test_valid_symbol(self):
        """Valid USDT symbol should pass."""
        assert validate_symbol("BTCUSDT") == "BTCUSDT"
        assert validate_symbol("ethusdt") == "ETHUSDT"  # Case insensitive
    
    def test_symbol_must_end_with_usdt(self):
        """Symbol must end with USDT."""
        with pytest.raises(ValueError, match="must end with USDT"):
            validate_symbol("BTC")
        with pytest.raises(ValueError, match="must end with USDT"):
            validate_symbol("BTCUSD")
    
    def test_symbol_cannot_be_empty(self):
        """Empty symbol should fail."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_symbol("")
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_symbol("   ")
    
    def test_symbol_must_be_string(self):
        """Symbol must be a string."""
        with pytest.raises(ValueError, match="must be a string"):
            validate_symbol(12345)  # type: ignore


class TestValidateSide:
    """Test order side validation."""
    
    def test_valid_side_buy(self):
        """BUY should be valid."""
        assert validate_side("BUY") == "BUY"
        assert validate_side("buy") == "BUY"
    
    def test_valid_side_sell(self):
        """SELL should be valid."""
        assert validate_side("SELL") == "SELL"
        assert validate_side("sell") == "SELL"
    
    def test_invalid_side(self):
        """Invalid side should fail."""
        with pytest.raises(ValueError, match="must be BUY or SELL"):
            validate_side("HOLD")
        with pytest.raises(ValueError, match="must be BUY or SELL"):
            validate_side("buy_limit")
    
    def test_side_must_be_string(self):
        """Side must be a string."""
        with pytest.raises(ValueError, match="must be a string"):
            validate_side(123)  # type: ignore


class TestValidateOrderType:
    """Test order type validation."""
    
    def test_valid_market(self):
        """MARKET should be valid."""
        assert validate_order_type("MARKET") == "MARKET"
        assert validate_order_type("market") == "MARKET"
    
    def test_valid_limit(self):
        """LIMIT should be valid."""
        assert validate_order_type("LIMIT") == "LIMIT"
        assert validate_order_type("limit") == "LIMIT"
    
    def test_invalid_order_type(self):
        """Invalid order type should fail."""
        with pytest.raises(ValueError, match="must be MARKET or LIMIT"):
            validate_order_type("STOP")
        with pytest.raises(ValueError, match="must be MARKET or LIMIT"):
            validate_order_type("OCO")
    
    def test_order_type_must_be_string(self):
        """Order type must be a string."""
        with pytest.raises(ValueError, match="must be a string"):
            validate_order_type(1)  # type: ignore


class TestValidateQuantity:
    """Test quantity validation."""
    
    def test_valid_quantity_float(self):
        """Valid float quantity should pass."""
        assert validate_quantity(0.01) == 0.01
        assert validate_quantity(1.5) == 1.5
        assert validate_quantity(100) == 100.0
    
    def test_valid_quantity_string(self):
        """Valid string quantity should be converted to float."""
        assert validate_quantity("0.01") == 0.01
        assert validate_quantity("1.5") == 1.5
    
    def test_quantity_must_be_positive(self):
        """Quantity must be greater than zero."""
        with pytest.raises(ValueError, match="must be positive"):
            validate_quantity(0)
        with pytest.raises(ValueError, match="must be positive"):
            validate_quantity(-0.01)
        with pytest.raises(ValueError, match="must be positive"):
            validate_quantity("-5")
    
    def test_quantity_must_be_valid_number(self):
        """Quantity must be a valid number."""
        with pytest.raises(ValueError, match="must be a valid number"):
            validate_quantity("abc")
        with pytest.raises(ValueError, match="must be a valid number"):
            validate_quantity("0.0.1")


class TestValidatePrice:
    """Test price validation."""
    
    def test_market_order_no_price_required(self):
        """Market orders don't require price."""
        assert validate_price(None, "MARKET") == 0.0
        assert validate_price("any string", "MARKET") == 0.0
    
    def test_limit_order_price_required(self):
        """Limit orders require price."""
        with pytest.raises(ValueError, match="Price is required"):
            validate_price(None, "LIMIT")
    
    def test_valid_limit_price_float(self):
        """Valid float price for LIMIT."""
        assert validate_price(65000.0, "LIMIT") == 65000.0
        assert validate_price(2500.5, "LIMIT") == 2500.5
    
    def test_valid_limit_price_string(self):
        """Valid string price for LIMIT."""
        assert validate_price("65000", "LIMIT") == 65000.0
        assert validate_price("2500.5", "LIMIT") == 2500.5
    
    def test_price_must_be_positive(self):
        """Price must be greater than zero."""
        with pytest.raises(ValueError, match="must be positive"):
            validate_price(0, "LIMIT")
        with pytest.raises(ValueError, match="must be positive"):
            validate_price(-100, "LIMIT")
    
    def test_price_must_be_valid_number(self):
        """Price must be a valid number."""
        with pytest.raises(ValueError, match="must be a valid number"):
            validate_price("invalid", "LIMIT")
        with pytest.raises(ValueError, match="must be a valid number"):
            validate_price("50,000", "LIMIT")
