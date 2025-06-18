import logging
from core.broker_interface import get_price, submit_order, get_account
from core.risk_manager import is_trade_allowed
from core.journal_logger import log_trade

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Example trade signal structure
# {
#   "symbol": "AAPL",
#   "side": "buy",  # or "sell"
#   "confidence": 0.85,
#   "setup_tag": "VWAP Bounce"
# }

def process_signal(signal):
    symbol     = signal["symbol"]
    side       = signal["side"]
    stop_loss  = float(signal["stop_loss"])
    confidence = signal.get("confidence", 0)

    logger.info(f"Received signal: {symbol} | {side.upper()} | confidence: {confidence} | stop: {stop_loss}")

    if not is_trade_allowed(symbol, side):
        logger.warning(f"Trade blocked by risk manager: {symbol} {side}")
        return None

    price = get_price(symbol)
    if price is None:
        logger.error(f"Could not fetch price for {symbol}")
        return None

    # 1. Calculate stop distance and position size
    stop_distance = abs(price - stop_loss)
    qty = determine_position_size(price, stop_loss, risk_pct=0.01)
    if qty == 0:
        logger.warning(f"Position size calculated as 0 — skipping trade.")
        return None

    # 2. Calculate take-profit (1.5R)
    r_multiple_target = 1.5
    if side == "buy":
        take_profit = price + (stop_distance * r_multiple_target)
    else:
        take_profit = price - (stop_distance * r_multiple_target)

    # 3. Submit order (can later add TP/SL as bracket order)
    order = submit_order(symbol=symbol, qty=qty, side=side)
    if order:
        logger.info(f"Executed trade: {order.id} | {symbol} | {side} | qty: {qty}")
        
        # Log trade to journal
        trade_data = {
            "symbol":           symbol,
            "qty":              qty,
            "entry_price":      price,
            "stop_loss":        stop_loss,
            "risk_amount":      stop_distance * qty,
            "confidence_score": confidence,
            "setup_tag":        signal.get("setup_tag"),
            "r_multiple":       r_multiple_target,
            "notes":            f"Take profit set at {take_profit:.2f}"
        }
        log_trade(trade_data)
    else:
        logger.error(f"Trade execution failed for {symbol} {side}")

    return order

def determine_position_size(price, stop_loss, risk_pct=0.01):
    account = get_account()
    if not account:
        return 0

    equity = float(account.equity)
    risk_capital = equity * risk_pct

    stop_distance = abs(price - stop_loss)
    if stop_distance == 0:
        return 0

    qty = int(risk_capital / stop_distance)
    return qty