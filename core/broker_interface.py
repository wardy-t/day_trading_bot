import os
import yaml
import logging
from alpaca_trade_api.rest import REST, TimeFrame, APIError

# Load logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load config
with open("config/secrets.yaml", "r") as f:
    secrets = yaml.safe_load(f)

with open("config/settings.yaml", "r") as f:
    settings = yaml.safe_load(f)

# Determine environment
BASE_URL = secrets["alpaca_base_url"]
API_KEY = secrets["alpaca_api_key"]
API_SECRET = secrets["alpaca_secret_key"]

# Initialize client
api = REST(API_KEY, API_SECRET, BASE_URL)

# ------------------------------
# Core broker functions
# ------------------------------

def connect():
    try:
        account = api.get_account()
        logger.info(f"Connected to Alpaca account: {account.account_number}")
        return True
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False

def get_account():
    try:
        return api.get_account()
    except Exception as e:
        logger.error(f"Error fetching account: {e}")
        return None

def get_position(symbol):
    try:
        return api.get_position(symbol)
    except APIError as e:
        if "position does not exist" in str(e):
            return None
        logger.error(f"Error fetching position for {symbol}: {e}")
        return None

def get_price(symbol):
    try:
        barset = api.get_bars(symbol, TimeFrame.Minute, limit=1)
        return float(barset[0].c) if barset else None
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return None

def submit_order(symbol, qty, side, type="market", time_in_force="gtc", limit_price=None, stop_price=None):
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=type,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price
        )
        logger.info(f"Order submitted: {order.id} for {symbol} ({side} {qty})")
        return order
    except Exception as e:
        logger.error(f"Order failed: {e}")
        return None
    

def submit_bracket_order(symbol, qty, side, entry_price, stop_loss, take_profit):
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type="limit",
            time_in_force="gtc",
            limit_price=entry_price,
            order_class="bracket",
            stop_loss={"stop_price": round(stop_loss, 2)},
            take_profit={"limit_price": round(take_profit, 2)}
        )
        logger.info(f"Bracket order submitted: {order.id} for {symbol} ({side} {qty})")
        return order
    except Exception as e:
        logger.exception(f"Failed to submit bracket order for {symbol}: {e}")
        return None

def cancel_order(order_id):
    try:
        api.cancel_order(order_id)
        logger.info(f"Order {order_id} cancelled.")
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {e}")

def get_order_status(order_id):
    try:
        return api.get_order(order_id)
    except Exception as e:
        logger.error(f"Error checking order {order_id}: {e}")
        return None
    
def get_last_closed_order(symbol):
    try:
        orders = api.list_orders(status='closed', limit=10)
        for order in orders:
            if order.symbol == symbol and order.filled_avg_price is not None:
                return order
        return None
    except Exception as e:
        logger.error(f"Error fetching closed order for {symbol}: {e}")
        return None

def get_tradable_symbols():
    try:
        assets = api.list_assets(status="active")
        tradable = [
            asset.symbol for asset in assets
            if asset.tradable and asset.exchange in ["NASDAQ", "NYSE", "AMEX"]
        ]
        logger.info(f"Loaded {len(tradable)} tradable symbols.")
        return tradable
    except Exception as e:
        logger.error(f"Error fetching tradable symbols: {e}")
        return []