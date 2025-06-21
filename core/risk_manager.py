import yaml
import logging
from core.broker_interface import get_account, get_position

# Load config
with open("config/settings.yaml", "r") as f:
    settings = yaml.safe_load(f)

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ----------------------------
# Main trade gatekeeper
# ----------------------------

def is_trade_allowed(symbol, side):
    account = get_account()
    if account is None:
        logger.error("Risk check failed: couldn't fetch account")
        return False

    # --- Daily Loss Check ---
    equity = float(account.equity)
    last_equity = float(account.last_equity)
    pnl_today = equity - last_equity
    max_loss = float(settings.get("max_daily_loss", 500))

    if pnl_today < -max_loss:
        logger.warning(f"Risk block: daily loss {pnl_today} > max allowed {max_loss}")
        return False

    # --- Position Size Check ---
    position = get_position(symbol)
    current_qty = int(position.qty) if position else 0
    max_qty = int(settings.get("max_position_size", 1000))

    if current_qty >= max_qty:
        logger.warning(f"Risk block: {symbol} position {current_qty} exceeds max {max_qty}")
        return False

    # --- Allowed Symbols ---
    allowed_symbols = settings.get("allowed_symbols", [])
    if symbol not in allowed_symbols:
        logger.warning(f"Risk block: {symbol} not in allowed symbols list.")
        return False

    logger.info(f"Risk manager approved: {symbol} | side: {side}")
    return True