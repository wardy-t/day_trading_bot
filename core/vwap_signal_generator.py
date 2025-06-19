import datetime
import pytz
import logging
from alpaca_trade_api.rest import REST, TimeFrame
from core.utils import calculate_vwap, calculate_rsi  # You will create these

logger = logging.getLogger(__name__)

from core.broker_interface import api

MARKET_TZ = pytz.timezone("America/New_York")
START_TIME = datetime.time(hour=9, minute=35)
END_TIME = datetime.time(hour=11, minute=0)

def is_market_open_now():
    now = datetime.datetime.now(MARKET_TZ).time()
    return START_TIME <= now <= END_TIME

def generate_vwap_bounce_signal(symbol: str):
    if not is_market_open_now():
        logger.info("Outside preferred VWAP bounce window")
        return None

    try:
        bars = api.get_bars(symbol, TimeFrame.Minute, limit=50).df
        if bars.empty:
            logger.warning(f"No bar data for {symbol}")
            return None

        bars = bars[bars['symbol'] == symbol]
        bars.set_index('timestamp', inplace=True)

        price = bars['close'].iloc[-1]
        vwap = calculate_vwap(bars)
        rsi = calculate_rsi(bars['close'])
        volume = bars['volume'].iloc[-1]
        avg_volume = bars['volume'].rolling(10).mean().iloc[-1]

        # --- Bounce logic ---
        if price > vwap and bars['low'].iloc[-2] < vwap < bars['close'].iloc[-1]:
            if rsi < 45 and volume > avg_volume:
                stop_loss = round(vwap * 0.995, 2)  # ~0.5% below VWAP
                risk_per_share = abs(price - stop_loss)
                take_profit = round(price + (1.5 * risk_per_share), 2)

                signal = {
                    "symbol": symbol,
                    "side": "buy",
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "confidence": 0.85,
                    "setup_tag": "VWAP Bounce"
                }
                logger.info(f"Generated VWAP bounce signal: {signal}")
                return signal

    except Exception as e:
        logger.exception(f"Failed to generate VWAP signal for {symbol}: {e}")

    return None