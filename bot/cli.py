"""
CLI interface for trading bot.
Handles command parsing, interactive mode, and user interaction.
"""

import argparse
import sys
from typing import Optional
from bot.orders import OrderManager
from bot.logging_config import logger
from bot import config


def format_order_summary(inputs: dict) -> str:
    """Format order input summary for display."""
    output = "\n"
    output += "=" * 35 + "\n"
    output += " " * 10 + "ORDER SUMMARY\n"
    output += "=" * 35 + "\n"
    output += f"Symbol     : {inputs['symbol']}\n"
    output += f"Side       : {inputs['side']}\n"
    output += f"Type       : {inputs['type']}\n"
    output += f"Quantity   : {inputs['qty']}\n"
    if inputs['type'] == 'LIMIT':
        output += f"Price      : {inputs['price']}\n"
    output += "\n"
    
    return output


def format_order_response(response: dict) -> str:
    """Format order response for display."""
    output = "\n"
    output += "=" * 35 + "\n"
    output += " " * 12 + "RESPONSE\n"
    output += "=" * 35 + "\n"
    output += f"Order ID        : {response['order_id']}\n"
    output += f"Status          : {response['status']}\n"
    output += f"Executed Qty    : {response['executed_qty']}\n"
    output += f"Average Price   : {response['average_price']}\n"
    output += "\n"
    
    return output


def format_success_message() -> str:
    """Format success message."""
    return "✅ Order placed successfully\n"


def format_error_message(error: str) -> str:
    """Format error message."""
    return f"❌ Order failed: {error}\n"


def get_interactive_inputs() -> dict:
    """
    Prompt user for order inputs interactively.
    
    Returns:
        Dictionary with user inputs
    """
    print("\n" + "=" * 40)
    print(" " * 12 + "PLACE ORDER")
    print("=" * 40)
    
    inputs = {}
    
    # Get symbol
    while True:
        symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
        if symbol:
            inputs['symbol'] = symbol
            break
        print("Symbol cannot be empty")
    
    # Get side
    while True:
        side = input("Enter side (BUY/SELL): ").strip().upper()
        if side in ["BUY", "SELL"]:
            inputs['side'] = side
            break
        print("Side must be BUY or SELL")
    
    # Get order type
    while True:
        order_type = input("Enter order type (MARKET/LIMIT): ").strip().upper()
        if order_type in ["MARKET", "LIMIT"]:
            inputs['type'] = order_type
            break
        print("Order type must be MARKET or LIMIT")
    
    # Get quantity
    while True:
        try:
            qty_str = input("Enter quantity: ").strip()
            qty = float(qty_str)
            if qty > 0:
                inputs['qty'] = qty_str
                break
            print("Quantity must be positive")
        except ValueError:
            print("Quantity must be a valid number")
    
    # Get price if LIMIT order
    if inputs['type'] == 'LIMIT':
        while True:
            try:
                price_str = input("Enter price: ").strip()
                price = float(price_str)
                if price > 0:
                    inputs['price'] = price_str
                    break
                print("Price must be positive")
            except ValueError:
                print("Price must be a valid number")
    else:
        inputs['price'] = None
    
    return inputs


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
  python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --qty 0.01 --price 60000
  python cli.py place-order  (interactive mode)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Place-order subcommand
    place_order_parser = subparsers.add_parser(
        'place-order',
        help='Place a market or limit order'
    )
    
    place_order_parser.add_argument(
        '--symbol',
        type=str,
        help='Trading symbol (e.g., BTCUSDT)'
    )
    
    place_order_parser.add_argument(
        '--side',
        type=str,
        help='Order side: BUY or SELL'
    )
    
    place_order_parser.add_argument(
        '--type',
        dest='order_type',
        type=str,
        help='Order type: MARKET or LIMIT'
    )
    
    place_order_parser.add_argument(
        '--qty',
        type=str,
        help='Order quantity'
    )
    
    place_order_parser.add_argument(
        '--price',
        type=str,
        help='Order price (required for LIMIT orders)'
    )
    
    return parser


def main():
    """
    Main CLI entry point.
    
    Handles:
    - Command parsing
    - Interactive mode fallback
    - Order placement
    - Output formatting
    - Error handling with proper exit codes
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        sys.exit(config.EXIT_SUCCESS)
    
    # Handle place-order command
    if args.command == 'place-order':
        # If no arguments provided, use interactive mode
        if not any([args.symbol, args.side, args.order_type, args.qty]):
            inputs = get_interactive_inputs()
        else:
            # Use provided arguments
            if not all([args.symbol, args.side, args.order_type, args.qty]):
                print("❌ Missing required arguments. Use --help for usage.")
                sys.exit(config.EXIT_FAILURE)
            
            # Normalize inputs to uppercase
            inputs = {
                'symbol': args.symbol.upper(),
                'side': args.side.upper(),
                'type': args.order_type.upper(),
                'qty': args.qty,
                'price': args.price
            }
        
        # Display order summary
        print(format_order_summary(inputs))
        
        # Place order
        order_manager = OrderManager()
        try:
            response = order_manager.place_order(
                symbol=inputs['symbol'],
                side=inputs['side'],
                order_type=inputs['type'],
                quantity=inputs['qty'],
                price=inputs['price']
            )
            
            # Display response
            print(format_order_response(response))
            print(format_success_message())
            
            sys.exit(config.EXIT_SUCCESS)
            
        except ValueError as e:
            print(format_error_message(str(e)))
            sys.exit(config.EXIT_FAILURE)
        except Exception as e:
            print(format_error_message(str(e)))
            sys.exit(config.EXIT_FAILURE)


if __name__ == '__main__':
    main()
