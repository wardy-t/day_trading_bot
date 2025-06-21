import yaml
import logging
import finnhub  # ✅ Use Finnhub instead of yfinance
from core.broker_interface import get_account, get_position

# Load config
with open("config/settings.yaml", "r") as f:
    settings = yaml.safe_load(f)

# Finnhub client setup
finnhub_client = finnhub.Client(api_key=settings["finnhub_api_key"])

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

def is_volatility_acceptable(threshold=20.0):
    """
    Fetches the current VIX value via Finnhub and returns False if it exceeds the threshold.
    """
    try:
        quote = finnhub_client.quote("^VIX")
        vix_value = quote.get("c", 0)
        logger.info(f"🔍 Current VIX: {vix_value}")
        return vix_value < threshold
    except Exception as e:
        logger.error(f"⚠️ Finnhub VIX check failed: {e}")
        return False  # Fail-safe: block trades if check fails