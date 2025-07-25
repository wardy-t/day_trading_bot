import logging
from core.broker_interface import get_price, submit_order, get_account
from core.risk_manager import is_trade_allowed
from core.journal_logger import log_trade
from core.broker_interface import submit_bracket_order

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

    qty = determine_position_size(price, stop_loss, risk_pct=0.01)
    if qty == 0:
        logger.warning("Position size calculated as 0 — skipping trade.")
        return None

    take_profit = round(price + abs(price - stop_loss) * 1.5, 2)

    order = submit_bracket_order(
        symbol=symbol,
        qty=qty,
        side=side,
        entry_price=price,
        stop_loss=stop_loss,
        take_profit=take_profit
    )

    if order:
        logger.info(f"Executed trade: {order.id} | {symbol} | {side} | qty: {qty}")

        trade_data = {
            "symbol":           symbol,
            "qty":              qty,
            "entry_price":      price,
            "stop_loss":        stop_loss,
            "risk_amount":      abs(price - stop_loss) * qty,
            "confidence_score": confidence,
            "setup_tag":        signal.get("setup_tag"),
            "r_multiple":       1.5,
        }
        log_trade(trade_data)
    else:
        logger.error(f"Trade execution failed for {symbol} {side}")

    return order

def determine_position_size(price, stop_loss, risk_pct=0.01, max_position_pct=0.03):
    account = get_account()
    if not account:
        return 0

    equity = float(account.equity)

    # Capital you're willing to risk on this trade (e.g. 1% of equity)
    risk_capital = equity * risk_pct

    # Maximum capital you're willing to commit to any single trade (e.g. 3%)
    max_position_value = equity * max_position_pct

    stop_distance = abs(price - stop_loss)
    if stop_distance == 0:
        return 0

    # Qty based on risk and stop loss
    qty_based_on_risk = int(risk_capital / stop_distance)

    # Qty based on total capital commitment limit
    qty_based_on_exposure = int(max_position_value / price)

    # Final qty is the smaller of the two
    qty = min(qty_based_on_risk, qty_based_on_exposure)

    logger.info(f"Qty calculated: risk-based = {qty_based_on_risk}, exposure-capped = {qty_based_on_exposure}, final = {qty}")
    return qty