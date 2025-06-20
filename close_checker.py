import time
import logging
from datetime import date
from core.broker_interface import get_position, get_last_closed_order
from core.journal_logger import get_open_trades, update_closed_trade

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_for_closed_trades():
    open_trades = get_open_trades()
    logger.info(f"Checking {len(open_trades)} open trades...")

    for trade in open_trades:
        symbol = trade["symbol"]
        ref = trade["ref"]
        qty = trade["qty"]
        buy_price = trade["buy_price"]

        position = get_position(symbol)

        if position is None:
            # Trade is now closed, fetch order fill data instead of live price
            order = get_last_closed_order(symbol)
            if order is None:
                logger.warning(f"Couldn’t fetch closed order for {symbol}")
                continue

            sell_price = round(float(order.filled_avg_price), 2)
            net_pnl = round((sell_price - buy_price) * qty, 2)
            net_roi = round(((sell_price - buy_price) / buy_price) * 100, 2)

            update_data = {
                "ref": ref,
                "sell_date": date.today(),
                "sell_price": sell_price,
                "net_pnl": net_pnl,
                "net_roi": net_roi
            }

            update_closed_trade(update_data)
            logger.info(f"🔒 Trade closed: {symbol} | PnL: {net_pnl} | ROI: {net_roi}%")
        else:
            logger.debug(f"Still open: {symbol}")

# Continuous loop
if __name__ == "__main__":
    while True:
        try:
            logger.info("Running close check...")
            check_for_closed_trades()
        except Exception as e:
            logger.exception(f"Error during close check: {e}")

        logger.info("Sleeping for 60 seconds...")
        time.sleep(60)